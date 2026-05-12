"""
Claude Code 适配器。

封装 Claude Code CLI (`claude`) 的调用，在命令执行前后采集事件。

使用示例:
    >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
    >>> from cybernetics_agent.adapters import ClaudeCodeAdapter
    >>> ctx = CyberneticsContext(CyberneticsConfig())
    >>> adapter = ClaudeCodeAdapter(ctx)
    >>> adapter.install(None)
    >>> result = adapter.run("写一个 Python 函数")
"""

from __future__ import annotations

import subprocess
from typing import Any, List, Optional

from .base import BaseAdapter


class ClaudeCodeAdapter(BaseAdapter):
    """Claude Code CLI 适配器。"""

    def __init__(self, ctx: Any, cli_path: str = "claude") -> None:
        super().__init__(ctx)
        self.cli_path = cli_path

    def install(self, target: Any) -> None:
        """检查 Claude Code 是否可用。"""
        try:
            subprocess.run([self.cli_path, "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass  # 允许未安装，适配器仍可创建
        self._installed = True

    def run(
        self,
        prompt: str,
        approval_mode: Optional[str] = None,
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
    ) -> str:
        """
        执行 Claude Code 并采集事件。

        参数:
            prompt: 给 Claude 的提示词
            approval_mode: 审批模式 (auto-read-only / auto-edit / ask)
            cwd: 工作目录
            env: 环境变量

        返回:
            Claude 的输出文本
        """
        cmd: List[str] = [self.cli_path]
        if approval_mode:
            cmd.extend(["--approval-mode", approval_mode])
        cmd.extend(["-p", prompt])

        self.emit(self._event_type("AGENT_START"), {"task": "claude_code", "prompt": prompt[:200]})

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                env={**dict(subprocess.os.environ), **(env or {})},
                timeout=600,
            )
            stdout = result.stdout
            stderr = result.stderr

            success = result.returncode == 0
            self.emit(self._event_type("AGENT_END"), {
                "task": "claude_code",
                "status": "success" if success else "failed",
                "exit_code": result.returncode,
                "output_length": len(stdout),
            })

            if not success and stderr:
                self.emit(self._event_type("ERROR"), {
                    "task": "claude_code",
                    "error": stderr[:500],
                })

            return stdout
        except subprocess.TimeoutExpired:
            self.emit(self._event_type("ERROR"), {
                "task": "claude_code",
                "error": "timeout after 600s",
            })
            raise

    def run_with_files(
        self,
        prompt: str,
        files: List[str],
        approval_mode: Optional[str] = None,
    ) -> str:
        """传入文件上下文后运行 Claude Code。"""
        file_context = "\n".join(f"@ {f}" for f in files)
        full_prompt = f"{file_context}\n\n{prompt}" if file_context else prompt
        return self.run(full_prompt, approval_mode=approval_mode)
