"""补齐 config.py + context.py 未覆盖分支 — 验证失败、插件加载。"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from cybernetics_agent.config import CyberneticsConfig
from cybernetics_agent.context import CyberneticsContext


class TestConfigValidatedBranches:
    def test_from_json_validated_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"project_name": ""}, f)
            f.flush()
            path = f.name
        with pytest.raises(ValueError, match="配置验证失败"):
            CyberneticsConfig.from_json_validated(path)
        Path(path).unlink()

    def test_from_dict_validated_raises(self):
        with pytest.raises(ValueError, match="配置验证失败"):
            CyberneticsConfig.from_dict_validated({"project_name": ""})

    def test_from_yaml_validated_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("project_name: ''\n")
            f.flush()
            path = f.name
        with pytest.raises(ValueError, match="配置验证失败"):
            CyberneticsConfig.from_yaml_validated(path)
        Path(path).unlink()


class TestContextPluginBranches:
    def test_load_plugins_none_paths_uses_default(self):
        config = CyberneticsConfig()
        config.plugins = {}
        ctx = CyberneticsContext(config)
        with tempfile.TemporaryDirectory():
            # no plugins in default ./plugins, should return 0
            with patch.object(Path, "exists", return_value=False):
                count = ctx.load_plugins()
            assert count == 0

    def test_load_plugins_with_paths(self):
        config = CyberneticsConfig()
        config.plugins = {"paths": ["/tmp/nonexistent_plugins"]}
        ctx = CyberneticsContext(config)
        count = ctx.load_plugins()
        assert count == 0

    def test_load_plugins_plugins_not_dict(self):
        config = CyberneticsConfig()
        config.plugins = None  # type: ignore
        ctx = CyberneticsContext(config)
        count = ctx.load_plugins()
        assert count == 0

    def test_unload_plugin(self):
        config = CyberneticsConfig()
        ctx = CyberneticsContext(config)
        from cybernetics_agent.core.feedback_loop import FeedbackLoop
        mod = FeedbackLoop(config={}, ctx=ctx)
        ctx.register_module(mod)
        assert "feedback_loop" in ctx.get_all_modules()
        ctx.unload_plugin("feedback_loop")
        assert "feedback_loop" not in ctx.get_all_modules()

    def test_list_plugins(self):
        config = CyberneticsConfig()
        ctx = CyberneticsContext(config)
        result = ctx.list_plugins()
        assert "loaded" in result
        assert "modules" in result

    def test_get_module_missing(self):
        config = CyberneticsConfig()
        ctx = CyberneticsContext(config)
        assert ctx.get_module("missing") is None

    def test_register_disabled_module(self):
        config = CyberneticsConfig()
        ctx = CyberneticsContext(config)
        from cybernetics_agent.core.feedback_loop import FeedbackLoop
        mod = FeedbackLoop(config={}, ctx=ctx)
        mod.enabled = False
        ctx.register_module(mod)
        assert "feedback" not in ctx.get_all_modules()

    def test_emit_methods(self):
        config = CyberneticsConfig()
        ctx = CyberneticsContext(config)
        ctx.emit_tool_result("search", ["r1"], success=True, duration=1.0)
        ctx.emit_tool_error("search", "boom", error_type="timeout")
        ctx.emit_llm_request("gpt-4", prompt_tokens=10)
        ctx.emit_llm_response("gpt-4", completion_tokens=5, duration=0.5)
        # should not raise

    def test_shutdown(self):
        config = CyberneticsConfig()
        ctx = CyberneticsContext(config)
        from cybernetics_agent.core.feedback_loop import FeedbackLoop
        mod = FeedbackLoop(config={}, ctx=ctx)
        ctx.register_module(mod)
        ctx.shutdown()
        assert ctx.get_all_modules() == {}
