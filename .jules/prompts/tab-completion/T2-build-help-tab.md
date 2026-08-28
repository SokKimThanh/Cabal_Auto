# T2 - Build Help Tab

Paste `00-global-rules.md` first, then this prompt.

```text
Implement Sprint 18 Phase 4 Task #5 (Create Help Tab) from
docs/sprints/sprint18/SPRINT18_PHASE4_TAB_REORGANIZATION.md.

Context:
ui/tabs/help_tab.py currently only contains `def _build_ui(self): pass` - a
never-implemented placeholder (marked "Status: Not started" in the design doc).
Unlike the Stats tab, no runtime data is lost by this being empty - it is a
pure documentation/UX gap for new users.

Goal:
Build the real Help tab UI per the design doc's Task #5 sections:
- Section 1: Quick Start Guide (step-by-step setup instructions; the design
  doc's sample text is a reasonable starting point, adapt as needed)
- Section 2: Keyboard Shortcuts (list the *current* global hotkeys read from
  hunt_cfg["global_hotkeys"] / HotkeyController, not the stale F9/ESC example
  in the old design doc - the app's actual hotkeys have changed since Sprint 18,
  e.g. Ctrl+Shift+R/E for start/stop; verify current bindings via repository
  search in ui/controllers/hotkey_controller.py before writing this section)
- Section 3: Troubleshooting (common issues and solutions; keep this short and
  specific to this codebase - e.g. missing `keyboard` package, pywin32 missing
  for overlay - rather than generic filler)
- Section 4: About (app name, version if available, GitHub repository link)

Files in scope:
- ui/tabs/help_tab.py
- lib/i18n/translations.py (new i18n keys for Help tab labels/content, en + vi)
- a small focused test (e.g. tests/test_ui_imports.py-style instantiate check)

Boundaries:
- Do not hardcode the keyboard shortcuts list from the old design doc as-is;
  verify current hotkeys via ui/controllers/hotkey_controller.py and hunt_cfg
  defaults first, since they have changed since Sprint 18 (this repo's actual
  history shows the hotkeys were migrated F8/F9 -> Ctrl+Shift+R/E at least
  once - do not reintroduce stale/incorrect shortcut documentation).
  Alt+1/Alt+2 tab-switch shortcuts are also relevant here.
- Keep this tab read-only/informational; do not add functional controls that
  belong in Setup or Hunt tabs.
- Reuse existing i18n helper (`self.app._t(key)` or `self._t`) rather than
  hardcoded bilingual if/else strings, matching the pattern in hunt_tab.py.

Acceptance criteria:
- Help tab renders Quick Start, Keyboard Shortcuts, Troubleshooting, and About
  sections with content specific to this app (not generic placeholder text).
- The Keyboard Shortcuts section accurately reflects the hotkeys currently
  registered by HotkeyController, verified by reading that file, not assumed
  from the old Sprint 18 doc.
- No functional/interactive controls beyond simple links/copy-to-clipboard
  conveniences are added to this tab.

Validation:
- Instantiate `App()` directly and assert the Help tab's widgets exist without
  exceptions.
- Run `py -m pytest tests/test_ui_imports.py -v`.
- Run `py .\app_gui.py` and manually confirm the Help tab renders and its
  listed shortcuts match what Ctrl+Shift+* / Alt+* actually do in the running app.
```
