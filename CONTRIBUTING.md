# Contributing to Cybernetics Agent

感谢你对 Cybernetics Agent 的兴趣！欢迎提交 Issue 和 Pull Request。

## 如何贡献

1. **Fork 仓库** 并克隆到本地
2. **创建分支** `git checkout -b feature/your-feature`
3. **提交更改** `git commit -am "feat: add new feature"`
4. **推送到远程** `git push origin feature/your-feature`
5. **创建 Pull Request**

## 开发环境

```bash
# 克隆仓库
git clone https://github.com/guojiaqi/cybernetics-agent.git
cd cybernetics-agent

# 运行测试
PYTHONPATH=src python3 -m pytest tests/ -v

# 运行冒烟测试
PYTHONPATH=src python3 -c "import cybernetics_agent; print('OK')"
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

## 问题反馈

- 使用 GitHub Issues 提交 bug 报告和功能请求
- 提供尽可能详细的复现步骤
