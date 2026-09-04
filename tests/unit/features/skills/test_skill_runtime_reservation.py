import time

from lib.features.skills.cast_delivery import CastOutcome
from lib.features.skills.runtime import SkillRuntime


def test_reserve_commit_release():
    skills_data = [
        {'name': 'Fireball', 'key': '1', 'type': 'attack', 'cooldown': 5.0},
        {'name': 'Iceball', 'key': '2', 'type': 'attack', 'cooldown': 5.0},
    ]
    runtime = SkillRuntime(skills_data)

    now = time.time()

    # Initial rotation is 0 (Fireball)
    assert runtime.attack_rotation_index == 0

    res1 = runtime.reserve_next_skill('attack', now)
    assert res1.skill_name == 'Fireball'

    # Reserving does not advance rotation index
    assert runtime.attack_rotation_index == 0

    # If rejected/released, still does not advance
    runtime.release_cast(res1.token, CastOutcome.REJECTED)
    assert runtime.attack_rotation_index == 0

    res2 = runtime.reserve_next_skill('attack', now)
    assert res2.skill_name == 'Fireball'

    # If accepted, we commit, advancing rotation
    runtime.commit_cast(res2.token, res2, now)
    assert runtime.attack_rotation_index == 1

    # Fireball is now on cooldown
    assert runtime.attack_skills[0].last_cast_time == now

    res3 = runtime.reserve_next_skill('attack', now)
    assert res3.skill_name == 'Iceball'
