"""
最优控制模块。

在约束条件下做最优资源分配。
支持 Token 预算、API 调用限额、成本管理。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import CyberneticsEvent, EventType, ICyberneticsModule


@dataclass
class BudgetPool:
    """单个预算池。"""
    name: str
    allocated: float
    consumed: float = 0.0
    reserved: float = 0.0

    @property
    def remaining(self) -> float:
        return self.allocated - self.consumed - self.reserved

    @property
    def usage_rate(self) -> float:
        if self.allocated > 0:
            return self.consumed / self.allocated
        return 0.0

    def can_afford(self, amount: float) -> bool:
        return self.remaining >= amount

    def consume(self, amount: float) -> bool:
        if self.can_afford(amount):
            self.consumed += amount
            return True
        return False

    def reserve(self, amount: float) -> bool:
        if self.remaining >= amount:
            self.reserved += amount
            return True
        return False

    def release(self, amount: float) -> None:
        self.reserved = max(0.0, self.reserved - amount)

    def reset(self) -> None:
        self.consumed = 0.0
        self.reserved = 0.0


class OptimalController(ICyberneticsModule):
    """
    最优控制模块。

    核心能力：
    1. 分池预算管理（Token / API调用 / 成本）
    2. 调用前预算检查
    3. 资源耗尽时的降级策略
    4. 速率限制（requests/minute）

    配置示例（cybernetics.json）：
        "optimal_control": {
            "enabled": true,
            "budgets": {
                "tokens_per_session": 100000,
                "api_calls_per_session": 50,
                "cost_usd_per_session": 5.0
            },
            "constraints": {
                "max_concurrent_tools": 5,
                "max_llm_requests_per_minute": 10
            }
        }
    """

    name = "optimal_control"

    def __init__(self, config: Dict[str, Any], ctx: Any) -> None:
        super().__init__(config, ctx)

        # 预算配置
        budgets = config.get("budgets", {})
        self._pools: Dict[str, BudgetPool] = {
            "tokens": BudgetPool("tokens", budgets.get("tokens_per_session", 100000)),
            "api_calls": BudgetPool("api_calls", budgets.get("api_calls_per_session", 50)),
            "cost_usd": BudgetPool("cost_usd", budgets.get("cost_usd_per_session", 5.0)),
        }

        # 约束配置
        constraints = config.get("constraints", {})
        self._max_concurrent_tools = constraints.get("max_concurrent_tools", 5)
        self._max_llm_rpm = constraints.get("max_llm_requests_per_minute", 10)

        # 速率限制计数
        self._llm_request_times: List[float] = []
        self._active_tools = 0

        # 统计
        self._rejected_requests = 0
        self._throttled_requests = 0

    def on_event(self, event: CyberneticsEvent) -> Optional[CyberneticsEvent]:
        """监听资源消耗事件，更新预算池。"""
        et = event.event_type
        payload = event.payload

        if et == EventType.LLM_REQUEST:
            tokens = payload.get("prompt_tokens", 0)
            self._pools["tokens"].consume(tokens)
            self._pools["api_calls"].consume(1)
            self._llm_request_times.append(time.time())
            # 清理过期记录
            cutoff = time.time() - 60
            self._llm_request_times = [t for t in self._llm_request_times if t > cutoff]

        elif et == EventType.LLM_RESPONSE:
            tokens = payload.get("completion_tokens", 0)
            self._pools["tokens"].consume(tokens)
            # 估算成本（简化模型）
            cost = self._estimate_cost(payload)
            self._pools["cost_usd"].consume(cost)

        elif et == EventType.TOOL_CALL:
            self._active_tools += 1

        elif et == EventType.TOOL_RESULT:
            self._active_tools = max(0, self._active_tools - 1)

        return event

    def _estimate_cost(self, payload: Dict[str, Any]) -> float:
        """估算一次 LLM 调用的成本。"""
        model = payload.get("model", "")
        completion_tokens = payload.get("completion_tokens", 0)
        prompt_tokens = payload.get("prompt_tokens", 0)
        total_tokens = completion_tokens + prompt_tokens

        # 简化估算（每 1K tokens 约 $0.002）
        base_rate = 0.002
        if "gpt-4" in model.lower():
            base_rate = 0.03
        elif "claude" in model.lower():
            base_rate = 0.008

        return (total_tokens / 1000) * base_rate

    def can_afford(
        self,
        pool_name: str,
        amount: float,
    ) -> bool:
        """
        检查是否能承担指定资源。"""
        pool = self._pools.get(pool_name)
        if not pool:
            return True
        return pool.can_afford(amount)

    def check_llm_rate_limit(self) -> bool:
        """
        检查 LLM 调用是否超过速率限制。"""
        cutoff = time.time() - 60
        recent_requests = [t for t in self._llm_request_times if t > cutoff]
        return len(recent_requests) < self._max_llm_rpm

    def check_tool_concurrency(self) -> bool:
        """检查工具并发数是否超限。"""
        return self._active_tools < self._max_concurrent_tools

    def get_budget_status(self) -> Dict[str, Any]:
        """获取预算使用情况。"""
        return {
            name: {
                "allocated": pool.allocated,
                "consumed": pool.consumed,
                "reserved": pool.reserved,
                "remaining": pool.remaining,
                "usage_rate": round(pool.usage_rate, 4),
            }
            for name, pool in self._pools.items()
        }

    def get_fallback_strategy(self) -> Dict[str, Any]:
        """
        获取当前的降级策略。

        根据预算消耗情况推荐合适的降级方案。
        """
        strategies = []

        token_pool = self._pools["tokens"]
        if token_pool.usage_rate > 0.9:
            strategies.append({
                "type": "compress_context",
                "priority": 1,
                "description": "压缩上下文以节省 token",
            })
        if token_pool.usage_rate > 0.7:
            strategies.append({
                "type": "use_cheaper_model",
                "priority": 2,
                "description": "切换到更便宜的 LLM 模型",
            })

        api_pool = self._pools["api_calls"]
        if api_pool.usage_rate > 0.8:
            strategies.append({
                "type": "batch_requests",
                "priority": 3,
                "description": "合并多个请求以减少 API 调用",
            })

        cost_pool = self._pools["cost_usd"]
        if cost_pool.usage_rate > 0.8:
            strategies.append({
                "type": "reduce_depth",
                "priority": 1,
                "description": "降低分析深度以节省成本",
            })

        return {
            "strategies": sorted(strategies, key=lambda s: s["priority"]),
            "most_critical_pool": self._get_most_critical_pool(),
        }

    def _get_most_critical_pool(self) -> Optional[str]:
        """获取最紧张的预算池。"""
        max_usage = -1.0
        critical = None
        for name, pool in self._pools.items():
            if pool.usage_rate > max_usage:
                max_usage = pool.usage_rate
                critical = name
        return critical

    def get_status(self) -> Dict[str, Any]:
        """获取模块状态。"""
        return {
            "enabled": self.enabled,
            "budgets": self.get_budget_status(),
            "constraints": {
                "max_concurrent_tools": self._max_concurrent_tools,
                "max_llm_rpm": self._max_llm_rpm,
            },
            "current_concurrent_tools": self._active_tools,
            "llm_requests_last_minute": len([
                t for t in self._llm_request_times if t > time.time() - 60
            ]),
            "rejected_requests": self._rejected_requests,
            "throttled_requests": self._throttled_requests,
            "fallback_strategy": self.get_fallback_strategy(),
        }

    def reset(self) -> None:
        """重置所有预算池。"""
        for pool in self._pools.values():
            pool.reset()
        self._llm_request_times.clear()
        self._active_tools = 0


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/core", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    ctx = CyberneticsContext(CyberneticsConfig())
    config = {
        "enabled": True,
        "budgets": {
            "tokens_per_session": 1000,
            "api_calls_per_session": 10,
            "cost_usd_per_session": 1.0,
        },
        "constraints": {
            "max_concurrent_tools": 3,
            "max_llm_requests_per_minute": 5,
        },
    }
    oc = OptimalController(config, ctx)
    oc.initialize()

    # 测试 1: 预算池管理
    assert oc.can_afford("tokens", 500) is True
    assert oc.can_afford("tokens", 1500) is False
    print("  ✅ 测试 1 通过：预算检查")

    # 测试 2: 事件消耗
    oc.on_event(CyberneticsEvent.create(
        EventType.LLM_REQUEST, "s1", {"prompt_tokens": 200}
    ))
    oc.on_event(CyberneticsEvent.create(
        EventType.LLM_RESPONSE, "s1", {"completion_tokens": 100, "model": "gpt-4"}
    ))

    status = oc.get_budget_status()
    assert status["tokens"]["consumed"] == 300
    assert status["api_calls"]["consumed"] == 1
    assert status["cost_usd"]["consumed"] > 0
    print("  ✅ 测试 2 通过：事件消耗")

    # 测试 3: 速率限制
    assert oc.check_llm_rate_limit() is True
    for _ in range(5):
        oc.on_event(CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {}))
    assert oc.check_llm_rate_limit() is False  # 已达上限 5/min
    print("  ✅ 测试 3 通过：速率限制")

    # 测试 4: 降级策略
    # 消耗大量 token
    for _ in range(3):
        oc.on_event(CyberneticsEvent.create(
            EventType.LLM_REQUEST, "s1", {"prompt_tokens": 300}
        ))
    strategy = oc.get_fallback_strategy()
    assert "strategies" in strategy
    assert len(strategy["strategies"]) > 0
    print("  ✅ 测试 4 通过：降级策略")

    # 测试 5: 重置
    oc.reset()
    status2 = oc.get_budget_status()
    assert status2["tokens"]["consumed"] == 0
    print("  ✅ 测试 5 通过：重置")

    print("\n  ✅ 最优控制模块所有冒烟测试通过！")
