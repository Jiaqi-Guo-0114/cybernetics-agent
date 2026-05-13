"""
策略预设库。

提供开箱即用的控制论配置模板，覆盖常见使用场景。
"""

from __future__ import annotations

import copy
from typing import Any, Dict

from .config import CyberneticsConfig


#: 高并发预设 — 最大化并行处理能力，适合批量任务和并行下载场景。
HIGH_CONCURRENCY: Dict[str, Any] = {
    "feedback_loop": {"enabled": True, "mode": "automatic", "actions": [], "max_feedback_depth": 5},
    "stability": {
        "enabled": True,
        "timeout": {"default": 60.0, "llm": 180.0, "download": 120.0, "tool": 60.0},
        "retry": {"max_retries": 2, "backoff": "exponential", "base_delay": 0.5, "max_delay": 30.0},
        "circuit_breaker": {"enabled": True, "failure_threshold": 10, "recovery_timeout": 30.0, "half_open_max_calls": 5},
        "graceful_degradation": {"enabled": True, "chain": ["fulltext", "abstract", "metadata"]},
        "parallel_competition": {"enabled": True, "groups": [], "timeout_seconds": 180.0},
    },
    "system_id": {"enabled": True, "metrics": ["conversion_rate", "latency", "error_rate", "token_usage", "throughput"], "sampling_rate": 1.0, "retention_days": 7},
    "optimal_control": {"enabled": True, "budgets": {"tokens_per_session": 200000, "api_calls_per_session": 100, "cost_usd_per_session": 10.0}, "constraints": {"max_concurrent_tools": 10, "max_llm_requests_per_minute": 20}},
    "info_flow": {"enabled": True, "filters": [], "channels": ["event_bus", "metrics", "storage"]},
    "adaptive": {"enabled": True, "learning_rate": 0.3, "parameters": [], "user_behavior": {"track_topics": True, "track_feedback": True, "topic_decay_half_life_days": 7}},
    "hierarchy": {"enabled": True, "layers": [{"name": "strategic", "decision_types": ["goal", "branch", "budget"]}, {"name": "tactical", "decision_types": ["parameter", "resource", "schedule"]}, {"name": "executive", "decision_types": ["tool", "retry", "error_recovery"]}]},
    "storage": {"backend": "jsonl", "path": "./.cybernetics", "rotation": {"max_file_size_mb": 10, "max_files": 10}},
}

#: 低成本预设 — 严格预算控制，适合开发测试和资源受限环境。
LOW_COST: Dict[str, Any] = {
    "feedback_loop": {"enabled": True, "mode": "manual", "actions": [], "max_feedback_depth": 1},
    "stability": {
        "enabled": True,
        "timeout": {"default": 15.0, "llm": 60.0, "download": 30.0, "tool": 15.0},
        "retry": {"max_retries": 1, "backoff": "fixed", "base_delay": 2.0, "max_delay": 10.0},
        "circuit_breaker": {"enabled": True, "failure_threshold": 3, "recovery_timeout": 120.0, "half_open_max_calls": 1},
        "graceful_degradation": {"enabled": True, "chain": ["abstract", "metadata"]},
        "parallel_competition": {"enabled": False, "groups": [], "timeout_seconds": 30.0},
    },
    "system_id": {"enabled": True, "metrics": ["error_rate", "cost"], "sampling_rate": 0.1, "retention_days": 3},
    "optimal_control": {"enabled": True, "budgets": {"tokens_per_session": 20000, "api_calls_per_session": 10, "cost_usd_per_session": 0.5}, "constraints": {"max_concurrent_tools": 2, "max_llm_requests_per_minute": 3}},
    "info_flow": {"enabled": True, "filters": ["error_only"], "channels": ["metrics"]},
    "adaptive": {"enabled": True, "learning_rate": 0.5, "parameters": [], "user_behavior": {"track_topics": False, "track_feedback": True, "topic_decay_half_life_days": 7}},
    "hierarchy": {"enabled": True, "layers": [{"name": "strategic", "decision_types": ["goal", "budget"]}, {"name": "tactical", "decision_types": ["parameter", "resource"]}, {"name": "executive", "decision_types": ["tool", "retry"]}]},
    "storage": {"backend": "jsonl", "path": "./.cybernetics", "rotation": {"max_file_size_mb": 5, "max_files": 3}},
}

#: 高可靠性预设 — 最大化稳定性，适合生产环境关键任务。
HIGH_RELIABILITY: Dict[str, Any] = {
    "feedback_loop": {"enabled": True, "mode": "automatic", "actions": ["retry", "degrade", "alert"], "max_feedback_depth": 5},
    "stability": {
        "enabled": True,
        "timeout": {"default": 45.0, "llm": 150.0, "download": 90.0, "tool": 45.0},
        "retry": {"max_retries": 5, "backoff": "exponential", "base_delay": 1.0, "max_delay": 120.0},
        "circuit_breaker": {"enabled": True, "failure_threshold": 3, "recovery_timeout": 180.0, "half_open_max_calls": 2},
        "graceful_degradation": {"enabled": True, "chain": ["fulltext", "abstract", "metadata", "fallback"]},
        "parallel_competition": {"enabled": True, "groups": [], "timeout_seconds": 120.0},
    },
    "system_id": {"enabled": True, "metrics": ["conversion_rate", "latency", "error_rate", "token_usage", "availability"], "sampling_rate": 1.0, "retention_days": 90},
    "optimal_control": {"enabled": True, "budgets": {"tokens_per_session": 150000, "api_calls_per_session": 80, "cost_usd_per_session": 8.0}, "constraints": {"max_concurrent_tools": 6, "max_llm_requests_per_minute": 15}},
    "info_flow": {"enabled": True, "filters": [], "channels": ["event_bus", "metrics", "storage", "alert"]},
    "adaptive": {"enabled": True, "learning_rate": 0.2, "parameters": [], "user_behavior": {"track_topics": True, "track_feedback": True, "topic_decay_half_life_days": 14}},
    "hierarchy": {"enabled": True, "layers": [{"name": "strategic", "decision_types": ["goal", "branch", "budget", "risk_assessment"]}, {"name": "tactical", "decision_types": ["parameter", "resource", "schedule", "rollback"]}, {"name": "executive", "decision_types": ["tool", "retry", "error_recovery", "checkpoint"]}]},
    "storage": {"backend": "jsonl", "path": "./.cybernetics", "rotation": {"max_file_size_mb": 50, "max_files": 30}},
}

