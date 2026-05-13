"""配置中心。支持 JSON 加载与 schema 验证。"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_DEFAULTS: dict[str, Any] = {
    "feedback_loop": {
        "enabled": True,
        "mode": "automatic",
        "actions": [],
        "max_feedback_depth": 3,
    },
    "stability": {
        "enabled": True,
        "timeout": {"default": 30.0, "llm": 120.0, "download": 60.0, "tool": 30.0},
        "retry": {"max_retries": 3, "backoff": "exponential", "base_delay": 1.0, "max_delay": 60.0},
        "circuit_breaker": {"enabled": True, "failure_threshold": 5, "recovery_timeout": 60.0, "half_open_max_calls": 3},
        "graceful_degradation": {"enabled": True, "chain": []},
        "parallel_competition": {"enabled": True, "groups": [], "timeout_seconds": 120.0},
    },
    "system_id": {
        "enabled": True,
        "metrics": ["conversion_rate", "latency", "error_rate", "token_usage"],
        "sampling_rate": 1.0,
        "retention_days": 30,
    },
    "optimal_control": {
        "enabled": True,
        "budgets": {"tokens_per_session": 100000, "api_calls_per_session": 50, "cost_usd_per_session": 5.0},
        "constraints": {"max_concurrent_tools": 5, "max_llm_requests_per_minute": 10},
    },
    "info_flow": {
        "enabled": True,
        "filters": [],
        "channels": ["event_bus", "metrics", "storage"],
    },
    "adaptive": {
        "enabled": True,
        "learning_rate": 0.3,
        "parameters": [],
        "user_behavior": {"track_topics": True, "track_feedback": True, "topic_decay_half_life_days": 7},
    },
    "hierarchy": {
        "enabled": True,
        "layers": [
            {"name": "strategic", "decision_types": ["goal", "branch", "budget"]},
            {"name": "tactical", "decision_types": ["parameter", "resource", "schedule"]},
            {"name": "executive", "decision_types": ["tool", "retry", "error_recovery"]},
        ],
    },
    "storage": {
        "backend": "jsonl",
        "path": "./.cybernetics",
        "rotation": {"max_file_size_mb": 10, "max_files": 10},
    },
}


@dataclass
class CyberneticsConfig:
    """声明式配置对象。"""
    version: str = "1.0"
    project_name: str = "unnamed-project"
    feedback_loop: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["feedback_loop"]))
    stability: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["stability"]))
    system_id: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["system_id"]))
    optimal_control: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["optimal_control"]))
    info_flow: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["info_flow"]))
    adaptive: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["adaptive"]))
    hierarchy: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["hierarchy"]))
    storage: dict[str, Any] = field(default_factory=lambda: copy.deepcopy(_DEFAULTS["storage"]))
    plugins: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CyberneticsConfig:
        """从字典加载。"""
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, path: str | Path) -> CyberneticsConfig:
        """从 JSON 文件加载。"""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls.__dataclass_fields__})

    @classmethod
    def from_yaml(cls, path: str | Path) -> CyberneticsConfig:
        """从 YAML 文件加载（需要 PyYAML）。"""
        import yaml
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls.__dataclass_fields__})

    def to_dict(self) -> dict[str, Any]:
        """转为字典。"""
        return asdict(self)

    def validate(self) -> list[str]:
        """
        验证配置有效性。

        Returns:
            错误信息列表。空列表表示验证通过。
        """
        errors: list[str] = []

        # 基础字段
        if not self.project_name or not isinstance(self.project_name, str):
            errors.append("project_name 必须是非空字符串")

        # feedback_loop
        fb = self.feedback_loop
        if not isinstance(fb, dict):
            errors.append("feedback_loop 必须是字典")
        else:
            if fb.get("max_feedback_depth", 0) < 0:
                errors.append("feedback_loop.max_feedback_depth 不能为负数")

        # stability
        st = self.stability
        if not isinstance(st, dict):
            errors.append("stability 必须是字典")
        else:
            timeout = st.get("timeout", {})
            for k, v in timeout.items():
                if not isinstance(v, (int, float)) or v <= 0:
                    errors.append(f"stability.timeout.{k} 必须是正数")

            retry = st.get("retry", {})
            if retry.get("max_retries", 0) < 0:
                errors.append("stability.retry.max_retries 不能为负数")

            cb = st.get("circuit_breaker", {})
            if cb.get("failure_threshold", 0) < 1:
                errors.append("stability.circuit_breaker.failure_threshold 必须 ≥ 1")

        # optimal_control
        oc = self.optimal_control
        if isinstance(oc, dict):
            budgets = oc.get("budgets", {})
            for k, v in budgets.items():
                if not isinstance(v, (int, float)) or v < 0:
                    errors.append(f"optimal_control.budgets.{k} 必须是非负数")

            constraints = oc.get("constraints", {})
            for k, v in constraints.items():
                if not isinstance(v, int) or v < 1:
                    errors.append(f"optimal_control.constraints.{k} 必须是正整数")

        # system_id
        sid = self.system_id
        if isinstance(sid, dict):
            rate = sid.get("sampling_rate", 1.0)
            if not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
                errors.append("system_id.sampling_rate 必须在 [0, 1] 区间内")

        return errors

    @classmethod
    def from_json_validated(cls, path: str | Path) -> CyberneticsConfig:
        """
        从 JSON 文件加载并验证。

        Raises:
            ValueError: 如果配置无效
        """
        cfg = cls.from_json(path)
        errors = cfg.validate()
        if errors:
            raise ValueError(f"配置验证失败 ({len(errors)} 个错误):\n" + "\n".join(f"  - {e}" for e in errors))
        return cfg

    @classmethod
    def from_yaml_validated(cls, path: str | Path) -> CyberneticsConfig:
        """
        从 YAML 文件加载并验证。

        Raises:
            ValueError: 如果配置无效
        """
        cfg = cls.from_yaml(path)
        errors = cfg.validate()
        if errors:
            raise ValueError(f"配置验证失败 ({len(errors)} 个错误):\n" + "\n".join(f"  - {e}" for e in errors))
        return cfg

    @classmethod
    def from_dict_validated(cls, data: dict[str, Any]) -> CyberneticsConfig:
        """
        从字典加载并验证。

        Raises:
            ValueError: 如果配置无效
        """
        cfg = cls.from_dict(data)
        errors = cfg.validate()
        if errors:
            raise ValueError(f"配置验证失败 ({len(errors)} 个错误):\n" + "\n".join(f"  - {e}" for e in errors))
        return cfg
