from datetime import datetime
from abh.src.consts import GeomagStormIndex
from abh.src.consts import SolarFlareClass
from abh.src.consts import HemisphereChoices
from abh.src.log import *
from os.path import join
from os.path import exists
from time import time
import pickle
import threading


class ScrapeResult():

    def __init__(self) -> None:
        self._raw_geomag_intensity: float = 0.0
        self._geomag_intesity: GeomagStormIndex = GeomagStormIndex.KP0
        self._raw_class: float = 0.0
        self._flare_class: SolarFlareClass = SolarFlareClass.M5
        self._hemisphere: HemisphereChoices = HemisphereChoices.BOTH
        self._data: str = ""
        self._attachments: list[str] = []
        self._scrape_time: datetime = datetime.utcnow()
        self._arrival_time: datetime = datetime(1970, 1, 1)  # Yes, it'll have arrived a long time ago
    # end def
    
    @property
    def raw_intensity(self) -> float:
        return self._raw_geomag_intensity
    # end def
    
    @property
    def intensity(self) -> GeomagStormIndex:
        return self._geomag_intesity
    # end def
    
    @property
    def raw_flare_class(self) -> float:
        return self._raw_class
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
        return self._data
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
# end def


class Scraper():

    _HISTORY_FILENAME = join("data", "scraper.bin")
    _THREAD_JOIN_TIMEOUT = 5.0
    _RESULTS_COND_TIMEOUT = 2.0

    def __init__(self) -> None:
        self._results: list[ScrapeResult] = []
        self._results_cond: threading.Condition = threading.Condition()
        self._running: bool = False
        self._thread: threading.Thread = None
        self._thread_evt: threading.Event = threading.Event()
    # end def

    def run_thread(self) -> None:

        if self._running:
            raise RuntimeError("Scraper is already running")
        # end if

        self._thread_evt.clear()
        self._thread = threading.Thread(target=_t_scraper, args=[self])
        self._thread.start()
        self._running = True
        debug("Scraper thread started")
    # end def

    def stop_thread(self) -> None:

        if not self._running:
            raise RuntimeError("Scraper is not running")
        # end if
        
        log("Stopping scraper...")
        self._thread_evt.set()
        try:
            self._thread.join(Scraper._THREAD_JOIN_TIMEOUT)

            # Thread did not stop
            if self._thread.is_alive():
                raise TimeoutError()
            # end if

            self._running = False
            debug("Scraper thread stopped")
        except TimeoutError:
            error("Failed to stop scraper thread")
        # end try
    # end de

    def load_history(self, file_name=_HISTORY_FILENAME) -> None:

        if self._running:
            raise RuntimeError("Scraper cannot load history files while running")
        # end if
        
        if not exists(file_name):
            warn("Scraper history file does not exist")
            return
        # end if

        with open(file_name, "rb") as history_file:
            loaded_list = pickle.load(history_file)
            if not isinstance(loaded_list, list) or any([not isinstance(result, ScrapeResult) for result in loaded_list]):
                raise RuntimeError("Invalid history file")
            # end if

            self._results.extend(loaded_list)
        # end with
    # end def
    
    def save_history(self, file_name=_HISTORY_FILENAME) -> None:
        lock_acquired = self._results_cond.acquire(blocking=True,
                                                   timeout=Scraper._RESULTS_COND_TIMEOUT)
        if not lock_acquired:
            raise RuntimeError("Failed to acquire lock to save results")
        # end if
        
        with open(file_name, "wb") as history_file:
            pickle.dump(self._results, history_file)
        # end with

        self._results_cond.release()
    # end def

    def _keep_alive(self) -> bool:
        return not self._thread_evt.is_set()
    # end def

    def _append_result(self, result: ScrapeResult) -> None:
        lock_acquired = self._results_cond.acquire(blocking=True,
                                                   timeout=Scraper._RESULTS_COND_TIMEOUT)
        if not lock_acquired:
            raise RuntimeError("Failed to acquire lock to get append latest result")
        # end if

        self._results.append(result)
        self._results_cond.release()
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
    Scraper thread

    @note  This is a thread's main loop. Use conditions and events to interact with it
    @param scraper: (Scraper) Scraper instance
    """

    scrape_interval_s: float = 60.0 * 5.0
    keep_alive: bool = True

    # Synch with next sharp minute
    remaining_secs = time() % 60
    debug(f"{remaining_secs:2.1f} seconds remaining until next scrape")
    keep_alive = not scraper._thread_evt.wait(remaining_secs)

    while keep_alive:
        scrape_time = time()
        result = ScrapeResult()
        result._scrape_time = scrape_time

        scraper._append_result(result)

        # Sleep & check if we need to loop
        keep_alive = not scraper._thread_evt.wait(scrape_interval_s)
    # end def
# end def
