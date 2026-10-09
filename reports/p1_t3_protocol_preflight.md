# Báo Cáo Kiểm Tra Tính Nhất Quán Protocol P1-T3 (P1-T3 Protocol Consistency & Pre-Flight Check)

> **Dự án**: Beyond Synthetic Missingness — Smart-Meter Imputation  
> **Mã Nhiệm Vụ**: `P1-T3 PRE-FLIGHT / PROTOCOL CONSISTENCY CHECK`  
> **Thời điểm thực hiện**: 2026-10-06T06:45:00+07:00 (UTC 2026-10-05 23:45:00Z)  
> **Trạng thái Task hiện tại trong governance**: `P1-T3: READY`  
> **Tài liệu Protocol thẩm quyền xem xét**: `TASK_PLAN.md`, `AGENTS.md`, `EXECUTOR.md`, `AUDITOR.md`, `configs/default.yaml`, `configs/local.yaml`, `reports/p1_inventory.md`, `audits/AUDIT_P1_T2_REAUDIT.md`  
> **Tập dữ liệu đầu vào đã kiểm chứng**: `data/interim/readings_utc.parquet` (208,224,479 dòng, 79 meters có dữ liệu, SHA-256: `5983397375...`)  

---

## Tóm Tắt Điều Hành (Executive Summary)

Báo cáo này thực hiện bước kiểm tra tiền trạm độc lập (**Pre-flight / Protocol Consistency Check**) cho nhiệm vụ **P1-T3** (*Chuẩn hóa lưới 15 phút: reindex đầy đủ, không nội suy, giữ NaN gốc*).

Mục tiêu duy nhất của bước kiểm tra này là:
1. Đối soát toàn diện các quy tắc hiện có trong protocol liên quan đến độ phân giải 15 phút, phép resampling/downsampling, trục thời gian, và ngữ nghĩa đo lường của biến mục tiêu $W$;
2. Kiểm tra tính khả thi và mâu thuẫn kỹ thuật của tiêu chí nghiệm thu trong `TASK_PLAN.md` đối với dữ liệu thực tế 208.22 triệu dòng đa tần suất (15s, 30s, 1m, 2m, pulse);
3. Đề xuất quy ước biên, toán tử chọn mẫu, và phương pháp luận rõ ràng nhằm ngăn chặn triệt để việc resampling vô tình biến thành imputation;
4. Đưa ra khuyến nghị chính thức về mặt quản trị nghiên cứu theo Hiến chương `AGENTS.md`.

**Kết luận sơ bộ cốt lõi**:
- Phát hiện **MÂU THUẪN TOÁN HỌC KHÔNG THỂ KHẢ THI (MATHEMATICAL IMPOSSIBILITY)** trong tiêu chí nghiệm thu P1-T3 hiện tại của `TASK_PLAN.md`: Yêu cầu *"số giá trị non-NaN không đổi so với trước reindex"* là bất khả thi khi chuyển đổi 208,224,479 quan sát thô tần suất cao (sub-minute) thành một lưới 15 phút chỉ có tối đa 13.98–16.62 triệu ô thời gian.
- Khuyến nghị quản trị chính thức: **`BLOCKED — PROTOCOL CLARIFICATION REQUIRED`**.
- Trình bày toàn bộ **Quy tắc chính xác đề xuất (Proposed Exact Rule)** sẵn sàng chuyển hóa thành Unit Test Suite ngay khi Protocol Owner phê duyệt.

---

## A. Current Protocol (Các Quy Tắc Đã Được Xác Định)

Qua việc rà soát toàn bộ các tài liệu nền tảng (`TASK_PLAN.md`, `AGENTS.md`, `AUDITOR.md`, `configs/default.yaml`, `configs/local.yaml`, `reports/p1_inventory.md`, `audits/AUDIT_P1_T2_REAUDIT.md`), các quy tắc hiện hữu được trích xuất như sau:

### 1. Độ phân giải nghiên cứu chuẩn (Research Resolution = 15 phút)
- **`TASK_PLAN.md` (Mục P1-T3)**: Mục tiêu là tạo ra `data/interim/readings_15min.parquet` từ `readings_utc.parquet`.
- **`configs/default.yaml` & `local.yaml`**: Khai báo tham số cấu hình hệ thống:
  ```yaml
  experiment:
    target_resolution: "15min"
    timezone: "UTC"
  ```
