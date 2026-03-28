import logging
import uuid
import click
import uvicorn
from datetime import datetime
from typing import List, Optional, Any, Dict, Union, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from agent import Agent
from models import JsonRpcRequest, JsonRpcResponse, Message, Task, TaskStatus, Artifact, ArtifactPart

# Setup logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hr-agent")

app = FastAPI(
    title="HR Agent API",
    description="AI-powered HR assistant with modular architecture",
    version="1.0.0"
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent (singleton pattern)
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    global agent
    logger.info("Starting HR Agent service...")
    agent = Agent()
    logger.info("✅ HR Agent service ready")

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "HR Agent - Agents of Chaos",
        "version": "1.0.0",
        "agent_ready": agent is not None
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/")
async def handle_rpc(request: Request):
    """Handle JSON-RPC requests."""
    
    if agent is None:
        return {
            "jsonrpc": "2.0",
            "id": "error",
            "error": {
                "code": -32603,
                "message": "Agent not initialized"
            }
        }
    
    try:
        # Parse JSON body
        body = await request.json()
        
        # Validate with Pydantic
        rpc_request = JsonRpcRequest(**body)
        
        if rpc_request.method == "message/send":
            try:
                # 1. Parse Input
                user_message = rpc_request.params.message
                session_id = rpc_request.params.session_id
                
                # Extract text
                input_text = ""
                for part in user_message.parts:
                    if part.kind == "text" and part.text:
                        input_text += part.text
                
                logger.info(f"Received message: {input_text[:100]}... (Session: {session_id})")
                
                # 2. Invoke Agent Logic
                response_text = agent.process_message(input_text)
                
                # 3. Construct Response
                task_id = str(uuid.uuid4())
                context_id = session_id if session_id else str(uuid.uuid4())
                
                artifact = Artifact(
                    parts=[ArtifactPart(text=response_text)]
                )
                
                task = Task(
                    id=task_id,
                    status=TaskStatus(
                        state="completed",
                        timestamp=datetime.now().isoformat()
                    ),
                    artifacts=[artifact],
                    contextId=context_id
                )
                
                response = JsonRpcResponse(
                    id=rpc_request.id,
                    result=task
                )
                
                return response.model_dump()
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                return {
                    "jsonrpc": "2.0",
                    "id": rpc_request.id,
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": rpc_request.id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {rpc_request.method}"
                }
            }
    
    except Exception as e:
        logger.error(f"Error parsing request: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": "error",
            "error": {
                "code": -32700,
                "message": "Parse error",
                "data": str(e)
            }
        }

if __name__ == "__main__":
    @click.command()
    @click.option('--host', 'host', default='0.0.0.0', help='Host to bind to')
    @click.option('--port', 'port', default=5000, help='Port to bind to')
    def main(host: str, port: int):
        """Start the HR Agent server."""
        logger.info(f"Starting server on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")

    main()
