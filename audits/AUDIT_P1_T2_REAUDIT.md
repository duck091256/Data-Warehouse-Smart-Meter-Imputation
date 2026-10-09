# INDEPENDENT AUDIT REPORT #2: [P1-T2] — Timezone & DST Standardization

> **Dự án**: Beyond Synthetic Missingness — Smart-Meter Imputation  
> **Mã Task**: `P1-T2` — Chuẩn hóa múi giờ và DST: quy về UTC, lưu cả local time  
> **Kiểm toán viên**: Independent Auditor #2 (Phiên kiểm toán độc lập sau Evidence Repair)  
> **Thời điểm kiểm toán**: 2026-10-06T01:36:00+07:00 (UTC 2026-10-05 18:36:00Z)  
> **Nguồn dữ liệu Authoritative**: `/run/media/duck/New Volume/Vice - Download/Honda_Dataset` (NTFS external partition)  
> **Tài liệu Protocol thẩm quyền**: `TASK_PLAN.md`, `AGENTS.md` (Single Source of Truth)  
> **Kết luận cuối cùng**: **PASS**  
> **Khuyến nghị Gate**: **P1-T2 SUFFICIENT EVIDENCE TO TRANSITION TO GATED**

---

## 1. Executive Summary & Verdict

Phiên kiểm toán **Independent Auditor #2** được tiến hành độc lập toàn diện, không thừa nhận số liệu từ báo cáo của Executor hay Audit #1, mà thực thi đo lường, kiểm tra trực tiếp trên:
1. Tập dữ liệu thô gốc ngoài phân vùng (`raw_dir`);
2. Mã nguồn ETL (`etl/normalize_utc.py`) và cấu hình hệ thống (`configs/default.yaml`, `configs/local.yaml`);
3. Tập dữ liệu trung gian đầu ra (`data/interim/readings_utc.parquet`, 3.66 GB, 208,224,479 dòng);
4. Toàn bộ 12 test suite P1-T2 (`tests/test_P1_T2.py`), 7 test suite Control Layer (`tests/test_control_layer.py`), và kịch bản cổng kiểm soát (`control/gate.sh`).

### Đánh giá tổng quan sau Evidence Repair:
- Vòng Evidence Repair đã **thực sự đóng toàn bộ các discrepancy và finding** trước đây.
- Bảng kiểm kê 40 biến đo lường từ 1,603 file thô đã được đối soát chính xác 100%, khắc phục hoàn toàn thiếu sót bỏ quên nhóm biến $W_1, W_2, W_3$ trong báo cáo Audit #1.
- Hiện tượng duplicate và mismatch tại `V.Z84` được khám nghiệm thực nghiệm trực tiếp trên file mục tiêu `V.Z84.W_raw.csv.gz`, phân định minh bạch ba tầng thông tin (Fact, Inference, Protocol Decision) và ghi nhận đúng bản chất `UNRESOLVED` do thiếu firmware log.
- Trục thời gian UTC và chuyển dịch DST (Spring/Fall 2018–2023) đã được kiểm chứng trên **toàn bộ 79 meters** (174,058 dòng vùng chuyển mùa) với **0 lỗi**.
- Tuyệt đối không có rò rỉ dữ liệu `_corrected_raw`, không có dữ liệu nội suy nhân tạo, dữ liệu thô nguyên vẹn 100%.

**Kết luận**: **PASS**. P1-T2 đáp ứng đầy đủ tiêu chí nghiệm thu định lượng, bảo toàn tính toàn vẹn nghiên cứu và đủ điều kiện để chuyển trạng thái sang `GATED`.

---

## 2. Báo Cáo Chi Tiết Theo 15 Chiều Kiểm Toán (Audit Dimensions)

### Chiều 1: Phân Loại Toàn Bộ Tập Dữ Liệu (Full File Classification)
Kiểm tra độc lập toàn bộ thư mục `/run/media/duck/New Volume/Vice - Download/Honda_Dataset` ghi nhận tổng cộng đúng **9,740 files**:

