import pytest
from unittest.mock import patch
from lib.features.skills.skill_runtime_service import SkillRuntimeService

@patch("lib.features.skills.skill_runtime_service.load_skill_library")
def test_skill_runtime_service_normalizes_data(mock_load):
    mock_load.return_value = {
        "fireball": {"type": "attack", "cooldown": 5.0}
    }

    service = SkillRuntimeService()
    skills = service.get_all_skills()

    assert len(skills) == 1
    assert skills[0]["name"] == "fireball"
    assert skills[0]["id"] == "fireball"

@patch("lib.features.skills.skill_runtime_service.load_skill_library")
def test_skill_runtime_service_normalizes_list_data(mock_load):
    mock_load.return_value = [
        {"id": "fireball", "type": "attack", "cooldown": 5.0}
    ]

    service = SkillRuntimeService()
    skills = service.get_all_skills()

    assert len(skills) == 1
    assert skills[0]["name"] == "fireball"
    assert skills[0]["id"] == "fireball"

@patch("lib.features.skills.skill_runtime_service.load_skill_library")
def test_skill_runtime_service_handles_corrupt_data(mock_load):
    mock_load.return_value = "this is a string, not a dict"

    service = SkillRuntimeService()
    skills = service.get_all_skills()

    assert isinstance(skills, list)
    assert len(skills) == 0

@patch("lib.features.skills.skill_runtime_service.save_skill_library")
def test_skill_runtime_service_save_skills(mock_save):
    mock_save.return_value = True

    service = SkillRuntimeService()
    result = service.save_skills({"fireball": {"name": "fireball"}})

    assert result is True
    mock_save.assert_called_once_with({"fireball": {"name": "fireball"}})
