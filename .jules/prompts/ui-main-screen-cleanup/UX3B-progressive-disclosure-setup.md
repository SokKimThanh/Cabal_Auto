# UX3B - Progressive Disclosure Trong Setup

Paste `00-global-rules.md` before this prompt.

```text
Implement only progressive disclosure inside the existing Setup UI.

Dependencies:
- UX3 Sidebar navigation has passed, or this session must keep the existing SetupTab route intact.

Goal:
Keep common setup visible first while making deeper tuning discoverable but subordinate.

Timebox: 25-30 minutes. At minute 25, run validation; use remaining time only for direct repair or the rollback/abort rule.

Files in scope:
- ui/tabs/setup_tab.py
- app_gui.py only if an existing SetupTab entry point requires a compatible parent integration
- focused tests only if practical

Layout contract:
- Work only inside the Setup content surface; do not increase Sidebar beyond `280 px` at 1920x1080 or `300 px` at any baseline.
- Use grid weights/minsize for internal responsiveness. Long content scrolls or collapses inside its owner, never by reducing Workspace.

Tasks:
- Preserve the Beginner / Intermediate / Advanced mode system and `_update_setup_visibility` behavior.
- Keep mode selector and common setup visible.
- Make advanced hunt/template/hotkey tuning a clearly labeled secondary disclosure state using existing widgets where possible.
- Keep the route to every hidden section discoverable.
- Keep blocking target-window/bounds warnings in Vùng A/B, not inside the disclosure content.

Acceptance criteria:
- Beginner exposes only essential/common setup without removing configuration access.
- Intermediate and Advanced expose the current deeper settings through an obvious path.
- Existing values persist and callbacks still apply the same config fields.
- Disclosure does not change hunt runtime behavior or duplicate bounds/config state.

Session boundary gate:
- Beginner: advanced controls hidden but discoverable; bounds warning still visible in A/B.
- Intermediate: intended advanced subset appears and can be hidden again without losing values.
- Advanced: all existing advanced controls remain reachable and config data is preserved.

Validation:
- run `py -m pytest tests/test_ui_imports.py` if applicable
- run the narrowest startup/import smoke check available
- manually check all three modes and report each as passed, failed, or manual-only
- report UIStyle tokens, Layout evidence at 1920x1080, and rebuild behavior after a language change
```