import pytest
import sys
import unittest.mock as mock

sys.modules['lib.system.window_manager'] = mock.MagicMock()
sys.modules['lib.vision.vision_engine'] = mock.MagicMock()

from app_gui import App

def test_canonical_roundtrip(mocker):
    app = App()

    app.monster_rotation_list = [
        {"monster_id": 1, "name": "Monster 1", "priority": 1, "dungeon_id": None},
        {"monster_id": 2, "name": "Monster 2", "priority": 2, "dungeon_id": None},
        {"monster_id": 3, "name": "Monster 3", "priority": 3, "dungeon_id": None}
    ]

    # Reorder
    app.monster_rotation_list[0], app.monster_rotation_list[1] = app.monster_rotation_list[1], app.monster_rotation_list[0]
    for i, m in enumerate(app.monster_rotation_list):
        m["priority"] = i + 1

    app._perform_save()

    cfg = app.hunt_cfg
    assert len(cfg["monster_rotation"]) == 3
    assert cfg["monster_rotation"][0]["monster_id"] == 2
    assert cfg["monster_rotation"][0]["priority"] == 1
    assert cfg["monster_rotation"][1]["monster_id"] == 1
    assert cfg["monster_rotation"][1]["priority"] == 2

def test_dirty_state_no_save_before_apply(mocker):
    app = App()
    app._schedule_save = mocker.MagicMock()

    app.monster_rotation_list = [
        {"monster_id": 1, "name": "Monster 1", "priority": 1, "dungeon_id": None},
        {"monster_id": 2, "name": "Monster 2", "priority": 2, "dungeon_id": None}
    ]

    app.monster_rotation_listbox = mocker.MagicMock()
    app.monster_rotation_listbox.curselection.return_value = [0]
    app.monster_rotation_listbox.size.return_value = 2

    app._on_monster_delete_from_list()

    assert len(app.monster_rotation_list) == 1
    assert app.monster_rotation_list[0]["monster_id"] == 2
    assert app.monster_rotation_list[0]["priority"] == 1

    app._schedule_save.assert_called()
