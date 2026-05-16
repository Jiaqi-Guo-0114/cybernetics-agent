# Configuration

> 声明式配置，8 大模块精细控制。

---

## 配置方式

### 方式 1：Python 代码

```python
from cybernetics_agent import CyberneticsConfig

cfg = CyberneticsConfig(
    project_name="my-agent",
    stability={
        "timeout": {"default": 30.0, "llm": 120.0, "download": 60.0},
        "retry": {"max_retries": 3, "backoff": "exponential", "base_delay": 1.0},
    },
)
```

### 方式 2：JSON 文件

```python
cfg = CyberneticsConfig.from_json("config.json")
# 或加载并验证
cfg = CyberneticsConfig.from_json_validated("config.json")
```

### 方式 3：YAML 文件（需安装 PyYAML）

```python
cfg = CyberneticsConfig.from_yaml("config.yaml")
cfg = CyberneticsConfig.from_yaml_validated("config.yaml")
```

---

## 配置结构

```python
CyberneticsConfig(
    version="1.0",                    # 配置版本
    project_name="unnamed-project",   # 项目名（用于标识和 Dashboard）
    feedback_loop={...},              # 反馈闭环
    stability={...},                  # 稳定性引擎
    system_id={...},                  # 系统辨识
    optimal_control={...},            # 最优控制
    info_flow={...},                  # 信息流
    adaptive={...},                   # 自适应调谐
    hierarchy={...},                  # 分层控制
    storage={...},                    # 存储
    plugins={},                       # 插件
)
```

---

## 模块详解

### feedback_loop — 反馈闭环

```python
{
    "enabled": True,           # 是否启用
    "mode": "automatic",       # 模式：automatic / manual
    "actions": [],             # 触发动作列表
    "max_feedback_depth": 3,   # 最大反馈深度（防无限循环）
}
```

### stability — 稳定性引擎

```python
{
    "enabled": True,
    "timeout": {                    # 超时配置（秒）
        "default": 30.0,            # 默认超时
        "llm": 120.0,               # LLM 调用超时
        "download": 60.0,           # 下载超时
        "tool": 30.0,               # 工具调用超时
    },
    "retry": {                      # 重试配置
        "max_retries": 3,           # 最大重试次数
        "backoff": "exponential",   # 退避策略：exponential / fixed
        "base_delay": 1.0,          # 基础延迟（秒）
        "max_delay": 60.0,          # 最大延迟（秒）
    },
    "circuit_breaker": {            # 熔断器
        "enabled": True,
        "failure_threshold": 5,     # 连续失败阈值
        "recovery_timeout": 60.0,   # 恢复超时（秒）
        "half_open_max_calls": 3,   # 半开状态最大试探调用数
    },
    "graceful_degradation": {       # 优雅降级
        "enabled": True,
        "chain": [],                # 降级链：["fulltext", "abstract", "metadata"]
    },
    "parallel_competition": {       # 并行竞争
        "enabled": True,
        "groups": [],               # 竞争组配置
        "timeout_seconds": 120.0,   # 竞争超时
    },
}
```

### system_id — 系统辨识

```python
{
    "enabled": True,
    "metrics": [                    # 采集的指标
        "conversion_rate",
        "latency",
        "error_rate",
        "token_usage",
    ],
    "sampling_rate": 1.0,           # 采样率 [0, 1]
    "retention_days": 30,           # 数据保留天数
}
```

### optimal_control — 最优控制

```python
{
    "enabled": True,
    "budgets": {                    # 预算限制
        "tokens_per_session": 100000,
        "api_calls_per_session": 50,
        "cost_usd_per_session": 5.0,
    },
    "constraints": {                # 并发约束
        "max_concurrent_tools": 5,
        "max_llm_requests_per_minute": 10,
    },
}
```

### info_flow — 信息流

```python
{
    "enabled": True,
    "filters": [],                  # 消息过滤器
    "channels": [                   # 输出渠道
        "event_bus",
        "metrics",
        "storage",
    ],
}
```

### adaptive — 自适应调谐

```python
{
    "enabled": True,
    "learning_rate": 0.3,           # 学习率
    "parameters": [],               # 自动调优参数列表
    "user_behavior": {              # 用户行为追踪
        "track_topics": True,
        "track_feedback": True,
        "topic_decay_half_life_days": 7,
    },
}
```

### hierarchy — 分层控制

```python
{
    "enabled": True,
    "layers": [                     # 三层架构
        {"name": "strategic",  "decision_types": ["goal", "branch", "budget"]},
        {"name": "tactical",  "decision_types": ["parameter", "resource", "schedule"]},
        {"name": "executive", "decision_types": ["tool", "retry", "error_recovery"]},
    ],
}
```

