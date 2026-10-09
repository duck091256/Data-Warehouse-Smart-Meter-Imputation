# TASK_PLAN.md — Beyond Synthetic Missingness (Smart-Meter Imputation)

> **Protocol Version**: v1.1 (Officialized 2026-10-06 by Protocol Owner)  
> **Preceding Version**: v1.0 (2026-10-04, historical baseline preserved)  
> **Governing Documents**: `AGENTS.md`, `RESEARCH_PLAN.md`, `reports/protocol_v1_1_amendment.md`, `reports/p1_t3_protocol_amendment_v1_1.md`  

Kế hoạch thực thi cho agent (Antigravity, model flash). Số tuần chỉ là ước lượng, co giãn theo deadline.

### Lịch sử sửa đổi Protocol (Protocol Revision History)

| Phiên bản | Ngày | Trạng thái | Tóm tắt thay đổi | Căn cứ phê duyệt |
|---|---|---|---|---|
| **Protocol v1.0** | 2026-10-04 | Đã thay thế (Superseded) | Kế hoạch ban đầu. Định nghĩa P1-T3 là reindex 15 phút với invariant bảo toàn số lượng non-NaN (`non_nan_after == non_nan_before`). Giả định sơ bộ về nhịp lấy mẫu từ kiểm kê mẫu. | Khởi tạo dự án ban đầu. |
| **Protocol v1.1** | 2026-10-06 | **Hiệu lực chính thức (Official)** | **Amendment toàn diện P1-T3 & Core Population**: <br>1. Thay thế reindex bằng **biểu diễn lưới chuẩn 15 phút / temporal downsampling** với bin nửa đóng bên phải $(t-15\text{m}, t]$ và toán tử **`LAST`**. <br>2. Thay invariant cũ bằng **Occupied Bin Preservation** ($count(\text{non\_nan\_15min}) == count(\text{raw\_occupied\_bins})$) và **Zero Synthetic Observations**. <br>3. Giữ trọn vẹn **79/79 W meters** trong Core Population theo General Core Eligibility Rule (bao gồm `H1.ZE20`). <br>4. Phân biệt `grid_timestamp_utc` và `source_timestamp_utc`. <br>5. Lưới meter: $\text{grid\_start} = \text{ceil\_15m}(\min)$, $\text{grid\_end} = \text{ceil\_15m}(\max)$ (không dùng floor). <br>6. Định nghĩa deterministic `cadence_class`, `cadence_nonstationary`, `bin_completeness`. <br>7. Nghiêm cấm đưa metadata đếm/completeness vào input feature mô hình imputation. <br>8. Xác nhận cân bằng số học 61,790 dòng trùng lặp ($208,286,269 = 208,224,479 + 61,790$). | Quyết định phê duyệt của Protocol Owner (`reports/protocol_v1_1_amendment.md`). |

---

## 0. Quy ước chung

### 0.1 Quyết định chiến lược (đã chốt)

1. **Benchmark 4 nhánh** (S-naive tách thành hai kiểu có độ khó khác nhau)
   - **S-point:** missing điểm đơn ngẫu nhiên, như benchmark thông thường.
   - **S-block:** block missing ngẫu nhiên, không cấu trúc.
   - **S-matched:** mask synthetic nhưng khớp phân phối gap length và missing rate với dữ liệu thực, độc lập giữa các meter.
   - **R-derived:** mask lấy từ failure episode thực, giữ cấu trúc correlated và hierarchy.
   - So S-matched với R-derived để tách riêng tác động của cấu trúc correlated + hierarchy.
   - **S-naive tổng hợp** (gộp S-point + S-block) chỉ báo cáo bổ sung, không là nhánh so sánh chính.
2. **Warehouse là xương sống:** lưu toàn bộ vòng đời thí nghiệm (dữ liệu, mask, model, kết quả).
3. **Phân tầng phạm vi** (đóng góp chính khép lại ở P4)
   - **Lõi nghiên cứu / MVP (bắt buộc):** P1–P4. Câu hỏi trung tâm: synthetic benchmark có bảo toàn độ khó và thứ hạng tương đối khi chuyển sang failure pattern thực hay không.
   - **Mở rộng 1:** P5 (SAITS, BRITS, TimesNet qua PyPOTS, trên subset meter).
   - **Mở rộng 2 (có điều kiện, tương ứng M4 của proposal):** P6 (selector/ensemble + downstream forecasting). Chỉ làm khi **cổng quyết định P4-T8** cho thấy ranking đổi đáng kể theo regime; nếu ranking ổn định thì selector không có động cơ và P6 được bỏ, ghi rõ lý do trong báo cáo.
   - P7 (dashboard + viết) luôn phải làm, kể cả khi chỉ có MVP.
4. **Mô hình baseline:** Linear, Seasonal Naive, KNN, XGBoost. Không dùng Random Forest (XGBoost đã đại diện nhóm cây); proposal cần sửa cho khớp.

### 0.1b Đối chiếu proposal (M) ↔ kế hoạch (P)

| Proposal | Kế hoạch | Ghi chú |
|---|---|---|
| M1: phân tích failure pattern | P1 + P2-T1/T2 | Lõi |
| M2: benchmark synthetic + real-derived | P2 | Lõi |
| M3: độ nhạy và ổn định ranking | P3 + P4 | Lõi, đóng góp chính |
| Deep learning | P5 | Mở rộng |
| M4: selector + downstream forecasting | P6 | Mở rộng có điều kiện |
| Báo cáo, dashboard | P7 | Bắt buộc |

### 0.1c Quần thể nghiên cứu cốt lõi & Quy tắc hợp lệ (Core Population & General Eligibility Rule — Protocol v1.1)

1. **Quy tắc hợp lệ tổng quát (General Core Eligibility Rule)**:
   ```text
   CoreEligible(m) iff
       history_duration_days(m) >= 365
       AND
       median_gap_seconds(m) <= 900
       AND
       occupied_15min_rate(m) >= 0.50
       AND
       measurement_semantics(m) = 'W'
   ```
2. **Lưu ý phạm vi & Giới hạn bắt buộc (Scope Disclosure / Limitation Note)**:
   > *Thresholds 365 days / 900 seconds / 50% were specified after inspecting the observed dataset, but before any model training, imputation result, ranking analysis, or performance-based selection. Since all 79 meters satisfy the rule, the rule does not act as an outcome-driven exclusion criterion in the current population. This fact must be disclosed explicitly as a limitation / scope note.*
