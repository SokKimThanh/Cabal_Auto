# Sprint 19 Task #5: Skill Rotation Builder

## 🎯 Mục Tiêu
Xây dựng giao diện và logic để tính toán chính xác timing cho skill rotation với:
- Thứ tự chiêu cụ thể
- Cooldown và cast time của từng chiêu
- Buff skills và attack skills
- Rhythm/nhịp điệu chi tiết từng giây

## ❌ Vấn Đề Với Timing Calculator Cũ

### 1. **Không có danh sách chiêu rõ ràng**
- User không biết sẽ dùng chiêu nào
- Không thể kiểm soát thứ tự

### 2. **Tính toán không chính xác**
```python
# CŨ: Tính trung bình đơn giản
rotation_cycle_time = sum(cast_time)
attacks_per_second = len(skills) / rotation_cycle_time
attack_interval = max(min_cooldown, avg_cast_time)
```

**Vấn đề**: Không tính cooldown overlap, không tính wait time thực tế

### 3. **Thiếu buff skills**
- Chỉ focus vào attack skills
- Không track buff timing

### 4. **Không lưu rotation sequence**
- Chỉ lưu timing tổng quát
- Auto không biết nhấn chiêu nào trước

## ✅ Giải Pháp: Skill Rotation Builder

### Architecture

```
lib/features/skill_rotation/
├── __init__.py
├── builder.py          # Core rotation calculation logic
├── ui_integration.py   # Integration with Library Manager
└── README.md
```

### Core Logic (`builder.py`)

```python
@dataclass
class SkillTiming:
    skill_name: str
    key: str
    skill_type: str  # 'attack' or 'buff'
    cast_time: float
    cooldown: float
    press_duration_ms: int
    
    # Calculated in rotation
    start_time: float = 0.0
    cast_finish_time: float = 0.0
    cooldown_ready_time: float = 0.0
    wait_after_cast: float = 0.0

@dataclass
class SkillRotation:
    skills: List[SkillTiming]
    total_cycle_time: float
    skills_per_cycle: int
    rhythm_description: str
    attack_interval: float
    attack_press_ms: int
```

### Calculation Algorithm

```python
def calculate_rotation_timing(skills: List[dict]) -> SkillRotation:
    skill_timings = []
    current_time = 0.0
    skill_cooldowns = {}  # Track last use time
    
    for skill in skills:
        # Check if on cooldown
        if skill_name in skill_cooldowns:
            cooldown_ready = skill_cooldowns[skill_name]
            if current_time < cooldown_ready:
                current_time = cooldown_ready  # Wait!
        
        # Create timing entry
        timing = SkillTiming(
            start_time=current_time,
            cast_finish_time=current_time + cast_time,
            cooldown_ready_time=current_time + cooldown,
            ...
        )
        
        # Update cooldown tracker
        skill_cooldowns[skill_name] = current_time + cooldown
        
        # Move to next skill (after cast finishes + buffer)
        current_time += cast_time + 0.1
    
    return SkillRotation(...)
```

### Example Output

```
🎵 Skill Rotation Timeline:
──────────────────────────────────────────────────────────────
1. [1] Dark Explosion (attack)
   ⏱️  Start: 0.00s
   🎯 Press key for 170ms
   ⏳ Cast time: 1.70s
   ✅ Cast finish: 1.70s
   🔄 Cooldown ready: 1.90s
   ⏸️  Wait: 0.10s

2. [4] Regeneration (buff)
   ⏱️  Start: 1.80s
   🎯 Press key for 100ms
   ⏳ Cast time: 1.00s
   ✅ Cast finish: 2.80s
   🔄 Cooldown ready: 4.00s
   ⏸️  Wait: 0.10s

3. [2] Bone Javelin (attack)
   ⏱️  Start: 2.90s
   🎯 Press key for 150ms
   ⏳ Cast time: 1.50s
   ✅ Cast finish: 4.40s
   🔄 Cooldown ready: 5.30s
   ⏸️  Wait: 0.90s

🔁 Rotation restarts at: 5.30s
```

## 🎨 UI Design

### Tab Layout: "Skill Rotation"

