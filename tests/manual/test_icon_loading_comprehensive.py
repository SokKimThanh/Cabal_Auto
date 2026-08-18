"""
Comprehensive Icon Loading Test

Tests all potential issues:
1. Path resolution
2. PIL/Pillow loading of .ico files
3. PhotoImage creation
4. Garbage collection prevention
5. Icon sizing and quality
"""
import pytest
import sys
from pathlib import Path
import tkinter as tk

pytestmark = [
    pytest.mark.manual,
    pytest.mark.gui
]

# Add project to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

try:
    from lib.ui.icon_helper import IconHelper
except ImportError:
    IconHelper = None  # type: ignore

def test_icon_loading():
    """Comprehensive icon loading test."""
    
    print("=" * 70)
    print("ICON LOADING DIAGNOSTIC TEST")
    print("=" * 70)
    
    # Test 1: Path Resolution
    print("\n[TEST 1] Path Resolution")
    print("-" * 70)
    
    icon_helper = IconHelper()
    
    for i, icon_dir in enumerate(icon_helper.icon_dirs, 1):
        exists = "✓ EXISTS" if icon_dir.exists() else "✗ MISSING"
        print(f"  Directory {i}: {exists}")
        print(f"    Path: {icon_dir}")
        
        if icon_dir.exists():
            icon_files = list(icon_dir.glob("*.ico"))
            print(f"    .ico files: {len(icon_files)}")
            if icon_files:
                print(f"    Examples: {', '.join([f.name for f in icon_files[:5]])}")
    
    # Test 2: PIL/Pillow Availability
    print("\n[TEST 2] PIL/Pillow Support")
    print("-" * 70)
    
    try:
        from PIL import Image, ImageTk
        print("  ✓ PIL/Pillow is installed")
        print(f"    PIL Version: {Image.__version__ if hasattr(Image, '__version__') else 'Unknown'}")
    except ImportError as e:
        print(f"  ✗ PIL/Pillow NOT available: {e}")
        print("    Install with: pip install Pillow")
    
    # Test 3: Icon Loading WITHOUT Tkinter
    print("\n[TEST 3] Icon Loading (No Tkinter - Should Fail)")
    print("-" * 70)
    
    test_icons = ['add', 'delete', 'save', 'cancel', 'refresh']
    
    for icon_name in test_icons:
        result = icon_helper.get_icon(icon_name, fallback='?', size=16)
        is_emoji = isinstance(result, str)
        status = "EMOJI" if is_emoji else "IMAGE"
        print(f"  [{status}] {icon_name:10} -> {type(result).__name__}")
    
    print("\n  Note: Icons will be emoji because no Tkinter root exists yet")
    
    # Test 4: Icon Loading WITH Tkinter
    print("\n[TEST 4] Icon Loading (With Tkinter Root)")
    print("-" * 70)
    
    root = tk.Tk()
    root.withdraw()  # Hide window
    
    # Create new IconHelper instance (fresh cache)
    icon_helper2 = IconHelper()
    
    loaded_icons = {}
    
    for icon_name in test_icons:
        result = icon_helper2.get_icon(icon_name, fallback='?', size=16)
        is_emoji = isinstance(result, str)
        is_photoimage = hasattr(result, 'width')  # PhotoImage has width() method
        
        loaded_icons[icon_name] = result
        
        if is_emoji:
            print(f"  [EMOJI] {icon_name:10} -> '{result}'")
        else:
            print(f"  [IMAGE] {icon_name:10} -> PhotoImage (type: {type(result).__name__})")
    
    # Test 5: Icon Sizing
    print("\n[TEST 5] Icon Sizing")
    print("-" * 70)
    
    for size in [16, 24, 32]:
        icon = icon_helper2.get_icon('add', fallback='➕', size=size)
        if not isinstance(icon, str):
            print(f"  Size {size}x{size}: PhotoImage created ✓")
        else:
            print(f"  Size {size}x{size}: Fallback to emoji '{icon}'")
    
    # Test 6: Cache Performance
    print("\n[TEST 6] Cache Performance")
    print("-" * 70)
    
    import time
    
    # First load (cache miss)
    start = time.perf_counter()
    icon1 = icon_helper2.get_icon('save', size=16)
    first_load_time = (time.perf_counter() - start) * 1000
    
    # Second load (cache hit)
    start = time.perf_counter()
    icon2 = icon_helper2.get_icon('save', size=16)
    cached_load_time = (time.perf_counter() - start) * 1000
    
    print(f"  First load (cache miss): {first_load_time:.2f}ms")
    print(f"  Second load (cache hit): {cached_load_time:.2f}ms")
    print(f"  Speed improvement: {first_load_time / cached_load_time:.0f}x faster")
    print(f"  Same object: {icon1 is icon2}")
    
    # Test 7: Visual Display Test
    print("\n[TEST 7] Visual Display Test")
    print("-" * 70)
    print("  Creating test window with icons...")
    
    # Create visible window
    root.deiconify()
    root.title("Icon Display Test")
    root.geometry("500x400")
    root.configure(bg='#f0f0f0')
    
    tk.Label(
        root,
        text="Icon Display Test - All Icons Should Show",
        font=('Arial', 14, 'bold'),
        bg='#f0f0f0'
    ).pack(pady=10)
    
    # Create buttons with icons
    button_frame = tk.Frame(root, bg='#f0f0f0')
    button_frame.pack(pady=20)
    
    for icon_name in test_icons:
        icon = loaded_icons[icon_name]
        is_emoji = isinstance(icon, str)
        
        frame = tk.Frame(button_frame, bg='#f0f0f0')
        frame.pack(pady=5)
        
        tk.Label(
            frame,
            text=f"{icon_name}:",
            font=('Arial', 10),
            bg='#f0f0f0',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        if is_emoji:
            # Emoji button
            btn = tk.Button(
                frame,
                text=icon,
                font=('Arial', 12),
                bg='#2196F3',
                fg='white',
                width=3,
                height=1
            )
            btn.pack(side='left', padx=5)
            
            tk.Label(
                frame,
                text="(Emoji fallback)",
                font=('Arial', 9),
                fg='#f44336',
                bg='#f0f0f0'
            ).pack(side='left')
        else:
            # Icon button
            btn = tk.Button(
                frame,
                image=icon,
                bg='#4CAF50',
                width=30,
                height=30
            )
            btn.image = icon  # Keep reference!
            btn.pack(side='left', padx=5)
            
            tk.Label(
                frame,
                text=f"(PhotoImage {type(icon).__name__})",
                font=('Arial', 9),
                fg='#4CAF50',
                bg='#f0f0f0'
            ).pack(side='left')
    
    # Test 8: Garbage Collection Test
    print("\n[TEST 8] Garbage Collection Test")
    print("-" * 70)
    
    test_frame = tk.Frame(root, bg='#f0f0f0')
    test_frame.pack(pady=20)
    
    tk.Label(
        test_frame,
        text="GC Test (icon reference managed):",
        font=('Arial', 10, 'bold'),
        bg='#f0f0f0'
    ).pack()
    
    # Create button WITHOUT keeping reference (should fail)
    icon_no_ref = icon_helper2.get_icon('warning', fallback='⚠️', size=16)
    btn_no_ref = tk.Button(
        test_frame,
        image=icon_no_ref if not isinstance(icon_no_ref, str) else None,
        text="NO REF" if isinstance(icon_no_ref, str) else "",
        bg='#FF9800',
        width=30,
        height=30
    )
    # DON'T keep reference: btn_no_ref.image = icon_no_ref
    btn_no_ref.pack(side='left', padx=5)
    
    tk.Label(
        test_frame,
        text="vs",
        font=('Arial', 10),
        bg='#f0f0f0'
    ).pack(side='left', padx=10)
    
    # Create button WITH reference (should work)
    icon_with_ref = icon_helper2.get_icon('check', fallback='✓', size=16)
    btn_with_ref = tk.Button(
        test_frame,
        image=icon_with_ref if not isinstance(icon_with_ref, str) else None,
        text="WITH REF" if isinstance(icon_with_ref, str) else "",
        bg='#4CAF50',
        width=30,
        height=30
    )
    btn_with_ref.image = icon_with_ref  # Keep reference!
    btn_with_ref.pack(side='left', padx=5)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_tested = len(test_icons)
    icons_loaded = sum(1 for icon in loaded_icons.values() if not isinstance(icon, str))
    emojis_used = total_tested - icons_loaded
    
    print(f"  Icons tested: {total_tested}")
    print(f"  PhotoImages loaded: {icons_loaded}")
    print(f"  Emoji fallbacks: {emojis_used}")
    print(f"  Cache size: {len(icon_helper2._cache)} items")
    print()
    
    if icons_loaded == total_tested:
        print("  ✓ SUCCESS: All icons loaded as PhotoImage")
    elif icons_loaded > 0:
        print(f"  ⚠ PARTIAL: {icons_loaded}/{total_tested} icons loaded")
    else:
        print("  ✗ FAILURE: No icons loaded, all using emoji fallback")
    
    print("\n  Check the window above to verify visual display")
    print("  Close window to end test")
    print("=" * 70)
    
    root.mainloop()

if __name__ == '__main__':
    test_icon_loading()
