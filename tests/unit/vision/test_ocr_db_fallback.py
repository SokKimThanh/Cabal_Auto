import pytest
import numpy as np
import time
from unittest.mock import MagicMock, patch
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
from lib.vision.target_name_reader import TargetNameReader
import lib.vision.target_name_reader

class TestOCRDBFallbackContract:
    def test_ocr_db_fallback_contract(self):
        """Verify that OCR fallback dictates id=0, hp=None, defense=None."""
        from lib.features.hunt.scene_monster_detector import SceneMonsterDetector
        vision_engine = MagicMock()
        runtime_queue = MagicMock()

        # Test SceneMonsterDetector enqueue fallback contract for DB Miss
        detector = SceneMonsterDetector(vision_engine, runtime_queue)

        det = MagicMock()
        det.template_id = "test_tmpl"
        det.score = 0.9
        det.bbox.return_value = (0, 0, 100, 100)

        tmpl = MagicMock()
        tmpl.id = "test_tmpl"
        tmpl.monster_id = "9999"  # Unknown ID
        tmpl.dungeon_id = None
        tmpl.enabled = True

        vision_engine.templates = {"test_tmpl": tmpl}
        vision_engine.detect_monster_pipeline.return_value = [det]

        with patch('lib.features.hunt.scene_monster_detector.get_monster_by_id_api', return_value=None):
            detector.process_frame(np.zeros((10, 10)))

            # The runtime queue add_or_update should be called with id=0 and name="Unknown target"
            runtime_queue.add_or_update.assert_called_with(
                monster_id=0,
                name="Unknown target",
                bbox=(0, 0, 100, 100),
                confidence=0.9,
                template_id="test_tmpl",
                resolution_state="db_miss",
                dungeon_id=None
            )

    @patch('lib.vision.target_name_reader.TargetNameReader._get_roi')
    def test_ocr_failure_safe(self, mock_get_roi):
        """Verify OCR fails safely when pytesseract throws or returns empty."""
        original_pytesseract = getattr(lib.vision.target_name_reader, 'pytesseract', None)
        original_tesseract_cmd = getattr(lib.vision.target_name_reader, 'TESSERACT_CMD', None)

        try:
            lib.vision.target_name_reader.pytesseract = MagicMock()
            lib.vision.target_name_reader.TESSERACT_CMD = "tesseract"

            reader = TargetNameReader()
            mock_get_roi.return_value = None
            result = reader.read_name(np.zeros((100, 100, 3), dtype=np.uint8))
            assert result == ""
        finally:
            lib.vision.target_name_reader.pytesseract = original_pytesseract
            lib.vision.target_name_reader.TESSERACT_CMD = original_tesseract_cmd

    def test_ocr_fallback_tesseract_mock(self):
        """Verify OCR handles generic text resolution and fallback."""
        original_pytesseract = getattr(lib.vision.target_name_reader, 'pytesseract', None)
        original_tesseract_cmd = getattr(lib.vision.target_name_reader, 'TESSERACT_CMD', None)

        try:
            mock_pytesseract = MagicMock()
            mock_pytesseract.image_to_string.return_value = "Unknown Monster "
            lib.vision.target_name_reader.pytesseract = mock_pytesseract
            lib.vision.target_name_reader.TESSERACT_CMD = "tesseract"

            reader = TargetNameReader()

            frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

            text = reader.read_name(frame)
            assert text == "Unknown Monster"
        finally:
            lib.vision.target_name_reader.pytesseract = original_pytesseract
            lib.vision.target_name_reader.TESSERACT_CMD = original_tesseract_cmd
