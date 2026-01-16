"""
Agent entry point and FastAPI application.
Handles requests, routes to agent, returns A2A protocol responses.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from src.agent import LinearSemanticAgent
from src.models.task import TaskRequest
from src.models.decision import AgentResponse
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Global agent instance
agent: LinearSemanticAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global agent

    # Startup
    logger.info("Starting Linear Semantic Agent API")
    try:
        agent = LinearSemanticAgent()
        await agent.initialize()
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize agent", error=str(e), exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Linear Semantic Agent API")


# Create FastAPI app
app = FastAPI(
    title="Linear Semantic Agent",
    description="AI agent for validating and categorizing Linear tasks for mapache.app",
    version=settings.agent_version,
    lifespan=lifespan
)


@app.post("/evaluate-task", response_model=AgentResponse)
async def evaluate_task(request: TaskRequest) -> AgentResponse:
    """
    Evaluate a task and return decision.

    Args:
        request: Task evaluation request

    Returns:
        Agent decision and reasoning
    """
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    logger.info(
        "Received evaluation request",
        task_id=request.task_id,
        source=request.source
    )

    start_time = time.time()

    try:
        # Convert request to task
        task = request.to_task()

        # Evaluate
        decision = await agent.evaluate_task(task)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Create response
        response = AgentResponse.from_decision(decision, processing_time_ms)

        logger.info(
            "Evaluation complete",
            task_id=request.task_id,
            decision=response.decision.value,
            confidence=response.confidence,
            processing_time_ms=processing_time_ms
        )

        return response

    except Exception as e:
        logger.error(
            "Evaluation failed",
            task_id=request.task_id,
            error=str(e),
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    if agent is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "reason": "Agent not initialized"}
        )

    try:
        health = await agent.get_agent_health()
        return {
            "status": "healthy",
            "agent": health,
            "environment": settings.environment,
            "version": settings.agent_version
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/live")
async def liveness_probe():
    """
    Liveness probe for Kubernetes.

    Returns:
        200 if alive
    """
    return {"status": "alive"}


@app.get("/ready")
async def readiness_probe():
    """
    Readiness probe for Kubernetes.

    Returns:
        200 if ready to accept requests
    """
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not ready"
        )

    return {"status": "ready"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Linear Semantic Agent",
        "version": settings.agent_version,
        "description": "AI agent for validating and categorizing Linear tasks for mapache.app",
        "endpoints": {
            "evaluate": "/evaluate-task",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns:
        Metrics in Prometheus format
    """
    # Simplified metrics implementation
    # In production, use prometheus_client library

    if agent is None:
        return ""

    try:
        health = await agent.get_agent_health()

        metrics_text = f"""
# HELP agent_projects_total Total number of cached projects
# TYPE agent_projects_total gauge
agent_projects_total {health.get('projects_count', 0)}

# HELP agent_cache_valid Is the projects cache valid
# TYPE agent_cache_valid gauge
agent_cache_valid {1 if health.get('cache_valid') else 0}

# HELP agent_version Agent version info
# TYPE agent_version gauge
agent_version{{version="{settings.agent_version}"}} 1
"""
        return metrics_text.strip()

    except Exception as e:
        logger.error("Metrics generation failed", error=str(e), exc_info=True)
        return ""


# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )
