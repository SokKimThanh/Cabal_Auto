# 🎨 Sprint 16: GUI Redesign Proposal - User-Friendly Auto Hunt

## 📋 Tổng quan vấn đề hiện tại

### ❌ Vấn đề người dùng gặp phải

#### 1. **Timing Calculator không liên kết với Skills**
```
Vấn đề:
- User nhập HP quái = 10,000
- User nhập Damage per hit = 500
- Chọn "Normal" attack speed (2.0 hits/sec)
- Calculator cho: lost_timeout=0.75s, attack_duration=12.0s

❌ NHƯNG: Calculator KHÔNG biết user đang dùng skill nào!
❌ Skills có cooldown khác nhau → attack speed thực tế khác calculator
❌ User phải manual guess attack speed → không chính xác
```

**Ví dụ thực tế**:
```
User có 3 attack skills:
- Skill 1: cooldown 1.0s, cast_time 0.5s
- Skill 2: cooldown 2.0s, cast_time 0.8s  
- Skill 3: cooldown 3.0s, cast_time 1.0s

Average attack speed = ???
→ Calculator không thể tính vì không biết skills!
→ Recommendations không chính xác!
```

#### 2. **Hunt Config quá phức tạp**
```
Người mới vào thấy:
❌ Target Key: TAB (là gì?)
❌ Attack Keys: 1,2,3 (tại sao phẩy?)
❌ Target Cycle Delay: 0.5 (nghĩa là gì?)
❌ Attack Interval: 0.5 (khác gì cycle delay?)
❌ Lost Timeout: 2.0 (mất gì?)
❌ Attack Duration: 10.0 (đánh bao lâu?)
❌ Search Interval: 1.0 (tìm kiếm gì?)
❌ Template Path: assets/... (đường dẫn?)
❌ Region: [100, 100, 800, 600] (4 số này?)
❌ LT, RB corners (là cái gì?)

→ OVERWHELMED! Không biết bắt đầu từ đâu!
```

#### 3. **RadioButton "Normal" không rõ nghĩa**
```
User thấy:
○ Slow (1 hit/sec)
● Normal (2 hit/sec)  ← Chọn cái này nghĩa là gì?
○ Fast (3 hit/sec)
○ Very Fast (4 hit/sec)

Câu hỏi:
- "Normal" theo vũ khí nào? Sword? Staff? Orb?
- Skills của tôi cooldown khác nhau, chọn sao?
- 2 hits/sec có đúng với build của tôi không?
→ User chỉ guess, không chắc chắn!
```

#### 4. **Không support multi-monster combo**
```
Level thấp (1-60): Đánh 1 loại quái → OK ✅

Level cao (60+): Đánh nhiều quái cùng lúc
- Goblin (HP: 5k, weak)
- Orc (HP: 10k, medium)  
- Dragon (HP: 50k, boss)

❌ Hiện tại: Chỉ chọn được 1 monster → không flexible
❌ Phải stop hunt, switch monster, restart → mất thời gian
❌ Không có skill rotation logic cho mixed targets
```

#### 5. **Thiếu hướng dẫn workflow**
```
Người mới:
1. Mở GUI → Thấy nhiều tabs, forms, buttons
2. Không biết bắt đầu từ đâu
3. Click random → Lỗi "Please configure..."
4. Frustrated → Bỏ cuộc

Cần:
✅ Wizard/Setup guide cho lần đầu
✅ Tooltips giải thích từng bước
✅ Validation messages thân thiện
✅ Default values hợp lý
```

---

## ✅ Giải pháp đề xuất

### 🎯 Sprint 16 Goals

#### **Phase 1: Skill-Based Timing Calculator** (Priority: HIGH)

**Vấn đề cần giải quyết**: Timing calculator phải dựa vào skills thực tế, không phải guess attack speed.

