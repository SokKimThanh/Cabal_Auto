# Data Sync Manager - UUID Monster System

## 📋 Tổng quan

Hệ thống quản lý đồng bộ dữ liệu giữa `monsters.json` và `hunt_config.json` với UUID.

## 🎯 Kiến trúc

### Cấu trúc dữ liệu

**monsters.json** - Source of truth (Nguồn chân lý)
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Cọc Gỗ",
    "level": 1,
    "priority": 1,
    "hp": 122.0,
    "damage_per_hit": 12.0,
    "templates": [],
    ...
  }
]
```

**hunt_config.json** - References only (Chỉ lưu tham chiếu)
```json
{
  "monster_list": [
    "550e8400-e29b-41d4-a716-446655440001",
    "another-uuid-here"
  ],
  "training_monster_list": [
    "550e8400-e29b-41d4-a716-446655440001"
  ]
}
```

### Lợi ích

✅ **Không trùng lặp dữ liệu** - Monster info chỉ lưu 1 nơi  
✅ **Dễ đồng bộ** - Chỉ cần sync ID, không cần copy object  
✅ **Nhất quán** - Update monster tự động ảnh hưởng tất cả  
✅ **Tiết kiệm** - File nhỏ hơn, ít redundancy  

## 🔧 API Reference

### DataSyncManager

**Load Operations**
```python
sync = DataSyncManager()

# Load all monsters
monsters = sync.load_monsters()  # List[Dict]

# Get specific monster
monster = sync.get_monster_by_id("uuid-here")  # Dict | None

# Get multiple monsters
monsters = sync.get_monsters_by_ids(["uuid-1", "uuid-2"])  # List[Dict]

# Load hunt config
config = sync.load_hunt_config()  # Dict
```

**Save Operations**
```python
# Save monsters
sync.save_monsters(monsters)  # -> bool

# Save hunt config
sync.save_hunt_config(config)  # -> bool
```

**Sync Operations**
```python
# Add monster to hunt list
sync.add_monster_to_hunt(monster_id, is_training=False)  # -> bool

# Delete monster (removes from both files)
sync.delete_monster(monster_id)  # -> bool

# Update monster (monsters.json only, hunt_config keeps ID)
sync.sync_monster_update(monster)  # -> bool

# Full sync (clean orphaned IDs)
sync.sync_all_monsters(monsters)  # -> bool
```

**Validation**
```python
# Check consistency
result = sync.validate_data_consistency()
# {
#   'valid': True,
#   'monsters_count': 10,
#   'hunt_ids_count': 5,
#   'training_ids_count': 3,
#   'orphaned_in_hunt': [],
#   'orphaned_in_training': []
# }

# Fix orphaned references
sync.fix_orphaned_references()  # -> bool
```

## 🔄 Workflows

### 1. Thêm Monster Mới

```python
# 1. Create monster with UUID
import uuid
new_monster = {
    'id': str(uuid.uuid4()),
    'name': 'Slime',
    'level': 5,
    'priority': 1,
    'templates': []
}

# 2. Add to monsters list
monsters.append(new_monster)
sync.save_monsters(monsters)

# 3. Add to hunt list (optional)
sync.add_monster_to_hunt(new_monster['id'], is_training=False)
```

### 2. Xóa Monster

```python
# Using sync manager (recommended)
sync.delete_monster(monster_id)  # Removes from BOTH files

# Manual (if needed)
monsters = [m for m in monsters if m['id'] != monster_id]
sync.save_monsters(monsters)
sync.sync_all_monsters(monsters)  # Clean up hunt_config
```

### 3. Cập nhật Monster

```python
# Update in monsters.json
monster['name'] = 'New Name'
monster['level'] = 10
sync.save_monsters(monsters)

# Hunt config automatically uses updated data (no sync needed)
# Because it only stores ID, lookup happens at runtime
```

### 4. Load Monster từ Hunt Config

```python
config = sync.load_hunt_config()
monster_ids = config.get('monster_list', [])

# Get full monster data
monsters = sync.get_monsters_by_ids(monster_ids)

for monster in monsters:
    print(f"{monster['name']} - Level {monster['level']}")
```

## 🛡️ Data Integrity

### Auto-cleanup on Empty

```python
# When monsters.json is empty
sync.save_monsters([])
sync.sync_all_monsters([])

# hunt_config automatically clears:
# monster_list: []
# training_monster_list: []
```

### Validation & Repair

```python
# Check for orphaned IDs
result = sync.validate_data_consistency()

if not result['valid']:
    print(f"Orphaned in hunt: {result['orphaned_in_hunt']}")
    print(f"Orphaned in training: {result['orphaned_in_training']}")
    
    # Auto-fix
    sync.fix_orphaned_references()
```

## 📝 Migration Notes

### Old Format (Full Objects)
```json
{
  "monster_list": [
    {
      "id": "uuid-1",
      "name": "Monster",
      "level": 5,
      ...
    }
  ]
}
```

### New Format (IDs Only)
```json
{
  "monster_list": [
    "uuid-1",
    "uuid-2"
  ]
}
```

### Migration Script
```python
# Convert old format to new
config = sync.load_hunt_config()

# Extract IDs from objects
if config.get('monster_list'):
    old_list = config['monster_list']
    if old_list and isinstance(old_list[0], dict):
        # Old format detected
        config['monster_list'] = [m.get('id') for m in old_list if m.get('id')]
        sync.save_hunt_config(config)
```

## 🔍 Testing

```bash
# Test sync manager
python scripts/test_sync_manager.py

# Test delete sync
python scripts/test_delete_sync.py
```

## 🎨 UI Integration

### Monster Editor

```python
class QuickMonsterEditor:
    def __init__(self):
        self.sync_manager = DataSyncManager()
    
    def _save_monsters(self):
        # Use sync manager
        return self.sync_manager.save_monsters(self.monsters)
    
    def delete_monster(self, monster_id):
        # Sync delete
        if self.sync_manager.delete_monster(monster_id):
            # Remove from local list
            self.monsters = [m for m in self.monsters if m['id'] != monster_id]
            self._refresh_ui()
```

## 📊 Performance

- **Load time**: O(n) - Linear scan for ID lookup
- **Save time**: O(1) - Direct JSON write
- **Sync time**: O(n) - Filter operations on lists
- **Memory**: Minimal - Only IDs stored in hunt_config

## 🚀 Future Enhancements

- [ ] Cache monster map for faster lookups
- [ ] Batch operations for multiple monsters
- [ ] Transaction rollback on failed operations
- [ ] Backup/restore functionality
- [ ] Change history tracking

## 📞 Support

Xem thêm:
- `lib/data/sync_manager.py` - Implementation
- `scripts/test_sync_manager.py` - Test examples
- `ui/windows/quick_monster_editor.py` - UI integration

---
**Author**: SokKimThanh  
**Date**: 2025-10-25  
**Version**: 1.0
