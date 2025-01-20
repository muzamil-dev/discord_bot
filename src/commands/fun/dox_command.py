import random
import discord # type: ignore
from discord.ext import commands # type: ignore
import json
import logging

with open('config/config.json') as config_file:
    config = json.load(config_file)

class DoxCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fake_addresses = config["fake_addresses"]
        self.fake_phone_numbers = config["fake_phone_numbers"]
        self.fake_ips = config["fake_ips"]

    @commands.command()
    async def dox(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.send("Vro gonna get yourself doxxed. Next time do this: `!dox @username`")
            logging.warning(f"{ctx.author} tried to use the dox command without specifying a member.")
            return

        address = random.choice(self.fake_addresses)
        phone = random.choice(self.fake_phone_numbers)
        ip = random.choice(self.fake_ips)

        logging.info(f"{ctx.author} used the dox command on {member.display_name}")
        await ctx.send(f"📁 **Dox on {member.display_name}**:\n"
                      f"🏠 Address: {address}\n"
                      f"📞 Phone: {phone}\n"
                      f"🌐 IP: {ip}\n")

async def setup(bot):
    await bot.add_cog(DoxCommand(bot))
