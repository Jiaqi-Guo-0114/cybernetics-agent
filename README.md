# 🦙 Cybernetics Agent

> 一个框架无关的控制论 Agent 增强层。
> 基于钱学森《工程控制论》七大核心原则，让任何 Python Agent 都能获得自适应、自恢复、自优化的能力。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## ✨ 特性

- 🔧 **框架无关** — 支持 Hermes、LangChain、CrewAI、AutoGen、纯 Python 等任何框架
- 📊 **七大原则** — 反馈闭环、稳定性优先、系统辨识、最优控制、信息流、自适应、分层控制
- ⚡ **零依赖** — 纯标准库，无需安装任何额外依赖
- 📄️ **声明式配置** — JSON/YAML 配置，即配即用
- 📈 **实时 Dashboard** — 本地 Web 仪表盘，可视化系统状态
- 🧠 **智能审计** — CLI 工具自动检测代码中的控制论缺陷

---

## 🚀 快速开始

### 安装

```bash
pip install cybernetics-agent
```

### 配置

创建 `cybernetics.json`：

```json
{
  "version": "1.0",
  "project_name": "my-agent",
  "feedback_loop": { "enabled": true },
  "stability": { "enabled": true }
}
```

### 代码中使用

```python
from cybernetics_agent import CyberneticsContext, CyberneticsConfig

# 加载配置
config = CyberneticsConfig.from_json("cybernetics.json")

# 创建上下文
ctx = CyberneticsContext(config)

# 发射事件（自动触发所有已启用的控制论模块）
ctx.emit_tool_result("search", ["result1", "result2"])
ctx.emit_tool_error("download", "timeout")

# 查看状态
print(ctx.get_status())
```

### 与 LangChain 整合

```python
from langchain_openai import ChatOpenAI
from cybernetics_agent.adapters import LangChainAdapter
from cybernetics_agent import CyberneticsContext, CyberneticsConfig

# 初始化控制论层
config = CyberneticsConfig.from_json("cybernetics.json")
ctx = CyberneticsContext(config)

# 创建 LangChain LLM 并接入适配器
llm = ChatOpenAI()
adapter = LangChainAdapter(ctx)
adapter.install(llm)

# 使用 LLM 时，所有调用自动被记录和分析
result = llm.invoke("Hello, world!")
```

### CLI 工具

```bash
# 初始化配置
cybernetix init

# 审计代码目录
cybernetix audit ./my_project

# 生成审计报告
cybernetix report --format markdown

# 启动 Dashboard
cybernetix dashboard --port 8080
```

---

## 🏠 架构

```
┌────────────────────────────────────────────────────────────────┐
│                     你的 Agent 项目                           │
├─────────────────────────────────────────────────────────────────┤
│  适配层（Hermes / LangChain / CrewAI / AutoGen / Native）    │
├─────────────────────────────────────────────────────────────────┤
│  核心框架 — 七大原则实现                       │
│  ─ FeedbackLoop / StabilityEngine / SystemIdentifier        │
│  ─ OptimalController / InfoFlow / AdaptiveTuner              │
│  ─ HierarchyController                                       │
├─────────────────────────────────────────────────────────────────┤
│  运行时层 — EventBus + StateManager + MetricsCollector   │
├─────────────────────────────────────────────────────────────────┤
│  存储层 — JSONL / SQLite / Redis（可插拔）              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📖 七大原则快速对照

| 原则 | 问题 | 解决方案 |
|------|------|---------|
| **反馈闭环** | 检测到问题但不行动？ | 检测→决策→行动的真闭环 |
| **稳定性优先** | 失败时崩溃？ | 重试、降级、熔断、并行竞争 |
| **系统辨识** | 不知道系统跑得怎么样？ | 性能指标采集、转化漏斗、预测模型 |
| **最优控制** | 浪费资源或超预算？ | Token/API/成本预算管理 |
| **信息流** | 信息噪声大、丢失？ | 事件滤波、去重、速率限制 |
| **自适应** | 参数一成不变？ | EMA 学习、用户行为追踪、动态调参 |
| **分层控制** | 所有决策压在同一层？ | 战略/战术/执行三层架构 |

---

## 📑 相关资料

- [RFC-001: 架构与接口设计](docs/RFC-001.md)
- [快速开始指南](docs/quickstart.md)
- [API 参考](docs/api-reference.md)
- [实际案例](examples/)

---

## 👥 贡献

欢迎 Issue 和 PR！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 📄️ License

MIT License © 2026 Cybernetics Agent Contributors
