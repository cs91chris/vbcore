from base64 import b64encode

from vbcore.tester.fetchmail import FetchMail


def fetch_emails(subject, recipient=None, **kwargs):
    client = FetchMail(**kwargs)
    return client.perform(recipient=recipient, subject=subject)


def basic_auth_header(username=None, password=None):
    token = b64encode(f"{username}:{password}".encode()).decode()
    return dict(Authorization=f"Basic {token}")


def build_url(url=None, **params):
    args = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{url}?{args}", args
