#!/usr/bin/env python3
"""Test that combobox displays window list correctly."""

import tkinter as tk
from tkinter import ttk
import logging

logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_combobox_display():
    print("\n" + "="*60)
    print("TEST: Combobox with Normal State")
    print("="*60)
    
    root = tk.Tk()
    root.title("Combobox Test")
    root.geometry("400x200")
    
    # Frame for combobox
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    
    # Label
    label = tk.Label(frame, text="Select Game Window:", font=("Arial", 10))
    label.pack(anchor="w", pady=(0, 5))
    
    # Combobox with normal state (not readonly)
    combo_var = tk.StringVar()
    combo = ttk.Combobox(frame, textvariable=combo_var, state="normal")
    combo.pack(fill="x", pady=(0, 20))
    
    # Set initial values
    combo["values"] = ["CABAL", "Other Window", "Another Game"]
    print(f"Set combobox values: {combo['values']}")
    
    # Instruction label
    info = tk.Label(frame, 
        text="Click in the combobox below to see the dropdown list appear immediately.\n"
        "With state='normal', the list shows without needing to click arrow.",
        bg="lightyellow", padx=10, pady=10, justify="left", wraplength=350
    )
    info.pack(fill="x", pady=(0, 10))
    
    # Buttons to simulate app behavior
    btn_frame = tk.Frame(frame)
    btn_frame.pack(fill="x", pady=(10, 0))
    
    def refresh_windows():
        print("Button clicked: Refresh windows")
        # Simulate refresh
        combo["values"] = ["CABAL (HWND:2689684)", "Updated Window"]
        combo_var.set("")  # Clear selection
        print(f"Updated combobox values: {combo['values']}")
        status.config(text="Found 2 window(s). Select and click Start.")
    
    def select_window():
        selected = combo_var.get()
        print(f"Button clicked: Start with selection: '{selected}'")
        if selected:
            status.config(text=f"Selected: {selected} ✓", fg="green")
        else:
            status.config(text="Please select a window!", fg="red")
    
    btn1 = tk.Button(btn_frame, text="🔄 Refresh Windows", command=refresh_windows)
    btn1.pack(side="left", padx=(0, 10))
    
    btn2 = tk.Button(btn_frame, text="▶ Start Hunt", command=select_window)
    btn2.pack(side="left")
    
    # Status
    status = tk.Label(frame, text="Click Refresh to populate list", 
                     font=("Arial", 9), fg="blue")
    status.pack(fill="x", pady=(10, 0))
    
    print(f"\nInitial state:")
    print(f"  combo['values']: {combo['values']}")
    print(f"  combo.get(): '{combo.get()}'")
    print(f"  combo_var.get(): '{combo_var.get()}'")
    
    print("\nTry clicking in the combobox - the dropdown should appear immediately!")
    print("="*60 + "\n")
    
    root.mainloop()

if __name__ == "__main__":
    test_combobox_display()
