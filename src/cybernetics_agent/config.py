"""配置中心。

支持从 JSON / YAML 加载，也支持程序化构建。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class FeedbackLoopConfig:
    """反馈闭环配置。"""
    enabled: bool = True
    mode: str = "automatic"  # "automatic" | "manual" | "advisory"
    actions: List[Dict[str, Any]] = field(default_factory=list)
    max_feedback_depth: int = 3


@dataclass
class RetryConfig:
    """重试配置。"""
    max_retries: int = 3
    backoff: str = "exponential"  # "exponential" | "linear" | "fixed"
    base_delay: float = 1.0
    max_delay: float = 60.0


@dataclass
class TimeoutConfig:
    """超时配置。"""
    default: float = 30.0
    llm: float = 120.0
    download: float = 60.0
    tool: float = 30.0


@dataclass
class CircuitBreakerConfig:
    """熔断器配置。"""
    enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3


@dataclass
class DegradationConfig:
    """降级配置。"""
    enabled: bool = True
    chain: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ParallelGroupConfig:
    """并行竞争组配置。"""
    name: str = "default"
    concurrency: str = "parallel"  # "parallel" | "serial"
    members: List[str] = field(default_factory=list)


@dataclass
class ParallelCompetitionConfig:
    """并行竞争配置。"""
    enabled: bool = True
    groups: List[ParallelGroupConfig] = field(default_factory=list)
    timeout_seconds: float = 120.0


@dataclass
class StabilityConfig:
    """稳定性配置。"""
    enabled: bool = True
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    graceful_degradation: DegradationConfig = field(default_factory=DegradationConfig)
    parallel_competition: ParallelCompetitionConfig = field(default_factory=ParallelCompetitionConfig)


@dataclass
class SystemIdConfig:
    """系统辨识配置。"""
    enabled: bool = True
    metrics: List[str] = field(default_factory=lambda: [
        "conversion_rate", "latency", "error_rate", "token_usage"
    ])
    sampling_rate: float = 1.0
    retention_days: int = 30


@dataclass
class BudgetConfig:
    """预算配置。"""
    tokens_per_session: int = 100000
    api_calls_per_session: int = 50
    cost_usd_per_session: float = 5.0


@dataclass
class ConstraintConfig:
    """约束配置。"""
    max_concurrent_tools: int = 5
    max_llm_requests_per_minute: int = 10


@dataclass
class OptimalControlConfig:
    """最优控制配置。"""
    enabled: bool = True
    budgets: BudgetConfig = field(default_factory=BudgetConfig)
    constraints: ConstraintConfig = field(default_factory=ConstraintConfig)


@dataclass
class InfoFilterConfig:
    """信息滤波器配置。"""
    type: str = "deduplicate"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InfoFlowConfig:
    """信息流配置。"""
    enabled: bool = True
    filters: List[InfoFilterConfig] = field(default_factory=list)
    channels: List[str] = field(default_factory=lambda: ["event_bus", "metrics", "storage"])


@dataclass
class AdaptiveParameterConfig:
    """自适应参数配置。"""
    name: str = ""
    base: Any = None
    min: Any = None
    max: Any = None
    options: List[Any] = field(default_factory=list)


@dataclass
class UserBehaviorConfig:
    """用户行为配置。"""
    track_topics: bool = True
    track_feedback: bool = True
    topic_decay_half_life_days: int = 7


@dataclass
class AdaptiveConfig:
    """自适应配置。"""
    enabled: bool = True
    learning_rate: float = 0.3
    parameters: List[AdaptiveParameterConfig] = field(default_factory=list)
    user_behavior: UserBehaviorConfig = field(default_factory=UserBehaviorConfig)


@dataclass
class HierarchyLayerConfig:
    """分层控制层配置。"""
    name: str = ""
    decision_types: List[str] = field(default_factory=list)


@dataclass
class HierarchyConfig:
    """分层控制配置。"""
    enabled: bool = True
    layers: List[HierarchyLayerConfig] = field(default_factory=lambda: [
        HierarchyLayerConfig("strategic", ["goal", "branch", "budget"]),
        HierarchyLayerConfig("tactical", ["parameter", "resource", "schedule"]),
        HierarchyLayerConfig("executive", ["tool", "retry", "error_recovery"]),
    ])


@dataclass
class StorageConfig:
    """存储配置。"""
    backend: str = "jsonl"  # "jsonl" | "sqlite" | "redis" | "memory"
    path: str = "./.cybernetics"
    rotation: Dict[str, Any] = field(default_factory=lambda: {
        "max_file_size_mb": 10,
        "max_files": 10,
    })
    # Redis 参数（可选）
    redis_url: Optional[str] = None
    redis_prefix: str = "cybernetics"


@dataclass
class CyberneticsConfig:
    """
    声明式配置对象。
    
    对应 cybernetics.json 或 cybernetics.yaml 文件。
    """
    version: str = "1.0"
    project_name: str = "unnamed-project"

    # 七大原则配置
    feedback_loop: FeedbackLoopConfig = field(default_factory=FeedbackLoopConfig)
    stability: StabilityConfig = field(default_factory=StabilityConfig)
    system_id: SystemIdConfig = field(default_factory=SystemIdConfig)
    optimal_control: OptimalControlConfig = field(default_factory=OptimalControlConfig)
    info_flow: InfoFlowConfig = field(default_factory=InfoFlowConfig)
    adaptive: AdaptiveConfig = field(default_factory=AdaptiveConfig)
    hierarchy: HierarchyConfig = field(default_factory=HierarchyConfig)

    # 存储配置
    storage: StorageConfig = field(default_factory=StorageConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CyberneticsConfig":
        """从字典构建配置。"""
        # 简化版本：逐层解包
        storage_data = data.pop("storage", {})
        storage = StorageConfig(**storage_data)

        feedback_data = data.pop("feedback_loop", {})
        feedback = FeedbackLoopConfig(**feedback_data)

        stability_data = data.pop("stability", {})
        stability = _build_stability_config(stability_data)

        system_id_data = data.pop("system_id", {})
        system_id = SystemIdConfig(**system_id_data)

        optimal_data = data.pop("optimal_control", {})
        optimal = _build_optimal_config(optimal_data)

        info_flow_data = data.pop("info_flow", {})
        info_flow = _build_info_flow_config(info_flow_data)

        adaptive_data = data.pop("adaptive", {})
        adaptive = _build_adaptive_config(adaptive_data)

        hierarchy_data = data.pop("hierarchy", {})
        hierarchy = _build_hierarchy_config(hierarchy_data)

        return cls(
            version=data.get("version", "1.0"),
            project_name=data.get("project_name", "unnamed-project"),
            feedback_loop=feedback,
            stability=stability,
            system_id=system_id,
            optimal_control=optimal,
            info_flow=info_flow,
            adaptive=adaptive,
            hierarchy=hierarchy,
            storage=storage,
        )

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "CyberneticsConfig":
        """从 JSON 文件加载配置。"""
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "CyberneticsConfig":
        """从 YAML 文件加载配置。"""
        # 避免强依赖 PyYAML，使用内嵌解析器
        path = Path(path)
        raw = path.read_text(encoding="utf-8")
        data = _parse_yaml_simple(raw)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "version": self.version,
            "project_name": self.project_name,
            "feedback_loop": self.feedback_loop.__dict__,
            "stability": self._stability_to_dict(),
            "system_id": self.system_id.__dict__,
            "optimal_control": self._optimal_to_dict(),
            "info_flow": self._info_flow_to_dict(),
            "adaptive": self._adaptive_to_dict(),
            "hierarchy": self._hierarchy_to_dict(),
            "storage": self.storage.__dict__,
        }

    def _stability_to_dict(self) -> Dict[str, Any]:
        s = self.stability
        return {
            "enabled": s.enabled,
            "timeout": s.timeout.__dict__,
            "retry": s.retry.__dict__,
            "circuit_breaker": s.circuit_breaker.__dict__,
            "graceful_degradation": s.graceful_degradation.__dict__,
            "parallel_competition": {
                "enabled": s.parallel_competition.enabled,
                "groups": [g.__dict__ for g in s.parallel_competition.groups],
                "timeout_seconds": s.parallel_competition.timeout_seconds,
            },
        }

    def _optimal_to_dict(self) -> Dict[str, Any]:
        o = self.optimal_control
        return {
            "enabled": o.enabled,
            "budgets": o.budgets.__dict__,
            "constraints": o.constraints.__dict__,
        }

    def _info_flow_to_dict(self) -> Dict[str, Any]:
        i = self.info_flow
        return {
            "enabled": i.enabled,
            "filters": [f.__dict__ for f in i.filters],
            "channels": i.channels,
        }

    def _adaptive_to_dict(self) -> Dict[str, Any]:
        a = self.adaptive
        return {
            "enabled": a.enabled,
            "learning_rate": a.learning_rate,
            "parameters": [p.__dict__ for p in a.parameters],
            "user_behavior": a.user_behavior.__dict__,
        }

    def _hierarchy_to_dict(self) -> Dict[str, Any]:
        h = self.hierarchy
        return {
            "enabled": h.enabled,
            "layers": [l.__dict__ for l in h.layers],
        }


# ── 私有构建函数 ──

def _build_stability_config(data: Dict[str, Any]) -> StabilityConfig:
    timeout_data = data.pop("timeout", {})
    timeout = TimeoutConfig(**timeout_data)

    retry_data = data.pop("retry", {})
    retry = RetryConfig(**retry_data)

    cb_data = data.pop("circuit_breaker", {})
    cb = CircuitBreakerConfig(**cb_data)

    deg_data = data.pop("graceful_degradation", {})
    deg = DegradationConfig(**deg_data)

    pc_data = data.pop("parallel_competition", {})
    groups_data = pc_data.pop("groups", [])
    groups = [ParallelGroupConfig(**g) for g in groups_data]
    pc = ParallelCompetitionConfig(
        enabled=pc_data.get("enabled", True),
        groups=groups,
        timeout_seconds=pc_data.get("timeout_seconds", 120.0),
    )

    return StabilityConfig(
        enabled=data.get("enabled", True),
        timeout=timeout,
        retry=retry,
        circuit_breaker=cb,
        graceful_degradation=deg,
        parallel_competition=pc,
    )


def _build_optimal_config(data: Dict[str, Any]) -> OptimalControlConfig:
    budget_data = data.pop("budgets", {})
    budgets = BudgetConfig(**budget_data)

    constraint_data = data.pop("constraints", {})
    constraints = ConstraintConfig(**constraint_data)

    return OptimalControlConfig(
        enabled=data.get("enabled", True),
        budgets=budgets,
        constraints=constraints,
    )


def _build_info_flow_config(data: Dict[str, Any]) -> InfoFlowConfig:
    filters_data = data.pop("filters", [])
    filters = [InfoFilterConfig(**f) for f in filters_data]

    return InfoFlowConfig(
        enabled=data.get("enabled", True),
        filters=filters,
        channels=data.get("channels", ["event_bus", "metrics", "storage"]),
    )


def _build_adaptive_config(data: Dict[str, Any]) -> AdaptiveConfig:
    params_data = data.pop("parameters", [])
    params = [AdaptiveParameterConfig(**p) for p in params_data]

    ub_data = data.pop("user_behavior", {})
    ub = UserBehaviorConfig(**ub_data)

    return AdaptiveConfig(
        enabled=data.get("enabled", True),
        learning_rate=data.get("learning_rate", 0.3),
        parameters=params,
        user_behavior=ub,
    )


def _build_hierarchy_config(data: Dict[str, Any]) -> HierarchyConfig:
    layers_data = data.pop("layers", [])
    layers = [HierarchyLayerConfig(**l) for l in layers_data]

    return HierarchyConfig(
        enabled=data.get("enabled", True),
        layers=layers if layers else [
            HierarchyLayerConfig("strategic", ["goal", "branch", "budget"]),
            HierarchyLayerConfig("tactical", ["parameter", "resource", "schedule"]),
            HierarchyLayerConfig("executive", ["tool", "retry", "error_recovery"]),
        ],
    )


# ── 简化 YAML 解析器（无外部依赖） ──

def _parse_yaml_simple(raw: str) -> Dict[str, Any]:
    """
    一个极简的 YAML 解析器，只支持常见结构。
    
    支持：
    - 键值对（字符串、数字、布尔、null）
    - 列表
    - 嵌套字典
    - 注释（# 开头或行内）
    """
    lines = raw.splitlines()
    return _parse_yaml_lines(lines, 0, 0)[0]


def _parse_yaml_lines(lines: List[str], start: int, base_indent: int) -> tuple:
    """递归解析 YAML 行。返回 (result_dict, next_line_index)。"""
    result: Dict[str, Any] = {}
    i = start

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()

        # 空行或注释
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(stripped)

        # 退出当前层级
        if indent < base_indent:
            break

        # 忽略更深的行（先处理当前层级）
        if indent > base_indent:
            i += 1
            continue

        # 解析键值对
        if ":" in stripped:
            key, _, value_part = stripped.partition(":")
            key = key.strip()
            value_str = value_part.strip()

            if not value_str:
                # 值在下一行（嵌套字典或列表）
                i += 1
                if i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.lstrip()
                    next_indent = len(next_line) - len(next_stripped)

                    if next_indent > indent:
                        if next_stripped.startswith("-"):
                            # 列表
                            result[key], i = _parse_yaml_list(lines, i, next_indent)
                        else:
                            # 嵌套字典
                            result[key], i = _parse_yaml_lines(lines, i, next_indent)
                    else:
                        # 空对象
                        result[key] = {}
                else:
                    result[key] = {}
            else:
                # 行内值
                result[key] = _parse_yaml_value(value_str)
                i += 1
        else:
            i += 1

    return result, i


def _parse_yaml_list(lines: List[str], start: int, base_indent: int) -> tuple:
    """解析 YAML 列表。返回 (list, next_line_index)。"""
    result: List[Any] = []
    i = start

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(stripped)

        if indent < base_indent:
            break

        if indent > base_indent:
            i += 1
            continue

        if stripped.startswith("-"):
            item_str = stripped[1:].strip()

            if not item_str:
                # 列表项是嵌套对象
                i += 1
                if i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.lstrip()
                    next_indent = len(next_line) - len(next_stripped)

                    if next_indent > indent:
                        item, i = _parse_yaml_lines(lines, i, next_indent)
                        result.append(item)
                    else:
                        result.append({})
                else:
                    result.append({})
            elif ":" in item_str:
                # 行内对象
                result.append(_parse_yaml_inline_dict(item_str))
                i += 1
            else:
                result.append(_parse_yaml_value(item_str))
                i += 1
        else:
            break

    return result, i


def _parse_yaml_value(value_str: str) -> Any:
    """解析单个 YAML 值。"""
    value_str = value_str.strip()

    # 布尔
    if value_str.lower() in ("true", "yes", "on"):
        return True
    if value_str.lower() in ("false", "no", "off"):
        return False

    # null
    if value_str.lower() in ("null", "~", ""):
        return None

    # 整数
    try:
        return int(value_str)
    except ValueError:
        pass

    # 浮点数
    try:
        return float(value_str)
    except ValueError:
        pass

    # 字符串（去掉引号）
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    return value_str


def _parse_yaml_inline_dict(item_str: str) -> Dict[str, Any]:
    """解析行内字典格式的列表项。"""
    result: Dict[str, Any] = {}
    parts = item_str.split(",")

    for part in parts:
        if ":" in part:
            k, _, v = part.partition(":")
            result[k.strip()] = _parse_yaml_value(v)

    return result


# ── 冒烟测试 ──
if __name__ == "__main__":
    # 测试 1: 最小配置
    minimal = CyberneticsConfig()
    assert minimal.version == "1.0"
    assert minimal.project_name == "unnamed-project"
    assert minimal.feedback_loop.enabled is True
    assert minimal.stability.retry.max_retries == 3
    print("  ✅ 测试 1 通过：默认配置")

    # 测试 2: JSON 加载
    import tempfile
    test_json = {
        "version": "2.0",
        "project_name": "test-pipeline",
        "stability": {
            "enabled": True,
            "retry": {"max_retries": 5, "backoff": "linear"},
        },
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_json, f)
        json_path = f.name

    cfg2 = CyberneticsConfig.from_json(json_path)
    assert cfg2.version == "2.0"
    assert cfg2.stability.retry.max_retries == 5
    assert cfg2.stability.retry.backoff == "linear"
    os.unlink(json_path)
    print("  ✅ 测试 2 通过：JSON 加载")

    # 测试 3: YAML 加载
    yaml_content = """
version: "3.0"
project_name: yaml-test
feedback_loop:
  enabled: false
  max_feedback_depth: 5
stability:
  timeout:
    default: 60
    llm: 300
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    cfg3 = CyberneticsConfig.from_yaml(yaml_path)
    assert cfg3.version == "3.0"
    assert cfg3.feedback_loop.enabled is False
    assert cfg3.feedback_loop.max_feedback_depth == 5
    assert cfg3.stability.timeout.default == 60
    assert cfg3.stability.timeout.llm == 300
    os.unlink(yaml_path)
    print("  ✅ 测试 3 通过：YAML 加载")

    # 测试 4: to_dict 转换
    d = cfg3.to_dict()
    assert d["version"] == "3.0"
    assert d["feedback_loop"]["enabled"] is False
    print("  ✅ 测试 4 通过：to_dict 转换")

    print("\n  ✅ 配置中心所有冒烟测试通过！")
