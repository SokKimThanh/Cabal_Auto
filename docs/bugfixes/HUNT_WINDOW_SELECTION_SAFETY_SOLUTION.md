# Giai phap an toan khi chon cua so de Hunt

**Ngay:** 2026-09-01  
**Trang thai:** De xuat de trien khai  
**Pham vi:** Chon cua so game, bat dau hunt, focus cua so va kiem tra template

## Van de

Hunt co the bat dau khi nguoi dung chon mot cua so khong phai Cabal. Kiem tra hien tai dua vao chuoi `"cabal"` trong process name **hoac** window title. Cach nay khong an toan vi title co the chua ten du an, file, hoac text "Cabal" trong VS Code va cac ung dung khac.

Sau khi hunt da bat dau, `HuntOrchestrator` con co fallback focus theo `window_title` neu focus theo `hwnd` that bai. Fallback nay co the focus sai cua so trung title, trong khi auto hotkey/tap van tiep tuc gui input.

Combobox hien tai quet toan bo cua so va tu dong chon muc dau tien. Khi chua co cua so Cabal, hanh vi nay tao cam giac nguoi dung da chon duoc muc hop le, du thuc te chua xac nhan game.

Template rong cung chi duoc phat hien khi khoi dong hunt. He thong da co thong bao i18n, nhung can chan truoc khi worker va OpenCV bat dau doc file.

## Ket luan ky thuat

`HWND` khong tu minh chung minh day la cua so Cabal. No chi la dinh danh cua mot cua so Windows tai mot thoi diem. Xac minh an toan can ket hop:

1. `HWND`: rang buoc thao tac voi dung cua so ma nguoi dung chon.
2. PID va process name truy van lai tu `HWND`: chung minh cua so do thuoc tien trinh Cabal duoc chap nhan.
3. Trang thai cua so: con ton tai, hien thi, khong bi thu nho/off-screen va co bounds hop le.
4. Danh sach template kha dung: co it nhat mot template duong dan ton tai va doc duoc.

Neu bat ky dieu kien nao that bai, he thong phai **fail closed**: khong focus, khong minimize GUI, khong tao worker hunt, va khong gui phim/chuot.

## Yeu cau hanh vi

### Combobox cua so

- Chi hien thi cua so co process name nam trong allowlist cau hinh, mac dinh la `cabal.exe`. Neu phien ban game co executable khac, them ten do vao allowlist co chu y.
- Neu khong tim thay cua so Cabal, combobox rong va Start bi khoa.
- Khong tu dong chon cua so bat ky. Chi tu dong chon khi quet duoc dung mot cua so Cabal, hoac khi `hwnd` da luu van xac minh dung PID/process sau khi quet lai.
- Moi item luu day du `hwnd`, `pid`, `proc`, `title`, `bounds`. Display text phai phan biet cac cua so trung title, vi du: `Cabal (cabal.exe, PID 1234)`.
- Khi refresh, neu `hunt_selected.hwnd` khong con trong danh sach Cabal hop le, xoa selection, xoa bounds, dat combobox rong va khoa Start.

### Nut Start

Start chi enabled khi co selection hop le va co template kha dung. Du truong hop UI cap nhat cham, `_validate_hunt_prerequisites` van phai kiem tra lai toan bo dieu kien ngay truoc `start_hunt`; nut bi khoa la UX, validation la hang rao bat buoc.

Thu tu validation:

1. `hunt_selected` phai la dict va co `hwnd` la so nguyen duong.
2. `hwnd` phai con ton tai (`WindowManager.is_window_valid`) va `get_window_info(hwnd)` phai tra ve thong tin.
3. PID truy van tu `hwnd` phai trung `hunt_selected["pid"]`; process name truy van lai phai thuoc allowlist Cabal. Khong tin `proc` da luu trong config vi no co the cu.
4. Cua so phai visible, enabled, khong minimized/off-screen, bounds hop le.
5. `hwnd` da xac minh phai ton tai trong `win_items` cua lan scan hien tai.
6. Phai co it nhat mot template dang enabled, file ton tai va co the nap. Khong coi `template_path` khong rong la hop le neu file khong ton tai.

Ket qua loi can dung i18n, bao gom `error_no_cabal_window` va `error_no_templates`; nen bo sung cac key rieng cho `error_no_window_selected`, `error_window_changed`, `error_window_unavailable`, va `error_invalid_template` de nguoi dung sua dung nguyen nhan.

### Khi hunt dang chay

- Focus va gui input chi dung `cfg["window_hwnd"]` da xac minh.
- Bo fallback focus theo title trong `HuntOrchestrator`. Title khong la dinh danh duy nhat va co the focus sai cua so.
- Trước moi chu ky co gui input, xac minh lai `hwnd` con hop le va process cua no van la Cabal. Neu that bai: dat `hunt_running = False`, log `window_validation_failed`, thong bao qua `schedule_ui_task`, va khong gui input nua.
- Khong truy cap hay `imread` template khi validation template that bai. Log chi mot su kien cau truc thay vi de OpenCV phat warning lap lai.

## Thiet ke de xuat

