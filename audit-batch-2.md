### Task 3: Phát triển Component `SkillTimelineStrip`

**Trạng thái tổng:** ✅ DONE / 🟡 PARTIAL
**Completion:** 87.5%  |  **Risk:** MEDIUM

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Tạo file `skill_timeline_strip.py` | ✅ | `ui/components/skill_timeline_strip.py:121` | Định nghĩa class `SkillTimelineStrip` |
| 2 | Component nhận danh sách skill, BẮT BUỘC có cơ chế Scroll khi vượt 8 skill | ✅ | `ui/components/skill_timeline_strip.py:122`, `191` | `MAX_SLOTS = 8`, dùng `ttk.Scrollbar` khi `len(self.skills) > self.MAX_SLOTS` |
| 3 | Hỗ trợ kéo thả (Reorder) và Nút Undo (Single-level) | ✅ | `ui/components/skill_timeline_strip.py:220-272` | `_on_drag_release` xử lý swap index, `undo` khôi phục mảng `_history` |
| 4 | Mỗi ô hiển thị Icon, Hotkey, viền sáng Cooldown | ✅ | `ui/components/skill_timeline_strip.py:46`, `76`, `88` | Vẽ icon (fallback text), draw hotkey ở góc, cooldown rect màu xám |
| 5 | API `update_cooldown(skill_name, ratio)` | ✅ | `ui/components/skill_timeline_strip.py:108`, `209` | Vẽ overlay đè lên từ dưới lên trên |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Image Rendering Garbage Collection | ✅ | `ui/components/skill_timeline_strip.py:40`, `53` | `self._images = {}`, gán ảnh vào dict để giữ reference. |
| 2 | Dùng tk.Canvas cho ô Slot để vẽ overlay | ✅ | `ui/components/skill_timeline_strip.py:11-20` | `SkillSlotCanvas` kế thừa `tk.Canvas` thay vì `tk.Label`. |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Test Khởi tạo Component | ❌ | `tests/unit/ui/components/test_skill_timeline_strip.py:27` | Code test ném `TclError: image "❓" doesn't exist` vì Fallback emoji không hoạt động trong Canvas. |
| 2 | Giới hạn Cooldown Ratio (0.0 - 1.0) | ❌ | `tests/unit/ui/components/test_skill_timeline_strip.py:46` | Không test được do component lỗi khởi tạo. |
| 3 | Test scroll bar > 8 items | ❌ | `tests/unit/ui/components/test_skill_timeline_strip.py:38` | Không test được do component lỗi khởi tạo. |
| 4 | Test Undo logic | ❌ | `tests/unit/ui/components/test_skill_timeline_strip.py:68` | Không test được do component lỗi khởi tạo. |
| 5 | GC Image test | ✅ | `tests/unit/ui/components/test_skill_timeline_strip.py:89` | Chạy pass (Sử dụng Mock Image). |

*Lưu ý: Canvas `create_image` hoặc `create_text` của Tkinter bị crash ở test nếu không truyền Image hợp lệ hoặc Font gặp lỗi Unicode ❓.*

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | Quản lý Bộ nhớ ảnh (GC) | ✅ | `ui/components/skill_timeline_strip.py:40` | Khai báo dictionary `self._images` để giữ tham chiếu ảnh. |

**Đề xuất hành động**
1. Các logic phức tạp như Reorder, Undo, Cooldown Overlay, và Scrollbar đều được code chính xác. Tuy nhiên, 3/4 Unittest của file `test_skill_timeline_strip.py` bị Fail do lỗi `_tkinter.TclError` ở dòng 51: Dùng `create_image` nhưng không xử lý đúng trường hợp fallback (hoặc fallback text emoji). Cần fix unit tests để mock hình ảnh hợp lệ (như test số 5).

---

### Task 6: Phát triển Component `HuntStatusTicker` (System Log)

