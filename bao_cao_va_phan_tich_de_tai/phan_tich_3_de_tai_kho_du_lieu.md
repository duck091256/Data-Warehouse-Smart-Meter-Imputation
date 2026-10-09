# Phân tích chi tiết 3 đề tài kho dữ liệu

Ba đề tài này đều có thể phát triển thành paper tốt, nhưng **độ khó về dữ liệu và khoảng trống khoa học rất khác nhau**. Sau khi đối chiếu thêm các công trình 2025–2026, không nên giữ nguyên phiên bản đơn giản của chúng mà cần chỉnh lại để tránh trùng với nghiên cứu đã có.

| Đề tài | Dữ liệu | Novelty có thể đạt | Độ khó | Khả năng hoàn thành | Tiềm năng |
|---|---:|---:|---:|---:|---:|
| **ESG Intelligence DW** | 7/10 | **9.5/10** | 9/10 | 7/10 | **Q1–Q2** |
| **Energy + Weather DW** | **10/10** | 8.5/10 | 6.5/10 | **9.5/10** | **Q2+, có thể Q1** |
| **Corporate Financial Distress DW** | 8.5/10 | 8.5/10 | 7.5/10 | 8.5/10 | **Q2+, có thể Q1** |

Nếu mục tiêu là **khả năng hoàn thành paper Q2 cao nhất**, nên nghiêng về **Energy + Weather**. Nếu muốn **Fintech và cân bằng novelty/khả thi**, chọn **Corporate Financial Distress**. Nếu chấp nhận khó để đổi lấy novelty cao, chọn **ESG**.

---

# 1. ESG Intelligence Data Warehouse

## Tên đề tài nên chỉnh

### Tiếng Anh

**A Longitudinal Multi-source ESG Intelligence Data Warehouse for Corporate Risk Prediction and Disclosure-Inconsistency Detection**

### Tiếng Việt

**Xây dựng kho dữ liệu ESG đa nguồn theo thời gian phục vụ dự báo rủi ro doanh nghiệp và phát hiện bất nhất trong công bố ESG**

Tên này phù hợp hơn “ESG Warehouse for Greenwashing Detection” vì **greenwashing ground truth rất khó có được**, trong khi “disclosure inconsistency” có thể đo được khách quan hơn.

## 1.1. Dữ liệu

Đề tài nên tích hợp ít nhất 4 loại dữ liệu.

### A. Báo cáo ESG/Sustainability

Crawl PDF từ website doanh nghiệp:

```text
Company
 └── ESG / Sustainability Reports
       ├── 2018
       ├── 2019
       ├── 2020
       ├── ...
       └── 2025
```

Dữ liệu cần lấy:

```text
company
year
report
paragraph
ESG pillar
ESG topic
claim
sentiment
commitment
target
numerical ESG value
```

Ví dụ:

> “We aim to reduce carbon emissions by 40% by 2030.”

Trích thành:

```text
company = X
topic = carbon_emission
claim_type = commitment
target = -40%
target_year = 2030
```

### B. Annual report / financial statements

SEC EDGAR rất thuận lợi nếu chọn doanh nghiệp Mỹ.

SEC cung cấp REST API công khai, không cần API key, gồm lịch sử filing và XBRL facts từ 10-K, 10-Q, 8-K...; dữ liệu XBRL còn được chuẩn hóa để so sánh giữa doanh nghiệp và theo thời gian.

Có thể lấy:

```text
Revenue
Net income
Assets
Debt
Cash flow
ROA
ROE
Leverage
```

### C. Tin tức ESG bên ngoài doanh nghiệp

Có thể sử dụng GDELT.

GDELT 2.0 cung cấp Event Database và Global Knowledge Graph đa ngôn ngữ và cập nhật khoảng mỗi 15 phút.

Ví dụ doanh nghiệp tuyên bố:

```text
Company ESG Report:

"Strong commitment to employee safety."
```

nhưng external news:

```text
Factory accident
Worker protest
Regulatory fine
Labor violation
```

Ta có:

\[
Disclosure \neq External\ Evidence
\]

Đây chính là thông tin mà warehouse tạo ra.

### D. Market/financial risk

Kết hợp:

```text
Stock price
Return
Volatility
Drawdown
Trading volume
```

