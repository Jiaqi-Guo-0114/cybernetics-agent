"""EventBus 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.event_bus import EventBus


class TestEventBusFinal:
    def test_get_stats_empty(self):
        bus = EventBus()
        stats = bus.get_stats()
        assert isinstance(stats, dict)

    def test_get_recent_events(self):
        bus = EventBus()
        for _i in range(5):
            bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        events = bus.get_recent_events()
        assert len(events) == 5
