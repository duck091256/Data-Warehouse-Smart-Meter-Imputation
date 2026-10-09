# Independent Audit Report: P1-T3 — 15-Minute Regular Grid Representation

> **Project**: Beyond Synthetic Missingness — Smart-Meter Imputation  
> **Protocol**: **Protocol v1.1 (Official)**  
> **Task Under Audit**: `P1-T3` (Standardized 15-Minute Regular Grid Representation / Downsampling)  
> **Auditor Role**: Independent Auditor  
> **Audit Execution Timestamp (UTC)**: 2026-10-06T18:51:30Z (Local: 2026-10-07T01:51:30+07:00)  
> **Input Artifact**: `data/interim/readings_utc.parquet` (P1-T2 Gated)  
> **Output Artifact Under Audit**: `data/interim/readings_15min.parquet`  
> **Executor Report Audited**: `data/audit_results/p1_t3_report.md`  
> **Final Audit Verdict**: **PASS**  
> **Gate Recommendation**: **PROCEED TO GATED (P1-T3 satisfies Protocol v1.1 in full)**

---

## 1. Executive Summary & Audit Verdict

This document presents the **Independent Audit Report** for task **P1-T3** under **Protocol v1.1**. In strict accordance with the Research Charter (`AGENTS.md`) and the Auditor Specification (`AUDITOR.md`), the auditor operated independently from the executor session and **did not accept any executor assertions without exhaustive empirical re-computation**.

An independent, end-to-end verification script was executed against the raw data lineage, interim UTC records (`readings_utc.parquet`, 208,224,479 rows), and the generated grid representation (`readings_15min.parquet`, 13,981,597 rows).

### Key Audit Findings
1. **Exhaustive Zero-Synthetic Verification (100% Non-Sampled)**:
   - All **13,333,577 occupied grid rows** were exhaustively compared against the authoritative P1-T2 records. Every single row maps bit-for-bit (IEEE-754 exact match) to an authentic source tuple `(meter_id, source_timestamp_utc, raw_source_file, value)` in `readings_utc.parquet`.
   - **0 synthetic values** were detected across all 79 meters.
2. **Occupied-Bin Preservation (100% Agreement)**:
   - For all **79 meters**, the number of non-null grid rows in the output exactly matches the number of occupied 15-minute intervals calculated directly from source observations:
     $$\sum_{m=1}^{79} N_{\text{source\_occupied}}(m) = \sum_{m=1}^{79} N_{\text{output\_non\_null}}(m) = \mathbf{13,333,577}$$
     Per-meter mismatch count is **0 / 79**.
3. **Strict 15-Minute Regularity & Boundary Alignment**:
   - Every meter exhibits exact 900-second steps between consecutive grid timestamps.
   - All 13,981,597 grid timestamps are strictly quarter-hour aligned (`:00, :15, :30, :45`, seconds = 0, microseconds = 0).
   - Key uniqueness `(meter_id, grid_timestamp_utc)` holds with zero duplicates.
4. **Right-Closed Ceiling Semantics**:
   - The interval convention $\text{Bin}(t) = (t - 15\text{m}, t]$ and operator $\text{LAST}$ are rigorously maintained.
   - For all 79 meters, `grid_start = ceil_to_15min(min(t))` and `grid_end = ceil_to_15min(max(t))`. Floor-based end logic was never used.
5. **Empty-Bin Integrity**:
   - All **648,020 empty grid bins** (4.63%) have `value = NaN`, `source_timestamp_utc = NULL`, `raw_source_file = NULL`, `raw_record_count = 0`, and `bin_completeness = 0.0`.
6. **Integrity & Governance Guardrails**:
   - `H1.ZE20` starts strictly at true installation (`2022-11-30 08:30:00 UTC`); no pre-installation grid rows exist.
   - Zero `_corrected_raw` files or records contribute to the output.
   - The external raw dataset remains 100% immutable and read-only.
   - Metadata columns (`raw_record_count`, `expected_record_count`, `bin_completeness`) are strictly protected against feature leakage.

### Final Verdict: **PASS**