3. **Quy mô quần thể cốt lõi**:
   - Toàn bộ **79 / 79 W meters** đều thỏa mãn quy tắc và được giữ trọn vẹn trong Core Population.
   - Tuyệt đối không loại trừ bất kỳ meter nào dựa trên: kết quả chạy mô hình, độ khó imputation, thứ hạng mô hình, hoặc kết quả phát hiện sự cố (failure detection).
4. **Vị trí của Meter `H1.ZE20`**:
   - `H1.ZE20` có khoảng 397 ngày dữ liệu (chính xác 396.61 ngày, ~13 tháng, từ 2022-11-30 đến 2023-12-31), median gap **30.0 giây**, tỷ lệ chiếm dụng **73.49%**. Do đó meter chỉ vượt ngưỡng lịch sử một cách vừa đủ; meter vẫn Core Eligible theo rule chung ($396.61 \ge 365$).
   - **Ràng buộc phân chia thời gian (Downstream Temporal Split Constraint)**: Các phân chia tập train/test theo thời gian (P3, P5, P6) bắt buộc phải kiểm tra sự tồn tại của từng meter trong khoảng thời gian split; tuyệt đối không ép `H1.ZE20` tham gia vào các giai đoạn thời gian trước khi meter này vận hành.
5. **Đính chính khẳng định về độ phủ hệ thống HVAC**:
   - Nghiêm cấm nhận định *"9 meter là toàn bộ HVAC"* hoặc *"loại bỏ 9 meter sẽ làm mất toàn bộ hệ HVAC"*. Toàn bộ phụ tải điện HVAC (chillers, AHU, máy bơm) đã được đo đạc đầy đủ bởi hệ thống 70 công tơ điện (`Z`, `ZE`, `H*.T.Z`), và meter nhiệt `H1.W12` (858K dòng, độ chiếm dụng 85.04% trong 6 năm) không nằm trong nhóm 9 meter này.
   - **Tuyên bố khoa học chính thức**: Việc lưu giữ các đồng hồ nhiệt nước (`H1.K11..K16`, `H1.W11`, `H2.K21`, `V.K21`) nhằm bổ sung **tính đa dạng tải vật lý đa năng lượng (multi-carrier energy diversity)**, kết hợp giữa chuỗi phụ tải điện và phụ tải nhiệt thủy lực.
6. **Cân bằng số học đối soát (Reconciliation Balance Target)**:
   $$\text{Raw } W \text{ (208,286,269)} = \text{Deduplicated } W \text{ (208,224,479)} + \text{V.Z84 Duplicates (61,790)}$$

### 0.1d Metadata đồng hồ & Phân lớp nhịp điệu (Meter Cadence & Metadata Protocol — Protocol v1.1)

1. **Lược đồ Metadata cấp Meter (`Dim_Meter`)**:
   Mỗi meter phải có các thuộc tính:
   ```text
   meter_id, meter_type, history_start, history_end, history_duration_days,
   median_gap_seconds, p95_gap_seconds, max_gap_seconds, occupied_15min_rate,
   cadence_class, cadence_nonstationary, core_eligible
   ```
2. **Quy tắc xác định `meter_type`**:
   - Phải xác định bằng chứng cứ từ tài liệu nguồn / metadata kỹ thuật nếu có.
   - Các nhóm chuẩn hóa: `electrical_load`, `electrical_generation/PV`, `thermal_cooling`, `thermal_heating`, `other`, `unknown`.
   - Không được suy diễn chỉ từ tên meter nếu không có chứng cứ. Nếu suy ra từ quy ước đặt tên (naming conventions), phải ghi rõ quy tắc, mức độ tin cậy và không trình bày như sự thật từ nguồn (source fact).
3. **Phân lớp nhịp điệu tất định (`cadence_class`)**:
   - Xác định từ **trung vị khoảng cách quan sát dương trên toàn lịch sử hợp lệ** (`median_gap_seconds = median(diff(timestamp_utc))` trên các hiệu số $> 0$ sau P1-T2). Không dùng mean gap hay max gap để phân lớp:
     - $\le 22.5\text{ s} \implies \text{C15S}$
     - $> 22.5\text{ s} - 45.0\text{ s} \implies \text{C30S}$
     - $> 45.0\text{ s} - 90.0\text{ s} \implies \text{C1M}$
     - $> 90.0\text{ s} - 180.0\text{ s} \implies \text{C2M}$
     - $> 180.0\text{ s} - 540.0\text{ s} \implies \text{C6M}$
     - $> 540.0\text{ s} - 900.0\text{ s} \implies \text{C10M\_PLUS}$
     - $> 900.0\text{ s} \implies \text{SPARSE\_GT15M}$
4. **Tính không dừng của nhịp điệu (`cadence_nonstationary`)**:
   - Tính thêm trung vị khoảng cách theo từng tháng lịch (`calendar month`). Nếu `cadence_class` của bất kỳ tháng nào khác với `cadence_class` toàn lịch sử, gán:
     $$\text{cadence\_nonstationary} = \text{true}$$
     và lưu tóm tắt các lớp nhịp điệu quan sát được. Lớp nhịp điệu toàn lịch sử vẫn được giữ làm baseline cố định.
5. **Độ đầy đủ của ô thời gian (`bin_completeness`)**:
   - Cho mỗi meter: $\text{estimated\_cadence\_seconds} = \text{median\_gap\_seconds}$.
   - Cho mỗi bin có $\text{observed\_count} = \text{raw\_record\_count}$:
     - Ô chuẩn ($900\text{s}$): $\text{expected\_record\_count\_full\_bin} = \max(1, \text{round}(900 / \text{estimated\_cadence\_seconds}))$.
     - Ô biên có độ dài phủ $\text{covered\_duration\_seconds}$: $\text{expected\_record\_count\_bin} = \max(1, \text{round}(\text{covered\_duration\_seconds} / \text{estimated\_cadence\_seconds}))$.
     - $\text{bin\_completeness} = \min(1.0, \text{observed\_count} / \text{expected\_record\_count\_bin})$.
   - Lưu trữ cả `expected_record_count` và `raw_record_count` để phục vụ đối soát.
   - **Tính chất**: `bin_completeness` là **descriptive metadata**, tuyệt đối không dùng để sửa, điền hoặc nội suy dữ liệu.
