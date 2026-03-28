"""
Pydantic models for A2A Protocol (JSON-RPC 2.0)

Unified Business Agent - Team Sleepyhead
Nasiko Hackathon 2026
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Request Models
# =============================================================================


class MessagePart(BaseModel):
    """Part of a message (can be text, image, file, etc.)"""

    kind: str  # text, image, file, etc.
    text: Optional[str] = None
    data: Optional[str] = None  # Base64 encoded data for images/files
    mimeType: Optional[str] = None
    url: Optional[str] = None


class Message(BaseModel):
    """User or assistant message"""

    role: str  # user, assistant, system
    parts: List[MessagePart]
    messageId: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


class MessageParams(BaseModel):
    """Parameters for message/send method"""

    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    message: Message
    context: Optional[Dict[str, Any]] = None


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request"""

    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    method: str  # message/send, agent/capabilities, etc.
    params: MessageParams


# =============================================================================
# Response Models
# =============================================================================


class ArtifactPart(BaseModel):
    """Part of an artifact (response component)"""

    kind: str = "text"  # text, code, image, file, etc.
    text: Optional[str] = None
    data: Optional[str] = None
    mimeType: Optional[str] = None
    language: Optional[str] = None  # For code artifacts


class Artifact(BaseModel):
    """Response artifact containing the agent's output"""

    artifactId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parts: List[ArtifactPart]
    metadata: Optional[Dict[str, Any]] = None


class HistoryItem(BaseModel):
    """Conversation history item"""

    contextId: str
    kind: str = "message"
    messageId: str
    role: str
    parts: List[MessagePart]
    taskId: Optional[str] = None
    timestamp: Optional[str] = None


class TaskStatus(BaseModel):
    """Task execution status"""

    state: str  # pending, in_progress, completed, failed, cancelled
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    error: Optional[str] = None
    progress: Optional[float] = None  # 0.0 to 1.0


class TaskResult(BaseModel):
    """Result from task execution"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kind: str = "task"
    status: TaskStatus
    artifacts: List[Artifact] = []
    history: Optional[List[HistoryItem]] = []
    contextId: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    sessionId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response"""

    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    result: TaskResult


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 Error"""

    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCErrorResponse(BaseModel):
    """JSON-RPC 2.0 Error Response"""

    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    error: JSONRPCError


# =============================================================================
# Helper Functions
# =============================================================================


def create_text_artifact(text: str, metadata: Optional[Dict[str, Any]] = None) -> Artifact:
    """Create a simple text artifact"""
    return Artifact(
        parts=[ArtifactPart(kind="text", text=text)],
        metadata=metadata or {},
    )


def create_error_response(request_id: str, code: int, message: str, data: Any = None) -> JSONRPCErrorResponse:
    """Create a JSON-RPC error response"""
    return JSONRPCErrorResponse(
        id=request_id,
        error=JSONRPCError(code=code, message=message, data=data),
    )


def create_success_response(
    request_id: str,
    text: str,
    session_id: Optional[str] = None,
    history: Optional[List[HistoryItem]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> JSONRPCResponse:
    """Create a successful JSON-RPC response"""
    task_id = str(uuid.uuid4())
    context_id = str(uuid.uuid4())

    return JSONRPCResponse(
        id=request_id,
        result=TaskResult(
            id=task_id,
            kind="task",
            status=TaskStatus(state="completed"),
            artifacts=[create_text_artifact(text, metadata)],
            history=history or [],
            contextId=context_id,
            sessionId=session_id,
            metadata=metadata or {},
        ),
    )


# =============================================================================
# Error Codes (JSON-RPC 2.0 Standard + Custom)
# =============================================================================

ERROR_PARSE_ERROR = -32700  # Invalid JSON
ERROR_INVALID_REQUEST = -32600  # Invalid Request object
ERROR_METHOD_NOT_FOUND = -32601  # Method does not exist
ERROR_INVALID_PARAMS = -32602  # Invalid method parameters
ERROR_INTERNAL_ERROR = -32603  # Internal JSON-RPC error

# Custom error codes (application-specific)
ERROR_AGENT_ERROR = -32000  # General agent error
ERROR_TOOL_ERROR = -32001  # Tool execution error
ERROR_MODULE_ERROR = -32002  # Module execution error
ERROR_DATABASE_ERROR = -32003  # Database operation error
ERROR_EXTERNAL_API_ERROR = -32004  # External API call failed
ERROR_VALIDATION_ERROR = -32005  # Input validation failed
ERROR_TIMEOUT_ERROR = -32006  # Operation timed out
ERROR_RATE_LIMIT_ERROR = -32007  # Rate limit exceeded
