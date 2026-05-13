"""
Slack Incoming Webhook 渠道。
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

from .base import AlertChannel
from ..core import AlertEvent


class SlackChannel(AlertChannel):
    """Slack Incoming Webhook 渠道。"""
    name = "slack"

    def __init__(self, webhook_url: str, timeout: float = 10.0) -> None:
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send(self, event: AlertEvent) -> bool:
        """发送告警到 Slack。"""
        color_map = {
            "info": "#36a64f",
            "warning": "#daa520",
            "error": "#ff0000",
            "critical": "#8b0000",
        }
        payload = {
            "attachments": [{
                "color": color_map.get(event.severity, "#36a64f"),
                "title": f"告警: {event.rule_name}",
                "text": event.message,
                "fields": [],
            }],
        }
        if event.metric_name:
            payload["attachments"][0]["fields"].append({
                "title": event.metric_name,
                "value": str(event.metric_value),
                "short": True,
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
