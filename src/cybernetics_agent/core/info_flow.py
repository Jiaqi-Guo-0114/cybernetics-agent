"""
信息流模块。

管理信息传递的信噪比、去重、速率限制。
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base import CyberneticsEvent, EventType, ICyberneticsModule


@dataclass
class DedupWindow:
    """去重窗口记录。"""
    key: str
    timestamp: float
    count: int = 1


class InfoFlow(ICyberneticsModule):
    """
    信息流模块。

    核心能力：
    1. 事件去重（在时间窗口内重复事件只保留一次）
    2. 速率限制（限制事件发射频率）
    3. 噪声过滤（过滤无关紧要的事件）
    4. 信息通道管理（控制事件流向哪些模块）

    配置示例（cybernetics.json）：
        "info_flow": {
            "enabled": true,
            "filters": [
                {"type": "deduplicate", "params": {"window_seconds": 5}},
                {"type": "rate_limit", "params": {"max_events_per_second": 100}}
            ],
            "channels": ["event_bus", "metrics", "storage"]
        }
    """

    name = "info_flow"

    def __init__(self, config: Dict[str, Any], ctx: Any) -> None:
        super().__init__(config, ctx)

        # 解析过滤器配置
        self._filters: List[Dict[str, Any]] = []
        for f in config.get("filters", []):
            self._filters.append({
                "type": f.get("type", "deduplicate"),
                "params": f.get("params", {}),
            })

        self._channels: List[str] = config.get("channels", ["event_bus", "metrics", "storage"])

        # 去重状态
        self._dedup_window: Dict[str, DedupWindow] = {}
        self._dedup_window_seconds = 5.0
        for f in self._filters:
            if f["type"] == "deduplicate":
                self._dedup_window_seconds = f["params"].get("window_seconds", 5.0)

        # 速率限制状态
        self._rate_limit_max = 100
        self._rate_limit_window: List[float] = []
        for f in self._filters:
            if f["type"] == "rate_limit":
                self._rate_limit_max = f["params"].get("max_events_per_second", 100)

        # 统计
        self._deduped_count = 0
        self._throttled_count = 0
        self._filtered_count = 0

    def on_event(self, event: CyberneticsEvent) -> Optional[CyberneticsEvent]:
        """
        处理事件，应用信息流过滤。

        返回 None 表示事件被过滤掉。
        """
        # 检查速率限制
        if not self._check_rate_limit():
            self._throttled_count += 1
            return event  # 速率限制不删除事件，只是记录

        # 检查去重
        if self._is_duplicate(event):
            self._deduped_count += 1
            return None  # 去重：删除事件

        # 检查通道
        if not self._should_route(event):
            self._filtered_count += 1
            return None

        return event

    def _check_rate_limit(self) -> bool:
        """检查是否在速率限制内。"""
        now = time.time()
        self._rate_limit_window = [t for t in self._rate_limit_window if now - t < 1.0]

        if len(self._rate_limit_window) >= self._rate_limit_max:
            return False

        self._rate_limit_window.append(now)
        return True

    def _is_duplicate(self, event: CyberneticsEvent) -> bool:
        """检查事件是否是重复的。"""
        # 生成去重键：事件类型 + session_id + 关键 payload
        key_parts = [
            event.event_type.value,
            event.session_id,
        ]
        # 包含一些关键 payload 字段
        if "tool_name" in event.payload:
            key_parts.append(event.payload["tool_name"])
        if "error_type" in event.payload:
            key_parts.append(event.payload["error_type"])

        key = "|".join(key_parts)
        now = time.time()

        # 清理过期窗口
        cutoff = now - self._dedup_window_seconds
        self._dedup_window = {
            k: v for k, v in self._dedup_window.items()
            if v.timestamp > cutoff
        }

        if key in self._dedup_window:
            self._dedup_window[key].count += 1
            return True

        self._dedup_window[key] = DedupWindow(key=key, timestamp=now)
        return False

    def _should_route(self, event: CyberneticsEvent) -> bool:
        """检查事件是否应该被路由到当前模块。"""
        # 简单实现：检查通道列表
        if "event_bus" in self._channels:
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """获取模块状态。"""
        now = time.time()
        recent_events = [t for t in self._rate_limit_window if now - t < 1.0]

        return {
            "enabled": self.enabled,
            "filters": [f["type"] for f in self._filters],
            "channels": self._channels,
            "current_eps": len(recent_events),
            "max_eps": self._rate_limit_max,
            "dedup_window_size": len(self._dedup_window),
            "deduped_count": self._deduped_count,
            "throttled_count": self._throttled_count,
            "filtered_count": self._filtered_count,
        }


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/core", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    ctx = CyberneticsContext(CyberneticsConfig())
    config = {
        "enabled": True,
        "filters": [
            {"type": "deduplicate", "params": {"window_seconds": 1.0}},
            {"type": "rate_limit", "params": {"max_events_per_second": 10}},
        ],
        "channels": ["event_bus"],
    }
    info = InfoFlow(config, ctx)
    info.initialize()

    # 测试 1: 正常事件通过
    evt = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
    result = info.on_event(evt)
    assert result is evt
    print("  ✅ 测试 1 通过：正常事件通过")

    # 测试 2: 重复事件去重
    evt2 = CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"})
    result2 = info.on_event(evt2)
    assert result2 is None  # 被去重了
    assert info._deduped_count == 1
    print("  ✅ 测试 2 通过：重复事件去重")

    # 测试 3: 不同事件不去重
    evt3 = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search"})
    result3 = info.on_event(evt3)
    assert result3 is evt3
    print("  ✅ 测试 3 通过：不同事件不去重")

    # 测试 4: 速率限制
    info2 = InfoFlow(config, ctx)
    for i in range(15):
        info2.on_event(CyberneticsEvent.create(EventType.CUSTOM, "s1", {"i": i}))
    assert info2._throttled_count > 0  # 超过限制的部分被记录
    print("  ✅ 测试 4 通过：速率限制")

    # 测试 5: 状态报告
    status = info.get_status()
    assert status["deduped_count"] == 1
    assert status["filters"] == ["deduplicate", "rate_limit"]
    print("  ✅ 测试 5 通过：状态报告")

    print("\n  ✅ 信息流模块所有冒烟测试通过！")
