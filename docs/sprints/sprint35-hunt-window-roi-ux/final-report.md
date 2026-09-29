# Sprint 35: Hunt Window ROI UX - Final Report & Technical Debt

## 1. Tổng hợp Audit (01-05)
- **Window Selection (01):** Xác định sự thiếu đồng bộ giữa UI và engine vision khi lấy hwnd, dẫn đến fallback sai cửa sổ.
- **ROI Capture Source (02):** Phân tích `ScreenCapture`, xác định nguồn capture không bám theo cửa sổ đã chọn mà capture fullscreen/vùng không chính xác.
- **Debug Vision (03):** Xác định `VisionSnapshotDebugger` chồng chéo vẽ box (engine đã vẽ nhưng UI vẽ lại) và thiếu thông tin text.
- **Scan Buttons (04):** Đặc tả hành vi 4 nút quét (combo_bar, self_stats, minimap, hunt_area) và xác định các nút chưa được implement.
- **UI Guidance (05):** Phân tích lớp phủ hướng dẫn vẽ ROI và các vấn đề liên quan.

## 2. Các vấn đề đã giải quyết (Fixed)
Dựa trên các prompt từ 06 đến 11:
- Đã sửa luồng ràng buộc (binding) window từ UI xuống engine.
- Đã căn chỉnh `ScreenCapture` bám theo chính xác cửa sổ được chọn.
- Đã hiển thị thông tin window (Title, PID) một cách rõ ràng.
- Đã cập nhật nhãn (labels) và hành vi của các nút Scan.
- Đã thêm lớp phủ hướng dẫn (Guidance Overlay) khi vẽ ROI.
- Đã có tính năng xem trước kết quả Scan (Result preview).

## 3. Technical Debt (Chưa fix / Còn nợ)
Từ ô "UNKNOWN" của Audit 04:
- Dữ liệu đọc cho `self_stats`: Nút được khai báo trên UI nhưng hoàn toàn thiếu implementation (luồng đọc giá trị máu/mana).
- Dữ liệu đọc cho `minimap`: Chưa có implementation cho vision engine quét `minimap`.
- Cả 4 nút quét đều thiếu cơ chế validation tọa độ ngay tại UI tại thời điểm thiết lập.

## 4. Rủi ro còn lại (Residual Risks)
- Multi-monitor (Đa màn hình).
- DPI scaling (Tỉ lệ co giãn màn hình trên Windows).
- Capture latency (Độ trễ capture ở một số môi trường).

## 5. Đề xuất Sprint 36
1. Auto-detect DPI scaling.
2. Multi-monitor support.
3. Auto-tune threshold cho skills detection.

## 6. Commit Hashes cho 11 Prompts
```text
90b6edc - Merge pull request #771 from SokKimThanh/fix/window-manager-lock-scan-15324136501786917625
87757c0 - fix(vision): lock selected game window for all hunt scans
d52568c - docs(sprint35): audit debug vision image source and overlays
76af067 - docs(sprint35): audit game window selection flow in Hunt tab
33c691d - docs(sprint35): audit roi scanner image source and coordinate origin
538b092 - docs(sprint35): audit ui guidance layer for roi scan workflow
684e168 - docs(sprint35): audit behavior spec for 4 hunt scan buttons
be005ef - docs(sprint35): add execution prompts for hunt window roi ux remediation
5c7b23e - fix(ui): Bring selected game window to foreground on ROI draw
```
