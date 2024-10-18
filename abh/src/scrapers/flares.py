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
        self._solar_winds = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
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
            result._flare_class = SolarFlareClass.round_to_val(max_intensity)

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