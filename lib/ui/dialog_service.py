import tkinter as tk
import tkinter.messagebox as messagebox
import threading

class DialogService:
    """
    Centralized service for displaying UI dialogs.
    Replaces direct calls to tkinter.messagebox to reduce UI framework coupling
    and allow for future custom-styled popups (e.g., matching UI Style V2).
    """
    _default_parent = None

    @classmethod
    def set_default_parent(cls, root: tk.Tk):
        """
        Sets the global default parent window for all dialogs.
        Ensures popups do not appear behind the main window.
        """
        cls._default_parent = root

    @classmethod
    def _get_parent(cls, parent=None):
        return parent if parent is not None else cls._default_parent

    @classmethod
    def _run_on_main_thread(cls, func, *args, **kwargs):
        """
        Executes a messagebox function safely on the main thread if possible.
        """
        # If there's no root window set, just run it directly (might crash if off-thread, but best effort)
        if not cls._default_parent:
            return func(*args, **kwargs)

        # If we are already on the main thread, or we can't reliably detect it,
        # just run it. (A simple check is if current thread is MainThread)
        if threading.current_thread() is threading.main_thread():
            return func(*args, **kwargs)
        else:
            # We are on a background thread. Schedule it on the main thread.
            # Note: This will not block and return a result. It's strictly fire-and-forget.
            cls._default_parent.after(0, lambda: func(*args, **kwargs))

    @classmethod
    def show_info(cls, title: str, message: str, parent=None):
        parent = cls._get_parent(parent)
        cls._run_on_main_thread(messagebox.showinfo, title, message, parent=parent)

    @classmethod
    def show_error(cls, title: str, message: str, parent=None):
        parent = cls._get_parent(parent)
        cls._run_on_main_thread(messagebox.showerror, title, message, parent=parent)

    @classmethod
    def show_warning(cls, title: str, message: str, parent=None):
        parent = cls._get_parent(parent)
        cls._run_on_main_thread(messagebox.showwarning, title, message, parent=parent)

    @classmethod
    def ask_yes_no(cls, title: str, message: str, parent=None) -> bool:
        """
        Displays a Yes/No dialog.
        WARNING: This is a blocking call and MUST be executed from the main Tkinter thread.
        Calling this from a background thread may cause application freezing or crashes.
        """
        parent = cls._get_parent(parent)
        # Cannot easily wrap a blocking call asynchronously without complicated event loops.
        # Run directly, relying on the caller to ensure they are on the main thread.
        return messagebox.askyesno(title, message, parent=parent)
