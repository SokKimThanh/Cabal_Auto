# 🎯 UI REDESIGN MASTER PLAN — Sprint 26 Phase 2

**Project**: Cabal Auto Hunt — UI Modernization  
**Status**: Ready to Build (Phase 2 begins immediately after)  
**Timeline**: 2-3 weeks (iterative, weekly phases)  
**Priority**: HIGH (Current UI degrading UX perception)

---

## 📚 Document Structure

You now have a complete redesign specification across 3 documents:

### 1. **PROMPT-UI-REDESIGN-PHASE-2.md** ⭐ START HERE
   - Executive summary and design philosophy
   - Complete color token system (semantic naming)
   - Typography and spacing system
   - All 7 component specifications (detailed)
   - 9-week phase breakdown with deliverables
   - Success criteria and testing strategy
   - Integration with larger workspace redesign

### 2. **PROMPT-UV-ui-visual-reference.md** 🎨 FOR VISUAL DESIGN
   - ASCII layout preview (full 1366×768)
   - Component-by-component visual breakdown
   - Color token cheat sheet
   - Spacing scale reference
   - State animations guide
   - Screenshot evidence checklist

### 3. **mô tả cải thiện giao diện.md** (Original design brief)
   - Original Vietnamese design requirements
   - Detailed problem analysis
   - Component improvement specifics

---

## 🚀 Quick Start Guide

### If you want to **BEGIN IMPLEMENTATION NOW**:

**Step 1: Read the spec** (30 minutes)
```bash
# Open in editor:
cat docs/sprints/sprint26-combat-refactor/PROMPT-UI-REDESIGN-PHASE-2.md
```

**Step 2: Create feature branch**
```bash
git checkout -b feature/ui-redesign-phase2
```

**Step 3: Start Phase 2.1 (Design System)**
```bash
# Create: lib/ui_style_v2.py
# Import: All color tokens, fonts, spacing constants
# Test: Create a test file to visualize tokens
```

**Step 4: Test after each phase**
```bash
python app_gui.py
# Take screenshots at 1024×600, 1366×768, 1920×1080
# Commit with evidence
```

---

## 🎨 Visual Preview

The redesign transforms the UI from:

### ❌ CURRENT STATE (Outdated):
```
- Inconsistent colors (mismatched themes in panels)
- Large wasted space above sidebar
- Unclear visual hierarchy
- Poor contrast and hard-to-read text
- Clunky buttons and controls
- No active state indicators
- Overwhelming color palette
- Feels "gớm" (ugly/outdated)
```

### ✅ NEW STATE (Modern):
```
- Unified dark theme (#0f0f0f base)
- Accent-green (#4ade80) for all interactive elements
- Clear information hierarchy
- Improved contrast (readability)
- Polished components with smooth states
- Visual active state indicators (borders, backgrounds)
- Professional color palette
- Feels premium and modern
```

---

## 📊 Phase Breakdown Summary

| Phase | Component | Duration | Deliverable | Status |
|-------|-----------|----------|-------------|--------|
| 2.1 | Design System | 3 days | `lib/ui_style_v2.py` | Ready |
| 2.2 | Sidebar | 2 days | New sidebar with logo + icons | Ready |
| 2.3 | Header | 2 days | Window selector + status chips | Ready |
| 2.4 | Hunt List Panel | 2 days | Styled tab bar + listbox | Ready |
| 2.5 | Target Panel | 2 days | Status badges + HP bar + stats | Ready |
| 2.6 | Combo Chain | 2 days | Card layout + Buff Lanes | Ready |
| 2.7 | Skill Stats Table | 2 days | Striped rows + inline bar chart | Ready |
| 2.8 | Status Bar | 1 day | Spinner + version info | Ready |
| 2.9 | Integration & Polish | 3 days | Testing + DPI scaling + screenshots | Ready |

**Total: 15 working days (3 weeks)**

---

## 🎯 What's Changing vs What's NOT

### ✅ VISUAL ONLY (No Logic Changes)
```
✨ Colors and styling
✨ Spacing and layout
✨ Font sizes and weights
✨ Icons and visual indicators
✨ Hover/active state animations
✨ Button appearance and sizing
```

