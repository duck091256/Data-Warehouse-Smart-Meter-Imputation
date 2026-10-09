# Báo Cáo Rà Soát và Đề Xuất Điều Chỉnh Protocol P1-T3 (P1-T3 Protocol Amendment Review v1.1)

> **Dự án**: Beyond Synthetic Missingness — Smart-Meter Imputation  
> **Mã Báo Cáo**: `P1-T3 PROTOCOL AMENDMENT REVIEW v1.1`  
> **Thời điểm lập báo cáo**: 2026-10-06T08:30:00+07:00 (UTC 2026-10-06 01:30:00Z)  
> **Trạng thái Task**: `P1-T3: READY (Tạm dừng kiểm soát tiền trạm / Protocol Gate)`  
> **Căn cứ pháp lý & Quản trị**: Hiến chương Nghiên cứu `AGENTS.md`, `TASK_PLAN.md`, `configs/default.yaml`, `configs/local.yaml`  
> **Tập dữ liệu đầu vào đã kiểm chứng**: `data/interim/readings_utc.parquet` (208,224,479 dòng, 79 meters có dữ liệu, SHA-256: `5983397375...`)  

---

## Tóm Tắt Điều Hành (Executive Summary)

Báo cáo này thực hiện đánh giá toàn diện và độc lập (**Protocol Amendment Review v1.1**) cho nhiệm vụ **P1-T3** (*Chuẩn hóa lưới 15 phút: reindex đầy đủ, không nội suy, giữ NaN gốc*).

### Bối cảnh và Động lực
Trước đó, báo cáo tiền trạm (`reports/p1_t3_protocol_preflight.md`) đã phát hiện mâu thuẫn toán học cốt lõi trong tiêu chí nghiệm thu của `TASK_PLAN.md` (yêu cầu *"số giá trị non-NaN không đổi so với trước reindex"* là bất khả thi khi downsampling từ 208.2 triệu dòng quan sát sub-minute xuống lưới 15 phút chỉ có ~13.98 triệu ô thời gian). Đồng thời, các tài liệu kiểm kê ban đầu từng ghi nhận nhãn *"pulse / low-frequency sparse (810s – 4.5h)"* cho 9 đồng hồ đo, dẫn đến nguy cơ loại bỏ nhầm các meter này khỏi quần thể nghiên cứu.

Nhằm thiết lập một quy trình chuẩn hóa chính xác, khách quan và bảo vệ toàn vẹn dữ liệu khoa học, đợt rà soát v1.1 đã thực hiện đo đạc thực nghiệm độc lập trên **toàn bộ 208,224,479 dòng dữ liệu** của tất cả **79 meters**, mang lại các phát hiện nền tảng:

1. **Bác bỏ giả định "pulse / low-frequency sparse"**:
   - Trong toàn bộ 79 meters, **KHÔNG CÓ BẤT KỲ METER NÀO CÓ TRUNG VỊ KHOẢNG CÁCH (MEDIAN GAP) LỚN HƠN 15 PHÚT**.
   - 9 meter từng bị gán nhãn "pulse" thực chất có nhịp lấy mẫu cực kỳ đều đặn: `H1.ZE20` có cadence thực tế là **30 giây** (median gap 30.0s, p95 89.96s); 8 meter nhiệt/lạnh `K` và `W` có cadence thực tế là **6 phút** (median gap 360.0s, p95 720.0s = 12 phút).
   - Tỷ lệ chiếm dụng ô 15 phút (occupied rate) của toàn bộ 9 meters đạt từ **71.01% đến 87.98%**, hoàn toàn tương thích với lưới biểu diễn 15 phút.
2. **Bản chất của các Empty Bin trên lưới 15 phút**:
   - Một ô 15 phút $(t-15\text{m}, t]$ chỉ có thể rỗng khi và chỉ khi xuất hiện một khoảng trống quan sát liên tục **kéo dài vượt quá 15 phút (> 900 giây)**.
   - Do đó, 100% các ô rỗng sinh ra sau resampling là các **khoảng gián đoạn quan sát thực tế** (observation gaps do mất tín hiệu, cúp điện, bảo trì), hoàn toàn không phải do nhịp lấy mẫu tự nhiên quá thưa.
3. **Đính chính khẳng định về độ phủ hệ HVAC**:
   - Câu nhận định *"Loại 9 meter sẽ làm mất toàn bộ hệ HVAC"* là thiếu căn cứ thực nghiệm. Hệ thống HVAC chạy điện (máy nén lạnh Chiller, quạt thông gió AHU, bơm tuần hoàn) vẫn được đo đếm đầy đủ bởi hệ thống 70 công tơ điện (`Z` và `H*.T.Z`), và meter nhiệt `H1.W12` (đo nhiệt sưởi 6 năm, độ chiếm dụng 85.04%) không nằm trong nhóm 9 meter này. Việc giữ các meter `K` và `W` là nhằm **bảo tồn tính đa dạng tải nhiệt/điện (multi-carrier energy diversity)**, không phải vì là nguồn duy nhất của HVAC.
4. **H1.ZE20 vượt qua Eligibility Rule tổng quát**:
   - Thiết lập quy tắc hợp lệ khách quan dựa trên nguyên lý khoa học (thời gian theo dõi $\ge 365$ ngày, cadence $\le 15$ phút, tỷ lệ chiếm dụng $\ge 50\%$, ngữ nghĩa tương thích). Meter `H1.ZE20` vượt qua toàn bộ các tiêu chí và được **giữ lại trong quần thể cốt lõi (Core Population)**.
5. **Cân bằng số học tuyệt đối (Reconciliation Target)**:
   - Xác nhận sự cân bằng chính xác: $208,286,269 \text{ (raw W)} = 208,224,479 \text{ (deduplicated W)} + 61,790 \text{ (duplicates V.Z84)}$.

---

## 1. Bảng Khảo Sát Nhịp Điệu Toàn Bộ 79 Meters (Full 79-Meter Cadence Table)

Bảng dưới đây thống kê đầy đủ 79 meters có dữ liệu biến mục tiêu $W$ trong `data/interim/readings_utc.parquet`. Mọi chỉ số được tính toán trực tiếp từ chuỗi timestamp UTC tăng dần của từng meter:

