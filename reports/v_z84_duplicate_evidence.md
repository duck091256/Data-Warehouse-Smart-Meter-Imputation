# Báo Cáo Bằng Chứng Về Duplicate Timestamps Tại Meter V.Z84 (Reconciled & Repaired)

> **Dự án**: Beyond Synthetic Missingness — Smart-Meter Imputation  
> **Mã Task**: `P1-T2` — Chuẩn hóa múi giờ và DST: quy về UTC, lưu cả local time  
> **Mục tiêu**: Điều tra thực nghiệm trực tiếp file `V.Z84.W_raw.csv.gz`, xác minh ngữ nghĩa đo lường, làm rõ hiện tượng mismatch và biện minh quy tắc khử trùng lặp (`keep_last`) theo Protocol P1-T2.  
> **Thời điểm cập nhật**: 2026-10-06 (Evidence Repair & Reconciliation)  

---

## 1. Xác Minh Ngữ Nghĩa Đo Lường (Semantics of W, W_in, W_out)

Meter `V.Z84` là đồng hồ đo tổng tại trạm cung cấp trung tâm (Versorgungszentrale - cấp 1 trong cấu trúc phân cấp toàn cơ sở nghiên cứu).

Theo tiêu chuẩn kỹ thuật đo đếm điện năng quốc tế (IEC 62053 / DIN EN 13757) và hệ thống ghi log của Honda Research Institute Europe:
- **`W_in` (Active Energy Import / Wirkarbeit Bezug)**: Điện năng tác dụng tiêu thụ nhận từ lưới ngoài vào cơ sở (kWh).
- **`W_out` (Active Energy Export / Wirkarbeit Lieferung)**: Điện năng tác dụng phát/cung cấp từ tổ máy phát/quang điện ra mạng lưới tòa nhà (kWh).
- **`W` (Net Active Energy / Wirkarbeit Saldo)**: Điện năng thuần tích lũy của đồng hồ hai chiều:
  $$\Delta W = W_{\text{out}} - W_{\text{in}}$$

### Đối chứng số liệu thực tế trước khi xuất hiện duplicate (trước tháng 05/2023):
Tại mốc thời gian `2019-06-28T22:00:39.000000+00:00`:
- $W_{\text{out}} = 850,775.3 \text{ kWh}$
- $W_{\text{in}} = 9.5 \text{ kWh}$
- $W = 850,765.8 \text{ kWh}$
- Kiểm tra số học:
  $$850,775.3 - 9.5 = 850,765.8 \text{ kWh} \quad (\text{Khớp chính xác } 100\%)$$

### [CORRECTION CRITICAL] Đặc tính biến thiên của W: Không giả định đơn điệu (Non-Monotonicity):
- **Báo cáo cũ tuyên bố**: *"Tất cả 3 đại lượng này đều là thanh ghi tích lũy đơn điệu không giảm (Monotonic Non-Decreasing Registers)"*.
- **Xác minh thực tế trên dữ liệu thô**: Tuyên bố trên là **SAI THỰC TẾ**. 
  - Trong `V.Z84.W_raw.csv.gz`, có tới **169,365 bước giảm (negative steps / decreases)** trong tổng số 4,210,903 khoảng đo.
  - **Bản chất vật lý**: Vì $W$ là Net Energy Saldo ($W_{\text{out}} - W_{\text{in}}$), vào các thời điểm cơ sở nhận điện năng từ lưới ngoài ($W_{\text{in}}$ tăng lên) trong khi máy phát nội bộ không phát ($W_{\text{out}}$ đứng yên), giá trị $W$ tự nhiên giảm xuống.
  - **Quy tắc Protocol**: Các bước giảm này là quan sát vật lý chân thực của đồng hồ hai chiều, **tuyệt đối không bị xóa, không bị lọc debounce hay làm phẳng nhân tạo** trong pipeline P1-T2.

---

## 2. Xác Minh Độ Phân Giải Thời Gian và Trình Tự Ghi Log (Chronology)

