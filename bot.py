import discord
from discord.ext import commands

# Intents are required to access certain events
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

# insert token here
bot.run('YOUR_TOKEN')
