# Future Roadmap for Main Screen UI

## 1. Objective and Scope

This document outlines the practical, phased roadmap for future main-screen features in the Cabal Auto application, derived from the UX5 session. The primary goal is to establish the main screen as a focused "command center" for the core hunt loop (window selection → bounds readiness → monster rotation configuration → hunt execution → status monitoring), ensuring that technical details and deep configurations are delegated to secondary panels or dedicated managers.

## 2. Four-Zone Layout Contract

The UI design relies on a strict four-zone baseline grid optimized for a 1920x1080 resolution (100% Windows DPI scaling). Features are assigned to one zone only; state is not duplicated.

| Zone | Baseline Dimensions at 100% DPI | Responsive / Layout Behavior |
| --- | --- | --- |
| **App Header** | `56 px` height target | Fixed height; maintains identity/language; text does not clip on font scaling. |
| **Zone A: Quick Action Bar** | `80 px` height target | Contains primary hunt actions (Start/Stop, Window selector, Refresh, bounds state). Must remain visible and not wrap unexpectedly. |
| **Zone C1: Sidebar** | `280 px` width target, `minsize=250 px` | Uses grid `weight`. Expands up to `300 px` at baseline. Below `1280 px` width, navigation/accordions collapse to preserve workspace. |
| **Zone B: Workspace** | Remaining area, `1640 x 744 px` target | Uses grid `weight`. Houses the primary panels (Monster Rotation, Active Status). Panels stack vertically if width is insufficient. |
| **Zone C2: Bottom Logs** | `200 px` height target | Explicitly collapsible. Defaults to collapsed when application height is below `900 px` to prioritize Zone B. |

*Note: For DPI scaling from 125% to 150%, absolute sizing is not enforced. The UI relies on `grid`, `weight`, `minsize`, and responsive fallbacks (e.g., text wrapping, collapsible sections, independent scrollbars) to maintain readability, reachability, and visual priority.*

## 3. Zone Allocation and Feature Assignments

Every future feature must be assigned a clear zone, visual priority, and data source. The UI does not own the business state; it merely renders the validated data from controllers and services.

| Feature | Zone | Visual Priority | Layout Budget & Responsive Behavior | Owner / Source of Truth |
| --- | --- | --- | --- | --- |
| **Window Selector & Refresh** | A | P0 | `420 x 36 px` (selector), `44 x 36 px` (refresh). Does not shrink or hide when narrow. | App UI / `AppWindowController` selection flow |
| **Bounds Readiness** | A | P0 | Min `260 x 36 px`. Wraps text with tooltips if needed. Must not be pushed down to logs. | App UI / `WindowSelectionService` normalized bounds |
| **Start / Stop Hunt** | A | P0 | `160 x 44 px` each. Start is dominant (green) when idle, Stop is dominant (red) when running. | App UI / Existing hunt callbacks |
| **Hunt State & Active Target** | B | P0 | Primary panel (`776 x 552 px`). Stacks vertically below `1280 px` width. | `HuntTab` / Existing runtime status |
| **Monster Rotation List** | B | P0 | Primary panel (`776 x 552 px`). Independent scrollbar. Cannot be shrunk below `360 px` by C2. | `HuntTab` / Rotation config & callbacks |
| **Quick Skill Slots** | B | P1 | Secondary strip (`1576 x 120 px`) below primary panels. Scrolls/collapses internally if DPI scaling reduces height. | `HuntTab` / Existing skill vars & bindings |
| **Quick Setup & Managers Entry** | C1 | P1 | Sidebar navigation target `280 px` width. Collapses accordion sections when narrow. | `SetupTab` / Existing manager callbacks |
| **Template / Target Region Entry** | C1 | P1 | Entry point button. Deep forms do not render on the main screen by default. | `SetupTab` / Existing config flow |
| **Hotkey Summary & Entry** | C1 | P1 | Small summary view. Full configuration opens via dedicated entry point. | `SetupTab` / Existing hotkey config |
| **Recent Activity Logs** | C2 | P2 | Bound, scrollable area. Collapsed by default at low screen heights. | Bottom Logs UI / Existing thread-safe source |
| **Technical Diagnostics / History** | C2 | P3 | Requires user action to expand. Must not replace primary status in B. | Bottom Logs UI / Existing source only |
| **Hunt Presets** | C1 | P2 | Sidebar entry point. Apply results reflect in A/B immediately. | Dedicated preset service (Not UI state) |
| **Smart Recommendations** | B | P3 | Single actionable, dismissible recommendation. Does not create a permanent panel. | Recommendation service / Runtime inputs |

