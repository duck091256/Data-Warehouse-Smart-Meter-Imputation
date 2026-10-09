# RESTART AUDIT REPORT

- **Dự án**: Beyond Synthetic Missingness — Smart-Meter Imputation
- **Thời điểm kiểm toán**: 2026-10-05T03:25:00+07:00
- **Trạng thái Git**: Empty Git repository (`git init` đã khởi tạo, chưa có commit nào theo Rule S)
- **Tài liệu Protocol chính thức**: `TASK_PLAN.md` (SHA-256: `16912dd7e6282170b36b0dc4dcbf0423348339306182578bbe0dc3324430546b`)

---

## 1. Mục tiêu và Phương pháp Kiểm toán

Báo cáo này kiểm toán toàn diện trạng thái repository hiện tại trước khi triển khai các giai đoạn nghiên cứu (P1–P7). Mục tiêu là:
1. Rà soát toàn bộ tài sản mã nguồn, dữ liệu, tài liệu hiện có trong workspace.
2. Phân loại từng tài sản theo 4 nhóm chuẩn mực:
   - **REUSE**: Tài sản hợp lệ, chuẩn xác với protocol hiện tại, tái sử dụng trực tiếp.
   - **REBUILD**: Thành phần bắt buộc theo protocol nhưng chưa có hoặc cần xây mới hoàn toàn.
   - **ARCHIVE**: Tài sản thuộc các đề tài cũ, tài liệu khảo sát lịch sử hoặc tài liệu tham khảo, giữ nguyên không xóa nhưng không nằm trong luồng thực thi nghiên cứu.
   - **UNKNOWN**: Tài sản chưa rõ nguồn gốc hoặc mục đích, cần làm rõ trước khi sử dụng.
3. Đối chiếu giữa đề xuất ban đầu và kế hoạch `TASK_PLAN.md`.
4. Đánh giá trạng thái bảo vệ dữ liệu thô (`data/raw/`).

---

## 2. Bảng Phân loại Tài sản Hiện tại

