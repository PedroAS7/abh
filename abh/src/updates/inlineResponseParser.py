from abh.src.updates.parser import TelegramUpdateParser
from abh.src.log            import *
from traceback              import format_exc
import telegram
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
            prompt, choices, delete_msg = cmd.get_interactive_choices(msg_parts[1:])

            if choices:
                if update.callback_query.message and hasattr(update.callback_query.message, "reply_text"):
                    await update.callback_query.message.reply_text(prompt, reply_markup=choices)
                    await update.callback_query.answer()
                else:
                    await update.callback_query.answer("Invalid command")
                # end if
            else:
                await cmd.run(update, app, *msg_parts)
                await update.callback_query.answer()
            # end if

            if delete_msg and update.callback_query.message:
                await update.callback_query.message.delete()
            # end if
        except ValueError:
            await update.callback_query.answer("Invalid command")

            if app.debug_mode:
                error(format_exc())
            # end if
        # end try
    # end def
# end class
