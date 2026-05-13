# Changelog

## [0.6.1] - 2026-05-13

### Added
- **性能基准测试** — pytest-benchmark 套件
  - 核心模块 7 个：单事件处理 + 批量 100 事件处理
  - Runtime 模块 3 个：EventBus、MetricsCollector、EventStore
  - 23 个 benchmark 测试全部通过
- **CI 覆盖率检查** — GitHub Actions 新增 `--cov-fail-under=90`
- **测试覆盖率大幅提升** — 从 58% → 92%（+34%）
  - 新增 590+ 测试用例，总计 720 个测试全部通过
  - 核心模块全覆盖：FeedbackLoop、SystemIdentifier、AdaptiveTuner、OptimalController、StabilityEngine、HierarchyController、InfoFlow
  - Runtime 层全覆盖：EventBus、EventStore（100%）、MetricsCollector（98%）、PluginLoader、StateManager（99%）
  - Alert 层全覆盖：6 个渠道（含错误处理 mock）、Manager、Rules
  - 新增 `.coveragerc` 配置文件，omit adapters/ 和 cli/ 目录
- **Bug 修复**: EventStore.prune() TypeError、context.py Path 导入

## [0.6.0] - 2026-05-13

### Added
- **事件持久化** (EventStore)
  - `runtime/event_store.py`: SQLite 存储层，零外部依赖
  - 三个表：`events`、`metrics`、`alerts`，带索引加速查询
  - 支持按时间范围、类型、严重级别筛选查询
  - 自动清理超过 30 天的旧数据
- **集成点**
  - MetricsCollector 自动将所有事件写入 SQLite
  - AlertManager 自动将触发的告警写入 SQLite
  - Dashboard 新增 `/api/history/*` 端点
- **Bug 修复**: EventStore 目录自动创建、Dashboard 版本号统一、SQLite 异常保护

### Previous Versions
See [Git history](https://github.com/Jiaqi-Guo-0114/cybernetics-agent/commits/main) for earlier releases (v0.1.0–v0.5.0).
