"""MetricsCollector 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.metrics_collector import MetricsCollector

class TestMetricsCollectorFinal:
    def test_record_multiple(self):
        col = MetricsCollector()
        for v in [0.1, 0.2, 0.3]:
            col.record("latency", v)
        s = col.get_summary()
        assert "latency" in s.get("histograms", {})

    def test_record_with_labels(self):
        col = MetricsCollector()
        col.record("latency", 0.5, labels={"region": "us"})
        s = col.get_summary()
        assert "histograms" in s

    def test_increment_no_labels(self):
        col = MetricsCollector()
        col.increment("req")
        col.increment("req")
        s = col.get_summary()
        assert "req" in s.get("counters", {})

    def test_prometheus_format(self):
        col = MetricsCollector()
        col.increment("calls", labels={"tool": "search"})
        out = col.to_prometheus("app")
        assert "app" in out
