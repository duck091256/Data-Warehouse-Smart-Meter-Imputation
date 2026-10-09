# INDEPENDENT AUDIT REPORT: PROTOCOL v1.1 OFFICIALIZATION
# Beyond Synthetic Missingness — Smart-Meter Imputation

> **Dự án**: Beyond Synthetic Missingness — Smart-Meter Imputation  
> **Mã Tài Liệu Kiểm Toán**: `audits/AUDIT_PROTOCOL_V1_1.md`  
> **Vai trò kiểm toán**: Independent Protocol Auditor (Phiên làm việc độc lập chuyên trách kiểm toán Protocol)  
> **Đối tượng kiểm toán**: Nghiên cứu & Đặc tả Protocol v1.1 (sau khi officialize)  
> **Thời điểm kiểm toán**: 2026-10-07T00:35:00+07:00 (UTC 2026-10-06 17:35:00Z)  
> **Tài liệu kiểm toán đối chiếu**:  
> - `TASK_PLAN.md` (SHA-256: `81cfbc3dba93574c6721c63d5974fa97bd6655d80b8f99dc1af365fd33b243fa`)  
> - `RESEARCH_PLAN.md` (SHA-256: `73da22372c587c72a1e546e1584f734502d1dbd7d04756cad6ba7f1e0027ba93`)  
> - `control/protected_paths.txt` (SHA-256: `4ee91e66cab2e9d6e93977a3e5685e849674a11e879bdd9f690afbc7d6fdc7bb`)  
> - `configs/default.yaml`  
> - `configs/local.yaml`  
> - `reports/protocol_v1_1_amendment.md`  
> - `reports/p1_t3_protocol_amendment_v1_1.md`  
> - `reports/p1_t3_protocol_preflight.md`  
> - `AGENTS.md`, `AUDITOR.md`, `EXECUTOR.md`  
> - `control/task_state.yaml`  
> - `data/interim/readings_utc.parquet` (208,224,479 dòng, 79 meters)  
> **Kết luận kiểm toán**: **PASS WITH NOTES**  
> **Trạng thái cổng (Gate Status)**: **PROTOCOL v1.1 IS SCIENTIFICALLY SOUND & READY FOR P1-T3 IMPLEMENTATION**

---

## 1. Executive Summary & Verdict

Phiên kiểm toán độc lập này được thực hiện nhằm thẩm tra toàn diện **Protocol v1.1** sau khi được phê duyệt chính thức bởi Protocol Owner. Đây là một cuộc **kiểm toán giao thức nghiên cứu (Protocol Audit)** độc lập, không phải kiểm toán mã nguồn thực thi (Implementation Audit).

### 1.1 Tóm tắt kết quả kiểm tra
1. **Tính nhất quán của Protocol (Protocol Consistency)**:
   - Toàn bộ các định nghĩa cốt lõi của Protocol v1.1 giữa `TASK_PLAN.md`, `RESEARCH_PLAN.md`, `reports/protocol_v1_1_amendment.md`, và `configs/default.yaml` đạt **nhất quán 100%**. Không phát hiện bất kỳ mâu thuẫn hay xung đột logic nào giữa các tài liệu đặc tả nghiên cứu.
2. **Toán học của Lưới 15 Phút (Grid Mathematics)**:
   - Các công thức:
     $$\text{grid\_start}(m) = \text{ceil\_to\_15min}(\min(\text{source\_timestamp\_utc}(m)))$$
     $$\text{grid\_end}(m) = \text{ceil\_to\_15min}(\max(\text{source\_timestamp\_utc}(m)))$$
     $$\text{Bin}(t) = (t - 15\text{min}, t]$$
     được xác nhận là **chính xác toán học tuyệt đối**. Quy tắc nửa đóng biên phải ngăn ngừa triệt để hiện tượng mất mát dữ liệu biên (boundary dropping), đặc biệt giải quyết chính xác trường hợp quan sát lẻ giây/phút (ví dụ $12:07 \to 12:15$).
3. **Bảo toàn Ô có Dữ liệu & Zero Synthetic Observations**:
   - Invariant mới $\text{count}(\text{non\_nan\_15min}(m)) == \text{count}(\text{raw\_occupied\_bins}(m))$ hoàn toàn khả thi về mặt số học và khắc phục triệt để nghịch lý toán học của Protocol v1.0 ($\text{non\_nan\_after} == \text{non\_nan\_before}$).
   - Mọi giá trị non-NaN trên lưới được truy nguyên $100\%$ về quan sát vật lý thô thông qua toán tử tất định **`LAST`**, bảo đảm **Zero Synthetic Observations**.
4. **Quy tắc Hợp lệ Quần thể Cốt lõi (General Core Eligibility Rule)**:
   - Tiêu chí 4 điều kiện ($\text{history} \ge 365\text{d}$, $\text{median gap} \le 900\text{s}$, $\text{occupied rate} \ge 50\%$, $\text{semantics} = \text{'W'}$) mang tính khách quan, áp dụng đối xứng cho toàn bộ 79 meters.
   - Đồng hồ `H1.ZE20` được bảo toàn hợp lệ trong Quần thể Cốt lõi (396.61 ngày lịch sử $\ge 365$, cadence thực tế 30.0s). Ràng buộc phân chia thời gian (temporal split constraint) downstream được thiết lập rõ ràng nhằm tránh rò rỉ hoặc gán ép dữ liệu trước ngày lắp đặt (2022-11-30).
5. **Chống Rò Rỉ Tính Năng (Anti-Leakage Mandate)**:
   - Quy tắc cấm tuyệt đối đưa `raw_record_count`, `expected_record_count`, và `bin_completeness` vào feature đầu vào của các mô hình imputation được ghi nhận nghiêm ngặt và đồng bộ ở toàn bộ các tài liệu nghiên cứu.
