# RESEARCH_PLAN.md — Beyond Synthetic Missingness (Smart-Meter Imputation)
# Methodological & Scientific Research Protocol

> **Protocol Version**: v1.1 (Officialized 2026-10-06 by Protocol Owner)  
> **Preceding Version**: v1.0 (2026-10-04, historical baseline preserved)  
> **Governing Documents**: `AGENTS.md`, `TASK_PLAN.md`, `reports/protocol_v1_1_amendment.md`, `reports/p1_t3_protocol_amendment_v1_1.md`  
> **Authoritative Dataset**: `data/interim/readings_utc.parquet` (208,224,479 deduplicated W readings, 79 meters)  

---

## 1. Executive Summary & Research Vision

### 1.1 Central Research Question
In time-series imputation for smart-meter energy data, benchmark evaluations conventionally inject synthetic missingness (point-wise or uncoordinated blocks) to assess model performance. This research program investigates:
> **Core Hypothesis**: Do synthetic missingness benchmarks preserve the relative performance rankings, error magnitude, and energy conservation properties of imputation algorithms when evaluated against authentic, multi-meter correlated failure episodes observed in physical power grids?

### 1.2 4-Branch Comparative Framework
To isolate the distinct physical mechanisms of missingness, the evaluation protocol establishes a 4-branch benchmark architecture:
1. **S-point (Synthetic Point)**: Uniformly random single-point omissions representing transient packet drops.
2. **S-block (Synthetic Block)**: Random continuous missing intervals lacking spatial or cross-meter coordination.
3. **S-matched (Synthetic Matched Distribution)**: Synthetic masks calibrated to match the empirical gap-length distribution and missing rates of real failure episodes, but sampled independently per meter (zero cross-meter correlation).
4. **R-derived (Real-Derived Failure Episodes)**: Mask topologies extracted directly from verified physical failure episodes recorded in operational issue tickets, preserving cross-meter correlation, temporal co-occurrence, and hierarchical network structure.

Direct comparison between **S-matched** and **R-derived** isolates the exact marginal contribution of multi-meter spatial correlation and hierarchy in benchmark distortion.

---

## 2. Protocol History & Revision Governance

| Protocol Version | Date | Status | Scope of Changes | Authorization |
|---|---|---|---|---|
| **v1.0** | 2026-10-04 | Superseded | Initial formulation. P1-T3 specified as 15-minute reindexing with invariant $\text{non\_nan\_after} == \text{non\_nan\_before}$. Preliminary cadence estimates from 1,000-row file samples. | Project Initiation |
| **v1.1** | 2026-10-06 | **Official & Active** | **Comprehensive P1-T3 & Core Population Amendment**: <br>1. P1-T3 reframed as **15-minute regular-grid representation / temporal downsampling** via right-closed intervals $(t-15\text{m}, t]$ and deterministic **`LAST`** operator.<br>2. Invariant replaced by **Occupied Bin Preservation** and **Zero Synthetic Observations**.<br>3. General Core Eligibility Rule established; **79 / 79 W meters** retained (including `H1.ZE20`).<br>4. Timestamp segregation: `grid_timestamp_utc` vs `source_timestamp_utc`.<br>5. Deterministic cadence classification (`C15S` to `SPARSE_GT15M`) and `bin_completeness`.<br>6. Strict prohibition of record counts/completeness as imputation model features.<br>7. Reconciliation of 61,790 duplicate records confirmed. | Protocol Owner Decision (`reports/protocol_v1_1_amendment.md`) |

---

## 3. Core Population & General Eligibility Rule (Protocol v1.1)

