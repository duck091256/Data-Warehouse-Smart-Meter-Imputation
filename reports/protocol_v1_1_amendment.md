# PROTOCOL AMENDMENT v1.1 — BEYOND SYNTHETIC MISSINGNESS
# Smart-Meter Imputation Research Protocol Amendment

> **Protocol Version**: v1.1 (Officially Approved & Enacted)  
> **Preceding Version**: v1.0 (Superseded; historical record preserved)  
> **Effective Date**: 2026-10-06  
> **Authoritative Baseline Dataset**: `data/interim/readings_utc.parquet` (208,224,479 deduplicated W readings, 79 meters)  
> **Governing Charter**: `AGENTS.md`  
> **Referenced Preflight & Evidence**: `reports/p1_t3_protocol_amendment_v1_1.md`, `reports/p1_t3_protocol_preflight.md`  

---

## 1. Executive Summary & Purpose

This amendment formally enacts **Protocol v1.1** for the research project *Beyond Synthetic Missingness — Smart-Meter Imputation*, superseding the initial Protocol v1.0 specifications for Stage P1-T3 and related downstream conventions.

The Protocol Owner has officially reviewed the experimental preflight evidence (`reports/p1_t3_protocol_amendment_v1_1.md`) and ratified the following core decisions:
1. **Full Core Population Retention**: All 79 W meters are retained in the Core Population. Meter `H1.ZE20` is explicitly retained as Core Eligible.
2. **Shift in P1-T3 Framing**: Task P1-T3 transitions from a naive "15-minute reindexing" to a **15-minute regular-grid representation / temporal downsampling**.
3. **Deterministic `LAST` Operator**: For every occupied interval $\text{Bin}(t) = (t-15\text{min}, t]$, the observation with maximum `source_timestamp_utc` represents the interval.
4. **Occupied Bin Preservation**: Replaces the mathematically flawed v1.0 invariant (`non_nan_after == non_nan_before`) with `count(non_nan_15min(m)) == count(raw_occupied_bins(m))`.
5. **Zero Synthetic Observations**: Output values are bit-for-bit raw sensor readings; no arithmetic transformation, interpolation, or smoothing is permitted at P1-T3.
6. **Separation of Timestamps**: Explicit distinction between `grid_timestamp_utc` and `source_timestamp_utc`.
7. **Empty Bin Semantics**: Empty bins remain `NaN`; an empty bin is an observation gap on the standardized grid, not an equipment failure label.
8. **Cadence-Aware Metadata**: Meter-level `cadence_class`, `cadence_nonstationary`, and bin-level `bin_completeness` are defined deterministically for downstream stratification.
9. **Leakage Protection**: `raw_record_count` and `bin_completeness` are strictly forbidden as input features to imputation models.

---

## Old rule

```text
non_nan_after_reindex == non_nan_before_reindex
```

## New rule

* 15-min temporal downsampling;
* right-closed/right-labeled bins: $\text{Bin}(t) = (t - 15\text{min}, t]$;
* `LAST` representative observation operator;
* occupied-bin preservation: $\text{count}(\text{non\_nan\_15min}(m)) == \text{count}(\text{raw\_occupied\_bins}(m))$;
* zero synthetic observations: exact bit-for-bit raw sensor readings.

## Why

Dữ liệu raw có cadence sub-minute/multi-minute, do đó old rule không khả thi.

Empirical verification của `data/interim/readings_utc.parquet` cho thấy:
- Toàn bộ tập dữ liệu gồm **208,224,479 dòng raw W** trên 79 meters trong 6 năm (2018–2023).
- Cadence thô là **sub-minute và multi-minute** (15s, 30s, 60s, 120s, 360s).
- Lưới 15 phút liên tục trong 6 năm chỉ có tối đa **210,337 bins/meter**, tức tổng cộng khoảng **13.98 triệu meter-bins**.
- Do đó, việc ép 208,224,479 quan sát thô vào 13,980,000 ô thời gian mà đòi hỏi `non_nan_after == non_nan_before` là một mâu thuẫn toán học hoàn toàn không khả thi.
- Hơn nữa, việc khớp giây chính xác `:00:00` sẽ loại bỏ tới 97% quan sát hợp lệ của các đồng hồ bị lệch pha giây hoặc trôi đồng hồ (ví dụ `V.Z84` với giây lẻ tại `:18`, `:33`, `:48`).

## Scope disclosure

