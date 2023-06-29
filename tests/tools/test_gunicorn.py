from unittest.mock import ANY, MagicMock, patch

from vbcore.standalone.wsgi_gunicorn import WorkerType
from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.wsgi_gunicorn.GUnicornServer")
def test_wsgi_gunicorn(mock_gunicorn, runner):
    factory = "app:create_app"
    instance = MagicMock()
    mock_gunicorn.return_value = instance

    result = runner.invoke(
        main,
        [
            "gunicorn",
            "--app",
            factory,
            "--workers",
            "1",
            "--threads",
            "4",
            "--user",
            "0",
            "--group",
            "0",
            "--worker-type",
            "uvicorn",
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_gunicorn.assert_called_once_with(
        app=factory,
        bind=("127.0.0.1:8000",),
        workers=1,
        threads=4,
        timeout=60,
        backlog=2048,
        keepalive=5,
        pidfile=".gunicorn.pid",
        proc_name="gunicorn",
        chdir=ANY,
        user="0",
        group="0",
        worker_connections=1000,
        worker_class=None,
        worker_type=WorkerType.UVICORN,
    )

    instance.run_forever.assert_called_once_with()
