from uuid import uuid4
from abh.src.updates.parser import TelegramUpdateParser
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent
from telegram.constants import ParseMode
import telegram
from html import escape
import shlex


class TelegramInlineResponseParser(TelegramUpdateParser):

    def can_handle(self, update: telegram.Update) -> bool:
        return update.callback_query
    # end def

    async def parse(self, update: telegram.Update, app: object):
        
        msg = update.callback_query.data
        msg_parts = shlex.split(msg)
       
        if not len(msg_parts):
            update.callback_query.answer("Invalid command!")
            return
        # end if
        
        try:
            cmd = app.get_command(msg_parts[0])
            prompt, choices = cmd.get_interactive_choices(msg_parts[1:])

            if choices:
                if update.callback_query.message and hasattr(update.callback_query.message, "reply_text"):
                    await update.callback_query.message.reply_text(prompt, reply_markup=choices)
                else:
                    await update.callback_query.answer("Invalid command")
                # end if
            else:
                cmd.run(update, app, msg_parts)
            # end if
        except ValueError as exe:
            await update.callback_query.answer("Invalid command")
        # end try
    # end def
# end class
