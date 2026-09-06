# UI REDESIGN PHASE 2 — Visual Reference & Layout Guide

**Status**: Ready for Implementation  
**Based on**: Design specification + Figma mockups  
**Updated**: 2026-09-06

---

## 🎨 Full Layout Preview (1366×768 Resolution)

```
┌────────────────────────────────────────────────────────────────────────────────────┐ 48px
│ ┌──────────────────────────┐  [●] Server    [●] Character    [●] Time  [▶ START]   │ HEADER
│ │ 🗺️ Chọn cửa số game...  │                                                       │
│ └──────────────────────────┘                                                       │
├──────────┬──────────────────────────────────────────────────────────────────────────┤
│          │                                                                          │
│  SIDEBAR │                   HUNT WORKSPACE (Main Content)                         │
│  200px   │                                                                          │
│          │  ┌─────────────────────────┬──────────────────────────┐                 │
│          │  │                         │                          │                 │
│  Săn     │  │  TARGET LIST            │  TARGET & STATUS         │                 │
│ ▶Thiết   │  │  (Left Top, 35%)        │  (Right Top, 50%)       │                 │
│  lập     │  │                         │                          │                 │
│          │  │  ┌─────────────────┐    │ [●] Ready               │                 │
│  Quản    │  │  │ Quái Đặc Biệt   │    │ 🐉 Monster Name         │                 │
│  lý      │  │  │ Cấp độ khủng    │    │ ┌────────┐  Cấp độ: XX  │                 │
│          │  │  │ Mục tiêu khác   │    │ │ Image  │  HP: ██████  │                 │
│  Thống   │  │  │                 │    │ │  80x80 │  Def: 1234   │                 │
│  Kê      │  │  └─────────────────┘    │ └────────┘  CD: -------│                 │
│          │  │  ▲▼◯✕                    │ [💾 Áp dụng Cài Đặt]     │                 │
│  Hỗ      │  │                         │                          │                 │
│  Trợ     │  ├─────────────────────────┼──────────────────────────┤                 │
│          │  │                         │                          │                 │
│          │  │  COMBO CHAIN            │  SKILL STATS             │                 │
│  🔧      │  │  (Left Bottom, 65%)     │  (Right Bottom, 50%)     │                 │
│ Thiết    │  │                         │                          │                 │
│  lập     │  │ ☑ Bật Auto [Alt+3] ⚙️  │  Kỹ Năng │ Lần │ Hái %  │                 │
│  nhanh    │  │                         │ ─────────┼─────┼────── │                 │
│          │  │ ┌──────────────────────┐│ Fireball │ 1m  │ 94%  ●│                 │
│          │  │ │Chain 1       │Chain 3││ Ice Bolt │ 2m  │ 87%  ●│                 │
│          │  │ │[Skill ▼]     │[Skill ││ Teleport│ 5m  │ 100% ●│                 │
│          │  │ │⏱ 0.5s 🔄 5s  │⏱ 1.2s ││                        │                 │
│          │  │ └──────────────────────┘│                        │                 │
│          │  │ ┌──────────────────────┐│                        │                 │
│          │  │ │Chain 2       │Chain 4││                        │                 │
│          │  │ │[Skill ▼]     │[Skill ││                        │                 │
│          │  │ │⏱ 0.5s 🔄 5s  │⏱ 1.2s ││                        │                 │
│          │  │ └──────────────────────┘│                        │                 │
│          │  │ ──────────────────────────                        │                 │
│          │  │ Buff Lanes                                       │                 │
│          │  │ ┌──────────────┐ ┌──────────────┐               │                 │
│          │  │ │ Buff 1       │ │ Buff 2       │               │                 │
│          │  │ │[Skill ▼]     │ │[Skill ▼]     │               │                 │
│          │  │ │⏱ 3.0s 🔄 30s │ │⏱ 2.0s 🔄 20s │               │                 │
│          │  │ └──────────────┘ └──────────────┘               │                 │
│          │  │                                                  │                 │
│          │  └─────────────────────────┴──────────────────────────┘                 │
│          │                                                                          │
├──────────┴──────────────────────────────────────────────────────────────────────────┤ 24px
│ ⠋ Đang kiểm tra CSDL...                        v2.1.0 · CSDL: ✓ · 0 lỗi           │ STATUS
└────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Component Details & States

### SIDEBAR (200px)

```
┌────────────────────┐
│ ⚔️ CABAL           │ ← Logo + Title (10px uppercase tracking-widest)
│    ASSISTANT       │
├────────────────────┤
│                    │
│ ▶ Săn              │ ← Active: bg-#1f2d1f, text-#4ade80, border-left-3px
│   Thiết lập        │
│   Quản lý Kỹ năng  │
│   Quản lý Quái     │
│   Quản lý Thư viện │
│                    │
│ 📊 Thống Kê        │ ← Section label: 10px uppercase
│   Thống kê         │
│   Hỗ Trợ           │
│                    │
│ 🔧 Thiết lập nhanh │ ← Last item
│                    │
└────────────────────┘

