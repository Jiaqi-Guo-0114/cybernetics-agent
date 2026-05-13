"""MetricsCollector 最终补充"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.metrics_collector import MetricsCollector


class TestMetricsCollectorEdgeCases:
    def test_record_gauge(self):
        col = MetricsCollector()
        col.record("temp", 25.0)
        s = col.get_summary()
        assert "temp" in s.get("histograms", {})

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

    def test_increment_with_labels(self):
        col = MetricsCollector()
        col.increment("req", labels={"method": "GET"})
        s = col.get_summary()
        assert "req" in s.get("counters", {})

    def test_prometheus_empty(self):
        col = MetricsCollector()
        assert col.to_prometheus("x") == ""

    def test_prometheus_with_data(self):
        col = MetricsCollector()
        col.increment("calls", labels={"tool": "search"})
        out = col.to_prometheus("app")
        assert "app" in out
