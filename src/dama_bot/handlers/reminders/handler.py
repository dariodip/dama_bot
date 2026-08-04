from dama_bot.handlers.reminders.scheduler import schedule_reminder
from dama_bot.handlers.reminders.models import Reminder
from telegram import Update
from telegram.ext import ContextTypes

from .service import create_reminder
from .parser import parse_reminder

async def remind(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
): 
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "Uso: /remind descrizione del promemoria"
        )
        return
    
    reminder = await parse_reminder(text)

    user_id=update.effective_user.id
    chat_id=update.effective_chat.id
    username=update.effective_user.username
    
    saved = create_reminder(reminder, chat_id, user_id, username)
    print(saved)
    schedule_reminder(context.application, saved)

    await update.message.reply_text(_get_message(reminder, username))

def _get_message(reminder: Reminder, username: str) -> str:
    return f"""
✅ Promemoria creato da @{username}

📝 {reminder.text}

⏰ {reminder.remind_at}
"""