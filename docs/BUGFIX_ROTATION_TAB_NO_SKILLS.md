# Bug Fix: Không Có Kỹ Năng Trong Tab Chu Kỳ Chiêu (Rotation Tab)

## 🐛 Vấn Đề

**Triệu chứng**: Khi mở Setup Wizard → Bước Skills → Mở Library Manager → Tab "Chu Kỳ Chiêu", không có kỹ năng nào hiện ra.

**User Flow**:
1. Mở Setup Wizard
2. Đến bước 4 (Skills Configuration)
3. Bấm nút "Open Skill Rotation Builder"
4. Library Manager mở ra
5. Chuyển sang tab "🎮 Chu Kỳ Chiêu" (Skill Rotation)
6. ❌ Panel bên trái hiện: "No skills found in hunt_config.json"
7. ❌ Không có skill nào để chọn

## 🔍 Phân Tích

### Root Cause

**File**: `lib/features/skill_rotation/ui_integration.py`  
**Method**: `_load_available_skills()` (line 318)

```python
# ❌ BUG - CHỈ load từ hunt_config.json
def _load_available_skills(self):
    """Load skills from hunt_config.json"""
    try:
        # Load from hunt_config
        hunt_config_path = Path(__file__).parent.parent.parent / 'lib' / 'data' / 'hunt_config.json'
        
        if hunt_config_path.exists():
            with open(hunt_config_path, 'r', encoding='utf-8') as f:
                hunt_config = json.load(f)
                self.available_skills = hunt_config.get('skill_slots', [])
```

**Vấn đề**:
- `SkillRotationUI` **chỉ** load skills từ `hunt_config.json`
- Trong Setup Wizard flow, `hunt_config.json` chưa tồn tại hoặc chưa có `skill_slots`
- Wizard chưa hoàn thành → chưa save config → file rỗng/không có data
- Kết quả: `available_skills = []` → Không có skills hiển thị

### Context Analysis

#### Setup Wizard Flow
```
1. User mở Setup Wizard
2. Đến Step 4 (Skills)
3. Bấm "Open Rotation Builder"
   ↓
4. setup_wizard.py gọi LibraryManagerWindow()
   - Truyền: skills=self.skills_data
   - skills_data load từ lib/data/skills.json
   ↓
5. LibraryManagerWindow.__init__()
   - Nhận: self.skills = skills.copy()
   - skills có data từ skills.json ✅
   ↓
6. Tab Rotation được build
   - Gọi: SkillRotationUI(parent, library_manager)
   - SkillRotationUI có reference: self.lib_manager
   ↓
7. SkillRotationUI._load_available_skills()
   - ❌ BUG: Chỉ load từ hunt_config.json
   - Bỏ qua self.lib_manager.skills (có data!)
   - hunt_config.json chưa có data → Fail!
```

#### Main App Flow (Normal)
```
1. User mở App
2. hunt_config.json đã tồn tại (từ lần setup trước)
3. Mở Library Manager từ menu
   ↓
4. LibraryManagerWindow() được tạo
   - skills parameter có thể empty
   - Không sao vì hunt_config.json có data
   ↓
5. SkillRotationUI._load_available_skills()
   - Load từ hunt_config.json ✅
   - Skills hiển thị bình thường
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SETUP WIZARD CONTEXT                     │
└─────────────────────────────────────────────────────────────┘

lib/data/skills.json        hunt_config.json
       ↓                           ↓
   (Has data)               (Empty/No data)
       ↓                           ↓
Setup Wizard loads          Wizard hasn't
skills_data ✅              saved yet ❌
       ↓                           ↓
Pass to LibraryManager      Not available
library_manager.skills ✅    for loading
       ↓                           ↓
   SkillRotationUI                 │
       │                           │
       │  ❌ BUG: Ignores          │
       │     lib_manager.skills    │
       │                           │
       └───────> Only loads from ──┘
                 hunt_config.json
                       ↓
                   Empty! ❌
                       ↓
           No skills displayed
```

## ✅ Giải Pháp

### Code Fix

**File**: `lib/features/skill_rotation/ui_integration.py`  
**Method**: `_load_available_skills()`

