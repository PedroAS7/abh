
import json
import math
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError
from ssl import SSLContext
from urllib.request import urlopen
from zoneinfo import ZoneInfo
from abh.src.consts import SolarFlareClass
from abh.src.log import error
from abh.src.scrapers.scraper import Scraper, SpecializedScraper, ScrapeResult


class NoaaFlareScraper(SpecializedScraper):

    def __init__(self):
        super().__init__("NOAA (USA) solar flare scraper")
        self._endpoint_1 = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json"
        self._endpoint_2 = "https://services.swpc.noaa.gov/json/goes/secondary/xrays-6-hour.json"
        self._forecast_north = "https://services.swpc.noaa.gov/images/animations/ovation/north/aurora_N_{date}.jpg"
        self._forecast_south = "https://services.swpc.noaa.gov/images/animations/ovation/south/aurora_S_{date}.jpg"
        self._magnetosphere = "https://services.swpc.noaa.gov/images/animations/geospace/velocity/latest.png"
        self._scrape_tz = ZoneInfo("Etc/UTC")
        self._timeout = 5
    # end def


    def scrape(self) -> list[ScrapeResult]:
        results = []

        scrape_data = self._get_best_candidate()
        if scrape_data:
            short_range = scrape_data[0]
            long_range = scrape_data[1]

            result = ScrapeResult()
            time_tag = datetime.strptime(short_range["time_tag"], "%Y-%m-%dT%H:%M:%SZ")
            result._start_time = time_tag
            result._end_time = time_tag + timedelta(minutes=Scraper.SCRAPE_INTERVAL)
            max_intensity = max(short_range["observed_flux"], long_range["observed_flux"])
            result._raw_flare_class = max_intensity

            # Calculate corresponding class
            log10_intensity = math.log10(max_intensity)
            norm_intensity = math.floor(log10_intensity * 10)

            if norm_intensity < SolarFlareClass.lowest():
                flare_class = SolarFlareClass.OTHER
            elif norm_intensity > SolarFlareClass.highest():
                flare_class = SolarFlareClass.highest()
            else:
                mod = -norm_intensity % 5
                flare_class = SolarFlareClass(norm_intensity + mod)
            # end if

            result._flare_class = flare_class

            # Add attachments. Images are generated every 5 minutes
            norm_date: datetime = time_tag - timedelta(minutes=time_tag.minute - (time_tag.minute % 5))
            result._attachments.append(self._magnetosphere)
            result._attachments.append(self._forecast_north.replace("{date}", norm_date.strftime("%Y-%m-%d_%H%M")))
            result._attachments.append(self._forecast_south.replace("{date}", norm_date.strftime("%Y-%m-%d_%H%M")))

            results.append(result)
        # end if

        return results
    # end def

    def _scrape_candidate(self, endpoint: str) -> list[dict] | None:
        scrape = None

        gcontext = SSLContext()
        scrape_data = urlopen(endpoint, timeout=self._timeout, context=gcontext)
        if scrape_data:
            try:
                result_json = json.loads(scrape_data.read())
                if len(result_json) < 2:
                    raise ValueError("Not enough data scraped")
                # end if
                scrape = result_json[-2:]
            except JSONDecodeError as e:
                error(f"Specialized scraper '{self._name}' failed to decode endpoint: {e.msg}")
            except ValueError as e:
                error(f"Specialized scraper '{self._name}' failed to scrape endpoint: {e}")
            # end try
        # end if

        return scrape
    # end def

    def _get_best_candidate(self) -> list[dict] | None:

        best = None
        primary = self._scrape_candidate(self._endpoint_1)
        secondary = self._scrape_candidate(self._endpoint_2)

        # One of both succeeded
        if primary or secondary:
            primary_time_tag = datetime.strptime(primary[0]["time_tag"], "%Y-%m-%dT%H:%M:%SZ") if primary else datetime.fromtimestamp(0)
            secondary_time_tag = datetime.strptime(secondary[0]["time_tag"], "%Y-%m-%dT%H:%M:%SZ") if secondary else datetime.fromtimestamp(0)

            # Either endpoint went offline for a moment
            if primary_time_tag > secondary_time_tag:
                best = primary
            elif primary_time_tag < secondary_time_tag:
                best = secondary
            else:
                if primary[0]["observed_flux"] > secondary[0]["observed_flux"]:
                    best = primary
                else:
                    best = secondary
                # end if
            # end if
        # end if

        return best
    # end def
# end class



class FlaresScraper(Scraper):
    def __init__(self):
        super().__init__("Solar flares",
                         "flares",
                         provides_intensity=False,
                         provides_class=True)

        self._append_specialized_scraper(NoaaFlareScraper())
    # end def
# end class