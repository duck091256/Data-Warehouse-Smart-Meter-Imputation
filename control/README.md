# Research Control Layer

Control layer kiểm chứng kỹ thuật cho **Beyond Synthetic Missingness — Smart-Meter Imputation**.
CLI và tiêu chí áp dụng chung cho Codex, Antigravity hoặc executor khác; không cấp quyền theo nhà cung cấp.
Research protocol, canonical task state và protected-path policy hiện hành không được P0a thay đổi.

## 1. Phạm vi bảo đảm

`gate.sh` kiểm tra working tree Git, scope được duyệt, protocol hashes, state snapshot
bằng validator hiện có và control regression tests. Linked worktree có `.git` là file được hỗ trợ.
`GATE = PASS` chỉ là kết quả kỹ thuật: không phải independent audit, human approval,
quyền commit/merge hoặc quyền chuyển research task sang `GATED`.
Validator hiện có vẫn có giới hạn về linear ordering, transition history và evidence;
P0a không sửa các semantics này.

| Thành phần | Trách nhiệm |
|---|---|
| `check_scope.py` | So union của branch/index/worktree/untracked changes với allowlist và protected policy từ approved base |
| `protocol_hash.sh` | In hoặc verify đúng ba protocol entries; `--save` là thao tác quản trị riêng |
| `validate_state.py` | Validator snapshot hiện hành, giữ nguyên trong P0a |
| `gate.sh` | Tổng hợp các kiểm tra trên, không tự bootstrap manifest hoặc ghi research state |
| `protected_paths.txt`, `protocol_hashes.txt`, `task_state.yaml` | Giữ nguyên; ngoại lệ P0a không cho phép sửa các file này |

## 2. Inputs tin cậy và quyền phê duyệt

Gate bắt buộc có `--base FULL_SHA` và `--scope-manifest EXTERNAL_JSON`.
Base phải là SHA đầy đủ của một commit tồn tại, là ancestor của `HEAD`, được người giao việc
chọn rõ ràng. Không tự suy từ `HEAD~1`, `origin/main` hoặc merge-base của nhánh remote.
Scope policy được đọc từ `BASE:control/protected_paths.txt`, không lấy bản candidate tự sửa.

Scope manifest đặt **ngoài checkout candidate** (kể cả sau resolve symlink), do operator
cung cấp từ phạm vi người dùng đã duyệt. Bốn trường bắt buộc, không có trường thừa hoặc trùng:

```json
{
  "base_commit": "<full-approved-commit-SHA>",
  "authority": "<reference to explicit human authorization>",
  "allowed_files": ["etl/example.py", "tests/test_example.py"],
  "protected_exceptions": ["tests/test_example.py"]
}
```

Đây là ví dụ cấu trúc, **không phải approval cho các file ví dụ**. Các paths là exact paths
relative với repo, không phải glob hay directory prefix. Không chấp nhận traversal,
Git administrative paths, duplicate entries hoặc exceptions ngoài allowlist.
Exception cho protocol, raw, canonical state, policy hoặc hash manifest bị từ chối trong P0a.
Danh sách protected mặc định không bị sửa hoặc mở rộng quyền bằng chính candidate.

`authority` là reference để review, **không phải chữ ký hay cơ chế xác thực**.
Việc đặt file ngoài checkout không tự biến file thành approval tin cậy. Operator/Auditor
phải đối chiếu nguồn approval, base và danh sách paths. Worker không được tự cấp ngoại lệ.
Khi kiểm toán thay đổi chính control scripts, phải dùng trusted tooling hoặc review độc lập;
chạy candidate gate không chứng minh bản thân candidate không bị can thiệp.

## 3. Chạy kiểm chứng

Chọn Python environment đã cài dependencies trong `requirements.txt`.
`PYTHON` nhận executable/path, không nhận shell command kèm flags. Gate dùng cùng executable
cho Python validators và `python -m pytest`; không gọi standalone `pytest` trên PATH.
Có thể tái dùng environment ngoài worktree bằng đường dẫn tuyệt đối.

