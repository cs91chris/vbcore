from unittest.mock import MagicMock, patch

from vbcore.net.sendmail import SMTPParams
from vbcore.tester.asserter import Asserter
from vbcore.tools.entrypoint import main


@patch("vbcore.tools.sendmail.SendMail")
def test_sendmail(mock_sendmail, runner, tmpdir, sendmail_envvar):
    _ = sendmail_envvar
    text_file = tmpdir.join("message.txt")
    text_file.write("sample message")

    attach_1 = tmpdir.join("attach-1.txt")
    attach_2 = tmpdir.join("attach-2.txt")
    attach_1.write("")
    attach_2.write("")

    attach_file_1 = f"{attach_1.dirname}/{attach_1.basename}"
    attach_file_2 = f"{attach_2.dirname}/{attach_2.basename}"

    mock_instance = MagicMock()
    mock_sendmail.return_value = mock_instance
    result = runner.invoke(
        main,
        [
            "sendmail",
            "--subject",
            "subject",
            "--to",
            "to@mail.com",
            "--text",
            f"{text_file.dirname}/{text_file.basename}",
            "-a",
            attach_file_1,
            "-a",
            attach_file_2,
        ],
    )

    Asserter.assert_none(result.exception, error=result.output)
    Asserter.assert_equals(result.exit_code, 0)

    mock_sendmail.assert_called_once_with(
        SMTPParams(
            host="localhost",
            port=22,
            timeout=10,
            debug=False,
            is_ssl=True,
            is_tls=False,
            user="user",
            password="password",
            sender="sender@mail.com",
        )
    )
    mock_instance.send_message.assert_called_once_with(
        subject="subject",
        to="to@mail.com",
        cc=None,
        reply_to=None,
        text="sample message",
        html=None,
        attachments=(attach_file_1, attach_file_2),
    )
