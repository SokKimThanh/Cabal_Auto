# Architecture Documentation

Tài liệu về kiến trúc hệ thống và các thành phần cốt lõi.

## Files

### Core Architecture
- **[GLOBAL_HOTKEY_ARCHITECTURE.md](GLOBAL_HOTKEY_ARCHITECTURE.md)** - Kiến trúc hệ thống global hotkeys
- **[GLOBAL_HOTKEYS_EXTENDED_ARCHITECTURE.md](GLOBAL_HOTKEYS_EXTENDED_ARCHITECTURE.md)** - Mở rộng kiến trúc hotkeys
- **[SINGLE_INSTANCE_LOCK.md](SINGLE_INSTANCE_LOCK.md)** - Single instance lock pattern

### Threading & Performance
- **[WORKER_THREAD_ARCHITECTURE.md](WORKER_THREAD_ARCHITECTURE.md)** - Worker thread architecture cho Vision System

## Related Documentation
- [Features](../features/) - Tính năng sử dụng các architecture patterns
- [Sprint 22](../sprints/sprint22/) - Implementation trong Sprint 22

## Boundaries (Architecture Cleanup Sprint)

As of the latest architecture cleanup, the responsibilities have been decoupled from the root application (`app_gui.py`):

*   **App Lifecycle:** `AppLifecycleController` (`ui/controllers/app_lifecycle_controller.py`) manages startup sequence checks, dependency warnings, and gracefully orchestrating shutdowns (`on_close`).
*   **App State:** `AppStateController` (`ui/controllers/app_state_controller.py`) isolates bounds persistence and generic config properties to keep the root app light.
*   **Window/Modal Lifecycle:** Decentralized. `AppWindowController` coordinates core windows. Modal windows like LibraryManager, MonsterManager, and SkillManager are orchestrated by their respective controllers (e.g., `LibraryManagerController`) which handle singletons and UI focus, preventing duplicate handles.
*   **Hunt Config Migration/Validation:** Config migration (`legacy` lists to `dicts` mapping) is managed by `lib/features/hunt/config_migrator.py`. Normalizing configuration limits and bounds validation rests inside `lib/features/hunt/config_validator.py`.
*   **Hunt Orchestration:** `HuntOrchestrator` (`lib/features/hunt/hunt_orchestrator.py`) handles the background loop, state machine, and event emission. Domain logic belongs to `HuntRunner`.
*   **Hotkeys:** `HotkeyController` (`ui/controllers/hotkey_controller.py`) serves as the single source for global keyboard hook registration, toggling logic, and dispatch routing.
*   **Overlay Lifecycle:** `OverlayController` (`ui/controllers/overlay_controller.py`) manages the cross-platform UI overlay lifecycle and coordinates safely with the separate low-level bounding-box utilities.
*   **Window Tracking:** Active application target bounds selection (e.g. updating scan areas from standard inputs) routes through `WindowSelectionService` (`lib/features/hunt/window_selection_service.py`) to keep pure business logic apart from UI configuration dictionaries.
*   **Monster Services:** Persistent state, caching and CRUD actions on hunt target data reside in `MonsterLibraryService` and `MonsterManager` logic, totally independent of the views.
*   **Skill Services:** `SkillRuntimeService` handles data persistence, reloading logic, and acts as the headless backend for skill slots, extracted fully from the main UI tab.

> **Contributor Note:**
> `app_gui.py` is now strictly a thin composition root and standard Tkinter bootstrapper. **Do not add new orchestration, lifecycle logic, or business state directly to `app_gui.py` or the `App` class.** If you are building a new feature, delegate its state and event connections to an appropriate `Service` or `Controller`.

### Validation and Smoke Tests

The final architecture can be validated using the following commands:
*   **Targeted UI Smoke Tests:** `xvfb-run -a python3 -m pytest tests/unit/ui/` (requires `pytest` and `xvfbwrapper`).
*   **App GUI Run:** `python app_gui.py` starts the Tkinter mainloop, which blocks and requires manual GUI interaction to exit cleanly unless a programmatic close (e.g. `app.destroy()`) is triggered. Wait until the window renders and manually attempt opening modal states (Monster Manager, Skill Manager).