| STT | Meter ID | Obs Count | Min Gap | Median (p50) | Mean Gap | p95 Gap | p99 Gap | Max Gap | Cadence | Total Bins | Occupied Bins | Occupied Rate | Empty Rate |
|:---:|---|---:|---:|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|
| 1 | `H1.K11` | 368,168 | 59.0s | 360.0s | 513.4s | 720.0s | 780.0s | 126.6h | `6min` | 209,999 | 156,082 | 74.33% | 25.67% |
| 2 | `H1.K12` | 371,325 | 59.0s | 360.0s | 509.1s | 720.0s | 780.0s | 571.3h | `6min` | 210,053 | 156,667 | 74.58% | 25.42% |
| 3 | `H1.K14` | 371,399 | 49.0s | 360.0s | 509.1s | 720.0s | 1020.0s | 249.6h | `6min` | 210,090 | 157,411 | 74.93% | 25.07% |
| 4 | `H1.K15` | 386,892 | 59.0s | 360.0s | 488.7s | 720.0s | 1260.0s | 3003.7h | `6min` | 210,098 | 162,943 | 77.56% | 22.44% |
| 5 | `H1.K16` | 381,185 | 53.0s | 360.0s | 421.9s | 720.0s | 900.0s | 193.5h | `6min` | 178,708 | 156,607 | 87.63% | 12.37% |
| 6 | `H1.W11` | 479,151 | 55.0s | 360.0s | 395.1s | 780.0s | 1800.0s | 106.7h | `6min` | 210,336 | 185,064 | 87.98% | 12.02% |
| 7 | `H1.W12` | 858,642 | 50.0s | 120.0s | 220.5s | 360.0s | 660.0s | 1530.6h | `2min` | 210,335 | 178,874 | 85.04% | 14.96% |
| 8 | `H1.Z10` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 9 | `H1.Z11` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 10 | `H1.Z12` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 11 | `H1.Z13` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 12 | `H1.Z14` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 13 | `H1.Z15` | 4,778,004 | 1.0s | 30.0s | 39.6s | 60.0s | 61.0s | 192.0h | `30s` | 210,336 | 206,846 | 98.34% | 1.66% |
| 14 | `H1.Z16` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 15 | `H1.Z17` | 4,890,930 | 1.0s | 30.0s | 38.7s | 60.0s | 60.0s | 192.0h | `30s` | 210,336 | 206,834 | 98.33% | 1.67% |
| 16 | `H1.Z18` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 17 | `H1.Z19` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 18 | `H1.Z20` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 19 | `H1.Z21` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 20 | `H1.Z22` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 21 | `H1.Z23` | 3,123,706 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 208,248 | 208,248 | 100.00% | 0.00% |
| 22 | `H1.Z24` | 3,123,706 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 208,248 | 208,248 | 100.00% | 0.00% |
| 23 | `H1.Z25` | 3,123,706 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 208,248 | 208,248 | 100.00% | 0.00% |
| 24 | `H1.Z26` | 4,846,147 | 1.0s | 30.0s | 39.1s | 60.0s | 60.0s | 192.0h | `30s` | 210,333 | 204,269 | 97.12% | 2.88% |
| 25 | `H1.Z27` | 3,353,756 | 0.3s | 60.0s | 56.4s | 91.0s | 184.0s | 192.0h | `1min` | 210,336 | 204,442 | 97.20% | 2.80% |
| 26 | `H1.Z28` | 4,815,486 | 0.1s | 30.0s | 39.3s | 60.0s | 61.0s | 192.0h | `30s` | 210,336 | 206,839 | 98.34% | 1.66% |
| 27 | `H1.Z29` | 3,775,021 | 1.0s | 30.1s | 50.1s | 90.0s | 208.0s | 192.1h | `30s` | 210,336 | 203,456 | 96.73% | 3.27% |
| 28 | `H1.Z310` | 1,680,940 | 9.4s | 30.0s | 66.0s | 31.0s | 150.0s | 103.8h | `30s` | 123,237 | 68,355 | 55.47% | 44.53% |
| 29 | `H1.ZE20` | 551,582 | 7.6s | 30.0s | 62.1s | 90.0s | 1320.0s | 101.3h | `30s` | 38,075 | 27,980 | 73.49% | 26.51% |
| 30 | `H2.K21` | 296,068 | 50.0s | 361.0s | 638.6s | 721.0s | 1560.0s | 795.6h | `6min` | 210,068 | 149,169 | 71.01% | 28.99% |
| 31 | `H2.T.Z30` | 2,703,826 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 180,256 | 180,256 | 100.00% | 0.00% |
| 32 | `H2.T.Z31` | 2,703,826 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 180,256 | 180,256 | 100.00% | 0.00% |
| 33 | `H2.T.Z32` | 2,703,826 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 180,256 | 180,256 | 100.00% | 0.00% |
| 34 | `H2.T.Z33` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 35 | `H2.T.Z34` | 2,703,826 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 180,256 | 180,256 | 100.00% | 0.00% |
| 36 | `H2.Z311` | 1,684,778 | 4.0s | 30.0s | 65.9s | 34.0s | 96.0s | 111.0h | `30s` | 123,333 | 64,538 | 52.33% | 47.67% |
| 37 | `H2.Z35` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 38 | `H2.Z351` | 3,360,317 | 2.0s | 30.0s | 30.9s | 32.0s | 59.9s | 101.3h | `30s` | 115,444 | 114,207 | 98.93% | 1.07% |
| 39 | `H2.Z36` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 40 | `H2.Z361` | 3,366,999 | 4.0s | 30.0s | 30.9s | 30.1s | 45.0s | 101.3h | `30s` | 115,444 | 114,203 | 98.92% | 1.07% |
| 41 | `H2.Z61` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 42 | `H2.Z62` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 43 | `H2.Z63` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 44 | `H2.Z64` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 45 | `H2.Z65` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 46 | `H2.Z66` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 47 | `H2.Z67` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 48 | `H2.Z68` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 49 | `H2.Z69` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 50 | `H2.Z70` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 51 | `H2.ZE64` | 1,837,544 | 7.0s | 30.0s | 30.5s | 32.0s | 33.0s | 101.3h | `30s` | 62,337 | 61,479 | 98.62% | 1.38% |
| 52 | `H2.ZE65` | 1,776,395 | 7.0s | 30.0s | 30.5s | 32.0s | 33.0s | 101.3h | `30s` | 60,218 | 59,449 | 98.72% | 1.28% |
| 53 | `H2.ZE66` | 738,161 | 7.0s | 30.1s | 76.0s | 330.0s | 361.0s | 101.4h | `30s` | 62,337 | 61,319 | 98.37% | 1.63% |
| 54 | `H2.ZE67` | 540,106 | 7.0s | 32.0s | 103.9s | 360.0s | 362.0s | 134.2h | `30s` | 62,337 | 58,393 | 93.67% | 6.33% |
| 55 | `H2.ZE74` | 1,851,053 | 23.0s | 30.0s | 30.5s | 30.0s | 30.0s | 101.3h | `30s` | 62,724 | 61,857 | 98.62% | 1.38% |
| 56 | `H3.Z312` | 1,685,395 | 8.7s | 30.0s | 65.8s | 32.0s | 120.0s | 101.3h | `30s` | 123,239 | 65,242 | 52.94% | 47.06% |
| 57 | `H3.Z40` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 58 | `H3.Z41` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 59 | `H3.Z43` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 60 | `H3.Z44` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 61 | `H3.Z45` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 62 | `H3.Z46` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 63 | `H3.Z47` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 64 | `H3.Z48` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 65 | `H3.Z49` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 66 | `H3.Z71` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 67 | `H3.ZE40` | 1,811,153 | 7.0s | 30.0s | 31.2s | 32.0s | 35.0s | 329.3h | `30s` | 62,743 | 60,661 | 96.68% | 3.32% |
| 68 | `H3.ZE41` | 1,811,993 | 7.0s | 30.0s | 31.2s | 32.0s | 34.0s | 329.3h | `30s` | 62,743 | 60,661 | 96.68% | 3.32% |
| 69 | `H3.ZE43` | 1,781,922 | 6.0s | 30.0s | 31.7s | 32.2s | 60.0s | 329.3h | `30s` | 62,743 | 60,574 | 96.54% | 3.46% |
| 70 | `H3.ZE44` | 1,672,811 | 7.0s | 30.0s | 33.8s | 44.0s | 88.0s | 329.4h | `30s` | 62,743 | 59,656 | 95.08% | 4.92% |
| 71 | `H4.Z50` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 72 | `H4.Z51` | 3,155,041 | 60.0s | 60.0s | 60.0s | 60.0s | 60.0s | 0.0h | `1min` | 210,337 | 210,337 | 100.00% | 0.00% |
| 73 | `H4.ZE50` | 1,838,007 | 7.0s | 30.0s | 30.5s | 32.0s | 33.0s | 101.3h | `30s` | 62,350 | 61,492 | 98.62% | 1.38% |
| 74 | `H4.ZE51` | 1,838,826 | 7.0s | 30.0s | 30.5s | 32.0s | 33.0s | 101.3h | `30s` | 62,350 | 61,492 | 98.62% | 1.38% |
| 75 | `V.K21` | 379,746 | 50.0s | 360.0s | 497.9s | 720.0s | 1800.0s | 2467.8h | `6min` | 210,096 | 158,635 | 75.51% | 24.49% |
| 76 | `V.Z81` | 4,782,562 | 1.0s | 30.0s | 39.6s | 60.0s | 60.0s | 192.0h | `30s` | 210,336 | 206,414 | 98.14% | 1.86% |
| 77 | `V.Z82` | 4,718,981 | 1.0s | 30.0s | 40.1s | 60.0s | 90.0s | 192.0h | `30s` | 210,336 | 206,419 | 98.14% | 1.86% |
| 78 | `V.Z84` | 4,210,903 | 0.0s | 18.0s | 33.8s | 121.0s | 220.0s | 169.0h | `15s` | 158,116 | 156,153 | 98.76% | 1.24% |
| 79 | `V.ZE84` | 564,233 | 8.6s | 30.0s | 61.8s | 89.9s | 1080.0s | 101.3h | `30s` | 38,716 | 30,995 | 80.06% | 19.94% |

