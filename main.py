import os
import json
import asyncio
import logging  # Import logging module
import discord # type: ignore
from discord.ext import commands # type: ignore
from dotenv import load_dotenv # type: ignore

from src.utils.state_manager import get_toggle_bot
from src import setup_ready_handler, setup_message_handler, setup_all_commands
from src.commands.utility.search_command import setup_search_command  # type: ignore
from src.utils.llm import setup_llm_command # type: ignore 


# Load environment variables from the .env file inside .venv
dotenv_path = os.path.join(os.path.dirname(__file__), '.venv', '.env')
print(f"Loading .env file from: {dotenv_path}")
load_dotenv(dotenv_path)

# Print environment variables for debugging
discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
the_one_api_key = os.getenv('THE_ONE_API_KEY')

# Load config and create bot
with open('config/config.json') as config_file:
    config = json.load(config_file)

# Handle both cases where the '!' prefix is included or not included
allowed_commands = [cmd.lstrip('!') for cmd in config.get('ALLOWED_COMMANDS', [])]
print(f"Allowed commands: {allowed_commands}")

# Define bot class
class MyBot(commands.Bot):
    async def process_commands(self, message):
        ctx = await self.get_context(message)
        
        if not get_toggle_bot():
            if ctx.command and ctx.command.name not in allowed_commands:
                await message.channel.send("The bot is currently disabled. Only specific commands are allowed.")
                return
        
        await super().process_commands(message)

    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if not get_toggle_bot():
            if ctx.command and ctx.command.name not in allowed_commands:
                await message.channel.send("The bot is currently disabled. Only specific commands are allowed.")
                return
        
        await self.process_commands(message)

    def dispatch(self, event_name, *args, **kwargs):
        if not get_toggle_bot() and event_name not in ['message', 'command', 'command_error']:
            return
        super().dispatch(event_name, *args, **kwargs)

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = MyBot(command_prefix=config["COMMAND_PREFIX"], intents=intents)

# Check for The One API key
if not the_one_api_key:
    raise ValueError("The One API key is missing in .env file")

# Set up handlers and register commands
async def setup():
    await setup_all_commands(bot)
    await setup_ready_handler(bot)
    await setup_message_handler(bot)
    await setup_llm_command(bot) 
    await setup_search_command(bot)  

# Run setup and start bot
async def main():
    await setup()
    await bot.start(discord_bot_token)

asyncio.run(main())