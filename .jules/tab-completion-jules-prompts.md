# Tab Completion Jules Prompt Copybook

Split one-session prompt files are available in `.jules/prompts/tab-completion/`. Use those files when launching Jules sessions to avoid overloading one session with both tabs at once.

## Context

`ui/tabs/stats_tab.py` and `ui/tabs/help_tab.py` were both left as empty placeholders (`def _build_ui(self): pass`) since Sprint 18 Phase 4, whose design doc explicitly marked them `Status: Not started`:

- `docs/sprints/sprint18/SPRINT18_PHASE4_TAB_REORGANIZATION.md` — Task #4 (Stats Tab) and Task #5 (Help Tab)

This is not a regression to revert (unlike the Monster/Skill Manager and Hunt tab gaps found earlier) — it is planned work that was never picked back up. The Stats tab gap is functionally more important: hunt statistics/performance metrics were deliberately removed from the Hunt tab in Sprint 18 expecting them to move here, so that data currently has nowhere to display at all. The Help tab gap is purely a documentation/UX convenience gap.

## Global Rules For Every Jules Session

Paste `.jules/prompts/tab-completion/00-global-rules.md` at the top of every prompt if Jules does not already have it in context.

## Session Order

| Order | File | Priority | Dependency |
| --- | --- | --- | --- |
| 1 | `T1-build-stats-tab.md` | Higher — recovers lost runtime/stats data | None; can start immediately |
| 2 | `T2-build-help-tab.md` | Lower — pure documentation/UX gap | None; independent of T1, can run in parallel or after |

Run each session independently; do not combine both tabs into one session. Review diff, run tests, and manually smoke-test each tab before moving to the next.
