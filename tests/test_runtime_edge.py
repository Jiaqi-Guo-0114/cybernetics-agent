"""Runtime 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.config_watcher import ConfigWatcher
from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.runtime.plugin_loader import PluginLoader
from cybernetics_agent.runtime.metrics_collector import MetricsCollector
from cybernetics_agent.runtime.state_manager import StateManager
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestRuntimeEdgeCases:
    def test_event_bus_emit_no_handler(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        assert len(bus.get_recent_events()) == 1

    def test_plugin_loader_init(self):
        pl = PluginLoader()
        assert pl is not None

    def test_state_manager_init(self, tmp_path):
        sm = StateManager({"backend": "jsonl", "path": str(tmp_path / "state.jsonl")})
        assert sm is not None
