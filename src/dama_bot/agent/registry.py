import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ValidationError

from dama_bot.agent.models import ToolResult, UserContext

logger = logging.getLogger(__name__)


class Tool:
    def __init__(self, name: str, description: str, args_schema: type[BaseModel], func: Callable):
        self.name = name
        self.description = description
        self.args_schema = args_schema
        self.func = func


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, args_schema: type[BaseModel]):
        def decorator(func: Callable):
            self.tools[name] = Tool(name, description, args_schema, func)
            return func

        return decorator

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
                success=False, message=f"Parametri non validi per lo strumento '{name}': {str(e)}"
            )

        try:
            if asyncio.iscoroutinefunction(tool.func):
                result = await tool.func(args, user_context, application)
            else:
                result = tool.func(args, user_context, application)

            if not isinstance(result, ToolResult):
                raise TypeError(
                    f"Il tool '{name}' deve restituire un oggetto ToolResult, "
                    f"ricevuto {type(result)}"
                )

            return result
        except Exception as e:
            logger.exception(f"Errore durante l'esecuzione del tool {name}")
            return ToolResult(
                success=False,
                message=f"Errore imprevisto durante l'esecuzione del tool '{name}': {str(e)}",
            )
