# Changelog

## [0.2.0] - 2026-05-13

### Added
- **策略预设库** (Strategy Presets): 4 种开箱即用配置模板
  - `high_concurrency` — 高并发，适合批量任务
  - `low_cost` — 严格预算控制，适合开发测试
  - `high_reliability` — 生产环境关键任务
  - `debug` — 排查问题专用
  - CLI 支持: `cybernetix preset list|show|apply|init`
- **配置验证增强**: `validate` 命令复用 `CyberneticsConfig.validate()` 提供 schema 级检查
- **最小示例**: 新增 `examples/minimal_langchain.py`、`examples/minimal_native.py`、`examples/minimal_hermes.py`
- **CLI `--version`**: 支持 `cybernetix --version` 查看版本号
- **测试覆盖**: 从 42 项增至 47 项，新增 preset CLI 和版本号测试

### Changed
- 统一配置格式: `init` 命令生成的配置与 presets 格式保持一致，解决旧格式与新格式不兼容问题

## [0.1.0] - 2026-05-12

### Added
- 初始发布: 控制论 Agent 增强层
- 七大核心模块: Feedback Loop, Stability, System ID, Optimal Control, Info Flow, Adaptive, Hierarchy
- 9 个框架适配器: LangChain, LlamaIndex, AutoGen, CrewAI, Claude Code, Codex, Hermes, OpenClaw, QwenPaw
- CLI 工具: `init`, `audit`, `report`, `dashboard`, `validate`
- 配置系统: JSON/YAML 加载 + schema 验证
- Web 仪表盘: 实时监控与可视化
