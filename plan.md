1. **Update `ui/views/icon_manager_frame.py`**
   - Add background threading logic for the `_on_sync` method to prevent UI freezing during sync operations. Disable `self.btn_sync` while syncing and update its text/state. Provide visual feedback when completed.
   - Implement a cooldown mechanism after syncing so `btn_sync` remains disabled for a certain duration (e.g., 60 seconds) to prevent spamming.
   - Use `attach_i18n_tooltip` on `self.btn_refresh` and `self.btn_sync` with new translation keys (e.g., `tooltip_icon_manager_refresh`, `tooltip_icon_manager_sync`) to clarify their functionalities.
   - Refactor `_on_sync` to perform a "smart check" or simple bulk processing via a background thread, and once finished, trigger `self.load_tree_data()` on the main thread via `.after()`.

2. **Update `lib/i18n/translations.py`**
   - Add new translation keys for tooltips under appropriate languages (`en`, `vi`):
     - `tooltip_icon_manager_refresh`: 'Reload list from database (does not alter data)' / 'Tải lại danh sách từ cơ sở dữ liệu (không thay đổi dữ liệu gốc)'
     - `tooltip_icon_manager_sync`: 'Scan and update icons from system to database. Takes time.' / 'Quét và cập nhật icon mới từ hệ thống vào cơ sở dữ liệu. Thao tác này có thể mất chút thời gian.'
     - `btn_syncing`: 'Syncing...' / 'Đang đồng bộ...'
     - `btn_sync_cooldown`: 'Synced ({s}s)' / 'Đã đồng bộ ({s}s)'
     - `msg_sync_success_none`: 'Data is already up to date.' / 'Dữ liệu đã ở trạng thái mới nhất.'

3. **Complete Pre-commit Steps**
   - Ensure proper testing, verifications, reviews, and reflections are done.

4. **Submit the change**
   - Submit code via `submit` tool.
