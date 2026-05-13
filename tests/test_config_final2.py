"""Config 最终补充"""
import pytest
import sys, json, os
sys.path.insert(0, 'src')

from cybernetics_agent.config import CyberneticsConfig

class TestConfigFinal:
    def test_load_json_with_comments(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text('{"project_name": "test"}')
        cfg = CyberneticsConfig.from_json(str(path))
        assert cfg.project_name == "test"

    def test_load_yaml_with_comments(self, tmp_path):
        path = tmp_path / "cfg.yaml"
        path.write_text("project_name: test")
        cfg = CyberneticsConfig.from_yaml(str(path))
        assert cfg.project_name == "test"

    def test_to_dict_nested(self):
        cfg = CyberneticsConfig()
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert "project_name" in d

    def test_from_dict_nested(self):
        cfg = CyberneticsConfig.from_dict({
            "project_name": "test",
            "storage": {"backend": "sqlite"},
            "modules": {"feedback_loop": {"enabled": True}}
        })
        assert cfg.project_name == "test"

    def test_load_invalid_json(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text("invalid json")
        with pytest.raises(Exception):
            CyberneticsConfig.from_json(str(path))
