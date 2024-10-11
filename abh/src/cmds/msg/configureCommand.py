from abh.src.chat import Chat
from abh.src.cmds.botCommand import BotCommand
from abh.src.consts import Emojis
from abh.src.consts import SolarFlareClass
from abh.src.consts import GeomagStormIndex
from abh.src.consts import HemisphereChoices
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


class ConfigureMsgCommand(BotCommand):

    _CMD_INDEX        = 0
    _SUBCMD_INDEX     = 1
    _ARGS_INDEX       = 2
    _BUTTONS_PER_LINE = 5

    def __init__(self) -> None:
        super().__init__("configure",
                         f"{Emojis.WRENCH.value} Configure bot",
                         False,
                         True)

        self.cmd_handlers = {
            _SubCmd.SEND_UPDATES.value      : self._run_send_updates,
            _SubCmd.FLARE_CLASS.value       : self._run_set_flare_class,
            _SubCmd.GEOMAG_INTENSITY.value  : self._run_set_geomag_intensity,
            _SubCmd.CHOOSE_HEMISPHERE.value : self._run_set_hemisphere,
            _SubCmd.INCLUDE_DATA.value      : self._run_include_data,
            _SubCmd.INCLUDE_IMAGES.value    : self._run_include_images,
            _SubCmd.PREDICT_TIME.value      : self._run_predict_time
            }
    # end def

    async def _run_send_updates(self,
                                update: telegram.Update,
                                app: object,
                                chat: Chat,
                                *args) -> None:
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

    async def _run_include_data(self,
                                update: telegram.Update,
                                app: object,
                                chat: Chat,
                                *args) -> None:
        # We're not expecting any args
        if not len(args):
            chat.settings.include_data = not chat.settings.include_data
            match chat.settings.include_data:
                case False:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot will won't include data")
                case True:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot will include data of the event")
            # end match
        # end if
    # end def

    async def _run_include_images(self,
                                  update: telegram.Update,
                                  app: object,
                                  chat: Chat,
                                  *args) -> None:
        # We're not expecting any args
        if not len(args):
            chat.settings.include_images = not chat.settings.include_images
            match chat.settings.include_images:
                case False:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot won't attach images")
                case True:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot will attach images to the event messages")
            # end match
        # end if
    # end def

    async def _run_predict_time(self,
                                update: telegram.Update,
                                app: object,
                                chat: Chat,
                                *args) -> None:
        # We're not expecting any args
        if not len(args):
            chat.settings.predict_time = not chat.settings.predict_time
            match chat.settings.predict_time:
                case False:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot won't predict arrival time")
                case True:
                    await update.effective_message.chat.send_message(f"{Emojis.OK.value} Bot will try to predict arrival time")
            # end match
        # end if
    # end def

    async def _run_set_flare_class(self,
                                   update: telegram.Update,
                                   app: object,
                                   chat: Chat,
                                   *args) -> None:
        try:
            if len(args) == 0:
                raise KeyError()
            # end if

            chosen_class: SolarFlareClass = SolarFlareClass[args[0]]
            chat.settings.min_flare_class = chosen_class
            await update.effective_message.chat.send_message(f"{Emojis.OK.value} Flare class trigger set")
        except KeyError:
            await update.effective_message.reply_text("Invalid choice!")
        # end try
    # end def

    async def _run_set_hemisphere(self,
                                  update: telegram.Update,
                                  app: object,
                                  chat: Chat,
                                  *args) -> None:
        try:
            if len(args) == 0:
                raise KeyError()
            # end if

            chosen_hemisphere: HemisphereChoices = HemisphereChoices[args[0]]
            chat.settings.northern_hemisphere = chosen_hemisphere == HemisphereChoices.NORTH
            chat.settings.southern_hemisphere = chosen_hemisphere == HemisphereChoices.SOUTH
            await update.effective_message.chat.send_message(f"{Emojis.OK.value} Hemisphere set")
        except KeyError:
            await update.effective_message.reply_text("Invalid choice!")
        # end try
    # end def

    async def _run_set_geomag_intensity(self,
                                        update: telegram.Update,
                                        app: object,
                                        chat: Chat,
                                        *args) -> None:
        try:
            if len(args) == 0:
                raise KeyError()
            # end if

            chosen_intensity: GeomagStormIndex = GeomagStormIndex[args[0]]
            chat.settings.min_geomag_value = chosen_intensity
            await update.effective_message.chat.send_message(f"{Emojis.OK.value} Geomagnetic intensity trigger set")
        except KeyError:
            await update.effective_message.reply_text("Invalid choice!")
        # end try
    # end def

    async def run(self,
                  update: telegram.Update,
                  app: object,
                  *args) -> None:
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
                                                      callback_data=f"{self.cmd} {_SubCmd.CHOOSE_HEMISPHERE.value} {HemisphereChoices.NORTH.name}"),

                        telegram.InlineKeyboardButton("Southern",
                                                      callback_data=f"{self.cmd} {_SubCmd.CHOOSE_HEMISPHERE.value} {HemisphereChoices.SOUTH.name}"),

                        telegram.InlineKeyboardButton("Both hemispheres",
                                                      callback_data=f"{self.cmd} {_SubCmd.CHOOSE_HEMISPHERE.value} {HemisphereChoices.BOTH.name}")
                    ]])

                case "class":
                    prompt = "What minimum solar flare class should trigger alerts?"
                    flare_help = SolarFlareClass.get_help()
                    for key in flare_help:
                        prompt += f"\n{SolarFlareClass(key).name} = {flare_help[key]}"
                    # end for
                    
                    buttons = [
                        telegram.InlineKeyboardButton(flare_class.name, callback_data=f"{self.cmd} {_SubCmd.FLARE_CLASS.value} {flare_class.name}")
                            for flare_class in SolarFlareClass
                    ]
                    
                    ret_val = telegram.InlineKeyboardMarkup([buttons[x:x+ConfigureMsgCommand._BUTTONS_PER_LINE] for x in range(0, len(buttons), ConfigureMsgCommand._BUTTONS_PER_LINE)])

                case "geomag":
                    prompt = "What minimum geomagnetic storm intensity should trigger alerts?"
                    geomag_help = GeomagStormIndex.get_help()
                    for key in geomag_help:
                        prompt += f"\n{GeomagStormIndex(key).name} = {geomag_help[key]}"
                    # end for

                    buttons = [
                        telegram.InlineKeyboardButton(geomag_class.name, callback_data=f"{self.cmd} {_SubCmd.GEOMAG_INTENSITY.value} {geomag_class.name}")
                            for geomag_class in GeomagStormIndex
                    ]

                    ret_val = telegram.InlineKeyboardMarkup([buttons[x:x+ConfigureMsgCommand._BUTTONS_PER_LINE] for x in range(0, len(buttons), ConfigureMsgCommand._BUTTONS_PER_LINE)])
            # end match
        # end with

        return prompt, ret_val, delete_msg
    # end def
# end class
