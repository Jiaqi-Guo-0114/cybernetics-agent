"""EventBus 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.event_bus import EventBus


class TestEventBusFinal2:
    def test_emit_no_subscribers(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        assert len(bus.get_recent_events()) == 1

    def test_get_stats_with_events(self):
        bus = EventBus()
        for _ in range(5):
            bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        stats = bus.get_stats()
        assert stats.get("tool_call", 0) >= 5
