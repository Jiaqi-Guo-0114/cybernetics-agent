"""
钉钉 Webhook 渠道。

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

from ..core import AlertEvent
from .base import AlertChannel


class DingTalkChannel(AlertChannel):
    """钉钉自定义机器人 Webhook。"""
    name = "dingtalk"

    def __init__(self, webhook_url: str, secret: str | None = None, timeout: float = 10.0) -> None:
        self.webhook_url = webhook_url
        self.secret = secret
        self.timeout = timeout

    def send(self, event: AlertEvent) -> bool:
        """发送告警到钉钉。"""
        payload: dict[str, Any] = {
            "msgtype": "text",
            "text": {
                "content": f"[告警:{event.severity.upper()}] {event.rule_name}\n{event.message}",
            },
        }
        url = self.webhook_url
        if self.secret:
            timestamp = str(int(time.time() * 1000))
            sign = self._sign(timestamp, self.secret)
            url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
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
        """生成钉钉签名。"""
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        return urllib.parse.quote(base64.b64encode(hmac_code).decode("utf-8"))
