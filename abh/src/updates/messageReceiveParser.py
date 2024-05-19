from abh.src.updates.parser import TelegramUpdateParser
from abh.src.log            import *
from traceback              import format_exc
import telegram
import shlex


class TelegramMessageReceiveParser(TelegramUpdateParser):

    def can_handle(self, update: telegram.Update) -> bool:
        return update.effective_user        \
            and update.message              \
            and not update.message_reaction \
            and not update.business_message \
            and not update.poll             \
            and not update.poll_answer      \
            and not update.chat_boost       \
            and not update.removed_chat_boost \
            and not update.message.left_chat_member \
            and not update.message.new_chat_members
    # end def

    async def parse(self, update: telegram.Update, app: object):
        # Inline query sent
        if update.message.via_bot == app.bot_user:
            
            try:
                cmd = app.get_command(update.message.text)
                cmd_parts = shlex.split(update.message.text)
                prompt, choices, delete_msg = cmd.get_interactive_choices(cmd_parts[1:])

                if choices:
                    await update.message.reply_text(prompt, reply_markup=choices)
                else:
                    await cmd.run(update, app, *cmd_parts)
                # end if
                
                if delete_msg:
                    await update.message.delete()
                # end if
            except ValueError:
                await update.message.reply_text("Invalid command!")

                if app.debug_mode:
                    error(format_exc())
                # end if
            # end try

        else:
            await update.message.reply_text(f"Please use the interactive menu by typing {app.bot_user.name}")
        # end if
    # end def
# end class
