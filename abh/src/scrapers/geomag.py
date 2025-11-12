import json
import re
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError
from ssl import SSLContext
from urllib.request import urlopen
from zoneinfo import ZoneInfo
from time import time

from abh.src.log import error
from abh.src.scrapers.scraper import (Scraper,
                                      SpecializedScraper,
                                      ScrapeResult)

OVATION_NORTH = "https://services.swpc.noaa.gov/images/animations/ovation/north/latest.jpg"
OVATION_SOUTH = "https://services.swpc.noaa.gov/images/animations/ovation/south/latest.jpg"
MAGNETOSPHERE = "https://services.swpc.noaa.gov/images/animations/geospace/velocity/latest.png"


def _get_attachments() -> dict[str, str]:
    curr_time = time()
    return {
        "Magnetosphere": f"{MAGNETOSPHERE}?avoid_cache={int(time())}",
        "Ovation North": f"{OVATION_NORTH}?avoid_cache={int(time())}",
        "Ovation South": f"{OVATION_SOUTH}?avoid_cache={int(time())}"
    }
# end def


class GfzPotsdamScraper(SpecializedScraper):

    def __init__(self):
        SpecializedScraper.__init__(self, "GFZ Potsdam (DE) forecast scraper")
        self._endpoint = "https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_nowcast.txt"
        self._scrape_tz = ZoneInfo("Europe/Berlin")
        self._timeout = 5
        self._line_regex = re.compile(
            br"\n(?P<year>\d{4}) (?P<month>\d{2}) (?P<day>\d{2}) (?P<hour>\d{2})\.\d \d{2}\.\d{2} \d+\.\d+ \d+\.\d+ +(?P<k>\d+\.\d+) +(?P<ap>\d+) (?P<is_sure>\d)")
        self._forecast_interval = timedelta(hours=3)

    # end def

    def scrape(self) -> list[ScrapeResult]:
        results = []

        scrape_data = urlopen(self._endpoint,
                              timeout=self._timeout)

        if scrape_data:

            try:
                result_txt = scrape_data.read()

                for re_match in self._line_regex.finditer(result_txt):
                    groups = re_match.groupdict()
                    forecast_time = datetime(year=int(groups["year"]),
                                             month=int(groups["month"]),
                                             day=int(groups["day"]),
                                             hour=int(groups["hour"]),
                                             tzinfo=self._scrape_tz)
                    forecast_time = forecast_time.astimezone(timezone.utc)
                    next_forecast_time = forecast_time + self._forecast_interval
                    k = groups["k"]

                    # Both unused
                    ap = groups["ap"]
                    is_sure = groups["is_sure"]

                    curr_forecast_time = forecast_time
                    # Create results
                    while curr_forecast_time < next_forecast_time:
                        result = ScrapeResult(start_time=curr_forecast_time,
                                              end_time=curr_forecast_time + timedelta(minutes=Scraper.SCRAPE_INTERVAL),
                                              is_prediction=False,
                                              raw_geomag_intensity=float(k),
                                              attachments=_get_attachments())

                        # Add scraping interval
                        curr_forecast_time = result.end_time
                        results.append(result)
                    # end while
                # end for

            except Exception as e:
                error(f"Specialized scraper '{self._name}' failed to scrape: {e}")
            # end try
        # end if

        return results
    # end def


# end class


class NoaaPlanetaryKScraper(SpecializedScraper):

    def __init__(self):
        SpecializedScraper.__init__(self, "NOAA (USA) planetary K index scraper")
        self._endpoint = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
        self._scrape_tz = ZoneInfo("Etc/UTC")
        self._timeout = 5

    # end def

    def scrape(self) -> list[ScrapeResult]:
        results = []

        gcontext = SSLContext()
        scrape_data = urlopen(self._endpoint, timeout=self._timeout, context=gcontext)

        if scrape_data:

            try:
                result_json = json.loads(scrape_data.read())

                for json_i in range(0, len(result_json), int(Scraper.SCRAPE_INTERVAL)):
                    planetary_ks = result_json[json_i: json_i + int(Scraper.SCRAPE_INTERVAL)]
                    time_tag = datetime.strptime(planetary_ks[0]["time_tag"], "%Y-%m-%dT%H:%M:%S")
                    time_tag = time_tag.astimezone(self._scrape_tz)
                    result = ScrapeResult(start_time=time_tag,
                                          end_time=time_tag + timedelta(minutes=Scraper.SCRAPE_INTERVAL),
                                          is_prediction=False,
                                          raw_geomag_intensity=max(planetary_ks, key=lambda planetary_k: planetary_k["estimated_kp"])["estimated_kp"],
                                          attachments=_get_attachments())
                    results.append(result)
                # end for

            except JSONDecodeError as e:
                error(f"Specialized scraper '{self._name}' failed to scrape: {e.msg}")
            # end try
        # end if

        return results
    # end def


# end class


class GeomagScraper(Scraper):
    def __init__(self):
        super().__init__("Geomagnetic intensity",
                         "geomag",
                         provides_intensity=True,
                         provides_class=False)

        self._append_specialized_scraper(GfzPotsdamScraper())
        self._append_specialized_scraper(NoaaPlanetaryKScraper())
    # end def
# end class
