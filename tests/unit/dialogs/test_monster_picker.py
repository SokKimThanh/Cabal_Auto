import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from dialogs.monster_picker import MonsterPickerDialog

@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk cannot initialize in this environment: {exc}")

    root.withdraw()
    yield root
    root.destroy()

@pytest.fixture
def mock_db_responses():
    all_monsters = [
        {"id": 1, "name": "Slime Xanh", "level": 10, "hp": 100, "dungeonId": "d1"},
        {"id": 2, "name": "Slime Đo", "level": 12, "hp": 150, "dungeonId": None}
    ]
    search_monsters = [
        {"id": 1, "name": "Slime Xanh", "level": 10, "hp": 100, "dungeonId": "d1"}
    ]
    return all_monsters, search_monsters

def test_picker_initial_load(tk_root, mock_db_responses):
    all_monsters, _ = mock_db_responses
    with patch("dialogs.monster_picker.get_all_monsters_api", return_value=all_monsters) as mock_get_all:
        on_select_mock = MagicMock()
        dialog = MonsterPickerDialog(tk_root, "vi", on_select_mock, lambda key: key)

        # Verify API called
        mock_get_all.assert_called_once_with(100)

        # Check UI render
        items = dialog.tree.get_children()
        assert len(items) == 2

        # Verify text format
        text0 = dialog.tree.item(items[0], "text")
        assert text0 == "[#1] Slime Xanh - Lv.10 | HP: 100"

        text1 = dialog.tree.item(items[1], "text")
        assert text1 == "[#2] Slime Đo - Lv.12 | HP: 150"

def test_picker_search(tk_root, mock_db_responses):
    all_monsters, search_monsters = mock_db_responses
    with patch("dialogs.monster_picker.get_all_monsters_api", return_value=all_monsters):
        with patch("dialogs.monster_picker.search_monsters_api", return_value=search_monsters) as mock_search:
            dialog = MonsterPickerDialog(tk_root, "vi", MagicMock(), lambda key: key)

            # Simulate typing
            dialog.search_var.set("xanh")

            # Trigger timeout manually to bypass debouncing
            if dialog._search_timer:
                dialog.after_cancel(dialog._search_timer)
            dialog._perform_search()

            mock_search.assert_called_once_with("xanh", limit=50)

            items = dialog.tree.get_children()
            assert len(items) == 1
            assert dialog.tree.item(items[0], "text") == "[#1] Slime Xanh - Lv.10 | HP: 100"

def test_picker_confirm_callback(tk_root, mock_db_responses):
    all_monsters, _ = mock_db_responses
    with patch("dialogs.monster_picker.get_all_monsters_api", return_value=all_monsters):
        on_select_mock = MagicMock()
        dialog = MonsterPickerDialog(tk_root, "vi", on_select_mock, lambda key: key)

        items = dialog.tree.get_children()
        dialog.tree.selection_set(items[0])

        dialog._on_confirm()

        # Verify callback payload contract
        on_select_mock.assert_called_once_with({
            "monster_id": 1,
            "name": "Slime Xanh",
            "dungeon_id": "d1"
        })

        # Dialog should be destroyed
        assert dialog.winfo_exists() == 0

def test_picker_empty_state(tk_root):
    with patch("dialogs.monster_picker.get_all_monsters_api", return_value=[]):
        dialog = MonsterPickerDialog(tk_root, "vi", MagicMock(), lambda key: key)

        assert len(dialog.tree.get_children()) == 0
        assert dialog.status_var.get() == "monster_picker_empty"

def test_picker_cancel_flow(tk_root, mock_db_responses):
    all_monsters, _ = mock_db_responses
    with patch("dialogs.monster_picker.get_all_monsters_api", return_value=all_monsters):
        on_select_mock = MagicMock()
        dialog = MonsterPickerDialog(tk_root, "vi", on_select_mock, lambda key: key)

        dialog._on_cancel()

        # Callback should not be fired
        on_select_mock.assert_not_called()

        assert dialog.winfo_exists() == 0
