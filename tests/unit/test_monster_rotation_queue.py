import pytest
from unittest.mock import MagicMock, patch

# Assume HuntApp is available for mocking UI controllers
from app_gui import App as HuntApp

@pytest.fixture
def mock_app():
    # Provide a minimally mocked App instance to avoid tk.Tk() GUI setup overhead
    app = MagicMock(spec=HuntApp)
    app.monster_rotation = []
    app._monster_metadata_cache = {}

    app._t = lambda key, **kwargs: key
    app.monster_rotation_listbox = MagicMock()

    app._mark_unsaved = MagicMock()

    # Recreate the target methods from App
    from app_gui import App as RealApp
    app._refresh_monster_rotation_list = RealApp._refresh_monster_rotation_list.__get__(app)
    app._on_monster_move_up = RealApp._on_monster_move_up.__get__(app)
    app._on_monster_move_down = RealApp._on_monster_move_down.__get__(app)
    app._on_monster_delete_from_list = RealApp._on_monster_delete_from_list.__get__(app)
    app._on_monster_add_smart = RealApp._on_monster_add_smart.__get__(app)
    app.current_lang = 'en'


    return app

def test_refresh_monster_rotation_list_caches_db_calls(mock_app):
    mock_app.monster_rotation = [
        {"monster_id": 1, "name": "Monster1", "priority": 1, "dungeon_id": "D1"},
        {"monster_id": 2, "name": "Monster2", "priority": 2, "dungeon_id": None}
    ]

    with patch('database.get_monster_by_id_api', side_effect=[
        {"id": 1, "level": 5, "hp": 50},
        None
    ]) as mock_by_id, \
         patch('database.find_monster_by_name_api', return_value={"id": 2, "level": 10, "hp": 200}) as mock_by_name:

        # First refresh calls DB
        mock_app._refresh_monster_rotation_list()

        assert mock_by_id.call_count == 2
        assert mock_by_name.call_count == 1

        calls = mock_app.monster_rotation_listbox.insert.call_args_list
        assert calls[0][0][1] == "[#1] Monster1 - Lv.5 | HP: 50"
        assert calls[1][0][1] == "[#2] Monster2 - Lv.10 | HP: 200"

        # Reset mocks
        mock_by_id.reset_mock()
        mock_by_name.reset_mock()

        # Second refresh should use cache
        mock_app._refresh_monster_rotation_list()

        mock_by_id.assert_not_called()
        mock_by_name.assert_not_called()


def test_refresh_handles_unknown_monsters(mock_app):
    mock_app.monster_rotation = [
        {"monster_id": 99, "name": "Missing", "priority": 1, "dungeon_id": None},
    ]

    with patch('database.get_monster_by_id_api', return_value=None), \
         patch('database.find_monster_by_name_api', return_value=None):

        mock_app._refresh_monster_rotation_list()

        mock_app.monster_rotation_listbox.insert.assert_called_with(
            "end", "[monster_rotation_unknown] Missing - Lv.-- | HP: --"
        )


def test_reorder_normalizes_priority(mock_app):
    mock_app.monster_rotation = [
        {"monster_id": 1, "name": "M1", "priority": 1, "dungeon_id": None},
        {"monster_id": 2, "name": "M2", "priority": 2, "dungeon_id": None},
        {"monster_id": 3, "name": "M3", "priority": 3, "dungeon_id": None},
    ]

    # Select index 1 (M2) and move down
    mock_app.monster_rotation_listbox.curselection.return_value = (1,)

    mock_app._on_monster_move_down()

    assert mock_app.monster_rotation[0]["name"] == "M1"
    assert mock_app.monster_rotation[1]["name"] == "M3"
    assert mock_app.monster_rotation[2]["name"] == "M2"

    # Priority should be continuous 1..3
    assert mock_app.monster_rotation[0]["priority"] == 1
    assert mock_app.monster_rotation[1]["priority"] == 2
    assert mock_app.monster_rotation[2]["priority"] == 3

    mock_app._mark_unsaved.assert_called_once()
    mock_app.monster_rotation_listbox.selection_set.assert_called_with(2)


