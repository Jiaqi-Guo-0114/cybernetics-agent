"""配置验证测试。"""

import json
import tempfile
from pathlib import Path

import pytest

from cybernetics_agent import CyberneticsConfig


class TestValidate:
    def test_default_config_is_valid(self):
        cfg = CyberneticsConfig()
        assert cfg.validate() == []

    def test_invalid_project_name(self):
        cfg = CyberneticsConfig(project_name="")
        errors = cfg.validate()
        assert any("project_name" in e for e in errors)

    def test_negative_feedback_depth(self):
        cfg = CyberneticsConfig()
        cfg.feedback_loop["max_feedback_depth"] = -1
        errors = cfg.validate()
        assert any("max_feedback_depth" in e for e in errors)

    def test_zero_timeout(self):
        cfg = CyberneticsConfig()
        cfg.stability["timeout"]["default"] = 0
        errors = cfg.validate()
        assert any("timeout.default" in e for e in errors)

    def test_negative_retry(self):
        cfg = CyberneticsConfig()
        cfg.stability["retry"]["max_retries"] = -1
        errors = cfg.validate()
        assert any("max_retries" in e for e in errors)

    def test_circuit_breaker_threshold_too_low(self):
        cfg = CyberneticsConfig()
        cfg.stability["circuit_breaker"]["failure_threshold"] = 0
        errors = cfg.validate()
        assert any("failure_threshold" in e for e in errors)

    def test_negative_budget(self):
        cfg = CyberneticsConfig()
        cfg.optimal_control["budgets"]["tokens_per_session"] = -100
        errors = cfg.validate()
        assert any("budgets.tokens_per_session" in e for e in errors)

    def test_zero_constraint(self):
        cfg = CyberneticsConfig()
        cfg.optimal_control["constraints"]["max_concurrent_tools"] = 0
        errors = cfg.validate()
        assert any("constraints.max_concurrent_tools" in e for e in errors)

    def test_sampling_rate_out_of_range(self):
        cfg = CyberneticsConfig()
        cfg.system_id["sampling_rate"] = 1.5
        errors = cfg.validate()
        assert any("sampling_rate" in e for e in errors)

        cfg.system_id["sampling_rate"] = -0.1
        errors = cfg.validate()
        assert any("sampling_rate" in e for e in errors)

    def test_multiple_errors(self):
        cfg = CyberneticsConfig()
        cfg.project_name = ""
        cfg.stability["timeout"]["default"] = -5
        cfg.optimal_control["budgets"]["cost_usd_per_session"] = -1
        errors = cfg.validate()
        assert len(errors) >= 3


class TestValidatedLoaders:
    def test_from_json_validated_ok(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"project_name": "good"}, f)
            path = f.name
        try:
            cfg = CyberneticsConfig.from_json_validated(path)
            assert cfg.project_name == "good"
        finally:
            Path(path).unlink()

    def test_from_json_validated_fails(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"project_name": "", "stability": {"timeout": {"default": 0}}}, f)
            path = f.name
        try:
            with pytest.raises(ValueError) as exc_info:
                CyberneticsConfig.from_json_validated(path)
            assert "配置验证失败" in str(exc_info.value)
        finally:
            Path(path).unlink()

    def test_from_dict_validated_ok(self):
        cfg = CyberneticsConfig.from_dict_validated({"project_name": "ok"})
        assert cfg.project_name == "ok"

    def test_from_dict_validated_fails(self):
        with pytest.raises(ValueError):
            CyberneticsConfig.from_dict_validated({"project_name": ""})
