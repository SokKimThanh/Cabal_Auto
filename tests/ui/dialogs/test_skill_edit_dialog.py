import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.dialogs.skill_edit_dialog import SkillEditDialog

def test_skill_edit_dialog_extracts_class_id_safely():
    root = tk.Tk()

    app_mock = MagicMock()
    app_mock.db_class_service.get_all_classes.return_value = [{"class_id": 1, "name": "Warrior"}]

    saved_data = None
    def mock_on_save(data):
        nonlocal saved_data
        saved_data = data

    dialog = SkillEditDialog(root, app_mock, "Test", {"name": "Test Skill"}, mock_on_save)

    # Simulate selecting valid class
    dialog.var_class_id_str.set("1 - Warrior")
    dialog._on_save_click()

    assert saved_data is not None
    assert saved_data["class_id"] == 1

    # Simulate selecting 0 - None
    saved_data = None
    dialog = SkillEditDialog(root, app_mock, "Test", {"name": "Test Skill"}, mock_on_save)
    dialog.var_class_id_str.set("0 - None")
    dialog._on_save_click()

    assert saved_data is not None
    assert saved_data["class_id"] is None

    # Simulate malformed text
    saved_data = None
    dialog = SkillEditDialog(root, app_mock, "Test", {"name": "Test Skill"}, mock_on_save)
    dialog.var_class_id_str.set("malformed-string")
    dialog._on_save_click()

    assert saved_data is not None
    assert saved_data["class_id"] is None

    root.destroy()
