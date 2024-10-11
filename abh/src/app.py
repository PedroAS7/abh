"""
Copyright 2024 PeterAS17 (www.peteras17.me)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


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