### 3.1 General Core Eligibility Definition
To prevent post-hoc, cherry-picked, or outcome-driven inclusion/exclusion of meters, membership in the Core Research Population is defined by a deterministic general rule:

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
- $\text{median\_gap\_seconds}(m) = \text{median}(\Delta t_i)$ across all strictly positive consecutive time differences $\Delta t_i > 0$ after P1-T2 deduplication.
- $\text{occupied\_15min\_rate}(m) = \frac{\text{count}(\text{raw\_occupied\_bins}(m))}{\text{total\_grid\_bins}(m)}$
- $\text{measurement\_semantics}(m) = \text{'W'}$: Raw active energy cumulative register (kWh), excluding synthetic/corrected registers (`_corrected_raw`).

### 3.2 Mandatory Scope Disclosure & Limitation Note
> **Methodological Scope Disclosure**:  
> The numerical thresholds (365 days history, 900 seconds median gap, 50% occupied rate) were specified after empirical inspection of dataset distributions, but strictly prior to any model training, imputation benchmark execution, ranking computation, or performance-driven selection.  
> Because all 79 available W meters satisfy this rule, the rule does not act as an outcome-driven exclusion criterion in the current population. This fact is formally disclosed as an empirical scope condition.

### 3.3 Core Population Membership: 79 / 79 Retained
- **All 79 meters** with target variable $W$ satisfy the General Core Eligibility Rule.
- **No meter is excluded** based on imputation performance, baseline error metrics, ranking outcome, or failure detection status.

### 3.4 Specific Ruling & Constraints for Meter H1.ZE20
- Comprehensive census reveals `H1.ZE20` is a 3-phase electrical feed-in meter with a **30.0-second median cadence** (551,582 raw readings, 73.49% occupied rate).
- Its operational history is **396.61 days** (~13 months, from 2022-11-30 to 2023-12-31). `H1.ZE20` has approximately 397 days of data, and therefore only narrowly satisfies the 365-day history threshold ($396.61 \ge 365$); the meter remains Core Eligible under the general rule.
- **Downstream Temporal Split Constraint**: Downstream train/test splits (P3, P5, P6) must verify whether a meter was active during the split window. Under no circumstances may `H1.ZE20` be evaluated or expected to provide readings prior to its installation date (2022-11-30).

### 3.5 Rectification of the HVAC Coverage Claim
- Early technical drafts hypothesized that omitting non-1min meters would eliminate HVAC coverage.
- Empirical review confirms that HVAC electrical loads (chillers, AHU fans, circulation pumps) are comprehensively metered by the 70 electrical meters (`Z`, `ZE`, `H*.T.Z`). Thermal heating meter `H1.W12` (858K readings, 85.04% occupied rate over 6 years) was never in question.
- **Scientifically Validated Claim**: Retaining hydronic meters (`H1.K11..K16`, `H1.W11`, `H2.K21`, `V.K21`) preserves **multi-carrier energy diversity** (coupling electric power profiles with hydronic thermal dynamics) rather than being the sole source of HVAC data.

### 3.6 Data Balance & Duplicate Reconciliation
The dataset exhibits strict mathematical balance:
$$\text{Raw } W \text{ Records (208,286,269)} = \text{Deduplicated } W \text{ (208,224,479)} + \text{V.Z84 Duplicates (61,790)}$$
- Deduplicated W records: $208,224,479$ stored in `data/interim/readings_utc.parquet`.
- Duplicate records: $61,790$ intra-file duplicate timestamps isolated to `V.Z84` on 2023-05-15 during post-outage reconnection, resolved via `keep_last` in P1-T2.

---

## 4. Meter Characterization & Cadence Protocol

### 4.1 Meter Metadata Schema (`Dim_Meter`)
Every meter in the warehouse must possess deterministic metadata:
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

### 4.2 Meter Type Attribution Rule
- `meter_type` must be grounded in source engineering documentation.
- Standardized taxonomy: `electrical_load`, `electrical_generation/PV`, `thermal_cooling`, `thermal_heating`, `other`, `unknown`.
- Inferences based solely on naming conventions must explicitly state the inference rule, confidence level, and must not be presented as source fact.

