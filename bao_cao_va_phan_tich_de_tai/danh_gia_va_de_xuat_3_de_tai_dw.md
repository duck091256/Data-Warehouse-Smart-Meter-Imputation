# BÁO CÁO PHÂN TÍCH, SO SÁNH VÀ ĐỀ XUẤT ĐỀ TÀI ĐỒ ÁN KHO DỮ LIỆU (DATA WAREHOUSE)

> **Tài liệu tổng hợp phục vụ thảo luận nhóm và báo cáo giảng viên hướng dẫn**  
> **Dựa trên tài liệu khảo sát:** `phan_tich_3_de_tai_kho_du_lieu.md`

---

## PHẦN 1: TÓM TẮT CHI TIẾT 3 ĐỀ TÀI NGHIÊN CỨU

Dưới đây là phần tóm lược song song 3 đề tài bằng ngôn ngữ dễ hiểu, hạn chế thuật ngữ trừu tượng để mọi thành viên trong nhóm đều có thể nắm bắt nhanh.

---

### 1. ĐỀ TÀI 1: ESG Intelligence Data Warehouse
*(Kho dữ liệu thông tin ESG phát hiện bất nhất công bố và dự báo rủi ro)*

* **Tên đề tài & Lĩnh vực:**  
  * *Tiếng Việt:* Xây dựng kho dữ liệu ESG đa nguồn theo thời gian phục vụ dự báo rủi ro doanh nghiệp và phát hiện bất nhất trong công bố ESG.  
  * *Tiếng Anh:* *A Longitudinal Multi-source ESG Intelligence Data Warehouse for Corporate Risk Prediction and Disclosure-Inconsistency Detection.*  
  * *Lĩnh vực:* Fintech / Tài chính bền vững (ESG & Quản trị rủi ro doanh nghiệp).
* **Vấn đề / Câu hỏi nghiên cứu (giải thích bình dân):**  
  Các doanh nghiệp thường tự viết báo cáo phát triển bền vững rất đẹp (ví dụ: "chúng tôi luôn đảm bảo an toàn lao động, cam kết cắt giảm 40% phát thải"). Nhưng thực tế bên ngoài, báo chí lại đưa tin về đình công, tai nạn lao động, hoặc xả thải trái phép.  
  👉 **Câu hỏi nghiên cứu:** Làm sao xây một kho dữ liệu kết hợp cả "lời doanh nghiệp tự kể" và "tin tức thực tế bên ngoài" để phát hiện sự "nói một đằng làm một nẻo" (bất nhất thông tin), và xem sự bất nhất này có cảnh báo trước sự sụt giảm giá cổ phiếu hay khó khăn tài chính của công ty hay không?
* **Nguồn dữ liệu & Tính khả thi:**  
  * *Báo cáo ESG:* Phải tự cào (crawl) các file PDF từ trang chủ doanh nghiệp (rất tốn công bóc tách văn bản, bảng biểu).  
  * *Báo cáo tài chính:* Hệ thống SEC EDGAR của Mỹ (công khai, miễn phí, chuẩn hóa XBRL).  
  * *Tin tức xã hội:* Cơ sở dữ liệu GDELT 2.0 (công khai, cập nhật sự kiện toàn cầu liên tục).  
  * *Thị trường:* Yahoo Finance (giá cổ phiếu, khối lượng giao dịch).  
  * *Đánh giá dữ liệu:* **Khá (7/10)**. Dữ liệu tài chính và tin tức thì dễ, nhưng xử lý hàng trăm file PDF báo cáo ESG rất vất vả; hơn nữa không có "nhãn chuẩn" (ground truth) sẵn có về việc doanh nghiệp nào thực sự greenwashing.
