import discord
from discord.ext import commands
import random  # For random selection of GIFs

# Intents are required to access certain events
intents = discord.Intents.default()
intents.messages = True  # Enable message intents to listen to messages
intents.message_content = True  # Required to read message content

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Predefined list of GIF URLs (you can add more URLs here)
gif_urls = [
    "https://tenor.com/view/cat-kitty-running-playing-having-fun-gif-26860048",  # Example GIF 1
    "https://tenor.com/view/yugioh-trap-card-trap-triggered-gif-12909225702038116",
    "/92ed8607219601e3.png"
]

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

    # Respond with a random GIF if "react" is mentioned
    if "react" in message.content.lower():
        random_gif = random.choice(gif_urls)  # Pick a random GIF from the list
        await message.channel.send(random_gif)

    # Process commands if they are used
    await bot.process_commands(message)

# Insert your bot token
bot.run('')
