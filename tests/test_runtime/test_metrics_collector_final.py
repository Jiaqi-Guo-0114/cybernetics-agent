"""MetricsCollector 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.metrics_collector import MetricsCollector

class TestMetricsCollectorFinal:
    def test_record_gauge(self):
        col = MetricsCollector()
        col.record("temp", 25.0)
        s = col.get_summary()
        assert "temp" in s.get("histograms", {})

    def test_increment(self):
        col = MetricsCollector()
        col.increment("req")
        col.increment("req", labels={"method": "GET"})
        s = col.get_summary()
        assert "req" in s.get("counters", {})

    def test_prometheus_empty(self):
        col = MetricsCollector()
        assert col.to_prometheus("x") == ""

    def test_prometheus_with_data(self):
        col = MetricsCollector()
        col.increment("req")
        out = col.to_prometheus("app")
        assert "app" in out