* **Khoảng trống nghiên cứu (Research Gap):**  
  * Trước đây: Đa số chỉ lấy báo cáo ESG phân tích cảm xúc (sentiment) tại một thời điểm cố định (1 năm/lần), hoặc phụ thuộc vào bảng điểm mua từ các tổ chức đánh giá đắt tiền.  
  * **Điểm chưa ai làm tốt:** Chưa có kho dữ liệu nào đối chiếu theo dòng thời gian liên tục giữa "lời tự công bố" với "bằng chứng tin tức bên ngoài", cũng như chưa chứng minh được sự bất nhất này có giá trị dự báo rủi ro tài chính tốt hơn số liệu kế toán truyền thống hay không.
* **Phương pháp / Mô hình dự kiến:**  
  * *Kho dữ liệu:* Thiết kế lược đồ đa chiều gồm `Fact_ESGDisclosure`, `Fact_ExternalESGEvent`, `Fact_Financial`, `Fact_Market` gắn với `Dim_Company`, `Dim_Time`, `Dim_Source`.  
  * *Mô hình NLP:* Dùng FinBERT / RoBERTa để trích xuất cam kết và mô hình suy luận ngôn ngữ (NLI) để tìm điểm mâu thuẫn giữa cam kết và tin tức.  
  * *Mô hình dự báo:* XGBoost, Random Forest hoặc Temporal Fusion Transformer (TFT) để dự báo biến động giá/rủi ro tài chính.
* **Kết quả kỳ vọng / Đóng góp:**  
  * Một kho dữ liệu đa nguồn kết nối dữ liệu phi cấu trúc (PDF, tin tức) với dữ liệu chuỗi thời gian tài chính.  
  * Bộ chỉ số đo lường mức độ bất nhất trong công bố ESG (*Disclosure Consistency Score - DCS*).  
  * Bằng chứng thực nghiệm cho thấy kết hợp chỉ số bất nhất ESG giúp nâng cao độ chính xác khi dự báo rủi ro doanh nghiệp.

---

### 2. ĐỀ TÀI 2: Energy + Weather Data Warehouse for Adaptive Forecasting
*(Kho dữ liệu Điện năng & Thời tiết phục vụ dự báo phụ tải thích nghi có chọn lọc)*

* **Tên đề tài & Lĩnh vực:**  
  * *Tiếng Việt:* Xây dựng kho dữ liệu điện năng và thời tiết phục vụ dự báo phụ tải thích nghi có chọn lọc trước sự thay đổi phân phối dữ liệu.  
  * *Tiếng Anh:* *A Drift-Attributed Energy–Weather Data Warehouse for Selective Adaptive Electricity Load Forecasting.*  
  * *Lĩnh vực:* Năng lượng thông minh & Khoa học Trái đất / Khí tượng (Smart Grid & Meteorology).
* **Vấn đề / Câu hỏi nghiên cứu (giải thích bình dân):**  
  Lượng điện tiêu thụ luôn thay đổi theo thời tiết (trời nóng thì bật máy lạnh, trời lạnh thì bật máy sưởi) và theo thói quen sinh hoạt. Khi hành vi sử dụng thay đổi đột ngột (trong ngành gọi là hiện tượng trôi dạt dữ liệu - *concept drift*), các thuật toán AI dự báo lượng điện dùng sẽ bị sai lệch.  
  Bình thường, cứ thấy sai số tăng là người ta lại bắt AI học lại từ đầu (retrain). Việc này rất lãng phí tài nguyên máy tính nếu nguyên nhân chỉ là đợt nắng nóng ngắn hạn.  
  👉 **Câu hỏi nghiên cứu:** Làm sao xây kho dữ liệu kết hợp cả điện năng và thời tiết để AI biết được: "Sai lệch này là do thời tiết đổi mùa tự nhiên" hay "do thói quen dùng điện thay đổi thực sự", từ đó chỉ huấn luyện lại mô hình khi thực sự cần thiết?
