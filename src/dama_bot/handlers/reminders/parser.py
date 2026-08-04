from zoneinfo import ZoneInfo
from datetime import datetime
from openai import AsyncOpenAI
from zoneinfo import ZoneInfo

from dama_bot.config import OPENAI_API_KEY, OPENAI_MODEL
from .models import Reminder

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)

rome = ZoneInfo("Europe/Rome")

async def parse_reminder(message: str) -> Reminder:
    now = datetime.now(ZoneInfo("Europe/Rome"))

    response = await client.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system",
            "content": f"""
You are a reminder parser.

Current date and time:
{now}

Extract:
- what needs to be remembered
- when it needs to be remembered

If the user does not specify a date, assign a default date 24 hours after the current moment.

Respond only with a JSON in the following format:
- text: "reminder text"
- remind_at: "YYYY-MM-DDTHH:MM:SS"

The user timezone is Europe/Rome.

Extract the reminder date and time.

Return remind_at as a naive datetime.
Do not convert it to UTC.
Do not add timezone information.
""",
            },
            {"role": "user", "content": message}
        ],
        response_format=Reminder,
    )

    reminder = response.choices[0].message.parsed
    reminder.remind_at = reminder.remind_at.replace(tzinfo=rome)

    return reminder