Ghi rõ eligibility thresholds được xác định sau khi quan sát dataset nhưng trước model outcomes; hiện tại chúng không loại meter nào:

> Thresholds 365 days / 900 seconds / 50% were specified after inspecting the observed dataset, but before any model training, imputation result, ranking analysis, or performance-based selection. Since all 79 meters satisfy the rule, the rule does not act as an outcome-driven exclusion criterion in the current population. This fact must be disclosed explicitly as a limitation / scope note.

## Known limitations

* ZE20 có lịch sử ngắn hơn phần lớn population (`H1.ZE20` có khoảng 397 ngày dữ liệu, nên chỉ vượt ngưỡng lịch sử một cách vừa đủ; meter vẫn Core Eligible theo rule chung).
* Cadence có thể thay đổi theo thời gian (`cadence_nonstationary = true`).
* Empty bins chưa đồng nghĩa failure (An empty 15-minute bin is an observation gap on the standardized grid. It is not automatically an equipment failure. Failure semantics are established later using quality flags and issue metadata).
* `bin_completeness` là descriptive, không phải label/model feature (cấm tuyệt đối đưa vào input feature của mô hình imputation).

---

## 2. Invariant Flaw in Protocol v1.0 & Mathematical Rationale

### 2.1 The Old Rule (Protocol v1.0)
In Protocol v1.0 (`TASK_PLAN.md`), the P1-T3 acceptance criterion was specified as:
```text
non_nan_after_reindex == non_nan_before_reindex
```
Under this rule, it was assumed that every raw non-NaN reading would map 1-to-1 onto a 15-minute grid row.

### 2.2 The Mathematical Impossibility
Empirical verification of `data/interim/readings_utc.parquet` revealed:
- The dataset comprises **208,224,479 raw W readings** across 79 meters over a 6-year operational horizon (2018–2023).
- The raw cadences are **sub-minute and multi-minute**:
  - 1 meter at 15s cadence (`V.Z84`)
  - 25 meters at 30s cadence (e.g., `H1.ZE20`, `H1.Z15`, `H1.Z17`)
  - 44 meters at 60s (1min) cadence
  - 1 meter at 120s (2min) cadence (`H1.W12`)
  - 8 meters at 360s (6min) cadence (`H1.K11..K16`, `H1.W11`, `H2.K21`, `V.K21`)
- A continuous 15-minute grid over the entire 6-year period contains only **210,337 bins per meter**, or approximately **13.98 million total meter-bins**.
- Compressing 208,224,479 raw observations into 13,980,000 bins while maintaining `non_nan_after == non_nan_before` is a **mathematical impossibility**.
- Furthermore, enforcing naive exact-second timestamp matching (`:00:00`) would drop up to 97% of valid physical readings for meters exhibiting second-level offsets or clock drift (e.g., `V.Z84` with timestamp seconds at `:18`, `:33`, `:48`).

### 2.3 The Solution in Protocol v1.1
P1-T3 is redefined as a **temporal downsampling onto a standardized regular grid**:
- Grid intervals are right-closed and right-labeled: $\text{Bin}(t) = (t - 15\text{min}, t]$.
- The representative value is chosen via the deterministic **`LAST`** operator.
- The new invariant is **Occupied Bin Preservation**: every bin containing $\ge 1$ raw observation yields exactly 1 non-NaN value, and every empty bin yields `NaN`.

---

## 3. General Core Eligibility Rule & Population Specification

### 3.1 Formal Eligibility Definition
To prevent ad-hoc or outcome-driven inclusion/exclusion of meters, membership in the **Core Research Population** is governed by a general, deterministic rule:

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

Where:
- $\text{history\_duration\_days}(m) = \frac{\max(\text{timestamp\_utc}) - \min(\text{timestamp\_utc})}{86400}$
- $\text{median\_gap\_seconds}(m) = \text{median}(\Delta t_i)$ for all positive consecutive time differences $\Delta t_i > 0$ after P1-T2 deduplication.
- $\text{occupied\_15min\_rate}(m) = \frac{\text{count}(\text{raw\_occupied\_bins}(m))}{\text{total\_grid\_bins}(m)}$
- $\text{measurement\_semantics}(m) = \text{'W'}$: Raw cumulative active energy register reading (kWh), excluding synthetic/corrected registers (`_corrected_raw`).

