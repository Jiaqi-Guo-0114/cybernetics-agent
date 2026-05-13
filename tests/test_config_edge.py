"""Config 最终补充"""
import sys

import pytest

sys.path.insert(0, 'src')

from cybernetics_agent.config import CyberneticsConfig


class TestConfigEdgeCases:
    def test_load_missing_json(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            CyberneticsConfig.from_json(str(tmp_path / "missing.json"))

    def test_load_missing_yaml(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            CyberneticsConfig.from_yaml(str(tmp_path / "missing.yaml"))

    def test_from_dict_and_to_dict(self):
        cfg = CyberneticsConfig.from_dict({"project_name": "test"})
        d = cfg.to_dict()
        assert d.get("project_name") == "test"
