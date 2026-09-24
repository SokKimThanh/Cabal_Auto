# Prompt: Sprint 24 — Vision & Scan Remediation (Batch-based)

## 📖 Context

Đọc trước:
- `00_context_audit_summary.md`
- `docs/sprints/sprint24-scan-vision-hotkey/scan_vision_evaluation_report.md`
- `audit-batch-2.md`
- `07_task_vision_debugger.md`

Báo cáo đánh giá Sprint 24 xác định 3 nhóm nợ kỹ thuật chính:
1. **Monsters**: `RuntimeMonsterQueue` dùng callback nặng, UI dùng `Listbox` gây flicker.
2. **Skills**: `VisionEngine` chưa có `detect_skills_pipeline`, `ScanController` chưa gắn `results["skills"]`.
3. **Combo**: Chưa có luồng riêng ~60 FPS, chưa có `ComboTimingEvent`.

**Trạng thái hiện tại (CRITICAL):**
- `lib/features/hunt/runtime_monster_queue.py` diff: `+2 / -152` → file có thể đã mất gần hết nội dung.
- Tồn tại file tạm: `*.orig`, `patch_*.patch` trong repo.
- Jules báo lỗi VM environment → cần chia batch nhỏ, verify từng bước.

## 🎯 Mục tiêu tổng

Hoàn thiện liên kết Vision & Scan cho Monsters / Skills / Combo, dọn nợ kỹ thuật Sprint 24, đảm bảo:
- UI không flicker, không block main thread.
- EventBus là kênh luân chuyển dữ liệu chính.
- Không xóa canvas khi timeout.
- Tất cả test pass.

## 🧭 Nguyên tắc thực thi (BẮT BUỘC)

1. **Chạy tuần tự từng batch** — không gộp batch.
2. Mỗi batch: **chỉ 1 mục tiêu**, **1–3 file**, **1 lệnh verify**.
3. **Không commit** file `.orig` hoặc `patch_*.patch`.
4. Sau mỗi batch: **DỪNG, báo cáo diff + kết quả test + xác nhận trước khi sang batch tiếp theo**.
5. Nếu VM lỗi hoặc file không rõ trạng thái → **DỪNG ngay, báo user**.
6. Tuân thủ i18n cho mọi text UI (bao gồm "Timeout").

## 🛑 Stop Conditions (toàn cục)

DỪNG và báo user nếu:
- VM environment lỗi khởi tạo.
- File chính bị mất code mà không chắc bản `.orig` là đúng.
- Test fail không rõ nguyên nhân.
- Cần đổi kiến trúc `Toplevel` hoặc `VisionEngine` timeout backend.
- Timeout xảy ra liên tục khiến app treo.

---

## 📦 BATCH 0 — Khôi phục & dọn dẹp (P0, BẮT BUỘC TRƯỚC)

### Mục tiêu
Đưa repo về trạng thái sạch, khôi phục file hỏng.

### Files
- `lib/features/hunt/runtime_monster_queue.py`
- `lib/features/hunt/runtime_monster_queue.py.orig`
- `ui/panels/monster_target_panel.py`
- `ui/panels/monster_target_panel.py.orig`
- `patch_scene_monster_queue.patch`
- `patch_ui_monster_target_panel.patch`
- `patch_ui_monster_target_panel2.patch`
- `patch_ui_monster_target_panel3.patch`

### Việc cần làm
1. `git status` + `git diff --stat` để liệt kê file thay đổi.
2. So sánh `runtime_monster_queue.py` với `.orig`:
   - Nếu file chính < 50% nội dung `.orig` → **restore từ `.orig`**.
   - Nếu file chính là bản đúng (đã sửa có chủ đích) → giữ, xóa `.orig`.
3. Tương tự với `monster_target_panel.py`.
4. Xóa tất cả file `*.orig` và `patch_*.patch` khỏi working tree.
5. Chạy verify.

### Verify
```bash
grep -n "class RuntimeMonsterQueue" lib/features/hunt/runtime_monster_queue.py
grep -n "def __init__" lib/features/hunt/runtime_monster_queue.py
pytest tests/ui/panels/test_monster_target_panel_detected.py -v
```

### Output
- Diff trước/sau từng file.
- Xác nhận đã xóa `.orig` và `patch_*.patch`.
- Kết quả test.
- Trạng thái repo (sạch/chưa sạch).

### Stop
Nếu không chắc file nào là bản đúng → DỪNG, báo user danh sách file nghi vấn.

---

## 📦 BATCH 1 — Monster Event qua EventBus (P1)

### Mục tiêu
`RuntimeMonsterQueue` publish `SceneMonstersDetectedEvent` qua EventBus thay vì callback nặng.

### Files
- `lib/events/event_bus.py` (chỉ đọc, xác nhận event tồn tại)
- `lib/features/hunt/runtime_monster_queue.py` (sửa)
- `tests/features/hunt/test_runtime_monster_queue.py` (thêm/sửa test)

### Dependency check
```bash
grep -rn "SceneMonstersDetectedEvent" lib/events/event_bus.py
```