- **Toàn bộ các pha downstream (P2–P7)**: Toàn bộ engine sinh mask (S-point, S-block, S-matched, R-derived), các baseline (Linear, Seasonal Naive, KNN, XGBoost), mô hình Deep Learning (SAITS, BRITS, TimesNet), phân tích ranking Kendall $\tau$, và downstream forecasting đều được thiết kế hoạt động trên bước lưới 15 phút.

### 2. Tiêu chuẩn trục thời gian và Múi giờ
- **Chuẩn hóa UTC**: Mọi timestamp trong pipeline được định vị duy nhất theo chuẩn UTC (`timestamp[us, tz=UTC]`), tăng dần đơn điệu, không lỗ hổng giả và không trùng lặp do chuyển đổi giờ mùa hè (DST transitions).
- **Wall-clock Local Time**: Lưu trữ kèm theo múi giờ địa phương Đức `Europe/Berlin` để phục vụ phân tích nhịp sinh hoạt phụ tải (Circadian Rhythm) mà không làm méo mó trục vật lý UTC.

### 3. Ngữ nghĩa đo lường của biến mục tiêu $W$ (Measurement Semantics)
- **$W$ là Net Active Energy Saldo**:
  - Biến $W$ (đo bằng kWh) là **thanh ghi năng lượng tích lũy thực tế (Cumulative Saldo Register)** tại thời điểm $t$, phản ánh hiệu năng lượng vào/ra tổng hợp của trạm đo ($W = W_{\text{out}} - W_{\text{in}}$).
  - Biến $W$ **không được giả định là đơn điệu tăng**. Khi trạm điện phát ngược vào lưới hoặc có dòng hoàn trả, thanh ghi $W$ tự nhiên giảm (ghi nhận thực tế 169,365 bước giảm tự nhiên tại `V.Z84.W`).
  - Pipeline P1-T2 và P1-T3 đọc trực tiếp biến $W$ thô từ cảm biến; **tuyệt đối không tự ý thay thế $W$ bằng phép trừ $W_{\text{out}} - W_{\text{in}}$** (vì phát hiện 4.94% mốc lệch do offset trôi dạt tại nguồn).
- **Phân biệt rạch ròi với Công suất $P$**:
  - $P$ (Watts/kW) là đại lượng công suất tức thời (instantaneous active power).
  - $W$ (kWh) là số đọc thanh ghi tích lũy (energy counter register).
  - Phép lấy trung bình cộng (`mean`) chỉ có ý nghĩa vật lý với công suất tức thời $P$, **không có ý nghĩa vật lý với thanh ghi tích lũy $W$**.

### 4. Tính toàn vẹn của Ground Truth (Ground Truth Invariants)
- **`AGENTS.md` (Quy tắc 5)**:
  - Tuyệt đối không dùng giá trị `_corrected_raw` (dữ liệu đảo pha CT tại nguồn) làm ground truth.
  - Ground truth chỉ được trích xuất từ các **clean segment hợp lệ** (liên tục, không thiếu, không có issue log, không bị corrected).
  - Không rò rỉ dữ liệu (No Leakage): Scaler chỉ fit trên train, giá trị dưới mask không xuất hiện trong feature.
- **Checklist Audit P1 (`TASK_PLAN.md` mục P1 Checklist)**:
  - *"Đối chiếu ngẫu nhiên 30 meter × 5 khoảng thời gian: giá trị warehouse = giá trị raw."*
  - *"Không có reindex/nội suy làm 'mọc' giá trị mới."*
  - *"Tỷ lệ nội suy / dữ liệu giả mạo: Đúng 0.0000%."*

---

## B. Contradictions & Ambiguities (Mâu Thuẫn & Điểm Chưa Rõ)

### 1. Mâu thuẫn toán học cốt lõi (Core Mathematical Contradiction)

Trong `TASK_PLAN.md` (Mục 93, dòng 101), chỉ tiêu kiểm thử cho Task P1-T3 được quy định nguyên văn:

> **"Mỗi meter có đủ số điểm kỳ vọng trên lưới; số giá trị non-NaN không đổi so với trước reindex"**

#### Bằng chứng thực nghiệm đối soát với dữ liệu thực tế:
1. **Dữ liệu đầu vào trước reindex (`readings_utc.parquet`)**:
   - Tổng số dòng dữ liệu: **208,224,479 dòng**.
   - Cột `value` chứa **208,224,479 giá trị non-NaN** (100% hợp lệ, tỷ lệ NaN = 0.000000%).
   - Tần suất phát tín hiệu gốc của 79 meters chứa dữ liệu:
     - **15 giây**: 1 meter (`V.Z84`), gồm **4,210,903** dòng.
     - **30 giây**: 17 meters (ví dụ `H1.Z310`, `H2.Z351`, `H2.ZE64`...), gồm **29,840,633** dòng.
     - **1 phút**: 51 meters (ví dụ `H1.Z10`, `H2.Z61`, `H3.Z40`...), gồm **169,728,785** dòng.
     - **2 phút**: 1 meter (`H1.W12`), gồm **858,642** dòng.
     - **Tần suất thấp / Xung sự kiện (Pulse)**: 9 meters (từ 810s đến 4.5h), gồm **3,585,516** dòng.
2. **Kích thước lý thuyết tối đa của lưới 15 phút**:
   - Khoảng thời gian toàn bộ dataset: `2017-12-31 23:00:03 UTC` đến `2024-01-01 00:00:00 UTC` (~6 năm).
   - Tổng số bước 15 phút lý thuyết trong 6 năm cho 1 meter:
     $$N_{\text{steps}} = \frac{6 \times 365.25 \times 24 \times 60}{15} \approx 210,437 \text{ slots/meter}$$
   - Nếu áp dụng lưới thời gian toàn cục cho toàn bộ **79 meters**:
     $$\text{Tổng số ô lưới tối đa} = 79 \times 210,437 = \mathbf{16,624,523} \text{ slots}$$
   - Nếu áp dụng lưới riêng biệt theo khoảng thời gian sống của từng meter (`[meter_min_ts, meter_max_ts]`):
     $$\text{Tổng số ô lưới thực tế} = \mathbf{13,981,638} \text{ slots}$$

#### Phân tích mâu thuẫn:
$$\mathbf{208,224,479} \text{ (non-NaN trước reindex)} \quad \gg \quad \mathbf{16,624,523} \text{ (tổng số ô trên lưới 15 phút)}$$
Tỷ lệ chênh lệch:
$$\frac{208,224,479}{16,624,523} \approx 12.525 \text{ lần}$$

Một lưới chuỗi thời gian đều đặn 15 phút có cấu trúc $1 \text{ dòng} / 1 \text{ meter} / 1 \text{ mốc thời gian}$. Do đó, một meter không thể chứa nhiều hơn 210,437 điểm trên lưới. 
- Nếu giữ nguyên toàn bộ 208,224,479 giá trị non-NaN, thì mỗi mốc 15 phút của meter `V.Z84` sẽ chứa ~60 dòng dữ liệu, phá vỡ hoàn toàn định nghĩa "lưới đều đặn 15 phút" và vi phạm tiêu chí *"mỗi meter có đủ số điểm kỳ vọng trên lưới"*.
- Nếu chuẩn hóa thành lưới đều đặn 15 phút (mỗi bước 15 phút đại diện bởi 1 giá trị), thì **bắt buộc phải nén / loại bỏ ~191.6 triệu quan sát thô cấp giây/phút**. Khi đó, số giá trị non-NaN sau khi chuyển đổi sẽ giảm từ 208.2M xuống mức $\le 16.6\text{M}$ (giảm hơn 92%).

👉 **Kết luận**: Yêu cầu *"số giá trị non-NaN không đổi so với trước reindex"* là **mâu thuẫn tuyệt đối về mặt toán học** với phép downsampling từ tần suất sub-minute sang lưới 15 phút.

### 2. Nguồn gốc của sự nhầm lẫn (Root Cause Analysis)