**Solution**:
```python
# NEW: Calculate attack speed FROM selected skills
def calculate_attack_speed_from_skills(skill_slots):
    """
    Calculate actual attack speed based on user's skill configuration.
    
    Args:
        skill_slots: List of skill names user will use for hunting
        
    Returns:
        float: Effective attacks per second
        
    Example:
        skills = ["Dark Explosion", "Fire Ball", "Lightning Strike"]
        → Load from skills.json
        → Average cooldown = 1.5s
        → Effective APS = 1 / 1.5 = 0.67 hits/sec
    """
    total_cooldown = 0
    count = 0
    
    for skill_name in skill_slots:
        skill = get_skill_by_name(skill_name)  # Load from skills.json
        total_cooldown += skill['cooldown']
        count += 1
    
    avg_cooldown = total_cooldown / count if count > 0 else 1.0
    attacks_per_second = 1.0 / avg_cooldown
    
    return attacks_per_second
```

**GUI Changes**:
```
Monster Manager → Timing Calculator Dialog:

┌─────────────────────────────────────────┐
│ Timing Calculator                       │
├─────────────────────────────────────────┤
│ Monster Stats:                          │
│   HP: [10000]                           │
│   Damage per hit: [500]                 │
│                                         │
│ Attack Speed Source:                    │
│   ● From Skills (Recommended)           │
│     Selected Skills: 3 skills           │
│     Avg Cooldown: 1.5s                  │
│     → APS: 0.67 hits/sec                │
│                                         │
│   ○ Manual (Advanced)                   │
│     [ ] Slow  [ ] Normal  [ ] Fast      │
│     Custom: [____] hits/sec             │
│                                         │
│ [Calculate] [Apply to Hunt] [Close]     │
└─────────────────────────────────────────┘
```

**Benefits**:
- ✅ Accurate timing dựa trên skills thực tế
- ✅ Không cần guess attack speed
- ✅ Auto-calculate từ Skills Manager
- ✅ Manual override cho advanced users

---

#### **Phase 2: Simplified Hunt Tab** (Priority: HIGH)

**Vấn đề cần giải quyết**: Hunt Config quá nhiều parameters phức tạp.

**Solution**: Chia làm 3 levels - Beginner, Intermediate, Advanced

**NEW Hunt Tab Layout**:

```
┌────────────────────────────────────────────────────────┐
│ 🎯 Hunt Configuration                                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Mode: [●Beginner ○Intermediate ○Advanced]             │
│                                                        │
│ ┌─ BEGINNER MODE ─────────────────────────────────┐   │
│ │                                                  │   │
│ │ 1️⃣ Select Game Window:                          │   │
│ │    [Game Window Dropdown ▼] [Bring to Front]    │   │
│ │                                                  │   │
│ │ 2️⃣ Select Monster to Hunt:                      │   │
│ │    [Monster Dropdown ▼]                          │   │
│ │    ℹ️ Monster config auto-applied               │   │
│ │                                                  │   │
│ │ 3️⃣ Select Skills to Use:                        │   │
│ │    ☑ Dark Explosion (1)                         │   │
│ │    ☑ Fire Ball (2)                              │   │
│ │    ☑ Lightning Strike (3)                       │   │
│ │    ℹ️ Skills will rotate automatically          │   │
│ │                                                  │   │
│ │ 4️⃣ Ready to Hunt:                               │   │
│ │    [▶ Start Hunt] [⏸ Stop (F9)]                │   │
│ │                                                  │   │
│ │ Status: Ready                                    │   │
│ │                                                  │   │
│ └──────────────────────────────────────────────────┘   │
│                                                        │
│ [⚙️ Advanced Settings...] [📚 Help & Guides]          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**INTERMEDIATE MODE** (click "Advanced Settings"):
```
┌─ INTERMEDIATE SETTINGS ──────────────────────────┐
│                                                  │
│ Target Settings:                                 │
│   Target Key: [TAB ▼] (Switch target)           │
│   Target Cycle Delay: [0.5] sec                  │
│   ℹ️ Time between TAB presses when searching    │
│                                                  │
│ Attack Settings:                                 │
│   Attack Interval: [0.5] sec                     │
│   ℹ️ Delay between skill casts                  │
│                                                  │
│ Detection Settings:                              │
│   Lost Timeout: [2.0] sec                        │
│   ℹ️ Switch to search if no target this long    │
│   Attack Min Duration: [10.0] sec                │
│   ℹ️ Keep attacking this long before checking   │
│                                                  │
│ [Save] [Reset to Defaults]                       │
│                                                  │
└──────────────────────────────────────────────────┘
```

**ADVANCED MODE** (click again):
```
┌─ ADVANCED SETTINGS ──────────────────────────────┐
│                                                  │
│ Manual Config Override:                          │
│   ☑ Override automatic settings                 │
│                                                  │
│   Attack Keys: [1,2,3]                          │
│   ℹ️ Manual key sequence (comma-separated)      │
│                                                  │
│   Key Hold Time: [100] ms                       │
│   ℹ️ How long to hold each key                  │
│                                                  │
│   Template Path: [Browse...]                     │
│   Region (LT): [100, 100]                       │
│   Region (RB): [900, 700]                       │
│   [Select Region on Screen]                      │
│                                                  │
│ [Save] [Reset]                                   │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Beginner: Chỉ 4 bước đơn giản
- ✅ Intermediate: Expose timing parameters với tooltips
- ✅ Advanced: Full control cho power users
- ✅ Progressive disclosure: Ẩn complexity cho đến khi cần

