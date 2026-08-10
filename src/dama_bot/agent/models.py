from typing import Any

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    user_id: int
    chat_id: int
    username: str | None = None


class ToolResult(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    message: str
    tool_called: str | None = None
