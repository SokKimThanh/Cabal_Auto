import pytest
import tkinter as tk
import uuid
from unittest.mock import Mock, patch
from dialogs.monster_edit import MonsterEditDialog

pytestmark = pytest.mark.unit


class MockDB:
    def get_dungeon_list(self):
        return []
    def get_monster_type_list(self):
        return []

class MockParent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = MockDB()
        self.monsters = []

    def get_all_monsters_for_validation(self):
        return self.monsters

@pytest.fixture
def tk_root():
    root = MockParent()
    root.withdraw()
    yield root
    root.destroy()

def test_new_monster_has_generated_id(tk_root):
    dialog = MonsterEditDialog(tk_root, monster=None)

    # Assert id was generated
    assert dialog.monster_data.get("id") is not None
    assert dialog.monster_data["id"] != ""
    assert isinstance(dialog.monster_data["id"], str)

    # Should display the ID
    assert dialog.id_val_label.cget("text") == f"#{dialog.monster_data['id']}"

def test_edit_monster_shows_readonly_id(tk_root):
    existing_monster = {"id": "test_id_123", "name": "Test Monster"}
    dialog = MonsterEditDialog(tk_root, monster=existing_monster)

    assert dialog.monster_data.get("id") == "test_id_123"
    assert dialog.id_val_label.cget("text") == "#test_id_123"

    # Generate button should be hidden for existing monster
    assert not dialog.btn_generate_id.winfo_ismapped()

def test_generate_id_button(tk_root):
    dialog = MonsterEditDialog(tk_root, monster=None)
    old_id = dialog.monster_data.get("id")

    dialog.btn_generate_id.invoke()

    new_id = dialog.monster_data.get("id")
    assert new_id != old_id
    assert dialog.id_val_label.cget("text") == f"#{new_id}"

def test_collect_data_includes_id(tk_root):
    dialog = MonsterEditDialog(tk_root, monster=None)

    # Mock entries
    dialog.name_entry.delete(0, tk.END)
    dialog.name_entry.insert(0, "New Test Monster")

    collected = dialog._collect_form_data()

    assert "id" in collected
    assert collected["id"] != ""
    assert collected["id"] == dialog.monster_data["id"]

def test_collect_data_preserves_existing_id(tk_root):
    existing_monster = {"id": "existing_id_999", "name": "Existing"}
    dialog = MonsterEditDialog(tk_root, monster=existing_monster)

    collected = dialog._collect_form_data()

    assert collected["id"] == "existing_id_999"
