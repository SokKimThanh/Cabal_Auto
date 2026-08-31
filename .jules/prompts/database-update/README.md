# Database Update Prompt Pack

Bộ prompt này cập nhật SQLite dựa trên dữ liệu hiện có, tuân thủ nghiêm ngặt các nguyên tắc: **additive**, **idempotent**, **zero-inference** và **có kiểm thử toàn vẹn**.

## Tài liệu quy chuẩn bắt buộc đọc trước khi chạy
1. `00-global-rules.md`: Quy tắc vận hành phiên (Timebox 30 phút, dừng phút 25, rollback bằng patch có chủ đích, cấm `git reset` hoặc broad discard)[cite: 2].
2. `docs/DATABASE_SKILL_CLASS_UPDATE_ROADMAP.md`: Source of truth cho mục tiêu và lộ trình cập nhật tổng thể[cite: 2, 8].
3. `docs/DATABASE_SOURCE_DATA_MANIFEST.md`: Danh mục source ID và file được phép sử dụng; cấm tuyệt đối file trùng tên, user library và web bundle trái phép[cite: 2, 8].
4. `docs/DATABASE_RELATIONSHIP_CONTRACT.md`: Quy chuẩn bắt buộc về FK actions, cardinality, seed order, unique constraints và orphan checks[cite: 2].
5. `docs/UI_DATABASE_INTEGRATION_CONTRACT.md`: Quy chuẩn phân định quyền sở hữu dữ liệu giữa DB catalogue và runtime user config (`skills.json`, `monsters.json`, `hunt_config.json`)[cite: 2, 6].

## Điều phối liên luồng (Cross-Stream Coordination)
- Tuân theo `CROSS_STREAM_PROMPT_EXECUTION_ORDER.md`[cite: 8].
- **Chốt chặn i18n:** `DB1` phải hoàn thành (`PASSED`) trước khi chạy session i18n `I3A`[cite: 8].
- **Chốt chặn UI:** `DB7` chỉ cung cấp read-only adapters/fallback tests; không tự ý bind adapter vào UI Tkinter (UI binding là session riêng sau DB7)[cite: 6, 8].

---

## Thứ tự thực hiện & Ranh giới từng Session

| Session | Tên file | Mục tiêu & Phạm vi chính | Gate / Ràng buộc chuyển tiếp |
| :--- | :--- | :--- | :--- |
| **DB0** | `DB0-schema-and-source-audit.md` | Audit schema hiện tại và đối chiếu source data[cite: 8]. | Xác định rõ boundary trước khi viết schema[cite: 2]. |
| **DB1** | `DB1-additive-schema-migration.md` | Tạo bảng/chỉ mục mới không phá hủy dữ liệu cũ[cite: 8]. | Prerequisite bắt buộc cho i18n `I3A` và `DB2`[cite: 8]. |
| **DB2** | `DB2-seed-classes.md` | Nạp dữ liệu danh mục Class chuẩn[cite: 8]. | Phải pass FK và unique constraint checks[cite: 2]. |
| **DB3** | `DB3-seed-skill-sprite-catalogue.md` | Nạp danh mục skill và sprite reference[cite: 8]. | Không gán class_id trực tiếp tại bước này[cite: 2]. |
| **DB4** | `DB4-seed-bm3-synergies.md` | Nạp dữ liệu hiệp đồng BM3 và hiệu ứng[cite: 8]. | Kiểm tra toàn vẹn parent-child synergy[cite: 2]. |
| **DB5** | `DB5-class-skill-mapping-audit.md` | Audit trích xuất bằng chứng class–skill từ source được cấp phép[cite: 1, 8]. | **BLOCK DB6** nếu manifest thiếu bằng chứng, mơ hồ hoặc suy diễn từ tên/icon[cite: 1, 8]. |
| **DB6** | `DB6-import-verified-class-skill-mappings.md` | Nạp mapping đã duyệt vào `class_skill_assignments`[cite: 4, 8]. | Chỉ nhận manifest DB5; cấm parse lại bundle trực tiếp[cite: 4]. |
| **DB7** | `DB7-runtime-integration.md` | Xây dựng read-only adapters và cơ chế fallback[cite: 5, 8]. | Cấm đè cấu hình user; cấm hook trực tiếp vào UI[cite: 5, 6]. |
| **DB8** | `DB8-integrity-tests-and-docs.md` | Chạy toàn bộ test suite toàn vẹn và cập nhật docs[cite: 7, 8]. | Báo cáo đầy đủ FK check, orphan check và row counts[cite: 2, 7]. |

---

## Quy tắc nghiêm ngặt trong từng Session
* **Nguyên tắc không suy diễn (Zero-Inference):** Tuyệt đối không tự suy đoán quan hệ class–skill từ sprite name, display name hoặc văn xuôi không có bằng chứng truy xuất nguồn[cite: 1, 2].
* **Bảo vệ User Configuration:** `lib/data/skills.json`, `lib/data/monsters.json`, và `lib/data/hunt_config.json` là source of truth của người dùng, không bao giờ bị ghi đè bởi DB catalogue[cite: 2, 6].
* **Không bỏ qua thứ tự:** Tuyệt đối không chạy session tiếp theo nếu session phụ thuộc trước đó chưa đạt trạng thái `PASSED`[cite: 8].