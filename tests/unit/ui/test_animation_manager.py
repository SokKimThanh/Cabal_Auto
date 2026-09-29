import pytest
import tkinter as tk
import time
from lib.ui.animation_manager import UIAnimationManager
from unittest.mock import MagicMock

@pytest.fixture
def manager():
    UIAnimationManager.reset_instance()
    return UIAnimationManager()

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

def test_register_tween_overrides_existing(manager, root):
    updates = []
    def update_func(val):
        updates.append(val)

    # Register first tween
    manager.register_tween('test_bar', root, 0, 100, 1000, update_func)

    assert len(manager.tweens) == 1
    assert 'test_bar' in manager.tweens
    assert manager.tweens['test_bar']['start_val'] == 0
    assert manager.tweens['test_bar']['end_val'] == 100

    # Simulate some time passing / changing current_val manually to test behavior
    manager.tweens['test_bar']['current_val'] = 50

    # Register second tween with same target_id
    manager.register_tween('test_bar', root, 0, 200, 1000, update_func)

    # Ensure queue only has 1 job
    assert len(manager.tweens) == 1

    # Check that new tween started from actual_start (current_val)
    assert manager.tweens['test_bar']['start_val'] == 50
    assert manager.tweens['test_bar']['end_val'] == 200

def test_register_tween_destroyed_widget(manager, root):
    updates = []
    def update_func(val):
        updates.append(val)

    # Create a frame to destroy
    frame = tk.Frame(root)

    manager.register_tween('destroyed_test', frame, 0, 100, 1000, update_func)
    assert 'destroyed_test' in manager.tweens

    # Destroy the frame
    frame.destroy()

    # Run the loop which should handle destroyed widgets without crashing
    manager._run_loop()

    # Loop should remove the tween for destroyed widget
    assert 'destroyed_test' not in manager.tweens

def test_cancel_tween(manager, root):
    def update_func(val):
        pass

    manager.register_tween('cancel_test', root, 0, 100, 1000, update_func)
    assert 'cancel_test' in manager.tweens

    manager.cancel_tween('cancel_test')
    assert 'cancel_test' not in manager.tweens

def test_tween_completion(manager, root):
    updates = []
    def update_func(val):
        updates.append(val)

    manager.register_tween('complete_test', root, 0, 100, 10, update_func)

    # Force elapsed time to be > duration
    manager.tweens['complete_test']['start_time'] = time.time() - 10

    manager._run_loop()

    # Tween should be complete and removed
    assert 'complete_test' not in manager.tweens
    assert 100 in updates
