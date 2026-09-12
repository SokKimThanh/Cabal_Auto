import tkinter.messagebox as messagebox

class DialogService:
    """Service to handle UI dialogs and messageboxes, isolating UI components from controllers."""

    @staticmethod
    def show_info(title: str, message: str, parent=None):
        messagebox.showinfo(title, message, parent=parent)

    @staticmethod
    def show_error(title: str, message: str, parent=None):
        messagebox.showerror(title, message, parent=parent)

    @staticmethod
    def show_warning(title: str, message: str, parent=None):
        messagebox.showwarning(title, message, parent=parent)

    @staticmethod
    def ask_yes_no(title: str, message: str, parent=None) -> bool:
        return messagebox.askyesno(title, message, parent=parent)

    @staticmethod
    def open_create_preset_dialog(parent, class_id: int, skill_summary: dict, on_save_callback):
        """Opens the CreatePresetDialog and waits for it."""
        from ui.dialogs.create_preset_dialog import CreatePresetDialog

        # Safely find the toplevel window
        try:
            toplevel = parent.winfo_toplevel()
        except AttributeError:
            toplevel = parent

        dialog = CreatePresetDialog(
            parent=toplevel,
            class_id=class_id,
            skill_summary=skill_summary,
            on_save_callback=on_save_callback
        )

        if hasattr(parent, "wait_window"):
            parent.wait_window(dialog)

    @staticmethod
    def open_preset_dialog(parent, app_state):
        """Opens the PresetDialog."""
        from ui.dialogs.preset_dialog import PresetDialog
        PresetDialog(parent, app_state)
