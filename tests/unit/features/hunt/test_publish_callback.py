import pytest
from unittest.mock import MagicMock, patch
from lib.features.hunt.runtime_monster_queue import RuntimeMonsterQueue

class TestPublishCallback:
    def test_publish_callback_scheduled(self):
        """Verify publish callback is scheduled via maybe_publish correctly."""
        callback = MagicMock()
        ui_scheduler = MagicMock()

        queue = RuntimeMonsterQueue(on_publish=callback)

        queue.add_or_update(
            monster_id=10,
            name="Test Mob",
            bbox=(0, 0, 10, 10),
            confidence=0.99,
            template_id="tmpl",
            resolution_state="db_match",
            dungeon_id=None
        )

        # Publish
        queue.maybe_publish(ui_scheduler)

        # ui_scheduler should be called to schedule callback to main thread
        ui_scheduler.assert_called_once()
        args, kwargs = ui_scheduler.call_args
        func = args[0]
        # execute the scheduled func
        func()

        callback.assert_called_once()
