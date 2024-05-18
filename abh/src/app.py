from abh.src.config import Config
from abh.src.config import ConfigKeyType
from abh.src.log import *
from traceback import format_exc
import telegram
import asyncio


#--
# Functions
#--

async def serve_bot(bot: telegram.Bot) -> None:

    next_id = 0
    

    while True:
        updates = await bot.get_updates(offset=next_id, timeout=60.0)

        if len(updates) == 0:
            continue
        # end if
        
        for update in updates:
            log(update)
            next_id = max(next_id, update.update_id + 1)
        # end for
    # end while
# end def


async def serve_forever(cfg: Config) -> None:

    bot: telegram.Bot | None = None
    try:
        bot = telegram.Bot(cfg[ConfigKeyType.BOT_TOKEN])
        bot_me = await bot.get_me()
            
        log(f"ID:\t\t\t{bot_me.id}")
        log(f"Name:\t\t\t{bot_me.full_name} ( @{bot_me.username} )")
        log(f"Can join groups:\t{'Yes' if bot_me.can_join_groups else 'No'}")
        log(f"Can read all msg:\t{'Yes' if bot_me.can_read_all_group_messages else 'No'}")
        
        bot_serve = asyncio.create_task(serve_bot(bot))
        await bot_serve
        
    except Exception:
        error(format_exc())

    finally:
        if bot:
            await bot.shutdown()
            await bot.log_out()
            await bot.close()
        # end if
    # end try

# end def


def run() -> None:

    log("ABH - Aurora Borealis Hunteurs bot")
    log("(Also known as C\xe9line.bot)")
    log("")
    indent()

    try:
        cfg = Config.read()
        asyncio.run(serve_forever(cfg))

    except KeyboardInterrupt:
        log("Ctrl + C detected")

    finally:
        project()
        log("")
        log("Bot has stopped")
    # end try
# end def
