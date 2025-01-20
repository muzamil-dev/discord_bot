from discord.ext import commands # type: ignore
from src.utils.state_manager import ( # type: ignore
    get_chat_mode, set_chat_mode,
    get_reece_enable, set_reece_enable,
    get_toggle_bot, set_toggle_bot,
    get_toggle_sunraku, set_toggle_sunraku
)
import logging

class ToggleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def toggle_chat(self, ctx):
        current_mode = get_chat_mode()
        new_mode = not current_mode
        set_chat_mode(new_mode)
        await ctx.send(f"Chat mode {'enabled' if new_mode else 'disabled'} 🎭")
        logging.info(f"{ctx.author} toggled chat mode to {'enabled' if new_mode else 'disabled'}")

    @commands.command()
    async def pingreece(self, ctx):
        current_state = get_reece_enable()
        new_state = not current_state
        set_reece_enable(new_state)
        await ctx.send(f"Ping Reece {'enabled' if new_state else 'disabled'} 🎭")
        logging.info(f"{ctx.author} toggled ping Reece to {'enabled' if new_state else 'disabled'}")

    @commands.command()
    async def toggle_bot(self, ctx):
        allowed_user_ids = [1130226630544068648, 297469573253300224]
        if ctx.author.id in allowed_user_ids:
            current_state = get_toggle_bot()
            new_state = not current_state
            set_toggle_bot(new_state)
            await ctx.send(f"Bot {'enabled 🟢' if new_state else 'disabled 🛑'}")
            logging.info(f"{ctx.author} toggled bot shutdown to {'enabled' if new_state else 'disabled'}")
        else:
            await ctx.send("You do not have permission to use this command.")
            logging.warning(f"{ctx.author} tried to use toggle_bot without permission")

    @commands.command()
    async def toggle_sunraku(self, ctx):
        current_state = get_toggle_sunraku()
        new_state = not current_state
        set_toggle_sunraku(new_state)
        await ctx.send(f"Sunraku events {'enabled' if new_state else 'disabled'} 🌞")
        logging.info(f"{ctx.author} toggled sunraku events to {'enabled' if new_state else 'disabled'}")

async def setup(bot):
    await bot.add_cog(ToggleCommands(bot))