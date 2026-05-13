"""MetricsCollector 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.metrics_collector import MetricsCollector


class TestMetricsCollectorExtra:
    def test_record_gauge(self):
        col = MetricsCollector()
        col.record("latency", 0.5)
        summary = col.get_summary()
        assert "histograms" in summary
        assert "latency" in summary["histograms"]

    def test_record_histogram(self):
        col = MetricsCollector()
        for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
            col.record("latency", v)
        summary = col.get_summary()
        assert "histograms" in summary
        assert "latency" in summary["histograms"]

    def test_to_prometheus_with_data(self):
        col = MetricsCollector()
        col.increment("calls", labels={"tool": "search"})
        col.record("latency", 0.5, labels={"tool": "search"})
        output = col.to_prometheus("cybernetics")
        assert len(output) > 0
        assert "cybernetics" in output
