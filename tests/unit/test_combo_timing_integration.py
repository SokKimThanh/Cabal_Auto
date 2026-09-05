import pytest
import time
from lib.features.skills.runtime import SkillRuntime
from lib.features.skills.cast_delivery import CastOutcome, CastReservation
from lib.features.timing.calculator import calculate_timing

@pytest.fixture
def skills_data():
    return [
        {'name': 'Fireball', 'key': '1', 'type': 'attack', 'cooldown': 2.0, 'cast_time': 1.0},
        {'name': 'Iceball', 'key': '2', 'type': 'attack', 'cooldown': 3.0, 'cast_time': 1.0},
        {'name': 'Lightning', 'key': '3', 'type': 'attack', 'cooldown': 4.0, 'cast_time': 1.0},
    ]

def test_standard_mode_advances_properly(skills_data):
    """Verify skill rotation advances using static timing intervals and APS recommendations."""
    runtime = SkillRuntime(skills_data)
    now = time.time()

    # Get attack to cast (should be Fireball)
    key = runtime.get_attack_to_cast(now)
    assert key == '1'

    # Reserve it
    res = runtime.reserve_next_skill('attack', now)
    assert res is not None
    assert res.skill_name == 'Fireball'

    # Pointer is not advanced yet
    assert runtime.attack_rotation_index == 0

    # Commit cast ACCEPTED
    runtime.commit_cast(res.token, CastOutcome.ACCEPTED, now)

    # Pointer advanced to 1
    assert runtime.attack_rotation_index == 1

    # Next skill
    key = runtime.get_attack_to_cast(now)
    assert key == '2'
    res2 = runtime.reserve_next_skill('attack', now)
    assert res2.skill_name == 'Iceball'

    # Commit REJECTED
    runtime.release_cast(res2.token, CastOutcome.REJECTED)

    # Pointer not advanced
    assert runtime.attack_rotation_index == 1

def test_combo_mode_sequential(skills_data):
    """Verify skill keys are reserved sequentially without skipping slots, and only commit_cast(ACCEPTED) advances the pointer."""
    runtime = SkillRuntime(skills_data)
    now = time.time()

    skill = runtime.get_next_combo_skill(now)
    assert skill is not None
    assert skill.name == 'Fireball'

    res = runtime.reserve_next_skill('attack', now, is_combo=True)
    assert res is not None
    assert res.skill_name == 'Fireball'
    assert runtime.combo_rotation_index == 0

    runtime.release_cast(res.token)
    assert runtime.combo_rotation_index == 0

    res2 = runtime.reserve_next_skill('attack', now, is_combo=True)
    assert res2 is not None
    runtime.commit_cast(res2.token, CastOutcome.ACCEPTED, now)

    assert runtime.combo_rotation_index == 1
def test_mode_switch_handoff(skills_data):
    """Start in Standard, advance, toggle combo, and assert it picks up."""
    runtime = SkillRuntime(skills_data)
    now = time.time()

    # Cast 1 in standard
    res1 = runtime.reserve_next_skill('attack', now, is_combo=False)
    runtime.commit_cast(res1.token, CastOutcome.ACCEPTED, now)
    assert runtime.attack_rotation_index == 1
    assert runtime.combo_rotation_index == 0

    # Toggle to combo
    runtime.sync_combo_pointer(to_combo=True)
    assert runtime.combo_rotation_index == 1

    # Cast in combo
    res2 = runtime.reserve_next_skill('attack', now, is_combo=True)
    assert res2.skill_name == 'Iceball'
    runtime.commit_cast(res2.token, CastOutcome.ACCEPTED, now)
    assert runtime.combo_rotation_index == 2

    # Toggle back to standard
    runtime.sync_combo_pointer(to_combo=False)
    assert runtime.attack_rotation_index == 2

def test_cooldown_bottleneck_warning(caplog, skills_data):
    """Construct a chain where total cast time < max cooldown, assert warning."""
    import logging

    caplog.set_level(logging.WARNING, logger="lib.features.timing.calculator")

    # max cooldown is 4.0, total cast time is 1.0+1.0+1.0 = 3.0. Bottleneck should happen!
    calculate_timing(
        monster_hp=1000,
        damage_per_hit=500,
        skill_rotation=skills_data,
    )

    assert "Bottleneck detected" in caplog.text
