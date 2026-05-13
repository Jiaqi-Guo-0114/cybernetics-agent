"""Alert Channels 错误处理 Mock 测试"""
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

class TestAlertChannelsErrorHandling:
    @patch("urllib.request.urlopen")
    def test_dingtalk_error_response(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{"errcode": 1, "errmsg": "error"}')
        ch = DingTalkChannel("https://oapi.dingtalk.com/robot/send?access_token=test", "secret123")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_discord_error_response(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{"message": "error"}')
        ch = DiscordChannel("https://discord.com/api/webhooks/test")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("smtplib.SMTP")
    def test_email_error(self, mock_smtp):
        mock_smtp.side_effect = Exception("SMTP error")
        ch = EmailChannel("smtp.test.com", 587, "user", "pass", "from@test.com", ["to@test.com"])
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_feishu_error_response(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{"code": 1, "msg": "error"}')
        ch = FeishuChannel("https://open.feishu.cn/open-apis/bot/v2/hook/test", "secret123")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_slack_error_response(self, mock_urlopen):
        mock_urlopen.return_value = Mock(read=lambda: b'{"ok": false, "error": "invalid"}')
        ch = SlackChannel("https://hooks.slack.com/services/test")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_error_response(self, mock_urlopen):
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError("url", 500, "error", {}, None)
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))

    @patch("urllib.request.urlopen")
    def test_webhook_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("URL error")
        ch = WebhookChannel("https://example.com/webhook")
        ch.send(AlertEvent("r", "warning", "hello"))
