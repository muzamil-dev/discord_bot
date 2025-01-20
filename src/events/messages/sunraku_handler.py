import datetime
from datetime import timezone
import random
from src.utils import send_message_with_retry, get_random_error_message # type: ignore
from src.utils.state_manager import get_toggle_sunraku
import logging

sunraku_timeouts = {}

async def handle_sunraku(message):
    logging.debug("Entered handle_sunraku")
    if not get_toggle_sunraku():
        logging.debug("Sunraku events disabled")
        return
        
    sunraku_id = 1207552021385969675
    sunraku = message.guild.get_member(sunraku_id)
    if sunraku:
        try:
            current_timeout = sunraku_timeouts.get(sunraku_id, datetime.timedelta())
            additional_timeout = datetime.timedelta(minutes=random.randint(1, 5))
            new_timeout = current_timeout + additional_timeout
            
            timeout_until = datetime.datetime.now(timezone.utc) + new_timeout
            await sunraku.edit(timed_out_until=timeout_until)
            
            sunraku_timeouts[sunraku_id] = new_timeout
            timeout_minutes = new_timeout.total_seconds() // 60
            
            await send_message_with_retry(message.channel, f"⏳ {sunraku}'s timeout has been increased by {additional_timeout}. New timeout: {timeout_minutes} minutes.")
            logging.info(f"Timed out {sunraku.display_name} for {timeout_minutes} minutes by {message.author}")
        except Exception as e:
            await send_message_with_retry(message.channel, get_random_error_message('timeout'))
            logging.error(f"Error timing out sunraku: {str(e)}")
    else:
        logging.error(f"Sunraku member not found in the guild")