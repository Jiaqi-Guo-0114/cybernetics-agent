"""
SMTP 邮件渠道。

使用标准库 smtplib，零外部依赖。
"""

from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from ..core import AlertEvent
from .base import AlertChannel


class EmailChannel(AlertChannel):
    """SMTP 邮件渠道。"""
    name = "email"

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        user: str,
        password: str,
        to_addrs: list[str],
        from_addr: str | None = None,
        use_tls: bool = True,
        timeout: float = 10.0,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.user = user
        self.password = password
        self.to_addrs = to_addrs
        self.from_addr = from_addr or user
        self.use_tls = use_tls
        self.timeout = timeout

    def send(self, event: AlertEvent) -> bool:
        """发送告警邮件。"""
        subject = f"[告警:{event.severity.upper()}] {event.rule_name}"
        body = f"{event.message}\n\n"
        if event.metric_name:
            body += f"指标: {event.metric_name} = {event.metric_value}\n"
        body += f"时间: {event.timestamp}"

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(self.to_addrs)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_addr, self.to_addrs, msg.as_string())
            return True
        except Exception:
            return False

    def health_check(self) -> bool:
        """健康检查。"""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout) as server:
                server.ehlo()
                return True
        except Exception:
            return False