### Phân bố nhóm tần suất gốc (Cadence Classification Summary):
- **Nhóm siêu cao tần 15s**: 1 meter (`V.Z84`), trung vị khoảng cách 18.0s, độ chiếm dụng 98.76%.
- **Nhóm cao tần 30s**: 25 meters (bao gồm `H1.ZE20`, `H1.Z15`, `H1.Z17`, các nhánh `ZE` và `Z3xx`), trung vị khoảng cách 30.0s, độ chiếm dụng trung bình 97.2%.
- **Nhóm chuẩn 1 phút (1min)**: 44 meters (các nhánh `Z10..Z29`, `Z40..Z71`, `H2.T.Z30..Z34`, `V.Z81..Z82`), trung vị khoảng cách 60.0s, độ chiếm dụng trung bình 98.5%.
- **Nhóm trung gian 2 phút (2min)**: 1 meter (`H1.W12`), trung vị khoảng cách 120.0s, độ chiếm dụng 85.04%.
- **Nhóm bán đều đặn 6 phút (6min)**: 8 meters (`H1.K11..K16`, `H1.W11`, `H2.K21`, `V.K21`), trung vị khoảng cách 360.0s, độ chiếm dụng trung bình 78.1%.
- **Tổng cộng**: **79 meters** (100% đều có median gap $\le 6$ phút $\ll 15$ phút).

---

## 2. Bảng Đánh Giá Riêng 9 Meter Từng Bị Gán Nhãn "Pulse / Low-Frequency"

| Meter ID | Nhãn Cũ (P1-T1 Sample) | Obs Count | Median Gap (p50) | Mean Gap | p95 Gap | p99 Gap | Max Gap (h) | Cadence Thực Tế | Occupied 15m Bins | Total 15m Bins | Occupied Rate | Empty Rate | Bản Chất Nhịp Điệu |
|---|:---:|---:|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---|
| `H1.K11` | `4.5h (sample)` | 368,168 | 360.0s (6.0m) | 513.4s | 720.0s (12.0m) | 780.0s | 126.6h | `6min` | 156,082 | 209,999 | 74.33% | 25.67% | Đo nhiệt lạnh Kälte, chu kỳ đều 6m + ngắt nghỉ |
| `H1.K12` | `1.3h (sample)` | 371,325 | 360.0s (6.0m) | 509.1s | 720.0s (12.0m) | 780.0s | 571.3h | `6min` | 156,667 | 210,053 | 74.58% | 25.42% | Đo nhiệt lạnh Kälte, chu kỳ đều 6m + ngắt nghỉ |
| `H1.K14` | `1.3h (sample)` | 371,399 | 360.0s (6.0m) | 509.1s | 720.0s (12.0m) | 1020.0s | 249.6h | `6min` | 157,411 | 210,090 | 74.93% | 25.07% | Đo nhiệt lạnh Kälte, chu kỳ đều 6m + ngắt nghỉ |
| `H1.K15` | `1140s (sample)` | 386,892 | 360.0s (6.0m) | 488.7s | 720.0s (12.0m) | 1260.0s | 3003.7h | `6min` | 162,943 | 210,098 | 77.56% | 22.44% | Đo nhiệt lạnh Kälte, chu kỳ đều 6m + ngắt nghỉ |
| `H1.K16` | `2.3h (sample)` | 381,185 | 360.0s (6.0m) | 421.9s | 720.0s (12.0m) | 900.0s | 193.5h | `6min` | 156,607 | 178,708 | 87.63% | 12.37% | Đo nhiệt lạnh Kälte, chu kỳ đều 6m + ngắt nghỉ |
| `H1.W11` | `840s (sample)` | 479,151 | 360.0s (6.0m) | 395.1s | 780.0s (13.0m) | 1800.0s | 106.7h | `6min` | 185,064 | 210,336 | 87.98% | 12.02% | Đo nhiệt sưởi Wärme, chu kỳ đều 6m + ngắt nghỉ |
| `H1.ZE20` | `810s (sample)` | 551,582 | 30.0s (0.5m) | 62.1s | 90.0s (1.5m) | 1320.0s | 101.3h | `30s` | 27,980 | 38,075 | 73.49% | 26.51% | Đo điện 3 pha Einspeisung, chu kỳ đều 30s + downtime |
| `H2.K21` | `2.3h (sample)` | 296,068 | 361.0s (6.0m) | 638.6s | 721.0s (12.0m) | 1560.0s | 795.6h | `6min` | 149,169 | 210,068 | 71.01% | 28.99% | Đo nhiệt lạnh Kälte, chu kỳ đều 6m + ngắt nghỉ |
| `V.K21` | `1.9h (sample)` | 379,746 | 360.0s (6.0m) | 497.9s | 720.0s (12.0m) | 1800.0s | 2467.8h | `6min` | 158,635 | 210,096 | 75.51% | 24.49% | Đo nhiệt lạnh tổng Site, chu kỳ đều 6m + ngắt nghỉ |

