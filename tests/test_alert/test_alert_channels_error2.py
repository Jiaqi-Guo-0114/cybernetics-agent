"""Alert Channels 错误处理路径补充测试"""
import pytest
import sys
from unittest.mock import Mock, patch
sys.path.insert(0, 'src')

from cybernetics_agent.alert.channels.email import EmailChannel
from cybernetics_agent.alert.channels.webhook import WebhookChannel
from cybernetics_agent.alert.core import AlertEvent

class TestAlertChannelsErrorPaths:
    @patch("smtplib.SMTP")
    def test_email_send_error(self, mock_smtp):
        mock_smtp.side_effect = Exception("SMTP error")
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", "from@test.com", ["to@test.com"])
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_json_error(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'invalid json')
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("URL error")
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))
