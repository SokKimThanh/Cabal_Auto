import os
import pytest

pytest.importorskip("tkinter", reason="Skipping UI tests because tkinter is not available")
pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests"
)

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

psutil = pytest.importorskip(
    "psutil", reason="psutil is optional; skip memory stability test when unavailable"
)
from lib.features.monsters.monster_repo import get_target_monster_info
from ui.tabs.hunt_tab import HuntTab


class DummyApp:
    def __init__(self):
        self.hunt_cfg = {}
        self.hunt_status = tk.StringVar()
        self.hunt_target_info = tk.StringVar()
        self.click_running = False

    def _t(self, key):
        return key

    def schedule_ui_task(self, task):
        task()

    def __getattr__(self, name):
        if name.startswith('_on_') or name.startswith('_refresh_') or name.startswith('_create_') or name.startswith('_update_'):
            return lambda *args, **kwargs: tk.Label() if name.startswith('_create_') else None
        if name.endswith('_var'):
            class DummyVar(tk.Variable):
                def __init__(self, name=""):
                    self.val = ""
                    self._name = name

                def set(self, val):
                    self.val = val

                def get(self):
                    return self.val

                def trace_add(self, *args, **kwargs):
                    pass

            var = DummyVar(name=name)
            try:
                var._name = name
            except AttributeError:
                pass
            setattr(self, name, var)
            return var
        if name == "skill_slot_count":
            return 8
        if name == "combo_start_key_cmb":
            cmb = tk.Entry()
            setattr(self, name, cmb)
            return cmb
        if name == "skills":
            return []

        class MockMagic:
            def __call__(self, *args, **kwargs):
                pass

            def __getattr__(self, name):
                return MockMagic()
        return MockMagic()


class TestTargetCardShell(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = DummyApp()

    def tearDown(self):
        self.root.destroy()

    @patch('database.get_monster_by_id_api', return_value=None)
    @patch('database.find_monster_by_name_api', return_value=None)
    @patch('lib.features.monsters.monster_repo.load_monster_library', return_value={})
    def test_schema_fallback(self, mock_load, mock_find, mock_get):
        info = get_target_monster_info("NonExistentMob")

        self.assertEqual(info["id"], "0")
        self.assertEqual(info["name"], "NonExistentMob")
        self.assertEqual(info["level"], "N/A")
        self.assertEqual(info["hp"], 10000)
        self.assertEqual(info["defense"], 0)
        self.assertIsNone(info["image_path"])
        self.assertTrue(info["is_placeholder"])

    @patch('database.get_monster_by_id_api')
    def test_schema_db_hit(self, mock_get):
        mock_get.return_value = {
            "id": "123",
            "name": "Goblin",
            "level": "5",
            "hp": 200,
            "defense": 10,
            "image_path": "path/to/img.png"
        }
        info = get_target_monster_info("123")

        self.assertEqual(info["id"], "123")
        self.assertEqual(info["name"], "Goblin")
        self.assertEqual(info["level"], "5")
        self.assertEqual(info["hp"], 200)
        self.assertEqual(info["defense"], 10)
        self.assertEqual(info["image_path"], "path/to/img.png")
        self.assertFalse(info["is_placeholder"])

    def test_zero_asset_fallback(self):
        tab = HuntTab(self.root, self.app)

        # Test zero-asset
        tab.set_target_photo(None)

        # Verify it falls back to text mode
        self.assertEqual(tab.target_image_label.cget("text"), "[ NO IMAGE ]")
        self.assertEqual(tab.target_image_label.cget("image"), "")
        self.assertIsNone(getattr(tab, "_current_target_photo", None))

    def test_clear_before_set_ordering(self):
        tab = HuntTab(self.root, self.app)

        # Spy on clear_target_photo
        tab.clear_target_photo = MagicMock(side_effect=tab.clear_target_photo)

        # Mock photos
        photo1 = tk.PhotoImage(width=1, height=1)
        photo2 = tk.PhotoImage(width=1, height=1)

        tab.set_target_photo(photo1)
        self.assertEqual(tab.clear_target_photo.call_count, 1)
        self.assertEqual(tab._current_target_photo, photo1)

        tab.set_target_photo(photo2)
        self.assertEqual(tab.clear_target_photo.call_count, 2)
        self.assertEqual(tab._current_target_photo, photo2)

    def test_high_load_memory_stability(self):
        tab = HuntTab(self.root, self.app)

        process = psutil.Process(os.getpid())

        # Warmup
        for _ in range(50):
            tab.set_target_photo(tk.PhotoImage(width=1, height=1))

        start_rss = process.memory_info().rss

        # High load
        for _ in range(500):
            tab.set_target_photo(tk.PhotoImage(width=1, height=1))

        end_rss = process.memory_info().rss

        # Check diff < 20MB
        diff_mb = (end_rss - start_rss) / (1024 * 1024)
        self.assertLess(diff_mb, 20.0, f"Memory leak detected! Grew by {diff_mb} MB")


if __name__ == '__main__':
    unittest.main()