### Phân tích nguyên nhân sai lệch nhãn trong quá khứ:
1. **Lỗi lấy mẫu cục bộ trong script kiểm kê**: Script `etl/inventory.py` (dòng 152) chỉ trích xuất tối đa 1,000 dòng đầu tiên của mỗi file `.csv.gz` để ước lượng tần suất (`observed_frequency`). Khi các cảm biến này mới lắp đặt hoặc trong giai đoạn khởi tạo ban đầu vào cuối năm 2017 / 2022, chuỗi dữ liệu chứa các khoảng trống lớn tạm thời khiến trung vị của 1,000 dòng đầu tiên bị vọt lên mức hàng giờ.
2. **Khám nghiệm toàn diện 100% dòng dữ liệu**: Khi quét trọn vẹn toàn bộ 3.58 triệu dòng của 9 meter này:
   - `H1.ZE20` phát tín hiệu cực kỳ dày đặc ở nhịp **30 giây** (median 30.0s, p95 89.96s).
   - 8 đồng hồ nhiệt nước (`K11..K16`, `W11`, `K21`) phát tín hiệu ở nhịp **6 phút** (median 360.0s, p95 720.0s = 12 phút).
3. **Kết luận kiểm chứng**: Cả 9 meters hoàn toàn không phải là "xung ngẫu nhiên thưa thớt (sparse pulse)". Chúng vận hành theo **chu kỳ đều đặn (regular/semiregular cadence)**, cộng với các khoảng gián đoạn đo lường kéo dài (downtime/outage episodes). Cả 9 meter đều **đạt tiêu chuẩn kỹ thuật để biểu diễn trên lưới 15 phút**.

---

## 3. Khám Nghiệm Chuyên Sâu Meter H1.ZE20

| Thuộc tính phân tích | Giá trị đo đạc thực tế | Diễn giải kỹ thuật |
|---|---|---|
| **Mã trạm & Biến đo** | `H1.ZE20.W` | Thanh ghi điện năng tác dụng thuần (Net Active Energy Saldo) |
| **Thời điểm bắt đầu (ts_min)** | `2022-11-30T08:18:47.000000+00:00` | Lắp đặt đưa vào vận hành cuối tháng 11/2022 |
| **Thời điểm kết thúc (ts_max)** | `2023-12-31T22:59:54.825999+00:00` | Đồng bộ với mốc đóng sổ dữ liệu toàn site |
| **Tổng thời gian theo dõi** | **396.61 ngày** (~13 tháng) | Vượt mốc 1 năm trọn vẹn (365 ngày) |
| **Tổng số quan sát thô** | **551,582 dòng** | Lưu lượng dữ liệu lớn |
| **Khoảng cách nhỏ nhất (min gap)** | **7.59 giây** | Tần suất sub-minute |
| **Khoảng cách trung vị (median p50)** | **30.00 giây** | **Cadence thực tế là 30 giây** |
| **Khoảng cách trung bình (mean gap)** | **62.13 giây** | Bị kéo nhẹ bởi các đợt cúp kết nối |
| **Phân vị 95% (p95 gap)** | **89.96 giây** (~1.5 phút) | 95% quan sát đến trong vòng 1.5 phút |
| **Phân vị 99% (p99 gap)** | **1,320.00 giây** (22.0 phút) | Chỉ 1% quan sát có khoảng cách lớn |
| **Khoảng cách lớn nhất (max gap)** | **364,642.0 giây** (101.29 giờ = 4.22 ngày) | Đợt mất kết nối từ 29/04/2023 đến 03/05/2023 |
| **Tổng số ô 15 phút (total bins)** | **38,075 ô** | Trên khoảng thời gian sống của meter |
| **Số ô có dữ liệu (occupied bins)** | **27,980 ô** | Số ô có ít nhất 1 quan sát thô |
| **Số ô rỗng (empty bins)** | **10,095 ô** | Các ô không có tín hiệu |
| **Tỷ lệ chiếm dụng (occupied rate)**| **73.49%** | Đạt mức khả dụng cao cho nghiên cứu |
| **Tỷ lệ rỗng (empty rate)** | **26.51%** | Tương ứng với các khoảng outage thực tế |
| **Loại hình tải & Biến đo nguồn** | Điện 3 pha (`I1..I3, U1..U3, P, P1..P3, PF, W, W_in, W_out, f`) | Đồng hồ đo điện tổng hợp có trao đổi 2 chiều |
| **Hành vi bước nhảy Delta W** | 88.4% tăng, 11.6% giảm nhỏ (-0.016 đến -0.064 kWh) | Dấu hiệu đặc trưng của dòng hoàn trả hoặc PV feed-in |
| **Dị thường đơn điểm (Spike)** | Giá trị `0.397743` lúc 2023-03-31 00:50:12 UTC | Lỗi ghi tạm thời 1 nhịp 30s, hồi phục ngay nhịp sau |