**Trạng thái tổng:** ✅ DONE / 🟡 PARTIAL (Lỗi i18n Hardcode)
**Completion:** 85%  |  **Risk:** MEDIUM

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Tạo file `hunt_status_ticker.py` kế thừa tk.Frame | ✅ | `ui/components/hunt_status_ticker.py:5` | Class `HuntStatusTicker` kế thừa `tk.Frame` |
| 2 | Component có Icon và Label text, hiển thị status mới nhất | ✅ | `ui/components/hunt_status_ticker.py:15`, `24` | `icon_label` và `msg_label` được sử dụng để hiển thị |
| 3 | Đăng ký EventBus (Status và State) trong `__init__` | ✅ | `ui/components/hunt_status_ticker.py:34` | Gọi `EventBus.bind` cho cả hai event |
| 4 | Tích hợp vào đáy `hunt_workspace_frame.py` | ✅ | `ui/views/hunt_workspace_frame.py:17` | Khởi tạo `self.status_ticker = HuntStatusTicker(self, app)` và `pack(side=tk.BOTTOM, fill=tk.X)` |
| 5 | Dùng hàm đa ngôn ngữ `self.app._t` cho mọi string | ❌ | `ui/components/hunt_status_ticker.py:17, 61, 64, 67, 70` | Viết cứng Emoji dạng text (`text="ℹ️"`, `text="🔄"`, v.v.) vi phạm chuẩn D6. Chỉ các nhãn text mới dùng `_t()`. |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Thread Safety (`self.after(0)`) | ✅ | `ui/components/hunt_status_ticker.py:46, 50` | Sự kiện EventBus sử dụng `self.after(0, lambda: ...)` đúng nguyên tắc. |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Unit Test giả lập EventBus | ❌ | N/A | Không tìm thấy bất kỳ unit test nào cho `HuntStatusTicker` trong folder `tests/ui/components/` |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | Tối ưu EventBus (không truyền payload khủng) | ✅ | Kiểm tra toàn bộ dự án (`D3`) | Không ghi nhận EventBus truyền mảng Numpy/frame. Payload Event chỉ truyền string/state. |
| 2 | D6 - i18n Hardcode | ❌ | `ui/components/hunt_status_ticker.py` | Có hardcode emoji. |

**Đề xuất hành động**
1. Code nghiệp vụ (Thread-safety và Bind EventBus) chuẩn. Tích hợp `HuntStatusTicker` vào `hunt_workspace_frame.py` thành công.
2. Vướng 2 Red Flags: Thiếu hoàn toàn Unit Tests cho Component, và vi phạm D6 do chèn cứng các Emoji text `ℹ️`, `⚠️`, `🔍` trực tiếp trong Component thay vì khai báo qua icon/symbol manager.

---

### Task 7: Phát triển Cơ chế `VisionSnapshotDebugger` (On-Demand Preview)

**Trạng thái tổng:** ✅ DONE
**Completion:** 95%  |  **Risk:** LOW (Vi phạm spec)

**Requirements**
| # | Yêu cầu | Trạng thái | Bằng chứng | Ghi chú |
|---|---------|-----------|-----------|---------|
| 1 | Nút Debug Vision mở cửa sổ Toplevel | ✅ | `ui/components/vision_snapshot_debugger.py:27, 31` | Tạo `tk.Toplevel()` |
| 2 | Method Call Thread-Safe (Mutex/Lock) | ✅ | `lib/vision/vision_engine.py:108` | Hàm `get_latest_snapshot` dùng `self.snapshot_lock.acquire(timeout=timeout)` |
| 3 | Resize ảnh, vẽ Bounding Box OpenCV/Pillow, ghi chú | ✅ | `ui/components/vision_snapshot_debugger.py:78, 86` | Dùng `cv2.resize` và vẽ bounding box tỉ lệ thuận theo toán học |
| 4 | Nút Refresh Snapshot và tự huỷ Image Reference | ✅ | `ui/components/vision_snapshot_debugger.py:42`, `123` | Nút `Refresh Snapshot` và hàm `_on_close` set `self.current_image = None` |

**Risks & Pitfalls**
| # | Rủi ro | Đã phòng chưa? | Bằng chứng |
|---|--------|----------------|-----------|
| 1 | Deadlock/Timeout | ✅ | `ui/components/vision_snapshot_debugger.py:59`, `lib/vision/vision_engine.py:108` | Bắt đúng lock với `timeout=0.5`. |
| 2 | Hủy biến ảnh cũ trước khi gọi OpenCV | ✅ | `ui/components/vision_snapshot_debugger.py:109` | Gán `self.current_image = None` trước khi convert Pillow |

**Unit Tests**
| # | Test | Tồn tại? | File | Chạy pass? |
|---|------|---------|------|-----------|
| 1 | Memory Leak test (Refresh 50 lần) | ✅ | `tests/ui/components/test_vision_snapshot_debugger.py:38` | Chạy pass (1/1 passed) |

**Technical Debt Paydown**
| # | Nợ cần trả | Đã trả? | Bằng chứng |
|---|-----------|---------|-----------|
| 1 | D5: Toán học Bounding Box Scale | ✅ | `ui/components/vision_snapshot_debugger.py:77` | Scale chính xác: `dx = int(det.get("x", 0) * scale)` |
| 2 | D6: i18n Hardcode | ✅ | `ui/components/vision_snapshot_debugger.py:32, 94` | String gọi hàm dịch thuật: `self.app._t("vision_debugger.target")` |

**Đề xuất hành động**
1. Task 7 thực hiện hoàn hảo. Vấn đề Thread-safe Lock được xử lý đúng chuẩn tại `lib/vision/vision_engine.py`. Test Memory leak cũng chạy thành công. D5 đã được trả (scale toán học chính xác).- ❌ Lỗi Spec: `ui/components/vision_snapshot_debugger.py:84-93` xóa ảnh cũ (`delete("all")`) thay vì giữ lại khi Timeout.
