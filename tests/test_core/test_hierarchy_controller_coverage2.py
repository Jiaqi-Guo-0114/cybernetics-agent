"""补齐 hierarchy_controller.py 未覆盖分支 — 层解析、错误分类、浮动、统计。"""

from __future__ import annotations

from unittest.mock import MagicMock

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.hierarchy_controller import HierarchyController


class TestHierarchyControllerBranches:
    def test_layer_config_parsing(self):
        ctx = MagicMock()
        hc = HierarchyController(
            config={
                "layers": [
                    {"name": "strategic", "decision_types": ["goal"]},
                    {"name": "tactical", "decision_types": ["parameter"]},
                    {"name": "executive", "decision_types": ["tool"]},
                ]
            },
            ctx=ctx,
        )
        assert hc._layer_order == ["strategic", "tactical", "executive"]
        assert hc._layers["strategic"] == ["goal"]

    def test_agent_start_event(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        event = CyberneticsEvent.create(EventType.AGENT_START, "s")
        hc.on_event(event)
        assert hc._decision_count == 1
        assert hc._decisions[0].layer == "strategic"

    def test_agent_end_event(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        event = CyberneticsEvent.create(EventType.AGENT_END, "s")
        hc.on_event(event)
        assert hc._decisions[-1].layer == "strategic"

    def test_tool_events_executive(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        for et in [EventType.TOOL_CALL, EventType.TOOL_RESULT, EventType.TOOL_ERROR,
                   EventType.RECOVERY, EventType.DEGRADATION]:
            hc.on_event(CyberneticsEvent.create(et, "s"))
        assert all(d.layer == "executive" for d in hc._decisions)

    def test_llm_events_tactical(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        for et in [EventType.LLM_REQUEST, EventType.LLM_RESPONSE]:
            hc.on_event(CyberneticsEvent.create(et, "s"))
        assert all(d.layer == "tactical" for d in hc._decisions)

    def test_error_budget_strategic(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.ERROR, "s", payload={"error_type": "budget"}
        )
        hc.on_event(event)
        assert hc._decisions[0].layer == "strategic"

    def test_error_strategy_strategic(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.ERROR, "s", payload={"error_type": "strategy"}
        )
        hc.on_event(event)
        assert hc._decisions[0].layer == "strategic"

    def test_error_resource_tactical(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.ERROR, "s", payload={"error_type": "resource"}
        )
        hc.on_event(event)
        assert hc._decisions[0].layer == "tactical"

    def test_error_schedule_tactical(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.ERROR, "s", payload={"error_type": "schedule"}
        )
        hc.on_event(event)
        assert hc._decisions[0].layer == "tactical"

    def test_error_unknown_executive(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        event = CyberneticsEvent.create(
            EventType.ERROR, "s", payload={"error_type": "unknown"}
        )
        hc.on_event(event)
        assert hc._decisions[0].layer == "executive"

    def test_make_decision_override(self):
        ctx = MagicMock()
        hc = HierarchyController(
            config={
                "layers": [
                    {"name": "strategic", "decision_types": ["goal"]},
                    {"name": "executive", "decision_types": ["tool"]},
                ]
            },
            ctx=ctx,
        )
        # "tool" belongs to executive, but we ask from strategic
        decision = hc.make_decision("strategic", "tool", {})
        assert decision.layer == "executive"
        assert hc._override_count == 1

    def test_find_layer_for_type_found(self):
        ctx = MagicMock()
        hc = HierarchyController(
            config={
                "layers": [
                    {"name": "a", "decision_types": ["x", "y"]},
                    {"name": "b", "decision_types": ["z"]},
                ]
            },
            ctx=ctx,
        )
        assert hc._find_layer_for_type("y") == "a"
        assert hc._find_layer_for_type("z") == "b"

    def test_find_layer_for_type_not_found(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        assert hc._find_layer_for_type("whatever") is None

    def test_get_decision_chain_with_filters(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        hc._record_decision("strategic", "d1", {})
        hc._record_decision("executive", "d2", {})
        assert len(hc.get_decision_chain(layer="strategic")) == 1
        assert len(hc.get_decision_chain(since=0)) == 2
        assert len(hc.get_decision_chain(layer="none")) == 0

    def test_get_layer_stats(self):
        ctx = MagicMock()
        hc = HierarchyController(
            config={
                "layers": [
                    {"name": "strategic", "decision_types": ["goal"]},
                    {"name": "executive", "decision_types": ["tool"]},
                ]
            },
            ctx=ctx,
        )
        hc._record_decision("strategic", "goal", {})
        stats = hc.get_layer_stats()
        assert stats["strategic"]["total_decisions"] == 1
        assert stats["executive"]["total_decisions"] == 0

    def test_reset(self):
        ctx = MagicMock()
        hc = HierarchyController(config={"layers": []}, ctx=ctx)
        hc._record_decision("a", "b", {})
        hc.reset()
        assert hc._decision_count == 0
        assert hc._override_count == 0
        assert hc._decisions == []
