import os
import typing as t
from multiprocessing import cpu_count

from decouple import Choices, Csv, UndefinedValueError
from gunicorn import util
from gunicorn.app.base import BaseApplication  # type: ignore

from vbcore.configurator import config, load_dotenv
from vbcore.enums import EnumMixin, StrEnum
from vbcore.importer import Importer
from vbcore.types import MISSING

# Supported env vars:
#  - GU_BIND
#  - GU_PID_FILE
#  - GU_PROC_NAME
#  - GU_TIMEOUT
#  - GU_BACKLOG
#  - GU_KEEP_ALIVE
#  - GU_CHDIR
#  - GU_USER
#  - GU_GROUP
#  - GU_FORWARDED_ALLOW_IPS
#  - GU_WORKER_CLASS
#  - GU_CONCURRENCY
#  - GU_WORKER_CONNECTIONS
#  - GU_LOG_LEVEL
#  - GU_ACCESS_LOG_FORMAT

LOG_LEVELS = ["debug", "info", "warning", "error"]


class WorkerType(EnumMixin, StrEnum):
    DEFAULT = "gthread"
    UVICORN = "uvicorn.workers.UvicornWorker"
    MEINHELD = "meinheld.gmeinheld.MeinheldWorker"


# pylint: disable=too-many-public-methods
class GUnicornServer(BaseApplication):
    def __init__(
        self,
        app: t.Union[str, t.Callable],
        worker_type: t.Optional[WorkerType] = None,
        **kwargs,
    ):
        load_dotenv()
        self.worker_type = worker_type or WorkerType.DEFAULT
        self.application = app
        self.options = kwargs
        super().__init__()

    def from_env_config(
        self, conf_key: str, opt_key: str, default: t.Any = MISSING, **kwargs
    ):
        _default = self.options.get(opt_key, default)
        if default == _default == MISSING:
            self.cfg.set(opt_key, config(conf_key, **kwargs))
            return
        try:
            self.cfg.set(opt_key, config(conf_key, **kwargs))
        except UndefinedValueError:
            self.cfg.set(opt_key, _default)

    def set_default_config(self):
        self.cfg.set("errorlog", "-")
        self.cfg.set("accesslog", "-")

    def load_from_env(self):
        self.from_env_config("GU_BIND", "bind", ["0.0.0.0:8000"], cast=Csv())
        self.from_env_config("GU_PID_FILE", "pidfile", ".gunicorn.pid")
        self.from_env_config("GU_PROC_NAME", "proc_name", None)
        self.from_env_config("GU_TIMEOUT", "timeout", 60, cast=int)
        self.from_env_config("GU_BACKLOG", "backlog", 2048, cast=int)
        self.from_env_config("GU_KEEP_ALIVE", "keepalive", 5, cast=int)
        self.from_env_config("GU_CHDIR", "chdir", util.getcwd())
        self.from_env_config("GU_USER", "user", os.geteuid())
        self.from_env_config("GU_GROUP", "group", os.getegid())
        self.from_env_config(
            "GU_FORWARDED_ALLOW_IPS", "forwarded_allow_ips", "127.0.0.1"
        )
        self.from_env_config("GU_WORKER_CLASS", "worker_class", self.worker_type.value)
        self.from_env_config("GU_THREADS", "threads", cpu_count() * 2 + 1, cast=int)
        self.from_env_config("GU_WORKERS", "workers", cpu_count(), cast=int)
        self.from_env_config(
            "GU_WORKER_CONNECTIONS", "worker_connections", 1000, cast=int
        )
        self.from_env_config(
            "GU_LOG_LEVEL", "loglevel", "info", cast=Choices(LOG_LEVELS)
        )
        self.from_env_config(
            "GU_ACCESS_LOG_FORMAT", "access_log_format", self.access_log_format
        )

    @property
    def access_log_format(self):
        return (
            ' %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
            " %({x-request-id}i)s %(L)s"  # custom
        )

    def set_hooks(self):
        self.cfg.set("on_starting", self._on_starting)
        self.cfg.set("on_reload", self._on_reload)
        self.cfg.set("when_ready", self._when_ready)
        self.cfg.set("pre_fork", self._pre_fork)
        self.cfg.set("post_fork", self._post_fork)
        self.cfg.set("post_worker_init", self._post_worker_init)
        self.cfg.set("worker_int", self._worker_int)
        self.cfg.set("pre_exec", self._pre_exec)
        self.cfg.set("worker_abort", self._worker_abort)
        self.cfg.set("pre_request", self.pre_request)
        self.cfg.set("post_request", self.post_request)
        self.cfg.set("child_exit", self._child_exit)
        self.cfg.set("worker_exit", self._worker_exit)
        self.cfg.set("nworkers_changed", self._nworkers_changed)
        self.cfg.set("on_exit", self._on_exit)

    def do_load_config(self):
        self.load_default_config()
        self.load_config()

    def load_config(self):
        self.set_hooks()
        self.set_default_config()
        for key, value in self.options.items():
            if value is not MISSING:
                self.cfg.set(key.lower(), value)
        self.load_from_env()

    def load(self):
        if isinstance(self.application, str):
            return Importer.from_module(self.application)
        return self.application

    # noinspection PyMethodMayBeStatic
    def init(self, parser, opts, args):
        _ = parser, opts, args

    def run_forever(self):
        self.run()

    @classmethod
    def _on_starting(cls, server):
        server.log.debug("server (pid: %s) is starting...", server.pid)
        cls.on_starting(server)

    @classmethod
    def _on_reload(cls, server):
        server.log.info("server (pid: %s) is reloading...", server.pid)
        cls.on_reload(server)

    @classmethod
    def _when_ready(cls, server):
        server.log.info("server (pid: %s) is ready. Spawning workers", server.pid)
        cls.when_ready(server)

    @classmethod
    def _pre_fork(cls, server, worker):
        server.log.debug("pre fork (pid: %s)", worker.pid)
        cls.pre_fork(server, worker)

    @classmethod
    def _post_fork(cls, server, worker):
        server.log.debug("worker spawned (pid: %s)", worker.pid)
        cls.post_fork(server, worker)

    @classmethod
    def _post_worker_init(cls, worker):
        worker.log.debug("worker (pid: %s) has initialized the application", worker.pid)
        cls.post_worker_init(worker)

    @classmethod
    def _worker_int(cls, worker):
        worker.log.info("worker (pid: %s) received INT or QUIT signal", worker.pid)
        cls.worker_int(worker)

    @classmethod
    def _pre_exec(cls, server):
        server.log.info("server (pid: %s) forked child, re-executing...", server.pid)
        cls.pre_exec(server)

    @classmethod
    def _worker_abort(cls, worker):
        worker.log.info("worker (pid: %s) received SIGABRT signal", worker.pid)
        cls.worker_abort(worker)

    @classmethod
    def _child_exit(cls, server, worker):
        server.log.debug("child worker (pid: %s) exited", worker.pid)
        cls.child_exit(server, worker)

    @classmethod
    def _worker_exit(cls, server, worker):
        server.log.debug("worker (pid: %s) exited", worker.pid)
        cls.worker_exit(server, worker)

    @classmethod
    def _nworkers_changed(cls, server, new_value, old_value):
        server.log.info(
            "number of workers changed from %s to %s", old_value or 0, new_value
        )
        cls.nworkers_changed(server, new_value, old_value)

    @classmethod
    def _on_exit(cls, server):
        server.log.info("server (pid: %s) exited", server.pid)
        cls.on_exit(server)

    @classmethod
    def on_starting(cls, server):
        _ = server

    @classmethod
    def on_reload(cls, server):
        _ = server

    @classmethod
    def when_ready(cls, server):
        _ = server

    @classmethod
    def pre_fork(cls, server, worker):
        _ = server, worker

    @classmethod
    def post_fork(cls, server, worker):
        _ = server, worker

    @classmethod
    def post_worker_init(cls, worker):
        _ = worker

    @classmethod
    def worker_int(cls, worker):
        _ = worker

    @classmethod
    def pre_exec(cls, server):
        _ = server

    @classmethod
    def worker_abort(cls, worker):
        _ = worker

    @classmethod
    def pre_request(cls, worker, req):
        _ = worker, req

    @classmethod
    def post_request(cls, worker, req, environ, resp):
        _ = worker, req, environ, resp

    @classmethod
    def child_exit(cls, server, worker):
        _ = server, worker

    @classmethod
    def worker_exit(cls, server, worker):
        _ = server, worker

    @classmethod
    def nworkers_changed(cls, server, new_value, old_value):
        _ = server, new_value, old_value

    @classmethod
    def on_exit(cls, server):
        _ = server
