import random 
from discord.ext import commands # type: ignore
import logging 
from src.utils import send_message_with_retry # type: ignore

class DiceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dice')
    async def roll_dice(self, ctx):
        result = random.randint(1, 6)
        await send_message_with_retry(ctx.channel, f"🎲 You rolled a {result}")
        logging.info(f"{ctx.author} rolled a {result}")

async def setup(bot):
    await bot.add_cog(DiceCommand(bot))
