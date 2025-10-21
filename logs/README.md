# Hunt Logs Directory

Thư mục này chứa các log files được tạo tự động khi chạy hunt.

## File Logs

### `hunt_structured.jsonl`
**Format:** JSON Lines (mỗi dòng là 1 JSON object độc lập)
**Mục đích:** Log structured events với timestamp chính xác

**Events được log:**
- `HUNT_START`: Bắt đầu hunt session
- `HUNT_STOP`: Kết thúc hunt session
- `STATE_CHANGE`: Thay đổi trạng thái (search ↔ attack)
- `MATCH`: Tìm thấy target (template matching)
- `LOST`: Mất target
- `ERROR`: Lỗi xảy ra trong hunt loop

**Example entries:**
```jsonl
{"event": "HUNT_START", "config": {"window_title": "CABAL", "target_key": "z", "attack_keys": ["1", "2", "3", "4"]}, "timestamp": "2025-10-21T15:21:25.862733"}
{"event": "MATCH", "template": "Coc Go 5", "monster": "", "box": {"left": 1022, "top": 387, "width": 167, "height": 264}, "confidence": 0.92, "timestamp": "2025-10-21T15:22:03.081870"}
{"event": "HUNT_STOP", "reason": "manual_stop", "duration_sec": 37.37, "timestamp": "2025-10-21T15:22:03.081870"}
```

### `hunt.log` (Legacy)
**Format:** Plain text với timestamps
**Mục đích:** Human-readable log cho debugging

## Auto-Rotation

Logs tự động rotate khi đạt kích thước lớn:
- `hunt_structured.jsonl` → `hunt_structured.jsonl.1`, `.2`, etc.
- Giữ tối đa 5 backup files
- Mỗi file tối đa 10MB

## Gitignore

⚠️ **Tất cả log files trong thư mục này bị gitignore** (không được commit lên Git)

**Lý do:**
- Log files chứa dữ liệu runtime cá nhân
- Kích thước lớn không phù hợp với Git
- Mỗi user có log riêng

**Được track:**
- ✅ `README.md` (file này)
- ✅ `hunt_structured.example.jsonl` (example file)
- ✅ `.gitkeep` (giữ thư mục trong Git)

## Analysis

Để phân tích logs, sử dụng:

```python
import json

# Read JSONL file
with open('logs/hunt_structured.jsonl', 'r') as f:
    events = [json.loads(line) for line in f]

# Filter by event type
matches = [e for e in events if e['event'] == 'MATCH']
errors = [e for e in events if e['event'] == 'ERROR']

# Calculate statistics
total_hunts = len([e for e in events if e['event'] == 'HUNT_START'])
avg_duration = sum(e['duration_sec'] for e in events if e['event'] == 'HUNT_STOP') / total_hunts
```

## Troubleshooting

### Log file quá lớn
- Xóa file cũ: `del logs\hunt_structured.jsonl.1`
- Hoặc archive: `move logs\*.jsonl.* archive\`

### Không thấy logs
- Kiểm tra quyền ghi file trong thư mục `logs/`
- Xem console output để debug logger initialization

### Parse errors
- JSONL file có thể bị corrupted nếu app crash
- Mỗi dòng phải là valid JSON object
- Dùng `jq` tool để validate: `type logs\hunt_structured.jsonl | jq .`

## Best Practices

1. **Đừng commit log files lên Git** - Đã được gitignore tự động
2. **Backup định kỳ** - Logs có thể hữu ích cho debugging
3. **Clean up cũ** - Xóa logs >1 tháng để tiết kiệm dung lượng
4. **Analyze trends** - Dùng logs để tối ưu hunt strategy

---

**Note:** File này được track trong Git để giúp users hiểu về log system. Các log files thật sự (.jsonl, .log) sẽ KHÔNG được commit.
