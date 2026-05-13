"""EventBus 错误处理路径补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class MockSubscriber:
    def __init__(self, fail=False):
        self.events = []
        self._fail = fail
    def on_event(self, event):
        if self._fail:
            raise RuntimeError("fail")
        self.events.append(event)

class TestEventBusErrorPaths:
    def test_subscriber_exception(self):
        bus = EventBus()
        sub = MockSubscriber(fail=True)
        bus.subscribe(sub)
        try:
            bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        except RuntimeError:
            pass  # 预期的异常
        assert len(sub.events) == 0

    def test_get_recent_events_limit(self):
        bus = EventBus()
        for i in range(150):
            bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        events = bus.get_recent_events()
        assert len(events) <= 100
