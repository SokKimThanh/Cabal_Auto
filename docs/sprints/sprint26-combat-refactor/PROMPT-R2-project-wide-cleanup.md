# Session Prompt R2: Project-Wide Cleanup And Inventory

**Timebox:** 25-30 phút mỗi batch; project lớn thì chạy nhiều batch theo cùng prompt  
**Priority:** High  
**Dependency:** Không có. Có thể chạy độc lập trên branch hiện tại.

## Objective

Rà soát và làm sạch toàn bộ file/thư mục của project Cabal Auto theo bằng chứng sử dụng thực tế. Cleanup phải giảm rác, file trùng, artifact tạm và tài liệu lỗi thời mà không làm mất source, dữ liệu runtime, database, asset hoặc test còn được dùng.

Session này ưu tiên inventory và classification. Không được xóa hàng loạt theo tên file, tuổi file hoặc cảm nhận “có vẻ không dùng”. Mọi xóa/di chuyển phải có manifest trước/sau và lý do truy vết được.

## Safety Contract

### Được dọn tự động sau khi xác nhận

- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `*.pyc`, `*.pyo`.
- Artifact tạm trong `tmp/` và `tmp_*/` nếu không còn process giữ file, không nằm trong asset/config/database và quá hạn theo policy batch.
- Log runtime đã quá hạn retention nếu user/project policy cho phép; không xóa log cần cho issue đang điều tra.
- File build/test output đã được `.gitignore` và không được test/runtime tham chiếu.

### Chỉ di chuyển hoặc xóa sau repository search + review

- File Python duplicate/legacy, module compatibility, launcher cũ, script one-off.
- Patch/reject/original files như `*.orig`, `*.rej`, `*.patch`, `*.diff`.
- Tài liệu trùng, tài liệu cũ trong root hoặc docs; ưu tiên chuyển vào `docs/archive/` và cập nhật index trước khi xóa.
- Empty directories không có vai trò runtime.
- Test script ở root hoặc test duplicate ngoài `tests/`.

### Không được xóa hoặc sửa nội dung trong session này nếu chưa có task riêng

- `lib/data/*.json`, `*.db`, `*.sql`, `monsters.db`, `monsters.db.sql`.
- `assets/`, `views/`, `ui/`, `lib/`, `dialogs/`, `tests/` source đang được import hoặc test.
- `config/`, `hunt_config.json`, `monsters.json`, `skills.json`, template/vision assets và user settings.
- `docs/archive/` chỉ được reorganize có manifest; không purge lịch sử.
- `.git/`, `.venv/`, virtual environment, dependency lock/config của tool.

Không dùng `git reset --hard`, `git checkout --`, `Remove-Item -Recurse` trên scope chưa review, hoặc command xóa hàng loạt không có dry-run.

## Phase 0: Preflight

1. Ghi branch, commit, dirty worktree và xác nhận thay đổi có sẵn của user; không overwrite/revert chúng.
2. Đọc `.gitignore`, `README.md`, `PROJECT_STRUCTURE.md`, `docs/INDEX.md` và rules trong `00-global-rules.md`.
3. Tạo inventory read-only gồm path, loại file, kích thước, git-tracked/untracked/ignored, last modified và lý do dự kiến.
4. Chụp baseline: `git status --short`, test smoke/import hiện tại và số lượng file theo thư mục.

Nếu baseline không chạy được, ghi nhận failure nhưng vẫn được tiếp tục inventory; không dùng cleanup để che failure.

## Phase 1: Detect Candidates

Phân loại mỗi candidate vào đúng một nhóm:

- `KEEP_RUNTIME`: source, config, DB, assets, test, launcher đang dùng.
- `KEEP_REFERENCE`: docs lịch sử/contract/roadmap cần giữ.
- `ARCHIVE_CANDIDATE`: docs/patch/report cũ cần chuyển archive.
- `DELETE_SAFE`: cache/artifact được phép xóa và đã xác nhận.
- `DELETE_REVIEW`: file có thể bỏ nhưng cần owner/user review.
- `UNKNOWN`: không đủ bằng chứng, tuyệt đối không xóa.

