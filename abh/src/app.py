from abh.src.chat                           import Chat
from abh.src.cmds.botCommand                import BotCommand
from abh.src.cmds.msg.aboutCommand          import AboutCommand
from abh.src.cmds.msg.configureCommand      import ConfigureMsgCommand
from abh.src.cmds.msg.latestInfoCommand     import LatestInfoCommand
from abh.src.cmds.msg.statusCommand         import StatusCommand
from abh.src.config                         import Config
from abh.src.config                         import ConfigKeyType
from abh.src.scrapers.scraper               import Scraper
from abh.src.updates.parser                 import TelegramUpdateParser
from abh.src.updates.messageReceiveParser   import TelegramMessageReceiveParser
from abh.src.updates.memberUpdatedParser    import TelegramMemberUpdatedParser
from abh.src.updates.inlineQueryParser      import TelegramInlineQueryParser
from abh.src.updates.inlineResponseParser   import TelegramInlineResponseParser
from abh.src.log                            import *
from os.path                                import join
from os.path                                import exists
from sys                                    import version_info
from traceback                              import format_exc
import asyncio
import pickle
import telegram

if version_info.major == 3 and version_info.minor > 11:
    from typing import Self
else:
    from typing_extensions import Self
# end if



#--
# Classes
#--

class BotApp():

    _DB_FILENAME = join("data", "chats.bin")
    _APP = None

    def __init__(self) -> None:
        self._bot_user: telegram.User = None
        self._chats: list[Chat] = []
        self._handlers: list[TelegramUpdateParser] = [
            TelegramMessageReceiveParser(),
            TelegramMemberUpdatedParser(),
            TelegramInlineQueryParser(),
            TelegramInlineResponseParser()
        ]
        self._commands: list[BotCommand] = [
            AboutCommand(),
            ConfigureMsgCommand(),
            LatestInfoCommand(),
            StatusCommand()
        ]
        self.debug_mode: bool = False
        self.scraper = Scraper()

        # Start scraper
        self.scraper.load_history()
        self.scraper.run_thread()
    # end def

    def stop(self):
        self.scraper.save_history()
        self.scraper.stop_thread()
    # end def

    def has_chat(self, uid: int) -> bool:
        found_chat = None
        for chat in self._chats:
            if chat.uid == uid:
                found_chat = chat
                break
            # end if
        # end for

        return True if found_chat else False
    # end def

    def add_chat(self, chat: Chat) -> None:
        if self.has_chat(chat.uid):
            raise ValueError("Chat already added to bot instance")
        # end if

        self._chats.append(chat)
    # end def

    def get_chat(self, uid: int) -> Chat:

        found_chat = None
        for chat in self._chats:
            if chat.uid == uid:
                found_chat = chat
                break
            # end if
        # end for

        if not found_chat:
            found_chat = Chat(uid, [])
            self.add_chat(found_chat)
        # end if

        return found_chat
    # end def

    def write(self) -> None:
        with open(BotApp._DB_FILENAME, "wb") as db_file:
            pickle.dump(self._chats, db_file)
        # end with
    # end def

    def get_handler(self, update: telegram.Update) -> TelegramUpdateParser:
        found_handler = None
        for handler in self._handlers:
            if handler.can_handle(update):
                found_handler = handler
                break
            # end if
        # end for

        if not found_handler:
            raise RuntimeError("No handler for this type of update")
        # end if

        return found_handler
    # end def

    def get_command(self, cmd: str) -> BotCommand:
        found_command = None
        for command in self.commands:
            if command.cmd == cmd.lower():
                found_command = command
                break
            # end for
        # end for

        if not found_command:
            raise ValueError("Invalid command")
        # end if

        return found_command
    # end def

    @property
    def bot_user(self) -> telegram.User:
        return self._bot_user
    # end def

    @property
    def commands(self) -> list[BotCommand]:
        return self._commands[:]
    # end def

    @staticmethod
    def singleton() -> Self:
        return BotApp._APP
    # end def

    @staticmethod
    def read() -> Self:
        BotApp._APP = BotApp()

        # Fresh start
        if not exists(BotApp._DB_FILENAME):
            return
        # end if

        read_chat_list = None
        with open(BotApp._DB_FILENAME, "rb") as db_file:
            read_chat_list = pickle.load(db_file)
            if not isinstance(read_chat_list, list):
                raise ValueError("Invalid bot DB file")
            # end if
        # end with

        BotApp._APP._chats = read_chat_list
    # end def
# end class


#--
# Functions
#--

async def serve_bot(bot: telegram.Bot) -> None:

    bot_me = await bot.get_me()
    app: BotApp = BotApp.singleton()
    next_id = 0
            
    log(f"ID:\t\t\t{bot_me.id}")
    log(f"Name:\t\t\t{bot_me.full_name} ( @{bot_me.username} )")
    log(f"Can join groups:\t{'Yes' if bot_me.can_join_groups else 'No'}")
    log(f"Can read all msg:\t{'Yes' if bot_me.can_read_all_group_messages else 'No'}")
    log("Bot is ready to get Telegram updates")
    
    while True:
        updates = await bot.get_updates(offset=next_id,
                                        timeout=60.0,
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


async def serve_forever(cfg: Config) -> None:

    bot: telegram.Bot | None = None
    app = BotApp.singleton()

    try:
        bot = telegram.Bot(cfg[ConfigKeyType.BOT_TOKEN], local_mode=True)
        await bot.initialize()
        app._bot_user = await bot.get_me()
        bot_serve = asyncio.create_task(serve_bot(bot))
        await bot_serve
        
    except Exception:
        error(format_exc())

    finally:
        if bot:
            await bot.shutdown()
        # end if
    # end try

# end def


def run() -> None:

    log("ABH - Aurora Borealis Hunterus bot")
    log("(Also known as C\xe9line.bot)")
    log("")
    indent()

    try:
        BotApp.read()
        cfg = Config.read()
        BotApp.singleton().debug_mode = cfg[ConfigKeyType.DEBUG_MODE]
        asyncio.run(serve_forever(cfg))

    except KeyboardInterrupt:
        log("Ctrl + C detected")

    except Exception:
        error(format_exc())

    finally:
        singleton = BotApp.singleton()
        if singleton:
            singleton.write()
            singleton.stop()
        # end if
        project()
        log("")
        log("Bot has stopped")
    # end try
# end def
