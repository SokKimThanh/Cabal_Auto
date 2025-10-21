# Package

# NOTE:
# This package and several UI modules intentionally keep Python-side
# references to Tkinter PhotoImage objects (for example `self._image_refs`)
# to prevent Tcl/Tk garbage-collection of images. Some older code also
# used dynamic attributes on widget/root objects (e.g. `root._image_refs`).
# Those uses are intentional and annotated with `# type: ignore[attr-defined]`
# where necessary to keep static analyzers happy while preserving runtime
# behavior. Prefer storing images in the owning window's `_image_refs` list.
