"""
配置环境变量注入测试。
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent.config import _resolve_env_vars, CyberneticsConfig


def test_resolve_env_var_plain():
    """${VAR} 语法。"""
    os.environ["CYBER_TEST_VAR"] = "hello"
    try:
        result = _resolve_env_vars({"key": "${CYBER_TEST_VAR}"})
        assert result == {"key": "hello"}
    finally:
        del os.environ["CYBER_TEST_VAR"]


def test_resolve_env_var_with_default():
    """${VAR:default} 语法。"""
    # 不设置环境变量，应使用默认值
    result = _resolve_env_vars({"key": "${CYBER_TEST_VAR_ABSENT:default_value}"})
    assert result == {"key": "default_value"}


def test_resolve_env_uri():
    """env://VAR 语法。"""
    os.environ["CYBER_TEST_URI"] = "secret123"
    try:
        result = _resolve_env_vars({"key": "env://CYBER_TEST_URI"})
        assert result == {"key": "secret123"}
    finally:
        del os.environ["CYBER_TEST_URI"]


def test_resolve_env_var_missing_raises():
    """未设置的环境变量应报错。"""
    try:
        _resolve_env_vars({"key": "${CYBER_TEST_VAR_DEFINITELY_MISSING}"})
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "CYBER_TEST_VAR_DEFINITELY_MISSING" in str(e)


def test_resolve_nested_dict():
    """递归解析嵌套字典。"""
    os.environ["CYBER_NESTED"] = "nested_value"
    try:
        result = _resolve_env_vars({
            "level1": {
                "level2": "${CYBER_NESTED}",
                "static": "unchanged",
            },
            "list": ["${CYBER_NESTED}", "static"],
        })
        assert result["level1"]["level2"] == "nested_value"
        assert result["level1"]["static"] == "unchanged"
        assert result["list"] == ["nested_value", "static"]
    finally:
        del os.environ["CYBER_NESTED"]


def test_from_dict_with_env():
    """from_dict 自动解析环境变量。"""
    os.environ["CYBER_PROJECT"] = "my-awesome-agent"
    try:
        cfg = CyberneticsConfig.from_dict({
            "project_name": "${CYBER_PROJECT}",
            "stability": {
                "timeout": {
                    "default": 60.0,
                },
            },
        })
        assert cfg.project_name == "my-awesome-agent"
        assert cfg.stability["timeout"]["default"] == 60.0
    finally:
        del os.environ["CYBER_PROJECT"]


def test_from_json_with_env():
    """from_json 自动解析环境变量。"""
    os.environ["CYBER_JSON_PROJECT"] = "json-project"
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write('{\"project_name\": \"${CYBER_JSON_PROJECT}\"}')
            path = f.name
        try:
            cfg = CyberneticsConfig.from_json(path)
            assert cfg.project_name == "json-project"
        finally:
            os.unlink(path)
    finally:
        del os.environ["CYBER_JSON_PROJECT"]


def test_mixed_string_with_env():
    """字符串中混合环境变量。"""
    os.environ["CYBER_PREFIX"] = "prod"
    try:
        result = _resolve_env_vars({"key": "${CYBER_PREFIX}-database"})
        assert result == {"key": "prod-database"}
    finally:
        del os.environ["CYBER_PREFIX"]


def test_pydantic_schema_available():
    """如果安装了 pydantic，schema 应该可用。"""
    try:
        from cybernetics_agent.config_schema import CyberneticsConfigModel, HAS_PYDANTIC
    except ImportError:
        HAS_PYDANTIC = False

    if not HAS_PYDANTIC:
        return  # 跳过

    # 验证有效配置
    model = CyberneticsConfigModel(project_name="test")
    assert model.project_name == "test"
    assert model.stability.timeout.default == 30.0


def test_pydantic_schema_invalid():
    """Pydantic schema 应该报错无效配置。"""
    try:
        from cybernetics_agent.config_schema import CyberneticsConfigModel, HAS_PYDANTIC
    except ImportError:
        HAS_PYDANTIC = False

    if not HAS_PYDANTIC:
        return  # 跳过

    import pytest
    with pytest.raises(Exception):
        CyberneticsConfigModel(project_name="", stability={"timeout": {"default": -1}})
