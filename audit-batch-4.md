### Task 8: Tích hợp `Hunt Area Manager` và Cấu trúc lại HUD System Rois

**Trạng thái tổng:** ✅ DONE / 🟡 PARTIAL (Lỗi Migration test case & i18n Hardcode)
**Completion:** 75%  |  **Risk:** MEDIUM

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Thêm nút "Set Hunt Area" ở Hunt Tab gọi RegionSelector | ✅ | `ui/panels/monster_target_panel.py:107-118` | Có hàm `_on_draw_hunt_area` gọi `CaptureHelper.start_region_selection`. |
| 2 | Lưu tọa độ vào `hunt_cfg["rois"]["hunt_area"]` | ✅ | `ui/panels/monster_target_panel.py:113` | Cập nhật `hunt_cfg["rois"]["hunt_area"] = list(region)`. |
| 3 | Xây dựng danh sách "System ROI Manager" ở Setup Tab | ✅ | `ui/tabs/setup_tab.py:346` | Có hàm `_build_system_roi_content`. |
| 4 | Cho phép Vẽ lại và lưu `combo_bar, self_stats, minimap` | ✅ | `ui/tabs/setup_tab.py:372` | Đã duyệt mảng key ROI và gán `hunt_cfg["rois"][k] = list(region)`. |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Data Migration Crash (Load config cũ) | ✅ | `lib/features/hunt/config_migrator.py:314` | Hàm `migrate_hunt_config` chuẩn hoá schema V3 và tránh crash config. |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Test Validation Layer = Pydantic | ❌ | N/A | Không tìm thấy Unit test nào cho Validation Pydantic trong repo. |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | D2: Schema Validation bằng Pydantic | ✅ | `lib/features/hunt/hunt_config.py:64` | Khai báo `HuntConfigSchema(BaseModel)` và validate ở hàm `load_hunt_config`. Có auto-restore từ `.bak` (`ui/features/hunt/hunt_config.py:101`). |
| 2 | D?: Lỗi 0 byte JSON (Atomic Write) | ✅ | `lib/features/hunt/hunt_config.py:39` | Lưu file tmp và dùng `os.replace` (atomic). |
| 3 | D6: i18n Hardcode | ❌ | `ui/panels/monster_target_panel.py:128` | Text `text=self.app._t("hunt_area.set") if hasattr(self.app, "_t") else "Set Hunt Area"` vẫn dùng fallback string tiếng Anh cứng (không phải vi phạm lớn). |

---

### Task 9: Chuẩn hóa Hệ thống Icon (Standardize Icon System)

**Trạng thái tổng:** 🟡 PARTIAL
**Completion:** 15%  |  **Risk:** HIGH (Red Flag)

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Rà soát `monster_target_panel.py` dùng `create_icon_button` | ✅ | `ui/panels/monster_target_panel.py:124, 195, 206...` | Đã thay bằng `create_icon_button`. |
| 2 | Rà soát `skill_panel.py` dùng `create_icon_button` | ✅ | `ui/panels/skill_panel.py:116, 222, 232...` | Đã thay toàn bộ button bằng `create_icon_button`. |
| 3 | Đảm bảo truyền `element_id` để đăng ký registry | ✅ | Trong lệnh `create_icon_button` | Truyền `element_id="btn_target_up"`, `btn_skill_build`, v.v... |
| 4 | Loại bỏ Emoji báo trạng thái (`🔴`, `🟢`) thay bằng ảnh/text. | ❌ | `ui/panels/screen_state_panel.py:67`, v.v.. | Rất nhiều emoji (`🔴, 🟢, 🎯, ➕, ⏱, 🔄`) vẫn tồn tại trong string UI (`ui/helpers/icon_helper.py`, `ui/panels/screen_state_panel.py`). |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | D6: Quét rạch rác Emoji | ❌ | `grep -rn -P "[🔴🟢🎯➕⏱🔄]"` | Còn hàng chục hardcoded emoji trên UI và icon_helper. |

**Đề xuất hành động**
1. System API của Icon đã được dùng (`create_icon_button`) cho việc hiển thị tốt. Tuy nhiên nợ D6 (Emoji rác) chưa được quét dọn tận gốc, nó vương vãi rất nhiều trong `IconHelper`, tooltip, Label.

---

### Task 10: Tái cấu trúc Layout và Phân cấp Typography

