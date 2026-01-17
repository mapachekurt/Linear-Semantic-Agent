
import vertexai
from vertexai.preview import reasoning_engines
from src.config.settings import settings

def test_remote():
    vertexai.init(
        project=settings.gcp_project_id,
        location=settings.gcp_region,
    )
    
    # Load the deployed engine - v3
    resource_name = "projects/928436235058/locations/us-central1/reasoningEngines/7826461205463040000"
    print(f"Connecting to reasoning engine: {resource_name}")
    remote_agent = reasoning_engines.ReasoningEngine(resource_name)
    
    # Test a simple query
    print("Sending test query...")
    try:
        response = remote_agent.query(
            task_description="Build a new landing page for mapache.app using modern design principles.",
            source="test_script"
        )
        print("Response received:")
        print(response)
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_remote()