### 2.1. Phân kỳ định dạng thời gian (Resolution Switch)
- **Giai đoạn 1 (Từ 2019-06-28 đến 2023-05-15 11:45:31 UTC)**:
  - Định dạng timestamp: `YYYY-MM-DDTHH:MM:SS.000000+00:00` (độ phân giải tròn giây).
  - Tần suất: phát xung khi có biến động phụ tải (khoảng 13s–18s/bản ghi).
  - Số bản ghi trùng lặp: **0 bản ghi**.
- **Sự kiện gián đoạn (Outage Event)**:
  - Căn cứ theo `issues/automatic_issues/V.Z84_issues_automatic.yaml`:
    ```yaml
    V.Z84@gap@1684151131:
      comment: gap, 1.311h from 2023-05-15T11:45:31Z to 2023-05-15T13:04:09Z
      time_end: 1684155849
      time_start: 1684151131
    ```
    Hệ thống ghi nhận sự cố mất kết nối kéo dài 1.311 giờ (từ 11:45:31 UTC đến 13:04:09 UTC ngày 2023-05-15).
- **Giai đoạn 2 (Sau kết nối lại lúc 13:04:09.963399 UTC ngày 2023-05-15)**:
  - Thiết bị ghi nhận chuyển sang độ phân giải microsecond: `.963399+00:00`.
  - Bắt đầu xuất hiện các dòng có cùng timestamp microsecond liên tiếp nhau.

### 2.2. Kiểm tra tính thứ tự (Chronology Check)
- 100% bản ghi trong toàn bộ các file của `V.Z84` đều tăng dần đơn điệu về trục thời gian (`out_of_order = 0`).
- 100% duplicate timestamps đều là **within-file duplicate liên tiếp nhau** (consecutive rows). Hoàn toàn không có hiện tượng lùi thời gian hay xáo trộn dòng.

---

## 3. Kiểm Tra Trực Tiếp Dữ Liệu Duplicate Trên File Mục Tiêu `V.Z84.W_raw.csv.gz`

Không suy luận gián tiếp từ `W_in` hay `W_out`, kiểm tra thực nghiệm độc lập trực tiếp trên `data/V.Z84/V.Z84.W_raw.csv.gz` (4,272,693 dòng thô) ghi nhận:

### 3.1. Phân loại cấu trúc cụm trùng lặp (Cluster Size Distribution)
Tổng số mốc thời gian có trùng lặp trong file $W$ là **55,109 mốc thời gian duy nhất**:
- **Cụm 2 dòng (Pairs)**: **48,428 mốc** ($48,428 \times 2 = 96,856$ dòng thô).
- **Cụm 3 dòng (Triplets)**: **6,681 mốc** ($6,681 \times 3 = 20,043$ dòng thô).
- **Tổng số dòng thừa bị loại bỏ khi áp dụng `keep_last`**:
  $$\text{Duplicates Removed} = (48,428 \times 1) + (6,681 \times 2) = 48,428 + 13,362 = \mathbf{61,790} \text{ dòng}$$
  Khớp chính xác tuyệt đối với con số 61,790 dòng loại bỏ trong `readings_utc_metadata.json` và kiểm kê P1-T1.

### 3.2. Chi tiết biến thiên giá trị trong từng cụm trùng lặp
Đối với 55,109 mốc thời gian lặp:

| Cấu trúc cụm | Dạng chuỗi giá trị | Số lượng mốc | Tỷ lệ (%) | Ý nghĩa kỹ thuật |
|---|---|---|---|---|
| **Cặp (Pair)** | $v_2 > v_1$ (bước tăng nhẹ 0.3–0.5 kWh) | 41,199 | 74.76% | Bản ghi sau cập nhật trạng thái tích lũy mới hơn ở cuối chu kỳ đọc |
| **Cặp (Pair)** | $v_2 < v_1$ (bước giảm nhẹ) | 6,919 | 12.56% | Cập nhật thanh ghi saldo khi phụ tải nhận điện từ lưới |
| **Cặp (Pair)** | $v_1 = v_2$ (giá trị giống hệt bit-for-bit) | 310 | 0.56% | Packet truyền thông gửi lặp (retransmission / duplicate ACK) |
| **Bộ ba (Triplet)** | $v_1 = v_2, v_3 > v_1$ | 4,136 | 7.51% | Hai packet đầu trùng lặp, packet thứ 3 cập nhật xung điện mới |
| **Bộ ba (Triplet)** | $v_1, v_2, v_3$ có 3 giá trị khác nhau | 2,291 | 4.16% | Cập nhật đa xung liên tiếp trong cùng nhãn microsecond |
| **Bộ ba (Triplet)** | $v_1 = v_2, v_3 < v_1$ | 205 | 0.37% | Hai packet đầu trùng lặp, packet thứ 3 cập nhật saldo giảm |
| **Bộ ba (Triplet)** | Khác (2 giá trị độc nhất) | 39 | 0.07% | Dạng biến thể packet |
| **Bộ ba (Triplet)** | $v_1 = v_2 = v_3$ (giống hệt nhau cả 3 dòng) | 10 | 0.02% | Retransmission lặp 3 lần |
| **Tổng cộng** | — | **55,109** | **100.00%** | Loại bỏ 61,790 dòng thừa, giữ lại đúng 55,109 bản ghi |

*Ghi chú số liệu*: Số lượng 4,710 dòng trùng `(timestamp, value)` xuất hiện trước đây trong một số báo cáo thực chất là số dòng thỏa mãn `df.duplicated(subset=['datetime_utc', 'val'])`:
$$4,136 + 205 + 39 + (2 \times 10) + 310 = 4,710 \text{ dòng}$$
Không phải là số cặp trùng giá trị như diễn giải cũ.

---

## 4. Phân Tích Hiện Tượng 4.94% Mismatch ($W_{\text{out}} - W_{\text{in}} - W \ne 0$)

Kiểm tra đối chiếu 3 file $W, W_{\text{in}}, W_{\text{out}}$ tại 37,322 mốc thời gian xuất hiện đồng thời cả 3 đại lượng sau khi áp dụng chính sách `keep_last`:
- **Khớp hoàn hảo ($|W_{\text{out}} - W_{\text{in}} - W| < 10^{-4}$)**: **35,478 mốc** (95.06%).
- **Lệch ($|W_{\text{out}} - W_{\text{in}} - W| \ge 10^{-4}$)**: **1,844 mốc** (4.94%).

### Chi tiết 1,844 mốc lệch:
1. **Phân loại duplicate vs singleton**:
   - **1,646 mốc (89.26%)** là các mốc thời gian có xuất hiện duplicate ở ít nhất 1 trong 3 file nguồn (310 mốc tại $W$, 1,276 mốc tại $W_{\text{in}}$, 1,621 mốc tại $W_{\text{out}}$).
   - **198 mốc (10.74%)** là các mốc singleton ở cả 3 file (không có duplicate ở bất kỳ file nào).
2. **Khung thời gian xuất hiện**:
   - 100% số mốc lệch đều xảy ra **sau ngày 2023-05-15 19:22:25 UTC** (giai đoạn sau sự cố mất kết nối và chuyển đổi định dạng microsecond).
3. **Mối liên hệ với Issue Episodes**:
   - 108 mốc lệch nằm trực tiếp bên trong cửa sổ sự cố (gap/outage) được ghi nhận trong `issues/automatic_issues/V.Z84_issues_automatic.yaml`.
   - 1,294 mốc lệch (70.17%) nằm trong phạm vi 24 giờ kể từ một sự cố ghi log.
4. **Ảnh hưởng của chiến lược deduplication**:
   - Với `keep_last`: 35,478 mốc khớp (95.06%), 1,844 mốc lệch.
   - Nếu dùng `keep_first`: chỉ có 29,369 mốc khớp (78.69%), số mốc lệch vọt lên tới 7,953 mốc (21.31%). Điều này chứng minh `keep_last` giảm thiểu sai lệch hơn 4 lần so với `keep_first`.

