# Tổng kết khảo sát đề tài môn Kho dữ liệu

Đã khảo sát 3 domain (y tế, kinh tế, khoa học trái đất) theo đúng 13 bước đã thống nhất. Mỗi domain đã có một ứng viên mạnh nhất, thu hẹp qua vòng tự phản biện. Dưới đây là tổng kết và những gì còn tồn đọng cần quyết định/kiểm tra trước khi khóa đề tài.

## 1. Ba ứng viên mạnh nhất

### H1 — Y tế
**Tên đề tài:** Cùng một bệnh thận mạn nhưng số tử vong không giống nhau — kho dữ liệu truy vết và đo độ lệch giữa CDC WONDER và GBD tại Hoa Kỳ, 1999–2021.

- **Dữ liệu:** CDC WONDER (mortality theo ICD-10 N18) và IHME GBD (cause-specific estimates) — đều aggregate, công khai, không cần định danh/CITI/DUA.
- **Khe hở:** Không phải "phát hiện hai nguồn khác nhau" (đã có paper so sánh CVD), mà là xây warehouse có lineage, snapshot và audit query để truy vết & giải thích sai lệch cho một nhóm bệnh hẹp.
- **Khối lượng ước tính:** 10–12 tuần, phù hợp 2 người.

### E2 — Kinh tế
**Tên đề tài:** Một lô hàng điện tử xuất khẩu và nhập khẩu không cho cùng một con số — kho dữ liệu đối chiếu mirror trade và mã HS của Việt Nam, 2015–2024.

- **Dữ liệu:** UN Comtrade + WITS, nhóm HS 85, 5 đối tác chính của Việt Nam. Đăng ký tài khoản free đủ hạn mức (đã verify: ~500 calls/ngày, tới 100.000 dòng/call — không phải giới hạn 500 dòng như preview không đăng ký).
- **Khe hở:** Đo có kiểm soát tác động của HS edition, reporter/partner, valuation (FOB/CIF) và missingness lên mirror asymmetry của một chuỗi hàng cụ thể.
- **Khối lượng ước tính:** 10–12 tuần.

### A — Khoa học trái đất
**Tên đề tài:** Thiết kế và đánh giá kho dữ liệu chất lượng-aware cho tổng hợp sự kiện ngập từ Sentinel-1, GPM IMERG và SRTM tại một tiểu vùng Đồng bằng sông Cửu Long, 2018–2024.

- **Dữ liệu:** Copernicus Sentinel-1 GRD (qua CDSE STAC), NASA GPM IMERG (rainfall), SRTM DEM, Global Surface Water — công khai, cần tài khoản free (CDSE + NASA Earthdata).
- **Khe hở:** Không cạnh tranh với GFM (flood monitoring toàn cầu) hay hướng động đất (đã có paper 2026 làm spatio-temporal earthquake warehouse tương tự); tập trung vào quality/provenance dimension và đo ảnh hưởng của missingness/lệch thời gian lên kết quả tổng hợp sự kiện ngập.
- **Khối lượng ước tính:** chưa có — cần bổ sung.

## 2. Bảng so sánh chéo

| Tiêu chí | H1 Y tế | E2 Kinh tế | A Trái đất |
|---|---|---|---|
| Loại dữ liệu | Bảng aggregate | Bảng aggregate | Raster + bảng |
| Độ khó kỹ thuật | Thấp–vừa | Thấp–vừa | Cao hơn (GDAL/rasterio, PostGIS/DuckDB spatial) |
| Rào cản truy cập | Không cần đăng ký | Cần tài khoản free (đủ hạn mức) | Cần 2 tài khoản free + OAuth |
| Tính mới/khe hở | Rõ, cần khóa hẹp | Rõ, cần kiểm tra thêm để tránh trùng nghiên cứu mirror-trade quốc tế | Rõ nhất, đã tự loại các hướng trùng |
| Phù hợp môn Kho dữ liệu (schema/ETL/dimension) | Vừa | Vừa | Cao — buộc thiết kế quality/provenance dimension nghiêm túc |
| Rủi ro bị hỏi "đã có ai làm chưa" | Vừa | Vừa | Thấp nhất |

## 3. Những gì còn tồn đọng — cần làm/quyết định trước khi khóa

### Quyết định chung (cần anh Phụng cho ý kiến)
- [ ] Môn Kho dữ liệu yêu cầu research contribution kiểu paper (research question, hypothesis, novelty) hay chỉ cần đồ án kỹ thuật (schema, ETL, OLAP, dashboard)? Câu trả lời ảnh hưởng tới việc có nên giữ toàn bộ phần tự phản biện tính mới như hiện tại không.
- [ ] Chốt 1 trong 3 domain, hoặc chạy pilot song song cả 3 rồi chọn theo kết quả thực tế.

### Gate rủi ro chí mạng — mỗi domain đều có một điểm chưa test
- [ ] **H1:** Chưa xác nhận GBD có phân loại/mapping đúng khớp CKD ↔ ICD-10 N18 hay không. Nếu không mapping được, phải đổi sang nhóm bệnh rộng hơn hoặc chuyển hướng khác trong domain y tế.
- [ ] **E2:** Chưa kiểm tra coverage dữ liệu HS85 của 5 đối tác chính có đủ dài và đủ đầy cho giai đoạn 2015–2024 không. Cần thêm bước tìm kiếm để xác nhận góc "warehouse có lineage/snapshot" cho mirror trade VN chưa bị nghiên cứu học thuật khác làm trùng.
- [ ] **A:** Chưa có danh sách cụ thể 5–10 sự kiện ngập ở ĐBSCL (2018–2024) kèm ngày bắt đầu/kết thúc rõ ràng — cần nguồn xác nhận (báo chí, VNDMA, Đài KTTV) trước khi định nghĩa được cửa sổ rainfall "trước–trong–sau event". Cũng cần bổ sung ước tính khối lượng công việc theo tuần.

### Việc kỹ thuật còn thiếu, chưa được nêu trong báo cáo khảo sát
- [ ] A: chưa tính đến bước đăng ký tài khoản CDSE và NASA Earthdata (free nhưng cần OAuth token) — nên làm sớm để tránh mất thời gian giữa chừng.
- [ ] A: báo cáo chưa nêu rõ warehouse sẽ không đối chiếu với ground truth ngập thực tế (ảnh độ phân giải cao, khảo sát thực địa) — chỉ đo tính ổn định nội bộ khi lọc theo ngưỡng chất lượng. Cần ghi rõ đây là giới hạn của đề tài, tránh hiểu nhầm là đo được độ chính xác flood mapping.
- [ ] H1: khi viết báo cáo cuối, cần làm rõ GBD là ước lượng mô hình hóa còn CDC WONDER là số liệu registry — "sai lệch" giữa hai nguồn là khác biệt phương pháp luận, không phải "nguồn nào đúng hơn".

## 4. Đề xuất bước tiếp theo
1. Anh Phụng cho ý kiến về yêu cầu thật sự của môn (research contribution vs đồ án kỹ thuật).
2. Chạy pilot 1–2 ngày cho gate rủi ro chí mạng của domain được ưu tiên (hoặc cả 3 nếu có thời gian).
3. Sau pilot, khóa 1 đề tài và tiếp tục bước 5–13 của pipeline.