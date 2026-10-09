# Tên đề tài: Xây dựng kho dữ liệu điện năng và thời tiết phục vụ dự báo phụ tải thích nghi có chọn lọc trước sự thay đổi phân phối dữ liệu (A Drift-Attributed Energy–Weather Data Warehouse for Selective Adaptive Electricity Load Forecasting)
## 1.	Đặt vấn đề: 
Trong vận hành hệ thống điện thông minh (Smart Grid) và tích hợp năng lượng tái tạo, dự báo phụ tải điện (Electricity Load Forecasting) là bài toán sống còn nhằm lập kế hoạch phát điện tối ưu và đảm bảo an ninh hệ thống. Nhu cầu sử dụng điện luôn chịu ảnh hưởng mật thiết từ các yếu tố thời tiết (nhiệt độ, bức xạ mặt trời) và nhịp độ sinh hoạt xã hội. Tuy nhiên, theo thời gian dài, phân phối dữ liệu tiêu thụ liên tục biến đổi (hiện tượng trôi dạt dữ liệu - *concept drift*), khiến độ chính xác của các mô hình AI dự báo phụ tải bị suy giảm nghiêm trọng. Ví dụ: khi gặp một đợt nắng nóng gay gắt đột ngột, phụ tải điện tăng vọt do người dân đồng loạt bật máy lạnh; sau khi đợt nóng kết thúc, phụ tải lại trở về mức bình thường. Các hệ thống hiện nay thường áp dụng cơ chế tự động tái huấn luyện (retrain) mô hình mỗi khi phát hiện sai số tăng hoặc theo chu kỳ cố định. Điều này đặt ra câu hỏi: liệu có cần thiết phải tốn tài nguyên máy tính để huấn luyện lại mô hình mỗi khi dữ liệu có biến động hay không?
Khi đó xuất hiện các vấn đề:
-	việc tái huấn luyện mô hình một cách "mù quáng" (blind retraining) mỗi khi sai số tăng làm lãng phí nghiêm trọng tài nguyên tính toán và chi phí vận hành (đi ngược lại xu thế Green AI)
-	tái huấn luyện liên tục trước những biến động thời tiết bất thường ngắn hạn có thể làm mô hình mất tính ổn định và làm sai lệch các quy luật tiêu thụ dài hạn đã học
-	các kho dữ liệu hiện tại chỉ đóng vai trò lưu trữ thụ động, chưa có cơ chế bóc tách nguyên nhân gây ra sai lệch dữ liệu (*drift attribution*) để hỗ trợ quyết định vận hành mô hình

    Vấn đề cốt lõi: Có thể sử dụng một Kho dữ liệu đa chiều tích hợp điện năng và thời tiết để nhận biết nguyên nhân gây ra trôi dạt dữ liệu, từ đó quyết định tái huấn luyện mô hình dự báo một cách có chọn lọc nhằm vừa duy trì độ chính xác vừa tiết kiệm tài nguyên tính toán hay không? Nghiên cứu xây dựng một kho dữ liệu điện năng – thời tiết tích hợp cơ chế phân loại nguyên nhân trôi dạt (Drift Attribution): khi sự sai lệch chỉ do biến động thời tiết tự nhiên thì giữ nguyên mô hình dự báo; khi phát hiện trôi dạt do thay đổi hành vi tiêu thụ thực sự làm suy giảm mô hình thì mới kích hoạt tái huấn luyện có chọn lọc (Selective Retraining), giúp tối ưu hóa chi phí điện toán mà vẫn bảo đảm độ chính xác.