---

#### **Phase 3: First-Time Setup Wizard** (Priority: MEDIUM)

**Vấn đề cần giải quyết**: Người mới không biết bắt đầu từ đâu.

**Solution**: Wizard hướng dẫn từng bước khi lần đầu mở app.

**Wizard Flow**:

```
┌──────────────────────────────────────────────────┐
│ 🎉 Welcome to Cabal Auto Hunt!                   │
├──────────────────────────────────────────────────┤
│                                                  │
│ This wizard will help you set up your first     │
│ auto hunt in 5 easy steps.                      │
│                                                  │
│ [Get Started] [Skip (I know what I'm doing)]    │
│                                                  │
└──────────────────────────────────────────────────┘

Step 1/5: Game Window
┌──────────────────────────────────────────────────┐
│ Select your Cabal game window:                   │
│                                                  │
│ [Cabal Origin - PID 12345 ▼]                    │
│                                                  │
│ ℹ️ Make sure your game is running first!        │
│                                                  │
│ [Back] [Next →]                                  │
└──────────────────────────────────────────────────┘

Step 2/5: Monster Setup
┌──────────────────────────────────────────────────┐
│ Let's add your first hunting target:            │
│                                                  │
│ Monster Name: [Goblin]                          │
│ HP: [5000]                                       │
│ Your Damage: [300] per hit                      │
│                                                  │
│ Template Image:                                  │
│ [Capture Screenshot] or [Browse File]           │
│                                                  │
│ [← Back] [Next →]                                │
└──────────────────────────────────────────────────┘

Step 3/5: Skills Setup
┌──────────────────────────────────────────────────┐
│ Add your hunting skills:                        │
│                                                  │
│ Skill 1: [Dark Explosion ▼]                     │
│   Cooldown: 1.5s  Key: [1]                      │
│                                                  │
│ Skill 2: [Fire Ball ▼]                          │
│   Cooldown: 2.0s  Key: [2]                      │
│                                                  │
│ [+ Add More Skills]                              │
│                                                  │
│ [← Back] [Next →]                                │
└──────────────────────────────────────────────────┘

Step 4/5: Auto-Calculate Timing
┌──────────────────────────────────────────────────┐
│ We'll calculate optimal timing for you:         │
│                                                  │
│ Based on:                                        │
│ - Monster HP: 5000                               │
│ - Your damage: 300/hit                          │
│ - Skills avg cooldown: 1.75s                    │
│                                                  │
│ Recommended:                                     │
│ ✅ Lost Timeout: 1.3s                           │
│ ✅ Attack Duration: 30.5s                       │
│                                                  │
│ [← Back] [Next →]                                │
└──────────────────────────────────────────────────┘

Step 5/5: Ready!
┌──────────────────────────────────────────────────┐
│ 🎉 Setup Complete!                               │
│                                                  │
│ Your configuration:                              │
│ - Monster: Goblin                                │
│ - Skills: 2 skills                               │
│ - Timing: Auto-calculated                        │
│                                                  │
│ [← Back] [Start Hunting! 🎯]                    │
└──────────────────────────────────────────────────┘
```