6. **NGHIÊM CẤM RÒ RỈ TÍNH NĂNG (Anti-Leakage Mandate)**:
   - **`raw_record_count` và `bin_completeness` CẤM TUYỆT ĐỐI đưa làm input feature cho bất kỳ mô hình imputation nào (P3, P5, P6).**
   - *Lý do*: Tại một bin bị mask, việc cung cấp số bản ghi thô hoặc độ đầy đủ sẽ tiết lộ rằng ô đó ban đầu có quan sát, phá hủy tính hợp lệ của benchmark.

### 0.1e Chuẩn mực biểu diễn lưới 15 phút (15-Minute Regular-Grid Representation — Protocol v1.1)

1. **Múi giờ & Mốc neo**: `UTC`. Neo tại $t \in \{\text{HH:00:00}, \text{HH:15:00}, \text{HH:30:00}, \text{HH:45:00}\}$ với second/microsecond = 0.
2. **Phạm vi lưới từng Meter**:
   $$\text{grid\_start}(m) = \text{ceil\_to\_15min}(\min(\text{source\_timestamp\_utc}))$$
   $$\text{grid\_end}(m) = \text{ceil\_to\_15min}(\max(\text{source\_timestamp\_utc}))$$
   **Tuyệt đối không dùng `floor` cho `grid_end`.** (Ví dụ quan sát cuối lúc $12:07$ rơi vào bin $(12:00, 12:15]$, do đó $\text{grid\_end} = \text{ceil}(12:07) = 12:15$).
3. **Ngữ nghĩa ô thời gian**: $\text{Bin}(t) = (t - 15\text{ phút}, t]$ (nửa đóng, gán nhãn biên phải).
4. **Toán tử chọn mẫu đại diện (`LAST`)**:
   - Nếu $\text{Bin}(t)$ có $\ge 1$ quan sát thô hợp lệ: chọn bản ghi có `source_timestamp_utc` lớn nhất.
   - Đầu ra: $\text{value} = \text{selected.value}$, $\text{source\_timestamp\_utc} = \text{selected.timestamp\_utc}$, $\text{raw\_source\_file} = \text{selected.raw\_source\_file}$, $\text{raw\_record\_count} = |\text{Bin}(t)|$.
   - Nghiêm cấm: `mean`, `sum`, `nearest`, `ffill`, `bfill`, `interpolation`, `smoothing`.
5. **Phân biệt rạch ròi giữa Grid Timestamp và Source Timestamp**:
   - `grid_timestamp_utc`: Timestamp chuẩn hóa của lưới 15 phút. Cặp `(grid_timestamp_utc, value)` là biểu diễn trên lưới, không phải raw observation.
   - `source_timestamp_utc`: Timestamp vật lý thật của cảm biến.
   - `timestamp_local`: Biểu diễn giờ địa phương Đức (`Europe/Berlin`) tại `grid_timestamp_utc` dùng cho phân tích chu kỳ ngày đêm downstream.
6. **Ngữ nghĩa ô rỗng (Empty Bin Semantics)**:
   - Nếu $\text{raw\_record\_count} = 0$: $\text{value} = \text{NaN}$, $\text{source\_timestamp\_utc} = \text{NULL}$, $\text{raw\_source\_file} = \text{NULL}$, $\text{bin\_completeness} = 0.0$.
   - **Tuyên bố chính thức**: *Ô 15 phút rỗng là một khoảng gián đoạn quan sát (observation gap) trên lưới chuẩn hóa. Nó chưa tự động được coi là sự cố thiết bị (equipment failure). Ngữ nghĩa failure chỉ được thiết lập downstream ở P1-T4 và P2 thông qua quality flags và issue logs.*
7. **Bảo toàn ô có dữ liệu (Occupied Bin Preservation Invariant)**:
   $$\text{count}(\text{non\_nan\_15min}(m)) = \text{count}(\text{raw\_occupied\_bins}(m)) \quad \forall m \in [1, 79]$$
8. **Bảo tồn quan sát gốc (Zero Synthetic Observation Invariant)**:
   Mọi giá trị non-NaN trong đầu ra phải truy nguyên $100\%$ về một tuple $(\text{meter\_id}, \text{source\_timestamp\_utc}, \text{raw\_source\_file}, \text{value})$ trong `readings_utc.parquet`.

### 0.2 Warehouse schema (mục tiêu)

| Loại | Bảng | Cột & Ngữ nghĩa chính |
|---|---|---|
| Dimension | `Dim_Meter` | `meter_id`, `meter_type`, `history_start`, `history_end`, `history_duration_days`, `median_gap_seconds`, `p95_gap_seconds`, `max_gap_seconds`, `occupied_15min_rate`, `cadence_class`, `cadence_nonstationary`, `core_eligible` |
| Dimension | `Dim_Time` | `time_id`, `timestamp_utc`, `timestamp_local`, `year`, `month`, `day`, `hour`, `minute`, `day_of_week`, `is_weekend`, `season` |
| Dimension | `Dim_Model` | `model_id`, `model_name`, `model_family` (baseline/DL), `hyperparameters` |
| Dimension | `Dim_Regime` | `regime_id`, `gap_length_bin`, `correlated_level`, `cadence_class` |
| Fact | `Fact_Reading` | `meter_id`, `grid_timestamp_utc`, `timestamp_local`, `source_timestamp_utc`, `value`, `raw_source_file`, `raw_record_count`, `expected_record_count`, `bin_completeness`, `cadence_class` (bảng `readings_15min`) |
| Fact | `Fact_FailureEpisode` | `episode_id`, `meter_id`, `start_time`, `end_time`, `duration_steps`, `failure_type`, `issue_ticket` |
| Fact | `Fact_Mask` | `mask_id`, `branch` (S-point/S-block/S-matched/R-derived), `meter_id`, `start_time`, `end_time`, `gap_length` |
| Fact | `Fact_ImputationResult` | `result_id`, `mask_id`, `model_id`, `mae`, `rmse`, `energy_bias_kwh` |
| Fact | `Fact_ForecastResult` | `forecast_id`, `imputation_result_id`, `mae_forecast`, `rmse_forecast` |
| Metadata | `Meta_Run` | `run_id`, `seed`, `data_version`, `config_hash`, `git_commit`, `timestamp`, `log_path` |

### 0.3 Cấu trúc repo gợi ý

```
data-warehousing/
├── TASK_PLAN.md
├── configs/            # yaml cho từng giai đoạn (seed, tham số)
├── data/               # raw/ (read-only), interim/, processed/
├── etl/                # script nạp warehouse
├── masks/              # mask engine
├── models/             # baseline + DL wrapper
├── analysis/           # ranking, bootstrap, OLAP query
├── tests/              # assert tự động theo từng task
├── audits/             # báo cáo audit theo giai đoạn (AUDIT_P1.md, ...)
└── reports/
```

