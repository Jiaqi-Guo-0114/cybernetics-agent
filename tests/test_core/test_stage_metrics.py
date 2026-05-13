"""StageMetrics 测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.stage_metrics import StageMetrics


class TestStageMetrics:
    def test_init(self):
        sm = StageMetrics("stage1")
        assert sm.stage_name == "stage1"
        assert sm.entry_count == 0
        assert sm.exit_count == 0
        assert sm.success_count == 0
        assert sm.error_count == 0
        assert sm.total_duration == 0.0

    def test_update_counts(self):
        sm = StageMetrics("stage1")
        sm.entry_count = 5
        sm.exit_count = 4
        sm.success_count = 3
        sm.error_count = 1
        sm.durations = [2.0, 3.0]
        sm.total_duration = 10.0
        assert sm.entry_count == 5
        assert sm.avg_duration == 2.5
        assert sm.success_rate == 0.75

    def test_success_rate_zero(self):
        sm = StageMetrics("stage1")
        assert sm.success_rate == 1.0  # 无成功/失败时默认 100%

    def test_avg_duration_zero(self):
        sm = StageMetrics("stage1")
        assert sm.avg_duration == 0.0

    def test_conversion_rate(self):
        sm = StageMetrics("stage1")
        sm.entry_count = 10
        sm.exit_count = 5
        assert sm.conversion_rate == 0.5

    def test_p95_duration(self):
        sm = StageMetrics("stage1", durations=[1.0, 2.0, 3.0, 4.0, 5.0])
        assert sm.p95_duration > 0
