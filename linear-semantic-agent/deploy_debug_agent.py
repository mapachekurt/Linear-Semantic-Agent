
import os
import vertexai
from vertexai.preview import reasoning_engines
from google.cloud import firestore
import google.auth

class DebugAgent:
    def set_up(self):
        pass
        
    def query(self, text: str):
        try:
            credentials, project = google.auth.default()
            identity = getattr(credentials, 'service_account_email', 'unknown')
            
            db = firestore.Client(project="linear-semantic-agents")
            collections = [c.id for c in db.collections()]
            
            return {
                "identity": identity,
                "project": project,
                "collections": collections,
                "env": dict(os.environ)
            }
        except Exception as e:
            import traceback
            return {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "identity": identity if 'identity' in locals() else 'unknown'
            }

def deploy():
    vertexai.init(
        project="linear-semantic-agents",
        location="us-central1",
        staging_bucket="gs://linear-semantic-agents-staging"
    )
    
    remote_agent = reasoning_engines.ReasoningEngine.create(
        DebugAgent(),
        display_name="Debug Identity Agent",
        requirements=["google-cloud-firestore", "google-auth"]
    )
    print(f"Deployed debug agent: {remote_agent.resource_name}")

if __name__ == "__main__":
    deploy()