Tao mot dich vu nho, vi du `CabalWindowValidationService`, de ca `AppWindowController`, `AppStateController` va `HuntOrchestrator` dung chung mot quy tac. Dich vu nay khong duoc goi Tkinter va tra ve ket qua du lieu thuan.

```python
@dataclass
class WindowValidationResult:
    is_valid: bool
    code: str
    window: Optional[dict] = None


def validate_selected_cabal_window(selected, known_items, allowed_processes):
    if not isinstance(selected, dict) or not isinstance(selected.get("hwnd"), int):
        return WindowValidationResult(False, "no_window_selected")

    info = WindowManager().get_window_info(selected["hwnd"])
    if info is None or not WindowManager().is_window_valid(selected["hwnd"]):
        return WindowValidationResult(False, "window_unavailable")
    if info.pid != selected.get("pid"):
        return WindowValidationResult(False, "window_changed")
    if info.process_name.lower() not in allowed_processes:
        return WindowValidationResult(False, "no_cabal_window")
    if not info.is_visible or not info.is_enabled or info.is_minimized or info.is_offscreen:
        return WindowValidationResult(False, "window_unavailable")
    if selected["hwnd"] not in {item["hwnd"] for item in known_items}:
        return WindowValidationResult(False, "window_changed")
    return WindowValidationResult(True, "ok", to_window_dict(info))
```

Title chi dung de hien thi cho nguoi dung. Neu can ho tro nhieu launcher/region, allowlist process phai duoc cau hinh ro rang; khong dung quy tac substring `"cabal" in title` lam dieu kien cho phep.

## Ke hoach thay doi

1. Cap nhat `AppWindowController._list_windows` de lay process name tu `WindowManager`, loc theo allowlist, va giu `hwnd` lam khoa selection.
2. Cap nhat `on_hunt_find_windows` de xoa selection thay vi chon cua so dau tien khi khong co selection Cabal da xac minh.
3. Cap nhat `on_window_combo_selected` de chi ghi config sau khi dich vu validation tra ve hop le; gui bounds tu `WindowInfo` moi nhat.
4. Cap nhat `AppStateController._validate_hunt_prerequisites` de goi dich vu validation va kiem tra template that su kha dung. Khong doc `window_title` trong config nhu nguon xac minh.
5. Dat state cua Start tu ket qua validation sau scan, sau chon, va sau refresh. Van giu validation dong bo trong `_request_start_hunt`.
6. Cap nhat `HuntOrchestrator` bo fallback theo `title`; su dung duy nhat `window_hwnd`. Kiem tra lai truoc input va dung an toan khi HWND/PID/process thay doi.
7. Cap nhat logger de ghi mot event ro rang, vi du `[BLOCKED] Hunt not started | Reason: no_cabal_window`, thay cho warning OpenCV lap lai.

## Kiem thu

Them unit test khong can Tkinter/Windows that bang mock `WindowManager`:

| Tinh huong | Ket qua mong doi |
| --- | --- |
| Chua chon combobox | Start bi khoa; validation tra `no_window_selected` |
| Chon Notepad/VS Code | Khong xuat hien trong combobox Cabal; Start bi khoa |
| Title VS Code chua "Cabal" | Bi tu choi vi process khong nam allowlist |
| `hwnd` da dong | Bi tu choi; khong focus, khong gui input |
| `hwnd` tro den PID khac | Bi tu choi voi `window_changed` |
| Cabal bi minimize/off-screen | Bi tu choi; khong gui input |
| Cabal hop le, template rong | Hien `error_no_templates`; orchestrator khong start |
| Cabal hop le, template file mat/hong | Hien `error_invalid_template`; khong goi matcher |
| Cabal hop le va template hop le | Hunt bat dau va chi focus/gui input vao dung HWND |
| Cua so doi sau khi hunt start | Hunt dung truoc lan gui input tiep theo |

Chay toi thieu: `pytest tests/unit/features/hunt tests/unit/test_action_bar.py`. Cac test Tkinter tren Linux headless can chay qua `xvfb-run -a pytest <test_paths>` theo cau hinh du an.

## Tieu chi nghiem thu

- Khong the bam Start khi combobox rong, khi chon cua so khong phai Cabal, khi HWND stale, hoac khi khong co template kha dung.
- Tieu de cua so co chu "Cabal" khong du de bat dau hunt.
- Sau khi start, khong co duong code nao focus theo `window_title` hoac gui input neu `window_hwnd` khong qua xac minh.
- Log chi ro ly do block/dung va khong con spam `cv::imread` cho template khong hop le.
- Cac test tren bao phu ca before-start va during-run validation.

## Ngoai pham vi

Bao cao VisionEngine neu ve mutation frame, timeout worker va homography la cac rui ro co that nhung doc lap voi an toan chon cua so. Nen xu ly bang ticket rieng: them `inplace_render=False`, dung `threading.Event` thay cho `time.sleep` khi stop, va tu choi homography non-convex/qua lon truoc khi tao bounding box.

## Tai lieu lien quan

- `ui/controllers/app_state_controller.py`
- `ui/controllers/app_window_controller.py`
- `lib/features/hunt/hunt_orchestrator.py`
- `lib/system/window_manager.py`
- `lib/i18n/translations.py`