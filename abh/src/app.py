from time import sleep
from abh.src.ManagedThread import ManagedThread
from abh.src.chat import Chat
from abh.src.cmds.botCommand import BotCommand
from abh.src.cmds.msg.aboutCommand import AboutCommand
from abh.src.cmds.msg.configureCommand import ConfigureMsgCommand
from abh.src.cmds.msg.latestInfoCommand import LatestInfoCommand
from abh.src.cmds.msg.statusCommand import StatusCommand
from abh.src.config import Config
from abh.src.config import ConfigKeyType
from abh.src.scrapers.cme import CmeScraper
from abh.src.scrapers.flares import FlaresScraper
from abh.src.scrapers.geomag import GeomagScraper
from abh.src.scrapers.scraper import Scraper
from abh.src.updates.listener import BotListener
from abh.src.updates.parser import TelegramUpdateParser
from abh.src.updates.messageReceiveParser import TelegramMessageReceiveParser
from abh.src.updates.memberUpdatedParser import TelegramMemberUpdatedParser
from abh.src.updates.inlineQueryParser import TelegramInlineQueryParser
from abh.src.updates.inlineResponseParser import TelegramInlineResponseParser
from abh.src.log import *
from os import mkdir
from os.path import join
from os.path import exists
from traceback import format_exc
from abh.src.updates.alerter import Alerter
import pickle
import telegram
import asyncio
import signal



# --
# Classes
# --


class BotApp:
    _DB_FOLDER = "data"
    _DB_FILENAME = join(_DB_FOLDER, "chats.bin")
    _APP = None

    def __init__(self) -> None:
        self.bot_user: telegram.User | None = None
        self.chats: list[Chat] = []
        self.handlers: list[TelegramUpdateParser] = [
            TelegramMessageReceiveParser(),
            TelegramMemberUpdatedParser(),
            TelegramInlineQueryParser(),
            TelegramInlineResponseParser()
        ]
        self.commands: list[BotCommand] = [
            AboutCommand(),
            ConfigureMsgCommand(),
            LatestInfoCommand(),
            StatusCommand()
        ]
        self.scrapers: list[Scraper] = []
        self.debug_mode: bool = False
    # end def

    def has_chat(self, uid: int) -> bool:
        found_chat = None
        for chat in self.chats:
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

        self.chats.append(chat)

    # end def

    def get_chat(self, uid: int) -> Chat:

        found_chat = None
        for chat in self.chats:
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
        if not exists(self._DB_FOLDER):
            mkdir(self._DB_FOLDER)
        # end if

        with open(BotApp._DB_FILENAME, "wb") as db_file:
            pickle.dump(self.chats, db_file)
        # end with

    # end def

    def get_handler(self, update: telegram.Update) -> TelegramUpdateParser:
        found_handler = None
        for handler in self.handlers:
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

    def add_scraper(self, scraper: Scraper):
        self.scrapers.append(scraper)
    # end def

    @staticmethod
    def singleton() -> 'BotApp':
        return BotApp._APP

    # end def

    @staticmethod
    def read() -> object:
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

        BotApp._APP.chats = read_chat_list
    # end def


# end class


# --
# Functions
# --

def graceful_stop(threads: list, bot_loop) -> None:

    for thread in threads:
        thread.stop_thread()
    # end for

    singleton = BotApp.singleton()
    if singleton:
        singleton.write()
    # end if

    if bot_loop:
        bot_loop.close()
    # end if

    project()
    log("")
    log("Bot has stopped")
    exit(0)
# end def

async def serve_forever(cfg: Config) -> None:
    bot: telegram.Bot | None = None
    app = BotApp.singleton()

    try:
        bot = telegram.Bot(cfg[ConfigKeyType.BOT_TOKEN], local_mode=True)
        await bot.initialize()
        app.bot_user = await bot.get_me()
        listener_thread = BotListener(app, bot, None)
        listener_thread.run_thread()

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

    threads: list[ManagedThread] = []

    # noinspection PyBroadException
    bot_loop = None
    try:
        signal.signal(signal.SIGINT, lambda _1,_2: graceful_stop(threads, bot_loop))
        signal.signal(signal.SIGTERM, lambda _1,_2: graceful_stop(threads, bot_loop))
        
        BotApp.read()
        cfg = Config.read()
        BotApp.singleton().debug_mode = cfg[ConfigKeyType.DEBUG_MODE]
        bot = telegram.Bot(cfg[ConfigKeyType.BOT_TOKEN], local_mode=True)
        
        bot_loop = asyncio.new_event_loop()
        bot_loop.run_until_complete(bot.initialize())
        BotApp.singleton().bot_user = bot_loop.run_until_complete(bot.get_me())

        flares_scraper = FlaresScraper()
        BotApp.singleton().add_scraper(flares_scraper)
        threads.append(flares_scraper)

        geomag_scraper = GeomagScraper()
        BotApp.singleton().add_scraper(geomag_scraper)
        threads.append(geomag_scraper)

        cme_scraper = CmeScraper()
        BotApp.singleton().add_scraper(cme_scraper)
        threads.append(cme_scraper)

        alerter_loop = asyncio.new_event_loop()
        threads.append(Alerter(BotApp.singleton(), alerter_loop))

        threads.append(BotListener(BotApp.singleton(), bot, bot_loop))

        for thread in threads:
            thread.run_thread()
        # end for

        # Eternally sleep until an exception happened or Ctrl + C was hit
        while True:
            sleep(1)
        # end while

    except KeyboardInterrupt:
        log("Stop requested")

    except Exception:
        error(format_exc())

    finally:
        graceful_stop(threads, bot_loop)
    # end try
# end def
