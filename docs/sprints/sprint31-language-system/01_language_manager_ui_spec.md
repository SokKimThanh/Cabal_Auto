# Sprint 31: Language Management System Specification

## 1. Title & Objective
**Feature:** Language Manager UI and Real-time Data Sync Mechanism.
**Objective:** Provide a robust, user-friendly GUI within the application to manage translation keys, and implement a live-update mechanism (`TranslationBinder` + `EventBus`) to immediately reflect language changes without restarting the app. The SQLite database serves as the Single Source of Truth (SSoT), with the ability to sync/export translations to static JSON files.

## 2. Context & Evolution from Sprint 29
In Sprint 29, the language manager was conceptualized with a Modal (popup) based UI and lacked real-time updates. Since the application architecture has transitioned to a strictly decoupled **Composition** pattern, this spec updates the approach:
1. **Live Updating:** Replaces the need for an app restart. Uses `TranslationBinder` combined with `EventBus` (`LanguageChangedEvent` and `TranslationDataUpdatedEvent`) to propagate language tokens directly to UI components.
2. **Improved UX/UI:** Eliminates annoying Modal popups in favor of an **Inline-Edit Split Pane** UI. Translators can view English and Vietnamese texts side-by-side on a single row, drastically improving productivity.

## 3. Database Architecture & Sync Mechanism
### 3.1 Service Expansion (`TranslationService`)
The current `TranslationService` (`lib/db/services/translation_service.py`) must be expanded to include:
- `update_translation(namespace, key, lang, text)`
- `delete_key(namespace, key)` (Deletes all languages for a given key).
- `get_namespaces()` - Returns unique namespaces for filtering.
- `get_all_grouped()` - Returns data grouped by (namespace, key) containing both 'en' and 'vi' texts for the new UI grid.

### 3.2 Synchronization (Database is SSoT)
- **Component:** `TranslationSyncManager`
- **Action:** A "Sync to JSON" mechanism.
- **Workflow:** Fetches all translations from the database, groups them by language, and exports them to `assets/i18n/<lang>.json`. A priority fallback must ensure the DB does not get overwritten by old Python dictionary files during app startup if the DB already contains data.

## 4. UI Design (`LanguageManagerFrame`)
Located in the main content area (`shell_zone_b`) and accessed via a Sidebar button. It uses a Split-Pane layout:

### 4.1 Top Section: Data Grid & Toolbar (60% height)
- **Toolbar:**
  - Search Entry (filters by key or text).
  - Namespace Combobox (filters by context).
  - Action Buttons: `[+] Add New`, `[Sync to JSON]`, `[Refresh]`.
- **Data Table (Treeview):**
  - Columns: `Namespace`, `Key`, `Text (EN)`, `Text (VI)`, `Updated At`.
  - Side-by-side translation columns allow instant visual comparison.
  - Clicking a row loads its data into the Bottom Form.

### 4.2 Bottom Section: Inline Edit Form (40% height)
A static form attached below the Treeview.
- **Fields:**
  - `Namespace` (Combobox/Entry).
  - `Key` (String Entry, disabled if editing existing, enabled if adding new).
  - `Text (EN)` (Large Text Area).
  - `Text (VI)` (Large Text Area).
- **Action Buttons:**
  - `Save`: Upserts both EN and VI texts to the database. Upon success, emits `TranslationDataUpdatedEvent`.
  - `Delete Key`: Deletes the key from the DB.
  - `Clear/Cancel`: Clears the form inputs.

## 5. Live Data Flow Connection
- **Event Dispatch:** When the user clicks "Save" in the UI, `TranslationService` updates the DB, and the Controller emits `TranslationDataUpdatedEvent`.
- **Event Reception:** `app_gui.py` listens for this event. It instructs `i18n.load_from_db()` to pull fresh data into memory, and then calls `self.translation_binder.refresh_all(self._t)`.
- **Result:** Every UI widget (labels, buttons) on the screen instantly updates its text without an app restart.

## 6. Known Risks & Mitigation
- **Thread Blocking:** Exporting large JSONs might freeze the UI. Mitigation: Run JSON export in a background thread or limit file sizes.
- **Missing Keys (Chicken & Egg):** The Language Manager's own buttons need translation keys. Mitigation: Seed the DB with these specific keys during initialization.
- **State Loss on Refresh:** Calling `refresh_all` might reset certain dynamic states if widgets are completely redrawn. Mitigation: `TranslationBinder` only updates the `text` attribute, preserving widget state.
