# Global Rules For Sprint 26 Combat & Vision Refactor Sessions

Paste this block before each Sprint 26 prompt.

```text
Follow the architecture and cleanup rules in Cabal_Auto.

Timebox and recovery (Strict 30-Minute Budget):
- Maximum 30 minutes. At minute 25 stop new feature work and run the focused validation.
- Use minutes 25-30 only for direct, targeted bug fixes that restore basic functionality.
- At minute 30, if validation still fails, revert all code changes made by the current session using a deliberate, reviewed patch. Never use git reset, git checkout --, or a broad discard command.

Core Architectural Rules:
- Vision Scope: Stop full-screen 3D HSV search. Target Bar at top-center of the screen is the single source of truth for monster health and target lock.
- Target Key Logic: 'Z' or target key is pressed ONCE when searching or when current target dies. NEVER spam 'Z' while target_active is True.
- Fast-Break: Skill cast-time waits must poll target health every 30-50ms and break immediately when health reaches zero to preserve combo flow.
- Main Thread Safety: Only the Main Thread calls Tkinter methods. Workers/services communicate via scheduler (after(0, ...)) or thread-safe callbacks.
- Boundary Checks: Must handle empty frame, game minimized/invalid bounds (-32000), target lost timeout, and missing templates.
- i18n & Style: Preserve UIStyle tokens. All new UI strings must support both 'en' and 'vi'.

Before final response:
- Report PASSED or ABORTED/REVERTED, modified files, validation commands/results, boundary case evidence, and deferred next session.