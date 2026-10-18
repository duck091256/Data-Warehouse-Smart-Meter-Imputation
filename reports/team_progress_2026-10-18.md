# Tiến độ dự án — 2026-10-18

## Trạng thái hiện tại

- P1-T1 đến P1-T5 đã ở trạng thái `GATED`; dữ liệu sạch hiện được lưu với ngưỡng segment `L=48`.
- P1-T6 trở đi và các task P2 hiện vẫn `BLOCKED`. Chưa sinh mask, chưa chạy benchmark imputation và chưa train mô hình.
- Đây là dự án ở giai đoạn hoàn tất nền dữ liệu P1 và chuẩn bị hợp đồng cho warehouse/mask; chưa ở giai đoạn huấn luyện.

## Quyết định nghiên cứu đã xác nhận

1. Giữ toàn bộ clean segment `L=48`. Ngữ cảnh 96 bước được xét theo từng mask/model, không nâng thành điều kiện lưu segment chung.
2. Giữ chuỗi `W` nguyên trạng làm target thanh ghi tích lũy theo protocol hiện tại. Không lấy sai phân để đổi sang năng lượng từng khoảng nếu chưa duyệt sửa protocol.
3. Đơn vị vật lý của từng meter vẫn `UNKNOWN` cho đến khi có bằng chứng nguồn tương ứng. Không tự quy đổi, chỉnh dấu hoặc sửa reset/rollover.

Các quyết định này không tự mở P2, không thay đổi protocol hoặc task state.

## Reader maintenance candidate

- Có candidate reader riêng, chưa thay ETL production. Theo evidence local của `data/audit_results/data_integrity_review_20261018_01a14bc6/execution_v5/`, bộ kiểm synthetic báo 33 pass; phép so sánh giới hạn trên 3 file W (664.236 dòng) khớp kết quả reader production trên subset đó. Reviewer độc lập không còn finding chặn trong phạm vi candidate.
- Kết quả này không phải nghiệm thu P1-T2, không chứng minh toàn bộ nguồn hoặc đơn vị vật lý, và không cấp quyền tích hợp production/P2.
- Gói evidence đầy đủ chưa được đưa vào commit này vì một số config lưu đường dẫn tuyệt đối của máy và có Parquet subset. Giữ nguyên evidence tại checkout để có thể lập gói chia sẻ đã làm sạch riêng.

## Tiếp theo

- Hoàn thiện quyết định/thiết kế P1-T6 theo hai hướng đã chốt, đồng thời xử lý metric phù hợp với target thanh ghi.
- Xác minh unit mapping từng meter từ tài liệu nguồn; giữ `UNKNOWN` ở nơi chưa đủ chứng cứ.
- Chỉ bắt đầu P2 sau khi các gate liên quan được giải quyết và có ủy quyền thực thi riêng.