```python
# ✅ FIXED - Load từ library_manager.skills TRƯỚC, fallback hunt_config.json
def _load_available_skills(self):
    """Load skills from library manager or hunt_config.json"""
    try:
        # Priority 1: Load from library manager's skills (for Setup Wizard context)
        if hasattr(self.lib_manager, 'skills') and self.lib_manager.skills:
            # Skills from library manager (master list)
            # Convert to skill_slots format if needed
            self.available_skills = []
            for skill in self.lib_manager.skills:
                skill_slot = {
                    'name': skill.get('name', 'Unnamed'),
                    'key': skill.get('key', ''),
                    'cooldown': skill.get('cooldown', 0),
                    'type': skill.get('type', 'attack')
                }
                self.available_skills.append(skill_slot)
        else:
            # Priority 2: Fallback to hunt_config.json (for main app context)
            hunt_config_path = Path(__file__).parent.parent.parent / 'lib' / 'data' / 'hunt_config.json'
            
            if hunt_config_path.exists():
                with open(hunt_config_path, 'r', encoding='utf-8') as f:
                    hunt_config = json.load(f)
                    self.available_skills = hunt_config.get('skill_slots', [])
        
        # Render skill checkboxes
        self._render_available_skills()
```

### Solution Strategy

**Two-Tier Loading**:

1. **Priority 1**: Load từ `library_manager.skills`
   - Dùng cho Setup Wizard context
   - Skills đã được load sẵn từ `skills.json`
   - Có sẵn trong memory

2. **Priority 2**: Fallback to `hunt_config.json`
   - Dùng cho Main App context
   - Khi library_manager.skills không có data
   - Hoặc mở từ menu chính (không qua wizard)

### Data Format Conversion

Skills từ `library_manager.skills` có format khác `hunt_config.skill_slots`:

**skills.json format**:
```json
{
  "name": "Fireball",
  "key": "1",
  "cooldown": 5,
  "type": "attack",
  "image_path": "..."
}
```

**skill_slots format** (needed by SkillRotationUI):
```json
{
  "name": "Fireball",
  "key": "1",
  "cooldown": 5,
  "type": "attack"
}
```

Code converts format khi load từ library_manager.skills.

## 🧪 Testing

### Test Suite Created

**File**: `tests/test_rotation_skills_loading.py`

**Test Scenarios**:

#### 1. Test from Setup Wizard Context
- Mock wizard opening Library Manager
- Pass skills from memory (`library_manager.skills`)
- Verify skills appear in Rotation tab
- Skills source: `lib/data/skills.json`

#### 2. Test from Main App Context
- Mock main app opening Library Manager  
- Pass empty skills list
- Verify skills load from `hunt_config.json` (fallback)
- Skills source: `hunt_config.json`

### How to Run Tests

```powershell
cd e:\Cabal_Auto
python tests\test_rotation_skills_loading.py
```

**Test Menu**:
- 1️⃣ Test from Setup Wizard Context (library_manager.skills)
- 2️⃣ Test from Main App Context (hunt_config.json fallback)

### Manual Test Steps

#### Test 1: Setup Wizard Context

1. Xóa/backup `lib/data/hunt_config.json` (đảm bảo không có data)
2. Chạy Setup Wizard:
   ```powershell
   python tests\test_setup_wizard_button.py
   ```
3. Đến Step 4 (Skills Configuration)
4. Bấm "🎯 Open Skill Rotation Builder"
5. Library Manager mở ra
6. Chuyển sang tab "🎮 Chu Kỳ Chiêu"
7. ✅ **VERIFY**: Panel bên trái hiện skills
8. ✅ **VERIFY**: Skills load từ `skills.json` (qua library_manager)

#### Test 2: Main App Context

1. Tạo `lib/data/hunt_config.json` với skills:
   ```json
   {
     "skill_slots": [
       {"name": "Slash", "key": "1", "cooldown": 3, "type": "attack"}
     ]
   }
   ```
2. Mở main app:
   ```powershell
   python app_gui.py
   ```
3. Mở Library Manager từ menu
4. Chuyển sang tab "Rotation"
5. ✅ **VERIFY**: Skills load từ `hunt_config.json`

## 📊 Kết Quả

### Trước Fix

| Context | Skills Source | Result |
|---------|--------------|--------|
| Setup Wizard | hunt_config.json | ❌ Empty → No skills |
| Main App | hunt_config.json | ✅ Works (if config exists) |

### Sau Fix