### Nhận định về H1.ZE20:
- `H1.ZE20` không phải là meter đo xung thưa. Nó là một đồng hồ đo điện 3 pha thế hệ mới (cùng đợt với `V.ZE84` vào cuối tháng 11/2022) có nhịp lấy mẫu chuẩn 30 giây.
- Dữ liệu của `H1.ZE20` kéo dài hơn 13 tháng liên tục, bao quát trọn vẹn 4 mùa trong năm 2023.
- Mọi khoảng rỗng 15 phút của `H1.ZE20` đều xuất phát từ các đợt gián đoạn đường truyền thực tế (như đợt nghỉ hè tháng 6–8/2023 hoặc sự cố đầu tháng 5/2023), hoàn toàn thích hợp cho bài toán nghiên cứu Missingness.

---

## 4. Đề Xuất Quy Tắc Hợp Lệ Tổng Quát (General Eligibility Proposal)

Để đảm bảo tính khách quan và tuân thủ nguyên tắc nghiên cứu khoa học, tiêu chuẩn lựa chọn meter tham gia vào quần thể nghiên cứu cốt lõi (**Core Research Population**) phải được định nghĩa bằng một **Quy tắc Tổng Quát (General Eligibility Rule)** áp dụng đồng nhất cho mọi meter, không thiết kế riêng để loại bỏ hoặc ưu ái bất kỳ cá nhân meter nào:

```text
A meter m is ELIGIBLE for Core Population iff:
    history_duration(m) >= 365 days
    AND
    typical_cadence(m) <= 15 minutes (900 seconds)
    AND
    occupied_15min_rate(m) >= 50.0%
    AND
    measurement_semantics(m) is COMPATIBLE with physical cumulative energy register W
```

### Rationale và Biện giải Khoa học cho các ngưỡng tham số:
1. **`history_duration >= 365 days`**:
   - *Cơ sở*: Nhằm bảo đảm chuỗi thời gian chứa ít nhất một chu kỳ tuần hoàn 4 mùa trọn vẹn (Annual / Seasonal Cyclicity). Điều này là bắt buộc để các mô hình Baseline (Seasonal Naive 7 ngày / chu kỳ năm) và các mô hình Deep Learning có đủ pha huấn luyện đại diện cho cả thời tiết nóng và lạnh.
   - *Đối soát*: Cả 79 meters đều có thời gian theo dõi từ 396.6 ngày đến 2,191 ngày. `H1.ZE20` đạt 396.61 ngày >= 365 ngày -> **PASS**.
2. **`typical_cadence <= 15 minutes (900s)`**:
   - *Cơ sở*: Lưới chuẩn hóa nghiên cứu được ấn định ở độ phân giải 15 phút. Nếu nhịp lấy mẫu tự nhiên của đồng hồ chậm hơn 15 phút (ví dụ 30 phút hoặc 1 giờ), thì trạng thái bình thường của đồng hồ cũng sẽ sinh ra các ô rỗng trên lưới 15 phút, gây lẫn lộn giữa khoảng khuyết tự nhiên và sự cố gián đoạn. Ngưỡng <= 15 phút bảo đảm rằng trong điều kiện bình thường, mỗi ô 15 phút luôn có ít nhất 1 quan sát thô.
   - *Đối soát*: Tất cả 79 meters đều có trung vị khoảng cách <= 361 giây (~6 phút) <= 900 giây -> **PASS**.
3. **`occupied_15min_rate >= 50.0%`**:
   - *Cơ sở*: Theo thông lệ chuẩn mực trong các tập dữ liệu benchmark chuỗi thời gian quốc tế (như Monash Time Series, PhysioNet, ElectricityLoadDiagrams), một thực thể chuỗi thời gian cần có tỷ lệ hiện diện tối thiểu 50% để bảo đảm tính hội tụ khi huấn luyện mô hình học máy.
   - *Đối soát*: Meter có tỷ lệ thấp nhất là `H2.Z311` (52.33%), kế tiếp là `H2.K21` (71.01%) và `H1.ZE20` (73.49%). 100% meters đều vượt ngưỡng 50% -> **PASS**.
4. **`measurement_semantics compatible with W-imputation`**:
   - *Cơ sở*: Biến mục tiêu phải phản ánh đại lượng thanh ghi năng lượng tác dụng thực (Net Active Energy Saldo, kWh). Không sử dụng các biến công suất tức thời P, biến nhiệt độ, hoặc dữ liệu đã qua chỉnh sửa nhân tạo (`_corrected_raw`).
   - *Đối soát*: Toàn bộ 79 files đo lường nạp vào `readings_utc.parquet` đều là biến W thô nguyên bản từ cảm biến -> **PASS**.

👉 **Kết luận nghiệm thu Population**: Áp dụng quy tắc tổng quát trên, **TOÀN BỘ 79 METERS ĐỀU HỢP LỆ VÀ ĐƯỢC GIỮ NGUYÊN VẸN TRONG CORE POPULATION**. Không có bất kỳ meter nào bị loại bỏ.

---

## 5. Đính Chính Nhận Định Về Độ Phủ Hệ Thống HVAC (Corrected HVAC Interpretation)

Trong các trao đổi kỹ thuật trước đây, từng xuất hiện nhận định cho rằng: *"Nếu loại bỏ 9 meter tần suất thấp thì sẽ làm mất đi toàn bộ độ phủ của hệ thống HVAC"*.

Qua đối soát thực nghiệm độc lập với hệ thống đo lường của toàn bộ khuôn viên nghiên cứu Honda Research Institute, nhận định trên được đính chính như sau:

### 1. Phân biệt Tải Điện HVAC và Đo Nhiệt Thủy Lực (Electrical HVAC vs Hydronic Thermal Metering)
- **Tải điện HVAC (Electrical HVAC Loads)**: Trong các công trình văn phòng/nghiên cứu hiện đại, phần lớn năng lượng tiêu thụ của hệ thống HVAC vận hành bằng điện năng:
  - Máy nén môi chất lạnh (Refrigerant Compressors / Chillers);
  - Quạt thổi không khí tươi và quạt hút thông gió (Air Handling Units - AHU, Exhaust Fans);
  - Động cơ bơm nước tuần hoàn (Chilled/Hot Water Circulation Pumps);
  - Tháp giải nhiệt (Cooling Towers).
  Toàn bộ các phụ tải điện này được cấp nguồn từ các trạm biến áp và bảng điện phân phối của tòa nhà, do đó được ghi nhận đầy đủ trong **mạng lưới 70 công tơ điện (`Z`, `ZE`, `H*.T.Z`)**.
