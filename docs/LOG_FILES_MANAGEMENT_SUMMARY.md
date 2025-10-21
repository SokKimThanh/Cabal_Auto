# Log Files Management - Summary

## Vấn đề ban đầu
File `logs/hunt_structured.jsonl` bị gitignore nên không được track trong Git, gây bất tiện khi muốn xem lịch sử hoặc chia sẻ example logs.

## Giải pháp đã triển khai

### 1. **.gitignore Configuration**
Updated `.gitignore` để:
- ✅ Giữ tất cả log files bị ignore (data cá nhân, kích thước lớn)
- ✅ Cho phép track documentation files với whitelist pattern
- ✅ Maintain best practices cho Git repo

**Changes:**
```diff
 # Hunt logs (runtime generated)
 # Prefer ignoring entire logs directory
 logs/
 logs/**/*.log
 logs/**/*.jsonl
 logs/**/*.txt
 
+# BUT allow example/template files to be tracked
+!logs/.gitkeep
+!logs/README.md
+!logs/hunt_structured.example.jsonl
+
 # Legacy single-file log patterns (kept for safety)
 hunt.log
 hunt.log.*
 hunt_structured.jsonl
 hunt_structured.jsonl.*
```

### 2. **Documentation Files Created**

#### `logs/README.md`
- ✅ **Tracked in Git** (whitelist pattern `!logs/README.md`)
- 📝 Comprehensive documentation về log system
- 📊 Event types và format specification
- 🔧 Analysis examples và troubleshooting guide
- 💡 Best practices cho log management

**Content includes:**
- Log file formats (JSONL vs plain text)
- Event types: `HUNT_START`, `MATCH`, `LOST`, `ERROR`, etc.
- Auto-rotation behavior (10MB limit, 5 backups)
- Python code examples for log analysis
- Troubleshooting common issues

#### `logs/hunt_structured.example.jsonl`
- ✅ **Tracked in Git** (whitelist pattern `!logs/hunt_structured.example.jsonl`)
- 📋 Example log entries with realistic data
- 🎯 Shows complete hunt session lifecycle
- 📖 Reference for log format understanding

**Sample events:**
```jsonl
{"event": "HUNT_START", "config": {...}, "timestamp": "..."}
{"event": "STATE_CHANGE", "old_state": "search", "new_state": "attack", ...}
{"event": "MATCH", "template": "Coc Go 5", "confidence": 0.92, ...}
{"event": "LOST", "duration": 13.84, ...}
{"event": "HUNT_STOP", "reason": "manual_stop", "duration_sec": 37.37}
```

#### `logs/.gitkeep`
- ✅ **Tracked in Git** (whitelist pattern `!logs/.gitkeep`)
- 📁 Ensures `logs/` directory exists in Git
- 💬 Contains explanation comment about purpose

### 3. **Git Operations Performed**

```bash
# Remove actual log files from Git tracking
git rm --cached logs/hunt.log logs/hunt_structured.jsonl

# Force add documentation files (bypass gitignore)
git add -f logs/.gitkeep logs/README.md logs/hunt_structured.example.jsonl
```

**Result:**
```
 M .gitignore                            # Updated whitelist patterns
 A logs/.gitkeep                         # New: Directory keeper
 A logs/README.md                        # New: Documentation
 A logs/hunt_structured.example.jsonl   # New: Example file
 D logs/hunt.log                         # Removed from tracking
 D logs/hunt_structured.jsonl           # Removed from tracking
```

## Cách hoạt động

### Runtime Behavior (Không thay đổi)
App vẫn tạo log files như bình thường:
```
logs/
├── hunt.log                      # ❌ Gitignored (runtime data)
├── hunt_structured.jsonl         # ❌ Gitignored (runtime data)
├── hunt_structured.jsonl.1       # ❌ Gitignored (backup)
├── hunt_structured.jsonl.2       # ❌ Gitignored (backup)
├── .gitkeep                      # ✅ Tracked (documentation)
├── README.md                     # ✅ Tracked (documentation)
└── hunt_structured.example.jsonl # ✅ Tracked (example)
```

### Git Tracking
- **Runtime logs** (`*.log`, `*.jsonl`): Bị ignore, không commit
- **Documentation files**: Được track, commit được
- **Directory structure**: Maintained qua `.gitkeep`

### Lợi ích
1. ✅ **Clean Git history**: Không có log data cá nhân
2. ✅ **Self-documenting**: README giải thích log system
3. ✅ **Example available**: Users có reference format
4. ✅ **Directory persistent**: `logs/` tồn tại khi clone repo
5. ✅ **No workflow changes**: App behavior không đổi

## Verification

### Check gitignore rules:
```bash
git check-ignore -v logs/hunt_structured.jsonl
# Output: .gitignore:212:logs/    logs/hunt_structured.jsonl
```

### Check tracked files:
```bash
git ls-files logs/
# Output:
# logs/.gitkeep
# logs/README.md
# logs/hunt_structured.example.jsonl
```

### Verify whitelist works:
```bash
git status --short
# Documentation files should show as staged/modified
# Runtime log files should NOT appear (ignored)
```

## Best Practices (Unchanged)

### For Users:
1. **Đừng commit log files** - Đã tự động ignore
2. **Xem README.md** - Để hiểu log format
3. **Reference example.jsonl** - Khi cần parse logs
4. **Clean up định kỳ** - Delete old logs >1 tháng

### For Developers:
1. **Document new event types** - Update README.md
2. **Update example file** - Khi thay đổi format
3. **Test gitignore** - Sau khi modify patterns
4. **Keep docs current** - README phải sync với code

## Troubleshooting

### "Log files vẫn xuất hiện trong git status"
**Cause:** Files đã được track trước khi gitignore  
**Fix:** 
```bash
git rm --cached logs/*.log logs/*.jsonl
git commit -m "Remove log files from tracking"
```

### "Không thể add documentation files"
**Cause:** `logs/` directory pattern chặn tất cả  
**Fix:** Dùng `-f` flag:
```bash
git add -f logs/README.md logs/hunt_structured.example.jsonl
```

### "README.md không được track"
**Cause:** Thiếu whitelist pattern `!logs/README.md`  
**Fix:** Add vào `.gitignore` sau dòng `logs/`

## Future Improvements

### Potential Enhancements:
1. **Log Viewer UI**: Built-in log browser trong app
2. **Export/Import**: Export logs to CSV/Excel
3. **Statistics Dashboard**: Real-time hunt performance metrics
4. **Cloud Backup**: Optional upload logs to cloud storage
5. **Compression**: Auto-compress old logs (gzip)

### Log Format Evolution:
- Add more event types (SKILL_CAST, HP_CHECK, etc.)
- Include performance metrics (FPS, latency)
- Support multiple monster tracking
- Add skill rotation timing data

---

**Status:** ✅ Completed  
**Files Changed:** 4 files  
**Git Impact:** Clean (no personal data tracked)  
**Documentation:** Comprehensive  
**Backward Compatible:** Yes (no app changes needed)
