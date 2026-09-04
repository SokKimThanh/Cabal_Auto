import os
import sqlite3
from typing import Any

import pytest


@pytest.fixture(scope="session")
def db_session():
    """SQLite in-memory database shared across the test session."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE dungeons (
            dungeonId TEXT PRIMARY KEY,
            name TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE monsters (
            id TEXT PRIMARY KEY,
            name TEXT,
            level INTEGER,
            exp INTEGER,
            hp INTEGER,
            defense INTEGER,
            attackRate INTEGER,
            defenseRate INTEGER,
            hpRecharge INTEGER,
            accuracy INTEGER,
            penetration INTEGER,
            damageReduction INTEGER,
            evasion INTEGER,
            resistCritRate INTEGER,
            primaryAttackMin INTEGER,
            primaryAttackMax INTEGER,
            secondaryAttackMin INTEGER,
            secondaryAttackMax INTEGER,
            ignoreAccuracy INTEGER,
            ignoreDamageReduction INTEGER,
            ignorePenetration INTEGER,
            absoluteDamage INTEGER,
            resistSkillAmp INTEGER,
            resistCritDamage INTEGER,
            resistSuppress INTEGER,
            resistSilence INTEGER,
            resistDiffDamage INTEGER,
            hpProportionDamage INTEGER,
            serverBossType INTEGER,
            dungeonId TEXT
        )
        """
    )

    sample_dungeons = [
        ("101", "101"),
        ("218", "218"),
        ("245", "245"),
        ("999", "999"),
    ]
    cursor.executemany(
        "INSERT OR REPLACE INTO dungeons (dungeonId, name) VALUES (?, ?)",
        sample_dungeons,
    )

    sample_monsters = [
        ("m1", "Quái Đen", 10, 100, 1200, 120, 500, 30, 0, 50, 10, 8, 20, 6, 90, 120, 80, 110, 5, 4, 10, 0, 0, 0, 0, 0, 0, 0, 0, "101"),
        ("m2", "Quái Đỏ", 12, 120, 1400, 140, 600, 35, 0, 55, 12, 10, 22, 7, 110, 140, 90, 120, 6, 5, 12, 0, 0, 0, 0, 0, 0, 0, 0, "101"),
        ("m3", "Quái Xanh", 15, 150, 1600, 160, 700, 40, 0, 60, 15, 12, 25, 8, 120, 150, 100, 130, 7, 6, 15, 0, 0, 0, 0, 0, 0, 0, 0, "218"),
        ("m4", "Quái Vàng", 18, 180, 2000, 180, 800, 45, 0, 65, 18, 14, 28, 10, 130, 170, 110, 140, 8, 7, 18, 0, 0, 0, 0, 0, 0, 0, 0, "218"),
        ("m5", "Quái Tím", 20, 200, 2400, 210, 900, 50, 0, 70, 20, 16, 30, 12, 140, 180, 120, 150, 9, 8, 20, 0, 0, 0, 0, 0, 0, 0, 0, "245"),
        ("m6", "Quái Trắng", 22, 220, 2600, 230, 1000, 55, 0, 75, 22, 18, 35, 14, 150, 200, 130, 170, 10, 9, 22, 0, 8, 15, 0, 0, 0, 0, 0, "245"),
        ("m7", "Quái Hồng", 25, 250, 3000, 260, 1100, 60, 0, 80, 25, 20, 40, 15, 160, 220, 140, 180, 12, 10, 25, 0, 10, 18, 0, 0, 0, 0, 0, "999"),
        ("m8", "Quái Bạc", 27, 270, 3300, 290, 1200, 65, 0, 85, 27, 22, 45, 18, 170, 230, 150, 200, 13, 11, 28, 0, 12, 20, 0, 0, 0, 0, 0, "999"),
        ("m9", "Quái Đom Đóm", 30, 300, 3800, 320, 1300, 70, 0, 90, 30, 25, 50, 20, 180, 250, 160, 220, 15, 12, 30, 0, 15, 25, 0, 0, 0, 0, 0, "101"),
        ("m10", "Quái Băng", 35, 350, 4500, 360, 1500, 75, 0, 95, 35, 30, 55, 22, 200, 280, 180, 240, 18, 15, 35, 0, 18, 30, 0, 0, 0, 0, 0, "218"),
        ("m11", "Quái Gỗ", 40, 400, 5200, 420, 1600, 80, 0, 100, 40, 35, 60, 25, 220, 300, 200, 260, 20, 17, 40, 0, 20, 35, 0, 0, 0, 0, 0, "245"),
        ("m12", "Quái Rồng", 45, 450, 6000, 460, 1700, 85, 0, 105, 45, 40, 65, 30, 250, 330, 220, 300, 22, 18, 45, 0, 22, 40, 0, 0, 0, 0, 0, "999"),
    ]

    cursor.executemany(
        """
        INSERT INTO monsters (
            id, name, level, exp, hp, defense, attackRate, defenseRate, hpRecharge,
            accuracy, penetration, damageReduction, evasion, resistCritRate,
            primaryAttackMin, primaryAttackMax, secondaryAttackMin, secondaryAttackMax,
            ignoreAccuracy, ignoreDamageReduction, ignorePenetration, absoluteDamage,
            resistSkillAmp, resistCritDamage, resistSuppress, resistSilence,
            resistDiffDamage, hpProportionDamage, serverBossType, dungeonId
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_monsters,
    )
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def db_reset(db_session):
    """Rollback the in-memory DB after each test to keep tests isolated and fast."""
    db_session.execute("BEGIN")
    yield
    db_session.rollback()


@pytest.fixture(autouse=True)
def mock_tk_headless(monkeypatch):
    """Replace GUI dependencies with lightweight stubs so tests run headlessly."""
    if os.environ.get("DISPLAY"):
        return
    try:
        import tkinter
        import tkinter.ttk as ttk
        import tkinter.messagebox as messagebox
        import tkinter.filedialog as filedialog
    except Exception:
        return

    class DummyVar:
        def __init__(self, value: Any = None):
            self._value = value
        def get(self):
            return self._value
        def set(self, value: Any):
            self._value = value
        def __call__(self, *args, **kwargs):
            return self.get()

    class DummyTk:
        def call(self, *args, **kwargs):
            return ''
        def eval(self, *args, **kwargs):
            return ''

    class DummyWidget:
        def __init__(self, *args, **kwargs):
            self.kwargs = dict(kwargs)
            self._text = kwargs.get('text', '')
            self._state = kwargs.get('state', 'normal')
            self._enabled = True
            self._image = None
            self._var = kwargs.get('variable')
            self._values = kwargs.get('values', [])
            self._selection = ()
            self._columns = list(kwargs.get('columns', []))
            self._config = {}
            self._value = ''
            self._items = []
            self.children = {}
            self._last_child_ids = {}
            self.tk = DummyTk()
            self._w = '.'
            self._name = 'dummy'
            if args and args[0] is not None and hasattr(args[0], 'tk'):
                self.master = args[0]
                self.tk = args[0].tk
                if self._w == '.':
                    self._w = f"{args[0]._w}.dummy"

        def __getitem__(self, key):
            if key == 'from' and 'from_' in self.kwargs:
                return self.kwargs['from_']
            return self._config.get(key, self.kwargs.get(key))

        def __setitem__(self, key, value):
            self._config[key] = value

        def pack(self, *args, **kwargs):
            return None
        def grid(self, *args, **kwargs):
            return None
        def place(self, *args, **kwargs):
            return None
        def pack_forget(self, *args, **kwargs):
            return None
        def destroy(self, *args, **kwargs):
            return None
        def configure(self, **kwargs):
            self.kwargs.update(kwargs)
            self._config.update(kwargs)
            for key, value in kwargs.items():
                setattr(self, key, value)
            return None
        def config(self, *args, **kwargs):
            if args and isinstance(args[0], dict):
                self.kwargs.update(args[0])
                self._config.update(args[0])
            for key, value in kwargs.items():
                setattr(self, key, value)
                self.kwargs[key] = value
                self._config[key] = value
            return None
        def title(self, *args, **kwargs):
            if args:
                self._title = str(args[0])
            return getattr(self, '_title', '')
        def cget(self, key, *args, **kwargs):
            return self.kwargs.get(key)
        def bind(self, *args, **kwargs):
            return None
        def selection_set(self, *args, **kwargs):
            return None
        def selection(self):
            return ()
        def get_children(self, *args, **kwargs):
            return []
        def delete(self, *args, **kwargs):
            if len(args) >= 2:
                self._items = []
            else:
                self._items = []
            self._value = ''
            self._selection = ()
            if '_tree_items' in self.__dict__:
                self._tree_items = {}
            return None
        def insert(self, *args, **kwargs):
            if len(args) >= 2 and args[0] == '' and ('text' in kwargs or 'values' in kwargs or len(args) >= 3):
                if '_tree_items' not in self.__dict__:
                    self._tree_items = {}
                iid = kwargs.get('iid') or f"item_{len(self._tree_items) + 1}"
                self._tree_items[iid] = {
                    'parent': args[0],
                    'index': args[1],
                    'text': kwargs.get('text', ''),
                    'values': kwargs.get('values', ()),
                }
                return iid

            if len(args) >= 2:
                index, value = args[0], args[1]
            elif kwargs.get('index') is not None and kwargs.get('string') is not None:
                index, value = kwargs['index'], kwargs['string']
            else:
                return None

            if index in (None, '', 'end', 'END'):
                self._items.append(str(value))
            else:
                try:
                    idx = int(index)
                except (TypeError, ValueError):
                    idx = 0
                self._items.insert(max(0, idx), str(value))

            self._value = ''.join(str(item) for item in self._items)
            return None
        def item(self, *args, **kwargs):
            return {}
        def heading(self, *args, **kwargs):
            return None
        def column(self, *args, **kwargs):
            return None
        def get(self, *args, **kwargs):
            if len(args) == 0:
                if hasattr(self, '_scale_val'):
                    return self._scale_val
                return self._value
            if len(args) == 1:
                idx = args[0]
                try:
                    idx = int(idx)
                except (TypeError, ValueError):
                    return self._value
                if idx < len(self._items):
                    return self._items[idx]
                return ''
            if len(args) >= 2:
                start, end = args[0], args[1]
                try:
                    start_idx = int(start)
                    end_idx = int(end)
                except (TypeError, ValueError):
                    return []
                return self._items[start_idx:end_idx + 1]
            return self._value
        def set(self, *args, **kwargs):
            if args:
                self._value = str(args[0])
                try:
                    self._scale_val = float(args[0])
                except (ValueError, TypeError):
                    pass
                self._items = [self._value] if self._value else []
            return None
        def selection_set(self, *args, **kwargs):
            if not args:
                self._selection = ()
                return None
            self._selection = tuple(args)
            return None
        def curselection(self):
            return tuple(self._selection or ())
        def selection(self):
            return tuple(self._selection or ())
        def getvar(self, *args, **kwargs):
            return None
        def setvar(self, *args, **kwargs):
            return None
        def event_generate(self, *args, **kwargs):
            return None
        def focus_force(self, *args, **kwargs):
            return None
        def lift(self, *args, **kwargs):
            return None
        def winfo_exists(self, *args, **kwargs):
            return True
        def winfo_rootx(self, *args, **kwargs):
            return 0
        def winfo_rooty(self, *args, **kwargs):
            return 0
        def winfo_height(self, *args, **kwargs):
            return 0
        def winfo_screenwidth(self, *args, **kwargs):
            return 1280
        def winfo_screenheight(self, *args, **kwargs):
            return 720
        def update_idletasks(self, *args, **kwargs):
            return None
        def after(self, *args, **kwargs):
            return 0
        def after_cancel(self, *args, **kwargs):
            return None
        def withdraw(self, *args, **kwargs):
            return None
        def deiconify(self, *args, **kwargs):
            return None
        def attributes(self, *args, **kwargs):
            return None
        def protocol(self, *args, **kwargs):
            return None
        def transient(self, *args, **kwargs):
            return None
        def grab_set(self, *args, **kwargs):
            return None
        def wait_window(self, *args, **kwargs):
            return None
        def __getattr__(self, name):
            return lambda *a, **k: None

    class DummyToplevel(DummyWidget):
        pass

    class DummyNotebook(DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._tab_opts = {}

        def add(self, child, *args, **kwargs):
            kw = dict(kwargs)
            if args and isinstance(args[0], dict):
                kw.update(args[0])
            self._tab_opts[child] = kw
            return None

        def tab(self, tab_id, option=None, **kwargs):
            if tab_id not in self._tab_opts:
                self._tab_opts[tab_id] = {}
            if kwargs:
                self._tab_opts[tab_id].update(kwargs)
            if option:
                return self._tab_opts[tab_id].get(option)
            return self._tab_opts[tab_id]

    class DummyCombobox(DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._values = kwargs.get('values', [])
        def config(self, *args, **kwargs):
            if 'values' in kwargs:
                self._values = kwargs['values']
            return super().config(*args, **kwargs)

    for name in [
        "Tk", "Toplevel", "Frame", "Label", "Entry", "Button", "Text", "Scale",
        "Scrollbar", "Menu", "Spinbox", "Canvas", "PhotoImage", "Listbox",
        "Checkbutton", "Radiobutton", "LabelFrame", "OptionMenu", "Message",
        "PanedWindow", "LabelFrame", "Dialog", "FileDialog"
    ]:
        if hasattr(tkinter, name):
            monkeypatch.setattr(tkinter, name, DummyWidget if name not in {"Tk", "Toplevel"} else (DummyWidget if name == "Tk" else DummyToplevel))

    monkeypatch.setattr(tkinter, "StringVar", DummyVar)
    monkeypatch.setattr(tkinter, "Tcl", DummyTk)
    monkeypatch.setattr(tkinter, "BooleanVar", DummyVar)
    monkeypatch.setattr(tkinter, "IntVar", DummyVar)
    monkeypatch.setattr(tkinter, "DoubleVar", DummyVar)
    monkeypatch.setattr(tkinter, "Variable", DummyVar)

    for name in ["Notebook", "Combobox", "Treeview", "Style", "Separator", "Progressbar", "Scrollbar", "Label", "Button", "Entry", "Frame"]:
        if hasattr(ttk, name):
            target = DummyWidget
            if name == "Notebook":
                target = DummyNotebook
            elif name == "Combobox":
                target = DummyCombobox
            monkeypatch.setattr(ttk, name, target)

    messagebox.askyesno = lambda *args, **kwargs: True
    messagebox.showwarning = lambda *args, **kwargs: None
    messagebox.showerror = lambda *args, **kwargs: None
    messagebox.showinfo = lambda *args, **kwargs: None

    filedialog.askopenfilename = lambda *args, **kwargs: ""
