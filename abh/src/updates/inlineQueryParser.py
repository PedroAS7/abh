from uuid import uuid4
from abh.src.updates.parser import TelegramUpdateParser
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent
from telegram.constants import ParseMode
import telegram
from html import escape


class TelegramInlineQueryParser(TelegramUpdateParser):

    def can_handle(self, update: telegram.Update) -> bool:
        return update.effective_user        \
            and update.inline_query
    # end def

    async def parse(self, update: telegram.Update, app: object):
        
        query = update.inline_query.query
        results = []

        for cmd in app.commands:

            if not cmd.target_msg or not cmd.cmd.startswith(query.lower()):
                continue
            # end for

            results.append(InlineQueryResultArticle(
                id=str(uuid4()),
                title=cmd.title,
                input_message_content=InputTextMessageContent(cmd.cmd),
            ))
        # end for
                
        await update.inline_query.answer(results)
    # end def
# end class
