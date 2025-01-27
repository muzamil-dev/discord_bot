import discord # type: ignore
from discord.ext import commands # type: ignore
import random
import logging

class DieCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='die', help='Send a funny death message. Usage: !die @user')
    async def die(self, ctx, member: discord.Member = None):
        templates = [
            "{} has met their untimely demise! {}",
            "{} has kicked the bucket! {}",
            "{} has shuffled off this mortal coil! {}",
            "{} has gone to the great beyond! {}",
            "{} has taken a permanent nap! {}",
            "{} has become one with the force! {}",
            "{} has bitten the dust! {}",
            "{} has checked out early! {}",
            "{} has gone to the big server in the sky! {}",
            "{} has logged out for the last time! {}",
            "{} DIEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE {}"
        ]

        random_phrases = [
            "💀",
            "🪣",
            "🌀",
            "🌌",
            "🛌",
            "🌟",
            "🌬️",
            "🏨",
            "☁️",
            "💻",
            "🔥",
            "💥",
            "⚡",
            "💣",
            "🔪",
            "🪓",
            "⚔️",
            "🧨",
            "🎯",
            "🏹",
            "🪃",
            "🧟",
            "👻",
            "😈",
            "🤡",
            "💀💀💀"
        ]

        if member is None:
            member = ctx.author

        if random.random() < 0.1:
            target = ctx.author
        else:
            target = member

        template = random.choice(templates)
        phrase = random.choice(random_phrases)
        response = template.format(target.mention, phrase)
        await ctx.send(response)
        logging.info(f"{ctx.author} used the die command on {target.display_name}")

async def setup(bot):
    await bot.add_cog(DieCommand(bot))