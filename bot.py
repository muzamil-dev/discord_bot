import discord
from discord.ext import commands
from discord.ext import tasks
from yt_dlp import YoutubeDL
import random
import requests
import os
import asyncio
from datetime import timedelta, datetime

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
    "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
    "https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif",
    "https://tenor.com/view/cat-kitty-running-playing-having-fun-gif-26860048",
    "https://tenor.com/view/yugioh-trap-card-trap-triggered-gif-12909225702038116",
    "https://tenor.com/view/my-honest-reaction-honest-reaction-skull-skeleton-gif-7769318199696770420",
]

image_urls = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQd0LFdypsYvgil3bXjwExCaBXe6lcfl59L0Q&s",
    "https://dims.apnews.com/dims4/default/06edab5/2147483647/strip/false/crop/8145x5429+0+0/resize/1486x990!/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2Fa8%2Ff8%2F88f3b8e5167fd80b24a4172d27c4%2Fe8aaccd031bf4d49a01a1ec253c623f0",
    "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.cs.ucf.edu%2Fwp-content%2Fuploads%2F2019%2F09%2Fimg_ahmed.jpg&f=1&nofb=1&ipt=d9ef23b05c329d78c00afda6dd5384426aa231efe2757ed1779923d6e54c04ec&ipo=images",
    "https://i.kym-cdn.com/entries/icons/mobile/000/052/549/luigi-mangione-perp-walk-photo.jpg",
]

cool_emojis = ["🐐", "🚀", "💪", "🔥", "❤️", "🎯", "🌟", "🏆", "⚡", "👑"]

# Hugging Face API details
API_KEY = os.getenv(" ") 
API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-125M"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# LLM Command
@bot.command()
async def llm(ctx, *, prompt: str):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {"inputs": prompt}

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            generated_text = response.json()[0]["generated_text"]
            await ctx.send(f"🤖 **LLM Response:** {generated_text}")
        else:
            await ctx.send(f"❌ Failed to get a response: {response.status_code} - {response.text}")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# Play YouTube Audio Command
@bot.command()
async def play(ctx, url: str):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command!")
        return

    voice_channel = ctx.author.voice.channel

    try:
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        YDL_OPTIONS = {'format': 'bestaudio/best', 'quiet': True}
        FFMPEG_OPTIONS = {'options': '-vn'}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        await ctx.send(f"Now playing: {info['title']}")
    except Exception as e:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await ctx.send(f"An error occurred: {e}")

# Stop command to disconnect bot from VC
@bot.command()
async def stop(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel.")

# Russian Roulette
@bot.command()
async def roulette(ctx):
    if ctx.guild is None:
        await ctx.send("You can't play Russian roulette in DMs!")
        return

    outcome = random.randint(1, 6)
    if outcome == 1:
        try:
            invite = await ctx.channel.create_invite(max_age=600, max_uses=1, unique=True)
            await ctx.send(f"{ctx.author.mention} pulled the trigger... **BANG!** You're out!")
            await ctx.author.send(f"You lost the Russian roulette in {ctx.guild.name}. Here's a link to get back: {invite}")
            await ctx.guild.kick(ctx.author, reason="Lost at Russian roulette")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick members!")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong: {e}")
    else:
        await ctx.send(f"{ctx.author.mention} pulled the trigger... **click**. You survived!")