### 0.4 Định dạng một task

Mọi task phải có đủ các trường sau, nếu thiếu thì chưa được giao cho agent:

```
ID:          Px-Ty
Mục tiêu:    1 câu
Đầu vào:     file/bảng cụ thể
Đầu ra:      file/bảng cụ thể
Kiểm thử:    assert/script chạy tự động, tiêu chí pass/fail định lượng
Phụ thuộc:   ID task trước
```

### 0.5 Quy tắc làm việc với agent (model flash)

- Mỗi lần giao **một task** (tối đa 2 task liên quan chặt). Không giao "làm cả P2".
- Mỗi task phải kèm **script test tự động** (`tests/test_Px_Ty.py`). Không chấp nhận báo cáo "đã xong" nếu test không chạy ra pass.
- Agent không được sửa `data/raw/` và không được sửa test để cho pass. Nếu test sai thì báo lại.
- Mọi script nhận `--seed` và `--config`; không hard-code đường dẫn hay seed.
- Mọi lần chạy ghi một dòng vào `Meta_Run`.
- Cuối mỗi task agent ghi log ngắn: đã làm gì, số liệu chính, điều chưa chắc chắn.
- Sau mỗi giai đoạn: chạy **audit riêng** (mục "Checklist audit" của giai đoạn) bằng một phiên agent mới, không dùng phiên đã code, rồi mới qua cổng.

### 0.6 Quy tắc bất biến (vi phạm là lỗi nghiêm trọng)

- Không dùng giá trị **corrected** làm ground truth.
- Không để cùng một outage/episode xuất hiện ở cả train và test.
- Ground truth chỉ lấy từ **clean segment** (không thiếu, không có issue, không bị corrected).
- Mọi con số trong báo cáo phải truy ngược được về một query trên warehouse.
- **Bảo toàn Occupied Bin & Zero Synthetic Observations (Protocol v1.1)**: Mọi non-NaN trên lưới 15 phút phải truy nguyên 100% về bản ghi raw tương ứng; cấm tạo giá trị nhân tạo qua mean, sum, nearest, ffill, bfill, interpolation.
- **Không rò rỉ tính năng (Anti-Leakage Mandate)**: `raw_record_count`, `expected_record_count`, và `bin_completeness` CẤM TUYỆT ĐỐI đưa vào input feature của bất kỳ mô hình imputation nào.
- **Phân biệt bản chất khoảng rỗng**: Ô rỗng 15 phút sau P1-T3 là observation gap trên biểu diễn chuẩn hóa, không được tự động gán nhãn sự cố thiết bị (failure label).
- **Tính bất biến của Core Population**: Giữ trọn 79/79 W meters; không loại trừ meter nào dựa trên kết quả chạy thử, độ khó imputation, thứ hạng hay kết quả phát hiện sự cố.

---

## P1 — Tiền xử lý + ETL (~1–1,5 tuần)

**Mục tiêu:** có dữ liệu chuẩn hóa 15 phút, xác định clean segment, nạp vào warehouse chạy lại được từ đầu.

| ID | Task | Đầu vào | Đầu ra | Kiểm thử |
|---|---|---|---|---|
| P1-T1 | Kiểm kê dữ liệu thô: số meter, khoảng thời gian, tần suất, cột, tỷ lệ NaN theo meter | `data/raw/*` | `reports/p1_inventory.md`, `data/interim/inventory.csv` | Tổng số dòng khớp nguồn; không có meter nào bị bỏ sót |
| P1-T2 | Chuẩn hóa múi giờ và DST: quy về UTC, lưu cả local time | raw + quy tắc múi giờ | `data/interim/readings_utc.parquet` | Không trùng timestamp theo meter; không lỗ hổng giả quanh ngày chuyển DST; đối soát cân bằng 61,790 dòng duplicate V.Z84 |
| P1-T3 | Biểu diễn lưới đều 15 phút (temporal downsampling): nửa đóng bên phải `(t-15m, t]`, toán tử `LAST`, giữ `NaN` cho empty bin, không nội suy (Protocol v1.1) | `data/interim/readings_utc.parquet` | `data/interim/readings_15min.parquet` | 9 tiêu chí nghiệm thu Protocol v1.1: Regularity; Grid length với `grid_end = ceil_15m(max)`; Occupied Bin Preservation; Zero Synthetic; Source provenance; Empty bin NaN; Clock drift immunity; Raw immutability; Corrected exclusion |
| P1-T4 | Đánh dấu cờ chất lượng từng điểm: missing, có issue log, corrected (Ratified Amendment: $Bin(t) \cap I \neq \emptyset \iff s \le t \land e > t - 15\text{min}$) | readings + issue logs + correction logs | cột cờ `is_missing`, `has_issue`, `is_corrected`, `is_valid_ground_truth` | `has_issue` = 816,799; `is_valid_ground_truth` = 12,637,042; $Q_1$=12,637,042, $Q_2$=696,535, $Q_3$=527,756, $Q_4$=120,264; 100% bit-for-bit values |
| P1-T5 | Trích **clean segment**: đoạn liên tục không thiếu, không issue, không corrected, độ dài ≥ L tối thiểu (tham số trong config) | cờ chất lượng | `data/processed/clean_segments.parquet` (meter, start, end, length) | Không có điểm nào trong segment mang cờ xấu; thống kê độ dài theo meter |
| P1-T6 | Thiết kế và tạo schema warehouse (DDL) | schema mục 0.2 | `etl/ddl.sql`, ERD (`reports/erd.png`) | DDL chạy được trên DB sạch; khóa ngoại hợp lệ |
| P1-T7 | ETL nạp `Dim_Meter` (hierarchy), `Dim_Time`, `Fact_Reading` | processed data + DDL | warehouse có dữ liệu | Số dòng warehouse = số dòng nguồn; chạy lại 2 lần cho kết quả giống hệt (idempotent) |
| P1-T8 | Viết `run_etl.sh` chạy từ đầu đến cuối bằng một lệnh | toàn bộ | script + log | Xóa DB, chạy lại, các assert P1-T7 vẫn pass |

