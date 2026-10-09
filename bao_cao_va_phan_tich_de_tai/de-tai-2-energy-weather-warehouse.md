# Đề tài: Energy + Weather Data Warehouse for Adaptive Forecasting

> **Tài liệu dẫn chứng khoa học & Phân tích chi tiết đề tài đề xuất (Proposal Evidence & Appendix)**  
> **Tên đề xuất chuẩn hóa:** Xây dựng kho dữ liệu điện năng và thời tiết phục vụ dự báo phụ tải thích nghi có chọn lọc trước sự thay đổi phân phối dữ liệu  
> *(A Drift-Attributed Energy–Weather Data Warehouse for Selective Adaptive Electricity Load Forecasting)*  
> **Lĩnh vực:** Kho dữ liệu (Data Warehouse), Lưới điện thông minh (Smart Grid) & MLOps thích ứng (Adaptive Time-Series)

---

## 1. Bối cảnh & Vấn đề nghiên cứu

### 1.1. Bối cảnh thực tiễn
Trong hệ thống quản lý năng lượng hiện đại và quá trình chuyển dịch sang năng lượng tái tạo, **dự báo phụ tải điện (Electricity Load Forecasting)** là nhiệm vụ sống còn. Dự báo chính xác nhu cầu sử dụng điện giúp các nhà điều hành lưới điện lập kế hoạch huy động nguồn phát tối ưu, giảm thiểu chi phí phát điện dự phòng và ngăn ngừa nguy cơ sự cố quá tải hệ thống.

### 1.2. Vấn đề cốt lõi (Giải thích trực quan cho người ngoài ngành)
Phụ tải điện chịu tác động trực tiếp và liên tục từ hai yếu tố:
1. **Điều kiện thời tiết:** Khi nắng nóng gay gắt, người dân đồng loạt bật máy lạnh; khi mùa đông lạnh giá, nhu cầu sưởi ấm tăng vọt.
2. **Hành vi tiêu thụ & Kinh tế - Xã hội:** Các ngày nghỉ lễ, ngày cuối tuần, hoặc những biến động kinh tế làm thay đổi nhịp sinh hoạt và sản xuất.

Trong vận hành dài hạn, các mối quan hệ này liên tục thay đổi theo thời gian — hiện tượng này trong khoa học dữ liệu gọi là **sự trôi dạt dữ liệu (Concept Drift / Distribution Shift)**. Khi xảy ra trôi dạt, các mô hình AI dự báo phụ tải sẽ nhanh chóng bị sai lệch nghiêm trọng.

### 1.3. Nút thắt kỹ thuật hiện nay
Giải pháp thông thường hiện nay là áp dụng cơ chế **"tái huấn luyện mù quáng" (Blind Retraining)**: cứ thấy sai số của mô hình tăng vượt ngưỡng, hệ thống lại tự động mang toàn bộ dữ liệu đi huấn luyện lại mô hình AI từ đầu. 
Cách làm này bộc lộ nhược điểm rất lớn:
* Gây lãng phí tài nguyên máy tính và năng lượng khổng lồ (đi ngược lại xu thế *Green AI*).
* Có thể làm mất tính ổn định của mô hình khi sự biến động chỉ bắt nguồn từ một đợt thời tiết dị thường ngắn hạn (ví dụ: một đợt nắng nóng vài ngày) chứ không phải do thói quen tiêu dùng điện đã thay đổi vĩnh viễn.

👉 **Vấn đề nghiên cứu đặt ra:** Làm thế nào để xây dựng một **Kho dữ liệu (Data Warehouse)** đa chiều tích hợp song song cả điện năng và khí tượng, đóng vai trò "bộ não" phân tích nguyên nhân sai lệch (*Drift Attribution*), từ đó giúp hệ thống biết chính xác **khi nào thực sự cần huấn luyện lại mô hình**, và **khi nào chỉ cần giữ nguyên** để tối ưu hóa tài nguyên?

---

## 2. Khoảng trống nghiên cứu (Research Gap)

