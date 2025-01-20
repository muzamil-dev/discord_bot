import random 
from src.utils import send_message_with_retry # type: ignore
import logging

def randomize_case(text):
    return ''.join(random.choice([char.upper(), char.lower()]) for char in text)

async def handle_love_millbot(message, cool_emojis):
    num_emojis = random.randint(3, 6)
    emojis = ''.join(random.choices(cool_emojis, k=num_emojis))
    await send_message_with_retry(message.channel, f"I love millbot {emojis}")
    logging.info(f"Responded to 'i love millbot' from {message.author}")

async def handle_millbot_nerd(message):
    nerdy_response = "🤓MiLlBoT NeRd"
    
    if message.reference and message.reference.message_id:
        replied_message = await message.channel.fetch_message(message.reference.message_id)
        await replied_message.add_reaction("🤓")
        quoted_sentence = randomize_case(replied_message.content)
        nerdy_response += f": \"{quoted_sentence}\""
    elif '"' in message.content:
        start = message.content.find('"') + 1
        end = message.content.rfind('"')
        quoted_sentence = message.content[start:end]
        quoted_sentence = randomize_case(quoted_sentence)
        nerdy_response += f": \"{quoted_sentence}\""

    await send_message_with_retry(message.channel, nerdy_response)
    logging.info(f"Responded to 'millbot nerd' from {message.author}")
