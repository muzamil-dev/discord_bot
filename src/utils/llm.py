import re
import requests  # type: ignore
import logging
import json
import discord  # type: ignore
from discord.ext import commands  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from src.commands.utility.search_command import SearchCommand  # type: ignore
import emoji  # type: ignore
import aiohttp  # type: ignore

CONFIG_FILE_PATH = 'config/config.json'

# Load configuration from file
with open(CONFIG_FILE_PATH, 'r') as config_file:
    config = json.load(config_file)

DEVICE_IP = config.get("DEVICE_IP", "http://localhost")  # Default to localhost if not provided

# Configure logging
logging.basicConfig(level=logging.INFO)

class SensitiveInfoFilter(logging.Filter):
    def filter(self, record):
        if DEVICE_IP in record.getMessage():
            record.msg = record.msg.replace(DEVICE_IP, '[REDACTED]')
        return True

# Add the filter to the root logger
logging.getLogger().addFilter(SensitiveInfoFilter())

class LLM:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_models(self):
        url = f"{self.base_url}/api/tags"  # This is the endpoint to get the list of models
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching models from LLM: {e}")
            raise RuntimeError("Failed to access models. Please check the server configuration.") from e

    async def ollama_generate(self, model, prompt):
        url = f"{self.base_url}/api/chat"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        try:
            logging.debug(f"Sending POST request to {url} with headers {headers} and data {json.dumps(data)}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    response.raise_for_status()
                    result = await response.json()
            
            if "message" in result and "content" in result["message"]:
                content = result["message"]["content"]
                # Remove content between <think> and </think> tags
                return content
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching models from LLM: {e}")
            raise RuntimeError("Failed to access models. Please check the server configuration.") from e

# Initialize LLM

base_url = f"{DEVICE_IP}:11434"  # Ollama's server URL
llm = LLM(base_url=base_url)

class LLMCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_command = SearchCommand(bot)  # Initialize SearchCommand
        self.search_enabled = False  # Toggle for search functionality

    @commands.command(name='toggle_search', help='Toggle the search functionality on or off.')
    async def toggle_search(self, ctx):
        self.search_enabled = not self.search_enabled
        status = "enabled" if self.search_enabled else "disabled"
        await ctx.send(f"Search functionality has been {status}.")

    @commands.command(name='llm', help='Generate a response using the LLM. Optionally use Wikipedia search if enabled.')
    async def llm(self, ctx, *, prompt: str):
        try:
            if self.search_enabled:
                # Use Wikipedia search
                summary = self.search_command.wikipedia_search(prompt)
                if summary:
                    response = f"Wikipedia Summary:\n{summary}"
                    await ctx.send(response)
                else:
                    await ctx.send("No search results found.")
                return

            # Dynamically fetch models
            models = llm.get_models()

            if not models:
                embed = discord.Embed(
                    title="Error",
                    description="No models available. Please check the Ollama server configuration.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Auto-select the first available model
            model = "deepseek-r1:8b"
            logging.info(f"Selected model: {model}")

            # Generating response from the model
            logging.info(f"Sending request to Ollama API with model: {model} and prompt: {prompt}")
            response_chunks = await llm.ollama_generate(model, prompt)

            for chunk in response_chunks:
                await ctx.send(chunk)
        
        except Exception as e:
            # Catch all exceptions (e.g., model fetching, server issues)
            sanitized_error = str(e).split(" for url: ")[0]  # Remove the URL from the error message
            logging.error(f"Error generating response from Ollama: {sanitized_error}")
            logging.error(f"Request details - Model: {model}, Prompt: {prompt}")

            embed = discord.Embed(
                title="Error",
                description=f"Could not fetch or detect model. Please try again later.\n\n**Details:** {sanitized_error}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup_llm_command(bot):
    await bot.add_cog(LLMCommand(bot))
    # Check if the bot can access the models
    try:
        models = llm.get_models()
        # logging.info(f"Successfully accessed models: {models}")
    except Exception as e:
        logging.error("Failed to access models on startup. You might need to change the device ip in config.json.")
        embed = discord.Embed(
            title="Startup Error",
            description="Failed to access models on startup. Please check the Ollama server configuration.",
            color=discord.Color.red()
        )
        logging.error(embed.to_dict())