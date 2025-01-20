import json
import random
from discord.ext import commands # type: ignore
import logging
from src.utils import send_message_with_retry # type: ignore

with open('config/config.json') as config_file:
    config = json.load(config_file)

class InspireCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes = config["INSPIRATIONAL_QUOTES"]

    @commands.command(name='inspire')
    async def inspire(self, ctx):
        quote = random.choice(self.quotes)
        await send_message_with_retry(ctx.channel, quote)
        logging.info(f"Sent inspirational quote to {ctx.author}")

async def setup(bot):
    await bot.add_cog(InspireCommand(bot))