**Wizard Features**:
- ✅ Step-by-step guidance
- ✅ Friendly explanations
- ✅ Auto-save progress
- ✅ Can skip for experienced users
- ✅ Validate each step before proceeding

---

#### **Phase 4: Multi-Monster Support** (Priority: MEDIUM)

**Vấn đề cần giải quyết**: Chỉ hunt 1 monster, không support combo nhiều quái.

**Solution**: Monster rotation/priority system

**NEW: Multi-Monster Hunt Mode**:

```
Hunt Tab:

┌─ MONSTER SELECTION ──────────────────────────────┐
│                                                  │
│ Hunt Mode:                                       │
│   ● Single Monster (Recommended)                 │
│   ○ Multi-Monster Rotation                       │
│   ○ Priority-Based (Advanced)                    │
│                                                  │
│ ┌── SINGLE MONSTER ────────────────────────┐    │
│ │ Monster: [Goblin ▼]                       │    │
│ │ Templates: 2 templates                    │    │
│ │ Status: Ready                             │    │
│ └───────────────────────────────────────────┘    │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Multi-Monster Rotation Mode**:
```
┌─ MULTI-MONSTER ROTATION ─────────────────────────┐
│                                                  │
│ Hunt these monsters in order:                    │
│                                                  │
│ 1. [Goblin ▼]          [↑] [↓] [×]             │
│    Priority: Normal                              │
│                                                  │
│ 2. [Orc ▼]             [↑] [↓] [×]             │
│    Priority: Normal                              │
│                                                  │
│ 3. [Dragon ▼]          [↑] [↓] [×]             │
│    Priority: Boss (longer timeout)              │
│                                                  │
│ [+ Add Monster]                                  │
│                                                  │
│ Rotation Strategy:                               │
│   ● Round-robin (equal time each)               │
│   ○ Priority-first (boss → strong → weak)       │
│                                                  │
│ ℹ️ Will cycle through all monsters during hunt  │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Priority-Based Mode**:
```
┌─ PRIORITY-BASED HUNT ────────────────────────────┐
│                                                  │
│ Hunt logic: Always prefer highest priority      │
│                                                  │
│ 🔴 HIGH Priority (hunt first):                   │
│   - Dragon (Boss)                                │
│   - Rare Mob                                     │
│                                                  │
│ 🟡 MEDIUM Priority (hunt if no high):            │
│   - Orc                                          │
│   - Elite Goblin                                 │
│                                                  │
│ 🟢 LOW Priority (hunt if nothing else):          │
│   - Goblin                                       │
│   - Weak Mob                                     │
│                                                  │
│ ℹ️ Auto will always target highest priority     │
│    monster visible on screen                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Level 1-60: Single monster (simple)
- ✅ Level 60+: Multi-monster rotation
- ✅ Boss priority: Always target boss first
- ✅ Flexible strategies

---

#### **Phase 5: Form Reorganization** (Priority: HIGH)

**Vấn đề cần giải quyết**: Forms lộn xộn, không có hierarchy rõ ràng.

**Solution**: Parent-Child form structure với tabs organized

**NEW Tab Structure**:

```
Main GUI:
┌──────────────────────────────────────────────────────┐
│ Cabal Auto Hunt                                      │
├──────────────────────────────────────────────────────┤
│ [🎯Hunt] [⚙️Setup] [📊Stats] [❓Help]                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  (Current tab content here)                          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**🎯 Hunt Tab** (Main action):
```
- [Beginner/Intermediate/Advanced mode toggle]
- Game window selector
- Monster selector (single/multi)
- Skill checkboxes
- Start/Stop buttons
- Real-time status
- Quick settings (collapsible)
```

