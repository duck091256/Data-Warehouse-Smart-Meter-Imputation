# AGENTS.md — Research Protocol & Governance Rules

Tài liệu này là **Hiến chương và Quy tắc bất biến** (Single Source of Governance) cho tất cả các AI coding agents, subagents và nhà nghiên cứu làm việc trên repository:
**Beyond Synthetic Missingness — Smart-Meter Imputation**

---

## 1. Research Protocol (Nguồn sự thật)

- `TASK_PLAN.md` và `RESEARCH_PLAN.md` (khi được tạo) là **nguồn sự thật duy nhất (Single Source of Truth)**.
- Mọi định nghĩa, công thức, giai đoạn (P1–P7) và tiêu chí nghiệm thu được quy định trong `TASK_PLAN.md` có hiệu lực tối cao.
- **Không tự ý sửa đổi protocol**: Mọi agent không được tự ý sửa đổi, nới lỏng hoặc thay thế bất kỳ định nghĩa nào trong protocol.
- Nếu phát hiện protocol có mâu thuẫn hoặc lỗ hổng kỹ thuật:
  - Ghi nhận trạng thái `BLOCKED` trong `control/task_state.yaml`.
  - Mô tả chi tiết vấn đề trong log của task.
  - Tuyệt đối không tự ý "chữa cháy" bằng cách sửa protocol file.

---

## 2. Scope Discipline (Kỷ luật phạm vi)

- **Một task tại một thời điểm**: Mỗi phiên làm việc chỉ được phép thực thi đúng **1 task** (hoặc tối đa 2 task liên quan cực kỳ mật thiết khi có chỉ thị rõ ràng từ người dùng).
- **Không làm lan man**: Tuyệt đối không tự động triển khai trước các task tiếp theo khi task hiện tại chưa hoàn thành và chưa qua gate kiểm soát.
- **Tập trung vào boundary**: Chỉ tạo và sửa các file thuộc `Allowed Files` của task được giao.

---

## 3. Protected Data (Bảo vệ dữ liệu gốc)

- Thư mục `data/raw/` là **READ ONLY tuyệt đối**.
- Không được thêm, xóa, sửa, ghi đè hoặc đổi tên bất kỳ file nào trong `data/raw/`.
- Dữ liệu thô phải được bảo toàn nguyên vẹn tính nguyên bản từ nguồn cung cấp (Honda Research Institute dataset).

---

## 4. Test Integrity (Tính toàn vẹn của kiểm thử)

- **Không sửa test để pass**: Tuyệt đối cấm hành vi sửa đổi logic assertion trong test chỉ để che giấu lỗi code hoặc làm test pass giả tạo.
- Test phản ánh chính xác các tiêu chí nghiệm thu định lượng của protocol.
- Nếu một test fail:
  - Phải điều tra nguyên nhân ở code implementation hoặc dữ liệu đầu vào.
  - Nếu test có lỗi cú pháp hoặc giả định sai so với protocol đã chốt, phải ghi rõ bằng chứng trước khi điều chỉnh và phải được kiểm toán viên (Auditor) chấp thuận.

---

## 5. Research Integrity (Tính trung thực khoa học)

1. **Ground Truth chân thực**:
   - Tuyệt đối **không dùng giá trị `corrected`** trong log sự cố làm ground truth.
   - Ground truth chỉ được trích xuất từ các **clean segment hợp lệ** (liên tục, không thiếu, không có issue log, không bị corrected).
2. **Không rò rỉ dữ liệu (No Leakage)**:
   - Tuyệt đối không để xảy ra temporal leakage hoặc feature leakage.
   - Giá trị ground truth dưới vùng mask không bao giờ được xuất hiện trong input feature của bất kỳ mô hình nào.
   - Scaler / Normalizer chỉ được fit trên tập train.
3. **Phân tách Train/Test nghiêm ngặt**:
   - Tuyệt đối **không để cùng một outage/episode xuất hiện ở cả train và test split**.
   - Split dữ liệu phải bảo toàn độc lập theo episode và theo mốc thời gian.
4. **Báo cáo trung thực**:
   - Báo cáo đầy đủ cả kết quả tiêu cực (negative results) hoặc khi mô hình đề xuất không vượt qua baseline.
   - Không "cherry-pick" cửa sổ dữ liệu, nhóm meter hoặc seed để làm đẹp số liệu.

---

## 6. Reproducibility (Khả năng tái lập)

- Mọi script thí nghiệm phải nhận các tham số `--seed` và `--config` từ dòng lệnh; tuyệt đối không hard-code seed hoặc siêu tham số trong mã nguồn.
- Mọi lần chạy sinh kết quả phải ghi một bản ghi vào `Meta_Run` trong warehouse với đầy đủ:
  - `seed`
  - `data_version`
  - `config_hash`
  - `git_commit`
  - `timestamp`
- Khi chạy lại với cùng seed và config trên cùng dữ liệu, kết quả đầu ra phải giống hệt 100%.

---

## 7. Provenance (Nguồn gốc số liệu)

- Mọi con số, biểu đồ, bảng tổng kết xuất hiện trong các báo cáo (`reports/*.md`) và dashboard phải truy ngược được về một database query (SQL), raw log hoặc script tính toán cụ thể.
- Nghiêm cấm đưa ra số liệu ước đoán hoặc không có vết kiểm chứng.

---

## 8. Stop Conditions (Điều kiện dừng khẩn cấp)

Agent bắt buộc phải dừng thực thi ngay lập tức và báo cáo cho người dùng khi gặp một trong các tình huống sau:
1. **Thiếu dữ liệu đầu vào**: File đầu vào hoặc bảng warehouse phụ thuộc không tồn tại hoặc rỗng.
2. **Test thất bại không rõ nguyên nhân**: Test fail sau 2 lần debug mà không xác định được căn nguyên logic.
3. **Phát hiện mâu thuẫn trong protocol**: Giữa các bảng mô tả, công thức hoặc quy tắc trong `TASK_PLAN.md`.
4. **Nguy cơ rò rỉ dữ liệu**: Khi phát hiện feature pipeline hoặc split logic có khả năng nhìn thấy trước tương lai hoặc ground truth.
5. **Yêu cầu nằm ngoài task scope**: Phát sinh nhu cầu sửa các module không thuộc phạm vi task hiện tại.
6. **Cần điều chỉnh research protocol**: Bất kỳ thay đổi nào ảnh hưởng tới định nghĩa failure episode, clean segment, mask branch, metric, ranking bootstrap.

---

## 9. Completion Rule (Quy tắc hoàn thành task)

Một task chỉ được coi là hoàn thành (`Done`) và được phép chuyển sang bước tiếp theo khi thỏa mãn đầy đủ các điều kiện sau:
1. Mã nguồn implementation hoàn tất đầy đủ theo đúng yêu cầu task.
2. Script kiểm thử tương ứng (`tests/test_<task_id>.py`) chạy pass 100%.
3. File log ngắn của task được ghi chép (mục tiêu, kết quả chính, rủi ro/điều chưa chắc chắn).
4. Không có bất kỳ vi phạm nào đối với các đường dẫn được bảo vệ (`control/protected_paths.txt`).
5. Scope của task được giữ nguyên vẹn, không lấn sang task khác.
6. Trạng thái trong `control/task_state.yaml` được cập nhật chính xác.
7. Vượt qua kiểm tra tự động của `control/gate.sh`.
