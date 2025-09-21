from traceback import format_exc

import telegram

from abh.src.thread import ManagedThread
from abh.src.log import *


class BotListener(ManagedThread):

    def __init__(self, bot_app: object, bot: object, loop):
        super().__init__("Listener")
        self._bot: object = bot
        self._app: object = bot_app
        self.loop = loop

    # end def

    def run_thread(self, **kwargs) -> None:
        super().run_thread(_t_start)

    # end def

    @property
    def app(self) -> object:
        return self._app

    # end def

    @property
    def bot(self) -> object:
        return self._bot
    # end def


# end class


def _t_start(listener: BotListener) -> None:
    loop = listener.loop
    loop.run_until_complete(_t_serve_bot(listener))


# end def


async def _t_serve_bot(listener: BotListener) -> None:
    timeout = 1.0
    bot = listener.bot
    bot_me = await bot.get_me()
    app = listener.app
    next_id = 0

    log(f"ID:\t\t\t{bot_me.id}")
    log(f"Name:\t\t\t{bot_me.full_name} ( @{bot_me.username} )")
    log(f"Can join groups:\t{'Yes' if bot_me.can_join_groups else 'No'}")
    log(f"Can read all msg:\t{'Yes' if bot_me.can_read_all_group_messages else 'No'}")
    log("Bot is ready to get Telegram updates")

    while listener.event_wait(0):
        updates = await bot.get_updates(offset=next_id,
                                        timeout=timeout,
                                        allowed_updates=telegram.Update.ALL_TYPES)

        if len(updates) == 0:
            continue
        # end if

        for update in updates:

            try:
                handler = app.get_handler(update)
                await handler.parse(update, app)
            except RuntimeError:
                warn(f"Received unsupported update of type {update.__class__}")

                if app.debug_mode:
                    error(format_exc())
                # end if
            except Exception:
                warn("Failed to respond to update")

                if app.debug_mode:
                    error(format_exc())
                # end if
            # end try

            next_id = max(next_id, update.update_id + 1)
        # end for
    # end while
# end def
