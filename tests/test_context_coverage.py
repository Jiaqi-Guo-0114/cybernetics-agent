"""Context 剩余代码补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core.base import ICyberneticsModule


class MockModule(ICyberneticsModule):
    def __init__(self, name, enabled=True):
        self._name = name
        self._enabled = enabled
    @property
    def name(self): return self._name
    @property
    def enabled(self): return self._enabled
    def initialize(self): pass
    def shutdown(self): pass
    def on_event(self, event): pass
    def get_status(self): return {"ok": True}

class TestContextCoverage:
    def test_load_plugins_with_dir(self, tmp_path):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        count = ctx.load_plugins([str(tmp_path)])
        assert isinstance(count, int)
        ctx.shutdown()

    def test_load_plugins_default(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        count = ctx.load_plugins()
        assert isinstance(count, int)
        ctx.shutdown()

    def test_unload_plugin(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        mod = MockModule("test_mod")
        ctx.register_module(mod)
        assert ctx.unload_plugin("test_mod") is True
        ctx.shutdown()

    def test_list_plugins(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        result = ctx.list_plugins()
        assert "loaded" in result
        assert "modules" in result
        ctx.shutdown()

    def test_register_disabled_module(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        mod = MockModule("disabled_mod", enabled=False)
        ctx.register_module(mod)
        assert ctx.get_module("disabled_mod") is None
        ctx.shutdown()

    def test_unregister_nonexistent(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.unregister_module("nonexistent")
        ctx.shutdown()

    def test_unregister_existing(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        mod = MockModule("test_mod")
        ctx.register_module(mod)
        ctx.unregister_module("test_mod")
        assert ctx.get_module("test_mod") is None
        ctx.shutdown()

    def test_shutdown(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        mod = MockModule("test_mod")
        ctx.register_module(mod)
        ctx.shutdown()
