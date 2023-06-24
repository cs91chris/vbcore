import click

from vbcore.files import FileHandler
from vbcore.net.sendmail import SendMail, SMTPParams
from vbcore.tools.cli import Cli, CliInputFile, CliOpt, CliReqOpt


def load_optional_file(file):
    if not file:
        return None
    with FileHandler().open(file) as fp:
        return fp.read()


@click.command(name="sendmail", help="send an email")
@CliReqOpt.string("-H", "--host", envvar="SMTP_HOST")
@CliReqOpt.integer("-P", "--port", envvar="SMTP_PORT")
@CliReqOpt.string("-u", "--user", envvar="SMTP_USER")
@CliReqOpt.string("-p", "--password", envvar="SMTP_PASSWORD")
@CliReqOpt.string("-s", "--sender", envvar="SMTP_SENDER")
@CliReqOpt.string("-S", "--subject")
@CliReqOpt.string("--to")
@CliOpt.string("--cc")
@CliOpt.string("--reply-to")
@CliOpt.flag("-v", "--debug")
@CliOpt.flag("--is-ssl", envvar="SMTP_IS_SSL")
@CliOpt.flag("--is-tls", envvar="SMTP_IS_TLS")
@CliOpt.integer("-t", "--timeout", default=10)
@CliOpt.string("--text", type=CliInputFile())
@CliOpt.string("--html", type=CliInputFile())
@CliOpt.multi("-a", "--attachments", type=CliInputFile())
def sendmail(subject, to, cc, reply_to, text, html, attachments, **kwargs):
    client = SendMail(SMTPParams(**kwargs))  # pylint: disable=missing-kwoa

    response = client.send_message(
        subject=subject,
        to=to,
        cc=cc,
        reply_to=reply_to,
        text=load_optional_file(text),
        html=load_optional_file(html),
        attachments=attachments,
    )
    Cli.print(f"message-id: {response.message_id}")