#: 调试预设 — 详细日志和完整指标采集，适合排查问题和开发调试。
DEBUG: Dict[str, Any] = {
    "feedback_loop": {"enabled": True, "mode": "automatic", "actions": ["log", "retry", "degrade"], "max_feedback_depth": 10},
    "stability": {
        "enabled": True,
        "timeout": {"default": 300.0, "llm": 600.0, "download": 300.0, "tool": 300.0},
        "retry": {"max_retries": 0, "backoff": "fixed", "base_delay": 0.0, "max_delay": 0.0},
        "circuit_breaker": {"enabled": False, "failure_threshold": 9999, "recovery_timeout": 0.0, "half_open_max_calls": 9999},
        "graceful_degradation": {"enabled": True, "chain": ["fulltext", "abstract", "metadata"]},
        "parallel_competition": {"enabled": True, "groups": [], "timeout_seconds": 600.0},
    },
    "system_id": {"enabled": True, "metrics": ["conversion_rate", "latency", "error_rate", "token_usage", "throughput", "queue_depth", "memory"], "sampling_rate": 1.0, "retention_days": 30},
    "optimal_control": {"enabled": True, "budgets": {"tokens_per_session": 999999, "api_calls_per_session": 9999, "cost_usd_per_session": 999.0}, "constraints": {"max_concurrent_tools": 20, "max_llm_requests_per_minute": 100}},
    "info_flow": {"enabled": True, "filters": [], "channels": ["event_bus", "metrics", "storage", "log"]},
    "adaptive": {"enabled": False, "learning_rate": 0.0, "parameters": [], "user_behavior": {"track_topics": False, "track_feedback": False, "topic_decay_half_life_days": 7}},
    "hierarchy": {"enabled": True, "layers": [{"name": "strategic", "decision_types": ["goal", "branch", "budget"]}, {"name": "tactical", "decision_types": ["parameter", "resource", "schedule"]}, {"name": "executive", "decision_types": ["tool", "retry", "error_recovery"]}]},
    "storage": {"backend": "jsonl", "path": "./.cybernetics", "rotation": {"max_file_size_mb": 100, "max_files": 50}},
}


_PRESETS = {
    "high_concurrency": HIGH_CONCURRENCY,
    "low_cost": LOW_COST,
    "high_reliability": HIGH_RELIABILITY,
    "debug": DEBUG,
}


def list_presets() -> list:
    """列出所有可用的预设名称。"""
    return list(_PRESETS.keys())


def get_preset(name: str) -> Dict[str, Any]:
    """
    获取指定名称的预设配置字典。

    Args:
        name: 预设名称，可选 ``high_concurrency`` / ``low_cost`` / ``high_reliability`` / ``debug``

    Returns:
        深拷贝后的配置字典

    Raises:
        KeyError: 如果预设名称不存在
    """
    if name not in _PRESETS:
        available = ", ".join(_PRESETS.keys())
        raise KeyError(f"未知预设 '{name}'。可用预设: {available}")
    return copy.deepcopy(_PRESETS[name])


def apply_preset(config: CyberneticsConfig, name: str) -> CyberneticsConfig:
    """
    将预设应用到现有配置上。

    使用深拷贝合并，不会修改传入的 ``config`` 对象。

    Args:
        config: 现有配置
        name: 预设名称

    Returns:
        合并后的新配置对象
    """
    preset = get_preset(name)
    merged = config.to_dict()

    def _deep_merge(base: dict, overlay: dict) -> dict:
        """深度合并两个字典，overlay 优先。"""
        result = copy.deepcopy(base)
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = _deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result

    merged = _deep_merge(merged, preset)
    return CyberneticsConfig.from_dict(merged)


def describe_preset(name: str) -> str:
    """
    返回预设的人类可读描述。

    用于 CLI ``cybernetix preset <name>`` 展示。
    """
    descriptions = {
        "high_concurrency": "高并发预设 | 最大化并行处理，适合批量任务。超时放宽，并行竞争开启，重试较少。",
        "low_cost": "低成本预设 | 严格预算控制，适合开发测试。超时缩短，重试最少，并行关闭，采样率降低。",
        "high_reliability": "高可靠性预设 | 生产环境关键任务。重试最多，熔断最严格，降级链最完整，保留期最长。",
        "debug": "调试预设 | 排查问题专用。超时最长，重试关闭，熔断关闭，完整指标采集，详细日志。",
    }
    return descriptions.get(name, "未知预设")