**⚙️ Setup Tab** (Configuration):
```
Subtabs:
- [Monsters] - Monster Manager (CRUD, templates)
- [Skills]   - Skills Manager (CRUD, cooldowns, buffs)
- [Config]   - Advanced hunt config (for power users)
```

**📊 Stats Tab** (Analytics):
```
- Hunt session history
- Monster kill counts
- Skill usage statistics
- Average kill time
- Experience/hour estimate
- Log viewer
```

**❓ Help Tab** (Documentation):
```
- Getting Started guide
- Video tutorials
- FAQ
- Troubleshooting
- Keyboard shortcuts
- About
```

**Benefits**:
- ✅ Clear separation: Hunt vs Setup vs Analytics
- ✅ Hunt tab: Quick access, no clutter
- ✅ Setup tab: All configuration in one place
- ✅ Stats tab: Monitor performance
- ✅ Help tab: Always available guidance

---

## 🎨 Visual Mockups

### Beginner Hunt Tab (Clean & Simple)
```
┌────────────────────────────────────────────────────────┐
│ 🎯 Hunt                                                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Mode: ●Beginner  ○Intermediate  ○Advanced            │
│                                                        │
│  ┌──────────────────────────────────────────────┐     │
│  │ 1️⃣ Select Game Window                        │     │
│  │    [Cabal Origin - PID 12345    ▼] [Bring]  │     │
│  │                                               │     │
│  │ 2️⃣ Select Monster                            │     │
│  │    [Goblin (5k HP, 2 templates) ▼]          │     │
│  │    ✅ Auto-applied timing settings           │     │
│  │                                               │     │
│  │ 3️⃣ Select Skills                             │     │
│  │    ☑ Dark Explosion (Key: 1, CD: 1.5s)      │     │
│  │    ☑ Fire Ball (Key: 2, CD: 2.0s)           │     │
│  │    ☐ Lightning Strike (Key: 3, CD: 2.5s)    │     │
│  │                                               │     │
│  │ 4️⃣ Start Hunting                             │     │
│  │    [▶ Start Hunt]  [⏸ Stop (F9)]           │     │
│  │                                               │     │
│  │    Status: Ready to hunt                     │     │
│  │    🟢 Game window connected                  │     │
│  │    🟢 Monster configured                     │     │
│  │    🟢 2 skills selected                      │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  [⚙️ Show Advanced Settings]  [📚 Help & Guides]      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Setup Tab - Monsters (Manager)
```
┌────────────────────────────────────────────────────────┐
│ ⚙️ Setup → Monsters                                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Monsters                    │  Monster Details       │
│  ┌────────────────────┐     │  ┌──────────────────┐  │
│  │ • Goblin           │     │  │ Name: Goblin     │  │
│  │ • Orc              │     │  │ HP: 5000         │  │
│  │ • Dragon           │ ←───┼─ │ Damage: 300      │  │
│  │                    │     │  │                  │  │
│  │ [+ New Monster]    │     │  │ Templates: 2     │  │
│  │ [− Delete]         │     │  │ [Manage...]      │  │
│  │ [↑] [↓]           │     │  │                  │  │
│  └────────────────────┘     │  │ [Save] [Cancel]  │  │
│                             │  └──────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 📊 Implementation Plan

### Sprint 16 Breakdown

