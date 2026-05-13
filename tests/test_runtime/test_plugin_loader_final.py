"""PluginLoader 最终补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.plugin_loader import PluginLoader


class TestPluginLoaderFinal:
    def test_list_loaded_empty(self):
        pl = PluginLoader()
        assert pl.list_loaded() == []

    def test_load_no_module(self):
        pl = PluginLoader()
        result = pl.load("nonexistent", {}, None)
        assert result is None
