import pytest
import tkinter as tk
from unittest.mock import Mock, patch
from ui.windows.monster_manager_win import MonsterManagerWin
import uuid

class MockDB:
    def __init__(self):
        self.monsters = [
            {"id": "1", "name": "Monster 1"},
            {"id": "2", "name": "Monster 2"},
            {"id": "3", "name": "Monster 3"},
        ]
        self.should_fail_save = False

    def get_all_monsters(self, offset=0, limit=100, name_filter=None):
        filtered = [m for m in self.monsters if not name_filter or name_filter in m["name"]]
        return filtered[offset:offset+limit]

    def count_monsters(self, name_filter=None):
        return len([m for m in self.monsters if not name_filter or name_filter in m["name"]])

    def save_monster(self, monster):
        pass

    def insert_or_update_monster(self, monster):
        if self.should_fail_save:
            return False

        for i, m in enumerate(self.monsters):
            if m["id"] == monster["id"]:
                self.monsters[i] = monster
                return True

        self.monsters.append(monster)
        return True

    def get_dungeon_list(self): return []
    def get_monster_type_list(self): return []

class MockParent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = MockDB()
        self.monster_file = "dummy_file.json"

@pytest.fixture
def manager_win():
    root = MockParent()
    root.withdraw()

    # Needs to bypass actual DB load
    with patch("ui.windows.monster_manager_win.MonsterManagerWin._load_monsters"):
        win = MonsterManagerWin(root)
        yield win
        win.destroy()
    root.destroy()


def simulate_save(win, data):
    m_id = data.get("id")
    if m_id:
        win.pending_changes[m_id] = data
    else:
        m_id = str(uuid.uuid4())
        data["id"] = m_id
        win.pending_changes[m_id] = data

    updated = False
    for idx, m in enumerate(win.monsters):
        if m.get("id") == m_id:
            win.monsters[idx] = data
            updated = True
            break
    if not updated:
        win.monsters.insert(0, data)

    win.set_dirty(True)
    win.set_monster_dirty(True)


def test_pending_changes_survive_filter_change(manager_win):
    manager_win.monsters = manager_win.db.get_all_monsters()
    manager_win.filtered_monsters = manager_win.monsters[:]

    # Simulate editing a monster and adding a pending change
    m_id = "1"
    new_data = {"id": m_id, "name": "Pending Monster 1"}
    simulate_save(manager_win, new_data)

    assert m_id in manager_win.pending_changes
    assert manager_win.pending_changes[m_id]["name"] == "Pending Monster 1"

    # Change filter to something else
    manager_win.search_term = "NonExistent"
    if hasattr(manager_win, "search_var"):
        manager_win.search_var.set("NonExistent")
    manager_win._apply_search()

    # Verify pending change is STILL there
    assert m_id in manager_win.pending_changes

    # It should also be returned in get_all_monsters_for_validation
    all_monsters = manager_win.get_all_monsters_for_validation()
    assert any(m["name"] == "Pending Monster 1" for m in all_monsters)


def test_failed_persistence_retains_pending_changes(manager_win):
    manager_win.monsters = manager_win.db.get_all_monsters()
    manager_win.filtered_monsters = manager_win.monsters[:]

    m_id = "2"
    new_data = {"id": m_id, "name": "Pending Monster 2"}
    simulate_save(manager_win, new_data)

    # Simulate DB failure
    manager_win.db.should_fail_save = True

    # Try saving
    success = manager_win._save_monsters()
    assert success is False

    # Verify pending change is NOT cleared
    assert m_id in manager_win.pending_changes


def test_successful_persistence_clears_pending_changes(manager_win):
    manager_win.monsters = manager_win.db.get_all_monsters()
    manager_win.filtered_monsters = manager_win.monsters[:]

    m_id = "3"
    new_data = {"id": m_id, "name": "Pending Monster 3"}
    simulate_save(manager_win, new_data)

    manager_win.db.should_fail_save = False

    with patch.object(manager_win, 'db') as mock_db:
        mock_db.insert_or_update_monster.return_value = True
        success = manager_win._save_monsters()
        assert success is True

    # Verify pending change is cleared
    assert m_id not in manager_win.pending_changes
    assert len(manager_win.pending_changes) == 0

def test_pending_added_record_survives_pagination_and_is_visible(manager_win):
    # Set page size to 1 for testing pagination
    manager_win.PAGE_SIZE = 1
    manager_win.monsters = manager_win.db.get_all_monsters()
    manager_win.filtered_monsters = manager_win.monsters[:]

    # Add new monster (pending)
    new_id = str(uuid.uuid4())
    new_data = {"id": new_id, "name": "New Pending"}
    simulate_save(manager_win, new_data)

    assert new_id in manager_win.pending_changes

    # Go to next page
    manager_win._on_next_page()

    all_monsters = manager_win.get_all_monsters_for_validation()
    assert any(m["id"] == new_id for m in all_monsters)