$$\begin{aligned}
\text{Tổng số files} &= \mathbf{9,740} \text{ files} \\
\text{Thư mục } \texttt{data/} &= \mathbf{9,631} \text{ files} \\
\text{Thư mục } \texttt{issues/} &= \mathbf{88} \text{ files (81 automatic + 7 manual)} \\
\text{Thư mục } \texttt{reduced\_data/} &= \mathbf{21} \text{ files (15min, 1h, 1min)} \\
\text{Files không giải thích được} &= \mathbf{0} \text{ files}
\end{aligned}$$

#### Phân rã nội bộ thư mục `data/` (9,631 files):
1. **Authoritative Raw Files** (`*_raw.csv.gz` ngoại trừ backup và corrected): **1,603 files**.
2. **Corrected Raw Files** (`_corrected_raw.csv.gz` tại `V.ZE84`): **21 files** (cô lập tuyệt đối).
3. **Backup Files** (trong `data/V.Z84/backup/`): **12 files** (gồm 2 file raw `W_in_raw`, `W_out_raw` và 10 file phái sinh).
4. **Derived Files** (bên thứ ba tiền xử lý ngoài backup: `_corrected.csv.gz`, `_harmonized.csv.gz`, `_resampled_*.csv.gz`): **7,995 files** (nếu tính cả 10 file phái sinh trong backup là 8,005 files).

```text
Phân loại chính (Primary Partition, Zero Overlap):
  1,603 (Authoritative Raw) + 21 (Corrected Raw) + 12 (Backup) + 7,995 (Derived) = 9,631 files
  9,631 (data/) + 88 (issues/) + 21 (reduced_data/) = 9,740 files (100% Khớp tuyệt đối)
```
- **Đánh giá**: **PASS**. Không có overlap kép, không có file chưa phân loại.

---

### Chiều 2: Đối Soát Toàn Bộ Dòng Dữ Liệu (Full Row Reconciliation)
Kiểm tra đối soát số học độc lập qua bảng kiểm kê 40 biến đo lường từ 1,603 files:

