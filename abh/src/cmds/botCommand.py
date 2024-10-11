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
import telegram


class BotCommand():

    def __init__(self,
                 cmd: str,
                 title: str,
                 target_cli: bool = False,
                 target_msg: bool = True) -> None:
        self._cmd: str = cmd.lower()
        self._title = title
        self._target_cli = target_cli
        self._target_msg = target_msg
    # end def

    async def run(self,
                  update: telegram.Update,
                  app: object,
                  *args) -> None:
        # Update chat admins if needed
        if update.effective_message:
            tg_chat = update.effective_message.chat

            # Private chats don't have admins
            if tg_chat.type == telegram.constants.ChatType.PRIVATE \
            or tg_chat.type == telegram.constants.ChatType.SENDER:
                admins = (tg_chat,)
            else:
                admins = await tg_chat.get_administrators()
            # end if

            chat: Chat = app.get_chat(tg_chat.id)
            chat.update_admins(admins)
        # end if
    # end def

    def get_interactive_choices(self, command_start: str | None = None) \
    -> tuple[str | None, telegram.InlineKeyboardMarkup | None, bool]:
        """
        Returns the choices the user has, in the form of interactive buttons

        @param command_start: (str) First keyword the user entered

        @return (tuple of str/None, InlineKeyboardMarkup/None, bool)
            First index is prompt
            Second index is the list of buttons
            Third button indicates whether the sent message should be deleted
        """
        return None, None, False
    # end def

    @property
    def cmd(self) -> str:
        return self._cmd
    # end def

    @property
    def title(self) -> str:
        return self._title
    # end def

    @property
    def target_cli(self) -> bool:
        return self._target_cli
    # end def

    @property
    def target_msg(self) -> bool:
        return self._target_msg
    # end def
# end def
