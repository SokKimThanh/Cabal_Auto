import pytest
import tkinter as tk
from unittest.mock import MagicMock

from ui.components.skill_timeline_strip import SkillTimelineStrip, SkillSlotCanvas
from lib.ui_style_v2 import UIStyleV2 as UI

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def skills_data():
    return [
        {"name": "Fireball", "icon_key": "skill_fire", "hotkey": "1"},
        {"name": "Ice Lance", "icon_key": "skill_ice", "hotkey": "2"},
        {"name": "Heal", "icon_key": "skill_heal", "hotkey": "3"},
    ]

@pytest.fixture
def timeline(root, skills_data):
    strip = SkillTimelineStrip(root, skills=skills_data)
    strip.pack()
    root.update()
    yield strip

def test_timeline_initialization(timeline):
    """Test component initializes without errors and renders correct number of slots."""
    assert len(timeline._slots) == 3
    assert timeline.undo_btn.cget("state") == "disabled"
    assert timeline.scrollbar.winfo_ismapped() == False  # under 8 items

def test_scroll_bar_appears_over_limit(root):
    """Test scrollbar renders when there are more than 8 slots."""
    skills = [{"name": f"Skill {i}", "icon_key": f"icon_{i}", "hotkey": str(i)} for i in range(10)]
    strip = SkillTimelineStrip(root, skills=skills)
    strip.pack()
    root.update()

    assert len(strip._slots) == 10
    assert strip.scrollbar.winfo_ismapped() == True

def test_update_cooldown_clamps_ratio(timeline):
    """Test update_cooldown clamps ratio and visually updates the slot."""
    slot = timeline._slots[0]

    # Test valid ratio
    timeline.update_cooldown("Fireball", 0.5)
    timeline.update()
    assert slot.itemcget(slot.cooldown_rect, "state") == "normal"
    assert slot.cget("highlightbackground") == UI.ACCENT_AMBER

    # Check coordinates calculation (bottom up)
    coords = slot.coords(slot.cooldown_rect)
    y_top = slot.SLOT_SIZE * 0.5 # 1.0 - 0.5
    assert coords == [0.0, y_top, float(slot.SLOT_SIZE), float(slot.SLOT_SIZE)]

    # Test clamped high
    timeline.update_cooldown("Fireball", 1.5)
    timeline.update()
    assert slot.itemcget(slot.cooldown_rect, "state") == "hidden"
    assert slot.cget("highlightbackground") == UI.BORDER_PRIMARY

    # Test clamped low
    timeline.update_cooldown("Fireball", -0.5)
    timeline.update()
    assert slot.itemcget(slot.cooldown_rect, "state") == "hidden"
    assert slot.cget("highlightbackground") == UI.BORDER_PRIMARY

def test_undo_functionality(timeline):
    """Test undo stack logic for Drag and Drop."""
    original_skills = list(timeline.skills)

    # Simulate drag start on first item
    slot = timeline._slots[0]
    event = MagicMock()
    timeline._on_drag_start(slot, event)

    assert len(timeline._history) == 1
    assert timeline._history[0] == original_skills

    # Modify skills manually to simulate a drop reorder
    timeline.skills = timeline.skills[::-1] # Reverse
    timeline.render_skills()
    assert timeline.undo_btn.cget("state") == "normal"

    # Hit undo
    timeline.undo()
    assert timeline.skills == original_skills
    assert timeline.undo_btn.cget("state") == "disabled"
    assert len(timeline._history) == 0

def test_image_reference_storage(root):
    """Test that SkillSlotCanvas stores photo image references so GC doesn't destroy them."""
    # Mock an image object using a real tk.PhotoImage to avoid TclError
    real_img = tk.PhotoImage(width=10, height=10)
    skill_data = {"name": "Fireball", "icon_key": "skill_fire", "hotkey": "1", "image_obj": real_img}

    timeline = SkillTimelineStrip(root, skills=[skill_data])
    timeline.pack()
    root.update()

    slot = timeline._slots[0]
    assert "icon" in slot._images
    assert slot._images["icon"] == real_img