### 🔒 UNCHANGED (Core Logic Preserved)
```
✓ Hunt orchestration logic
✓ Database and service layer
✓ Keyboard shortcuts and hotkeys
✓ File structure (still app_gui.py, ui/tabs/)
✓ All functionality works exactly the same
✓ No breaking changes to existing code
```

---

## 💡 Design Philosophy

The new design follows these principles:

### 1. **Dark Theme First**
   - Base: #0f0f0f (true black)
   - Surfaces: #1a1a1a (elevated gray)
   - Better on eyes, matches game aesthetic

### 2. **Accent Color Consistency**
   - Green (#4ade80) for ALL primary actions
   - Every active state uses same green
   - Creates visual cohesion

### 3. **Clear Hierarchy**
   - Large panels (hunt, target, stats) are primary
   - Supporting elements are secondary
   - No competing for attention

### 4. **State Visibility**
   - Every interactive element shows clear state (default/hover/active/disabled)
   - Smooth transitions (200ms) between states
   - No surprises

### 5. **Responsive Design**
   - Works at 1024×600 minimum
   - Full screen at 1920×1080
   - DPI aware (100%-200% scaling)
   - No overlapping or broken layouts

---

## 📋 Key Decisions & Rationale

| Decision | Why | Benefit |
|----------|-----|---------|
| Sidebar logo + branding | Creates identity and polish | Professional appearance |
| SVG icons (not text) | Clearer visual meaning | Better UX, accessible |
| Semantic color tokens | Single source of truth | Easy to theme later |
| Card-based layout | Clear grouping | Better information hierarchy |
| Accent-green everywhere | Unified design language | Cohesive feel |
| Sticky table headers | Better scrolling UX | No confusion about columns |
| Inline bar charts | Space-efficient stats | More info in less space |
| Status badges with states | Clear state indication | No guessing what's happening |

---

## ✨ Highlights of New Design

### Sidebar
- ✨ Logo + "CABAL ASSISTANT" branding
- ✨ Icons next to each menu item
- ✨ Active state with green left border
- ✨ Group labels for organization

### Header
- ✨ Window selector with refresh button
- ✨ 3 status chips (Server, Character, Time)
- ✨ Start button disabled until ready
- ✨ Compact language selector

### Hunt Panel
- ✨ Unified tab styling
- ✨ Empty state with guidance
- ✨ Icon-only action buttons (move, toggle, delete, add)
- ✨ Tooltips on all buttons

### Target Panel
- ✨ Status badge with pulse animation when hunting
- ✨ Gradient HP bar
- ✨ 3-column stats grid
- ✨ Professional "Apply Settings" button

### Combo Chain
- ✨ Custom styled checkbox with pop animation
- ✨ 4-card layout for combo chains
- ✨ 2-card layout for buff lanes
- ✨ Icon indicators (⏱ cast, 🔄 cooldown)

### Skill Stats
- ✨ Sticky headers
- ✨ Striped row styling
- ✨ Inline bar charts for success %
- ✨ Custom scrollbar

### Status Bar
- ✨ Animated spinner
- ✨ Version info
- ✨ DB connection status
- ✨ Error counter

---

## 🔧 Technology Stack

```
Tkinter (existing)
  - Custom styling using `tk.Frame`, `tk.Button`, etc.
  - Color tokens via constants
  - Font management via `tkinter.font`

CSS-like organization (via ui_style_v2.py):
  - Color tokens (semantic naming)
  - Font definitions
  - Spacing constants
  - State styling (hover, active, disabled)

Custom components:
  - Reusable button styles
  - Panel wrapper with borders
  - Tab bar styling
  - Badge components
  - Icon buttons
```

---

## 📈 Success Metrics

After completing Phase 2, we measure:

### Visual Quality
- [ ] Screenshots look professional and modern
- [ ] No component is "gớm" (ugly)
- [ ] Consistent spacing and alignment
- [ ] Smooth state transitions
- [ ] Readable at all screen sizes

### Code Quality
- [ ] All colors from `ui_style_v2.py` (no hardcoded hex)
- [ ] Consistent component patterns
- [ ] Well-documented design tokens
- [ ] Clean separation of concerns

### User Experience
- [ ] Clear active state indicators
- [ ] Obvious disabled states
- [ ] Helpful tooltips on hover
- [ ] Intuitive layout and grouping

### Testing
- [ ] Screenshots at 3+ resolutions
- [ ] DPI scaling validated
- [ ] Visual regression tests passed
- [ ] All functionality preserved

---

## 🎬 Getting Started

### Option 1: Guided Implementation (Recommended)
1. Read `PROMPT-UI-REDESIGN-PHASE-2.md` carefully (1 hour)
2. Create `lib/ui_style_v2.py` with all tokens
3. Test the token system with a demo
4. Implement Phase 2.2 (Sidebar) as a proof-of-concept
5. If satisfied, continue with remaining phases

### Option 2: Full Build
1. Review all documents
2. Create feature branch
3. Implement all 9 phases sequentially
4. Test after each phase
5. Merge when complete

### Option 3: Prioritized Build
1. Implement only highest-value phases:
   - Phase 2.1: Design System (enables everything)
   - Phase 2.3: Header (most visible)
   - Phase 2.5: Target Panel (most important)
   - Phase 2.6: Combo Chain (most used)
2. Then continue with remaining phases

---

## 📞 Integration with Larger Project

This redesign (Phase 2) is part of a larger Workspace Redesign:

```
Sprint 26: Hunt Workspace Redesign
├─ Phase 1: Database Layer ✅ COMPLETE
│  └─ SkillPresetService, repositories, schema
│
├─ Phase 2: Visual Redesign (THIS DOCUMENT) ← YOU ARE HERE
│  └─ Modern dark theme, new components, improved UX
│
├─ Phase 3: Panel Extraction
│  └─ Extract logic into panel classes
│
└─ Phase 4: Layout Refactoring
   └─ Implement 4-panel 60/40 split layout
```

Each phase builds on previous ones. Phase 2 prepares the UI for Phase 3.

---

## ⚠️ Important Notes

### Before Starting
- [ ] Ensure feature branch created: `feature/ui-redesign-phase2`
- [ ] Backup current `app_gui.py` (git handles this)
- [ ] Have screenshots taken at current state for comparison
- [ ] Ensure all previous fixes (sidebar, tabs) are committed

### During Implementation
- [ ] Test after each phase
- [ ] Commit frequently with descriptive messages
- [ ] Take screenshots at 1366×768 for evidence
- [ ] Don't skip phases (sequential dependencies)

### After Completion
- [ ] Create PR with before/after screenshots
- [ ] Code review by team lead
- [ ] Merge to main when approved
- [ ] Plan Phase 3 (Panel Extraction)

---

## 🎨 Design Tool Reference

The Figma design shows:
- High-fidelity mockups of all components
- Color swatches and token system
- Interactive states (hover, active, disabled)
- Responsive layouts at different sizes
- Animation previews

**Note**: This Tkinter implementation follows the design but adapts it to Tkinter constraints (e.g., custom scrollbars instead of CSS).

---

## 📞 Questions?

Refer to these documents in order:

1. **"Why this design?"** → See Design Philosophy section above
2. **"How do I implement it?"** → Read `PROMPT-UI-REDESIGN-PHASE-2.md`
3. **"What does it look like?"** → See `PROMPT-UV-ui-visual-reference.md`
4. **"What are the colors?"** → See Color Tokens Cheat Sheet

---

## ✅ Checklist to Begin

- [ ] Read this master plan (you're reading it now!)
- [ ] Open `PROMPT-UI-REDESIGN-PHASE-2.md` in editor
- [ ] Review `PROMPT-UV-ui-visual-reference.md` for visuals
- [ ] Create feature branch: `git checkout -b feature/ui-redesign-phase2`
- [ ] Start Phase 2.1: Create `lib/ui_style_v2.py`
- [ ] Take baseline screenshots
- [ ] Commit first change

---

## 🚀 Let's Build Something Beautiful!

The current UI feels outdated. This redesign will transform it into something modern, professional, and polished. Every component follows a unified design language. The implementation is straightforward: systematically apply the token system to each component.

**Expected outcome**: A UI that users are proud to use. No more "gớm" feeling!

---

**Status**: Ready for development  
**Est. Completion**: 2-3 weeks  
**Next Step**: Begin Phase 2.1 (Design System)

**Good luck! 🎯**
