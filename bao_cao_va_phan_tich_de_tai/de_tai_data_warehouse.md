# ĐỀ XUẤT ĐỀ TÀI NGHIÊN CỨU

**Tên đề tài:** Đánh giá độ tin cậy của benchmark khôi phục dữ liệu năng lượng dưới các mẫu thiếu dữ liệu bắt nguồn từ lỗi thực của đồng hồ thông minh  
**Tên tiếng Anh:** *Beyond Synthetic Missingness: Evaluating the Reliability of Energy Time-Series Imputation under Empirically Observed Smart-Meter Failure Patterns*

---

## 1. Đặt vấn đề

Dữ liệu từ smart meter thường xuất hiện khoảng thiếu do sự cố cảm biến, gateway, truyền thông, bảo trì hoặc gián đoạn vận hành. Các khoảng thiếu này có thể làm sai lệch phân tích tiêu thụ năng lượng, dự báo phụ tải và các tác vụ tối ưu hóa hệ thống năng lượng.

Nhiều nghiên cứu imputation vẫn đánh giá mô hình bằng các mẫu thiếu dữ liệu nhân tạo như point missing, random missing hoặc block missing. Tuy nhiên, missingness trong hệ thống thực có thể kéo dài, xuất hiện theo cấu trúc phân cấp và làm nhiều meter liên quan mất dữ liệu đồng thời. Bộ dữ liệu Honda cung cấp 6 năm dữ liệu năng lượng, cấu trúc meter phân cấp, issue labels và các sự kiện gateway failure đã được ghi nhận, tạo điều kiện để đánh giá vấn đề này trên dữ liệu vận hành thực [1].

> **Bài toán nghiên cứu:** Các benchmark synthetic missingness có phản ánh đúng độ khó và bảo toàn thứ hạng tương đối của các phương pháp imputation khi chuyển sang failure pattern quan sát từ hệ thống smart meter thực hay không; đồng thời, các đặc trưng quan sát được của missing pattern có thể được sử dụng để lựa chọn chiến lược imputation phù hợp hơn hay không?

---

## 2. Các vấn đề chính

* **Thiếu tính đại diện:** Synthetic missingness chưa phản ánh đầy đủ các gap dài, correlated missingness hoặc mất đồng thời nhiều meter do gateway outage.
* **Vấn đề Ground Truth:** Các outage thực thường không có ground truth tại khoảng bị mất; dùng trực tiếp corrected values làm ground truth có thể làm kết quả phụ thuộc vào chính heuristic correction của bộ dữ liệu.
* **Độ ổn định của mô hình:** Một mô hình tốt trên random hoặc block missing chưa chắc duy trì hiệu năng và thứ hạng khi missing pattern thay đổi theo sự cố vận hành thực.
* **Tiêu chí đánh giá hạn hẹp:** Đánh giá imputation không nên chỉ dựa trên MAE/RMSE mà cần xem xét tính nhất quán năng lượng và ảnh hưởng tới downstream load forecasting.

---

## 3. Khoảng trống nghiên cứu

Các nghiên cứu trước đã cho thấy missing pattern ảnh hưởng đáng kể đến hiệu năng imputation [2]. Gần đây, DIM-SUM cũng khai thác các missing pattern quan sát thực để tạo chiến lược masking thích nghi [3]. Vì vậy, việc lấy missing mask thực rồi replay lên dữ liệu đầy đủ không nên được xem là tính mới chính. 

Khoảng trống cần kiểm chứng là: **Liệu các benchmark synthetic phổ biến có bảo toàn độ khó, thứ hạng tương đối và downstream utility của các mô hình khi chuyển sang các failure pattern được rút ra từ issue logs và cấu trúc vận hành của một hệ thống smart meter công nghiệp, đặc biệt đối với correlated multi-meter outages hay không?**

Đề tài khai thác issue metadata, meter hierarchy và các sự kiện gateway failure đã được ghi nhận trong bộ Honda để xây dựng thư viện *real-failure-derived masks*. Các mask này được replay lên các đoạn dữ liệu sạch nhằm giữ cấu trúc missingness quan sát ngoài thực tế nhưng vẫn có ground truth. Trên cơ sở đó, nghiên cứu đánh giá mức thay đổi thứ hạng mô hình và xây dựng *failure-pattern-aware selector/ensemble* chỉ dựa trên các đặc trưng có thể quan sát tại thời điểm thiếu dữ liệu, như:
* Chiều dài khoảng thiếu (gap length)
* Số lượng meter bị mất đồng thời
* Vị trí trong cấu trúc phân cấp (meter hierarchy)
* Đặc trưng tải lân cận (context features)

---

## 4. Giải pháp đề xuất

### Quy trình nghiên cứu
$$\text{Issue logs} + \text{meter hierarchy} \longrightarrow \text{Trích xuất failure pattern} \longrightarrow \text{Tạo mask library} \longrightarrow \text{Replay trên dữ liệu sạch} \longrightarrow \text{Imputation} \longrightarrow \text{So sánh ranking} \longrightarrow \text{Failure-pattern-aware strategy} \longrightarrow \text{Forecasting}$$

