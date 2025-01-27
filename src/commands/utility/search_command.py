import requests # type: ignore
import discord # type: ignore
from discord.ext import commands # type: ignore
import logging
from bs4 import BeautifulSoup # type: ignore
import asyncio
import urllib.parse
import wikipedia # type: ignore

class SearchCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def web_search(self, query):
        async def _fetch(url):
            headers = {'User-Agent': 'Mozilla/5.0'}
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: requests.get(url, headers=headers))

        try:
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            response = await _fetch(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__a')
            if results:
                urls = [urllib.parse.unquote(result.get('href').split('uddg=')[1].split('&')[0]) for result in results[:2]]  # Limit to top 2 results
                texts = []
                for url in urls:
                    page_response = await _fetch(url)
                    page_soup = BeautifulSoup(page_response.text, 'html.parser')
                    title = page_soup.title.string if page_soup.title else 'No title'
                    description = page_soup.find('meta', attrs={'name': 'description'})
                    description = description['content'] if description else page_soup.get_text(separator='\n', strip=True)[:500]
                    texts.append((url, f"{title}\n{description}"))  # Limit to first 500 characters if no description
                return texts
            return []
        except Exception as e:
            logging.error(f"Search failed: {str(e)}")
            return []

    def wikipedia_search(self, query):
        try:
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]  # Limit to first 5 options
            return f"Disambiguation error. Options: {options}"
        except Exception as e:
            return f"An error occurred: {e}"

    @commands.command(name='search')
    async def search(self, ctx, *, query: str):
        logging.info(f"Received search command with query: {query}")
        try:
            results = await self.web_search(query)
            if not results:
                logging.info("No results found.")
                await ctx.send("No results found.")
                return

            for i, (url, text) in enumerate(results):  # Limit to top 2 results
                logging.info(f"Sending result: {url}")
                await ctx.send(f"**Result {i + 1}:**\n{url}\n{text}\n")

        except Exception as e:
            logging.error(f"Error performing search: {e}")
            await ctx.send(f"Error performing search: {e}")

async def setup_search_command(bot):
    await bot.add_cog(SearchCommand(bot))