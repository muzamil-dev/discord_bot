import json
from discord.ext import commands # type: ignore
import logging

with open('config/config.json') as config_file:
    config = json.load(config_file)

class ListCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = config["events"]

    @commands.command()
    async def list_events(self, ctx):
        events_list = "\n".join(self.events)
        await ctx.send(f"Available on_message events:\n{events_list}")
        logging.info(f"{ctx.author} requested events list")

async def setup(bot):
    await bot.add_cog(ListCommands(bot))