Mâu thuẫn này phát sinh từ **mô hình tư duy (mental model) của hàm `pd.Series.reindex()` trong thư viện Pandas**:
- Trong giáo trình hoặc tài liệu Pandas chuẩn: Một chuỗi thời gian *vốn đã được đo ở tần suất 15 phút* nhưng bị khuyết một số mốc (ví dụ có 00:00, 00:30 nhưng thiếu 00:15). Khi gọi `series.reindex(complete_15min_range)`, hàm sẽ chèn các giá trị `NaN` vào các mốc khuyết mà không làm mất đi các giá trị ban đầu. Khi đó:
  $$\text{count}(\text{non-NaN sau reindex}) \equiv \text{count}(\text{non-NaN trước reindex})$$
- Tuy nhiên, trong bài toán thực tế của trạm Honda Smart-Meter: Dữ liệu nguồn **chưa hề nằm trên lưới 15 phút**, mà đang phát ở tần suất 15 giây, 30 giây, 1 phút, 2 phút. Quá trình biến đổi từ sub-minute sang 15 phút là một phép **Downsampling / Temporal Aggregation**, không phải là một phép `reindex` 1:1 đơn thuần.

### 3. Thảm họa nếu áp dụng "Exact Timestamp Matching" (Reindex Khớp Tuyệt Đối Giây)

Nếu một kỹ sư thực hiện máy móc yêu cầu "reindex" bằng cách chỉ lọc những bản ghi có timestamp trùng khớp hoàn toàn với các mốc `:00:00.000`, `:15:00.000`, `:30:00.000`, `:45:00.000`, kết quả thực nghiệm sẽ dẫn đến sự phá hủy dữ liệu:

| Meter ID | Tần suất gốc | Tổng dòng thô thực tế | Dòng khớp chính xác `:00, :15, :30, :45` | Tỷ lệ dữ liệu bị xóa bỏ giả tạo (False Missingness) |
|---|:---:|---:|---:|:---:|
| `H1.Z10` | 1 phút (đồng hồ chuẩn) | 3,155,041 | 210,337 | 0.0% (Khớp 100% mốc 15m) |
| `V.Z84` | 15–18 giây (trôi xung nhịp) | 4,210,903 | 4,201 | **97.3% mốc 15m bị biến thành NaN giả** |
| `H1.Z310` | 30 giây (lệch +2s: `:02`, `:32`) | 1,680,940 | 773 | **96.8% mốc 15m bị biến thành NaN giả** |
| `H1.W12` | 2 phút | 858,642 | 87,114 | **43.6% mốc 15m bị biến thành NaN giả** |

- **Nguyên nhân**: Cảm biến `V.Z84` có bộ đếm thời gian trôi tự do (ví dụ phát lúc `22:00:39`, `22:00:57`, `22:01:14`), còn `H1.Z310` luôn phát tại giây thứ 2 và giây thứ 32 (`:02`, `:32`). Nếu yêu cầu khớp chính xác giây `00`, hệ thống sẽ coi 97% khoảng thời gian bình thường của các meter này là "mất điện" (missing gap)!
- Điều này sẽ phá vỡ hoàn toàn bài toán nghiên cứu Missingness ở P2, biến dữ liệu hoạt động bình thường thành hàng nghìn "failure episode giả".

### 4. Các điểm mơ hồ kỹ thuật chưa được định nghĩa trong Protocol

1. **Thiếu quy ước biên (Boundary Convention)**:
   - Một khoảng 15 phút kết thúc lúc $t$ là khoảng nửa đóng nửa mở bên phải $(t - 15\text{m}, t]$ hay nửa đóng nửa mở bên trái $[t, t + 15\text{m})$?
   - Nhãn thời gian đại diện cho khoảng là nhãn đầu khoảng (Left Label) hay nhãn cuối khoảng (Right Label)?
2. **Thiếu toán tử chọn mẫu đại diện (Aggregation / Selection Operator)**:
   - Khi một khoảng 15 phút chứa 15 đến 60 bản ghi thô, giá trị nào được chọn làm đại diện: `last`, `first`, `nearest`, hay `mean`?
3. **Mơ hồ về phạm vi thời gian (Time Horizon Alignment)**:
   - Mỗi meter có trục lưới riêng bắt đầu từ mốc đo đầu tiên của meter đó (`meter-specific`), hay tất cả 79 meters đều bị kéo dãn trên cùng một trục thời gian 6 năm từ `2017-12-31` đến `2024-01-01` (`global timeline`)?

