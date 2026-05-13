"""Config 验证路径补充测试"""
import json
import sys

import pytest

sys.path.insert(0, 'src')

from cybernetics_agent.config import CyberneticsConfig


class TestConfigValidation:
    def test_invalid_project_name(self):
        cfg = CyberneticsConfig()
        cfg.project_name = ""
        errors = cfg.validate()
        assert any("project_name" in e for e in errors)

    def test_invalid_project_name_type(self):
        cfg = CyberneticsConfig()
        cfg.project_name = 123
        errors = cfg.validate()
        assert any("project_name" in e for e in errors)

    def test_invalid_feedback_loop_type(self):
        cfg = CyberneticsConfig()
        cfg.feedback_loop = "invalid"
        errors = cfg.validate()
        assert any("feedback_loop" in e for e in errors)

    def test_invalid_feedback_depth(self):
        cfg = CyberneticsConfig()
        cfg.feedback_loop = {"max_feedback_depth": -1}
        errors = cfg.validate()
        assert any("max_feedback_depth" in e for e in errors)

    def test_invalid_stability_type(self):
        cfg = CyberneticsConfig()
        cfg.stability = "invalid"
        errors = cfg.validate()
        assert any("stability" in e for e in errors)

    def test_invalid_timeout_value(self):
        cfg = CyberneticsConfig()
        cfg.stability = {"timeout": {"default": -1}}
        errors = cfg.validate()
        assert any("timeout" in e for e in errors)

    def test_invalid_timeout_type(self):
        cfg = CyberneticsConfig()
        cfg.stability = {"timeout": {"default": "bad"}}
        errors = cfg.validate()
        assert any("timeout" in e for e in errors)

    def test_invalid_retry(self):
        cfg = CyberneticsConfig()
        cfg.stability = {"retry": {"max_retries": -1}}
        errors = cfg.validate()
        assert any("max_retries" in e for e in errors)

    def test_invalid_circuit_breaker(self):
        cfg = CyberneticsConfig()
        cfg.stability = {"circuit_breaker": {"failure_threshold": 0}}
        errors = cfg.validate()
        assert any("failure_threshold" in e for e in errors)

    def test_invalid_budget(self):
        cfg = CyberneticsConfig()
        cfg.optimal_control = {"budgets": {"llm": -1}}
        errors = cfg.validate()
        assert any("budgets" in e for e in errors)

    def test_invalid_budget_type(self):
        cfg = CyberneticsConfig()
        cfg.optimal_control = {"budgets": {"llm": "bad"}}
        errors = cfg.validate()
        assert any("budgets" in e for e in errors)

    def test_invalid_constraint(self):
        cfg = CyberneticsConfig()
        cfg.optimal_control = {"constraints": {"max_tools": 0}}
        errors = cfg.validate()
        assert any("constraints" in e for e in errors)

    def test_invalid_constraint_type(self):
        cfg = CyberneticsConfig()
        cfg.optimal_control = {"constraints": {"max_tools": 1.5}}
        errors = cfg.validate()
        assert any("constraints" in e for e in errors)

    def test_invalid_sampling_rate_high(self):
        cfg = CyberneticsConfig()
        cfg.system_id = {"sampling_rate": 1.5}
        errors = cfg.validate()
        assert any("sampling_rate" in e for e in errors)

    def test_invalid_sampling_rate_low(self):
        cfg = CyberneticsConfig()
        cfg.system_id = {"sampling_rate": -0.5}
        errors = cfg.validate()
        assert any("sampling_rate" in e for e in errors)

    def test_invalid_sampling_rate_type(self):
        cfg = CyberneticsConfig()
        cfg.system_id = {"sampling_rate": "bad"}
        errors = cfg.validate()
        assert any("sampling_rate" in e for e in errors)

    def test_from_json_validated_fail(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"project_name": ""}))
        with pytest.raises(ValueError):
            CyberneticsConfig.from_json_validated(str(path))

    def test_from_yaml_validated_fail(self, tmp_path):
        path = tmp_path / "cfg.yaml"
        path.write_text("project_name: ''")
        with pytest.raises(ValueError):
            CyberneticsConfig.from_yaml_validated(str(path))

    def test_from_dict_validated_fail(self):
        with pytest.raises(ValueError):
            CyberneticsConfig.from_dict_validated({"project_name": ""})