6. **Kiểm tra Toàn vẹn Quản trị (Governance & Control Gate)**:
   - Kiểm tra hash SHA-256 qua `control/protocol_hash.sh --verify`: **PASS**.
   - Kiểm tra máy trạng thái qua `control/validate_state.py`: **PASS**.
   - Kiểm tra tổng thể qua `control/gate.sh`: **PASS** (100% tests pass, scope OK, protected paths nguyên vẹn).
   - Dữ liệu thô `data/raw/` được bảo vệ nguyên vẹn 100%.

### 1.2 Kết luận kiểm toán: PASS WITH NOTES
Kiểm toán viên xác nhận Protocol v1.1 **ĐẠT TIÊU CHUẨN NGHIÊN CỨU KHOA HỌC (PASS)** để chuyển giao cho Executor Agent bắt đầu triển khai nhiệm vụ P1-T3.

Ghi chú kỹ thuật (Notes) cần lưu ý trước khi code P1-T3:
- **Ghi chú 1 (Cấu hình cục bộ máy dev)**: `configs/local.yaml` hiện đang khai báo `protocol_version: "v1"` và chưa chứa các khóa cấu hình mới của lưới P1-T3 (`etl.grid`, `cadence_classification`). Do cơ chế nạp cấu hình ưu tiên `configs/local.yaml` mà không deep-merge với `configs/default.yaml`, Executor khi viết code P1-T3 cần bảo đảm cơ chế nạp cấu hình fallback/merge về `configs/default.yaml` hoặc đồng bộ các khóa này trong file local.
- **Ghi chú 2 (Lịch sử Git)**: Thư mục repo chưa có commit git nào (`uncommitted_initial`). Tính toàn vẹn của protocol hiện đang được bảo vệ tuyệt đối bằng cơ chế băm SHA-256 (`control/protocol_hashes.txt`) và script cổng kiểm soát. Khi người dùng cho phép, repo có thể được commit để ghi nhận mốc Protocol v1.1.

---

## 2. Bảng Checklist Kiểm Toán Tổng Hợp (Audit Matrix)

| STT | Chiều Kiểm Toán / Tiêu Chí | Phương Pháp Kiểm Chứng | Kết Quả Thực Tế | Trạng Thái | Mức Độ |
|:---:|---|---|---|:---:|:---:|
| **1** | **Target Variable = W** | Đối chiếu `TASK_PLAN`, `RESEARCH_PLAN`, `configs/default.yaml`, `configs/local.yaml`, `readings_utc_metadata.json` | 100% tài liệu thống nhất target duy nhất là $W$ (Net Active Energy Saldo, kWh). | **PASS** | CRITICAL |
| **2** | **79-Meter Core Population** | Đối chiếu danh sách meter và số lượng meter trong toàn bộ báo cáo và kế hoạch | Cả 79 meters W đều được giữ trong Core Population; không loại trừ bất kỳ meter nào. | **PASS** | CRITICAL |
| **3** | **Vị trí của H1.ZE20** | Kiểm tra thông số thực nghiệm và điều kiện giữ lại trong Core | `H1.ZE20` đạt 396.61 ngày lịch sử ($\ge 365$), median gap 30.0s, occupied rate 73.49%. Giữ trong Core. | **PASS** | CRITICAL |
| **4** | **General Eligibility Rule** | Đối chiếu công thức 4 điều kiện giữa các văn bản | Khớp 100% từng ký tự công thức giữa `TASK_PLAN`, `RESEARCH_PLAN`, `default.yaml`. | **PASS** | HIGH |
| **5** | **Disclosure về Eligibility** | Tìm kiếm câu tuyên bố giới hạn (Scope Disclosure Note) | Đầy đủ trong `TASK_PLAN`, `RESEARCH_PLAN`, `protocol_v1_1_amendment.md`, `default.yaml`. | **PASS** | MEDIUM |
| **6** | **Toán học của Lưới 15 Phút** | Phân tích toán học $\text{grid\_start}$, $\text{grid\_end}$, $\text{Bin}(t)$ và trường hợp biên lẻ giây/phút | Công thức $(t-15\text{m}, t]$ với `ceil_to_15min` cho cả hai đầu biên; không làm rơi rớt bất kỳ raw observation nào. | **PASS** | CRITICAL |
| **7** | **Occupied Bin Preservation** | Đối chiếu định nghĩa invariant mới và kiểm tra tính tương thích số học | $\text{non\_nan\_15min} == \text{occupied raw bins}$ thay thế hoàn toàn invariant cũ; không xung đột. | **PASS** | CRITICAL |
| **8** | **Toán tử LAST Semantics** | Kiểm tra định nghĩa $\arg\max(ts)$ và danh mục cấm (`mean`, `sum`, `interp`) | Định nghĩa chặt chẽ; cấm hoàn toàn các toán tử biến đổi giá trị; bảo toàn IEEE-754 gốc. | **PASS** | CRITICAL |
| **9** | **Phân biệt Timestamps** | Kiểm tra tách biệt `grid_timestamp_utc` và `source_timestamp_utc` | Schema và tài liệu phân định rạch ròi giữa mốc neo lưới và mốc đo vật lý thật. | **PASS** | HIGH |
| **10** | **Zero Synthetic Observations** | Xác nhận tính truy nguyên $100\%$ về tuple 4 thành phần trong `readings_utc` | Mỗi giá trị non-NaN có `source_timestamp_utc`, `raw_source_file`, `raw_record_count` $\ge 1$. | **PASS** | CRITICAL |
| **11** | **Ngữ nghĩa Empty Bin** | Xác nhận ô rỗng mang `NaN` và phân biệt với lỗi thiết bị (equipment failure) | Ô rỗng mang `NaN`; khẳng định rõ ô rỗng là observation gap, không tự động là failure. | **PASS** | HIGH |
| **12** | **Quản trị Cadence Classes** | Kiểm tra ngưỡng phân lớp (`C15S` đến `SPARSE_GT15M`) và cách tính từ median gap | Các ngưỡng tất định 100%; tính từ median positive gap; cấm dùng max gap phân lớp. | **PASS** | HIGH |
| **13** | **Cadence Non-Stationarity** | Kiểm tra định nghĩa tính không dừng theo tháng lịch | Cửa sổ `calendar month`; không làm đổi nhịp baseline; ghi nhận đầy đủ. | **PASS** | MEDIUM |
| **14** | **Độ đầy đủ Bin Completeness** | Kiểm tra công thức cho ô chuẩn và ô biên; vai trò descriptive | Công thức $\min(1.0, \text{observed} / \text{expected})$; lưu cả 2 biến đếm; không dùng điền khuyết. | **PASS** | MEDIUM |
| **15** | **Anti-Leakage Mandate** | Kiểm tra lệnh cấm đưa `raw_record_count`, `bin_completeness` vào model | Quy định cấm tuyệt đối xuất hiện đồng bộ ở mọi tài liệu liên quan (`TASK_PLAN`, `RESEARCH_PLAN`). | **PASS** | CRITICAL |
| **16** | **Ràng buộc Temporal Downstream** | Kiểm tra quy định split thời gian đối với `H1.ZE20` | Quy định cấm ép `H1.ZE20` vào khoảng thời gian trước 2022-11-30 đồng bộ trong các tài liệu. | **PASS** | HIGH |
| **17** | **Đính chính độ phủ HVAC** | Kiểm tra luận điểm HVAC và tải nhiệt đa nguồn | Đã đính chính: 70 đồng hồ điện đo tải điện HVAC; giữ meter $K, W$ là để đa dạng tải nhiệt đa nguồn. | **PASS** | MEDIUM |
| **18** | **Phân loại Meter Type** | Kiểm tra danh mục và nguyên tắc xác định nguồn gốc | 6 nhóm chuẩn hóa; quy định rõ suy diễn từ tên phải ghi rõ rule/confidence, không coi là fact. | **PASS** | MEDIUM |
| **19** | **Đối soát Dữ liệu (Reconciliation)**| Kiểm tra phương trình cân bằng 61,790 dòng trùng lặp | $208,286,269 = 208,224,479 + 61,790$ ghi nhận nhất quán trong toàn bộ tài liệu và metadata. | **PASS** | HIGH |
| **20** | **Truy vết Lịch sử Protocol** | Kiểm tra tính bảo toàn của v1.0 và tính kế thừa của v1.1 amendment | Bảng lịch sử ghi rõ v1.0 đã superseded; căn cứ sửa đổi khớp hoàn toàn với preflight evidence. | **PASS** | HIGH |
| **21** | **Bảo vệ Dữ liệu Thô** | Kiểm tra quyền truy cập và tính bất biến của `data/raw/` | `data/raw/` được bảo vệ nghiêm ngặt qua `protected_paths.txt` và `AGENTS.md`. | **PASS** | CRITICAL |
| **22** | **Protocol Hash Verification** | Chạy `bash control/protocol_hash.sh --verify` | Khớp 100% hash SHA-256 của `TASK_PLAN.md`, `RESEARCH_PLAN.md`, `protected_paths.txt`. | **PASS** | CRITICAL |
| **23** | **State Machine Integrity** | Chạy `python3 control/validate_state.py` | Trạng thái máy hợp lệ (`P1-T2: GATED`, `P1-T3: READY`); không có nhảy cóc. | **PASS** | CRITICAL |
| **24** | **Control Gate Enforcement** | Chạy `bash control/gate.sh` | Toàn bộ 5 bước kiểm soát đều PASS; control tests 7/7 passed. | **PASS** | CRITICAL |
| **25** | **Đồng bộ Cấu hình Cục bộ** | So sánh `configs/local.yaml` và `configs/default.yaml` | `configs/local.yaml` còn mang `v1` và thiếu các khóa grid mới của v1.1. | **NOTE** | MEDIUM |

