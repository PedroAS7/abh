"""
Copyright 2024 PeterAS17 (www.peteras17.me)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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

    def run_thread(self, t_func: callable) -> None:

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
            self._thread.join(ManagedThread._THREAD_JOIN_TIMEOUT)

            # Thread did not stop
            if self._thread.is_alive():
                raise TimeoutError()
            # end if

            self._running = False
            debug(f"Thread '{self._name}' stopped")
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