### 3.2 Mandatory Scope Disclosure & Limitation Note
> **Explicit Scope Disclosure**:  
> The numerical thresholds (365 days, 900 seconds, 50% occupied rate) were specified after inspecting the observed dataset characteristics, but strictly prior to any model training, imputation benchmarking, ranking analysis, or performance-driven selection.  
> Because all 79 available W meters satisfy this rule, the rule does not act as an outcome-driven exclusion criterion in the current population. This fact is explicitly recorded as a methodological scope condition.

### 3.3 Core Population Status: 79 / 79 Meters Retained
- **All 79 meters** satisfy the General Core Eligibility Rule.
- **No meter is excluded** on the basis of model performance, imputation difficulty, failure episode count, or ranking stability.

### 3.4 Specific Ruling on Meter H1.ZE20
- Initial inventory samples mislabeled `H1.ZE20` as an 810s pulse meter. Full-history auditing demonstrated that `H1.ZE20` is a 3-phase electrical feed-in/net meter with a **30.0-second median cadence** (551,582 raw readings; 73.49% occupied rate).
- Its operational history is **396.61 days** (~13 months, from 2022-11-30 to 2023-12-31). `H1.ZE20` có khoảng 397 ngày dữ liệu, nên chỉ vượt ngưỡng lịch sử một cách vừa đủ; meter vẫn Core Eligible theo rule chung ($396.61 \ge 365$).
- **Downstream Split Constraint**: Because `H1.ZE20` begins on 2022-11-30, downstream temporal splits (P3, P5, P6) must verify meter presence during the active split window and must never force `H1.ZE20` into temporal periods prior to its deployment.

### 3.5 Rectification of the HVAC Coverage Claim
- The hypothesis that "excluding the 9 non-1min meters would eliminate all HVAC coverage" is empirically inaccurate.
- Office HVAC electrical loads (chillers, AHU supply/exhaust fans, circulation pumps, cooling towers) are metered via the 70 electrical meters (`Z`, `ZE`, `H*.T.Z`). Additionally, thermal heating meter `H1.W12` (858,642 readings, 85.04% occupied rate over 6 years) was never in the questioned group.
- **Accurate Scientific Claim**: Retaining hydronic meters (`H1.K11..K16`, `H1.W11`, `H2.K21`, `V.K21`) provides **multi-carrier energy diversity** (coupling electrical load profiles with hydronic thermal energy dynamics) rather than acting as the sole provider of HVAC load.

---

## 4. Meter Metadata & Cadence Classification Protocol

### 4.1 Meter Metadata Schema
Every meter in `Dim_Meter` and pipeline metadata must record:
```text
meter_id
meter_type
history_start
history_end
history_duration_days
median_gap_seconds
p95_gap_seconds
max_gap_seconds
occupied_15min_rate
cadence_class
cadence_nonstationary
core_eligible
```

### 4.2 Meter Type Determination Rule
- `meter_type` must be grounded in source documentation and engineering metadata.
- Permitted standardized categories:
  - `electrical_load`
  - `electrical_generation/PV`
  - `thermal_cooling`
  - `thermal_heating`
  - `other`
  - `unknown`
- Naming conventions alone cannot be cited as source fact without explicit disclosure. If inferred from naming conventions (e.g., prefix `K` = Kälte/cooling, `W` = Wärme/heating, `ZE` = Einspeisung/PV), the classification rule, evidence source, and confidence level must be documented.

### 4.3 Deterministic Cadence Class Thresholds
Meter-level `cadence_class` is classified strictly using the **median positive inter-observation gap** ($\Delta t > 0$ after P1-T2 deduplication). Mean gap and max gap are not used as classifiers.

```text
Threshold Definition:
  median_gap_seconds <= 22.5 s       --> C15S
  22.5 s < median_gap_seconds <= 45.0 s --> C30S
  45.0 s < median_gap_seconds <= 90.0 s --> C1M
  90.0 s < median_gap_seconds <= 180.0 s--> C2M
  180.0 s < median_gap_seconds <= 540.0 s-> C6M
  540.0 s < median_gap_seconds <= 900.0 s-> C10M_PLUS
  median_gap_seconds > 900.0 s       --> SPARSE_GT15M
```