| Context | Skills Source | Result |
|---------|--------------|--------|
| Setup Wizard | library_manager.skills | ✅ Works! |
| Main App | hunt_config.json (fallback) | ✅ Works! |

### User Experience

**Before**:
```
Setup Wizard → Rotation Builder
    ↓
"No skills found in hunt_config.json"
    ↓
❌ Cannot build skill rotation
❌ Confusing - skills exist but don't show
```

**After**:
```
Setup Wizard → Rotation Builder
    ↓
Skills loaded from memory ✅
    ↓
✅ Can select and arrange skills
✅ Smooth workflow
```

## 📁 Files Changed

### Modified Files

1. **`lib/features/skill_rotation/ui_integration.py`**
   - Method: `_load_available_skills()` (line 318)
   - Changes: Added priority loading logic
   - Lines modified: ~25 lines (expanded from ~10)

### New Files

2. **`tests/test_rotation_skills_loading.py`** (New)
   - Test suite for skills loading
   - 2 test scenarios
   - Lines: 500+

3. **`docs/BUGFIX_ROTATION_TAB_NO_SKILLS.md`** (New)
   - Documentation (this file)

## 🔧 Technical Details

### Why Two Data Sources?

**skills.json** (Master List):
- Complete list of all available skills
- Includes all metadata (image_path, etc.)
- Used for skill library management
- Source of truth

**hunt_config.json** (Active Config):
- Currently selected/configured skills
- Subset of skills.json
- Used by hunting bot at runtime
- Created after wizard completion

### Loading Strategy Comparison

#### Before (Single Source)
```python
# Only hunt_config.json
available_skills = load_from_hunt_config()
# ❌ Fails if hunt_config doesn't exist
```

#### After (Priority Loading)
```python
# Try library_manager first
if library_manager.skills:
    available_skills = library_manager.skills  # ✅
else:
    # Fallback to hunt_config
    available_skills = load_from_hunt_config()  # ✅
```

### Context Detection

Code uses duck typing to detect context:
```python
if hasattr(self.lib_manager, 'skills') and self.lib_manager.skills:
    # Wizard context - skills available in memory
else:
    # Main app context - load from file
```

## 🎯 Related Issues

### Fixed
- ✅ Skills không hiện trong Rotation tab từ Setup Wizard
- ✅ "No skills found" message khi skills thực sự tồn tại

### Not Affected
- ✅ Skills loading trong Monster tab (dùng mechanism khác)
- ✅ Skills selection trong Setup Wizard Step 4 (trực tiếp từ skills.json)
- ✅ Main app Library Manager (đã có hunt_config.json)

## 💡 Lessons Learned

### Code Design
1. **Multiple Data Sources**: Cần support nhiều contexts với data sources khác nhau
2. **Priority Loading**: Load from memory trước, fallback to file
3. **Context Awareness**: Code nên aware về context (wizard vs main app)

### Testing
1. **Context-Specific Tests**: Test cả 2 contexts riêng biệt
2. **Data Availability**: Test với missing data, partial data, complete data
3. **Integration Tests**: Test toàn bộ flow, không chỉ isolated units

### Documentation
1. **User Flows**: Document rõ các user flows khác nhau
2. **Data Flow Diagrams**: Visual diagrams giúp hiểu data flow
3. **Context Explanation**: Giải thích tại sao có multiple approaches

## 🚀 Future Improvements

### Short-Term
1. Add logging để track skills loading source
2. Add validation cho skill data format
3. Add error messages rõ ràng hơn

### Long-Term
1. **Unified Skills Manager**: Centralize skills loading logic
2. **Cache Layer**: Cache skills để tránh reload nhiều lần
3. **Skills Sync**: Auto-sync giữa skills.json và hunt_config.json

## 🏁 Conclusion

**Bug Status**: ✅ **FIXED**

**Changes**: Minimal (~25 lines)

**Impact**: High (critical feature unusable trong Setup Wizard)

**Testing**: Comprehensive test suite created

**Risk**: Very low (simple priority loading logic)

**User Benefit**: Setup Wizard flow giờ hoạt động hoàn chỉnh

---

**Bug Report Date**: 2025-01-21  
**Fixed Date**: 2025-01-21  
**Severity**: High (feature broken in wizard context)  
**Complexity**: Low (simple loading logic)  
**Status**: ✅ Verified and Documented