### Chi tiết Tiêu chí Nghiệm thu P1-T3 (Protocol v1.1 Acceptance Criteria)
1. **Test 1 — Regularity**: Mỗi meter, các grid timestamps tăng đúng 15 phút, nằm đúng mốc `:00/:15/:30/:45`, giây và microsecond bằng 0.
2. **Test 2 — Expected grid length**: Bậc lưới bằng $\frac{\text{grid\_end}(m) - \text{grid\_start}(m)}{15\text{ phút}} + 1$, trong đó $\text{grid\_start}(m) = \text{ceil\_to\_15min}(\min(\text{source\_timestamp\_utc}))$ và $\text{grid\_end}(m) = \text{ceil\_to\_15min}(\max(\text{source\_timestamp\_utc}))$. Tuyệt đối không dùng `floor` cho `grid_end`.
3. **Test 3 — Occupied Bin Preservation**: $count(\text{non\_nan\_15min}(m)) == count(\text{raw\_occupied\_bins}(m))$ với từng meter. Mọi occupied bin tạo đúng 1 non-NaN, mọi empty bin tạo NaN.
4. **Test 4 — Zero Synthetic**: Mỗi giá trị non-NaN đầu ra phải khớp chính xác 100% bit-for-bit với bản ghi raw được chọn.
5. **Test 5 — Source provenance**: Mỗi dòng non-NaN phải có `source_timestamp_utc`, `raw_source_file`, và $\text{raw\_record\_count} \ge 1$.
6. **Test 6 — Empty bin**: Ô rỗng có `value = NaN`, `source_timestamp_utc = NULL`, `raw_source_file = NULL`, $\text{raw\_record\_count} = 0$, $\text{bin\_completeness} = 0.0$.
7. **Test 7 — Clock drift immunity**: Cảm biến tần suất 15s/30s/60s/120s/360s không bị mất độ phủ giả chỉ vì timestamp không rơi đúng giây `:00`.
8. **Test 8 — Raw immutability**: Thư mục `data/raw/` được bảo toàn nguyên vẹn 100%.
9. **Test 9 — Corrected exclusion**: Không bản ghi `_corrected_raw` nào lọt vào đầu ra chính thức.

### Chi tiết Tiêu chí Nghiệm thu P1-T4 (Ratified Protocol v1.1 Amendment — Issue Overlap Semantics)
1. **Ngữ nghĩa Giao tập Ô thời gian và Khoảng sự cố (Set Intersection Semantics)**:
   - Với ô lưới nửa đóng phải $\text{Bin}(t) = (t - 15\text{min}, t] = (t - 900\text{s}, t]$ và khoảng sự cố $I = [s, e]$:
     $$\text{has\_issue}(t) = \text{TRUE} \iff \text{Bin}(t) \cap I \neq \emptyset \iff (s \le t) \land (e > t - 900\text{s})$$
   - Boundary-start inclusion: Nếu sự cố bắt đầu đúng nhãn mốc lưới ($s = t$), ô lưới đó mang `has_issue = TRUE`.
   - Left-boundary exclusion: Nếu sự cố kết thúc đúng biên trái mở ($e = t - 900\text{s}$), ô lưới không bị gắn cờ nếu không có khoảng sự cố khác giao cắt.
   - Zero-duration consistency: Sự cố tức thời $[s, s]$ được gắn cờ nhất quán khi $t - 900\text{s} < s \le t$.
2. **Tiêu chuẩn Số lượng & Phân bố Bốn góc phần tư (Four-Quadrant Yield)**:
   - Tổng số dòng: đúng 13,981,597 dòng across 79 core meters.
   - `has_issue`: đúng 816,799 dòng mang cờ TRUE.
   - `is_valid_ground_truth`: đúng 12,637,042 dòng mang cờ TRUE (bảo vệ tuyệt đối khỏi quan sát hỏng tại biên $s = t$).
   - $Q_1$ (Clean Observed, `!missing & !issue`): 12,637,042 dòng.
   - $Q_2$ (Issue Observed, `!missing & issue`): 696,535 dòng.
   - $Q_3$ (Unrelated Gap, `missing & !issue`): 527,756 dòng.
   - $Q_4$ (Corroborated Gap, `missing & issue`): 120,264 dòng.
3. **Bảo toàn Dữ liệu & Chống Rò rỉ**:
   - 100% giá trị `value`, `grid_timestamp_utc`, `source_timestamp_utc` bảo toàn bit-for-bit từ P1-T3 (Value buffer SHA-256: `8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe`).
   - Đúng 648,020 vị trí NaN được bảo toàn.
   - `is_corrected = FALSE` cho 100% dòng (zero corrected raw files).

**Cổng nghiệm thu P1**
- [ ] ETL chạy lại được từ đầu bằng một lệnh.
- [ ] Số dòng warehouse khớp nguồn và bảo toàn Occupied Bins.
- [ ] Có thống kê clean segment theo meter (số segment, tổng độ dài, meter nào không có segment nào).

**Checklist audit P1**
- [ ] Đối chiếu ngẫu nhiên 30 meter × 5 khoảng thời gian: giá trị warehouse = giá trị raw (toán tử `LAST`).
- [ ] Kiểm tra ngày chuyển DST (cả hai chiều) cho ít nhất 3 meter.
- [ ] Không có giá trị corrected lọt vào clean segment (query kiểm tra cờ).
- [ ] Không có reindex/nội suy làm "mọc" giá trị mới (Zero Synthetic Observation).
- [ ] Invariant Occupied Bin Preservation đạt 100% cho toàn bộ 79 meters.
- [ ] `grid_end` được tính bằng `ceil_to_15min(max(source_timestamp))`, không dùng `floor`.
- [ ] `Meta_Run` ghi đủ seed, data_version, config_hash.
- [ ] Hierarchy trong `Dim_Meter` khớp tài liệu nguồn (không meter mồ côi).

---

## P2 — Mask engine (~1,5 tuần)

**Mục tiêu:** sinh 4 nhánh mask (S-point, S-block, S-matched, R-derived), replay lên clean segment, tái lập được bằng seed.

