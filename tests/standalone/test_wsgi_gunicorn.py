from unittest.mock import ANY, call, MagicMock, patch

from vbcore.standalone.wsgi_gunicorn import GUnicornServer
from vbcore.tester.asserter import Asserter


@patch("gunicorn.app.base.Config.set")
def test_load_config(mock_set_config):
    server = GUnicornServer(MagicMock())

    calls = mock_set_config.call_args_list
    Asserter.assert_len(calls, 33)

    Asserter.assert_equals(calls[0], call("on_starting", server._on_starting))
    Asserter.assert_equals(calls[1], call("on_reload", server._on_reload))
    Asserter.assert_equals(calls[2], call("when_ready", server._when_ready))
    Asserter.assert_equals(calls[3], call("pre_fork", server._pre_fork))
    Asserter.assert_equals(calls[4], call("post_fork", server._post_fork))
    Asserter.assert_equals(calls[5], call("post_worker_init", server._post_worker_init))
    Asserter.assert_equals(calls[6], call("worker_int", server._worker_int))
    Asserter.assert_equals(calls[7], call("pre_exec", server._pre_exec))
    Asserter.assert_equals(calls[8], call("worker_abort", server._worker_abort))
    Asserter.assert_equals(calls[9], call("pre_request", server.pre_request))
    Asserter.assert_equals(calls[10], call("post_request", server.post_request))
    Asserter.assert_equals(calls[11], call("child_exit", server._child_exit))
    Asserter.assert_equals(calls[12], call("worker_exit", server._worker_exit))
    Asserter.assert_equals(calls[13], call("nworkers_changed", server._nworkers_changed))
    Asserter.assert_equals(calls[14], call("on_exit", server._on_exit))
    Asserter.assert_equals(calls[15], call("errorlog", "-"))
    Asserter.assert_equals(calls[16], call("accesslog", "-"))
    Asserter.assert_equals(calls[17], call("bind", ["0.0.0.0:8000"]))
    Asserter.assert_equals(calls[18], call("pidfile", ".gunicorn.pid"))
    Asserter.assert_equals(calls[19], call("proc_name", None))
    Asserter.assert_equals(calls[20], call("timeout", 60))
    Asserter.assert_equals(calls[21], call("backlog", 2048))
    Asserter.assert_equals(calls[22], call("keepalive", 5))
    Asserter.assert_equals(calls[23], call("chdir", ANY))
    Asserter.assert_equals(calls[24], call("user", ANY))
    Asserter.assert_equals(calls[25], call("group", ANY))
    Asserter.assert_equals(calls[26], call("forwarded_allow_ips", "127.0.0.1"))
    Asserter.assert_equals(calls[27], call("worker_class", "gthread"))
    Asserter.assert_equals(calls[28], call("threads", ANY))
    Asserter.assert_equals(calls[29], call("workers", ANY))
    Asserter.assert_equals(calls[30], call("worker_connections", 1000))
    Asserter.assert_equals(calls[31], call("loglevel", "info"))
    Asserter.assert_equals(calls[32], call("access_log_format", server.access_log_format))
