import logging
from discord.ext import commands # type: ignore

async def setup_error_handler(bot):
    @bot.event
    async def on_command_error(ctx, error):
        command_content = ctx.message.content if ctx.message else "Unknown command"
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Please use a valid command.")
            logging.error(f"Command not found: {command_content}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
            logging.error(f"Missing required argument: {error.param.name} for command: {command_content}")
        else:
            await ctx.send(f"An error occurred: {str(error)}")
            logging.error(f"An error occurred with command '{command_content}': {str(error)}")