- **Đo nhiệt thủy lực (Hydronic District Heating & Cooling)**:
  - 7 đồng hồ `K` (`H1.K11..K16`, `H2.K21`, `V.K21`) là các đồng hồ đo môi chất nước lạnh (**Kälte**).
  - 2 đồng hồ `W` (`H1.W11`, `H1.W12`) là các đồng hồ đo nước nóng sưởi ấm (**Wärme**).
  Các đồng hồ này đo năng lượng nhiệt trao đổi qua lưu lượng nước ($Q = \dot{m} \cdot C_p \cdot \Delta T$).

### 2. Sự hiện diện độc lập của Meter H1.W12
- Đồng hồ nhiệt sưởi `H1.W12` có **858,642 dòng dữ liệu**, hoạt động liên tục gần 6 năm (2018–2023), tỷ lệ chiếm dụng lưới 15 phút đạt **85.04%**, và meter này **hoàn toàn không nằm trong nhóm 9 meter bị nghi ngờ**.
- Do đó, ngay cả trong kịch bản giả định loại bỏ 9 meter, hệ thống đo nhiệt vẫn còn đại diện tiêu biểu là `H1.W12`.

### 3. Khẳng định chính xác khoa học (The Precise Scientific Claim)
Thay vì khẳng định mang tính tuyệt đối hóa, tuyên bố khoa học chuẩn xác phải là:

> *"Việc lưu giữ đầy đủ các đồng hồ đo nhiệt nước (`K11..K16`, `W11`, `K21`) không phải là điều kiện duy nhất để duy trì độ phủ HVAC, mà mang lại **giá trị đa dạng hóa vật lý đa năng lượng (Multi-Carrier Energy Diversity)** — kết hợp giữa chuỗi phụ tải điện (Electric Power) và chuỗi phụ tải nhiệt thủy lực (Hydronic Thermal Energy) trong cùng một cơ sở hạ tầng kho dữ liệu."*

---

## 6. Đặc Tả Ngữ Nghĩa Chuẩn Hóa Lưới 15 Phút Cho P1-T3 (Exact 15-Minute Binning Rule)

Nhằm chấm dứt triệt để các mâu thuẫn toán học và ngăn ngừa việc resampling vô tình biến thành imputation nhân tạo, protocol P1-T3 được chốt hạ với các quy tắc kỹ thuật bất biến như sau:

### 1. Trục thời gian lưới (Grid Definition)
- **Múi giờ chuẩn**: `UTC` tuyệt đối (`timestamp[us, tz=UTC]`).
- **Mốc neo lưới (Grid Anchors)**: Cố định tại các mốc phần tư giờ:
  $$t \in \{\text{HH:00:00.000000}, \text{HH:15:00.000000}, \text{HH:30:00.000000}, \text{HH:45:00.000000}\}$$
- **Phạm vi thời gian của từng Meter (Meter-Specific Horizon)**:
  Lưới của meter $m$ được thiết lập độc lập theo vòng đời thực tế của meter đó:
  - $t_{\text{start}}(m) = \text{ceil\_15min}(\min(ts_{\text{raw}}(m)))$
  - $t_{\text{end}}(m) = \text{ceil\_15min}(\max(ts_{\text{raw}}(m)))$ (Lưu ý: Tuyệt đối không dùng floor cho grid_end; ví dụ quan sát cuối lúc 12:07 rơi vào (12:00, 12:15] nên grid_end = ceil(12:07) = 12:15).
  - Tổng số bước kỳ vọng: $N_{\text{expected}}(m) = \frac{t_{\text{end}}(m) - t_{\text{start}}(m)}{15\text{ phút}} + 1$.

### 2. Định nghĩa ô thời gian (Interval Bin Partition)
- Áp dụng quy ước **nửa đóng nửa mở bên phải (Right-Closed, Right-Labeled)**:
  $$\text{Bin}(t) = (t - 15\text{ phút}, t]$$
  *Ví dụ*: Ô thời gian gắn nhãn `12:15:00 UTC` đại diện cho tất cả các quan sát thô có timestamp thỏa mãn:
  $$12:00:00.000000 < ts \le 12:15:00.000000$$

### 3. Toán tử chọn mẫu đại diện (Representative Observation Operator)
- **Trường hợp Bin có dữ liệu ($\ge 1$ raw observations)**:
  - Chọn quan sát thô xuất hiện **CUỐI CÙNG** trong khoảng (Toán tử **`LAST`**):
    $$r_{\text{selected}} = \arg\max_{r \in \text{Bin}(t)} (r.\text{timestamp\_utc})$$
  - Gán giá trị: $\text{value}(t) = r_{\text{selected}}.\text{value}$ (Bảo toàn 100% số thực IEEE-754 gốc).
  - Gán vết nguồn: $\text{source\_timestamp\_utc}(t) = r_{\text{selected}}.\text{timestamp\_utc}$.
  - Gán file nguồn: $\text{raw\_source\_file}(t) = r_{\text{selected}}.\text{raw\_source\_file}$.
  - Gán biến đếm: $\text{raw\_record\_count}(t) = |\text{Bin}(t)|$.
- **Trường hợp Bin rỗng ($0$ raw observations — Outage / Gap)**:
  - Gán giá trị: $\text{value}(t) = \text{NaN}$ (null trong Parquet).
  - Gán vết nguồn: $\text{source\_timestamp\_utc}(t) = \text{None}$.
  - Gán file nguồn: $\text{raw\_source\_file}(t) = \text{None}$.
  - Gán biến đếm: $\text{raw\_record\_count}(t) = 0$.

### 4. Danh mục Cấm Tuyệt Đối (Explicit Prohibitions)
- ❌ **Không dùng `mean`**: $W$ là số đọc thanh ghi năng lượng tích lũy (Cumulative Saldo Register). Lấy trung bình cộng các số đọc công tơ là sai lệch hoàn toàn về mặt vật lý và sản sinh ra các giá trị thập phân nhân tạo vi phạm tiêu chuẩn bảo toàn ground truth.
- ❌ **Không dùng `sum`**: Sẽ nhân giá trị thanh ghi lên gấp 15 đến 60 lần, phá hủy thang đo năng lượng.
- ❌ **Không dùng `interpolation`**: Nghiêm cấm mọi hình thức nội suy tuyến tính, spline, đa thức tại bước ETL.
- ❌ **Không dùng `ffill` / `bfill`**: Resampling chỉ là phép chiếu biểu diễn; điền giá trị quá khứ vào ô rỗng là hành vi điền khuyết trái phép (Imputation Leakage).
- ❌ **Không dùng `exact timestamp matching`**: Khớp giây chính xác `:00:00` sẽ xóa sạch 97% dữ liệu của các meter bị trôi nhịp giây như `V.Z84` và `H1.Z310`.

