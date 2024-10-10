# USA: https://services.swpc.noaa.gov/json/planetary_k_index_1m.json
# Germany: https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_nowcast.txt

import json
from json import JSONDecodeError
from datetime import datetime, timedelta
from abh.src.consts import GeomagStormIndex
from abh.src.log import error
from zoneinfo import ZoneInfo
from urllib.request import urlopen
from abh.src.scrapers.scraper import (Scraper,
                                      SpecializedScraper,
                                      ScrapeResult)


class NoaaPlanetaryKScraper(SpecializedScraper):

    def __init__(self):
        SpecializedScraper.__init__(self,
                                    "NOAA (USA) planetary K index scraper")
        self._endpoint = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
        self._scrape_tz = ZoneInfo("Etc/UTC")
        self._timeout = 5

    # end def

    def scrape(self) -> list[ScrapeResult]:
        results = []

        scrape_data = urlopen(self._endpoint,
                              timeout=self._timeout)

        if scrape_data:

            try:
                result_json = json.loads(scrape_data.read())

                for json_i in range(0, len(result_json), int(Scraper.SCRAPE_INTERVAL)):
                    result = ScrapeResult()
                    planetary_ks = result_json[json_i: json_i + int(Scraper.SCRAPE_INTERVAL)]
                    time_tag = datetime.strptime(planetary_ks[0]["time_tag"], "%Y-%m-%dT%H:%M:%S")
                    time_tag.replace(tzinfo=self._scrape_tz)
                    result._start_time = time_tag
                    result._end_time = time_tag + timedelta(minutes=Scraper.SCRAPE_INTERVAL)
                    result._raw_geomag_intensity = max(planetary_ks,
                                                       key=lambda planetary_k: planetary_k["estimated_kp"])["estimated_kp"]
                    result._geomag_intensity = GeomagStormIndex(max(planetary_ks,
                                                                    key=lambda planetary_k: planetary_k["kp_index"])["kp_index"])
                    results.append(result)
                # end for

            except JSONDecodeError as e:
                error(f"Specialized scraper '{self.name}' failed to scrape: {e.msg}")
            # end try
        # end if

        return results
    # end def
# end class


class GeomagScraper(Scraper):
    def __init__(self):
        super().__init__("Geomagnetic intensity",
                         provides_intensity=True,
                         provides_class=False)

        self._append_specialized_scraper(NoaaPlanetaryKScraper())
    # end def
# end class