All 14 mandatory acceptance criteria of Protocol v1.1 are independently verified and satisfied in full.

---

## 2. Artifact Provenance & Cryptographic Hashes

| Artifact Property | Value / Measurement | Auditor Status |
|---|---|:---:|
| **Output File** | `data/interim/readings_15min.parquet` | Verified |
| **Output File Size** | 394,072,801 bytes (375.82 MB) | Matches bit-for-bit |
| **Output SHA-256** | `f50a2ff27b142a895a8cabfbc0bcf3750aad28d5dcd5af2cb51a13628dce22dd` | Matches bit-for-bit |
| **Input File** | `data/interim/readings_utc.parquet` | Verified |
| **Input File Size** | 3,662,760,196 bytes (3.41 GB) | Matches bit-for-bit |
| **Input SHA-256** | `5983397375f03a5f0fd3cdab29c4ea561e3b68e13547aeca294f5ed8a2139b13` | Matches bit-for-bit |
| **Executor Report** | `data/audit_results/p1_t3_report.md` | Verified |
| **Executor Report SHA-256**| `e88f5f06d98a194fb664013f42141dae1f82c09aca09c432c2e3a888c1815c13` | Verified |
| **Config Hash** | `d2d17337de0d0b2e0fe36b4430c5a34b063549ccb2dc78203ecb9bef2d8b843a` | Verified |
| **Random Seed** | `42` | Verified |
| **Target Population** | 79 / 79 Core W Meters | Complete |

---

## 3. Mandatory Independent Check Results (Checks 1–14)

### Check 1: Artifact Existence & Schema Verification
- **Test Objective**: Verify physical existence, readability, schema fidelity, uniqueness key, and total population count.
- **Auditor Verification**:
  - The output file `data/interim/readings_15min.parquet` exists and is readable as a valid Apache Parquet table with 79 row groups (1 row group per meter).
  - Total rows: **13,981,597**.
  - All 10 expected fields strictly match the required types:
    ```sql
    meter_id              VARCHAR NOT NULL
    grid_timestamp_utc    TIMESTAMP_MICROS [UTC] NOT NULL
    timestamp_local       TIMESTAMP_MICROS [naive] NOT NULL
    source_timestamp_utc  TIMESTAMP_MICROS [UTC] NULLABLE
    value                 DOUBLE NULLABLE
    raw_source_file       VARCHAR NULLABLE
    raw_record_count      INTEGER NOT NULL
    expected_record_count INTEGER NOT NULL
    bin_completeness      DOUBLE NOT NULL
    cadence_class         VARCHAR NOT NULL
    ```
  - Exactly one row exists per `(meter_id, grid_timestamp_utc)` (0 duplicates).
  - Exactly **79 meters** are present, matching 100% of the meters in `readings_utc.parquet`.
- **Status**: **PASS**

---

### Check 2: Regularity & Grid Alignment
- **Test Objective**: Verify consecutive grid timestamp step size of 900 seconds and quarter-hour alignment across all meters.
- **Auditor Verification**:
  - For every meter $m \in [1..79]$:
    $$\Delta t_k = t_{k+1} - t_k = 900{,}000{,}000\ \mu\text{s} = 900.0\ \text{seconds} = 15\ \text{minutes}$$
  - Step size mismatches: **0**.
  - Remainder modulo $900{,}000{,}000\ \mu\text{s}$ equals $0$ for all 13,981,597 rows.
  - Minutes are strictly in `{:00, :15, :30, :45}` with seconds = 0 and microseconds = 0.
- **Status**: **PASS**

---

### Check 3: Boundary Semantics (Right-Closed Interval Proof)
- **Test Objective**: Verify the right-closed, right-labeled bin partition $\text{Bin}(t) = (t - 15\text{m}, t]$ using explicit test cases.
- **Mathematical Formula**:
  $$\text{grid\_label}(ts) = \left\lfloor \frac{ts + W - 1}{W} \right\rfloor \times W, \quad W = 15 \times 60 \times 10^6\ \mu\text{s}$$
