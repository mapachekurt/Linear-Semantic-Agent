
import os
from typing import List, Optional
from src.agent import LinearSemanticAgent
from src.models.task import Task
from src.models.decision import Decision

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
                # We need to run this as a task or use a helper
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