#### **Week 1: Core UX Improvements**
- [ ] Implement Beginner/Intermediate/Advanced mode toggle
- [ ] Redesign Hunt tab với 4-step beginner layout
- [ ] Add skill-based timing calculator
- [ ] Progressive disclosure for advanced settings

#### **Week 2: Setup Wizard**
- [ ] Create first-time setup wizard (5 steps)
- [ ] Wizard state persistence
- [ ] Skip wizard option
- [ ] Validation at each step

#### **Week 3: Multi-Monster Support**
- [ ] Multi-monster rotation mode
- [ ] Priority-based hunt mode
- [ ] Monster switching logic
- [ ] UI for monster list management

#### **Week 4: Form Reorganization**
- [ ] Restructure tabs (Hunt/Setup/Stats/Help)
- [ ] Setup tab subtabs (Monsters/Skills/Config)
- [ ] Stats tab implementation
- [ ] Help tab with guides

#### **Week 5: Polish & Testing**
- [ ] Tooltips for all fields
- [ ] Friendly error messages
- [ ] Default values optimization
- [ ] User testing & feedback
- [ ] Documentation update

---

## 🎯 Expected Outcomes

### User Experience Improvements

#### Before (Current):
```
New User Journey:
1. Opens GUI → Confused by tabs
2. Clicks Monster Manager → Empty list
3. Tries Hunt tab → Many fields, no idea what to fill
4. Googles "what is lost timeout" → No results
5. Gives up → Uses manual play
```

#### After (Sprint 16):
```
New User Journey:
1. Opens GUI → Wizard appears "Welcome!"
2. Follows 5 steps → Monster added, skills added, timing calculated
3. Click "Start Hunting" → Working immediately!
4. Checks Stats tab → Sees kill count, learns system
5. Happy user → Recommends to friends 🎉
```

### Technical Improvements

- ✅ **Accurate timing**: Calculated from actual skills, not guessed
- ✅ **Less configuration**: Auto-calculated defaults
- ✅ **Better workflow**: Beginner → Intermediate → Advanced
- ✅ **Multi-monster**: Support level 60+ gameplay
- ✅ **Organized UI**: Clear hierarchy, easy navigation

---

## 🚀 Migration Strategy

### Backward Compatibility

**Existing configs will still work**:
```python
# Old config (hunt_config.json):
{
  "attack_keys": ["1", "2", "3"],
  "lost_timeout_sec": 2.0,
  "attack_min_duration_sec": 10.0
}

# Migration:
if 'attack_keys' in config:
    # Legacy mode: Use manual keys
    mode = 'advanced'
else:
    # New mode: Use skills from skills.json
    mode = 'beginner'
```

**Show migration prompt**:
```
┌──────────────────────────────────────────────┐
│ 🆕 New Version Detected!                     │
├──────────────────────────────────────────────┤
│                                              │
│ We've improved the configuration system.    │
│                                              │
│ Your existing settings will still work,     │
│ but we recommend using the new wizard for   │
│ better experience.                           │
│                                              │
│ [Run Setup Wizard] [Keep Current Settings]  │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 📝 Summary

### Problems Solved

1. ✅ **Timing Calculator**: Now uses actual skills, not guessed attack speed
2. ✅ **Complex UI**: Beginner mode hides complexity
3. ✅ **Confusing terms**: Tooltips explain everything
4. ✅ **No guidance**: Setup wizard for first-time users
5. ✅ **Single monster**: Multi-monster rotation support
6. ✅ **Messy forms**: Organized tabs (Hunt/Setup/Stats/Help)

### User Benefits

- 🎯 **Beginners**: 4 simple steps to start hunting
- 🎯 **Intermediate**: See timing parameters, adjust as needed
- 🎯 **Advanced**: Full control, manual overrides
- 🎯 **Level 60+**: Multi-monster rotation
- 🎯 **Everyone**: Better tooltips, friendly messages

---

**Ready to implement Sprint 16?** 🚀
