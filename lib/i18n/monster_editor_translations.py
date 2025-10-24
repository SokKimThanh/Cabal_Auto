"""
Monster Editor i18n Translations.

Translations for Monster Editor UI components.
Namespace: 'monster_editor'

Author: SokKimThanh
Created: 2025-10-24
"""

MONSTER_EDITOR_TRANSLATIONS = {
    'vi': {
        # Menu items
        'menu_open_monster_editor': 'Mở Quản Lý Quái Vật',
        'menu_monster_editor_settings': 'Cài Đặt Quái Vật',
        
        # Window titles
        'quick_editor_title': 'Sửa Quái Nhanh',
        'full_editor_title': 'Quản Lý Quái Vật',
        'capture_panel_title': 'Chụp Template',
        
        # Labels
        'monster_name_label': 'Tên quái:',
        'monster_level_label': 'Cấp độ:',
        'monster_threshold_label': 'Ngưỡng nhận diện:',
        'template_list_label': 'Danh sách Template:',
        
        # Buttons
        'btn_save': 'Lưu',
        'btn_cancel': 'Hủy',
        'btn_capture': 'Chụp Vùng',
        'btn_test': 'Test Nhận Diện',
        'btn_add_template': 'Thêm Template',
        'btn_remove_template': 'Xóa',
        'btn_new_monster': 'Tạo Mới',
        'btn_edit_monster': 'Sửa',
        'btn_delete_monster': 'Xóa',
        
        # Tooltips
        'tooltip_capture': 'Chụp vùng màn hình để tạo template',
        'tooltip_test': 'Test nhận diện template trên màn hình hiện tại',
        'tooltip_save': 'Lưu thay đổi vào file cấu hình',
        'tooltip_cancel': 'Hủy thay đổi',
        'tooltip_new_monster': 'Tạo quái vật mới',
        'tooltip_edit_monster': 'Sửa quái vật đang chọn',
        'tooltip_delete_monster': 'Xóa quái vật đang chọn',
        
        # Messages
        'msg_monster_created': 'Đã tạo quái vật thành công',
        'msg_monster_updated': 'Đã cập nhật quái vật thành công',
        'msg_monster_deleted': 'Đã xóa quái vật thành công',
        'msg_template_added': 'Đã thêm template thành công',
        'msg_template_removed': 'Đã xóa template thành công',
        'msg_test_success': 'Tìm thấy {} kết quả (độ tin cậy: {:.1%})',
        'msg_test_failed': 'Không tìm thấy kết quả',
        'msg_capture_started': 'Đang chụp vùng... Di chuyển chuột và click để chọn',
        'msg_capture_cancelled': 'Đã hủy chụp vùng',
        
        # Errors
        'error_name_empty': 'Tên quái không được để trống',
        'error_level_invalid': 'Cấp độ phải là số nguyên dương',
        'error_threshold_range': 'Ngưỡng phải từ 0.0 đến 1.0',
        'error_template_not_found': 'Không tìm thấy template',
        'error_capture_failed': 'Lỗi khi chụp vùng: {}',
        'error_test_failed': 'Lỗi khi test template: {}',
        
        # Confirm dialogs
        'confirm_delete_title': 'Xác nhận xóa',
        'confirm_delete_message': 'Bạn có chắc muốn xóa quái "{}" không?',
        'confirm_delete_template_title': 'Xác nhận xóa template',
        'confirm_delete_template_message': 'Bạn có chắc muốn xóa template này không?',
        
        # Progress
        'progress_capturing': 'Đang chụp...',
        'progress_testing': 'Đang test...',
        'progress_saving': 'Đang lưu...',
        'progress_loading': 'Đang tải...',
        
        # Column headers
        'col_name': 'Tên',
        'col_level': 'Cấp',
        'col_templates': 'Templates',
        'col_threshold': 'Ngưỡng',
        'col_path': 'Đường dẫn',
        
        # Status indicators
        'status_modified': '● Đã chỉnh sửa (chưa lưu)',
        'status_unsaved': 'Có thay đổi chưa lưu',
        'status_saved': 'Đã lưu tất cả',
        
        # Tabs
        'tab_info': 'Thông Tin Quái',
        'tab_templates': 'Templates',
        
        # Additional labels
        'label_monster_list': 'Danh Sách Quái Vật',
        'monster_list_title': 'Danh Sách Quái Vật',
        'monster_priority_label': 'Độ ưu tiên:',
        'monster_hp_label': 'HP:',
        'monster_damage_label': 'Sát thương mỗi đòn:',
        'monster_desc_label': 'Mô tả:',
        'template_list_title': 'Danh sách Templates:',
        'default_monster_name': 'Quái Mới',
        
        # Additional buttons
        'btn_save_all': 'Lưu Tất Cả',
        'btn_close': 'Đóng',
        'btn_add_monster': 'Thêm Quái',
        'btn_browse': 'Chọn File',
        'btn_delete_template': 'Xóa Template',
        'btn_delete': 'Xóa',
        
        # Additional messages
        'msg_test_result': 'Tìm thấy: {}, Độ tin cậy: {:.1%}',
        'msg_save_success': 'Đã lưu danh sách quái vật thành công',
        'msg_no_data': 'Không có dữ liệu để lưu',
        'msg_unsaved_changes': 'Bạn có thay đổi chưa lưu. Bỏ qua chúng?',
        
        # Titles
        'title_confirm': 'Xác nhận',
        
        # Warnings
        'warning_no_monster_selected': 'Vui lòng chọn một quái để xóa.',
        
        # Confirmations
        'confirm_delete_monster': "Bạn có chắc muốn xóa '{}' không?",
    },
    'en': {
        # Menu items
        'menu_open_monster_editor': 'Open Monster Manager',
        'menu_monster_editor_settings': 'Monster Settings',
        
        # Window titles
        'quick_editor_title': 'Quick Monster Editor',
        'full_editor_title': 'Monster Manager',
        'capture_panel_title': 'Capture Template',
        
        # Labels
        'monster_name_label': 'Monster name:',
        'monster_level_label': 'Level:',
        'monster_threshold_label': 'Recognition threshold:',
        'template_list_label': 'Template List:',
        
        # Buttons
        'btn_save': 'Save',
        'btn_cancel': 'Cancel',
        'btn_capture': 'Capture Region',
        'btn_test': 'Test Recognition',
        'btn_add_template': 'Add Template',
        'btn_remove_template': 'Remove',
        'btn_new_monster': 'New',
        'btn_edit_monster': 'Edit',
        'btn_delete_monster': 'Delete',
        
        # Tooltips
        'tooltip_capture': 'Capture screen region to create template',
        'tooltip_test': 'Test template recognition on current screen',
        'tooltip_save': 'Save changes to configuration file',
        'tooltip_cancel': 'Cancel changes',
        'tooltip_new_monster': 'Create new monster',
        'tooltip_edit_monster': 'Edit selected monster',
        'tooltip_delete_monster': 'Delete selected monster',
        
        # Messages
        'msg_monster_created': 'Monster created successfully',
        'msg_monster_updated': 'Monster updated successfully',
        'msg_monster_deleted': 'Monster deleted successfully',
        'msg_template_added': 'Template added successfully',
        'msg_template_removed': 'Template removed successfully',
        'msg_test_success': 'Found {} matches (confidence: {:.1%})',
        'msg_test_failed': 'No matches found',
        'msg_capture_started': 'Capturing... Move mouse and click to select region',
        'msg_capture_cancelled': 'Capture cancelled',
        
        # Errors
        'error_name_empty': 'Monster name cannot be empty',
        'error_level_invalid': 'Level must be a positive integer',
        'error_threshold_range': 'Threshold must be between 0.0 and 1.0',
        'error_template_not_found': 'Template not found',
        'error_capture_failed': 'Capture failed: {}',
        'error_test_failed': 'Test failed: {}',
        
        # Confirm dialogs
        'confirm_delete_title': 'Confirm Delete',
        'confirm_delete_message': 'Are you sure you want to delete "{}"?',
        'confirm_delete_template_title': 'Confirm Delete Template',
        'confirm_delete_template_message': 'Are you sure you want to delete this template?',
        
        # Progress
        'progress_capturing': 'Capturing...',
        'progress_testing': 'Testing...',
        'progress_saving': 'Saving...',
        'progress_loading': 'Loading...',
        
        # Column headers
        'col_name': 'Name',
        'col_level': 'Level',
        'col_templates': 'Templates',
        'col_threshold': 'Threshold',
        'col_path': 'Path',
        
        # Status indicators
        'status_modified': '● Modified (not saved)',
        'status_unsaved': 'Unsaved changes',
        'status_saved': 'All saved',
        
        # Tabs
        'tab_info': 'Monster Info',
        'tab_templates': 'Templates',
        
        # Additional labels
        'label_monster_list': 'Monster List',
        'monster_list_title': 'Monster List',
        'monster_priority_label': 'Priority:',
        'monster_hp_label': 'HP:',
        'monster_damage_label': 'Damage per hit:',
        'monster_desc_label': 'Description:',
        'template_list_title': 'Template List:',
        'default_monster_name': 'New Monster',
        
        # Additional buttons
        'btn_save_all': 'Save All',
        'btn_close': 'Close',
        'btn_add_monster': 'Add Monster',
        'btn_browse': 'Browse',
        'btn_delete_template': 'Delete Template',
        'btn_delete': 'Delete',
        
        # Additional messages
        'msg_test_result': 'Found: {}, Confidence: {:.1%}',
        'msg_save_success': 'Monsters saved successfully',
        'msg_no_data': 'No data to save',
        'msg_unsaved_changes': 'You have unsaved changes. Discard them?',
        
        # Titles
        'title_confirm': 'Confirm',
        
        # Warnings
        'warning_no_monster_selected': 'Please select a monster to delete.',
        
        # Confirmations
        'confirm_delete_monster': "Are you sure you want to delete '{}'?",
        'msg_test_result': 'Matches: {}, Confidence: {:.1%}',
    }
}
