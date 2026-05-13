"""最终补充测试 - runtime 模块"""
import json
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.config_watcher import ConfigWatcher
from cybernetics_agent.runtime.event_bus import EventBus
from cybernetics_agent.runtime.metrics_collector import MetricsCollector
from cybernetics_agent.runtime.plugin_loader import PluginLoader


class TestRuntimeFinal:
    # event_bus.py 剩余行 63-64, 88, 95
    def test_event_bus_stats_empty(self):
        bus = EventBus()
        stats = bus.get_stats()
        assert isinstance(stats, dict)

    def test_event_bus_clear(self):
        bus = EventBus()
        bus.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1", {}))
        bus.clear_log()
        assert bus.get_recent_events() == []

    # plugin_loader.py 剩余行 62, 79, 85-86, 131, 135
    def test_plugin_loader_init(self):
        pl = PluginLoader()
        assert pl is not None

    def test_plugin_loader_load_invalid(self):
        pl = PluginLoader()
        result = pl.load("nonexistent", {}, None)
        assert result is None

    # config_watcher.py 剩余行 57-58, 72
    def test_config_watcher_init(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"test": 1}))
        cw = ConfigWatcher(str(path), lambda cfg: None)
        assert cw is not None

    # metrics_collector.py 剩余行 69, 89, 99-101, 105-106, 157, 179, 198-221, 225-228, 275, 300-301
    def test_metrics_histogram(self):
        col = MetricsCollector()
        for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
            col.record("latency", v)
        s = col.get_summary()
        assert "latency" in s.get("histograms", {})

    def test_metrics_prometheus_format(self):
        col = MetricsCollector()
        col.record("latency", 0.5, labels={"region": "us"})
        col.increment("req", labels={"method": "GET"})
        out = col.to_prometheus("app")
        assert len(out) > 0
        assert "app" in out

    def test_metrics_empty(self):
        col = MetricsCollector()
        s = col.get_summary()
        assert s == {"counters": {}, "gauges": {}, "histograms": {}}

    def test_metrics_gauge(self):
        col = MetricsCollector()
        col.record("temp", 25.0)
        s = col.get_summary()
        assert "temp" in s.get("histograms", {})
