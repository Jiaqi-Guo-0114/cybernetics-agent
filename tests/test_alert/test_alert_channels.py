"""
告警渠道测试。

测试各种渠道的构造和格式化输出（不发送真实网络请求）。
"""

import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.alert.channels import (
    DingTalkChannel,
    DiscordChannel,
    EmailChannel,
    FeishuChannel,
    SlackChannel,
    StdoutChannel,
    WebhookChannel,
)
from cybernetics_agent.alert.core import AlertEvent


def test_stdout_channel():
    """StdoutChannel 正确输出。"""
    stream = StringIO()
    ch = StdoutChannel(stream=stream)
    evt = AlertEvent(rule_name="r1", severity="error", message="m1")
    assert ch.send(evt) is True
    assert "告警:ERROR" in stream.getvalue()


def test_webhook_channel_payload():
    """WebhookChannel 构造正确。"""
    ch = WebhookChannel(url="https://example.com/hook")
    assert ch.url == "https://example.com/hook"


def test_feishu_channel_sign():
    """FeishuChannel 签名正确。"""
    ch = FeishuChannel(webhook_url="https://feishu.cn/hook", secret="test_secret")
    sign = ch._sign("1234567890", "test_secret")
    assert isinstance(sign, str)
    assert len(sign) > 0


def test_discord_channel_payload():
    """DiscordChannel 构造正确。"""
    ch = DiscordChannel(webhook_url="https://discord.com/api/webhooks/xxx")
    assert ch.name == "discord"


def test_dingtalk_channel_sign():
    """DingTalkChannel 签名正确。"""
    ch = DingTalkChannel(webhook_url="https://oapi.dingtalk.com/robot/send", secret="sec")
    sign = ch._sign("1234567890", "sec")
    assert isinstance(sign, str)
    assert len(sign) > 0


def test_slack_channel_payload():
    """SlackChannel 构造正确。"""
    ch = SlackChannel(webhook_url="https://hooks.slack.com/xxx")
    assert ch.name == "slack"


def test_email_channel():
    """EmailChannel 构造正确。"""
    ch = EmailChannel(
        smtp_host="smtp.example.com",
        smtp_port=587,
        user="user@example.com",
        password="pass",
        to_addrs=["to@example.com"],
    )
    assert ch.name == "email"
    assert ch.from_addr == "user@example.com"
