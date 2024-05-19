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

    def run(self,
            update: telegram.Update,
            app: object,
            *args):
        raise NotImplementedError("Command did not override run method")
    # end def

    def get_interactive_choices(self, command_start: str | None = None) -> tuple[str | None, telegram.InlineKeyboardMarkup | None]:
        return None, None
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
