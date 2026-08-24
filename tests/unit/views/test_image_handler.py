import pytest
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from views.image_handler import ImageHandler

@pytest.fixture
def mock_pil_available():
    with patch("views.image_handler.PIL_AVAILABLE", True), \
         patch("views.image_handler.Image", MagicMock()), \
         patch("views.image_handler.ImageTk", MagicMock()), \
         patch("views.image_handler.ImageDraw", MagicMock()):
        yield

@pytest.fixture
def handler():
    return ImageHandler(max_cache_size=2)

def test_get_preview_image_empty_path(handler):
    result, error = handler.get_preview_image("")
    assert result is None
    assert error == "No path provided"

    result, error = handler.get_preview_image("   ")
    assert result is None
    assert error == "No path provided"

def test_get_preview_image_file_not_found(handler, mock_pil_available):
    with patch("views.image_handler.ImageHandler._create_placeholder", return_value="mock_placeholder"):
        result, error = handler.get_preview_image("non_existent_file.png")
        assert result == "mock_placeholder"
        assert "File not found: non_existent_file.png" in error

def test_get_preview_image_pil_unavailable(handler):
    with patch("views.image_handler.PIL_AVAILABLE", False):
        with patch.object(Path, "exists", return_value=True):
            result, error = handler.get_preview_image("fake_path.png")
            assert result is None
            assert error == "PIL library not installed"

def test_get_preview_image_success(handler, mock_pil_available):
    with patch("views.image_handler.Image.open") as mock_open:
        with patch("views.image_handler.ImageTk.PhotoImage", return_value="mock_photo"):
            mock_img = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_img
            with patch.object(Path, "exists", return_value=True):
                result, error = handler.get_preview_image("fake_path.png", size=(64, 64))
                assert result == "mock_photo"
                assert error is None
                mock_img.thumbnail.assert_called_once_with((64, 64))

def test_get_preview_image_cache_hit(handler, mock_pil_available):
    with patch("views.image_handler.Image.open") as mock_open:
        with patch("views.image_handler.ImageTk.PhotoImage", return_value="mock_photo"):
            mock_img = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_img
            with patch.object(Path, "exists", return_value=True):
                # First call should load and cache
                result1, error1 = handler.get_preview_image("fake_path.png")
                assert result1 == "mock_photo"
                assert error1 is None
                assert mock_open.call_count == 1

                # Second call should hit the cache
                result2, error2 = handler.get_preview_image("fake_path.png")
                assert result2 == "mock_photo"
                assert error2 is None
                assert mock_open.call_count == 1 # Still 1

def test_get_preview_image_cache_eviction(handler, mock_pil_available):
    # handler fixture has max_cache_size=2
    with patch("views.image_handler.Image.open") as mock_open:
        mock_photos = ["photo1", "photo2", "photo3"]
        with patch("views.image_handler.ImageTk.PhotoImage", side_effect=mock_photos):
            mock_img = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_img
            with patch.object(Path, "exists", return_value=True):
                # Fill cache
                handler.get_preview_image("file1.png")
                handler.get_preview_image("file2.png")
                assert len(handler._cache) == 2

                # Add 3rd item, should evict the oldest (file1.png)
                handler.get_preview_image("file3.png")
                assert len(handler._cache) == 2

                # Check contents
                keys = list(handler._cache.keys())
                assert any("file2.png" in k for k in keys)
                assert any("file3.png" in k for k in keys)
                assert not any("file1.png" in k for k in keys)

def test_get_preview_image_exception_handling(handler, mock_pil_available):
    with patch("views.image_handler.Image.open", side_effect=Exception("Read error")):
        with patch.object(Path, "exists", return_value=True):
            with patch.object(handler, "_create_placeholder", return_value="mock_placeholder"):
                result, error = handler.get_preview_image("corrupt_file.png")
                assert result == "mock_placeholder"
                assert "Failed to read image: Read error" in error

def test_clear_cache(handler):
    handler._cache = {"key1": "val1", "key2": "val2"}
    assert len(handler._cache) == 2
    handler.clear_cache()
    assert len(handler._cache) == 0

def test_create_placeholder_success(mock_pil_available):
    handler = ImageHandler()
    with patch("views.image_handler.Image.new", create=True) as mock_new:
        mock_img = MagicMock()
        mock_new.return_value = mock_img
        with patch("views.image_handler.ImageTk.PhotoImage", return_value="mock_placeholder_photo"):
            # Disable ImageDraw logic since we are mocking image itself
            with patch("views.image_handler.ImageDraw", None):
                result = handler._create_placeholder((32, 32), "test")
                assert result == "mock_placeholder_photo"
                mock_new.assert_called_once_with("RGB", (32, 32), color=(220, 220, 220))

def test_create_placeholder_pil_unavailable():
    handler = ImageHandler()
    with patch("views.image_handler.PIL_AVAILABLE", False):
        result = handler._create_placeholder((32, 32), "test")
        assert result is None

def test_create_placeholder_exception(mock_pil_available):
    handler = ImageHandler()
    with patch("views.image_handler.Image.new", create=True, side_effect=Exception("Fake error")):
        result = handler._create_placeholder((32, 32), "test")
        assert result is None


def test_get_preview_image_absolute_path(handler, mock_pil_available):
    with patch("views.image_handler.Image.open") as mock_open:
        with patch("views.image_handler.ImageTk.PhotoImage", return_value="mock_photo"):
            mock_img = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_img
            with patch.object(Path, "exists", return_value=True):
                # An absolute path on linux looks like /some/path
                abs_path_str = "/fake/absolute/path.png"
                result, error = handler.get_preview_image(abs_path_str)
                assert result == "mock_photo"
                assert error is None


def test_create_placeholder_imagedraw(mock_pil_available):
    handler = ImageHandler()
    with patch("views.image_handler.Image.new", create=True) as mock_new:
        mock_img = MagicMock()
        mock_new.return_value = mock_img
        with patch("views.image_handler.ImageTk.PhotoImage", return_value="mock_placeholder_photo"):
            # We need to mock ImageDraw itself
            with patch("views.image_handler.ImageDraw") as mock_draw_module:
                mock_draw = MagicMock()
                mock_draw_module.Draw.return_value = mock_draw

                result = handler._create_placeholder((32, 32), "test")
                assert result == "mock_placeholder_photo"

                # Verify ImageDraw was called
                mock_draw_module.Draw.assert_called_once_with(mock_img)
                mock_draw.rectangle.assert_called_once_with([(0, 0), (31, 31)], outline=(180, 180, 180))
