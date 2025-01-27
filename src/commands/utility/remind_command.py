from discord.ext import commands # type: ignore
import time
import logging
from datetime import datetime, timedelta
from dateutil import parser # type: ignore
from src.features.reminder.reminder_manager import save_reminder, schedule_reminder, get_user_reminders, remove_reminder 

class RemindCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remindme', help='Sets a reminder for a specified time or date')
    async def remind(self, ctx, time_str: str, *, reminder_text: str):
        """Sets a reminder for a specified time or date
        Usage: !remindme 1h30m Check the oven
               !remindme on 31st Check the oven
               !remindme on 5/23 Check the oven
               !remindme on 4/6/2026 Check the oven"""
        
        total_seconds = 0
        time_units = {'y': 31536000, 'mo': 2592000, 'd': 86400, 'h': 3600, 'm': 60, 's': 1}

        if time_str.startswith('on '):
            date_str = time_str[3:]
            try:
                # Parse the date string using dateutil.parser
                reminder_date = parser.parse(date_str, fuzzy=True, default=datetime.now())
                
                current_time = datetime.now()
                if reminder_date < current_time:
                    reminder_date = reminder_date.replace(year=current_time.year + 1)
                    
                # Convert to Unix timestamp
                total_seconds = (reminder_date.timestamp() - current_time.timestamp())
            except (ValueError, OverflowError) as e:
                await ctx.send("Invalid date format. Please use a format like 'on 31st', 'on 5/23', or 'on 4/6/2026'.")
                logging.error(f"Invalid date format: {date_str} - {str(e)}")
                return

        else:
            current = ''
            i = 0
            while i < len(time_str):
                if time_str[i].isdigit():
                    current += time_str[i]
                else:
                    if i + 1 < len(time_str) and time_str[i:i+2] in time_units:
                        total_seconds += int(current or 0) * time_units[time_str[i:i+2]]
                        i += 1
                    elif time_str[i] in time_units:
                        total_seconds += int(current or 0) * time_units[time_str[i]]
                    current = ''
                i += 1

        if total_seconds > 0:
            reminder = {
                'channel_id': ctx.channel.id,
                'user_id': ctx.author.id,
                'user_mention': ctx.author.mention,
                'text': reminder_text,
                'time': time.time() + total_seconds
            }
            
            save_reminder(reminder)
            self.bot.loop.create_task(schedule_reminder(self.bot, reminder, total_seconds))
            await ctx.send(f"I'll remind you about '{reminder_text}' on {reminder_date.strftime('%Y-%m-%d %H:%M:%S')}" if time_str.startswith('on ') else f"I'll remind you about '{reminder_text}' in {time_str}")
            logging.info(f"Reminder set by {ctx.author} for {time_str} from now")
        else:
            await ctx.send("Invalid time format. Please use a format like '1y2mo3d4h5m6s' or 'on 31st' or 'on 5/23' or 'on 4/6/2026'.")

    @commands.command(name='showreminds', help='Shows your active reminders and the remaining time')
    async def show_reminds(self, ctx):
        """Shows your active reminders and the remaining time"""
        user_reminders = get_user_reminders(ctx.author.id)
        if not user_reminders:
            await ctx.send("You have no active reminders.")
            return

        reminder_messages = []
        current_time = time.time()
        for reminder in user_reminders:
            remaining_time = reminder['time'] - current_time
            days, remainder = divmod(remaining_time, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            reminder_messages.append(f"Reminder: {reminder['text']} - Time left: {int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s")

        await ctx.send("\n".join(reminder_messages))

    @commands.command(name='delreminds', help='Deletes a specific reminder')
    async def del_reminds(self, ctx, *, reminder_text: str):
        """Deletes a specific reminder
        Usage: !delreminds Check the oven"""
        user_reminders = get_user_reminders(ctx.author.id)
        reminder_to_delete = None
        for reminder in user_reminders:
            if reminder['text'] == reminder_text:
                reminder_to_delete = reminder
                break

        if reminder_to_delete:
            remove_reminder(reminder_to_delete)
            await ctx.send(f"Deleted reminder: {reminder_text}")
            logging.info(f"Deleted reminder: {reminder_text} by {ctx.author}")
        else:
            await ctx.send(f"No reminder found with text: {reminder_text}")

    @remind.error
    async def remind_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'time_str':
                await ctx.send("You need to specify the time for the reminder. Usage: !remindme 1h30m Check the oven")
            elif error.param.name == 'reminder_text':
                await ctx.send("You need to specify the reminder text. Usage: !remindme 1h30m Check the oven")
        else:
            await ctx.send(f"An error occurred: {str(error)}")
            logging.error(f"An error occurred in remindme command: {str(error)}")

async def setup(bot):
    await bot.add_cog(RemindCommand(bot))