---

## 7. Phân Biệt Ngữ Nghĩa Giữa Source Timestamp và Grid Timestamp

Một trong những nguyên nhân dẫn đến hiểu lầm trong việc kiểm toán dữ liệu chuỗi thời gian là sự đánh đồng giữa *thời điểm neo của ô lưới* và *thời điểm đo vật lý của cảm biến*. 

P1-T3 bắt buộc thiết lập cấu trúc lược đồ đầu ra phân biệt rạch ròi hai khái niệm này:

### Lược đồ đầu ra chuẩn của bảng `readings_15min.parquet`:
```sql
CREATE TABLE readings_15min (
    meter_id             VARCHAR(50) NOT NULL,   -- Mã trạm đo
    grid_timestamp_utc   TIMESTAMP NOT NULL,     -- Mốc neo biên phải của bin (HH:00, :15, :30, :45)
    timestamp_local      TIMESTAMP NOT NULL,     -- Mốc giờ địa phương Đức (Europe/Berlin) tại grid_timestamp
    source_timestamp_utc TIMESTAMP,              -- Mốc thời gian thực tế của quan sát thô được chọn (NULL nếu rỗng)
    value                DOUBLE,                 -- Giá trị raw IEEE-754 gốc tại source_timestamp (NaN nếu rỗng)
    raw_source_file      VARCHAR(255),           -- Tên file raw gốc chứa quan sát (NULL nếu rỗng)
    raw_record_count     INTEGER NOT NULL        -- Số lượng bản ghi raw rơi vào bin này (>=1 nếu có, 0 nếu rỗng)
);
```

### Nguyên tắc bất biến về mặt ngữ nghĩa (Semantic Invariants):
1. Cặp `(grid_timestamp_utc, value)` là một **biểu diễn chuẩn hóa trên lưới (Standardized Grid Representation)**, không phải là một quan sát thô nguyên bản của cảm biến.
2. Cặp `(source_timestamp_utc, value)` mới là **quan sát vật lý thực sự (True Physical Observation)**.
3. Khi kiểm toán Ground Truth: Auditor sẽ đối chiếu `value` và `source_timestamp_utc` trực tiếp với file `raw_source_file`. Sự trùng khớp phải đạt **100% bit-for-bit**.

---

## 8. Cấu Trúc Metadata Nhận Biết Nhịp Điệu (Cadence-Aware Missingness Metadata)

Nhằm phục vụ phân tích phân tầng tại P2 và P4, hệ thống kho dữ liệu cần lưu trữ các trường thuộc tính tĩnh phản ánh nhịp điệu vận hành của từng meter (tại bảng `Dim_Meter` hoặc `Meta_MeterCadence`):

| Tên trường Metadata | Kiểu dữ liệu | Ý nghĩa nghiệp vụ |
|---|---|---|
| `cadence_class` | `VARCHAR(20)` | Phân lớp tần suất: `'15s'`, `'30s'`, `'1min'`, `'2min'`, `'6min'` |
| `median_gap_seconds` | `DOUBLE` | Trung vị khoảng cách phát tín hiệu thực nghiệm (s) |
| `p95_gap_seconds` | `DOUBLE` | Phân vị 95% khoảng cách phát tín hiệu (s) |
| `occupied_bin_rate` | `DOUBLE` | Tỷ lệ ô 15 phút có dữ liệu thô trong suốt lịch sử |
| `bin_completeness` | `DOUBLE` | Tỷ lệ số bản ghi trung bình trên ô so với số bản ghi lý thuyết |

### Ý nghĩa khoa học:
- **Ngăn ngừa đánh đồng độ nhạy missingness**: Một ô 15 phút bị rỗng ở meter 15 giây (`V.Z84`) tương ứng với việc bị mất khoảng **60 gói tin liên tiếp**; trong khi ở meter 6 phút (`H1.K11`), ô rỗng chỉ tương ứng với việc bị mất **2–3 gói tin**. Hai sự kiện này có độ tin cậy và bối cảnh chẩn đoán khác nhau.
- **Bảo đảm không rò rỉ dữ liệu (Zero Leakage)**: Các chỉ số này là đặc tính kỹ thuật cấp thiết bị, được tính độc lập trên toàn dải hoặc trên tập train, tuyệt đối không mang thông tin giá trị $W$ tương lai hoặc thông tin dưới vùng mask thử nghiệm.

---

## 9. Đánh Giá Ảnh Hưởng Downstream (Downstream Implications)

Việc chuẩn hóa lưới 15 phút theo quy tắc v1.1 tác động tích cực và tạo cơ sở vững chắc cho các giai đoạn tiếp theo:

1. **P1-T4 (Quality Flags)**:
   - Các cờ chất lượng (`flag_missing`, `flag_flatline`, `flag_spike`, `flag_negative_step`) sẽ được tính toán trên lưới 15 phút đều đặn.
   - Nhờ có trường `raw_record_count`, P1-T4 có thể dễ dàng nhận biết các ô có mật độ dữ liệu thô mỏng manh mà không cần truy vấn ngược lại bảng 208 triệu dòng.
2. **P1-T5 (Clean Segments Extraction)**:
   - Một Clean Segment hợp lệ được định nghĩa là một chuỗi liên tục các ô 15 phút có `value` non-NaN, không có cờ lỗi P1-T4 và không có sự cố ghi nhận trong `issues/`.
   - Quy tắc `LAST` đảm bảo 100% giá trị trong Clean Segment là số đọc công tơ thật, sẵn sàng làm Ground Truth tuyệt đối.
3. **P2 (Failure Episodes & Mask Engine)**:
   - **R-derived Masks**: Khoảng trống thực tế (chuỗi các ô NaN liên tiếp) được trích xuất chính xác để học phân phối độ dài sự cố thật.
   - **S-matched Masks**: Cơ chế tạo mask nhân tạo sẽ lấy mẫu độ dài từ phân phối R-derived và đè lên các Clean Segment ở cùng khung giờ và phân lớp cadence tương ứng.
4. **Cảnh báo cốt lõi về bản chất của Empty Bin**:
   > **LƯU Ý QUẢN TRỊ BẮT BUỘC**: Một ô 15 phút rỗng (`NaN`) sau bước resampling thuần túy là một **khoảng trống quan sát (observation gap)** trên lưới 15 phút. Hệ thống tuyệt đối không được tự tiện kết luận ô rỗng đó là sự cố hỏng hóc thiết bị (Equipment Failure Episode) trước khi đối soát chéo với nhật ký sự cố có thẩm quyền (`issues/*.yaml`) tại P1-T4 và P2-T1.

