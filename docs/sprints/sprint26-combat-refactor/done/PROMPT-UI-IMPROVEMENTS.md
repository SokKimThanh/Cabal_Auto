Bản Mô Tả Thiết Kế Cải Tiến — Trợ Lý Săn Cabal
Tổng quan kiến trúc layout
Giữ nguyên cấu trúc 3 vùng: Sidebar trái · Header trên · Vùng nội dung chính. Toàn bộ dùng dark theme, nền tổng #0f0f0f, surface panel #1a1a1a, border phân tách #2a2a2a.

1. Sidebar
Hiện tại: Sidebar bắt đầu từ giữa màn hình, không có logo, không có icon, không có trạng thái active/hover rõ ràng. Phần trên sidebar là một vùng đen trống lớn.

Cải tiến:

Sidebar rộng 200px, chiều cao 100vh, nền #111111, border-right 1px solid #2a2a2a
Đầu sidebar: Logo/icon Cabal (kiếm hoặc biểu tượng game) + tên "Cabal Assistant" in hoa nhỏ 10px tracking-widest text-[#4ade80], padding top 16px
Menu items có icon SVG bên trái (16px), label text 13px, padding 10px 16px, border-radius 6px khi hover/active
⚡ Thiết lập nhanh
🐉 Quản lý quái vật
⚔️ Quản lý kỹ năng
📚 Quản lý thư viện
📊 Thống kê
❓ Hỗ trợ
Active state: nền #1f2d1f, text #4ade80, đường dọc 3px solid #4ade80 ở cạnh trái
Hover state: nền #1a1a1a, text #d1d5db
Group label ("Quản lý", "Thống kê") in 10px uppercase tracking-wider text-[#555], không clickable, margin-top 16px
2. Header
Hiện tại: Thanh tìm kiếm dài chiếm ~55% chiều rộng nhưng không có label. Vùng giữa header trống. Nút "Bắt đầu săn" active dù chưa chọn cửa số. Dropdown ngôn ngữ "vi" bị nhỏ và tách biệt.

Cải tiến:

Header cao 48px, nền #111111, border-bottom 1px solid #2a2a2a
Bên trái: Dropdown chọn cửa số — width 320px, placeholder "Chọn cửa số...", icon map-pin bên trái, nền #1a1a1a, border 1px solid #333, border-radius 6px; nút refresh icon cạnh bên
Giữa header (thay vì để trống): 3 stat chip nhỏ hiển thị realtime — 🟢 Kết nối, Server: --, Nhân vật: -- — mỗi chip nền #1f1f1f, text 12px text-[#888]
Bên phải: Nút "Bắt đầu săn" — khi chưa chọn cửa số: disabled, nền #1f2d1f, text #555, cursor not-allowed, tooltip "Vui lòng chọn cửa số trước"; khi đã chọn: nền #16a34a hover #15803d, text trắng, icon play
Dropdown ngôn ngữ gộp vào một menu icon 🌐 nhỏ gọn hơn
3. Vùng nội dung chính
Hiện tại: Có khoảng trống lớn phía trên (khoảng 1/3 chiều cao) trước khi xuất hiện các panel — do sidebar và nội dung không bắt đầu từ cùng chiều cao. Các panel nổi trên nền xám nhạt không đồng nhất với dark theme.

Cải tiến:

Nội dung bắt đầu ngay dưới header, không có khoảng trống thừa
Nền vùng content #0f0f0f đồng nhất — bỏ vùng nền xám #e5e5e5 của giao diện gốc
Layout grid: cột trái 600px · cột phải chiếm phần còn lại, gap 8px, padding 12px
4. Panel — Danh Sách Sẽ Đánh (trái trên)
Hiện tại: Tab bar 3 màu khác nhau (xám, xanh dương, xanh lá) không nhất quán. Listbox trắng nổi bật giữa giao diện tối. Nút điều khiển (▲▼✓✗) màu đỏ/xanh thô, không có tooltip.

Cải tiến:

Panel wrapper: nền #1a1a1a, border 1px solid #2a2a2a, border-radius 8px
Tab bar thống nhất: tất cả tabs nền #111, text #888, khi active nền #1f2d1f text #4ade80, border-bottom 2px solid #4ade80, border-radius 6px 6px 0 0
Listbox: nền #111, border 1px solid #2a2a2a, text #d1d5db, font 13px; mỗi row hover nền #1f1f1f
Empty state khi không có mục: icon target mờ + text "Chưa có mục tiêu — nhấn + để thêm" màu #555, căn giữa
Nút điều khiển bên phải: thay bằng icon buttons 28×28px — Move Up ↑, Move Down ↓, Enable/Disable toggle, Delete — tất cả nền #222, border 1px solid #333, icon màu #888, hover icon màu #fff; có tooltip khi hover
5. Panel — Mục Tiêu & Trạng Thái (phải trên)
Hiện tại: "CHỜ" là text xanh lá thô không có visual container. Placeholder ảnh [KHÔNG CÓ ẢNH] chỉ là text trong box tối. Progress bar máu gần như vô hình. Stats (Cấp Độ, Máu, Phòng Thủ) hiển thị label nhưng không có giá trị.

Cải tiến:

Status banner thay thế dòng "Sẵn sàng săn / Mục tiêu: Trống":
Trạng thái đang chờ: badge pill ● Đang chờ nền #292218 text #f59e0b
Trạng thái sẵn sàng: badge pill ● Sẵn sàng nền #1f2d1f text #4ade80
Trạng thái đang săn: badge pill ● Đang săn nền #1e2d3d text #38bdf8 với pulse animation
Khu vực target info chia 2 cột: trái là ảnh quái (80×80px, border-radius 8px, nền #111, icon placeholder khi không có ảnh); phải là tên quái 16px font-semibold, trạng thái badge
Progress bar máu: height 8px, background #1f1f1f, fill gradient #dc2626 → #f97316, border-radius 4px, kèm text HP: --/-- (--%) bên phải, font 11px text-[#888]
Stats row dùng grid 3 cột, mỗi stat: label 10px text-[#555] uppercase, value 14px text-[#d1d5db] font-mono; giá trị hiển thị -- khi chưa có data
Nút "Áp dụng Cài đặt Săn": width đủ rộng, icon save, nền #16a34a, không thay đổi so với gốc nhưng thêm loading state khi đang lưu
6. Panel — Combo Chain (trái dưới)
Hiện tại: Checkbox "Bật Auto Combo" text gần như không đọc được (tối trên tối). Label C: và CD: không rõ nghĩa. Các slot Combo Chain và Buff Lane trông như form thô, không có visual grouping.

Cải tiến:

Header row: Checkbox styled rõ ràng — checkbox custom border #4ade80, khi checked nền #4ade80 icon tick trắng; label "Bật Auto Combo" text #d1d5db 13px; phím tắt "Alt+3" hiển thị như keyboard badge kbd nền #222 border #444 text #aaa; dropdown icon ⚙ bên phải
Mỗi Combo Chain slot là một card: nền #111, border 1px solid #2a2a2a, border-radius 6px, padding 8px
Label nhỏ "Chain 1/2/3/4" màu #555 10px
Dropdown kỹ năng: nền #0f0f0f, border #333, text #d1d5db
Stat row dưới: ⏱ Cast: --s và 🔄 CD: --s thay vì C: CD:
Section separator dạng divider giữa Combo Chain và Buff Lane, kèm label "Buff Lanes" 10px uppercase text-[#555]
Buff Lane slots cùng card style nhưng nền khác biệt nhẹ #161616 để phân biệt vai trò
7. Panel — Thống Kê Hiệu Suất Kỹ Năng (phải dưới)
Hiện tại: Table header hiển thị đúng nhưng empty state "Chưa có dữ liệu" bị mờ, khó đọc. Không có visual phân tách giữa rows.

Cải tiến:

Table header: nền #111, text 11px uppercase tracking-wide text-[#555], border-bottom 1px solid #2a2a2a, sticky khi scroll
Empty state: icon chart-bar mờ 32px + text "Chưa có dữ liệu kỹ năng" text-[#444] 13px + sub-text "Bắt đầu săn để thu thập thống kê" text-[#333] 11px, căn giữa panel
Khi có data: rows xen kẽ nền #1a1a1a / #111, hover nền #1f1f1f; cột "Tỷ lệ %" hiển thị mini inline bar (width tỷ lệ với giá trị, nền #4ade80 opacity 60%, height 4px)
Scrollbar styled: width 4px, thumb #333, hover #555
8. Status Bar (dưới cùng)
Hiện tại: Text "Đang kiểm tra CSDL..." không có loading indicator, không có thêm thông tin nào.

Cải tiến:

Chiều cao 24px, nền #0a0a0a, border-top 1px solid #1f1f1f, padding 0 12px
Bên trái: spinner 10px + text trạng thái animation dots "Đang kiểm tra CSDL..."
Bên phải: v2.x.x · CSDL: ✓ · 0 lỗi text 11px text-[#444]
Token màu tổng hợp
Token	Giá trị	Dùng cho
bg-base	#0f0f0f	Nền tổng
bg-surface	#1a1a1a	Panel, card
bg-elevated	#111111	Sidebar, header, input
border	#2a2a2a	Đường phân tách
text-primary	#d1d5db	Nội dung chính
text-muted	#6b7280	Label phụ
text-subtle	#374151	Placeholder
accent-green	#4ade80	Active, thành công
accent-green-bg	#1f2d1f	Active background
accent-amber	#f59e0b	Cảnh báo, chờ
accent-blue	#38bdf8	Đang chạy
danger	#dc2626	Máu, xóa
Bạn muốn tôi build ngay theo spec này không?

build ra thử 1 bản




Đã build xong. Giao diện bao gồm:

Sidebar với logo, icon cho từng mục, active state xanh lá, group labels
Header với dropdown chọn cửa số, 3 status chip giữa, nút "Bắt đầu săn" bị disable cho đến khi chọn dungeon
Panel Danh sách đánh — tab bar thống nhất, empty state có icon hướng dẫn, nút điều khiển có tooltip
Panel Mục Tiêu — status badge (idle/ready/hunting), placeholder quái, HP bar gradient, stats grid 3 cột với giá trị --
Panel Combo Chain — checkbox tùy chỉnh, card cho từng chain với icon ⏱/🔄, Buff Lanes section riêng
Panel Thống Kê — table có striped rows, inline bar chart cho cột Tỷ lệ %
Status bar — spinner + version + CSDL status
Font Inter + JetBrains Mono cho data. Scrollbar tùy chỉnh mảnh. 