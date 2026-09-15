with open("app_gui.py", "a") as f:
    f.write('''
def main():
    import tkinter as tk
    from lib.system.instance_lock import SingleInstanceLock
    from lib.ui.dialog_service import DialogService

    instance_lock = SingleInstanceLock("CabalAutoHunt_v1")
    if not instance_lock.acquire():
        root = tk.Tk()
        root.withdraw()
        DialogService.show_error(
            "Application Already Running",
            "Another instance is already running!",
            parent=root,
        )
        root.destroy()
        return

    try:
        from lib.core.app_container import AppContainer
        root = tk.Tk()
        container = AppContainer()
        app = App(root=root, di_container=container)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
    finally:
        instance_lock.release()

if __name__ == "__main__":
    main()
''')
