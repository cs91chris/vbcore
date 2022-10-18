import logging

from vbcore.standalone.wsgi_gunicorn import GUnicornServer

logging.basicConfig(level=logging.DEBUG)


def app(environ, start_response):
    _ = environ

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"Hello World"]


if __name__ == "__main__":
    server = GUnicornServer(
        "wsgi_gunicorn:app",
        bind="localhost:5000",
        loglevel="debug",
    )
    server.run_forever()
