from src.utils import send_message_with_retry # type: ignore
import logging

async def handle_hello(message):
    await send_message_with_retry(message.channel, f"Hello {message.author.mention}!")
    logging.info(f"Responded to 'hello' from {message.author}")