để nghiên cứu:

\[
ESG\ inconsistency_t
\rightarrow
Financial\ Risk_{t+1:t+k}
\]

## 1.2. Kho dữ liệu nên thiết kế như thế nào?

Có thể xây:

```text
                 Dim_Company
                      │
                      ↓
             ┌── Fact_ESGDisclosure
             │
Dim_Time ────┼── Fact_ESGEvent
             │
             ├── Fact_Financial
             │
             └── Fact_Market
                      ↑
                      │
                  Dim_Source
```

Một bảng rất quan trọng là:

### `Fact_ESGDisclosure`

```text
company_id
report_date
ESG_pillar
ESG_topic
claim_type
sentiment
commitment_score
numeric_target
target_year
```

và:

### `Fact_ExternalESGEvent`

```text
company_id
event_time
ESG_topic
event_type
event_sentiment
event_severity
source
```

Từ đó tạo:

\[
DisclosureConsistencyScore
\]

Ví dụ:

\[
DCS_{i,t}
=
DisclosurePositive_{i,t}
-
ExternalNegativeEvidence_{i,t}
\]

Giá trị càng cao bất thường có thể biểu thị:

> Corporate disclosure rất tích cực nhưng external evidence rất tiêu cực.

## 1.3. Khoảng trống nghiên cứu

Một hướng nghiên cứu gần đây đã xây ESG-washing Severity Index bằng TF-IDF, LDA và sentiment trên sustainability reports của hàng trăm công ty toàn cầu, nhưng dữ liệu vẫn thiên về snapshot/cross-sectional. Vì vậy, chỉ sentiment analysis ESG report để phát hiện greenwashing không còn đủ mới.

Các systematic review 2025–2026 tiếp tục chỉ ra các vấn đề:

- dữ liệu ESG không nhất quán;
- phụ thuộc nhiều vào database thương mại;
- cập nhật ESG thường theo năm;
- thiếu dữ liệu cho emerging markets;
- khó kiểm chứng greenwashing bằng external evidence.

Từ đó có 3 gap tốt.

### Gap A — Self-reported ESG vs external evidence

Phần lớn ESG analysis sử dụng:

\[
ESG\ report
\]

Trong khi có thể nghiên cứu:

\[
ESG\ report
+
News
+
Financial\ result
\]

để kiểm tra:

> Doanh nghiệp nói gì so với những gì thực tế xảy ra?

### Gap B — Static ESG → Dynamic ESG

Các ESG rating thường rất thưa.

Trong warehouse có thể xây:

\[
ESGScore(company,t)
\]

theo tháng hoặc tuần thay vì một score/năm.

Ví dụ:

```text
2025-01 ESG score = 0.72
2025-02 = 0.70
2025-03 scandal → 0.43
2025-04 = 0.45
```

Sau đó nghiên cứu:

\[
DynamicESG_t
\rightarrow
Risk_{t+1}
\]

### Gap C — ESG disagreement có giá trị dự báo không?

Câu hỏi:

> Khoảng cách giữa corporate ESG disclosure và external ESG evidence có dự báo volatility, drawdown hoặc financial distress tốt hơn ESG disclosure đơn lẻ hay không?

## 1.4. Kỹ thuật áp dụng

### NLP

```text
BERT
RoBERTa
FinBERT
DeBERTa
Sentence Transformer
LLM
```

Ứng dụng cho:

- ESG classification;
- sentiment;
- topic extraction;
- event extraction;
- claim extraction.

Có thể dùng NLI:

```text
ESG Claim
     +
External News
     ↓
Entailment
Neutral
Contradiction
```

### AI dự báo

```text
Logistic Regression
Random Forest
XGBoost
LightGBM
Temporal Fusion Transformer
```

### XAI

```text
SHAP
```

## 1.5. Thí nghiệm paper

Có thể xây 4 model:

| Model | Data |
|---|---|
| M0 | Financial |
| M1 | Financial + ESG disclosure |
| M2 | Financial + external ESG events |
| **M3** | **Financial + disclosure + external evidence + inconsistency score** |

Nếu:

\[
M3>M0,M1,M2
\]

thì warehouse thực sự tạo contribution.

## 1.6. Tính khả thi

