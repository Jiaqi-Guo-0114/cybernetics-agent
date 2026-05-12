"""配置中心。支持 JSON 加载。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Union


_DEFAULTS: Dict[str, Any] = {
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
    feedback_loop: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["feedback_loop"]))
    stability: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["stability"]))
    system_id: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["system_id"]))
    optimal_control: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["optimal_control"]))
    info_flow: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["info_flow"]))
    adaptive: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["adaptive"]))
    hierarchy: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["hierarchy"]))
    storage: Dict[str, Any] = field(default_factory=lambda: dict(_DEFAULTS["storage"]))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CyberneticsConfig":
        """从字典加载。"""
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "CyberneticsConfig":
        """从 JSON 文件加载。"""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls.__dataclass_fields__})

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "CyberneticsConfig":
        """从 YAML 文件加载（需要 PyYAML）。"""
        import yaml
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in cls.__dataclass_fields__})

    def to_dict(self) -> Dict[str, Any]:
        """转为字典。"""
        return asdict(self)
