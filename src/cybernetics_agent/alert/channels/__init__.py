"""
告警渠道集合。

每个渠道单独实现，零依赖。
"""

from __future__ import annotations

from .base import AlertChannel
from .dingtalk import DingTalkChannel
from .discord import DiscordChannel
from .email import EmailChannel
from .feishu import FeishuChannel
from .slack import SlackChannel
from .stdout import StdoutChannel
from .webhook import WebhookChannel

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