### Dữ liệu: **7/10**

Financial data: dễ.

News: dễ.

ESG reports: lấy được nhưng crawl/parse PDF tốn công.

Ground truth greenwashing: **khó**.

Do đó nên **không đặt target chính là binary greenwashing**, mà đặt:

> **ESG disclosure inconsistency + financial risk prediction.**

### Khả thi paper: **8/10**

### Novelty: **9–9.5/10**

### Rủi ro lớn nhất

**Data engineering + entity matching + ESG label.**

---

# 2. Energy + Weather Data Warehouse for Adaptive Forecasting

Đây là đề tài **dễ triển khai nhất trong ba đề tài**.

## Tên nên chỉnh

### Tiếng Anh

**A Drift-Attributed Energy–Weather Data Warehouse for Selective Adaptive Electricity Load Forecasting**

### Tiếng Việt

**Xây dựng kho dữ liệu điện năng và thời tiết phục vụ dự báo phụ tải thích nghi có chọn lọc trước sự thay đổi phân phối dữ liệu**

Nên thêm **drift-attributed** và **selective** vì các nghiên cứu gần đây đã làm concept drift + retraining.

## 2.1. Dữ liệu

### Dataset A — Open Power System Data

OPSD cung cấp time-series:

- electricity load;
- wind;
- solar;
- electricity price;
- hourly resolution;
- nhiều quốc gia châu Âu.

Ví dụ:

```text
timestamp
country
load
wind
solar
price
```

### Dataset B — OPSD Weather

OPSD cũng có weather dataset theo quốc gia:

- hourly;
- temperature;
- direct radiation;
- diffuse radiation.

Join rất thuận lợi:

```text
Germany Load
      +
Germany Weather
      ↓
timestamp
```

### Dataset C — ERA5

Nếu muốn mạnh hơn, ERA5 cung cấp weather hourly dài hạn và độ phủ toàn cầu với các biến:

```text
temperature
dew point
pressure
wind
precipitation
```

### Dataset D — UCI

UCI ElectricityLoadDiagrams20112014 có:

- 370 clients;
- mỗi 15 phút;
- 140.256 time points;
- không missing value.

Có thể dùng làm external benchmark.

## 2.2. Kho dữ liệu

```text
                     Dim_Time
                        │
            ┌───────────┼───────────┐
            ↓           ↓           ↓
       Fact_Load    Fact_Weather  Fact_Price
            │
            └───────────┬───────────┘
                        ↓
                  Dim_Region
```

Thêm:

```text
Fact_Forecast
Fact_DriftEvent
```

`Fact_DriftEvent`:

```text
timestamp
region
feature
drift_type
drift_score
detector
model_error
retraining_triggered
```

Đây là điểm biến warehouse thành một phần methodology.

## 2.3. Feature engineering

Từ load:

```text
load_lag_1h
load_lag_24h
load_lag_168h
rolling_mean_24h
rolling_mean_7d
rolling_std_7d
```

Weather:

```text
temperature
humidity
precipitation
wind
radiation
```

Calendar:

```text
hour
weekday
weekend
holiday
month
season
```

Interaction:

\[
Temperature\times Hour
\]

\[
Temperature^2
\]

vì load thường không tuyến tính với nhiệt độ.

## 2.4. Khoảng trống nghiên cứu

Các paper 2025–2026 đã sử dụng:

- ADWIN;
- KSWIN;
- Page-Hinkley;
- PELT;
- automatic retraining;
- adaptive N-BEATS;
- weather-aware distribution-shift correction.

Vì vậy:

> “Detect concept drift → retrain model”

**không còn đủ novelty.**

### Gap mạnh hơn: drift xảy ra do cái gì?

Ta có:

\[
Load\ drift
\]

nhưng drift có thể do:

```text
Weather change
Season change
Holiday
Consumption behavior
Economic event
Structural change
```

Không phải drift nào cũng cần retrain model.

Câu hỏi:

> **Có thể sử dụng Data Warehouse đa nguồn để phân biệt drift do weather/season bình thường với harmful concept drift thực sự làm model suy giảm hay không?**

### Drift attribution

Case 1:

```text
Temperature:
20 → 35°C

Load:
5000 → 8000 MW
```