### 2.1. Hiện trạng nghiên cứu (State-of-the-Art)
* **Dự báo phụ tải kết hợp thời tiết:** Đã được nghiên cứu rộng rãi với các mô hình học máy từ truyền thống (Linear Regression, LightGBM, XGBoost) đến học sâu chuỗi thời gian tiên tiến (LSTM, N-BEATS, Temporal Fusion Transformer, PatchTST).
* **Phát hiện trôi dạt dữ liệu (Drift Detection):** Các thuật toán như ADWIN, KSWIN, Page-Hinkley, PELT và các độ đo khoảng cách phân phối xác suất (Wasserstein distance, Population Stability Index - PSI, KL-Divergence) đã được chứng minh hiệu quả trong việc phát hiện thời điểm phân phối thay đổi.
* **Quy trình tái huấn luyện tự động (Continuous Retraining):** Các công trình gần đây (2025–2026) đã đề xuất việc kết hợp bộ dò drift để kích hoạt tái huấn luyện tự động cho các mô hình chuỗi thời gian.

### 2.2. Khoảng trống khoa học cần giải quyết (The Research Gaps)
Mặc dù bài toán dự báo điện và phát hiện drift đều không mới, nhưng việc kết nối chúng qua một kiến trúc Kho dữ liệu tạo ra 3 khoảng trống nghiên cứu có giá trị cao:

* **Khoảng trống 1 — Bóc tách nguyên nhân gây trôi dạt (Drift Attribution):**  
  Phần lớn các nghiên cứu xem drift là một "hộp đen" và kích hoạt retrain ngay khi có cảnh báo. Tuy nhiên, sự dịch chuyển phân phối dữ liệu gồm 2 bản chất khác biệt:
  * *Dịch chuyển biến độc lập lành tính (Covariate Shift):* Nhiệt độ tăng từ 20°C lên 37°C làm phụ tải tăng vọt. Bản chất mối quan hệ vật lý giữa nhiệt độ và tải không đổi, mô hình tích hợp biến thời tiết vẫn xử lý tốt mà không cần retrain.
  * *Trôi dạt khái niệm có hại (Harmful Concept Drift):* Thời tiết hoàn toàn bình thường nhưng thói quen sử dụng điện của người dân/doanh nghiệp thay đổi đột ngột (ví dụ: chuyển dịch sang xe điện hàng loạt, thay đổi ca kíp sản xuất). Đây mới là lúc mô hình thực sự bị lỗi thời và bắt buộc phải retrain.
* **Khoảng trống 2 — Tái huấn luyện thích nghi có chọn lọc (Selective Retraining):**  
  Chưa có cơ chế tối ưu hóa sự đánh đổi giữa **độ chính xác dự báo** và **chi phí tính toán**. Mục tiêu đặt ra là giảm thiểu số lần retrain (giảm chi phí điện toán) nhưng vẫn duy trì hoặc cải thiện độ chính xác so với việc retrain liên tục.
* **Khoảng trống 3 — Nâng tầm vai trò của Kho dữ liệu trong hệ thống MLOps:**  
  Thông thường, Data Warehouse chỉ đóng vai trò kho chứa dữ liệu thụ động. Trong đề tài này, Data Warehouse được thiết kế chủ động với bảng sự kiện đặc thù (`Fact_DriftEvent`), trực tiếp lưu vết lịch sử trôi dạt, phục vụ phân tích đa chiều (OLAP) về độ ổn định của lưới điện và hỗ trợ quyết định vận hành mô hình.

---

## 3. Nguồn dữ liệu dự kiến & Đánh giá tích hợp ETL

### 3.1. Danh mục các nguồn dữ liệu sử dụng

