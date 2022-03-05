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
from vbcore.uuid import get_uuid

AddressType = t.Union[str, t.Tuple[str, ...]]


@dataclasses.dataclass
class SMTPResponse:
    message_id: str
    response: t.Dict[str, t.Tuple[int, bytes]]


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

    @classmethod
    def validate_email(cls, email: str, restricted: bool = True) -> ValidatedEmail:
        if restricted and not CommonRegex.is_valid_email(email):
            raise ValueError(f"invalid email: {email}")
        return validate_email(email, dns_resolver=caching_resolver())

    @classmethod
    def prepare_addresses(cls, addr: AddressType) -> str:
        return ",".join(addr) if isinstance(addr, tuple) else addr

    # pylint: disable=too-many-arguments
    @classmethod
    def message(
        cls,
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
        message_id: t.Optional[str] = None,
    ) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["From"] = sender
        message["Subject"] = subject
        message["X-Priority"] = str(priority)
        message["Reply-To"] = reply_to or sender
        message["To"] = cls.prepare_addresses(to)
        message["Date"] = formatdate(localtime=True)
        message["Message-Id"] = make_msgid(
            idstring=str(message_id or get_uuid()),
            domain=parseaddr(sender)[1].split("@")[1],
        )

        if cc:
            message["Cc"] = cls.prepare_addresses(cc)
        if bcc:
            message["Bcc"] = cls.prepare_addresses(bcc)

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

    def send(self, message: MIMEMultipart, **kwargs) -> SMTPResponse:
        params = self.params
        with self.get_instance(**kwargs) as server:
            if params.is_tls:
                server.starttls()
            if params.user:
                server.login(params.user, params.password)

            server.set_debuglevel(params.debug)
            return SMTPResponse(
                message_id=message["Message-Id"],
                response=server.send_message(message),
            )

    # pylint: disable=too-many-arguments
    def send_message(
        self,
        subject: str,
        to: AddressType,
        sender: t.Optional[str] = None,
        priority: int = 3,
        html: t.Optional[str] = None,
        text: t.Optional[str] = None,
        reply_to: t.Optional[str] = None,
        cc: t.Optional[AddressType] = (),
        bcc: t.Optional[AddressType] = (),
        headers: t.Optional[t.Dict[str, str]] = None,
        message_id: t.Optional[str] = None,
        **kwargs,
    ) -> SMTPResponse:
        _sender = sender or str(self.params.sender) or self.params.user
        message = self.message(
            subject=subject,
            to=to,
            sender=_sender,
            priority=priority,
            html=html,
            text=text,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
            headers=headers,
            message_id=message_id,
        )
        return self.send(message, **kwargs)
