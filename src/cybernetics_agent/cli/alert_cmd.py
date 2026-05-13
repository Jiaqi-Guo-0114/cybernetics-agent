"""
告警管理命令。

提供渠道测试、规则状态查看、手动触发告警等功能。
"""

from __future__ import annotations

import json
import sys
from typing import Any

from ..alert.channels import (
    DiscordChannel,
    DingTalkChannel,
    EmailChannel,
    FeishuChannel,
    SlackChannel,
    StdoutChannel,
    WebhookChannel,
)
from ..alert.core import AlertEvent


CHANNEL_MAP: dict[str, type] = {
    "stdout": StdoutChannel,
    "webhook": WebhookChannel,
    "feishu": FeishuChannel,
    "discord": DiscordChannel,
    "dingtalk": DingTalkChannel,
    "slack": SlackChannel,
    "email": EmailChannel,
}


def _load_config(path: str) -> dict[str, Any]:
    """加载配置文件。"""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _create_channel(name: str, cfg: dict[str, Any]) -> Any:
    """根据配置创建渠道实例。"""
    cls = CHANNEL_MAP.get(name)
    if not cls:
        return None
    try:
        if name == "stdout":
            return StdoutChannel()
        elif name == "webhook":
            return WebhookChannel(url=cfg["url"], headers=cfg.get("headers"), timeout=cfg.get("timeout", 10.0))
        elif name == "feishu":
            return FeishuChannel(webhook_url=cfg["webhook_url"], secret=cfg.get("secret"), timeout=cfg.get("timeout", 10.0))
        elif name == "discord":
            return DiscordChannel(webhook_url=cfg["webhook_url"], timeout=cfg.get("timeout", 10.0))
        elif name == "dingtalk":
            return DingTalkChannel(webhook_url=cfg["webhook_url"], secret=cfg.get("secret"), timeout=cfg.get("timeout", 10.0))
        elif name == "slack":
            return SlackChannel(webhook_url=cfg["webhook_url"], timeout=cfg.get("timeout", 10.0))
        elif name == "email":
            return EmailChannel(
                smtp_host=cfg["smtp_host"],
                smtp_port=cfg["smtp_port"],
                user=cfg["user"],
                password=cfg["password"],
                to_addrs=cfg["to_addrs"],
                from_addr=cfg.get("from_addr"),
                use_tls=cfg.get("use_tls", True),
                timeout=cfg.get("timeout", 10.0),
            )
    except Exception:
        return None
    return None


def run_alert_test(parsed: Any) -> int:
    """测试告警渠道。"""
    config = _load_config(parsed.config)
    alert_cfg = config.get("alert", {})
    channels_cfg = alert_cfg.get("channels", {})

    test_evt = AlertEvent(
        rule_name="cli_test",
        severity="info",
        message="这是一条 CLI 测试告警",
    )

    target = parsed.channel
    results = []

    for name, cfg in channels_cfg.items():
        if target and name != target:
            continue
        if not cfg.get("enabled", True):
            continue
        ch = _create_channel(name, cfg)
        if not ch:
            results.append((name, False, "未知渠道类型"))
            continue
        try:
            ok = ch.send(test_evt)
            results.append((name, ok, "发送成功" if ok else "发送失败"))
        except Exception as e:
            results.append((name, False, str(e)))

    if not results:
        print("未找到配置的告警渠道。" if target else "未配置告警渠道。")
        return 0

    print(f"{'渠道':<12} {'状态':<8} {'信息'}")
    print("-" * 50)
    for name, ok, msg in results:
        status = "✅ 通过" if ok else "❌ 失败"
        print(f"{name:<12} {status:<8} {msg}")

    return 0 if all(r[1] for r in results) else 1


def run_alert_status(parsed: Any) -> int:
    """查看告警规则状态。"""
    config = _load_config(parsed.config)
    alert_cfg = config.get("alert", {})
    rules = alert_cfg.get("rules", [])
    channels_cfg = alert_cfg.get("channels", {})

    if not rules:
        print("未配置告警规则。")
        return 0

    print(f"{'规则名称':<20} {'类型':<12} {'指标':<16} {'操作':<6} {'阈值':<8} {'严重性':<8} {'渠道'}")
    print("-" * 90)
    for rule in rules:
        print(
            f"{rule.get('name', 'N/A'):<20} "
            f"{rule.get('type', 'N/A'):<12} "
            f"{rule.get('metric', 'N/A'):<16} "
            f"{rule.get('operator', 'N/A'):<6} "
            f"{rule.get('threshold', 'N/A'):<8} "
            f"{rule.get('severity', 'warning'):<8} "
            f"{', '.join(rule.get('channels', []))}"
        )

    print(f"\n活动渠道: {', '.join(n for n, c in channels_cfg.items() if c.get('enabled', True))}")
    return 0


def run_alert_fire(parsed: Any) -> int:
    """手动触发告警。"""
    config = _load_config(parsed.config)
    alert_cfg = config.get("alert", {})
    channels_cfg = alert_cfg.get("channels", {})

    evt = AlertEvent(
        rule_name="manual_fire",
        severity=parsed.severity,
        message=parsed.message,
    )

    target = parsed.channel
    sent = False

    for name, cfg in channels_cfg.items():
        if target and name != target:
            continue
        if not cfg.get("enabled", True):
            continue
        ch = _create_channel(name, cfg)
        if not ch:
            continue
        try:
            ch.send(evt)
            sent = True
            print(f"[{name}] 告警已发送。")
        except Exception as e:
            print(f"[{name}] 发送失败: {e}")

    if not sent:
        print("未能发送告警到任何渠道。")
        return 1

    return 0


def run_alert(parsed: Any) -> int:
    """告警命令入口。"""
    sub = parsed.alert_command
    if sub == "test":
        return run_alert_test(parsed)
    elif sub == "status":
        return run_alert_status(parsed)
    elif sub == "fire":
        return run_alert_fire(parsed)
    else:
        print("未知的告警子命令。用法: cybernetix alert {test|status|fire}")
        return 1
