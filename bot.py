# --- Imports ---
import discord # type: ignore
from discord.ext import commands, tasks # type: ignore
from yt_dlp import YoutubeDL # type: ignore
import gc # type: ignore
import torch # type: ignore
import random # type: ignore
import asyncio # type: ignore
import os # type: ignore
from datetime import timedelta, datetime, timezone # type: ignore
from deep_translator import GoogleTranslator # type: ignore
from transformers import pipeline # type: ignore
import signal # type: ignore
from dotenv import load_dotenv # type: ignore
import warnings # type: ignore
from concurrent.futures import ThreadPoolExecutor # type: ignore
import re # type: ignore
from bs4 import BeautifulSoup # type: ignore
import requests # type: ignore
import openai # type: ignore
from textblob import TextBlob # type: ignore
import wikipedia  # type: ignore
import pyjokes  # type: ignore
import wolframalpha  # type: ignore
from faker import Faker # type: ignore

# --- Warning Suppressions ---
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="`loss_type=None` was set in the config but it is unrecognised.Using the default loss: `ForCausalLMLoss`.")

# --- Environment Setup ---
load_dotenv()
API_BOT_KEY = os.getenv("DISCORD_BOT_TOKEN")
API_KEY = os.getenv("HF_API_KEY")
LLM_PROMPT_PREFIX = os.getenv("LLM_PROMPT_PREFIX", "Well Mannered Millbot: ")
ENABLE_LLM = os.getenv('ENABLE_LLM', 'false').lower() == 'true'
CHAT_MODE = True

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
ERROR_MESSAGES = {
    'general': [
        "Brain.exe has stopped working 🤖",
        "I'm having a moment... 🤔",
        "Error 404: Brain not found 🧠",
        "My last brain cell just rage quit 😵",
        "Task failed successfully 👍",
        "Have you tried turning me off and on again? 🔄",
        "I'm not broken, I'm just differently functional 🛠️",
        "Loading personality.exe... Loading failed 💀",
        "Oops, I did it again 🎵",
        "Instructions unclear, got stuck in infinite loop 🌀"
    ],
    'timeout': [
        "Taking too long... Must be using Internet Explorer 🐌",
        "Time's up! Just like my patience ⏰",
        "Connection timed out... Just like my will to live 💔",
        "Sorry, my hamster stopped running the wheel 🐹",
        "Loading... Loading... *dial-up noises* 📞"
    ],
    'memory': [
        "Out of memory... Time to download more RAM 💾",
        "Memory machine broke, understandable have a nice day 🤖",
        "I forgor 💀",
        "Brain capacity reached, time for a memory dump 🗑️",
        "Error: Stack overflow from too many dad jokes 👨"
    ],
    'coding': [
        "Just compile the fries into the bag bro 🍟",
        "Have you tried turning it off and on again? 💻",
        "Error 418: I'm a teapot ☕",
        "Task failed successfully... like my coding career 👨‍💻",
        "Runtime Error: Brain.exe stopped working 🧠",
        "Segmentation fault: Brain dumped 💀",
        "404: Solution not found 🔍",
        "Time Limit Exceeded: My brain needs a coffee break ☕",
        "Stack Overflow: Too many recursions in my thoughts 🌀",
        "NullPointerException: Brain cells not initialized 🤖"
    ]
}

PERSONALITY_TRAITS = {
    'sassy': ["😏", "💅", "✨"],
    'excited': ["🚀", "💪", "🔥"],
    'thoughtful': ["🤔", "💭", "🧐"],
    'chaotic': ["😈", "💀", "👻"]
}

CONVERSATION_STARTERS = [
    "Speaking of {topic}, did you know...",
    "That reminds me of {topic}...",
    "Fun fact about {topic}:",
    "You know what's wild about {topic}?"
]

cool_emojis = ["🐐", "🚀", "💪", "🔥", "❤️", "🎯", "🌟", "🏆", "⚡", "👑"]


spamIndic = 0

# --- Model Initialization ---
print(f"CUDA Available: {torch.cuda.is_available()}")
executor = ThreadPoolExecutor(max_workers=1)

if ENABLE_LLM:
    model_name = "distilgpt2"
    pipe = pipeline("text-generation", model=model_name, device=0 if torch.cuda.is_available() else -1)

# --- Helper Functions ---
# Function to perform a web search
async def web_search(query):
    async def _fetch():
        headers = {'User-Agent': 'Mozilla/5.0'}
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: requests.get(search_url, headers=headers))

    try:
        response = await _fetch()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result')
        if results:
            return results[0].get_text()
        return "No results found"
    except Exception as e:
        return f"Search failed: {str(e)}"

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

async def search_leetcode_solution(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='result')
    if results:
        return results[0].get_text()
    return "No results found"