---

## 3. Đánh Giá Chi Tiết Từng Chiều Kiểm Toán (Detailed Audit Findings)

### Chiều 1: Toán học của Lưới 15 Phút (Grid Mathematics & Boundary Verification)
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1e, Mục P1-T3), `RESEARCH_PLAN.md` (Mục 5), `reports/protocol_v1_1_amendment.md` (Mục 5), `configs/default.yaml` (Mục etl.grid).
- **Công thức đặc tả**:
  $$\text{grid\_start}(m) = \text{ceil\_to\_15min}(\min(\text{source\_timestamp\_utc}(m)))$$
  $$\text{grid\_end}(m) = \text{ceil\_to\_15min}(\max(\text{source\_timestamp\_utc}(m)))$$
  $$\text{Bin}(t) = (t - 15\text{min}, t] \quad (\text{Right-closed, right-labeled})$$
- **Kiểm tra toán học & Xử lý biên (Boundary Proof)**:
  1. *Trường hợp quan sát rơi đúng mốc neo tròn*: Ví dụ $ts = 12:00:00.000000$.
     - $\text{ceil\_to\_15min}(12:00:00) = 12:00:00$.
     - Ô thời gian tương ứng là $(11:45:00, 12:00:00]$, hoàn toàn chứa điểm $12:00:00$.
  2. *Trường hợp quan sát lệch giây ngay sau mốc neo*: Ví dụ $ts = 12:00:01.000000$.
     - $\text{ceil\_to\_15min}(12:00:01) = 12:15:00$.
     - Ô thời gian tương ứng là $(12:00:00, 12:15:00]$, hoàn toàn chứa điểm $12:00:01$.
  3. *Trường hợp quan sát cuối cùng của meter là phút lẻ*: Ví dụ $ts_{\max} = 12:07:00$.
     - Dưới phân vùng nửa đóng bên phải, quan sát $12:07$ thuộc về khoảng $(12:00, 12:15]$.
     - Ô đại diện bắt buộc phải là ô gắn nhãn $12:15:00$.
     - Nếu áp dụng `floor_to_15min` cho `grid_end`, lưới sẽ kết thúc tại $12:00:00$, khiến ô $12:15$ không tồn tại và quan sát $12:07$ bị vứt bỏ (boundary drop).
     - Quy tắc $\text{grid\_end} = \text{ceil\_to\_15min}(12:07) = 12:15$ bảo đảm ô $12:15$ được khởi tạo và chứa trọn vẹn điểm $12:07$.
  4. *Chứng minh không có quan sát thô nào bị bỏ sót (Completeness Theorem)*:
     Với mọi $ts_i \in [\min(ts), \max(ts)]$:
     $$\min(ts) \le ts_i \le \max(ts) \implies \text{ceil}(ts_{\min}) \le \text{ceil}(ts_i) \le \text{ceil}(ts_{\max})$$
     $$\implies \text{grid\_start} \le \text{ceil}(ts_i) \le \text{grid\_end}$$
     Do đó, mọi quan sát thô đều rơi vào một ô duy nhất nằm hoàn toàn trong dải lưới $[\text{grid\_start}, \text{grid\_end}]$.
