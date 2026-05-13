"""Tests for core.base — EventType, CyberneticsEvent, ICyberneticsModule."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

from cybernetics_agent.core.base import (
    CyberneticsEvent,
    EventType,
    ICyberneticsModule,
)


class TestEventType:
    """EventType 枚举测试。"""

    def test_all_members_exist(self):
        expected = {
            "AGENT_START", "AGENT_END",
            "TOOL_CALL", "TOOL_RESULT", "TOOL_ERROR",
            "LLM_REQUEST", "LLM_RESPONSE", "LLM_ERROR",
            "USER_INPUT", "USER_FEEDBACK",
            "STAGE_TRANSITION", "ERROR", "RECOVERY", "DEGRADATION",
            "CUSTOM",
        }
        assert {m.name for m in EventType} == expected

    def test_value_mapping(self):
        assert EventType.AGENT_START.value == "agent_start"
        assert EventType.TOOL_ERROR.value == "tool_error"
        assert EventType.CUSTOM.value == "custom"

    def test_enum_comparison(self):
        assert EventType.ERROR != EventType.RECOVERY
        assert EventType.AGENT_START == EventType.AGENT_START


class TestCyberneticsEvent:
    """CyberneticsEvent 数据类测试。"""

    def test_direct_construction(self):
        event = CyberneticsEvent(
            event_type=EventType.TOOL_CALL,
            timestamp=1234.5,
            session_id="sess-01",
            payload={"tool": "search"},
            metadata={"source": "cli"},
            event_id="evt-1234",
        )
        assert event.event_type == EventType.TOOL_CALL
        assert event.timestamp == 1234.5
        assert event.session_id == "sess-01"
        assert event.payload == {"tool": "search"}
        assert event.metadata == {"source": "cli"}
        assert event.event_id == "evt-1234"

    def test_default_payload_and_metadata(self):
        event = CyberneticsEvent(
            event_type=EventType.LLM_REQUEST,
            timestamp=time.time(),
            session_id="sess-02",
        )
        assert event.payload == {}
        assert event.metadata == {}

    def test_default_event_id_is_hex(self):
        event = CyberneticsEvent(
            event_type=EventType.ERROR,
            timestamp=time.time(),
            session_id="sess-03",
        )
        assert len(event.event_id) == 16
        int(event.event_id, 16)  # valid hex

    def test_create_classmethod(self):
        before = time.time()
        event = CyberneticsEvent.create(
            event_type=EventType.USER_INPUT,
            session_id="sess-04",
            payload={"text": "hello"},
            metadata={"user": "alice"},
        )
        after = time.time()
        assert event.event_type == EventType.USER_INPUT
        assert event.session_id == "sess-04"
        assert event.payload == {"text": "hello"}
        assert event.metadata == {"user": "alice"}
        assert before <= event.timestamp <= after
        assert len(event.event_id) == 16

    def test_create_with_none_payload_metadata(self):
        event = CyberneticsEvent.create(
            event_type=EventType.CUSTOM,
            session_id="sess-05",
        )
        assert event.payload == {}
        assert event.metadata == {}

    def test_create_event_id_is_unique(self):
        events = [
            CyberneticsEvent.create(EventType.CUSTOM, "s")
            for _ in range(50)
        ]
        ids = [e.event_id for e in events]
        assert len(set(ids)) == len(ids)

    def test_event_id_length_always_16(self):
        for _ in range(20):
            event = CyberneticsEvent.create(EventType.AGENT_START, "s")
            assert len(event.event_id) == 16


class TestICyberneticsModule:
    """ICyberneticsModule 抽象基类测试。"""

    def test_cannot_instantiate_directly(self):
        ctx = MagicMock()
        with pytest.raises(TypeError):
            ICyberneticsModule(config={}, ctx=ctx)

    def test_subclass_must_implement_on_event(self):
        class Partial(ICyberneticsModule):
            name = "partial"

            def get_status(self):
                return {}

        ctx = MagicMock()
        with pytest.raises(TypeError):
            Partial(config={}, ctx=ctx)

    def test_subclass_must_implement_get_status(self):
        class Partial(ICyberneticsModule):
            name = "partial"

            def on_event(self, event):
                return event

        ctx = MagicMock()
        with pytest.raises(TypeError):
            Partial(config={}, ctx=ctx)

    def test_valid_subclass_lifecycle(self):
        class Valid(ICyberneticsModule):
            name = "valid"

            def on_event(self, event):
                return event

            def get_status(self):
                return {"active": True}

        ctx = MagicMock()
        mod = Valid(config={"k": "v"}, ctx=ctx)
        assert mod.config == {"k": "v"}
        assert mod.ctx is ctx
        assert mod._initialized is False
        assert mod.enabled is True
        assert mod.name == "valid"

        mod.initialize()
        assert mod._initialized is True

        mod.shutdown()
        assert mod._initialized is False

    def test_repr(self):
        class Valid(ICyberneticsModule):
            name = "repr_test"

            def on_event(self, event):
                return event

            def get_status(self):
                return {}

        ctx = MagicMock()
        mod = Valid(config={}, ctx=ctx)
        r = repr(mod)
        assert "Valid" in r
        assert "repr_test" in r
        assert "enabled=True" in r

    def test_event_pass_through(self):
        class PassThrough(ICyberneticsModule):
            name = "pass"

            def on_event(self, event):
                event.metadata["processed"] = True
                return event

            def get_status(self):
                return {}

        ctx = MagicMock()
        mod = PassThrough(config={}, ctx=ctx)
        event = CyberneticsEvent.create(EventType.TOOL_CALL, "s")
        result = mod.on_event(event)
        assert result is event
        assert result.metadata["processed"] is True

    def test_event_consume_returns_none(self):
        class Sink(ICyberneticsModule):
            name = "sink"

            def on_event(self, event):
                return None

            def get_status(self):
                return {}

        ctx = MagicMock()
        mod = Sink(config={}, ctx=ctx)
        event = CyberneticsEvent.create(EventType.ERROR, "s")
        assert mod.on_event(event) is None

    def test_enabled_attribute(self):
        class OnOff(ICyberneticsModule):
            name = "onoff"
            enabled = False

            def on_event(self, event):
                return event

            def get_status(self):
                return {}

        ctx = MagicMock()
        mod = OnOff(config={}, ctx=ctx)
        assert mod.enabled is False
