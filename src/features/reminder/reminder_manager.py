import json
import time
import asyncio
import logging
from src.utils import send_message_with_retry # type: ignore

reminders = []

async def load_reminders(bot):
    with open('config/config.json') as config_file:
        config = json.load(config_file)
        
    reminders_file = config["REMINDERS_FILE_NAME"]
    
    try:
        with open(f'config/{reminders_file}', 'r') as f:
            reminders = json.load(f)
            for reminder in reminders:
                delay = reminder['time'] - time.time()
                if delay > 0:
                    bot.loop.create_task(schedule_reminder(bot, reminder, delay))
                else:
                    await schedule_reminder(bot, reminder, 0, missed=True)
        logging.info("Loaded reminders from file")
    except FileNotFoundError:
        logging.info("No reminders file found")
        return []

def save_reminder(reminder):
    with open('config/config.json') as config_file:
        config = json.load(config_file)
    
    reminders_file = config["REMINDERS_FILE_NAME"]
    
    try:
        with open(f'config/{reminders_file}', 'r') as f:
            reminders = json.load(f)
    except FileNotFoundError:
        reminders = []
    
    reminders.append(reminder)
    with open(f'config/{reminders_file}', 'w') as f:
        json.dump(reminders, f)
    logging.info(f"Saved reminder: {reminder}")

def remove_reminder(reminder):
    with open('config/config.json') as config_file:
        config = json.load(config_file)
    
    reminders_file = config["REMINDERS_FILE_NAME"]
    
    try:
        with open(f'config/{reminders_file}', 'r') as f:
            reminders = json.load(f)
        reminders = [r for r in reminders if r != reminder]
        with open(f'config/{reminders_file}', 'w') as f:
            json.dump(reminders, f)
        logging.info(f"Removed reminder: {reminder}")
    except FileNotFoundError:
        logging.error("No reminders file found when trying to remove reminder")

async def schedule_reminder(bot, reminder, delay, missed=False):
    if delay > 0:
        await asyncio.sleep(delay)
    
    channel = bot.get_channel(reminder['channel_id'])
    if missed:
        await send_message_with_retry(channel, 
            f"{reminder['user_mention']}, this is your reminder for {reminder['text']}. "
            "My bad vro, someone pulled the plug on me.")
        logging.info(f"Sent missed reminder: {reminder}")
    else:
        await send_message_with_retry(channel, 
            f"{reminder['user_mention']}, this is your reminder for {reminder['text']}")
        logging.info(f"Sent reminder: {reminder}")
    
    remove_reminder(reminder)

def get_user_reminders(user_id):
    with open('config/config.json') as config_file:
        config = json.load(config_file)
    
    reminders_file = config["REMINDERS_FILE_NAME"]
    
    try:
        with open(f'config/{reminders_file}', 'r') as f:
            reminders = json.load(f)
        user_reminders = [reminder for reminder in reminders if reminder.get('user_id') == user_id]
        return user_reminders
    except FileNotFoundError:
        return []