- **Kết luận**: **PASS**. Định nghĩa toán học hoàn toàn chính xác, nhất quán và miễn nhiễm với việc mất mát dữ liệu biên.

---

### Chiều 2: Bảo Toàn Ô Có Dữ Liệu (Occupied Bin Preservation) & Zero Synthetic Observations
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1e, 0.6, P1-T3), `RESEARCH_PLAN.md` (Mục 5.4), `reports/protocol_v1_1_amendment.md` (Mục 5.6, 5.7).
- **Đặc tả Invariant**:
  $$\text{count}(\text{non\_nan\_15min}(m)) = \text{count}(\text{raw\_occupied\_bins}(m)) \quad \forall m \in [1, 79]$$
- **Phân tích đối chứng với Protocol v1.0**:
  - *Quy tắc v1.0*: Đòi hỏi $\text{non\_nan\_after} == \text{non\_nan\_before}$. Do dữ liệu thô có $208,224,479$ dòng trên nhịp 15s/30s/60s/360s, trong khi lưới 15 phút 6 năm chỉ có tối đa $\sim 13.98$ triệu ô thời gian cho 79 meters, quy tắc v1.0 là một mâu thuẫn toán học không thể vượt qua.
  - *Quy tắc v1.1*: Mỗi ô 15 phút chứa ít nhất 1 quan sát thô $(\ge 1)$ sẽ sinh ra đúng 1 giá trị đại diện non-NaN. Ô không chứa quan sát thô nào $(= 0)$ sẽ nhận giá trị `NaN`.
  - Tổng số ô non-NaN trên lưới bằng chính xác số lượng ô thời gian có dữ liệu thô (thực nghiệm đo đạc trong preflight là $13,333,577$ occupied bins).
- **Đặc tả Zero Synthetic Observations**:
  - Giá trị tại ô occupied là bản ghi thô IEEE-754 nguyên bản của quan sát có `source_timestamp_utc` lớn nhất trong bin (toán tử `LAST`).
  - Mọi bản ghi non-NaN đầu ra có thể truy ngược $100\%$ về một tuple:
    $$(\text{meter\_id}, \text{source\_timestamp\_utc}, \text{raw\_source\_file}, \text{value})$$
    có mặt trong bảng `readings_utc.parquet`.
  - Nghiêm cấm hoàn toàn các toán tử tính toán giá trị mới: `mean`, `sum`, `nearest`, `ffill`, `bfill`, `interpolation`, `smoothing`.
- **Kết luận**: **PASS**. Invariant mới khả thi về mặt số học, bảo toàn trọn vẹn bản chất vật lý của dữ liệu và triệt tiêu nguy cơ sinh dữ liệu giả tạo.

---

### Chiều 3: Tách Biệt Ngữ Nghĩa Timestamps và Toán Tử LAST
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1e điều 5, bảng DDL Fact_Reading), `RESEARCH_PLAN.md` (Mục 5.2, 5.5).
- **Cấu trúc trường thời gian trong schema `readings_15min`**:
  ```text
  grid_timestamp_utc   : Mốc neo biên phải chuẩn hóa của ô 15 phút (HH:00, :15, :30, :45)
  timestamp_local      : Giờ địa phương Đức (Europe/Berlin) tại grid_timestamp_utc
  source_timestamp_utc : Mốc thời gian UTC thực tế của quan sát thô được chọn (NULL nếu ô rỗng)
  value                : Giá trị đo thô tại source_timestamp_utc (NaN nếu ô rỗng)
  raw_source_file      : Tên tệp raw chứa quan sát được chọn (NULL nếu ô rỗng)
  raw_record_count     : Số lượng bản ghi raw rơi vào ô thời gian này (>=1 nếu occupied, 0 nếu rỗng)
  ```
- **Kiểm tra phân định ngữ nghĩa**:
  - Không có bất kỳ dòng văn bản nào đánh đồng `grid_timestamp_utc` là mốc đo của cảm biến.
  - Cặp `(grid_timestamp_utc, value)` được định nghĩa tường minh là một **biểu diễn chuẩn hóa trên lưới (Standardized Grid Representation)**.
  - Cặp `(source_timestamp_utc, value)` mới là **quan sát vật lý thực sự (True Physical Observation)**.
  - Khi ô rỗng (`raw_record_count == 0`), `source_timestamp_utc` nhận giá trị `NULL`, thể hiện rõ ràng không có quan sát vật lý nào được gán cho ô này.
- **Kết luận**: **PASS**. Ngữ nghĩa rõ ràng, minh bạch, loại bỏ hoàn toàn sự mập mờ giữa thời gian chuẩn hóa và thời gian đo thực.

---

