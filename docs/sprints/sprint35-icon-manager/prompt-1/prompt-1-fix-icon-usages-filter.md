# Prompt 1: Fix Icon Usages Filter and UI Element Sync

## Objective (Goal)
To improve the usability of the Icon Manager by allowing users to easily identify, highlight, and filter UI buttons that are mapped to icons with missing visual images (displaying a question mark `❓` fallback). Additionally, resolve a technical debt issue where dynamically loaded UI buttons were missing from the Icon Manager lists until an application restart.

## Scope
- Update `ui/views/icon_manager_frame.py` to evaluate icon statuses (`GREEN`, `YELLOW`, `RED`) dynamically via the SQLite `icons` table.
- Apply Treeview tag styling (`error`) to color missing icon mappings in red text.
- Add a "Filter Errors" toggle checkbox (`var_filter_errors_only`) to easily view only problematic buttons.
- Update `_load_all_usage_ids` to fetch and display uninstantiated UI elements directly from the `ui_elements` database table to bypass UIElementRegistry lazy loading limitations.
- Address technical debt in `lib/events/ui_element_registry.py` and `lib/db/services/icon_sync_manager.py` by introducing a `UIElementRegisteredEvent` to live-sync new UI button registrations to the database instantly.

## Definition of Done
1. UI elements with broken/missing icon mappings display in red text within the Usages tree view.
2. A checkbox labeled "Chỉ hiện các UI Button bị lỗi Icon" effectively filters out healthy mappings.
3. The Usages tree view populates fully with all buttons tracked in the `ui_elements` database table, not just those currently loaded into memory.
4. New buttons dynamically spawned by `create_icon_button` save instantly to the DB via `EventBus` without needing a system restart.
5. Code passes existing test suites and avoids regressions.

## Impact Analysis
- Modifies Icon Manager tree building logic (`IconManagerFrame`). Minor performance footprint by running database status queries in a background thread.
- `IconSyncManager` now binds to the event bus, producing minimal extra I/O during real-time UI construction. No circular dependencies established.

## Acceptance Test (Scenario-based)
- Given the Icon Manager is open, When a user clicks the "Chỉ hiện các UI Button bị lỗi Icon" checkbox, Then only buttons mapped to missing icons or default emojis should remain visible.
- Given a new tab with a new `create_icon_button` is opened for the first time, When navigating back to Icon Manager, Then the new button should instantly appear in the "Available Elements" list.

## Risks
- Potential `_tkinter.TclError` if trying to insert or style tree nodes concurrently across threads. Handled by executing DB reads in background while batching Tree inserts directly via `_apply_element_filter`.

## Anti-patterns
- Deferring DB synchronization strictly to startup payloads (`sync_registry_to_db`). Overcome by dispatching an event stream for real-time upserts.
- Direct database calls within the Tkinter mainloop. Solved by pushing SQLite connections to threading.

## Rollback Plan
- Revert the three commits associated with branch `fix-icon-manager-error-filter`.

## Technical Debt Handling
- Addressed the caching and lazy-loading discrepancy inside `UIElementRegistry` by switching to event-driven DB persistence.

## Commit Strategy
- Commit 1: Introduce error tagging and checkbox filter for Icon Manager list.
- Commit 2: Expand Icon Manager element extraction to include full `ui_elements` DB query.
- Commit 3: Introduce live DB synchronization via `UIElementRegisteredEvent` inside `IconSyncManager`.

## Report
The tasks outlined above were successfully implemented and merged. The Icon Manager now fully lists all database-tracked UI elements. The red text highlights correctly identify broken icon mappings, and the user toggle filters correctly. Furthermore, dynamically registering elements via `create_icon_button` now instantly synchronizes with the database, fixing a major visibility gap.

## Tech Notes
- We used `sqlite3.connect` specifically within the background thread (`_load_all_usage_ids`) to avoid SQLite threading locks.
- Dispatched `UIElementRegisteredEvent` whenever `UIElementRegistry.register` flags a new, unique button tuple `(module, screen, element_id)`.
