
import os
import vertexai
from vertexai.preview import reasoning_engines
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
        from src.models.task import Task
        
        self._ensure_init()
        
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
            return {"error": str(e)}

def deploy():
    print("Starting deployment to Vertex AI Reasoning Engine...")
    
    # Initialize Vertex AI
    vertexai.init(
        project=settings.gcp_project_id,
        location=settings.gcp_region,
        staging_bucket='gs://linear-semantic-agents-staging'
    )

    # Define minimal requirements for Reasoning Engine runtime
    requirements = [
        "google-cloud-aiplatform[reasoningengine]>=1.48.0",
        "google-cloud-firestore",
        "httpx",
        "tenacity",
        "pydantic-settings",
        "python-dotenv",
        "structlog",
        "langchain",
        "langchain-google-vertexai",
        "nest-asyncio"
    ]

    # Create the Reasoning Engine
    # Note: We bundle the 'src' directory as part of the deployment
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(current_dir, "src")
        
        remote_agent = reasoning_engines.ReasoningEngine.create(
            LinearReasoningAgent(),
            requirements=requirements,
            display_name="Linear Semantic Agent",
            description="AI agent for validating and categorizing Linear tasks",
            extra_packages=[src_path]
        )

        print(f"Deployment successful!")
        print(f"Reasoning Engine Resource Name: {remote_agent.resource_name}")
        
        # Save the resource name to a file for later use
        with open("reasoning_engine_resource.txt", "w") as f:
            f.write(remote_agent.resource_name)
    except Exception as e:
        print(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy()