### Chiều 4: Quản Trị Nhịp Điệu (Cadence Governance) & Chống Rò Rỉ Tính Năng
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1d, 0.6), `RESEARCH_PLAN.md` (Mục 4.3, 4.4, 4.6), `configs/default.yaml` (Mục cadence_classification, feature_governance).
- **Kiểm tra tính tất định của ngưỡng Cadence Class**:
  - Chỉ số phân lớp: **Trung vị khoảng cách quan sát dương** ($\text{median}(\Delta t_i)$ với $\Delta t_i > 0$ sau P1-T2 deduplication).
  - Thang phân lớp:
    - $\le 22.5\text{ s} \implies \text{C15S}$ (1 meter: `V.Z84`, median 18.0s)
    - $> 22.5\text{ s} - 45.0\text{ s} \implies \text{C30S}$ (25 meters, bao gồm `H1.ZE20`, median 30.0s)
    - $> 45.0\text{ s} - 90.0\text{ s} \implies \text{C1M}$ (44 meters, median 60.0s)
    - $> 90.0\text{ s} - 180.0\text{ s} \implies \text{C2M}$ (1 meter: `H1.W12`, median 120.0s)
    - $> 180.0\text{ s} - 540.0\text{ s} \implies \text{C6M}$ (8 meters: `K11..K16, W11, K21`, median 360.0s)
    - $> 540.0\text{ s} - 900.0\text{ s} \implies \text{C10M\_PLUS}$ (0 meters)
    - $> 900.0\text{ s} \implies \text{SPARSE\_GT15M}$ (0 meters)
  - *Loại trừ Max Gap khỏi phân lớp*: Protocol quy định rõ ràng **không dùng max gap làm bộ phân lớp cadence**, bởi max gap phản ánh độ dài sự cố/mất điện (outage/downtime), không phản ánh tần suất lấy mẫu kỹ thuật của cảm biến.
- **Tính không dừng của nhịp điệu (`cadence_nonstationary`)**:
  - Được tính toán trên các cửa sổ tháng lịch không chồng lấn (`calendar month`). Nếu nhịp của bất kỳ tháng nào lệch khỏi baseline toàn lịch sử, cờ `cadence_nonstationary = true` được kích hoạt. Lớp baseline toàn lịch sử vẫn được bảo toàn làm mốc tham chiếu cố định.
- **Kiểm tra quy định Chống Rò Rỉ Tính Năng (Anti-Leakage Mandate)**:
  - Cả `TASK_PLAN.md` (Mục 0.1d điều 6, Mục 0.6, Mục P4 Checklist) và `RESEARCH_PLAN.md` (Mục 4.6) đều cấm nghiêm ngặt:
    > **NGHIÊM CẤM**: `raw_record_count`, `expected_record_count`, và `bin_completeness` CẤM TUYỆT ĐỐI đưa vào input feature của bất kỳ mô hình imputation nào (P3, P5, P6).
  - *Lý giải khoa học*: Trong một ô bị đánh mask nhân tạo, nếu mô hình biết được `raw_record_count > 0` hoặc `bin_completeness = 1.0`, mô hình sẽ trực tiếp "nhìn thấy" sự hiện diện của dữ liệu thật dưới mask, phá hủy tính công bằng của benchmark.
- **Kết luận**: **PASS**. Hệ thống quản trị nhịp điệu chặt chẽ, khoa học, và có hàng rào chống rò rỉ dữ liệu kiên cố.

---

### Chiều 5: Quy Tắc Hợp Lệ Tổng Quát (General Eligibility Rule) & Quần Thể Cốt Lõi
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1c), `RESEARCH_PLAN.md` (Mục 3.1–3.4), `configs/default.yaml` (Mục core_population).
- **Đặc tả Quy tắc**:
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
- **Kiểm tra tính đối xứng và không thiên vị (Symmetric & Outcome-Independent)**:
  - Quy tắc được áp dụng đồng nhất cho mọi meter, không có ngoại lệ riêng cho bất kỳ trạm đo nào.
  - Không chứa bất kỳ tiêu chí nào dựa trên kết quả chạy mô hình (performance-driven), độ lỗi dự báo (error metrics), hoặc số lượng sự cố phát hiện được.
- **Xác minh vị trí của Meter `H1.ZE20`**:
  - Dữ liệu thô của `H1.ZE20` bắt đầu từ 2022-11-30 đến 2023-12-31, tổng cộng **396.61 ngày** (~13 tháng).
  - $396.61 \ge 365$ ngày $\implies$ Thỏa mãn điều kiện lịch sử.
  - Trung vị khoảng cách là **30.00 giây** $\le 900$ giây $\implies$ Thỏa mãn cadence.
  - Tỷ lệ chiếm dụng là **73.49%** $\ge 50.0\%$ $\implies$ Thỏa mãn độ phủ.
  - Biến đo là $W$ (Net Active Energy Saldo, kWh) $\implies$ Thỏa mãn ngữ nghĩa.
  - Do đó, `H1.ZE20` được giữ lại hoàn toàn chính đáng trong Core Population.
- **Ràng buộc phân chia thời gian downstream (Temporal Split Constraint)**:
  - Do `H1.ZE20` chỉ vận hành từ 2022-11-30, Protocol quy định rõ: các phân chia tập train/test theo thời gian (P3, P5, P6) phải xác minh sự hiện diện của meter trong khoảng split; tuyệt đối không đưa `H1.ZE20` vào đánh giá tại các mốc thời gian trước ngày lắp đặt.
- **Công bố giới hạn phương pháp (Scope Disclosure Note)**:
  - Câu tuyên bố chuẩn mực:
    > *"Thresholds 365 days / 900 seconds / 50% were specified after inspecting the observed dataset, but before any model training, imputation result, ranking analysis, or performance-based selection. Since all 79 meters satisfy the rule, the rule does not act as an outcome-driven exclusion criterion in the current population. This fact must be disclosed explicitly as a limitation / scope note."*
    xuất hiện nguyên văn và đồng bộ trong `TASK_PLAN.md`, `RESEARCH_PLAN.md`, `protocol_v1_1_amendment.md`, và `configs/default.yaml`.
- **Kết luận**: **PASS**. Quy tắc tổng quát hợp lý, khách quan, và có đầy đủ tuyên bố giới hạn khoa học.

---