### 4.3 Deterministic Cadence Classes
`cadence_class` is classified using the meter's **median positive inter-observation gap** ($\Delta t > 0$ after P1-T2 deduplication):
- $\le 22.5\text{ s} \implies \text{C15S}$ (1 meter: `V.Z84`)
- $> 22.5 - 45.0\text{ s} \implies \text{C30S}$ (25 meters: `H1.ZE20`, `ZE`, `Z3xx` branches)
- $> 45.0 - 90.0\text{ s} \implies \text{C1M}$ (44 meters: standard minute meters)
- $> 90.0 - 180.0\text{ s} \implies \text{C2M}$ (1 meter: `H1.W12`)
- $> 180.0 - 540.0\text{ s} \implies \text{C6M}$ (8 meters: hydronic `K` and `W11` meters)
- $> 540.0 - 900.0\text{ s} \implies \text{C10M\_PLUS}$ (0 meters)
- $> 900.0\text{ s} \implies \text{SPARSE\_GT15M}$ (0 meters)

### 4.4 Cadence Non-Stationarity
- Median gaps are recomputed over non-overlapping **calendar month** windows.
- If any monthly window deviates from the all-history `cadence_class`, the flag is set:
  $$\text{cadence\_nonstationary} = \text{true}$$
  and the observed monthly classes are logged. The baseline `cadence_class` remains unchanged.

### 4.5 Deterministic Bin Completeness Formula
For meter $m$ with $\text{estimated\_cadence\_seconds} = \text{median\_gap\_seconds}(m)$:
- Full 15-minute bin ($900\text{ s}$):
  $$\text{expected\_record\_count\_full\_bin} = \max\left(1, \text{round}\left(\frac{900}{\text{estimated\_cadence\_seconds}}\right)\right)$$
- Boundary bin of valid coverage $\text{covered\_duration\_seconds}$:
  $$\text{expected\_record\_count\_bin} = \max\left(1, \text{round}\left(\frac{\text{covered\_duration\_seconds}}{\text{estimated\_cadence\_seconds}}\right)\right)$$
- Bin completeness metric:
  $$\text{bin\_completeness} = \min\left(1.0, \frac{\text{observed\_count}}{\text{expected\_record\_count\_bin}}\right)$$
  where $\text{observed\_count} = \text{raw\_record\_count}$.
- Both `expected_record_count` and `raw_record_count` are stored for auditability.
- `bin_completeness` is purely **descriptive metadata** and must never modify values or trigger fills.

### 4.6 Strict Anti-Leakage Mandate
- **`raw_record_count` and `bin_completeness` MUST NEVER be used as input features to imputation models.**
- *Rationale*: Supplying observation density or completeness under an artificially masked window directly leaks ground-truth observation presence to the model.

---

## 5. Standardized 15-Minute Grid Representation (P1-T3)

### 5.1 Temporal Anchors & Range
- **Timezone**: `UTC` (`timestamp[us, tz=UTC]`).
- **Quarter-Hour Grid Anchors**: $t \in \{\text{HH:00:00}, \text{HH:15:00}, \text{HH:30:00}, \text{HH:45:00}\}$ with seconds and microseconds equal to zero.
- **Meter-Specific Grid Horizon**:
  $$\text{grid\_start}(m) = \text{ceil\_to\_15min}(\min(\text{source\_timestamp\_utc}(m)))$$
  $$\text{grid\_end}(m) = \text{ceil\_to\_15min}(\max(\text{source\_timestamp\_utc}(m)))$$
  > **CRITICAL RULE**: Do NOT use `floor` for `grid_end`. An observation at $12:07$ belongs to $(12:00, 12:15]$ and must be represented by the grid row $12:15$. Using `floor` would drop the final observation.

