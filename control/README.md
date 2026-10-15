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

## 7. Governance Amendment v1 — pinned finalization verification

P0a/default behavior above is unchanged. A separate opt-in Integrator path verifies an
explicitly approved finalization of **one research task to GATED/PASSED/PASSED**. It does
not support arbitrary state edits, starting the next task, failed-state repair, protocol
changes, or automatic state writes. This narrow operation addresses canonical-recording
lag after final acceptance; BLOCKED/READY/IN_PROGRESS/TEST_PASSED/AUDIT_PASSED may be
finalized only when all preceding tasks exist and are GATED and final acceptance is bound.
The pointer may be the target itself or its immediate gated predecessor. All other task
entries and protocol fields are preserved. A generic snapshot PASS is not authorization.

```bash
"$PYTHON" -I -B control/check_scope.py --base "$BASE_SHA" --scope-manifest "$APPROVAL_JSON" \
  --state-transition /external/transition.json --authorization-sha256 "$RESEARCHER_PIN"
PYTHON="$PYTHON" bash control/gate.sh --base "$BASE_SHA" --scope-manifest "$APPROVAL_JSON" \
  --state-transition /external/transition.json --authorization-sha256 "$RESEARCHER_PIN"
```

These are read-only verifiers of the candidate state, not commands that apply a transition. Transition CLI requires Python `-I`; the gate selects it automatically for Python checks/tests. This removes candidate/PYTHONPATH dependency shadowing. It compiles verified validator source bytes directly and refuses root/control/test `.pyc` caches (which `-B` alone would still read). Use a clean isolated checkout; do not silently delete existing caches to force PASS. The selected Python environment and executable gate/checker must themselves be trusted. Transition verification prohibits Git clean/process filters and fsmonitor callbacks, compares all other BASE tracked files to actual physical bytes/Git executable flags (or pinned frozen byte/permission identities), and rejects extra Python files at repository root and under control/tests. Git replacement objects are disabled for baseline identity reads in both default and transition checks. Transition pytest disables conftest discovery and assertion-rewrite caches. Git baseline mode records executable flags rather than umask-specific write bits; special permission bits are refused, and frozen identities bind full ordinary permission bits. This mode deliberately requires an untransformed, regular-file checkout; sparse/symlink/submodule/transformed checkouts fail closed. Ignored data outside these critical code paths still needs filesystem protection.
Transition mode stops immediately on any check failure, before executing downstream validators/tests that scope may have rejected. Default P0a mode retains its existing aggregated diagnostics. The gate still requires scope, protocol hashes, state validation and control regressions;
when the transition regression suite exists in candidate or approved base, it is mandatory
as well. Existing legacy fixture repositories without that suite remain testable.
The amended controls must first be reviewed and integrated into a trusted baseline before
using this mode: control/check_scope.py, gate.sh, validate_state.py, protocol_hash.sh and
policy/hash manifests must match the approved BASE bytes. HEAD must equal BASE exactly.

### Approval and evidence contract

The Researcher must approve the exact external record digest through a trusted human
channel, together with actual task acceptance. `RESEARCHER_PIN` comes from that approval;
workers must not compute a new digest and present it as fresh approval after editing a
record. A `role` string, JSON record, external location, or hash **does not authenticate
human identity**. The operator/independent reviewer must verify actual authorization and
pin provenance. This is an operator-trusted, offline binding mechanism, not digital signing.
The current implementation authorization does not authorize a real P1-T5 transition.

`transition.json` requires exactly these fields (version is integer 1):

