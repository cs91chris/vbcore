import os
import smtplib
import typing as t
from dataclasses import dataclass
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid, parseaddr

from vbcore.files import FileHandler
from vbcore.misc import get_uuid
from vbcore.types import CoupleStr, OptStr, StrDict, StrList, StrTuple

AddressType = t.Union[str, StrTuple]


@dataclass(frozen=True)
class SMTPResponse:
    message_id: str
    response: t.Dict[str, t.Tuple[int, bytes]]


@dataclass(frozen=True, kw_only=True)
class SMTPParams:
    host: str
    port: int
    timeout: int = 10
    debug: bool = False
    is_ssl: bool = False
    is_tls: bool = False
    user: OptStr = None
    password: OptStr = None
    sender: t.Optional[t.Union[str, CoupleStr]] = None


@dataclass(frozen=True)
class MessageData:
    subject: str
    priority: int = 3
    html: OptStr = None
    text: OptStr = None
    message_id: OptStr = None
    headers: t.Optional[StrDict] = None
    attachments: t.Optional[StrList] = None


@dataclass(frozen=True)
class MessageAddresses:
    sender: str
    to: AddressType  # pylint: disable=invalid-name
    cc: AddressType = ()  # pylint: disable=invalid-name
    bcc: AddressType = ()
    reply_to: OptStr = None


class SendMail:
    def __init__(self, params: SMTPParams, **kwargs):
        self.params = params
        self._smtp_args = kwargs

    @classmethod
    def prepare_addresses(cls, addr: AddressType) -> str:
        return ",".join(addr) if isinstance(addr, tuple) else addr

    @classmethod
    def add_attachments(cls, message: MIMEBase, files: StrList):
        for filename in files:
            with FileHandler(filename).open_binary() as file:
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

    def get_smtp_class(self) -> t.Union[t.Type[smtplib.SMTP_SSL], t.Type[smtplib.SMTP]]:
        return smtplib.SMTP_SSL if self.params.is_ssl else smtplib.SMTP

    def get_instance(self, **kwargs) -> t.Union[smtplib.SMTP_SSL, smtplib.SMTP]:
        smtp_class = self.get_smtp_class()
        smtp_options = {**self._smtp_args, **kwargs}
        return smtp_class(self.params.host, self.params.port, **smtp_options)

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
        sender: OptStr = None,
        priority: int = 3,
        html: OptStr = None,
        text: OptStr = None,
        reply_to: OptStr = None,
        message_id: OptStr = None,
        cc: t.Optional[AddressType] = (),
        bcc: t.Optional[AddressType] = (),
        headers: t.Optional[StrDict] = None,
        attachments: t.Optional[StrList] = None,
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
