"""Config 补充测试"""
import sys

import pytest

sys.path.insert(0, 'src')

from cybernetics_agent.config import CyberneticsConfig


class TestConfigExtra:
    def test_from_dict(self):
        cfg = CyberneticsConfig.from_dict({"project_name": "test"})
        assert cfg.project_name == "test"

    def test_from_json_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            CyberneticsConfig.from_json(str(tmp_path / "missing.json"))

    def test_from_yaml_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            CyberneticsConfig.from_yaml(str(tmp_path / "missing.yaml"))
