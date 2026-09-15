# Review Prompt 025: Extract Monster Rotation Logic

## Verification Steps
1. Search `app_gui.py` to confirm deletion of monster UI handlers (e.g., `_on_monster_move_up`, `_refresh_monster_rotation_list`, `on_scene_monsters_detected`).
2. Verify these methods have been integrated into a dedicated `MonsterRotationView` or the existing `HuntTab` component.
3. Check that UI click events (add, move, delete) are routed to `MonsterRotationController` via `EventBus`.
4. Ensure the view synchronizes data properly with `AppStateController` to prevent processing stale listbox states.

## Checklist
- [x] Monster UI handler methods deleted from `app_gui.py`.
- [x] Logic implemented in `MonsterRotationView` or `HuntTab`.
- [x] Click events use `EventBus` to notify `MonsterRotationController`.
- [x] Monster detection auto-mapping continues to work flawlessly.
