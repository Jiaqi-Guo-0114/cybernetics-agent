"""
状态管理器。

负责跨会话状态的持久化和检索。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..config import StorageConfig
    from ..core.base import CyberneticsEvent


class StateManager:
    """
    状态管理器。

    支持多种存储后端（memory / jsonl / sqlite），
    负责持久化事件和跨会话状态。

    使用示例:
        >>> manager = StateManager(config.storage)
        >>> manager.save_event(event)
        >>> events = manager.load_events(session_id="sess_001")
    """

    def __init__(self, config: "StorageConfig") -> None:
        self.config = config
        self._backend = config.backend
        self._path = Path(config.path)
        self._memory: List[Dict[str, Any]] = []
        self._closed = False

        if self._backend in ("jsonl", "sqlite"):
            self._path.mkdir(parents=True, exist_ok=True)

    def save_event(self, event: "CyberneticsEvent") -> None:
        """
        保存事件到存储。

        根据配置的 backend 选择存储方式。
        """
        if self._closed:
            return

        record = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp,
            "session_id": event.session_id,
            "payload": event.payload,
            "metadata": event.metadata,
        }

        if self._backend == "memory":
            self._memory.append(record)
        elif self._backend == "jsonl":
            self._append_jsonl(record)
        elif self._backend == "sqlite":
            self._insert_sqlite(record)

    def _append_jsonl(self, record: Dict[str, Any]) -> None:
        """追加写入 JSONL 文件。"""
        filepath = self._path / "events.jsonl"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _insert_sqlite(self, record: Dict[str, Any]) -> None:
        """插入 SQLite 数据库。"""
        import sqlite3

        db_path = self._path / "events.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT,
                timestamp REAL,
                session_id TEXT,
                payload TEXT,
                metadata TEXT
            )
        """)

        cursor.execute(
            "INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?)",
            (
                record["event_id"],
                record["event_type"],
                record["timestamp"],
                record["session_id"],
                json.dumps(record["payload"]),
                json.dumps(record["metadata"]),
            ),
        )
        conn.commit()
        conn.close()

    def load_events(
        self,
        session_id: Optional[str] = None,
        event_type: Optional[str] = None,
        since: Optional[float] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        加载历史事件。

        参数:
            session_id: 按 session 过滤
            event_type: 按事件类型过滤
            since: 按时间戳过滤（大于等于）
            limit: 最大返回数量
        """
        if self._backend == "memory":
            events = list(self._memory)
        elif self._backend == "jsonl":
            events = self._load_jsonl_events()
        elif self._backend == "sqlite":
            events = self._load_sqlite_events()
        else:
            events = []

        # 应用过滤条件
        if session_id:
            events = [e for e in events if e.get("session_id") == session_id]
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        if since is not None:
            events = [e for e in events if e.get("timestamp", 0) >= since]

        # 按时间排序，取最近的
        events.sort(key=lambda e: e.get("timestamp", 0), reverse=True)
        return events[:limit]

    def _load_jsonl_events(self) -> List[Dict[str, Any]]:
        """加载 JSONL 文件中的所有事件。"""
        filepath = self._path / "events.jsonl"
        if not filepath.exists():
            return []

        events = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events

    def _load_sqlite_events(self) -> List[Dict[str, Any]]:
        """加载 SQLite 数据库中的所有事件。"""
        import sqlite3

        db_path = self._path / "events.db"
        if not db_path.exists():
            return []

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")

        events = []
        for row in cursor.fetchall():
            events.append({
                "event_id": row[0],
                "event_type": row[1],
                "timestamp": row[2],
                "session_id": row[3],
                "payload": json.loads(row[4]),
                "metadata": json.loads(row[5]),
            })
        conn.close()
        return events

    def get_session_count(self) -> int:
        """获取唯一 session 数量。"""
        events = self.load_events(limit=10000)
        return len(set(e.get("session_id") for e in events if e.get("session_id")))

    def close(self) -> None:
        """关闭状态管理器。"""
        self._closed = True


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    import tempfile
    sys.path.insert(0, str(__file__).rsplit("/runtime", 1)[0])
    from core.base import CyberneticsEvent, EventType
    from config import StorageConfig

    # 测试 1: Memory 后端
    mem_config = StorageConfig(backend="memory")
    mem_mgr = StateManager(mem_config)

    evt = CyberneticsEvent.create(EventType.TOOL_CALL, "sess_001", {"tool": "search"})
    mem_mgr.save_event(evt)

    events = mem_mgr.load_events(session_id="sess_001")
    assert len(events) == 1
    assert events[0]["event_type"] == "tool_call"
    print("  ✅ 测试 1 通过：Memory 后端")

    # 测试 2: JSONL 后端
    with tempfile.TemporaryDirectory() as tmpdir:
        jsonl_config = StorageConfig(backend="jsonl", path=tmpdir)
        jsonl_mgr = StateManager(jsonl_config)

        evt2 = CyberneticsEvent.create(EventType.TOOL_RESULT, "sess_002", {"result": "ok"})
        jsonl_mgr.save_event(evt2)

        events2 = jsonl_mgr.load_events(session_id="sess_002")
        assert len(events2) == 1
        assert events2[0]["payload"]["result"] == "ok"
        print("  ✅ 测试 2 通过：JSONL 后端")

        jsonl_mgr.close()

    # 测试 3: SQLite 后端
    with tempfile.TemporaryDirectory() as tmpdir:
        sqlite_config = StorageConfig(backend="sqlite", path=tmpdir)
        sqlite_mgr = StateManager(sqlite_config)

        evt3 = CyberneticsEvent.create(EventType.ERROR, "sess_003", {"msg": "fail"})
        sqlite_mgr.save_event(evt3)

        events3 = sqlite_mgr.load_events(event_type="error")
        assert len(events3) == 1
        assert events3[0]["payload"]["msg"] == "fail"
        print("  ✅ 测试 3 通过：SQLite 后端")

        sqlite_mgr.close()

    print("\n  ✅ 状态管理器所有冒烟测试通过！")
