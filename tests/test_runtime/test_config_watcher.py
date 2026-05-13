"""
ConfigWatcher 测试。
"""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cybernetics_agent.runtime.config_watcher import ConfigWatcher


def test_watcher_detects_change():
    """Watcher 能检测到文件修改。"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"a": 1}')
        path = f.name

    try:
        triggered = []

        def callback():
            triggered.append(True)

        watcher = ConfigWatcher(path, callback, interval=0.5)
        watcher.start()

        # 等待一次检测
        time.sleep(0.7)

        # 修改文件
        with open(path, "w") as f:
            f.write('{"a": 2}')

        # 等待检测到变化
        time.sleep(0.7)

        watcher.stop()

        assert len(triggered) >= 1
    finally:
        os.unlink(path)


def test_watcher_no_false_positive():
    """未修改时不应触发。"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"a": 1}')
        path = f.name

    try:
        triggered = []

        def callback():
            triggered.append(True)

        watcher = ConfigWatcher(path, callback, interval=0.3)
        watcher.start()

        time.sleep(1.0)

        watcher.stop()

        # 未修改文件，不应触发
        assert len(triggered) == 0
    finally:
        os.unlink(path)


def test_watcher_start_stop_idempotent():
    """启动/停止幂等。"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"a": 1}')
        path = f.name

    try:
        watcher = ConfigWatcher(path, lambda: None, interval=1.0)
        watcher.start()
        watcher.start()  # 二次启动不应报错
        watcher.stop()
        watcher.stop()  # 二次停止不应报错
        assert True
    finally:
        os.unlink(path)