Đây có thể là covariate/weather shift.

Case 2:

```text
Temperature: stable

Load behavior: suddenly changes
```

Có thể là concept drift.

## 2.5. Research Questions

**RQ1**

> Weather-aware forecasting có tốt hơn load-only forecasting không?

**RQ2**

> Những thay đổi distribution nào thực sự làm forecasting error tăng?

**RQ3**

> Drift-triggered retraining có tốt hơn periodic retraining không?

**RQ4**

> Drift attribution có giúp giảm số lần retraining nhưng vẫn giữ accuracy không?

RQ4 là điểm mạnh nhất.

## 2.6. Kỹ thuật áp dụng

### Forecasting baseline

```text
Linear Regression
XGBoost
LightGBM
```

### Time-series

```text
LSTM
N-BEATS
TFT
PatchTST
Transformer
```

Không cần chạy tất cả. Có thể dùng:

```text
LightGBM
N-BEATS
PatchTST
```

### Drift detection

```text
ADWIN
KSWIN
Page-Hinkley
PELT
```

Thêm statistical distance:

\[
PSI
\]

\[
KL\ divergence
\]

\[
Wasserstein\ distance
\]

\[
MMD
\]

## 2.7. Experimental design

So sánh:

| Strategy | Ý nghĩa |
|---|---|
| S0 | Không retrain |
| S1 | Retrain mỗi tuần |
| S2 | Retrain mỗi tháng |
| S3 | Drift detected → retrain |
| **S4** | **Harmful drift detected → selective retrain** |

Mục tiêu:

\[
Error(S4)\le Error(S3)
\]

nhưng:

\[
RetrainingCount(S4)<RetrainingCount(S3)
\]

Tức không chỉ accuracy mà còn **computational efficiency**.

## 2.8. Metrics

Forecast:

```text
MAE
RMSE
sMAPE
MASE
```

Adaptive framework:

```text
Number of retrainings
Training time
Drift detection delay
False drift alarms
```

Có thể tạo:

\[
AdaptiveUtility
=
ForecastError
+
\lambda\times RetrainingCost
\]

## 2.9. Tính khả thi

### Dữ liệu: **10/10**

Rất tốt.

Có thể tải trực tiếp, không cần crawl phức tạp.

### Data Warehouse: **9.5/10**

Schema rõ, timestamp rõ, nguồn dữ liệu dễ join.

### Computing: **8.5/10**

LightGBM/N-BEATS chạy tương đối nhẹ.

PatchTST cần GPU nhưng không quá nặng.

### Novelty sau khi chỉnh: **8.5/10**

### Khả năng hoàn thành: **9.5/10**

Trong ba hướng, **đây là hướng an toàn nhất cho một nhóm muốn hoàn thành paper**.

---

# 3. Corporate Financial Distress Warehouse

Đây là hướng Fintech tốt, nhưng **phải nâng novelty khá mạnh**.

## Tên đề tài

### Phiên bản vừa sức

**English**

**A Point-in-Time Longitudinal Corporate Financial Warehouse for Multi-Horizon Financial Distress Prediction**

**Vietnamese**

**Xây dựng kho dữ liệu tài chính doanh nghiệp theo thời gian phục vụ dự báo sớm kiệt quệ tài chính đa kỳ**

### Phiên bản mạnh hơn

**A Multimodal Longitudinal Corporate Intelligence Warehouse for Multi-Horizon Financial Distress Prediction**

Tức thêm annual-report text.

## 3.1. Dữ liệu — phương án dễ

UCI có **Polish Companies Bankruptcy Dataset**:

- 10.503 instances;
- 65 financial features;
- doanh nghiệp bankrupt 2000–2012;
- doanh nghiệp hoạt động 2007–2013;
- chia thành các trường hợp dự báo từ 1 đến 5 năm.

Dataset này thuận tiện cho baseline:

\[
FinancialRatios
\rightarrow
Bankruptcy
\]

Nhưng không nên dùng làm contribution chính vì dữ liệu đã cũ và chưa thể hiện vai trò kho dữ liệu mạnh.

## 3.2. Phương án dữ liệu mạnh hơn: tự tạo warehouse từ SEC

SEC EDGAR cung cấp:

```text
10-K
10-Q
8-K
XBRL
filing history
```