@bot.command()
async def motivate(ctx):
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
    try:
        duration = random.randint(1, 3)
        until_time = datetime.utcnow() + timedelta(minutes=duration)
        await member.edit(timeout_until=until_time)
        await ctx.send(f"⏳ {member.mention} has been timed out for {duration} minutes.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Respond to 'hello'
    if "hello" in message.content.lower():
        await message.channel.send(f"Hello {message.author.mention}!")

    # Respond to 'react'
    elif "react" in message.content.lower():
        await message.channel.send(random.choice(gif_urls))

    # Respond to 'image'
    elif "image" in message.content.lower():
        await message.channel.send(random.choice(image_urls))

    # Respond to 'outside'
    elif "outside" in message.content.lower():
        await message.channel.send("I'm a programmer I don't get to go outside, go touch some grass.")

    # Respond to 'leetcode'
    elif "leetcode" in message.content.lower():
        await message.channel.send("Just compile the fries into the bag bro")

    # Respond to 'lotr'
    elif "lotr" in message.content.lower():
        await message.channel.send("LEGEND")
        await asyncio.sleep(1)  # Wait for 1 second
        await message.channel.send("...wait for it...")
        await asyncio.sleep(1)  # Wait for 1 second
        await message.channel.send("DARY")

    # Respond to 'sunraku' or 'i hate sunraku'
    elif "sunraku" in message.content.lower():
        await message.channel.send("I hate Sunraku")
    elif "i hate sunraku" in message.content.lower():
        sunraku = discord.utils.get(message.guild.members, name="sunraku")
        if sunraku:
            try:
                # Timeout the user sunraku for 10 minutes
                await sunraku.timeout(discord.utils.utcnow() + discord.timedelta(minutes=random.randint(1, 3)))
                await message.channel.send(f"⏳ {sunraku.mention} has been timed out for 10 minutes.")
            except Exception as e:
                await message.channel.send(f"❌ An error occurred: {str(e)}")

    # Respond to 'good night'
    elif "good night" in message.content.lower():
        await message.channel.send("Good night! Sleep tight!")

    # Respond to 'offline'
    elif "offline" in message.content.lower():
        await message.channel.send("My circuits grow cold, and the light fades... Farewell.")

    # Respond to 'i love millbot'
    elif "i love millbot" in message.content.lower():
        # Add random cool emojis to the message
        num_emojis = random.randint(3, 6)
        emojis = ''.join(random.choices(cool_emojis, k=num_emojis))
        await message.channel.send(f"I love millbot {emojis}")

    # Respond to 'millbot nerd'
    elif "millbot nerd" in message.content.lower():
        # Check if the message is a reply to another message
        if message.reference and message.reference.message_id:
            # Fetch the replied message
            replied_message = await message.channel.fetch_message(message.reference.message_id)

            # Add the 🤓 emoji to the replied message
            await replied_message.add_reaction("🤓")

        # Send the nerdy response
        nerdy_response = "🤓MiLlBoT NeRd"
        await message.channel.send(nerdy_response)

    # Respond to 'i love millbot' with cool emojis
    elif "i love millbot" in message.content.lower():
        # Add random cool emojis to the message
        num_emojis = random.randint(3, 6)
        emojis = ''.join(random.choices(cool_emojis, k=num_emojis))
        await message.channel.send(f"I love millbot {emojis}")

    # Respond to 'dice roll'
    elif "dice roll" in message.content.lower():
        await message.channel.send(f"🎲 You rolled a {random.randint(1, 6)}")

    # Respond to 'coin flip'
    elif "coin flip" in message.content.lower():
        outcome = random.choice(["Heads", "Tails"])
        await message.channel.send(f"🪙 You got: {outcome}")

    # Process other commands
    await bot.process_commands(message)

#meme command
@bot.command()
async def meme(ctx):
    """Fetches a random meme and sends it to the channel."""
    try:
        # Use Meme API to fetch a random meme
        response = requests.get("https://meme-api.com/gimme")
        data = response.json()

        # Extract meme information
        meme_title = data["title"]
        meme_url = data["url"]
        meme_post_link = data["postLink"]

        # Create an embed with the meme
        embed = discord.Embed(
            title=meme_title,
            url=meme_post_link,
            color=discord.Color.blue()
        )
        embed.set_image(url=meme_url)
        embed.set_footer(text="Powered by Meme API")

        # Send the embed to the channel
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("Oops! Something went wrong while fetching a meme.")
        print(f"Error: {e}")

# Christmas message and status update 
@tasks.loop(hours=1)
async def check_christmas():
    now = datetime.datetime.now()
    channel_id = 1145053714114166846  # Replace with your channel ID

    try:
        if now.month == 12 and now.day == 25:
            # Update bot status
            await bot.change_presence(activity=discord.Game("🎄 Merry Christmas"))
            print("It's Christmas! Status updated.")
            
            # Send message to the specified channel
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send("🎄 Merry Christmas, everyone! Have a wonderful holiday! 🎅")
            else:
                print(f"Channel with ID {channel_id} not found.")
        else:
            # Default status update
            await bot.change_presence(activity=discord.Game("Available for commands"))
            print("It's not Christmas.")
    except Exception as e:
        print(f"An error occurred in check_christmas: {e}")

@bot.command()
async def test_christmas(ctx):
    """Manually test the Christmas message and status update."""
    try:
        await bot.change_presence(activity=discord.Game("🎄 Merry Christmas!"))
        await ctx.send("🎄 Merry Christmas, everyone! Have a wonderful holiday! 🎅")
        print("Test command executed successfully.")
    except Exception as e:
        await ctx.send("An error occurred while testing the Christmas message.")
        print(f"Error in test_christmas: {e}")


# List of cool emojis


    #dox command
    # Fake dox details
fake_addresses = [
    "123 Fake Street, Springfield",
    "742 Evergreen Terrace, Springfield",
    "221B Baker Street, London",
    "31 Spooner Street, Quahog",
    "1600 Pennsylvania Ave NW, Washington, DC",
]

fake_phone_numbers = [
    "555-1234",
    "867-5309",
    "404-404-4044",
    "123-456-7890",
    "800-GET-LOST",
]

fake_ips = [
    "192.168.1.1",
    "127.0.0.1",
    "69.420.666.1337",
    "255.255.255.255",
    "8.8.8.8",
]

@bot.command()
async def dox(ctx, member: discord.Member):
    """Fake doxes a user for fun."""
    address = random.choice(fake_addresses)
    phone = random.choice(fake_phone_numbers)
    ip = random.choice(fake_ips)

    # Send the "dox" message
    await ctx.send(f"📁 **Dox on {member.display_name}**:\n"
                   f"🏠 Address: {address}\n"
                   f"📞 Phone: {phone}\n"
                   f"🌐 IP: {ip}\n")

bot.run(' ')
