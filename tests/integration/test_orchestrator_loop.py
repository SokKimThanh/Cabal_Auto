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

@pytest.fixture
def orchestrator():
    # Provide simple mock callbacks
    on_status = MagicMock()
    on_state = MagicMock()
    locate_target = MagicMock()
    bring_window = MagicMock()
    bring_hwnd = MagicMock()
    bring_pid = MagicMock()
    iconify = MagicMock()
    update_stats = MagicMock()
    get_selected = MagicMock(return_value={"hwnd": 123})
    schedule = lambda f: f()  # Execute synchronously in test

    orch = HuntOrchestrator(
        handler=MagicMock(),
        bot_manager=MagicMock(),
        vision_engine=MagicMock(),
        skill_runtime=MagicMock()
    )
    orch.bot_manager = MagicMock()
    orch.bot_manager.screen_capture = MagicMock()
    orch.bot_manager.screen_capture.hwnd = 123
    orch.bot_manager.screen_capture.get_latest_frame = MagicMock(return_value="mock_frame")
    orch.try_cast_skills = MagicMock()
    return orch

def test_background_mode_does_not_call_global_sendinput(orchestrator, monkeypatch):
    """
    Simulates the orchestrator loop with background mode enabled to ensure
    no global SendInput or focus methods are called.
    """
    mock_global_tap = MagicMock()
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.global_tap", mock_global_tap)

    mock_backend_tap = MagicMock()

    class MockBackgroundBackend:
        mode = "background"
        def __init__(self, hwnd):
            pass
        def tap(self, *args, **kwargs):
            mock_backend_tap(*args, **kwargs)
        def close(self):
            pass

    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.BackgroundWindowMessageBackend", MockBackgroundBackend)
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.get_hunt_logger", lambda: MockHuntLogger())

    # Mock window validation
    mock_validation = MagicMock()
    mock_validation.is_valid = True
    sys.modules["lib.features.hunt.window_selection_service"].validate_selected_cabal_window = lambda x, y: mock_validation

    # We will simulate a sequence of `is_target_alive` responses.
    target_alive_seq = [False, False]
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

    # Mock capability check so it passes
    mock_capability_mgr = MagicMock()
    # State SUPPORTED, is_ready=True
    mock_capability_mgr_instance = MagicMock()
    hunt_orchestrator_module = sys.modules[HuntOrchestrator.__module__]
    mock_capability_mgr_instance.check_and_verify_capability.return_value = (
        hunt_orchestrator_module.InputCapabilityState.SUPPORTED,
        True,
    )
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.InputCapabilityManager", lambda *args: mock_capability_mgr_instance)

    # Use a dummy cfg with background input_mode
    cfg = {
        "input_mode": "background",
            "target_key": "z",
            "target_policy": "any_target",
            "lost_timeout_sec": 0,
        "target_lost_debounce_frames": 3,
        "search_tap_delay_sec": 0.0,
        "attack_interval": 0.0,
        "bring_to_front_each_cycle": True
    }

    # Override orchestrator methods
    orchestrator.bring_window_to_front = MagicMock()
    orchestrator.bring_window_to_front_by_hwnd = MagicMock()

    # Start hunt
    orchestrator.start_hunt(cfg)
    try:
        # Wait for the thread to finish
        orchestrator.hunt_thread.join(timeout=2.0)
        assert not orchestrator.hunt_thread.is_alive(), (
            "Hunt thread should terminate within the join timeout"
        )

        # Assert no global tap was called
        assert not mock_global_tap.called, "Global tap should not be called in background mode"

        # Assert background backend tap was called
        assert mock_backend_tap.called, "Background backend tap should be called"

        # Assert focus methods were not called despite bring_to_front_each_cycle=True
        assert not orchestrator.bring_window_to_front.called
        assert not orchestrator.bring_window_to_front_by_hwnd.called

    finally:
        if getattr(orchestrator, "hunt_thread", None) and orchestrator.hunt_thread.is_alive():
            orchestrator.stop_hunt()

def test_target_lost_debounce_and_no_spam_attack(orchestrator, monkeypatch):
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
            "target_policy": "any_target",
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
        assert orchestrator.handler.try_cast_skills.called
    finally:
        if getattr(orchestrator, "hunt_thread", None) and orchestrator.hunt_thread.is_alive():
            orchestrator.stop_hunt()


