import pytest
import time
import sys
from unittest.mock import MagicMock, patch
import tkinter as tk

import platform
if platform.system() != 'Windows':
    for m in ['win32gui', 'win32con', 'win32process', 'win32api', 'pywintypes']:
        sys.modules[m] = MagicMock()

from lib.vision.target_hp_reader import TargetHPReader
from lib.features.hunt.window_selection_service import WindowRecoveryController
from ui.tabs.hunt_tab import HuntTab

# Mock dependencies
class MockApp:
    def __init__(self):
        self.hunt_cfg = {"window_hwnd": 12345}
        self.hunt_status = tk.StringVar()
        self.hunt_target_info = tk.StringVar()
        self.target_policy_var = tk.StringVar(value="configured_only")
        self.monster_rotation = []
        self.auto_combo_var = tk.BooleanVar()
        self.combo_start_key_cmb = MagicMock()
        self.click_running = False
        self.monster_estimate_var = tk.StringVar()
        self.skill_slot_count = 8
        self.skill_stats_tree = MagicMock()

    def schedule_ui_task(self, func):
        func()

    def _create_icon_button(self, parent, icon_emoji, command, style, bg_color, hover_color):
        return tk.Button(parent, text=icon_emoji, command=command)

    def _create_tooltip(self, widget, text):
        pass

    def _on_monster_add_smart(self):
        pass

    def _on_monster_remove(self):
        pass

    def _on_monster_move_up(self): pass
    def _on_monster_move_down(self): pass
    def _on_monster_clear_rotation(self): pass
    def _on_config_monster(self): pass
    def _on_monster_delete_from_list(self): pass

    def _t(self, key):
        return key

    def _refresh_monster_select_options(self):
        pass

    def _refresh_monster_rotation_list(self):
        pass

    def _update_attack_keys_from_slots(self):
        pass

    def show_toast(self, msg):
        pass

@pytest.fixture
def tk_root():
    root = tk.Tk()
    yield root
    root.destroy()


def test_stress_hp_throttling():
    """Stress Test HP Throttling: Send 2000 events in 5s. Assert canvas draw called exactly 50 times."""
    detector = MagicMock()
    detector.get_hp_percentage.return_value = 95.0
    reader = TargetHPReader(detector)

    # We will simulate 2000 updates over 5.0 seconds
    # Max allowed updates is 50 (10 FPS * 5 seconds)

    updates = 0
    start_time = 1000.0

    # Simulate monotonic time
    def mock_time():
        nonlocal current_time
        return current_time

    current_time = start_time
    with patch('time.monotonic', side_effect=mock_time):
        # Initial call to set the baseline
        reader.calculate_target_hp_percent(None)

        for i in range(2000):
            # Alternating HP to trigger delta
            detector.get_hp_percentage.return_value = 95.0 if i % 2 == 0 else 90.0

            prev_drawn = reader.last_drawn_percent
            result = reader.calculate_target_hp_percent(None)

            if result != prev_drawn:
                updates += 1

            # Increment time slightly (5s total / 2000 iterations = 0.0025s per iteration)
            current_time += 0.0025

    # Should be approximately 50 updates due to 100ms throttle.
    assert 48 <= updates <= 51


def test_delta_threshold_skip():
    """Test Delta Threshold Skip: Within valid 100ms window, send delta < 0.5%, assert no update."""
    detector = MagicMock()
    detector.get_hp_percentage.return_value = 100.0
    reader = TargetHPReader(detector)

    with patch('time.monotonic', return_value=1000.0):
        # Initial draw
        res = reader.calculate_target_hp_percent(None)
        assert res == 100.0

    with patch('time.monotonic', return_value=1000.2): # 200ms elapsed
        detector.get_hp_percentage.return_value = 99.6 # Delta 0.4
        res = reader.calculate_target_hp_percent(None)
        # Should NOT draw because delta < 0.5
        assert res == 100.0
        assert reader.last_drawn_percent == 100.0

    with patch('time.monotonic', return_value=1000.4): # 400ms elapsed
        detector.get_hp_percentage.return_value = 99.5 # Delta 0.5
        res = reader.calculate_target_hp_percent(None)
        # SHOULD draw because delta >= 0.5
        assert res == 99.5
        assert reader.last_drawn_percent == 99.5


def test_graceful_death_delay(tk_root):
    """Test Graceful Death Delay: HP=0% changes state to dead and schedules clear card in 200ms."""
    app = MockApp()
    tab = HuntTab(tk_root, app)
    tab._pending_clear_id = None

    # Mock clear_target_card
    with patch.object(tab, 'clear_target_card') as mock_clear:
        tab.update_hp_display(0.0)

        # Verify UI state is dead
        assert tab.hp_canvas.itemcget(tab.hp_fill, "fill") == "#52525B"
        assert tab.hp_canvas.itemcget(tab.hp_text, "text") == "target_card.target_dead"

        # Verify delay is scheduled
        assert tab._pending_clear_id is not None


def test_rapid_retarget_cancels_pending_clear(tk_root):
    """Test Rapid Re-target Cancels Pending Clear: Retargeting within 200ms calls after_cancel."""
    app = MockApp()
    tab = HuntTab(tk_root, app)

    with patch.object(tab, 'after_cancel') as mock_cancel:
        tab._pending_clear_id = "test_timer_id"

        # Update target card (retargeting)
        with patch('ui.tabs.hunt_tab.get_target_monster_info', return_value={"id": 1, "name": "test", "level": 1, "hp": 100, "defense": 10, "is_placeholder": False}):
            tab.update_target_card("test_mob")

        # Verify cancel called
        mock_cancel.assert_called_once_with("test_timer_id")
        assert tab._pending_clear_id is None


def test_3_step_recovery_retry_and_failure():
    """Test 3-Step Recovery Retry & Failure Fallback: Wait, retry, fail safely."""
    # Reset singleton
    WindowRecoveryController._instance = None
    controller = WindowRecoveryController.instance()

    # Mock scheduler
    def mock_scheduler(delay, func):
        func()

    on_progress = MagicMock()
    on_failure = MagicMock()

    with patch('lib.features.hunt.window_selection_service.WindowManager') as MockWM:
        wm_instance = MockWM.return_value
        wm_instance.restore.return_value = False

        controller.start_async_recovery(
            hwnd=123,
            schedule_after_ms=mock_scheduler,
            on_progress=on_progress,
            on_failure=on_failure
        )

        # Should attempt 3 times, fail, and call on_failure
        assert on_progress.call_count == 3
        on_failure.assert_called_once()
        assert controller._retry_in_progress is False


def test_shared_retry_lock_with_ux1():
    """Test Shared Retry Lock With UX1: Concurrent requests only execute one."""
    WindowRecoveryController._instance = None
    controller = WindowRecoveryController.instance()

    def mock_scheduler(delay, func):
        # Do not immediately execute to simulate async overlap
        pass

    on_progress1 = MagicMock()
    on_progress2 = MagicMock()

    with patch('lib.features.hunt.window_selection_service.WindowManager') as MockWM:
        wm_instance = MockWM.return_value
        wm_instance.restore.return_value = False
        wm_instance.set_foreground.return_value = False
        # First call
        controller.start_async_recovery(123, mock_scheduler, on_progress1, MagicMock())
        # Second call immediately after (before first finishes)
        controller.start_async_recovery(123, mock_scheduler, on_progress2, MagicMock())

        # First call executes step 1
        assert on_progress1.call_count == 1
        # Second call is ignored due to lock
        assert on_progress2.call_count == 0
