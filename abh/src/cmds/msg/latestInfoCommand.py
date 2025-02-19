from abh.src.cmds.botCommand import BotCommand
from abh.src.consts import Emojis, GeomagStormIndex
from abh.src.log import *
import telegram

from abh.src.scrapers.scraper import ScrapeResult


class LatestInfoCommand(BotCommand):

    def __init__(self) -> None:
        super().__init__("latest",
                         f"{Emojis.CLOCK.value} Latest information",
                         False,
                         True)
    # end def

    async def run(self,
                  update: telegram.Update,
                  app: 'BotApp',
                  *args) -> None:
        await super().run(update, app, *args)
        
        if len(args) != 1:
            await update.message.reply_text("Invalid command!")
        else:
            latest_result: ScrapeResult | None = None
            for scraper in app.scrapers:
                if scraper.latest is None:
                    continue
                # end if

                latest_result = scraper.latest.merge(latest_result)
            # end for

            if latest_result is None:
                await update.message.reply_text("Latest info not available!")
            else:
                message = "Latest info available:\n"

                message += f"Info time: {latest_result.scrape_time}\n"
                message += f"From: {latest_result.start_time if latest_result.start_time.year > 1970 else '-'}\n"
                message += f"To: {latest_result.end_time if latest_result.end_time.year > 1970 else '-'}\n"
                message += f"Storm intensity: {latest_result.intensity.name if latest_result.intensity != GeomagStormIndex.KP0 else '-'}\n"
                message += f"Flare class: {latest_result.flare_class.name or '-'}\n"
                message += f"ETA: {latest_result.arrival_time if latest_result.arrival_time.year > 1970 else '-'}\n"
                message += f"Hemisphere(s): {latest_result.hemisphere or '-'}\n"
                message += f"Is a prediction? {'Yes' if latest_result.is_prediction else 'No'}"

                await update.message.reply_text(message)
            # end if
        # end if
    # end def
# end class
