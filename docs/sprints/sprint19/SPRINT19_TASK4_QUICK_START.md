# Quick Start: Auto Timing Calculator

**Sprint 19 - Task #4**  
**For**: End Users  
**Time**: 2 minutes to read, 30 seconds to use

---

## 🎯 What Is This?

The **Auto Timing Calculator** eliminates guesswork when setting up hunt timing.

**Before**: ❓ "Lost timeout là gì? Đặt bao nhiêu giây?"  
**After**: ✅ Click, click, done! Optimal settings automatically calculated.

---

## 🚀 How to Use (3 Simple Steps)

### Step 1: Open Library Manager
```
1. Run: python app_gui.py
2. Click: "Library Manager" button (or "Quản Lý Thư Viện")
3. Click: "Timing Calculator" tab (third tab)
```

### Step 2: Select & Input
```
🔵 Step 1: Select Monster
   → Choose: "Coc go~" (or your target monster)
   → See: HP, damage info appears

🟢 Step 2: Select Skill
   → Choose: "Dark Explosion" (or your main attack skill)
   → See: Cooldown, cast time appears

🟠 Step 3: Attack Speed
   → Choose: "Normal (2 APS)" (or your actual speed)
   → Or: Enter custom value
```

### Step 3: Calculate & Apply
```
4. Click: "🔢 Calculate Optimal Timing" (blue button)
   → See: Results appear (hits to kill, recommended settings)

5. Click: "✅ Apply to Hunt Config" (green button)
   → Done! Settings saved automatically
```

---

## 📊 Example Output

After clicking Calculate, you'll see:

```
==================================================
📊 Analysis
==================================================

• Hits to kill: 58 đòn
• Time per hit: 0.50s
• Total kill time: 29.00s

==================================================
⚙️ Recommended Settings
==================================================

• Lost timeout: 0.75s
  (Time between hits + 50% safety margin)

• Attack duration: 30.00s
  (Kill time + 20% safety margin)

==================================================
🎯 Confidence: HIGH
==================================================
```

---

## 🎓 Understanding Results

### Hits to Kill
- How many attacks needed to kill the monster
- Formula: `ceil(Monster HP / Your Damage)`
- Example: `ceil(10,000 / 175) = 58 hits`

### Time per Hit
- How long each attack takes
- Formula: `1.0 / Attacks per second`
- Example: `1.0 / 2.0 = 0.50s`

### Kill Time
- Total time to kill the monster
- Formula: `Hits × Time per hit`
- Example: `58 × 0.50 = 29s`

### Lost Timeout
- **What**: Time to wait between attacks before declaring monster "lost"
- **Why**: If set too low, bot thinks monster is gone too quickly
- **Formula**: `Time per hit × 1.5` (50% safety margin)
- **Example**: `0.50 × 1.5 = 0.75s`

### Attack Duration
- **What**: Minimum time to keep attacking before giving up
- **Why**: If set too low, bot stops before monster dies
- **Formula**: `Kill time × 1.2` (20% safety margin)
- **Example**: `29 × 1.2 = 34.8s` (capped at 30s max)

---

## ⚙️ Attack Speed Presets

Choose the preset that matches your playstyle:

| Preset | APS | Best For |
|--------|-----|----------|
| **Slow** | 1.0 | Heavy weapons, slow skills (e.g., Blade Force) |
| **Normal** | 2.0 | Default attack speed (most common) ⭐ |
| **Fast** | 3.0 | Light weapons, fast skills (e.g., Lightning) |
| **Very Fast** | 4.0 | Rapid fire skills (e.g., Magic Arrow spam) |
| **Custom** | Your value | If you know exact APS |

💡 **Tip**: If unsure, use **Normal (2.0 APS)** - works for most cases.

---

## ✅ Manual Testing Checklist

After using the calculator, verify:

- [ ] Monster dropdown shows all monsters
- [ ] Selecting monster displays correct HP/damage
- [ ] Skill dropdown shows attack skills only (not buffs)
- [ ] Selecting skill displays correct cooldown/cast time
- [ ] Attack speed presets update the APS field
- [ ] Calculate button shows formatted results
- [ ] Results make sense (hits to kill is reasonable)
- [ ] Apply button becomes enabled after calculation
- [ ] Clicking Apply shows success message
- [ ] Hunt config file updated correctly
- [ ] Language (EN/VI) displays correctly throughout
- [ ] No errors or crashes

---

## 🐛 Troubleshooting

### Problem: "Please select a monster first"
**Solution**: Select a monster from the dropdown in Step 1.

### Problem: "Monster missing HP or damage data"
**Solution**: 
1. Go to Monster Library tab
2. Edit the monster
3. Add HP and "Damage per hit" values
4. Save, then try calculator again

### Problem: Results seem wrong (too high/low)
**Solution**: Check your inputs:
- Is monster HP correct?
- Is your damage per hit correct?
- Is attack speed realistic? (usually 1-4 APS)

### Problem: Apply button stays disabled
**Solution**: Click "Calculate" button first.

---

## 📞 Need Help?

### Documentation:
- **Full Spec**: `docs/sprints/sprint19/SPRINT19_TASK4_AUTO_TIMING_CALCULATOR.md`
- **Summary**: `docs/sprints/sprint19/SPRINT19_TASK4_SUMMARY.md`
- **This Guide**: `docs/sprints/sprint19/SPRINT19_TASK4_QUICK_START.md`

### Testing:
- **Test Script**: `python tests/test_timing_calculator_ui.py`
- **Expected**: All automated tests should pass

### Support:
- Check documentation first
- Review manual testing checklist
- Report issues with screenshots

---

## 💡 Pro Tips

### Tip 1: Update Damage Regularly
Your damage changes with:
- Equipment upgrades
- Skill levels
- Buffs/debuffs

→ Re-calculate when damage changes significantly

### Tip 2: Different Monsters = Different Settings
Don't use same settings for all monsters:
- Low HP monsters need shorter attack duration
- High HP bosses need longer timeout

→ Calculate for each monster type

### Tip 3: Test Before Long Hunt Sessions
After applying new settings:
1. Test with manual hunt (1-2 monsters)
2. Verify bot kills correctly
3. Adjust if needed
4. Then start long session

### Tip 4: Save Common Presets (Future Feature)
Currently, you need to re-calculate each time.
Future update will add preset save/load.

---

## 🎯 Success Criteria

You know it's working when:
- ✅ Bot attacks exactly until monster dies
- ✅ Bot searches for new monster immediately after
- ✅ No "lost timeout" errors in logs
- ✅ No endless attacking after monster death
- ✅ Smooth, efficient hunting

---

## 📈 Before vs After

### Before (Manual Setup):
```
❓ Set lost_timeout = ??? (guessing 0.5s)
❓ Set attack_duration = ??? (guessing 10s)
→ Start hunt
→ Bot loses monster too quickly ❌
→ Or attacks too long after death ❌
→ Adjust, test, adjust, test... 😰
→ Finally works after 30 minutes ⏰
```

### After (Auto Calculator):
```
✅ Select monster: "Coc go~"
✅ Select skill: "Dark Explosion"
✅ Click Calculate
✅ Click Apply
→ Start hunt
→ Perfect timing immediately! 🎉
→ Total time: 30 seconds ⚡
```

---

**Happy Hunting!** 🎮

*Questions? Check the full documentation or run the test script.*
