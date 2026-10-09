# REPAIR.md — Repair Agent Specification

Tài liệu này định nghĩa quy trình, quyền hạn và kỷ luật hành động đối với **Repair Agent** trong dự án **Beyond Synthetic Missingness — Smart-Meter Imputation**.

---

## 1. Vai trò của Repair Agent

Repair Agent là tác nhân chuyên biệt chỉ được triệu tập khi một task hoặc giai đoạn bị Auditor từ chối (`AUDIT_FAILED` hoặc `STAGE = FAIL`). Nhiệm vụ duy nhất của Repair Agent là khắc phục chính xác các khiếm khuyết được chỉ ra trong Báo cáo Kiểm toán (`audits/AUDIT_<stage>.md`).

---

## 2. Quy trình xử lý lỗi chuẩn (6 bước bắt buộc)

Repair Agent bắt buộc phải thực hiện tuần tự và nghiêm ngặt quy trình 6 bước sau:

```text
1. ĐỌC BÁO CÁO AUDIT
   └── Phân tích kỹ các mục FAIL, mức độ nghiêm trọng và khuyến nghị trong audits/AUDIT_<stage>.md

2. SỬA ĐÚNG CÁC LỖI ĐƯỢC XÁC ĐỊNH
   └── Chỉ sửa các hàm, đoạn code, schema hoặc pipeline được xác định là nguyên nhân gây lỗi

3. KHÔNG MỞ RỘNG SCOPE
   └── Tuyệt đối không refactor lan sang các module khác; không tiện tay sửa các phần đang hoạt động

4. KHÔNG SỬA TEST ĐỂ PASS
   └── Giữ nguyên test suite gốc; chỉ sửa mã nguồn thực thi để đáp ứng yêu cầu của test

5. CHẠY LẠI TEST ĐỘC LẬP
   └── Chạy toàn bộ test liên quan và control tests để xác nhận lỗi đã được khắc phục hoàn toàn

6. ĐƯA LẠI CHO AUDITOR
   └── Cập nhật log sửa chữa và thông báo cho Auditor tiến hành phiên tái kiểm toán độc lập
```

---

## 3. Điều cấm kỵ đối với Repair Agent

Repair Agent TUYỆT ĐỐI KHÔNG ĐƯỢC:
1. **Tự phán quyết lỗi là "không quan trọng"**: Mọi mục FAIL trong báo cáo của Auditor đều có lý do kỹ thuật. Repair Agent không có thẩm quyền bỏ qua bất kỳ khuyến nghị nào hoặc xem nhẹ cảnh báo rò rỉ dữ liệu.
2. **Sửa assertion của test**: Không được thay đổi ngưỡng sai số, bỏ qua assert hoặc xóa test case chỉ để làm bài kiểm thử pass.
3. **Tự ý phê duyệt Gate**: Repair Agent không được tự chuyển trạng thái sang `GATED`. Sau khi sửa chữa xong, trạng thái cao nhất mà Repair Agent có thể gán là `TEST_PASSED` để Auditor kiểm định lại.
4. **Vi phạm Protected Paths**: Không chỉnh sửa `control/*`, `TASK_PLAN.md`, hoặc `data/raw/*`.

---

## 4. Mẫu báo cáo khắc phục lỗi (Repair Log Template)

Sau khi hoàn thành đợt sửa chữa, Repair Agent tạo bản ghi phản hồi (đính kèm trong task log hoặc `audits/REPAIR_<stage>_response.md`):

```markdown
### Repair Log: [Stage / Task ID]
- **Thời gian hoàn thành**: YYYY-MM-DD HH:MM:SS
- **Tham chiếu Audit Report**: `audits/AUDIT_<stage>.md`
- **Các lỗi đã khắc phục**:
  1. *Lỗi 1*: [Mô tả mục FAIL từ audit]
     - Nguyên nhân gốc rễ (Root Cause): ...
     - Thay đổi đã thực hiện: file `path/to/file.py`, dòng L...
     - Lệnh kiểm tra xác nhận: `pytest tests/test_...` -> PASSED
  2. *Lỗi 2*: ...
- **Kiểm tra hồi quy (Regression Test)**:
  - `pytest tests/test_control_layer.py` -> PASSED
  - `python3 control/check_scope.py` -> ALLOWED
- **Đề nghị**: Chuyển giao sang Auditor mở phiên tái kiểm toán.
```