| Tên nguồn dữ liệu | Đơn vị chủ quản / Nguồn gốc thật | Dạng dữ liệu & Nội dung chính | Độ phân giải | Phạm vi thời gian | Độ khả dụng |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Open Power System Data (OPSD) – Time-series** | TU Berlin / DIW Berlin / Neon Neue Energieökonomik (dự án học thuật Đức, dữ liệu gốc từ ENTSO-E) | Phụ tải thực tế (Actual Load MW), sản lượng điện gió/mặt trời, giá điện thị trường, phủ 37 quốc gia châu Âu | 15 phút – 1 giờ tùy quốc gia | 2015 – 2020 (ngừng cập nhật tích cực từ 2020) | Công khai 100%, tải trực tiếp CSV/SQLite |
| **OPSD Weather Data** | Renewables.ninja, tổng hợp từ **NASA MERRA-2 reanalysis** (không phải ERA5) | Nhiệt độ, bức xạ trực tiếp/khuếch tán — **trung bình có trọng số dân số ở cấp quốc gia**, không phân giải theo vùng trong nước | 1 giờ | Đến hết **2019** | Công khai 100%, CSV/SQLite |
| **UCI Electricity Load Diagrams (ElectricityLoadDiagrams20112014)** *(benchmark phụ)* | UCI Machine Learning Repository | Tiêu thụ điện của 370 khách hàng riêng biệt (140.256 mốc thời gian, không thiếu giá trị) | 15 phút | 2011 – 2014 | Mở, dùng kiểm thử tổng quát hóa |
| **ENTSO-E Transparency Platform** *(nguồn bổ sung, khuyến nghị thêm)* | European Network of Transmission System Operators | Phụ tải thực tế theo giờ, tiếp tục cập nhật từ 2016 đến hiện tại | 1 giờ | 2016 – nay | Công khai, tải theo từng nước/tháng |
| **ERA5 Reanalysis (thật)** *(nguồn bổ sung, khuyến nghị thêm)* | ECMWF / Copernicus Climate Change Service | Nhiệt độ, bức xạ, gió — dạng lưới địa lý chi tiết (0.25°), có thể tự tính trung bình theo vùng tùy ý thay vì phụ thuộc cách gộp sẵn của OPSD | 1 giờ | 1940 – nay | Công khai, cần tài khoản CDS API |

### 3.2. Vì sao thêm 2 nguồn bổ sung?

- **OPSD dừng cập nhật từ 2020** → nếu chỉ dùng OPSD, dữ liệu "mới nhất" của đồ án chỉ đến 2019-2020. Bổ sung **ENTSO-E Transparency Platform** giúp mở rộng chuỗi thời gian đến hiện tại, tăng độ thuyết phục khi thầy hỏi "sao dữ liệu cũ vậy".
- **Dữ liệu thời tiết OPSD chỉ có 1 giá trị/quốc gia/giờ** → nếu đề tài muốn `Dim_Region` có ý nghĩa thực sự (so sánh vùng miền, không chỉ so sánh quốc gia), nên dùng **ERA5 dạng lưới thô** và tự tính trung bình theo vùng mong muốn, thay vì phụ thuộc cách gộp sẵn (population-weighted) của OPSD.
- Việc này cũng đúng khớp với khoảng trống 1 (Covariate Shift do thời tiết) — cần dữ liệu thời tiết đủ chi tiết để phân biệt thời tiết bất thường **cục bộ** với xu hướng **toàn vùng**.

### 3.3. Đánh giá độ khả thi và kỹ thuật tích hợp (ETL)