### 5.2 Bin Semantics & Representative Selection (`LAST`)
- **Interval Partition**: Right-closed, right-labeled: $\text{Bin}(t) = (t - 15\text{ minutes}, t]$.
- **Occupied Bins ($\ge 1$ raw observations)**:
  $$\text{selected} = \arg\max_{r \in \text{Bin}(t)} (r.\text{timestamp\_utc})$$
  - $\text{value} = \text{selected.value}$ (bit-for-bit raw IEEE-754 value)
  - $\text{source\_timestamp\_utc} = \text{selected.timestamp\_utc}$
  - $\text{raw\_source\_file} = \text{selected.raw\_source\_file}$
  - $\text{raw\_record\_count} = |\text{Bin}(t)|$
- **Strictly Prohibited Operators**: `mean`, `sum`, `nearest`, `ffill`, `bfill`, `interpolation`, `smoothing`.

### 5.3 Empty Bins & Failure Semantics Distinction
- **Empty Bins ($0$ raw observations)**:
  - $\text{value} = \text{NaN}$, $\text{source\_timestamp\_utc} = \text{NULL}$, $\text{raw\_source\_file} = \text{NULL}$, $\text{raw\_record\_count} = 0$, $\text{bin\_completeness} = 0.0$.
- **Official Semantic Statement**:  
  *An empty 15-minute bin represents an observation gap on the standardized representation. It is not automatically an equipment failure. Failure semantics are established downstream in P1-T4 and P2 via quality flags and issue metadata.*

### 5.4 Core Invariants
1. **Occupied Bin Preservation**:
   $$\text{count}(\text{non\_nan\_15min}(m)) = \text{count}(\text{raw\_occupied\_bins}(m)) \quad \forall m \in [1, 79]$$
2. **Zero Synthetic Observations**:
   Every non-NaN value maps directly to an authentic tuple $(\text{meter\_id}, \text{source\_timestamp\_utc}, \text{raw\_source\_file}, \text{value})$ in `readings_utc.parquet`.

### 5.5 Target Schema of `readings_15min.parquet`
```sql
CREATE TABLE readings_15min (
    meter_id              VARCHAR(50) NOT NULL,
    grid_timestamp_utc    TIMESTAMP NOT NULL,
    timestamp_local       TIMESTAMP NOT NULL,
    source_timestamp_utc  TIMESTAMP,
    value                 DOUBLE,
    raw_source_file       VARCHAR(255),
    raw_record_count      INTEGER NOT NULL,
    expected_record_count INTEGER NOT NULL,
    bin_completeness      DOUBLE NOT NULL,
    cadence_class         VARCHAR(20) NOT NULL
);
```

---

## 6. Research Roadmap & Milestone Architecture

- **P1 — Preprocessing & Warehouse ETL**:
  Standardized 15-minute grid generation (P1-T3), quality flags marking (P1-T4), clean segments extraction (P1-T5), warehouse schema creation (P1-T6), and idempotent ETL ingestion (P1-T7/T8).
- **P2 — Mask Engine Architecture**:
  Extraction of failure episodes from issue logs, empirical gap analysis, and reproducible synthesis of the 4 benchmark branches (S-point, S-block, S-matched, R-derived) with strict anti-leakage guards.
- **P3 — Baseline Imputation Benchmark**:
  Unified interface benchmarking 4 foundational methods (Linear, Seasonal Naive, KNN, XGBoost) on stratified clean segments under fixed seed.
- **P4 — Ranking & Structural Sensitivity Analysis (Primary Contribution)**:
  Kendall rank correlation ($\tau$) across branches, bootstrap confidence intervals, and multi-dimensional OLAP slicing across gap lengths, cross-meter correlation levels, and `cadence_class`. Pre-registered decision gate (P4-T8) governs progression to P6.
- **P5 — Deep Learning Imputation (Extension 1)**:
  Evaluation of SAITS, BRITS, and TimesNet via PyPOTS under strict episode-split protocols.
- **P6 — Context-Aware Dynamic Selector & Downstream Forecasting (Extension 2 — Conditional)**:
  Activated only if P4-T8 detects significant regime-dependent ranking shifts.
- **P7 — Analytics Dashboard, Reproducibility Package & Reporting**:
  OLAP cubes, Power BI dashboard, and complete audit provenance traceability.

