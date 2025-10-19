"""Demo: Template Lock/Unlock với Save Ngay

Test tính năng:
1. Template locked khi chọn
2. Click Edit → unlock + badge "Đang chỉnh sửa" (orange)
3. Click Save → lưu ngay + copy image + badge "Đã lưu" (green)
4. Auto-lock sau khi save

Usage:
    python tests/demo_template_save.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import messagebox

def main():
    print("=" * 70)
    print("Demo: Template Edit with Instant Save")
    print("=" * 70)
    print("\nHướng dẫn test:")
    print("1. Mở Library Manager → Tab 'Thư Viện Quái Vật'")
    print("2. Chọn quái 'Coc go~' (có nhiều templates)")
    print("3. Chọn một template từ danh sách bên trái")
    print("=" * 70)
    print("\n✅ KIỂM TRA:")
    print("   - Fields bị KHÓA (không thể edit)")
    print("   - Icon button: ✏️ (Edit)")
    print("   - Tooltip: 'Sửa template'")
    print()
    print("4. Nhấn nút ✏️")
    print("=" * 70)
    print("\n✅ KIỂM TRA:")
    print("   - Fields MỞ KHÓA (có thể edit)")
    print("   - Icon button: 💾 (Save)")
    print("   - Tooltip: 'Nhấn để lưu template'")
    print("   - Badge: '🟧 Đang chỉnh sửa' (nền cam)")
    print()
    print("5. Chỉnh sửa tên, threshold, hoặc region")
    print()
    print("6. Nhấn nút 💾")
    print("=" * 70)
    print("\n✅ KIỂM TRA:")
    print("   - Fields tự động KHÓA lại")
    print("   - Icon button: ✏️ (Edit)")
    print("   - Badge: '🟩 Đã lưu' (nền xanh lá, 3 giây)")
    print("   - File: lib/data/monsters.json được update")
    print("   - Ảnh từ tmp/ copy sang assets/images/monsters/")
    print()
    print("=" * 70)
    print("\n📁 Files để check:")
    print("   - lib/data/monsters.json (dữ liệu template)")
    print("   - assets/images/monsters/ (ảnh đã copy)")
    print()
    print("=" * 70)
    print("\n🔄 Test lại:")
    print("   - Nhấn ✏️ → Chỉnh sửa → Nhấn 💾")
    print("   - Verify badge: Đang chỉnh sửa → Đã lưu")
    print()
    print("=" * 70)
    
    # Confirm to continue
    root = tk.Tk()
    root.withdraw()
    
    response = messagebox.askyesno(
        "Start Test",
        "Ready to test?\n\n"
        "App will open Library Manager.\n"
        "Follow the instructions printed in terminal."
    )
    
    if not response:
        print("\n❌ Test cancelled")
        root.destroy()
        return
    
    root.destroy()
    
    # Launch app
    print("\n🚀 Launching app...")
    print("Please follow the steps above to test template save feature.")
    print()
    
    try:
        import app_gui
        # This will start the main app
    except Exception as e:
        print(f"\n❌ Failed to launch app: {e}")
        print("\nManual launch:")
        print("   python app_gui.py")

if __name__ == '__main__':
    main()