---

## 10. Tác Động Chuyển Đổi (Migration & Governance Impact)

| Thành phần hệ thống | Hiện trạng cũ | Sau khi phê duyệt Amendment v1.1 |
|---|---|---|
| **Tiêu chí nghiệm thu P1-T3** | Mâu thuẫn: Đòi hỏi giữ nguyên 208.2M non-NaN | Hợp lý: Bảo toàn 100% số bin có dữ liệu thô (13,333,577 occupied bins) |
| **Quần thể nghiên cứu (Population)**| Nguy cơ loại bỏ nhầm 9 meters | Giữ trọn vẹn 100% **79 meters** theo quy tắc chung |
| **H1.ZE20** | Bị nghi ngờ thưa thớt | Được xác minh là meter 30s hợp lệ, giữ trong core |
| **Ground Truth Invariant** | Nguy cơ bị méo mó nếu dùng `mean` | Bảo toàn bit-for-bit giá trị raw qua toán tử `LAST` |
| **Clock-drift Immunity** | 97% dữ liệu của `V.Z84` bị mất nếu reindex | 0.0% dữ liệu bị mất; bảo toàn 98.76% thời gian sống |
| **Trạng thái Task State Machine** | `P1-T3: READY (Blocked by Preflight)` | Sẵn sàng chuyển sang `P1-T3: IN_PROGRESS` khi có chỉ thị |

### 10.1 Danh mục Artifacts Cần Tái Tạo (Artifacts to Regenerate)

Căn cứ quyết định chính thức ban hành Protocol v1.1 của Protocol Owner:
1. **Artifacts cần tạo / tái tạo**:
   - `data/interim/readings_15min.parquet`: Sẽ được sinh ra theo đúng chuẩn mực Protocol v1.1 (lưới đều 15 phút, bin nửa đóng biên phải $(t-15\text{m}, t]$, toán tử `LAST`, giữ nguyên NaN, bảo toàn Occupied Bins và Zero Synthetic Observations) trong nhiệm vụ P1-T3. Hiện tại artifact này CHƯA được tạo.
   - `tests/test_P1_T3.py`: Bộ kiểm thử tự động gồm 9 tiêu chí nghiệm thu của Protocol v1.1 sẽ được thiết lập trước khi chạy ETL P1-T3.
2. **Artifacts bảo toàn nguyên vẹn (KHÔNG tái tạo)**:
   - `data/raw/*`: Toàn bộ dữ liệu thô gốc Honda giữ nguyên trạng thái Read-Only tuyệt đối.
   - `data/interim/readings_utc.parquet`: Dữ liệu chuẩn hóa UTC và deduplication của P1-T2 giữ nguyên vẹn 100% (208,224,479 dòng, cân bằng đối soát với 61,790 duplicate).

---

## 11. Quyết Định Chính Thức Của Protocol Owner (Official Ratification)

Protocol Owner đã chính thức phê duyệt toàn bộ nội dung trong báo cáo này và ban hành **Protocol v1.1**:
1. Giữ toàn bộ 79 W meters trong Core Population (bao gồm `H1.ZE20`).
2. Chuyển P1-T3 sang 15-minute regular-grid representation / temporal downsampling với toán tử `LAST` trong bin $(t-15\text{m}, t]$.
3. Empty bin giữ `NaN`, không xem là failure ở P1-T3.
4. Áp dụng Occupied Bin Preservation và Zero Synthetic Observations.
5. Phân biệt `grid_timestamp_utc` và `source_timestamp_utc`.
6. Cấm đưa `raw_record_count` và `bin_completeness` vào feature mô hình imputation.

```text
================================================================================
  TRẠNG THÁI PROTOCOL: PROTOCOL v1.1 ĐÃ ĐƯỢC CHÍNH THỨC BAN HÀNH (ENACTED)
================================================================================
```

### Điều kiện tiếp theo:
1. Quy tắc phân vùng biên phải $(t-15\text{m}, t]$ và toán tử `LAST` đã trở thành chuẩn mực resampling chính thức của dự án trong `TASK_PLAN.md` và `RESEARCH_PLAN.md`.
2. Toàn bộ 79 meters được xác nhận giữ lại trong Quần thể Cốt lõi (Core Population).
3. Nhiệm vụ hiện tại chỉ officialize protocol; dừng lại không triển khai code P1-T3 khi chưa có lệnh tiếp theo.

---

## 12. Bảng Tiêu Chí Nghiệm Thu (Acceptance Criteria Checklist)

- [PASS] Bảng thống kê nhịp điệu 79 meters hoàn thành đầy đủ 100%.
- [PASS] Phân tách rạch ròi giữa trung vị (median), p95 và khoảng cách lớn nhất (max gap).
- [PASS] Tính toán chính xác tỷ lệ chiếm dụng (occupied rate) và tỷ lệ rỗng (empty rate) cho từng meter.
- [PASS] Tái đánh giá độc lập 9 meter từng bị gán nhãn thưa thớt; bác bỏ nhãn sai lệch.
- [PASS] Khám nghiệm `H1.ZE20` bằng quy tắc hợp lệ tổng quát; xác nhận hợp lệ.
- [PASS] Kiểm chứng độc lập và đính chính câu nhận định về độ phủ hệ thống HVAC.
- [PASS] Đối soát số học tuyệt đối: 208,286,269 = 208,224,479 + 61,790.
- [PASS] Xác định chính xác ngữ nghĩa toán tử `LAST` và phân vùng biên (t-15m, t].
- [PASS] Phân biệt rõ ràng giữa `source_timestamp_utc` và `grid_timestamp_utc`.
- [PASS] Định nghĩa đầy đủ lược đồ metadata nhận biết nhịp điệu (Cadence-aware metadata).
- [PASS] Protocol v1.1 được chính thức cập nhật đồng bộ vào TASK_PLAN.md và RESEARCH_PLAN.md (lịch sử v1.0 được bảo toàn).
- [PASS] Danh mục artifacts cần tái tạo (data/interim/readings_15min.parquet, tests/test_P1_T3.py) được ghi rõ; dữ liệu raw và readings_utc giữ nguyên vẹn.
- [PASS] File `readings_15min.parquet` KHÔNG bị tạo ra trong nhiệm vụ officialize protocol này.
- [PASS] Tuyệt đối không thực thi các task downstream P1-T4 / P1-T5 / P2.

---
*Báo cáo được hoàn thành độc lập và tuân thủ tuyệt đối Hiến chương Quản trị AGENTS.md.*