- **Khóa ghép nối:** Cả 3 nguồn chính (OPSD Load, OPSD Weather, ENTSO-E) đều dùng `timestamp` (chuẩn ISO-8601) và có thể chuẩn hóa về `country_code` (ISO-3166) làm khóa vùng — việc join khả thi vì dữ liệu đã được các nguồn chuẩn hóa sẵn ở cấp quốc gia, không phải vì dữ liệu "hoàn hảo tự nhiên".
- **Độ sạch dữ liệu:** OPSD được xử lý và kiểm tra bởi nhóm nghiên cứu học thuật (TU Berlin, DIW Berlin) trước khi công bố, có tài liệu mô tả quy trình làm sạch (README/datapackage.json đi kèm mỗi gói) — nên trích dẫn cụ thể README thay vì đưa ra con số % thiếu dữ liệu không kiểm chứng được.
- **Thách thức ETL cần xử lý:**
  1. *Khác biệt độ phân giải*: OPSD Load có nơi 15 phút, nơi 60 phút — cần resample thống nhất về 1 mức trước khi join với Weather (chỉ có hourly).
  2. *Đồng bộ nguồn Load kép*: Nếu dùng cả OPSD (đến 2020) và ENTSO-E TP (2016 trở đi) để nối dài chuỗi thời gian, cần kiểm tra độ nhất quán giữa 2 nguồn ở giai đoạn chồng lấn (2016-2020) trước khi ghép.
  3. *Đồng bộ múi giờ*: Quy chuẩn toàn bộ về UTC, xử lý DST.
  4. *Nếu dùng ERA5*: cần thêm bước trích xuất giá trị theo tọa độ/vùng mong muốn từ dữ liệu lưới (khác với OPSD Weather đã gộp sẵn) — tăng khối lượng ETL nhưng đổi lại độ chi tiết vùng miền thật sự.
  
---

## 4. Phương pháp & Kiến trúc Kho dữ liệu

### 4.1. Mô hình dữ liệu đa chiều (Constellation / Galaxy Schema)
Kho dữ liệu được thiết kế theo mô hình chòm sao với trung tâm là các bảng Fact theo dòng thời gian và các chiều dùng chung (Conformed Dimensions):

```text
                     ┌──────────────────┐
                     │     Dim_Time     │
                     └────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌───────────┐       ┌────────────┐      ┌────────────┐
    │ Fact_Load │       │Fact_Weather│      │ Fact_Price │
    └─────┬─────┘       └─────┬──────┘      └─────┬──────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │    Dim_Region    │
                     └──────────────────┘
                              ▲
          ┌───────────────────┴───────────────────┐
          │                                       │
    ┌─────┴───────────┐                   ┌───────┴──────────┐
    │  Fact_Forecast  │                   │ Fact_DriftEvent  │
    └─────────────────┘                   └──────────────────┘
```

#### Chi tiết các bảng chính:
* **Chiều chung (Dimensions):**
  * `Dim_Time`: `Time_ID`, `Full_Timestamp`, `Hour`, `Day`, `Weekday`, `Weekend_Flag`, `Holiday_Flag`, `Month`, `Season`.
  * `Dim_Region`: `Region_ID`, `Country_Code`, `Region_Name`, `Timezone`, `Climate_Zone`.
* **Bảng dữ liệu thực tế (Facts):**
  * `Fact_Load`: `Time_ID`, `Region_ID`, `Actual_Load_MW`, `Solar_Gen_MW`, `Wind_Gen_MW`.
  * `Fact_Weather`: `Time_ID`, `Region_ID`, `Temperature_C`, `Direct_Radiation`, `Diffuse_Radiation`, `Wind_Speed`, `Humidity`.
  * `Fact_Forecast`: `Time_ID`, `Region_ID`, `Model_ID`, `Forecast_Horizon`, `Predicted_Load_MW`, `Error_MAE`.
  * **Bảng sáng tạo cốt lõi — `Fact_DriftEvent`:**  
    Ghi nhận dấu vết các đợt biến động dữ liệu: `Event_ID`, `Time_ID`, `Region_ID`, `Feature_Name`, `Drift_Detector`, `Drift_Score`, `Drift_Type` *(Covariate vs Concept)*, `Is_Harmful_Flag`, `Retraining_Triggered`.

### 4.2. Kỹ thuật tạo đặc trưng trực tiếp trong Kho dữ liệu (In-Warehouse Feature Engineering)
* **Đặc trưng độ trễ (Lags):** Tải điện tại thời điểm $t-1$ giờ, $t-24$ giờ (ngày hôm trước), $t-168$ giờ (tuần trước).
* **Đặc trưng thống kê trượt (Rolling Stats):** Giá trị trung bình trượt 24 giờ (`rolling_mean_24h`), độ lệch chuẩn trượt 7 ngày (`rolling_std_7d`).
* **Tương tác phi tuyến thời tiết:** Tạo đặc trưng $\text{Temperature}^2$ và $\text{Temperature} \times \text{Hour}$ để mô phỏng đường cong tiêu thụ hình chữ U (nhu cầu tăng vọt ở cả hai ngưỡng quá lạnh và quá nóng).

