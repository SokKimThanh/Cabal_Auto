# Review: UX5.1 Prompt vs Tình Trạng Hiện Tại (2026-09-05)

**Tóm tắt:** UX5.1 và CB4A là **hai tài liệu song song định nghĩa cùng một feature** (Target Card Panel). Cần **hợp nhất thành một session duy nhất** trước khi implement để tránh code trùng lặp. Tình trạng codebase sẵn sàng 85% cho UX5.1 (chỉ thiếu i18n keys + target card panel).

---

## 1. Quan Hệ CB4A ↔ UX5.1: **TRƯỜNG HỢP (b) – HAI BẢN ĐẶC TẢ KHÁC NHAU CHO CÙNG FEATURE**

### Phân Tích

| Khía Cạnh | CB4A | UX5.1 | Kết Luận |
|---|---|---|---|
| **Objective** | Real-time HP tracking + status display | Fallback schema + memory management | **Bổ sung nhau, không thay thế** |
| **Hàm tra cứu quái** | `get_target_monster_info()` (2-tầng: DB→JSON) | `safe_get_monster_data()` (3-tầng: quái→default→placeholder) | ⚠️ **Hai hàm khác nhau, cần hợp nhất** |
| **Fallback ảnh** | DB path → `default_monster.png` | DB path → `default_monster.png` → text "NO IMAGE" | ✅ Tương thích (UX5.1 chi tiết hơn) |
| **Target Card Panel** | Hiển thị: tên, ảnh, máu % thời gian thực | Hiển thị: tên, ảnh, chỉ số cơ bản | ⚠️ **CB4A = UX5.1 + HP bar real-time** |
| **PhotoImage Thread-Safety** | Đọc file BG → Init PhotoImage on Main | Không đề cập explicit | ✅ Giống nhau (CB4A chặt chẽ hơn) |
| **i18n Keys** | Không listed explicit (chỉ ý chung) | `target_card.level`, `target_card.status_*` | ⚠️ **Cần tổng hợp** |
| **Tests** | 6 test cases (valid/missing asset/combat/race/placeholder/no-duplicate) | 3 test cases (fallback schema/zero-asset/memory stability) | ⚠️ **Cần merge test suites** |

### Kết Luận Quan Hệ
- **UX5.1 là shell nền tảng** (tập trung vào reliability: fallback an toàn, memory management)
- **CB4A là enhancement** (tập trung vào feature: real-time HP + status state machine)
- Chúng **định nghĩa cùng một layer** nhưng từ các góc độ khác nhau
- **Ghi chú trong CB4A**: "Nếu UX5.1 đã implement, CB4A chỉ cần thêm HP reader + status machine"
- **Ghi chú trong UX5.1**: "Nếu CB4A đã implement, hàm tra cứu quái phải là cùng một function"

---

## 2. Tình Trạng Codebase: **85% Sẵn Sàng**

### ✅ Đã Có

| Component | File | Status | Note |
|---|---|---|---|
| **hunt_tab.py** | `ui/tabs/hunt_tab.py` | ✅ Tồn tại | Framework cơ bản; chưa có Target Card Panel |
| **i18n system** | `lib/i18n/translations.py` | ✅ Hoạt động | GLOBAL_TRANSLATIONS self-registers; ready for new keys |
| **UI Style** | `lib/ui_style.py` | ✅ Sẵn có | UIStyle constants for colors/fonts |
| **Vision Layer (CB1)** | `lib/vision/target_bar_detector.py` | ✅ Hoạt động | TargetBarDetector.get_hp_percentage() đã implement |
| **Monster Repo Structure** | `lib/features/monsters/` | ✅ Tồn tại | Sẵn sàng cho tra cứu DB |

### ⚠️ Thiếu / Chưa Implement

| Component | Purpose | Severity | Notes |
|---|---|---|---|
| **get_target_monster_info()** (CB4A) | Tra cứu quái 2-tầng DB→JSON | HIGH | Cần implement ở `lib/features/monsters/monster_repo.py` hoặc `lib/vision/target_hp_reader.py` |
| **safe_get_monster_data()** (UX5.1) | Fallback schema an toàn | HIGH | Cần implement; có thể được CB4A thay thế nếu design đúng |
| **Target Card Panel** | Giao diện thẻ quái | HIGH | Chưa implement ở `hunt_tab.py` |
| **target_hp_reader.py** (CB4A) | HP% throttling + smoothing | MEDIUM | Cần create; gọi vào CB1 thay vì duplicate logic |
| **i18n keys** | Dịch Target Card labels | MEDIUM | Chỉ cần thêm ~10 lines vào GLOBAL_TRANSLATIONS |
| **Test suite** | `tests/unit/test_target_card_shell.py` | MEDIUM | Chưa exist; cần merge CB4A + UX5.1 test plans |
| **Memory profiling** | psutil.Process().memory_info() | LOW | Chỉ dùng cho high-load test; psutil có sẵn không? |

