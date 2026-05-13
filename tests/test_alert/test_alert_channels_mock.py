"""Alert Channels Mock 测试"""
import pytest
import sys
from unittest.mock import Mock, patch
sys.path.insert(0, 'src')

from cybernetics_agent.alert.channels.dingtalk import DingTalkChannel
from cybernetics_agent.alert.channels.discord import DiscordChannel
from cybernetics_agent.alert.channels.email import EmailChannel
from cybernetics_agent.alert.channels.feishu import FeishuChannel
from cybernetics_agent.alert.channels.slack import SlackChannel
from cybernetics_agent.alert.channels.webhook import WebhookChannel

from cybernetics_agent.alert.core import AlertEvent

class TestAlertChannelsMock:
    @patch("urllib.request.urlopen")
    def test_dingtalk_send(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{"errcode": 0}')
        ch = DingTalkChannel("https://oapi.dingtalk.com/robot/send?access_token=test", "secret123")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_discord_send(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{}')
        ch = DiscordChannel("https://discord.com/api/webhooks/test")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("smtplib.SMTP")
    def test_email_send(self, mock_smtp):
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", "from@test.com", ["to@test.com"])
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_feishu_send(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{"code": 0}')
        ch = FeishuChannel("https://open.feishu.cn/open-apis/bot/v2/hook/test", "secret123")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_slack_send(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{"ok": true}')
        ch = SlackChannel("https://hooks.slack.com/services/test")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_send(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{}')
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_send_error(self, mock_urlopen):
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError("url", 500, "error", {}, None)
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))
