
"""
Standalone deployment script that bundles all agent code inline.
This avoids issues with extra_packages in Vertex AI Reasoning Engine.
"""

import os
import sys
import vertexai
from vertexai.preview import reasoning_engines

# Add parent directory to path for local imports during deployment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import settings

class LinearReasoningAgent:
    """Wrapper for LinearSemanticAgent to be used with Vertex AI Reasoning Engine."""
    
    def __init__(self):
        self.agent = None

    def set_up(self):
        """No-op set_up for faster deployment. Real init happens in query."""
        print("Reasoning Engine set_up called.")
        pass

    def _ensure_init(self):
        """Ensure the agent is initialized."""
        if self.agent is not None:
            return
            
        import asyncio
        print("Initializing LinearSemanticAgent...")
        try:
            # Import inline to ensure modules are available
            import sys
            import os
            
            # Add code directory to path
            code_dir = os.path.dirname(os.path.abspath(__file__))
            if code_dir not in sys.path:
                sys.path.insert(0, code_dir)
            
            from src.agent import LinearSemanticAgent
            self.agent = LinearSemanticAgent()
            
            # Use existing loop if available
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # In Vertex AI managed env, we might be inside a loop already
                import nest_asyncio
                nest_asyncio.apply()
            
            loop.run_until_complete(self.agent.initialize())
            print("Agent initialized successfully.")
        except Exception as e:
            print(f"FAILED to initialize agent: {e}")
            import traceback
            traceback.print_exc()
            raise

    def query(self, task_description: str, source: str = "user", task_id: str = "raw") -> dict:
        """Evaluate a task."""
        import asyncio
        
        self._ensure_init()
        
        # Import Task model
        from src.models.task import Task
        
        task = Task(
            task_description=task_description,
            source=source,
            task_id=task_id
        )
        
        try:
            loop = asyncio.get_event_loop()
            decision = loop.run_until_complete(self.agent.evaluate_task(task))
            return {
                "decision": decision.decision.value,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "suggested_action": decision.suggested_action,
                "alignment_score": decision.alignment_score,
                "tags": decision.tags
            }
        except Exception as e:
            print(f"Query failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "traceback": traceback.format_exc()}

def deploy():
    print("Starting deployment to Vertex AI Reasoning Engine...")
    
    # Initialize Vertex AI
    vertexai.init(
        project=settings.gcp_project_id,
        location=settings.gcp_region,
        staging_bucket='gs://linear-semantic-agents-staging'
    )

    # Define requirements
    requirements = [
        "google-cloud-aiplatform[reasoningengine]>=1.48.0",
        "google-cloud-firestore",
        "google-auth",
        "httpx",
        "tenacity",
        "pydantic-settings",
        "numpy",
        "pandas",
        "python-dotenv",
        "structlog",
        "langchain",
        "langchain-google-vertexai",
        "nest-asyncio"
    ]

    # Create the Reasoning Engine
    # Bundle the entire src directory
    try:
        import shutil
        import tempfile
        
        # Create temp directory and copy src
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = os.path.join(os.path.dirname(__file__), "src")
            dest_path = os.path.join(tmpdir, "src")
            shutil.copytree(src_path, dest_path)
            
            # Copy mapache context
            mapache_doc = os.path.join(os.path.dirname(__file__), "..", "mapache_context_document.md")
            if os.path.exists(mapache_doc):
                shutil.copy(mapache_doc, tmpdir)
            
            # Change to temp directory for deployment
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                remote_agent = reasoning_engines.ReasoningEngine.create(
                    LinearReasoningAgent(),
                    requirements=requirements,
                    display_name="Linear Semantic Agent v3",
                    description="AI agent for validating and categorizing Linear tasks",
                    extra_packages=["src"]
                )

                print(f"Deployment successful!")
                print(f"Reasoning Engine Resource Name: {remote_agent.resource_name}")
                
                # Save the resource name to a file for later use
                resource_file = os.path.join(original_dir, "reasoning_engine_resource.txt")
                with open(resource_file, "w") as f:
                    f.write(remote_agent.resource_name)
            finally:
                os.chdir(original_dir)
                
    except Exception as e:
        print(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy()