### ✅ Dependencies Ready

- **PIL/ImageTk**: Imported in hunt_tab.py (with fallback)
- **TargetBarDetector**: Đã implement ở CB1
- **Tkinter (ttk.Progressbar, Label, Frame)**: Standard library
- **i18n registry pattern**: Self-registration already in place

---

## 3. Dependencies & Blocking Issues

### Block 1: **CB4A ↔ UX5.1 Collision** (MUST RESOLVE FIRST)

**Vấn đề:** Hai tài liệu định nghĩa `get_target_monster_info()` vs `safe_get_monster_data()` với logic chồng chéo nhưng không hoàn toàn giống.

**Khuyến cáo:**
```
Option A (Recommended): Hợp nhất trước implement
  - Chọn UX5.1 làm base (vì chi tiết hơn về fallback 3-tầng)
  - Rename thành get_target_monster_info() (CB4A name cho consistency)
  - Thêm is_placeholder flag (UX5.1 design)
  - Ghi chú trong prompt: "Hàm này được tái sử dụng bởi cả CB4A HP reader lẫn UX5.1 fallback logic"

Option B: Implement tách rồi refactor sau
  - Implement UX5.1 trước (nhẹ nhàng hơn: fallback 3-tầng)
  - Cập nhật CB4A prompt khi implement (sau 1 sprint)
  - Risk: Code duplication, maintenance overhead
```

**Recommendation: Chọn Option A**

---

### Block 2: **CB4A HP Reader Depends on CB1** (Non-blocking)

UX5.1 không cần, nhưng CB4A cần:
- ✅ `TargetBarDetector.get_hp_percentage()` đã implement ở CB1
- ⚠️ Cần verify: `get_hp_percentage()` signature + throttling behavior trước khi CB4A gọi

**Action:** Đọc CB1 implementation để confirm interface.

---

### Block 3: **Thread-Safety for PhotoImage** (Implementation Note)

CB4A nêu rõ: **PhotoImage khởi tạo phải ở Main Thread**

**Tình trạng:** hunt_tab.py chưa implement async image loading. Khi implement UX5.1, cần:
1. Background thread đọc PIL `Image.open(path)` + resize
2. Main thread gọi `ImageTk.PhotoImage(image_obj)` via `schedule_ui_task()`
3. Giữ strong reference: `self._current_target_photo = photo_obj`
4. Clear trước set: `self.clear_target_photo()` → `self.set_target_photo(new_photo)`

**Khuyến cáo:** Áp dụng CB4A pattern (chặt chẽ hơn UX5.1).

---

## 4. i18n Keys: Cần Thêm

**Vị trí:** `lib/i18n/translations.py` (đơn vị: ~10 lines)

```python
GLOBAL_TRANSLATIONS = {
    "en": {
        # ... existing ...
        "target_card.level": "Level",
        "target_card.max_hp": "Max HP",
        "target_card.defense": "Defense",
        "target_card.status_idle": "Ready to hunt",  # Hoặc "Idle"
        "target_card.status_approaching": "🏃 Approaching...",
        "target_card.status_attacking": "⚔️ Attacking...",
        "target_card.unknown_mob": "Unknown Target",
        # (Optional, nếu implement "no image" fallback text)
        # "target_card.no_image": "[ NO IMAGE ]",
    },
    "vi": {
        # ... existing ...
        "target_card.level": "Cấp độ",
        "target_card.max_hp": "Máu tối đa",
        "target_card.defense": "Chỉ số thủ",
        "target_card.status_idle": "Sẵn sàng săn",
        "target_card.status_approaching": "🏃 Đang tiếp cận...",
        "target_card.status_attacking": "⚔️ Đang tấn công...",
        "target_card.unknown_mob": "Mục tiêu lạ",
        # "target_card.no_image": "[ KHÔNG CÓ HÌNH ÁNH ]",
    }
}
```

**Note:** CB4A không listed explicit keys → cần tổng hợp từ cả hai prompt.

---

## 5. Scope Clarification: **Chọn UX5.1 Trước hay Chọn CB4A?**

### Timeline Recommendation

**Scenario 1: Implement UX5.1 trước (Recommended for MVP)**
- **Timeframe:** 20-25 min (per prompt)
- **Scope:** Target Card shell + fallback 3-tầng + memory management
- **Output:** Working panel, zero-asset safe, DPI-aware
- **Then:** Thêm CB4A features (HP reader + status FSM) sau 1 sprint nếu có requirement
- **Advantage:** Sớm có working feature, giảm risk

