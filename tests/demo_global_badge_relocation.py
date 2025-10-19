"""
Demo/Test Script: Global Unsaved Badge Relocation
==================================================

Test badge "Chưa lưu" đã được di chuyển lên top bar cạnh nút Save.

✅ Fixed: Badge giờ hiển thị trạng thái global của cả 3 tab
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║   TEST: Global Unsaved Badge in Top Bar                       ║
╔════════════════════════════════════════════════════════════════╗

📋 Test Checklist:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 1: Badge Position - In Top Bar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. python app_gui.py
2. Click "Quản Lý Thư Viện"
3. Observe top bar layout

Expected Layout:
┌──────────────────────────────────────────────────────────────┐
│ [Library Manager]                    [CHƯA LƯU] [💾] [✖]    │ ← Top bar
├──────────────────────────────────────────────────────────────┤
│ [Quái Vật] [Kỹ Năng] [Timing]                               │
│                                                              │
│  ... Tab content ...                                         │
└──────────────────────────────────────────────────────────────┘

Verification:
[ ] Badge is in TOP BAR (not in tab area)
[ ] Badge is RIGHT OF Save button 💾
[ ] Badge is initially HIDDEN (no changes yet)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 2: Global Badge - Monster Tab Changes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. Tab "Quái Vật"
2. Add new monster (click + button)
3. Enter name: "Test Monster"
4. Click "Lưu quái" in dialog
5. Check top bar

Expected Result:
✅ Global badge "CHƯA LƯU" appears in TOP BAR
✅ Badge has orange background (#FFA726 or similar)
✅ Badge text: "CHƯA LƯU" (VI) or "UNSAVED" (EN)
✅ Badge positioned right of 💾 button

Verification:
[ ] Badge visible in top bar
[ ] Badge orange background
[ ] Badge near Save button
[ ] Badge shows "CHƯA LƯU"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 3: Badge Visible Across All Tabs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. With monster changes (from Test 2)
2. Switch to Tab "Kỹ Năng"
3. Check top bar
4. Switch to Tab "Timing"
5. Check top bar
6. Switch back to Tab "Quái Vật"

Expected Result:
✅ Badge "CHƯA LƯU" STAYS VISIBLE when switching tabs
✅ Badge position FIXED in top bar
✅ Badge doesn't move or flicker

Verification:
[ ] Badge visible in "Kỹ Năng" tab
[ ] Badge visible in "Timing" tab
[ ] Badge visible in "Quái Vật" tab
[ ] Badge position stable (no movement)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 4: Multiple Tabs - Combined Changes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. Tab "Quái Vật" → Edit a monster
2. Check badge → Should show "CHƯA LƯU"
3. Tab "Kỹ Năng" → Edit a skill
4. Check badge → Should STILL show "CHƯA LƯU"
5. Tab "Timing" → Apply timing calculation
6. Check badge → Should STILL show "CHƯA LƯU"

Expected Result:
✅ Badge appears after FIRST change (any tab)
✅ Badge STAYS visible as more changes added
✅ Badge reflects COMBINED state of all 3 tabs

Verification:
[ ] Badge appears after monster edit
[ ] Badge stays after skill edit
[ ] Badge stays after timing apply
[ ] Badge visible in all tabs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 5: Save All - Badge Disappears
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. With changes from Test 4 (all 3 tabs changed)
2. Click 💾 Save button in TOP BAR
3. Wait for success message
4. Check top bar

Expected Result:
✅ Success message: "Changes applied"
✅ Badge "CHƯA LƯU" DISAPPEARS from top bar
✅ All changes saved to files:
   - lib/data/monsters.json
   - lib/data/skills.json
   - lib/data/hunt_config.json

Verification:
[ ] Success message shown
[ ] Badge disappeared
[ ] Files updated (check timestamps)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 6: Template Badge - Independent from Global
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. Tab "Quái Vật" → Select monster "Coc go~"
2. Select template "Coc go 1"
3. Click ✏️ Edit button (in template form)
4. Edit template name
5. Observe TWO badges

Expected Result:
✅ GLOBAL badge in top bar: "CHƯA LƯU" (orange)
✅ TEMPLATE badge in form: "Đang chỉnh sửa" (orange)
✅ Two badges visible SIMULTANEOUSLY
✅ No conflict between badges

Badge Positions:
┌──────────────────────────────────────────────────────────────┐
│ [Title]                              [CHƯA LƯU] [💾] [✖]    │ ← Global
├──────────────────────────────────────────────────────────────┤
│ [Template: Coc go 1]        [Đang chỉnh sửa] [💾]          │ ← Template
│  Template fields...                                          │
└──────────────────────────────────────────────────────────────┘

Verification:
[ ] Global badge in top bar (orange)
[ ] Template badge in form (orange)
[ ] Both badges visible together
[ ] Different positions (no overlap)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 7: Template Save - Global Badge Remains
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. Continue from Test 6 (template editing)
2. Click 💾 Save button in TEMPLATE FORM (not top bar)
3. Observe badge changes
4. Wait 3+ seconds

Expected Result:
✅ TEMPLATE badge changes: "Đang chỉnh sửa" → "Đã lưu" (green, 3s)
✅ GLOBAL badge STAYS: "CHƯA LƯU" (orange, unchanged)
✅ After 3s: Template badge disappears
✅ Global badge STILL visible (main form not saved yet)

Explanation:
- Template save → Only saves template to memory
- Main form → Still has unsaved changes
- Need to click TOP BAR 💾 to save everything

Verification:
[ ] Template badge turns green "Đã lưu"
[ ] Global badge stays orange "CHƯA LƯU"
[ ] After 3s: Template badge hidden
[ ] Global badge still visible

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 8: Final Save - All Badges Disappear
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Steps:
1. Continue from Test 7 (template saved, global unsaved)
2. Click 💾 Save button in TOP BAR
3. Confirm success message
4. Check both badge positions

Expected Result:
✅ Success message shown
✅ GLOBAL badge disappears from top bar
✅ TEMPLATE badge already hidden (from Test 7)
✅ Window closes or stays open (based on settings)

Verification:
[ ] Success message
[ ] Global badge gone
[ ] Template badge gone
[ ] All changes saved to disk

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 9: Badge Colors & Styles
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Visual Inspection:

Global Badge (Top Bar):
[ ] Background: Orange (#FFA726 or UI.COLOR_WARNING)
[ ] Text: White (#FFFFFF)
[ ] Font: Bold, size 9
[ ] Padding: 8px horizontal, 4px vertical
[ ] Text: "CHƯA LƯU" (VI) or "UNSAVED" (EN)

Template Badge (Form):
[ ] Background: Orange (#FF9800) when editing
[ ] Background: Green (#4CAF50) when saved
[ ] Text: White (#FFFFFF)
[ ] Font: Bold, size 9
[ ] Text: "Đang chỉnh sửa" / "Đã lưu"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST 10: Edge Cases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case 1: Open window → No changes
Expected: NO badge visible

Case 2: Load existing data → No changes
Expected: NO badge visible

Case 3: Change → Undo → No net change
Expected: Badge STILL visible (system tracks "changed" flag)

Case 4: Rapid tab switching with badge
Expected: Badge position STABLE, no flicker

Case 5: Window resize
Expected: Badge stays near Save button (relative position)

Verification:
[ ] All edge cases handled correctly
[ ] No visual glitches
[ ] Badge behavior predictable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Summary: Badge System Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Two Independent Badge Systems:

1. GLOBAL BADGE (Top Bar)
   - Purpose: Show unsaved changes from ALL tabs
   - Location: Top bar, right of 💾 Save button
   - Tracks: Monster changes + Skill changes + Timing changes
   - Color: Orange (#FFA726)
   - Text: "CHƯA LƯU" / "UNSAVED"
   - Control: _mark_unsaved(True/False)

2. TEMPLATE BADGE (Monster Tab)
   - Purpose: Show template editing state
   - Location: Template form title, right side
   - States: "Đang chỉnh sửa" (orange) → "Đã lưu" (green, 3s)
   - Control: _show_editing_badge(), _show_saved_badge()

Key Differences:
┌───────────────┬──────────────────┬─────────────────────┐
│               │ Global Badge     │ Template Badge      │
├───────────────┼──────────────────┼─────────────────────┤
│ Location      │ Top bar          │ Template form       │
│ Scope         │ All 3 tabs       │ Current template    │
│ Trigger       │ Any data change  │ Template edit       │
│ Visibility    │ All tabs         │ Monster tab only    │
│ Save button   │ Top bar 💾       │ Template form 💾    │
│ Persistence   │ Until main save  │ Until template save │
└───────────────┴──────────────────┴─────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Test Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If all tests pass:
✅ Global badge correctly positioned in top bar
✅ Badge visible across all tabs
✅ Badge tracks combined state of all 3 tabs
✅ Badge disappears after save
✅ Template badge independent and functional
✅ No conflicts between badges

If any test fails:
❌ Review docs/sprints/sprint19/UX_GLOBAL_BADGE_RELOCATION.md
❌ Check lib/ui/library_manager.py implementation
❌ Verify badge widget references (unsaved_badge vs template_badge)

╚════════════════════════════════════════════════════════════════╝
""")
