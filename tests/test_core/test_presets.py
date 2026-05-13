"""
策略预设库测试。
"""

import pytest

from cybernetics_agent import CyberneticsConfig
from cybernetics_agent.presets import (
    HIGH_CONCURRENCY,
    LOW_COST,
    HIGH_RELIABILITY,
    DEBUG,
    list_presets,
    get_preset,
    apply_preset,
    describe_preset,
)


class TestListPresets:
    def test_returns_all_names(self):
        names = list_presets()
        assert sorted(names) == ["debug", "high_concurrency", "high_reliability", "low_cost"]


class TestGetPreset:
    def test_high_concurrency(self):
        preset = get_preset("high_concurrency")
        assert preset["stability"]["parallel_competition"]["enabled"] is True
        assert preset["stability"]["timeout"]["llm"] == 180.0

    def test_low_cost(self):
        preset = get_preset("low_cost")
        assert preset["stability"]["parallel_competition"]["enabled"] is False
        assert preset["optimal_control"]["budgets"]["tokens_per_session"] == 20000

    def test_high_reliability(self):
        preset = get_preset("high_reliability")
        assert preset["stability"]["retry"]["max_retries"] == 5
        assert preset["stability"]["circuit_breaker"]["failure_threshold"] == 3

    def test_debug(self):
        preset = get_preset("debug")
        assert preset["stability"]["retry"]["max_retries"] == 0
        assert preset["stability"]["circuit_breaker"]["enabled"] is False

    def test_unknown_preset_raises(self):
        with pytest.raises(KeyError) as exc_info:
            get_preset("nonexistent")
        assert "nonexistent" in str(exc_info.value)
        assert "high_concurrency" in str(exc_info.value)

    def test_returns_deep_copy(self):
        p1 = get_preset("debug")
        p2 = get_preset("debug")
        p1["feedback_loop"]["enabled"] = False
        assert p2["feedback_loop"]["enabled"] is True  # 深拷贝，不影响原始预设


class TestApplyPreset:
    def test_applies_over_existing(self):
        base = CyberneticsConfig(project_name="test")
        result = apply_preset(base, "low_cost")
        assert result.project_name == "test"  # 保留原值
        assert result.stability["parallel_competition"]["enabled"] is False  # 预设覆盖

    def test_does_not_mutate_original(self):
        base = CyberneticsConfig()
        original_retry = base.stability["retry"]["max_retries"]
        apply_preset(base, "high_reliability")
        assert base.stability["retry"]["max_retries"] == original_retry  # 原对象不变

    def test_all_presets_produce_valid_config(self):
        base = CyberneticsConfig()
        for name in list_presets():
            result = apply_preset(base, name)
            errors = result.validate()
            assert errors == [], f"预设 '{name}' 产生无效配置: {errors}"


class TestDescribePreset:
    def test_known_presets(self):
        assert "高并发" in describe_preset("high_concurrency")
        assert "低成本" in describe_preset("low_cost")
        assert "高可靠性" in describe_preset("high_reliability")
        assert "调试" in describe_preset("debug")

    def test_unknown_preset(self):
        assert describe_preset("unknown") == "未知预设"


class TestPresetConstants:
    def test_constants_are_dicts(self):
        for preset in [HIGH_CONCURRENCY, LOW_COST, HIGH_RELIABILITY, DEBUG]:
            assert isinstance(preset, dict)
            assert "feedback_loop" in preset
            assert "stability" in preset
            assert "optimal_control" in preset
