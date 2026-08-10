from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, Field

from dama_bot.agent.core import Agent
from dama_bot.agent.models import ToolResult, UserContext
from dama_bot.agent.registry import ToolRegistry


# Dummy args model for testing
class DummyArgs(BaseModel):
    value: str = Field(..., description="A dummy string")


@pytest.fixture
def registry():
    return ToolRegistry()


def test_tool_registry_registration(registry):
    @registry.register(
        name="dummy.tool", description="A dummy tool for testing", args_schema=DummyArgs
    )
    def dummy_func(args, user_context, application):
        return ToolResult(success=True, message=f"Got {args.value}")

    assert "dummy.tool" in registry.tools
    tool = registry.tools["dummy.tool"]
    assert tool.description == "A dummy tool for testing"
    assert tool.args_schema == DummyArgs


@pytest.mark.asyncio
async def test_tool_registry_execution_success(registry):
    @registry.register(name="dummy.tool", description="Desc", args_schema=DummyArgs)
    async def dummy_func(args, user_context, application):
        return ToolResult(success=True, message=f"Value: {args.value}")

    ctx = UserContext(user_id=1, chat_id=2)
    res = await registry.execute("dummy.tool", '{"value": "hello"}', ctx, None)

    assert res.success is True
    assert res.message == "Value: hello"


@pytest.mark.asyncio
async def test_tool_registry_invalid_args(registry):
    @registry.register(name="dummy.tool", description="Desc", args_schema=DummyArgs)
    def dummy_func(args, user_context, application):
        return ToolResult(success=True, message="ok")

    ctx = UserContext(user_id=1, chat_id=2)
    # Missing required 'value' key
    res = await registry.execute("dummy.tool", "{}", ctx, None)
    assert res.success is False
    assert "Parametri non validi" in res.message


@pytest.mark.asyncio
async def test_agent_handle_message_no_tool(mocker, registry):
    # Mock OpenAI client
    mock_openai = MagicMock()
    mocker.patch("dama_bot.agent.core.AsyncOpenAI", return_value=mock_openai)

    # Mock completion response
    mock_choice = MagicMock()
    mock_choice.message.content = "Ciao! Come posso aiutarti oggi?"
    mock_choice.message.tool_calls = None

    mock_completions = AsyncMock()
    mock_completions.create.return_value = MagicMock(choices=[mock_choice])
    mock_openai.chat.completions = mock_completions

    agent = Agent(registry)
    ctx = UserContext(user_id=1, chat_id=2)

    response = await agent.handle_message("Ciao", ctx, None)

    assert response.message == "Ciao! Come posso aiutarti oggi?"
    assert response.tool_called is None
    mock_completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_agent_handle_message_with_tool_call(mocker, registry):
    # Register a tool
    @registry.register(name="test.tool", description="Test tool", args_schema=DummyArgs)
    async def dummy_tool(args, user_context, application):
        return ToolResult(success=True, message=f"Tool success: {args.value}")

    mock_openai = MagicMock()
    mocker.patch("dama_bot.agent.core.AsyncOpenAI", return_value=mock_openai)

    # First turn response: request a tool call
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_abc123"
    mock_tool_call.function.name = "test.tool"
    mock_tool_call.function.arguments = '{"value": "work"}'

    mock_message_1 = MagicMock()
    mock_message_1.content = None
    mock_message_1.tool_calls = [mock_tool_call]
    mock_message_1.model_dump.return_value = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "call_abc123",
                "type": "function",
                "function": {"name": "test.tool", "arguments": '{"value": "work"}'},
            }
        ],
    }

    # Second turn response: final text response
    mock_message_2 = MagicMock()
    mock_message_2.content = "Ho eseguito lo strumento per il lavoro."
    mock_message_2.tool_calls = None
    mock_message_2.model_dump.return_value = {
        "role": "assistant",
        "content": "Ho eseguito lo strumento per il lavoro.",
    }

    mock_completions = AsyncMock()
    # Configure it to return first message on first call, second on second call
    mock_completions.create.side_effect = [
        MagicMock(choices=[mock_choice_1])
        for mock_choice_1 in [MagicMock(message=mock_message_1), MagicMock(message=mock_message_2)]
    ]
    mock_openai.chat.completions = mock_completions

    agent = Agent(registry)
    ctx = UserContext(user_id=1, chat_id=2)

    response = await agent.handle_message("Fai quella cosa", ctx, None)

    assert response.message == "Ho eseguito lo strumento per il lavoro."
    assert response.tool_called == "test.tool"
    assert mock_completions.create.call_count == 2