| Tài sản / Đường dẫn | Phân loại | Mô tả & Đánh giá | Hướng xử lý |
|---|:---:|---|---|
| `TASK_PLAN.md` | **REUSE** | Kế hoạch nghiên cứu và ma trận task chi tiết (P1–P7). Single Source of Truth. | Giữ nguyên tuyệt đối (Protected path). Hash đã ghi nhận. |
| `AGENTS.md` | **REUSE** | Hiến chương và quy tắc bất biến chung cho mọi coding agent. | Thành phần Governance của Control Layer. |
| `EXECUTOR.md` | **REUSE** | Hướng dẫn và quy trình 9 bước cho Executor Agent. | Thành phần Governance của Control Layer. |
| `AUDITOR.md` | **REUSE** | Quy trình và tiêu chuẩn kiểm toán độc lập cho Auditor Agent. | Thành phần Governance của Control Layer. |
| `REPAIR.md` | **REUSE** | Quy trình sửa lỗi nghiêm ngặt cho Repair Agent khi audit fail. | Thành phần Governance của Control Layer. |
| `control/task_state.yaml` | **REUSE** | State machine quản lý trạng thái các task nghiên cứu. | Theo dõi trạng thái tiến độ, chặn vượt rào. |
| `control/protected_paths.txt` | **REUSE** | Danh sách các đường dẫn bất khả xâm phạm. | Nạp vào `check_scope.py`. |
| `control/check_scope.py` | **REUSE** | Công cụ kiểm tra phạm vi file thay đổi so với protected paths. | Thực thi tự động trong CI/Gate. |
| `control/protocol_hash.sh` | **REUSE** | Công cụ tính toán và kiểm chứng hash SHA-256 của protocol. | Ngăn chặn sửa trộm protocol. |
| `control/validate_state.py` | **REUSE** | Trình kiểm tra tính hợp lệ của state machine và gating order. | Tích hợp vào gate kiểm soát. |
| `control/gate.sh` | **REUSE** | Cổng kiểm soát tổng thể trước khi nghiệm thu từng task. | Chạy kiểm tra tự động trước bàn giao. |
| `tests/test_control_layer.py` | **REUSE** | Test suite kiểm tra 7 yêu cầu cốt lõi của Control Layer (100% pass). | Chạy hồi quy qua pytest. |
| `bao_cao_va_phan_tich_de_tai/de_tai_data_warehouse.md` | **REUSE** | Đề xuất đề tài nghiên cứu chính thức: "Beyond Synthetic Missingness". Khớp 100% với `TASK_PLAN.md`. | Giữ lại làm tài liệu cơ sở khoa học của đề tài. |
| `bao_cao_va_phan_tich_de_tai/de-tai-2-energy-weather-warehouse.md` | **ARCHIVE** | Đề xuất đề tài thay thế cũ (Đề tài 2: Kho dữ liệu điện và thời tiết - OPSD/ENTSO-E/ERA5). | Lưu trữ lịch sử, không tham gia vào pipeline hiện tại. |
| `bao_cao_va_phan_tich_de_tai/de-xuat-de-tai-2-energy-weather.md` | **ARCHIVE** | Tóm tắt đề xuất Đề tài 2 cũ. | Lưu trữ lịch sử. |
| `bao_cao_va_phan_tich_de_tai/danh_gia_va_de_xuat_3_de_tai_dw.md` | **ARCHIVE** | Báo cáo so sánh 3 hướng đề tài kho dữ liệu ban đầu. | Lưu trữ lịch sử. |
| `bao_cao_va_phan_tich_de_tai/phan_tich_3_de_tai_kho_du_lieu.md` | **ARCHIVE** | Phân tích chi tiết 3 hướng đề tài ban đầu. | Lưu trữ lịch sử. |
| `bao_cao_va_phan_tich_de_tai/mẫu_đề_xuất_đề_tài.md` | **ARCHIVE** | Mẫu đề xuất đồ án của trường VKU. | Lưu trữ mẫu biểu. |
| `bao_cao_va_phan_tich_de_tai/old/*` | **ARCHIVE** | Các bản khảo sát sơ bộ ban đầu (Y tế & Kinh tế, Trái Đất...). | Lưu trữ lịch sử. |
| `documents/*.pdf` | **ARCHIVE** | Đề cương chi tiết và Syllabus môn Kho dữ liệu VKU 2025. | Tài liệu tham khảo môn học. |
| `data/raw/` | **REUSE** | Thư mục fallback cục bộ trong repo. Toàn bộ pipeline hiện tại đã cấu hình nạp từ **External Raw Dataset** an toàn. | Giữ nguyên rỗng trong repo, toàn bộ pipeline đọc từ `data.raw_dir` ngoài qua config. |
| External Raw Dataset | **REUSE** | Bộ dữ liệu gốc Honda Research Institute tại `/run/media/duck/New Volume/Vice - Download/Honda_Dataset` (81 meters, issues logs). | Nguồn dữ liệu Authoritative duy nhất, READ ONLY tuyệt đối, nạp qua `configs/local.yaml`. |
| `src/config.py` & `etl/config.py` | **REUSE** | Module nạp cấu hình và resolve đường dẫn raw data an toàn (hỗ trợ khoảng trắng, kiểm tra READ ONLY). | Tái sử dụng cho toàn bộ pipeline ETL, mask, models, analysis. |
| `configs/local.yaml` | **REUSE** | Cấu hình máy cá nhân chứa đường dẫn external raw dataset (được bảo vệ qua `.gitignore`). | Quản lý độc lập theo từng môi trường máy developer. |
| Preprocessing pipeline | **REBUILD** | Tiền xử lý, timezone UTC/local, lưới 15 phút, quality flags, clean segments. | Chưa có mã nguồn. Xây dựng mới tại P1 (T1–T5). |
| Warehouse schema & ETL | **REBUILD** | DDL star/snowflake schema (`Dim_Meter`, `Dim_Time`, `Fact_Reading`...). | Chưa có mã nguồn. Xây dựng mới tại P1 (T6–T8). |
| Failure Episode & Mask Engine | **REBUILD** | Trích episode, sinh mask 4 nhánh (S-point, S-block, S-matched, R-derived). | Chưa có mã nguồn. Xây dựng mới tại P2 (T1–T7). |
| Baseline Models | **REBUILD** | Base interface, Linear, Seasonal Naive, KNN, XGBoost. | Chưa có mã nguồn. Xây dựng mới tại P3 (T1–T4). |
| Evaluation Metrics | **REBUILD** | MAE, RMSE, Energy Consistency Metric. | Chưa có mã nguồn. Xây dựng mới tại P3-T5. |
| Ranking & OLAP Analysis | **REBUILD** | Kendall tau, Bootstrap CI, phân tích regime, OLAP queries. | Chưa có mã nguồn. Xây dựng mới tại P4. |
| Deep Learning Models | **REBUILD** | SAITS, BRITS, TimesNet qua PyPOTS. | Chưa có mã nguồn. Xây dựng mới tại P5 (nếu có GPU). |
| Selector / Downstream | **REBUILD** | Pattern-aware selector + forecasting. | Có điều kiện (chỉ làm nếu P4-T8 trigger). |

---

## 3. Rà soát Chi tiết theo từng Khía cạnh Nghiên cứu

### 3.1. Dữ liệu thô và Bảo vệ dữ liệu (`data/raw/` & External Raw Dataset)
- **Vị trí vật lý Authoritative**: `/run/media/duck/New Volume/Vice - Download/Honda_Dataset` (phân vùng NTFS3 ngoài repo).
- **Cấu trúc dữ liệu đã xác thực (READ ONLY)**:
  - `data/`: 81 thư mục meter (ví dụ: `H1.K11`, `H2.Z311`, `H3.Z44`...), mỗi meter chứa các chuỗi thời gian nén `.csv.gz` đầy đủ các biến đo (công suất, điện áp, dòng điện, tần số) ở cả định dạng raw (`*_raw.csv.gz`), harmonized (`*_harmonized.csv.gz`) và corrected (`*_corrected.csv.gz`).
  - `issues/`: 81 file `automatic_issues` và 7 file `manual_issues` phục vụ trích xuất failure episode trong P2.
  - `reduced_data/`: Dữ liệu rút gọn đi kèm từ nguồn gốc.
