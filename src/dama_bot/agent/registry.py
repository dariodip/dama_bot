import json
import logging
from typing import Any

from pydantic import ValidationError

from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.plugin import Tool

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_openai_tools(self) -> list[dict]:
        res = []
        for tool in self.tools.values():
            res.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.args_schema.model_json_schema(),
                    },
                }
            )
        return res

    def get_tools(self) -> dict[str, str]:
        return {tool.name: tool.description for tool in self.tools.values()}

    async def execute(
        self, name: str, args_str: str, user_context: UserContext, application: Any
    ) -> ToolResult:
        if name not in self.tools:
            return ToolResult(success=False, message=f"Strumento '{name}' non trovato.")

        tool = self.tools[name]
        try:
            args_dict = json.loads(args_str)
            args = tool.args_schema(**args_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            return ToolResult(
                success=False, message=f"Invalid arguments for tool '{name}': {str(e)}"
            )

        try:
            result = await tool.execute(args, user_context, application)

            if not isinstance(result, ToolResult):
                raise TypeError(
                    f"The tool '{name}' must return a ToolResult object, got {type(result)}"
                )

            return result
        except Exception as e:
            logger.exception(f"Unexpected error while executing tool '{name}': {str(e)}")
            return ToolResult(
                success=False,
                message=f"Unexpected error while executing tool '{name}': {str(e)}",
            )
