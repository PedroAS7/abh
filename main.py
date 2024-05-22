from abh.src.app import run
import asyncio


if __name__ != "__main__":
    raise ImportError("File must not be imported")
# end if

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
