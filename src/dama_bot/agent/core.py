import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from openai import AsyncOpenAI

from dama_bot.agent.models import AgentResponse, UserContext
from dama_bot.agent.registry import ToolRegistry
from dama_bot.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, registry: ToolRegistry):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.registry = registry

    async def handle_message(
        self, message: str, user_context: UserContext, application: Any
    ) -> AgentResponse:
        now = datetime.now(ZoneInfo("Europe/Rome"))

        system_prompt = f"""You are Dama Bot, 
a personal Telegram assistant for Dario and Manuela, 
a couple living in Italy.
Current local date and time: {now.isoformat()} (timezone: Europe/Rome).

You must help the user by using the registered tools.
- ONLY perform operations through the provided tools.
- Never claim you have performed an action unless a tool has returned success.
- If the user asks for a capability that is not supported by any tool, state clearly
  that you cannot perform it. Do not pretend or simulate it.
- Ask for clarification if required arguments (like dates/times for a reminder) are
  missing and cannot be safely inferred. Do not make up IDs or dates.
- Answer in Italian in a concise, natural, and helpful manner.
- If a date is not specified, assume that it is today. 
- If only a day of the week is specified, assume it is the next occurrence of that day.
- If not specified, assume that weeks, months and years are the current ones.
- If a time is not specified, assume that it is the next occurrence of that time.
- If you don't know the answer, say that you don't know and do not invent an answer.
- Don't ask follow up questions.
- If the command arguments are not complete, ask for clarification. And retry.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        last_tool_called = None

        # We limit the loop to 5 turns to prevent infinite execution loops
        for turn in range(5):
            tools_definitions = self.registry.get_openai_tools()
            kwargs = {}
            if tools_definitions:
                kwargs["tools"] = tools_definitions
                kwargs["tool_choice"] = "auto"

            try:
                response = await self.client.chat.completions.create(
                    model=OPENAI_MODEL, messages=messages, **kwargs
                )
            except Exception as e:
                logger.error(f"OpenAI completion error: {e}")
                return AgentResponse(
                    message=(
                        "Scusa, ho riscontrato un problema di comunicazione con il "
                        "mio modulo di intelligenza artificiale. Riprova più tardi."
                    ),
                    tool_called=last_tool_called,
                )

            message_obj = response.choices[0].message
            messages.append(message_obj.model_dump(exclude_none=True))

            if not message_obj.tool_calls:
                # The LLM generated a final text response without any tool calls.
                return AgentResponse(
                    message=message_obj.content or "", tool_called=last_tool_called
                )

            # Process tool calls
            for tool_call in message_obj.tool_calls:
                tool_name = tool_call.function.name
                tool_args_str = tool_call.function.arguments

                logger.info(
                    f"Turn {turn}: LLM requested tool '{tool_name}' with args: {tool_args_str}"
                )
                last_tool_called = tool_name

                tool_result = await self.registry.execute(
                    name=tool_name,
                    args_str=tool_args_str,
                    user_context=user_context,
                    application=application,
                )

                logger.info(
                    f"Tool '{tool_name}' result: success={tool_result.success}, "
                    f"message='{tool_result.message}'"
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result.model_dump_json(),
                    }
                )

        # If we exceeded the turn count without returning a text response, return an error
        return AgentResponse(
            message=(
                "Scusa, l'operazione ha richiesto troppi passaggi e non è stato "
                "possibile completarla."
            ),
            tool_called=last_tool_called,
        )
