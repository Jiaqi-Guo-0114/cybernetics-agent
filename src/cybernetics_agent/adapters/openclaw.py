"""
OpenClaw 适配器。

适配 OpenClaw Agent 框架，通过 HTTP API 交互采集事件。

使用示例:
    >>> from cybernetics_agent.adapters import OpenClawAdapter
    >>> adapter = OpenClawAdapter(ctx, base_url="http://localhost:8080")
    >>> adapter.install(None)
    >>> response = adapter.chat("你好")
"""

from __future__ import annotations

import contextlib
import json
from typing import Any
from urllib.request import Request, urlopen

from .base import BaseAdapter


class OpenClawAdapter(BaseAdapter):
    """OpenClaw Agent HTTP 适配器。"""

    def __init__(
        self,
        ctx: Any,
        base_url: str = "http://localhost:8080",
        api_key: str | None = None,
    ) -> None:
        super().__init__(ctx)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def install(self, target: Any) -> None:
        """检查 OpenClaw 服务是否可达。"""
        with contextlib.suppress(Exception):
            self._health_check()  # 允许未启动
        self._installed = True

    def _health_check(self) -> bool:
        """健康检查。"""
        req = Request(f"{self.base_url}/health", method="GET")
        with urlopen(req, timeout=5) as resp:
            return resp.status == 200

    def _request(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """发送 HTTP 请求。"""
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")

        with urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def chat(self, message: str, session_id: str | None = None) -> str:
        """
        发送消息到 OpenClaw 并获取响应。

        参数:
            message: 用户消息
            session_id: 会话 ID（可选）

        返回:
            OpenClaw 的响应文本
        """
        self.emit(self._event_type("AGENT_START"), {"task": "openclaw_chat", "message": message[:200]})

        try:
            payload = {"message": message}
            if session_id:
                payload["session_id"] = session_id

            result = self._request("/chat", payload)
            reply = result.get("reply", result.get("response", str(result)))

            self.emit(self._event_type("AGENT_END"), {
                "task": "openclaw_chat",
                "status": "success",
                "reply_length": len(reply),
            })
            return reply
        except Exception as e:
            self.emit(self._event_type("ERROR"), {
                "task": "openclaw_chat",
                "error": str(e),
            })
            raise

    def send_tool_result(
        self,
        tool_name: str,
        result: Any,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """发送工具结果到 OpenClaw。"""
        self.emit(self._event_type("TOOL_RESULT"), {"tool_name": tool_name})
        payload = {"tool_name": tool_name, "result": result}
        if session_id:
            payload["session_id"] = session_id
        return self._request("/tool_result", payload)
