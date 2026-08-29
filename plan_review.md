# Proposed Plan

The task requires fixing two major issues around pending changes and pagination in the `MonsterManagerWin` UI and its edit dialog (`MonsterEditDialog`).

## Issues identified
1. **Pagination causing data loss on refresh**: When a new monster is added (or edited) via `MonsterEditDialog`, it is saved in `pending_changes` and appended to `self.monsters`. Then `_refresh_monster_table()` is immediately called. `_refresh_monster_table()` queries the database with the *current page* limit/offset, which likely won't contain the newly created monster yet (since it's only in `pending_changes` and not the DB). `_refresh_monster_table()` then loops through the returned DB page, updating existing records in the page with `pending_changes`, but **it discards any pending records that are not in the DB page**. This means newly added records disappear from the UI entirely (though they still exist in `pending_changes` for saving).
2. **Duplicate name validation is constrained to the visible page**: `MonsterEditDialog._on_save` checks for duplicates by passing `self.parent.monsters` (which is `manager.monsters`, i.e., just the current visible page). It needs to check against the entire dataset to prevent duplicate names on different pages.

## Proposed Fixes
1. **Fix duplicate name validation**:
   - In `MonsterEditDialog._on_save`, instead of just checking `getattr(self.parent, "monsters", [])`, we check against the full dataset if possible.
   - We will add a method to `MonsterManagerWin` called `get_all_monsters_for_validation()` which queries the database for all monsters (or uses `self.db.get_all_monsters()`/fallback list + pending changes) to get a complete list.
   - We update `MonsterEditDialog._on_save` to use this new method: `monsters_list = getattr(self.parent, "get_all_monsters_for_validation", lambda: getattr(self.parent, "monsters", []))()`.

2. **Fix pending data loss on pagination**:
   - In `MonsterManagerWin._refresh_monster_table()`:
     - After fetching `self.filtered_monsters` from the DB and applying `pending_changes` to existing items in the page, we need to find all pending changes that are *not* currently in `self.filtered_monsters`.
     - We will prepend or append these "orphaned" pending changes to `self.filtered_monsters` so they remain visible on the UI, ensuring the user can see their unsaved edits and new additions regardless of what page they are on.

3. **Verify the fixes**:
   - Run our `test_pagination.py` and `test_duplicate.py` scripts to verify the behavior.
   - I will use `xvfb-run -a pytest ...` to run the UI tests and manually verify the changes.

I will request a plan review for this.
