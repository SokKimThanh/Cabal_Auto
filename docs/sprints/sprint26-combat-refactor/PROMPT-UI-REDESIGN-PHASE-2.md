# UI REDESIGN PHASE 2: Modern Dark Theme Implementation

**Version**: 2.0  
**Date**: 2026-09-06  
**Status**: Ready for Implementation  
**Priority**: HIGH (Current UI appearance degrading user experience)  
**Target**: Complete redesign with modern dark theme, component system, and improved UX

---

## 🎯 Executive Summary

The current Cabal Auto UI feels outdated and inconsistent. This phase implements a **complete visual redesign** using:
- Modern dark theme (#0f0f0f base)
- Cohesive color system (accent-green #4ade80 for actions)
- Component-based styling system
- Improved information hierarchy
- Better visual feedback and states

**Timeline**: 2-3 weeks  
**Scope**: Sidebar, Header, Hunt Panel, Status displays, Tables, Buttons  
**Non-Breaking**: All functionality preserved, UI only

---

## 📋 Design System Foundation

### Color Palette (Semantic Tokens)

```
BACKGROUNDS:
  bg-base        #0f0f0f  → Main app background
  bg-surface     #1a1a1a  → Panels, cards, elevated content
  bg-elevated    #111111  → Sidebar, header, inputs, surfaces
  bg-subtle      #0a0a0a  → Status bar, dividers
  
BORDERS & DIVIDERS:
  border-primary #2a2a2a  → Standard panel borders
  border-subtle  #1f1f1f  → Subtle dividers, secondary borders
  
TEXT:
  text-primary   #d1d5db  → Main content text (88% opacity #fff)
  text-secondary #9ca3af  → Secondary text (60% opacity #fff)
  text-muted     #6b7280  → Tertiary text (45% opacity #fff)
  text-subtle    #374151  → Placeholders (28% opacity #fff)
  
ACCENT COLORS:
  accent-green   #4ade80  → Active, success, primary actions
  accent-green-bg #1f2d1f → Green background tint
  accent-amber   #f59e0b  → Warning, waiting state
  accent-blue    #38bdf8  → Info, running/active state
  danger         #dc2626  → Errors, critical, health low
  
OPACITIES:
  Disabled       20% opacity
  Hover          +10% opacity or +1 shade lighter
  Focus          Border + shadow highlight
```

### Typography

```
Font Stack:
  UI: "Inter", "Segoe UI", sans-serif
  Data/Code: "JetBrains Mono", "Courier New", monospace

Sizes:
  Title/Section   16px weight-600  (h3)
  Header         14px weight-600  (h4)
  Body           13px weight-400  (p)
  Label          12px weight-500  (label)
  Small          11px weight-400  (caption)
  Tiny           10px weight-500  (badge, tag)
```

### Spacing & Radius

```
Spacing:
  xs   4px
  sm   8px
  md   12px
  lg   16px
  xl   24px
  
Border Radius:
  sm   4px    (inputs, small elements)
  md   6px    (buttons, cards)
  lg   8px    (panels)
  xl   12px   (large sections)
```

---

## 🎨 Component Specifications

### 1. Sidebar (Left Navigation) — 200px Fixed

**Structure**:
```
┌─────────────────────────┐
│ ⚔️ CABAL ASSISTANT      │ ← Logo + Title (16px top)
│                         │
│ ▶ Săn                   │ ← Active item (highlighted)
│   Thiết lập             │
│   Quản lý Kỹ năng       │
│   Quản lý Quái          │
│   Quản lý Thư viện      │
│                         │
│ 📊 Thống Kê            │
│ ❓ Hỗ trợ              │
│                         │
│ 🔧 Thiết lập nhanh      │
└─────────────────────────┘
```

**Design Details**:
- Width: 200px (fixed)
- Height: 100vh
- Background: #111111
- Border-right: 1px solid #2a2a2a
- Padding: 16px vertical, 8px horizontal

**Header Section** (Logo):
- Icon: 24×24px (Cabal sword/emblem SVG)
- Text: "CABAL ASSISTANT" 10px uppercase tracking-widest text-accent-green
- Padding-top: 16px, padding-bottom: 12px
- Border-bottom: 1px solid #2a2a2a

**Menu Items**:
- Padding: 10px 12px (compact)
- Margin: 6px 4px
- Font: 13px, text-primary
- Icon: 16×16px SVG + 8px gap + label
- Border-radius: 6px

**States**:
- Default: bg-transparent, text-secondary, icon text-muted
- Hover: bg-elevated, text-primary, icon text-primary
- Active: 
  - bg-accent-green-bg
  - text-accent-green
  - icon text-accent-green
  - Border-left: 3px solid accent-green
  - Padding-left: 9px (accommodate border)

**Group Labels** (Section Headers):
- Font: 10px uppercase tracking-wider
- Color: text-muted
- Margin-top: 16px
- Margin-bottom: 6px
- Padding-left: 12px
- Not clickable

**Icons** (SVG-based):
```
Săn              → 🎯 target
Thiết lập        → ⚙️ settings
Quản lý Kỹ năng  → ⚔️ sword/skill
Quản lý Quái     → 🐉 dragon/monster
Quản lý Thư viện → 📚 book/library
Thống Kê         → 📊 chart
Hỗ Trợ           → ❓ help
Thiết lập nhanh  → 🔧 wrench
```

---

### 2. Header (Top Bar) — 48px

**Structure**:
```
┌────────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────┐  [●] Server  [●] Character  [●] Status │
│ │ 🗺️ Chọn cửa số...     │                                          │
│ │ (Dropdown with refresh) │                                 [Start] │
│ └─────────────────────────┘                                         │
└────────────────────────────────────────────────────────────────────┘
```

**Design Details**:
- Height: 48px
- Background: #111111
- Border-bottom: 1px solid #2a2a2a
- Padding: 8px 12px
- Display: flex, align-items center, justify-content space-between

**Left: Window Selector**:
- Dropdown width: 280px
- Background: #0f0f0f
- Border: 1px solid #333
- Border-radius: 6px
- Padding: 8px 12px
- Placeholder: "Chọn cửa số game..."
- Icon: 🗺️ map-pin (left)
- Refresh button: 28×28px icon-only next to dropdown
  - bg-transparent, hover bg-elevated
  - Icon: 🔄 refresh

**Center: Status Chips** (3 columns):
- Grid layout, gap 8px
- Each chip: bg-elevated, border 1px solid border-primary, border-radius 4px, padding 6px 10px
- Font: 12px text-muted
- Icons: ● 8px dot (text-accent-green if OK, text-danger if error)
- Content: `[●] Server: <status>` | `[●] Character: <name>` | `[●] Time: HH:MM`

**Right: Action Buttons**:
- Start Hunt Button:
  - Width: 120px, height: 32px
  - Font: 13px font-semibold
  - Icon: ▶️ (left 6px gap)
  - State 1 (not ready): bg-disabled (#333), text-muted, cursor-not-allowed, tooltip "Chọn cửa số trước"
  - State 2 (ready): bg-accent-green, text-black, cursor-pointer, hover bg-accent-green (+10% brightness)
  - Border-radius: 6px
  - Transition: 200ms

- Language Selector:
  - Icon-only button: 🌐
  - 28×28px, bg-transparent, border 1px solid transparent
  - Hover: border-primary
  - Dropdown menu on click: "English", "Tiếng Việt"

---

### 3. Hunt Panel — Target List (Left Top, 35% height)

**Panel Wrapper**:
- Background: #1a1a1a
- Border: 1px solid #2a2a2a
- Border-radius: 8px
- Overflow: hidden (for tab bar radius)

**Tab Bar**:
- Background: #111111
- Display: flex (tabs)
- Border-bottom: 1px solid #2a2a2a
- Each tab: padding 10px 14px, font 13px, text-muted
- Active tab:
  - text-accent-green
  - border-bottom: 2px solid accent-green (overrides panel border)
  - background: rgba(74, 222, 128, 0.05)

**Content Area**:
- Background: #0f0f0f
- Padding: 8px
- Max-height: calc(35% - 32px for tab bar)
- Overflow: auto

**Listbox** (Target list):
- Border: none (already in panel)
- Background: #111111
- Each row: padding 8px, border-radius 4px, margin-bottom 2px
- Font: 13px text-primary
- Row hover: bg-elevated
- Row selected: bg-accent-green-bg, border-left 2px solid accent-green

**Empty State**:
- Icon: 🎯 (32px, opacity 30%)
- Text: "Chưa có mục tiêu"
- Subtext: "Nhấn + để thêm hoặc kéo từ danh sách quái"
- Alignment: center, padding: 24px

**Action Buttons** (Right side, small icons):
- Layout: vertical stack, gap 6px
- Each button: 28×28px, border-radius 4px
- Background: #222222
- Border: 1px solid #333
- Icon: 16×16px, text-muted
- Hover: bg-elevated, icon text-primary
- Tooltip on hover (12px, bg-elevated, border-primary)

**Buttons**:
```
↑      Move Up
↓      Move Down
◯      Toggle Enable/Disable
✕      Delete
⊕      Add New
```

---

### 4. Target & Status Panel (Right Top, 50% height)

**Layout**: 2-column (60% image, 40% stats)

**Left Column (Image)**:
- Image placeholder: 80×80px, border-radius 8px, background #111111
- Border: 1px solid #2a2a2a
- When empty: icon 🐉 (40px, opacity 20%)
- When loaded: actual monster image

**Right Column (Info)**:
- Layout: flex column, gap 8px

**Status Badge**:
- Height: 24px
- Border-radius: 12px (pill)
- Font: 12px font-semibold
- Padding: 4px 12px
- Icon + text

- States:
  - Idle: bg-#292218, text-amber (#f59e0b), icon ● → "Chờ"
  - Ready: bg-#1f2d1f, text-accent-green, icon ● → "Sẵn sàng"
  - Hunting: bg-#1e2d3d, text-accent-blue, icon ● (pulse animation) → "Đang săn"

**Monster Info**:
- Name: 16px font-semibold text-primary
- Type: 12px text-muted
- Level: "Lv. XX" 13px text-secondary

**HP Bar**:
- Height: 8px
- Width: 100% of container
- Background: #1f1f1f
- Fill: linear-gradient(90deg, #dc2626 → #f97316)
- Border-radius: 4px
- Overflow: hidden
- Label (right): "HP: 1234/5678 (42%)" 11px text-muted, margin-top 4px

**Stats Grid** (3 columns):
- Grid: 3 equal columns, gap 8px
- Each stat:
  - Label: 10px uppercase text-muted
  - Value: 14px font-mono text-primary
  - Border-bottom: 1px solid border-subtle
  - Padding: 8px 0

- Stats:
  ```
  Cấp độ    Máu        Phòng thủ
  Level     HP/Max     Defense
  ────      ────       ────
  ```

**Action Button**:
- Width: 100%
- Height: 36px
- Font: 13px font-semibold
- Background: accent-green
- Text: black
- Icon: 💾 save (left)
- Hover: brightness(110%)
- Active: brightness(90%)
- Border-radius: 6px

---

### 5. Combo Chain Panel (Left Bottom, 65% height)

**Header Section**:
- Display: flex, align-items center, gap 12px
- Padding: 10px 12px
- Border-bottom: 1px solid border-primary
- Background: #111111

**Auto Combo Checkbox**:
- Custom checkbox: 18×18px
- Border: 2px solid border-primary
- Background: transparent
- When unchecked: empty
- When checked: background accent-green, icon ✓ white, animation pop 200ms
- Label: "Bật Auto Combo" 13px text-primary
- Keyboard badge: "Alt+3" 10px, bg-elevated, border border-subtle, border-radius 4px, padding 2px 6px

**Settings Icon**:
- Button: 28×28px, bg-transparent, border none
- Icon: ⚙️ 16px text-muted
- Hover: text-primary

**Content Area**:
- Padding: 10px
- Background: #0f0f0f
- Overflow: auto

**Combo Chain Slots** (4 cards):
- Each card: width calc(25% - 6px), aspect-ratio, bg-elevated
- Border: 1px solid border-primary
- Border-radius: 6px
- Padding: 8px
- Margin: 3px
- Display: inline-block

**Card Content**:
- Label: "Chain 1/2/3/4" 10px text-muted uppercase
- Dropdown: full width, bg-#0f0f0f, border 1px solid border-subtle, padding 6px
- Stat row: "⏱ Cast: 0.5s" + "🔄 CD: 5.0s" 11px text-muted, display grid 2 columns

**Divider Between Sections**:
- Margin: 12px 0
- Border-top: 1px solid border-primary
- Label: "Buff Lanes" 10px uppercase text-muted, centered in divider background

**Buff Lanes** (2 slots):
- Same card style as Combo Chain
- Background: #161616 (slightly different to indicate role)
- Width: calc(50% - 6px)

---

### 6. Skill Stats Panel (Right Bottom, 50% height)

**Table Structure**:
- Full width, height: 100%
- Overflow: auto (with custom scrollbar)
- Border: 1px solid border-primary
- Border-radius: 6px (bottom corners)

**Table Header**:
- Background: #111111
- Border-bottom: 1px solid border-primary
- Sticky (position: sticky, top: 0)
- Padding: 8px 10px
- Font: 11px uppercase tracking-wider text-muted

Columns:
```
Kỹ Năng        Lần Cuối    Hái Chiêu    Tỷ Lệ %
Skill Name     Last Hit    Hit Count    Success %
```

**Empty State**:
- Icon: 📊 (40px, opacity 20%)
- Text: "Chưa có dữ liệu kỹ năng" 13px text-muted
- Subtext: "Bắt đầu săn để thu thập thống kê" 11px text-subtle
- Alignment: center, padding: 24px

**Table Rows**:
- Height: 28px
- Padding: 6px 10px
- Font: 12px text-primary
- Border-bottom: 1px solid border-subtle
- Striped: alternating bg-elevated / bg-#0f0f0f

- Row hover: bg-#1f1f1f, cursor pointer

**Columns**:
- Kỹ Năng: text-primary font-semibold
- Lần Cuối: text-secondary font-mono (timestamp)
- Hái Chiêu: text-accent-green font-mono
- Tỷ Lệ %: inline bar chart
  - Background bar: bg-elevated, height 4px
  - Fill bar: bg-accent-green, opacity 60%, width = value%
  - Value text: 11px text-muted, positioned right

**Scrollbar** (Custom):
- Width: 4px
- Track: bg-transparent
- Thumb: bg-#333
- Thumb hover: bg-#555
- Border-radius: 2px

---

### 7. Status Bar (Bottom, 24px)

**Structure**:
```
┌────────────────────────────────────────────────┐
│ ⠋ Đang kiểm tra CSDL...    v2.1.0 · CSDL: ✓ · 0 │
└────────────────────────────────────────────────┘
```

**Design**:
- Height: 24px
- Background: #0a0a0a
- Border-top: 1px solid #1f1f1f
- Padding: 0 12px
- Display: flex, align-items center, justify-content space-between
- Font: 11px text-muted
- Position: fixed, bottom 0

**Left Section**:
- Spinner animation: 10×10px (animated dots)
- Status text: "Đang kiểm tra CSDL..." (animates to 3 states with dots: · ·· ···)

**Right Section**:
- Version: "v2.1.0"
- Separator: "·"
- DB Status: "CSDL: ✓" (text-accent-green) or "CSDL: ✕" (text-danger)
- Error count: "0 lỗi" (or number of errors)

---

## 🔧 Implementation Path

### Phase 2.1: Design System & Tokens (Week 1)

**Tasks**:
1. [ ] Create `lib/ui_style_v2.py` with all color tokens
2. [ ] Define all font sizes, weights, spacing constants
3. [ ] Create reusable style dictionaries for buttons, inputs, panels
4. [ ] Update `pyproject.toml` with font dependencies (Inter, JetBrains Mono)
5. [ ] Create test file to visualize all tokens

**Deliverable**: Token system ready for components

---

### Phase 2.2: Sidebar Redesign (Week 1)

**Tasks**:
1. [ ] Refactor sidebar layout (logo + menu)
2. [ ] Implement icon buttons with SVG icons
3. [ ] Style active/hover states with accent-green
4. [ ] Add group labels and section styling
5. [ ] Implement smooth transitions

**Deliverable**: New sidebar matching design spec

---

### Phase 2.3: Header Redesign (Week 1)

**Tasks**:
1. [ ] Build window selector dropdown with icons
2. [ ] Add 3 status chips (Server, Character, Time)
3. [ ] Implement Start button with enable/disable state
4. [ ] Add language selector dropdown
5. [ ] Add tooltips for disabled state

**Deliverable**: New header with all interactive elements

---

### Phase 2.4: Hunt Panel (List) Redesign (Week 2)

**Tasks**:
1. [ ] Refactor tab bar styling (unified design)
2. [ ] Redesign listbox with hover/select states
3. [ ] Create empty state with icon and guidance
4. [ ] Build icon-only action buttons (move, toggle, delete, add)
5. [ ] Add tooltips to all buttons

**Deliverable**: Polished hunt list panel

---

### Phase 2.5: Target & Status Panel Redesign (Week 2)

**Tasks**:
1. [ ] Create 2-column layout (image + info)
2. [ ] Build status badge with 3 states (Idle/Ready/Hunting)
3. [ ] Implement gradient HP bar
4. [ ] Create 3-column stats grid
5. [ ] Style action button

**Deliverable**: Redesigned target display panel

---

### Phase 2.6: Combo Chain Panel Redesign (Week 2)

**Tasks**:
1. [ ] Style custom checkbox with animation
2. [ ] Create combo slot cards (4×1 + 2×1 layout)
3. [ ] Add stat rows (Cast time + CD)
4. [ ] Build Buff Lanes section with divider
5. [ ] Add keyboard shortcut badge

**Deliverable**: Modern combo chain UI

---

### Phase 2.7: Skill Stats Table Redesign (Week 2)

**Tasks**:
1. [ ] Implement sticky header
2. [ ] Create striped row styling
3. [ ] Build inline bar chart for % column
4. [ ] Create empty state
5. [ ] Style custom scrollbar

**Deliverable**: Professional stats table

---

### Phase 2.8: Status Bar Redesign (Week 2)

**Tasks**:
1. [ ] Create bottom status bar with spinner
2. [ ] Add animated status text (dots cycling)
3. [ ] Implement version + DB status display
4. [ ] Add error count indicator

**Deliverable**: Polished status bar

---

### Phase 2.9: Integration & Polish (Week 3)

**Tasks**:
1. [ ] Test all components at different screen sizes (1024, 1366, 1920)
2. [ ] Test DPI scaling (100%, 125%, 150%)
3. [ ] Add transition animations for state changes
4. [ ] Implement dark/light theme toggle (if requested)
5. [ ] Performance optimization (scrolling, animations)
6. [ ] Screenshot evidence at 3+ resolutions

**Deliverable**: Production-ready UI

---

## 🎯 Success Criteria

### Visual Quality
- [ ] No hardcoded colors (all tokens from design system)
- [ ] Consistent spacing and alignment
- [ ] Smooth hover/active state transitions
- [ ] Professional appearance (no "gớm" feeling)
- [ ] Screenshots show polished UI

### Functionality
- [ ] All existing features work
- [ ] No breaking changes
- [ ] Responsive at 1024×600, 1366×768, 1920×1080
- [ ] DPI scaling works (100%, 125%, 150%)
- [ ] Tooltips show on hover

### Code Quality
- [ ] All colors come from `lib/ui_style_v2.py`
- [ ] No inline hex colors
- [ ] Consistent font usage
- [ ] Clean component hierarchy
- [ ] Documented design tokens

### Testing
- [ ] Visual regression tests (screenshot comparison)
- [ ] Unit tests for state changes
- [ ] Integration tests (sidebar click → view switch)
- [ ] User acceptance testing (manual review)

---

## 📊 Design Preview

See Figma design: https://www.figma.com/design/... (High-fidelity mockups with all states)

Key screenshots:
1. **Sidebar** - Logo, active states, icons
2. **Header** - Window selector, status chips, start button states
3. **Hunt Panel** - List with empty state, action buttons
4. **Target Panel** - Status badge animations, HP bar, stats
5. **Combo Chain** - Card layout, Buff Lanes section
6. **Skill Stats** - Table with striped rows, inline bar chart
7. **Full Layout** - All panels together at 1366×768

---

## 🔗 Integration with Workspace Redesign

This UI redesign is **Phase 2** of the larger Workspace Redesign project:

- **Phase 1 (✅ Complete)**: Database layer + Service layer (SkillPresetService, etc.)
- **Phase 2 (Current)**: Visual redesign with modern dark theme
- **Phase 3 (Next)**: Panel extraction and logic reorganization
- **Phase 4 (Later)**: Full 4-panel responsive layout

This redesign prepares the UI for Phase 3 by:
1. Creating consistent component patterns
2. Establishing design tokens (easier to extract)
3. Improving code organization (styled sections)
4. Building confidence in UI changes before refactoring logic

---

## 📝 Notes

### What's NOT Changing
- Core hunt logic and orchestration
- Database or service layer
- Keyboard shortcuts and hotkeys
- File structure (still `app_gui.py`, `ui/tabs/`, etc.)

### What's CHANGING
- Every visible color and style
- Component spacing and sizing
- Icon usage and visual indicators
- State representations (badges, animations)
- Scrollbar and UI polish

### Browser/Version Support
- Python 3.10+
- Tkinter 8.6+
- Windows 10/11
- DPI aware (100%-200%)

---

## ✅ Commit Strategy

After each weekly phase, commit with clear messages:

```bash
git add .
git commit -m "refactor(ui): redesign [component] - modern dark theme

- Updated colors to token system
- Improved spacing and alignment
- Added hover/active state styling
- [Component] now matches design spec

See: docs/sprints/sprint26-combat-refactor/PROMPT-UI-REDESIGN-PHASE-2.md"

git push origin feature/ui-redesign-phase2
```

Then create PR with screenshot evidence.

---

## 🚀 Getting Started

1. Create feature branch: `git checkout -b feature/ui-redesign-phase2`
2. Review design specs above
3. Start with Phase 2.1 (Design System tokens)
4. Build incrementally, testing after each phase
5. Document progress in ticket tracking
6. Screenshot at 3 resolutions as evidence

---

**Ready to begin? Start with Phase 2.1: Create the design token system in `lib/ui_style_v2.py`**
