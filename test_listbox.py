import tkinter as tk
from ui.components.image_library_component import ImageLibraryComponent
from ui.models.image_library_model import ImageLibraryModel

class DummyApp:
    def _t(self, key, **kwargs):
        return key

root = tk.Tk()
app = DummyApp()
model = ImageLibraryModel()
comp = ImageLibraryComponent(root, app, model, None, lambda: {'icon.png': {'sidebar_button'}})
comp.pack()
comp._update_image_listbox(['icon.png', 'build.png'])
print(comp.img_listbox.get(0, tk.END))
