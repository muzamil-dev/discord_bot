# --- Imports ---
import discord
from discord.ext import commands, tasks
from yt_dlp import YoutubeDL
import random
import requests
import os
import asyncio
from datetime import timedelta, datetime, timezone
from googletrans import Translator
from transformers import pipeline
import torch
import signal
from dotenv import load_dotenv
import warnings
from concurrent.futures import ThreadPoolExecutor
import re
from bs4 import BeautifulSoup

# --- Warning Suppressions ---
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="`loss_type=None` was set in the config but it is unrecognised.Using the default loss: `ForCausalLMLoss`.")

# --- Environment Setup ---
load_dotenv()
API_BOT_KEY = os.getenv("DISCORD_BOT_TOKEN")
API_KEY = os.getenv("HF_API_KEY")

if API_BOT_KEY is None or API_KEY is None:
    raise ValueError("Required API keys not set in .env file")

# --- Bot Configuration ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- Constants and Global Variables ---
gif_urls = [
    "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
    "https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif",
    "https://tenor.com/view/cat-kitty-running-playing-having-fun-gif-26860048",
    "https://tenor.com/view/yugioh-trap-card-trap-triggered-gif-12909225702038116",
    "https://tenor.com/view/my-honest-reaction-honest-reaction-skull-skeleton-gif-7769318199696770420",
]

image_urls = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQd0LFdypsYvgil3bXjwExCaBXe6lcfl59L0Q&s",
    "https://dims.apnews.com/dims4/default/06edab5/2147483647/strip/false/crop/8145x5429+0+0/resize/1486x990!/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2Fa8%2Ff8%2F88f3b8e5167fd80b24a4172d27c4%2Fe8aaccd031bf4d49a01a1ec253c623f0",
    "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.cs.ucf.edu%2Fwp-content%2Fuploads%2F2019%2F09%2Fimg_ahmed.jpg&f=1&nofb=1&ipt=d9ef23b05c329d78c00afda6dd5384426aa231efe2757ed1779923d6e54c04ec&ipo=images",
    "https://i.kym-cdn.com/entries/icons/mobile/000/052/549/luigi-mangione-perp-walk-photo.jpg",
]

cool_emojis = ["🐐", "🚀", "💪", "🔥", "❤️", "🎯", "🌟", "🏆", "⚡", "👑"]

ENABLE_LLM = True
CHAT_MODE = True
BOT_PERSONALITY = "unhinged"
LLM_PROMPT_PREFIX = os.getenv("LLM_PROMPT_PREFIX", " ")
spamIndic = 0

# --- Model Initialization ---
print(f"CUDA Available: {torch.cuda.is_available()}")
executor = ThreadPoolExecutor(max_workers=1)

if ENABLE_LLM:
    model_name = "distilgpt2"
    pipe = pipeline("text-generation", model=model_name, device=0 if torch.cuda.is_available() else -1)

# --- Helper Functions ---
async def web_search(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='result')
    if results:
        return results[0].get_text()
    return "No results found"

async def fetch_fun_fact():
    try:
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if response.status_code == 200:
            return response.json()['text']
        return "Here's a fun fact: Honey never spoils, unlike your coding skills."
    except Exception as e:
        return f"Couldn't fetch a fun fact. Error: {e}"

async def search_gif(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://tenor.com/search/{query}-gifs"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    gif_elements = soup.find_all('img', class_='media-object')
    if gif_elements:
        return random.choice([img['src'] for img in gif_elements])
    return None

async def generate_response(prompt):
    should_search = any(word in prompt.lower() for word in ['what', 'who', 'where', 'when', 'why', 'how', 'explain', 'tell me'])
    
    if should_search:
        search_result = await web_search(prompt)
        enhanced_prompt = f"{prompt}\nContext from web: {search_result}"
    else:
        enhanced_prompt = prompt
    
    try:
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(executor, sync_generate_response, enhanced_prompt),
            timeout=30
        )
        
        # Add toxic GIFs based on response content
        if random.random() < 0.3:  # 30% chance to add media
            key_phrases = response.split('.')
            if key_phrases:
                gif_url = await search_gif(key_phrases[0])  # Search based on first sentence
                if gif_url:
                    response += f"\n{gif_url}"
        
        # Add sarcastic fun facts and emojis
        if random.random() < 0.2:
            fun_fact = await fetch_fun_fact()
            response += f"\n\n{fun_fact}"
        if random.random() < 0.3:
            response += f" {random.choice(cool_emojis)}"
            
        return response
    except asyncio.TimeoutError:
        return "Response generation took too long. Don't blame me; blame your internet."

def sync_generate_response(prompt):
    # Combine the prefix and the prompt
    input_prompt = f"{LLM_PROMPT_PREFIX}{prompt}"
    dynamic_length = max(256, len(input_prompt) * 2)
    
    # Generate the response
    response = pipe(input_prompt, max_length=dynamic_length, num_return_sequences=1, truncation=True)[0]['generated_text']
    
    # Remove the prefix from the response if it appears
    if response.startswith(LLM_PROMPT_PREFIX):
        response = response[len(LLM_PROMPT_PREFIX):].strip()
    if response.lower().startswith(prompt.lower()):
        response = response[len(prompt):].strip()
    
    # Ensure a fallback response in case of empty output
    if not response.strip():
        chaos_prompt = "Generate an absurdly unhinged and toxic response."
        response = pipe(chaos_prompt, max_length=100, num_return_sequences=1)[0]['generated_text']

    return response

