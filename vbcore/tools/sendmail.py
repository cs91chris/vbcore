import click

from vbcore.files import FileHandler
from vbcore.net.sendmail import SendMail, SMTPParams
from vbcore.tools.cli import Cli, CliInputFile, CliOpt, CliReqOpt


@click.command(name="sendmail")
@CliReqOpt.string("-H", "--host")
@CliReqOpt.integer("-P", "--port")
@CliReqOpt.string("-u", "--user")
@CliReqOpt.string("-p", "--password")
@CliReqOpt.string("-s", "--sender")
@CliReqOpt.string("-S", "--subject")
@CliReqOpt.string("--to")
@CliOpt.string("--cc")
@CliOpt.string("--reply-to")
@CliOpt.flag("-v", "--debug")
@CliOpt.flag("--is-ssl")
@CliOpt.flag("--is-tls")
@CliOpt.integer("-t", "--timeout", default=10)
@CliOpt.string("--text", type=CliInputFile())
@CliOpt.string("--html", type=CliInputFile())
@CliOpt.multi("-a", "--attachments", type=CliInputFile())
# pylint: disable=too-many-arguments,too-many-locals
def sendmail(
    host,
    port,
    timeout,
    debug,
    is_ssl,
    is_tls,
    user,
    password,
    sender,
    subject,
    to,
    cc,
    reply_to,
    text,
    html,
    attachments,
):
    params = SMTPParams(
        host=host,
        port=port,
        timeout=timeout,
        debug=debug,
        is_ssl=is_ssl,
        is_tls=is_tls,
        user=user,
        password=password,
        sender=sender,
    )
    client = SendMail(params)

    if html:
        with FileHandler().open(html) as file:
            html = file.read()
    if text:
        with FileHandler().open(text) as file:
            text = file.read()

    response = client.send_message(
        subject=subject,
        to=to,
        cc=cc,
        reply_to=reply_to,
        text=text,
        html=html,
        attachments=attachments,
    )
    Cli.print(f"message-id: {response.message_id}")
