# Setup Tab UI Refactor Execution Prompt

**Goal**: Refactor the `SetupTab` (`ui/tabs/setup_tab.py`) to align with the new `ResponsiveGridBase` architecture, improve numerical inputs, and eliminate UI occlusion while strictly adhering to `UIStyleV2` and the `i18n` localization system.

**Context**:
The current `SetupTab` relies on a rigid grid layout with raw `ttk.Entry` fields for advanced numerical inputs. While functionally sound, it does not respond gracefully to window resizing (especially below 800x600) and suffers from poor UX regarding input validation. Additionally, the collapsible sections use heavily nested, "boxed-in" frames which feel visually heavy.

## Required Tasks

### 1. Architectural Migration (`ResponsiveGridBase`)
- Refactor the class `SetupTab(tk.Frame)` to inherit from `ResponsiveGridBase`.
- Ensure all children (collapsible sections, inputs, mode selectors) are parented to `self.get_content_frame()` rather than `self`.
- Verify that expanding all collapsible sections does not result in the content overflowing silently (the canvas scrollbar should appear).

### 2. Upgrade Numerical Inputs
- Replace all standard `ttk.Entry` widgets used for numerical parameters (e.g., `press_ms`, `target_cycle`, `search_interval`, `attack_interval`, `lost_timeout`, `attack_duration`) with native `ttk.Spinbox` controls.
- Implement strict numerical validation and define logical `from_` and `to` boundary ranges for each Spinbox based on reasonable gameplay thresholds.
- Add an inline visual indicator (e.g., dynamic color highlighting on the label or a tiny icon tooltip) when a value reaches an extreme threshold (e.g., search interval below 0.1s).

### 3. Layout and Visual Cleanup
- Simplify the collapsible frame layouts (`_build_collapsible_group`) to reduce unnecessary `tk.LabelFrame` nesting. Rely on `UIStyleV2.SPACE_*` padding tokens and whitespace for visual hierarchy rather than solid borders.
- Refactor the "Bắt đầu Hunt:" and "Dừng Hunt:" labels within the Global Hotkeys section. They are currently slightly redundant; redesign this sub-section to be more concise (e.g., "Start/Stop Hotkeys"). Remember to update/add the necessary `i18n` keys in `lib/i18n/translations.py`.

### 4. Improve File Dialog UX
- When `_browse_template` is clicked, offload the blocking `filedialog.askopenfilename()` call properly, or at least disable the browse button temporarily while the native dialog is open to prevent UI freezing/multiple clicks.

## Constraints & Checks
- **No Hardcoded Strings**: Under no circumstances should raw language strings (e.g., `if self.lang == 'en'`) be introduced. Always use `self._t("key")` and define translations.
- **Zero Occlusion Rule**: The resulting UI must pass the `winfo_width() >= winfo_reqwidth()` heuristic check on an 800x600 window.
- **Tests**: Verify `run_tests.py` still passes. Mock `ResponsiveGridBase` behaviors if necessary.