Có thể xây:

```text
Company
    │
    ├── quarterly financials
    ├── annual financials
    ├── 10-K text
    ├── Risk Factors
    ├── MD&A
    └── corporate events
```

## 3.3. Nhãn distress lấy ở đâu?

Một hướng tốt là lấy **bankruptcy events** từ 8-K.

SEC filings sử dụng:

> **Item 1.03 — Bankruptcy or Receivership**

Ta xác định:

\[
T_{bankruptcy}
\]

Sau đó tạo observation:

\[
T-1,\ T-2,\ T-3
\]

years.

Ví dụ:

```text
Company bankrupt 2025

2022 → prediction horizon 3 years
2023 → horizon 2 years
2024 → horizon 1 year
```

## 3.4. Kho dữ liệu

```text
                    Dim_Company
                         │
                         ↓
             ┌── Fact_Financial
             │
Dim_Time ────┼── Fact_Market
             │
             ├── Fact_Macro
             │
             ├── Fact_FilingText
             │
             └── Fact_DistressEvent
```

`Fact_Financial`:

```text
company
period_end
filing_date

revenue
assets
liabilities
cash
debt
net_income
cash_flow
```

Chú ý:

```text
period_end
```

khác:

```text
filing_date
```

Điều này rất quan trọng.

## 3.5. Point-in-Time Correctness

Ví dụ:

Financial statement có:

```text
period_end = 31/12/2024
```

nhưng doanh nghiệp công bố:

```text
filing_date = 15/03/2025
```

Nếu dự đoán tại:

```text
01/02/2025
```

thì **không được phép sử dụng báo cáo này**.

Warehouse phải enforce:

\[
filing\_date\le prediction\_date
\]

Đây là một contribution Data Warehouse rất đẹp.

## 3.6. Khoảng trống nghiên cứu

Các ý tưởng đơn giản đã được làm khá nhiều.

Các paper gần đây đã kết hợp:

- accounting variables;
- market variables;
- macro factors;
- time-aware train/test;
- XGBoost/RF;
- SHAP.

Ngoài ra, các nghiên cứu 2025–2026 cũng đã kết hợp:

- financial indicators nhiều năm;
- annual report text nhiều năm;
- Longformer;
- BiLSTM;
- TextCNN;
- textual risk disclosures.

Do đó:

> **Financial ratios + XGBoost + SHAP không còn đủ novelty.**

## 3.7. Gap đề xuất: Multi-Horizon Point-in-Time Early Warning

Đừng chỉ dự báo:

\[
Distress=yes/no
\]

mà:

\[
P(Distress\ within\ 1y)
\]

\[
P(Distress\ within\ 2y)
\]

\[
P(Distress\ within\ 3y)
\]

Ví dụ:

```text
Company X

2022  Risk 3Y = 0.30
2023  Risk 2Y = 0.51
2024  Risk 1Y = 0.84
2025  Bankruptcy
```

Từ đó nghiên cứu:

> **Risk trajectory trước bankruptcy thay đổi như thế nào?**

## 3.8. Gap thứ hai: Financial trajectory chứ không chỉ financial value

Không chỉ dùng:

\[
Debt_t
\]

mà:

\[
Debt_t-Debt_{t-1}
\]

và:

\[
trend(Debt_{t-8:t})
\]

Ví dụ feature:

```text
revenue_growth_4q
debt_growth_4q
margin_trend
cashflow_decline
liquidity_trend
earnings_volatility
```

Warehouse chính là nơi sinh các historical trajectories này.

## 3.9. Gap thứ ba: Early-warning stage

Bankruptcy là trạng thái quá muộn.

Có thể định nghĩa:

```text
Stage 0: Healthy
Stage 1: Warning
Stage 2: Severe distress
Stage 3: Bankruptcy
```

và nghiên cứu:

\[
Stage_0
\rightarrow Stage_1
\rightarrow Stage_2
\rightarrow Stage_3
\]

## 3.10. Kỹ thuật áp dụng

### Baseline

```text
Logistic Regression
Random Forest
XGBoost
LightGBM
```

### Time-aware models

```text
LSTM
GRU
Temporal Fusion Transformer
```

Transformer không bắt buộc.

