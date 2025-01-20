from discord.ext import commands # type: ignore
import asyncio 

class SpamCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_tasks = {}

    @commands.command(name='spam', help='Repeats the given text until stopped')
    async def spam(self, ctx, *, text: str):
        """Repeats the given text until stopped
        Usage: !spam This is a spam message"""
        if ctx.author.id in self.spam_tasks:
            await ctx.send("You are already spamming. Use !stop to stop the spam.")
            return

        async def spam_task():
            while True:
                await ctx.send(text)
                await asyncio.sleep(1)

        task = self.bot.loop.create_task(spam_task())
        self.spam_tasks[ctx.author.id] = task
        await ctx.send(f"Started spamming: {text}")

    @commands.command(name='stop', help='Stops all spam')
    async def stop(self, ctx):
        """Stops all spam
        Usage: !stop"""
        if not self.spam_tasks:
            await ctx.send("There are no active spam tasks.")
            return

        for user_id, task in self.spam_tasks.items():
            task.cancel()
        self.spam_tasks.clear()
        await ctx.send("Stopped all spamming.")

async def setup(bot):
    await bot.add_cog(SpamCommand(bot))