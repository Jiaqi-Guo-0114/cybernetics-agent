"""Config 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.config import CyberneticsConfig

class TestConfigFinal:
    def test_to_dict(self):
        cfg = CyberneticsConfig()
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert "project_name" in d

    def test_from_dict(self):
        cfg = CyberneticsConfig.from_dict({"project_name": "test"})
        assert cfg.project_name == "test"

    def test_from_json_file(self, tmp_path):
        import json
        path = tmp_path / "cfg.json"
        path.write_text(json.dumps({"project_name": "json"}))
        cfg = CyberneticsConfig.from_json(str(path))
        assert cfg.project_name == "json"
