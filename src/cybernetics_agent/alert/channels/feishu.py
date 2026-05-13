"""
飞书 Webhook 渠道。

支持签名验证。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import urllib.request
from typing import Any

from .base import AlertChannel
from ..core import AlertEvent


class FeishuChannel(AlertChannel):
    """飞书自定义机器人 Webhook。"""
    name = "feishu"

    def __init__(self, webhook_url: str, secret: str | None = None, timeout: float = 10.0) -> None:
        self.webhook_url = webhook_url
        self.secret = secret
        self.timeout = timeout

    def send(self, event: AlertEvent) -> bool:
        """发送告警到飞书。"""
        timestamp = str(int(time.time()))
        payload: dict[str, Any] = {
            "msg_type": "text",
            "content": {
                "text": f"[告警:{event.severity.upper()}] {event.rule_name}\n{event.message}",
            },
        }
        if self.secret:
            sign = self._sign(timestamp, self.secret)
            payload["timestamp"] = timestamp
            payload["sign"] = sign

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

    def _sign(self, timestamp: str, secret: str) -> str:
        """生成飞书签名。"""
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(hmac_code).decode("utf-8")
