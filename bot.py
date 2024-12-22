import discord 
from discord.ext import commands, tasks
from yt_dlp import YoutubeDL
import random
import requests
import os
import asyncio
import datetime

# API KEYS IN ONE LOCATION
HF_APIKEY = ""

# Intents for accessing specific events
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

# Create bot instance with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Predefined list of GIF and image URLs
gif_urls = [
    "https://tenor.com/view/cat-kitty-running-playing-having-fun-gif-26860048",
    "https://tenor.com/view/yugioh-trap-card-trap-triggered-gif-12909225702038116",
    "https://tenor.com/view/my-honest-reaction-honest-reaction-skull-skeleton-gif-7769318199696770420",
]

image_urls = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQd0LFdypsYvgil3bXjwExCaBXe6lcfl59L0Q&s",
    "https://dims.apnews.com/dims4/default/06edab5/2147483647/strip/false/crop/8145x5429+0+0/resize/1486x990!/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2Fa8%2Ff8%2F88f3b8e5167fd80b24a4172d27c4%2Fe8aaccd031bf4d49a01a1ec253c623f0",
    "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.cs.ucf.edu%2Fwp-content%2Fuploads%2F2019%2F09%2Fimg_ahmed.jpg&f=1&nofb=1&ipt=d9ef23b05c329d78c00afda6dd5384426aa231efe2757ed1779923d6e54c04ec&ipo=images",
]

# Hugging Face API details (use env variable for security)
API_KEY = os.getenv(HF_APIKEY)
API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-125M"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# LLM Command
@bot.command()
async def llm(ctx, *, prompt: str):
    """Generate a response from Hugging Face's hosted GPT-Neo model."""
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "inputs": prompt
    }

    try:
        # Make the API request
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            # Parse the response and send the result back to Discord
            generated_text = response.json()[0]["generated_text"]
            await ctx.send(f"🤖 **LLM Response:** {generated_text}")
        else:
            await ctx.send(f"❌ Failed to get a response: {response.status_code} - {response.text}")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# Play YouTube Audio Command
@bot.command()
async def play(ctx, url: str):
    """Joins the user's voice channel and plays audio from the given YouTube URL."""
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command!")
        return

    voice_channel = ctx.author.voice.channel

    try:
        # Connect to the voice channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        # Use yt-dlp to get audio stream URL
        YDL_OPTIONS = {'format': 'bestaudio/best', 'quiet': True}
        FFMPEG_OPTIONS = {'options': '-vn'}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        # Play the audio
        ctx.voice_client.stop()  # Stop any existing audio
        ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        await ctx.send(f"Now playing: {info['title']}")
    except Exception as e:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await ctx.send(f"An error occurred: {e}")

# Stop command to disconnect bot from VC
@bot.command()
async def stop(ctx):
    """Stops the audio and disconnects the bot from the voice channel."""
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel.")

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

@bot.command()
async def motivate(ctx):
    """Send a random motivational quote."""
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            quote = response.json()[0]['q']
            author = response.json()[0]['a']
            await ctx.send(f"💪 **Motivational Quote:** \"{quote}\" - {author}")
        else:
            await ctx.send(f"❌ Failed to get a quote: {response.status_code} - {response.text}")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

@bot.command()
async def timeout(ctx, member: discord.Member):
    """Timeout a member and the user who triggers the command."""
    try:
        # Random timeout duration between 1 to 3 minutes
        duration = random.randint(1, 3)
        
        # Timeout the specified member
        await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=duration))
        await ctx.send(f"⏳ {member.mention} has been timed out for {duration} minutes.")

        # Timeout the user who triggered the command for double the duration
        await ctx.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=duration * 2))
        await ctx.send(f"⏳ {ctx.author.mention} has also been timed out for {duration * 2} minutes.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

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
        await message.channel.send("LEGEND")
        await asyncio.sleep(1)  # Wait for 1 second
        await message.channel.send("...wait for it...")
        await asyncio.sleep(1)  # Wait for 1 second
        await message.channel.send("DARY")

    # Respond with a random image if "image" is mentioned
    if "image" in message.content.lower():
        random_image = random.choice(image_urls)  # Pick a random image from the list
        await message.channel.send(random_image)

    if "sunraku" in message.content.lower():
        await message.channel.send("I love Sunraku")

    if any(keyword in message.content.lower() for keyword in ["mill", "muzamill"]):
        await message.channel.send("I hate MuzaMill, bro sucks on nuts")

    if "good night" in message.content.lower():
        await message.channel.send("Good night! Sleep tight!")

    if "i hate sunraku" in message.content.lower():
        sunraku = discord.utils.get(message.guild.members, name="sunraku")
        if sunraku:
            try:
                # Timeout the user sunraku for 10 minutes
                await sunraku.timeout(discord.utils.utcnow() + discord.timedelta(minutes=random.randint(1, 3)))
                await message.channel.send(f"⏳ {sunraku.mention} has been timed out for 10 minutes.")
            except Exception as e:
                await message.channel.send(f"❌ An error occurred: {str(e)}")

    # Process commands if they are used
    await bot.process_commands(message)
    
@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if "hello" in message.content.lower():
        await message.channel.send(f"Hello {message.author.mention}!")


    await bot.process_commands(message)

@tasks.loop(hours=1)
async def check_christmas():
    now = datetime.datetime.now()

    if now.month == 12 and now.day == 25:
        await bot.change_presence(activity=discord.Game("🎄 Merry Christmas"))
        print("It's Christmas! status updated")
    
        channel_id = 1145053714114166846

        channel = bot.get_channel(channel_id)

        if channel:
            await channel.send("🎄 Merry Christmas, everyone! Have a wonderful holiday! 🎅")
    
    else: 

        await bot.change_presence(activity=discord.Game("Available for commands"))
        print("It's not Christmas")


@bot.command()
async def test_christmas(ctx):
    """Manually test the Christmas message and status update."""
    await bot.change_presence(activity=discord.Game("🎄 Merry Christmas!"))
    await ctx.send("🎄 Merry Christmas, everyone! Have a wonderful holiday! 🎅")


# Insert your bot token
bot.run('')
