"""PluginLoader 异常路径"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.runtime.plugin_loader import PluginLoader

class TestPluginLoaderException:
    def test_unload_not_loaded(self):
        pl = PluginLoader()
        pl.unload("nonexistent")