## 2.	Data:
Dữ liệu năng lượng và khí tượng công khai chuẩn quốc tế, gồm 2 nguồn chính và 2 nguồn bổ sung:
-	**Dữ liệu điện năng (Open Power System Data - OPSD Time-series):** Phụ tải điện thực tế (Actual Load MW), sản lượng điện gió, điện mặt trời và giá điện thị trường, phủ 37 quốc gia châu Âu (trọng tâm: Đức). Ngừng cập nhật tích cực từ 2020.
-	**Dữ liệu thời tiết (OPSD Weather Data):** Nhiệt độ (°C), bức xạ mặt trời trực tiếp và khuếch tán — tổng hợp từ **NASA MERRA-2 reanalysis** (bởi Renewables.ninja), trung bình có trọng số dân số ở cấp quốc gia. Dữ liệu đến hết 2019.
-	**Dữ liệu kiểm thử mở rộng (UCI Electricity Load Diagrams):** Số đo tiêu thụ điện của 370 hộ tiêu thụ riêng biệt (140.256 mốc thời gian, không thiếu giá trị), giai đoạn 2011–2014, dùng để kiểm định tính tổng quát.
-	**Nguồn bổ sung 1 — ENTSO-E Transparency Platform:** Phụ tải thực tế theo giờ, tiếp tục cập nhật từ 2016 đến hiện tại — dùng để nối dài chuỗi thời gian sau khi OPSD ngừng cập nhật (2020).
-	**Nguồn bổ sung 2 — ERA5 Reanalysis (ECMWF/Copernicus):** Nhiệt độ, bức xạ, gió dạng lưới địa lý chi tiết (0.25°) — dùng để tự tính đặc trưng thời tiết theo vùng mong muốn, thay vì phụ thuộc mức gộp quốc gia sẵn có của OPSD Weather, giúp `Dim_Region` có ý nghĩa phân tích thực sự.
-	Độ phân giải thời gian: 15 phút – 1 giờ tùy nguồn.
-	Giai đoạn dữ liệu tổng thể dự kiến sử dụng: 2015–nay (nhờ nối dài bằng ENTSO-E/ERA5), trong đó phần lõi OPSD 2015–2019/2020 có chất lượng đã được kiểm chứng bởi nhóm nghiên cứu học thuật (TU Berlin, DIW Berlin).
## 3.	Khoảng trống nghiên cứu

| Công trình | Đã giải quyết | Phần còn thiếu so với đề tài |	Link |
| :--- | :--- | :--- | :--- |
| Open Power System Data: Frictionless data for electricity system modelling (Wiese et al., 2019) | Thu thập, chuẩn hóa và cung cấp dữ liệu phụ tải, năng lượng tái tạo và thời tiết theo giờ cho các quốc gia châu Âu trên một nền tảng mở. | Chỉ là nền tảng phân phối và làm sạch dữ liệu bảng tĩnh, chưa xây dựng kiến trúc Data Warehouse đa chiều (Constellation schema) phục vụ MLOps và giám sát trôi dạt dữ liệu thời gian thực. | https://doi.org/10.1016/j.apenergy.2018.11.097 |
| Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting (Lim et al., 2021) | Ứng dụng mô hình học sâu kết hợp đa biến đầu vào (thời tiết, lịch mùa vụ) để dự báo chuỗi thời gian phụ tải với độ chính xác cao và có khả năng giải thích. | Giả định mô hình là tĩnh sau khi huấn luyện; chưa giải quyết vấn đề trôi dạt dữ liệu theo thời gian dài và chưa có cơ chế thích nghi khi phân phối dữ liệu thay đổi. | https://doi.org/10.1016/j.ijforecast.2021.03.012 |
| Learning under Concept Drift: A Review (Lu et al., 2019) | Khảo sát toàn diện các phương pháp phát hiện trôi dạt khái niệm (concept drift) và chiến lược thích ứng (adaptive learning) trong luồng dữ liệu. | Tổng kết lý thuyết chung, chưa đi sâu vào bài toán chuỗi thời gian năng lượng – thời tiết; chưa giải quyết bài toán bóc tách nguyên nhân drift (drift attribution) để tránh retrain lãng phí. | https://arxiv.org/pdf/2004.05785 |
| A Time Series is Worth 64 Words: Long-Term Forecasting with Transformers - PatchTST (Nie et al., 2023) | Mô hình Transformer dạng patch đạt hiệu năng vượt trội trong dự báo chuỗi thời gian dài hạn bao gồm phụ tải điện và thời tiết. | Chi phí tính toán để huấn luyện lại (retraining cost) rất lớn; việc tái huấn luyện tự động mỗi khi phát hiện drift là cực kỳ tốn kém nếu không có cơ chế lọc chọn lọc. | https://arxiv.org/abs/2211.14730 |
| The ENTSO-E Transparency Platform – A review of Europe's most ambitious electricity data platform (Hirth, Mühlenpfordt & Bulkeley, 2018) | Đánh giá hệ thống nền tảng dữ liệu vận hành lưới điện châu Âu, cập nhật liên tục đến hiện tại (khắc phục hạn chế OPSD ngừng cập nhật từ 2020). | Chính bài báo cũng chỉ ra ENTSO-E TP còn nhiều vấn đề về chất lượng dữ liệu (thiếu, không nhất quán giữa các nguồn); nền tảng không có cơ chế kho dữ liệu, giám sát trôi dạt hay hỗ trợ quyết định retrain. | https://doi.org/10.1016/j.apenergy.2018.04.048 |
| The ERA5 global reanalysis (Hersbach et al., 2020) | Cung cấp dữ liệu tái phân tích khí tượng toàn cầu độ phân giải cao (~31km/0.25°, hourly), khắc phục hạn chế OPSD Weather chỉ có 1 giá trị/quốc gia/giờ. | Là nguồn dữ liệu khí tượng thuần túy, hoàn toàn độc lập với dữ liệu điện năng; không có cơ chế liên kết với phụ tải điện, không phân biệt được ảnh hưởng thời tiết (Covariate Shift) với thay đổi hành vi tiêu thụ (Concept Drift) — việc này đề tài phải tự xây dựng. | https://doi.org/10.1002/qj.3803 |
 