Bằng chứng bắt buộc cho code/script:

- Repository search theo module path, filename, symbol, console/launcher entry point.
- Kiểm tra import/re-export, dynamic import, `importlib`, plugin/config reference, subprocess và test discovery.
- Với file CLI/launcher, search README/docs/CI/task/batch/PowerShell references.
- Với docs, kiểm tra inbound links từ README/index/roadmap và links nội bộ.
- Với data/assets, search path/filename và kiểm tra loader glob/DB references.

Không coi “không có kết quả text search” là đủ bằng chứng khi có dynamic path hoặc runtime discovery.

## Phase 2: Dry-Run Manifest

Tạo artifact `docs/maintenance/project-cleanup-manifest.md` gồm:

- `KEEP`: path, lý do, evidence.
- `ARCHIVE`: source path, destination path, links cần cập nhật.
- `DELETE_SAFE`: path, loại artifact, lý do an toàn.
- `DELETE_REVIEW`: path, risk, reviewer decision cần có.
- `UNKNOWN`: path, câu hỏi còn thiếu.
- Summary số lượng bytes/files trước và dự kiến sau cleanup.

Không thực hiện DELETE_REVIEW hoặc UNKNOWN trong cùng batch. Nếu có hơn 20 candidate hoặc candidate nằm trong source/runtime, dừng sau manifest để review scope.

## Phase 3: Apply Conservative Cleanup

Chỉ apply các mục `DELETE_SAFE` đã có trong manifest và các mục archive đã xác định destination:

- Dùng thao tác file có thể review qua `git diff/status`.
- Khi archive docs, cập nhật links/index trong cùng change; không tạo bản sao trùng lâu dài.
- Không sửa logic, API, schema, config values hoặc formatting diện rộng.
- Không xóa directory nếu chưa xác nhận sau thao tác directory không còn file cần giữ.
- Giữ log/manifest thay đổi để rollback thủ công bằng patch có phạm vi rõ.

## Phase 4: Validation

Chạy các kiểm tra phù hợp với phạm vi:

```powershell
py -m compileall -q app_gui.py lib ui dialogs views
py -m pytest --collect-only -q
py -m pytest tests/unit/ui/controllers/test_library_manager_controller.py -q
py -m pytest tests/unit/test_target_bar_detector.py -q
py -m pytest tests/unit/features/hunt/test_runtime_monster_queue.py tests/unit/features/hunt/test_scene_monster_detector.py -q
```

Nếu cleanup chạm launcher/docs only, vẫn phải chạy import/collection tối thiểu và kiểm tra broken links nội bộ nếu tool có sẵn. Nếu chạm source, chạy focused tests của module đó trước khi test rộng hơn.

Kiểm tra sau cleanup:

- Không còn import/module/path reference tới file đã archive/delete.
- Không mất file config/database/asset/test ngoài manifest.
- `git status` chỉ chứa thay đổi trong manifest và scope cleanup.
- App import/startup smoke không fail do missing module/path.
- Không có duplicate canonical file tạo thành hai nguồn sự thật.

## Batch Boundary Gate

**PASSED khi:**

- Inventory toàn project trong scope batch có classification và evidence.
- Chỉ `DELETE_SAFE` được xóa; mọi code/data không chắc chắn được giữ.
- Archive có destination và links/index đã cập nhật.
- Manifest trước/sau khớp thay đổi thực tế.
- Focused validation pass hoặc failure được ghi rõ là baseline/unrelated.

**BLOCKED khi:**

- Không phân biệt được file active với file legacy/dynamic.
- Candidate có thể là config/database/asset đang dùng nhưng chưa có owner xác nhận.
- Cleanup yêu cầu thay đổi logic hoặc xóa code chưa chứng minh unused.
- Có dirty user changes xung đột với thao tác archive/delete.
- Validation phát hiện import, test discovery, startup hoặc path regression.

Báo cáo `PASSED`, `BLOCKED_REVIEW_REQUIRED`, `BASELINE_FAILURE` hoặc `REVERTED` kèm manifest, danh sách path đã thay đổi và command validation.