* **Nguồn dữ liệu & Tính khả thi:**  
  * *Open Power System Data (OPSD):* Dữ liệu phụ tải, giá điện, điện mặt trời, điện gió của các nước châu Âu theo từng giờ, tải file CSV có sẵn.  
  * *OPSD Weather / ERA5:* Dữ liệu khí tượng (nhiệt độ, bức xạ, gió, mưa) theo từng giờ, ghép nối cực kỳ khớp với dữ liệu điện qua mốc thời gian (*timestamp*).  
  * *UCI Electricity:* Dữ liệu 370 hộ tiêu thụ đo mỗi 15 phút (dùng làm dữ liệu thử nghiệm mở rộng).  
  * *Đánh giá dữ liệu:* **Xuất sắc (10/10)**. Dữ liệu công khai, định dạng bảng hoàn toàn sạch sẽ, không cần cào bới web, nhãn thời gian và phụ tải đầy đủ 100%.
* **Khoảng trống nghiên cứu (Research Gap):**  
  * Trước đây: Việc "phát hiện sai lệch rồi tự động retrain mô hình" đã có nhiều người làm (dùng ADWIN, KSWIN...).  
  * **Điểm chưa ai làm tốt:** Chưa ai phân biệt được nguyên nhân gây ra sai lệch (*Drift Attribution*). Việc retrain mù quáng gây tốn tài nguyên tính toán không cần thiết. Chưa có kho dữ liệu nào tích hợp bảng theo dõi sự kiện trôi dạt dữ liệu (`Fact_DriftEvent`) để phục vụ chiến lược tái huấn luyện có chọn lọc (*Selective Retraining*).
* **Phương pháp / Mô hình dự kiến:**  
  * *Kho dữ liệu:* Các bảng sự kiện `Fact_Load`, `Fact_Weather`, `Fact_Price` và đặc biệt là `Fact_DriftEvent` (lưu lại thời điểm, chỉ số drift, nguyên nhân), gắn với `Dim_Time`, `Dim_Region`.  
  * *Kỹ thuật phát hiện drift:* ADWIN, KSWIN kết hợp các độ đo khoảng cách thống kê (Wasserstein distance, PSI).  
  * *Mô hình dự báo:* LightGBM, N-BEATS hoặc PatchTST.  
  * *Chiến lược thích nghi:* Tái huấn luyện có chọn lọc (chỉ retrain khi drift do thay đổi bản chất hành vi).
* **Kết quả kỳ vọng / Đóng góp:**  
  * Kiến trúc kho dữ liệu chuyên dụng tích hợp giám sát chất lượng và phân phối dữ liệu theo thời gian thực.  
  * Mô hình dự báo phụ tải thích nghi thông minh, đạt độ chính xác cao nhưng **giảm đáng kể số lần phải huấn luyện lại**, tối ưu tài nguyên tính toán.

---

### 3. ĐỀ TÀI 3: Corporate Financial Distress Warehouse
*(Kho dữ liệu tài chính doanh nghiệp chuẩn thời điểm dự báo sớm kiệt quệ đa kỳ)*

* **Tên đề tài & Lĩnh vực:**  
  * *Tiếng Việt:* Xây dựng kho dữ liệu tài chính doanh nghiệp theo thời gian phục vụ dự báo sớm kiệt quệ tài chính đa kỳ.  
  * *Tiếng Anh:* *A Point-in-Time Longitudinal Corporate Financial Warehouse for Multi-Horizon Financial Distress Prediction.*  
  * *Lĩnh vực:* Fintech / Phân tích rủi ro tín dụng & Tài chính doanh nghiệp (Credit Risk & Corporate Finance).
* **Vấn đề / Câu hỏi nghiên cứu (giải thích bình dân):**  
  Một công ty không bao giờ phá sản chỉ sau một đêm, mà thường suy yếu dần qua 2–3 năm.  
  Khi làm dự báo, nhiều người mắc lỗi: kỳ kế toán quý kết thúc ngày 31/12, nhưng thực tế đến tận ngày 15/03 năm sau công ty mới nộp báo cáo. Nếu lấy số liệu ngày 31/12 để dự đoán tình hình vào tháng 1 thì chính là "ăn gian / nhìn trộm tương lai" (*lookahead bias*), vì thời điểm tháng 1 ngoài đời chưa ai biết số liệu đó.  
  👉 **Câu hỏi nghiên cứu:** Làm sao xây kho dữ liệu bảo đảm tính chuẩn xác tuyệt đối về mốc thời gian thực nộp báo cáo (*Point-in-Time*), để theo dõi quỹ đạo suy yếu của doanh nghiệp và cảnh báo sớm: "Khả năng công ty này kiệt quệ trong 1 năm, 2 năm, 3 năm tới là bao nhiêu %?" thay vì chỉ đoán có/không khi đã quá muộn?
