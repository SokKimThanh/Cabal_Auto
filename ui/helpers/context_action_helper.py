import tkinter as tk
import logging
from typing import Optional, Callable
from ui.dialogs.icon_picker import IconPickerWindow
from database import get_db

logger = logging.getLogger(__name__)

class ContextActionHelper:
    @staticmethod
    def bind_icon_picker_context_menu(widget: tk.Widget, element_id: str, app=None, on_success: Optional[Callable] = None):
        """
        Gắn sự kiện Right-Click vào widget để mở IconPickerWindow.
        Khi chọn xong, cập nhật widget.config(image=...) và lưu vào database trực tiếp.
        """
        def _on_right_click(event):
            # Lấy module/screen từ widget chain hoặc mặc định
            module_name = getattr(widget, "MODULE_NAME", "App")

            # Trích xuất screen từ parent chain nếu có, hoặc để General
            screen_name = getattr(widget, "SCREEN_NAME", "General")

            def _on_icon_selected(icon_key: str):
                logger.info(f"[ContextAction] Nhận icon '{icon_key}' cho {element_id}")

                try:
                    from lib.db.services.icon_service import IconService
                    db = get_db()
                    icon_service = IconService(db.conn)

                    # Cập nhật usage trong db
                    # Xoá mapping cũ trước (hoặc để service lo việc trùng lặp)
                    existing = icon_service.get_usage_by_element(module_name, getattr(widget, "COMPONENT_TYPE", "button"), element_id)
                    if existing:
                        icon_service.delete_usage(existing.get('id') or existing.get('usage_id'))

                    success = icon_service.register_usage(icon_key, module_name, getattr(widget, "COMPONENT_TYPE", "button"), element_id)

                    if success:
                        # Cập nhật hiển thị UI lập tức
                        from ui.helpers.icon_helper import get_icon_helper
                        helper = get_icon_helper()

                        # Get icon
                        icon_data = icon_service.get_icon_by_key(icon_key)
                        fallback = icon_data.get('fallback_emoji', '') if icon_data else ""
                        new_img = helper.get_icon(icon_key, fallback=fallback)

                        # Lưu tham chiếu để tránh GC
                        if not hasattr(widget, '_ctx_image_ref'):
                            widget._ctx_image_ref = []

                        if not isinstance(new_img, str):
                            widget._ctx_image_ref = [new_img]
                            widget.config(image=new_img, text="")
                        else:
                            widget.config(image="", text=new_img)

                        # Refresh cache
                        if hasattr(helper, 'clear_cache'):
                            helper.clear_cache(icon_key)

                        if on_success:
                            on_success(icon_key)

                except Exception as e:
                    logger.error(f"[ContextAction] Lỗi lưu/cập nhật icon {icon_key} cho {element_id}: {e}")

            picker = IconPickerWindow(widget.winfo_toplevel(), _on_icon_selected, app=app)

        # Bind cho cả Windows (<Button-3>) và macOS/Linux cũ (<Button-2>)
        widget.bind("<Button-3>", _on_right_click)
        widget.bind("<Button-2>", _on_right_click)
