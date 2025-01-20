import logging
from src.features.reminder.reminder_manager import load_reminders # type: ignore

async def setup_ready_handler(bot):
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        await load_reminders(bot)
        logging.info(f'Bot is ready and logged in as {bot.user}')
