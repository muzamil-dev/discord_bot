import discord # type: ignore
from discord.ext import commands # type: ignore
import random
import json
import asyncio
import dateparser # type: ignore
import time
import datetime
import requests # type: ignore
import parsedatetime # type: ignore
import os
import logging
import state # type: ignore

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

fake_addresses = config["fake_addresses"]
fake_phone_numbers = config["fake_phone_numbers"]
fake_ips = config["fake_ips"]
events = config["events"]
REMINDERS_FILE = config["REMINDERS_FILE_NAME"]
TIMERS_FILE_NAME = config["TIMERS_FILE_NAME"]

@commands.command()
async def dox(ctx, member: discord.Member = None):
    """Fake doxes a user for fun."""
    if member is None:
        await ctx.send("Vro gonna get yourself doxxed. Next time do this: `!dox @username`")
        logging.warning(f"{ctx.author} tried to use the dox command without specifying a member.")
        return

    address = random.choice(fake_addresses)
    phone = random.choice(fake_phone_numbers)
    ip = random.choice(fake_ips)

    # Log the dox command usage
    logging.info(f"{ctx.author} used the dox command on {member.display_name}. Address: {address}, Phone: {phone}, IP: {ip}")

    # Send the "dox" message
    await ctx.send(f"📁 **Dox on {member.display_name}**:\n"
                   f"🏠 Address: {address}\n"
                   f"📞 Phone: {phone}\n"
                   f"🌐 IP: {ip}\n")
    
# ---------------------------- Reminders ----------------------------
def save_reminder(reminder):
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            reminders = json.load(f)
    else:
        reminders = []

    reminders.append(reminder)
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f)
    logging.info(f"Saved reminder: {reminder}")

def remove_reminder(reminder):
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            reminders = json.load(f)
        reminders = [r for r in reminders if r != reminder]
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(reminders, f)
    logging.info(f"Removed reminder: {reminder}")

async def load_reminders(bot):
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            reminders = json.load(f)
        for reminder in reminders:
            delay = reminder['time'] - time.time()
            if delay > 0:
                bot.loop.create_task(schedule_reminder(bot, reminder, delay))
            else:
                # If the reminder time has already passed, trigger it immediately with an apology
                await schedule_reminder(bot, reminder, 0, missed=True)
    logging.info("Loaded reminders from file")

async def schedule_reminder(bot, reminder, delay, missed=False):
    if delay > 0:
        await asyncio.sleep(delay)
    channel = bot.get_channel(reminder['channel_id'])
    if missed:
        await channel.send(f"{reminder['user_mention']}, this is your reminder for {reminder['text']}. My bad vro, someone pulled the plug on me.")
        logging.info(f"Sent missed reminder: {reminder}")
    else:
        await channel.send(f"{reminder['user_mention']}, this is your reminder for {reminder['text']}")
        logging.info(f"Sent reminder: {reminder}")
    remove_reminder(reminder)

@commands.command()
async def remind(ctx, *, reminder: str):
    """Reminds the user after a specified amount of time."""
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(reminder)
    
    if parse_status == 0:
        await ctx.send("Invalid time format. Please specify a valid duration.")
        logging.warning(f"{ctx.author} provided an invalid time format: {reminder}")
        return
    
    delay = time.mktime(time_struct) - time.mktime(time.localtime())
    
    if delay <= 0:
        await ctx.send("The specified time is in the past. Please specify a future time.")
        logging.warning(f"{ctx.author} provided a past time: {reminder}")
        return

    # Extract the reminder message if provided
    reminder_parts = reminder.split(' ', 1)
    if len(reminder_parts) > 1:
        reminder_message = reminder_parts[1]
    else:
        reminder_message = ""

    reminder_data = {
        'time': time.time() + delay,
        'channel_id': ctx.channel.id,
        'user_mention': ctx.author.mention,
        'text': reminder_message
    }
    save_reminder(reminder_data)
    await ctx.send(f"Reminder set for {reminder_parts[0]}")
    logging.info(f"{ctx.author} set a reminder: {reminder_data}")
    await asyncio.sleep(delay)
    await ctx.send(f"{ctx.author.mention}, this is your reminder for {reminder_message}")
    remove_reminder(reminder_data)

@commands.command()
async def meme(ctx):
    """Sends a random meme."""
    # URL to fetch the latest hot memes from r/memes
    randomnum = random.randint(0, 1)
    if randomnum == 0:
        url = 'https://www.reddit.com/r/memes/hot/.json?limit=200'
    else:
        url = 'https://www.reddit.com/r/memes/new/.json?limit=200'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        memes = response.json()['data']['children']
        meme = random.choice(memes)['data']
        meme_url = meme['url']
        await ctx.send(meme_url)
    else:
        await ctx.send("Couldn't fetch a meme at the moment. Please try again later.")

# ----------------------------- Stopwatch  Commands -----------------------------


@commands.command()
async def toggle_chat(ctx):
    """Toggles chat mode on/off."""
    current_mode = state.get_chat_mode()
    state.set_chat_mode(not current_mode)
    await ctx.send(f"Chat mode {'enabled' if not current_mode else 'disabled'} 🎭")
    logging.info(f"{ctx.author} toggled chat mode to {'enabled' if not current_mode else 'disabled'}")
@commands.command()
async def pingreece(ctx):
    """Toggles pinging Reece on/off."""
    current_state = state.get_reece_enable()
    state.set_reece_enable(not current_state)
    await ctx.send(f"Ping Reece {'enabled' if not current_state else 'disabled'} 🎭")
    logging.info(f"{ctx.author} toggled ping Reece to {'enabled' if not current_state else 'disabled'}")

@commands.command()
async def list_events(ctx):
    """Lists all available on_message events."""
    events_list = "\n".join(events)
    await ctx.send(f"Available on_message events:\n{events_list}")

def setup(bot):
    bot.add_command(dox)
    bot.add_command(remind)
    bot.add_command(meme)
    bot.add_command(toggle_chat)
    bot.add_command(pingreece)
    bot.add_command(list_events)