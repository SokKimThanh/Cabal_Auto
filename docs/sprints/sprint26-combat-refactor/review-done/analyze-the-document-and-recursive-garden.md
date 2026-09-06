# Context

The user has attached two inputs:
1. **UISTYLEV2-COMPLETENESS-ASSESSMENT.md** — a structured audit of a Python Tkinter design system (`UIStyleV2`) that is 60% complete, with 6 identified gaps across backward compatibility, icons, component methods, animations, and accessibility.
2. **image.png** — a screenshot of the actual desktop application ("Trợ lý săn Cabal" — Cabal Hunting Assistant), showing a dark-themed Tkinter UI with a green-accented sidebar, tabbed panels, and status indicators.

The task is to build an **interactive React web app** that renders an automated, phased Python implementation guide derived from the document analysis and screen layout. The guide must be session-aware (< 1 hour cap), include a secondary review pass, and surface unresolved items in a separate report section.

---

# What to Build

A single-page React app in `src/App.tsx` that functions as an **Automated Python Implementation Guide** — a structured, interactive document that walks developers through enhancing `UIStyleV2` in phases, with Python code snippets, progress tracking, a session timer, and an unresolved issues panel.

---

# Design System

## Palette (matching reference screenshot)
Dark ground — matches the Cabal app's exact dark theme:
- `--bg-base`: `#111214` (deepest, window chrome)
- `--bg-surface`: `#1a1c1f` (panel backgrounds)
- `--bg-elevated`: `#242629` (cards, sidebar items)
- `--bg-input`: `#2a2d31` (inputs, code blocks)
- `--accent-green`: `#22c55e` (active sidebar, CTAs — matches screenshot green)
- `--accent-green-bg`: `#0f2318` (green accent background)
- `--accent-blue`: `#3b82f6`
- `--text-primary`: `#e8eaed`
- `--text-secondary`: `#9ca3af`
- `--text-muted`: `#6b7280`
- `--border`: `#2e3135`

## Fonts
- **Inter** (Google Fonts) — UI text
- **JetBrains Mono** (Google Fonts) — code blocks and labels

Wire both in `src/index.css` with `@import` before `@import 'tailwindcss'`.

---

# App Structure & Phases

## Layout
Two-column layout (matches reference screenshot proportions):
- **Left sidebar** (220px fixed): session timer, phase navigator, progress bar
- **Main content** (flex-1): active phase content with code blocks

## Sections / Phases

### Phase 1 — Critical (Est. 15 min)
Two tasks, each with a Python code block:
1. **THEME_* aliases** — add ~20 lines mapping `THEME_BG_APP`, `THEME_BG_SIDEBAR`, etc. to existing BG_* tokens
2. **SPACING_* aliases** — add 10 lines mapping `SPACING_2` through `SPACING_32` to numeric values

### Phase 2 — High Priority (Est. 20 min)
Three tasks:
1. **SIZE_SECTION alias** — 1-line addition
2. **Sidebar icon mapping** — `SIDEBAR_ICONS` dict + `get_sidebar_icon()` classmethod
3. **Component style methods** — `get_tab_style()`, `get_badge_style()`, `get_sidebar_item_style()`, `get_label_style()`

### Phase 3 — Medium (Est. 10 min, if time allows)
Two tasks:
1. **Animation/transition tokens** — `TRANSITION_FAST/NORMAL/SLOW/VERY_SLOW` constants
2. **A11y utilities** — `check_contrast_ratio()` stub + pre-calculated safe pairs

## Secondary Review Panel
After Phase 3, a "Secondary Review" section that:
- Re-evaluates each phase's additions against the completeness matrix
- Shows updated estimated scores (Visual Hierarchy, Nav Clarity, etc.)
- Flags any cross-phase dependencies or ordering risks

## Session Manager (sidebar)
- Countdown timer starting at 60:00, ticking down in real time
- Color shifts: green → amber (< 15 min) → red (< 5 min)
- Estimated time remaining per phase shown next to each phase nav item
- When session would be exhausted: auto-surface "Unresolved Issues Report"

## Unresolved Issues Report (bottom panel / modal)
Appears when session timer < 5 min or user clicks "Generate Report":
- Lists incomplete tasks with their priority
- Shows which phases were not started
- Formatted as a copyable summary

---

# Key Implementation Details

## Files to modify
- `src/index.css` — add Google Fonts `@import` lines at top
- `src/App.tsx` — full implementation (replace empty scaffold)

## Component breakdown inside App.tsx
All self-contained in one file to keep the scaffold simple:

- `SessionTimer` — `useEffect` interval counting down from 3600 seconds
- `PhaseNav` — sidebar phase list with time estimates and completion checkboxes
- `CodeBlock` — dark-themed `<pre>` with copy button, uses JetBrains Mono
- `TaskCard` — expandable card with title, description, estimated lines, and CodeBlock
- `PhaseSection` — groups TaskCards for one phase, shows phase header and total time
- `SecondaryReview` — shows before/after completeness matrix with updated scores
- `UnresolvedReport` — modal/panel listing incomplete tasks

## State
```tsx
const [activePhase, setActivePhase] = useState(0)
const [completedTasks, setCompletedTasks] = useState<Set<string>>(new Set())
const [secondsLeft, setSecondsLeft] = useState(3600)
const [showReport, setShowReport] = useState(false)
```

## Python code snippets
Each `TaskCard` contains the actual Python code from the assessment document — verbatim, properly indented, ready to copy into `UIStyleV2`.

---

# Verification

After implementation:
1. Visually confirm the app matches the dark aesthetic of the reference screenshot
2. Confirm the session timer counts down correctly
3. Confirm phase navigation switches active content
4. Confirm code blocks are readable with JetBrains Mono
5. Confirm the unresolved report appears when triggered
6. Confirm responsive layout at narrower widths collapses sidebar

No build or typecheck needed — Vite hot-reload in the preview panel is sufficient.
