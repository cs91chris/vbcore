import logging
import typing as t
from io import StringIO

from apscheduler import events as scheduler_events
from apscheduler.job import Job
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from vbcore.datastruct import Dumper, LazyDump
from vbcore.uuid import get_uuid


class APScheduler:
    def __init__(
        self,
        *args,
        scheduler: t.Type[BaseScheduler] = BlockingScheduler,
        gconfig: dict = None,
        events_to_listen: int = None,
        auto_start: bool = False,
        **kwargs,
    ):
        self.logger = logging.getLogger(self.__module__)
        super().__init__(*args, **kwargs)
        self._scheduler = scheduler(gconfig or {})
        self._events = events_to_listen or scheduler_events.EVENT_ALL
        self._scheduler.add_listener(self._event_listener, self._events)
        if auto_start:
            self._scheduler.start()

    @classmethod
    def factory(
        cls, config: dict, scheduler_class: t.Optional[t.Type[BaseScheduler]] = None
    ) -> "APScheduler":
        instance = cls(scheduler=scheduler_class, **config["SCHEDULER"])
        instance.load_jobs(config["JOBS"])
        instance.logger.info("%s", LazyDump(instance.dump_jobs))
        return instance

    @property
    def scheduler(self) -> BaseScheduler:
        return self._scheduler

    def dump_jobs(self) -> str:
        dump = StringIO()
        self._scheduler.print_jobs(out=dump)
        return dump.getvalue()

    @staticmethod
    def _repr_job_event(event: scheduler_events.SchedulerEvent):
        if isinstance(event, scheduler_events.JobEvent):
            return f"{repr(event)}-<{event.job_id}>-<{event.jobstore}>"
        return repr(event)

    def _event_listener(self, event):
        if not event.code & self._events:
            return

        self.logger.debug(
            "received event %s", Dumper(event, callback=self._repr_job_event)
        )
        if event.code == scheduler_events.EVENT_JOB_ERROR:
            self.logger.error("An error occurred when executing job: %s", event.job_id)
            self.logger.exception(event.exception)
            self.logger.error(event.traceback)
        elif event.code == scheduler_events.EVENT_JOB_ADDED:
            self.logger.info("successfully added job: %s", event.job_id)
        elif event.code == scheduler_events.EVENT_JOB_EXECUTED:
            self.logger.info(
                "successfully executed job: %s, returned value: %s",
                event.job_id,
                event.retval,
            )

    @classmethod
    def get_id(cls) -> str:
        return str(get_uuid())

    def load_jobs(self, jobs_config: t.List[dict]):
        for config in jobs_config:
            self.add_job(**config)

    def add_job(
        self,
        task: t.Union[t.Callable, str],
        *args,
        params: t.Optional[dict] = None,
        **kwargs,
    ) -> Job:
        job_id = self.get_id()
        job = self._scheduler.add_job(
            task, args=args, kwargs=params, id=job_id, **kwargs
        )
        self.logger.debug("added job '%s' with id '%s'", task, job_id)
        return job

    def __del__(self):
        try:
            self._scheduler.shutdown()
        except AttributeError:
            pass  # pragma: no cover
