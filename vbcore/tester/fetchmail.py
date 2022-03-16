import time
import typing as t

from vbcore.datastruct import ObjectDict
from vbcore.http.client import HTTPClient


class FetchMail(HTTPClient):
    """
    Fetch emails from sendria
    """

    def __init__(
        self,
        endpoint: str,
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        retry: int = 3,
        wait: int = 1,
        timeout: int = 3,
    ):
        super().__init__(
            endpoint, username=username, password=password, timeout=timeout
        )
        self.retry = retry
        self.wait = wait

    def fetch(self, recipient: str, subject: str) -> t.List[ObjectDict]:
        response = []
        resp = self.request("/", raise_on_exc=True)
        emails = resp.body.data if isinstance(resp.body, ObjectDict) else resp
        for email in emails:
            if recipient in email.recipients_envelope:
                if subject and email.subject != subject:
                    continue
                response.append(email)

        return response

    def perform(
        self, recipient: str, subject: str, delete: bool = True
    ) -> t.List[ObjectDict]:
        for _ in range(0, self.retry):
            res = self.fetch(recipient, subject)
            if delete:
                for r in res:
                    self.request(uri=f"/{r.id}", method="DELETE")
            if res:
                return res

            time.sleep(self.wait)
        return []