Colors:
- Background: #111111
- Border-right: 1px solid #2a2a2a
- Active: #1f2d1f (bg), #4ade80 (text), 3px left border
- Hover: #1a1a1a (bg), #d1d5db (text)
- Text: 13px Inter, icon 16px SVG
- Padding: 10px 12px per item
```

---

### HEADER (48px)

```
┌────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────┐  [●] Server    [●] Character  [▶ S]   │
│ │🗺️ Chọn cửa số game...  │                                     │
│ └──────────────────────┘ (Dropdown)      (Status chips)        │
└────────────────────────────────────────────────────────────────┘

Dropdown:
  - Width: 280px
  - Placeholder: "Chọn cửa số game..."
  - Icon: 🗺️ (map-pin, left side)
  - Adjacent button: 🔄 (refresh, 28×28px icon)
  - bg: #0f0f0f, border: 1px solid #333, radius: 6px

Status Chips:
  - Grid: 3 equal columns, gap 8px
  - Each: bg-#1a1a1a, border 1px solid #2a2a2a, radius 4px
  - Font: 12px text-#6b7280
  - Icon: 8px dot (● green if OK, red if error)
  
Start Button (Right):
  - Width: 120px, height: 32px
  - Font: 13px font-semibold, icon ▶️
  - Disabled: bg-#333, text-#6b7280, cursor not-allowed
  - Enabled: bg-#4ade80, text-black, hover +10% brightness
  - Tooltip on disabled: "Chọn cửa số trước"

Language:
  - Icon button: 🌐 (28×28px)
  - Dropdown on click: English / Tiếng Việt
```

---

### TARGET LIST PANEL (Left Top, 35%)

```
┌─────────────────────────────────────────────┐
│ Quái đặc chủng │ Tự nhân diện │ Mục tiêu khác │ ← Tab bar
├─────────────────────────────────────────────┤
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 🎯 Chưa có mục tiêu                    │ │ ← Empty state
│ │ Nhấn + để thêm hoặc kéo từ danh sách  │ │
│ └─────────────────────────────────────────┘ │
│                                     ▲▼◯✕   │ ← Action buttons
│                                             │
└─────────────────────────────────────────────┘

Tab Bar:
  - bg-#111111, border-bottom 1px solid #2a2a2a
  - Inactive tab: text-#6b7280, hover bg-#1a1a1a
  - Active tab: text-#4ade80, border-bottom 2px solid #4ade80

Listbox:
  - bg-#111111, border none
  - Each row: 8px padding, rounded 4px, margin 2px 0
  - Default: text-#d1d5db
  - Hover: bg-#1a1a1a
  - Selected: bg-#1f2d1f, left border 2px solid #4ade80

