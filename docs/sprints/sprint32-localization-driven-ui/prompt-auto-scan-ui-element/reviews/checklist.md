# Review Checklist: Auto-Scan UI Elements (Runtime Registry)

- [ ] `UIElementRegistry` đã được tạo đúng và hoạt động an toàn (không bị memory leak/lỗi trùng lặp).
- [ ] Các hàm trong `ui/components/icon_button.py` đã nhận thêm parameter `element_id`.
- [ ] Backward compatibility của các hàm helpers không bị phá vỡ.
- [ ] `IconManagerFrame._load_all_usage_ids` đã thực hiện merge dữ liệu DB và Registry đúng cách.
- [ ] Combobox trong UI Icon Manager hiển thị đúng dữ liệu merged và tính năng auto-complete/search hoạt động bình thường (không bị chặn do `validate="key"`).
- [ ] Unit test cho Registry chạy Pass xanh.
