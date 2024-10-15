from datetime import datetime
from abh.src.ManagedThread import ManagedThread
from abh.src.consts import GeomagStormIndex
from abh.src.consts import SolarFlareClass
from abh.src.consts import HemisphereChoices
from abh.src.log import *
from os.path import join
from os.path import exists
from time import time
import pickle
import threading


class ScrapeResult:

    def __init__(self) -> None:
        self._raw_geomag_intensity: float = 0.0
        self._geomag_intensity: GeomagStormIndex = GeomagStormIndex.KP0
        self._raw_flare_class: float = 0.0
        self._flare_class: SolarFlareClass = SolarFlareClass.OTHER
        self._hemisphere: HemisphereChoices = HemisphereChoices.BOTH
        self._attachments: list[str] = []
        self._scrape_time: datetime = datetime.utcnow()
        self._arrival_time: datetime = datetime(1970, 1, 1)  # Yes, it'll have arrived a long time ago
        self._is_prediction: bool = False
        self._start_time: datetime = datetime.utcnow()
        self._end_time: datetime = datetime.utcnow()
    # end def

    def merge(self, other: 'ScrapeResult') -> 'ScrapeResult':
        self._raw_geomag_intensity = max(self._raw_geomag_intensity, other._raw_geomag_intensity)
        self._geomag_intensity = max(self._geomag_intensity, other._geomag_intensity)
        self._raw_flare_class = max(self._raw_flare_class, other._raw_flare_class)
        self._flare_class = max(self._flare_class, other._flare_class)
        self._hemisphere |= other._hemisphere
        self.attachments.extend(other.attachments)
        return self
    # end def

    @property
    def raw_intensity(self) -> float:
        return self._raw_geomag_intensity
    # end def

    @property
    def intensity(self) -> GeomagStormIndex:
        return self._geomag_intensity
    # end def

    @property
    def raw_flare_class(self) -> float:
        return self._raw_flare_class
    # end def

    @property
    def flare_class(self) -> SolarFlareClass:
        return self._flare_class
    # end def

    @property
    def hemisphere(self) -> HemisphereChoices:
        return self._hemisphere
    # end def

    @property
    def data(self) -> str:
        return (f"Gr:{self._raw_geomag_intensity},Gi:{self._geomag_intensity},"
                f"Cr:{self.raw_flare_class},Ci:{self.flare_class},"
                f"H:{self.hemisphere},"
                f"M:{self.attachments},"
                f"P:{self.is_prediction},"
                f"S:{self.start_time.timestamp()},"
                f"E:{self.end_time.timestamp()},"
                f"T:{self.scrape_time.timestamp()},"
                f"A:{self.arrival_time.timestamp()}")
    # end def

    @property
    def attachments(self) -> list:
        return self._attachments
    # end def

    @property
    def scrape_time(self) -> datetime:
        return self._scrape_time
    # end def

    @property
    def arrival_time(self) -> datetime:
        return self._arrival_time
    # end def

    @property
    def is_prediction(self) -> bool:
        return self._is_prediction
    # end def

    @property
    def start_time(self) -> datetime:
        return self._start_time
    # end def

    @property
    def end_time(self) -> datetime:
        return self._end_time
    # end def
# end def


class SpecializedScraper:
    def __init__(self,
                 name: str) -> None:
        self._name = name
    # end def

    """
    Performs a specialized scrape
    Note: returned list must contain scrape results of (Scraper.SCRAPE_INTERVAL) minutes of interval.
    Scraper is not at fault if results get messy
    """
    def scrape(self) -> list[ScrapeResult]:
        raise NotImplementedError()
    # end def
# end def


