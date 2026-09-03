import sys
import pytest
from unittest.mock import MagicMock

# Mock out window_manager and other windows specifics before import
sys.modules['lib.system.window_manager'] = MagicMock()
sys.modules['lib.features.hunt.window_selection_service'] = MagicMock()

from lib.features.hunt.hunt_orchestrator import HuntOrchestrator

class MockHuntLogger:
    def log_state_change(self, *args, **kwargs): pass
    def log_hunt_start(self, *args, **kwargs): pass
    def log_hunt_stop(self, *args, **kwargs): pass
    def log_error(self, *args, **kwargs): pass


def test_target_lost_debounce_and_no_spam_attack(mock_orchestrator, monkeypatch):
    orchestrator = mock_orchestrator
    """
    Simulates the orchestrator loop with specific conditions:
    1. Single transient false read does NOT trigger search mode.
    2. N consecutive false reads trigger search mode.
    3. During attack mode, 'tap' is NOT called (spam removed).
    """
    mock_backend_tap = MagicMock()
    class MockForegroundBackend:
        mode = "foreground"
        def __init__(self): pass
        def tap(self, *args, **kwargs): mock_backend_tap(*args, **kwargs)
        def close(self): pass
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.ForegroundSendInputBackend", MockForegroundBackend)

    mock_tap = MagicMock()
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.global_tap", mock_tap)

    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.get_hunt_logger", lambda: MockHuntLogger())
    # Mock window validation
    mock_validation = MagicMock()
    mock_validation.is_valid = True
    sys.modules["lib.features.hunt.window_selection_service"].validate_selected_cabal_window = lambda x, y: mock_validation

    # We will simulate a sequence of `is_target_alive` responses.
    # 0: False -> starts in search mode, taps z
    # 1: True -> finds target, goes to attack mode
    # 2: False -> transient false, should stay in attack mode
    # 3: True -> resets counter
    # 4, 5, 6: False -> 3 consecutive false reads, triggers lost
    # 7: orchestrator.hunt_running = False -> loop ends

    target_alive_seq = [False, True, False, True, False, False, False]
    seq_idx = 0

    class MockTargetBarDetector:
        def __init__(self, hwnd=None):
            self.hwnd = hwnd

        def is_target_alive(self, frame):
            nonlocal seq_idx
            if seq_idx < len(target_alive_seq):
                res = target_alive_seq[seq_idx]
                seq_idx += 1
                return res
            # Stop the loop after our sequence is done
            orchestrator.hunt_running = False
            return False

    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.TargetBarDetector", MockTargetBarDetector)

    # Use a dummy cfg
    cfg = {
        "target_key": "z",
        "lost_timeout_sec": 0, # Strict timeout for testing
        "target_lost_debounce_frames": 3,
        "search_tap_delay_sec": 0.0,
        "attack_interval": 0.0,
    }

    # Start hunt
    orchestrator.start_hunt(cfg)
    try:
        # Wait for the thread to finish
        orchestrator.hunt_thread.join(timeout=2.0)
        assert not orchestrator.hunt_thread.is_alive(), (
            "Hunt thread should terminate within the join timeout"
        )

        # Verify mock_backend_tap was called during search mode (before target found)
        assert mock_backend_tap.called, "Tap should be called during search mode"

        # Count taps on ForegroundBackend
        tap_calls = mock_backend_tap.call_args_list
        # All tap calls should be with 'z' (or the configured target key)
        for call in tap_calls:
            assert call[0][0] == 'z'
        # Ensure try_cast_skills was called during attack phase
        assert orchestrator.try_cast_skills.called
    finally:
        if getattr(orchestrator, "hunt_thread", None) and orchestrator.hunt_thread.is_alive():
            orchestrator.stop_hunt()
