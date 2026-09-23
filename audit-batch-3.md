### Task 4: Cấu trúc lại `SkillPanel` & Cải tiến Nút Bật/Tắt Combo

**Trạng thái tổng:** 🟡 PARTIAL
**Completion:** 83.3% (10/12 items) |  **Risk:** HIGH

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Sửa file `skill_panel.py` | ✅ | `ui/panels/skill_panel.py` | Có sửa đổi |
| 2 | Xóa các hàm `_build_combo_section` và `_build_buff_section` | ✅ | `ui/panels/skill_panel.py` | Đã xoá toàn bộ |
| 3 | Chèn `ComboRhythmBar` lên trên cùng | ✅ | `ui/panels/skill_panel.py:65` | `ComboRhythmBar(self.content_frame)` |
| 4 | Chèn 2 `SkillTimelineStrip` (Combo & Buff) | ✅ | `ui/panels/skill_panel.py:89, 102` | Khởi tạo `self.attack_timeline` và `self.buff_timeline` |
| 5 | Đổi Checkbox thành Nút Toggle | ✅ | `ui/panels/skill_panel.py:115` | Có `self.btn_toggle_combo` dạng button |
| 6 | BẮT BUỘC giữ nguyên biến `self.widgets["auto_combo_var"]` | ✅ | `ui/panels/skill_panel.py:112` | `self.widgets["auto_combo_var"] = tk.BooleanVar(value=True)` |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Truyền Event đúng xuống luồng/Controller | ❌ | `ui/panels/skill_panel.py:129` | **FAIL**: Bypass Controller, ghi đè trực tiếp `app_state.hunt_cfg`. KHÔNG gọi `save_hunt_config()`. Đây là Bug nghiêm trọng về State Persistence và Tight Coupling (D1). |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Test toggle button đổi state | ✅ | `tests/ui/panels/test_skill_panel.py` | Chạy pass (Test mock cũng vô tình mock Bypass config) |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | Sửa Lỗi Binding Vô Danh (Update `hunt_cfg`) | ❌ | `ui/panels/skill_panel.py:129` | **FAIL**: Vẫn vi phạm D1 (không qua Controller). |
| 2 | i18n Hardcode cho "Bật Auto Combo" | ✅ | `tests/ui/panels/test_skill_panel.py:37` | Đã dùng i18n `cget("text") == "translated_skill_panel.combo_start"`. |

**Đánh giá Cascade Integration (Bug Task 1 ↔ Task 4)**
- ❌ **FAILED:** (Tính vào Completion) Mặc dù `SkillTimelineStrip` được tạo, nhưng **hoàn toàn không có dòng code nào gọi `self.controller.get_combo_sequence()` hoặc `get_buff_sequence()`** (đã xây dựng ở Task 1) để truyền vào `SkillTimelineStrip`.
- Hậu quả: Strip được render rỗng. Đây là lỗi Integration nghiêm trọng làm vỡ chức năng chính của panel.

**Đề xuất hành động**
1. Lỗi D1 bypass config `app_state.hunt_cfg["combo"]["enabled"] = new_state` cần được fix, chuyển qua Controller thay vì chỉnh sửa dict trực tiếp.
2. Tích hợp API giữa `SkillPanelController` và `SkillTimelineStrip` đang bị rỗng. Cần thêm luồng nạp dữ liệu.

---

### Task 5: Áp dụng Animation & Font Mono cho Target Status và Stats

**Trạng thái tổng:** 🟡 PARTIAL
**Completion:** 81.8% (9/11 items) |  **Risk:** HIGH

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Cập nhật Text HP tức thời | ✅ | `ui/panels/target_status_panel.py:270` | Text HP update ngay lập tức qua `self.hp_val_lbl.config(...)` |
| 2 | Tweening Thanh Bar HP bằng `UIAnimationManager` | ✅ | `ui/panels/target_status_panel.py:284` | Có gọi `self.animation_manager.register_tween` |
| 3 | Label font dùng mono (TargetStatusPanel) | ✅ | `ui/panels/target_status_panel.py:90, 107` | Dùng `self.font_mono` |
| 4 | Giữ cấu trúc `Treeview` ở `SkillStatsPanel` | ✅ | `ui/panels/skill_stats_panel.py:84` | Dùng `ttk.Treeview` |
| 5 | Tần suất refresh 1s, max 50 items (`SkillStatsPanel`) | ✅ | `ui/panels/skill_stats_panel.py:31, 39` | Code có `now - self._last_update_time < 1.0` và `[:50]` |
| 6 | Cột `success_rate` hiện `%` bằng font mono | ✅ | `ui/panels/skill_stats_panel.py:46, 120` | Dùng `f"{success_rate:5.1f}%"` và style `"Mono.Treeview"` |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Queue Tweening HP | ✅ | Dựa vào `UIAnimationManager` Task 0 | Animation Manager đã làm tốt việc Override (Cancel cái cũ). |
| 2 | Crash `TclError` (Kiểm tra `winfo_exists()`) | ✅ | `ui/panels/target_status_panel.py:275` | `update_hp_canvas` có dòng `if self.hp_bar_canvas.winfo_exists():` |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Helpers/Animation tests | ❌ | N/A | Hoàn toàn không có file test `test_target_status_panel.py` trong repo. Việc thiếu Test cho UI phức tạp này là một Red Flag. |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | Xóa gọi `self.after` ngoài `TargetStatusPanel` | ✅ | `ui/panels/target_status_panel.py` | Không tồn tại `self.after` để animate (Cải thiện D4). |
| 2 | D6 - i18n Hardcode | ❌ | `ui/panels/target_status_panel.py:26` | (Tính vào Completion) Hardcode `text="📊 Target Status"` thay vì dùng key ngôn ngữ `self.app._t()`. Tương tự với `SkillStatsPanel`. |

**Đánh giá Legacy code / Dead code (Code Smell)**
- `ui/panels/target_status_panel.py:40, 112`: Còn chứa method `_setup_legacy_wrappers` dùng monkey-patch. Tuy nhiên grep trong `tests/` không thấy phụ thuộc trực tiếp vào các hàm legacy này, nên xoá để giảm code smell.

**Đề xuất hành động**
1. Panel phức tạp như TargetStatus mà thiếu hoàn toàn Unit Tests. Cần viết test bổ sung.
2. D6 bị vi phạm trắng trợn trên Panel Titles, cần quy hoạch lại.
3. Code smell `_setup_legacy_wrappers` cần được xoá bỏ.