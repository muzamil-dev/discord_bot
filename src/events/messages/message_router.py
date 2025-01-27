import json
import random
import logging
from discord.ext import commands # type: ignore
from datetime import datetime, timezone, timedelta
from .hello_response import handle_hello
from .leetcode_response import handle_leetcode
from .millbot_responses import handle_love_millbot, handle_millbot_nerd
from .sunraku_handler import handle_sunraku
from .moonraku_handler import handle_moonraku
from src.commands.quotes.lotr_command import LotrCommand
from src.utils.state_manager import get_toggle_bot, get_toggle_sunraku, get_reece_enable
from src.utils.llm import llm # updated import

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

with open('config/config.json') as config_file:
    config = json.load(config_file)

allowed_commands = config.get('ALLOWED_COMMANDS', [])

async def setup_message_handler(bot):
    @bot.event
    async def on_message(message):
        try:
            # logger.info(f"Received message: {message.content} from {message.author}")
            sunraku_state = get_toggle_sunraku()
            logger.debug(f"Current Sunraku state: {sunraku_state}")

            if not get_toggle_bot():
                if not any(message.content.startswith(cmd) for cmd in allowed_commands):
                    logger.info("Bot is toggled off. Ignoring message.")
                    return

            ctx = await bot.get_context(message)
            if ctx.command:
                logger.info(f"Processing command: {message.content} from {message.author}")
                await bot.process_commands(message)
                return

            if message.author == bot.user:
                return

            content = message.content.lower()

            if "hello" in content:
                await handle_hello(message)
            elif "react" in content:
                await message.channel.send(random.choice(config["gif_urls"]))
                logger.info(f"Responded to 'react' from {message.author}")
            elif "image" in content:
                await message.channel.send(random.choice(config["image_urls"]))
                logger.info(f"Responded to 'image' from {message.author}")
            elif "outside" in content:
                await message.channel.send("I'm a programmer I don't get to go outside, go touch some grass.")
                logger.info(f"Responded to 'outside' from {message.author}")
            elif "leetcode" in content:
                await handle_leetcode(message)
            elif "i love millbot" in content:
                await handle_love_millbot(message, config["cool_emojis"])
            elif "millbot nerd" in content:
                await handle_millbot_nerd(message)
            elif sunraku_state and "moonraku" in content:
                await handle_moonraku(message)
            elif sunraku_state and "sunraku" in content:  
                await handle_sunraku(message)
            elif "good night" in content:
                await message.channel.send("Good night! Sleep tight!")
                logger.info(f"Responded to 'good night' from {message.author}")
            elif "offline" in content:
                await message.channel.send("My circuits grow cold, and the light fades... Farewell.")
                logger.info(f"Responded to 'offline' from {message.author}")
            elif "dice roll" in content:
                await message.channel.send(f"🎲 You rolled a {random.randint(1, 6)}")
                logger.info(f"Responded to 'dice roll' from {message.author}")
            elif "coin flip" in content:
                outcome = random.choice(["Heads", "Tails"])
                await message.channel.send(f"🪙 You got: {outcome}")
                logger.info(f"Responded to 'coin flip' from {message.author}")
            elif "one does not" in content:
                await message.channel.send("https://tenor.com/tR4n.gif")
                logger.info(f"Responded to 'one does not' from {message.author}")
            elif "generate" in content:
                await message.channel.send("Blud think im ChatGPT or something")
                logger.info(f"Responded to 'generate' from {message.author}")
            elif "rm -rf" in content:
                await message.channel.send("https://tenor.com/view/linux-sudo-rm-rf-gif-24248977")
                logger.info(f"Responded to 'rm -rf' from {message.author}")
            elif "griddy" in content:
                await message.channel.send("https://cdn.discordapp.com/attachments/1310472438785507358/1321354263460581486/Mead_hitting_the_Griddy.mov")
                logger.info(f"Responded to 'griddy' from {message.author}")
            elif "reece" in content:
                gif_url = "https://tenor.com/view/whoischelsea-reeses-twitch-gif-23723197"
                reece_id = 485284378717716491
                if get_reece_enable():
                    reece = message.guild.get_member(reece_id)
                    await message.channel.send(f"{reece.mention} {gif_url}")
                    logger.info(f"Responded to 'reece' from {message.author} with mention")
                else:
                    await message.channel.send(gif_url)
                    logger.info(f"Responded to 'reece' from {message.author} without mention")
            elif "lotr" in content:
                ctx = await bot.get_context(message)
                cog = bot.get_cog('LotrCommand')
                if cog:
                    await cog.lotr(ctx)
                logger.info(f"Responded to 'lotr' from {message.author}")

        except Exception as e:
            logger.error(f"Error processing message: {message.content} from {message.author}: {str(e)}")
            raise e