```json
{
  "version": 1,
  "operation": "FINALIZE_TASK",
  "role": "Researcher",
  "decision": "APPROVE_CANONICAL_TRANSITION",
  "reference": "actual direct human approval reference for this exact transition",
  "approved_at": "UTC ISO timestamp ending Z",
  "expires_at": "UTC ISO timestamp ending Z",
  "task_id": "exact task ID",
  "base_commit": "full approved HEAD SHA",
  "before_sha256": "SHA256 of BASE:control/task_state.yaml bytes",
  "after_sha256": "SHA256 of exact candidate control/task_state.yaml bytes",
  "delta": [{"path": ["tasks", "exact task ID", "status"], "before": "BLOCKED", "after": "GATED"}],
  "scope_sha256": "SHA256 of exact external approved scope JSON bytes",
  "authorization_evidence": {"path": "/external/human-approval.md", "sha256": "actual byte hash"},
  "final_acceptance": {"path": "/external/acceptance.json", "sha256": "actual byte hash"},
  "frozen_files": {}
}
```

The sample delta is schematic and incomplete: supply the entire stable list returned by
`semantic_delta(before, after)`, including pointer/stage and test/audit changes when they
actually change. Delta contains only string-key paths and exact old/new values; it cannot
execute expressions. `after` must equal a deep copy of `before` with only target status,
test, audit and current pointer/stage updated. Strict YAML rejects duplicate keys, anchors,
aliases and non-string scalar fields; strict JSON rejects duplicate/extra fields and NaN.
Expired/future approvals, replay on a new HEAD/base, wrong pre/post/scope/evidence hashes,
unknown task, skipped/missing prerequisite, unrelated changes or already GATED task fail.
State index content must be the approved old or new image; conflicting index and mode
changes fail. Hidden assume-unchanged/skip-worktree index flags are forbidden; every non-state index entry must equal BASE, including intent-to-add detection. No new token database or second canonical state store is introduced.
Rechecking the same candidate during the approval window is deliberately idempotent;
read-only gates do not consume approvals. After integration/another baseline, a new record
and human pin are required. Protect the pin/approval channel; coordinated malicious record
and pin replacement cannot be authenticated by this offline verifier.

`acceptance.json` is a separately pinned human-reviewed wrapper around existing final-gate
and auditor evidence; do not edit the original package to fit this format:

```json
{
  "task_id": "exact task ID",
  "verdict": "ACCEPTED",
  "test": "PASSED",
  "audit": "PASSED",
  "evidence": [{"path": "/absolute/path/to/final-gate-or-audit-evidence", "sha256": "actual byte hash"}]
}
```

Evidence references must be absolute regular files without symlink components. Approval,
scope and acceptance records must be outside checkout. References bind evidence bytes;
they do not execute tests, establish scientific truth, authenticate the auditor or verify
unlisted data dependencies. The Researcher/reviewer must check evidence sufficiency and
candidate/artifact identity. No scientific ETL is triggered by this governance gate.

### Exact scope with existing accepted files

The unchanged four-field scope manifest must contain the canonical state path and its exact
exception. In transition mode its allowlist must equal the actual Git change union, and
`frozen_files` must map **every other existing changed path** to an object with exactly `sha256` (approved byte hash) and `mode` (integer Unix permission bits, e.g. decimal 420 for 0644). Both must match; chmod drift fails.
A cumulative historical exception may cover an unchanged previously accepted untracked
test; it does not grant new test modification authority. Additional changed control,
protocol/raw paths and tracked protected files are forbidden even if listed/frozen.
Unrelated staged changes are forbidden. New/missing/modified frozen files, unused allowlist
paths or unlisted exceptions fail. Ignored/external artifacts require pinned acceptance
evidence references and read-only filesystem protection; Git scope cannot observe transient
or ignored writes. These verifiers perform no writes and cannot enforce external process
permissions. No switch of base, diagnostic policy override, hash bootstrap, or weaker test
assertions is an approved workaround.

Safe operator sequence: integrate/review governance code under its own authorization;
verify accepted research evidence and exact baseline; construct the proposed state bytes
outside canonical storage; obtain Researcher approval of the exact record/digest and later
write scope; an authorized Integrator applies only those approved bytes; run this mandatory
gate and independent review before any separately approved Git integration. Stop on stale
inputs, missing/expired approval or any failed check. Do not advance the next task.