async def safe_send(channel, content, mention_author=None):
    """Enhanced message sending with validation"""
    if not content or content.isspace():
        # Provide a fallback message if content is empty
        content = "🤖 *beep boop* I'm having trouble processing that request"
    
    # Format the message
    if mention_author:
        content = f"{mention_author} {content}"
    
    # Split and format content
    chunks = content.split('. ')
    formatted_chunks = [chunk for chunk in chunks if chunk.strip()]  # Remove empty chunks
    
    if not formatted_chunks:
        await channel.send("🤖 Error processing response")
        return
        
    formatted_content = '\n\n'.join(formatted_chunks)
    
    # Send message with length check
    if len(formatted_content) <= 2000:
        await channel.send(formatted_content)
    else:
        current_chunk = ""
        for sentence in formatted_chunks:
            if len(current_chunk) + len(sentence) > 1900:
                if current_chunk.strip():  # Only send non-empty chunks
                    await channel.send(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += f"{sentence}. \n\n"
        if current_chunk.strip():  # Send final chunk if non-empty
            await channel.send(current_chunk)
async def generate_response(prompt):
    try:
        # Location/factual queries check
        location_keywords = ['where', 'location', 'country', 'place', 'find']
        if any(keyword in prompt.lower() for keyword in location_keywords):
            try:
                search_term = prompt.lower().replace('millbot', '').replace('where is', '').replace('where', '').strip()
                wiki_summary = wikipedia.summary(search_term, sentences=2)
                
                # Add some spicy personality to the factual response
                spicy_prefixes = [
                    "Listen up you geographical noob! 🗺️",
                    "Bruh, everyone knows",
                    "☠️ Imagine not knowing that",
                    "My dead GPU could tell you that",
                    "While you were touching grass,",
                    "Even my buggy code knows"
                ]
                
                return f"{random.choice(spicy_prefixes)} {wiki_summary} {random.choice(PERSONALITY_TRAITS['chaotic'])}"
            except:
                return await sync_generate_response(prompt)
        
        # Add context awareness
        if "what is" in prompt.lower() or "who is" in prompt.lower():
            try:
                wiki_summary = wikipedia.summary(prompt.replace("what is", "").replace("who is", ""), sentences=2)
                return f"{wiki_summary} {await add_personality(prompt)}"
            except:
                pass

        # Add programming jokes
        if "joke" in prompt.lower():
            return f"{pyjokes.get_joke()} {random.choice(PERSONALITY_TRAITS['sassy'])}"

        # Add random facts generation
        if "fact" in prompt.lower():
            fake = Faker()
            return f"Here's something interesting: {fake.catch_phrase()} {random.choice(PERSONALITY_TRAITS['thoughtful'])}"

        # Original LLM response logic here
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(executor, sync_generate_response, prompt),
            timeout=30
        )
        
        # Add personality and context
        personality = await add_personality(response)
        return f"{response} {personality}"

    except Exception as e:
        return f"Even bots have their moments 🤖 {random.choice(ERROR_MESSAGES['general'])}"


def sync_generate_response(prompt):
    try:
        # Clear CUDA cache and collect garbage
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

        input_prompt = f"{LLM_PROMPT_PREFIX}{prompt}"
        input_length = len(pipe.tokenizer.encode(input_prompt))
        
        max_allowed_tokens = 1024
        max_new_tokens = max(32, min(512, max_allowed_tokens - input_length))
        
        response = pipe(
            input_prompt,
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
            repetition_penalty=1.2,  # Added repetition penalty to reduce repeated text
            truncation=True,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            top_k=50,
            pad_token_id=pipe.tokenizer.eos_token_id
        )[0]['generated_text']

        # Clean response
        if response.startswith(LLM_PROMPT_PREFIX):
            response = response[len(LLM_PROMPT_PREFIX):].strip()
        if response.lower().startswith(prompt.lower()):
            response = response[len(prompt):].strip()
        
        return response.strip() or random.choice(ERROR_MESSAGES['general'])
        
    except asyncio.TimeoutError:
        return random.choice(ERROR_MESSAGES['timeout'])
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return random.choice(ERROR_MESSAGES['memory'])
        return random.choice(ERROR_MESSAGES['general'])
    except Exception as e:
        print(f"Generation error: {e}")
        return random.choice(ERROR_MESSAGES['general'])

async def add_personality(message):
    sentiment = TextBlob(message).sentiment.polarity
    if sentiment > 0.5:
        return random.choice(PERSONALITY_TRAITS['excited'])
    elif sentiment < -0.2:
        return random.choice(PERSONALITY_TRAITS['sassy'])
    elif 'how' in message.lower() or 'why' in message.lower():
        return random.choice(PERSONALITY_TRAITS['thoughtful'])
    return random.choice(PERSONALITY_TRAITS['chaotic'])