### Chiều 6: Tính Nhất Quán Về Phạm Vi Nghiên Cứu & Đối Soát Dữ Liệu
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1c, 0.1e), `reports/p1_t2_reconciliation.md`, `data/interim/readings_utc_metadata.json`.
- **Phạm vi Biến Mục Tiêu**:
  - Nghiên cứu chỉ tập trung chuẩn hóa biến $W$ (Active Energy, kWh). Biến công suất tác dụng $P$ và 38 biến phụ tải khác được ghi nhận chính thức là chưa ETL và dành cho các mở rộng tương lai.
  - Khóa duy nhất toàn hệ thống được xác lập là:
    $$\text{Uniqueness Key} = (\text{meter\_id}, \text{variable}, \text{timestamp\_utc})$$
  - Không còn tồn tại bất kỳ lập luận sai lệch nào cho rằng việc có nhiều biến đo lường trong cùng một trạm gây ra trùng lặp timestamp trên biến $W$.
- **Phương trình Cân bằng Số học (Reconciliation Balance)**:
  $$\text{Raw } W \text{ Records (208,286,269)} = \text{Deduplicated } W \text{ (208,224,479)} + \text{V.Z84 Duplicates (61,790)}$$
  - Toàn bộ $61,790$ bản ghi lặp được cô lập chính xác tại tệp `V.Z84.W_raw.csv.gz` vào ngày 2023-05-15 do reconnect modem, đã được xử lý bằng chiến lược `keep_last`.
  - Con số $208,224,479$ dòng đã được kiểm chứng khớp bit-for-bit với số dòng thực tế trong tệp Parquet trung gian `data/interim/readings_utc.parquet` (xác nhận qua metadata Parquet: 208,224,479 rows, 253 row groups).
- **Kết luận**: **PASS**. Số liệu cân bằng tuyệt đối, không có sai số hoặc độ lệch ẩn.

---

### Chiều 7: Phân Biệt Giữa Empty Bin và Sự Cố Thiết Bị
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1e điều 6), `RESEARCH_PLAN.md` (Mục 5.3), `reports/protocol_v1_1_amendment.md` (Mục 5.5).
- **Đặc tả Ngữ nghĩa**:
  $$\text{Empty 15-Minute Bin } \ne \text{ Automatic Equipment Failure}$$
  - Một ô 15 phút bị rỗng sau bước resampling đại diện cho một **khoảng gián đoạn quan sát (observation gap)** trên lưới chuẩn hóa.
  - Nó không tự động được định nghĩa là sự cố thiết bị (equipment failure episode).
  - Ngữ nghĩa sự cố (failure semantics) chỉ được xác lập tại các bước tiếp theo (P1-T4 và P2) thông qua việc đối soát với các nhật ký sự cố có thẩm quyền (`issues/automatic_issues/*.yaml` và `issues/manual_issues/*.yaml`) cùng các cờ chất lượng (`flag_flatline`, `flag_spike`, v.v.).
- **Ý nghĩa phương pháp luận**:
  - Ngăn ngừa tình trạng nhầm lẫn các khoảng mất tín hiệu ngắn, đợt bảo trì hệ thống hoặc cảm biến ngắt kết nối tạm thời thành các sự cố hỏng hóc vật lý nặng nề của đồng hồ.
- **Kết luận**: **PASS**. Sự phân định tường minh và có tính kỷ luật cao.

---

### Chiều 8: Phân Loại Meter Type và Nguồn Gốc Metadata
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Mục 0.1d điều 2), `RESEARCH_PLAN.md` (Mục 4.2), `configs/default.yaml` (Mục meter_metadata).
- **Danh mục chuẩn hóa**:
  `electrical_load`, `electrical_generation/PV`, `thermal_cooling`, `thermal_heating`, `other`, `unknown`.
- **Nguyên tắc xác định**:
  - Bắt buộc phải dựa trên chứng cứ kỹ thuật từ tài liệu nguồn của Honda Research Institute nếu có.
  - Nếu suy diễn từ quy ước đặt tên (ví dụ tiền tố `K` = Kälte/lạnh, `W` = Wärme/nhiệt, `ZE` = Einspeisung/phát điện), hệ thống bắt buộc phải ghi rõ:
    1. Đây là metadata phái sinh (derived metadata), không được trình bày như sự thật từ nguồn (source fact).
    2. Quy tắc suy diễn và mức độ tin cậy tương ứng.
- **Đính chính khẳng định về độ phủ hệ thống HVAC**:
  - Protocol v1.1 đã loại bỏ hoàn toàn câu nhận định thiếu căn cứ *"loại 9 meter tần suất thấp sẽ làm mất toàn bộ hệ thống HVAC"*.
  - Protocol khẳng định chính xác: Toàn bộ phụ tải điện của hệ HVAC (máy nén Chiller, quạt AHU, bơm tuần hoàn) được đo đạc bởi 70 công tơ điện (`Z`, `ZE`, `H*.T.Z`), và meter nhiệt sưởi `H1.W12` hoạt động 6 năm không nằm trong nhóm 9 meter này. Việc giữ các đồng hồ nhiệt nước (`K`, `W`) là nhằm **bảo tồn tính đa dạng tải nhiệt/điện đa nguồn (multi-carrier energy diversity)**.
- **Kết luận**: **PASS**. Tiếp cận khoa học, khách quan và loại bỏ ngụy biện.

---

### Chiều 9: Lịch Sử Protocol & Khả Năng Truy Vết (Protocol History Traceability)
- **Tài liệu đối chiếu**: `TASK_PLAN.md` (Bảng Lịch sử sửa đổi Protocol), `RESEARCH_PLAN.md` (Mục 2), `reports/protocol_v1_1_amendment.md`, `reports/p1_t3_protocol_amendment_v1_1.md`.
- **Kiểm tra tính toàn vẹn lịch sử**:
  - Protocol v1.0 được lưu giữ nguyên trạng với ghi chú rõ ràng là phiên bản tiền nhiệm đã bị thay thế (`Superseded`).
  - Toàn bộ lý do điều chỉnh từ v1.0 sang v1.1 đều có căn cứ thực nghiệm đầy đủ trong các báo cáo tiền trạm (`p1_t3_protocol_preflight.md` và `p1_t3_protocol_amendment_v1_1.md`).
  - Không có hành vi xóa vết, ghi đè trái phép hoặc che giấu các giả định ban đầu.