---

## C. Feasible Interpretation (Cách Hiểu Khả Thi, Bảo Toàn Ý Đồ Nghiên Cứu)

Để bảo đảm tính toàn vẹn nghiên cứu mà không làm sai lệch ý đồ của Protocol Owner, chúng tôi thiết lập cách hiểu kỹ thuật khả thi và chính xác như sau:

### 1. Phân biệt rạch ròi giữa "Biểu diễn 15 phút" và "Điền khuyết (Imputation)"

```text
┌────────────────────────────────────────────────────────┐
│  High-Cadence Raw Stream (15s / 30s / 1m / 2m)         │
└──────────────────────────┬─────────────────────────────┘
                           │  [P1-T3 Resampling: Representation Only]
                           ▼
┌────────────────────────────────────────────────────────┐
│  Standardized 15-Minute Grid (readings_15min.parquet)  │
│  - Bins with raw data   ──> Exact Raw IEEE-754 Reading │
│  - Bins with NO data    ──> NaN (Preserved Real Gap)   │
└──────────────────────────┬─────────────────────────────┘
                           │  [P3/P5 ML Models: Imputation]
                           ▼
┌────────────────────────────────────────────────────────┐
│  Imputed Time Series (Only applied under Mask regimes) │
└──────────────────────────┬─────────────────────────────┘
```

- **Resampling / Representation**: Là quá trình chọn ra **một quan sát đo lường vật lý có thật** trong khoảng 15 phút để làm đại diện cho trạng thái của đồng hồ tại mốc thời gian đó. Quá trình này **không được phép sinh ra bất kỳ giá trị ước tính nào**.
- **Imputation**: Chỉ xảy ra khi một khoảng 15 phút thực sự không có quan sát thô nào (do mất điện, đứt cáp, lỗi gateway) HOẶC khi bị đè mask thử nghiệm. Giá trị khuyết này **phải được giữ nguyên là `NaN` trong suốt P1**; tuyệt đối không dùng forward-fill (`ffill`), backward-fill (`bfill`), hay nội suy tuyến tính (`linear interpolation`) tại P1-T3.

### 2. Đánh giá các phương án toán tử chọn mẫu theo Semantics của $W$

| Phương án | Bản chất toán học | Mức độ phù hợp với $W$ | Vi phạm Invariant? | Đánh giá |
|---|---|---|:---:|---|
| **Exact Reindex** | Lọc chính xác $ts == t$ | Kém: Mất 97% dữ liệu của các meter trôi nhịp giây | Không vi phạm nhưng làm hỏng dữ liệu | **LOẠI BỎ** |
| **Mean (Trung bình)** | $\frac{1}{N} \sum W_i$ | **Sai vật lý**: $W$ là số đọc công tơ tích lũy, trung bình không có nghĩa trạng thái | **VI PHẠM**: Sinh ra số thực nhân tạo, vi phạm *"giá trị warehouse = raw"* | **LOẠI BỎ** |
| **Sum (Tổng)** | $\sum W_i$ | **Sai ngớ ngẩn**: Nhân giá trị công tơ lên 15–60 lần | **VI PHẠM**: Phá vỡ toàn bộ thang đo năng lượng | **LOẠI BỎ** |
| **First (Đầu khoảng)** | Bản ghi đầu tiên trong $[t, t+15\text{m})$ | Tạm chấp nhận, nhưng lệch quy ước kết toán điện năng | Không vi phạm | Khả thi nhưng kém ưu tiên |
| **Last (Cuối khoảng)** | Bản ghi cuối cùng trong $(t-15\text{m}, t]$ | **Hoàn hảo**: Phản ánh chính xác số đọc công tơ chốt tại cuối chu kỳ thanh toán 15 phút | **TUÂN THỦ 100%**: Giá trị lấy ra là bản ghi thô IEEE-754 nguyên bản | **KHUYẾN NGHỊ CAO NHẤT** |

### 3. Tái định nghĩa tiêu chuẩn nghiệm thu "Non-NaN Invariant"

