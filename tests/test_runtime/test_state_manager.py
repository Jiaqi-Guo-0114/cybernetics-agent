"""StateManager 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.state_manager import StateManager

class TestStateManager:
    def test_memory_backend(self):
        sm = StateManager({"backend": "memory"})
        evt = CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {"tool": "search"})
        sm.save_event(evt)
        events = sm.load_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "tool_call"
        sm.close()

    def test_load_events_filter(self):
        sm = StateManager({"backend": "memory"})
        sm.save_event(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        sm.save_event(CyberneticsEvent(EventType.ERROR, 0.0, "s2", {}))
        events = sm.load_events(session_id="s1")
        assert len(events) == 1
        events = sm.load_events(event_type="error")
        assert len(events) == 1
        sm.close()

    def test_load_events_since(self):
        import time
        sm = StateManager({"backend": "memory"})
        t0 = time.time()
        sm.save_event(CyberneticsEvent(EventType.TOOL_CALL, t0, "s1", {}))
        events = sm.load_events(since=t0)
        assert len(events) == 1
        events = sm.load_events(since=t0 + 10)
        assert len(events) == 0
        sm.close()

    def test_load_events_limit(self):
        sm = StateManager({"backend": "memory"})
        for i in range(5):
            sm.save_event(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {"i": i}))
        events = sm.load_events(limit=3)
        assert len(events) == 3
        sm.close()

    def test_jsonl_backend(self, tmp_path):
        sm = StateManager({"backend": "jsonl", "path": str(tmp_path / "state")})
        evt = CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {"tool": "search"})
        sm.save_event(evt)
        events = sm.load_events()
        assert len(events) == 1
        sm.close()

    def test_sqlite_backend(self, tmp_path):
        sm = StateManager({"backend": "sqlite", "path": str(tmp_path / "state")})
        evt = CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {"tool": "search"})
        sm.save_event(evt)
        events = sm.load_events()
        assert len(events) == 1
        sm.close()

    def test_closed(self):
        sm = StateManager({"backend": "memory"})
        sm.close()
        sm.save_event(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        events = sm.load_events()
        assert len(events) == 0

    def test_get_session_count(self):
        sm = StateManager({"backend": "memory"})
        sm.save_event(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        sm.save_event(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s1", {}))
        sm.save_event(CyberneticsEvent(EventType.TOOL_CALL, 0.0, "s2", {}))
        assert sm.get_session_count() == 2
        sm.close()

    def test_load_events_unknown_backend(self):
        sm = StateManager({"backend": "unknown"})
        events = sm.load_events()
        assert events == []
        sm.close()

    def test_jsonl_empty(self, tmp_path):
        sm = StateManager({"backend": "jsonl", "path": str(tmp_path / "state")})
        events = sm.load_events()
        assert events == []
        sm.close()