**Scenario 2: Merge + Implement cùng lúc**
- **Timeframe:** 40-50 min (gấp đôi)
- **Scope:** UX5.1 base + CB4A HP reader + status machine
- **Output:** Full-featured Target Card (panel + real-time HP + states)
- **Advantage:** Hoàn chỉnh hơn, không refactor sau
- **Disadvantage:** Risk lớn hơn, có thể không kịp 25-30 min timebox

### Decision Point

**Khuyến cáo: Chọn Scenario 1 (UX5.1 trước)**
- Sprint này: Implement UX5.1 shell (safely)
- Sprint tới: Enhance với CB4A (HP reader + FSM)
- Lợi: Giữ timebox, de-risk, dễ review

---

## 6. Lộ Trình Implement (Nếu chọn UX5.1 trước)

### Phase 1: Hợp Nhất Prompt (5 min, BEFORE CODE)
- [ ] Merge CB4A + UX5.1 requirements thành một unified prompt
- [ ] Xác định: `get_target_monster_info()` là hàm duy nhất (not two)
- [ ] Đánh dấu CB4A features as "Phase 2 enhancement"

### Phase 2: Code UX5.1 (20 min)
- [ ] Implement `get_target_monster_info()` ở `lib/features/monsters/monster_repo.py`
  - Schema with `is_placeholder` flag
  - 3-tầng fallback: DB → JSON → mặc định
- [ ] Implement Target Card panel ở `ui/tabs/hunt_tab.py`
  - Header bar + status badge
  - Image label with fallback chain (1 Label widget, 3 tầng content)
  - Info column (name, level, hp, defense)
- [ ] Add i18n keys ở `lib/i18n/translations.py`
- [ ] Implement `clear_target_photo()` + `set_target_photo()` (memory management)

### Phase 3: Tests (10 min)
- [ ] `test_target_card_shell.py` (merge CB4A + UX5.1 test plans)
  - Schema fallback
  - Zero-asset safety
  - High-load memory
  - Clear-before-set ordering
  - DPI rendering
- [ ] Run visual check: 100%-200% DPI

### Phase 4: Review + Report (5 min)
- [ ] Verify all gate criteria met (see Session Boundary Gate)
- [ ] Report: PASSED / REVERTED

**Total Estimated Effort: 40-50 min** (thay vì 20-25 min per UX5.1, do cần merge prompts + thêm some CB4A-level rigor)

---

## 7. Checklist: Trước Khi Implement

- [ ] Xác nhận: UX5.1 sẽ implement trước, CB4A sau (hoặc merge thành một?)
- [ ] Xác nhận: `get_target_monster_info()` là hàm duy nhất (not `safe_get_monster_data()`)
- [ ] Xác nhận: PhotoImage thread-safety pattern áp dụng CB4A rigor
- [ ] Xác nhận: Timebox: 40-50 min (thay vì 20-25 min)
- [ ] Xác nhận: Test suite sẽ merge CB4A + UX5.1 test plans
- [ ] Checked: CB1 `get_hp_percentage()` interface (cho CB4A Phase 2)
- [ ] Checked: `lib/data/monsters.json` path + fallback (nếu DB miss)

---

## 8. Vấn Đề Cần Hỏi

1. **CB4A vs UX5.1:** Có muốn merge thành một session hay keep tách?
2. **Timebox:** Có chịu extend sang 40-50 min để hoàn chỉnh không?
3. **CB4A HP reader:** Có muốn implement cùng Phase này hay defer sang sprint tới?
4. **Test priority:** Có muốn high-load memory test (psutil-based) hay chỉ unit tests?

---

## Summary Table: Readiness Assessment

| Criterion | Status | Notes |
|---|---|---|
| **Architecture Clarity** | ⚠️ Needs merge | CB4A + UX5.1 chồng chéo |
| **Codebase Readiness** | ✅ 85% | hunt_tab.py tồn tại, i18n ready |
| **Dependencies** | ✅ Sẵn | Vision, UI, i18n all in place |
| **Documentation** | ✅ Sẵn | Hai prompt đầy đủ (nhưng không đồng bộ) |
| **Tests** | ⚠️ Cần merge | CB4A 6 tests + UX5.1 3 tests → 9 unified |
| **i18n** | ⚠️ Missing keys | Cần thêm 7-10 keys (10 min work) |
| **Risk Level** | 🟡 MEDIUM | Chủ yếu là merge design, implement low-risk |

---

**Report Date:** 2026-09-05  
**Reviewed By:** Copilot Agent  
**Status:** Ready for implementation after prompt merge clarification