### [CRITICAL] Trạng thái nguyên nhân: UNRESOLVED (Chưa chứng minh triệt để)
- Hiện tượng lệch 4.94% sau ngày 15/05/2023 tương quan chặt chẽ với:
  - Sự trôi dạt offset phần cứng chưa hiệu chuẩn (ví dụ offset cố định ~462.87 kWh tại $W_{\text{out}}$ hoặc ~287.64 kWh tại $W_{\text{in}}$).
  - Độ trễ truyền thông bất đồng bộ giữa các thanh ghi Modbus sau khi thiết bị khởi động lại.
- **Kết luận khoa học**: Vì không có dữ liệu chẩn đoán nội bộ firmware của thiết bị đo từ nhà sản xuất, nguyên nhân gốc rễ cụ thể của 1,844 mốc này được phân loại chính thức là **UNRESOLVED (Chưa giải quyết triệt để)**.
- **Nguyên tắc bảo vệ dữ liệu**: Tuyệt đối **không được tự động nội suy, sửa đổi hay ép buộc số liệu** của $W$ dựa trên công thức $W_{\text{out}} - W_{\text{in}}$. Pipeline P1-T2 đọc trung thực 100% giá trị $W$ từ file nguồn `V.Z84.W_raw.csv.gz`.

---

## 5. Phân Định Rạch Ròi: Fact, Inference, và Protocol Decision

Để đảm bảo tính trung thực và chuẩn mực khoa học (Research Integrity), báo cáo phân định rõ 3 cấp độ:

| Cấp độ | Nội dung xác nhận |
|---|---|
| **1. Observed Fact<br>(Thực tế quan sát)** | - `V.Z84.W_raw.csv.gz` có đúng 4,272,693 dòng, 55,109 mốc timestamp lặp (48,428 cặp, 6,681 bộ ba), loại bỏ đúng 61,790 dòng.<br>- Toàn bộ duplicate xuất hiện sau sự cố mất kết nối ngày 15/05/2023.<br>- $W$ có 169,365 bước giảm tự nhiên do nhận điện từ lưới.<br>- 95.06% mốc thời gian thỏa mãn $W_{\text{out}} - W_{\text{in}} - W = 0$; 4.94% (1,844 mốc) có chênh lệch.<br>- Trục thời gian thô tăng dần đơn điệu (`out_of_order = 0`). |
| **2. Inference<br>(Suy luận kỹ thuật)** | - Hiện tượng duplicate cùng giá trị sinh ra do cơ chế gửi lại packet (retransmission/duplicate ACK).<br>- Hiện tượng cặp dòng khác giá trị phản ánh việc cập nhật thanh ghi ở cuối chu kỳ đọc và việc bù trừ offset chưa hiệu chuẩn của cảm biến.<br>- Nguyên nhân cụ thể của 4.94% mismatch là chưa thể chứng minh triệt để (UNRESOLVED) nếu thiếu log firmware thiết bị. |
| **3. Protocol Decision<br>(Quyết định chuẩn hóa)** | - Áp dụng chính sách `keep_last` cho việc khử trùng lặp theo cấu hình tường minh `etl.deduplication.strategy: "keep_last"`.<br>- Không debounce hay ép buộc tính đơn điệu cho biến $W$.<br>- Giữ nguyên vẹn 100% giá trị thô của $W$ từ file nguồn, không tính toán can thiệp hay sửa đổi từ $W_{\text{in}}, W_{\text{out}}$. |

---

## 6. Kết Luận

- Hiện tượng duplicate tại `V.Z84` đã được kiểm tra trực tiếp trên file mục tiêu $W$, phân loại đầy đủ cấu trúc cụm (cặp và bộ ba) và phân tích định lượng chính xác 100%.
- Sai lệch về tính "đơn điệu" trước đây đã được đính chính hoàn toàn.
- Hiện tượng mismatch 4.94% được phân tích định lượng rõ ràng và ghi nhận đúng bản chất UNRESOLVED, bảo toàn sự tôn trọng tuyệt đối đối với dữ liệu thô.

