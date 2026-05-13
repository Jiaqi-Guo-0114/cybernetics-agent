"""MetricsCollector 最终补充"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.metrics_collector import MetricsCollector


class TestMetricsCollectorFinal2:
    def test_histogram_percentiles(self):
        col = MetricsCollector()
        for v in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            col.record("latency", v)
        s = col.get_summary()
        assert "latency" in s.get("histograms", {})

    def test_prometheus_histogram(self):
        col = MetricsCollector()
        col.record("latency", 0.5, labels={"region": "us"})
        out = col.to_prometheus("app")
        assert len(out) > 0

    def test_prometheus_counter_labels(self):
        col = MetricsCollector()
        col.increment("requests", labels={"method": "GET", "status": "200"})
        out = col.to_prometheus("app")
        assert len(out) > 0

    def test_empty_histogram(self):
        col = MetricsCollector()
        col.record("empty_metric", 1.0)
        s = col.get_summary()
        assert "empty_metric" in s.get("histograms", {})
