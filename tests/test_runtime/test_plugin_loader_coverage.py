"""PluginLoader 剩余代码补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.plugin_loader import PluginLoader


class TestPluginLoaderCoverage:
    def test_discover_empty(self, tmp_path):
        pl = PluginLoader()
        result = pl.discover(tmp_path)
        assert result == []

    def test_load_invalid(self):
        pl = PluginLoader()
        result = pl.load("nonexistent", {}, None)
        assert result is None

    def test_unload_nonexistent(self):
        pl = PluginLoader()
        pl.unload("nonexistent")
