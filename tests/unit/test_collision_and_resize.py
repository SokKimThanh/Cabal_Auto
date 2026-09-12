import os
from pathlib import Path
from PIL import Image
import pytest
from unittest.mock import patch
from lib.managers.icon_file_manager import import_icon_file

@pytest.fixture
def mock_icons_dir(tmp_path):
    with patch('lib.managers.icon_file_manager.get_icons_directory', return_value=tmp_path):
        yield tmp_path

def test_collision(mock_icons_dir, tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create dummy source image
    source_file = source_dir / "test.png"
    img = Image.new('RGB', (64, 64))
    img.save(source_file)

    # Import first time
    name1 = import_icon_file(str(source_file))
    assert name1 == "test.png"
    assert (mock_icons_dir / "test.png").exists()

    # Import second time
    name2 = import_icon_file(str(source_file))
    assert name2 == "test_1.png"
    assert (mock_icons_dir / "test_1.png").exists()

def test_resize_large_image(mock_icons_dir, tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create large dummy source image
    source_file = source_dir / "large.png"
    img = Image.new('RGB', (500, 300))
    img.save(source_file)

    name = import_icon_file(str(source_file))

    # Verify it was resized
    target_path = mock_icons_dir / name
    with Image.open(target_path) as resized:
        width, height = resized.size
        assert max(width, height) <= 128
        assert width == 128
        assert height in (76, 77)