## 4. Primary Readiness and Recovery Model

Window selection, window bounds validation, and target region validation are integral to the primary readiness model. The UI relies strictly on `normalize_window_bounds_value` and `WindowSelectionService.update_bounds` as the single source of truth for window bounds. **The UI must never maintain a separate or duplicate copy of the window bounds state.**

| Runtime Condition | Primary Display Location | User-Visible Message | Recovery Action | Source of Truth |
| --- | --- | --- | --- | --- |
| **Valid bounds / Ready** | Zone A & B Summary | `Window ready` + window name | Start Hunt / Capture region | Normalized bounds (`WindowSelectionService`) |
| **No selected window** | Zone A & B Summary | `Chưa chọn cửa sổ game` | Select window / Refresh | Existing selected-window state |
| **Invalid / Malformed bounds** | Zone A & B Summary | `Không thể dùng biên cửa sổ` | Refresh / Select another window | Normalized bounds (`WindowSelectionService`) |
| **Window minimized / unavailable** | Zone A & B Summary | Brief reason window is unavailable | Restore game / Refresh / Reselect | Existing window lookup runtime state |
| **Invalid target region** | Zone A/B Warning, C1 Entry | `Vùng target nằm ngoài game window` | Capture / Edit region | Existing target-region validation |
| **Hunt running** | Zone A & B | `Running` + current target | Stop Hunt | Existing hunt runtime state |
| **Blocking error** | Zone A & B | Concise error reason | Action specific to the error | Existing hunt runtime state |

*Note: All recovery states display clear textual instructions, not just color changes, to ensure accessibility and clarity. Errors that block the Start Hunt action must be clearly visible in Zones A or B, not buried in Zone C2 logs.*

## 5. Sequence of UX Improvements

To avoid feature bloat and prioritize utility over novelty, implementation must be incremental, practical, and sequenced. Each stage must pass full boundary tests before proceeding.

### Phase 0: Safe Foundation and Core Layout
1. **UX1:** Refine visual hierarchy and scaling of the Quick Action Bar (Zone A) without changing callbacks.
2. **UX1B:** Introduce bounds readiness state to Zone A using the normalized bounds from existing services.
3. **UX2.1 & UX2.2:** Establish the four-zone core grid outer shell (`1920x1080` target) and reparent existing components (Action Bar, Notebook) without altering their internal layout.

### Phase 1: Workspace and Sidebar Refinement
1. **UX2B.1:** Subdivide Zone B into Monster Rotation and Active Target & Status panels with independent layout behavior.
2. **UX2B.2:** Move skill slots into a dedicated quick view strip.
3. **UX3 & UX3B:** Reorganize Zone C1 into progressive disclosure entry points for deep configuration and managers, keeping the Sidebar from expanding beyond its layout budget.

### Phase 2: Runtime Observability and Future Features
1. **UX4:** Standardize status rendering in Zone B, ensuring valid, warning, and error states have distinct styling and recovery actions.
2. **UX4B:** Implement the C2 Bottom Logs container, strictly relying on a thread-safe data source for recent activity.
3. **Future (Post-Stabilization):** Introduce Hunt Presets via C1, compact run summaries in C2, and smart recommendations in B, ensuring none of these features duplicate state or override primary hunt controls.

## 6. Execution Contracts & Visual Design Mandates

- **Ownership & Lifecycle:** The Main Thread is the sole owner of Tkinter updates; background workers must pass data via a scheduler (`after(0, ...)`) or `queue.Queue`.
- **DPI & Layout:** Hard-coded absolute pixel dimensions for interactive components are forbidden. The application uses proportional grid weights and `minsize` fallbacks to support 125%-150% DPI environments.
- **Visual Palette:** Status signals rely on `lib.ui_style.UIStyle` (Green for ready/start, Red for blocking error/stop, Orange for warnings, Blue for refresh/neutral). Semantic text contrast adheres to WCAG AA ($4.5:1$ minimum).
- **i18n Readiness:** Every user-visible string introduced in this roadmap requires a translation key (`en` and `vi`) via `App._t` or zone-specific `_t` helpers. Raw keys and string concatenation are strictly prohibited.