
# Module Split Audit Report: Code Loss & Architecture

## 1. So sánh Gốc -> Hiện tại/module mới -> Trạng thái

| Hàm/Khối gốc (app_gui_original.md) | Hiện tại / Module mới | Trạng thái |
| :--- | :--- | :--- |
| `_normalize_window_bounds` | `lib/features/hunt/hunt_config.py` & `ui/controllers/app_runtime_bridge.py` | `moved` & duplicated |
| `_normalize_template_entry` | N/A (removed entirely) | `missing-risk` |
| `_sanitize_templates` | `lib/features/hunt/hunt_config.py` (simplified version) | `replaced` |
| `load_monster_library` | `lib/features/monsters/monster_repo.py` | `moved` |
| `save_monster_library` | `lib/features/monsters/monster_repo.py` | `moved` |
| `load_skill_library` | `lib/features/skills/skill_repo.py` & `ui/windows/library_manager.py` | `moved` |
| `save_skill_library` | `lib/features/skills/skill_repo.py` | `moved` |
| `calculate_attack_speed_from_skills`| `lib/features/skills/runtime.py` (assumed based on roadmap) | `moved` |
| `load_config` | `scripts/main_safe.py` & `lib/features/hunt/hunt_config.py` | `moved` |
| `save_config` | `lib/features/hunt/hunt_config.py` (ConfigManager) | `replaced` |
| `load_hunt_config` | `lib/features/hunt/hunt_config.py` | `moved` |
| `save_hunt_config` | `lib/features/hunt/hunt_config.py` | `moved` |
| `on_close` | `ui/controllers/app_runtime_bridge.py` | `moved` |
| `destroy` | `app_gui.py` & `ui/controllers/app_runtime_bridge.py` | `kept` (split logic) |

## 2. Các rủi ro bị mất (Missing Risks)

1. **`_normalize_template_entry` (Missing-risk)**
   - **Tình trạng:** Hàm cũ trong `app_gui_original.md` xử lý việc bình thường hóa `threshold` (giới hạn 0.0 - 1.0) và validate `path`, `name`. Hàm này đã biến mất hoàn toàn trong `hunt_config.py` hay `monster_repo.py`.
   - **Cách khôi phục:** Cần bổ sung lại logic validate/normalize cho template entry vào một hàm dùng chung trong `hunt_config.py` hoặc `monster_repo.py` khi load templates.
   - **Lý do:** Thiếu validate có thể gây lỗi `ValueError` hoặc `TypeError` khi engine sử dụng các giá trị `threshold` không hợp lệ.

2. **Sự trùng lặp và không nhất quán trong `destroy()`**
   - **Tình trạng:** Trong `app_gui.py` (dòng 3738) vẫn còn code dọn dẹp `_overlay_controller.stop()`, `_bot_manager.destroy()`, và `keyboard.remove_hotkey()`. Trong khi đó, `ui/controllers/app_runtime_bridge.py` (dòng 668, `on_close`) cũng gọi `self._unregister_global_hotkeys()` và `self._overlay_controller.stop()`.
   - **Cách khôi phục:** Cần tập trung logic dọn dẹp vào một chỗ duy nhất (`AppLifecycleController` theo đúng roadmap, hiện tại đang tạm ở `app_runtime_bridge.py`) và xóa code thừa trong `app_gui.py::destroy()`.

## 3. Các phần cố ý xóa (Intentionally Removed)

- Các wrapper rỗng, các class/hàm logic không còn được UI trực tiếp gọi đã được move vào các module `lib/features/hunt/hunt_config.py` hoặc `ui/controllers/app_runtime_bridge.py`. Việc này phù hợp với mục tiêu tách `app_gui.py` thành một composition root mỏng theo roadmap.
- `App.__init__` không còn gánh việc load config và validate (đã move sang controller và config migrator).

## 4. Các đoạn code phức tạp có thể đơn giản hóa

1. **`ui/controllers/app_runtime_bridge.py` - Compatibility Layer quá tải**
   - `AppRuntimeBridgeMixin` đang trở thành một "God Object" mới (chứa đủ thứ từ library manager callbacks, window listing, overlay tracking, đến `on_close` lifecycle).
   - **Đề xuất:** Theo đúng roadmap (Sprint 1 & 3), nên tách riêng `AppLifecycleController` (cho `on_close`, `destroy`), `WindowTrackerController` (cho việc track và list windows) và `OverlayController` riêng biệt thay vì dồn hết vào `AppRuntimeBridgeMixin`.

2. **Dữ liệu legacy config & Migration**
   - Hàm `_sanitize_templates` hiện tại trong `hunt_config.py` khá lỏng lẻo so với bản gốc. Cần sử dụng một validator schema chung hoặc tập trung vào `ConfigMigrator` theo roadmap (Sprint 2) để đảm bảo migration an toàn hơn.