| ID | Task | Đầu vào | Đầu ra | Kiểm thử |
|---|---|---|---|---|
| P2-T1 | Trích failure episode từ issue logs: (meter, start, end, loại lỗi, nhóm correlated) | issue logs | `Fact_FailureEpisode` | Số episode khớp log; không episode có `end < start`; không trùng lặp |
| P2-T2 | Mô tả thống kê episode: phân phối gap length, missing rate theo meter, mức correlated (nhiều meter cùng hỏng cùng lúc), hierarchy | `Fact_FailureEpisode` | `reports/p2_episode_stats.md` + bảng | Có histogram gap length (đã chia bin); định nghĩa "mức correlated" ghi rõ bằng công thức |
| P2-T3 | Quy tắc ghép mask với clean segment: cùng loại ngày (ngày làm việc/cuối tuần), cùng khung giờ, cùng mùa nếu có thể | episode stats + clean segments | `docs/mask_placement_rules.md` + hàm `place_mask()` | Test: mask không bao giờ đè lên điểm ngoài clean segment; quy tắc ghép được áp dụng cho 100% mask |
| P2-T4 | Sinh **R-derived**: replay hình dạng episode thực lên clean segment, giữ cấu trúc correlated giữa các meter | T1–T3 | `Fact_Mask` (branch = R) | Thứ tự và độ lệch thời gian giữa các meter trong cùng episode được giữ nguyên |
| P2-T5a | Sinh **S-point**: missing điểm đơn ngẫu nhiên | config tỷ lệ missing | `Fact_Mask` (branch = S-point) | Missing rate tổng thể xấp xỉ mục tiêu (dung sai ghi trong config); không có gap dài hơn 1 bước |
| P2-T5b | Sinh **S-block**: block missing ngẫu nhiên, không cấu trúc correlated | config tỷ lệ missing, phân phối độ dài block | `Fact_Mask` (branch = S-block) | Missing rate xấp xỉ mục tiêu; vị trí block độc lập giữa các meter |
| P2-T6 | Sinh **S-matched**: khớp phân phối gap length và missing rate với R-derived, nhưng độc lập giữa các meter (không correlated) | R-derived stats | `Fact_Mask` (branch = S-matched) | Kiểm định khớp phân phối gap (KS hoặc so quantile) với R-derived đạt ngưỡng trong config; không còn tương quan giữa meter |
| P2-T7 | Cố định seed, version hóa mask | tất cả | `masks/v1/` + hash | Chạy lại với cùng seed ra mask giống hệt (so hash) |
| P2-T8 | Test chống rò rỉ | mask + data | `tests/test_leakage_P2.py` | Giá trị ground truth của điểm bị mask không xuất hiện trong input của bất kỳ model nào |

**Cổng nghiệm thu P2**
- [ ] Phân phối gap length và missing rate của S-matched khớp R-derived.
- [ ] Mask tái lập được hoàn toàn bằng seed.
- [ ] Test không rò rỉ ground truth pass.

**Checklist audit P2**
- [ ] Vẽ lại phân phối gap của 4 nhánh trên cùng một biểu đồ, kiểm tra bằng mắt.
- [ ] R-derived thật sự còn tương quan giữa các meter; S-matched thì không (đo bằng một chỉ số cụ thể).
- [ ] Mask không dùng dữ liệu corrected để xác định vùng "sạch".
- [ ] Quy tắc ghép mask không làm lệch phân phối loại ngày/khung giờ so với episode thực.
- [ ] Kiểm tra ngẫu nhiên 20 mask: giá trị gốc dưới mask = giá trị raw.
- [ ] Số lượng mask mỗi nhánh (S-point, S-block, S-matched, R-derived) bằng nhau, hoặc có lý do ghi rõ nếu khác.

---

## P3 — Baseline end-to-end (~1 tuần)

**Mục tiêu:** chạy 4 baseline trên một nhóm nhỏ meter, ghi kết quả vào warehouse, pipeline lặp lại được.

| ID | Task | Đầu vào | Đầu ra | Kiểm thử |
|---|---|---|---|---|
| P3-T1 | Chọn nhóm pilot (~10–20 meter, đủ đa dạng theo hierarchy/loại tải) | clean segments | `configs/pilot_meters.yaml` | Có ghi tiêu chí chọn; không chọn theo kết quả |
| P3-T2 | Interface chung cho imputer: `fit(train)`, `impute(masked)` | — | `models/base.py` | Mọi baseline dùng chung interface; test với dữ liệu giả |
| P3-T3 | Cài **Linear interpolation** và **Seasonal Naive** | base | `models/linear.py`, `models/seasonal_naive.py` | Test trên chuỗi tổng hợp có đáp án biết trước |
| P3-T4 | Cài **KNN** và **XGBoost** (feature chỉ từ phần không bị mask) | base | `models/knn.py`, `models/xgb.py` | Test: không dùng bất kỳ giá trị nào trong vùng mask làm feature |
| P3-T5 | Định nghĩa metric: MAE, RMSE, và metric bảo toàn năng lượng (sai lệch tổng kWh trong gap) | — | `analysis/metrics.py` | Unit test với ví dụ tính tay |
| P3-T6 | Runner: chạy (model × nhánh × meter × mask) và ghi `Fact_ImputationResult` | tất cả | kết quả trong warehouse | Số dòng kết quả = số tổ hợp kỳ vọng; không NaN trong cột metric |
| P3-T7 | Kiểm tra tính hợp lý | kết quả | `reports/p3_sanity.md` | Linear tốt ở gap ngắn, kém ở gap dài; Seasonal Naive ổn ở gap dài; nếu không, điều tra trước khi đi tiếp |

**Cổng nghiệm thu P3**
- [ ] Số liệu hợp lý theo kỳ vọng vật lý (xem P3-T7).
- [ ] Chạy lại cùng seed ra kết quả giống hệt.
- [ ] Mọi kết quả đã nằm trong `Fact_ImputationResult`.

**Checklist audit P3**
- [ ] Thử một "oracle" (impute bằng đúng ground truth): lỗi phải bằng 0, chứng minh pipeline đo đúng.
- [ ] Thử một "tệ nhất" (impute bằng hằng số): lỗi phải cao hơn mọi baseline.
- [ ] Đọc code từng baseline, xác nhận không nhìn thấy giá trị dưới mask.
- [ ] Hyperparameter được chọn trên tập tách riêng, không chọn trên tập đánh giá.
- [ ] Kiểm tra biên: gap ở đầu/cuối segment, gap dài hơn context.
- [ ] Thời gian chạy và bộ nhớ ghi lại để ước lượng chi phí P5.

---

## P4 — Phân tích ranking (~1 tuần)

**Mục tiêu:** trả lời câu hỏi cốt lõi: ranking của các phương pháp trên S-point/S-block/S-matched có giống R-derived không, và vì sao.

