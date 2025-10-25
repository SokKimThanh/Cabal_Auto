"""Minimal test to isolate empty window issue."""

import tkinter as tk

print("\n=== Test 1: Basic Tk + Toplevel ===")
print("Creating main window...")
root = tk.Tk()
root.title("Main Window")
root.geometry("300x200")

def test_toplevel():
    print("\nCreating Toplevel...")
    top = tk.Toplevel(root)
    top.title("Toplevel Window")
    top.geometry("250x150")
    
    label = tk.Label(top, text="Toplevel created")
    label.pack(pady=50)
    
    print("Toplevel created successfully")
    print(f"Root children: {len(root.winfo_children())}")
    print("Check taskbar - should be +1 window only")

btn = tk.Button(root, text="Open Toplevel", command=test_toplevel)
btn.pack(pady=80)

print("\nMain window created")
print("Click button to test Toplevel creation")
print("Expected: +1 window (Toplevel only)")
print("Bug: +2 windows (Toplevel + empty window)")

root.mainloop()