### Survival Analysis

Thay vì:

\[
Bankrupt?
\]

dự báo:

\[
Time\ to\ Distress
\]

Có thể dùng:

```text
Cox Proportional Hazard
Random Survival Forest
DeepSurv
```

Câu hỏi:

> Không chỉ doanh nghiệp có phá sản không, mà còn **khi nào**.

Đây phù hợp với longitudinal warehouse hơn classification thông thường.

## 3.11. NLP nếu muốn tăng novelty

Từ 10-K:

```text
Item 1A Risk Factors
MD&A
Auditor comments
```

tạo:

```text
risk sentiment
uncertainty
financial risk topics
liquidity concerns
going concern language
```

Nhưng NLP text đơn thuần không còn là novelty.

Novelty nên là:

\[
Financial
+
Text
+
Point-in-time
+
Multi-horizon
\]

## 3.12. Experimental design

Có thể làm:

| Model | Information |
|---|---|
| M0 | Current financial |
| M1 | Current + historical financial |
| M2 | M1 + market/macro |
| M3 | M2 + textual risk |
| **M4** | **M3 + point-in-time temporal trajectories** |

Dự báo:

```text
1-year distress
2-year distress
3-year distress
```

## 3.13. Metrics

Do distress imbalance:

```text
PR-AUC
ROC-AUC
Recall
Precision
F1
Brier Score
```

Nếu survival:

```text
C-index
Integrated Brier Score
```

Ngoài accuracy nên đánh giá **calibration**.

Nếu model nói:

\[
P(distress)=0.8
\]

thì xác suất đó có đáng tin hay không?

## 3.14. Tính khả thi

### Nếu dùng UCI/Kaggle

**9.5/10**

Nhưng novelty:

**5–6/10**

### Nếu tự xây SEC longitudinal warehouse

Dữ liệu:

**9/10**

Data engineering:

**7.5/10**

Distress label:

**7/10**

Overall:

**8/10**

### Novelty

Nếu:

> Financial ratios + XGBoost + SHAP

→ **5/10**

Nếu:

> Point-in-time DW + multi-horizon + longitudinal features

→ **8.5/10**

Nếu thêm:

> multimodal text + survival analysis

→ **9/10**

---

# So sánh trực tiếp 3 đề tài

| Tiêu chí | ESG Intelligence | Energy + Weather | Financial Distress |
|---|---:|---:|---:|
| Tải dữ liệu dễ | 7 | **10** | 9 |
| Crawl cần thiết | Nhiều | Hầu như không | Trung bình |
| Làm DW có ý nghĩa | **9** | 9 | **9.5** |
| NLP | **Rất nhiều** | Không cần | Tùy chọn |
| Time Series | Có | **Rất mạnh** | Có |
| Fintech | **Rất mạnh** | Không | **Rất mạnh** |
| Label dễ | 6 | **10** | 7 |
| GPU cần thiết | Có thể | Có thể | Có thể |
| Novelty ceiling | **10** | 8.5 | 9 |
| Rủi ro đề tài | **Cao** | **Thấp** | Trung bình |
| Khả năng ra paper | 8 | **9.5** | **9** |
| Q2 potential | **Cao** | **Cao** | **Cao** |
| Q1 potential | **Rất cao nếu làm tốt** | Có | Có |

# Kết luận lựa chọn

Nếu ưu tiên **paper chắc tay, dữ liệu dễ và triển khai trong thời gian hữu hạn**, nên chọn:

> **Energy + Weather Data Warehouse**

Contribution nên là:

\[
\boxed{
Weather-aware\ DW
+
Drift\ attribution
+
Harmful\ drift\ detection
+
Selective\ retraining
}
\]

Nếu muốn **đúng Fintech và vẫn kiểm soát được độ khó**, nên chọn:

> **A Point-in-Time Longitudinal Corporate Financial Warehouse for Multi-Horizon Financial Distress Prediction**

Nếu muốn **novelty ceiling cao nhất** và chấp nhận rủi ro dữ liệu cao hơn, chọn:

> **ESG Intelligence Data Warehouse**

nhưng nên tránh đặt “greenwashing detection” làm target duy nhất và chuyển thành:

> **Disclosure inconsistency + corporate financial risk prediction**
