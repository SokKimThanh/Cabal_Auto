import pytest
import time
from lib.features.hunt.runtime_monster_queue import RuntimeMonsterQueue

pytestmark = pytest.mark.integration


def test_runtime_monster_queue_deduplication():
    queue = RuntimeMonsterQueue(capacity=50, ttl_sec=1.0)

    # Add monster
    queue.add_or_update(
        monster_id=1,
        name="Slime",
        bbox=(100, 100, 50, 50),
        confidence=0.9,
        template_id="tmpl_1",
        resolution_state="db_match"
    )
    assert len(queue.get_snapshot()) == 1

    # Add same monster nearby (should deduplicate)
    queue.add_or_update(
        monster_id=1,
        name="Slime",
        bbox=(105, 105, 50, 50),
        confidence=0.95,
        template_id="tmpl_1",
        resolution_state="db_match"
    )
    snap = queue.get_snapshot()
    assert len(snap) == 1
    assert snap[0]["confidence"] == 0.95
    assert snap[0]["bbox"] == (105, 105, 50, 50)

    # Add same monster far away (should not deduplicate)
    queue.add_or_update(
        monster_id=1,
        name="Slime",
        bbox=(500, 500, 50, 50),
        confidence=0.8,
        template_id="tmpl_1",
        resolution_state="db_match"
    )
    assert len(queue.get_snapshot()) == 2

def test_runtime_monster_queue_ttl():
    queue = RuntimeMonsterQueue(capacity=50, ttl_sec=0.1)
    queue.add_or_update(
        monster_id=1,
        name="Slime",
        bbox=(100, 100, 50, 50),
        confidence=0.9,
        template_id="tmpl_1",
        resolution_state="db_match"
    )

    assert len(queue.get_snapshot()) == 1
    time.sleep(0.15)
    assert len(queue.get_snapshot()) == 0

def test_runtime_monster_queue_capacity():
    queue = RuntimeMonsterQueue(capacity=2, ttl_sec=10.0)
    queue.add_or_update(1, "A", (10, 10, 10, 10), 0.5, "t", "db_match")
    queue.add_or_update(2, "B", (20, 20, 10, 10), 0.9, "t", "db_match")

    # Add third item, should drop the lowest confidence (A: 0.5)
    queue.add_or_update(3, "C", (30, 30, 10, 10), 0.7, "t", "db_match")

    snap = queue.get_snapshot()
    assert len(snap) == 2
    monster_ids = [s["monster_id"] for s in snap]
    assert 2 in monster_ids
    assert 3 in monster_ids
    assert 1 not in monster_ids

def test_runtime_monster_queue_attack_queue_policies():
    queue = RuntimeMonsterQueue(capacity=50, ttl_sec=10.0)
    queue.add_or_update(1, "MatchedConfigured", (10, 10, 10, 10), 0.9, "t", "db_match")
    queue.add_or_update(2, "MatchedNotConfigured", (20, 20, 10, 10), 0.8, "t", "db_match")
    queue.add_or_update(0, "Unknown", (30, 30, 10, 10), 0.9, "t", "unmapped_visual")
    queue.add_or_update(3, "DBMiss", (40, 40, 10, 10), 0.9, "t", "db_miss")

    # Policy: configured_only
    q_conf = queue.get_attack_queue("configured_only", [1])
    assert len(q_conf) == 1
    assert q_conf[0]["monster_id"] == 1

    # Policy: all_resolved
    q_all = queue.get_attack_queue("all_resolved", [1])
    assert len(q_all) == 2
    ids = [q["monster_id"] for q in q_all]
    assert 1 in ids
    assert 2 in ids
    assert 0 not in ids
    assert 3 not in ids

    # Policy: any_target (should return empty or be unused for DB matching logic)
    q_any = queue.get_attack_queue("any_target", [1])
    assert len(q_any) == 0

def test_runtime_monster_queue_immutability():
    queue = RuntimeMonsterQueue(capacity=50, ttl_sec=10.0)
    queue.add_or_update(1, "Slime", (10, 10, 10, 10), 0.9, "t", "db_match")
    snap1 = queue.get_snapshot()

    # Mutate state in queue by updating the same monster
    queue.add_or_update(1, "Slime", (20, 20, 20, 20), 0.95, "t", "db_match")

    assert isinstance(snap1, tuple)
    assert snap1[0]["bbox"] == (10, 10, 10, 10) # Should remain unchanged
