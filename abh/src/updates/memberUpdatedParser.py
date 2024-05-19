from abh.src.chat import Chat
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
                                       "Hi \U0001F44B! Thanks for adding me! Let one of the admins configure me by @ me, followed by 'setup'")
            # end if
            
            await update.effective_sender.send_dice()
        # end if
    # end def
# end class
