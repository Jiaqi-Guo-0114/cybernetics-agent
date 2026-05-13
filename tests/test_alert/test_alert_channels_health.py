"""Alert Channels health_check 异常路径"""
import pytest
import sys
from unittest.mock import patch
sys.path.insert(0, 'src')

from cybernetics_agent.alert.channels.email import EmailChannel
from cybernetics_agent.alert.channels.webhook import WebhookChannel

class TestAlertChannelsHealth:
    @patch("smtplib.SMTP")
    def test_email_health_check_fail(self, mock_smtp):
        mock_smtp.side_effect = Exception("fail")
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", ["to@test.com"])
        result = ch.health_check()
        assert result is False

    @patch("urllib.request.urlopen")
    def test_webhook_health_check_fail(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("fail")
        ch = WebhookChannel("https://example.com/webhook")
        result = ch.health_check()
        assert result is False
