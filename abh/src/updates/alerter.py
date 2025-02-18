import datetime
from asyncio import get_event_loop
from telegram import InputMediaPhoto
from telegram.constants import ParseMode
from abh.src.ManagedThread import ManagedThread
from abh.src.chat import Chat
from abh.src.consts import Emojis
from abh.src.scrapers.scraper import ScrapeResult
from abh.src.log import debug


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


async def _trigger_alerts(max_intensity_alert: ScrapeResult,
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

        message = await bot.send_message(chat.uid,
                                         _sanitize_markdown(message_text),
                                         ParseMode.MARKDOWN_V2,
                                         disable_notification=False)

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

        await bot.send_message(chat.uid,
                               _sanitize_markdown(message_text),
                               ParseMode.MARKDOWN_V2,
                               disable_notification=False)
    # end if


# end def


def _get_next_geomag_alert(chat, selected_alert):

    # No selected alert? No next alert.
    if selected_alert is None:
        return None
    # end if

    # If the currently-set alert is stronger than this one, no alert is triggered
    active_alert = chat.settings.active_intensity_alert
    if active_alert is not None and selected_alert.intensity <= active_alert.intensity:
        return None
    # end for

    return selected_alert
# end def


def _get_next_flare_alert(chat, selected_alert):

    # No selected alert? No next alert.
    if selected_alert is None:
        return None
    # end if

    # If the currently-set alert is stronger than this one, no alert is triggered
    active_alert = chat.settings.active_flare_alert
    if active_alert is not None and selected_alert.flare_class <= active_alert.intensity:
        return None
    # end for

    return selected_alert
# end def


async def _manage_alerts(alerts: list[ScrapeResult],
                         chat: Chat,
                         app) -> None:
    max_intensity_alert: ScrapeResult | None = None
    max_flare_class_alert: ScrapeResult | None = None

    # If most recent alert is outside of trigger levels, we'll remove the currently-set alerts
    most_recent = alerts[-1]

    if most_recent.flare_class < chat.settings.min_flare_class:
        chat.settings.active_flare_alert = None
    # endif

    if most_recent.intensity < chat.settings.min_geomag_value:
        chat.settings.active_intensity_alert = None
    # endif

    for alert in alerts:

        # Not strong enough to trigger
        if alert.intensity < chat.settings.min_geomag_value \
        or alert.flare_class < chat.settings.min_flare_class:
            continue
        # end if

        correct_hemisphere = (alert.hemisphere & chat.settings.northern_hemisphere == chat.settings.northern_hemisphere) \
                          or (alert.hemisphere & chat.settings.southern_hemisphere == chat.settings.southern_hemisphere)

        # We'll skip alerts that wouldn't trigger for the selected hemisphere
        if not correct_hemisphere:
            continue
        # end if

        higher_intensity_than_prev = not max_intensity_alert   or max_intensity_alert.intensity < alert.intensity
        bigger_flare_than_prev     = not max_flare_class_alert or max_flare_class_alert.flare_class < alert.flare_class

        # Keep track of alert because it's more intense than the previous one
        if higher_intensity_than_prev:
            max_intensity_alert = alert
        # end if

        # Keep track of alert because the flare is bigger than the previous one
        if bigger_flare_than_prev:
            max_flare_class_alert = alert
        # end if
    # end for

    # Check whether these alerts are worth notifying over or not
    max_intensity_alert   = _get_next_geomag_alert(chat, max_intensity_alert)
    max_flare_class_alert =  _get_next_flare_alert(chat, max_flare_class_alert)

    if max_intensity_alert is not None or max_flare_class_alert is not None:
        await _trigger_alerts(max_intensity_alert,
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

            # Only keep alerts that are recent enough
            _nowMinus5h = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).timestamp()
            recent_alerts = [alert for alert in alerts if alert.start_time.timestamp() >= _nowMinus5h]
            del alerts

            # Sort by date, oldest to newest
            recent_alerts = sorted(recent_alerts, key=lambda alert: alert.start_time.timestamp())

            # Only iterate through non-muted chats
            for chat in [chat for chat in alerter.app.chats if chat.settings.send_updates]:
                await _manage_alerts(recent_alerts, chat, alerter.app)
            # end for
        # end if

        alerter.event_wait(alerter.POOL_INTERVAL)
    # end while

    debug("[Alerter] Alerter finished")
# end def
