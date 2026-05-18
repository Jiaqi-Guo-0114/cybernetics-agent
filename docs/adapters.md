# Adapters

> 一行代码将 Cybernetics Agent 接入你的现有框架。

Cybernetics Agent 是**框架无关**的——它本身不依赖任何 LLM 框架。通过适配器层，你可以在不修改业务代码的情况下，为任何 Python Agent 添加控制论增强。

---

## 可用适配器

| 适配器 | 目标框架 | 接入方式 |
|--------|---------|---------|
| `NativeAdapter` | 纯 Python | 直接包裹函数调用 |
| `LangChainAdapter` | LangChain | 回调处理器 |
| `AutoGenAdapter` | AutoGen | 代理包装器 |
| `CrewAIAdapter` | CrewAI | 任务包装器 |
| `HermesAdapter` | Hermes Agent | 工具调用拦截 |
| `ClaudeCodeAdapter` | Claude Code CLI | 子进程包裹 |
| `CodexAdapter` | OpenAI Codex CLI | 子进程包裹 |
| `OpenClawAdapter` | OpenClaw (HTTP) | HTTP 中间件 |
| `QwenpawAdapter` | Qwenpaw | 工具调用拦截 |

---

## 通用接入模式

所有适配器遵循相同的模式：

```python
from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.adapters import SomeAdapter

cfg = CyberneticsConfig(project_name="my-app")
ctx = CyberneticsContext(cfg)

# 创建适配器
adapter = SomeAdapter(ctx)

# 然后正常使用你的框架——Cybernetics 自动包裹所有关键调用
```

---

## 各框架示例

### 纯 Python (NativeAdapter)

最轻量的接入方式，适合任何 Python 项目：

```python
from cybernetics_agent.adapters import NativeAdapter

adapter = NativeAdapter(ctx)

# 包裹任意函数
@adapter.wrap("search_api")
def search(query: str):
    return requests.get(f"https://api.example.com/search?q={query}").json()

# 调用时自动获得重试、熔断、降级保护
results = search("machine learning")
```

### LangChain (LangChainAdapter)

```python
from cybernetics_agent.adapters import LangChainAdapter
from langchain import OpenAI, LLMChain, PromptTemplate

# 创建适配器
adapter = LangChainAdapter(ctx)

# 正常使用 LangChain——所有 tool 调用自动被包裹
llm = OpenAI()
chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{input}"))
result = chain.run("Hello")

# Cybernetics 自动：
# - 超时控制
# - 失败重试
# - 熔断保护
# - 指标采集
```

### AutoGen (AutoGenAdapter)

```python
from cybernetics_agent.adapters import AutoGenAdapter
import autogen

adapter = AutoGenAdapter(ctx)

# 包装 AutoGen 代理
assistant = adapter.wrap_agent(
    autogen.AssistantAgent(name="assistant", llm_config={...})
)

# 所有代理交互自动获得稳定性保护
```

### CrewAI (CrewAIAdapter)

```python
from cybernetics_agent.adapters import CrewAIAdapter
from crewai import Agent, Task, Crew

adapter = CrewAIAdapter(ctx)

# 包装整个 Crew
crew = Crew(agents=[...], tasks=[...])
wrapped_crew = adapter.wrap_crew(crew)

# 执行时自动获得控制论增强
result = wrapped_crew.kickoff()
```

### Hermes Agent (HermesAdapter)

```python
from cybernetics_agent.adapters import HermesAdapter

adapter = HermesAdapter(ctx)

# 拦截 Hermes 的工具调用
adapter.hook_tools()

# 之后所有 Hermes tool 调用自动获得：
# - 超时控制（API 不挂等死）
# - 失败重试（网络抖动自动恢复）
# - 熔断保护（连续失败停止调用）
# - 降级策略（PDF 下载失败切 abstract-only）
# - 事件记录（Dashboard 实时可见）
```

### Claude Code CLI (ClaudeCodeAdapter)

```python
from cybernetics_agent.adapters import ClaudeCodeAdapter

adapter = ClaudeCodeAdapter(ctx)

# 包裹 Claude Code 子进程调用
result = adapter.run("claude", ["--prompt", "refactor this code"])

# 自动监控子进程状态，异常时告警
```

### OpenAI Codex CLI (CodexAdapter)

```python
from cybernetics_agent.adapters import CodexAdapter

adapter = CodexAdapter(ctx)
result = adapter.run("codex", ["--files", "src/"])
```

---

## 异步适配器（v0.6.4+）

对于异步框架（如 asyncio、FastAPI、aiohttp），使用 `AsyncCyberneticsContext` 和 `AsyncEventBus`：

```python
import asyncio
from cybernetics_agent import CyberneticsConfig
from cybernetics_agent.runtime.async_context import AsyncCyberneticsContext

cfg = CyberneticsConfig(project_name="async-agent")

async def main():
    async with AsyncCyberneticsContext(cfg) as ctx:
        # 异步工具调用自动被包裹
        result = await ctx.emit_tool_call("search_api", {"query": "AI"})
        # 重试、熔断、降级在异步环境下同样生效

asyncio.run(main())
```

所有同步适配器都有对应的异步版本，使用方式相同：

```python
from cybernetics_agent.adapters import AsyncNativeAdapter

async with AsyncCyberneticsContext(cfg) as ctx:
    adapter = AsyncNativeAdapter(ctx)

    @adapter.wrap("async_search")
    async def search(query: str):
        return await aiohttp.get(f"https://api.example.com/search?q={query}")

    results = await search("machine learning")
```

---

## 自定义适配器

如果现有适配器不满足需求，可以继承 `BaseAdapter` 自定义：

```python
from cybernetics_agent.adapters import BaseAdapter

class MyFrameworkAdapter(BaseAdapter):
    def __init__(self, ctx):
        super().__init__(ctx)

    def wrap_tool(self, tool_func):
        """包装单个工具函数"""
        @functools.wraps(tool_func)
        def wrapper(*args, **kwargs):
            self._ctx.emit_tool_call(tool_func.__name__, args)
            try:
                result = tool_func(*args, **kwargs)
                self._ctx.emit_tool_result(tool_func.__name__, result)
                return result
            except Exception as e:
                self._ctx.emit_tool_error(tool_func.__name__, e)
                raise
        return wrapper
```

---

## Dogfooding 示例

实际生产中的接入案例：[Hermes Agent 文献检索 Pipeline](../scripts/dogfood_cybernetics.py)

```python
class CyberneticsPipeline:
    def __init__(self, output_dir: Path = None):
        self.searcher = SearchOrchestrator(...)
        self.downloader = DownloadManager(...)

    @with_cybernetics_retry("stage0_search", max_retries=3)
    async def search_papers(self, query: str, max_results: int = 10):
        return await self.searcher.search(query, max_results=max_results)

    @with_cybernetics_retry("stage0_download", max_retries=2)
    async def download_pdfs(self, papers: list):
        # 下载失败 → 自动降级到 abstract-only
        ...
```