### storage — 存储

```python
{
    "backend": "jsonl",             # 后端：jsonl / sqlite
    "path": "./.cybernetics",       # 存储路径
    "rotation": {                   # 日志轮转
        "max_file_size_mb": 10,
        "max_files": 10,
    },
}
```

---

## 验证配置

```python
# 验证并获取错误列表
errors = cfg.validate()
if errors:
    for e in errors:
        print(f"❌ {e}")
else:
    print("✅ 配置验证通过")

# 或使用自动验证的加载方法
cfg = CyberneticsConfig.from_json_validated("config.json")
```

验证规则包括：
- `project_name` 必须是非空字符串
- 所有 timeout 值必须是正数
- `max_retries` 不能为负数
- `failure_threshold` 必须 ≥ 1
- 预算值必须是非负数
- `sampling_rate` 必须在 [0, 1] 区间内

---

## 环境变量注入（v0.6.4+）

配置文件支持动态环境变量注入，无需硬编配置值。

### 语法

| 语法 | 示例 | 结果 |
|------|------|------|
| `${VAR}` | `"project_name": "${CYBER_PROJECT}"` | 从环境变量读取 |
| `${VAR:default}` | `"api_key": "${CYBER_API_KEY:sk-default}"` | 未设置时使用默认值 |
| `env://VAR` | `"secret": "env://CYBER_SECRET"` | 从环境变量读取 |

### 示例

```json
{
    "project_name": "${CYBER_PROJECT_NAME:my-agent}",
    "stability": {
        "timeout": {
            "llm": ${CYBER_LLM_TIMEOUT:120.0}
        }
    },
    "alert": {
        "channels": {
            "feishu": {
                "webhook_url": "env://FEISHU_WEBHOOK_URL"
            }
        }
    }
}
```

### 安全建议

- 敏感配置（API key、webhook URL）使用 `env://` 或 `${VAR}` 语法
- 不要将 `.env` 文件提交到版本控制
- 生产环境使用秘密管理工具（如 Vault、AWS Secrets Manager）

---

## Pydantic Schema 验证（v0.6.4+）

安装 `pydantic` 后可使用强类型验证：

```bash
pip install pydantic
```

```python
from cybernetics_agent.config_schema import CyberneticsConfigModel

# 强类型验证
model = CyberneticsConfigModel(
    project_name="my-agent",
    stability={"timeout": {"default": 30.0}},
)

# 自动验证规则：负数 timeout 报错、空 project_name 报错
```

---

## OpenTelemetry 配置（v0.6.4+）

安装 `opentelemetry-api` 后自动启用追踪：

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

```python
from cybernetics_agent.runtime.tracing import CyberneticsTracer

ctx = CyberneticsContext(
    config,
    tracer=CyberneticsTracer("my-agent"),
)
# 每次 emit() 自动创建 span
```

环境变量配置 OTLP 导出：

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://jaeger.example.com:4317
```

---

## 异步配置（v0.6.4+）

```python
import asyncio
from cybernetics_agent.async_support import AsyncCyberneticsContext

async def main():
    ctx = AsyncCyberneticsContext(config)
    await ctx.emit("tool_result", result="ok")
    await ctx.close()

asyncio.run(main())
```

异步 EventBus 示例：

```python
from cybernetics_agent.async_support import AsyncEventBus

bus = AsyncEventBus()

async def handler(event):
    print(f"收到: {event}")

bus.subscribe("tool_result", handler)
await bus.emit("tool_result", {"status": "ok"})
```

---

## 配置热重载

Dashboard 启动时自动监听配置文件变更，修改后自动重载：

```bash
cybernetix dashboard --config cfg.json
# 修改 cfg.json → 5秒后自动生效
```

---

## 告警配置（Dashboard 专用）

在配置文件中添加 `alert` 字段启用告警：

```json
{
    "alert": {
        "enabled": true,
        "rules": [
            {
                "type": "threshold",
                "name": "high_error_rate",
                "metric": "error_rate",
                "operator": ">",
                "threshold": 0.1,
                "severity": "warning"
            }
        ]
    }
}
```

告警规则类型：
- `threshold` — 阈值规则（ metric operator threshold ）

告警渠道需在代码中注册：
```python
from cybernetics_agent.alert import AlertManager
from cybernetics_agent.alert.channels import StdoutChannel, FeishuChannel

alert_manager = AlertManager()
alert_manager.register_channel("stdout", StdoutChannel())
alert_manager.register_channel("feishu", FeishuChannel(webhook_url="..."))
```

支持的渠道：飞书、钉钉、Discord、Slack、Email、Webhook、Stdout
