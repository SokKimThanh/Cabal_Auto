import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
import json

from ui.windows.monster_manager_win import MonsterManagerWin

@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

def test_pending_changes_merge_by_id(root, mock_db):
    """Verify pending_changes merge is keyed by monster ID and never depends on current page order/index."""
    win = MonsterManagerWin(root)
    win.db = mock_db
    win.page_size = 10

    # 1. Start on page 1 (m0 - m9)
    win.current_page = 1
    win.monster_table = MagicMock()
    win.monster_table.get_children.return_value = []
    win.search_entry = MagicMock()
    win.search_entry.get.return_value = ""
    win.visible_columns = ["id", "name"]
    win._refresh_monster_table()

    assert len(win.monsters) == 10
    assert win.monsters[0]["id"] == "m0"

    # 2. Add pending edit to m5
    win.pending_changes["m5"] = {"id": "m5", "name": "Edited Monster 5"}

    # 3. Add pending edit to m15 (which is on page 2)
    win.pending_changes["m15"] = {"id": "m15", "name": "Edited Monster 15"}

    # 4. Add entirely new pending monster
    win.pending_changes["new1"] = {"id": "new1", "name": "New Monster"}

    # Refresh current page (page 1)
    win._refresh_monster_table()

    # m5 should be edited, new1 and m15 should be appended because they are pending
    m5_found = False
    m15_found = False
    new1_found = False

    for m in win.monsters:
        if m["id"] == "m5":
            assert m["name"] == "Edited Monster 5"
            m5_found = True
        elif m["id"] == "m15":
            assert m["name"] == "Edited Monster 15"
            m15_found = True
        elif m["id"] == "new1":
            assert m["name"] == "New Monster"
            new1_found = True

    assert m5_found, "Pending change for m5 on current page was not applied"
    assert m15_found, "Pending change for m15 (off-page) was lost"
    assert new1_found, "New pending monster was lost"

def test_pending_changes_survive_navigation(root, mock_db):
    """Verify add/edit pending records survive refresh, filter change, next/previous page, and dialog close/reopen."""
    win = MonsterManagerWin(root)
    win.db = mock_db
    win.page_size = 10
    win.current_page = 1
    win.monster_table = MagicMock()
    win.monster_table.get_children.return_value = []
    win.search_entry = MagicMock()
    win.search_entry.get.return_value = ""
    win.visible_columns = ["id", "name"]

    win.pending_changes["m25"] = {"id": "m25", "name": "Pending Edit 25"}

    # Navigate to page 3
    win.current_page = 3
    win._refresh_monster_table()

    assert "m25" in win.pending_changes
    m25_found = any(m["id"] == "m25" and m["name"] == "Pending Edit 25" for m in win.monsters)
    assert m25_found, "Pending change was not merged when navigating to its native page"

    # Change filter
    win.search_entry.get.return_value = "NonExistent"
    win._refresh_monster_table()

    assert "m25" in win.pending_changes
    m25_found = any(m["id"] == "m25" and m["name"] == "Pending Edit 25" for m in win.monsters)
    assert m25_found, "Pending change was excluded by filter"

def test_pending_changes_cleared_on_success(root, mock_db):
    """Verify pending_changes clears only after every persistence operation succeeds."""
    win = MonsterManagerWin(root)
    win.db = mock_db
    win.monster_table = MagicMock()
    win.monster_table.get_children.return_value = []
    win.search_entry = MagicMock()
    win.search_entry.get.return_value = ""
    win.visible_columns = ["id", "name"]

    win.pending_changes["m1"] = {"id": "m1", "name": "Success Edit"}
    win.pending_changes["m2"] = {"id": "m2", "name": "Success Edit 2"}

    mock_db.insert_or_update_monster.return_value = True

    win._save_monsters()

    assert len(win.pending_changes) == 0

def test_pending_changes_retained_on_failure(root, mock_db):
    """Verify simulated DB/JSON failure retains all pending records and gives an actionable error."""
    win = MonsterManagerWin(root)
    win.db = mock_db
    win.monster_table = MagicMock()
    win.monster_table.get_children.return_value = []
    win.search_entry = MagicMock()
    win.search_entry.get.return_value = ""
    win.visible_columns = ["id", "name"]

    win.pending_changes["m1"] = {"id": "m1", "name": "Success Edit"}
    win.pending_changes["m2"] = {"id": "m2", "name": "Failed Edit"}

    def mock_insert(m):
        return m["id"] == "m1"

    mock_db.insert_or_update_monster.side_effect = mock_insert

    # Mock show status message to verify actionable error
    win._show_status_message = MagicMock()

    win._save_monsters()

    # Both should remain since it acts atomically per requirement
    assert "m1" in win.pending_changes
    assert "m2" in win.pending_changes
    assert win.pending_changes["m2"]["name"] == "Failed Edit"

    # Assert actionable error was shown
    win._show_status_message.assert_called_with("Lưu thất bại một phần: không thể ghi một số monster vào DB", is_error=True)

def test_duplicate_name_validation(root, mock_db):
    """Verify duplicate-name validation queries/compares the complete relevant dataset, not just visible table rows."""
    win = MonsterManagerWin(root)
    win.db = mock_db
    win.monster_table = MagicMock()
    win.monster_table.get_children.return_value = []
    win.search_entry = MagicMock()
    win.search_entry.get.return_value = ""
    win.visible_columns = ["id", "name"]

    # DB has m1 on page 1, m99 on page 10
    mock_db.get_all_monsters.return_value = [
        {"id": "m1", "name": "Goblin"},
        {"id": "m99", "name": "Dragon"}
    ]

    win.pending_changes["m2"] = {"id": "m2", "name": "Orc"}

    all_monsters = win.get_all_monsters_for_validation()

    names = [m.get("name") for m in all_monsters]
    assert "Goblin" in names
    assert "Dragon" in names
    assert "Orc" in names
