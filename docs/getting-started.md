# Getting Started

> 5分钟让你的 Agent 拥有生产级稳定性。

---

## 安装

```bash
pip install cybernetics-agent
```

可选依赖：
```bash
# 监控仪表盘（FastAPI + SSE）
pip install cybernetics-agent[dashboard]

# YAML 配置支持
pip install cybernetics-agent[yaml]

# 全部可选依赖
pip install cybernetics-agent[all]
```

---

## Hello World

```python
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.presets import apply_preset

# 1. 创建配置
cfg = CyberneticsConfig(project_name="my-first-agent")

# 2. 应用预设（高可靠性模式）
apply_preset(cfg, "high_reliability")

# 3. 启动上下文
ctx = CyberneticsContext(cfg)

# 4. 你的业务代码——Cybernetics 自动包裹
try:
    result = your_api_call()
    ctx.emit_tool_result("my_api", result)
except Exception as e:
    ctx.emit_tool_error("my_api", e)
    # Cybernetics 自动重试 → 熔断 → 降级 → 告警

# 5. 关闭
ctx.shutdown()
```

---

## 用预设快速配置

Cybernetics Agent 提供 4 种开箱即用的策略预设：

| 预设 | 场景 | 特点 |
|------|------|------|
| `high_reliability` | 生产环境 | 重试5次，熔断严格，降级链完整 |
| `high_concurrency` | 批量任务 | 并行竞争，超时放宽，重试较少 |
| `low_cost` | 开发测试 | 预算严格，超时短，采样率降低 |
| `debug` | 排查问题 | 超时最长，重试关闭，完整日志 |

```python
from cybernetics_agent.presets import apply_preset, list_presets

# 列出所有预设
print(list_presets())  # ['high_concurrency', 'low_cost', 'high_reliability', 'debug']

# 应用到配置
cfg = CyberneticsConfig()
apply_preset(cfg, "high_reliability")
```

---

## CLI 快速上手

```bash
# 初始化配置
cybernetix init

# 列出预设
cybernetix preset list

# 应用预设并导出
cybernetix preset apply high_reliability -o cfg.json

# 验证配置
cybernetix validate cfg.json

# 启动监控仪表盘
cybernetix dashboard

# 测试告警
cybernetix alert test

# 审计代码
cybernetix audit ./src

# 查看版本
cybernetix --version
```

---

## 下一步

- [配置详解](configuration.md) — 深入了解每个模块的配置选项
- [适配器接入](adapters.md) — 将 Cybernetics 接入 LangChain / AutoGen / CrewAI 等框架
- [监控仪表盘](dashboard.md) — 实时查看 Agent 运行状态和告警
