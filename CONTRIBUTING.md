# Contributing to Cybernetics Agent

感谢你对 Cybernetics Agent 的兴趣！欢迎提交 Issue 和 Pull Request。

## 设计原则

本项目遵循两个核心原则，所有贡献都应参考：

1. **如无必要，勿增实体**（奥卡姆剑刀）— 不引入不必要的依赖、不创建不必要的抽象层、不添加不必要的配置项。每行代码都必须有存在的理由。如果一个功能可以用更少的代码实现，那就是更好的实现。

2. **大把拆小，组合为工作流** — 复杂功能不是一个巨大的类，而是多个小模块的组合。模块之间零依赖，单独可用、单独可测。如果一个文件超过 300 行或一个类超过 10 个方法，就应该考虑拆分。

## 如何贡献

1. **Fork 仓库** 并克隆到本地
2. **创建分支** `git checkout -b feature/your-feature`
3. **提交更改** `git commit -am "feat: add new feature"`
4. **推送到远程** `git push origin feature/your-feature`
5. **创建 Pull Request**

## 开发环境

```bash
# 克隆仓库
git clone https://github.com/Jiaqi-Guo-0114/cybernetics-agent.git
cd cybernetics-agent

# 运行测试
PYTHONPATH=src python3 -m pytest tests/ -v

# 运行测试并生成覆盖率报告
PYTHONPATH=src python3 -m pytest tests/ --cov=src/cybernetics_agent -v
```

## 提交规范

- 使用 [Conventional Commits](https://www.conventionalcommits.org/)
- 保持测试通过
- 添加相关测试用例
- 更新文档（如果需要）

## 代码风格

- Python 3.9+ 兼容
- 纯标准库，无外部依赖
- 类型注解尽量完整
- 中文注释、中文用户面向字符串
- **提交前三件套**：
  ```bash
  # 1. ruff 代码检查
  ruff check src/ tests/
  
  # 2. 全量测试
  PYTHONPATH=src python3 -m pytest tests/ -q --tb=line
  
  # 3. 覆盖率检查（不得低于 90%）
  PYTHONPATH=src python3 -m pytest tests/ --cov=src/cybernetics_agent --cov-fail-under=90 -q
  ```
  常见问题：未使用的 import（F401）、未使用的变量（F841）。可自动修复：
  ```bash
  ruff check src/ tests/ --fix
  ```
- **类型检查（推荐）**：
  ```bash
  python3 -m mypy src/cybernetics_agent --ignore-missing-imports --no-error-summary
  ```

## 隐私安全

- **git author 必须匿名**—不得使用真实姓名或个人邮箱作为 commit author
- 提交前请确认：`git config user.name` 和 `user.email` 均为匿名值
- 如已泄露实名，使用 `git-filter-repo` 重写历史

## 测试规范

- 每个新功能/修复必须配套测试
- 测试文件名以 `test_` 开头
- 使用 `unittest.mock` 模拟外部 I/O（HTTP、SMTP、文件系统）
- 不要在测试中使用 `time.sleep`，如需待用 `monkeypatch`
- 测试类名不要重复（跨文件重复会导致 pytest 收集异常）
- 提交前确保本地通过全量测试：
  ```bash
  PYTHONPATH=src python3 -m pytest tests/ -q --tb=line
  ```

## 问题反馈

- 使用 GitHub Issues 提交 bug 报告和功能请求
- 提供尽可能详细的复现步骤
