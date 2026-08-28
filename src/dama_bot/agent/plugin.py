from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel

from dama_bot.agent.models import ToolResult, UserContext


@runtime_checkable
class Tool(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def args_schema(self) -> type[BaseModel]: ...

    async def execute(
        self, args: Any, user_context: UserContext, application: Any
    ) -> ToolResult: ...


@runtime_checkable
class Plugin(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    def get_tools(self) -> list[Tool]: ...

    async def on_start(self, application: Any) -> None:
        """Optional hook called when the bot starts."""
        ...


class FunctionTool:
    def __init__(self, name: str, description: str, args_schema: type[BaseModel], func: Callable):
        self._name = name
        self._description = description
        self._args_schema = args_schema
        self._func = func

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def args_schema(self) -> type[BaseModel]:
        return self._args_schema

    async def execute(self, args: Any, user_context: UserContext, application: Any) -> ToolResult:
        import asyncio

        if asyncio.iscoroutinefunction(self._func):
            return await self._func(args, user_context, application)
        else:
            return self._func(args, user_context, application)
