# Language Management System Specification

## 1. Title & Objective
**Feature:** Language Manager UI and JSON Sync Mechanism.
**Objective:** Provide a graphical user interface (GUI) within the application to manage translation keys, and implement a robust two-way/one-way synchronization mechanism that strictly treats the SQLite Database as the Single Source of Truth, allowing translations to be exported back to static files (JSON or Python dicts).

## 2. Context
Currently, the application relies on `TranslationService` to load data from the SQLite database. During startup, static dictionaries from Python files (`lib/i18n/*_translations.py`) are upserted into the database. However, there is no UI to manually view, edit, add, or delete these translations. Furthermore, if a translation is modified directly in the database (or via a future UI), there is no mechanism to sync these changes back to the source code repository (JSON/Python files), creating a disconnect between the source of truth (DB) and version control.

## 3. Database Architecture & Sync Mechanism
### 3.1 Service Expansion
The current `TranslationService` only supports `get_all`, `upsert`, and `bulk_upsert`. It must be expanded to include:
- `update(id, namespace, key, lang, text)`
- `delete(id)`
- `get_namespaces()` - Returns unique namespaces for filtering.

### 3.2 Synchronization (Database is the Source of Truth)
- **Component:** `TranslationSyncManager`
- **Action:** A "Sync to File" mechanism.
- **Workflow:**
  1. User clicks the "Sync to JSON/File" button on the UI.
  2. The system fetches all translations from the database.
  3. It groups them by namespace (and/or language).
  4. It writes them out to formatted JSON files (e.g., `assets/i18n/<lang>.json` or replacing current dictionary files depending on the architectural decision, preferably JSON for ease of parsing).

## 4. UI Design
### 4.1 Integration Point
- **Sidebar Integration:** A new navigation button added to the main sidebar (similar to Icon Manager, Monster Manager).
- **Shortcut:** `<Control-l>` mapped to open the Language Manager.

### 4.2 Main View (`LanguageManagerFrame`)
Located in the main content area (`shell_zone_b`).
- **Toolbar:**
  - Search Entry (filters by key or text).
  - Namespace Combobox (filters by specific UI context).
  - Language Filter (All, en, vi).
  - Action Buttons: `Add`, `Edit`, `Delete`, `Refresh`, and `Sync to JSON` (prominent button).
- **Data Table (Treeview):**
  - Columns: `ID`, `Namespace`, `Key`, `Language`, `Text`, `Updated At`.
  - Double-click a row to open the Edit Dialog.

### 4.3 Add/Edit Dialog (`TranslationDialog`)
A modal `Toplevel` window to manage a single translation entry.
- **Fields:**
  - `Namespace` (Combobox with existing ones or text entry for new).
  - `Key` (String Entry).
  - `Language` (Combobox: en, vi).
  - `Text` (Text Area/Entry for the actual translation).
- **Validation:** Ensure no duplicate (namespace, key, lang) combinations exist.

## 5. Detailed Implementation Guide
### Step 1: Backend Updates
- Update `lib/db/services/translation_service.py` to include `update` and `delete`.
- Create `lib/i18n/translation_sync_manager.py` with an `export_to_json` method.

### Step 2: UI View Creation
- Create `ui/views/language_manager_frame.py`.
- Implement `ttk.Treeview` and populate it using `TranslationService.get_all()`.
- Implement filtering logic purely on the UI side or via DB queries.

### Step 3: UI Dialog Creation
- Create `ui/dialogs/translation_dialog.py`.
- Implement save logic that calls `TranslationService.upsert` or `update`, then triggers a refresh on the main frame.

### Step 4: Integration
- Edit `ui/app_gui.py` to import `LanguageManagerFrame`.
- Add a sidebar button referencing `btn_language_manager` (requires adding this key to translations first!).

## 6. Known Issues, Risks & System Weaknesses
- **SSoT Conflict (Manual Import/Export vs. Startup Auto-seed):** If the application continues to automatically seed data from static Python files (`.py`) on startup, it will silently overwrite any manual updates or newly imported JSON data stored in the database. A priority fallback mechanism must be established to prevent this architectural conflict.
- **Unsaved Changes & Diff Checking:** There is a risk of data loss if the user exits the application (or switches views) without exporting their manual edits, as there is currently no unsaved changes warning prompt. Furthermore, the sync/export operation may cause performance issues or file bloating if it blindly dumps the entire database instead of comparing and exporting only the changed differences (diffs).
- **Tkinter UI Thread Blocking:** Loading thousands of translation keys into a `Treeview` or performing heavy file I/O operations (such as importing/exporting large JSON files) on the main thread will cause the UI to freeze.
- **Duplicate Modal Instances:** Users rapidly double-clicking a row in the Treeview may unintentionally open multiple, duplicate `TranslationDialog` windows. This must be mitigated using `wait_window()` to block the parent.
- **Encoding Issues:** Corruptions of non-ASCII characters (e.g., Vietnamese diacritics) will occur if file read/write operations for JSON or Python files do not strictly enforce `encoding='utf-8'`.
- **The Chicken and Egg Problem:** The Language Manager's own UI text (buttons, labels) needs translation keys to render itself. We must define its keys in `lib/i18n/` first so it doesn't crash before the user can edit them.
- **Live Updating:** If a user edits a translation that is currently visible on the screen, should it update immediately? For MVP, a simple app restart or a `AppStateController.emit('i18n_updated')` might be needed.

## 7. Acceptance Criteria
- [ ] Sidebar contains a working Language Manager button.
- [ ] Treeview correctly displays all translations from the database.
- [ ] User can Add, Edit, and Delete translation entries.
- [ ] User can search and filter translations by namespace/language.
- [ ] Pressing "Sync" successfully dumps the database state to JSON files on disk.
- [ ] Code passes flake8 and existing unit tests.