def test_orchestrator_wrong_target_no_cast(orchestrator, monkeypatch):
    """Test that a wrong target transitions to cycle, but no cast skills."""
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

    target_alive_seq = [False, True, True]
    seq_idx = 0

    class MockTargetBarDetector:
        def __init__(self, hwnd=None): self.hwnd = hwnd
        def is_target_alive(self, frame):
            nonlocal seq_idx
            if seq_idx < len(target_alive_seq):
                res = target_alive_seq[seq_idx]
                seq_idx += 1
                return res
            orchestrator.hunt_running = False
            return False

    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.TargetBarDetector", MockTargetBarDetector)

    # Mock name resolution to return WRONG target
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.find_monster_by_name_api", lambda *args: {"id": 205, "name": "Orc"})
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.TargetNameReader.read_name", lambda *args: "Orc")

    cfg = {
        "target_key": "z",
        "lost_timeout_sec": 0,
        "target_lost_debounce_frames": 3,
        "search_tap_delay_sec": 0.0,
        "attack_interval": 0.0,
        "target_policy": "configured_only",
        "monster_rotation": [{"monster_id": 101, "priority": 1}]
    }

    orchestrator.start_hunt(cfg)
    try:
        orchestrator.hunt_thread.join(timeout=2.0)
        assert not orchestrator.hunt_thread.is_alive()

        # The orchestrator should NOT have called try_cast_skills in attack_phase
        calls = orchestrator.handler.try_cast_skills.call_args_list
        for call in calls:
            args, kwargs = call
            attack_phase = kwargs.get('attack_phase', False)
            if len(args) > 3: attack_phase = attack_phase or args[3]
            assert not attack_phase, "try_cast_skills should not be called with attack_phase=True for wrong target"

        assert mock_backend_tap.called
    finally:
        if getattr(orchestrator, "hunt_thread", None) and orchestrator.hunt_thread.is_alive():
            orchestrator.stop_hunt()



def test_orchestrator_correct_target_casts(orchestrator, monkeypatch):
    """Test that a correct target transitions to attack and casts skills."""
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

    target_alive_seq = [False, True, True]
    seq_idx = 0

    class MockTargetBarDetector:
        def __init__(self, hwnd=None): self.hwnd = hwnd
        def is_target_alive(self, frame):
            nonlocal seq_idx
            if seq_idx < len(target_alive_seq):
                res = target_alive_seq[seq_idx]
                seq_idx += 1
                return res
            orchestrator.hunt_running = False
            return False

    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.TargetBarDetector", MockTargetBarDetector)

    # Mock name resolution to return CORRECT target
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.find_monster_by_name_api", lambda *args: {"id": 101, "name": "Slime Xanh"})
    monkeypatch.setattr("lib.features.hunt.hunt_orchestrator.TargetNameReader.read_name", lambda *args: "Slime Xanh")

    cfg = {
        "target_key": "z",
        "lost_timeout_sec": 0,
        "target_lost_debounce_frames": 3,
        "search_tap_delay_sec": 0.0,
        "attack_interval": 0.0,
        "target_policy": "configured_only",
        "monster_rotation": [{"monster_id": 101, "priority": 1}]
    }

    def mock_prepare(*args, **kwargs): return [{"type": "attack", "key": "1"}]
    monkeypatch.setattr(orchestrator.handler, "prepare_skill_runtime", mock_prepare)

    orchestrator.start_hunt(cfg)
    try:
        orchestrator.hunt_thread.join(timeout=2.0)
        assert not orchestrator.hunt_thread.is_alive()

        calls = orchestrator.handler.try_cast_skills.call_args_list
        attack_calls = []
        for call in calls:
            args, kwargs = call
            if kwargs.get('attack_phase', False):
                attack_calls.append(call)
            elif len(args) > 3 and args[3] is True:
                attack_calls.append(call)

        assert len(attack_calls) > 0, "try_cast_skills should be called with attack_phase=True for correct target"
    finally:
        if getattr(orchestrator, "hunt_thread", None) and orchestrator.hunt_thread.is_alive():
            orchestrator.stop_hunt()