* **Nguồn dữ liệu & Tính khả thi:**  
  * *SEC EDGAR (Mỹ):* Cung cấp báo cáo 10-K (năm), 10-Q (quý) dạng số liệu chuẩn hóa XBRL và lịch sử ngày nộp thực tế (`filing_date`) qua REST API miễn phí.  
  * *Nhãn kiệt quệ/phá sản:* Lấy trực tiếp từ báo cáo sự kiện bất thường Form 8-K (Item 1.03 - Phá sản hoặc tiếp quản tài sản).  
  * *Dữ liệu thị trường & Vĩ mô:* Yahoo Finance (giá cổ phiếu) và FRED API (lãi suất, lạm phát).  
  * *Đánh giá dữ liệu:* **Rất tốt (8.5/10)**. Nguồn dữ liệu mở, chuẩn mực quốc tế, nhưng cần viết mã ETL cẩn thận để lọc đúng mã doanh nghiệp và khớp ngày công bố thực tế.
* **Khoảng trống nghiên cứu (Research Gap):**  
  * Trước đây: Đa số các đồ án chỉ lấy chỉ số tài chính tĩnh tại một năm ném vào XGBoost để đoán "Phá sản: Có hay Không" (rất cũ, thiếu tính thực tiễn).  
  * **Điểm chưa ai làm tốt:** Rất ít nghiên cứu xử lý triệt để tính đúng đắn thời điểm (*Point-in-Time correctness*) để tránh rò rỉ dữ liệu. Ngoài ra, việc dự báo sớm đa kỳ (1 năm, 2 năm, 3 năm) và theo dõi quỹ đạo biến động liên tục qua nhiều quý (ví dụ: tốc độ tăng nợ trong 4 quý liền) chưa được giải quyết thấu đáo trong kiến trúc kho dữ liệu.
* **Phương pháp / Mô hình dự kiến:**  
  * *Kho dữ liệu:* `Fact_Financial` (quản lý song song `period_end` và `filing_date`), `Fact_Market`, `Fact_Macro`, `Fact_DistressEvent` gắn với `Dim_Company`, `Dim_Time`.  
  * *Kỹ thuật đặc trưng:* Tạo các biến quỹ đạo biến động (*trajectory features*: tốc độ tăng trưởng nợ 4 quý, xu hướng suy giảm dòng tiền).  
  * *Mô hình dự báo:* XGBoost / LightGBM kết hợp phân tích thời gian sống sót (*Survival Analysis*: Random Survival Forest, Cox Proportional Hazard) để dự đoán thời điểm kiệt quệ.
* **Kết quả kỳ vọng / Đóng góp:**  
  * Một kho dữ liệu chuẩn mực triệt tiêu hoàn toàn rủi ro rò rỉ dữ liệu trong phân tích tài chính.  
  * Hệ thống cảnh báo sớm đa kỳ hạn (1 năm, 2 năm, 3 năm) và xác định quỹ đạo suy yếu của doanh nghiệp, giúp nhà đầu tư và ngân hàng có phương án ứng phó sớm.

---

## PHẦN 2: BẢNG SO SÁNH CHÉO 3 ĐỀ TÀI

