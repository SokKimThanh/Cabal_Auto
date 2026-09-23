import pytest
from unittest.mock import MagicMock
from ui.controllers.skill_panel_controller import SkillPanelController

@pytest.fixture
def app_state():
    mock_state = MagicMock()
    # In tests, simulate the new getter helper instead of a direct dict attribute
    mock_cfg = {
        "skill_slots": [
            {"type": "attack", "name": "Fireball"},
            {"type": "attack", "name": "Ice Lance"},
        ],
        "buff_slots": [
            {"type": "buff", "name": "Shield"},
        ]
    }

    def mock_get_hunt_config_value(key, default=None):
        return mock_cfg.get(key, default)

    mock_state.get_hunt_config_value = mock_get_hunt_config_value

    def mock_set_hunt_config_value(key, value):
        mock_cfg[key] = value

    mock_state.set_hunt_config_value = mock_set_hunt_config_value

    return mock_state

def test_get_combo_sequence(app_state):
    controller = SkillPanelController(app_state)
    sequence = controller.get_combo_sequence()
    assert isinstance(sequence, list)
    assert len(sequence) == 2
    assert sequence[0]["name"] == "Fireball"
    assert sequence[1]["name"] == "Ice Lance"

def test_get_buff_sequence(app_state):
    controller = SkillPanelController(app_state)
    sequence = controller.get_buff_sequence()
    assert isinstance(sequence, list)
    assert len(sequence) == 1
    assert sequence[0]["name"] == "Shield"

def test_sequence_mutation(app_state):
    controller = SkillPanelController(app_state)

    # Test mutation on combo sequence
    combo_seq = controller.get_combo_sequence()
    initial_length = len(combo_seq)

    # Adding a skill to the underlying list
    combo_seq.append({"type": "attack", "name": "Lightning"})

    # Check if the sequence reflects the change
    updated_seq = controller.get_combo_sequence()
    assert len(updated_seq) == initial_length + 1
    assert updated_seq[-1]["name"] == "Lightning"

    # Removing a skill
    updated_seq.pop()
    final_seq = controller.get_combo_sequence()
    assert len(final_seq) == initial_length
