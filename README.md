# 🐙 Cybernetics Agent

> 一个框架无关的控制论 Agent 增强层。
> 让任何 Python Agent 获得自适应、自恢复、自优化的生产级能力。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-950%2F950-brightgreen.svg)]()

🌐 **[English](README.en.md)** · **[Français](README.fr.md)** · **[Español](README.es.md)** · **[日本語](README.ja.md)** · **[한国어](README.ko.md)**

---

**Documentation**: [docs/](docs/) · **Changelog**: [CHANGELOG.md](CHANGELOG.md) · **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## What is Cybernetics Agent?

Cybernetics Agent 是一个 Python 库，为你的 AI Agent 添加**生产级稳定性**——无需修改现有代码。

它基于钱学森《工程控制论》，自动为你的 Agent 提供：
- 失败自动重试与熔断保护
- 资源预算与约束检查
- 自适应参数调优
- 实时监控与告警

**框架无关**：不依赖任何 LLM 框架，一行代码接入 LangChain、AutoGen、CrewAI 等。

## 🚀 Quick Start

```bash
pip install git+https://github.com/Jiaqi-Guo-0114/cybernetics-agent.git
```

```python
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.presets import apply_preset

# 生产级稳定性配置
ctx = CyberneticsContext(CyberneticsConfig(
    project_name='my-agent',
))
apply_preset(ctx.config, 'high_reliability')

# 你的业务代码——Cybernetics 自动包裹
result = ctx.emit_tool_result('search_api', query="machine learning")
# 失败？自动重试3次 → 仍失败？熔断器打开 → 返回降级结果 → 飞书告警
```

## ✅ Features

### Core Engine
- **框架无关** — 不依赖任何 LLM 框架，纯标准库
- **七大控制论原则** — 钱学森《工程控制论》全覆盖
- **自适应调优** — ε-greedy 参数自动优化
- **分层控制** — 战略/战术/执行三层架构

### Operations & Monitoring
- **稳定性引擎** — 重试、熔断器、降级、超时控制
- **Metrics 导出** — Prometheus / OpenMetrics 文本格式
- **实时 Dashboard** — FastAPI + 独立前端，SSE 事件流，告警面板 + 历史查询
- **告警系统** — 阈值规则 + 7 个通知渠道，支持 group_by 聚合与窗口抑制
- **事件持久化** — SQLite WAL 模式，批量写入，进程重启不丢失
- **数据归档** — 冷数据 gzip 压缩归档，支持本地/S3，自动清理
- **配置热重载** — 运行时修改配置文件自动生效
- **环境变量注入** — `${VAR}` / `env://VAR` 语法，支持默认值
- **健康检查** — `/health` / `/ready` 探针，适配 K8s
- **性能回归测试** — pytest-benchmark + CI 基线对比

### Integration & Developer Experience
- **多框架适配** — LangChain、AutoGen、CrewAI、Hermes、Claude Code、Codex 等
- **异步支持** — AsyncCyberneticsContext + async EventBus，全链路 async/await
- **OpenTelemetry 追踪** — 分布式追踪集成（可选依赖）
- **控制论深度算法** — PID 控制器、UCB/Thompson Sampling、MPC 资源分配
- **Plugin 系统** — 热插拔自定义模块
- **完整 CLI** — `cybernetix` 命令行工具，含 shell 自动补全
- **声明式配置** — JSON/YAML + Pydantic Schema 验证
- **策略预设** — 4 种开箱即用配置模板
- **线程安全** — 内置线程锁保护
- **Docker / K8s** — 多阶段镜像 + Helm-ready 清单

## 🎯 Seven Principles

| 原则 | 模块 | 功能 | 解决的问题 |
|------|------|------|-----------|
| 1. 反馈闭环 | FeedbackLoop | 触发式行动，自动调整 | Agent 执行后无人验证结果 |
| 2. 稳定性优先 | StabilityEngine | 重试、熔断器、降级、超时控制 | API 挂了 Agent 就崩溃 |
| 3. 系统辨识 | SystemIdentifier | 转化漏斗、效率指标采集 | 不知道 Agent 哪里效率低 |
| 4. 最优控制 | OptimalController | 预算管理、约束检查 | Token/成本超支 |
| 5. 信息论 | InfoFlow | 消息过滤、分发 | 噪音信息淹没关键信号 |
| 6. 自适应 | AdaptiveTuner | 参数自动调优 | 手工调参耗时且不精准 |
| 7. 分层控制 | HierarchyController | 战略/战术/执行三层架构 | 缺乏全局调度与优先级管理 |

## 🔧 Adapters

```python
from cybernetics_agent.adapters import (
    NativeAdapter,       # 纯 Python
    LangChainAdapter,    # LangChain
    AutoGenAdapter,      # AutoGen
    CrewAIAdapter,       # CrewAI
    HermesAdapter,       # Hermes Agent
    ClaudeCodeAdapter,   # Claude Code CLI
    CodexAdapter,        # OpenAI Codex CLI
    OpenClawAdapter,     # OpenClaw (HTTP)
    QwenpawAdapter,      # Qwenpaw
)

# LangChain 5秒接入示例
adapter = LangChainAdapter(ctx)
# 然后正常使用你的 LangChain chain
# Cybernetics 自动包裹所有 tool 调用
```

## 📁 CLI

```bash
cybernetix init                          # 初始化配置
cybernetix preset list                   # 列出策略预设
cybernetix preset apply <name> -o cfg.json  # 应用预设
cybernetix validate cfg.json             # 验证配置文件
cybernetix dashboard                     # 启动监控仪表盘（默认 http://localhost:8080）
cybernetix alert test                    # 测试告警渠道
cybernetix alert status                  # 查看告警规则状态
cybernetix alert fire -m "msg" -s error  # 手动触发告警
cybernetix audit ./src                   # 审计代码缺陷
cybernetix run ./task.py                 # 运行任务并采集指标
cybernetix completion bash               # 生成 bash 自动补全脚本
cybernetix --version                     # 查看版本号
```

## 📊 Dashboard

启动监控仪表盘：

```bash
cybernetix dashboard  # 默认 http://localhost:8080
```

- 实时事件流（SSE）
- 告警规则可视化
- 历史查询与过滤
- 性能指标趋势图

![Dashboard Preview](assets/dashboard_preview.png)

## 📚 Documentation

- [Getting Started](docs/getting-started.md) — 5分钟上手
- [Adapters](docs/adapters.md) — 接入 LangChain / AutoGen / CrewAI 等框架
- [Configuration](docs/configuration.md) — 8大模块配置详解
- [Dashboard](docs/dashboard.md) — 实时监控与告警面板
- [Architecture & Design](docs/v0.7.0-design.md)
- [RFC-001](docs/RFC-001.md)
- [Changelog](CHANGELOG.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📝 License

MIT License © 2026 Cybernetics Agent Contributors