| ID | Task | Đầu vào | Đầu ra | Kiểm thử |
|---|---|---|---|---|
| P4-T1 | Tính ranking theo từng meter/segment (không chỉ ranking tổng) | `Fact_ImputationResult` | bảng ranking | Mỗi meter có đủ model; xử lý hòa hạng nhất quán |
| P4-T2 | Kendall τ giữa các nhánh: S-point vs R, S-block vs R, S-matched vs R (so sánh chính); S-point vs S-block, S-naive tổng hợp vs R (bổ sung) | bảng ranking | phân phối τ theo meter | τ nằm trong [-1, 1]; unit test với ranking giả biết trước |
| P4-T3 | Bootstrap CI (resample theo meter hoặc episode, không resample từng điểm) | T2 | bảng τ kèm CI 95% | Seed cố định; CI hẹp dần khi tăng số lần bootstrap |
| P4-T4 | Phân tách theo bin gap length × mức correlated × cadence_class | bảng ranking | OLAP cube / bảng pivot | Phân tầng theo cadence_class (và khi cần meter_type); mỗi ô có đủ mẫu tối thiểu; ô thiếu mẫu được đánh dấu, không điền |
| P4-T5 | Phân tích energy consistency (tổng kWh trong gap) theo nhánh | metric | bảng + biểu đồ | Khớp công thức ở P3-T5 |
| P4-T6 | Viết các OLAP query chuẩn (SQL/MDX) cho các câu hỏi chính | warehouse | `analysis/olap_queries.sql` | Mỗi query chạy được và trả kết quả khớp bảng ở T1–T5 |
| P4-T7 | Tóm tắt kết luận và giới hạn | tất cả | `reports/p4_findings.md` | Mỗi kết luận có tham chiếu tới một query |
| P4-T8 | **Cổng quyết định P6**: đối chiếu kết quả P4 với tiêu chí kích hoạt đã khai báo trước trong `configs/p6_trigger.yaml` (ví dụ: CI của τ giữa S-matched/S-point/S-block và R nằm dưới ngưỡng, hoặc mô hình tốt nhất khác nhau ở ≥ X% ô gap × correlated) | P4-T3, P4-T4 | `reports/p6_decision.md` (làm / không làm P6, kèm bằng chứng) | Tiêu chí và ngưỡng được commit **trước** khi chạy phân tích P4 (hash trong `Meta_Run`); kết luận chỉ dựa trên tiêu chí đó |

**Cổng nghiệm thu P4**
- [ ] Có khoảng tin cậy (bootstrap) cho mọi kết luận về ranking.
- [ ] Có kết luận rõ: ranking đổi hay không đổi, ở đâu, do cấu trúc nào (so S-matched vs R-derived).
- [ ] Báo cáo có phân tầng tối thiểu theo `cadence_class` (và `meter_type` khi cần); không gộp tất cả meter thành một population duy nhất khi phân tích độ nhạy liên quan tới cadence.
- [ ] Có `p6_decision.md`: quyết định làm hay không làm P6, theo tiêu chí khai báo trước.
- [ ] **Lõi nghiên cứu / MVP hoàn thành tại đây.**

**Checklist audit P4**
- [ ] Không kết luận từ một con số τ tổng duy nhất; luôn có phân phối + CI.
- [ ] Với ~8 phương pháp, τ nhiễu: đã báo cáo mức nhiễu này.
- [ ] Phân tầng tối thiểu theo `cadence_class`; không đánh đồng meter 15s với meter 6min.
- [ ] Tuyệt đối không dùng `raw_record_count` hay `bin_completeness` làm input feature cho bất kỳ baseline/model nào.
- [ ] Bootstrap resample theo đơn vị độc lập (meter/episode), không phải theo điểm.
- [ ] Không "cherry-pick" bin hoặc nhóm meter sau khi đã thấy kết quả.
- [ ] Tiêu chí kích hoạt P6 được commit trước khi thấy kết quả P4 (kiểm tra git history).
- [ ] S-point và S-block được báo cáo riêng, không chỉ bản gộp.
- [ ] Mọi con số trong `p4_findings.md` truy ngược được tới query.
- [ ] Kết quả âm hoặc không có sự khác biệt vẫn được báo cáo trung thực.

---

## P5 — Deep learning (Mở rộng 1, ~1,5 tuần)

**Mục tiêu:** thêm SAITS, BRITS, TimesNet (PyPOTS) trên subset meter, trong ngân sách GPU.

| ID | Task | Đầu vào | Đầu ra | Kiểm thử |
|---|---|---|---|---|
| P5-T1 | Dựng môi trường PyPOTS, chạy smoke test | — | `requirements-dl.txt`, log | Train 1 epoch trên dữ liệu nhỏ không lỗi |
| P5-T2 | Chốt split: theo thời gian **và** theo episode; không outage nào ở cả train và test | clean segments + episodes | `data/processed/dl_split.parquet` | Test giao nhau train/test theo episode ID = rỗng; test ranh giới thời gian |
| P5-T3 | Wrapper 3 model theo interface P3-T2 | PyPOTS | `models/saits.py`, `brits.py`, `timesnet.py` | Output cùng định dạng với baseline |
| P5-T4 | Giới hạn ngân sách: số epoch, số seed (≥3), early stopping dựa trên validation tách riêng | config | `configs/dl.yaml` | Thời gian/VRAM ghi trong `Meta_Run` |
| P5-T5 | Train + đánh giá trên cùng split và cùng mask như baseline | split + mask | `Fact_ImputationResult` (model DL) | So sánh công bằng: cùng meter, cùng mask, cùng metric |
| P5-T6 | Cập nhật phân tích ranking P4 có thêm DL | P4 + T5 | `reports/p5_findings.md` | Chạy lại các query P4 với model mới, không đổi định nghĩa |

**Cổng nghiệm thu P5**
- [ ] Chạy được trong ngân sách GPU, có ≥3 seed.
- [ ] So sánh công bằng cùng split, cùng mask.

**Checklist audit P5**
- [ ] Kiểm tra rò rỉ train/test theo episode và theo thời gian (kể cả qua normalization: scaler fit chỉ trên train).
- [ ] Early stopping/hyperparameter không dùng tập test.
- [ ] Kết quả báo mean ± std qua seed, không chỉ seed tốt nhất.
- [ ] Mask dùng khi train (nếu có) không trùng mask dùng khi test.
- [ ] Baseline P3 được đánh giá lại trên đúng subset meter của DL.

---

## P6 — Selector + downstream forecasting (M4, mở rộng có điều kiện, ~1,5 tuần)

