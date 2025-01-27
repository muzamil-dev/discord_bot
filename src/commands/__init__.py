from .fun.coin_command import setup as setup_coin
from .fun.dice_command import setup as setup_dice
from .fun.dox_command import setup as setup_dox
from .fun.meme_command import setup as setup_meme
from .fun.spam_command import setup as setup_spam
from .fun.shoot_command import setup as setup_shoot 
from .fun.die_command import setup as setup_die 
from .quotes.inspire_command import setup as setup_inspire
from .quotes.lotr_command import setup as setup_lotr
from .system.list_commands import setup as setup_list_commands
from .system.toggle_commands import setup as setup_toggle_commands
from .utility.remind_command import setup as setup_remind

async def setup_all_commands(bot):
    await setup_coin(bot)
    await setup_dice(bot)
    await setup_dox(bot)
    await setup_meme(bot)
    await setup_spam(bot)
    await setup_inspire(bot)
    await setup_lotr(bot)
    await setup_list_commands(bot)
    await setup_toggle_commands(bot)
    await setup_remind(bot)
    await setup_shoot(bot)
    await setup_die(bot)
    return bot