def test_delete_normalizes_priority(mock_app):
    mock_app.monster_rotation = [
        {"monster_id": 1, "name": "M1", "priority": 1, "dungeon_id": None},
        {"monster_id": 2, "name": "M2", "priority": 2, "dungeon_id": None},
        {"monster_id": 3, "name": "M3", "priority": 3, "dungeon_id": None},
    ]

    # Select index 1 (M2) and delete
    mock_app.monster_rotation_listbox.curselection.return_value = (1,)

    mock_app._on_monster_delete_from_list()

    assert len(mock_app.monster_rotation) == 2
    assert mock_app.monster_rotation[0]["name"] == "M1"
    assert mock_app.monster_rotation[1]["name"] == "M3"

    # Priority should be continuous 1..2
    assert mock_app.monster_rotation[0]["priority"] == 1
    assert mock_app.monster_rotation[1]["priority"] == 2

    mock_app._mark_unsaved.assert_called_once()

def test_picker_integration(mock_app):
    mock_app.monster_rotation = []

    with patch('app_gui.MonsterPickerDialog') as mock_dialog:
        mock_app._on_monster_add_smart()

        # The callback is passed as the third argument to MonsterPickerDialog
        on_monster_selected = mock_dialog.call_args[0][2]

        # Simulate selecting a monster
        on_monster_selected({"monster_id": 99, "name": "PickerMonster", "dungeon_id": "D99"})

        assert len(mock_app.monster_rotation) == 1
        assert mock_app.monster_rotation[0]["monster_id"] == 99
        assert mock_app.monster_rotation[0]["name"] == "PickerMonster"
        assert mock_app.monster_rotation[0]["priority"] == 1
        assert mock_app.monster_rotation[0]["dungeon_id"] == "D99"

        mock_app._mark_unsaved.assert_called_once()
        # method bound so no assert_called
        pass


def test_dirty_state_preservation(mock_app):
    mock_app.monster_rotation = []

    with patch('app_gui.MonsterPickerDialog') as mock_dialog:
        mock_app._on_monster_add_smart()
        on_monster_selected = mock_dialog.call_args[0][2]
        on_monster_selected({"monster_id": 1, "name": "M1", "dungeon_id": None})

    # Assert _mark_unsaved was called indicating dirty state
    mock_app._mark_unsaved.assert_called_once()


def test_metadata_not_persisted(mock_app):
    # Setup state
    mock_app.monster_rotation = [
        {"monster_id": 1, "name": "M1", "priority": 1, "dungeon_id": None}
    ]

    # Simulate DB lookup fetching extra metadata (hp, level)
    with patch('database.get_monster_by_id_api', return_value={"id": 1, "level": 10, "hp": 500}):
        mock_app._refresh_monster_rotation_list()

        # Ensure that the extra metadata was not injected into the persistent dict
        entry = mock_app.monster_rotation[0]
        assert "level" not in entry
        assert "hp" not in entry
        assert list(entry.keys()) == ["monster_id", "name", "priority", "dungeon_id"]

def test_rotation_mode_boundary(mock_app):
    # Verify we only toggle UI mode and don't mutate UX3B runtime policy
    mock_app.rotation_mode_var = MagicMock()
    mock_app.rotation_mode_var.get.return_value = "Priority"
    mock_app.rotation_mode_map = {"Priority": "priority"}
    mock_app.hunt_cfg = {}
    mock_app.hunt_status = MagicMock()

    # Needs a mock for _on_rotation_mode_changed
    from app_gui import App as RealApp
    mock_app._on_rotation_mode_changed = RealApp._on_rotation_mode_changed.__get__(mock_app)

    mock_app._on_rotation_mode_changed()

    assert mock_app.hunt_cfg["rotation_mode"] == "priority"
    assert "target_policy" not in mock_app.hunt_cfg
