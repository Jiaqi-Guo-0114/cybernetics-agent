"""
告警渠道集合。

每个渠道单独实现，零依赖。
"""

from __future__ import annotations

from .base import AlertChannel
from .stdout import StdoutChannel
from .webhook import WebhookChannel
from .feishu import FeishuChannel
from .discord import DiscordChannel
from .dingtalk import DingTalkChannel
from .slack import SlackChannel
from .email import EmailChannel

__all__ = [
    "AlertChannel",
    "StdoutChannel",
    "WebhookChannel",
    "FeishuChannel",
    "DiscordChannel",
    "DingTalkChannel",
    "SlackChannel",
    "EmailChannel",
]
