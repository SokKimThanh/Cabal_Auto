import pytest
import tkinter as tk
from unittest.mock import Mock, patch
from dialogs.monster_edit import MonsterEditDialog

pytestmark = pytest.mark.unit


class MockDB:
    def get_dungeon_list(self):
        return [{"id": "d1", "name": "Dungeon 1"}, {"id": "d2", "name": "Dungeon 2"}]

    def get_monster_type_list(self):
        return [{"value": "t1", "label": "Type 1"}, {"value": "t2", "label": "Type 2"}]

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

def test_reference_comboboxes_populated(tk_root):
    dialog = MonsterEditDialog(tk_root, monster=None)

    # check if dungeon_combo has values
    dungeon_values = dialog.dungeon_combo.cget("values")
    assert "<Không / None>" in dungeon_values
    assert "Dungeon 1" in dungeon_values
    assert "Dungeon 2" in dungeon_values

    boss_type_values = dialog.boss_type_combo.cget("values")
    assert "<Không / None>" in boss_type_values
    assert "Type 1" in boss_type_values
    assert "Type 2" in boss_type_values

def test_empty_db_fallback(tk_root):
    tk_root.db = None # no DB
    dialog = MonsterEditDialog(tk_root, monster=None)

    dungeon_values = dialog.dungeon_combo.cget("values")
    assert "<Không / None>" in dungeon_values
    assert len(dungeon_values) == 1

def test_label_to_id_mapping(tk_root):
    dialog = MonsterEditDialog(tk_root, monster=None)

    # User selects "Dungeon 1" and "Type 2"
    dialog.dungeon_combo.set("Dungeon 1")
    dialog.boss_type_combo.set("Type 2")

    data = dialog._collect_form_data()
    assert data["dungeonId"] == "d1"
    assert data["serverBossType"] == "t2"

def test_none_never_serializes_as_string_none(tk_root):
    dialog = MonsterEditDialog(tk_root, monster=None)

    # User selects "<Không / None>"
    dialog.dungeon_combo.set("<Không / None>")
    dialog.boss_type_combo.set("<Không / None>")

    data = dialog._collect_form_data()
    assert data["dungeonId"] is None
    assert data["serverBossType"] is None

    # Also test if original data had "None" string
    dialog2 = MonsterEditDialog(tk_root, monster={"id": "1", "name": "Test", "dungeonId": "None"})
    data2 = dialog2._collect_form_data()
    assert data2["dungeonId"] is None

def test_edit_load_preserves_unmatched_historical_reference_ids(tk_root):
    dialog = MonsterEditDialog(tk_root, monster={"id": "1", "name": "Test", "dungeonId": "unknown_dungeon"})

    # The combobox should display the unmatched ID (possibly with a fallback label)
    assert "unknown_dungeon" in dialog.dungeon_combo.get() or "unknown_dungeon (Unknown)" in dialog.dungeon_combo.get()

    # Collection should preserve it
    data = dialog._collect_form_data()
    assert data["dungeonId"] == "unknown_dungeon"

def test_new_defaults_do_not_overwrite_user_entered_values(tk_root):
    dialog = MonsterEditDialog(tk_root, monster={"id": "1", "name": "Test", "dungeonId": "d2", "serverBossType": "t1"})
    data = dialog._collect_form_data()
    assert data["dungeonId"] == "d2"
    assert data["serverBossType"] == "t1"
