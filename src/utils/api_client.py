import asyncio
import discord # type: ignore
import requests # type: ignore
import logging
import json
import random

async def send_message_with_retry(channel, content, max_retries=5):
    for attempt in range(max_retries):
        try:
            await channel.send(content)
            return
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.retry_after if hasattr(e, 'retry_after') else (2 ** attempt)
                logging.warning(f"Rate limited. Retrying in {retry_after} seconds.")
                await asyncio.sleep(retry_after)
            else:
                raise
    logging.error(f"Failed to send message after {max_retries} attempts.")

def get_random_error_message(error_type='general'):
    with open('config/config.json') as config_file:
        config = json.load(config_file)
    return random.choice(config["ERROR_MESSAGES"].get(error_type, config["ERROR_MESSAGES"]['general']))