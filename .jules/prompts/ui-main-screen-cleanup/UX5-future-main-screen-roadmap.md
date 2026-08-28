# UX5 - Roadmap Tương Lai Cho Màn Hình Chính

Paste `00-global-rules.md` before this prompt.

```text
Define a practical future roadmap for main-screen features based on the UX analysis in docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md.

Goal:
Identify which capabilities should be surfaced directly on the main screen and which should remain in secondary panels or dedicated managers.

Timebox:
- Documentation-only session; maximum 20 minutes.
- Do not edit Python UI files. Use implementation evidence from prior sessions and identify any layout work still deferred.

Files in scope:
- docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md
- app_gui.py
- ui/tabs/*.py
- focused documentation and UI planning only

Primary UX objective:
Create a plan for future UI improvements that keeps the main screen focused on the hunt loop and user actions, not on every detail of the system.

Design intent:
The roadmap should be practical, phased, and architecture-aware. It should decide what is essential to show immediately, what is secondary, and what belongs in future iterations.

Layout contract for this session:
- Treat the four-zone baseline as fixed: Header `56 px`, Action Bar `80 px`, Sidebar `280 px`, Workspace `1640 x 744 px`, Bottom Logs `1640 x 200 px` at `1920x1080`.
- Assign every proposed feature to exactly one zone before recommending it.
- Primary actions and blocking state belong in Vùng A/B; configuration entry points belong in C1; technical history belongs in C2.
- Reject roadmap proposals that require a feature to duplicate state, hide bounds validation, or compete with Start/Stop for visual dominance.

Tasks:
- list which current and future features belong on the main screen
- distinguish between primary controls, active status, and secondary configuration
- include target-window, window-bounds, and target-region validation in the primary readiness model
- recommend likely future additions such as quick dashboard, target status, presets, warnings, and smart recommendations
- keep the plan practical and sequenced so it can be delivered in small UX improvements
- avoid feature bloat; prioritize utility over novelty

Acceptance criteria:
- the final proposal clearly separates primary, secondary, and future features
- the plan matches the software automation objective: convenience, natural flow, and smooth experience
- recommendations are actionable and compatible with the current architecture
- the roadmap is incremental and easy to implement in small steps
- the roadmap preserves one normalized source of truth for window bounds rather than introducing duplicate state

Session boundary gate:
- identify how the roadmap handles valid bounds, no selected window, invalid/minimized window, and invalid target region
- identify the user-visible recovery action for each state
- confirm no roadmap item creates a separate UI-owned copy of window bounds
- report these decisions in the resulting planning document before ending the session

Validation:
- this session is primarily planning/documentation; validate by reviewing the document for internal consistency and alignment with the current app structure
- confirm the roadmap does not drift toward feature sprawl or over-design
- include a zone allocation table for every future feature, including its visual priority and expected impact on the `1920x1080` layout budget
```
