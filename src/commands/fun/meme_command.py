import random
import requests # type: ignore
from discord.ext import commands # type: ignore
import logging
from src.utils import send_message_with_retry # type: ignore

class MemeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        url = f'https://www.reddit.com/r/memes/{"hot" if random.randint(0,1) else "new"}/.json?limit=200'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                memes = response.json()['data']['children']
                meme = random.choice(memes)['data']
                await send_message_with_retry(ctx.channel, meme['url'])
                logging.info(f"{ctx.author} requested a meme")
            else:
                await send_message_with_retry(ctx.channel, "Couldn't fetch a meme at the moment. Please try again later.")
                logging.error(f"Failed to fetch meme. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error fetching meme: {str(e)}")
            await send_message_with_retry(ctx.channel, "Error fetching meme")

async def setup(bot):
    await bot.add_cog(MemeCommand(bot))
