from datetime import datetime
from functools import partial
from textwrap import dedent
from unittest.mock import MagicMock

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    JobExecutionEvent,
)

from vbcore.standalone.scheduler import APScheduler
from vbcore.tester.asserter import Asserter


def test_factory():
    scheduler = APScheduler.factory(config={})
    Asserter.assert_isinstance(scheduler, APScheduler)


def test_dump_jobs():
    scheduler = APScheduler.factory(config={})
    str_jobs = scheduler.dump_jobs()
    expected = dedent("Pending jobs:\nNo pending jobs\n")
    Asserter.assert_equals(dedent(str_jobs).replace("  ", ""), expected)

    jobs = [
        {
            "task": lambda a: print(a),
            "trigger": "interval",
            "minutes": 2,
            "params": {"a": "A"},
        }
    ]
    scheduler.load_jobs(jobs)
    expected = dedent(
        "Pending jobs:\ntest_dump_jobs.<locals>.<lambda> (trigger: interval[0:02:00], pending)\n"
    )
    str_jobs = scheduler.dump_jobs()
    Asserter.assert_equals(dedent(str_jobs).replace("  ", ""), expected)


def test_event_listener():
    scheduler = APScheduler.factory(config={})
    event = partial(
        JobExecutionEvent, job_id="1", scheduled_run_time=datetime.now(), jobstore=MagicMock()
    )

    scheduler.event_listener(event(EVENT_JOB_ERROR))
    scheduler.event_listener(event(EVENT_JOB_ADDED))
    scheduler.event_listener(event(EVENT_JOB_EXECUTED))
