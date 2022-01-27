import dataclasses
import logging
import smtplib
import typing as t
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate, parseaddr
from smtplib import SMTP

from email_validator import caching_resolver, validate_email, ValidatedEmail

from vbcore.misc import CommonRegex

RespType = t.Dict[str, t.Tuple[int, bytes]]
AddressType = t.Union[str, t.Tuple[str, ...]]


@dataclasses.dataclass
class SMTPParams:
    host: str
    port: int
    timeout: int = 10
    debug: bool = False
    is_ssl: bool = False
    is_tls: bool = False
    user: t.Optional[str] = None
    password: t.Optional[str] = None
    sender: t.Optional[t.Union[str, t.Tuple[str, str]]] = None


class SendMail:
    smtp_class: t.Type[smtplib.SMTP] = smtplib.SMTP

    def __init__(self, params: SMTPParams, **kwargs):
        self.params = params
        self._smtp_args = kwargs
        self._log = logging.getLogger(self.__module__)

    @staticmethod
    def validate_email(email: str, restricted: bool = True) -> ValidatedEmail:
        if restricted and not CommonRegex.is_valid_email(email):
            raise ValueError(f"invalid email: {email}")
        return validate_email(email, dns_resolver=caching_resolver())

    # pylint: disable=too-many-locals
    @staticmethod
    def message(
        sender: str,
        to: AddressType,
        subject: str,
        priority: int = 3,
        html: t.Optional[str] = None,
        text: t.Optional[str] = None,
        reply_to: t.Optional[str] = None,
        cc: t.Optional[AddressType] = (),
        bcc: t.Optional[AddressType] = (),
        headers: t.Optional[t.Dict[str, str]] = None,
    ) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["From"] = sender
        message["Subject"] = subject
        message["X-Priority"] = str(priority)
        message["Reply-To"] = reply_to or sender
        message["To"] = ",".join(to) if isinstance(to, tuple) else to

        _, email = parseaddr(sender)
        sender_domain = email.split("@")[1]
        message["Message-Id"] = make_msgid(domain=sender_domain)
        message["Date"] = formatdate(localtime=True)

        if cc:
            message["Cc"] = ",".join(cc) if isinstance(cc, tuple) else cc
        if bcc:
            message["Bcc"] = ",".join(bcc) if isinstance(bcc, tuple) else bcc

        if headers:
            for k, v in headers.items():
                message.add_header(k, v)

        if text:
            message.attach(MIMEText(text, "plain"))
        if html:
            message.attach(MIMEText(html, "html"))

        return message

    def get_instance(self, **kwargs) -> SMTP:
        params = self.params
        smtp_class = smtplib.SMTP_SSL if params.is_ssl else self.smtp_class
        smtp_options = {**self._smtp_args, **kwargs}
        return smtp_class(params.host, params.port, **smtp_options)  # type: ignore

    def send(self, message: MIMEMultipart, **kwargs) -> RespType:
        params = self.params
        with self.get_instance(**kwargs) as server:
            if params.is_tls:
                server.starttls()
            if params.user:
                server.login(params.user, params.password)

            server.set_debuglevel(params.debug)
            return server.send_message(message)

    def send_message(
        self,
        subject: str,
        recipients: AddressType,
        sender: t.Optional[str] = None,
        **kwargs,
    ) -> RespType:
        _sender = sender or str(self.params.sender) or self.params.user
        return self.send(self.message(_sender, recipients, subject, **kwargs))
