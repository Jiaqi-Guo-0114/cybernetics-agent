"""EventStore 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.runtime.event_store import EventStore


class TestEventStoreExtra:
    def test_close(self, tmp_path):
        db = str(tmp_path / "store.db")
        store = EventStore(db)
        store.write_event("e", {})
        store.close()
        assert store._conn is None
