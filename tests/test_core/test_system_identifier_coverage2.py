"""补齐 system_identifier.py 未覆盖分支 — 错误路径、漏斗边界、预测逻辑。"""

from __future__ import annotations

from unittest.mock import MagicMock

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.system_identifier import SystemIdentifier


class TestSystemIdentifierBranches:
    def test_stage_transition_failure(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.STAGE_TRANSITION, "s",
            payload={"stage": "s1", "success": False, "duration": 10.0},
        )
        si.on_event(event)
        sm = si._stage_metrics["s1"]
        assert sm.error_count == 1
        assert sm.success_count == 0
        assert sm.exit_count == 0

    def test_stage_duration_list_truncation(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        # append 1002 durations to trigger truncation
        for i in range(1002):
            event = CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s1", "success": True, "duration": float(i)},
            )
            si.on_event(event)
        assert len(si._stage_metrics["s1"].durations) == 500

    def test_tool_duration_truncation(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        for i in range(1002):
            event = CyberneticsEvent.create(
                EventType.TOOL_RESULT, "s",
                payload={"tool_name": "t1", "duration": float(i)},
            )
            si.on_event(event)
        assert len(si._tool_stats["t1"]["durations"]) == 500

    def test_llm_error_event(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.LLM_ERROR, "s",
            payload={"model": "gpt-4", "prompt_tokens": 10, "completion_tokens": 5},
        )
        si.on_event(event)
        assert si._llm_stats["gpt-4"]["errors"] == 1
        assert si._llm_stats["gpt-4"]["calls"] == 1

    def test_llm_duration_truncation(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        for i in range(1002):
            event = CyberneticsEvent.create(
                EventType.LLM_RESPONSE, "s",
                payload={"model": "m1", "duration": float(i)},
            )
            si.on_event(event)
        assert len(si._llm_stats["m1"]["durations"]) == 500

    def test_conversion_funnel_missing_stages(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        funnel = si.get_conversion_funnel(["a", "b", "c"])
        assert funnel["a_to_b"] == 0.0
        assert funnel["b_to_c"] == 0.0
        assert "overall" not in funnel  # less than 2 stages with data

    def test_conversion_funnel_overall(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        for _ in range(10):
            si.on_event(CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s1", "success": True, "duration": 1.0},
            ))
        for _ in range(5):
            si.on_event(CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s2", "success": True, "duration": 1.0},
            ))
        funnel = si.get_conversion_funnel(["s1", "s2"])
        assert funnel["s1_to_s2"] == 0.5
        assert funnel["overall"] == 0.5

    def test_predict_performance_empty(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        result = si.predict_performance()
        assert result["confidence"] == "low"
        assert result["expected_duration"] == 0
        assert result["bottleneck"] is None

    def test_predict_performance_with_stages(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        for _ in range(50):
            si.on_event(CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s1", "success": True, "duration": 2.0},
            ))
        for _ in range(25):
            si.on_event(CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s2", "success": True, "duration": 3.0},
            ))
        result = si.predict_performance(expected_stages=["s1", "s2"])
        assert result["expected_duration"] == 5.0
        assert result["confidence"] == "medium"
        assert result["bottleneck"] == "s1_to_s2"

    def test_predict_performance_high_confidence(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        for _ in range(101):
            si.on_event(CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s1", "success": True, "duration": 1.0},
            ))
        result = si.predict_performance(expected_stages=["s1"])
        assert result["confidence"] == "high"

    def test_predict_broad_query(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        for _ in range(50):
            si.on_event(CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s1", "success": True, "duration": 10.0},
            ))
        result = si.predict_performance(query_type="broad", expected_stages=["s1"])
        assert result["expected_duration"] == 15.0
        assert result["query_type"] == "broad"

    def test_predict_narrow_query(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        for _ in range(50):
            si.on_event(CyberneticsEvent.create(
                EventType.STAGE_TRANSITION, "s",
                payload={"stage": "s1", "success": True, "duration": 10.0},
            ))
        result = si.predict_performance(query_type="narrow", expected_stages=["s1"])
        assert result["expected_duration"] == 7.0
        assert result["query_type"] == "narrow"

    def test_tool_performance_single(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        si.on_event(CyberneticsEvent.create(
            EventType.TOOL_RESULT, "s",
            payload={"tool_name": "t1", "duration": 2.0},
        ))
        perf = si.get_tool_performance("t1")
        assert perf["calls"] == 1
        assert perf["success_rate"] == 1.0
        assert perf["avg_duration"] == 2.0

    def test_tool_performance_all(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        si.on_event(CyberneticsEvent.create(
            EventType.TOOL_RESULT, "s",
            payload={"tool_name": "t1", "duration": 1.0},
        ))
        all_perf = si.get_tool_performance()
        assert "t1" in all_perf

    def test_tool_performance_missing(self):
        ctx = MagicMock()
        si = SystemIdentifier(config={}, ctx=ctx)
        assert si.get_tool_performance("missing") == {}