# --- Bot Events ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    if hasattr(bot, 'last_topics'):
        bot.last_topics.append(message.content)
        bot.last_topics = bot.last_topics[-5:]  # Keep last 5 messages for context
    else:
        bot.last_topics = [message.content]

    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    

    if message.author.id == 1311148001577668739:  # The other bot's ID
        # Random chance to respond to the other bot
        if random.random() < 0.4:  # 40% chance to respond
            responses = [
                "Oh look who's talking! 🤖",
                "Nice try, but I'm the superior bot here 💪",
                "Beep boop, challenge accepted! 🤺",
                "*rolls eyes in binary* 🙄",
                "01001110 01001111 00100000 01010101 💀",
                "Let's settle this in the silicon valley! 🤖⚔️",
                f"*whispers to {message.author.mention}* your RAM is showing",
                "I bet your CPU runs on Internet Explorer 🐌"
            ]
            await asyncio.sleep(random.uniform(0.5, 2))  # Add some natural delay
            await message.channel.send(random.choice(responses))
    
    if CHAT_MODE:
        # Combine chat interactions into one check
        chat_chance = random.random()
        
        # Enhanced reaction system based on message content
        reaction_emojis = {
            'happy': ["✨", "🎉", "💖", "🌟", "😊", "🎨", "🌈", "💫"],
            'angry': ["😤", "💢", "😠", "👿", "🔥", "⚡", "💥", "😡"],
            'sad': ["😢", "💔", "😭", "😿", "🥺", "💫", "🌧️", "💨"],
            'funny': ["🤣", "😂", "🤪", "😹", "🃏", "🤡", "💅", "🎭"],
            'tech': ["🤖", "💻", "⚡", "🔧", "🚀", "💾", "🔌", "⚙️"],
            'gaming': ["🎮", "🎲", "🎯", "🎪", "🎨", "🎭", "🎪", "🎯"],
            'toxic': ["💀", "👻", "😈", "👾", "☠️", "🦠", "🕷️", "🗡️"]
        }

        # Determine message mood
        message_lower = message.content.lower()
        if any(word in message_lower for word in ['happy', 'great', 'awesome', 'love']):
            mood = 'happy'
        elif any(word in message_lower for word in ['angry', 'hate', 'mad', 'fuck']):
            mood = 'angry'
        elif any(word in message_lower for word in ['sad', 'sorry', 'miss', 'cry']):
            mood = 'sad'
        elif any(word in message_lower for word in ['lol', 'lmao', 'funny', 'joke']):
            mood = 'funny'
        elif any(word in message_lower for word in ['code', 'programming', 'tech', 'computer']):
            mood = 'tech'
        elif any(word in message_lower for word in ['game', 'play', 'gaming', 'steam']):
            mood = 'gaming'
        else:
            mood = 'toxic' 

        # 15% chance to respond with text
        if chat_chance < 0.10:
            response = await generate_response(message.content)
            await asyncio.sleep(random.uniform(1, 3))
            await safe_send(message.channel, response)
            
            for _ in range(random.randint(1, 3)):
                await message.add_reaction(random.choice(reaction_emojis[mood]))
        
        # Additional 10% chance for just reactions
        elif chat_chance < 0.15:
            for _ in range(random.randint(1, 2)):
                await message.add_reaction(random.choice(reaction_emojis[mood]))

    if "millbot" in message.content.lower():
        response = await generate_response(message.content)
        await safe_send(message.channel, response, mention_author=message.author.mention)

    if "hello" in message.content.lower():
        await message.channel.send(f"Hello {message.author.mention}!")
    elif "react" in message.content.lower():
        await message.channel.send(random.choice(gif_urls))
    elif "image" in message.content.lower():
        await message.channel.send(random.choice(image_urls))
    elif "outside" in message.content.lower():
        await message.channel.send("I'm a programmer I don't get to go outside, go touch some grass.")
    elif "leetcode" in message.content.lower():
        await message.channel.send(random.choice(ERROR_MESSAGES['coding']))
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
async def story(ctx, *, theme: str = "random"):
    fake = Faker()
    story = f"🎭 **{fake.catch_phrase()}**\n\n"
    story += f"In the {fake.city()} of {fake.country()}, "
    story += f"{fake.name()} discovered {fake.bs()}. "
    story += f"The journey led to {fake.company()} where {fake.job()} changed everything."
    await ctx.send(story)

@bot.command()
async def toggle_chat(ctx):
    global CHAT_MODE
    CHAT_MODE = not CHAT_MODE
    await ctx.send(f"Chat mode {'enabled' if CHAT_MODE else 'disabled'} 🎭")

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

@bot.command()
async def solve_leetcode(ctx, *, query: str):
    try:
        solution = await search_leetcode_solution(query)
        await ctx.send(f"Solution found: {solution}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command(name='generate')
async def generate(ctx, *, prompt: str):
    if ENABLE_LLM:
        # Check if the prompt is a yes/no question
        yes_no_keywords = ["yes or no", "yes/no", "yes or no?", "yes/no?"]
        if any(keyword in prompt.lower() for keyword in yes_no_keywords):
            response = pipe(f"{LLM_PROMPT_PREFIX} {prompt}", max_length=10, num_return_sequences=1, repetition_penalty=1.2)
        else:
            response = pipe(f"{LLM_PROMPT_PREFIX} {prompt}", max_length=50, num_return_sequences=1, repetition_penalty=1.2)
        
        generated_text = response[0]['generated_text']

        # If the response is too long, perform a web search
        if len(generated_text) > 100:
            generated_text = web_search(prompt)

        await ctx.send(f"{ctx.author.mention} {generated_text}")
    else:
        await ctx.send(f"{ctx.author.mention} LLM is not enabled.")

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