* **Xây dựng benchmark song song:** Thiết lập hai nhóm benchmark: *synthetic missingness* và *real-failure-derived missingness* với cùng nguyên tắc đánh giá.
* **So sánh diện rộng:** So sánh các phương pháp imputation từ baseline đơn giản, machine learning đến deep learning trên nhiều meter và nhiều mức độ missingness.
* **Định lượng độ dịch chuyển:** Định lượng mức thay đổi hiệu năng và thứ hạng mô hình giữa hai nhóm benchmark theo gap length, missing rate và mức độ correlated missingness.
* **Chiến lược thích nghi:** Xây dựng *failure-pattern-aware selector/ensemble* dựa trên các đặc trưng missingness quan sát được, không giả định biết trước nguyên nhân lỗi.
* **Đánh giá downstream task:** Kiểm tra dữ liệu sau imputation bằng bài toán load forecasting để xác định giá trị ứng dụng thực tế.

---

## 5. Mục tiêu nghiên cứu

| Mục tiêu | Nội dung chi tiết |
| :--- | :--- |
| **M1** | Phân tích và mô tả các failure pattern từ issue logs, meter hierarchy và các sự kiện outage được ghi nhận trong bộ dữ liệu Honda. |
| **M2** | Xây dựng benchmark synthetic và real-failure-derived có ground truth bằng cách replay failure masks lên các đoạn dữ liệu sạch. |
| **M3** | Đánh giá độ nhạy của hiệu năng và độ ổn định thứ hạng của các phương pháp imputation giữa các missingness regime. |
| **M4** | Đề xuất failure-pattern-aware imputation strategy và đánh giá giá trị của chiến lược này trên downstream load forecasting. |

---

## 6. Phương pháp thực nghiệm

* **Dữ liệu:** Bộ *"A Real-World Energy Management Dataset from a Smart Company Building for Optimization and Machine Learning"* của Honda Research Institute Europe [1]. Ưu tiên dữ liệu điện ở độ phân giải 15 phút, các meter có lịch sử dữ liệu đủ dài và issue metadata rõ ràng.
* **Synthetic scenarios:** Point missing, random block và block missing với nhiều độ dài gap/missing rate được kiểm soát.
* **Failure-derived scenarios:** Trích pattern từ issue logs và các outage đã được ghi nhận, bao gồm single-meter gaps và correlated multi-meter/gateway outages; sau đó replay lên các khoảng dữ liệu sạch tương thích.
* **Nguyên tắc Ground Truth:** Chỉ sử dụng giá trị gốc ở các đoạn dữ liệu sạch trước khi masking; không xem corrected/fill values trong khoảng lỗi thực là ground truth tuyệt đối.
* **Chia tập và kiểm chứng:** Chia dữ liệu theo thời gian và theo failure episode khi phù hợp để tránh temporal leakage; lặp thí nghiệm trên nhiều meter, nhiều đoạn dữ liệu và nhiều lần replay để đánh giá độ ổn định.

---

## 7. Phương pháp so sánh

| Nhóm phương pháp | Phương pháp cụ thể |
| :--- | :--- |
| **Baseline đơn giản** | Linear interpolation, Seasonal Naive |
| **Machine Learning** | KNN, Random Forest / XGBoost |
| **Deep Learning** | BRITS, SAITS, TimesNet |
| **Đề xuất** | Failure-pattern-aware selector/ensemble dựa trên gap, meter và context features |

---

## 8. Chỉ số đánh giá

* **MAE, RMSE:** Đo sai số khôi phục dữ liệu; báo cáo theo từng missingness regime và kèm độ bất định qua nhiều lần replay khi phù hợp.
* **Spearman $\rho$ hoặc Kendall $\tau$:** Đo độ ổn định thứ hạng của các mô hình giữa synthetic và failure-derived benchmark.
* **Energy consistency error:** Đo sai lệch tổng năng lượng hoặc mức tiêu thụ tích lũy trong khoảng gap.
* **Forecast MAE/RMSE:** Đo mức độ ảnh hưởng của dữ liệu sau imputation tới độ chính xác của bài toán downstream load forecasting.

---

## 9. Kết quả dự kiến

1. Xây dựng được bộ failure patterns và benchmark real-failure-derived có ground truth dựa trên issue logs và cấu trúc vận hành của hệ thống smart meter.
2. Xác định rõ mức độ mà synthetic benchmark bảo toàn hoặc làm sai lệch độ khó, hiệu năng và thứ hạng tương đối của các phương pháp imputation trong các kịch bản lỗi thực tế.
3. Đánh giá được tính hiệu quả của *failure-pattern-aware selector/ensemble* trong việc duy trì hiệu năng ổn định so với việc áp dụng một mô hình cố định, đồng thời định lượng tác động của từng chiến lược tới bài toán load forecasting.

---

## Tài liệu tham khảo chính

* **[1]** Engel, J., Castellani, A., Wollstadt, P., et al. (2025). *A Real-World Energy Management Dataset from a Smart Company Building for Optimization and Machine Learning*. Scientific Data, 12, 864. [https://doi.org/10.1038/s41597-025-05186-3](https://doi.org/10.1038/s41597-025-05186-3)
* **[2]** Du, W., Wang, J., Qian, L., et al. (2024). *TSI-Bench: Benchmarking Time Series Imputation*. arXiv:2406.12747.
* **[3]** Hildebrant, R., Bhope, R. A., Mehrotra, S., Tull, C. R., & Venkatasubramanian, N. (2025). *DIM-SUM: Dynamic IMputation for Smart Utility Management*. Proceedings of the VLDB Endowment, 18(11), 4451-4464. [https://doi.org/10.14778/3749646.3749705](https://doi.org/10.14778/3749646.3749705)