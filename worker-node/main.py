"""
NEXUS-AI Distributed Grid (NADG) - Worker Node
============================================================
Purpose: Execute tasks received from the Master Orchestrator
Stack: FastAPI + Python subprocess execution
============================================================
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import subprocess
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load authentication token from environment
NADG_AUTH_TOKEN = os.environ.get('NADG_AUTH_TOKEN', '')

# Log authentication status once at startup
if not NADG_AUTH_TOKEN:
    logging.warning("NADG_AUTH_TOKEN not configured - authentication disabled (insecure)")

app = FastAPI(
    title="NADG Worker Node",
    description="Worker node for NEXUS-AI Distributed Grid",
    version="1.0.0"
)


def verify_auth_token(x_nadg_auth: str = Header(None)):
    """
    FastAPI dependency to verify the X-NADG-AUTH header.
    Returns 401 Unauthorized if the header is missing or invalid.
    """
    if not NADG_AUTH_TOKEN:
        # If no token is configured, skip authentication (for backward compatibility)
        return True
    
    if x_nadg_auth is None:
        logger.error("Missing X-NADG-AUTH header")
        raise HTTPException(
            status_code=401,
            detail="Missing X-NADG-AUTH header"
        )
    
    if x_nadg_auth != NADG_AUTH_TOKEN:
        logger.error("Invalid X-NADG-AUTH token")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
    return True


class TaskRequest(BaseModel):
    task: str
    task_id: int = 0
    timeout: int = 30


class TaskResponse(BaseModel):
    task_id: int
    status: str
    output: str
    error: str = ""
    executed_at: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "NADG Worker Node",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "uptime": "running",
        "worker_id": os.environ.get("WORKER_ID", "unknown"),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/execute", response_model=TaskResponse)
async def execute_task(task_request: TaskRequest, authenticated: bool = Depends(verify_auth_token)):
    """
    Execute a task received from the master orchestrator.
    The task is executed as Python code in a subprocess.
    Note: In a production environment, implement proper sandboxing and input validation.
    """
    logger.info(f"Received task {task_request.task_id}: {task_request.task}")
    
    try:
        # For security, we'll execute Python code instead of arbitrary shell commands
        # In a production environment, you'd want more sophisticated sandboxing
        
        # Prepare the task execution
        result = subprocess.run(
            ["python3", "-c", task_request.task],
            capture_output=True,
            text=True,
            timeout=task_request.timeout
        )
        
        response = TaskResponse(
            task_id=task_request.task_id,
            status="completed" if result.returncode == 0 else "failed",
            output=result.stdout,
            error=result.stderr,
            executed_at=datetime.now().isoformat()
        )
        
        logger.info(f"Task {task_request.task_id} completed with status: {response.status}")
        return response
        
    except subprocess.TimeoutExpired:
        logger.error(f"Task {task_request.task_id} timed out")
        raise HTTPException(
            status_code=408,
            detail=f"Task execution timed out after {task_request.timeout} seconds"
        )
    except Exception as e:
        logger.error(f"Task {task_request.task_id} failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )


@app.post("/execute-python")
async def execute_python_task(task_request: TaskRequest, authenticated: bool = Depends(verify_auth_token)):
    """
    Execute a Python task in a more controlled manner.
    This endpoint is specifically for Python code execution.
    """
    logger.info(f"Received Python task {task_request.task_id}")
    
    try:
        # Execute Python code
        result = subprocess.run(
            ["python3", "-c", task_request.task],
            capture_output=True,
            text=True,
            timeout=task_request.timeout,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        return {
            "task_id": task_request.task_id,
            "status": "completed" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode,
            "executed_at": datetime.now().isoformat()
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail=f"Task execution timed out after {task_request.timeout} seconds"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )


@app.get("/status")
async def get_status():
    """Get current worker status"""
    return {
        "status": "active",
        "worker_id": os.environ.get("WORKER_ID", "unknown"),
        "capabilities": ["python", "subprocess"],
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
