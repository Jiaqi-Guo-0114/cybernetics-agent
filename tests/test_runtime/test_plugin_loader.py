"""
插件加载器测试。
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.runtime.plugin_loader import PluginLoader
from cybernetics_agent.core.base import ICyberneticsModule, CyberneticsEvent, EventType


class DummyModule(ICyberneticsModule):
    """测试用虚拟模块。"""
    name = "dummy_test"

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent:
        return event

    def get_status(self) -> dict:
        return {"ok": True}


def test_discover_empty_dir():
    """空目录应返回空列表。"""
    with tempfile.TemporaryDirectory() as tmp:
        loader = PluginLoader()
        result = loader.discover(Path(tmp))
        assert result == []


def test_discover_finds_plugin():
    """发现符合接口的插件类。"""
    with tempfile.TemporaryDirectory() as tmp:
        plugin_file = Path(tmp) / "my_plugin.py"
        plugin_file.write_text('''
from cybernetics_agent.core.base import ICyberneticsModule, CyberneticsEvent

class MyPlugin(ICyberneticsModule):
    name = "my_plugin"

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent:
        return event

    def get_status(self) -> dict:
        return {"active": True}
''')
        loader = PluginLoader()
        result = loader.discover(Path(tmp))
        assert len(result) == 1
        assert result[0].name == "my_plugin"
        assert "MyPlugin" in result[0].module_class.__name__


def test_discover_skips_private():
    """跳过以 _ 开头的文件。"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "_private.py").write_text("x = 1")
        loader = PluginLoader()
        result = loader.discover(Path(tmp))
        assert result == []


def test_load_and_unload():
    """加载和卸载插件。"""
    with tempfile.TemporaryDirectory() as tmp:
        plugin_file = Path(tmp) / "test_plugin.py"
        plugin_file.write_text('''
from cybernetics_agent.core.base import ICyberneticsModule, CyberneticsEvent

class TestPlugin(ICyberneticsModule):
    name = "test_plugin"

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent:
        return event

    def get_status(self) -> dict:
        return {}
''')
        loader = PluginLoader()
        discovered = loader.discover(Path(tmp))
        assert len(discovered) == 1

        instance = loader.load(discovered[0], {}, None)
        assert instance is not None
        assert instance.name == "test_plugin"
        assert loader.is_loaded("test_plugin")

        loader.unload("test_plugin")
        assert not loader.is_loaded("test_plugin")
