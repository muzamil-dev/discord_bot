from .fun.dox_command import setup as setup_dox
from .fun.dice_command import setup as setup_dice
from .fun.coin_command import setup as setup_coin
from .fun.meme_command import setup as setup_meme
from .fun.spam_command import setup as setup_spam # type: ignore
from .quotes.lotr_command import setup as setup_lotr
from .quotes.inspire_command import setup as setup_inspire
from .system.toggle_commands import setup as setup_toggles
from .system.list_commands import setup as setup_list
from .utility.remind_command import setup as setup_remind # type: ignore


async def setup_all_commands(bot):
    await setup_dox(bot)
    await setup_dice(bot)
    await setup_coin(bot)
    await setup_meme(bot)
    await setup_lotr(bot)
    await setup_inspire(bot)
    await setup_toggles(bot)
    await setup_list(bot)
    await setup_remind(bot)
    await setup_spam(bot)