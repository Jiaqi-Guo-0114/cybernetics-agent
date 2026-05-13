"""Context load_plugins 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext

class TestContextLoadPlugins:
    def test_load_plugins_with_plugins_config(self, tmp_path):
        cfg = CyberneticsConfig()
        cfg.plugins = {"paths": [str(tmp_path)]}
        ctx = CyberneticsContext(cfg)
        count = ctx.load_plugins()
        assert isinstance(count, int)
        ctx.shutdown()

    def test_load_plugins_nonexistent_dir(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        count = ctx.load_plugins(["/nonexistent/path"])
        assert isinstance(count, int)
        ctx.shutdown()
