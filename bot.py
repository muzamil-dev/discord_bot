import datetime
from datetime import timezone
import discord # type: ignore
from discord.ext import commands # type: ignore
from discord.ext import tasks # type: ignore
from yt_dlp import YoutubeDL # type: ignore
import random
import requests 	# type: ignore
import os
import asyncio
import json
from dotenv import load_dotenv # type: ignore
import logging
import bot_commands as cmd # type: ignore
from bot_commands import load_reminders # type: ignore
import state # type: ignore

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler('bot.log', mode='w'),  # Reset log file on each run
    logging.StreamHandler()  # Also log to console
])


# Load configuration from config.json and loads .env file
with open('config.json') as config_file:
    config = json.load(config_file)

cool_emojis = config.get("cool_emojis", [])
gif_urls = config.get("gif_urls", [])
image_urls = config.get("image_urls", [])

load_dotenv()

# Intents for accessing specific events
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

# Create bot instance with intents
bot = commands.Bot(command_prefix=config["COMMAND_PREFIX"], intents=intents)

# Load commands from bot_commands.py
cmd.setup(bot)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await load_reminders(bot)
    
async def handle_i_hate_sunraku(message):
    sunraku_id = 1207552021385969675
    sunraku = message.guild.get_member(sunraku_id)
    timeout_duration = datetime.timedelta(minutes=random.randint(1, 5))
    timeout_minutes = timeout_duration.total_seconds() // 60
    if sunraku:
        try:
            # Timeout the user sunraku for a random duration between 5 and 10 minutes
            timeout_until = datetime.datetime.now(timezone.utc) + timeout_duration
            await sunraku.edit(timed_out_until=timeout_until)
            await message.channel.send(f"⏳ {sunraku.mention} has been timed out for {timeout_minutes} minutes.")
            logging.info(f"Timed out {sunraku.display_name} for {timeout_minutes} minutes by {message.author}")
        except Exception as e:
            await message.channel.send(f"❌ An error occurred: {str(e)}")
            logging.error(f"An error occurred while timing out sunraku: {str(e)}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        # Respond to 'hello'
        if "hello" in message.content.lower():
            await message.channel.send(f"Hello {message.author.mention}!")
            logging.info(f"Responded to 'hello' from {message.author}")

        # Respond to 'react'
        elif "react" in message.content.lower():
            await message.channel.send(random.choice(gif_urls))
            logging.info(f"Responded to 'react' from {message.author}")

        # Respond to 'image'
        elif "image" in message.content.lower():
            await message.channel.send(random.choice(image_urls))
            logging.info(f"Responded to 'image' from {message.author}")

        # Respond to 'outside'
        elif "outside" in message.content.lower():
            await message.channel.send("I'm a programmer I don't get to go outside, go touch some grass.")
            logging.info(f"Responded to 'outside' from {message.author}")

        # Respond to 'leetcode'
        elif "leetcode" in message.content.lower():
            await message.channel.send("Just compile the fries into the bag bro")
            logging.info(f"Responded to 'leetcode' from {message.author}")

        # Respond to 'lotr'
        elif "lotr" in message.content.lower():
            await message.channel.send("LEGENDARYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
            logging.info(f"Responded to 'lotr' from {message.author}")

        # # Respond to 'sunraku' or 'i hate sunraku'
        # elif "i hate sunraku" in message.content.lower():
        #     sunraku_id = 1207552021385969675
        #     sunraku = message.guild.get_member(sunraku_id)
        #     timeout_duration = datetime.timedelta(minutes=random.randint(1, 5))
        #     timeout_minutes = timeout_duration.total_seconds() // 60
        #     if sunraku:
        #         try:
        #             # Timeout the user sunraku for a random duration between 5 and 10 minutes
        #             timeout_until = datetime.datetime.now(timezone.utc) + timeout_duration
        #             await sunraku.edit(timed_out_until=timeout_until)
        #             await message.channel.send(f"⏳ {sunraku.mention} has been timed out for {timeout_minutes} minutes.")
        #             logging.info(f"Timed out {sunraku.display_name} for {timeout_minutes} minutes by {message.author}")
        #         except Exception as e:
        #             await message.channel.send(f"❌ An error occurred: {str(e)}")
        #             logging.error(f"An error occurred while timing out sunraku: {str(e)}")
        
        elif "sunraku" in message.content.lower():
            await message.channel.send("I hate Sunraku")
            logging.info(f"Responded to 'sunraku' from {message.author}")
            
			# Also trigger the 'i hate sunraku' logic
            await handle_i_hate_sunraku(message)

        # Respond to 'good night'
        elif "good night" in message.content.lower():
            await message.channel.send("Good night! Sleep tight!")
            logging.info(f"Responded to 'good night' from {message.author}")

        # Respond to 'offline'
        elif "offline" in message.content.lower():
            await message.channel.send("My circuits grow cold, and the light fades... Farewell.")
            logging.info(f"Responded to 'offline' from {message.author}")

        # Respond to 'i love millbot'
        elif "i love millbot" in message.content.lower():
            # Add random cool emojis to the message
            num_emojis = random.randint(3, 6)
            emojis = ''.join(random.choices(cool_emojis, k=num_emojis))
            await message.channel.send(f"I love millbot {emojis}")
            logging.info(f"Responded to 'i love millbot' from {message.author}")

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
            logging.info(f"Responded to 'millbot nerd' from {message.author}")

        # Respond to 'dice roll'
        elif "dice roll" in message.content.lower():
            await message.channel.send(f"🎲 You rolled a {random.randint(1, 6)}")
            logging.info(f"Responded to 'dice roll' from {message.author}")
        
        # Respond to 'coin flip'
        elif "coin flip" in message.content.lower():
            outcome = random.choice(["Heads", "Tails"])
            await message.channel.send(f"🪙 You got: {outcome}")
            logging.info(f"Responded to 'coin flip' from {message.author}")

        elif "one does not" in message.content.lower():
            await message.channel.send("https://tenor.com/tR4n.gif")
            logging.info(f"Responded to 'one does not' from {message.author}")
        
        elif "generate" in message.content.lower():
            await message.channel.send("Blud think im ChatGPT or something")
            logging.info(f"Responded to 'generate' from {message.author}")
            
        elif "rm -rf" in message.content.lower():
            await message.channel.send("https://tenor.com/view/linux-sudo-rm-rf-gif-24248977")
            logging.info(f"Responded to 'rm -rf' from {message.author}")
            
        elif "griddy" in message.content.lower():
            await message.channel.send("https://cdn.discordapp.com/attachments/1310472438785507358/1321354263460581486/Mead_hitting_the_Griddy.mov?ex=678946cd&is=6787f54d&hm=179a5989732cb2a3177ef9ef28852b5a8309f5e1b30c6d798f8c13ff92194e0b&")
            logging.info(f"Responded to 'griddy' from {message.author}")

        if "reece" in message.content.lower():
            gif_url = "https://tenor.com/view/whoischelsea-reeses-twitch-gif-23723197"
            reece_id = 485284378717716491
            
            if state.get_reece_enable():
                reece = message.guild.get_member(reece_id)
                await message.channel.send(f"{reece.mention} {gif_url}", )
                logging.info(f"Responded to 'reece' from {message.author} with mention")
            else:
                await message.channel.send(gif_url)
                logging.info(f"Responded to 'reece' from {message.author} without mention")
        
        # Process other commands
        await bot.process_commands(message)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        await message.channel.send(f"❌ An error occurred: {str(e)}")


# Run the bot with the token from the environment variable
try:
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
except RuntimeError as e:
    if str(e) == "Event loop stopped before Future completed.":
        logging.error("Event loop stopped before Future completed. My bad vro, someone pulled the plug on me.")
    else:
        raise