"""
核心模块性能基准测试。

使用 pytest-benchmark 采集关键操作的性能数据。
在 CI 中自动对比上次基线，性能下降 >10% 则报错。

运行方式：
    # 保存基线
    PYTHONPATH=src pytest tests/benchmark/ --benchmark-only --benchmark-save=baseline

    # 对比基线
    PYTHONPATH=src pytest tests/benchmark/ --benchmark-only --benchmark-compare
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig
from cybernetics_agent.context import CyberneticsContext
from cybernetics_agent.core import (
    AdaptiveTuner,
    FeedbackLoop,
    HierarchyController,
    InfoFlow,
    OptimalController,
    SystemIdentifier,
)
from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.runtime.event_store import EventStore


class TestEventBusBenchmark:
    """EventBus 性能基准。"""

    def test_emit_single_event(self, benchmark) -> None:
        """单条事件发射性能。"""
        bus = EventBus()
        from cybernetics_agent.core.base import CyberneticsEvent, EventType
        evt = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={"tool": "search"},
        )
        benchmark(bus.emit, evt)


class TestEventStoreBenchmark:
    """EventStore 性能基准。"""

    def test_write_single_event(self, benchmark, tmp_path) -> None:
        """单条事件写入性能。"""
        store = EventStore(str(tmp_path / "bench.db"))
        benchmark(store.write_event, "tool_call", {"tool": "search"})

    def test_write_events_batch_100(self, benchmark, tmp_path) -> None:
        """批量写入 100 条事件性能。"""
        store = EventStore(str(tmp_path / "bench.db"))
        events = [
            {"event_type": "click", "payload": {"id": i}}
            for i in range(100)
        ]
        benchmark(store.write_events_batch, events)

    def test_query_events(self, benchmark, tmp_path) -> None:
        """查询事件性能。"""
        store = EventStore(str(tmp_path / "bench.db"))
        for i in range(1000):
            store.write_event("test", {"id": i})
        benchmark(store.query_events, limit=100)


class TestCoreModulesBenchmark:
    """核心模块性能基准。"""

    def test_feedback_loop_evaluate(self, benchmark) -> None:
        """FeedbackLoop 条件评估性能。"""
        from cybernetics_agent.core.base import CyberneticsEvent, EventType
        fl = FeedbackLoop({
            "enabled": True,
            "mode": "automatic",
            "actions": [
                {"trigger": "tool_error_rate > 0.3", "action": "retry"},
            ],
            "max_feedback_depth": 3,
        }, None)
        fl.initialize()
        evt = CyberneticsEvent.create(
            event_type=EventType.TOOL_ERROR,
            session_id="s1",
            payload={"tool": "search"},
        )
        benchmark(fl.on_event, evt)

    def test_stability_engine_retry_policy(self, benchmark) -> None:
        """StabilityEngine 重试策略计算性能。"""
        from cybernetics_agent.core.stability_engine import RetryPolicy
        policy = RetryPolicy(max_retries=5, backoff="exponential", base_delay=1.0, max_delay=60.0)
        benchmark(policy.get_delay, 3)

    def test_system_identifier_record(self, benchmark) -> None:
        """SystemIdentifier 记录事件性能。"""
        si = SystemIdentifier({
            "enabled": True,
            "metrics": ["conversion_rate", "latency"],
            "sampling_rate": 1.0,
            "retention_days": 30,
        }, None)
        si.initialize()
        from cybernetics_agent.core.base import CyberneticsEvent, EventType
        evt = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={"tool": "search", "success": True, "duration": 0.5},
        )
        benchmark(si.on_event, evt)

    def test_optimal_controller_budget_check(self, benchmark) -> None:
        """OptimalController 预算检查性能。"""
        oc = OptimalController({
            "enabled": True,
            "budgets": {"tokens_per_session": 100000, "api_calls_per_session": 50, "cost_usd_per_session": 5.0},
            "constraints": {"max_concurrent_tools": 5, "max_llm_requests_per_minute": 10},
        }, None)
        oc.initialize()
        benchmark(oc.can_afford, "tokens", 1000)

    def test_info_flow_filter(self, benchmark) -> None:
        """InfoFlow 消息过滤性能。"""
        from cybernetics_agent.core.base import CyberneticsEvent, EventType
        info = InfoFlow({
            "enabled": True,
            "filters": [
                {"event_type": "tool_result", "condition": "payload.success == true"},
            ],
            "channels": ["event_bus", "metrics"],
        }, None)
        info.initialize()
        evt = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={"success": True},
        )
        benchmark(info.on_event, evt)

    def test_adaptive_tuner_decide(self, benchmark) -> None:
        """AdaptiveTuner 决策性能。"""
        at = AdaptiveTuner({
            "enabled": True,
            "learning_rate": 0.3,
            "parameters": [
                {"name": "temperature", "type": "float", "range": [0.0, 2.0], "default": 1.0},
            ],
            "user_behavior": {"track_topics": True, "track_feedback": True, "topic_decay_half_life_days": 7},
        }, None)
        at.initialize()
        # 预先训练一些数据
        for i in range(50):
            at.set_parameter("temperature", 0.5 + i * 0.02)
            at.auto_tune()
        benchmark(at.suggest_parameters)

    def test_hierarchy_decide(self, benchmark) -> None:
        """HierarchyController 决策性能。"""
        hc = HierarchyController({
            "enabled": True,
            "layers": [
                {"name": "strategic", "decision_types": ["goal", "budget"]},
                {"name": "tactical", "decision_types": ["parameter"]},
                {"name": "executive", "decision_types": ["tool"]},
            ],
        }, None)
        hc.initialize()
        benchmark(hc.make_decision, "executive", "tool", {"tool": "search"})


class TestContextBenchmark:
    """上下文性能基准。"""

    def test_context_emit_tool_result(self, benchmark, tmp_path) -> None:
        """CyberneticsContext 发射工具结果事件性能。"""
        cfg = CyberneticsConfig()
        # 使用 tmp_path 避免写入到用户目录
        cfg.storage = {"backend": "jsonl", "path": str(tmp_path / ".cybernetics"), "rotation": {"max_file_size_mb": 10, "max_files": 10}}
        ctx = CyberneticsContext(cfg)
        benchmark(ctx.emit_tool_result, "search", ["r1"], True, 0.5)
