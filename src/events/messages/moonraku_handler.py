import datetime
from datetime import timezone
import random
from src.utils import send_message_with_retry, get_random_error_message # type: ignore
from src.utils.state_manager import get_toggle_sunraku 
import logging

sunraku_timeouts = {}



async def handle_moonraku(message):
    if not get_toggle_sunraku():
        return
        
    sunraku_id = 1207552021385969675
    sunraku = message.guild.get_member(sunraku_id)
    if sunraku:
        try:
            current_time = datetime.datetime.now(timezone.utc)
            timeout_until = sunraku.timed_out_until or current_time
            
            current_timeout = (timeout_until - current_time) if timeout_until > current_time else datetime.timedelta()
            
            reduction_minutes = random.randint(1, 5)
            reduction_timeout = datetime.timedelta(minutes=reduction_minutes)
            
            new_timeout = max(current_timeout - reduction_timeout, datetime.timedelta())
            
            new_timeout_until = current_time + new_timeout if new_timeout > datetime.timedelta() else None
            await sunraku.edit(timed_out_until=new_timeout_until)
            
            sunraku_timeouts[sunraku_id] = new_timeout
            timeout_minutes = new_timeout.total_seconds() / 60
            
            await send_message_with_retry(
                message.channel, 
                f"⏳ {sunraku}'s timeout has been reduced by {reduction_timeout}. New timeout: {timeout_minutes:.1f} minutes."
            )
            logging.info(f"Reduced timeout for {sunraku.display_name} by {reduction_timeout}. New timeout: {timeout_minutes:.1f} minutes by {message.author}")
            
        except Exception as e:
            await send_message_with_retry(message.channel, get_random_error_message('timeout'))
            logging.error(f"Error reducing timeout for sunraku: {str(e)}")