- **Independent Test Suite**:
  | Input Source Timestamp (UTC) | Expected Grid Label | Actual Computed Grid Label | Status |
  |---|---|---|:---:|
  | `2023-01-01 12:00:00.000000` | `2023-01-01 12:00:00` | `2023-01-01 12:00:00` | **PASS** |
  | `2023-01-01 12:00:01.000000` | `2023-01-01 12:15:00` | `2023-01-01 12:15:00` | **PASS** |
  | `2023-01-01 12:14:59.999999` | `2023-01-01 12:15:00` | `2023-01-01 12:15:00` | **PASS** |
  | `2023-01-01 12:15:00.000000` | `2023-01-01 12:15:00` | `2023-01-01 12:15:00` | **PASS** |
  | `2023-01-01 12:15:01.000000` | `2023-01-01 12:30:00` | `2023-01-01 12:30:00` | **PASS** |
- **Status**: **PASS**

---

### Check 4: Grid Bounds & Ceiling Logic Verification
- **Test Objective**: Independently verify for all 79 meters that:
  $$\text{grid\_start}(m) = \text{ceil\_to\_15min}(\min(ts_{\text{source}}(m)))$$
  $$\text{grid\_end}(m) = \text{ceil\_to\_15min}(\max(ts_{\text{source}}(m)))$$
  and that floor-based logic is never used for `grid_end`.
- **Auditor Verification**:
  - First and last source timestamps were computed directly from `readings_utc.parquet` for each meter.
  - Actual first and last grid timestamps in `readings_15min.parquet` were compared against independent calculations.
  - Result: **0 boundary mismatches** across all 79 meters.
  - When $\max(ts_{\text{source}})$ is not exactly aligned to a 15-minute boundary (e.g. `H1.K11` ends at `22:54:00 UTC`), `grid_end` correctly evaluates to `23:00:00 UTC`, whereas floor logic would have truncated it to `22:45:00 UTC`. Floor end logic was rejected in 100% of cases.
- **Status**: **PASS**

---

### Check 5: LAST Representative Operator Verification
- **Test Objective**: Verify that inside any bin containing multiple raw observations, the record selected for `source_timestamp_utc`, `value`, and `raw_source_file` is chronologically the **LAST** observation in that bin.
- **Auditor Verification**:
  - Tested exhaustively across all **13,333,577 occupied bins**.
  - In each bin $(t-15\text{m}, t]$, the source record having $\max(ts_{\text{source}})$ was independently computed from `readings_utc.parquet`.
  - In 100% of cases, the output `source_timestamp_utc`, `value`, and `raw_source_file` matched this last record.
  - Mismatches: **0**.
- **Status**: **PASS**

---

### Check 6: Occupied-Bin Preservation (Independent Calculation)
- **Test Objective**: Verify exact equality between distinct source 15-minute occupied intervals in P1-T2 and non-null rows in P1-T3.
- **Auditor Verification**:
  - Calculated independently from P1-T2:
    $$\text{Total Source Occupied Bins} = \mathbf{13{,}333{,}577}$$
  - Measured from P1-T3 output:
    $$\text{Total Output Non-Null Bins} = \mathbf{13{,}333{,}577}$$
  - Per-meter mismatches: **0 meters out of 79**.
  - Occupied bin preservation rate: **100.00%**.
- **Status**: **PASS**

---

### Check 7: Zero Synthetic Observations — EXHAUSTIVE VERIFICATION
- **Test Objective**: Attempt exhaustive verification that every non-null output row maps to an authentic source tuple in P1-T2, and satisfies $t - 15\text{m} < ts_{\text{source}} \le t$.
- **Disclosure on Exhaustiveness**:
  > **AUDITOR DISCLOSURE**: Computational capacity allowed **100% EXHAUSTIVE VERIFICATION** across all **13,333,577 occupied rows**. No sampling was needed. This invariant is proven unconditionally.
- **Verification Details**:
  1. Every non-null output row $(m, ts_{\text{source}}, \text{file}, \text{val})$ was matched against the corresponding record in `readings_utc.parquet`.
  2. Bit-for-bit IEEE-754 value identity: **13,333,577 / 13,333,577 matches (100%)**.
  3. Raw source file identity: **13,333,577 / 13,333,577 matches (100%)**.
  4. Timestamp membership: In all 13,333,577 rows, $t - 15\text{m} < ts_{\text{source}} \le t$ holds strictly (0 out-of-bounds rows).
  5. Synthetic observations detected: **0**.
