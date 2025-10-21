# Sprint 22 Patch 1 - Quick Implementation Guide

**For**: Developer implementing Training Mode  
**Status**: 30% Complete - Next steps outlined below

---

## ✅ Completed (30%)

1. **Database Schema**: `training_mode` field added to monsters.json
2. **Load Function**: `load_monster_library()` reads training_mode
3. **Save Function**: `save_monster_library()` writes training_mode
4. **Documentation**: Complete feature spec created

---

## 🔧 Next Steps: Remaining Implementation (70%)

### Step 1: Add Training Mode UI to Hunt Tab

**File**: `app_gui.py`  
**Function**: `_build_hunt_tab()`  
**Location**: After monster rotation section (around line 892)

```python
# Add after self._refresh_monster_rotation_list() call

# Section: Training Mode (Sprint 22 Patch 1)
training_frame = tk.LabelFrame(frm, text="🎯 Training Mode", padx=10, pady=8)
training_frame.grid(row=3, column=0, columnspan=4, sticky='we', pady=(0,12))

# Training mode toggle
self.training_mode_var = tk.BooleanVar(value=False)
training_check = tk.Checkbutton(
    training_frame,
    text="Enable Training Mode (Practice Skills)",
    variable=self.training_mode_var,
    command=self._on_training_mode_changed,
    font=('Arial', 9)
)
training_check.pack(anchor='w', pady=4)

# Description
training_desc = tk.Label(
    training_frame,
    text="Practice skill rotation on training dummy without target switching. Perfect for testing timing and cooldowns.",
    fg='#666',
    font=('Arial', 9),
    wraplength=600,
    justify='left'
)
training_desc.pack(anchor='w', pady=(0,8))

# Skill stats frame (hidden by default)
self.skill_stats_frame = tk.Frame(training_frame, relief='sunken', bd=1, bg='#f9f9f9')
self.skill_stats_frame.pack(fill='x', pady=(8,0))
self.skill_stats_frame.pack_forget()  # Hide initially

# Build skill stats UI
self._build_skill_stats_display()
```

---

### Step 2: Implement Training Mode Toggle Logic

**File**: `app_gui.py`  
**Add new method** (around line 1600, after other monster methods)

```python
def _on_training_mode_changed(self):
    """Handle training mode toggle (Sprint 22 Patch 1)."""
    is_training = self.training_mode_var.get()
    
    if is_training:
        # Filter to training monsters only
        training_monsters = [m for m in self.monsters if m.get('training_mode', False)]
        
        if not training_monsters:
            messagebox.showwarning(
                "Training Mode",
                "No training dummy found. Please add a monster with training_mode=true (e.g., 'Coc go~')."
            )
            self.training_mode_var.set(False)
            return
        
        # Disable rotation mode
        self.rotation_mode_combo.config(state='disabled')
        
        # Update monster list to show only training dummies
        self.monster_rotation_listbox.delete(0, 'end')
        for monster in training_monsters:
            name = monster.get('name', 'Unknown')
            self.monster_rotation_listbox.insert('end', f"🎯 {name} (Training)")
        
        # Auto-select first training dummy
        if training_monsters:
            self.monster_rotation_listbox.selection_set(0)
            # Store training monster for hunt config
            self.hunt_cfg['training_monster'] = training_monsters[0]['name']
            self.hunt_cfg['training_mode'] = True
        
        # Show skill stats
        self.skill_stats_frame.pack(fill='x', pady=(8,0))
        
        # Update status
        self.hunt_status.set("🎯 Training Mode Active - Ready to practice skills")
        
    else:
        # Re-enable rotation mode
        self.rotation_mode_combo.config(state='readonly')
        
        # Restore normal monster list
        self._refresh_monster_rotation_list()
        
        # Hide skill stats
        self.skill_stats_frame.pack_forget()
        
        # Clear training mode from config
        self.hunt_cfg['training_mode'] = False
        if 'training_monster' in self.hunt_cfg:
            del self.hunt_cfg['training_monster']
        
        # Update status
        self.hunt_status.set("Hunt Idle - Select monster and click Start Hunt")
```

---

### Step 3: Build Skill Stats Display

**File**: `app_gui.py`  
**Add new method** (after `_on_training_mode_changed`)