| Tiêu chí so sánh | Đề tài 1: ESG Intelligence DW | Đề tài 2: Energy + Weather DW | Đề tài 3: Corporate Financial Distress DW |
| :--- | :--- | :--- | :--- |
| **1. Độ khả thi về dữ liệu** | **Trung bình - Khá (7/10)**<br>• Báo cáo tài chính, tin tức dễ lấy.<br>• Báo cáo ESG là file PDF nhiều định dạng, cào và bóc tách rất cực.<br>• Không có nhãn chuẩn mực sẵn có về "greenwashing". | **Hoàn hảo (10/10)**<br>• Dữ liệu OPSD và thời tiết có sẵn file CSV/Parquet sạch sẽ.<br>• Dữ liệu chuẩn theo từng giờ, không bị thiếu sót.<br>• Không cần cào web, nhãn phụ tải điện có sẵn 100%. | **Rất tốt (8.5/10)**<br>• API SEC EDGAR mở, chuẩn hóa định dạng XBRL.<br>• Nhãn phá sản lấy từ Form 8-K rõ ràng.<br>• Cần kỹ thuật xử lý để lọc sạch các báo cáo nộp muộn hoặc nộp lại. |
| **2. Độ rõ ràng của Gap nghiên cứu** | **Khá tốt (8.5/10)**<br>• So sánh "lời công ty nói" với "tin tức bên ngoài".<br>• Tuy nhiên khái niệm "bất nhất" mang tính định tính, khó lượng hóa tuyệt đối. | **Cực kỳ rõ ràng (9.0/10)**<br>• Phân biệt nguyên nhân gây sai lệch dữ liệu (do thời tiết hay do hành vi).<br>• Mục tiêu rất cụ thể: giảm số lần retrain để tiết kiệm tài nguyên tính toán. | **Rất rõ ràng (8.5/10)**<br>• Khắc phục lỗi rò rỉ dữ liệu (*Point-in-Time*).<br>• Chuyển từ bài toán đoán "có/không" sang dự báo đa kỳ hạn (1-2-3 năm). |
| **3. Tính mới (Novelty)** | **Rất cao (9.5/10)**<br>• Kết hợp cả PDF NLP + Đồ thị tri thức + Kho dữ liệu tài chính.<br>• Tiềm năng viết bài báo hội nghị/tạp chí quốc tế rất lớn. | **Khá (8.0/10)**<br>• Dự báo phụ tải điện là đề tài kinh điển.<br>• Tính mới tập trung toàn bộ vào *Drift Attribution* và *Selective Retraining*. | **Khá (8.0/10)**<br>• Dự báo phá sản đã có nhiều người làm.<br>• Điểm mới phụ thuộc vào việc làm chuẩn chỉ *Point-in-Time* và *Survival Analysis*. |
| **4. Độ phức tạp kỹ thuật DW (ETL)** | **Rất phức tạp (9/10)**<br>• ETL hỗn hợp: file văn bản PDF, đồ thị sự kiện GDELT, chuỗi thời gian giá cổ phiếu.<br>• Thách thức lớn ở khâu khớp tên công ty (*entity matching*). | **Chuẩn mực, vừa sức (6.5/10)**<br>• Đúng chuẩn môn Kho dữ liệu: Fact/Dimension theo thời gian và không gian rõ ràng.<br>• Ghép nối dữ liệu tự nhiên qua khóa thời gian (`timestamp`). | **Vừa phải - Khá (7.5/10)**<br>• Phức tạp ở logic thời gian kép: ngày chốt kỳ (`period_end`) vs ngày nộp đơn (`filing_date`).<br>• Cần tính các biến trễ (lag) và xu hướng 4–8 quý. |
| **5. Rủi ro chính khi thực hiện** | ⚠️ **Rủi ro rất cao:**<br>• Sa lầy vào xử lý văn bản (NLP) mà quên mất thiết kế kho dữ liệu.<br>• Lệch pha thời gian giữa tin tức và báo cáo.<br>• Nguy cơ trễ tiến độ rất lớn. | 🟢 **Rủi ro rất thấp:**<br>• Dữ liệu chắc chắn tải về được ngay.<br>• Không sợ tắc nghẽn ở khâu tiền xử lý.<br>• Thuật toán chuỗi thời gian luôn cho kết quả đo lường rõ ràng. | 🟡 **Rủi ro trung bình:**<br>• Tỷ lệ công ty phá sản thấp dẫn đến mất cân bằng dữ liệu nặng.<br>• Cần kiểm soát chặt chẽ việc rò rỉ dữ liệu giữa các quý. |
| **6. Phù hợp thời gian làm đồ án** | ❌ **Rất dễ cháy deadline (6/10)**<br>• Khối lượng công việc quá lớn cho 1 học kỳ đại học.<br>• Quá nhiều công đoạn rời rạc cần tích hợp. | ✅ **Cực kỳ lý tưởng (9.5/10)**<br>• Tiến độ phân bổ rất mượt cho 8–12 tuần.<br>• Dễ dàng phân chia công việc độc lập cho các thành viên trong nhóm. | 🆗 **Khá phù hợp (8/10)**<br>• Khả thi tốt nếu nhóm tập trung vào số liệu tài chính dạng bảng, bỏ qua phân tích chữ trong 10-K. |

