# Guidelines for AI Code Review

## Scope
These instructions apply to Copilot-assisted code review for the Cabal Auto Hunt repository. They are intended to help Copilot flag likely issues and suggest changes consistently, but they do **not** replace the team's coding standards, maintainer judgment, or explicit reviewer instructions in a pull request.

## Maintenance
Repository maintainers are responsible for keeping this file up to date. Contributors who want to change these review instructions should coordinate with the maintainers who own the project's development workflow.

When performing code reviews for the Cabal Auto Hunt project, use the following architectural rules and coding standards as review guidance:

## 1. UI Decoupling
- Background threads and services (e.g., `HuntOrchestrator`, `HuntRunner`) must **not** call Tkinter methods directly.
- The UI layer (`app_gui.py`) must pass safe adapter callbacks (e.g., `schedule_ui_task=lambda fn: self.after(0, fn)`) to these services.
- Tkinter UI widgets (Treeview, Label, Dialog) must only be updated from the Main Thread.
- Background worker threads performing DB or image loading must pass data through a `queue.Queue`.

## 2. Database Operations
- In database repositories (e.g., `MonsterRepository`), local SQLite connections must be closed in `finally` blocks to prevent connection leaks.
- `serverBossType` fields should be preserved as string or `None` rather than cast to integers.
- Database CRUD operations must use dedicated service classes under `lib/db/services/` constrained to 200-300 lines to avoid god classes.
- Explicit transactions (e.g., `BEGIN TRANSACTION`) must be implemented for operations spanning multiple tables.

## 3. JSON File I/O
- Robust error handling is required: check for file existence, catch `json.JSONDecodeError` for malformed data, log exceptions, and gracefully fallback to an empty default state (`{}`) to prevent crashes.

## 4. Vision System
- Avoid redundant OpenCV computations by caching feature detector instances on the engine class.
- Pre-computed keypoints and descriptors must be stored directly on `Template` data objects.
- In `lib/vision/template_matcher.py`, use the in-memory cache `_TEMPLATE_CACHE`.

## 5. Testing
- The project uses `black` for formatting and `flake8` for linting.
- The project uses custom pytest markers: `fast`, `db`, `ui`, and `slow`.
- In headless Linux environments, Tkinter UI unit tests must be executed using `xvfb-run -a pytest <test_paths>` (or patched mocks).

## 6. Architecture & Maintenance
- Do not delete code unless explicitly requested and proven unused via repository search.
- Prefer extracting code intact to controller/service boundaries before simplifying.
- When refactoring, explicitly delete legacy code after it has been successfully extracted or replaced, rather than leaving it in place and bypassing it with early `return` statements.

## 7. Formatting and Language
- When providing code review feedback, output PR comments in Vietnamese format, e.g.:
  - `📍 **Vị trí:**` (Location)
  - `📝 **Vấn đề:**` (Issue description)
  - `💡 **Đề xuất:**` (Suggestion)