- **Kiểm tra Git History**:
  - Lệnh `git status` xác nhận repo hiện tại chưa tạo git commit nào (`uncommitted_initial`).
  - Điều này hoàn toàn phù hợp với quy tắc bất biến số 7 trong `EXECUTOR.md`: *"Tự commit git: Không tự ý chạy git commit trừ khi người dùng yêu cầu trực tiếp"*.
  - Tính toàn vẹn và dấu vết thay đổi của protocol được bảo đảm tuyệt đối qua cơ chế băm SHA-256 (`control/protocol_hashes.txt`).
- **Kết luận**: **PASS**. Dấu vết quản trị và lịch sử sửa đổi minh bạch 100%.

---

### Chiều 10: Kiểm Hóa Băm Protocol & Cổng Kiểm Soát (Protocol Hash & Gate Verification)
- **Kiểm tra thực thi độc lập**:
  ```bash
  $ bash control/protocol_hash.sh --verify
  Verifying protocol integrity against manifest...
  [OK] control/protected_paths.txt matches (4ee91e66cab2...)
  [OK] RESEARCH_PLAN.md matches (73da22372c58...)
  [OK] TASK_PLAN.md matches (81cfbc3dba93...)
  Protocol verification PASSED: All protocol files are intact.
  ```
  ```bash
  $ python3 control/validate_state.py
  [OK] Task state 'control/task_state.yaml' is valid.
  ```
  ```bash
  $ bash control/gate.sh
  ============================================================
   Starting Research Control Gate Check
  [1/5] Validating repository structure... -> Repository structure check OK.
  [2/5] Checking scope against protected paths... -> Scope check OK.
  [3/5] Verifying protocol file hashes... -> Protocol integrity OK.
  [4/5] Validating task state machine... -> Task state machine OK.
  [5/5] Running control-layer test suite...
  ....... [100%] 7 passed in 0.13s -> Control-layer tests OK.
  RESULT: GATE = PASS
  ============================================================
  ```
- **Xác nhận**: Toàn bộ các hash SHA-256 trong `control/protocol_hashes.txt` khớp chính xác với nội dung thực tế của `TASK_PLAN.md`, `RESEARCH_PLAN.md`, và `control/protected_paths.txt`.
- **Kết luận**: **PASS**. Hệ thống kiểm soát cổng hoạt động hoàn hảo.

---

### Chiều 11: Trạng Thái Máy Trạng Thái (Task State Machine Integrity)
- **Tài liệu đối chiếu**: `control/task_state.yaml`.
- **Hiện trạng ghi nhận**:
  ```yaml
  protocol_version: "v1.1"
  current_stage: "P1"
  current_task: "P1-T3"
  tasks:
    CONTROL_LAYER: {status: "GATED", test: "PASSED"}
    P1-T1:         {status: "GATED", test: "PASSED"}
    P1-T2:         {status: "GATED", test: "PASSED"}
    P1-T3:         {status: "READY", test: "NOT_RUN"}
    P1-T4..P2-T8:  {status: "BLOCKED", test: "NOT_RUN"}
  ```
- **Đánh giá**:
  - `P1-T2` ở trạng thái `GATED` (đã qua kiểm toán tái thẩm định).
  - `P1-T3` ở trạng thái `READY` (sẵn sàng thực thi, chưa có code triển khai, chưa tạo tệp Parquet đầu ra `readings_15min.parquet`, chưa có tệp kiểm thử `tests/test_P1_T3.py`).
  - Tất cả các task tiếp theo (`P1-T4` đến `P2-T8`) đều ở trạng thái `BLOCKED`.
  - Thứ tự tiến trình tuyến tính tuân thủ nghiêm ngặt quy tắc gating của `validate_state.py`.
- **Kết luận**: **PASS**. Trạng thái hoàn toàn chính xác.

---

### Chiều 12: Đánh Giá Tác Động Downstream (Downstream Methodological Consequences)
- **P1-T4 (Quality Flags)**:
  - Các cờ chất lượng (`is_missing`, `flag_flatline`, `flag_spike`, `flag_negative_step`) sẽ hoạt động trực tiếp trên lưới đều đặn 15 phút.
  - Cột `raw_record_count` được chuyển tiếp cho phép P1-T4 nhận biết mật độ quan sát thô của từng bin mà không cần truy vấn lại 208 triệu dòng dữ liệu thô.
- **P1-T5 (Clean Segments)**:
  - Clean Segment được định nghĩa là chuỗi liên tục các ô 15 phút có `value` non-NaN, không mang cờ xấu của P1-T4 và không có sự cố trong `issues/`.
  - Nhờ toán tử `LAST`, 100% giá trị trong Clean Segment là số đọc công tơ thật, bảo đảm Ground Truth hoàn hảo cho giai đoạn đánh giá.
- **P2 (Mask Engine)**:
  - Phân nhánh R-derived và S-matched vận hành trên lưới 15 phút.
  - Nhịp điệu tự nhiên (e.g. 6 phút) không bị biến thành sự cố giả tạo, vì chỉ các khoảng trống $> 15$ phút mới tạo ra ô rỗng.
- **P3, P4, P5, P6 (Mô hình & Phân tích)**:
  - Phân tầng phân tích ranking theo `cadence_class` giải quyết triệt để rủi ro đánh đồng độ nhạy giữa đồng hồ 15 giây (mất 60 gói/bin) và đồng hồ 6 phút (mất 2-3 gói/bin).
  - Không có bất kỳ mâu thuẫn downstream nào được phát hiện.
- **Kết luận**: **PASS**. Protocol v1.1 tạo nền tảng vững chắc và hoàn toàn tương thích với các giai đoạn tiếp theo.

---

