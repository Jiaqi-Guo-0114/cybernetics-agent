"""
分层控制模块。

实现战略/战术/执行三层架构。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .base import CyberneticsEvent, EventType, ICyberneticsModule


class LayerType(Enum):
    """分层类型。"""
    STRATEGIC = "strategic"  # 战略层：目标、分支、预算
    TACTICAL = "tactical"    # 战术层：参数、资源、调度
    EXECUTIVE = "executive"  # 执行层：工具、重试、错误恢复


@dataclass
class Decision:
    """单个决策。"""
    layer: str
    decision_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    approved: bool = True


class HierarchyController(ICyberneticsModule):
    """
    分层控制模块。

    核心能力：
    1. 分层决策：战略层、战术层、执行层
    2. 层间协调：上层决策下发给下层执行
    3. 权限控制：某些决策必须由特定层批准
    4. 决策记录：追溯决策链

    配置示例（cybernetics.json）：
        "hierarchy": {
            "enabled": true,
            "layers": [
                {"name": "strategic", "decision_types": ["goal", "branch", "budget"]},
                {"name": "tactical", "decision_types": ["parameter", "resource", "schedule"]},
                {"name": "executive", "decision_types": ["tool", "retry", "error_recovery"]}
            ]
        }
    """

    name = "hierarchy"

    def __init__(self, config: Dict[str, Any], ctx: Any) -> None:
        super().__init__(config, ctx)

        # 解析层配置
        self._layers: Dict[str, List[str]] = {}
        layer_order = []
        for layer_data in config.get("layers", []):
            name = layer_data["name"]
            types = layer_data.get("decision_types", [])
            self._layers[name] = types
            layer_order.append(name)

        self._layer_order = layer_order

        # 决策记录
        self._decisions: List[Decision] = []
        self._pending_decisions: Dict[str, Decision] = {}

        # 统计
        self._decision_count = 0
        self._override_count = 0

    def on_event(self, event: CyberneticsEvent) -> Optional[CyberneticsEvent]:
        """监听事件，确定哪一层负责处理。"""
        et = event.event_type

        # 根据事件类型确定决策层级
        if et in (EventType.AGENT_START, EventType.AGENT_END):
            self._record_decision("strategic", "session_control", event.payload)

        elif et in (EventType.TOOL_CALL, EventType.TOOL_RESULT, EventType.TOOL_ERROR,
                    EventType.RECOVERY, EventType.DEGRADATION):
            self._record_decision("executive", "tool_execution", event.payload)

        elif et in (EventType.LLM_REQUEST, EventType.LLM_RESPONSE):
            self._record_decision("tactical", "resource_allocation", event.payload)

        elif et == EventType.ERROR:
            # 根据错误类型分配
            error_type = event.payload.get("error_type", "unknown")
            if error_type in ["budget", "strategy"]:
                layer = "strategic"
            elif error_type in ["resource", "schedule"]:
                layer = "tactical"
            else:
                layer = "executive"
            self._record_decision(layer, f"error_handling_{error_type}", event.payload)

        return event

    def _record_decision(self, layer: str, decision_type: str, params: Dict[str, Any]) -> None:
        """记录一个决策。"""
        decision = Decision(
            layer=layer,
            decision_type=decision_type,
            params=params,
        )
        self._decisions.append(decision)
        self._decision_count += 1

    def make_decision(
        self,
        layer: str,
        decision_type: str,
        params: Dict[str, Any],
    ) -> Decision:
        """在指定层做出一个决策。

        如果该决策类型不属于该层，
        会自动上浮到正确的层。
        """
        # 检查层级权限
        correct_layer = self._find_layer_for_type(decision_type)
        if correct_layer and correct_layer != layer:
            layer = correct_layer
            self._override_count += 1

        decision = Decision(
            layer=layer,
            decision_type=decision_type,
            params=params,
        )
        self._decisions.append(decision)
        self._decision_count += 1
        return decision

    def _find_layer_for_type(self, decision_type: str) -> Optional[str]:
        """查找某个决策类型属于哪一层。"""
        for layer_name, types in self._layers.items():
            if decision_type in types:
                return layer_name
        return None

    def get_decision_chain(
        self,
        layer: Optional[str] = None,
        since: Optional[float] = None,
    ) -> List[Decision]:
        """
        获取决策链。

        参数:
            layer: 按层级过滤
            since: 按时间过滤
        """
        decisions = self._decisions
        if layer:
            decisions = [d for d in decisions if d.layer == layer]
        if since:
            decisions = [d for d in decisions if d.timestamp >= since]
        return decisions

    def get_layer_stats(self) -> Dict[str, Any]:
        """获取各层级的决策统计。"""
        stats: Dict[str, Dict[str, Any]] = {}
        for layer in self._layer_order:
            layer_decisions = [d for d in self._decisions if d.layer == layer]
            stats[layer] = {
                "total_decisions": len(layer_decisions),
                "decision_types": list(set(d.decision_type for d in layer_decisions)),
            }
        return stats

    def get_status(self) -> Dict[str, Any]:
        """获取模块状态。"""
        return {
            "enabled": self.enabled,
            "layers": self._layer_order,
            "layer_permissions": self._layers,
            "total_decisions": self._decision_count,
            "override_count": self._override_count,
            "layer_stats": self.get_layer_stats(),
            "recent_decisions": [
                {
                    "layer": d.layer,
                    "type": d.decision_type,
                    "timestamp": d.timestamp,
                }
                for d in self._decisions[-10:]
            ],
        }

    def reset(self) -> None:
        """重置所有决策记录。"""
        self._decisions.clear()
        self._pending_decisions.clear()
        self._decision_count = 0
        self._override_count = 0


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/core", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    ctx = CyberneticsContext(CyberneticsConfig())
    config = {
        "enabled": True,
        "layers": [
            {"name": "strategic", "decision_types": ["goal", "branch", "budget"]},
            {"name": "tactical", "decision_types": ["parameter", "resource"]},
            {"name": "executive", "decision_types": ["tool", "retry"]},
        ],
    }
    hc = HierarchyController(config, ctx)
    hc.initialize()

    # 测试 1: 层级初始化
    assert "strategic" in hc._layers
    assert "tactical" in hc._layers
    assert "executive" in hc._layers
    print("  ✅ 测试 1 通过：层级初始化")

    # 测试 2: 事件路由
    hc.on_event(CyberneticsEvent.create(EventType.AGENT_START, "s1", {}))
    hc.on_event(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {"tool_name": "search"}))
    hc.on_event(CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4"}))

    assert hc._decision_count == 3
    print("  ✅ 测试 2 通过：事件路由")

    # 测试 3: 主动决策
    decision = hc.make_decision("executive", "tool", {"tool": "search"})
    assert decision.layer == "executive"
    assert decision.decision_type == "tool"
    print("  ✅ 测试 3 通过：主动决策")

    # 测试 4: 层级替代
    # "budget" 属于 strategic 层，但我们尝试在 executive 层做出
    decision2 = hc.make_decision("executive", "budget", {"amount": 100})
    assert decision2.layer == "strategic"  # 被自动上浮
    assert hc._override_count == 1
    print("  ✅ 测试 4 通过：层级替代")

    # 测试 5: 决策链
    chain = hc.get_decision_chain(layer="executive")
    assert len(chain) >= 1
    print("  ✅ 测试 5 通过：决策链")

    # 测试 6: 状态报告
    status = hc.get_status()
    assert status["total_decisions"] > 0
    assert "strategic" in status["layer_stats"]
    print("  ✅ 测试 6 通过：状态报告")

    print("\n  ✅ 分层控制模块所有冒烟测试通过！")
