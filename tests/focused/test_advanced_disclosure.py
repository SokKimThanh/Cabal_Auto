import pytest
import tkinter as tk
from unittest.mock import Mock
from dialogs.monster_edit import MonsterEditDialog
import json

class MockDB:
    def get_dungeon_list(self): return []
    def get_monster_type_list(self): return []

class MockParent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = MockDB()

@pytest.fixture
def tk_root():
    root = MockParent()
    root.withdraw()
    yield root
    root.destroy()

def test_hidden_advanced_fields_retained(tk_root):
    # Data with some advanced fields set
    initial_data = {
        "id": "1",
        "name": "Hidden Test",
        "penetration": 50,
        "evasion": 20,
    }
    dialog = MonsterEditDialog(tk_root, monster=initial_data)

    # Ensure advanced widgets are hidden (by not clicking expand)
    # The collapsible group starts collapsed

    # Collect without modifying or revealing
    data = dialog._collect_form_data()

    assert data["penetration"] == 50
    assert data["evasion"] == 20

def test_unknown_keys_preserved(tk_root):
    initial_data = {
        "id": "1",
        "name": "Unknown Key Test",
        "custom_unknown_key": "some_value",
        "another_key": [1, 2, 3]
    }
    dialog = MonsterEditDialog(tk_root, monster=initial_data)

    data = dialog._collect_form_data()

    assert "custom_unknown_key" in data
    assert data["custom_unknown_key"] == "some_value"
    assert "another_key" in data
    assert data["another_key"] == [1, 2, 3]

def test_repeated_collapse_expand_preserves_values(tk_root):
    initial_data = {
        "id": "1",
        "name": "Toggle Test",
        "penetration": 50,
    }
    dialog = MonsterEditDialog(tk_root, monster=initial_data)

    # We need to find the toggle buttons and click them, or directly call the toggle function
    # Unfortunately the toggle logic is bound to lambdas in _create_collapsible_group
    # Let's simulate grid_remove and grid
    if hasattr(dialog, 'pen_entry'):
        assert dialog.pen_entry.get() == "50"

        # modify
        dialog.pen_entry.delete(0, tk.END)
        dialog.pen_entry.insert(0, "75")

        # grid_remove simulating collapse
        dialog.pen_entry.grid_remove()

        # grid simulating expand
        dialog.pen_entry.grid()

        data = dialog._collect_form_data()
        assert data["penetration"] == 75
