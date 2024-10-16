import json
import math
import re
from json import JSONDecodeError
from datetime import datetime, timedelta, timezone
from ssl import SSLContext

from abh.src.consts import GeomagStormIndex
from abh.src.log import error, debug
from zoneinfo import ZoneInfo
from urllib.request import urlopen
from abh.src.scrapers.scraper import (Scraper,
                                      SpecializedScraper,
                                      ScrapeResult)


class NasaCcmcScraper(SpecializedScraper):

    def __init__(self):
        SpecializedScraper.__init__(self, "NASA's Community Coordinated Modelin Center")
        self._endpoint = "https://kauai.ccmc.gsfc.nasa.gov/CMEscoreboard/WS/get/predictions?skipNoArrivalObservedCMEs=true&CMEtimeStart={date}"
        self._scrape_tz = ZoneInfo("Etc/UTC")
        self._timeout = 15
    # end def

    def scrape(self) -> list[ScrapeResult]:
        results = []

        a_week_ago = datetime.utcnow() - timedelta(days=7)
        url = self._endpoint.replace("{date}", a_week_ago.strftime("%Y-%m-%d"))
        scrape_data = urlopen(url, timeout=self._timeout)

        if scrape_data:
            
            try:
                result_json = json.loads(scrape_data.read())
                if len(result_json) < 1:
                    raise ValueError("Not enough data scraped")
                # end if

                latest_result = result_json[0]
                max_predicts = [pred["predictedMaxKpUpperRange"] or GeomagStormIndex.KP0.value for pred in latest_result["predictions"]]
                min_predicts = [pred["predictedMaxKpLowerRange"] or GeomagStormIndex.KP9.value for pred in latest_result["predictions"]]

                result = ScrapeResult()
                result._arrival_time = datetime.strptime(latest_result["arrivalTime"], "%Y-%m-%dT%H:%MZ")
                result._start_time = datetime.strptime(latest_result["observedTime"], "%Y-%m-%dT%H:%MZ")
                result._end_time = result.arrival_time
                result._raw_geomag_intensity = latest_result["maxKP"]
                result._geomag_intensity = GeomagStormIndex(int(math.floor(result._raw_geomag_intensity)))
                result.attachments.append({
                    "kpMax": GeomagStormIndex(int(max(max_predicts))),
                    "kpMin": GeomagStormIndex(int(min(min_predicts)))
                })
                result._is_prediction = True
                results.append(result)

            except JSONDecodeError as e:
                error(f"Specialized scraper '{self._name}' failed to decode endpoint: {e.msg}")
            except ValueError:
                debug(f"Specialized scraper '{self._name}' didn't find any CME")
            # end try
        # end if

        return results
    # end def
# end class


class CmeScraper(Scraper):
    def __init__(self):
        super().__init__("Coronal Mass Ejection",
                         "cme",
                         provides_intensity=True,
                         provides_class=False)

        self._append_specialized_scraper(NasaCcmcScraper())
        self._alerts = {}
    # end def

    def scrape(self):
        super().scrape()

        for result in self._results:
            if result not in self._alerts:
                self._alerts[result] = False
            # end if
        # end for
    # end def

    def get_new(self) -> list[ScrapeResult]:
        new_cme = []
        for scrape_result in self._alerts:
            if not self._alerts[scrape_result]:
                self._alerts[scrape_result] = True
                new_cme.append(scrape_result)
            # end if
        # end for

        return new_cme
    # end def
# end class
