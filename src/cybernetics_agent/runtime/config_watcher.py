"""
配置热重载。

轮询配置文件修改时间，变化时自动重新加载。
零外部依赖，仅使用标准库。
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Callable


class ConfigWatcher:
    """
    配置热重载监听器。

    使用轮询方式检测文件修改，不依赖 watchdog 等外部库。
    """

    def __init__(
        self,
        path: str,
        callback: Callable[[], None],
        interval: float = 5.0,
    ) -> None:
        self.path = path
        self.callback = callback
        self.interval = interval
        self._last_mtime: float | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """启动轮询线程。"""
        if self._running:
            return
        self._running = True
        self._last_mtime = self._get_mtime()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止轮询线程。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.interval + 1.0)
            self._thread = None

    def _get_mtime(self) -> float | None:
        """获取文件修改时间。"""
        try:
            return os.path.getmtime(self.path)
        except OSError:
            return None

    def _loop(self) -> None:
        """轮询循环。"""
        while self._running:
            time.sleep(self.interval)
            if not self._running:
                break
            current = self._get_mtime()
            if current is not None and self._last_mtime is not None and current != self._last_mtime:
                self._last_mtime = current
                try:
                    self.callback()
                except Exception:
                    pass
            elif current is not None and self._last_mtime is None:
                self._last_mtime = current
