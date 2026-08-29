import pytest
import tkinter as tk
import json
import os

pytest.importorskip("tkinter", reason="Skipping UI imports because tkinter is not available in headless environment")

pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests"
)

def test_hidden_fields_retention():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()
    try:
        # Initial monster data with some advanced and unknown fields
        existing_monster = {
            "id": "m1",
            "name": "Test Monster",
            "penetration": 55,
            "resistCritRate": 44,
            "damage_per_hit": 15,
            "priority": 3,
            "unknown_field_123": "preserve_me",
            "another_unknown": [1, 2, 3]
        }

        dialog = MonsterEditDialog(root, monster=existing_monster)

        # Modify a visible field
        dialog.name_entry.delete(0, tk.END)
        dialog.name_entry.insert(0, "Modified Name")

        # Collect data WITHOUT ever expanding the advanced groups
        collected_data = dialog._collect_form_data()

        # Assertions
        assert collected_data["name"] == "Modified Name"

        # Hidden/Advanced fields should be retained
        assert collected_data["penetration"] == 55
        assert collected_data["resistCritRate"] == 44

        # Local metadata should be retained
        assert collected_data["damage_per_hit"] == 15
        assert collected_data["priority"] == 3

        # Unknown keys should be retained
        assert collected_data["unknown_field_123"] == "preserve_me"
        assert collected_data["another_unknown"] == [1, 2, 3]

    finally:
        root.destroy()

def test_repeated_collapse_expand_preserves_values():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = MonsterEditDialog(root)

        # Set some advanced field values manually in the UI
        dialog.pen_entry.delete(0, tk.END)
        dialog.pen_entry.insert(0, "123")

        # Find a collapsible group toggle (simulating clicking the header)
        # In _create_collapsible_group, the arrow is bound to <Button-1>.
        # We can just simulate the toggle behavior directly or trigger the event.
        # Actually, let's just trigger the event on one of the headers.

        def find_headers(widget):
            headers = []
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame) and child.cget("cursor") == "hand2":
                    headers.append(child)
                headers.extend(find_headers(child))
            return headers

        headers = find_headers(dialog)
        if headers:
            header = headers[0]
            # trigger toggle
            header.event_generate("<Button-1>")
            dialog.update()

            # trigger toggle again
            header.event_generate("<Button-1>")
            dialog.update()

            # verify value is not lost
            assert dialog.pen_entry.get() == "123"

            data = dialog._collect_form_data()
            assert data["penetration"] == 123

    finally:
        root.destroy()

def test_complete_candidate_output_fields():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = MonsterEditDialog(root)

        data = dialog._collect_form_data()

        # Check all canonical DB columns
        for col in MonsterEditDialog.DB_COLUMNS:
            key = col["key"]
            assert key in data, f"Missing canonical field {key}"

        # Check all local metadata
        for meta in MonsterEditDialog.LOCAL_METADATA:
            key = meta["key"]
            assert key in data, f"Missing local metadata field {key}"

    finally:
        root.destroy()

def test_widget_visibility_with_grid_remove_pack_forget():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = MonsterEditDialog(root, monster={"id": "m1", "name": "Monster1"})

        # Hide the advanced widgets container (simulating grid_remove/pack_forget)
        parent_frame = dialog.pen_entry.master

        # set a value
        dialog.pen_entry.delete(0, tk.END)
        dialog.pen_entry.insert(0, "999")

        # hide it
        parent_frame.pack_forget()
        dialog.update()

        # check that data collection still works
        data = dialog._collect_form_data()
        assert data["penetration"] == 999

    finally:
        root.destroy()
