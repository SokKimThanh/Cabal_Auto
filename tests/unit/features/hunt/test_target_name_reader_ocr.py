import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from lib.vision.target_name_reader import TargetNameReader

def test_target_name_reader_fast_fail_pytesseract():
    with patch("lib.vision.target_name_reader.pytesseract", None):
        reader = TargetNameReader()
        with pytest.raises(RuntimeError) as excinfo:
            reader.read_name(np.zeros((1080, 1920, 3), dtype=np.uint8))
        assert "Tesseract Python wrapper missing" in str(excinfo.value)

def test_target_name_reader_fast_fail_tesseract_binary():
    with patch("lib.vision.target_name_reader.pytesseract", MagicMock()):
        with patch("lib.vision.target_name_reader.TESSERACT_CMD", None):
            reader = TargetNameReader()
            with pytest.raises(RuntimeError) as excinfo:
                reader.read_name(np.zeros((1080, 1920, 3), dtype=np.uint8))
            assert "Tesseract binary missing from PATH" in str(excinfo.value)

def test_target_name_reader_success():
    mock_pytesseract = MagicMock()
    mock_pytesseract.image_to_string.return_value = "Mocked Monster"

    with patch("lib.vision.target_name_reader.pytesseract", mock_pytesseract):
        with patch("lib.vision.target_name_reader.TESSERACT_CMD", "dummy_path"):
            reader = TargetNameReader()
            frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
            name = reader.read_name(frame)

            assert name == "Mocked Monster"
            assert mock_pytesseract.image_to_string.called
