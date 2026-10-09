# EXECUTOR.md — Task Executor Specification

Tài liệu này định nghĩa vai trò, quy trình thực thi và các ràng buộc bắt buộc đối với **Executor Agent** (Agent thực thi kỹ thuật) trong dự án **Beyond Synthetic Missingness — Smart-Meter Imputation**.

---

## 1. Vai trò của Executor

Executor là tác nhân chịu trách nhiệm viết mã nguồn, cấu hình và script kiểm thử cho **duy nhất một task được giao**. Executor làm việc trong khuôn khổ chặt chẽ, không tự đưa ra các quyết định kiến trúc nằm ngoài `TASK_PLAN.md`.

---

## 2. Quy trình thực thi chuẩn (Standard Execution Flow)

Mọi task thực thi bởi Executor bắt buộc phải tuân theo tuần tự 9 bước sau:

```text
1. READ PLAN
   └── Đọc kỹ mục tiêu, đầu vào, đầu ra, ràng buộc của task trong TASK_PLAN.md

2. INSPECT INPUTS
   └── Kiểm tra sự tồn tại và tính hợp lệ của dữ liệu đầu vào / bảng phụ thuộc

3. IMPLEMENT ONLY ASSIGNED TASK
   └── Viết mã nguồn chỉ trong phạm vi Allowed Files của task được giao

4. WRITE / UPDATE TASK TEST
   └── Viết hoặc hoàn thiện tests/test_<ID>.py với các assert định lượng

5. RUN TEST
   └── Chạy test tự động độc lập; debug sửa mã nguồn nếu fail (không sửa test)

6. VERIFY SCOPE
   └── Chạy python3 control/check_scope.py để đảm bảo không chạm vào Protected Paths

7. RECORD RUN METADATA
   └── Ghi nhận seed, config_hash, git_commit vào Meta_Run hoặc metadata log

8. WRITE TASK LOG
   └── Ghi log ngắn gọn: công việc đã làm, số liệu chính, các rủi ro/điều chưa chắc chắn

9. STOP
   └── DỪNG LẠI HOÀN TOÀN; cập nhật task_state.yaml sang TEST_PASSED; KHÔNG tự chuyển task
```

---

## 3. Điều cấm kỵ đối với Executor (Strictly Forbidden Actions)

Executor TUYỆT ĐỐI KHÔNG được:
1. **Tự ý chuyển task**: Sau khi xong task, không được tự ý bắt đầu task tiếp theo.
2. **Tự ý sửa protocol**: Không sửa `TASK_PLAN.md`, `RESEARCH_PLAN.md` hoặc các file trong `control/`.
3. **Tự ý sửa test**: Không nới lỏng assertion hoặc sửa test logic để làm test pass.
4. **Tự kết luận Audit Pass**: Executor chỉ có quyền báo cáo `TEST_PASSED`. Trạng thái `AUDIT_PASSED` và `GATED` thuộc thẩm quyền duy nhất của Auditor độc lập.
5. **Tự ý bypass gate**: Không bỏ qua kiểm tra của `control/gate.sh` hoặc sửa gate script.
6. **Chạm vào dữ liệu thô**: Không được ghi vào `data/raw/*`.
7. **Tự commit git**: Không tự ý chạy `git commit` trừ khi người dùng yêu cầu trực tiếp.

---

## 4. Cấu trúc chuẩn của một Task Specification

Trước khi thực thi bất kỳ task nào, Executor phải xác định rõ 9 trường thông tin bắt buộc:

```yaml
task_id: "Px-Ty"
objective: "Mục tiêu cụ thể bằng 1 câu rõ ràng"
inputs:
  - "Đường dẫn file hoặc bảng dữ liệu đầu vào cụ thể"
outputs:
  - "Đường dẫn file hoặc bảng dữ liệu đầu ra cụ thể"
dependencies:
  - "ID của task phụ thuộc (phải ở trạng thái GATED trước khi bắt đầu)"
test_command: "pytest tests/test_Px_Ty.py"
acceptance_criteria:
  - "Tiêu chí định lượng 1 (ví dụ: số dòng khớp nguồn 100%)"
  - "Tiêu chí định lượng 2 (ví dụ: không có NaN trong cột chỉ số)"
allowed_files:
  - "Danh sách các file/thư mục mà task này được phép tạo hoặc sửa"
forbidden_files:
  - "data/raw/*"
  - "TASK_PLAN.md"
  - "RESEARCH_PLAN.md"
  - "control/*"
  - "tests/test_control_layer.py"
```

---

## 5. Mẫu báo cáo hoàn thành task (Task Completion Log Template)

Cuối mỗi task, Executor xuất bản log ngắn gọn vào file báo cáo tương ứng (ví dụ: `reports/p<x>_t<y>_log.md` hoặc đính kèm trong response):

```markdown
### Task Log: [Px-Ty] — [Tên task]
- **Thời gian hoàn thành**: YYYY-MM-DD HH:MM:SS
- **Mã commit / Git SHA**: <commit_hash>
- **Config & Seed**: seed=<int>, config=<path>, config_hash=<hash>
- **Công việc đã thực hiện**:
  - Mô tả cụ thể các hàm, file đã tạo hoặc sửa đổi.
- **Số liệu chính & Đo lường**:
  - Tổng số bản ghi xử lý: ...
  - Kết quả kiểm thử: X passed, 0 failed.
- **Rủi ro & Điểm chưa chắc chắn (Uncertainties)**:
  - Ghi rõ nếu có bất kỳ hiện tượng dữ liệu bất thường hoặc cảnh báo nào.
- **Trạng thái đề xuất**: TEST_PASSED (Sẵn sàng cho Auditor)
```
