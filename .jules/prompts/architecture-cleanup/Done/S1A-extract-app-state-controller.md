# S1A - Extract App State Controller

Paste `00-global-rules.md` first, then this prompt.

```text
Implement the Sprint 1 app state extraction from .jules/architecture-sprint-roadmap.md.

Goal:
Move bound state management and non-widget root state bookkeeping out of app_gui.py into ui/controllers/app_state_controller.py.

Files in scope:
- app_gui.py
- ui/controllers/app_state_controller.py
- ui/controllers/__init__.py
- focused tests only if needed

Boundaries:
- app_gui.py may keep actual Tk widgets and composition references.
- app_state_controller.py should own state initialization/access patterns that are not themselves Tk widget construction.
- Preserve existing public attribute names on App when needed for compatibility.
- Do not move window open/focus lifecycle in this session.
- Do not move close/dispose behavior in this session.

Acceptance criteria:
- App can instantiate with the same externally visible behavior.
- app_gui.py has less direct state setup logic.
- No config shape or startup behavior changes.

Validation:
- Run the narrowest existing App instantiation or GUI smoke test.
- If no narrow test exists, run `py -m pytest tests/test_ui_imports.py` and a syntax/import check for touched files.
- Run `py .\app_gui.py` only if it is safe/non-blocking in this repo.
```