---

## PHẦN 3: ĐÁNH GIÁ, CHẤM ĐIỂM VÀ ĐỀ XUẤT HÀNH ĐỘNG

### 3.1. Bảng chấm điểm chi tiết (Thang điểm 1 - 10)

> *Ghi chú: Điểm số đánh giá dựa trên sự cân bằng giữa chất lượng học thuật và tính khả thi trong thời gian làm đồ án môn học.*

| Tiêu chí đánh giá (Trọng số) | Đề tài 1: ESG Intelligence | Đề tài 2: Energy + Weather | Đề tài 3: Financial Distress | Lý do đánh giá |
| :--- | :---: | :---: | :---: | :--- |
| **Khả thi dữ liệu (25%)** | 7.0 | **10.0** | 8.5 | Đề tài 2 dữ liệu hoàn hảo, sạch sẽ. Đề tài 1 mất điểm do khâu cào PDF và thiếu nhãn chuẩn. |
| **Độ rõ của Research Gap (15%)** | 8.5 | **9.0** | 8.5 | Đề tài 2 gap mang tính kỹ thuật rất cụ thể, dễ đo lường bằng con số chi phí điện toán. |
| **Tính mới / Novelty (20%)** | **9.5** | 8.0 | 8.0 | Đề tài 1 ý tưởng độc đáo, thời sự nhất. Hai đề tài còn lại là bài toán quen nhưng giải pháp mới. |
| **Độ phù hợp kỹ thuật DW (15%)** | 6.5 | **9.0** | 8.5 | Đề tài 2 thể hiện hoàn hảo kỹ năng mô hình hóa DW (Fact/Dim/Drift). Đề tài 1 quá lệch sang NLP. |
| **Độ an toàn / Kiểm soát rủi ro (10%)** | 5.5 | **9.5** | 7.5 | Đề tài 2 rủi ro bằng 0 về nguồn dữ liệu. Đề tài 1 dễ bị "vỡ trận" ở khâu tiền xử lý văn bản. |
| **Phù hợp thời gian đồ án (15%)** | 6.0 | **9.5** | 8.0 | Đề tài 2 vừa vặn từng tuần làm đồ án. Đề tài 1 đòi hỏi khối lượng việc vượt quá một đồ án môn học. |
| **ĐIỂM TỔNG HỢP (Có trọng số)** | **7.30 / 10** | **9.25 / 10** | **8.20 / 10** | **Đề tài 2 là lựa chọn vượt trội về tính hiệu quả và khả năng hoàn thành.** |

---

### 3.2. Đề xuất ưu tiên cho nhóm

#### 🥇 LỰA CHỌN ƯU TIÊN SỐ 1 (Khuyên chọn): ĐỀ TÀI 2 - Energy + Weather Data Warehouse
* **Lý do lựa chọn:**
  1. **An toàn tuyệt đối về dữ liệu:** Dữ liệu OPSD và ERA5 đã được cộng đồng quốc tế kiểm chứng, tải về là dùng được ngay, loại bỏ 100% rủi ro tắc nghẽn ở khâu thu thập.
  2. **Đúng bản chất môn Kho dữ liệu:** Thể hiện trọn vẹn các kỹ năng cốt lõi của môn học: thiết kế mô hình đa chiều (Fact Load, Fact Weather, Fact Drift Event kết hợp Dim Time, Dim Region), quy trình ETL chuẩn hóa theo mốc thời gian, xử lý tập dữ liệu lớn hàng trăm ngàn dòng.
  3. **Đóng góp thông minh, thực tế:** Ý tưởng "Drift Attribution" (giúp hệ thống phân biệt sai lệch để chỉ retrain khi cần thiết) giải quyết trực tiếp bài toán tiết kiệm chi phí máy tính (*Green Computing*), rất dễ trình bày và thuyết phục giảng viên.