---

## 7. P1-T3 Acceptance Criteria & Verification Matrix

| Test ID | Criterion | Quantitative Requirement |
|---|---|---|
| **Test 1** | Regularity | Strictly 15-minute steps; anchored at `:00/:15/:30/:45`; sec/usec = 0 |
| **Test 2** | Expected Grid Length | Step count matches $\frac{\text{grid\_end} - \text{grid\_start}}{15\text{m}} + 1$ with $\text{grid\_start} = \text{ceil\_15m}(\min)$ and $\text{grid\_end} = \text{ceil\_15m}(\max)$ |
| **Test 3** | Occupied Bin Preservation | $\text{count}(\text{non\_nan\_15min}(m)) == \text{count}(\text{raw\_occupied\_bins}(m))$ per meter |
| **Test 4** | Zero Synthetic Observations | Every non-NaN value matches selected raw reading bit-for-bit |
| **Test 5** | Source Provenance | Every non-NaN row contains valid `source_timestamp_utc`, `raw_source_file`, $\text{raw\_record\_count} \ge 1$ |
| **Test 6** | Empty Bin Semantics | Empty bins contain `value = NaN`, `NULL` source fields, count = 0, completeness = 0.0 |
| **Test 7** | Clock Drift Immunity | Sub-minute and phase-offset readings are 100% captured into their corresponding bin |
| **Test 8** | Raw Immutability | `data/raw/` remains completely unmodified |
| **Test 9** | Corrected Exclusion | `_corrected_raw` records strictly excluded from authoritative output |

---

## 8. P1-T4 Acceptance Criteria & Verification Matrix (Ratified Amendment)

| Test ID | Criterion | Quantitative Requirement |
|---|---|---|
| **Test 1** | Schema & Types | 14 columns present; `is_missing`, `has_issue`, `is_corrected`, `is_valid_ground_truth` are boolean |
| **Test 2** | Overlap Semantics | Non-empty set intersection: $\text{Bin}(t) \cap I \neq \emptyset \iff (s \le t) \land (e > t - 15\text{min})$ |
| **Test 3** | Boundary-Start Rule | $s = t \implies \text{has\_issue} = \text{TRUE}$ (includes 1,143 boundary start cases across 57 meters) |
| **Test 4** | Open Left Boundary | $e = t - 15\text{min} \implies \text{has\_issue} = \text{FALSE}$ (strictly $e > t - 15\text{min}$) |
| **Test 5** | Zero-Duration Point Events | Instantaneous point events $[s, s]$ flagged iff $t - 15\text{min} < s \le t$ (44 isolated bins preserved) |
| **Test 6** | Ground Truth Protection | $\text{is\_valid\_ground\_truth} = 12,637,042$ rows; excludes all 1,096 occupied boundary failure readings |
| **Test 7** | Four-Quadrant Yield | $Q_1 = 12,637,042$; $Q_2 = 696,535$; $Q_3 = 527,756$; $Q_4 = 120,264$ across 13,981,597 total rows |
| **Test 8** | Value Immutability | Float values, timestamps, and 648,020 NaNs match P1-T3 bit-for-bit (Buffer SHA: `8cfc5fcdc0...`) |
| **Test 9** | Raw Immutability | Honda raw dataset and `data/raw/` remain 100% untouched and read-only |

---

## 9. Research Governance & Code of Conduct

All research agents and contributors must strictly abide by `AGENTS.md`:
1. `data/raw/` is permanently read-only.
2. Ground truth is extracted strictly from clean segments; `_corrected_raw` data is forbidden as ground truth.
3. No data leakage: feature pipelines must not peek under masks or into the future. Normalizers fit only on training sets.
4. Independent train/test splits: no failure episode may straddle train and test sets.
5. All runs record full provenance in `Meta_Run` (seed, git commit, config hash).
6. Negative results and neutral findings must be fully reported without cherry-picking.

*End of Research Protocol v1.1.*
