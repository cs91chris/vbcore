import asyncio
import threading
import typing as t

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
