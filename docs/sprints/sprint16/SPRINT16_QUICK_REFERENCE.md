# 🎯 Quick Reference - Sprint 16 GUI Redesign

## 📌 TL;DR

**What's changing**: GUI sẽ được redesign để thân thiện hơn với người mới.

**Why**: User feedback cho thấy giao diện hiện tại quá phức tạp, timing calculator không chính xác, thiếu hướng dẫn.

**When**: Sprint 16 planning complete, implementation start soon.

---

## 🔍 Main Problems → Solutions

### 1. Timing Calculator Inaccurate
```
❌ Problem:
User phải GUESS attack speed (slow/normal/fast)
→ Timing recommendations không chính xác

✅ Solution:
Calculator tự động tính attack speed TỪ skills thực tế
→ Accurate recommendations!
```

### 2. Too Many Settings
```
❌ Problem:
Hunt tab có 10+ parameters
User mới không biết điền gì

✅ Solution:
Beginner Mode: Chỉ 4 bước (game window, monster, skills, start)
Advanced Mode: Show all parameters (for power users)
```

### 3. No First-Time Guidance
```
❌ Problem:
User mở app → Không biết bắt đầu từ đâu

✅ Solution:
Setup Wizard: 5 steps hướng dẫn chi tiết
Skip option nếu đã biết
```

### 4. Only 1 Monster
```
❌ Problem:
Level 60+ phải hunt nhiều quái
Hiện tại chỉ support 1 quái

✅ Solution:
Multi-Monster Mode:
- Rotation: Hunt theo vòng
- Priority: Hunt boss trước
```

### 5. Messy Forms
```
❌ Problem:
All tabs cùng level, khó navigate

✅ Solution:
New tabs:
- Hunt (main action)
- Setup (all config)
- Stats (analytics)
- Help (guides)
```

---

## 🎨 Visual Comparison

### Before (Current)
```
┌────────────────────────────────────┐
│ Hunt Tab                           │
├────────────────────────────────────┤
│ Window Title: [________]           │
│ Target Key: [TAB]                  │
│ Attack Keys: [1,2,3]               │
│ Attack Press MS: [100]             │
│ Target Cycle Delay: [0.5]          │
│ Search Interval: [1.0]             │
│ Attack Interval: [0.5]             │
│ Lost Timeout: [2.0]                │
│ Attack Duration: [10.0]            │
│ Template Path: [Browse...]         │
│ Region: [100, 100, 800, 600]       │
│ Confidence: [0.8]                  │
│ Grayscale: [☑]                     │
│ [Start Hunt] [Stop]                │
└────────────────────────────────────┘

User: "Ơ... nhiều quá, điền sao đây? 😵"
```

### After (Sprint 16 - Beginner Mode)
```
┌────────────────────────────────────┐
│ Hunt Tab                           │
├────────────────────────────────────┤
│ Mode: ●Beginner ○Advanced          │
│                                    │
│ 1️⃣ Game Window:                   │
│    [Cabal - PID 12345 ▼] [Bring]  │
│                                    │
│ 2️⃣ Monster:                        │
│    [Goblin (5k HP) ▼]             │
│                                    │
│ 3️⃣ Skills:                         │
│    ☑ Dark Explosion (Key: 1)      │
│    ☑ Fire Ball (Key: 2)           │
│                                    │
│ 4️⃣ Ready:                          │
│    [▶ Start Hunt] [⏸ Stop]        │
│                                    │
│ Status: Ready to hunt ✅           │
└────────────────────────────────────┘

User: "Dễ quá! Chỉ 4 bước! 😊"
```

---

## 🚀 New Features

