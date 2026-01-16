"""
Vertex AI integration for embeddings and LLM calls.
"""

from typing import List, Optional
import numpy as np
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import settings
from src.config.constants import VERTEX_AI_BATCH_SIZE
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VertexAIClient:
    """Client for Vertex AI embeddings and models."""

    def __init__(self):
        """Initialize Vertex AI client."""
        aiplatform.init(
            project=settings.gcp_project_id,
            location=settings.vertex_ai_location
        )

        self.embedding_model = TextEmbeddingModel.from_pretrained(settings.embeddings_model)
        logger.info(
            "Vertex AI client initialized",
            project=settings.gcp_project_id,
            model=settings.embeddings_model
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_text(
        self,
        text: str,
        task_type: str = "SEMANTIC_SIMILARITY"
    ) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text
            task_type: Task type (SEMANTIC_SIMILARITY, RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, etc.)

        Returns:
            Embedding vector as numpy array
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return np.zeros(settings.embeddings_dimension)

        try:
            # Create input with task type
            embedding_input = TextEmbeddingInput(
                text=text,
                task_type=task_type
            )

            # Get embeddings
            embeddings = self.embedding_model.get_embeddings([embedding_input])

            if not embeddings or len(embeddings) == 0:
                logger.error("No embeddings returned")
                return np.zeros(settings.embeddings_dimension)

            # Convert to numpy array
            embedding_values = embeddings[0].values
            embedding_array = np.array(embedding_values)

            logger.debug(
                "Generated embedding",
                text_length=len(text),
                embedding_dim=len(embedding_array),
                task_type=task_type
            )

            return embedding_array

        except Exception as e:
            logger.error("Error generating embedding", error=str(e), exc_info=True)
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_texts(
        self,
        texts: List[str],
        task_type: str = "SEMANTIC_SIMILARITY"
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts (batch).

        Args:
            texts: List of input texts
            task_type: Task type

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Remove empty texts
        valid_texts = [t for t in texts if t and t.strip()]

        if not valid_texts:
            logger.warning("No valid texts for batch embedding")
            return [np.zeros(settings.embeddings_dimension) for _ in texts]

        try:
            # Process in batches
            all_embeddings = []

            for i in range(0, len(valid_texts), VERTEX_AI_BATCH_SIZE):
                batch = valid_texts[i:i + VERTEX_AI_BATCH_SIZE]

                # Create inputs with task type
                embedding_inputs = [
                    TextEmbeddingInput(text=text, task_type=task_type)
                    for text in batch
                ]

                # Get embeddings
                embeddings = self.embedding_model.get_embeddings(embedding_inputs)

                # Convert to numpy arrays
                batch_arrays = [
                    np.array(emb.values) for emb in embeddings
                ]

                all_embeddings.extend(batch_arrays)

                logger.debug(
                    "Generated batch embeddings",
                    batch_size=len(batch),
                    total=len(all_embeddings)
                )

            return all_embeddings

        except Exception as e:
            logger.error("Error generating batch embeddings", error=str(e), exc_info=True)
            raise


class EmbeddingService:
    """High-level service for embeddings with caching."""

    def __init__(self, vertex_client: VertexAIClient, firestore_client):
        """
        Initialize embedding service.

        Args:
            vertex_client: Vertex AI client
            firestore_client: Firestore client for caching
        """
        self.vertex_client = vertex_client
        self.firestore_client = firestore_client
        logger.info("Embedding service initialized")

    async def get_embedding(
        self,
        text: str,
        task_type: str = "SEMANTIC_SIMILARITY",
        use_cache: bool = True
    ) -> np.ndarray:
        """
        Get embedding with caching.

        Args:
            text: Input text
            task_type: Task type
            use_cache: Whether to use cache

        Returns:
            Embedding vector
        """
        # Check cache first
        if use_cache:
            cached = await self.firestore_client.get_embedding(text)
            if cached is not None:
                logger.debug("Using cached embedding", text_length=len(text))
                return cached

        # Generate new embedding
        embedding = await self.vertex_client.embed_text(text, task_type)

        # Store in cache
        if use_cache:
            await self.firestore_client.store_embedding(text, embedding)

        return embedding

    async def get_embeddings(
        self,
        texts: List[str],
        task_type: str = "SEMANTIC_SIMILARITY",
        use_cache: bool = True
    ) -> List[np.ndarray]:
        """
        Get embeddings for multiple texts with caching.

        Args:
            texts: List of input texts
            task_type: Task type
            use_cache: Whether to use cache

        Returns:
            List of embedding vectors
        """
        embeddings = []
        texts_to_embed = []
        cache_indices = []

        # Check cache for each text
        for i, text in enumerate(texts):
            if use_cache:
                cached = await self.firestore_client.get_embedding(text)
                if cached is not None:
                    embeddings.append(cached)
                    continue

            # Need to generate
            texts_to_embed.append(text)
            cache_indices.append(i)
            embeddings.append(None)  # Placeholder

        # Generate missing embeddings
        if texts_to_embed:
            logger.info(
                "Generating embeddings",
                total=len(texts),
                cached=len(texts) - len(texts_to_embed),
                to_generate=len(texts_to_embed)
            )

            new_embeddings = await self.vertex_client.embed_texts(texts_to_embed, task_type)

            # Store in cache and update results
            for i, embedding in enumerate(new_embeddings):
                result_idx = cache_indices[i]
                embeddings[result_idx] = embedding

                if use_cache:
                    await self.firestore_client.store_embedding(texts_to_embed[i], embedding)

        return embeddings

    async def embed_project(self, project_name: str, project_description: Optional[str]) -> np.ndarray:
        """
        Generate embedding for a project.

        Args:
            project_name: Project name
            project_description: Project description

        Returns:
            Project embedding
        """
        # Combine name and description
        text = project_name
        if project_description:
            text = f"{project_name}: {project_description}"

        return await self.get_embedding(text, task_type="RETRIEVAL_DOCUMENT")

    async def embed_task(self, task_description: str) -> np.ndarray:
        """
        Generate embedding for a task.

        Args:
            task_description: Task description

        Returns:
            Task embedding
        """
        return await self.get_embedding(task_description, task_type="RETRIEVAL_QUERY")
