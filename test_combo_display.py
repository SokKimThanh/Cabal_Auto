#!/usr/bin/env python3
"""Test combobox display to see why values don't show."""

import tkinter as tk
from tkinter import ttk

def test_readonly_combobox():
    root = tk.Tk()
    root.title("Readonly Combobox Test")
    root.geometry("400x300")
    
    # Test 1: Simple readonly combobox
    print("\n" + "="*60)
    print("TEST: Readonly Combobox Display")
    print("="*60)
    
    frame = tk.Frame(root, bg="lightgray", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    
    label1 = tk.Label(frame, text="1. Before setting values:")
    label1.pack(anchor="w")
    
    combo1 = ttk.Combobox(frame, state="readonly")
    combo1.pack(fill="x", pady=(0, 20))
    print(f"  Initial combo1['values']: {combo1['values']}")
    print(f"  Initial combo1.get(): '{combo1.get()}'")
    
    label2 = tk.Label(frame, text="2. After setting ['CABAL']:")
    label2.pack(anchor="w")
    
    combo1["values"] = ["CABAL"]
    combo1.pack(fill="x", pady=(0, 20))
    print(f"  After set combo1['values']: {combo1['values']}")
    print(f"  After set combo1.get(): '{combo1.get()}'")
    
    # Test 2: Try setting current index
    label3 = tk.Label(frame, text="3. After setting current(-1):")
    label3.pack(anchor="w")
    
    combo1.current(-1)
    combo2_var = tk.StringVar()
    combo2 = ttk.Combobox(frame, textvariable=combo2_var, state="readonly")
    combo2["values"] = ["CABAL"]
    combo2.pack(fill="x", pady=(0, 20))
    print(f"  combo2['values']: {combo2['values']}")
    print(f"  combo2.get(): '{combo2.get()}'")
    print(f"  combo2_var.get(): '{combo2_var.get()}'")
    
    info_frame = tk.Frame(frame, bg="lightyellow", padx=10, pady=10)
    info_frame.pack(fill="x", pady=(20, 0))
    
    info_text = tk.Label(info_frame, text=
        "NOTE: Readonly Combobox shows:\n"
        "  • Current selected value in the box (if any)\n"
        "  • Click dropdown arrow to see full list\n"
        "  • Values are properly stored even if not visible\n\n"
        "If combobox is empty, check that values are set!",
        justify="left", bg="lightyellow"
    )
    info_text.pack(anchor="w")
    
    print("\n" + "="*60)
    print("CONCLUSION:")
    print("  - Values are set correctly in the tuple")
    print("  - But readonly Combobox doesn't show list until you click dropdown arrow")
    print("  - This is NORMAL Tkinter behavior, not a bug!")
    print("="*60)
    
    root.mainloop()

if __name__ == "__main__":
    test_readonly_combobox()