Distribution across the 79 Core Meters:
- `C15S`: 1 meter (`V.Z84`, median 18.0s)
- `C30S`: 25 meters (`H1.ZE20`, `H1.Z15`, `H1.Z17`, `H1.Z26`, `H1.Z28`, `H1.Z29`, `H1.Z310`, `H2.Z311`, `H2.Z351`, `H2.Z361`, `H2.ZE64..ZE74`, `H3.Z312`, `H3.ZE40..ZE44`, `H4.ZE50..ZE51`, `V.Z81..Z82`, `V.ZE84`)
- `C1M`: 44 meters (`H1.Z10..Z14`, `H1.Z16`, `H1.Z18..Z25`, `H1.Z27`, `H2.T.Z30..Z34`, `H2.Z35..Z36`, `H2.Z61..Z70`, `H3.Z40..Z41`, `H3.Z43..Z49`, `H3.Z71`, `H4.Z50..Z51`)
- `C2M`: 1 meter (`H1.W12`, median 120.0s)
- `C6M`: 8 meters (`H1.K11..K16`, `H1.W11`, `H2.K21`, `V.K21`, median 360.0s)
- `C10M_PLUS`: 0 meters
- `SPARSE_GT15M`: 0 meters

### 4.4 Cadence Non-Stationarity
To detect sensor reconfigurations across time:
- The median gap is computed over non-overlapping **calendar month** windows.
- If the cadence class of any calendar month deviates from the meter-level baseline, set:
  $$\text{cadence\_nonstationary} = \text{true}$$
- Summary of observed monthly classes is recorded. The meter-level baseline `cadence_class` remains unchanged.

### 4.5 Deterministic Bin Completeness Formula
For every meter $m$ with $\text{estimated\_cadence\_seconds} = \text{median\_gap\_seconds}(m)$:
- For a standard full bin ($900\text{ s}$):
  $$\text{expected\_record\_count\_full\_bin} = \max\left(1, \text{round}\left(\frac{900}{\text{estimated\_cadence\_seconds}}\right)\right)$$
- For boundary bins with coverage duration $\text{covered\_duration\_seconds}$:
  $$\text{expected\_record\_count\_bin} = \max\left(1, \text{round}\left(\frac{\text{covered\_duration\_seconds}}{\text{estimated\_cadence\_seconds}}\right)\right)$$
- Bin completeness metric:
  $$\text{bin\_completeness} = \min\left(1.0, \frac{\text{observed\_count}}{\text{expected\_record\_count\_bin}}\right)$$
  where $\text{observed\_count} = \text{raw\_record\_count}$.
- Both `expected_record_count` and `raw_record_count` are stored to allow auditing.

---

## 5. Standardized 15-Minute Grid Definition (P1-T3)

### 5.1 Timezone & Grid Anchors
- **Timezone**: `UTC` (`timestamp[us, tz=UTC]`).
- **Grid Anchors**: Aligned to quarter-hour boundaries:
  $$t \in \{\text{HH:00:00}, \text{HH:15:00}, \text{HH:30:00}, \text{HH:45:00}\}$$
  with seconds and microseconds strictly equal to zero.

### 5.2 Meter-Specific Grid Range
The regular grid range is bounded by:
$$\text{grid\_start}(m) = \text{ceil\_to\_15min}(\min(\text{source\_timestamp\_utc}(m)))$$
$$\text{grid\_end}(m) = \text{ceil\_to\_15min}(\max(\text{source\_timestamp\_utc}(m)))$$

> **CRITICAL RULE**: Do NOT use `floor` for `grid_end`.  
> *Rationale*: Under right-closed semantics $(t-15\text{m}, t]$, an observation at $12:07$ falls into $(12:00, 12:15]$ and must be represented by the grid row $12:15$. If `grid_end` were floored to $12:00$, the final observation would be dropped. Thus, $\text{grid\_end} = \text{ceil\_to\_15min}(12:07) = 12:15$.

### 5.3 Bin Partition Semantics
$$\text{Bin}(t) = (t - 15\text{ minutes}, t]$$
Right-closed, right-labeled.
*Example*: Grid timestamp `12:15:00 UTC` covers $(12:00:00.000000, 12:15:00.000000]$.

### 5.4 Representative Observation Operator (`LAST`)
- If $\text{Bin}(t)$ contains $\ge 1$ raw observation:
  $$\text{selected} = \arg\max_{r \in \text{Bin}(t)} (r.\text{timestamp\_utc})$$
  - $\text{value} = \text{selected.value}$ (exact IEEE-754 value)
  - $\text{source\_timestamp\_utc} = \text{selected.timestamp\_utc}$
  - $\text{raw\_source\_file} = \text{selected.raw\_source_file}$
  - $\text{raw\_record\_count} = |\text{Bin}(t)|$
  - $\text{bin\_completeness} = \min(1.0, |\text{Bin}(t)| / \text{expected\_record\_count})$