```python
def _build_skill_stats_display(self):
    """Build skill statistics display for training mode (Sprint 22 Patch 1)."""
    # Header
    header = tk.Frame(self.skill_stats_frame, bg='#e3f2fd', relief='ridge', bd=1)
    header.pack(fill='x', pady=(4,4))
    
    tk.Label(
        header, 
        text="📊 Skill Performance Statistics", 
        font=('Arial', 9, 'bold'), 
        bg='#e3f2fd',
        fg='#1976d2'
    ).pack(pady=6)
    
    # Stats table container
    table_container = tk.Frame(self.skill_stats_frame, bg='white')
    table_container.pack(fill='both', expand=True, padx=4, pady=4)
    
    # Column headers
    columns = [
        ("Skill", 20),
        ("Casts", 8),
        ("Last Cast", 15),
        ("Cooldown", 12),
        ("Success %", 10)
    ]
    
    header_row = tk.Frame(table_container, bg='#f0f0f0', relief='raised', bd=1)
    header_row.pack(fill='x', pady=(0,2))
    
    for col_name, width in columns:
        tk.Label(
            header_row, 
            text=col_name, 
            font=('Arial', 8, 'bold'),
            bg='#f0f0f0',
            width=width,
            anchor='w',
            padx=4
        ).pack(side='left', padx=1)
    
    # Stats rows frame (dynamic content)
    self.skill_stats_rows_frame = tk.Frame(table_container, bg='white')
    self.skill_stats_rows_frame.pack(fill='both', expand=True)
    
    # Placeholder text
    self.skill_stats_placeholder = tk.Label(
        self.skill_stats_rows_frame,
        text="Start hunt to see skill statistics...",
        fg='#999',
        font=('Arial', 9, 'italic'),
        bg='white'
    )
    self.skill_stats_placeholder.pack(pady=20)
    
    # Initialize stats dict
    self.skill_stats_labels = {}
```

---

### Step 4: Add Update Stats Method

**File**: `app_gui.py`  
**Add new method** (after `_build_skill_stats_display`)

```python
def update_skill_stats(self, skill_stats):
    """Update skill statistics display (called from hunt loop).
    
    Args:
        skill_stats: dict of {skill_name: {cast_count, last_cast_time, cooldown, success_rate}}
    """
    # Hide placeholder
    if hasattr(self, 'skill_stats_placeholder'):
        self.skill_stats_placeholder.pack_forget()
    
    # Clear existing rows
    for widgets in self.skill_stats_labels.values():
        for w in widgets:
            w.destroy()
    self.skill_stats_labels.clear()
    
    # Add new rows
    import time
    for skill_name, stats in skill_stats.items():
        row_frame = tk.Frame(self.skill_stats_rows_frame, bg='white', relief='flat')
        row_frame.pack(fill='x', pady=1)
        
        cast_count = stats.get('cast_count', 0)
        last_cast = stats.get('last_cast_time')
        cooldown = stats.get('cooldown_remaining', 0)
        success = stats.get('success_count', 0)
        
        # Format values
        last_cast_str = f"{time.time() - last_cast:.1f}s ago" if last_cast else "Never"
        cooldown_str = f"{cooldown:.1f}s" if cooldown > 0 else "Ready"
        success_rate = f"{(success/cast_count*100):.0f}%" if cast_count > 0 else "N/A"
        
        # Color code success rate
        if cast_count > 0:
            rate = (success/cast_count*100)
            if rate >= 90:
                success_color = '#4caf50'  # Green
            elif rate >= 70:
                success_color = '#ff9800'  # Orange
            else:
                success_color = '#f44336'  # Red
        else:
            success_color = '#666'
        
        # Create labels
        labels = []
        values = [
            (skill_name, 20, '#000'),
            (str(cast_count), 8, '#000'),
            (last_cast_str, 15, '#666'),
            (cooldown_str, 12, '#1976d2' if cooldown > 0 else '#4caf50'),
            (success_rate, 10, success_color)
        ]
        
        for value, width, fg in values:
            label = tk.Label(
                row_frame, 
                text=value, 
                font=('Arial', 8),
                bg='white',
                fg=fg,
                width=width,
                anchor='w',
                padx=4
            )
            label.pack(side='left', padx=1)
            labels.append(label)
        
        self.skill_stats_labels[skill_name] = labels
```

---

### Step 5: Modify Hunt Logic

**File**: `ui/auto_hunt.py`  
**Function**: `hunt_loop()` (around line 100-200)

**Find the target lost/timeout section and add**:

```python
# Around line 150-200, find the target lost detection
# Add training mode check:

is_training = cfg.get('training_mode', False)

# In the main hunt loop:
while not hunt_stopped:
    box, template_info = locate_target(cfg)
    
    if box:
        # Target found - attack
        attack_monster(box, cfg, runtime, logger, app_root)
    else:
        # Target lost
        if is_training:
            # Training mode: don't switch, just wait and retry
            logger.info("🎯 Training target not visible, retrying...")
            time.sleep(0.5)
            continue  # Skip target switching
        else:
            # Normal mode: handle target lost (existing logic)
            lost_count += 1
            if lost_count >= max_lost:
                # Switch to next monster...
                # ...existing code...
```