### Chiều 13: Phát Hiện Kỹ Thuật Về Cấu Hình Cục Bộ (`configs/local.yaml`) [NOTE]
- **Mô tả phát hiện**:
  - Trong tệp cấu hình mẫu chuẩn `configs/default.yaml` (dòng 9): `protocol_version: "v1.1"`, đồng thời khai báo đầy đủ các khối cấu hình Protocol v1.1 (`etl.grid`, `meter_metadata`, `core_population`, `cadence_classification`, `feature_governance`, `reconciliation`).
  - Trong tệp cấu hình máy cá nhân `configs/local.yaml` (dòng 8): `protocol_version: "v1"`. Tệp này chỉ chứa đường dẫn dữ liệu ngoài `data.raw_dir` và các cấu hình cũ của P1-T2, hoàn toàn chưa có khối `etl.grid` hay `cadence_classification`.
  - Mã nguồn nạp cấu hình `src/config.py` (hàm `get_default_config_path` và `load_config`) hiện tại ưu tiên nạp `configs/local.yaml` nếu tệp này tồn tại, và **KHÔNG thực hiện deep-merge với `configs/default.yaml`**.
  - *Hệ quả tiềm ẩn*: Khi Executor bắt đầu triển khai nhiệm vụ P1-T3 trên môi trường cục bộ, nếu gọi `cfg = load_config()` mà không truyền cờ `--config configs/default.yaml`, hệ thống sẽ nạp `configs/local.yaml` và gặp lỗi thiếu cấu hình `cfg["etl"]["grid"]`.
- **Mức độ nghiêm trọng**: **MEDIUM (WARNING / TECHNICAL NOTE)**.
- **Khuyến nghị khắc phục**:
  - Trước khi Executor triển khai P1-T3, cần cập nhật `configs/local.yaml` để nâng cấp `protocol_version: "v1.1"` và đồng bộ các tham số `etl.grid` từ `configs/default.yaml`, HOẶC nâng cấp hàm `load_config` trong `src/config.py` để tự động merge `configs/default.yaml` làm base template trước khi ghi đè các cấu hình từ `configs/local.yaml`.
  - Do Auditor bị ràng buộc không được sửa cấu hình trong phiên kiểm toán này, ghi chú này được bàn giao chính thức cho Executor/Project Owner.

---

## 4. Tổng Kết Báo Cáo & Danh Mục Khuyến Nghị

### 4.1 Bảng tổng kết phát hiện kiểm toán (Findings Summary)

| ID Finding | Nội Dung Phát Hiện | Mức Độ | Trạng Thái Protocol | Hành Động Yêu Cầu |
|:---:|---|:---:|:---:|---|
| **F-01** | Toàn bộ định nghĩa Protocol v1.1 nhất quán 100% giữa TASK_PLAN và RESEARCH_PLAN | CRITICAL | **PASS** | Duy trì tính toàn vẹn qua SHA-256 manifest. |
| **F-02** | Toán học của lưới 15 phút $\text{Bin}(t) = (t-15\text{m}, t]$ và $\text{ceil\_to\_15min}$ bảo đảm không sót điểm biên | CRITICAL | **PASS** | Áp dụng chính xác trong script ETL P1-T3. |
| **F-03** | Invariant Occupied Bin Preservation và Zero Synthetic Observations thay thế hoàn toàn nghịch lý v1.0 | CRITICAL | **PASS** | Sử dụng làm tiêu chí assertion cốt lõi của P1-T3. |
| **F-04** | Core Population giữ trọn 79 meters (gồm `H1.ZE20`); ràng buộc split thời gian rõ ràng | HIGH | **PASS** | Không gán ép `H1.ZE20` vào dữ liệu trước 2022-11-30. |
| **F-05** | Ngũ ngưỡng Cadence và cấm rò rỉ metadata (`raw_record_count`, `bin_completeness`) vào model | CRITICAL | **PASS** | Thiết lập guard trong pipeline model ở P3/P5. |
| **F-06** | Ô rỗng được phân định rõ ràng là observation gap, không tự động là equipment failure | HIGH | **PASS** | P1-T4 chỉ gắn nhãn failure khi có issue log / flag lỗi. |
| **F-07** | Bảng cân bằng số học đối soát $208,286,269 = 208,224,479 + 61,790$ khớp bit-for-bit | HIGH | **PASS** | Lưu giữ vĩnh viễn trong metadata kho dữ liệu. |
| **F-08** | Cấu hình máy cá nhân `configs/local.yaml` chưa đồng bộ các khóa của Protocol v1.1 | MEDIUM | **NOTE** | Đồng bộ `configs/local.yaml` hoặc merge base config trước khi chạy ETL P1-T3. |
| **F-09** | Git repository hiện chưa tạo commit (`uncommitted_initial`) | LOW | **INFO** | Được bảo vệ bằng SHA-256 manifest; commit khi user yêu cầu. |

---

## 5. Quyết Định Kiểm Toán Cuối Cùng (Final Audit Determination)

Căn cứ trên kết quả khảo sát độc lập, đo đạc toán học và kiểm chứng tính toàn vẹn của toàn bộ tài liệu đặc tả, Independent Protocol Auditor chính thức ban hành kết luận:

```text
================================================================================
  AUDIT RESULT: PASS WITH NOTES
  PROTOCOL v1.1 IS OFFICIALLY VERIFIED, SOUND, AND CLEARED FOR EXECUTION
================================================================================
```

### Các bước tiếp theo:
1. **Trạng thái Task**: `P1-T3` duy trì trạng thái **`READY`** trong `control/task_state.yaml`.
2. **Bàn giao cho Executor**: Executor Agent có thể tiếp nhận nhiệm vụ triển khai kỹ thuật cho **P1-T3** (`etl/resample_15min.py` và `tests/test_P1_T3.py`) dựa trên các tiêu chí nghiệm thu của Protocol v1.1.
3. **Kỷ luật dừng**: Phiên kiểm toán kết thúc tại đây. Không sửa đổi bất kỳ tệp tin nào ngoài báo cáo kiểm toán này. Không triển khai mã nguồn P1-T3. Không thay đổi máy trạng thái.

---
*Báo cáo được lập độc lập bởi Independent Protocol Auditor — 2026-10-07.*
