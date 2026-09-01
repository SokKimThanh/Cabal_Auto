from lib.db.services.translation_service import TranslationService
from lib.db.connection import get_connection

def seed_window_translations():
    ts = TranslationService()

    # English
    ts.upsert('global', 'error_no_window_selected', 'en', 'No window selected. Please select a target window.')
    ts.upsert('global', 'error_window_changed', 'en', 'Target window process changed or is invalid. Hunt blocked.')
    ts.upsert('global', 'error_window_unavailable', 'en', 'Target window is closed, minimized, or unavailable.')
    ts.upsert('global', 'error_invalid_template', 'en', 'One or more selected template files do not exist or are invalid.')

    # Vietnamese
    ts.upsert('global', 'error_no_window_selected', 'vi', 'Chưa chọn cửa sổ. Vui lòng chọn cửa sổ mục tiêu.')
    ts.upsert('global', 'error_window_changed', 'vi', 'Tiến trình cửa sổ mục tiêu đã thay đổi hoặc không hợp lệ. Đã chặn Hunt.')
    ts.upsert('global', 'error_window_unavailable', 'vi', 'Cửa sổ mục tiêu đã bị đóng, thu nhỏ hoặc không khả dụng.')
    ts.upsert('global', 'error_invalid_template', 'vi', 'Một hoặc nhiều tệp template đã chọn không tồn tại hoặc không hợp lệ.')

    conn, is_local = get_connection()
    if conn:
        try:
            conn.commit()
        except Exception as e:
            print(f"Failed to commit window validation translations: {e}")
            raise
        finally:
            if is_local:
                conn.close()

    print("Window validation translations seeded successfully.")

if __name__ == "__main__":
    seed_window_translations()
