"""Config 测试"""
import pytest
import sys, json
sys.path.insert(0, 'src')

from cybernetics_agent.config import CyberneticsConfig

class TestCyberneticsConfig:
    def test_init_defaults(self):
        cfg = CyberneticsConfig()
        assert cfg.project_name == "unnamed-project"

    def test_from_json(self, tmp_path):
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"project_name": "test"}))
        cfg = CyberneticsConfig.from_json(str(path))
        assert cfg.project_name == "test"

    def test_from_yaml(self, tmp_path):
        path = tmp_path / "cfg.yaml"
        path.write_text("project_name: test_yaml")
        cfg = CyberneticsConfig.from_yaml(str(path))
        assert cfg.project_name == "test_yaml"

    def test_to_dict(self):
        cfg = CyberneticsConfig()
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert "project_name" in d
