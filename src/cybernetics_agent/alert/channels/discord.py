"""
Discord Webhook 渠道。
"""

from __future__ import annotations

import json
import urllib.request

from ..core import AlertEvent
from .base import AlertChannel


class DiscordChannel(AlertChannel):
    """Discord Webhook 渠道。"""
    name = "discord"

    def __init__(self, webhook_url: str, timeout: float = 10.0) -> None:
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send(self, event: AlertEvent) -> bool:
        """发送告警到 Discord。"""
        color_map = {
            "info": 3447003,
            "warning": 16776960,
            "error": 15158332,
            "critical": 16711680,
        }
        payload = {
            "embeds": [{
                "title": f"告警: {event.rule_name}",
                "description": event.message,
                "color": color_map.get(event.severity, 3447003),
                "fields": [],
            }],
        }
        if event.metric_name:
            payload["embeds"][0]["fields"].append({
                "name": event.metric_name,
                "value": str(event.metric_value),
                "inline": True,
            })

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status < 400
        except Exception:
            return False
