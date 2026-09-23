# Kế hoạch Kiểm thử (Test Plan) - Sprint 33

## 1. Mục tiêu
Đảm bảo phần Refactor tách biệt UI và Logic hoạt động đúng, không phá vỡ logic cũ và giải quyết được bài toán Crash do Threading. Các test case tuân theo chuẩn Arrange - Act - Assert (AAA).

## 2. Các Kịch bản Kiểm thử Cốt lõi (Core Test Scenarios)

### 2.1. Kiểm thử Tách biệt Logic & UI (EventBus)

```python
def test_combo_hit_event_updates_ui_safely(mocker):
    # Arrange
    ui_manager = UIAnimationManager()
    bar = ComboRhythmBar(root)
    mock_canvas_itemconfig = mocker.patch.object(bar.canvas, 'itemconfig')

    # Act
    # Giả lập Event từ Background thread
    event = ComboHitEvent(timestamp=time.time(), skill_id=10, success_rate=0.9, is_sweet_spot=True)
    EventBus.publish(event)

    # Phải gọi update() để Tkinter xử lý các hàm after() trong hàng đợi
    root.update()

    # Assert
    # Kiểm tra hàm itemconfig được gọi để cập nhật UI, chứng tỏ luồng EventBus -> UI thông suốt
    mock_canvas_itemconfig.assert_called()
```

### 2.2. Kiểm thử Tự động chọn Mục tiêu (Auto Target) khi Target chết

```python
def test_orchestrator_presses_z_on_target_death(mocker):
    # Arrange
    mock_keyboard = mocker.patch('lib.system.input_backend.ForegroundSendInputBackend.tap')
    orchestrator = HuntOrchestrator(...)

    # Act
    # Target chết phát event HP = 0
    EventBus.publish(TargetHpUpdatedEvent(hp_percent=0.0))
    # Hoặc logic bên trong Orchestrator tự phát hiện loop báo dead
    orchestrator._handle_target_dead()

    # Assert
    # Hàm tap(key='Z') phải được gọi ít nhất 1 lần để chuyển mục tiêu
    mock_keyboard.assert_called_with('Z', mocker.ANY)
```

### 2.3. Kiểm thử Tải danh sách Kỹ năng theo Class (SkillPresetService)

```python
def test_class_switch_reloads_available_skills():
    # Arrange
    service = SkillPresetService()
    service.set_class(class_id=1)  # Class: Blader
    skills_class_1 = service.get_available_skills()

    # Act
    service.set_class(class_id=2)  # Class: Wizard
    skills_class_2 = service.get_available_skills()

    # Assert
    assert skills_class_1 != skills_class_2
    assert len(skills_class_2) > 0
    assert all(s.get('class_id') == 2 for s in skills_class_2)
```

### 2.4. Kiểm thử Chuyển đổi Unicode Progress Bar (Visual Stats)

```python
def test_unicode_progress_bar_formatting():
    # Arrange
    from ui.helpers.format_helper import format_progress_bar

    # Act
    bar_70 = format_progress_bar(percent=70.0, length=10)
    bar_0 = format_progress_bar(percent=0.0, length=10)
    bar_100 = format_progress_bar(percent=100.0, length=10)

    # Assert
    assert bar_70 == "███████░░░"
    assert bar_0 == "░░░░░░░░░░"
    assert bar_100 == "██████████"
```

## 3. Tiêu chí Chấp nhận (Acceptance Criteria)
1. **Zero Threading Error:** Chạy công cụ Auto Hunt ở chế độ giả lập trong 5 phút không sinh ra bất kỳ lỗi `_tkinter.TclError` nào liên quan đến gọi UI ngoài luồng chính.
2. **Backward Compatible:** Không sửa đổi trực tiếp các file JSON config hiện hữu. Tool vẫn đọc được cấu hình Combo và Buff cũ thành Timeline mới.
3. **Hiệu suất UI:** Mức sử dụng CPU của process ứng dụng giảm tối thiểu 10% khi chạy tính năng RhythmBar (đã giới hạn FPS qua UIAnimationManager) so với bản chưa refactor.
