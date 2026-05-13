"""
事件持久化存储。

使用 SQLite 标准库，零外部依赖。
支持事件、指标快照、告警历史的持久化存储和查询。
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any


class EventStore:
    """
    事件持久化存储。

    使用 SQLite 存储事件、指标快照和告警历史。
    """

    def __init__(self, db_path: str | None = None) -> None:
        if db_path is None:
            db_path = str(Path.home() / ".hermes" / "cybernetics_events.db")
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _ensure_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __del__(self) -> None:
        self.close()

    def _init_db(self) -> None:
        """初始化数据库表结构。"""
        conn = self._ensure_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT,
                session_id TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                labels TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                rule_name TEXT NOT NULL,
                severity TEXT,
                message TEXT,
                metric_name TEXT,
                metric_value REAL,
                labels TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_time ON metrics(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)")
        conn.commit()

    def write_event(self, event_type: str, payload: dict[str, Any], session_id: str | None = None) -> None:
        """写入事件。"""
        with self._lock:
            conn = self._ensure_conn()
            conn.execute(
                "INSERT INTO events (timestamp, event_type, payload, session_id) VALUES (?, ?, ?, ?)",
                (time.time(), event_type, json.dumps(payload, ensure_ascii=False, default=str), session_id),
            )
            conn.commit()

    def write_metric(self, metric_name: str, metric_value: float, labels: dict[str, str] | None = None) -> None:
        """写入指标快照。"""
        with self._lock:
            conn = self._ensure_conn()
            conn.execute(
                "INSERT INTO metrics (timestamp, metric_name, metric_value, labels) VALUES (?, ?, ?, ?)",
                (time.time(), metric_name, metric_value, json.dumps(labels or {}, ensure_ascii=False)),
            )
            conn.commit()

    def write_alert(self, rule_name: str, severity: str, message: str, metric_name: str | None = None, metric_value: float | None = None, labels: dict[str, str] | None = None) -> None:
        """写入告警。"""
        with self._lock:
            conn = self._ensure_conn()
            conn.execute(
                "INSERT INTO alerts (timestamp, rule_name, severity, message, metric_name, metric_value, labels) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (time.time(), rule_name, severity, message, metric_name, metric_value, json.dumps(labels or {}, ensure_ascii=False)),
            )
            conn.commit()

    def query_events(self, from_time: float | None = None, to_time: float | None = None, event_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """查询事件。"""
        conditions = []
        params: list[Any] = []
        if from_time is not None:
            conditions.append("timestamp >= ?")
            params.append(from_time)
        if to_time is not None:
            conditions.append("timestamp <= ?")
            params.append(to_time)
        if event_type is not None:
            conditions.append("event_type = ?")
            params.append(event_type)

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"SELECT id, timestamp, event_type, payload, session_id FROM events {where} ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._lock:
            conn = self._ensure_conn()
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
            return [
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "event_type": row["event_type"],
                    "payload": json.loads(row["payload"]) if row["payload"] else {},
                    "session_id": row["session_id"],
                }
                for row in rows
            ]

    def query_metrics(self, metric_name: str | None = None, from_time: float | None = None, to_time: float | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """查询指标历史。"""
        conditions = []
        params: list[Any] = []
        if metric_name is not None:
            conditions.append("metric_name = ?")
            params.append(metric_name)
        if from_time is not None:
            conditions.append("timestamp >= ?")
            params.append(from_time)
        if to_time is not None:
            conditions.append("timestamp <= ?")
            params.append(to_time)

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"SELECT id, timestamp, metric_name, metric_value, labels FROM metrics {where} ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._lock:
            conn = self._ensure_conn()
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
            return [
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "metric_name": row["metric_name"],
                    "metric_value": row["metric_value"],
                    "labels": json.loads(row["labels"]) if row["labels"] else {},
                }
                for row in rows
            ]

    def query_alerts(self, from_time: float | None = None, to_time: float | None = None, severity: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """查询告警历史。"""
        conditions = []
        params: list[Any] = []
        if from_time is not None:
            conditions.append("timestamp >= ?")
            params.append(from_time)
        if to_time is not None:
            conditions.append("timestamp <= ?")
            params.append(to_time)
        if severity is not None:
            conditions.append("severity = ?")
            params.append(severity)

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"SELECT id, timestamp, rule_name, severity, message, metric_name, metric_value, labels FROM alerts {where} ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._lock:
            conn = self._ensure_conn()
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
            return [
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "rule_name": row["rule_name"],
                    "severity": row["severity"],
                    "message": row["message"],
                    "metric_name": row["metric_name"],
                    "metric_value": row["metric_value"],
                    "labels": json.loads(row["labels"]) if row["labels"] else {},
                }
                for row in rows
            ]

    def get_stats(self) -> dict[str, Any]:
        """获取存储统计信息。"""
        with self._lock:
            conn = self._ensure_conn()
            event_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            metric_count = conn.execute("SELECT COUNT(*) FROM metrics").fetchone()[0]
            alert_count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            return {
                "events": event_count,
                "metrics": metric_count,
                "alerts": alert_count,
                "db_path": self.db_path,
            }

    def prune(self, max_age_days: float = 30.0) -> dict[str, int]:
        """清理超过指定天数的旧数据。"""
        cutoff = time.time() - (max_age_days * 86400)
        with self._lock:
            conn = self._ensure_conn()
            c1 = conn.execute("DELETE FROM events WHERE timestamp < ?", (cutoff,)).rowcount
            c2 = conn.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff,)).rowcount
            c3 = conn.execute("DELETE FROM alerts WHERE timestamp < ?", (cutoff,)).rowcount
            conn.commit()
            return {"events": c1, "metrics": c2, "alerts": c3}
