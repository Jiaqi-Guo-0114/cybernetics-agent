"""ParameterState 测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.parameter_state import ParameterState


class TestParameterState:
    def test_init(self):
        ps = ParameterState("lr", 0.1, 0.01, min_value=0.001, max_value=1.0)
        assert ps.name == "lr"
        assert ps.current_value == 0.1
        assert ps.base_value == 0.01
        assert ps.min_value == 0.001
        assert ps.max_value == 1.0
        assert ps.adjustment_count == 0
        assert ps.ema_value == 0.0

    def test_with_options(self):
        ps = ParameterState("mode", "fast", "normal", options=["slow", "normal", "fast"])
        assert ps.options == ["slow", "normal", "fast"]