Thay vì hiểu một cách bất khả thi là $\text{count}(\text{non-NaN})_{15\text{m}} = \text{count}(\text{non-NaN})_{\text{raw}} = 208,224,479$, tiêu chuẩn nghiệm thu định lượng đúng đắn phải được diễn đạt thành hai tiêu chí con:

1. **Bảo toàn số khoảng thời gian có dữ liệu (Occupied Bin Preservation)**:
   Mọi khoảng thời gian 15 phút chứa ít nhất 1 bản ghi thô hợp lệ đều phải sinh ra đúng 1 giá trị non-NaN trên lưới (không bị rơi rụng do lệch giây hay trôi xung nhịp). Ngược lại, chỉ những khoảng thời gian hoàn toàn không có bản ghi thô nào mới nhận giá trị `NaN`.
2. **Không sản sinh dữ liệu nhân tạo (Zero Synthetic Observations Invariant)**:
   100% các giá trị non-NaN trên lưới 15 phút phải tồn tại nguyên bản bit-for-bit (IEEE 754 float64) trong tập dữ liệu thô `readings_utc.parquet`. Tuyệt đối không có bất kỳ giá trị tính toán hay nội suy nào.

---

## D. Recommendation (Khuyến Nghị Quản Trị)

Căn cứ theo Điều 1 và Điều 8 của Hiến chương Nghiên cứu `AGENTS.md`:
> *"Nếu phát hiện protocol có mâu thuẫn hoặc lỗ hổng kỹ thuật: Ghi nhận trạng thái BLOCKED... Tuyệt đối không tự ý 'chữa cháy' bằng cách sửa protocol file."*  
> *"Stop Conditions: Agent bắt buộc phải dừng thực thi ngay lập tức và báo cáo cho người dùng khi... Phát hiện mâu thuẫn trong protocol giữa các bảng mô tả, công thức hoặc quy tắc trong TASK_PLAN.md."*

Khuyến nghị chính thức của Pre-Flight Audit:

```text
================================================================================
  KHUYẾN NGHỊ: BLOCKED — PROTOCOL CLARIFICATION REQUIRED
================================================================================
```

### Lý do chi tiết:
1. Tiêu chí nghiệm thu tại dòng 101 của `TASK_PLAN.md` (*"số giá trị non-NaN không đổi so với trước reindex"*) mâu thuẫn toán học trực tiếp với phép downsampling từ 208 triệu dòng xuống lưới 15 phút.
2. Nếu Executor tự ý triển khai mã nguồn và nới lỏng test để bỏ qua tiêu chí này, Executor sẽ vi phạm nghiêm trọng Quy tắc 4 của `AGENTS.md` (*"Không sửa test để pass"*).
3. Do đó, quy trình bắt buộc phải tạm dừng tại cổng kiểm soát tiền trạm để **Protocol Owner / Người dùng xác nhận điều chỉnh định nghĩa tiêu chí nghiệm thu** trước khi cho phép P1-T3 chuyển sang thực thi.

---

## E. Proposed Exact Rule (Quy Tắc Chính Xác Đề Xuất)

Dưới đây là đặc tả quy tắc kỹ thuật hoàn chỉnh, chặt chẽ và không thể hiểu nước đôi, sẵn sàng chuyển thành Unit Test Suite và triển khai ngay khi Protocol Owner phê duyệt:

### 1. Quy ước trục thời gian và ranh giới phân vùng (Boundary Convention)
- **Múi giờ**: `UTC` tuyệt đối (`timestamp[us, tz=UTC]`).
- **Mốc neo lưới (Grid Anchors)**: Cố định tại các phút tròn phần tư giờ:
  $$t \in \{\text{HH:00:00.000000}, \text{HH:15:00.000000}, \text{HH:30:00.000000}, \text{HH:45:00.000000}\}$$
- **Quy ước phân vùng khoảng thời gian (Interval Bin Partition)**:
  Sử dụng quy ước **nửa đóng nửa mở bên phải (Right-Closed, Right-Labeled)**:
  $$\text{Bin}(t) = (t - 15\text{ phút}, t]$$
  Ví dụ: Mốc lưới `12:15:00 UTC` đại diện cho khoảng thời gian $(12:00:00, 12:15:00]$.
