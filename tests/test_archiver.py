"""
EventArchiver 测试。
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent.runtime.archiver import EventArchiver
from cybernetics_agent.runtime.event_store import EventStore


def test_archive_and_restore():
    """归档和恢复事件。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EventStore(str(Path(tmpdir) / "test.db"))
        archiver = EventArchiver(archive_dir=str(Path(tmpdir) / "archives"))

        # 写入旧事件（31天前）
        old_time = time.time() - 31 * 86400
        store._conn.execute(
            "INSERT INTO events (timestamp, event_type, payload) VALUES (?, ?, ?)",
            (old_time, "test", '{"msg": "old"}'),
        )
        store._conn.commit()

        # 归档
        count = archiver.archive(store, older_than_days=30, compress=False)
        assert count == 1

        # 恢复
        restored = archiver.restore()
        assert len(restored) == 1
        assert restored[0]["payload"]["msg"] == "old"


def test_archive_with_compression():
    """带压缩的归档。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EventStore(str(Path(tmpdir) / "test.db"))
        archiver = EventArchiver(archive_dir=str(Path(tmpdir) / "archives"))

        old_time = time.time() - 31 * 86400
        store._conn.execute(
            "INSERT INTO events (timestamp, event_type, payload) VALUES (?, ?, ?)",
            (old_time, "test", '{"msg": "compressed"}'),
        )
        store._conn.commit()

        count = archiver.archive(store, older_than_days=30, compress=True)
        assert count == 1

        # 验证文件是 .gz
        archives = archiver.list_archives()
        assert len(archives) == 1
        assert archives[0]["compressed"] is True

        restored = archiver.restore()
        assert len(restored) == 1
        assert restored[0]["payload"]["msg"] == "compressed"


def test_archive_no_old_events():
    """没有旧事件时不应归档。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EventStore(str(Path(tmpdir) / "test.db"))
        archiver = EventArchiver(archive_dir=str(Path(tmpdir) / "archives"))

        # 写入新事件
        store.write_event("test", {"msg": "new"})

        count = archiver.archive(store, older_than_days=30)
        assert count == 0


def test_archive_delete_after():
    """归档后删除。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EventStore(str(Path(tmpdir) / "test.db"))
        archiver = EventArchiver(archive_dir=str(Path(tmpdir) / "archives"))

        old_time = time.time() - 31 * 86400
        store._conn.execute(
            "INSERT INTO events (timestamp, event_type, payload) VALUES (?, ?, ?)",
            (old_time, "test", '{"msg": "delete_me"}'),
        )
        store._conn.commit()

        count = archiver.archive(store, older_than_days=30, delete_after_archive=True)
        assert count == 1

        # 验证已删除
        events = store.query_events(limit=100)
        assert len(events) == 0


def test_list_archives():
    """列出归档。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EventStore(str(Path(tmpdir) / "test.db"))
        archiver = EventArchiver(archive_dir=str(Path(tmpdir) / "archives"))

        old_time = time.time() - 31 * 86400
        store._conn.execute(
            "INSERT INTO events (timestamp, event_type, payload) VALUES (?, ?, ?)",
            (old_time, "test", '{"msg": ""}'),
        )
        store._conn.commit()

        archiver.archive(store, older_than_days=30, compress=True)
        archives = archiver.list_archives()
        assert len(archives) == 1
        assert archives[0]["day"]  # 应该有日期
        assert archives[0]["size_bytes"] > 0


def test_cleanup_local():
    """清理本地过期归档。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        archiver = EventArchiver(archive_dir=str(Path(tmpdir) / "archives"))

        # 创建一个旧文件（100天前）
        old_file = Path(tmpdir) / "archives" / "events_2020-01-01.jsonl.gz"
        old_file.parent.mkdir(parents=True, exist_ok=True)
        old_file.write_text("")
        # 修改文件时间为 100 天前
        os = __import__("os")
        old_mtime = time.time() - 100 * 86400
        os.utime(old_file, (old_mtime, old_mtime))

        deleted = archiver.cleanup_local(older_than_days=90)
        assert deleted == 1
        assert not old_file.exists()


def test_s3_not_available():
    """S3 未配置时应该正常工作。"""
    archiver = EventArchiver(s3_bucket=None)
    assert not archiver.s3_available


def test_restore_by_day():
    """按天恢复。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EventStore(str(Path(tmpdir) / "test.db"))
        archiver = EventArchiver(archive_dir=str(Path(tmpdir) / "archives"))

        old_time = time.time() - 31 * 86400
        day_str = time.strftime("%Y-%m-%d", time.localtime(old_time))
        store._conn.execute(
            "INSERT INTO events (timestamp, event_type, payload) VALUES (?, ?, ?)",
            (old_time, "test", '{"msg": "specific_day"}'),
        )
        store._conn.commit()

        archiver.archive(store, older_than_days=30, compress=False)
        restored = archiver.restore(day=day_str)
        assert len(restored) == 1