### Feature 1: Smart Timing Calculator
```
Old Way:
1. Monster HP: 10000
2. Damage: 500
3. Attack speed: ○Slow ●Normal ○Fast ○Very Fast
   (User không biết chọn gì, guess "Normal")
4. Calculate
→ Kết quả có thể KHÔNG CHÍNH XÁC vì guess sai

New Way:
1. Monster HP: 10000
2. Damage: 500
3. Attack speed: ●From Skills (auto-detect)
   Skills: Dark Explosion (1.5s CD), Fire Ball (2.0s CD)
   → Auto calculated: 0.57 hits/sec
4. Calculate
→ Kết quả CHÍNH XÁC vì dựa trên skills thật!
```

### Feature 2: Setup Wizard
```
First time opening app:

┌─────────────────────────────────┐
│ Welcome to Cabal Auto Hunt! 🎉  │
├─────────────────────────────────┤
│ Let's set up your first hunt    │
│ in 5 easy steps.                │
│                                 │
│ [Get Started →]                 │
│ [Skip (I know what to do)]      │
└─────────────────────────────────┘

→ Follow 5 steps
→ Everything configured
→ Ready to hunt!
```

### Feature 3: Multi-Monster Hunting
```
Current:
- Select Monster: [Goblin ▼]
→ Only hunt Goblin

New:
- Hunt Mode: [○Single ●Rotation ○Priority]
- Monster List:
  1. Goblin
  2. Orc
  3. Dragon
→ Hunt all 3 in rotation!
```

### Feature 4: Progressive Modes
```
Beginner Mode:
- 4 simple steps
- No technical terms
- Auto-calculated defaults

Intermediate Mode:
- + Show timing parameters
- + Tooltips explain everything
- Can adjust if needed

Advanced Mode:
- + Manual overrides
- + Custom regions
- + Template paths
- Full control!
```

---

## 📅 Timeline

```
Week 1: Core UX improvements
  - Mode toggle
  - Beginner layout
  - Skill-based calculator

Week 2: Setup Wizard
  - 5-step wizard
  - Validation
  - Skip option

Week 3: Multi-Monster
  - Rotation mode
  - Priority mode
  - Switching logic

Week 4: Tab Reorg
  - Hunt/Setup/Stats/Help
  - Subtabs
  - Navigation

Week 5: Polish
  - Tooltips
  - Error messages
  - Testing
  - Docs
```

---

## ❓ FAQ

### Q: Sẽ mất config cũ không?
**A**: KHÔNG! Config cũ vẫn hoạt động. Sẽ có migration tool và advanced mode.

### Q: Phải setup lại từ đầu?
**A**: KHÔNG! Nếu đã có config, vẫn dùng được. Wizard chỉ cho người mới.

### Q: Advanced features có bị xóa không?
**A**: KHÔNG! Tất cả features giữ nguyên. Chỉ organized tốt hơn.

### Q: Khi nào release?
**A**: Đang planning. Dự kiến ~5 weeks implementation.

### Q: Có thể contribute ideas?
**A**: CÓ! Feedback luôn được welcome. File issue trên GitHub.

---

## 💡 Your Feedback Helped!

Sprint 16 được thiết kế dựa trên feedback thực tế:

✅ "Timing calculator không chính xác"
→ Fixed: Skill-based calculation

✅ "Không hiểu RadioButton Normal"
→ Fixed: Auto-detect from skills

✅ "Quá nhiều settings, bị ngộp"
→ Fixed: Beginner mode (4 steps only)

✅ "Cần hướng dẫn cho người mới"
→ Fixed: Setup wizard

✅ "Không support multi-monster"
→ Fixed: Rotation & priority modes

✅ "Forms lộn xộn"
→ Fixed: Tab reorganization

**Thank you for feedback! 🙏**

---

## 📚 More Info

- Full proposal: `docs/REDESIGN_PROPOSAL_SPRINT16.md`
- Planning summary: `docs/sprints/SPRINT16_PLANNING_SUMMARY.md`
- Current context: `docs/archive/v2/context/CONTEXT_MAIN.txt`

---

**Status**: Planning Complete ✅  
**Next**: Implementation Starting Soon 🚀  
**Questions**: Create GitHub issue or ask in discussions
