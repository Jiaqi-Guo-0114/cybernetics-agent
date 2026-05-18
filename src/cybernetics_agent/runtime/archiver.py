"""
数据归档与压缩。

支持将 EventStore 中的冷数据压缩存档到本地或 S3。

安装 boto3 后支持 S3 上传：
    pip install boto3

使用示例：
    >>> archiver = EventArchiver("./archives")
    >>> archived = archiver.archive(
    ...     event_store=store,
    ...     older_than_days=30,
    ...     compress=True,
    ... )
    >>> print(f"归档了 {archived} 条事件")
"""

from __future__ import annotations

import gzip
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .event_store import EventStore


try:
    import boto3
    HAS_BOTO3 = True
except ImportError:  # pragma: no cover
    HAS_BOTO3 = False


class EventArchiver:
    """
    事件数据归档器。

    支持本地文件系统和 S3 存储后端。
    """

    def __init__(
        self,
        archive_dir: str = "./archives",
        s3_bucket: str | None = None,
        s3_prefix: str = "cybernetics/events",
        s3_region: str = "us-east-1",
    ) -> None:
        """
        初始化归档器。

        参数:
            archive_dir: 本地归档目录
            s3_bucket: S3 桶名称（可选）
            s3_prefix: S3 对象前缀
            s3_region: S3 区域
        """
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.s3_region = s3_region
        self._s3_client: Any = None

    @property
    def s3_available(self) -> bool:
        """S3 是否可用。"""
        return HAS_BOTO3 and self.s3_bucket is not None

    def _get_s3_client(self) -> Any:
        """获取 S3 客户端（懒加载）。"""
        if self._s3_client is None and self.s3_available:
            self._s3_client = boto3.client("s3", region_name=self.s3_region)
        return self._s3_client

    def archive(
        self,
        event_store: EventStore,
        older_than_days: int = 30,
        compress: bool = True,
        delete_after_archive: bool = False,
    ) -> int:
        """
        将冷数据归档到本地或 S3。

        参数:
            event_store: 事件存储
            older_than_days: 归档 N 天之前的数据
            compress: 是否使用 gzip 压缩
            delete_after_archive: 归档后是否从 EventStore 删除

        返回:
            归档的事件数量
        """
        cutoff = time.time() - (older_than_days * 86400)
        events = event_store.query_events(
            from_time=0,
            to_time=cutoff,
            limit=100000,
        )

        if not events:
            return 0

        # 按天分组
        daily: dict[str, list[dict]] = {}
        for evt in events:
            day = time.strftime("%Y-%m-%d", time.localtime(evt["timestamp"]))
            daily.setdefault(day, []).append(evt)

        total_archived = 0
        for day, day_events in daily.items():
            count = self._archive_day(day, day_events, compress)
            total_archived += count

        if delete_after_archive and total_archived > 0:
            self._delete_archived_events(event_store, cutoff)

        return total_archived

    def _archive_day(self, day: str, events: list[dict], compress: bool) -> int:
        """归档单天的事件。"""
        filename = f"events_{day}.jsonl"
        if compress:
            filename += ".gz"

        local_path = self.archive_dir / filename

        # 写入文件
        if compress:
            with gzip.open(local_path, "wt", encoding="utf-8") as f:
                for evt in events:
                    f.write(json.dumps(evt, ensure_ascii=False) + "\n")
        else:
            with open(local_path, "w", encoding="utf-8") as f:
                for evt in events:
                    f.write(json.dumps(evt, ensure_ascii=False) + "\n")

        # 如果配置了 S3，上传
        if self.s3_available:
            self._upload_to_s3(local_path, filename)

        return len(events)

    def _upload_to_s3(self, local_path: Path, filename: str) -> bool:
        """上传文件到 S3。"""
        try:
            s3 = self._get_s3_client()
            if s3 is None:
                return False
            key = f"{self.s3_prefix}/{filename}"
            s3.upload_file(str(local_path), self.s3_bucket, key)
            return True
        except Exception:
            return False

    def _delete_archived_events(self, event_store: EventStore, cutoff: float) -> None:
        """从 EventStore 删除已归档的事件。"""
        try:
            conn = event_store._conn
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM events WHERE timestamp < ?",
                (cutoff,),
            )
            conn.commit()
        except Exception:
            pass

    def restore(
        self,
        day: str | None = None,
        local_only: bool = True,
    ) -> list[dict]:
        """
        从归档中恢复事件。

        参数:
            day: 指定日期 (YYYY-MM-DD)。为 None 则返回所有已归档事件。
            local_only: 是否只从本地恢复

        返回:
            事件列表
        """
        results: list[dict] = []

        patterns = [f"events_{day}.jsonl*"] if day else ["events_*.jsonl*"]

        for pattern in patterns:
            for path in self.archive_dir.glob(pattern):
                events = self._read_archive_file(path)
                results.extend(events)

        return results

    def _read_archive_file(self, path: Path) -> list[dict]:
        """读取单个归档文件。"""
        events: list[dict] = []
        try:
            if str(path).endswith(".gz"):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            events.append(json.loads(line))
            else:
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            events.append(json.loads(line))
        except Exception:
            pass
        return events

    def list_archives(self) -> list[dict]:
        """列出所有本地归档。"""
        archives: list[dict] = []
        for path in self.archive_dir.glob("events_*.jsonl*"):
            stat = path.stat()
            archives.append({
                "filename": path.name,
                "day": path.name.replace("events_", "").replace(".jsonl", "").replace(".gz", ""),
                "size_bytes": stat.st_size,
                "modified": stat.st_mtime,
                "compressed": str(path).endswith(".gz"),
            })
        return sorted(archives, key=lambda x: x["day"])

    def cleanup_local(self, older_than_days: int = 90) -> int:
        """
        清理本地过期归档文件。

        返回:
            删除的文件数量
        """
        cutoff = time.time() - (older_than_days * 86400)
        deleted = 0
        for path in self.archive_dir.glob("events_*.jsonl*"):
            try:
                if path.stat().st_mtime < cutoff:
                    path.unlink()
                    deleted += 1
            except Exception:
                pass
        return deleted
