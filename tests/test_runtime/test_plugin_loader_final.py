"""PluginLoader 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.plugin_loader import PluginLoader

class TestPluginLoaderFinal:
    def test_init(self):
        pl = PluginLoader()
        assert pl is not None

    def test_load_nonexistent(self):
        pl = PluginLoader()
        result = pl.load("nonexistent", {}, None)
        assert result is None
