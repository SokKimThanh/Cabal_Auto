import pytest
from lib.features.hunt.target_rotation_coordinator import TargetRotationCoordinator

def test_empty_rotation_no_attack():
    coord = TargetRotationCoordinator("configured_only", [])
    assert not coord.is_rotation_valid()
    assert coord.evaluate_target(101, True) == TargetRotationCoordinator.UNKNOWN

def test_sequence_wrap_around():
    rotation = [{"monster_id": 101, "priority": 1}, {"monster_id": 205, "priority": 2}]
    coord = TargetRotationCoordinator("configured_only", rotation)
    assert coord.get_desired_target()["monster_id"] == 101
    coord.advance_pointer()
    assert coord.get_desired_target()["monster_id"] == 205
    coord.advance_pointer()
    assert coord.get_desired_target()["monster_id"] == 101 # wrapped

def test_priority_sorting():
    rotation = [
        {"monster_id": 300, "priority": 3},
        {"monster_id": 100, "priority": 1},
        {"monster_id": 200, "priority": 2}
    ]
    coord = TargetRotationCoordinator("configured_only", rotation)
    assert coord.configured_rotation[0]["monster_id"] == 100
    assert coord.configured_rotation[1]["monster_id"] == 200
    assert coord.configured_rotation[2]["monster_id"] == 300

def test_match_and_mismatch_logic():
    rotation = [{"monster_id": 101, "priority": 1}]
    coord = TargetRotationCoordinator("configured_only", rotation)
    assert coord.evaluate_target(101, True) == TargetRotationCoordinator.MATCHED
    assert coord.evaluate_target(205, True) == TargetRotationCoordinator.MISMATCH

def test_unknown_ocr_id_0():
    rotation = [{"monster_id": 101, "priority": 1}]
    coord = TargetRotationCoordinator("configured_only", rotation)
    assert coord.evaluate_target(0, True) == TargetRotationCoordinator.UNKNOWN
    assert coord.evaluate_target(None, True) == TargetRotationCoordinator.UNKNOWN

def test_id_normalization():
    rotation = [{"monster_id": "101", "priority": 1}]
    coord = TargetRotationCoordinator("configured_only", rotation)
    assert coord.configured_rotation[0]["monster_id"] == 101
    assert coord.evaluate_target("101", True) == TargetRotationCoordinator.MATCHED

def test_advance_pointer_once():
    rotation = [{"monster_id": 101, "priority": 1}, {"monster_id": 205, "priority": 2}]
    coord = TargetRotationCoordinator("configured_only", rotation)
    # Target mismatch doesn't advance
    assert coord.evaluate_target(205, True) == TargetRotationCoordinator.MISMATCH
    assert coord.get_desired_target()["monster_id"] == 101
    # Advance simulates confirmed completion
    coord.advance_pointer()
    assert coord.get_desired_target()["monster_id"] == 205

def test_all_resolved_policy():
    coord = TargetRotationCoordinator("all_resolved", [])
    runtime_queue = [
        {"monster_id": 205, "match_type": "db_match"},
        {"monster_id": 101, "match_type": "db_match"}
    ]
    coord.update_runtime_queue(runtime_queue)
    assert coord.evaluate_target(205, True) == TargetRotationCoordinator.MATCHED
    assert coord.evaluate_target(101, True) == TargetRotationCoordinator.MISMATCH # Active is first seen (205)

    # Missing from queue
    assert coord.evaluate_target(300, True) == TargetRotationCoordinator.MISMATCH

    coord.advance_pointer()
    assert coord.evaluate_target(101, True) == TargetRotationCoordinator.MATCHED

def test_any_target_policy():
    coord = TargetRotationCoordinator("any_target", [])
    assert coord.evaluate_target(None, True) == TargetRotationCoordinator.MATCHED
    assert coord.evaluate_target(0, True) == TargetRotationCoordinator.MATCHED
    assert coord.evaluate_target(101, True) == TargetRotationCoordinator.MATCHED
    # Doesn't advance specific ID
    coord.advance_pointer()
    assert coord.get_desired_target() == {"name": "Any Target", "monster_id": None}
