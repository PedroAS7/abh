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

from abh.src.ManagedThread import ManagedThread
from abh.src.chat import Chat
from abh.src.cmds.botCommand import BotCommand
from abh.src.cmds.msg.aboutCommand import AboutCommand
from abh.src.cmds.msg.configureCommand import ConfigureMsgCommand
from abh.src.cmds.msg.latestInfoCommand import LatestInfoCommand
from abh.src.cmds.msg.statusCommand import StatusCommand
from abh.src.config import Config
from abh.src.config import ConfigKeyType
from abh.src.scrapers.scraper import Scraper
from abh.src.updates.listener import BotListener
from abh.src.updates.parser import TelegramUpdateParser
from abh.src.updates.messageReceiveParser import TelegramMessageReceiveParser
from abh.src.updates.memberUpdatedParser import TelegramMemberUpdatedParser
from abh.src.updates.inlineQueryParser import TelegramInlineQueryParser
from abh.src.updates.inlineResponseParser import TelegramInlineResponseParser
from abh.src.log import *
from os.path import join
from os.path import exists
from traceback import format_exc
import pickle
import telegram


# --
# Classes
# --


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
    def singleton() -> object:
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

        BotApp._APP._chats = read_chat_list
    # end def


# end class


# --
# Functions
# --

async def serve_forever(cfg: Config) -> None:
    bot: telegram.Bot | None = None
    app = BotApp.singleton()

    try:
        bot = telegram.Bot(cfg[ConfigKeyType.BOT_TOKEN], local_mode=True)
        await bot.initialize()
        app._bot_user = await bot.get_me()
        listener_thread = BotListener(app, bot)
        listener_thread.run_thread()

    except Exception:
        error(format_exc())

    finally:
        if bot:
            await bot.shutdown()
        # end if
    # end try
# end def


async def run() -> None:
    log("ABH - Aurora Borealis Hunterus bot")
    log("(Also known as C\xe9line.bot)")
    log("")
    indent()

    threads: list[ManagedThread] = []

    # noinspection PyBroadException
    try:
        BotApp.read()
        cfg = Config.read()
        BotApp.singleton().debug_mode = cfg[ConfigKeyType.DEBUG_MODE]
        bot = telegram.Bot(cfg[ConfigKeyType.BOT_TOKEN], local_mode=True)
        await bot.initialize()
        BotApp.singleton()._bot_user = await bot.get_me()

        threads.append(Scraper())
        threads.append(BotListener(BotApp.singleton(), bot))

        for thread in threads:
            thread.run_thread(None)
        # end for

    except KeyboardInterrupt:
        log("Ctrl + C detected")

    except Exception:
        error(format_exc())

    finally:

        for thread in threads:
            thread.stop_thread()
        # end for

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
