from abh.src.config import Config
from abh.src.config import ConfigKeyType
import telegram
import asyncio


async def serve_forever(cfg: Config) -> None:
    
    bot: telegram.Bot = telegram.Bot(cfg[ConfigKeyType.BOT_TOKEN])

    async with bot:
        pass
    # end with

    return 0
# end def


def run() -> None:
    
    print("ABH - Aurora Borealis Hunteurs bot")
    print("(Also known as C\xe9line.bot)")

    try:
        cfg = Config.read()
        asyncio.run(serve_forever(cfg))
    except KeyboardInterrupt:
        print("Ctrl + C detected")
    # end try

    print("Bot has stopped")

# end def