#### 🥈 LỰA CHỌN THAY THẾ (Nếu nhóm thích Fintech): ĐỀ TÀI 3 - Corporate Financial Distress Warehouse
* **Lý do cân nhắc:** Nếu nhóm có định hướng nghề nghiệp trong ngành Tài chính/Ngân hàng.
* **Lưu ý triển khai:** Chỉ làm phiên bản **dữ liệu dạng bảng** lấy từ SEC EDGAR và chỉ số chứng khoán. Tuyệt đối **không đưa phần phân tích văn bản PDF** vào để tránh biến đồ án thành bài tập NLP. Trọng tâm ghi điểm là giải quyết triệt để bài toán *Point-in-Time* (chống rò rỉ dữ liệu).

#### ⚠️ CẢNH BÁO ĐỐI VỚI ĐỀ TÀI 1 (ESG Intelligence):
* Ý tưởng đề tài rất hay và tiềm năng bài báo khoa học lớn. Tuy nhiên, đối với một **đồ án môn học**, đây là "cái bẫy thời gian". Nhóm sẽ mất tới 70% công sức chỉ để viết code cào PDF, sửa lỗi font chữ, thiết kế prompt cho LLM, nối bảng tin tức... và có thể không kịp tập trung vào kiến trúc Kho dữ liệu — phần chiếm tỷ trọng điểm chính của môn học.

---

### 3.3. Ba câu hỏi cần làm rõ trước khi chốt đề tài

1. **Hỏi Giảng viên về trọng tâm chấm điểm:**
   > *"Thưa Thầy/Cô, đồ án môn mình ưu tiên đánh giá sâu vào phần nào: Kiến trúc kho dữ liệu, thiết kế Fact/Dim, quy trình ETL và chất lượng dữ liệu (Data-centric) hay đánh giá độ phức tạp của các mô hình AI/Machine Learning ở đầu ra (Model-centric)?"*  
   *(Nếu thầy/cô coi trọng kiến trúc kho dữ liệu: Đề tài 2 và 3 là lựa chọn chuẩn xác nhất).*

2. **Hỏi Giảng viên về phạm vi nguồn dữ liệu:**
   > *"Đồ án có bắt buộc phải dùng dữ liệu của Việt Nam không, hay nhóm có thể sử dụng các bộ dữ liệu công khai chuẩn mực quốc tế (như OPSD châu Âu, SEC EDGAR của Mỹ) để bảo đảm tính đầy đủ và có thể tái lập được?"*  
   *(Dữ liệu Việt Nam ở cả 3 mảng này đều thiếu thốn và không có API mở; được dùng dữ liệu quốc tế sẽ giúp nhóm tiết kiệm hàng chục giờ cào dữ liệu).*

3. **Trao đổi nội bộ nhóm về kỹ năng và mục tiêu:**
   * Thế mạnh của các thành viên là gì: Thao tác số liệu bảng, chuỗi thời gian (hợp Đề tài 2); Kiến thức tài chính, doanh nghiệp (hợp Đề tài 3); hay Xử lý ngôn ngữ tự nhiên NLP (hợp Đề tài 1)?
   * Mục tiêu chung của cả nhóm là: **Làm chắc tay, đạt điểm tuyệt đối môn học một cách khoa học** (chọn Đề tài 2) hay **Chấp nhận làm thêm giờ để thử sức với nghiên cứu mới lạ** (chọn Đề tài 1 hoặc 3)?
