"""Context load_plugins 异常路径"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext

class TestContextLoadPlugins:
    def test_load_plugins_with_bad_dir(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        count = ctx.load_plugins(["/nonexistent"])
        assert count == 0
        ctx.shutdown()