- **Phạm vi thời gian của từng Meter (Meter-Specific Grid Range)**:
  Đối với mỗi meter $m$:
  - Mốc bắt đầu lưới: $t_{\text{start}}(m) = \text{ceil\_15min}(\min(ts_{\text{raw}}(m)))$
  - Mốc kết thúc lưới: $t_{\text{end}}(m) = \text{floor\_15min}(\max(ts_{\text{raw}}(m)))$
  - Số bước lưới kỳ vọng của meter $m$:
    $$N_{\text{expected}}(m) = \frac{t_{\text{end}}(m) - t_{\text{start}}(m)}{15\text{ phút}} + 1$$

### 2. Toán tử chọn mẫu đại diện (Representative Observation Operator)
Trong mỗi khoảng $\text{Bin}(t) = (t - 15\text{ phút}, t]$ của meter $m$:
- **Trường hợp A: Khoảng có ít nhất 1 bản ghi thô hợp lệ ($\ge 1$ raw observations)**:
  - Chọn bản ghi có timestamp lớn nhất trong khoảng (toán tử **`LAST`**):
    $$r_{\text{selected}} = \arg\max_{r \in \text{Bin}(t)} (r.\text{timestamp\_utc})$$
  - Gán giá trị: $\text{value}(t) = r_{\text{selected}}.\text{value}$ (giữ nguyên vẹn 100% độ chính xác số thực IEEE 754 float64).
  - Gán provenance: $\text{raw\_source\_file}(t) = r_{\text{selected}}.\text{raw\_source\_file}$.
  - Gán số bản ghi gộp: $\text{raw\_record\_count}(t) = |\text{Bin}(t)|$.
- **Trường hợp B: Khoảng không có bất kỳ bản ghi thô nào ($0$ raw observations — Outage / Gap)**:
  - Gán giá trị: $\text{value}(t) = \text{NaN}$ (null trong Parquet).
  - Gán provenance: $\text{raw\_source\_file}(t) = \text{None}$.
  - Gán số bản ghi gộp: $\text{raw\_record\_count}(t) = 0$.
  - **Nghiêm cấm**: Tuyệt đối không điền giá trị từ bin trước (`ffill`), bin sau (`bfill`), hay nội suy (`interpolate`).

### 3. Bộ tiêu chí nghiệm thu định lượng (Unit Test Specifications cho `tests/test_P1_T3.py`)

Khi Protocol Owner phê duyệt quy tắc trên, file kiểm thử `tests/test_P1_T3.py` sẽ thực thi 5 bài test tự động không khoan nhượng:

