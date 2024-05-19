from abh.src.chat import Chat
from abh.src.cmds.botCommand import BotCommand
from abh.src.consts import Emojis, SolarFlareClass
from abh.src.consts import GeomagStormIndex
from abh.src.log import *
from enum import Enum
import telegram


class _SubCmd(Enum):
    SEND_UPDATES      = "update"
    PREDICT_TIME      = "predict"
    CHOOSE_HEMISPHERE = "hemisphere"
    INCLUDE_DATA      = "data"
    INCLUDE_IMAGES    = "images"
    FLARE_CLASS       = "class"
    GEOMAG_INTENSITY  = "geomag"
# end class


class _HemisphereChoices(Enum):
    NORTH             = "north"
    SOUTH             = "south"
    BOTH              = "both"
# end class


class ConfigureMsgCommand(BotCommand):

    _CMD_INDEX        = 0
    _SUBCMD_INDEX     = 1
    _ARGS_INDEX       = 2

    def __init__(self) -> None:
        super().__init__("configure",
                         f"{Emojis.WRENCH.value} Configure bot",
                         False,
                         True)

        self.cmd_handlers = {
            _SubCmd.SEND_UPDATES.value: self._run_send_updates
            }
    # end def

    async def _run_send_updates(self,
                                update: telegram.Update,
                                app: object,
                                chat: Chat,
                                *args):
        # We're not expecting any args
        if not len(args):
            chat.settings.send_updates = not chat.settings.send_updates
            match chat.settings.send_updates:
                case False:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot will stop sending updates")
                case True:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot will send updates")
            # end match
            
        # end if
    # end def

    async def run(self,
                  update: telegram.Update,
                  app: object,
                  *args):
        await super().run(update, app, *args)

        # We have args, and the command is indeed from this class
        if len(args) > ConfigureMsgCommand._SUBCMD_INDEX and args[ConfigureMsgCommand._CMD_INDEX] == self.cmd:
            chat: Chat = app.get_chat(update.effective_message.chat.id)

            # Configuration command requires admin rights
            if chat.is_admin(update.effective_sender.id):

                if args[ConfigureMsgCommand._SUBCMD_INDEX] in self.cmd_handlers:
                    await self.cmd_handlers[args[ConfigureMsgCommand._SUBCMD_INDEX]](update,
                                                                                     app,
                                                                                     chat,
                                                                                     *(args[ConfigureMsgCommand._ARGS_INDEX:]))
                else:
                    warn(f"Got an unknown command '{args[ConfigureMsgCommand._CMD_INDEX]} {args[ConfigureMsgCommand._SUBCMD_INDEX]}'")
                # end if
            else:
                update.effective_message.reply_text("You must be an admin to configure the bot")
            # end if
        # end if
    # end def

    def get_interactive_choices(self, command_args: list[str] | None = None) \
        -> tuple[str | None, telegram.InlineKeyboardMarkup | None, bool]:
        
        prompt = "Please choose:"
        ret_val = None
        delete_msg = False

        if not command_args:
            prompt = "What setting would you like to configure?"
            ret_val = telegram.InlineKeyboardMarkup([
                [
                    telegram.InlineKeyboardButton(f"{Emojis.BELL.value} Send updates",
                                                  callback_data=f"{self.cmd} {_SubCmd.SEND_UPDATES.value}")
                ],
                [
                    telegram.InlineKeyboardButton(f"{Emojis.CLOCK.value} Predict time",
                                                  callback_data=f"{self.cmd} {_SubCmd.PREDICT_TIME.value}"),

                    telegram.InlineKeyboardButton(f"{Emojis.GLOBE.value} Hemisphere",
                                                  callback_data=f"{self.cmd} {_SubCmd.CHOOSE_HEMISPHERE.value}")
                ],
                [
                    telegram.InlineKeyboardButton(f"{Emojis.GRAPH.value} Include data",
                                                  callback_data=f"{self.cmd} {_SubCmd.INCLUDE_DATA.value}"),

                    telegram.InlineKeyboardButton(f"{Emojis.MILKY_WAY.value} Include images",
                                                  callback_data=f"{self.cmd} {_SubCmd.INCLUDE_IMAGES.value}")
                ],
                [
                    telegram.InlineKeyboardButton(f"{Emojis.WRENCH.value} Flare class trigger",
                                                  callback_data=f"{self.cmd} {_SubCmd.FLARE_CLASS.value}"),

                    telegram.InlineKeyboardButton(f"{Emojis.WRENCH.value} Geomagnetic trigger",
                                                  callback_data=f"{self.cmd} {_SubCmd.GEOMAG_INTENSITY.value}")
                ],
            ])

        elif len(command_args) == 1:
            match command_args[0]:
                case "hemisphere":
                    prompt = "What hemisphere's events should trigger alerts?"
                    ret_val = telegram.InlineKeyboardMarkup([[
                        telegram.InlineKeyboardButton("Northern",
                                                      callback_data=f"{self.cmd} {_SubCmd.CHOOSE_HEMISPHERE.value} {_HemisphereChoices.NORTH.value}"),

                        telegram.InlineKeyboardButton("Southern",
                                                      callback_data=f"{self.cmd} {_SubCmd.CHOOSE_HEMISPHERE.value} {_HemisphereChoices.SOUTH.value}"),

                        telegram.InlineKeyboardButton("Both hemispheres",
                                                      callback_data=f"{self.cmd} {_SubCmd.CHOOSE_HEMISPHERE.value} {_HemisphereChoices.BOTH.value}")
                    ]])

                case "class":
                    prompt = "What minimum solar flare class should trigger alerts?"
                    flare_help = SolarFlareClass.get_help()
                    for key in flare_help:
                        prompt += f"\n{SolarFlareClass(key).name} = {flare_help[key]}"
                    # end for

                    ret_val = telegram.InlineKeyboardMarkup([[
                        telegram.InlineKeyboardButton(flare_class.name, callback_data=f"{self.cmd} {_SubCmd.FLARE_CLASS.value} {flare_class.value}")
                            for flare_class in SolarFlareClass
                    ]])

                case "geomag":
                    prompt = "What minimum geomagnetic storm intensity should trigger alerts?"
                    geomag_help = GeomagStormIndex.get_help()
                    for key in geomag_help:
                        prompt += f"\n{GeomagStormIndex(key).name} = {geomag_help[key]}"
                    # end for

                    ret_val = telegram.InlineKeyboardMarkup([[
                        telegram.InlineKeyboardButton(geomag_class.name, callback_data=f"{self.cmd} {_SubCmd.GEOMAG_INTENSITY.value} {geomag_class.value}")
                            for geomag_class in GeomagStormIndex
                    ]])
            # end match
        # end with

        return prompt, ret_val, delete_msg
    # end def
# end class
