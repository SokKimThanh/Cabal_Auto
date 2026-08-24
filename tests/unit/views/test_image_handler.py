import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from views.image_handler import ImageHandler

def test_image_handler_init():
    handler = ImageHandler(max_cache_size=10)
    assert handler.max_cache_size == 10
    assert len(handler._cache) == 0

def test_get_preview_image_empty_path():
    handler = ImageHandler()
    photo, error = handler.get_preview_image("")
    assert photo is None
    assert error == "No path provided"

@patch('views.image_handler.PIL_AVAILABLE', False)
def test_get_preview_image_pil_unavailable():
    handler = ImageHandler()
    photo, error = handler.get_preview_image("some_path.png")
    assert photo is None
    assert error == "PIL library not installed"

def test_get_preview_image_file_not_found(tmp_path):
    handler = ImageHandler()

    missing_file = tmp_path / "missing.png"

    with patch('views.image_handler.PIL_AVAILABLE', True), \
         patch('views.image_handler.Image') as mock_image, \
         patch('views.image_handler.ImageTk') as mock_imagetk, \
         patch('views.image_handler.ImageDraw') as mock_imagedraw:

        mock_photo = MagicMock()
        mock_imagetk.PhotoImage.return_value = mock_photo

        photo, error = handler.get_preview_image(str(missing_file))

        assert photo == mock_photo  # Returns placeholder
        assert "File not found" in error
        mock_imagetk.PhotoImage.assert_called_once()


def test_get_preview_image_success(tmp_path):
    # Mock file existence
    valid_file = tmp_path / "valid.png"
    valid_file.touch()

    handler = ImageHandler()

    with patch('views.image_handler.PIL_AVAILABLE', True), \
         patch('views.image_handler.Image') as mock_image, \
         patch('views.image_handler.ImageTk') as mock_imagetk:

        # Mock Image.open context manager
        mock_img_instance = MagicMock()
        mock_image.open.return_value.__enter__.return_value = mock_img_instance
        mock_photo = MagicMock()
        mock_imagetk.PhotoImage.return_value = mock_photo

        photo, error = handler.get_preview_image(str(valid_file))

        assert photo == mock_photo
        assert error is None
        mock_img_instance.thumbnail.assert_called_once_with((96, 96))

        # Check if caching works
        photo2, error2 = handler.get_preview_image(str(valid_file))
        assert photo2 == mock_photo
        assert error2 is None
        assert mock_image.open.call_count == 1  # Should hit cache, open shouldn't be called again


def test_get_preview_image_read_error(tmp_path):
    # Mock file existence
    corrupt_file = tmp_path / "corrupt.png"
    corrupt_file.touch()

    handler = ImageHandler()

    with patch('views.image_handler.PIL_AVAILABLE', True), \
         patch('views.image_handler.Image') as mock_image, \
         patch('views.image_handler.ImageTk') as mock_imagetk, \
         patch('views.image_handler.ImageDraw') as mock_imagedraw:

        # Make Image.open raise an exception
        mock_image.open.side_effect = Exception("Corrupt image data")

        # Mock the placeholder creation
        mock_photo = MagicMock()
        mock_imagetk.PhotoImage.return_value = mock_photo

        photo, error = handler.get_preview_image(str(corrupt_file))

        assert photo == mock_photo  # Returns placeholder
        assert "Failed to read image" in error
        assert "Corrupt image data" in error


def test_cache_eviction(tmp_path):
    handler = ImageHandler(max_cache_size=2)

    with patch('views.image_handler.PIL_AVAILABLE', True), \
         patch('views.image_handler.Image') as mock_image, \
         patch('views.image_handler.ImageTk') as mock_imagetk:

        for i in range(3):
            file_path = tmp_path / f"img_{i}.png"
            file_path.touch()

            mock_img_instance = MagicMock()
            mock_image.open.return_value.__enter__.return_value = mock_img_instance
            mock_photo = MagicMock()
            mock_imagetk.PhotoImage.return_value = mock_photo

            handler.get_preview_image(str(file_path))

        assert len(handler._cache) == 2
        # The first image (img_0.png) should be evicted
        evicted_path = tmp_path / "img_0.png"
        cache_key = f"{evicted_path.resolve()}_96x96"
        assert cache_key not in handler._cache

def test_clear_cache():
    handler = ImageHandler()
    handler._cache['some_key'] = 'some_val'
    handler.clear_cache()
    assert len(handler._cache) == 0
