import random
from discord.ext import commands # type: ignore
import logging
from src.utils import send_message_with_retry # type: ignore

class CoinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='coin')
    async def flip_coin(self, ctx):
        outcome = random.choice(["Heads", "Tails"])
        await send_message_with_retry(ctx.channel, f"🪙 You got: {outcome}")
        logging.info(f"{ctx.author} flipped a coin and got {outcome}")

async def setup(bot):
    await bot.add_cog(CoinCommand(bot))
