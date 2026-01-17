
import vertexai
from vertexai.preview import reasoning_engines
from src.config.settings import settings

def test_debug():
    vertexai.init(
        project=settings.gcp_project_id,
        location=settings.gcp_region,
    )
    
    # Load the debug agent
    resource_name = "projects/928436235058/locations/us-central1/reasoningEngines/6995547074213183488"
    print(f"Connecting to debug agent: {resource_name}")
    debug_agent = reasoning_engines.ReasoningEngine(resource_name)
    
    # Query it
    print("Querying debug agent...")
    response = debug_agent.query(text="identify")
    print("Response:")
    import json
    print(json.dumps(response, indent=2, default=str))

if __name__ == "__main__":
    test_debug()
