import discord # type: ignore
from discord.ext import commands # type: ignore
import random
import logging

class ShootCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shoot', help='Shoot another user. Usage: !shoot @user')
    async def shoot(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.send("You need to mention a user to shoot. Usage: `!shoot @username`")
            logging.warning(f"{ctx.author} tried to use the shoot command without specifying a member.")
            return

        fancy_texts = [
            f"🔫 {ctx.author.mention} shoots {member.mention} with a water gun! 💦",
            f"💥 {ctx.author.mention} fires a laser at {member.mention}! Pew pew! 🔫",
            f"🎯 {ctx.author.mention} throws a pie at {member.mention}'s face! 🥧",
            f"💣 {ctx.author.mention} launches a confetti bomb at {member.mention}! 🎉",
            f"🏹 {ctx.author.mention} shoots an arrow of love at {member.mention}! 💘",
            f"⚔️ {ctx.author.mention} challenges {member.mention} to a duel! En garde! 🗡️",
            f"🪃 {ctx.author.mention} throws a boomerang at {member.mention}! It comes back! 🌀",
            f"🧨 {ctx.author.mention} sets off fireworks around {member.mention}! 🎆",
            f"🪓 {ctx.author.mention} swings an axe at {member.mention}! Just kidding! 🪓",
            f"🔪 {ctx.author.mention} slices the air near {member.mention}! Close call! 🔪"
        ]

        response = random.choice(fancy_texts)
        await ctx.send(response)
        logging.info(f"{ctx.author} used the shoot command on {member.display_name}")

async def setup(bot):
    await bot.add_cog(ShootCommand(bot))