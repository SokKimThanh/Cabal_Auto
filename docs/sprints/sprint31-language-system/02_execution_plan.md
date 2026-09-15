# Sprint 31: Execution Plan - Language System

This document breaks down the implementation of the Language Manager System into manageable tasks.

## Phase 1: Stabilization & Data Flow (Current Phase)
- **Task 1.1:** Audit current `TranslationBinder` and fix the broken connection in `app_gui.py` (`on_language_change` missing `refresh_all()`).
- **Task 1.2:** Write integration tests (`test_language_data_flow.py`) to verify that the `TranslationBinder` successfully updates mock UI elements when `LanguageChangedEvent` is fired.

## Phase 2: Backend Expansion (Database & Sync)
- **Task 2.1:** Expand `TranslationService` in `lib/db/services/translation_service.py` to support `update_translation`, `delete_key`, and `get_all_grouped`.
- **Task 2.2:** Create `TranslationSyncManager` to handle exporting database contents to `assets/i18n/*.json`.
- **Task 2.3:** Write backend unit tests for the expanded DB service and sync manager.

## Phase 3: Language Manager UI Implementation
- **Task 3.1:** Create `LanguageManagerController` to handle business logic (loading data, saving data, filtering).
- **Task 3.2:** Build `LanguageManagerFrame` in `ui/views/language_manager_frame.py` featuring the Treeview (Top pane) and Inline Edit Form (Bottom pane).
- **Task 3.3:** Integrate the new Frame into `app_gui.py` and `NavigationController`. Add a button to the `SidebarComponent` to open the view.

## Phase 4: Live Data Update Integration
- **Task 4.1:** Introduce `TranslationDataUpdatedEvent` into `EventBus`.
- **Task 4.2:** Ensure `LanguageManagerController` emits this event upon successful saves.
- **Task 4.3:** Bind this event in `app_gui.py` to trigger `i18n.load_from_db()` and `translation_binder.refresh_all()`.
- **Task 4.4:** Perform manual UI testing to verify translations change in real-time when edited via the new UI.
