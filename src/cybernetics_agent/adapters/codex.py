"""
Codex 适配器。

封装 OpenAI Codex CLI (`codex`) 的调用，在命令执行前后采集事件。

使用示例:
    >>> from cybernetics_agent.adapters import CodexAdapter
    >>> adapter = CodexAdapter(ctx)
    >>> adapter.install(None)
    >>> result = adapter.run("写一个单元测试")
"""

from __future__ import annotations

import subprocess
from typing import Any, List, Optional

from .base import BaseAdapter


class CodexAdapter(BaseAdapter):
    """OpenAI Codex CLI 适配器。"""

    def __init__(self, ctx: Any, cli_path: str = "codex") -> None:
        super().__init__(ctx)
        self.cli_path = cli_path

    def install(self, target: Any) -> None:
        """检查 Codex 是否可用。"""
        try:
            subprocess.run([self.cli_path, "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        self._installed = True

    def run(
        self,
        prompt: str,
        approval_mode: Optional[str] = None,
        model: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> str:
        """
        执行 Codex 并采集事件。

        参数:
            prompt: 给 Codex 的提示词
            approval_mode: 审批模式 (auto-edit / suggest / full-auto)
            model: 模型名称
            cwd: 工作目录

        返回:
            Codex 的输出文本
        """
        cmd: List[str] = [self.cli_path, "-q", prompt]
        if approval_mode:
            cmd.extend(["--approval-mode", approval_mode])
        if model:
            cmd.extend(["--model", model])

        self.emit(self._event_type("AGENT_START"), {"task": "codex", "prompt": prompt[:200]})

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=600,
            )
            stdout = result.stdout
            success = result.returncode == 0

            self.emit(self._event_type("AGENT_END"), {
                "task": "codex",
                "status": "success" if success else "failed",
                "exit_code": result.returncode,
                "output_length": len(stdout),
            })

            if not success and result.stderr:
                self.emit(self._event_type("ERROR"), {
                    "task": "codex",
                    "error": result.stderr[:500],
                })

            return stdout
        except subprocess.TimeoutExpired:
            self.emit(self._event_type("ERROR"), {"task": "codex", "error": "timeout after 600s"})
            raise

    def review(self, file_path: str) -> str:
        """让 Codex 审查指定文件。"""
        prompt = f"Review the code in {file_path} and suggest improvements."
        return self.run(prompt)