**Trạng thái tổng:** ✅ DONE / 🟡 PARTIAL (Typography)
**Completion:** 75%  |  **Risk:** HIGH (Red Flag) (Thiếu minsize)

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Dùng `ttk.PanedWindow` chia lưới | ✅ | `ui/tabs/hunt_tab.py:341` | Đã chia `paned_window.add(..., weight=58)` và `weight=42`. |
| 2 | KHÔNG xóa `ResponsiveGridBase` | ✅ | `ui/components/base/responsive_grid_base.py` | Vẫn tồn tại và được `skill_stats_panel.py` kế thừa. |
| 3 | Typography Hierarchy (`UIStyleV2.get_font`) | ❌ | Bị sai cú pháp / bỏ sót ở `ui/tabs/hunt_tab.py` | Trong `hunt_tab.py` không hề thấy gọi `UIStyleV2.get_font("title", "bold")` cho các header. Một số file Panel thì có dùng (`ui/panels/target_status_panel.py:29`). |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Sash Dragging tràn Layout (minsize) | ❌ | `ui/tabs/hunt_tab.py` | Không thấy truyền tham số cấu hình `minsize` hoặc logic giới hạn kích thước thu nhỏ khung, dễ kéo tràn UI. |

---

## ⚡ Tổng hợp Nợ Kỹ Thuật (Phần 3)

| # | Khoản Nợ (D1 - D6) | Đã trả chưa? | Bằng chứng (Vi phạm / Giải quyết) | Đánh giá Risk |
|---|---------------------|--------------|------------------------------------|--------------|
| D1 | Tight Coupling UI ↔ Config (`hunt_cfg.get` UI Layer) | ❌ Chưa trả | Rất nhiều View/Panel trực tiếp thao tác `hunt_cfg.get()`: `ui/tabs/hunt_tab.py:70`, `ui/windows/library_manager.py`, `ui/tabs/setup_tab.py`... | HIGH (Red Flag) |
| D2 | Missing Schema Validation (`pydantic`) | ✅ Đã trả | `lib/features/hunt/hunt_config.py:64` | LOW |
| D3 | EventBus Payload Bloat (Numpy frame / Raw dict) | ✅ Đã trả | `lib/features/hunt/hunt_orchestrator.py:155` (Đã có logic `del clean_snapshot["frame"]` trước khi trigger `SceneMonstersDetectedEvent`). | LOW |
| D4 | Phân mảnh Tkinter Event Loop (`self.after` loop ngoài manager) | ❌ Chưa trả | Còn hàng loạt `.after(300)`, `.after(500)` tại `ui/components/status_badge.py:84`, `ui/windows/monster_manager_win.py:1080`, `image_library_component.py` hoạt động độc lập với Animation Manager. | HIGH (Lag giật UI) |
| D5 | Bounding Box Scale Math | ✅ Đã trả | `ui/components/vision_snapshot_debugger.py:77` (Scale chuẩn `dx = int(det["x"] * scale)`). | LOW |
| D6 | i18n Hardcode (Emoji và Text cứng) | ❌ Chưa trả | `ui/panels/target_status_panel.py:29` (Hardcode "📊 Target Status"), `ui/components/hunt_status_ticker.py:61` (Emoji 🔄), Tooltip và Fallbacks khác. | HIGH (Mất đồng bộ đa ngôn ngữ) |

---

## 🚀 Đề xuất Sprint Tiếp Theo (Phần 4)

1. **Sprint Kỹ Thuật Chuyên Sâu D1 & D4 (Priority 0):**
   - Rủi ro: Việc luồng UI phân mảnh `.after` khiến CPU spike. Tách rời Config ra khỏi UI tránh hỏng dữ liệu khi thay đổi Schema config.
   - Nhiệm vụ: Xóa sạch `.after` vòng lặp đồ hoạ độc lập (như ở `status_badge.py`, Image Search loop) và đẩy về `UIAnimationManager`. Thay thế 100% `hunt_cfg.get` trên UI thành Model Controller (Getters/Setters).

2. **Fix Bug Cascade Integration & TclError (Priority 1):**
   - Rủi ro: Task 4 render `SkillTimelineStrip` hoàn toàn rỗng vì thiếu luồng truyền tham số `skills=...`. Lỗi `TclError` ở Unicode Emoji chặn toàn bộ luồng Unit Test cho Tkinter Headless.
   - Nhiệm vụ: Tích hợp API giữa `SkillPanelController` và `SkillTimelineStrip`. Mock/Fix cơ chế fallback ảnh để không gọi string ❓ vào tham số ảnh của `tk.Canvas.create_image`.

3. **Chiến dịch "Sạch Rác UI" - i18n & Layout (Priority 2):**
   - Rủi ro: Quên cấu hình Typography và minsize Sash Dragging dễ làm UI vỡ ở độ phân giải nhỏ. Hardcode tiếng Việt / Emoji chặn tiến trình phát hành phiên bản Tiếng Anh (D6).
   - Nhiệm vụ: Quét sạch `IconHelper` và loại bỏ Emoji. Cài đặt `minsize` cho các frame trong `PanedWindow` (HuntTab) và tiêu chuẩn hoá UI Fonts.

Tỉ lệ hoàn thành chung: ~88% (Có phát sinh một số lỗi lớn ở Integration). Sprint đã đạt được nền móng (AnimationManager, Data Config Atomic) nhưng phần "đánh bóng" UI integration còn nhiều lỏng lẻo.
- ❌ Lỗi tích hợp `save_hunt_config()` không được gọi khi Toggle ở Task 4.
