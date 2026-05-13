"""Alert Channels 最终补充测试"""
import pytest
import sys
from unittest.mock import Mock, patch
sys.path.insert(0, 'src')

from cybernetics_agent.alert.channels.email import EmailChannel
from cybernetics_agent.alert.channels.webhook import WebhookChannel
from cybernetics_agent.alert.core import AlertEvent

class TestAlertChannelsFinal:
    @patch("smtplib.SMTP")
    def test_email_with_metric(self, mock_smtp):
        mock_smtp.return_value = Mock(
            __enter__=lambda s: s,
            __exit__=lambda *args: None,
            starttls=lambda: None,
            login=lambda u, p: None,
            sendmail=lambda f, t, m: None,
        )
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", ["to@test.com"])
        evt = AlertEvent("r", "warning", "hello", metric_name="cpu", metric_value=90.0)
        result = ch.send(evt)
        assert result is True

    @patch("smtplib.SMTP")
    def test_email_health_check(self, mock_smtp):
        mock_smtp.return_value = Mock(
            __enter__=lambda s: s,
            __exit__=lambda *args: None,
            ehlo=lambda: None,
        )
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", ["to@test.com"])
        result = ch.health_check()
        assert result is True

    @patch("urllib.request.urlopen")
    def test_webhook_send_success(self, mock_urlopen):
        mock_resp = Mock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *args: None
        mock_urlopen.return_value = mock_resp
        ch = WebhookChannel("https://example.com/webhook")
        evt = AlertEvent("r", "warning", "hello")
        result = ch.send(evt)
        assert result is True

    @patch("urllib.request.urlopen")
    def test_webhook_health_check(self, mock_urlopen):
        mock_resp = Mock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *args: None
        mock_urlopen.return_value = mock_resp
        ch = WebhookChannel("https://example.com/webhook")
        result = ch.health_check()
        assert result is True
