"""Alert Channels 最终补充测试"""
import sys
from unittest.mock import Mock, patch

sys.path.insert(0, 'src')

from cybernetics_agent.alert.channels.email import EmailChannel
from cybernetics_agent.alert.channels.webhook import WebhookChannel
from cybernetics_agent.alert.core import AlertEvent


class TestAlertChannelsFinal:
    @patch("smtplib.SMTP")
    def test_email_send_exception(self, mock_smtp):
        mock_smtp.side_effect = Exception("SMTP fail")
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", "from@test.com", ["to@test.com"])
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("smtplib.SMTP")
    def test_email_send_server_error(self, mock_smtp):
        mock_smtp.return_value = Mock(
            starttls=lambda: None,
            login=lambda u, p: None,
            sendmail=lambda f, t, m: (_ for _ in ()).throw(Exception("send fail")),
            quit=lambda: None,
        )
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", "from@test.com", ["to@test.com"])
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_invalid_json(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'not json')
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_url_exception(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("URL fail")
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))
