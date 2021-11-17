import atexit

from logging import config as logging_config
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

valid_ident = logging_config.valid_ident
# noinspection PyUnresolvedReferences
ConvertingDict = logging_config.ConvertingDict  # type: ignore
# noinspection PyUnresolvedReferences
ConvertingList = logging_config.ConvertingList  # type: ignore


class QueueListenerHandler(QueueHandler):
    def __init__(
        self, handlers, respect_handler_level=False, auto_run=True, queue=Queue(-1)
    ):
        queue = self._resolve_queue(queue)
        super().__init__(queue)
        handlers = self._resolve_handlers(handlers)
        # noinspection PyUnresolvedReferences
        self._listener = QueueListener(
            self.queue, *handlers, respect_handler_level=respect_handler_level
        )
        if auto_run:
            self.start()
            atexit.register(self.stop)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    @staticmethod
    def _resolve_handlers(h):
        if not isinstance(h, ConvertingList):
            return h
        return [h[i] for i in range(len(h))]

    @staticmethod
    def _resolve_queue(q):
        if not isinstance(q, ConvertingDict):
            return q
        if "__resolved_value__" in q:
            return q["__resolved_value__"]

        cname = q.pop("class")
        klass = q.configurator.resolve(cname)
        props = q.pop(".", None) or {}
        kwargs = {k: q[k] for k in q if valid_ident(k)}
        result = klass(**kwargs)
        for name, value in props.items():
            setattr(result, name, value)

        q["__resolved_value__"] = result
        return result