Empty State:
  - Icon: 🎯 (40px, opacity 20%)
  - Text: "Chưa có mục tiêu" (13px text-#6b7280)
  - Subtext: instruction (11px text-#555)
  - Centered with padding 24px

Action Buttons:
  - Layout: vertical stack, gap 6px (right side)
  - Each: 28×28px, bg-#222, border 1px solid #333, radius 4px
  - Icon: 16px text-#6b7280
  - Hover: bg-#1a1a1a, icon text-#d1d5db
  - Buttons: ↑ ↓ ◯ ✕ ⊕
```

---

### TARGET & STATUS PANEL (Right Top, 50%)

```
┌──────────────────────────────────────────┐
│ ┌──────────────────────────────────────┐ │
│ │ [●] Ready                            │ │ ← Status badge
│ │ ┌─────────┐  Mục Tiêu Không Xác Định │ │
│ │ │   🐉    │  Cấp độ: --              │ │ ← 2-column layout
│ │ │ 80×80   │  HP: ████████████ (100%)│ │    (60% image, 40% info)
│ │ │ Image   │  Phòng Thủ: --           │ │
│ │ └─────────┘                          │ │
│ │ ┌──────────────────────────────────┐ │ │
│ │ │ [💾 Áp dụng Cài đặt Săn]        │ │ │ ← Button
│ │ └──────────────────────────────────┘ │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘

Image Placeholder:
  - 80×80px, border-radius 8px
  - bg-#111111, border 1px solid #2a2a2a
  - When empty: icon 🐉 (40px, opacity 20%)
  - When loaded: actual monster sprite

Status Badge States:
  - Idle: bg-#292218, text-#f59e0b, icon ● → "Chờ"
  - Ready: bg-#1f2d1f, text-#4ade80, icon ● → "Sẵn sàng"
  - Hunting: bg-#1e2d3d, text-#38bdf8, icon ●(pulse) → "Đang săn"
  - Height: 24px, padding 4px 12px, border-radius 12px (pill)

Info Section:
  - Name: 16px font-semibold text-#d1d5db
  - Type: 12px text-#6b7280
  - Level: "Lv. XX" 13px text-#9ca3af

HP Bar:
  - Height: 8px, width 100%
  - Background: #1f1f1f
  - Fill: linear-gradient(90deg, #dc2626 → #f97316)
  - border-radius: 4px
  - Label right: "HP: 1234/5678 (42%)" 11px text-#6b7280

Stats Grid (3 columns):
  - Cấp độ │ Máu    │ Phòng Thủ
  - Level  │ HP/Max │ Defense
  - ────── │ ────── │ ────────
  - Each cell: label 10px text-#555, value 14px text-#d1d5db mono
  - Border-bottom: 1px solid #1f1f1f
  - Padding: 8px 0

Action Button:
  - Width: 100%, height: 36px
  - bg-#4ade80, text-black, icon 💾
  - Font: 13px font-semibold
  - border-radius: 6px
  - Hover: brightness(110%), Active: brightness(90%)
```

---

### COMBO CHAIN PANEL (Left Bottom, 65%)

```
┌────────────────────────────────────────────────────┐
│ ☑ Bật Auto Combo    [Alt+3]    ⚙️                 │ ← Header
├────────────────────────────────────────────────────┤
│                                                    │
│ ┌──────────────┬──────────────┬──────────────┐    │
│ │ Chain 1      │ Chain 3      │              │    │
│ │[Fireball  ▼] │[Ice Bolt  ▼] │              │    │
│ │⏱ 0.5s  🔄 5s │⏱ 1.2s  🔄 10s│              │    │
│ └──────────────┴──────────────┴──────────────┘    │
│                                                    │
│ ┌──────────────┬──────────────┐                   │
│ │ Chain 2      │ Chain 4      │                   │
│ │[Skill    ▼]  │[Skill    ▼]  │                   │
│ │⏱ 0.5s  🔄 5s │⏱ 1.2s  🔄 10s│                   │
│ └──────────────┴──────────────┘                   │
│                                                    │
│ ─────────────── Buff Lanes ───────────────────    │ ← Divider
│                                                    │
│ ┌──────────────────┬──────────────────┐           │
│ │ Buff Lane 1      │ Buff Lane 2      │           │
│ │[Heal Spell  ▼]   │[Buff Spell  ▼]   │           │
│ │⏱ 3.0s  🔄 30s    │⏱ 2.0s  🔄 20s    │           │
│ └──────────────────┴──────────────────┘           │
│                                                    │
└────────────────────────────────────────────────────┘

Header:
  - Checkbox: 18×18px, border 2px solid #2a2a2a
    - Unchecked: empty
    - Checked: bg-#4ade80, icon ✓ white, animation pop 200ms
  - Label: "Bật Auto Combo" 13px text-#d1d5db
  - Keyboard badge: "Alt+3" 10px, bg-#1a1a1a, border-primary, radius 4px
  - Settings icon: ⚙️ 16px text-#6b7280 (button, 28×28px)

Combo Chain Cards:
  - Layout: 4 cards per row (25% width each, gap 6px)
  - bg-#1a1a1a, border 1px solid #2a2a2a, radius 6px, padding 8px
  - Label: "Chain 1/2/3/4" 10px text-#6b7280 uppercase
  - Dropdown: full width, bg-#0f0f0f, border 1px solid #333, padding 6px
  - Stats: "⏱ 0.5s" + "🔄 5s" 11px text-#6b7280 (2-column grid)

Buff Lanes Section:
  - Divider: margin 12px 0, border-top 1px solid #2a2a2a
  - Label: "Buff Lanes" 10px uppercase text-#6b7280 (centered)
  - Cards: same style as Combo Chain but bg-#161616 (different shade)
  - 2 cards per row (50% width each, gap 6px)
```

---

### SKILL STATS TABLE (Right Bottom, 50%)

```
┌──────────────────────────────────────────────┐
│ Kỹ Năng        │ Lần Cuối │ Hái Chiêu │ Tỷ % │ ← Header (sticky)
├──────────────────────────────────────────────┤
│ Fireball       │ 1m ago   │ 24        │ ████ 96% │
│ Ice Bolt       │ 3m ago   │ 18        │ ███░ 75% │
│ Teleport       │ 5m ago   │ 12        │ █████ 100%│
│ Flame Burst    │ 7m ago   │ 8         │ ██░░ 42% │
│                                              │
│ (scroll)                                     │
└──────────────────────────────────────────────┘

Table Header (Sticky):
  - bg-#111111, border-bottom 1px solid #2a2a2a
  - Position: sticky, top: 0
  - Font: 11px uppercase tracking-wider text-#555
  - Padding: 8px 10px
  - Columns: Kỹ Năng (40%) │ Lần Cuối (20%) │ Hái Chiêu (20%) │ Tỷ % (20%)

Table Rows:
  - Height: 28px, padding: 6px 10px
  - Font: 12px text-#d1d5db
  - Border-bottom: 1px solid #1f1f1f
  - Striped: alternating bg-#1a1a1a / bg-#111111
  - Hover: bg-#1f1f1f, cursor pointer

Columns:
  - Kỹ Năng: text-primary font-semibold (skill name)
  - Lần Cuối: text-secondary font-mono (timestamp: "1m ago")
  - Hái Chiêu: text-#4ade80 font-mono (number: "24")
  - Tỷ %: inline bar chart
    - BG bar: bg-#1f1f1f, height 4px
    - Fill: bg-#4ade80, opacity 60%, width = value%
    - Text: 11px text-#6b7280, positioned right

Empty State:
  - Icon: 📊 (40px, opacity 20%)
  - Text: "Chưa có dữ liệu kỹ năng" 13px text-#6b7280
  - Subtext: "Bắt đầu săn để thu thập thống kê" 11px text-#555
  - Centered with padding 24px

Scrollbar (Custom):
  - Width: 4px
  - Track: transparent
  - Thumb: bg-#333, hover bg-#555
  - border-radius: 2px
```

---

### STATUS BAR (24px)

```
┌────────────────────────────────────────────────────────────────┐
│ ⠋ Đang kiểm tra CSDL...              v2.1.0 · CSDL: ✓ · 0 lỗi │
└────────────────────────────────────────────────────────────────┘

Layout:
  - Height: 24px, padding: 0 12px
  - Background: #0a0a0a
  - Border-top: 1px solid #1f1f1f
  - Display: flex, justify-content space-between
  - Position: fixed, bottom: 0, left: 0, right: 0, z-index: 100

Left Section:
  - Spinner: 10×10px animated dots (cycling: · ·· ···)
  - Text: "Đang kiểm tra CSDL..." (11px text-#6b7280)
  - Animation: dots cycle every 1s

Right Section:
  - Version: "v2.1.0" 11px text-#6b7280
  - Separator: "·" 11px text-#6b7280
  - DB Status: "CSDL: ✓" (text-#4ade80) or "CSDL: ✕" (text-#dc2626)
  - Error count: "0 lỗi" (or number of errors)
```

---

## 🎨 Color Tokens Cheat Sheet

| Use Case | Token | Color | Example |
|----------|-------|-------|---------|
| **Backgrounds** | | | |
| Main app | bg-base | #0f0f0f | Root container |
| Panels/Cards | bg-surface | #1a1a1a | Panel wrappers |
| Elevated (sidebar) | bg-elevated | #111111 | Sidebar, header, inputs |
| Status bar | bg-subtle | #0a0a0a | Bottom bar |
| | | | |
| **Borders** | | | |
| Standard | border-primary | #2a2a2a | Panel edges |
| Subtle | border-subtle | #1f1f1f | Dividers |
| | | | |
| **Text** | | | |
| Main content | text-primary | #d1d5db | Body text |
| Secondary | text-secondary | #9ca3af | Labels, subtext |
| Muted | text-muted | #6b7280 | Tertiary text |
| Subtle | text-subtle | #374151 | Placeholders |
| | | | |
| **Accents** | | | |
| Primary action | accent-green | #4ade80 | Active, success |
| Primary bg tint | accent-green-bg | #1f2d1f | Active background |
| Warning | accent-amber | #f59e0b | Idle, warning state |
| Info | accent-blue | #38bdf8 | Running, info |
| Danger | danger | #dc2626 | Errors, critical |

---

## 📐 Spacing Scale

```
Spacing units (multiples of 4px):
xs   = 4px   (buttons, gaps)
sm   = 8px   (padding, small gaps)
md   = 12px  (default padding)
lg   = 16px  (section padding)
xl   = 24px  (large gaps)

Border Radius:
sm   = 4px   (inputs, small elements)
md   = 6px   (buttons, cards)
lg   = 8px   (panels)
xl   = 12px  (large sections)
```

---

## ✨ State Animations

```
Transition Properties:
- Default: 200ms ease-in-out
- Fast: 100ms ease-in
- Slow: 300ms ease-out

Examples:
Button hover:
  background: 200ms ease-in-out
  opacity: 100ms ease-in

Checkbox check:
  animation: pop 200ms cubic-bezier(0.68, -0.55, 0.265, 1.55)
  (bounce effect)

Status badge pulse (hunting):
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1)
  opacity: 0% → 100% → 0%
```

---

## 🖼️ Screenshot Evidence Checklist

After implementing each phase, capture screenshots at these resolutions:

**Resolution 1: 1024×600 (Minimum)**
- [ ] Sidebar visible, not overlapping
- [ ] Header complete with dropdown and buttons
- [ ] All 4 panels visible (scroll if needed)
- [ ] No overlapping text or components
- [ ] Status bar at bottom

**Resolution 2: 1366×768 (Standard)**
- [ ] All panels visible without scroll
- [ ] Perfect 60/40 column split in hunt panel
- [ ] All text readable
- [ ] Spacing correct and consistent

**Resolution 3: 1920×1080 (Full HD)**
- [ ] Responsive scaling works
- [ ] No excessive empty space
- [ ] Components maintain proportions
- [ ] Professional appearance

**DPI Scaling**:
- [ ] 100% DPI test
- [ ] 125% DPI test (font sizes increase)
- [ ] 150% DPI test (all elements scale)

---

## 🚀 Implementation Checklist

### Phase 2.1: Design System (Week 1)
- [ ] Create `lib/ui_style_v2.py`
- [ ] Define all color tokens
- [ ] Create font constants
- [ ] Create spacing constants
- [ ] Test token system with demo file

### Phase 2.2: Sidebar (Week 1)
- [ ] Logo + title section
- [ ] Icon buttons with SVG
- [ ] Active/hover states
- [ ] Group labels
- [ ] Test navigation

### Phase 2.3: Header (Week 1)
- [ ] Window selector dropdown
- [ ] Status chips display
- [ ] Start button with states
- [ ] Language selector
- [ ] Tooltips

### Phase 2.4-2.7: Main Panels (Week 2)
- [ ] Hunt list panel
- [ ] Target panel
- [ ] Combo chain panel
- [ ] Skill stats table

### Phase 2.8-2.9: Finalization (Week 3)
- [ ] Status bar
- [ ] Integration testing
- [ ] DPI scaling validation
- [ ] Screenshot evidence
- [ ] Performance optimization

---

**Next Step: Read `PROMPT-UI-REDESIGN-PHASE-2.md` for detailed implementation guide**
