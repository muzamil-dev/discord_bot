import discord
from discord.ext import commands
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import random  # For random selection of GIFs and images

# Intents are required to access certain events
intents = discord.Intents.default()
intents.messages = True  # Enable message intents to listen to messages
intents.message_content = True  # Required to read message content
intents.guilds = True  # Required to access guild information
intents.members = True  # Required to kick members

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Predefined list of GIF and image URLs
gif_urls = [
    "https://tenor.com/view/cat-kitty-running-playing-having-fun-gif-26860048",
    "https://tenor.com/view/yugioh-trap-card-trap-triggered-gif-12909225702038116",
]

image_urls = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQd0LFdypsYvgil3bXjwExCaBXe6lcfl59L0Q&s",
    "https://dims.apnews.com/dims4/default/06edab5/2147483647/strip/false/crop/8145x5429+0+0/resize/1486x990!/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2Fa8%2Ff8%2F88f3b8e5167fd80b24a4172d27c4%2Fe8aaccd031bf4d49a01a1ec253c623f0",
]

# Event: When the bot is logged in and ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Command: Russian Roulette
@bot.command()
async def roulette(ctx):
    """Play Russian roulette. Lose and you get kicked, but receive a re-invite."""
    # Check if the command is invoked in a guild
    if ctx.guild is None:
        await ctx.send("You can't play Russian roulette in DMs!")
        return

    # Russian roulette logic: 1 in 6 chance of "losing"
    outcome = random.randint(1, 6)  # 1 to 6
    if outcome == 1:
        # The user "loses" and gets kicked
        try:
            # Create an invite link (valid for 10 minutes, one use)
            invite = await ctx.channel.create_invite(max_age=600, max_uses=1, unique=True)
            
            # Inform the channel
            await ctx.send(f"{ctx.author.mention} pulled the trigger... **BANG!** You're out!")
            
            # DM the user with the invite link
            await ctx.author.send(f"You lost the Russian roulette in {ctx.guild.name}. Here's a link to get back: {invite}")
            
            # Kick the user
            await ctx.guild.kick(ctx.author, reason="Lost at Russian roulette")
        except discord.Forbidden:
            
            await ctx.send("I don't have permission to kick members!")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong: {e}")
    else:
        # The user "survives"
        await ctx.send(f"{ctx.author.mention} pulled the trigger... **click**. You survived!")

# Event: Respond to messages
@bot.event
async def on_message(message):
    # Avoid responding to bot's own messages
    if message.author == bot.user:
        return

    # Respond if "hello" is mentioned
    if "hello" in message.content.lower():
        await message.channel.send('Hello!')

    # Respond if "outside" is mentioned
    if "outside" in message.content.lower():
        await message.channel.send("I'm a programmer I don't get to go outside, go touch some grass.")

    if "leetcode" in message.content.lower():
        await message.channel.send("Just compile the fries into the bag bro")

    # Respond with a random GIF if "react" is mentioned
    if "react" in message.content.lower():
        random_gif = random.choice(gif_urls)  # Pick a random GIF from the list
        await message.channel.send(random_gif)

    if "lotr" in message.content.lower():
        await message.channel.send("MID")

    # Respond with a random image if "image" is mentioned
    if "image" in message.content.lower():
        random_image = random.choice(image_urls)  # Pick a random image from the list
        await message.channel.send(random_image)

    if "sunraku" in message.content.lower():
        await message.channel.send("I hate Sunraku")

    # Process commands if they are used
    await bot.process_commands(message)
    
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


# Insert your bot token
bot.run('')
