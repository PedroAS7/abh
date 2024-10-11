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

from abh.src.chat import Chat
from abh.src.consts import Emojis
from abh.src.updates.parser import TelegramUpdateParser
import telegram


class TelegramMemberUpdatedParser(TelegramUpdateParser):

    def can_handle(self, update: telegram.Update) -> bool:
        return update.effective_chat         \
            and update.effective_user        \
            and update.my_chat_member        \
            and not update.effective_message
    # end def

    async def parse(self, update: telegram.Update, app: object):
        bot = update._bot

        # Bot has been added
        if update.my_chat_member.new_chat_member.user == app.bot_user \
        and (not update.my_chat_member.old_chat_member
             or update.my_chat_member.old_chat_member.status == telegram.constants.ChatMemberStatus.LEFT):

            # First time it's been added
            if not app.has_chat(update.effective_chat.id):
                # Adder is admin
                new_chat = Chat(update.effective_chat.id, [update.effective_user.id])
                app.add_chat(new_chat)
                await bot.send_message(update.effective_chat.id,
                                       f"Hi {Emojis.WAVE.value}! Thanks for adding me! Let one of the admins configure me by typing {bot.name}")
            # end if
        # end if
    # end def
# end class
