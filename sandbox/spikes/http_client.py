import logging

from vbcore.http.client import HTTPClient

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    client = HTTPClient("http://httpbin.org", dump_body=True)
    response = client.get("/anything", headers={"TEST": "TEST"})