class Scraper(ManagedThread):

    SCRAPE_INTERVAL = 5.0 # 5 minutes
    SCRAPE_INTERVAL_S = 60.0 * SCRAPE_INTERVAL

    def __init__(self,
                 name,
                 file_name,
                 provides_intensity: bool,
                 provides_class: bool) -> None:
        super().__init__(f"Scraper '{name}'")
        self._provides_intensity = provides_intensity
        self._provides_class = provides_class
        self._name = name
        self._file_name = file_name
        self._history_filename = join("data", f"scraper_{file_name}.bin")
        self._specialized_scrapers: list[SpecializedScraper] = []
        self._results: list[ScrapeResult] = []
        self._results_cond: threading.Condition = threading.Condition()
    # end def

    def run_thread(self, **kwargs) -> None:
        self.load_history()
        super().run_thread(_t_scraper)
    # end def

    def stop_thread(self) -> None:
        super().stop_thread()
        self.save_history()
    # end def

    def load_history(self) -> None:

        if self._running:
            raise RuntimeError("Scraper cannot load history files while running")
        # end if

        if not exists(self._history_filename):
            warn("Scraper history file does not exist")
            return
        # end if

        with open(self._history_filename, "rb") as history_file:
            loaded_list = pickle.load(history_file)
            if not isinstance(loaded_list, list) or any([not isinstance(result, ScrapeResult) for result in loaded_list]):
                raise RuntimeError("Invalid history file")
            # end if

            self._results.extend(loaded_list)
        # end with
    # end def

    def save_history(self) -> None:
        lock_acquired = self._results_cond.acquire(blocking=True,
                                                   timeout=Scraper._RESULTS_COND_TIMEOUT)
        if not lock_acquired:
            raise RuntimeError("Failed to acquire lock to save results")
        # end if

        with open(self._history_filename, "wb") as history_file:
            pickle.dump(self._results, history_file)
        # end with

        self._results_cond.release()
    # end def

    def scrape(self):
        debug(f"[{self.name}] Scrape started")
        for scraper in self._specialized_scrapers:
            self._append_result(scraper.scrape())
        # end for
        debug(f"[{self.name}] Scrape finished")
    # end def

    def _append_specialized_scraper(self, scraper: SpecializedScraper) -> None:
        self._specialized_scrapers.append(scraper)
    # end def

    def _append_result(self, results: list[ScrapeResult]) -> None:

        lock_acquired = self._results_cond.acquire(blocking=True,
                                                   timeout=Scraper._RESULTS_COND_TIMEOUT)

        if not lock_acquired:
            raise RuntimeError("Failed to acquire lock to get append latest result")
        # end if

        results = sorted(results, key=lambda scrape_result: scrape_result.start_time, reverse=True)
        earliest_result = self._results[-1] if len(self._results) > 0 else None
        latest_result = self._results[0] if len(self._results) > 0 else None
        
        earlier_to_new_results_i = 0
        if len(results):
            earliest_new_result = results[-1]

            for i in range(len(self._results) - 1, -1, -1):
                if self._results[i].start_time < earliest_new_result.start_time:
                    earlier_to_new_results_i = i
                    break
                # end if
            # end for
        # end if

        for result in results:
            
            if not latest_result or result.start_time >= latest_result.end_time:
                self._results.append(result)
                continue
            # end if

            if not earliest_result or result.end_time <= earliest_result.start_time:
                self._results.append(result)
                continue
            # end if
            
            # Merge scrapes with overlapping times
            for i in range(earlier_to_new_results_i, len(self._results)):
                reg_result = self._results[i]

                if reg_result.start_time <= result.start_time < reg_result.end_time:
                    self._results[i] = reg_result.merge(result)
                    break
                # end if
            # end for
        # end for

        self._results = sorted(self._results, key=lambda _result: _result.start_time, reverse=True)
        self._results_cond.release()
    # end def

    @property
    def name(self):
        return self._name
    # end def

    @property
    def provides_intensity(self) -> bool:
        return self._provides_intensity
    # end def

    @property
    def provides_class(self) -> bool:
        return self._provides_class
    # end def

    @property
    def latest(self) -> ScrapeResult | None:
        lock_acquired = self._results_cond.acquire(blocking=True,
                                                   timeout=Scraper._RESULTS_COND_TIMEOUT)
        if not lock_acquired:
            raise RuntimeError("Failed to acquire lock to get latest result")
        # end if

        latest_result = self._results[-1] if len(self._results) else None
        self._results_cond.release()

        return latest_result
    # end def
# end class


def _t_scraper(scraper: Scraper):
    """
    Scraper thread entrypoint

    @note  This is a thread's main loop. Use conditions and events to interact with it
    @param scraper: (Scraper) Scraper instance
    """

    # Synch with next sharp minute
    remaining_secs = time() % 60
    debug(f"[{scraper.name}] {remaining_secs:2.1f} seconds remaining until next scrape")
    keep_alive = not scraper.event_wait(remaining_secs)

    while scraper.keep_alive():
        scraper.scrape()

        # Sleep & check if we need to loop
        scraper.event_wait(Scraper.SCRAPE_INTERVAL_S)
    # end def

    debug(f"[{scraper.name}] Thread is dying")
# end def
