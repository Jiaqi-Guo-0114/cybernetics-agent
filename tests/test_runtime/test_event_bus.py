"""EventBus 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.event_bus import EventBus

class MockModule:
    def __init__(self, name):
        self.name = name
        self.events = []
    def on_event(self, evt):
        self.events.append(evt)
        return evt

class TestEventBus:
    def test_init(self):
        bus = EventBus()
        assert bus.get_stats() == {}

    def test_emit_no_subscribers(self):
        bus = EventBus()
        evt = CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {"tool": "search"})
        bus.emit(evt)
        assert len(bus.get_recent_events()) == 1

    def test_subscribe_all_emit(self):
        bus = EventBus()
        mod = MockModule("m1")
        bus.subscribe(mod)
        evt = CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {})
        bus.emit(evt)
        assert len(mod.events) == 1

    def test_subscribe_typed_emit(self):
        bus = EventBus()
        mod = MockModule("m1")
        bus.subscribe(mod, event_types=["tool_call"])
        bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        bus.emit(CyberneticsEvent(EventType.ERROR, 0.0, "s1", {}))
        assert len(mod.events) == 1
        assert mod.events[0].event_type == EventType.TOOL_CALL

    def test_unsubscribe(self):
        bus = EventBus()
        mod = MockModule("m1")
        bus.subscribe(mod)
        bus.unsubscribe(mod)
        bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        assert len(mod.events) == 0

    def test_unsubscribe_not_subscribed(self):
        bus = EventBus()
        mod = MockModule("m1")
        bus.unsubscribe(mod)  # 不应报错

    def test_get_recent_events_filter(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        bus.emit(CyberneticsEvent(EventType.ERROR, 0.0, "s1", {}))
        evts = bus.get_recent_events(event_type="error")
        assert len(evts) == 1
        assert evts[0].event_type == EventType.ERROR

    def test_get_recent_events_limit(self):
        bus = EventBus()
        for i in range(5):
            bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {"i": i}))
        evts = bus.get_recent_events(limit=2)
        assert len(evts) == 2

    def test_clear_log(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        bus.clear_log()
        assert bus.get_recent_events() == []

    def test_get_stats(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        bus.emit(CyberneticsEvent(EventType.ERROR, 0.0, "s1", {}))
        stats = bus.get_stats()
        assert stats["tool_call"] == 2
        assert stats["error"] == 1

    def test_log_overflow(self):
        bus = EventBus()
        bus._max_log_size = 4
        for i in range(10):
            bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {"i": i}))
        assert len(bus._event_log) <= 4  # 截取后不超过 max_log_size

    def test_stop_propagation(self):
        bus = EventBus()
        class Stopper:
            def on_event(self, evt):
                return None
        bus.subscribe(Stopper(), event_types=["tool_call"])
        bus.emit(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        # 不应报错