```bash
export PYTHON=/path/to/venv/bin/python
BASE_SHA='<full-approved-commit-SHA>'
APPROVAL_JSON=/path/outside/checkout/approved-scope.json
bash control/gate.sh --base "$BASE_SHA" --scope-manifest "$APPROVAL_JSON"
```

Kiểm tra scope riêng:

```bash
"$PYTHON" -B control/check_scope.py --base "$BASE_SHA" --scope-manifest "$APPROVAL_JSON"
bash control/protocol_hash.sh --verify
```

Git errors, base/policy/scope inputs không hợp lệ, paths ngoài scope hoặc protected paths
thiếu exception đều trả exit code khác 0. Policy override `--rules` không được dùng trong Git gate.
`--files ... [--rules ...]` chỉ là diagnostic denylist check; output ghi rõ không kiểm chứng Git scope.
Gọi scope/gate không có inputs bắt buộc sẽ FAIL; các prompt cũ dùng lệnh không tham số cần
operator bổ sung approved inputs, không được mặc định một base hoặc bỏ scope check.

## 4. Changed files và giới hạn

Scope lấy union của:

1. Final tree diff `BASE` tới `HEAD` cho committed changes.
2. Staged/index diff.
3. Unstaged/working-tree diff.
4. Non-ignored untracked files.

Rename detection bị tắt để kiểm tra cả source và destination như delete/add.
Git paths dùng NUL separators, giữ đúng spaces, quotes, Unicode, tabs và newlines.
Union vẫn phát hiện index/worktree changes ngay cả khi chúng triệt tiêu nhau trong net diff.
Repository redirect environment variables được loại khỏi Git inspection để không đọc nhầm index/repo.

Không kiểm tra toàn bộ commit history nếu thay đổi đã được revert trước `HEAD`.
Ignored files, external dataset, nested submodule contents và writes thoáng qua không được
Git diff bao quát. Raw-data immutability vẫn cần read-only filesystem/sandbox riêng;
scope PASS không chứng minh dữ liệu raw chưa từng bị ghi. P0a không chạy pipeline hoặc scan dataset.

`--check-outputs [--task ID]` là kiểm tra presence/non-empty cho output specifications hiện có.
Task chưa có specification sẽ FAIL; kiểm tra này không chứng minh scientific acceptance,
content correctness hoặc freshness. Gate không tự chạy research-task tests.

## 5. Hash verification và tests

Hash manifest phải có đúng một SHA-256 entry cho mỗi file:
`TASK_PLAN.md`, `RESEARCH_PLAN.md`, `control/protected_paths.txt`.
Thiếu/rỗng/comment-only, malformed, duplicate, extra path, missing file hoặc hash mismatch đều FAIL.
`--verify` và gate không ghi manifest; gate không bao giờ gọi `--save`.
`--save` vẫn là thao tác quản trị chỉ dùng sau approval riêng cho protocol/policy amendment,
không thuộc quyền P0a và không được dùng để chữa verification failure.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  "$PYTHON" -B -m pytest tests/test_control_layer.py -q -p no:cacheprovider
```

Gate tắt bytecode, pytest cache và third-party plugin autoload. Regression tests tạo commits
và linked worktrees **chỉ trong disposable repositories ở temporary directory**, không commit
vào dự án hoặc thao tác worktree người dùng. Nested gate fixtures dùng một test nhỏ để tránh
đệ quy test suite. Fixtures kiểm tra cả gate PASS và các failure paths thực sự.
Không cần local raw configuration hoặc interim artifacts để chạy control tests.

## 6. Bàn giao

Ghi candidate base/diff identity, approved scope, Python executable, commands và results khi bàn giao.
Đối chiếu lại scope, protocol hashes và state sau test. Independent Auditor review cùng candidate;
canonical state và Git integration chỉ đổi theo authorization riêng. Sửa code sau kiểm chứng
làm mất hiệu lực evidence liên quan, cần chạy lại kiểm tra bị ảnh hưởng.