**Add skill tracking** (in attack function):

```python
# In attack_monster() or wherever skills are cast:
def track_skill_execution(skill_name, success, app_root=None):
    """Track skill execution for training mode stats."""
    if not hasattr(track_skill_execution, 'stats'):
        track_skill_execution.stats = {}
    
    stats = track_skill_execution.stats
    
    if skill_name not in stats:
        stats[skill_name] = {
            'cast_count': 0,
            'last_cast_time': None,
            'cooldown_remaining': 0,
            'success_count': 0
        }
    
    s = stats[skill_name]
    s['cast_count'] += 1
    s['last_cast_time'] = time.time()
    
    if success:
        s['success_count'] += 1
    
    # Update UI if app_root exists
    if app_root and hasattr(app_root, 'update_skill_stats'):
        try:
            app_root.update_skill_stats(stats)
        except:
            pass  # UI update failed, continue

# Call after each skill cast:
track_skill_execution(skill_name, success=True, app_root=app_root)
```

---

### Step 6: Add Translations

**File**: `lib/i18n/en.json`

```json
{
  ...existing translations...,
  "training_mode": "Training Mode",
  "training_mode_enable": "Enable Training Mode (Practice Skills)",
  "training_mode_desc": "Practice skill rotation on training dummy without target switching. Perfect for testing timing and cooldowns.",
  "training_mode_active": "Training Mode Active - Attacking training dummy",
  "training_mode_no_dummy": "No training dummy found. Please add a monster with training_mode=true.",
  "skill_stats_header": "Skill Performance Statistics",
  "skill_name": "Skill",
  "cast_count": "Casts",
  "last_cast": "Last Cast",
  "cooldown": "Cooldown",
  "success_rate": "Success %"
}
```

**File**: `lib/i18n/vi.json`

```json
{
  ...existing translations...,
  "training_mode": "Chế Độ Luyện Tập",
  "training_mode_enable": "Bật chế độ luyện tập (Luyện kỹ năng)",
  "training_mode_desc": "Luyện skill rotation trên cọc gỗ mà không chuyển mục tiêu. Hoàn hảo cho việc kiểm tra timing và cooldown.",
  "training_mode_active": "Chế độ luyện tập đang hoạt động",
  "training_mode_no_dummy": "Không tìm thấy cọc gỗ luyện tập",
  "skill_stats_header": "Thống Kê Hiệu Suất Kỹ Năng",
  "skill_name": "Kỹ Năng",
  "cast_count": "Số Lần",
  "last_cast": "Lần Cuối",
  "cooldown": "Hồi Chiêu",
  "success_rate": "Thành Công %"
}
```

---

### Step 7: Update Hunt Config Save

**File**: `app_gui.py`  
**Function**: `on_hunt_start()` (around line 2400)

**Add training mode to config save**:

```python
def on_hunt_start(self):
    # ...existing code...
    
    # Save training mode flag
    self.hunt_cfg['training_mode'] = self.training_mode_var.get()
    
    # ...rest of existing code...
    
    # Save config
    with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
```

---

## 🧪 Testing Checklist

After implementation, test:

1. **Training Mode Toggle**:
   - [ ] Checkbox enables/disables correctly
   - [ ] Monster list filters to training dummies only
   - [ ] Rotation mode disabled when training mode ON
   - [ ] Stats frame shows/hides correctly

2. **Hunt with Training Mode**:
   - [ ] Hunt starts with training dummy
   - [ ] Skills execute normally
   - [ ] Target never switches (even when lost)
   - [ ] No timeout errors

3. **Skill Stats**:
   - [ ] Stats update in real-time
   - [ ] Cast count increments
   - [ ] Last cast time accurate
   - [ ] Success rate calculates correctly
   - [ ] Colors change based on success rate

4. **Edge Cases**:
   - [ ] No training dummy: shows warning
   - [ ] Switch modes while hunting: graceful handling
   - [ ] Multiple training dummies: all shown

---

## 📝 Final Steps

1. **Test thoroughly** with all scenarios
2. **Update README.md** with training mode section
3. **Update INDEX.md** to link to Sprint 22 docs
4. **Take screenshots** for documentation
5. **Create demo video** (optional)

---

## 🎯 Summary

**Completed**: Database schema, load/save functions, documentation  
**Remaining**: UI implementation, hunt logic, translations

**Estimated Time**: 2-3 hours for full implementation

**Files to Modify**:
- `app_gui.py` (~200 lines added)
- `ui/auto_hunt.py` (~50 lines modified)
- `lib/i18n/en.json` (~10 translations)
- `lib/i18n/vi.json` (~10 translations)

Good luck with implementation! 🚀
