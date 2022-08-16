import dataclasses
import logging
import os
import smtplib
import typing as t
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid, parseaddr
from smtplib import SMTP

from email_validator import caching_resolver, validate_email, ValidatedEmail

from vbcore.misc import CommonRegex
from vbcore.uuid import get_uuid

AddressType = t.Union[str, t.Tuple[str, ...]]


@dataclasses.dataclass
class SMTPResponse:
    message_id: str
    response: t.Dict[str, t.Tuple[int, bytes]]


@dataclasses.dataclass(frozen=True)
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


@dataclasses.dataclass(frozen=True)
class MessageData:
    subject: str
    priority: int = 3
    html: t.Optional[str] = None
    text: t.Optional[str] = None
    headers: t.Optional[t.Dict[str, str]] = None
    message_id: t.Optional[str] = None
    attachments: t.Optional[t.List[str]] = None


@dataclasses.dataclass(frozen=True)
class MessageAddresses:
    sender: str
    to: AddressType
    reply_to: t.Optional[str] = None
    cc: AddressType = ()
    bcc: AddressType = ()


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

    @classmethod
    def add_attachments(cls, message: MIMEBase, files: t.List[str]):
        for filename in files:
            with open(filename, "rb") as file:
                attach = MIMEApplication(file.read())
                filename = os.path.basename(filename)
                attach.add_header(
                    "Content-Disposition", f"attachment; filename={filename}"
                )
                message.attach(attach)

    @classmethod
    def message(cls, addresses: MessageAddresses, data: MessageData) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["From"] = addresses.sender
        message["Subject"] = data.subject
        message["X-Priority"] = str(data.priority)
        message["Reply-To"] = addresses.reply_to or addresses.sender
        message["To"] = cls.prepare_addresses(addresses.to)
        message["Date"] = formatdate(localtime=True)
        message["Message-Id"] = make_msgid(
            idstring=str(data.message_id or get_uuid()),
            domain=parseaddr(addresses.sender)[1].split("@")[1],
        )

        if addresses.cc:
            message["Cc"] = cls.prepare_addresses(addresses.cc)
        if addresses.bcc:
            message["Bcc"] = cls.prepare_addresses(addresses.bcc)

        if data.headers:
            for k, v in data.headers.items():
                message.add_header(k, v)

        if data.text:
            message.attach(MIMEText(data.text, "plain"))
        if data.html:
            message.attach(MIMEText(data.html, "html"))

        cls.add_attachments(message, data.attachments or [])
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

    # pylint: disable=too-many-arguments,too-many-locals
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
        attachments: t.Optional[t.List[str]] = None,
        **kwargs,
    ) -> SMTPResponse:
        _sender = sender or str(self.params.sender) or self.params.user
        message = self.message(
            MessageAddresses(
                to=to,
                sender=_sender,
                reply_to=reply_to,
                cc=cc,
                bcc=bcc,
            ),
            MessageData(
                subject=subject,
                priority=priority,
                html=html,
                text=text,
                headers=headers,
                message_id=message_id,
                attachments=attachments,
            ),
        )
        return self.send(message, **kwargs)