- **Status**: **PASS**

---

### Check 8: Empty-Bin Semantics Verification
- **Test Objective**: Verify that every empty grid row contains strictly `NaN / NULL` and 0 counts, with no synthetic values.
- **Auditor Verification**:
  - Total empty grid rows: **648,020** (4.63% of total grid rows).
  - Evaluated exhaustively across all 648,020 rows:
    - `value IS NULL`: 648,020 / 648,020 (100%)
    - `source_timestamp_utc IS NULL`: 648,020 / 648,020 (100%)
    - `raw_source_file IS NULL`: 648,020 / 648,020 (100%)
    - `raw_record_count == 0`: 648,020 / 648,020 (100%)
    - `bin_completeness == 0.0`: 648,020 / 648,020 (100%)
  - Non-null or synthetic leaks into empty bins: **0**.
- **Status**: **PASS**

---

### Check 9: H1.ZE20 Temporal Coverage & Absence of Pre-Installation Fabrication
- **Test Objective**: Inspect the beginning of `H1.ZE20` coverage and ensure no grid row exists prior to actual meter commissioning.
- **Auditor Verification**:
  - `H1.ZE20` source start in `readings_utc.parquet`: `2022-11-30 08:18:47 UTC`.
  - `H1.ZE20` grid start in `readings_15min.parquet`: `2022-11-30 08:30:00 UTC` ($=\text{ceil}(08:18:47)$).
  - Grid rows before `2022-11-30 08:30:00 UTC`: **0**.
  - Total grid rows: **38,075** (27,980 occupied, 10,095 empty).
  - No pre-installation fabrication detected.
- **Status**: **PASS**

---

### Check 10: Corrected Raw Protection & Lineage Trace
- **Test Objective**: Verify that no `*_corrected_raw*` file contributed to the P1-T3 output.
- **Auditor Verification**:
  - Audited all distinct file names present in `raw_source_file` across the entire 13,981,597 grid table:
    $$\{ f \in \text{raw\_source\_file} \mid \text{"corrected"} \in f \} = \emptyset$$
  - Corrected raw files found: **0**.
  - Lineage strictly traces back to authoritative raw files vetted during P1-T2.
- **Status**: **PASS**

---

### Check 11: External Raw Immutability
- **Test Objective**: Verify that the external authoritative dataset has not been modified.
- **Auditor Verification**:
  - External raw path: `/run/media/duck/New Volume/Vice - Download/Honda_Dataset`.
  - Verified directory structure (`data/`, `issues/`, `reduced_data/`) and timestamp immutability.
  - Repo directory `data/raw/` remains completely empty and pristine.
- **Status**: **PASS**

---

### Check 12: Feature Leakage Protection
- **Test Objective**: Confirm that descriptive metadata columns are strictly banned from model inputs.
- **Auditor Verification**:
  - `configs/local.yaml` contains explicit `feature_governance` policy:
    ```yaml
    feature_governance:
      forbidden_as_imputation_inputs:
        - "raw_record_count"
        - "bin_completeness"
        - "expected_record_count"
    ```
  - Downstream modules are prohibited from exposing these columns as model feature inputs during evaluation, preventing information leakage about ground truth presence.
- **Status**: **PASS**

---

### Check 13: Population Integrity (79/79 Meters Retained)
- **Test Objective**: Verify that all 79 eligible meters are retained in the output, and no meters are dropped or added.
- **Auditor Verification**:
  - Evaluated the General Core Eligibility Rule across all 79 meters:
    $$\text{history\_duration}(m) \ge 365\ \text{days} \quad \wedge \quad \text{median\_gap}(m) \le 900\ \text{s} \quad \wedge \quad \text{occupied\_rate}(m) \ge 50\%$$
  - All 79 meters satisfy the rule:
    - Minimum duration: 396.61 days (`H1.ZE20` $\ge 365$)
    - Maximum median gap: 361.0s (`H2.K21` $\le 900$)
    - Minimum occupied rate: 52.33% (`H2.Z311` $\ge 50.0\%$)
  - Output population: exactly **79 meters** (100% retained).