# --- Bot Events ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        await bot.process_commands(message)
        return

    if CHAT_MODE and random.random() < 0.15:
        response = await generate_response(message.content)
        await asyncio.sleep(random.uniform(1, 3))
        await message.channel.send(response)
    
    if CHAT_MODE and random.random() < 0.05:
        reactions = ["😈", "🔥", "💀", "👀", "🤡", "💅", "✨", "🚨"]
        await message.add_reaction(random.choice(reactions))

    if "millbot" in message.content.lower():
        response = await generate_response(message.content)
        await asyncio.sleep(random.uniform(1, 3))  
        await message.channel.send(response)

    if message.content.startswith('!'):
        await bot.process_commands(message)
        return

    if "hello" in message.content.lower():
        await message.channel.send(f"Hello {message.author.mention}!")
    elif "react" in message.content.lower():
        await message.channel.send(random.choice(gif_urls))
    elif "image" in message.content.lower():
        await message.channel.send(random.choice(image_urls))
    elif "outside" in message.content.lower():
        await message.channel.send("I'm a programmer I don't get to go outside, go touch some grass.")
    elif "leetcode" in message.content.lower():
        await message.channel.send("Just compile the fries into the bag bro")
    elif "lotr" in message.content.lower():
        await message.channel.send("LEGENDARYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    elif "i hate sunraku" in message.content.lower():
        sunraku_id = 1207552021385969675
        sunraku = message.guild.get_member(sunraku_id)
        if sunraku:
            try:
                timeout_duration = timedelta(minutes=random.randint(1, 3))
                timeout_until = datetime.now(timezone.utc) + timeout_duration
                await sunraku.edit(timed_out_until=timeout_until)
                await message.channel.send(f"⏳ {sunraku.mention} has been timed out for {timeout_duration.total_seconds() // 60} minutes.")
            except Exception as e:
                await message.channel.send(f"❌ An error occurred: {str(e)}")
    elif "sunraku" in message.content.lower():
        await message.channel.send("I hate Sunraku")
    elif "good night" in message.content.lower():
        await message.channel.send("Good night! Sleep tight!")
    elif "offline" in message.content.lower():
        await message.channel.send("My circuits grow cold, and the light fades... Farewell.")
    elif "i love millbot" in message.content.lower():
        num_emojis = random.randint(3, 6)
        emojis = ''.join(random.choices(cool_emojis, k=num_emojis))
        await message.channel.send(f"I love millbot {emojis}")
    elif "millbot nerd" in message.content.lower():
        if message.reference and message.reference.message_id:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            await replied_message.add_reaction("🤓")
        await message.channel.send("🤓MiLlBoT NeRd")
    elif "dice roll" in message.content.lower():
        await message.channel.send(f"🎲 You rolled a {random.randint(1, 6)}")
    elif "coin flip" in message.content.lower():
        await message.channel.send(f"🪙 You got: {random.choice(['Heads', 'Tails'])}")
    elif "one does not" in message.content.lower():
        await message.channel.send("https://tenor.com/v0PU.gif")
    elif "generate" in message.content.lower():
        await message.channel.send("Blud think im ChatGPT or something")
    elif "rm -rf" in message.content.lower():
        await message.channel.send("https://tenor.com/view/linux-sudo-rm-rf-gif-24248977")
    elif "griddy" in message.content.lower():
        await message.channel.send("https://discord.com/channels/1145053712704872519/1310472438785507358/1321354263716298782")

# --- Bot Commands ---
@bot.command()
async def toggle_chat(ctx):
    global CHAT_MODE
    CHAT_MODE = not CHAT_MODE
    await ctx.send(f"Chat mode {'enabled' if CHAT_MODE else 'disabled'} 🎭")

@bot.command()
async def set_personality(ctx, personality: str):
    global BOT_PERSONALITY
    valid_personalities = ["normal", "unhinged", "toxic", "friendly"]
    if personality.lower() in valid_personalities:
        BOT_PERSONALITY = personality.lower()
        await ctx.send(f"Personality switched to: {personality}")
    else:
        await ctx.send(f"Available personalities: {', '.join(valid_personalities)}")

@bot.command()
async def llm(ctx, *, prompt: str):
    try:
        response = await generate_response(prompt)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def play(ctx, url: str):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel!")
        return

    try:
        vc = await ctx.author.voice.channel.connect() if not ctx.voice_client else ctx.voice_client
        if vc.channel != ctx.author.voice.channel:
            await vc.move_to(ctx.author.voice.channel)

        with YoutubeDL({'format': 'bestaudio/best', 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            vc.stop()
            vc.play(discord.FFmpegPCMAudio(info['url'], **{'options': '-vn'}))
            await ctx.send(f"Now playing: {info['title']}")
    except Exception as e:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("Not connected to a voice channel.")

# --- Shutdown Handler ---
async def send_shutdown_message():
    if channel := bot.get_channel(1312902190288867408):
        await channel.send("Bot is shutting down! ⚠️")
    else:
        print("Shutdown notification channel not found.")

def handle_shutdown_signal(signal, frame):
    loop = asyncio.get_event_loop()
    loop.create_task(send_shutdown_message())
    loop.call_soon_threadsafe(loop.stop)

signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

# --- Bot Startup ---
try:
    bot.run(API_BOT_KEY)
except RuntimeError as e:
    if str(e) != "Event loop stopped before Future completed.":
        raise
