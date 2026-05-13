"""
通用 HTTP Webhook 渠道。

支持自定义 URL 和 headers。
"""

from __future__ import annotations

import json
import urllib.request

from ..core import AlertEvent
from .base import AlertChannel


class WebhookChannel(AlertChannel):
    """通用 HTTP Webhook 渠道。"""
    name = "webhook"

    def __init__(self, url: str, headers: dict[str, str] | None = None, timeout: float = 10.0) -> None:
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout

    def send(self, event: AlertEvent) -> bool:
        """发送告警到 Webhook。"""
        payload = json.dumps(event.to_dict(), ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=payload,
            headers=self.headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status < 400
        except Exception:
            return False

    def health_check(self) -> bool:
        """健康检查。"""
        try:
            req = urllib.request.Request(self.url, method="HEAD")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status < 500
        except Exception:
            return False
