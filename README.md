# 🦙 Cybernetics Agent

> 一个框架无关的控制论 Agent 增强层。
> 基于钱学森《工程控制论》七大核心原则，让任何 Python Agent 都能获得自适应、自恢复、自优化的能力。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-83%2F83-brightgreen.svg)]()

🌐 **[English](README.en.md)** · **[Français](README.fr.md)** · **[Español](README.es.md)** · **[日本語](README.ja.md)** · **[한국어](README.ko.md)**

---

## ✅ 特性

- **框架无关** — 不依赖任何 LLM 框架，纯标准库
- **七大原则** — 钱学森《工程控制论》全覆盖
- **多框架适配** — 支持 LangChain、AutoGen、CrewAI、Hermes、Claude Code、Codex 等
- **声明式配置** — JSON/YAML 配置，灵活可控
- **策略预设** — 4 种开箱即用配置模板
- **Metrics 导出** — Prometheus / OpenMetrics 文本格式
- **Plugin 系统** — 热插拔自定义模块
- **实时 Dashboard** — FastAPI + SSE 事件流
- **自适应调优** — ε-greedy 参数自动优化
- **完整 CLI** — `cybernetix` 命令行工具
- **线程安全** — 内置线程锁保护

**设计哲学**: ① 如无必要，勿增实体 ② 大把拆小，组合为工作流

## 🚀 快速开始

```bash
# 安装
pip install cybernetics-agent

# 初始化配置
cybernetix init

# 使用
python -c "
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
ctx = CyberneticsContext(CyberneticsConfig(project_name='my-agent'))
ctx.emit_tool_result('search', ['paper1', 'paper2'])
print(ctx.get_status())
"
```

## 🎯 七大原则

| 原则 | 模块 | 功能 |
|------|------|------|
| 1. 反馈闭环 | FeedbackLoop | 触发式行动，自动调整 |
| 2. 稳定性优先 | StabilityEngine | 重试、熔断器、降级、超时控制 |
| 3. 系统辨识 | SystemIdentifier | 转化漏斗、效率指标采集 |
| 4. 最优控制 | OptimalController | 预算管理、约束检查 |
| 5. 信息论 | InfoFlow | 消息过滤、分发 |
| 6. 自适应 | AdaptiveTuner | 参数自动调优 |
| 7. 分层控制 | HierarchyController | 战略/战术/执行三层架构 |

## 🔧 支持的框架

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
```

## 📁 CLI 工具

```bash
cybernetix init                          # 初始化配置
cybernetix preset list                   # 列出策略预设
cybernetix preset show <name>            # 查看预设详情
cybernetix preset apply <name> -o cfg.json  # 应用预设
cybernetix validate cfg.json             # 验证配置文件
cybernetix plugin list                   # 列出插件
cybernetix plugin discover               # 发现插件
cybernetix dashboard                     # 启动监控仪表盘
cybernetix audit ./src                   # 审计代码缺陷
cybernetix run ./task.py                 # 运行任务并采集指标
cybernetix --version                     # 查看版本号
```

## 📊 监控仪表盘

![Dashboard Preview](assets/dashboard_preview.png)

启动监控仪表盘：
```bash
cybernetix dashboard
```

## 📝 许可证

MIT License © 2026 Cybernetics Agent Contributors
