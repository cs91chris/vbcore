import dataclasses
import smtplib
import typing as t
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate, parseaddr
from smtplib import SMTP

RespType = t.Dict[str, t.Tuple[int, bytes]]
AddressType = t.Union[str, t.Tuple[str, ...]]


# pylint: disable=too-many-instance-attributes
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
    smtp_class: t.Optional[t.Type[SMTP]] = None
    smtp_extra_args: dict = dataclasses.field(default_factory=dict)


class SendMail:
    def __init__(self, params: SMTPParams):
        self.params = params

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
        smtp_class: t.Type[smtplib.SMTP] = smtplib.SMTP
        if params.smtp_class is not None:
            smtp_class = params.smtp_class
        elif params.is_ssl:
            smtp_class = smtplib.SMTP_SSL

        smtp_options = {**params.smtp_extra_args, **kwargs}
        return smtp_class(params.host, params.port, **smtp_options)

    def check_recipient(self, email: str, **kwargs) -> bool:
        with self.get_instance(**kwargs) as server:
            server.helo()
            server.mail(str(self.params.sender) or self.params.user)
            response = server.rcpt(email)
            if response[0] == 250:
                return True
            if response[0] == 550:
                return False
            raise smtplib.SMTPException(response)

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