- Strictly prohibited operators: `mean`, `sum`, `nearest`, `ffill`, `bfill`, `interpolation`, `smoothing`.

### 5.5 Empty Bin Semantics
- If $\text{Bin}(t)$ contains $0$ raw observations:
  - $\text{value} = \text{NaN}$
  - $\text{source\_timestamp\_utc} = \text{NULL}$
  - $\text{raw\_source\_file} = \text{NULL}$
  - $\text{raw\_record\_count} = 0$
  - $\text{bin\_completeness} = 0.0$
- **Distinction between Observation Gap and Equipment Failure**:
  An empty bin after P1-T3 represents an observation gap on the standardized 15-minute grid representation. It does **not** constitute an equipment failure label. Failure semantics are established downstream in P1-T4 and P2 via quality flags and issue logs.

### 5.6 Invariant: Occupied Bin Preservation
$$\text{count}(\text{non\_nan\_15min}(m)) = \text{count}(\text{raw\_occupied\_bins}(m)) \quad \forall m \in [1, 79]$$
Every raw-occupied bin yields exactly one non-NaN reading; every empty bin yields `NaN`.

### 5.7 Invariant: Zero Synthetic Observations
Every non-NaN value in `readings_15min.parquet` must map directly to an authentic tuple:
$$(\text{meter\_id}, \text{source\_timestamp\_utc}, \text{raw\_source\_file}, \text{value})$$
present in `readings_utc.parquet`.

### 5.8 Schema of `readings_15min.parquet`
```sql
CREATE TABLE readings_15min (
    meter_id             VARCHAR(50) NOT NULL,
    grid_timestamp_utc   TIMESTAMP NOT NULL,
    timestamp_local      TIMESTAMP NOT NULL,
    source_timestamp_utc TIMESTAMP,
    value                DOUBLE,
    raw_source_file      VARCHAR(255),
    raw_record_count     INTEGER NOT NULL,
    expected_record_count INTEGER NOT NULL,
    bin_completeness     DOUBLE NOT NULL,
    cadence_class        VARCHAR(20) NOT NULL
);
```

---

## 6. Strict Research Integrity & Anti-Leakage Constraints

### 6.1 Prohibition of Metadata as Imputation Features
- Fields `raw_record_count`, `expected_record_count`, and `bin_completeness` are **descriptive and audit metadata only**.
- **STRICT PROHIBITION**: These fields must **NEVER** be provided as input features to any baseline or machine learning imputation model (P3, P5, P6).
- *Rationale*: Under masked regions, providing `raw_record_count` or `bin_completeness` would leak the fact that raw observations originally existed beneath the mask, completely compromising benchmark validity.

### 6.2 Data Reconciliation Audit
The authoritative row balance is documented and verified:
$$\text{Raw } W \text{ Records (208,286,269)} = \text{Deduplicated } W \text{ (208,224,479)} + \text{V.Z84 Duplicates (61,790)}$$
- Deduplicated W records: $208,224,479$ stored in `data/interim/readings_utc.parquet`.
- Duplicate records: $61,790$ intra-file duplicate timestamps isolated to `V.Z84` on 2023-05-15 during post-outage reconnection, resolved via `keep_last` in P1-T2.

---

## 7. Downstream Implications & Artifact Regeneration

1. **P1-T3 Artifacts**:
   - `data/interim/readings_15min.parquet` will be produced in accordance with Protocol v1.1.
   - P1-T3 is currently in `READY` status; no invalid artifact was generated.
2. **P1-T4 Quality Flags**:
   - Flags (`is_missing`, `flatline`, `spike`, etc.) operate on the standardized 15-minute grid.
3. **P1-T5 Clean Segments**:
   - Clean segments are extracted as consecutive non-NaN, non-issue, non-corrected 15-minute intervals.
4. **P2 Mask Engine**:
   - Synthetic (S-point, S-block, S-matched) and real-derived (R-derived) masks operate on the 15-minute grid.
5. **P4 Stratified Sensitivity Analysis**:
   - Performance and ranking consistency analyses must be stratified by `cadence_class`.
6. **Artifacts to Regenerate**:
   - Historical raw files (`data/raw/*`) and P1-T2 outputs (`readings_utc.parquet`) remain 100% untouched.
   - Downstream test suite (`tests/test_P1_T3.py`) will be constructed to test the 9 acceptance criteria of Protocol v1.1.

---

## 8. Official P1-T3 Acceptance Criteria (Checklist)

