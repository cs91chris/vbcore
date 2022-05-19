import abc
import asyncio
import dataclasses
import logging
import threading
import typing as t
from contextlib import contextmanager
from enum import auto
from queue import Queue

from vbcore.datastruct import StrEnum

try:
    import nest_asyncio
except ImportError:
    nest_asyncio = None


class BatchExecutor:
    def __init__(self, tasks: t.Optional[list] = None, **__):
        """

        :param tasks:
        """
        self._tasks = tasks or []

    @staticmethod
    def prepare_task(task: t.Union[t.Tuple, t.Callable]) -> t.Tuple[t.Callable, dict]:
        """

        :param task:
        :return:
        """
        if callable(task):
            return task, {}

        if len(task) > 1:
            return task[0], task[1] or {}

        return task[0], {}

    def run(self) -> t.List:
        responses = []
        for task in self._tasks:
            func, args = self.prepare_task(task)
            responses.append(func(**args))
        return responses


class AsyncBatchExecutor(BatchExecutor):
    def __init__(self, return_exceptions: bool = False, **kwargs):
        """

        :param tasks:
        :param return_exceptions:
        """
        super().__init__(**kwargs)
        self._return_exceptions = return_exceptions

    @staticmethod
    async def _executor(fun: t.Callable, **kwargs):
        return fun(**kwargs)  # pragma: no cover

    @staticmethod
    def is_async(fun: t.Callable):
        return asyncio.iscoroutinefunction(fun)

    async def batch(self):
        tasks = []
        for task in self._tasks:
            func, args = self.prepare_task(task)
            if not self.is_async(func):
                tasks.append(self._executor(func, **args))  # pragma: no cover
            else:
                tasks.append(func(**args))

        return await asyncio.gather(*tasks, return_exceptions=self._return_exceptions)

    def run(self) -> t.List:
        try:
            asyncio.get_running_loop()
            if nest_asyncio is not None:
                # noinspection PyUnresolvedReferences
                nest_asyncio.apply()  # pragma: no cover
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.batch())


class Thread(threading.Thread):
    def __init__(
        self,
        runnable: t.Callable,
        *args,
        params: t.Optional[dict] = None,
        daemon: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._runnable = runnable
        self._args = args
        self._params = params or {}
        self.response = None
        self.daemon = daemon

    def run(self):
        self.response = self._runnable(*self._args, **self._params)


class DaemonThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, daemon=True, **kwargs)

    def run(self):
        self._runnable(*self._args, **self._params)


class ThreadBatchExecutor(BatchExecutor):
    def __init__(
        self,
        thread_class: t.Optional[t.Type[Thread]] = None,
        single_thread: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._single_thread = single_thread
        self._thread_class = thread_class or Thread

        if self._single_thread:
            self._tasks[0] = self._thread_class(super().run)
            return

        for i, task in enumerate(self._tasks):
            if isinstance(task, dict):
                thread = self._thread_class(**task)
            else:
                func, args = self.prepare_task(task)
                thread = self._thread_class(func, params=args)
            self._tasks[i] = thread

    def run(self) -> t.Optional[t.List]:
        for task in self._tasks:
            task.start()

        for task in self._tasks:
            if task.daemon is False:
                task.join()
            else:
                return None

        if self._single_thread:
            return self._tasks[0].response

        return [task.response for task in self._tasks]


class WorkersType(StrEnum):
    PRODUCER = auto()
    CONSUMER = auto()


@dataclasses.dataclass
class BatchSize:
    pool_workers: int = 5
    producer_queue: int = 0
    consumer_queue: int = 0
    worker_type: WorkersType = WorkersType.PRODUCER


class PCTask(abc.ABC):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._log = logging.getLogger(self.__module__)

    @abc.abstractmethod
    def perform(self, item):
        pass  # pragma: no cover


class IProducerConsumerBatchExecutor(abc.ABC):
    def __init__(
        self,
        producer: PCTask,
        consumer: PCTask,
        *_,
        **__,
    ):
        self._producer = producer
        self._consumer = consumer
        self.is_running: bool = False
        self._log = logging.getLogger(self.__module__)

    @contextmanager
    def runner(self):
        if not self.is_running:
            self.startup()
        yield self
        self.barrier()

    def startup(self):
        self.is_running = True

    def barrier(self):
        self.is_running = False

    @abc.abstractmethod
    def consumer(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def producer(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def load(self, item):
        pass  # pragma: no cover

    def run_on(self, items: t.Iterable):
        with self.runner() as executor:
            for item in items:
                executor.load(item)


class LinearExecutor(IProducerConsumerBatchExecutor):
    def consumer(self):
        """No consumer required"""

    def producer(self):
        """No producer required"""

    def load(self, item):
        product = self._producer.perform(item)
        self._consumer.perform(product)


class ProducerConsumerBatchExecutor(IProducerConsumerBatchExecutor):
    def __init__(
        self,
        producer: PCTask,
        consumer: PCTask,
        *args,
        batch_size: t.Optional[BatchSize] = None,
        thread_class: t.Type[Thread] = Thread,
        **kwargs,
    ):
        super().__init__(producer, consumer, *args, **kwargs)
        self._thread_class = thread_class
        self.size: BatchSize = batch_size or BatchSize()
        self._consumer_queue: Queue = Queue(self.size.consumer_queue)
        self._producer_queue: Queue = Queue(self.size.producer_queue)

    def startup(self):
        workers = (
            (self.producer, WorkersType.PRODUCER)
            if self.size.worker_type == WorkersType.PRODUCER
            else (self.consumer, WorkersType.CONSUMER)
        )
        single = (
            (self.consumer, WorkersType.CONSUMER)
            if self.size.worker_type == WorkersType.PRODUCER
            else (self.producer, WorkersType.PRODUCER)
        )
        self.start_threads(single, workers)
        super().startup()

    def start_threads(
        self,
        single: t.Tuple[t.Callable, WorkersType],
        workers: t.Tuple[t.Callable, WorkersType],
    ):
        self._thread_class(single[0], daemon=True, name=single[1]).start()
        for num in range(0, self.size.pool_workers):
            name = f"{workers[1]}-{num+1}"
            self._thread_class(workers[0], daemon=True, name=name).start()

    def consumer(self):
        while True:
            item = self._consumer_queue.get()
            try:
                self._consumer.perform(item)
            except Exception as exc:  # pylint: disable=broad-except
                self._log.exception(exc)
            finally:
                self._consumer_queue.task_done()

    def producer(self):
        while True:
            item = self._producer_queue.get()
            try:
                item = self._producer.perform(item)
                self._consumer_queue.put(item)
            except Exception as exc:  # pylint: disable=broad-except
                self._log.exception(exc)
            finally:
                self._producer_queue.task_done()

    def barrier(self):
        self._producer_queue.join()
        self._consumer_queue.join()
        super().barrier()

    def load(self, item):
        self._producer_queue.put(item)
