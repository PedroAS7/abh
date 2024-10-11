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

from uuid import uuid4
from abh.src.updates.parser import TelegramUpdateParser
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent
import telegram


class TelegramInlineQueryParser(TelegramUpdateParser):

    def can_handle(self, update: telegram.Update) -> bool:
        return update.effective_user \
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
