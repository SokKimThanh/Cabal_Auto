### Task 0: Xây dựng nền tảng `UIAnimationManager`

**Trạng thái tổng:** ✅ DONE
**Completion:** 100%  |  **Risk:** LOW

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Tạo class `UIAnimationManager` (Singleton) | ✅ | `lib/ui/animation_manager.py:5` | Singleton thực thi qua `__new__` |
| 2 | Duy trì 1 vòng lặp `.after(16)` duy nhất | ✅ | `lib/ui/animation_manager.py:114` | Chỉ có 1 loop `self._run_loop` dùng `after(16, self._run_loop)` trên valid widget |
| 3 | API `register_tween` với cơ chế Override | ✅ | `lib/ui/animation_manager.py:25` | Nếu `target_id` tồn tại, lấy `actual_start = self.tweens[target_id]['current_val']` |
| 4 | Cung cấp API `cancel_tween(target_id)` | ✅ | `lib/ui/animation_manager.py:56` | Có hàm `cancel_tween` xoá khỏi queue |
| 5 | Kiểm tra `widget.winfo_exists()` | ✅ | `lib/ui/animation_manager.py:70` | Bắt lỗi `tk.TclError` và check `winfo_exists()` xoá tween nếu widget bị destroy |

**Risks & Pitfalls**
(Không có trong spec)

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Gọi 2 lần `register_tween` (Override) | ✅ | `tests/unit/ui/test_animation_manager.py:16` | Chạy pass (4/4 tests passed) |
| 2 | Destroy giả lập widget, loop không crash | ✅ | `tests/unit/ui/test_animation_manager.py:41` | Chạy pass |

**Technical Debt Paydown**
*(File 00 nói xoá self.after rải rác - check D4 toàn bộ dự án)*
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | Phân mảnh Tkinter Event Loop | ❌ | `ui/components/image_library_component.py:150` và hàng chục file khác trong `ui/` vẫn dùng `self.after` |

**Legacy / Dead code còn sót**
- Không có yêu cầu xoá dead code cụ thể trong spec Task 0.
- Tuy nhiên hàng loạt `self.after` rải rác chưa được quy hoạch lại.

**Đề xuất hành động**
1. Task 0 đã hoàn thành xuất sắc yêu cầu nền tảng, code đúng chuẩn Singleton và chống TclError rất tốt. Tuy nhiên nợ kỹ thuật (D4) vẫn chưa được giải quyết triệt để trên toàn bộ dự án (có thể do các task khác chưa migrate).

---

### Task 1: Nâng cấp Data Layer cho Skill Panel

**Trạng thái tổng:** ✅ DONE
**Completion:** 100%  |  **Risk:** LOW

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Chỉnh sửa `ui/controllers/skill_panel_controller.py` | ✅ | `ui/controllers/skill_panel_controller.py:1` | Đã cập nhật |
| 2 | Tạo method `get_combo_sequence` và `get_buff_sequence` | ✅ | `ui/controllers/skill_panel_controller.py:146`, `158` | Đã tồn tại |
| 3 | Lưu trữ tương thích cấu trúc mảng (`hunt_config.json`) | ✅ | `ui/controllers/skill_panel_controller.py:150` | Lấy list trực tiếp từ `hunt_cfg.get("skill_slots", [])` và `buff_slots` |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Tương thích ngược / Data binding | ✅ | `ui/controllers/skill_panel_controller.py:150` | Trả về list Python thông thường. (Cần kiểm tra Task 4 xem UI tích hợp có crash không) |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Trả về chuỗi sequence mảng | ✅ | `tests/ui/controllers/test_skill_panel_controller.py:19` | Test pass sau khi fix dependencies |
| 2 | Sequence mutation (thêm/xóa) | ✅ | `tests/ui/controllers/test_skill_panel_controller.py:35` | Test pass |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | Xoá decoupling UI ↔ Config (Không gọi `hunt_cfg.get` từ UI) | ❌ | `ui/panels/monster_target_panel.py:57`, `ui/tabs/hunt_tab.py:70`, ... | Rất nhiều file trong `ui/` vẫn gọi trực tiếp `hunt_cfg.get`. |

**Đề xuất hành động**
1. Data Layer hoạt động tốt và test pass. Tuy nhiên, rủi ro liên quan tới Tech Debt (D1) chưa được giải quyết triệt để. Dev mới chỉ đổi cấu trúc lấy dữ liệu trong Controller, nhưng chưa dọn dẹp các lời gọi `hunt_cfg.get` trực tiếp từ các file View (như `hunt_tab.py`, `setup_tab.py`).

---

### Task 2: Phát triển Component `ComboRhythmBar`

**Trạng thái tổng:** ✅ DONE
**Completion:** 100%  |  **Risk:** LOW

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | File `combo_rhythm_bar.py` kế thừa Canvas/Frame | ✅ | `ui/components/combo_rhythm_bar.py:6` | Kế thừa `ttk.Frame` |
| 2 | Vẽ vùng "Sweet Spot" 0.78 và nút Toggle | ✅ | `ui/components/combo_rhythm_bar.py:7`, `34` | Dùng `SWEET_SPOT_RATIO = 0.78`, nút Checkbutton hiển thị/ẩn thanh bar |
| 3 | Phương thức `trigger_hit()` nháy màu 200ms | ✅ | `ui/components/combo_rhythm_bar.py:88` | Gọi `self.animation_manager.register_tween` duration 200ms |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Debounce Logic (200ms) nút Toggle / Trigger | ✅ | `ui/components/combo_rhythm_bar.py:57`, `92` | Chống spam bằng `if (current_time - self.last_trigger_time) * 1000 < self.DEBOUNCE_MS:` |
| 2 | Không dùng `time.sleep`, gọi UIAnimationManager | ✅ | `ui/components/combo_rhythm_bar.py:101` | Tween fade color đăng ký qua Animation Manager |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Headless initialization & trigger_hit | ✅ | `tests/unit/ui/components/test_combo_rhythm_bar.py:28` | Pass 5/5 tests |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | Gom nhóm Animation Loop (ko self.after) | ✅ | `ui/components/combo_rhythm_bar.py:101` | Dùng đúng `UIAnimationManager` để chạy hiệu ứng thay vì `after` |

**Đề xuất hành động**
1. Task 2 hoàn thành chuẩn xác theo spec. Không có vấn đề.