### 4.3. Cơ chế dự báo thích nghi có chọn lọc (Selective Adaptive Framework)
* **Mô hình dự báo cơ sở:** Sử dụng **LightGBM** (hiệu năng cao, chạy nhanh, phù hợp tabular time-series) làm mô hình xương sống, kết hợp đối chiếu với mô hình học sâu **N-BEATS** hoặc **PatchTST**.
* **Thuật toán phân biệt nguyên nhân (Drift Attribution Logic):**
  1. Khi bộ phát hiện (ADWIN / KSWIN) ghi nhận sai lệch phân phối: Thuật toán kiểm tra ma trận tương quan giữa độ lệch tải và các biến khí tượng trong `Fact_Weather`.
  2. Nếu sai lệch được giải thích trọn vẹn bởi biến động nhiệt độ (Covariate Shift) $\rightarrow$ Mô hình vẫn trong vùng kiểm soát $\rightarrow$ **Không kích hoạt huấn luyện lại**.
  3. Nếu thời tiết ổn định nhưng sai số mô hình tăng vọt liên tục (Harmful Concept Drift) $\rightarrow$ **Kích hoạt tái huấn luyện có chọn lọc (Selective Retraining)** trên cửa sổ trượt mới nhất.
* **Đo lường hiệu quả (Hàm thỏa dụng - Utility Function):**
  $$\text{AdaptiveUtility} = \text{ForecastError} + \lambda \times \text{RetrainingCost}$$
  Mục tiêu chứng minh: Chiến lược mới đạt sai số tương đương việc retrain liên tục ($\text{Error}_{S4} \le \text{Error}_{S3}$) nhưng số lần retrain giảm từ **40% – 60%** ($\text{Count}_{S4} \ll \text{Count}_{S3}$).

---

## 5. Đóng góp kỳ vọng của đề tài

### 5.1. Đóng góp về mặt học thuật
1. **Mô hình hóa MLOps hướng Kho dữ liệu:** Đề xuất một kiến trúc kho dữ liệu tiên tiến, nơi DW không chỉ là tầng lưu trữ báo cáo mà trực tiếp tham gia vào vòng lặp thích ứng của mô hình thông minh (`Fact_DriftEvent`).
2. **Tiếp cận bài toán Green AI:** Chứng minh bằng thực nghiệm rằng việc bóc tách nguyên nhân trôi dạt dữ liệu (Drift Attribution) giúp tối ưu hóa chi phí tính toán mà không làm suy giảm độ chính xác dự báo.
3. **Tiềm năng công bố khoa học:** Đề tài có tính hoàn chỉnh rất cao, dễ dàng phát triển thành bài báo hội nghị/tạp chí chuyên ngành quốc tế uy tín (xếp hạng Q2 trở lên).

### 5.2. Đóng góp về mặt đồ án môn học & Ứng dụng thực tiễn
* Cung cấp một sản phẩm đồ án mẫu mực cho môn Kho dữ liệu: thiết kế Star/Constellation Schema chuẩn hóa, quy trình ETL tự động hóa xử lý hàng triệu bản ghi, tối ưu hóa truy vấn thời gian thực.
* Sản phẩm đầu ra có tính ứng dụng cao, có thể mở rộng thành Dashboard theo dõi phụ tải và tình trạng ổn định dữ liệu cho các trung tâm điều độ lưới điện.

---

## 6. Tính khả thi & Đánh giá rủi ro

### 6.1. Kế hoạch triển khai chi tiết theo tuần (Khung thời gian 10 - 12 tuần)

