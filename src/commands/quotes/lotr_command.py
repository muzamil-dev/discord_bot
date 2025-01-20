import os
import requests # type: ignore
import random
from discord.ext import commands # type: ignore
import logging
from src.utils import send_message_with_retry

class LotrCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes = []

    async def fetch_quotes(self):
        api_key = os.getenv('THE_ONE_API_KEY')
        if not api_key:
            logging.error("The One API key is missing in .env file")
            return
        
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get('https://the-one-api.dev/v2/quote', headers=headers)
        
        if response.status_code == 200:
            quotes = response.json()['docs']
            self.quotes = [quote['dialog'] for quote in quotes]
            logging.info(f"Fetched {len(self.quotes)} LOTR quotes")
        else:
            logging.error(f"Failed to fetch LOTR quotes. Status: {response.status_code}")

    @commands.command()
    async def lotr(self, ctx):
        if not self.quotes:
            await self.fetch_quotes()
        
        if self.quotes:
            quote = random.choice(self.quotes)
            await send_message_with_retry(ctx.channel, quote)
            logging.info(f"Sent LOTR quote to {ctx.author}")
        else:
            await send_message_with_retry(ctx.channel, "Could not fetch a quote at this time.")
            logging.error("LOTR quotes list is empty")

async def setup(bot):
    cog = LotrCommand(bot)
    await cog.fetch_quotes()
    await bot.add_cog(cog)