- **Status**: **PASS**

---

### Check 14: Determinism & Hash Reproducibility
- **Test Objective**: Verify deterministic execution and provenance metadata.
- **Auditor Verification**:
  - Output SHA-256 computed independently:
    `f50a2ff27b142a895a8cabfbc0bcf3750aad28d5dcd5af2cb51a13628dce22dd`
  - Matches `output_sha256` in `data/interim/readings_15min_metadata.json` and `p1_t3_report.md`.
  - Config hash matches: `d2d17337de0d0b2e0fe36b4430c5a34b063549ccb2dc78203ecb9bef2d8b843a`.
  - Random seed: `42`.
  - Row order is deterministic: grouped by `meter_id` (alphabetical order) and strictly sorted by `grid_timestamp_utc`.
- **Status**: **PASS**

---

## 4. Full 79-Meter Independent Audit Evidence Table

Every meter was audited independently against source P1-T2 data. In the table below:
- **Preservation**: `N_out_occupied == N_src_occupied`
- **Bounds**: `grid_start == ceil(src_min)` and `grid_end == ceil(src_max)`

| # | Meter ID | Cadence | Raw Source Rows | Grid Rows | Occupied Bins | Empty Bins | Occupied Rate | Preservation | Bounds | Audit Status |
|:---:|---|:---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|
| 1 | `H1.K11` | C6M | 368,168 | 209,999 | 156,082 | 53,917 | 74.33% | PASS | PASS | **PASS** |
| 2 | `H1.K12` | C6M | 371,325 | 210,053 | 156,667 | 53,386 | 74.58% | PASS | PASS | **PASS** |
| 3 | `H1.K14` | C6M | 371,399 | 210,090 | 157,411 | 52,679 | 74.93% | PASS | PASS | **PASS** |
| 4 | `H1.K15` | C6M | 386,892 | 210,098 | 162,943 | 47,155 | 77.56% | PASS | PASS | **PASS** |
| 5 | `H1.K16` | C6M | 381,185 | 178,708 | 156,607 | 22,101 | 87.63% | PASS | PASS | **PASS** |
| 6 | `H1.W11` | C6M | 479,151 | 210,336 | 185,064 | 25,272 | 87.98% | PASS | PASS | **PASS** |
| 7 | `H1.W12` | C2M | 858,642 | 210,335 | 178,874 | 31,461 | 85.04% | PASS | PASS | **PASS** |
| 8 | `H1.Z10` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 9 | `H1.Z11` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 10 | `H1.Z12` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 11 | `H1.Z13` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 12 | `H1.Z14` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 13 | `H1.Z15` | C30S | 4,778,004 | 210,336 | 206,846 | 3,490 | 98.34% | PASS | PASS | **PASS** |
| 14 | `H1.Z16` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 15 | `H1.Z17` | C30S | 4,890,930 | 210,336 | 206,834 | 3,502 | 98.33% | PASS | PASS | **PASS** |
| 16 | `H1.Z18` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 17 | `H1.Z19` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 18 | `H1.Z20` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 19 | `H1.Z21` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 20 | `H1.Z22` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 21 | `H1.Z23` | C1M | 3,123,706 | 208,248 | 208,248 | 0 | 100.00% | PASS | PASS | **PASS** |
| 22 | `H1.Z24` | C1M | 3,123,706 | 208,248 | 208,248 | 0 | 100.00% | PASS | PASS | **PASS** |
| 23 | `H1.Z25` | C1M | 3,123,706 | 208,248 | 208,248 | 0 | 100.00% | PASS | PASS | **PASS** |
| 24 | `H1.Z26` | C30S | 4,846,147 | 210,333 | 204,269 | 6,064 | 97.12% | PASS | PASS | **PASS** |
| 25 | `H1.Z27` | C1M | 3,353,756 | 210,336 | 204,442 | 5,894 | 97.20% | PASS | PASS | **PASS** |
| 26 | `H1.Z28` | C30S | 4,815,486 | 210,336 | 206,839 | 3,497 | 98.34% | PASS | PASS | **PASS** |
| 27 | `H1.Z29` | C30S | 3,775,021 | 210,336 | 203,456 | 6,880 | 96.73% | PASS | PASS | **PASS** |
| 28 | `H1.Z310` | C30S | 1,680,940 | 123,237 | 68,355 | 54,882 | 55.47% | PASS | PASS | **PASS** |
| 29 | `H1.ZE20` | C30S | 551,582 | 38,075 | 27,980 | 10,095 | 73.49% | PASS | PASS | **PASS** |
| 30 | `H2.K21` | C6M | 296,068 | 210,068 | 149,169 | 60,899 | 71.01% | PASS | PASS | **PASS** |
| 31 | `H2.T.Z30` | C1M | 2,703,826 | 180,256 | 180,256 | 0 | 100.00% | PASS | PASS | **PASS** |
| 32 | `H2.T.Z31` | C1M | 2,703,826 | 180,256 | 180,256 | 0 | 100.00% | PASS | PASS | **PASS** |
| 33 | `H2.T.Z32` | C1M | 2,703,826 | 180,256 | 180,256 | 0 | 100.00% | PASS | PASS | **PASS** |
| 34 | `H2.T.Z33` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 35 | `H2.T.Z34` | C1M | 2,703,826 | 180,256 | 180,256 | 0 | 100.00% | PASS | PASS | **PASS** |
| 36 | `H2.Z311` | C30S | 1,684,778 | 123,333 | 64,538 | 58,795 | 52.33% | PASS | PASS | **PASS** |
| 37 | `H2.Z35` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 38 | `H2.Z351` | C30S | 3,360,317 | 115,444 | 114,207 | 1,237 | 98.93% | PASS | PASS | **PASS** |
| 39 | `H2.Z36` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 40 | `H2.Z361` | C30S | 3,366,999 | 115,444 | 114,203 | 1,241 | 98.92% | PASS | PASS | **PASS** |
| 41 | `H2.Z61` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 42 | `H2.Z62` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 43 | `H2.Z63` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 44 | `H2.Z64` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 45 | `H2.Z65` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 46 | `H2.Z66` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 47 | `H2.Z67` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 48 | `H2.Z68` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 49 | `H2.Z69` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 50 | `H2.Z70` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 51 | `H2.ZE64` | C30S | 1,837,544 | 62,337 | 61,479 | 858 | 98.62% | PASS | PASS | **PASS** |
| 52 | `H2.ZE65` | C30S | 1,776,395 | 60,218 | 59,449 | 769 | 98.72% | PASS | PASS | **PASS** |
| 53 | `H2.ZE66` | C30S | 738,161 | 62,337 | 61,319 | 1,018 | 98.37% | PASS | PASS | **PASS** |
| 54 | `H2.ZE67` | C30S | 540,106 | 62,337 | 58,393 | 3,944 | 93.67% | PASS | PASS | **PASS** |
| 55 | `H2.ZE74` | C30S | 1,851,053 | 62,724 | 61,857 | 867 | 98.62% | PASS | PASS | **PASS** |
| 56 | `H3.Z312` | C30S | 1,685,395 | 123,239 | 65,242 | 57,997 | 52.94% | PASS | PASS | **PASS** |
| 57 | `H3.Z40` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 58 | `H3.Z41` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 59 | `H3.Z43` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 60 | `H3.Z44` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 61 | `H3.Z45` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 62 | `H3.Z46` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 63 | `H3.Z47` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 64 | `H3.Z48` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 65 | `H3.Z49` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 66 | `H3.Z71` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 67 | `H3.ZE40` | C30S | 1,811,153 | 62,743 | 60,661 | 2,082 | 96.68% | PASS | PASS | **PASS** |
| 68 | `H3.ZE41` | C30S | 1,811,993 | 62,743 | 60,661 | 2,082 | 96.68% | PASS | PASS | **PASS** |
| 69 | `H3.ZE43` | C30S | 1,781,922 | 62,743 | 60,574 | 2,169 | 96.54% | PASS | PASS | **PASS** |
| 70 | `H3.ZE44` | C30S | 1,672,811 | 62,743 | 59,656 | 3,087 | 95.08% | PASS | PASS | **PASS** |
| 71 | `H4.Z50` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 72 | `H4.Z51` | C1M | 3,155,041 | 210,337 | 210,337 | 0 | 100.00% | PASS | PASS | **PASS** |
| 73 | `H4.ZE50` | C30S | 1,838,007 | 62,350 | 61,492 | 858 | 98.62% | PASS | PASS | **PASS** |
| 74 | `H4.ZE51` | C30S | 1,838,826 | 62,350 | 61,492 | 858 | 98.62% | PASS | PASS | **PASS** |
| 75 | `V.K21` | C6M | 379,746 | 210,096 | 158,635 | 51,461 | 75.51% | PASS | PASS | **PASS** |
| 76 | `V.Z81` | C30S | 4,782,562 | 210,336 | 206,414 | 3,922 | 98.14% | PASS | PASS | **PASS** |
| 77 | `V.Z82` | C30S | 4,718,981 | 210,336 | 206,419 | 3,917 | 98.14% | PASS | PASS | **PASS** |
| 78 | `V.Z84` | C15S | 4,210,903 | 158,116 | 156,153 | 1,963 | 98.76% | PASS | PASS | **PASS** |
| 79 | `V.ZE84` | C30S | 564,233 | 38,716 | 30,995 | 7,721 | 80.06% | PASS | PASS | **PASS** |
| **ALL** | **79 METERS** | — | **208,224,479** | **13,981,597** | **13,333,577** | **648,020** | **95.37%** | **PASS** | **PASS** | **PASS** |

