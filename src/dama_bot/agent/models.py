from typing import Any
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    message: str
    tool_called: str | None = None

class CreateReminderArgs(BaseModel):
    text: str = Field(..., description="Description of the reminder")
    remind_at: str = Field(..., description="Date and time when the user should be reminded")
