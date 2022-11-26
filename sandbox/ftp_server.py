from pyftpdlib import servers
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler


class MyHandler(FTPHandler):
    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        pass

    def on_login(self, username):
        pass

    def on_logout(self, username):
        pass

    def on_file_sent(self, file):
        pass

    def on_file_received(self, file):
        pass

    def on_incomplete_file_sent(self, file):
        pass

    def on_incomplete_file_received(self, file):
        import os

        os.remove(file)


def main(host: str, port: int):
    authorizer = DummyAuthorizer()
    authorizer.add_user("user", "12345", "./TMP/user", perm="elradfmwMT")
    authorizer.add_anonymous("./TMP/nobody")

    dtp_handler = ThrottledDTPHandler
    dtp_handler.read_limit = 30 * 1024  # 30 Kb/sec
    dtp_handler.write_limit = 30 * 1024  # 30 Kb/sec

    handler = MyHandler
    handler.authorizer = authorizer
    handler.dtp_handler = dtp_handler

    server = servers.FTPServer((host, port), handler)
    server.serve_forever()


if __name__ == "__main__":
    main(host="0.0.0.0", port=21021)
