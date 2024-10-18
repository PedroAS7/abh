import datetime
from asyncio import get_event_loop
from datetime import timedelta

from telegram import InputMediaPhoto
from telegram.constants import ParseMode

from ManagedThread import ManagedThread
from chat import Chat
from consts import Emojis
from abh.src.scrapers.scraper import ScrapeResult
from log import debug


def _sanitize_markdown(text: str) -> str:
    # From https://stackoverflow.com/a/71313944
    return text.replace('[', '\\[') \
        .replace(']', '\\]') \
        .replace('(', '\\(') \
        .replace(')', '\\)') \
        .replace('>', '\\>') \
        .replace('#', '\\#') \
        .replace('+', '\\+') \
        .replace('-', '\\-') \
        .replace('=', '\\=') \
        .replace('|', '\\|') \
        .replace('{', '\\{') \
        .replace('}', '\\}') \
        .replace('.', '\\.') \
        .replace('!', '\\!')


# end def


class Alerter(ManagedThread):
    POOL_INTERVAL = 60  # 1 minute

    def __init__(self, bot_app, loop):
        self.loop = loop
        self._app = bot_app
        super().__init__("Alerter")

    # end def

    @property
    def app(self):
        return self._app

    # end def

    def run_thread(self, **kwargs) -> None:
        super().run_thread(_t_start)
    # end def


# end class


def _trigger_alerts(max_intensity_alert: ScrapeResult,
                    max_flare_class_alert: ScrapeResult,
                    chat: Chat,
                    app):
    bot = app.bot_user.get_bot()
    loop = get_event_loop()

    if max_intensity_alert:
        chat.settings.active_intensity_alert = max_intensity_alert

        if max_intensity_alert.is_prediction:
            message_text = f"""
{Emojis.SIREN.value} *Storm approaching* {Emojis.SIREN.value}

A solar storm is approaching Earth
*Potential intensity (KP):* {max_intensity_alert.raw_geomag_intensity} (forecast min: {max_intensity_alert.attachments[0]['kpMin']}, max: {max_intensity_alert.attachments[0]['kpMax']})
*ETA:* {max_intensity_alert.arrival_time.strftime("%c")}
*Detection time*: {max_intensity_alert.start_time.strftime("%c")}
            """
        else:
            message_text = f"""
{Emojis.SIREN.value} *Storm reached Earth* {Emojis.SIREN.value}

A solar storm has reached Earth
*Intensity (KP):* {max_intensity_alert.raw_geomag_intensity}
*Detection time*: {max_intensity_alert.start_time.strftime("%c")} UTC
            """
        # end if

        message = loop.run_until_complete(bot.send_message(chat.uid,
                                                           _sanitize_markdown(message_text),
                                                           ParseMode.MARKDOWN_V2,
                                                           disable_notification=False))

        if len(max_intensity_alert.attachments):
            loop.run_until_complete(message.reply_media_group(
                [InputMediaPhoto(attachment) for attachment in max_intensity_alert.attachments if
                 isinstance(attachment, str)],
                disable_notification=False))
        # end if
    # end if

    if max_flare_class_alert:
        chat.settings.active_flare_alert = max_flare_class_alert

        message_text = f"""
{Emojis.SIREN.value} *New solar flare* {Emojis.SIREN.value}

A new solar flare has been detected
*Class:* {max_flare_class_alert.flare_class.name}
*Detection time*: {max_flare_class_alert.start_time.strftime("%c")} UTC
        """

        loop.run_until_complete(bot.send_message(chat.uid,
                                                 _sanitize_markdown(message_text),
                                                 ParseMode.MARKDOWN_V2,
                                                 disable_notification=False))
    # end if


# end def


async def _manage_alerts(alerts: list[ScrapeResult],
                         chat: Chat,
                         app) -> None:
    max_intensity_alert: ScrapeResult | None = None
    max_flare_class_alert: ScrapeResult | None = None

    for alert in alerts:

        # Alert is too old
        if alert.start_time.timestamp() < (
                datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).timestamp():
            continue
        # end if

        correct_hemisphere = (alert.hemisphere & chat.settings.northern_hemisphere == chat.settings.northern_hemisphere) \
                          or (alert.hemisphere & chat.settings.southern_hemisphere == chat.settings.southern_hemisphere)

        higher_intensity_than_prev = not max_intensity_alert or max_intensity_alert.intensity < alert.intensity
        bigger_flare_than_prev = not max_flare_class_alert or max_flare_class_alert.flare_class < alert.flare_class

        if higher_intensity_than_prev \
                and correct_hemisphere:
            max_intensity_alert = alert
        # end if

        if bigger_flare_than_prev \
                and correct_hemisphere:
            max_flare_class_alert = alert
        # end if
    # end for

    # Removed expired alerts, or don't alert if less than current alert
    if max_intensity_alert is not None:
        if max_intensity_alert.intensity < chat.settings.min_geomag_value \
                or (chat.settings.active_intensity_alert is not None
                    and max_intensity_alert.intensity <= chat.settings.active_intensity_alert.intensity):
            max_intensity_alert = None
        # end if
    # end for

    if max_flare_class_alert is not None:
        if max_flare_class_alert.flare_class < chat.settings.min_flare_class \
                or (chat.settings.active_flare_alert is not None
                    and max_flare_class_alert.flare_class <= chat.settings.active_flare_alert.flare_class):
            max_flare_class_alert = None
        # end if
    # end for

    if max_intensity_alert is not None or max_flare_class_alert is not None:
        _trigger_alerts(max_intensity_alert,
                        max_flare_class_alert,
                        chat,
                        app)
    # end if
# end def


def _t_start(alerter: Alerter) -> None:
    loop = alerter.loop
    loop.run_until_complete(_t_run_alerter(alerter))


# end def


async def _t_run_alerter(alerter: Alerter):
    debug("[Alerter] Alerter started")

    while alerter.keep_alive():

        alerts: list[ScrapeResult] = []
        for scraper in alerter.app.scrapers:
            alerts.extend(scraper.get_new())
        # end for

        if len(alerts):
            # Only iterate through non-muted chats
            for chat in [chat for chat in alerter.app.chats if chat.settings.send_updates]:
                await _manage_alerts(alerts, chat, alerter.app)
            # end for
        # end if

        alerter.event_wait(alerter.POOL_INTERVAL)
    # end while

    debug("[Alerter] Alerter finished")
# end def
