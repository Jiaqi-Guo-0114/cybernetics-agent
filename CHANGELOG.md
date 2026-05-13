# Changelog

## [0.3.0] - 2026-05-13

### Added
- **Metrics 导出**: `MetricsCollector.to_prometheus()` / `to_openmetrics()` 支持 Prometheus 文本格式导出
- **Plugin 系统**: 热插拔自定义模块
  - `PluginLoader.discover()` 自动发现插件目录
  - `CyberneticsContext.load_plugins()` 动态加载/卸载
  - CLI: `cybernetix plugin list|discover`
- **真实 Dashboard**: FastAPI + SSE 实时事件流
  - 优先使用 FastAPI，回退到 http.server
  - `/metrics` Prometheus 端点
  - `/api/events` SSE 实时事件流
  - `/api/metrics|status|config` JSON API
  - 前端实时指标刷新 + 事件日志
- **自适应调优落地**: `AdaptiveTuner`
  - `auto_tune()`: ε-greedy 自动参数优化
  - `suggest_parameters()`: 推荐调整方案（不应用）
  - `_estimate_confidence()`: 样本量化置信度估计
  - 支持数值型和选项型参数自动调整
- **测试覆盖**: 从 47 项增至 63 项，新增 metrics 导出、plugin、dashboard、auto-tuning 测试

### Fixed
- 修复隐私泄露: 移除本地路径、内部端口和旧用户名引用

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