**Chỉ bắt đầu khi P4 đã qua cổng và `reports/p6_decision.md` kết luận "làm".** Nếu kết luận "không làm", ghi lý do vào báo cáo (ranking ổn định thì selector không có động cơ) và chuyển thẳng sang P7.

| ID | Task | Đầu vào | Đầu ra | Kiểm thử |
|---|---|---|---|---|
| P6-T1 | Định nghĩa feature tại thời điểm thiếu (độ dài gap, giờ/ngày, mùa, mức correlated, hierarchy, đặc trưng ngữ cảnh) | mask + data | `analysis/selector_features.py` | Feature chỉ dùng thông tin có sẵn **trước/tại** thời điểm thiếu |
| P6-T2 | Label: model tốt nhất cho từng episode | `Fact_ImputationResult` | bảng label | Mỗi episode có đúng một label (hoặc quy tắc hòa rõ ràng) |
| P6-T3 | Split theo episode và thời gian | — | split file | Giao nhau episode giữa train/test = rỗng |
| P6-T4 | Train selector, so với **best-single** và **oracle** | T1–T3 | kết quả selector | Oracle ≥ selector ≥ chance; best-single được tính trên cùng test |
| P6-T5 | Downstream forecasting: một forecaster cố định, đánh giá trên dữ liệu thực sạch | imputed data | `Fact_ForecastResult` | Forecaster, hyperparameter, split không đổi giữa các chiến lược imputation |
| P6-T6 | Báo cáo trung thực | tất cả | `reports/p6_findings.md` | Nêu rõ nếu selector không vượt best-single ổn định |

**Cổng nghiệm thu P6**
- [ ] `p6_decision.md` kết luận "làm".
- [ ] Selector vượt best-single ổn định, **hoặc** báo cáo trung thực là không.

**Checklist audit P6**
- [ ] Không rò rỉ nhãn qua feature (ví dụ feature dẫn xuất từ lỗi imputation).
- [ ] Chênh lệch forecasting chỉ đến từ chiến lược imputation.
- [ ] Có khoảng tin cậy cho mọi so sánh với best-single.
- [ ] Đã so sánh với oracle để biết trần cải thiện.

---

## P7 — Dashboard + viết (~1,5 tuần)

| ID | Task | Đầu vào | Đầu ra | Kiểm thử |
|---|---|---|---|---|
| P7-T1 | Mô hình OLAP (cube/measure/hierarchy) cho các câu hỏi chính | warehouse | tài liệu OLAP | Measure khớp query P4-T6 |
| P7-T2 | Dashboard Power BI: ranking theo gap length × mức correlated, so 4 nhánh, energy consistency | OLAP | file `.pbix` + ảnh chụp | Con số trên dashboard khớp query SQL (đối chiếu ≥ 10 ô) |
| P7-T3 | Viết báo cáo/paper: dữ liệu, mask, phương pháp, kết quả, giới hạn | reports P1–P6 | bản nháp báo cáo | Mỗi bảng/hình có nguồn là query hoặc script cụ thể |
| P7-T4 | Gói tái lập: README, `run_all.sh`, hướng dẫn chạy lại | repo | README | Người khác chạy lại được MVP từ máy sạch |
| P7-T5 | Chuẩn bị vấn đáp: sổ tay "con số → query → bảng → dòng raw" | tất cả | `reports/viva_cheatsheet.md` | Chọn ngẫu nhiên 10 con số, truy ngược được hết |

**Cổng nghiệm thu P7**
- [ ] Vấn đáp được mọi con số từ warehouse.
- [ ] Dashboard và báo cáo nhất quán với nhau.

**Checklist audit P7**
- [ ] Mọi con số trong báo cáo khớp dashboard và query.
- [ ] Hạn chế và phạm vi (MVP/mở rộng đã làm gì, chưa làm gì) được nêu rõ.
- [ ] Không có khẳng định nào vượt quá bằng chứng.
- [ ] Repo chạy lại được, seed và version dữ liệu ghi đầy đủ.

---

## Phụ lục A — Mẫu prompt giao việc cho agent

```
Bối cảnh: dự án Beyond Synthetic Missingness, giai đoạn <Px>.
Task: <ID> — <mục tiêu 1 câu>.
Đầu vào: <file/bảng>.
Đầu ra yêu cầu: <file/bảng>.
Ràng buộc: không sửa data/raw; không sửa test; không dùng corrected làm ground truth; seed lấy từ config.
Kiểm thử: chạy tests/test_<ID>.py, phải pass. Nếu không pass, báo nguyên nhân, đừng sửa test.
Khi xong: ghi log ngắn (đã làm gì, số liệu chính, điều chưa chắc chắn). Không bắt đầu task khác.
```

## Phụ lục B — Mẫu prompt audit (phiên agent mới, không có bối cảnh code)

```
Bạn là auditor độc lập cho giai đoạn <Px>. Không viết lại code. Chỉ kiểm tra.
1. Đọc cổng nghiệm thu và checklist audit của giai đoạn <Px> trong TASK_PLAN.md.
2. Với mỗi mục: chạy lệnh/query kiểm tra thật, ghi lệnh và kết quả.
3. Đối chiếu số liệu với nguồn raw, không tin báo cáo của agent trước.
4. Xuất audits/AUDIT_<Px>.md gồm: mục pass, mục fail, bằng chứng, mức nghiêm trọng, khuyến nghị.
5. Nếu có bất kỳ mục "quy tắc bất biến" nào fail, kết luận giai đoạn KHÔNG qua cổng.
```

## Phụ lục C — Rủi ro chính

| Rủi ro | Dấu hiệu | Cách giảm |
|---|---|---|
| Kendall τ nhiễu do ít phương pháp | CI rất rộng | Ranking theo từng meter/segment, báo phân phối + CI |
| Rò rỉ train/test | Kết quả DL tốt bất thường | Split theo episode + thời gian, test giao nhau |
| Ngữ cảnh tải lệch khi replay mask | R-derived khác biệt do loại ngày, không do cấu trúc | Quy tắc ghép theo loại ngày/khung giờ/mùa |
| Agent flash báo cáo sai | "Xong" nhưng test không chạy | Assert tự động bắt buộc, audit bằng phiên riêng |
| Hết thời gian | P5–P6 kéo dài | Đóng góp chính khép lại ở P4; P6 chỉ chạy khi P4-T8 cho phép; P7 luôn giữ chỗ |
