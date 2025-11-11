import pickle
import threading
import uuid
from datetime import datetime, timezone
from os.path import exists
from os.path import join
from time import time
from dataclasses import dataclass, field

from abh.src.thread import ManagedThread
from abh.src.consts import GeomagStormIndex
from abh.src.consts import HemisphereChoices
from abh.src.consts import SolarFlareClass
from abh.src.log import *


@dataclass
class ScrapeResult:
    id: uuid.UUID = uuid.uuid4()
    raw_geomag_intensity: float = 0.0
    raw_flare_class: float = 0.0
    hemisphere: HemisphereChoices = HemisphereChoices.BOTH
    attachments: dict = field(default_factory=dict)
    scrape_time: datetime = datetime.now(timezone.utc)
    arrival_time: datetime = datetime(1970, 1, 1)  # Yes, it'll have arrived a long time ago
    is_prediction: bool = False
    start_time: datetime = datetime.now(timezone.utc)
    end_time: datetime = datetime.now(timezone.utc)

    @property
    def data(self) -> str:
        return (f"Gr:{self.raw_geomag_intensity},Gi:{self.intensity},"
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
    def intensity(self) -> GeomagStormIndex:
        return GeomagStormIndex(int(self.raw_geomag_intensity))
    # end def

    @property
    def flare_class(self) -> SolarFlareClass:
        return SolarFlareClass.round_to_val(self.raw_flare_class)
    # end def

    @staticmethod
    def _merge_dates(date1: datetime, date2: datetime) -> datetime:

        if date1.year == 1970:
            return date2
        # end if

        if date2.year == 1970:
            return date1
        # end if

        return datetime.fromtimestamp(min(date1.astimezone(timezone.utc).timestamp(),
                                          date2.astimezone(timezone.utc).timestamp()),
                                      timezone.utc)

    # end def

    def merge(self, other: 'ScrapeResult') -> 'ScrapeResult':

        if other is None:
            return self
        # end if

        merged = ScrapeResult()
        merged._end_time = ScrapeResult._merge_dates(other.end_time, self.end_time)
        merged._scrape_time = ScrapeResult._merge_dates(other.scrape_time, self.scrape_time)
        merged._start_time = ScrapeResult._merge_dates(other.start_time, self.start_time)
        merged._arrival_time = ScrapeResult._merge_dates(other.arrival_time, self.arrival_time)
        merged._geomag_intensity = other.intensity if other.intensity and other.intensity > self.intensity else self.intensity
        merged._flare_class = max(other.flare_class, self.flare_class)
        merged._raw_geomag_intensity = max(other.raw_geomag_intensity, self.raw_flare_class)
        merged._is_prediction = other.is_prediction or self.is_prediction
        merged._attachments = other.attachments.copy().update(self.attachments) if self.attachments else other.attachments.copy()
        merged._hemisphere = other.hemisphere | self.hemisphere
        return merged
    # end def

    def __hash__(self):
        return self.id.__hash__()
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
    SCRAPE_INTERVAL = 5.0  # 5 minutes
    SCRAPE_INTERVAL_S = 60.0 * SCRAPE_INTERVAL

    NEWLY_ADDED_SCRAPE = 0
    NEWLY_ADDED_CHECKED = 1
    NEWLY_ADDED_MATCHED = 2

    def __init__(self,
                 name,
                 file_name,
                 provides_intensity: bool,
                 provides_class: bool) -> None:
        super().__init__(f"Scraper '{name}'")
        self._newly_added: dict[uuid.UUID, list[ScrapeResult | bool]] = {}
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
            if not isinstance(loaded_list, list) or any(
                    [not isinstance(result, ScrapeResult) for result in loaded_list]):
                raise RuntimeError("Invalid history file")
            # end if

            self._results.extend(loaded_list)
        # end with
        log(f"[{self.name}] Loaded scrape history")

    # end def

    def save_history(self) -> None:
        lock_acquired = self._results_cond.acquire(blocking=True,
                                                   timeout=Scraper._RESULTS_COND_TIMEOUT)
        if not lock_acquired:
            raise RuntimeError("Failed to acquire lock to save results")
        # end if

        with open(self._history_filename, "wb") as history_file:
            # noinspection PyTypeChecker
            pickle.dump(self._results, history_file)
        # end with

        self._results_cond.release()
        log(f"[{self.name}] Saved scrape history")

    # end def

    def scrape(self):
        debug(f"[{self.name}] Scrape started")
        for scraper in self._specialized_scrapers:
            self._append_result(scraper.scrape())
        # end for

        for result in self._results:
            if result.id not in self._newly_added.keys():
                self._newly_added[result.id] = [result,  False, False]
            else:
                self._newly_added[result.id][self.NEWLY_ADDED_MATCHED] = True
            # end if
        # end for

        debug(f"[{self.name}] Scrape finished")

    # end def

    def _append_specialized_scraper(self, scraper: SpecializedScraper) -> None:
        self._specialized_scrapers.append(scraper)

    # end def

    def _append_result(self, results: list[ScrapeResult]) -> None:

        # Normalize dates to UTC
        for result in results:
            result.start_time = result.start_time.replace(tzinfo=timezone.utc)
            result.end_time = result.end_time.replace(tzinfo=timezone.utc)
            result.scrape_time = result.end_time.replace(tzinfo=timezone.utc)
            result.arrival_time = result.end_time.replace(tzinfo=timezone.utc)
        # end for

        with self._results_cond:

            results = sorted(results, key=lambda scrape_result: scrape_result.start_time, reverse=True)
            result_count = len(self._results)
            earliest_result = self._results[-1] if result_count > 0 else None
            latest_result = self._results[0] if result_count > 0 else None

            earlier_to_new_results_i = result_count
            if len(results):
                earliest_new_result = results[-1]

                for i in range(result_count - 1, -1, -1):
                    if self._results[i].start_time.timestamp() < earliest_new_result.start_time.timestamp():
                        earlier_to_new_results_i = i
                        break
                    # end if
                # end for
                debug(f"[{self.name}] Skipping {result_count - earlier_to_new_results_i} / {result_count} results")
            # end if

            for result in results[earlier_to_new_results_i:]:

                if not latest_result or result.start_time.timestamp() >= latest_result.end_time.timestamp():
                    self._results.append(result)
                    continue
                # end if

                if not earliest_result or result.end_time.timestamp() <= earliest_result.start_time.timestamp():
                    self._results.append(result)
                    continue
                # end if

                # Merge scrapes with overlapping times
                for i in range(earlier_to_new_results_i, len(self._results)):
                    reg_result = self._results[i]

                    if reg_result.start_time.timestamp() <= result.start_time.timestamp() < reg_result.end_time.timestamp():
                        self._results[i] = reg_result.merge(result)
                        break
                    # end if
                # end for
            # end for

            self._results = sorted(self._results, key=lambda _result: _result.start_time, reverse=True)
        # end with

    # end def

    def get_new(self) -> list[ScrapeResult]:
        new_results = []
        old_results = []
        self._results_cond.acquire()
        for result_id in self._newly_added:
            result_info = self._newly_added[result_id]

            # Result is too old. Ignore it, and remove it later
            if not result_info[self.NEWLY_ADDED_MATCHED]:
                old_results.append(result_id)
                continue
            # end if

            if not result_info[self.NEWLY_ADDED_CHECKED]:
                result_info[self.NEWLY_ADDED_CHECKED] = True
                new_results.append(result_info[self.NEWLY_ADDED_SCRAPE])
            # end if

            # Reset so we know which results are too old
            result_info[self.NEWLY_ADDED_MATCHED] = False
        # end for

        # Remove old results
        [self._newly_added.pop(result_id) for result_id in old_results]
        self._results_cond.release()

        return new_results

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

        if not self._results_cond.acquire(blocking=True, timeout=Scraper._RESULTS_COND_TIMEOUT):
            return None
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

    while scraper.keep_alive():
        start_time = time()
        scraper.scrape()
        end_time = time()

        # Sleep & check if we need to loop
        if end_time - start_time < Scraper.SCRAPE_INTERVAL_S:
            debug(f"[{scraper.name}] Scraping took {end_time - start_time:.2f} seconds")
            scraper.event_wait(Scraper.SCRAPE_INTERVAL_S)
        else:
            warn(f"[{scraper.name}] Scraping took too long to complete. Looping!")
        # end if
    # end def

    debug(f"[{scraper.name}] Thread is dying")
# end def
