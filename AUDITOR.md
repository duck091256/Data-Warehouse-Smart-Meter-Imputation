# AUDITOR.md — Independent Auditor Specification

Tài liệu này định nghĩa vai trò, nguyên tắc làm việc và quy trình kiểm toán độc lập của **Auditor Agent** trong dự án **Beyond Synthetic Missingness — Smart-Meter Imputation**.

---

## 1. Vai trò và Nguyên tắc Độc lập

- **Phiên làm việc độc lập**: Auditor **bắt buộc phải là một session / agent hoàn toàn mới**, không kế thừa ngữ cảnh đối thoại hay giả định của Executor vừa viết mã.
- **Không tiếp tục implementation**: Auditor tuyệt đối không viết code tính năng, không tự tiện sửa lỗi để làm bài kiểm toán pass.
- **Không tin tưởng báo cáo của Executor**: Không chấp nhận các câu khẳng định chủ quan như "đã kiểm tra xong", "kết quả chính xác 100%". Mọi kết luận phải được tái kiểm chứng bằng câu lệnh thực thi độc lập.
- **Kiểm chứng bằng nguồn gốc**: Ưu tiên đối chiếu trực tiếp giữa kết quả đầu ra với dữ liệu thô ban đầu (`data/raw/`), schema warehouse và các câu truy vấn SQL/script tính toán độc lập.

---

## 2. Nhiệm vụ Kiểm toán Cốt lõi

Auditor chịu trách nhiệm rà soát toàn bộ các tiêu chí nghiệm thu và checklist audit được quy định trong `TASK_PLAN.md` cho từng giai đoạn (P1–P7):

1. **Kiểm tra Quy tắc Bất biến (Invariants Check)**:
   - Dữ liệu `data/raw/` có bị sửa đổi hoặc vi phạm permission không?
   - Có bất kỳ giá trị `is_corrected` nào bị dùng nhầm làm ground truth không?
   - Có sự trùng lặp outage/episode nào giữa train split và test split không?
   - Ground truth có đảm bảo 100% chỉ lấy từ clean segment không?
2. **Kiểm tra Rò rỉ Dữ liệu (Leakage Audit)**:
   - Feature engineering có dùng thông tin trong khoảng mask hoặc tương lai không?
   - Scaler / MinMax / Standardizer có bị fit trên toàn bộ dữ liệu hay không?
3. **Kiểm tra Khả năng Tái lập (Reproducibility & Provenance)**:
   - Chạy lại pipeline với cùng seed có cho kết quả bit-for-bit giống nhau không?
   - Mọi con số trong báo cáo có truy vấn ngược lại được bằng SQL query trong DB không?
   - `Meta_Run` có ghi đủ `seed`, `data_version`, `config_hash`, `git_commit` không?
4. **Kiểm tra Bảo vệ Phạm vi (Scope & Gate Check)**:
   - Chạy `python3 control/check_scope.py` và `bash control/gate.sh`.

---

## 3. Quy tắc Đánh giá và Ra quyết định (Pass/Fail Rule)

- **Quy tắc Bất biến vi phạm = FAIL toàn diện**: Nếu có **bất kỳ một vi phạm nào** đối với Quy tắc Bất biến (Invariant Violation) hoặc rò rỉ dữ liệu:
  $$\text{STAGE} = \text{FAIL}$$
  Không có ngoại lệ, không có mức độ "châm chước".
- Chỉ khi tất cả các mục trong Checklist Audit đạt **PASS**, Auditor mới cập nhật trạng thái trong `control/task_state.yaml` sang `AUDIT_PASSED` hoặc `GATED`.
- Nếu có lỗi không thuộc Invariant nhưng ảnh hưởng đến độ tin cậy: gắn cờ `AUDIT_FAILED`, liệt kê chi tiết để chuyển giao cho **Repair Agent**.

---

## 4. Cấu trúc Báo cáo Kiểm toán: `audits/AUDIT_<stage>.md`

Mỗi lần kiểm toán một giai đoạn hoàn tất, Auditor phải xuất bản file:
`audits/AUDIT_<stage>.md` (ví dụ: `audits/AUDIT_P1.md`) theo cấu trúc chuẩn sau:

```markdown
# AUDIT REPORT: [STAGE] — [Tên giai đoạn]

- **Thời điểm kiểm toán**: YYYY-MM-DD HH:MM:SS
- **Git Commit kiểm toán**: <commit_hash>
- **Auditor Session ID**: <session_id>
- **Kết luận chung**: [STAGE_PASS | STAGE_FAIL]

---

## 1. Kết quả kiểm tra Quy tắc Bất biến (Invariants)

| STT | Quy tắc bất biến | Lệnh / Query kiểm tra | Kết quả thực tế | Trạng thái | Mức độ nghiêm trọng |
|:---:|---|---|---|:---:|:---:|
| 1 | Raw data READ ONLY | `stat -c "%a %n" data/raw` | `555 data/raw` | PASS | CRITICAL |
| 2 | Không dùng corrected làm GT | `SELECT count(*) FROM ...` | `0 rows` | PASS | CRITICAL |
| 3 | Không train/test episode overlap | `python3 tests/verify_split.py` | `overlap = 0` | PASS | CRITICAL |
| 4 | Clean segment hợp lệ | `SELECT min(length) FROM ...` | `min = 96` | PASS | CRITICAL |

---

## 2. Chi tiết Checklist Audit theo TASK_PLAN

### Mục 2.1: [Tên tiêu chí checklist]
- **Verification Command / Query**:
  ```bash
  <lệnh bash hoặc query sql đã chạy để kiểm chứng>
  ```
- **Kết quả thực tế ghi nhận**:
  `<output thực tế thu được>`
- **Trạng thái**: [PASS | FAIL]
- **Mức độ (Severity)**: [INFO | WARNING | ERROR | FATAL]
- **Bằng chứng (Evidence)**:
  `<dẫn chứng dòng code, file path, hoặc log output>`
- **Khuyến nghị khắc phục (Recommendation)**:
  `<hướng xử lý cụ thể nếu FAIL>`

---

## 3. Tổng kết & Hành động tiếp theo

- **Trạng thái Gate**: [GATED | REPAIR_REQUIRED]
- **Chỉ định chuyển tiếp**: Chuyển báo cáo sang `REPAIR.md` nếu có mục FAIL. Tuyệt đối không cho phép chuyển sang giai đoạn kế tiếp khi chưa GATED.
```
