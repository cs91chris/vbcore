import os
from multiprocessing import cpu_count
from typing import TYPE_CHECKING

import click

from vbcore.datastruct.lazy import LazyImporter
from vbcore.tools.cli import CliOpt, CliReqOpt

if TYPE_CHECKING:
    from vbcore.standalone.wsgi_gunicorn import GUnicornServer, WorkerType
else:
    GUnicornServer, WorkerType = LazyImporter.import_many(
        "vbcore.standalone.wsgi_gunicorn:GUnicornServer",
        "vbcore.standalone.wsgi_gunicorn:WorkerType",
        message="you must install gunicorn",
    )


@click.command(name="gunicorn")
@CliReqOpt.string("-a", "--app")
@CliOpt.multi("-b", "--bind", envvar="GU_BIND", default=["127.0.0.1:8000"])
@CliOpt.integer("-w", "--workers", envvar="GU_WORKERS", default=cpu_count())
@CliOpt.integer("-t", "--threads", envvar="GU_THREADS", default=cpu_count() * 2 + 1)
@CliOpt.integer("--worker-connections", envvar="GU_WORKER_CONNECTIONS", default=1000)
@CliOpt.integer("-T", "--timeout", envvar="GU_TIMEOUT", default=60)
@CliOpt.integer("--backlog", envvar="GU_BACKLOG", default=2048)
@CliOpt.integer("--keepalive", envvar="GU_KEEP_ALIVE", default=5)
@CliOpt.string("--pidfile", envvar="GU_PID_FILE", default=".gunicorn.pid")
@CliOpt.string("--proc-name", envvar="GU_PROC_NAME", default="gunicorn")
@CliOpt.string("--chdir", envvar="GU_CHDIR", default=os.getcwd())
@CliOpt.string("-u", "--user", envvar="GU_USER", default=os.geteuid())
@CliOpt.string("-g", "--group", envvar="GU_GROUP", default=os.getegid())
@CliOpt.string("--worker-class", envvar="GU_WORKER_CLASS")
@CliOpt.choice(
    "-W",
    "--worker-type",
    envvar="GU_WORKER_TYPE",
    default="DEFAULT",
    values=["DEFAULT", "UVICORN", "MEINHELD"],
    callback=lambda _, __, x: WorkerType(x.upper()),
    case_sensitive=False,
)
def main(**kwargs):
    """start the gunicorn server"""
    server = GUnicornServer(**kwargs)
    server.run_forever()