```
┌─────────────────────────────────────────────────────────────┐
│  🎮 SKILL ROTATION BUILDER                                  │
├────────────────────┬────────────────────────────────────────┤
│ 📚 AVAILABLE       │ 🎯 ROTATION SEQUENCE                   │
│ SKILLS             │                                        │
│                    │ 1. Dark Explosion (attack)             │
│ [x] Dark Explosion │    ⏱️  1.7s cast, 🔄 1.9s CD          │
│     Attack         │    [Move Up] [Move Down] [Remove]     │
│     CD: 1.9s       │                                        │
│     Cast: 1.7s     │ 2. Regeneration (buff)                 │
│                    │    ⏱️  1.0s cast, 🔄 2.2s CD          │
│ [x] Bone Javelin   │    [Move Up] [Move Down] [Remove]     │
│     Attack         │                                        │
│     CD: 2.4s       │ 3. Bone Javelin (attack)               │
│     Cast: 1.5s     │    ⏱️  1.5s cast, 🔄 2.4s CD          │
│                    │    [Move Up] [Move Down] [Remove]     │
│ [ ] Skull Shooter  │                                        │
│     Attack         │ [Add Selected Skills ➜]               │
│     CD: 2.2s       │ [Clear All]                            │
│     Cast: 1.5s     │                                        │
│                    │                                        │
│ [x] Regeneration   │                                        │
│     Buff           │                                        │
│     CD: 2.2s       │                                        │
│     Cast: 1.0s     │                                        │
└────────────────────┴────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📊 ROTATION ANALYSIS                                       │
├─────────────────────────────────────────────────────────────┤
│  🔄 Total Cycle Time: 5.30 seconds                          │
│  ⚡ Skills per cycle: 3 skills                              │
│  🎵 Rhythm: [View detailed timeline...]                     │
│                                                             │
│  📋 CÁC CON SỐ SẼ LƯU:                                      │
│    • Chu kỳ tổng: 5.30 giây                                │
│    • Số chiêu: 3 chiêu                                     │
│    • Giữ phím trung bình: 160 mili-giây                    │
│                                                             │
│  🎵 NHỊP ĐIỆU THỰC HIỆN:                                    │
│    1. Giây 0.00: Bấm [1] Dark Explosion (giữ 170ms)        │
│       → Đợi 1.70s (đang cast)                              │
│       → Đợi thêm 0.10s                                     │
│                                                             │
│    2. Giây 1.80: Bấm [4] Regeneration (giữ 100ms)          │
│       → Đợi 1.00s (đang cast)                              │
│       → Đợi thêm 0.10s                                     │
│                                                             │
│    3. Giây 2.90: Bấm [2] Bone Javelin (giữ 150ms)          │
│       → Đợi 1.50s (đang cast)                              │
│       → Đợi thêm 0.90s                                     │
│                                                             │
│    🔁 Sau 5.30s → Lặp lại từ đầu                           │
└─────────────────────────────────────────────────────────────┘

[Calculate Rotation] [Apply to Hunt Config] [Test Preview]
```

## 📝 Implementation Plan

### Phase 1: Core Logic ✅ (DONE)
- [x] `builder.py` with rotation calculation
- [x] Test với example data
- [x] Verify timing accuracy

### Phase 2: UI Integration (IN PROGRESS)
- [ ] Create new "Skill Rotation" tab in Library Manager
- [ ] Two-panel layout: Available Skills + Rotation Sequence
- [ ] Drag-and-drop or button-based reordering
- [ ] Real-time preview of rotation

### Phase 3: Hunt Config Integration
- [ ] Save rotation to `hunt_config.json`
- [ ] Add `skill_rotation` field:
  ```json
  {
    "skill_rotation": {
      "enabled": true,
      "sequence": [
        {"name": "Dark Explosion", "key": "1", "type": "attack", ...},
        {"name": "Regeneration", "key": "4", "type": "buff", ...},
        {"name": "Bone Javelin", "key": "2", "type": "attack", ...}
      ],
      "total_cycle_time": 5.30,
      "attack_interval": 2.65,
      "attack_press_ms": 160
    }
  }
  ```

### Phase 4: Auto Hunt Integration
- [ ] Update `auto_hunt.py` to read rotation sequence
- [ ] Implement rotation execution loop
- [ ] Replace simple attack with skill rotation

## 🧪 Testing

### Test Case 1: Attack + Buff Rotation
```python
skills = [
    {'name': 'Dark Explosion', 'key': '1', 'type': 'attack', 'cooldown': 1.9, 'cast_time': 1.7},
    {'name': 'Regeneration', 'key': '4', 'type': 'buff', 'cooldown': 2.2, 'cast_time': 1.0},
    {'name': 'Bone Javelin', 'key': '2', 'type': 'attack', 'cooldown': 2.4, 'cast_time': 1.5}
]

Expected:
- Total cycle: ~5.3s
- Skill 1 at 0.00s
- Skill 2 at 1.80s (after skill 1 finishes)
- Skill 3 at 2.90s (after skill 2 finishes)
```

### Test Case 2: Cooldown Overlap
```python
skills = [
    {'name': 'Quick Strike', 'key': '1', 'type': 'attack', 'cooldown': 5.0, 'cast_time': 0.5},
    {'name': 'Quick Strike', 'key': '1', 'type': 'attack', 'cooldown': 5.0, 'cast_time': 0.5}
]

Expected:
- Skill 1 at 0.00s
- Skill 2 at 5.00s (must wait for cooldown!)
- Total cycle: ~5.5s
```

## 📊 Success Metrics

1. **Accuracy**: Rotation timing matches actual game cooldowns
2. **Flexibility**: Supports any skill order, buff + attack mix
3. **Clarity**: User can see exact timeline before applying
4. **Integration**: Auto executes exact sequence saved

## 🚀 Next Steps

1. Continue Phase 2: Build UI components
2. Test UI with mock data
3. Integrate with hunt_config save/load
4. Update auto_hunt to execute rotation

---

**Status**: Phase 1 Complete ✅, Phase 2 In Progress 🚧
**Last Updated**: 2025-10-19
