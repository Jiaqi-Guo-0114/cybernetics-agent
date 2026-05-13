"""
Qwenpaw 适配器。

适配 Qwenpaw Agent 框架。
支持 HTTP API 和本地进程调用两种模式。

使用示例:
    >>> from cybernetics_agent.adapters import QwenpawAdapter
    >>> adapter = QwenpawAdapter(ctx, mode="http", base_url="http://localhost:8000")
    >>> adapter.install(None)
    >>> response = adapter.chat("你好")
"""

from __future__ import annotations

import contextlib
import json
import subprocess
from typing import Any
from urllib.request import Request, urlopen

from .base import BaseAdapter


class QwenpawAdapter(BaseAdapter):
    """Qwenpaw Agent 适配器。"""

    def __init__(
        self,
        ctx: Any,
        mode: str = "http",
        base_url: str = "http://localhost:8000",
        cli_path: str = "qwenpaw",
        api_key: str | None = None,
    ) -> None:
        super().__init__(ctx)
        self.mode = mode
        self.base_url = base_url.rstrip("/")
        self.cli_path = cli_path
        self.api_key = api_key

    def install(self, target: Any) -> None:
        """检查 Qwenpaw 是否可用。"""
        if self.mode == "http":
            with contextlib.suppress(Exception):
                req = Request(f"{self.base_url}/health", method="GET")
                with urlopen(req, timeout=5):
                    pass
        else:
            with contextlib.suppress(FileNotFoundError, subprocess.CalledProcessError):
                subprocess.run([self.cli_path, "--version"], capture_output=True, check=True)
        self._installed = True

    def _http_request(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """HTTP 模式请求。"""
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        with urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _cli_run(self, prompt: str, args: list[str] | None = None) -> str:
        """CLI 模式执行。"""
        cmd: list[str] = [self.cli_path, prompt]
        if args:
            cmd.extend(args)

        self.emit(self._event_type("AGENT_START"), {"task": "qwenpaw", "prompt": prompt[:200]})

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        success = result.returncode == 0

        self.emit(self._event_type("AGENT_END"), {
            "task": "qwenpaw",
            "status": "success" if success else "failed",
            "output_length": len(result.stdout),
        })

        if not success and result.stderr:
            self.emit(self._event_type("ERROR"), {"task": "qwenpaw", "error": result.stderr[:500]})

        return result.stdout

    def chat(self, message: str, session_id: str | None = None) -> str:
        """发送消息并获取响应。"""
        if self.mode == "http":
            self.emit(self._event_type("AGENT_START"), {"task": "qwenpaw_chat", "message": message[:200]})
            try:
                payload = {"message": message}
                if session_id:
                    payload["session_id"] = session_id
                result = self._http_request("/chat", payload)
                reply = result.get("reply", result.get("response", str(result)))
                self.emit(self._event_type("AGENT_END"), {"task": "qwenpaw_chat", "status": "success"})
                return reply
            except Exception as e:
                self.emit(self._event_type("ERROR"), {"task": "qwenpaw_chat", "error": str(e)})
                raise
        else:
            return self._cli_run(message)

    def run_with_files(self, prompt: str, files: list[str]) -> str:
        """传入文件上下文后运行。"""
        if self.mode == "cli":
            file_args = []
            for f in files:
                file_args.extend(["--file", f])
            return self._cli_run(prompt, file_args)
        else:
            self.emit(self._event_type("TOOL_CALL"), {"tool_name": "qwenpaw_files", "files": files})
            payload = {"message": prompt, "files": files}
            result = self._http_request("/chat", payload)
            return result.get("reply", str(result))