Nếu chưa có → DỪNG, yêu cầu tách batch tạo event trước.

### Requirements
1. Snapshot gửi qua EventBus chỉ gồm: `id`, `name`, `x`, `y`, `confidence`, `distance`, `timestamp`.
2. KHÔNG đẩy object nặng (monster instance, frame, image) vào event.
3. Giữ IOU dedup và sort theo confidence.
4. Publish theo chu kỳ ~5 FPS (0.2s), không block main thread.

### Verify
```bash
grep -n "SceneMonstersDetectedEvent" lib/features/hunt/runtime_monster_queue.py
pytest tests/features/hunt/test_runtime_monster_queue.py -v
```

### Acceptance Criteria
- [ ] AC1: Event publish có payload nhẹ (chỉ primitive types).
- [ ] AC2: Test mock EventBus pass.
- [ ] AC3: Không có callback nặng trực tiếp lên UI.
- [ ] AC4: IOU dedup vẫn hoạt động.

### Output
1. Diff logic (≤ 30 dòng).
2. Kết quả test.
3. Xác nhận payload schema.

---

## 📦 BATCH 2 — Monster UI dùng Treeview (P1)

### Mục tiêu
`monster_target_panel.py` chuyển `tk.Listbox` → `ttk.Treeview`, update từng dòng, chống flicker.

### Files
- `ui/panels/monster_target_panel.py`
- `tests/ui/panels/test_monster_target_panel_detected.py`

### Requirements
1. `_update_detected_monsters_list` dùng `ttk.Treeview`.
2. Cập nhật qua `tree.item(iid, values=...)`, KHÔNG `delete("all")` mỗi lần refresh.
3. Chỉ thêm/xóa row khi tập monster ID thay đổi.
4. Subscribe `SceneMonstersDetectedEvent` từ Batch 1.
5. Cột tối thiểu: Name, HP (nếu có), Distance, Confidence.
6. Text UI theo i18n.

### Verify
```bash
grep -n "Treeview" ui/panels/monster_target_panel.py
grep -n "delete(\"all\")" ui/panels/monster_target_panel.py
pytest tests/ui/panels/test_monster_target_panel_detected.py -v
```

Kỳ vọng: `delete("all")` KHÔNG xuất hiện trong `_update_detected_monsters_list`.

### Manual test
Giả lập event liên tục 5 FPS trong 30s → UI không giật, không mất dòng.

### Acceptance Criteria
- [ ] AC1: Dùng `ttk.Treeview`.
- [ ] AC2: Không `delete("all")` trong refresh loop.
- [ ] AC3: Test pass.
- [ ] AC4: i18n text đúng.

### Output
1. Diff logic (≤ 40 dòng).
2. Kết quả test.
3. Screenshot/manual note nếu có.

---

## 📦 BATCH 3 — Skills VisionEngine (P2)

### Mục tiêu
Thêm `detect_skills_pipeline(frame)` vào `VisionEngine`.

### Files
- `lib/vision/vision_engine.py`
- `tests/lib/vision/test_vision_engine_skills.py` (mới)

### Requirements
1. Crop ROI thanh kỹ năng/cooldown (cấu hình qua config, không hardcode).
2. Nhận diện skill ready vs cooldown bằng `cv2.matchTemplate` hoặc grayscale threshold.
3. Trả về `List[int]` các skill index ready (VD: `[1, 2, 4]`).
4. Không block, không dùng `time.sleep`.

### Verify
```bash
pytest tests/lib/vision/test_vision_engine_skills.py -v
```

### Acceptance Criteria
- [ ] AC1: Method tồn tại với signature `detect_skills_pipeline(self, frame) -> List[int]`.
- [ ] AC2: Test với ảnh mẫu ready/cooldown pass.
- [ ] AC3: Không hardcode tọa độ ROI.

### Output
1. Diff logic (≤ 30 dòng).
2. Kết quả test.

---

## 📦 BATCH 4 — Skills ScanController (P2)

### Mục tiêu
Gắn `results["skills"]` vào `run_scan()`.

### Files
- `lib/features/hunt/scan_controller.py`
- `tests/features/hunt/test_scan_controller.py`

### Dependency
Batch 3 phải hoàn thành.

### Requirements
1. Trong `run_scan()`, gọi `detect_skills_pipeline(frame)` sau khi quét monster.
2. Gán `results["skills"] = <list>`.
3. Không phá logic monster scan hiện có.
4. `show_results(results)` nhận và hiển thị được `results["skills"]`.

### Verify
```bash
grep -n "detect_skills_pipeline\|results\[\"skills\"\]" lib/features/hunt/scan_controller.py
pytest tests/features/hunt/test_scan_controller.py -v
```

### Acceptance Criteria
- [ ] AC1: `run_scan()` gọi pipeline skills.
- [ ] AC2: Payload có key `skills`.
- [ ] AC3: Test pass, monster scan không regression.

### Output
1. Diff logic (≤ 20 dòng).
2. Kết quả test.

---

## 📦 BATCH 5 — ComboTimingEvent (P2)

### Mục tiêu
Khai báo `ComboTimingEvent` trong `event_bus.py`.

