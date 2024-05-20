from abh.src.cmds.botCommand import BotCommand
from abh.src.consts import Emojis
from abh.src.log import *
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