## 4.	Tóm tắt nội dung và các kỹ thuật của nghiên cứu
Quy trình dự kiến:
Dữ liệu Điện & Thời tiết → Kho dữ liệu (Constellation Schema) → Phát hiện Drift & Bóc tách nguyên nhân → Tái huấn luyện có chọn lọc → Dự báo thích ứng
Các bước chính:
1.	Thu thập và làm sạch dữ liệu phụ tải, thời tiết và giá điện từ OPSD, ENTSO-E và ERA5; đồng bộ hóa thống nhất theo múi giờ chuẩn UTC; đối chiếu độ nhất quán OPSD–ENTSO-E ở giai đoạn chồng lấn (2016–2020).
2.	Thiết kế và cài đặt Kho dữ liệu theo mô hình chòm sao (Constellation Schema) gồm các chiều Dim_Time, Dim_Region và các bảng sự kiện Fact_Load, Fact_Weather, Fact_Price, Fact_Forecast.
3.	Tạo các đặc trưng chuỗi thời gian trực tiếp trong kho dữ liệu (In-Warehouse Features): đặc trưng độ trễ (lags 1h, 24h, 168h), thống kê trượt (rolling mean 24h, rolling std 7d) và tương tác phi tuyến thời tiết (Temperature^2, Temperature × Hour).
4.	Tích hợp cơ chế phát hiện trôi dạt dữ liệu bằng ADWIN, KSWIN và khoảng cách Wasserstein; lưu vết toàn bộ lịch sử biến động vào bảng sáng tạo Fact_DriftEvent.
5.	Xây dựng thuật toán bóc tách nguyên nhân trôi dạt (Drift Attribution): phân biệt trôi dạt do thời tiết biến động (Covariate Shift) và trôi dạt do thay đổi hành vi tiêu thụ (Harmful Concept Drift).
6.	Cài đặt chiến lược tái huấn luyện có chọn lọc (Selective Retraining): chỉ kích hoạt huấn luyện lại khi xảy ra trôi dạt có hại làm suy giảm mô hình; giữ nguyên mô hình khi biến động chỉ là thời tiết ngắn hạn.
7.	So sánh
-	S0: Không tái huấn luyện (No retraining)
-	S1: Tái huấn luyện định kỳ hàng tuần (Weekly retraining)
-	S2: Tái huấn luyện định kỳ hàng tháng (Monthly retraining)
-	S3: Tái huấn luyện mù quáng mỗi khi phát hiện drift (Naive drift-triggered retraining)
-	S4: Phương pháp đề xuất - Tái huấn luyện có chọn lọc theo nguyên nhân drift (Selective adaptive retraining).
8.	Đánh giá bằng:
-	Sai số dự báo phụ tải: MAE, RMSE, sMAPE, MASE
-	Số lần tái huấn luyện mô hình (Retraining count)
-	Thời gian tính toán và chi phí điện toán (Computation cost)
-	Tỷ lệ cảnh báo trôi dạt sai lệch (False drift alarms)
-	Hàm thỏa dụng thích ứng: AdaptiveUtility = ForecastError + λ × RetrainingCost.