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

from abh.src.cmds.botCommand import BotCommand
from abh.src.consts import Emojis
import telegram

class StatusCommand(BotCommand):

    def __init__(self) -> None:
        super().__init__("status",
                         f"{Emojis.GRAPH.value} Bot status",
                         False,
                         True)
    # end def

    async def run(self,
                  update: telegram.Update,
                  app: object,
                  *args) -> None:
        await super().run(update, app, *args)
        
        if len(args) != 1:
            await update.message.reply_text("Invalid command!")
        else:
            # TODO: show bot status
            pass
        # end if
    # end def
# end class
