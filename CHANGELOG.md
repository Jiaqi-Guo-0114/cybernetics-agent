# Changelog

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
