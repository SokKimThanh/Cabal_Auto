import pytest
from unittest.mock import patch

from lib.managers.icon_file_manager import import_icon_file, delete_icon_file
from ui.helpers.icon_helper import IconHelper


@pytest.fixture
def mock_icons_dir(tmp_path):
    with patch('lib.managers.icon_file_manager.get_icons_directory', return_value=tmp_path):
        yield tmp_path


def test_import_icon_file(mock_icons_dir, tmp_path):
    # Create a separate dir for source files so they don't share tmp_path directly
    # with the mocked target dir and cause SameFileError.
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create a dummy source file
    source_file = source_dir / "dummy_source.png"
    source_file.write_text("dummy image data")

    # Test importing with default name
    imported_name = import_icon_file(str(source_file))
    assert imported_name == "dummy_source.png"
    assert (mock_icons_dir / "dummy_source.png").exists()

    # Test importing with new name
    imported_name2 = import_icon_file(str(source_file), "new_name.ico")
    assert imported_name2 == "new_name.ico"
    assert (mock_icons_dir / "new_name.ico").exists()


def test_delete_icon_file(mock_icons_dir):
    # Create a file in the target directory
    target_file = mock_icons_dir / "to_delete.png"
    target_file.write_text("data")

    # Test successful delete
    assert delete_icon_file("to_delete.png") is True
    assert not target_file.exists()

    # Test deleting non-existent file
    assert delete_icon_file("non_existent.png") is False

    # Test empty filename
    assert delete_icon_file("") is False


@pytest.fixture
def icon_helper_with_mock_dirs(tmp_path):
    helper = IconHelper()
    # Override icon directories to point to tmp_path
    helper.icon_dirs = [tmp_path]
    return helper, tmp_path


def test_resolve_icon_display(icon_helper_with_mock_dirs):
    helper, mock_dir = icon_helper_with_mock_dirs

    # Create test files
    png_file = mock_dir / "test_icon.png"
    ico_file = mock_dir / "test_icon.ico"

    # Test Priority 1: PNG exists
    png_file.write_text("png data")
    ico_file.write_text("ico data")

    data = {'filepath': 'test_icon.xxx', 'fallback_emoji': '🔥'}
    path, res_type, success = helper.resolve_icon_display(data)
    assert path == str(png_file)
    assert res_type == "image"
    assert success is True

    # Test Priority 2: PNG deleted, ICO exists
    png_file.unlink()
    path, res_type, success = helper.resolve_icon_display(data)
    assert path == str(ico_file)
    assert res_type == "image"
    assert success is True

    # Test Priority 3: Both deleted, Fallback to Emoji
    ico_file.unlink()
    path, res_type, success = helper.resolve_icon_display(data)
    assert path == '🔥'
    assert res_type == "text"
    assert success is False

    # Test Priority 3 with empty fallback emoji (should use default)
    data_no_emoji = {'filepath': 'test_icon.xxx'}
    path, res_type, success = helper.resolve_icon_display(data_no_emoji)
    assert path == '❓'
    assert res_type == "text"
    assert success is False


def test_evaluate_icon_status(icon_helper_with_mock_dirs):
    helper, mock_dir = icon_helper_with_mock_dirs

    # Case 1: GREEN - File exists
    png_file = mock_dir / "green_icon.png"
    png_file.write_text("data")
    assert helper.evaluate_icon_status({'filepath': 'green_icon.png'}) == "GREEN"

    # Case 2: YELLOW - Intentional Fallback (empty filepath, has emoji)
    assert helper.evaluate_icon_status({'filepath': '', 'fallback_emoji': '🌟'}) == "YELLOW"
    assert helper.evaluate_icon_status({'fallback_emoji': '🌟'}) == "YELLOW"

    # Case 3: RED - Missing file
    assert helper.evaluate_icon_status({'filepath': 'missing_icon.png', 'fallback_emoji': '🌟'}) == "RED"

    # Case 4: RED - Both empty
    assert helper.evaluate_icon_status({'filepath': '', 'fallback_emoji': ''}) == "RED"
    assert helper.evaluate_icon_status({}) == "RED"
