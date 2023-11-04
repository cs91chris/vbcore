from asyncio import AbstractEventLoop, get_event_loop, Queue
from signal import SIGABRT, SIGINT, Signals, SIGTERM
from typing import Iterable, Optional, Union

from vbcore.datastruct.lazy import SignalDumper
from vbcore.loggers import VBLoggerMixin


class Heartbeat(VBLoggerMixin):
    def __init__(
        self,
        delay: float = 30,
        loop: Optional[AbstractEventLoop] = None,
        stop_signals: Iterable[Union[int, Signals]] = (),
    ):
        self.delay = delay
        self._queue: Queue = Queue()
        self.loop = loop or get_event_loop()
        self.stop_signals = stop_signals or (SIGINT, SIGTERM, SIGABRT)

    def register_signals(self) -> None:
        def handler_wrapper(s: Signals) -> None:
            self.log.info("received signal %s", SignalDumper(s))
            self.shutdown()

        for sig in self.stop_signals:
            try:
                _s = Signals(sig)
                self.loop.add_signal_handler(_s.value, lambda s=_s: handler_wrapper(s))
                self.log.info("registered shutdown handler on signal %s", SignalDumper(_s))
            except Exception as exc:  # pylint: disable=broad-except
                self.log.exception(exc)
                self.log.error("unable to register shutdown handler for signal %s", sig)

    def start(self) -> None:
        self.register_signals()
        self.pulse()
        self.log.info("started heartbeat")

    def shutdown(self) -> None:
        self._queue.put_nowait(False)
        self.log.info("stopped heartbeat")

    def beat_hook(self) -> None:
        """subclass can hook at beat time"""

    def heartbeat(self) -> None:
        self.log.debug("received heartbeat: still alive")
        self.beat_hook()
        self._queue.put_nowait(True)

    def pulse(self) -> None:
        self.loop.call_later(self.delay, self.heartbeat)

    async def run_forever(self) -> None:
        while await self._queue.get():
            self.pulse()