| # | Acceptance Criterion | Verification Method |
|---|---|---|
| **1** | **Regularity** | Grid timestamps increase by exactly 15 minutes, anchored to `:00/:15/:30/:45` with second/microsecond = 0. |
| **2** | **Expected Grid Length** | Grid steps equal $\frac{\text{grid\_end}(m) - \text{grid\_start}(m)}{15\text{ min}} + 1$, with $\text{grid\_start} = \text{ceil\_15m}(\min)$ and $\text{grid\_end} = \text{ceil\_15m}(\max)$. |
| **3** | **Occupied Bin Preservation** | $\text{count}(\text{non\_nan\_15min}(m)) == \text{count}(\text{raw\_occupied\_bins}(m))$ for each meter. |
| **4** | **Zero Synthetic Observations** | Every non-NaN value matches a raw observation in `readings_utc.parquet` bit-for-bit. |
| **5** | **Source Provenance** | Every non-NaN row contains valid `source_timestamp_utc`, `raw_source_file`, and $\text{raw\_record\_count} \ge 1$. |
| **6** | **Empty Bin Integrity** | Empty bins have `value = NaN`, `source_timestamp_utc = NULL`, `raw_source_file = NULL`, $\text{raw\_record\_count} = 0$, $\text{bin\_completeness} = 0.0$. |
| **7** | **Clock Drift Immunity** | Sub-minute and non-zero-second observations are fully captured without spurious gap creation. |
| **8** | **Raw Immutability** | `data/raw/` remains unmodified and read-only. |
| **9** | **Corrected Exclusion** | `_corrected_raw` records remain completely excluded from authoritative output. |

---

## 9. Conclusion & Protocol Owner Approval

Protocol v1.1 is hereby officialized as the governing standard for Stage P1-T3 and all downstream research tasks.

*Approved by Protocol Owner — 2026-10-06.*

---

## 10. Targeted Amendment: P1-T4 Issue Overlap Semantics (Ratified 2026-10-08)

> **Amendment Title**: P1-T4 Issue-Interval Overlap Semantics  
> **Status**: **RATIFIED / CONFIRMED (Strict Interpretation B)**  
> **Effective Date**: 2026-10-08  
> **Target Task**: P1-T4 — Build Quality & Provenance Flags  
> **Affected Artifact**: `data/interim/readings_15min_flagged.parquet`  

### 10.1 Formal Mathematical Rule
A standardized 15-minute grid bin $\text{Bin}(t) = (t - 15\text{min}, t] = (t - 900\text{s}, t]$ is issue-affected ($\text{has\_issue}(t) = \text{TRUE}$) if and only if the set of timestamps represented by the bin has a non-empty intersection with an authoritative issue interval $I = [s, e]$:
$$\text{has\_issue}(t) = \text{TRUE} \iff \text{Bin}(t) \cap I \neq \emptyset \iff (s \le t) \land (e > t - 900\text{s})$$

Formal consequences:
1. **Boundary-Start Inclusion**: An issue starting at $s = t$ is included ($s \le t$ is True, $e > t - 900\text{s}$ is True).
2. **Left-Boundary Exclusion**: An issue ending at $e = t - 900\text{s}$ is excluded ($t - 900\text{s}$ is open in $\text{Bin}(t)$).
3. **Zero-Duration Point Events**: Instantaneous point events $[s, s]$ are included whenever $t - 900\text{s} < s \le t$, naturally unified without special-case branching.

### 10.2 Empirical Effect & Reconciliation
- **Total Rows**: 13,981,597 (conserved 100%)
- **`has_issue` Delta**: $+1,143$ bins ($\text{False} \to \text{True}$); $815,656 \to 816,799$
- **Ground Truth Delta**: $-1,096$ bins ($\text{True} \to \text{False}$); $12,638,138 \to 12,637,042$
- **Four Quadrants**:
  - $Q_1$ (Clean Observed): $12,638,138 \to 12,637,042$ ($\Delta = -1,096$)
  - $Q_2$ (Issue Observed): $695,439 \to 696,535$ ($\Delta = +1,096$)
  - $Q_3$ (Unrelated Gap): $527,803 \to 527,756$ ($\Delta = -47$)
  - $Q_4$ (Corroborated Gap): $120,217 \to 120,264$ ($\Delta = +47$)
- **Invariant Conservation**: Value buffer SHA-256 (`8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe`), 648,020 NaNs, and all inherited provenance columns remain 100% bit-identical.