- **Biện pháp bảo vệ**:
  - Tuyệt đối không copy hay move raw dataset vào repo để tránh trùng lặp dữ liệu lớn và nguy cơ rò rỉ.
  - Toàn bộ pipeline truy cập raw dataset thông qua cơ chế config (`--config <path>` hoặc `configs/local.yaml`).
  - Đường dẫn máy cá nhân được bảo vệ bằng `.gitignore` trong `configs/local.yaml`.
  - Mọi thao tác đọc dữ liệu sử dụng `pathlib.Path` an toàn trước khoảng trắng và tuân thủ chế độ READ ONLY tuyệt đối.

### 3.2. Tiền xử lý, Chuẩn hóa Múi giờ và Lưới 15 phút
- **Trạng thái**: Hoàn toàn chưa có code trong repo.
- **Yêu cầu tương lai (P1)**:
  - Cần quy về UTC đồng thời giữ local time để xử lý đúng hiện tượng biến đổi tải theo giờ địa phương và chuyển đổi giờ mùa hè (DST).
  - Chuẩn hóa reindex lưới 15 phút: giữ nguyên các khoảng trống dưới dạng `NaN`, tuyệt đối không tự ý nội suy điền giá trị ở bước này.
  - Đánh dấu 3 cờ chất lượng: `is_missing`, `has_issue`, `is_corrected`.

### 3.3. Trích xuất Clean Segment và Quy tắc Ground Truth
- **Trạng thái**: Chưa có code.
- **Cảnh báo quan trọng**:
  - Không được dùng giá trị `corrected` trong log làm ground truth.
  - Clean segment phải là các đoạn liên tục thực sự sạch: không missing, không có issue log, không bị corrected, độ dài $\ge L$ (theo config).

### 3.4. Mô hình Warehouse và DDL
- **Trạng thái**: Chưa có DDL hoặc database file.
- **Kiến trúc mục tiêu**: Các bảng Fact (`Fact_Reading`, `Fact_FailureEpisode`, `Fact_Mask`, `Fact_ImputationResult`, `Fact_ForecastResult`), các bảng Dim (`Dim_Meter`, `Dim_Time`, `Dim_Model`, `Dim_Regime`) và bảng quản lý chạy lặp lại (`Meta_Run`).

### 3.5. Mask Engine (4 nhánh so sánh)
- **Trạng thái**: Chưa có code.
- **Yêu cầu đối chiếu**:
  - Nhánh 1: **S-point** (point missing ngẫu nhiên).
  - Nhánh 2: **S-block** (block missing ngẫu nhiên, độc lập giữa các meter).
  - Nhánh 3: **S-matched** (khớp phân phối độ dài gap và tỷ lệ missing với dữ liệu thực, nhưng độc lập không có tương quan giữa các meter).
  - Nhánh 4: **R-derived** (replay hình dạng sự cố thực từ `Fact_FailureEpisode`, bảo toàn tương quan không gian và cấu trúc phân cấp hierarchy).

### 3.6. Baseline Models, Deep Learning và Đánh giá
- **Trạng thái**: Hoàn toàn chưa có.
- **Yêu cầu tuân thủ**:
  - Loại bỏ Random Forest (như đã chốt trong mục 0.1 của `TASK_PLAN.md`), chỉ giữ XGBoost làm đại diện nhóm cây.
  - Bắt buộc kiểm tra rò rỉ (leakage): mô hình không được nhìn thấy dữ liệu tương lai hoặc dữ liệu nằm dưới mask.

---

## 4. Khuyến nghị và Kế hoạch Tiếp theo

1. **Tuyệt đối không xóa các tài liệu cũ**: Giữ nguyên thư mục `bao_cao_va_phan_tich_de_tai/` và `documents/` ở trạng thái lưu trữ (ARCHIVE) để phục vụ kiểm tra đề tài và lịch sử môn học.
2. **Kích hoạt Gating cho P1-T1**:
   - Hiện tại task `CONTROL_LAYER` đã hoàn thành đầy đủ các tiêu chuẩn kỹ thuật (mã nguồn governance, state machine, kiểm tra phạm vi, protocol hashing và 100% test pass).
   - Sau khi task này được nghiệm thu (`GATED`), task `P1-T1` (Kiểm kê dữ liệu thô) mới được phép chuyển sang trạng thái `READY`.
3. **Cảnh báo Executor**: Không tự ý bắt đầu `P1-T1` trong phiên làm việc hiện tại.