---

## 5. Auditor Notes & Advisory for Downstream Stages

While all criteria for P1-T3 pass unconditionally, the independent auditor emphasizes the following **critical governance notes** for subsequent stages:

1. **Observation Gaps vs Equipment Failure Episodes (P1-T4, P2-T1)**:
   - The 648,020 empty grid bins (`NaN`) represent observation gaps on the regular 15-minute grid (i.e. periods where no raw telemetry was received for $> 900$ seconds).
   - In accordance with Protocol v1.1, downstream tasks (P1-T4 quality flagging and P2-T1 episode extraction) **must not treat an empty bin as an equipment failure** unless corroborated by authoritative issue logs in `issues/*.yaml`.
2. **Temporal Split Constraints for Meter H1.ZE20 (P1-T5, P3, P4)**:
   - `H1.ZE20` was commissioned on **2022-11-30 08:18:47 UTC**. Its total lifespan covers ~397 days (2022-11-30 to 2023-12-31).
   - While `H1.ZE20` meets the General Core Eligibility Rule ($\ge 365$ days), downstream temporal split logic must never attempt to evaluate or backfill `H1.ZE20` in periods prior to 2022-11-30.
3. **Strict Prohibition on Metadata Leakage (P2, P3, P4)**:
   - The columns `raw_record_count`, `expected_record_count`, and `bin_completeness` were verified to be descriptive diagnostic attributes.
   - These columns **must never be fed into baseline or deep learning imputation models** as input features, as doing so would leak ground truth presence inside masked evaluation windows.
4. **Hydronic Multi-Carrier Energy Diversity**:
   - The 8 thermal meters (`K11..K16`, `W11`, `K21`) with 6-minute median cadence achieved high occupied bin preservation ($71.01\% - 87.98\%$). They provide vital multi-carrier physical diversity alongside the 70 electrical meters.

---

## 6. Audit Conclusion & Gate Certification

- **Task**: P1-T3 (Build 15-Minute Regular Grid)
- **Protocol Conformance**: 100% compliant with Protocol v1.1 Official.
- **Invariant Breaches**: 0
- **Data Leaks**: 0
- **Mismatches in Population**: 0
- **Final Audit Verdict**: **PASS**

P1-T3 is formally certified as **AUDIT PASSED**. The pipeline artifacts and documentation are authoritative and verified ready for gating.
