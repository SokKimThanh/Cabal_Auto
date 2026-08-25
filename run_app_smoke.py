import tkinter as tk
from app_gui import App

def test_app():
    app = App()

    # Let the after callbacks run
    app.update()

    # Close
    app.on_close()

if __name__ == '__main__':
    test_app()
    print("App created and closed successfully")
