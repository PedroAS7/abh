from abh.src.log import *
import threading


class ManagedThread:

    _THREAD_JOIN_TIMEOUT = 5.0
    _RESULTS_COND_TIMEOUT = 2.0

    def __init__(self, name: str) -> None:
        self._name: str = name
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._thread_evt: threading.Event = threading.Event()
    # end def

    def run_thread(self, t_func: callable = None) -> None:

        if not t_func:
            raise RuntimeError("t_func is None")
        # end if

        if self._running:
            raise RuntimeError(f"Thread '{self._name}' is already running")
        # end if

        self._thread_evt.clear()
        self._thread = threading.Thread(target=t_func, args=[self])
        self._thread.start()
        self._running = True
        debug(f"Thread '{self._name}' started")
    # end def

    def stop_thread(self) -> None:

        if not self._running:
            raise RuntimeError(f"Thread '{self._name}' is not running")
        # end if

        log(f"Stopping thread '{self._name}'...")
        self._thread_evt.set()
        try:
            while self._thread.is_alive():
                self._thread.join(ManagedThread._THREAD_JOIN_TIMEOUT)

                # Thread stopped
                if not self._thread.is_alive():
                    self._running = False
                    debug(f"Thread '{self._name}' stopped")
                    break
                # end if
                
                warn(f"Thread '{self._name}' failed to stop. Retrying")
            # end while
        except TimeoutError:
            error(f"Failed to stop thread '{self._name}'")
        # end try
    # end def

    def keep_alive(self) -> bool:
        return not self._thread_evt.is_set()
    # end def

    def event_wait(self, timeout) -> bool:
        return not self._thread_evt.wait(timeout)
    # end def
# end class
