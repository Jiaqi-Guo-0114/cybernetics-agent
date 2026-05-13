"""PluginLoader 最终补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.plugin_loader import PluginLoader

class TestPluginLoaderFinal2:
    def test_load_invalid_module(self):
        pl = PluginLoader()
        result = pl.load("nonexistent_module", {}, None)
        assert result is None

    def test_unload_not_loaded(self):
        pl = PluginLoader()
        pl.unload("nonexistent")
