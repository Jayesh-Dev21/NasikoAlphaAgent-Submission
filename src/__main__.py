"""
FastAPI server for Unified Business Agent (A2A Protocol / JSON-RPC 2.0)

Team Sleepyhead - Nasiko Hackathon 2026
"""

import logging
import uuid
import click
import uvicorn
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.agent import Agent
from src.utils.database import get_storage_debug_info
from src.models import (
    JSONRPCRequest,
    create_error_response,
    create_success_response,
    ERROR_PARSE_ERROR,
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_INTERNAL_ERROR,
)

# Setup logging with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/agent.log', mode='a')
    ]
)
logger = logging.getLogger("prathamai-agent")

# FastAPI application
app = FastAPI(
    title="Unified Business Agent API",
    description="Multi-domain AI agent for customer service, data analytics, and finance/accounting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (singleton pattern)
agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize agent and dependencies on startup."""
    global agent
    
    logger.info("=" * 80)
    logger.info("Starting Unified Business Agent service...")
    logger.info("Team: Sleepyhead | Hackathon: Nasiko 2026")
    logger.info("=" * 80)
    
    try:
        # Initialize the agent
        agent = Agent()
        logger.info("✅ Agent initialized successfully")
        logger.info("✅ Unified Business Agent service ready")
        logger.info(f"✅ Server listening for JSON-RPC 2.0 requests")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Unified Business Agent service...")
    # Add any cleanup logic here (close DB connections, etc.)
    logger.info("✅ Shutdown complete")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Unified Business Agent",
        "team": "Sleepyhead",
        "hackathon": "Nasiko 2026",
        "version": "1.0.0",
        "status": "running",
        "agent_ready": agent is not None,
        "protocol": "A2A (JSON-RPC 2.0)",
        "domains": [
            "customer_service",
            "data_analytics",
            "finance_accounting",
            "scheduling",
            "document_processing"
        ],
        "endpoints": {
            "rpc": "POST /",
            "health": "GET /health",
            "docs": "GET /docs",
            "debug_storage": "GET /debug/storage"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    if agent is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "reason": "Agent not initialized"
            }
        )
    
    return {
        "status": "healthy",
        "service": "prathamai-agent",
        "timestamp": datetime.now().isoformat(),
        "agent_initialized": True
    }


@app.get("/debug/storage")
async def debug_storage():
    """Return active storage backend and configuration hints."""
    try:
        return {
            "status": "ok",
            "storage": get_storage_debug_info(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to collect storage debug info: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to collect storage debug info",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )


@app.post("/")
async def handle_json_rpc(request: Request):
    """
    Handle JSON-RPC 2.0 requests (A2A Protocol).
    
    Supports:
    - message/send: Process user messages and return agent responses
    - task/status: Check task execution status (future)
    """
    
    # Check if agent is initialized
    if agent is None:
        return {
            "jsonrpc": "2.0",
            "id": "error",
            "error": {
                "code": ERROR_INTERNAL_ERROR,
                "message": "Agent not initialized"
            }
        }
    
    rpc_id = "error"

    try:
        # Parse JSON body
        body = await request.json()
        logger.debug(f"Received request: {body}")
        rpc_id = str(body.get("id", "error"))
        
        # Validate with Pydantic (strict JSON-RPC 2.0 validation)
        rpc_request = JSONRPCRequest(**body)
        
        # Route by method
        request_id = rpc_request.id or str(uuid.uuid4())

        if rpc_request.method == "message/send":
            return await handle_message_send(rpc_request)
        
        elif rpc_request.method == "task/status":
            # Future: implement task status checking
            return create_error_response(
                request_id,
                ERROR_METHOD_NOT_FOUND,
                "Method not implemented yet: task/status"
            ).model_dump()
        
        else:
            # Method not found
            logger.warning(f"Unknown method requested: {rpc_request.method}")
            return create_error_response(
                request_id,
                ERROR_METHOD_NOT_FOUND,
                f"Method not found: {rpc_request.method}"
            ).model_dump()
    
    except ValueError as e:
        # Pydantic validation error (invalid request structure)
        logger.error(f"Invalid request format: {e}")
        return create_error_response(
            rpc_id,
            ERROR_INVALID_REQUEST,
            "Invalid request structure",
            str(e),
        ).model_dump()
    
    except Exception as e:
        # Parse error or other unexpected errors
        logger.error(f"Error parsing request: {e}", exc_info=True)
        return create_error_response(
            rpc_id,
            ERROR_PARSE_ERROR,
            "Parse error",
            str(e),
        ).model_dump()


async def handle_message_send(rpc_request: JSONRPCRequest) -> Dict[str, Any]:
    """
    Handle message/send method.
    
    Flow:
    1. Extract user message text from parts
    2. Pass to agent for processing
    3. Construct A2A protocol response with artifacts
    """
    
    request_id = rpc_request.id or str(uuid.uuid4())

    if agent is None:
        return create_error_response(
            request_id,
            ERROR_INTERNAL_ERROR,
            "Agent not initialized",
        ).model_dump()

    try:
        storage_info = get_storage_debug_info()
        response_metadata = {
            "storage": {
                "active_backend": storage_info.get("active_backend", "unknown"),
                "connected": storage_info.get("connected", False),
            }
        }

        # 1. Extract Input
        user_message = rpc_request.params.message
        session_id = rpc_request.params.session_id or str(uuid.uuid4())
        context = rpc_request.params.context or {}
        
        # Extract text from message parts
        input_text = ""
        for part in user_message.parts:
            if part.kind == "text" and part.text:
                input_text += part.text
        
        if not input_text.strip():
            logger.warning("Empty message received")
            return create_error_response(
                request_id,
                ERROR_INVALID_REQUEST,
                "Empty message - no text content found"
            ).model_dump()

        # Deterministic network-safe capability response (bypasses LLM).
        normalized = input_text.strip().lower()
        if normalized in {
            "what can you help me with?",
            "what can you help me with",
            "help",
            "capabilities",
            "what can you do",
            "what can you do?",
            "summarize what you can do in one sentence.",
            "summarize what you can do in one sentence",
        }:
            response_text = (
                "I can help across five business areas: "
                "(1) customer support tickets and sentiment analysis, "
                "(2) data analytics for CSV/Excel/JSON datasets, "
                "(3) finance tasks like expenses, invoice OCR, and budget checks, "
                "(4) scheduling meetings and finding time slots, and "
                "(5) document OCR and extraction. "
                "You can ask me for single tasks or end-to-end multi-step workflows."
            )
            response = create_success_response(
                request_id=request_id,
                text=response_text,
                session_id=session_id,
                metadata=response_metadata,
            )
            return response.model_dump()
        
        logger.info(f"Processing message (Session: {session_id}): {input_text[:100]}...")
        
        # 2. Process with Agent
        response_text = agent.process_message(
            input_text=input_text,
            session_id=session_id,
            context=context
        )
        
        logger.info(f"Agent response generated: {response_text[:100]}...")
        
        # 3. Construct JSON-RPC Response
        response = create_success_response(
            request_id=request_id,
            text=response_text,
            session_id=session_id,
            metadata=response_metadata,
        )
        
        return response.model_dump()
    
    except Exception as e:
        # Internal error during message processing
        logger.error(f"Error processing message: {e}", exc_info=True)
        return create_error_response(
            request_id,
            ERROR_INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        ).model_dump()


# CLI Entry Point
if __name__ == "__main__":
    @click.command()
    @click.option('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    @click.option('--port', default=5000, help='Port to bind to (default: 5000)')
    @click.option('--reload', is_flag=True, help='Enable auto-reload for development')
    def main(host: str, port: int, reload: bool):
        """
        Start the Unified Business Agent server.
        
        Examples:
            python -m src --host 0.0.0.0 --port 5000
            python -m src --reload  # Development mode with auto-reload
        """
        logger.info(f"Starting server on {host}:{port}")
        if reload:
            logger.info("Auto-reload enabled (development mode)")
        
        uvicorn.run(
            "src.__main__:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    
    main()
