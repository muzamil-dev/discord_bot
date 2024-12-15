import discord
from discord.ext import commands

# Intents are required to access certain events
intents = discord.Intents.default()
intents.messages = True  # Enable message intents to listen to messages
intents.message_content = True  # Required to read message content

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Event: When the bot is logged in and ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Event: Respond to specific keywords
@bot.event
async def on_message(message):
    # Avoid responding to the bot's own messages
    if message.author == bot.user:
        return

    # Respond if "hello" is mentioned
    if "hello" in message.content.lower():
        await message.channel.send('Hello!')

    # Respond if "outside" is mentioned
    if "outside" in message.content.lower():
        await message.channel.send("I'm a programmer I don't get to go outside, go touch some grass.")

    # Process commands if they are used
    await bot.process_commands(message)

# Insert your bot token
bot.run('YOUR_BOT_TOKEN')