| Giai đoạn | Tuần thực hiện | Nội dung công việc cụ thể | Kết quả đầu ra (Deliverables) |
| :--- | :---: | :--- | :--- |
| **Giai đoạn 1: Chuẩn bị dữ liệu** | Tuần 1 – 2 | Tải tập dữ liệu OPSD (Load, Weather, Price) của Đức/châu Âu. Khám phá và làm sạch dữ liệu. | Bộ dữ liệu sạch, script nạp dữ liệu thô. |
| **Giai đoạn 2: Thiết kế & Xây dựng DW** | Tuần 3 – 4 | Thiết kế Constellation Schema trên hệ quản trị CSDL (PostgreSQL / ClickHouse). Viết pipeline ETL nạp dữ liệu vào các bảng Dim/Fact. | Kho dữ liệu vận hành hoàn chỉnh với các khóa liên kết. |
| **Giai đoạn 3: Feature & Drift Pipeline** | Tuần 5 – 6 | Tạo các View/Table đặc trưng (lags, rolling stats). Cài đặt các bộ phát hiện drift (ADWIN, KSWIN) và thiết lập bảng `Fact_DriftEvent`. | Bảng đặc trưng hoàn chỉnh và cơ chế bắt sự kiện drift tự động. |
| **Giai đoạn 4: Thử nghiệm mô hình thích ứng** | Tuần 7 – 8 | Xây dựng mô hình LightGBM và N-BEATS. Thực nghiệm 4 chiến lược cập nhật: Không retrain (S0), Định kỳ (S1), Retrain mù quáng (S3), và Tái huấn luyện có chọn lọc (S4). | Bảng số liệu đối chiếu độ chính xác và số lần retrain. |
| **Giai đoạn 5: Tổng kết & Báo cáo** | Tuần 9 – 10 | Trực quan hóa Dashboard OLAP (Metabase / PowerBI) theo dõi drift và phụ tải. Hoàn thiện báo cáo đồ án môn học. | Báo cáo đồ án hoàn chỉnh, Dashboard demo trực quan. |

### 6.2. Phân tích rủi ro chính và phương án giảm thiểu

| Rủi ro tiềm ẩn | Mức độ | Nguyên nhân | Giải pháp giảm thiểu cụ thể |
| :--- | :---: | :--- | :--- |
| **Lệch pha thời gian giữa các nguồn** | Thấp | Khác biệt về múi giờ hoặc quy ước giờ mùa hè (DST). | Quy chuẩn toàn bộ thời gian về giờ UTC nguyên bản ngay từ bước tiền xử lý của pipeline ETL. |
| **Quá tải tài nguyên máy tính** | Thấp | Chạy các mô hình Deep Learning phức tạp trên chuỗi thời gian nhiều năm. | Sử dụng **LightGBM** làm mô hình chính (chạy mất vài phút trên CPU thông thường). Mô hình Deep Learning (N-BEATS) chỉ chạy trên tập đại diện hoặc tận dụng Google Colab miễn phí. |
| **Tắc nghẽn nguồn dữ liệu** | Không có | Lo sợ nguồn dữ liệu bị chặn hoặc gián đoạn API. | Dữ liệu OPSD và ERA5 là dạng dữ liệu nghiên cứu lịch sử mở, tải trọn gói một lần là có toàn bộ dữ liệu làm đồ án, không phụ thuộc API trực tiếp. |

---

## 7. Kết luận đề xuất

> **Tóm tắt thông điệp bảo vệ trước Giảng viên:**  
> Đề tài **"Energy + Weather Data Warehouse for Adaptive Forecasting"** là phương án lựa chọn tối ưu và an toàn nhất cho đồ án môn Kho dữ liệu. Đề tài sở hữu nguồn dữ liệu sạch chuẩn quốc tế, loại bỏ hoàn toàn rủi ro tắc nghẽn khâu tiền xử lý, đồng thời giải quyết bài toán khoa học giàu tính thời sự: **dùng Kho dữ liệu để phân biệt nguyên nhân trôi dạt dữ liệu, từ đó tái huấn luyện AI có chọn lọc nhằm tiết kiệm điện toán**. Đây là công trình vừa đáp ứng trọn vẹn yêu cầu chuyên môn về mô hình hóa kho dữ liệu, vừa mở ra tiềm năng công bố bài báo khoa học chất lượng cao.
