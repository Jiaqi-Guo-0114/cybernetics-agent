"""EventBus 剩余代码补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.event_bus import EventBus


class MockSubscriber:
    def __init__(self):
        self.events = []
    def on_event(self, event):
        self.events.append(event)

class TestEventBusCoverage:
    def test_subscribe_unsubscribe(self):
        bus = EventBus()
        sub = MockSubscriber()
        bus.subscribe(sub)
        bus.unsubscribe(sub)
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        assert len(sub.events) == 0

    def test_get_stats(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        stats = bus.get_stats()
        assert isinstance(stats, dict)

    def test_clear_log(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        bus.clear_log()
        assert bus.get_recent_events() == []
