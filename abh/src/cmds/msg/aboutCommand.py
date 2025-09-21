import telegram

from abh.src import (APP_NAME,
                     APP_AUTHORS,
                     APP_VERSION,
                     APP_WEBSITE)
from abh.src.cmds.botCommand import BotCommand
from abh.src.consts import Emojis


class AboutCommand(BotCommand):

    def __init__(self) -> None:
        super().__init__("about",
                         f"{Emojis.QUESTION.value} About",
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
            reply_message = f"""
{APP_NAME} version {APP_VERSION}
Created by {','.join(APP_AUTHORS)}
Project information at {APP_WEBSITE}
"""
            await update.message.reply_text(reply_message)
        # end if
    # end def
# end class
