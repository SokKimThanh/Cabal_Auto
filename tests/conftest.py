"""
Pytest configuration and fixtures for Cabal_Auto tests.

This file provides:
- Import path setup for project modules
- Platform detection fixtures
- Auto-skip markers for platform-specific tests
- Common test utilities and fixtures
"""
import sys
import platform
from pathlib import Path
import pytest

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Platform detection
IS_WINDOWS = sys.platform == 'win32' or platform.system() == 'Windows'
IS_LINUX = sys.platform.startswith('linux') or platform.system() == 'Linux'
IS_MACOS = sys.platform == 'darwin' or platform.system() == 'Darwin'


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "windows: mark test as Windows-only (will skip on other platforms)"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as requiring GUI interaction"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "vision: mark test as vision/image processing test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow-running"
    )


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests based on platform markers."""
    skip_windows = pytest.mark.skip(reason="Test requires Windows platform")
    
    for item in items:
        # Auto-skip Windows-only tests on non-Windows platforms
        if "windows" in item.keywords and not IS_WINDOWS:
            item.add_marker(skip_windows)


# ============================================================================
# Fixtures - Platform Mocks
# ============================================================================

@pytest.fixture(autouse=True, scope='session')
def setup_platform_mocks():
    """Centralized platform compatibility mocks for cross-platform testing."""
    import sys
    from unittest.mock import MagicMock
    if platform.system() != 'Windows':
        mocks_dict = {
            'win32gui': MagicMock(),
            'cv2': MagicMock(),
            'numpy': MagicMock(),
            'win32con': MagicMock(),
            'win32process': MagicMock(),
            'win32api': MagicMock(),
            'pywintypes': MagicMock(),
        }
        for module_name, mock_module in mocks_dict.items():
            if module_name not in sys.modules:
                sys.modules[module_name] = mock_module
        yield
        # We generally leave sys.modules mocked for the session
    else:
        yield


# ============================================================================
# Fixtures - Platform Detection
# ============================================================================

@pytest.fixture
def is_windows():
    """Fixture that returns True if running on Windows."""
    return IS_WINDOWS


@pytest.fixture
def is_linux():
    """Fixture that returns True if running on Linux."""
    return IS_LINUX


@pytest.fixture
def is_macos():
    """Fixture that returns True if running on macOS."""
    return IS_MACOS


@pytest.fixture
def platform_name():
    """Fixture that returns the platform name."""
    return platform.system()


# ============================================================================
# Fixtures - Skip Decorators
# ============================================================================

@pytest.fixture
def skip_if_not_windows():
    """Fixture that skips test if not on Windows."""
    if not IS_WINDOWS:
        pytest.skip("Test requires Windows platform")


@pytest.fixture
def skip_if_not_linux():
    """Fixture that skips test if not on Linux."""
    if not IS_LINUX:
        pytest.skip("Test requires Linux platform")


@pytest.fixture
def skip_if_ci():
    """Fixture that skips test if running in CI environment."""
    import os
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        pytest.skip("Test skipped in CI environment")


# ============================================================================
# Fixtures - Test Utilities
# ============================================================================

@pytest.fixture
def project_root_path():
    """Fixture that returns the project root path."""
    return project_root


@pytest.fixture
def assets_path():
    """Fixture that returns the assets directory path."""
    return project_root / 'assets'


@pytest.fixture
def temp_test_dir(tmp_path):
    """Fixture that provides a temporary directory for test files."""
    return tmp_path


# ============================================================================
# Fixtures - Mock Imports (for non-Windows platforms)
# ============================================================================

@pytest.fixture
def mock_win_input():
    """
    Fixture that provides a mock win_input module for testing on non-Windows.
    
    Usage:
        def test_something(mock_win_input):
            mock_win_input.tap('1')  # Will not actually send input on non-Windows
    """
    if IS_WINDOWS:
        # On Windows, use the real module
        from lib.system import win_input
        return win_input
    else:
        # On non-Windows, use a mock
        class MockWinInput:
            @staticmethod
            def key_down(key: str):
                pass
            
            @staticmethod
            def key_up(key: str):
                pass
            
            @staticmethod
            def tap(key: str, press_ms: int = 50):
                pass
            
            IS_WINDOWS = False
        
        return MockWinInput()


# ============================================================================
# Fixtures - Vision/Image Testing
# ============================================================================

@pytest.fixture
def sample_image_path():
    """Fixture that returns path to sample test image."""
    sample_path = project_root / 'tests' / 'samples' / 'sample.png'
    if sample_path.exists():
        return sample_path
    return None


@pytest.fixture
def mock_screen_capture():
    """
    Fixture that mocks screen capture for testing without actual screenshots.
    
    Returns a function that returns a dummy image array.
    """
    def _capture(region=None):
        import numpy as np
        # Return a dummy 100x100 RGB image
        return np.zeros((100, 100, 3), dtype=np.uint8)
    
    return _capture


# ============================================================================
# Core Domain Mocks
# ============================================================================

@pytest.fixture
def mock_bot_manager():
    from unittest.mock import MagicMock
    import numpy as np

    mgr = MagicMock()
    mgr.screen_capture = MagicMock()
    mgr.screen_capture.get_latest_frame.return_value = np.zeros((1080, 1920, 3), dtype=np.uint8)
    return mgr


@pytest.fixture
def mock_orchestrator(mock_bot_manager):
    from unittest.mock import MagicMock
    from lib.features.hunt.hunt_orchestrator import HuntOrchestrator

    def sync_schedule(task):
        task()

    orch = HuntOrchestrator(
        on_status_update=MagicMock(),
        on_state_change=MagicMock(),
        locate_target=MagicMock(),
        prepare_skill_runtime=MagicMock(),
        try_cast_skills=MagicMock(),
        bring_window_to_front=MagicMock(),
        bring_window_to_front_by_hwnd=MagicMock(),
        bring_window_to_front_by_pid=MagicMock(),
        iconify_app=MagicMock(),
        update_skill_stats_display=MagicMock(),
        get_hunt_selected=MagicMock(return_value={"hwnd": 123}),
        schedule_ui_task=sync_schedule,
        clear_target_ui=MagicMock(),
        set_target_info=MagicMock(),
        on_scene_monsters_detected=MagicMock()
    )
    orch.bot_manager = mock_bot_manager
    orch.hunt_running = False
    orch.start_hunt = MagicMock(side_effect=orch.start_hunt)
    orch.stop_hunt = MagicMock(side_effect=orch.stop_hunt)
    return orch


@pytest.fixture
def mock_hunt_app(mock_orchestrator):
    from unittest.mock import MagicMock
    app = MagicMock()
    app.hunt_orchestrator = mock_orchestrator
    return app


@pytest.fixture
def mock_vision_engine():
    from unittest.mock import MagicMock
    engine = MagicMock()
    engine.detect_templates = MagicMock(return_value=[])
    engine.detect_monsters = MagicMock(return_value=[])
    return engine


# ============================================================================
# DB Mocks
# ============================================================================

@pytest.fixture
def mock_db():
    from unittest.mock import MagicMock
    db = MagicMock()
    # Provide multiple pages of monsters
    def get_filtered_monsters(keyword, monster_type, dungeon_id, page, page_size, sort_column, sort_order):
        return {
            "items": [{"id": f"m{i}", "name": f"Monster {i}"} for i in range((page-1)*page_size, page*page_size)],
            "total": 100,
            "page": page,
            "page_size": page_size
        }
    db.get_filtered_monsters = get_filtered_monsters
    return db

@pytest.fixture
def mock_db_responses():
    all_monsters = [
        {"id": 1, "name": "Slime Xanh", "level": 10, "hp": 100, "dungeonId": "d1"},
        {"id": 2, "name": "Slime Đo", "level": 12, "hp": 150, "dungeonId": None}
    ]
    search_monsters = [
        {"id": 1, "name": "Slime Xanh", "level": 10, "hp": 100, "dungeonId": "d1"}
    ]
    return all_monsters, search_monsters


# ============================================================================
# Session-level Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_session_info():
    """Fixture that provides information about the test session."""
    return {
        "platform": platform.system(),
        "python_version": sys.version,
        "is_windows": IS_WINDOWS,
        "is_linux": IS_LINUX,
        "is_macos": IS_MACOS,
        "project_root": str(project_root),
    }


@pytest.fixture(scope="session", autouse=True)
def print_test_environment(test_session_info):
    """Auto-use fixture that prints test environment info at session start."""
    print("\n" + "="*60)
    print("TEST ENVIRONMENT")
    print("="*60)
    for key, value in test_session_info.items():
        if key == "python_version":
            # Print only first line of Python version
            value = value.split('\n')[0]
        print(f"{key:20s}: {value}")
    print("="*60 + "\n")

@pytest.fixture
def patched_monster_editor(tmp_path):
    """Shared fixture for monster editor tests - patches common mocks."""
    from unittest.mock import patch

    # Create temp data file
    temp_data_file = tmp_path / "monsters.json"
    temp_data_file.write_text('[]', encoding='utf-8')

    # Create list of patches
    patches_list = [
        patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file),
        patch('ui.windows.monster_manager_win.get_db', return_value=None),
        patch('ui.windows.monster_manager_win.DataSyncManager', autospec=True),
    ]

    # Apply all patches
    mocks = [p.start() for p in patches_list]

    yield {
        'temp_data_file': temp_data_file,
        'DATA_PATH_mock': mocks[0],
        'get_db_mock': mocks[1],
        'DataSyncManager_mock': mocks[2],
        'patches': patches_list
    }

    # Stop all patches
    for p in patches_list:
        p.stop()

    # Cleanup
    try:
        if temp_data_file.exists():
            temp_data_file.unlink()
    except (PermissionError, OSError):
        import time
        time.sleep(0.05)
        try:
            temp_data_file.unlink()
        except Exception:
            pass
