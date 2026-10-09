# Research Control Layer

Thư mục này chứa toàn bộ hệ thống governance, state machine, kiểm tra phạm vi (scope check) và cổng kiểm soát (gate) cho dự án nghiên cứu **Beyond Synthetic Missingness — Smart-Meter Imputation**.

---

## 1. Mục tiêu kiến trúc

Hệ thống Control Layer được thiết kế nhằm đảm bảo:
1. **Tính bất biến của Research Protocol**: Ngăn chặn tình trạng agent tự ý thay đổi protocol, nới lỏng định nghĩa hoặc sửa đổi các file hướng dẫn.
2. **Kỷ luật phạm vi (Scope Discipline)**: Ngăn chặn sửa đổi các file/thư mục được bảo vệ (`data/raw/`, `TASK_PLAN.md`, `control/`, `tests/test_control_layer.py`).
3. **Kiểm soát trạng thái tuyến tính (Linear Gating)**: Không cho phép bắt đầu task tiếp theo khi task trước chưa đạt trạng thái `GATED` qua kiểm toán độc lập.
4. **Tính tái lập & Truy xuất nguồn gốc**: Đảm bảo toàn bộ quy trình kiểm thử và hash được thực thi định lượng.

---

## 2. Thành phần chi tiết

| File | Chức năng | Cách sử dụng |
|---|---|---|
| `task_state.yaml` | Quản lý trạng thái vòng đời của từng task (BLOCKED, READY, IN_PROGRESS, TEST_PASSED, GATED...) | Đọc/cập nhật bởi Executor, Auditor và scripts |
| `protected_paths.txt` | Khai báo danh sách các file và thư mục cấm can thiệp bởi research executor | Được nạp bởi `check_scope.py` |
| `check_scope.py` | Kiểm tra các file bị thay đổi (từ `git diff --name-only` hoặc tham số) so với protected paths | `python3 control/check_scope.py` |
| `protocol_hash.sh` | Tính toán và kiểm chứng hash SHA-256 của các protocol files | `bash control/protocol_hash.sh [--save\|--verify]` |
| `validate_state.py` | Kiểm tra tính toàn vẹn cú pháp YAML và logic chuyển trạng thái của task_state.yaml | `python3 control/validate_state.py` |
| `gate.sh` | Cổng kiểm tra toàn diện trước khi bàn giao hoặc nghiệm thu | `bash control/gate.sh` |

---

## 3. Quy trình làm việc của Agent với Gate

1. **Trước khi bắt đầu task**:
   - Kiểm tra trạng thái của task trong `task_state.yaml` (phải là `READY` hoặc `GATED` cho task trước).
2. **Trong quá trình làm task**:
   - Chỉ sửa các file thuộc `Allowed Files` của task.
   - Thường xuyên kiểm tra phạm vi: `python3 control/check_scope.py`.
3. **Khi hoàn thành implementation và test**:
   - Chạy test của task: `pytest tests/test_<ID>.py`.
   - Cập nhật `task_state.yaml`: `status: "TEST_PASSED"`.
   - Chạy smoke check gate: `bash control/gate.sh`.
   - Dừng lại, chuyển quyền kiểm toán cho Auditor độc lập.
4. **Auditor nghiệm thu**:
   - Kiểm tra độc lập theo `AUDITOR.md`.
   - Nếu đạt yêu cầu: chuyển trạng thái sang `GATED`.
   - Nếu có lỗi: chuyển `AUDIT_FAILED` cho `REPAIR.md`.
