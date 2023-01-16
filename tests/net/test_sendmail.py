import base64
import os
import re
import tempfile
import unittest
from email.utils import parsedate
from unittest.mock import MagicMock

from vbcore.http.headers import ContentTypeEnum
from vbcore.net.sendmail import MessageAddresses, MessageData, SendMail, SMTPParams


class MockSmtp(SendMail):
    smtp_class = MagicMock()

    def get_smtp_class(self):
        return self.smtp_class

    @staticmethod
    def is_valid_rfc_2822_date(date):
        return bool(parsedate(date))


class ModuleTest(unittest.TestCase):
    def setUp(self):
        # pylint: disable=consider-using-with
        self.tmp_dir = tempfile.TemporaryDirectory()

        self.to_cc = "cc@mail.com"
        self.to_bcc = "bcc@mail.com"
        self.sender = "sender@mail.com"
        self.reply_to = "reply@mail.com"
        self.recipient = "destination@mail.com"
        self.client = MockSmtp(SMTPParams(host="127.0.0.1", port=25))
        self.message_id_regex = re.compile(r"^<\d*\.\d*\.\d*\.[a-z0-9]{32}@mail.com>$")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_prepare_message(self):
        message = self.client.message(
            MessageAddresses(
                to=self.recipient,
                sender=self.sender,
                reply_to=self.reply_to,
                cc=(self.to_cc,),
                bcc=(self.to_bcc,),
            ),
            MessageData(
                subject="TEST MAIL",
                html="<h1>TEST MAIL</h1>",
                text="TEST MAIL",
                headers={
                    "X-Custom-Header": "value",
                },
            ),
        )

        self.assertTrue(message.is_multipart())
        self.assertTrue(self.client.is_valid_rfc_2822_date(message["Date"]))
        self.assertTrue(self.message_id_regex.match(message["Message-Id"]))
        self.assertEqual(message["From"], self.sender)
        self.assertEqual(message["Reply-To"], self.reply_to)
        self.assertEqual(message["To"], self.recipient)
        self.assertEqual(message["Cc"], self.to_cc)
        self.assertEqual(message["Bcc"], self.to_bcc)
        self.assertEqual(message["X-Priority"], "3")
        self.assertEqual(message["Subject"], "TEST MAIL")
        self.assertEqual(message["X-Custom-Header"], "value")
        self.assertEqual(message.get_content_type(), "multipart/alternative")
        self.assertEqual(message.get_payload(0).get_content_type(), "text/plain")
        self.assertEqual(message.get_payload(1).get_content_type(), "text/html")

    def test_sendmail(self):
        response = self.client.send_message(
            to=self.recipient,
            sender=self.sender,
            reply_to=self.reply_to,
            cc=(self.to_cc,),
            bcc=(self.to_bcc,),
            subject="TEST MAIL",
            html="<h1>TEST MAIL</h1>",
            text="TEST MAIL",
            headers={
                "X-Custom-Header": "value",
            },
        )
        self.assertTrue(self.message_id_regex.match(response.message_id))

    def test_attachment(self):
        content = b"TEST"
        filename = os.path.join(self.tmp_dir.name, "test.xlsx")
        with open(filename, "wb") as file:
            file.write(content)

        message = self.client.message(
            addresses=MessageAddresses(to=self.recipient, sender=self.sender),
            data=MessageData(subject="subject"),
        )
        self.client.add_attachments(message, [filename])

        attach = message.get_payload(0)
        encoded_content = base64.b64encode(content).decode()
        self.assertEqual(attach.get_payload(), f"{encoded_content}\n")
        self.assertEqual(attach.get_content_type(), ContentTypeEnum.STREAM)
        self.assertEqual(attach.get_content_disposition(), "attachment")
        self.assertEqual(attach.get_filename(), "test.xlsx")
