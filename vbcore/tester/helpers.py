import typing as t
from base64 import b64encode

from vbcore.tester.fetchmail import FetchMail


def fetch_emails(subject: str, recipient: t.Optional[str] = None, **kwargs):
    client = FetchMail(**kwargs)
    return client.perform(recipient=recipient, subject=subject)


def basic_auth_header(username: str, password: str) -> t.Dict[str, str]:
    token = b64encode(f"{username}:{password}".encode()).decode()
    return dict(Authorization=f"Basic {token}")


def build_url(url: str, **params) -> t.Tuple[str, str]:
    args = "&".join([f"{k}={v}" for k, v in params.items()])
    if args:
        return f"{url}?{args}", args
    return url, ""


def do_not_dump_long_string(field: str):
    if field and len(field) < 20:
        return field
    return "None" if not field else ""