### Files
- `lib/events/event_bus.py`
- `tests/lib/events/test_event_bus_combo.py` (mới)

### Requirements
1. Class `ComboTimingEvent` với field tối thiểu: `status` (VD `"PERFECT"`, `"GOOD"`, `"MISS"`), `timestamp`.
2. Publish/subscribe hoạt động.

### Verify
```bash
grep -n "class ComboTimingEvent" lib/events/event_bus.py
pytest tests/lib/events/test_event_bus_combo.py -v
```

### Output
1. Diff logic (≤ 15 dòng).
2. Kết quả test.

---

## 📦 BATCH 6 — ComboVisionThread (P2)

### Mục tiêu
Luồng riêng ~60 FPS nhận diện combo, bắn `ComboTimingEvent`.

### Files
- `lib/features/combo/combo_timing_detector.py` (mới)
- `tests/features/combo/test_combo_timing_detector.py` (mới)

### Dependency
Batch 5 phải hoàn thành.

### Requirements
1. `ComboVisionThread` là worker thread độc lập, không chung với Monster queue.
2. Chỉ capture vùng nhỏ (~200x20 px) tại ROI thanh combo.
3. Dò pixel/màu sáng (không dùng template matching nặng).
4. Target ~60 FPS (không sleep cứng; dùng capture timing).
5. Khi đạt Perfect → `EventBus.trigger(ComboTimingEvent(status="PERFECT"))`.
6. Có cơ chế stop/cleanup an toàn.

### Verify
```bash
grep -n "class ComboVisionThread" lib/features/combo/combo_timing_detector.py
pytest tests/features/combo/test_combo_timing_detector.py -v
```

### Stop
Nếu capture API không thread-safe → DỪNG, báo user.

### Acceptance Criteria
- [ ] AC1: Thread riêng, không block main.
- [ ] AC2: Capture ROI nhỏ, không full frame.
- [ ] AC3: Bắn event khi Perfect.
- [ ] AC4: Có stop() an toàn.
- [ ] AC5: Test mock pass.

### Output
1. Diff logic (≤ 50 dòng).
2. Kết quả test.
3. FPS đo được (mock hoặc manual).

---

## 📦 BATCH 7 — Vision Fallback fix (P2)

### Mục tiêu
`VisionSnapshotDebugger` không xóa canvas khi timeout.

### Files
- `ui/components/vision_snapshot_debugger.py`
- `tests/ui/components/test_vision_snapshot_debugger.py`

### Requirements
1. Trong nhánh `frame is None`, **BỎ** `self.canvas.delete("all")`.
2. Giữ nguyên ảnh cũ trên canvas.
3. Overlay text "Timeout/No Frame" theo i18n.
4. Không crash, không rò rỉ bộ nhớ.

### Verify
```bash
grep -A 5 -n "frame is None" ui/components/vision_snapshot_debugger.py
pytest tests/ui/components/test_vision_snapshot_debugger.py -v
```

Kỳ vọng: nhánh `frame is None` KHÔNG chứa `delete("all")`.

### Manual
Mở debugger, trigger timeout từ Vision Engine → canvas giữ ảnh cũ.

### Acceptance Criteria
- [ ] AC1: Không `delete("all")` trong nhánh `frame is None`.
- [ ] AC2: Ảnh cũ được giữ.
- [ ] AC3: Test pass.
- [ ] AC4: i18n cho text "Timeout".

### Output
1. Diff logic (≤ 10 dòng).
2. Kết quả test.
3. Manual note.

---

## 📦 BATCH 8 — Regression & Docs (P3)

### Mục tiêu
Chạy test tổng, cập nhật docs, dọn nợ còn lại.

### Files
- `tests/` (chạy toàn bộ liên quan)
- `docs/sprints/sprint24-scan-vision-hotkey/scan_vision_evaluation_report.md`

### Việc cần làm
1. Chạy:
   ```bash
   pytest tests/features/hunt/ tests/lib/vision/ tests/lib/events/ \
          tests/features/combo/ tests/ui/panels/ tests/ui/components/ -v
   ```
2. Kiểm tra EventBus race condition (subscribe/unsubscribe).
3. Manual test:
   - UI Monster không lag.
   - Timeout giữ ảnh cũ.
   - Combo event bắn đúng khi Perfect.
4. Cập nhật report với kết quả thực tế.
5. Ghi lại nợ kỹ thuật còn lại (nếu có).

### Output
1. Tổng kết pass/fail.
2. Danh sách nợ còn lại.
3. Diff docs (≤ 30 dòng).

---

## 📤 Output Format (mỗi batch)

```
### Batch N — <tên>
1. Files changed: <list>
2. Diff logic: <≤ 50 dòng>
3. Test result: <command + output tóm tắt>
4. Blocker: <nếu có>
5. Trạng thái: DONE / BLOCKED / NEEDS_USER
```

---

## 🔗 Reference
- `00_context_audit_summary.md`
- `audit-batch-2.md`
- `07_task_vision_debugger.md`
- `docs/sprints/sprint24-scan-vision-hotkey/scan_vision_evaluation_report.md`