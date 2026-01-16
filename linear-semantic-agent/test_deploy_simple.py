
import vertexai
from vertexai.preview import reasoning_engines

class SimpleAgent:
    def set_up(self):
        pass
    def query(self, text: str):
        return f"Echo: {text}"

def deploy():
    vertexai.init(
        project="linear-semantic-agents",
        location="us-central1",
        staging_bucket="gs://linear-semantic-agents-staging"
    )
    remote_agent = reasoning_engines.ReasoningEngine.create(
        SimpleAgent(),
        display_name="Simple Test Agent",
    )
    print(f"Deployed simple agent: {remote_agent.resource_name}")

if __name__ == "__main__":
    deploy()
