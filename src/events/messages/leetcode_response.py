from src.utils import send_message_with_retry # type: ignore
import logging

async def handle_leetcode(message):
    await send_message_with_retry(message.channel, "Just compile the fries into the bag bro")
    logging.info(f"Responded to 'leetcode' from {message.author}")
