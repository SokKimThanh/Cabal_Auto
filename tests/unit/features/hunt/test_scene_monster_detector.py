import pytest
from unittest.mock import MagicMock
from lib.features.hunt.scene_monster_detector import SceneMonsterDetector
from lib.features.hunt.runtime_monster_queue import RuntimeMonsterQueue
from lib.vision.vision_engine import Detection

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_vision_engine():
    engine = MagicMock()

    # Setup mock templates
    tmpl1 = MagicMock()
    tmpl1.id = "t1"
    tmpl1.enabled = True
    tmpl1.monster_id = 1
    tmpl1.dungeon_id = None

    tmpl2 = MagicMock()
    tmpl2.id = "t2"
    tmpl2.enabled = True
    tmpl2.monster_id = None
    tmpl2.dungeon_id = None

    engine.templates = {"t1": tmpl1, "t2": tmpl2}

    return engine

def test_scene_monster_detector_pipeline(mock_vision_engine, monkeypatch):
    # Mock DB lookup
    def mock_get_monster_by_id_api(monster_id):
        if monster_id == "1":
            return {"id": 1, "name": "Slime DB"}
        return None
    monkeypatch.setattr("lib.features.hunt.scene_monster_detector.get_monster_by_id_api", mock_get_monster_by_id_api)

    queue = RuntimeMonsterQueue()
    detector = SceneMonsterDetector(mock_vision_engine, queue)

    # Mock detection results
    det1 = Detection(x=10, y=10, w=20, h=20, score=0.9, template_id="t1")
    # This shouldn't be matched because we only pass valid templates, but let's test safety
    det2 = Detection(x=50, y=50, w=20, h=20, score=0.8, template_id="t2")

    mock_vision_engine.detect_monster_pipeline.return_value = [det1, det2]

    # Mock frame with size
    mock_frame = MagicMock()
    mock_frame.size = 100

    # Process
    detector.process_frame(mock_frame)

    # Verify detect_monster_pipeline was called correctly
    mock_vision_engine.detect_monster_pipeline.assert_called_once()
    kwargs = mock_vision_engine.detect_monster_pipeline.call_args[1]
    assert kwargs.get("use_fast_hsv") is False
    assert "t1" in kwargs.get("template_ids")
    assert "t2" not in kwargs.get("template_ids")

    # Verify queue snapshot
    snap = queue.get_snapshot()
    assert len(snap) == 2

    item1 = next(i for i in snap if i["template_id"] == "t1")
    assert item1["monster_id"] == 1
    assert item1["resolution_state"] == "db_match"
    assert item1["name"] == "Slime DB"

    item2 = next(i for i in snap if i["template_id"] == "t2")
    assert item2["monster_id"] == 0
    assert item2["resolution_state"] == "unmapped_visual"
