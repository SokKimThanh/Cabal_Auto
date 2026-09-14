# Sprint 30 Phase 4 Prompt 025: Extract Monster Rotation Logic

## Goal
Extract all monster rotation and selection UI logic from `app_gui.py`.

## Details
- Relocate functions like `_on_monster_move_up`, `_on_monster_move_down`, `_on_monster_delete_from_list`, `_on_monster_add_smart`, and `_refresh_monster_rotation_list` to a dedicated `MonsterRotationView` or existing `HuntTab`.
- Relocate detection and snapshot mapping methods like `on_scene_monsters_detected` and `_update_detected_monsters_list`.
- Route UI click events directly to `MonsterRotationController` using `EventBus` instead of passing them through the `App` god class.

## Acceptance Criteria
- Over 300 lines of monster rotation UI logic are completely removed from `app_gui.py`.
- Adding, moving, and deleting monsters in the rotation list functions identically.
- `pylint app_gui.py` remains at 10.0.
