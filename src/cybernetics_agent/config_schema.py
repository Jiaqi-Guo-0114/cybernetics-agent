"""
Pydantic v2 配置 Schema（可选依赖）。

提供完整的类型安全配置验证。
如果未安装 pydantic，本模块被忽略，不影响核心功能。

安装：
    pip install pydantic

使用：
    from cybernetics_agent.config_schema import CyberneticsConfigModel
    cfg = CyberneticsConfigModel(**data)
"""

from __future__ import annotations

from typing import Any

try:
    from pydantic import BaseModel, Field, field_validator
    HAS_PYDANTIC = True
except ImportError:  # pragma: no cover
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore[misc,assignment]

if HAS_PYDANTIC:

    class FeedbackLoopConfig(BaseModel):
        enabled: bool = True
        mode: str = "automatic"
        actions: list[Any] = Field(default_factory=list)
        max_feedback_depth: int = Field(default=3, ge=0)

    class TimeoutConfig(BaseModel):
        default: float = Field(default=30.0, gt=0)
        llm: float = Field(default=120.0, gt=0)
        download: float = Field(default=60.0, gt=0)
        tool: float = Field(default=30.0, gt=0)

    class RetryConfig(BaseModel):
        max_retries: int = Field(default=3, ge=0)
        backoff: str = "exponential"
        base_delay: float = Field(default=1.0, gt=0)
        max_delay: float = Field(default=60.0, gt=0)

    class CircuitBreakerConfig(BaseModel):
        enabled: bool = True
        failure_threshold: int = Field(default=5, ge=1)
        recovery_timeout: float = Field(default=60.0, gt=0)
        half_open_max_calls: int = Field(default=3, ge=1)

    class GracefulDegradationConfig(BaseModel):
        enabled: bool = True
        chain: list[Any] = Field(default_factory=list)

    class ParallelCompetitionConfig(BaseModel):
        enabled: bool = True
        groups: list[Any] = Field(default_factory=list)
        timeout_seconds: float = Field(default=120.0, gt=0)

    class StabilityConfig(BaseModel):
        enabled: bool = True
        timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)
        retry: RetryConfig = Field(default_factory=RetryConfig)
        circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
        graceful_degradation: GracefulDegradationConfig = Field(default_factory=GracefulDegradationConfig)
        parallel_competition: ParallelCompetitionConfig = Field(default_factory=ParallelCompetitionConfig)

    class SystemIdConfig(BaseModel):
        enabled: bool = True
        metrics: list[str] = Field(default_factory=lambda: ["conversion_rate", "latency", "error_rate", "token_usage"])
        sampling_rate: float = Field(default=1.0, ge=0, le=1)
        retention_days: int = Field(default=30, ge=1)

    class BudgetsConfig(BaseModel):
        tokens_per_session: float = Field(default=100000.0, ge=0)
        api_calls_per_session: float = Field(default=50.0, ge=0)
        cost_usd_per_session: float = Field(default=5.0, ge=0)

    class ConstraintsConfig(BaseModel):
        max_concurrent_tools: int = Field(default=5, ge=1)
        max_llm_requests_per_minute: int = Field(default=10, ge=1)

    class OptimalControlConfig(BaseModel):
        enabled: bool = True
        budgets: BudgetsConfig = Field(default_factory=BudgetsConfig)
        constraints: ConstraintsConfig = Field(default_factory=ConstraintsConfig)

    class InfoFlowConfig(BaseModel):
        enabled: bool = True
        filters: list[Any] = Field(default_factory=list)
        channels: list[str] = Field(default_factory=lambda: ["event_bus", "metrics", "storage"])

    class UserBehaviorConfig(BaseModel):
        track_topics: bool = True
        track_feedback: bool = True
        topic_decay_half_life_days: int = Field(default=7, ge=1)

    class AdaptiveConfig(BaseModel):
        enabled: bool = True
        learning_rate: float = Field(default=0.3, gt=0, le=1)
        parameters: list[Any] = Field(default_factory=list)
        user_behavior: UserBehaviorConfig = Field(default_factory=UserBehaviorConfig)

    class HierarchyLayerConfig(BaseModel):
        name: str
        decision_types: list[str]

    class HierarchyConfig(BaseModel):
        enabled: bool = True
        layers: list[HierarchyLayerConfig] = Field(default_factory=lambda: [
            HierarchyLayerConfig(name="strategic", decision_types=["goal", "branch", "budget"]),
            HierarchyLayerConfig(name="tactical", decision_types=["parameter", "resource", "schedule"]),
            HierarchyLayerConfig(name="executive", decision_types=["tool", "retry", "error_recovery"]),
        ])

    class RotationConfig(BaseModel):
        max_file_size_mb: int = Field(default=10, ge=1)
        max_files: int = Field(default=10, ge=1)

    class StorageConfig(BaseModel):
        backend: str = "jsonl"
        path: str = "./.cybernetics"
        rotation: RotationConfig = Field(default_factory=RotationConfig)

    class CyberneticsConfigModel(BaseModel):
        """Pydantic v2 配置 Schema。"""
        version: str = "1.0"
        project_name: str = Field(default="unnamed-project", min_length=1)
        feedback_loop: FeedbackLoopConfig = Field(default_factory=FeedbackLoopConfig)
        stability: StabilityConfig = Field(default_factory=StabilityConfig)
        system_id: SystemIdConfig = Field(default_factory=SystemIdConfig)
        optimal_control: OptimalControlConfig = Field(default_factory=OptimalControlConfig)
        info_flow: InfoFlowConfig = Field(default_factory=InfoFlowConfig)
        adaptive: AdaptiveConfig = Field(default_factory=AdaptiveConfig)
        hierarchy: HierarchyConfig = Field(default_factory=HierarchyConfig)
        storage: StorageConfig = Field(default_factory=StorageConfig)
        plugins: dict[str, Any] = Field(default_factory=dict)

        @field_validator("project_name")
        @classmethod
        def _validate_project_name(cls, v: str) -> str:
            if not v.strip():
                raise ValueError("project_name 不能为空")
            return v


def _config_to_pydantic(cfg: Any) -> Any:
    """将 CyberneticsConfig dataclass 转换为 Pydantic model。"""
    if not HAS_PYDANTIC:
        raise ImportError("pydantic 未安装")
    return CyberneticsConfigModel(**cfg.to_dict())
