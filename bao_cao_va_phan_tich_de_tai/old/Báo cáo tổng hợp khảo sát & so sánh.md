# BÁO CÁO TỔNG HỢP KHẢO SÁT & SO SÁNH 3 ĐỀ TÀI ĐỒ ÁN MÔN KHO DỮ LIỆU (DATA WAREHOUSE)

> **Tài liệu lưu hành nội bộ nhóm**  
> **Mục đích:** Cung cấp thông tin súc tích, khách quan về kết quả thực hiện Bước 1–5 (chọn domain, khảo sát tài liệu, lập bản đồ nghiên cứu, xác định khoảng trống, tự phản biện và thu hẹp phạm vi) của 3 hướng đề tài: **Y tế**, **Kinh tế**, và **Khoa học Trái đất** để thành viên trong nhóm đánh giá và cùng ra quyết định.

---

## MỤC LỤC
1. [Tổng quan bối cảnh khảo sát](#1-tổng-quan-bối-cảnh-khảo-sát)
2. [Tóm tắt chi tiết từng đề tài](#2-tóm-tắt-chi-tiết-từng-đề-tài)
   - [Đề tài 1: Y tế (Health)](#đề-tài-1-y-tế-health)
   - [Đề tài 2: Kinh tế (Economics)](#đề-tài-2-kinh-tế-economics)
   - [Đề tài 3: Khoa học Trái đất (Earth Sciences)](#đề-tài-3-khoa-học-trái-đất-earth-sciences)
3. [Bảng so sánh chéo 3 đề tài](#3-bảng-so-sánh-chéo-3-đề-tài)
4. [Những điểm còn tồn đọng / Cần quyết định trước khi chốt đề tài](#4-những-điểm-còn-tồn-đọng--cần-quyết-định-trước-khi-chốt-đề-tài)

---

## 1. TỔNG QUAN BỐI CẢNH KHẢO SÁT

Cả 3 đề tài đều được thực hiện theo quy trình chuẩn 13 bước của đồ án môn Kho dữ liệu. Báo cáo này tổng hợp kết quả của **Bước 1 đến Bước 5**:
- **Khảo sát hệ thống / paper hiện hành:** Xác định những gì cộng đồng đã giải quyết và những điểm còn bỏ sót.
- **Lập bản đồ nghiên cứu:** Phân loại mật độ nghiên cứu theo từng chiều kỹ thuật.
- **Xác định khoảng trống (Research Gap):** Lựa chọn bài toán có khe hở kỹ thuật khả thi ở quy mô sinh viên.
- **Tự phản biện & Thu hẹp (Scoping):** Chuyển từ các ý tưởng rộng ("xây kho dữ liệu chung chung") sang bài toán hẹp, có câu hỏi nghiên cứu, giả thuyết và phương pháp đo lường bằng truy vấn kiểm toán dữ liệu (lineage, snapshot, quality-aware).

---

## 2. TÓM TẮT CHI TIẾT TỪNG ĐỀ TÀI

---

### ĐỀ TÀI 1: Y TẾ (HEALTH)

* **Tên đề tài (bản đã thu hẹp / final):**  
  *“Cùng một bệnh thận mạn nhưng số tử vong không giống nhau — Kho dữ liệu truy vết và đo độ lệch giữa CDC WONDER và GBD tại Hoa Kỳ, 1999–2021.”*

* **Vấn đề / Câu hỏi nghiên cứu:**  
  * *Câu hỏi nghiên cứu:* Sau khi chuẩn hóa năm, đơn vị, dân số và nhóm bệnh, sai lệch về số ca tử vong và tỷ lệ tử vong (mortality rate) giữa CDC WONDER và GBD là bao nhiêu? Xu hướng có đồng nhất không và sự sai lệch đó có ổn định theo thời gian / nhóm dân số không?
  * *Giả thuyết:* Hai nguồn có thể cùng chỉ ra xu hướng dài hạn nhưng vẫn có sai lệch có hệ thống về độ lớn do khác biệt về định nghĩa, phân loại nguyên nhân tử vong và phương pháp xử lý dữ liệu (redistribution / smoothing).

* **Vì sao có khe hở (Khác biệt so với hệ thống / paper đã có):**  
  * *Hệ thống / Chuẩn đã khảo sát:* MIMIC-IV, eICU-CRD, OMOP CDM/OHDSI, WHO GHO OData / xMart, Our World in Data (OWID), CDC WONDER, IHME GBD.
  * *Paper liên quan:* Một bài báo gần đây đã so sánh trực tiếp CDC WONDER và GBD đối với tử vong tim mạch (CVD) và tiểu đường (Diabetes), chỉ ra xu hướng tương tự nhưng độ lớn khác nhau.
  * *Điểm khác biệt / Khe hở kỹ thuật:* Không lặp lại phân tích dịch tễ học tổng quát. Đề tài tập trung vào bài toán Kho dữ liệu (DW): xây dựng cơ chế truy vết (lineage), lưu trữ ảnh chụp theo thời gian (snapshot) và truy vấn kiểm toán (audit query) cho một nhóm bệnh hẹp (CKD). Kho dữ liệu lưu đồng thời giá trị, định nghĩa, mã nguyên nhân, mẫu số dân số, phiên bản và tham số truy vấn; hỗ trợ phân rã sai lệch thành các thành phần: khác biệt định nghĩa, khác biệt nguồn, khoảng bất định (uncertainty) và quy tắc tiền xử lý.

* **Nguồn dữ liệu chính & Mức độ dễ tiếp cận:**  
  * *CDC WONDER:* Dữ liệu tử vong dựa trên giấy chứng tử (Death Certificate) và mã ICD-10 (N18 cho CKD), phân theo năm, tuổi, giới, chủng tộc, địa lý.
  * *IHME GBD Results:* Ước tính nguyên nhân tử vong cụ thể giai đoạn 1990–2021, có kèm khoảng bất định (Uncertainty Interval - UI).
  * *Mức độ tiếp cận:* Dữ liệu tổng hợp (aggregate), hoàn toàn công khai, không chứa thông tin định danh cá nhân; **không cần CITI training, không cần ký DUA**, không cần quy trình phê duyệt y đức (IRB).

* **Cách đo / Công thức đánh giá chính:**  
  * *Mô hình dữ liệu:* Star schema gồm bảng sự kiện `fact_mortality` và các chiều `dim_source`, `dim_cause`, `dim_time`, `dim_population`, `dim_definition`, `dim_version`.
  * *Chỉ số đánh giá (Metrics):* Sai lệch tương đối (Relative difference), sai lệch tuyệt đối (Absolute difference), độ đồng thuận xu hướng (Trend agreement), mức độ giao thoa khoảng tin cậy / khoảng bất định (Overlap CI/UI), độ đầy đủ dữ liệu (Completeness), và khả năng tái lập kết quả truy vấn từ snapshot (Snapshot reproducibility).

* **Rủi ro lớn nhất / Điều chưa xác nhận (Gate pilot test):**  
  * *Rủi ro:* Danh mục bệnh thận mạn (CKD) trong GBD không khớp hoàn toàn với mã ICD-10 N18 của CDC WONDER.
  * *Gate kiểm tra:* Chạy pilot test xác nhận mức độ mapping giữa 2 nguồn. Nếu không khớp đủ, phải thu hẹp thành nhóm danh mục rộng hơn (*chronic kidney disease/renal failure category*) hoặc chuyển hướng sang đề tài theo dõi metadata drift (H3: WHO vs OWID) thay vì gộp mã tùy ý.

* **Khối lượng công việc ước tính:**  
  * Mức độ: **Vừa (khoảng 10–12 tuần)**; phù hợp nhóm 2 người trong 1 học kỳ.

---

### ĐỀ TÀI 2: KINH TẾ (ECONOMICS)

* **Tên đề tài (bản đã thu hẹp / final):**  
  *“Một lô hàng điện tử xuất khẩu và nhập khẩu không cho cùng một con số — Kho dữ liệu đối chiếu mirror trade và mã HS của Việt Nam, 2015–2024.”*

* **Vấn đề / Câu hỏi nghiên cứu:**  
  * *Câu hỏi nghiên cứu:* Trong giai đoạn 2015–2024, với nhóm ngành điện tử (HS 85) và 5 đối tác thương mại chính, mức độ bất đối xứng gương (mirror asymmetry) của Việt Nam thay đổi thế nào sau khi kiểm soát phiên bản mã HS (HS edition), luồng thương mại (flow), phương thức định giá (FOB/CIF) và dữ liệu thiếu (missingness)?
  * *Giả thuyết:* Một phần đáng kể biến động trong chuỗi thống kê thương mại không xuất phát từ thay đổi kinh tế thực tế mà đến từ quy tắc phân loại mã hàng, độ bao phủ báo cáo và các đợt điều chỉnh hồi tố (revision).

* **Vì sao có khe hở (Khác biệt so với hệ thống / paper đã có):**  
  * *Hệ thống / Chuẩn đã khảo sát:* World Bank Indicators API, IMF Data API / WEO, FRED/ALFRED, OECD Data API, Eurostat SDMX API, UN Comtrade / WITS, ILOSTAT.
  * *Chính sách Comtrade:* UN Comtrade có hỗ trợ mirror comparison và classification conversion, nhưng Comtrade xác nhận chỉ giữ phiên bản dữ liệu hiện tại mà không lưu trữ kho lưu trữ lịch sử nhiều phiên bản (no version/revision archive).
  * *Điểm khác biệt / Khe hở kỹ thuật:* Không xây dựng công cụ thay thế Comtrade, mà thiết kế kho dữ liệu phục vụ kiểm toán nội bộ dữ liệu (internal audit). Schema lưu trữ đồng thời cả luồng dữ liệu của nước báo cáo (reporter flow) và luồng đối ứng (mirror flow), lưu vết mã gốc, mã chuyển đổi, phiên bản HS, đơn vị tính, phương thức định giá và snapshot thời gian tải; thực hiện phân tích thành phần (ablation study) để chứng minh cùng một câu hỏi truy vấn sẽ cho kết quả khác nhau tùy thuộc vào phương pháp chuẩn hóa dữ liệu.

* **Nguồn dữ liệu chính & Mức độ dễ tiếp cận:**  
  * *UN Comtrade API & WITS Metadata:* Thống kê thương mại theo reporter, partner, product (HS 85), flow, period.
  * *Mức độ tiếp cận:* Dữ liệu công khai, có thể dùng API Preview / Free hoặc tải file; **không cần cấp phép IRB / DUA**. Tuy nhiên, việc trích xuất hàng loạt không giám sát (bulk/unattended extraction) có giới hạn hạn mức (rate limit / request quotas).

* **Cách đo / Công thức đánh giá chính:**  
  * *Phạm vi nghiên cứu:* Việt Nam, nhóm ngành HS 85, 5 đối tác thương mại lớn nhất, giai đoạn 2015–2024.
  * *Chỉ số đánh giá (Metrics):* Tỷ số bất đối xứng gương (Mirror asymmetry ratio), mức độ biến động khi chuyển đổi phiên bản HS (HS conversion impact via ablation), độ bao phủ quan sát (Coverage), tỷ lệ thiếu dữ liệu (Missingness), và độ ổn định chuỗi số liệu sau cập nhật (Stability after revisions).

* **Rủi ro lớn nhất / Điều chưa xác nhận (Gate pilot test):**  
  * *Rủi ro:* Comtrade và WITS thuộc cùng một hệ sinh thái dữ liệu (không phải 2 nguồn độc lập hoàn toàn); đối tác báo cáo thiếu dữ liệu hoặc không đều đặn qua các năm.
  * *Gate kiểm tra:* Chạy pilot test tải mẫu số liệu thực tế; kiểm tra tính liên tục của dữ liệu 5 đối tác (missingness phải được ghi nhận như một kết quả phân tích, tuyệt đối không tự ý nội suy hoặc điền số 0); kiểm tra giới hạn request của API.

* **Khối lượng công việc ước tính:**  
  * Mức độ: **Vừa – Cao (khoảng 10–12 tuần)**; khối lượng ETL cao hơn do phải xử lý chuyển đổi phiên bản HS và đối soát luồng gương.

---

### ĐỀ TÀI 3: KHOA HỌC TRÁI ĐẤT (EARTH SCIENCES)

* **Tên đề tài (bản đã thu hẹp / final):**  
  *“Kho dữ liệu chất lượng-aware cho phân tích sự kiện ngập bằng dữ liệu Sentinel-1 và GPM tại một tiểu vùng Đồng bằng sông Cửu Long”*  
  *(Tên chi tiết trong đề xuất: Thiết kế và đánh giá kho dữ liệu chất lượng-aware cho tổng hợp sự kiện ngập từ Sentinel-1, GPM IMERG và SRTM tại một tiểu vùng Đồng bằng sông Cửu Long giai đoạn 2018–2024).*

* **Vấn đề / Câu hỏi nghiên cứu:**  
  * *Câu hỏi nghiên cứu:* Việc mô hình hóa chất lượng quan sát (quality flag), dữ liệu thiếu (missingness) và độ lệch thời gian (temporal misalignment) trong kho dữ liệu ảnh hưởng thế nào đến độ đầy đủ và độ ổn định của các truy vấn tổng hợp sự kiện ngập?
  * *Giả thuyết:* Một kho dữ liệu có chiều thông tin chất lượng/nguồn gốc (quality/provenance dimension) giúp phát hiện các sự kiện có số liệu thống kê không đáng tin cậy và làm thay đổi kết luận tổng hợp so với kho dữ liệu truyền thống chỉ lưu giá trị ngập đơn thuần.

* **Vì sao có khe hở (Khác biệt so với hệ thống / paper đã có):**  
  * *Hệ thống / Paper đã khảo sát:* GeoCube, ecodatacube.eu, Ocean-DC, NASA Harmony / Earthdata GIS, Copernicus Data Space STAC, USGS ComCat + ShakeMap, NOAA Climate Data Online, Sentinel-1 Global Flood Monitoring (GFM).
  * *Điểm khác biệt / Khe hở kỹ thuật:* Các hệ thống hiện hành như GFM tập trung vào giám sát diện rộng toàn cầu / thời gian thực; STAC/Harmony tối ưu hóa catalog và truy xuất file; GeoCube/Ocean-DC tối ưu tạo khối ảnh raster tổng quát. Đề tài không cạnh tranh thuật toán flood mapping hay deep learning, mà giải quyết bài toán Data Warehouse: thiết kế kho dữ liệu hướng sự kiện (event-centric DW) tích hợp chiều chất lượng (quality dimension) để kiểm toán độ tin cậy của truy vấn thiên tai khi có sự lệch pha thời gian và độ phân giải giữa ảnh radar Sentinel-1, lượng mưa vệ tinh GPM và địa hình SRTM.

* **Nguồn dữ liệu chính & Mức độ dễ tiếp cận:**  
  * *Copernicus Sentinel-1 GRD (qua CDSE STAC API):* Dữ liệu ảnh radar xác định diện tích mặt nước / ngập.
  * *NASA GPM IMERG:* Lượng mưa tích lũy trước, trong và sau sự kiện.
  * *NASA/USGS SRTM DEM:* Dữ liệu độ cao địa hình.
  * *Global Surface Water:* Lớp bản đồ mặt nước thường trực làm nền tham chiếu.
  * *Mức độ tiếp cận:* Dữ liệu hoàn toàn công khai, có API/STAC catalog chuẩn hóa; **không cần cấp quyền IRB / DUA**.

* **Cách đo / Công thức đánh giá chính:**  
  * *Phạm vi nghiên cứu:* 1 tiểu vùng tại ĐBSCL (1–2 tỉnh), 5–10 sự kiện ngập lớn giai đoạn 2018–2024.
  * *Chỉ số đánh giá (Metrics):* Diện tích ngập theo sự kiện, lượng mưa tích lũy cửa sổ 1–3 ngày, tỷ lệ bao phủ dữ liệu (Coverage ratio), tỷ lệ pixel bị thiếu (Missing pixel ratio), độ trễ thu nạp dữ liệu (Ingestion latency), độ lệch thời gian (Temporal gap), và mức độ biến động của kết quả tổng hợp khi thay đổi ngưỡng lọc chất lượng (Quality thresholds).

* **Rủi ro lớn nhất / Điều chưa xác nhận (Gate pilot test):**  
  * *Rủi ro:* Khối lượng xử lý dữ liệu raster không gian quá lớn gây quá tải đường ống ETL và hạ tầng lưu trữ.
  * *Gate kiểm tra:* Thực hiện cắt nhỏ phạm vi không gian (chọn trước 1 tiểu vùng), chỉ trích xuất và lưu trữ chỉ số thống kê / tile đã xử lý sẵn thay vì nạp toàn bộ ảnh raster thô; xác nhận tính đồng bộ về thời gian giữa ảnh Sentinel-1 và dữ liệu mưa GPM cho 5–10 sự kiện đã chọn.

* **Khối lượng công việc ước tính:**  
  * Báo cáo gốc ghi: **Khả thi cao với nhóm 2 người trong 1 học kỳ** *(Báo cáo gốc chưa nêu số tuần cụ thể)*.

---

## 3. BẢNG SO SÁNH CHÉO 3 ĐỀ TÀI

| Tiêu chí so sánh | Đề tài 1: Y tế (CDC WONDER vs GBD) | Đề tài 2: Kinh tế (Comtrade Mirror Trade) | Đề tài 3: Khoa học Trái đất (Sentinel-1 & GPM Flood DW) |
| :--- | :--- | :--- | :--- |
| **1. Độ khó kỹ thuật & ETL** | **Vừa**<br>• Dữ liệu bảng (tabular/aggregate).<br>• ETL tập trung vào mapping mã bệnh ICD-10/GBD và chuẩn hóa đơn vị/dân số. | **Vừa – Cao**<br>• Dữ liệu bảng nhưng phức tạp do bảng đối chiếu chuyển đổi phiên bản mã HS qua các năm.<br>• Phải xử lý logic đối soát đa luồng (reporter flow vs mirror flow, FOB/CIF). | **Vừa – Cao**<br>• Dữ liệu raster viễn thám kết hợp bảng biểu.<br>• Phải tiền xử lý trích xuất raster statistics và căn chỉnh lưới không gian – thời gian (spatio-temporal alignment). |
| **2. Rào cản truy cập dữ liệu** | **Rất thấp**<br>• Nguồn aggregate công khai (CDC WONDER, GBD).<br>• Không cần CITI, không cần DUA, không thông tin cá nhân. | **Thấp**<br>• Nguồn công khai (UN Comtrade, WITS).<br>• Không cần DUA/IRB.<br>• Cần lưu ý hạn mức request API khi kéo dữ liệu tự động. | **Thấp**<br>• Nguồn công khai qua API/STAC (Copernicus CDSE, NASA Earthdata).<br>• Không cần DUA/IRB.<br>• Cần tải và lưu trữ file raster đã cắt. |
| **3. Độ rõ của tính mới (Technical Novelty)** | **Rõ ràng (Mức vừa – cao)**<br>• Khác biệt ở cơ chế lineage, snapshot và audit query giải thích sai lệch số liệu tử vong (thay vì bài toán dịch tễ học thuần túy). | **Rõ ràng (Mức vừa – cao)**<br>• Khác biệt ở schema lưu trữ đồng thời snapshot đa phiên bản và kiểm toán tác động của chuyển đổi mã HS (Comtrade chỉ lưu bản cuối). | **Rõ ràng (Mức vừa)**<br>• Khác biệt ở kho dữ liệu hướng sự kiện gắn kèm chiều chất lượng (quality-aware), không cạnh tranh thuật toán nhận diện ngập với GFM. |
| **4. Mức phù hợp môn Kho dữ liệu** *(Schema / ETL / Dimension)* | **Rất cao**<br>• Thiết kế Star schema kinh điển rõ ràng (`fact_mortality`, các dimension về định nghĩa, phiên bản, dân số).<br>• Đo lường giá trị trực tiếp bằng truy vấn SQL so sánh và kiểm toán. | **Rất cao**<br>• Schema phân tích luồng gương và phiên bản phân loại.<br>• Thể hiện rõ kỹ thuật ETL chuyển đổi dimension và truy vấn kiểm toán độ lệch số liệu thương mại. | **Cao**<br>• Schema hướng sự kiện kết hợp chiều chất lượng dữ liệu (`dim_quality`, `dim_provenance`, `fact_flood_event`).<br>• Đòi hỏi thiết kế ETL kết hợp xử lý không gian (PostGIS/DuckDB). |
| **5. Rủi ro lớn nhất** | • Không mapping được hoàn toàn mã CKD giữa ICD-10 (N18) và danh mục GBD.<br>• Bị phản biện "đã có paper so sánh dịch tễ học". | • Comtrade và WITS chung hệ sinh thái (không phải 2 nguồn độc lập tuyệt đối).<br>• Dữ liệu đối tác bị thiếu (missingness) làm gián đoạn chuỗi quan sát. | • Pipeline ETL bị quá tải nếu xử lý raster viễn thám không đúng cách.<br>• Thiếu sự kiện ngập có đủ ảnh radar trùng khớp với ngày mưa lớn. |

---

## 4. NHỮNG ĐIỂM CÒN TỒN ĐỌNG / CẦN QUYẾT ĐỊNH TRƯỚC KHI CHỐT ĐỀ TÀI

Để đảm bảo việc lựa chọn đề tài diễn ra suôn sẻ và tránh rủi ro vỡ tiến độ, nhóm cần làm rõ và đưa ra quyết định đối với các điểm còn thiếu hoặc giả định chưa kiểm chứng sau đây:

### A. Kiểm chứng kỹ thuật bắt buộc (Pilot Test Gates trong 3–5 ngày)
1. **Đối với Đề tài Y tế:**
   - *Kiểm tra mapping mã bệnh:* Cần tải dữ liệu mẫu thực tế của CDC WONDER (mã N18) và GBD Results (danh mục CKD) để xác nhận hai bên có khớp nối được ở cấp độ tuổi/giới tính/năm hay không. Nếu không khớp, nhóm cần thống nhất trước: có chấp nhận mở rộng sang category rộng hơn (*chronic kidney disease & renal failure*) hay chuyển sang đề tài H3 (drift metadata giữa WHO và OWID)?
2. **Đối với Đề tài Kinh tế:**
   - *Kiểm tra độ bao phủ dữ liệu:* Tải thử dữ liệu mã HS 85 của Việt Nam giai đoạn 2015–2024 với 5 đối tác lớn trên UN Comtrade. Cần xác nhận 5 đối tác này có báo cáo đầy đủ cả 10 năm không và tỷ lệ thiếu dữ liệu là bao nhiêu.
   - *Kiểm tra hạn mức API:* Thử nghiệm cơ chế trích xuất batch để xem có bị chặn rate-limit của UN Comtrade API hay không.
3. **Đối với Đề tài Khoa học Trái đất:**
   - *Khảo sát sự kiện ngập & dữ liệu ảnh:* Xác định chính xác 1–2 tỉnh ở ĐBSCL và lập danh sách 5–10 sự kiện ngập lịch sử (2018–2024). Cần kiểm tra trên Copernicus CDSE xem tại các ngày diễn ra sự kiện có ảnh Sentinel-1 khả dụng (không bị lỗi hoặc lệch ngày quá xa so với dữ liệu mưa GPM IMERG) hay không.
   - *Thử nghiệm pipeline raster:* Viết script tiền xử lý mẫu (cắt tile, tính diện tích ngập và xuất ra dạng bảng aggregate) để đảm bảo không bị nghẽn tài nguyên phần cứng.

### B. Những thông tin báo cáo gốc còn thiếu / Cần thống nhất
1. **Ước tính thời gian chi tiết:**
   - Đề tài Y tế và Kinh tế có ước tính cụ thể là **10–12 tuần**.
   - Đề tài Khoa học Trái đất **chưa có con số tuần chi tiết** (chỉ ghi chung là "khả thi cao trong 1 học kỳ"). Cần xây dựng bảng kế hoạch phân bổ thời gian chi tiết cho đề tài này nếu nhóm muốn cân nhắc.
2. **Lựa chọn công nghệ & Hệ quản trị cơ sở dữ liệu (DBMS / Warehouse Engine):**
   - Cả 3 báo cáo đều chưa chốt hệ quản trị cơ sở dữ liệu cụ thể cho kho dữ liệu (ví dụ: PostgreSQL, DuckDB, ClickHouse, hay BigQuery/Snowflake). Nhóm cần thống nhất stack công nghệ phù hợp với năng lực thành viên.
3. **Kiểm tra trùng lặp tài liệu sâu hơn (Literature Novelty Check):**
   - Cần thực hiện tìm kiếm tài liệu học thuật theo đúng phạm vi hẹp đã chốt của từng đề tài để đảm bảo không bị trùng lặp với các đồ án / công bố gần nhất (đặc biệt là bài báo so sánh CDC WONDER - GBD năm 2026 trong Y tế và các paper về Spatio-temporal DW năm 2026 trong Khoa học Trái đất).