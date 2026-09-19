# Fallback Strategies & Execution Order

Thứ tự thực thi các prompt:
1. `sprint32-prompt-1-create-registry.md`
2. `sprint32-prompt-2-update-helpers.md`
3. `sprint32-prompt-3-integrate-icon-manager.md`

## Fallback Strategies

Nếu gặp lỗi trong quá trình thực thi:
1. **Lỗi khi tích hợp Registry vào Helper:** Nếu việc tiêm Singleton (instance) gây ra lỗi do import vòng (circular import) hoặc khó thiết lập ở mức helper tĩnh, hãy thử fallback về việc sử dụng Class attributes (như `@classmethod` và biến `_cache` class-level) thay vì tạo instance độc lập.
2. **Lỗi hiển thị Combobox trong Icon Manager:** Nếu việc merge danh sách giữa DB và Registry tạo ra danh sách quá lớn làm treo UI (ít khả năng xảy ra, nhưng nếu có), hãy fallback bằng cách giới hạn số lượng hiển thị trong Combobox hoặc chỉ render khi user gõ search.
