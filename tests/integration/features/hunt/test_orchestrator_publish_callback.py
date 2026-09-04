import pytest
import time
from unittest.mock import MagicMock
from lib.features.hunt.runtime_monster_queue import RuntimeMonsterQueue

pytestmark = pytest.mark.integration


def test_runtime_queue_publish_callback_rate_limit():
    callback = MagicMock()

    # Track task executions
    tasks = []
    def schedule_fn(task):
        tasks.append(task)
        task()

    queue = RuntimeMonsterQueue(capacity=50, ttl_sec=1.0, publish_callback=callback)

    # Fast loop simulating frame processing
    for _ in range(10):
        queue.add_or_update(
            monster_id=1,
            name="Slime",
            bbox=(10, 10, 10, 10),
            confidence=0.9,
            template_id="t",
            resolution_state="db_match"
        )
        queue.maybe_publish(schedule_fn)

    # Despite 10 iterations, it should only publish once immediately
    # due to the 5 FPS rate limit (1/5.0s = 200ms interval)
    assert callback.call_count == 1
    assert len(tasks) == 1

    # Wait to pass rate limit
    time.sleep(0.25)

    # Next publish should work
    queue.maybe_publish(schedule_fn)
    assert callback.call_count == 2
    assert len(tasks) == 2

    # No schedule_fn or callback should be safe
    queue_no_cb = RuntimeMonsterQueue(publish_callback=None)
    queue_no_cb.maybe_publish(schedule_fn) # should not crash

    queue.maybe_publish(None) # should not crash