```python
# ------------------------------------------------------------------------------
# Test 1: Tính Đều Đặn Của Lưới Thời Gian (Strict Temporal Regularity)
# ------------------------------------------------------------------------------
def test_1_strict_15min_regularity(df_15min_by_meter):
    for meter_id, df_m in df_15min_by_meter.items():
        diffs = df_m['timestamp_utc'].diff().dropna()
        # Mọi bước nhảy thời gian phải đúng chính xác 15 phút (900 giây)
        assert (diffs == pd.Timedelta(minutes=15)).all()
        # Phút chỉ được thuộc {0, 15, 30, 45}, giây và microsecond bằng 0
        assert df_m['timestamp_utc'].dt.minute.isin([0, 15, 30, 45]).all()
        assert (df_m['timestamp_utc'].dt.second == 0).all()
        assert (df_m['timestamp_utc'].dt.microsecond == 0).all()

# ------------------------------------------------------------------------------
# Test 2: Bảo Toàn Số Điểm Kỳ Vọng (Expected Step Count Invariant)
# ------------------------------------------------------------------------------
def test_2_expected_step_count(df_15min_by_meter, expected_steps_dict):
    for meter_id, df_m in df_15min_by_meter.items():
        assert len(df_m) == expected_steps_dict[meter_id]

# ------------------------------------------------------------------------------
# Test 3: Bảo Toàn Khoảng Có Dữ Liệu (Occupied Bin Preservation)
# ------------------------------------------------------------------------------
def test_3_occupied_bin_preservation(df_15min_by_meter, raw_occupied_bins_dict):
    for meter_id, df_m in df_15min_by_meter.items():
        non_nan_count = df_m['value'].count()
        expected_occupied_count = raw_occupied_bins_dict[meter_id]
        # Số ô non-NaN trên lưới phải bằng chính xác số bin (t-15m, t] có dữ liệu thô
        assert non_nan_count == expected_occupied_count

# ------------------------------------------------------------------------------
# Test 4: Không Sinh Dữ Liệu Giả Mạo (0.0000% Synthetic Observations)
# ------------------------------------------------------------------------------
def test_4_zero_synthetic_observations(df_15min_by_meter, raw_df_by_meter):
    # Lấy mẫu ngẫu nhiên 1,000 điểm non-NaN từ các meter
    # Đối chiếu giá trị IEEE-754 float64: phải trùng khớp chính xác với một bản ghi raw
    for sample_point in sample_1000_points:
        assert sample_point.value in raw_df_by_meter[sample_point.meter_id]['value'].values

# ------------------------------------------------------------------------------
# Test 5: Chống Lỗi Trôi Nhịp Giây Cho Meter Tần Suất Cao (Clock-Drift Immunity)
# ------------------------------------------------------------------------------
def test_5_clock_drift_meters_coverage(df_15min_by_meter):
    # Meter V.Z84 (15s) và H1.Z310 (30s lệch 2s) không được bị mất dữ liệu giả tạo
    # Trong các giai đoạn hoạt động bình thường, tỷ lệ coverage phải đạt xấp xỉ 100%
    v_z84 = df_15min_by_meter['V.Z84']
    assert (v_z84.loc['2021-03-01':'2021-03-31', 'value'].isna().sum()) == 0
```

---

## Bảng Đối Soát Định Lượng Trước & Sau Đề Xuất

| Chỉ số kỹ thuật | Hiện trạng Protocol cũ (`TASK_PLAN.md`) | Đề xuất Pre-Flight Audit |
|---|---|---|
| **Định nghĩa tiêu chuẩn Non-NaN** | Số giá trị non-NaN giữ nguyên (208.2M) | Bảo toàn số bin có dữ liệu thô (~13.8M–14.0M) |
| **Tính khả thi toán học** | **0% (Bất khả thi)** | **100% (Khả thi, chính xác bit-for-bit)** |
| **Quy ước biên bin** | Chưa định nghĩa | Nửa đóng nửa mở bên phải $(t-15\text{m}, t]$ |
| **Toán tử chọn mẫu** | Chưa định nghĩa | `LAST` observation trong bin |
| **Tỷ lệ mất dữ liệu giả ở `V.Z84`** | 97.3% (nếu reindex giây) | **0.0% (Bảo toàn 100% thời gian hoạt động)** |
| **Tỷ lệ mất dữ liệu giả ở `H1.Z310`**| 96.8% (nếu reindex giây) | **0.0% (Bảo toàn 100% thời gian hoạt động)** |
| **Tính toàn vẹn Ground Truth** | Nguy cơ bị méo mó | **Bảo toàn 100% giá trị gốc IEEE-754** |
| **Nội suy / Imputation giả mạo** | Nghiêm cấm | **Nghiêm cấm 100%** |

---

## Kết Luận & Hành Động Tiếp Theo

1. Pre-flight check đã hoàn thành đầy đủ, chi tiết và có căn cứ thực nghiệm số liệu trên 208 triệu dòng dữ liệu.
2. Không có bất kỳ file dữ liệu thô (`data/raw/`), file protocol (`TASK_PLAN.md`), hay bảng trung gian (`readings_15min.parquet`) nào bị tạo ra hay can thiệp.
3. Báo cáo này kính chuyển tới **Protocol Owner / Người dùng** để:
   - Phê duyệt quyết định làm rõ mâu thuẫn tiêu chí nghiệm thu của P1-T3;
   - Đồng ý áp dụng **Quy tắc phân vùng biên Right-Closed $(t-15\text{m}, t]$ với toán tử `LAST`** và tiêu chuẩn nghiệm thu Occupied Bin Preservation;
   - Cập nhật tài liệu protocol hoặc ban hành chỉ thị cho phép Executor chuyển sang triển khai mã nguồn chính thức của P1-T3.