| STT | Nhóm biến | Biến thành phần | Số files | Tổng số dòng thô | Duplicates | Trạng thái ETL P1-T2 |
|:---:|---|---|:---:|:---:|:---:|---|
| **1** | **Điện năng tác dụng (Target)** | **$W$** | **80** | **208,286,269** | **61,790** | **Nạp vào `readings_utc.parquet`** |
| 2 | Công suất tác dụng | $P$ | 80 | 224,471,216 | 0 | Chưa ETL (dành cho Auxiliary) |
| 3 | Công suất từng pha | $P_1, P_2, P_3$ | 213 | 605,167,901 | 0 | Chưa ETL |
| 4 | Điện áp từng pha | $U_1, U_2, U_3$ | 213 | 592,634,009 | 0 | Chưa ETL |
| 5 | Dòng điện từng pha | $I_1, I_2, I_3$ | 213 | 538,239,457 | 0 | Chưa ETL |
| 6 | Hệ số công suất | $PF, PF_1, PF_2, PF_3$ | 283 | 731,568,531 | 0 | Chưa ETL |
| 7 | Tần số lưới | $f$ | 70 | 175,401,119 | 0 | Chưa ETL |
| 8 | Điện năng vào/ra | $W_{\text{in}}, W_{\text{out}}$ | 142 | 187,840,583 | 224,656 | Chưa ETL ($W_{\text{in}}$: 60k dup, $W_{\text{out}}$: 164k dup) |
| 9 | Điện năng từng pha | $W_1, W_2, W_3$ | 78 | 208,322,078 | 0 | Chưa ETL (Đã bổ sung sau Audit #1) |
| 10 | Công suất phản kháng | $Q, WQ, WQ_{\text{in}}, WQ_{\text{out}}$ | 176 | 357,726,093 | 0 | Chưa ETL |
| 11 | Cảm biến nhiệt phụ tải | $T_{\text{diff}}, V, q_v, T_{vl}, T_{rl}$ | 45 | 57,763,240 | 0 | Chưa ETL |
| 12 | Trạm khí tượng | 10 cảm biến | 10 | 65,066,609 | 0 | Chưa ETL |
| **TỔNG** | **40 Biến Đo Lường** | — | **1,603** | **3,952,487,105** | **286,446** | **Tự cân bằng 100%** |

#### Phương trình cân bằng dòng dữ liệu (Balance Equation):
$$3,952,487,105 \text{ (tổng thô)} - 3,744,200,836 \text{ (39 biến phụ)} = 208,286,269 \text{ ($W$ raw rows)}$$
$$208,286,269 \text{ ($W$ raw)} - 61,790 \text{ (duplicates dropped)} = \mathbf{208,224,479} \text{ (parquet rows)}$$
- **Đánh giá**: **PASS**. Khớp chính xác bit-for-bit, chênh lệch bằng đúng 0.

---

### Chiều 3: Phạm Vi Biến Mục Tiêu W (W Scope Discipline)
- **Target Variable**: Cấu hình tường minh tại `configs/default.yaml` và `configs/local.yaml` là `etl.target_variable: "W"`.
- **Nội dung `readings_utc.parquet`**: Đã quét toàn bộ 253 row groups bằng PyArrow; tập giá trị duy nhất trong cột `variable` là `{"W"}`. Không có bất kỳ biến nào khác lọt vào.
- **Biến phụ tải $P$ và các biến auxiliary**: Chưa được ETL, không giả mạo là đã ETL.
- **Uniqueness Key**: Khóa duy nhất là:
  $$\mathbf{(\text{meter\_id}, \text{variable}, \text{timestamp\_utc})}$$
- **Lập luận khoa học**: Bác bỏ lập luận của auditor trước ("gộp nhiều biến sẽ trùng timestamp"). Khẳng định việc chỉ xử lý $W$ là quyết định thiết kế nghiên cứu xuất phát từ bài toán cốt lõi: *Smart-Meter Active Energy Imputation (15-min kWh)*.
- **Đánh giá**: **PASS**.

---

### Chiều 4: Khám Nghiệm Thực Nghiệm Duplicate Tại Meter V.Z84
Kiểm tra thực nghiệm trực tiếp toàn bộ 4,272,693 dòng của `data/V.Z84/V.Z84.W_raw.csv.gz`:
- **Tổng số dòng thô**: 4,272,693 dòng.
- **Số timestamp duy nhất**: 4,210,903 timestamps.
- **Số mốc timestamp bị lặp**: 55,109 mốc thời gian.
- **Phân bổ cấu trúc cụm**:
  - Cặp (Pairs - 2 dòng/mốc): **48,428 mốc** ($48,428 \times 2 = 96,856$ dòng).
  - Bộ ba (Triplets - 3 dòng/mốc): **6,681 mốc** ($6,681 \times 3 = 20,043$ dòng).
  - Không có mốc nào có $\ge 4$ dòng.
- **Số dòng thừa bị drop khi áp dụng `keep_last`**:
  $$\text{Dropped} = (48,428 \times 1) + (6,681 \times 2) = 48,428 + 13,362 = \mathbf{61,790} \text{ dòng}$$
- **Xác minh phương trình**:
  $$4,272,693 - 61,790 = 4,210,903 \text{ (Khớp 100\% với số dòng V.Z84 trong parquet)}$$
- **So sánh trực tiếp `keep_last` raw vs parquet**: Khớp bit-for-bit trên toàn bộ 4,210,903 dòng.
- **Đánh giá**: **PASS**.

---

### Chiều 5: Tính Chuẩn Mực Trong Diễn Đạt Khoa Học (Scientific Wording Audit)
Đã rà soát chi tiết toàn văn `reports/v_z84_duplicate_evidence.md` và `reports/p1_t2_reconciliation.md`. Báo cáo đã phân tách nghiêm ngặt 3 tầng thông tin:
1. **Observed Fact (Thực tế quan sát)**:
   - Các con số định lượng (4,272,693 dòng thô, 55,109 mốc lặp, 61,790 dòng thừa, 169,365 bước giảm).
   - Thứ tự thời gian đơn điệu tăng dần (`out_of_order = 0`).
   - Mốc xuất hiện sau sự cố mất kết nối ngày 2023-05-15 11:45:31 UTC.
2. **Inference (Suy luận kỹ thuật / Giả thuyết)**:
   - Hiện tượng duplicate cùng giá trị được suy luận là do cơ chế mạng (retransmission / duplicate ACK).
   - Hiện tượng cập nhật khác giá trị phản ánh thanh ghi cuối chu kỳ và offset trôi dạt trước khi ổn định.
   - Các thuật ngữ Modbus, packet retransmission, hardware offset được xếp rõ vào tầng **Inference/Hypothesis**, không bị viết thành Fact.
3. **Protocol Decision (Quyết định chuẩn hóa)**:
   - Áp dụng `keep_last` theo cấu hình tường minh để loại bỏ 61,790 dòng thừa và giữ giá trị chuẩn.
   - Không can thiệp, không ép buộc tính đơn điệu, không tự tính $W = W_{\text{out}} - W_{\text{in}}$.
- **Đánh giá**: **PASS**.

---

### Chiều 6: Kiểm Tra Hiện Tượng Mismatch 4.94% ($W_{\text{out}} - W_{\text{in}} - W \ne 0$)
Độc lập tính toán giao thoa 3 file thô $W, W_{\text{in}}, W_{\text{out}}$ tại 37,322 mốc thời gian xuất hiện đồng thời cả 3 biến sau `keep_last`:
- **Khớp hoàn hảo ($|W_{\text{out}} - W_{\text{in}} - W| < 10^{-4}$)**: **35,478 mốc (95.06%)**.
- **Lệch ($|W_{\text{out}} - W_{\text{in}} - W| \ge 10^{-4}$)**: **1,844 mốc (4.94%)**.
- **Phân bổ 1,844 mốc lệch**:
  - **1,646 mốc (89.26%)** có duplicate ở ít nhất 1 trong 3 file nguồn.
  - **198 mốc (10.74%)** là mốc singleton trên cả 3 file.
  - 100% mốc lệch xảy ra **sau ngày 2023-05-15 19:22:25 UTC**.
- **So sánh `keep_last` vs `keep_first`**:
  - Với `keep_last`: 35,478 mốc khớp (95.06%), 1,844 mốc lệch (4.94%).
  - Với `keep_first`: chỉ 29,369 mốc khớp (78.69%), 7,953 mốc lệch (21.31%). `keep_last` giảm sai lệch 4.3 lần.
- **Trạng thái nguyên nhân**: Được ghi nhận chính thức là **`UNRESOLVED`** do thiếu telemetry firmware từ nhà sản xuất.
- **Tính độc lập của pipeline**: Pipeline đọc trực tiếp $W$, không dùng công thức trừ nên hoàn toàn không bị ảnh hưởng.
- **Đánh giá**: **PASS**.

---

### Chiều 7: Đặc Tính Không Đơn Điệu Của W (Non-Monotonic W)
- **Rà soát mã nguồn & Test**:
  - `grep -in "monotonic" etl/` $\rightarrow$ 0 kết quả.
  - `grep -in "monotonic" tests/` $\rightarrow$ 0 kết quả.
  - Hoàn toàn không có assertion ép buộc tính đơn điệu trong implementation hay test suite.
- **Đính chính văn bản**: Mọi khẳng định cũ coi "W là thanh ghi đơn điệu không giảm" đã bị loại bỏ khỏi các báo cáo. Báo cáo ghi nhận rõ bản chất $W$ là Net Energy Saldo có **169,365 bước giảm tự nhiên** trong `V.Z84.W`.
- **Đánh giá**: **PASS**.

---

### Chiều 8: Chuẩn Hóa Múi Giờ và Chuyển Đổi DST (Timezone & DST Standardization)
Độc lập kiểm tra toàn bộ quần thể **79 meters** có dữ liệu trong Parquet qua toàn bộ 12 đợt chuyển mùa (6 mùa xuân, 6 mùa thu từ 2018 đến 2023):
- **Cửa sổ kiểm tra**: $\pm 2$ giờ quanh thời điểm chuyển đổi 01:00 UTC (khoảng thời gian 240 phút mỗi kỳ chuyển đổi).
- **Tổng số dòng dữ liệu kiểm tra trực tiếp**: **174,058 dòng** (làm rõ: con số 175,060 dòng trong bản log sơ bộ trước đây xuất phát từ cửa sổ lấy mẫu rộng hơn ~2.05h; kiểm tra chính xác trên cửa sổ $\pm 2$h ghi nhận đúng 174,058 dòng trên toàn bộ 79 meters).
- **Kết quả thực tế**:
  - Mùa Xuân (Spring): 01:00 UTC nhảy từ CET (+1, `is_dst=False`) lên CEST (+2, `is_dst=True`). Trục UTC tăng dần liên tục, **0 khoảng trống UTC giả**.
  - Mùa Thu (Fall): 01:00 UTC chuyển từ CEST (+2, `is_dst=True`) về CET (+1, `is_dst=False`). Trục UTC tăng dần đơn điệu, **0 bản ghi trùng lặp UTC**. Giờ địa phương lặp lại được phân định tuyệt đối bằng cờ `is_dst`.
  - Trên toàn bộ 208,224,479 dòng: `utc_offset_hours` 100% thuộc {1, 2}, và `is_dst == (utc_offset_hours == 2)` đạt 100%.
  - **Tổng số lỗi**: **0 lỗi**.
- **Đánh giá**: **PASS**.

---

### Chiều 9: Không Sinh Dữ Liệu Giả Mạo (No Synthetic Observations)
- **Quan hệ bao hàm toán học trên toàn bộ dataset**:
  $$\text{Output Observations } (208,224,479) \equiv \text{Raw Observations } (208,286,269) \setminus \text{Deduplicated Rows } (61,790)$$
  Kiểm tra độc lập trên toàn bộ **80 meters** của biến $W$ xác nhận đẳng thức:
  $$\text{Parquet Rows} = \text{Raw Rows} - \text{Duplicate Rows}$$
  thỏa mãn tuyệt đối $100\%$ trên từng meter riêng biệt (78 meters không duplicate có Parquet = Raw; 1 meter $V.Z84$ có Parquet = Raw - 61,790; 1 meter $H3.Z42$ có $0$ dòng).
- **Kiểm tra Checksum/Hash nhị phân chuỗi giá trị (Binary SHA-256 of float64 array)**:
  - Đã tính toán và đối chiếu mã băm SHA-256 trực tiếp từ mảng nhị phân `float64` (`tobytes()`) đọc qua PyArrow giữa file raw và file parquet:
    - `H1.Z10` (3,155,041 dòng): Khớp bit-for-bit $100\%$ (`30d4298fd3db8fd1323d2d446cb117a2c0bc3a88cc0d62c01ec97757edfa8d11`).
      *(Lưu ý kỹ thuật: Kiểm toán viên phát hiện nếu dùng `pd.read_csv` thông thường của pandas, parser C của pandas tự động làm tròn các số thực 17 chữ số như tại dòng 110,042 từ `18189.838852459012` thành `18189.83885245901`, gây lệch giả tạo trên 405,900 dòng nếu so sánh thô bằng pandas. PyArrow CSV reader bảo toàn độ chính xác số thực IEEE 754 nguyên bản từ file raw).*
    - `V.ZE84` (564,233 dòng): Khớp bit-for-bit $100\%$ (`9d9a3d14de6d3b409638e74db3a6fc9b2d3b80c8b9675823093a3674418072b7`).
    - `H1.K11` (368,168 dòng): Khớp giá trị $100\%$ (`value` trong parquet lưu `float64` chuẩn hóa theo CANONICAL_SCHEMA có mã băm `382064ade2d23672619179f9c8eb8f35028057b05197dc113c32152802923756`, chuyển đổi từ file thô lưu dạng số nguyên `int64`).
- **Tỷ lệ nội suy/dữ liệu giả mạo**: Đúng $\mathbf{0.0000\%}$. Pipeline P1-T2 chỉ chuẩn hóa định dạng thời gian và khử trùng lặp, không sinh thêm bất kỳ quan sát nào.
- **Đánh giá**: **PASS**.

---

### Chiều 10: Tính Toàn Vẹn Của Dữ Liệu Thô (Raw Data Integrity)
- **File mtime**: Quét toàn bộ 9,740 files trong `Honda_Dataset`: **0 file** có mtime sau ngày 04/10/2026.
- **Kích thước byte**: Đối chiếu kích thước byte thực tế của toàn bộ **1,603 file thô** với bản ghi kiểm kê P1-T1 tại `data/interim/inventory_by_file.csv`: **1,603/1,603 files khớp bit-for-bit (0 mismatches)**.
- **Thư mục local `data/raw/`**: Hoàn toàn trống và sạch (read-only invariant bảo toàn).
- **Đánh giá**: **PASS**.

---

### Chiều 11: Khả Năng Tái Lập (Reproducibility & Provenance)
- **Tính tiền định logic (Logical Determinism)**:
  - Unit test `test_10_deterministic_reproducibility` chạy thực nghiệm lại pipeline trên cùng cấu hình và seed 42, kiểm tra bit-for-bit các cột định danh, thời gian và giá trị.
- **Mã băm SHA-256 đầu ra**:
  - File `data/interim/readings_utc.parquet` có kích thước 3,662,760,196 bytes, mã SHA-256 thực tế trên đĩa là:
    `5983397375f03a5f0fd3cdab29c4ea561e3b68e13547aeca294f5ed8a2139b13`
    trùng khớp bit-for-bit với bản ghi `output_sha256` trong `data/interim/readings_utc_metadata.json`.
- **Đánh giá**: **PASS**.

---

### Chiều 12: Kiểm Tra Tầng Kiểm Soát (Control Layer & Scope Gate)
Đã audit trực tiếp mã nguồn `control/check_scope.py`:
- Tham số `--task P1-T2` chỉ bổ sung kiểm tra sự tồn tại và tính hợp lệ của các output artifacts bắt buộc (`TASK_REQUIRED_OUTPUTS["P1-T2"]`), hoàn toàn **không làm suy yếu hay bỏ qua bất kỳ kiểm tra protected paths nào**.
- Nếu có file cấm (như `TASK_PLAN.md` hay `data/raw/`), script lập tức báo vi phạm `[SCOPE VIOLATION]` và trả về mã lỗi `exit 1`.
- Kết quả chạy thực nghiệm:
  1. `.venv/bin/pytest tests/test_control_layer.py -v` $\rightarrow$ **7 passed in 0.16s**.
  2. `bash control/gate.sh` $\rightarrow$ **RESULT: GATE = PASS**.
  3. `python3 control/check_scope.py --task P1-T2` $\rightarrow$ **OUTPUT VERIFICATION PASSED, ALLOWED**.
- **Đánh giá**: **PASS**.

---

### Chiều 13: Cấu Hình Hệ Thống (Config Discipline)
- Cả `configs/default.yaml` và `configs/local.yaml` đều khai báo nhất quán:
  - `etl.target_variable: "W"`
  - `etl.local_timezone: "Europe/Berlin"`
  - `etl.deduplication.strategy: "keep_last"`
  - `etl.corrected_raw_policy.exclude: true`
  - `etl.empty_files_policy.skip_cleanly: true`
- Ghi chú `rationale` trong file cấu hình đã được cập nhật chính xác để phản ánh tính không đơn điệu của $W$.
- Đây là quyết định cấu hình kỹ thuật minh bạch, tuân thủ Rule 6 của `AGENTS.md`, không phải thay đổi ngầm protocol.
- **Đánh giá**: **PASS**.

---

### Chiều 14: Tính Toàn Vẹn Của Protocol (Protocol Integrity)
- Chạy `bash control/protocol_hash.sh --verify`:
  ```text
  Verifying protocol integrity against manifest...
  [OK] control/protected_paths.txt matches (4ee91e66cab2...)
  [OK] TASK_PLAN.md matches (16912dd7e628...)
  Protocol verification PASSED: All protocol files are intact.
  ```
- Không có bất kỳ thay đổi trái phép nào đối với `TASK_PLAN.md` hay `control/protected_paths.txt`.
- **Đánh giá**: **PASS**.

---

### Chiều 15: Kết Luận và Điều Kiện Gate (Audit Output & Recommendation)

| STT | Tiêu chí đánh giá | Kết quả thực tế | Trạng thái |
|:---:|---|---|:---:|
| 1 | File classification reconcile 100% | 9,740 files phân loại đầy đủ, 0 unexplained | **PASS** |
| 2 | Row reconciliation cân bằng | 3.95B raw $\rightarrow$ 208.28M W $\rightarrow$ 208.22M parquet | **PASS** |
| 3 | W scope minh bạch | Chỉ có $W$ trong parquet, key đầy đủ 3 trường | **PASS** |
| 4 | Duplicates V.Z84 kiểm tra trực tiếp | 55,109 mốc lặp, 61,790 dòng loại bỏ, keep_last bảo toàn register | **PASS** |
| 5 | Scientific wording phân định rạch ròi | Fact, Inference, Protocol Decision tách biệt | **PASS** |
| 6 | 4.94% mismatch phân tích đầy đủ | 1,844 mốc, 100% sau sự cố, ghi nhận UNRESOLVED | **PASS** |
| 7 | W non-monotonicity được thừa nhận | 169,365 bước giảm tự nhiên, không assertion đơn điệu | **PASS** |
| 8 | DST chuẩn hóa trên toàn bộ quần thể | 79 meters, 12 transitions, 174,058 dòng, 0 lỗi | **PASS** |
| 9 | Không dữ liệu giả mạo (0.0000% synthetic) | Checksum khớp bit-for-bit với nguồn thô | **PASS** |
| 10 | Dữ liệu thô nguyên vẹn | 0 file modified, 1,603 file sizes khớp P1-T1 | **PASS** |
| 11 | Tái lập tiền định | SHA-256 khớp metadata, test 10 pass | **PASS** |
| 12 | Control layer vững chắc | Gate pass, scope check phát hiện 100% vi phạm | **PASS** |
| 13 | Config provenance minh bạch | Khai báo tường minh, có rationale đầy đủ | **PASS** |
| 14 | Protocol nguyên vẹn | Protocol hash khớp manifest tuyệt đối | **PASS** |

---

## 3. Kết Luận Chung & Khuyến Nghị Gate

- **Kết luận Audit #2**: **PASS**
- Toàn bộ các nghi vấn, sai lệch số liệu và thiếu sót của đợt audit trước đã được **Evidence Repair giải quyết triệt để** bằng bằng chứng thực nghiệm độc lập.
- Task `P1-T2` đã hoàn thành xuất sắc, tuân thủ trọn vẹn Hiến chương `AGENTS.md` và Protocol `TASK_PLAN.md`.
- **Khuyến nghị cho Coordinator / Orchestrator**:
  1. Cho phép Task `P1-T2` chuyển trạng thái sang **`GATED`** trong `control/task_state.yaml`.
  2. Mở khóa cho Task `P1-T3` (Lưới thời gian đều đặn 15 phút, reindex không nội suy) chuyển trạng thái sang **`READY`**.
  3. Duy trì nguyên tắc sử dụng duy nhất biến mục tiêu $W$ từ `data/interim/readings_utc.parquet` làm đầu vào cho P1-T3.
