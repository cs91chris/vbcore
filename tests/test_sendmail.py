import re
import unittest
from email.utils import parsedate
from unittest.mock import MagicMock

from vbcore.sendmail import SendMail, SMTPParams


class MockSmtp(SendMail):
    smtp_class = MagicMock()

    @staticmethod
    def is_valid_rfc_2822_date(date):
        return bool(parsedate(date))


class ModuleTest(unittest.TestCase):
    def setUp(self):
        self.client = MockSmtp(SMTPParams(host="127.0.0.1", port=25))
        self.message_id_regex = re.compile(
            r"^<[0-9]*\.[0-9]*\.[0-9]*\.[a-z0-9]{32}@mail.com>$"
        )

    def test_prepare_message(self):
        message = self.client.message(
            subject="TEST MAIL",
            to="destination@mail.com",
            sender="sender@mail.com",
            html="<h1>TEST MAIL</h1>",
            text="TEST MAIL",
            reply_to="reply@mail.com",
            cc=("cc@mail.com",),
            bcc=("bcc@mail.com",),
            headers={
                "X-Custom-Header": "value",
            },
        )

        self.assertTrue(message.is_multipart())
        self.assertTrue(self.client.is_valid_rfc_2822_date(message["Date"]))
        self.assertTrue(self.message_id_regex.match(message["Message-Id"]))
        self.assertEqual(message["From"], "sender@mail.com")
        self.assertEqual(message["Subject"], "TEST MAIL")
        self.assertEqual(message["Reply-To"], "reply@mail.com")
        self.assertEqual(message["To"], "destination@mail.com")
        self.assertEqual(message["Cc"], "cc@mail.com")
        self.assertEqual(message["Bcc"], "bcc@mail.com")
        self.assertEqual(message["X-Priority"], "3")
        self.assertEqual(message["X-Custom-Header"], "value")
        self.assertEqual(message.get_content_type(), "multipart/alternative")
        self.assertEqual(message.get_payload(0).get_content_type(), "text/plain")
        self.assertEqual(message.get_payload(1).get_content_type(), "text/html")

    def test_sendmail(self):
        response = self.client.send_message(
            subject="TEST MAIL",
            to="destination@mail.com",
            sender="sender@mail.com",
            html="<h1>TEST MAIL</h1>",
            text="TEST MAIL",
            reply_to="reply@mail.com",
            cc=("cc@mail.com",),
            bcc=("bcc@mail.com",),
            headers={
                "X-Custom-Header": "value",
            },
        )
        self.assertTrue(self.message_id_regex.match(response.message_id))
