from abh.src.cmds.botCommand import BotCommand
from abh.src.consts import SolarFlareClass
from enum import IntEnum
import telegram


class ConfigureMsgCommand(BotCommand):

    def __init__(self) -> None:
        super().__init__("configure",
                         "Configure bot",
                         False,
                         True)
    # end def

    def run(self, update: telegram.Update, app: object, *args):
        pass
    # end def

    def get_interactive_choices(self, command_args: list[str] | None = None) -> tuple[str | None, telegram.InlineKeyboardMarkup | None]:
        
        prompt = "Please choose:"
        ret_val = None

        if not command_args:
            prompt = "What setting would you like to configure?"
            ret_val = telegram.InlineKeyboardMarkup([
                [
                    telegram.InlineKeyboardButton("Send updates", callback_data=f"{self.cmd} updates")
                ],
                [
                    telegram.InlineKeyboardButton("Predict time", callback_data=f"{self.cmd} predict"),
                    telegram.InlineKeyboardButton("Hemisphere", callback_data=f"{self.cmd} hemisphere")
                ],
                [
                    telegram.InlineKeyboardButton("Include data", callback_data=f"{self.cmd} data"),
                    telegram.InlineKeyboardButton("Include images", callback_data=f"{self.cmd} hemisphere")
                ],
                [
                    telegram.InlineKeyboardButton("Flare class trigger", callback_data=f"{self.cmd} class"),
                    telegram.InlineKeyboardButton("Geomagnetic trigger", callback_data=f"{self.cmd} geomag")
                ],
            ])

        elif len(command_args) == 1:
            match command_args[0]:
                case "hemisphere":
                    prompt = "What hemisphere's events should trigger alerts?"
                    ret_val = telegram.InlineKeyboardMarkup([[
                        telegram.InlineKeyboardButton("Northern", callback_data=f"{self.cmd} hemisphere north"),
                        telegram.InlineKeyboardButton("Southern", callback_data=f"{self.cmd} hemisphere south"),
                        telegram.InlineKeyboardButton("Both hemispheres", callback_data=f"{self.cmd} hemisphere both")
                    ]])

                case "class":
                    prompt = "What minimum solar flare class should trigger alerts?"
                    flare_help = SolarFlareClass.get_help()
                    for key in flare_help:
                        prompt += f"\n{SolarFlareClass(key).name} = {flare_help[key]}"
                    # end for

                    ret_val = telegram.InlineKeyboardMarkup([[
                        telegram.InlineKeyboardButton(flare_class.name, callback_data=f"{self.cmd} class {flare_class.value}")
                            for flare_class in SolarFlareClass
                    ]])
            # end match
        # end with

        return prompt, ret_val
    # end def
# end class
