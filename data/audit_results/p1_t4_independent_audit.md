# Independent Audit Report — Task P1-T4: Quality & Provenance Flags

- **Audit Target**: `data/interim/readings_15min_flagged.parquet`
- **Primary Input (P1-T3)**: `data/interim/readings_15min.parquet`
- **Executor Report**: `data/audit_results/p1_t4_report.md`
- **Protocol**: Protocol v1.1 (Official) — `TASK_PLAN.md`, `RESEARCH_PLAN.md`
- **Auditor Role**: Independent Verification & Forensics (Zero Modification)
- **Audit Timestamp**: 2026-10-07T09:55:00Z
- **Independent Audit Verdict**: **PASS WITH NOTES**

---

## 1. Executive Summary & Verdict

### Final Verdict: **PASS WITH NOTES**

An exhaustive, independent verification of Task P1-T4 ("Build Quality & Provenance Flags") was executed across all 13,981,597 output rows and all 79 meters. The verification was conducted without importing or reusing the executor's implementation code, using independently constructed Python/NumPy interval engines and raw YAML parsing.

All mandatory scientific invariants and protocol gates were verified 100%:
1. **P1-T3 Immutability**: 100% bit-for-bit identical for all 10 inherited columns. The float value buffer SHA-256 (`8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe`) matches bit-for-bit across all 13.98M rows.
2. **Missingness Invariant (`is_missing`)**: Exactly 648,020 empty bins (`raw_record_count == 0` and `value IS NULL`) have `is_missing = TRUE`; exactly 13,333,577 occupied bins have `is_missing = FALSE`.
3. **Empty Bins != Equipment Failure**: Exactly 527,803 empty bins (3.77% of dataset) outside authoritative issue intervals maintain `has_issue = FALSE`, rigorously respecting Protocol v1.1 Invariant 0.1e/0.6.
4. **Issue Reconciliation (`has_issue`)**: Exactly 815,656 bins intersect authoritative issue intervals (`has_issue = TRUE`), verified with zero false positives and zero false negatives against the independent baseline recomputation.
5. **Clean Ground Truth Invariant (`is_valid_ground_truth`)**: Exactly 12,638,138 rows (90.39%) satisfy `(~is_missing & ~has_issue & ~is_corrected)`.
6. **Corrected Raw Protection (`is_corrected`)**: 100% of rows have `is_corrected = FALSE`. Zero records from `_corrected_raw` contributed to authoritative values.
7. **Bit-for-Bit Determinism**: Re-execution of the pipeline into an isolated scratch directory produced an artifact with SHA-256 `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`, matching the production artifact byte-for-byte.
8. **Test Suite & Governance**: Unit tests pass 15/15; full repository test suite passes 64/64; `validate_state.py` passes; `gate.sh` returns `RESULT: GATE = PASS`; `check_scope.py` returns `ALLOWED`.

### Summary of Audit Notes (Non-blocking):
- **Note 1 (Boundary Sensitivity Analysis)**: Competing boundary interpretation B (set intersection including single boundary point $s = t$) would flag 1,143 additional bins (0.008% of all rows across 57 meters) compared to Interpretation A (positive-length continuous overlap, implemented by executor). This difference is scientifically non-material and fully documented below.
- **Note 2 (Upstream Copy-Paste in H1.Z19 Manual Issue)**: `H1.Z19_issues_manual.yaml` contains `reference: H2.Z311`, but filename and key prefix `H1.Z19@...` prove it belongs to H1.Z19. Attributed correctly with zero cross-meter contamination.
- **Note 3 (Outside Population Manual Files)**: `H3.ZE50_issues_manual.yaml` and `H3.ZE51_issues_manual.yaml` reference meters not present in the dataset (likely typographical references to Building 4 meters `H4.ZE50/51`). Because all internal fields specify `H3.ZE50/51`, they were not applied to `H4.ZE50/51`.

---

## 2. Independent Audit Method

To ensure absolute independence:
1. **Zero Executor Import**: The core audit logic was implemented without importing `etl/quality_flags.py` or calling its internal functions.
2. **Independent Interval Engine**: An independent interval parsing and interval-to-grid matching algorithm was developed from first principles in a dedicated scratch environment (`scratch/audit_*.py`).
3. **Exhaustive Row-Group Scanning**: The entire 13,981,597 row dataset across all 79 Parquet row groups was streamed and verified row-by-row.
4. **Independent YAML Parsing**: All 88 YAML issue files (81 automatic, 7 manual) were parsed independently using pure PyYAML, validating timestamps, key prefixes, references, and comments.
5. **Multi-Interpretation Sensitivity Engine**: An automated engine evaluated all 148,968 issue intervals against all grid bins under 3 competing mathematical boundary definitions.

---

## 3. Baseline & Immutability Snapshot

Prior to performing substantive audit operations, an authoritative cryptographic snapshot was established:

| Artifact / Path | SHA-256 Checksum | Audit Status |
|---|---|:---:|
| `TASK_PLAN.md` | `81cfbc3dba93574c6721c63d5974fa97bd6655d80b8f99dc1af365fd33b243fa` | Verified Unchanged |
| `RESEARCH_PLAN.md` | `73da22372c587c72a1e546e1584f734502d1dbd7d04756cad6ba7f1e0027ba93` | Verified Unchanged |
| `configs/default.yaml` | `6651f81c1ee8cf77a7b6786345f83cc96924f35c391f92da88d33170dc85abac` | Verified Unchanged |
| `configs/local.yaml` | `d2d17337de0d0b2e0fe36b4430c5a34b063549ccb2dc78203ecb9bef2d8b843a` | Verified Unchanged |
| `tests/test_P1_T4.py` | `3f90096bdc00ac620565949705c724033355fea6aa9a69d9907dfb179fd1bc6e` | Verified Unchanged |
| `control/task_state.yaml` | `75d45e9b1cd2c78ef0a9a1f82c620ba6db34e6c4f8afd84a631c0d901011ee88` | Verified Unchanged |
| `control/protected_paths.txt`| `4ee91e66cab2e9d6e93977a3e5685e849674a11e879bdd9f690afbc7d6fdc7bb` | Verified Unchanged |
| `control/protocol_hashes.txt`| `ac2cce0cc28f87d136e491644aae15135a65ec2946c7d3eba01329401350cec6` | Verified Unchanged |
| `data/interim/readings_15min.parquet` (P1-T3) | `f50a2ff27b142a895a8cabfbc0bcf3750aad28d5dcd5af2cb51a13628dce22dd` | Verified Unchanged |
| `data/interim/readings_15min_flagged.parquet` (P1-T4) | `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705` | Verified Production Target |

**Raw Dataset State**:
The authoritative external Honda dataset directory (`/run/media/duck/New Volume/Vice - Download/Honda_Dataset`) showed filesystem modification timestamps dating to `2026-10-02 17:54:10 +0700`, preceding P1-T4 execution. File contents and directory permissions were verified read-only and unmutated.

---

## 4. Artifact Existence & Schema

The output artifact `data/interim/readings_15min_flagged.parquet` was independently inspected:
- **Total Rows**: Exactly 13,981,597
- **Row Groups**: Exactly 79 (1 row group per meter)
- **Column Count**: Exactly 14 columns
- **Key Uniqueness**: `(meter_id, grid_timestamp_utc)` is unique with 0 duplicates; grid timestamps advance strictly in 15-minute intervals ($900\text{s}$) with 0 second/microsecond jitter.
- **Null Values**:
  - `meter_id`: 0 nulls
  - `grid_timestamp_utc`: 0 nulls
  - `timestamp_local`: 0 nulls
  - `raw_record_count`: 0 nulls
  - `expected_record_count`: 0 nulls
  - `bin_completeness`: 0 nulls
  - `cadence_class`: 0 nulls
  - `is_missing`: 0 nulls (`bool`)
  - `has_issue`: 0 nulls (`bool`)
  - `is_corrected`: 0 nulls (`bool`)
  - `is_valid_ground_truth`: 0 nulls (`bool`)
  - `value`: 648,020 nulls (4.63%)
  - `source_timestamp_utc`: 648,020 nulls (4.63%)
  - `raw_source_file`: 648,020 nulls (4.63%)

All four quality flags are strictly typed as `bool` (`pa.bool_()`).

---

## 5. Exhaustive P1-T3 Immutability

Every single row of all 79 row groups was compared directly between `readings_15min.parquet` (P1-T3) and `readings_15min_flagged.parquet` (P1-T4).

| Column | Equivalence Check | Result |
|---|---|:---:|
| `meter_id` | String equality across all 79 meters | **100.00% Identical** |
| `grid_timestamp_utc` | Microsecond timestamp equality | **100.00% Identical** |
| `timestamp_local` | Microsecond timestamp equality | **100.00% Identical** |
| `source_timestamp_utc` | Microsecond timestamp + null position equality | **100.00% Identical** |
| `value` | Bit-for-bit IEEE 754 float64 comparison | **100.00% Identical** |
| `value` (NaN positions) | NaN boolean mask comparison (648,020 NaNs) | **100.00% Identical** |
| `value` (SHA-256 buffer hash)| `8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe` | **100.00% Identical** |
| `raw_source_file` | String equality + null position equality | **100.00% Identical** |
| `raw_record_count` | Int32 equality across all rows | **100.00% Identical** |
| `expected_record_count`| Int32 equality across all rows | **100.00% Identical** |
| `bin_completeness` | Float64 equality across all rows | **100.00% Identical** |
| `cadence_class` | String equality across all rows | **100.00% Identical** |

**Verdict on P1-T3 Immutability**: PASS (Zero mutations introduced).

---

## 6. Exhaustive `is_missing` Verification

The flag `is_missing` was independently recomputed across all 13,981,597 rows according to the specification:
$$\text{is\_missing} = (\text{raw\_record\_count} == 0) \land (\text{value IS NULL})$$

- **Occupied Bins (`raw_record_count > 0`)**: Exactly 13,333,577 rows have `is_missing = FALSE`. All 13,333,577 rows have valid non-null floats, non-null `source_timestamp_utc`, and non-null `raw_source_file`.
- **Empty Bins (`raw_record_count == 0`)**: Exactly 648,020 rows have `is_missing = TRUE`. All 648,020 rows have `value = NaN`, `source_timestamp_utc = NULL`, and `raw_source_file = NULL`.
- **Mismatches**: Exactly 0.

---

## 7. Global Issue Source Forensics (All YAML Files)

An exhaustive forensic scan of all files in `/run/media/duck/New Volume/Vice - Download/Honda_Dataset/issues/` was conducted:
- **Automatic Issue Files**: 81 files (`automatic_issues/*.yaml`), totaling 148,958 logged issue records.
- **Manual Issue Files**: 7 files (`manual_issues/*.yaml`), totaling 10 logged issue records (plus 1 documentation template `1_issues_manual_template.yaml`).
- **Total Issue Records Scanned**: 148,968 records across 88 YAML files.

### Mismatch Inventory:
1. **Automatic Issue Channel Suffixes**: In automatic issue files, internal `reference` fields and issue key prefixes include channel designations (e.g. `H2.Z62.W`, `H2.Z62.WQ`, `H2.Z62.WQexp`, `H2.Z62.Wexp` inside `H2.Z62_issues_automatic.yaml`). These represent multi-channel measurements of the same physical meter. Mapping to the parent meter is consistent.
2. **`H1.Z19_issues_manual.yaml` Upstream Copy-Paste**:
   - YAML Key: `H1.Z19@transformer_factor@removal`
   - File Name: `H1.Z19_issues_manual.yaml`
   - Comment: `Z19 Munters: installation was removed in November 2022...`
   - Erroneous internal field: `reference: H2.Z311`
   - *Forensic Finding*: File naming, key prefix, and textual comment confirm meter `H1.Z19`. The internal field `H2.Z311` is a copy-paste artifact from authoring `H2.Z311_issues_manual.yaml`.
3. **Outside Population Issue Files**:
   - `H3.Z42_issues_automatic.yaml`: Meter `H3.Z42` (raw file was 0-byte empty, not in 79 core meters).
   - `WeatherStation.Weather_issues_automatic.yaml`: Meteorological sensor, not an electrical meter.
   - `H3.ZE50_issues_manual.yaml` and `H3.ZE51_issues_manual.yaml`: Nonexistent meters (likely typographical references to Building 4 meters `H4.ZE50` and `H4.ZE51`).

### Status of `H2.Z311`:
- `H2.Z311` has its own authoritative manual issue file: `H2.Z311_issues_manual.yaml`.
- It defines two genuine manual intervals:
  1. `2020-06-25 07:00:00 UTC` to `2021-02-10 13:32:00 UTC` (`transformer_factor@wrong`)
  2. `2020-11-12 10:08:49 UTC` to `2020-11-16 07:27:26 UTC` (`gap@energy_offline`)
- `H2.Z311` is **NOT omitted, NOT duplicated, NOT misassigned**, and **did NOT receive H1.Z19's issue interval**.

---

## 8. Issue Interval Validity Classification

Every issue interval across all 148,968 issue records was independently classified:

| Classification | Count | Description / Impact |
|---|:---:|---|
| **Valid Finite Interval** (`ts < te`) | **142,213** | Standard outage/anomaly intervals spanning continuous time. |
| **Zero-Duration Point Event** (`ts == te`)| **6,755** | Instantaneous measurement errors (`reason: zero` or spikes). Matched to the right-closed bin containing timestamp $t_s$. |
| **Reversed Interval** (`te < ts`) | **0** | None detected across all 88 files. |
| **Open-Ended Interval** (`end` absent) | **0** | None detected. All intervals have finite explicit bounds. |
| **Malformed / Unparseable Records** | **0** | None detected. All 148,968 records parsed cleanly. |
| **Exact Duplicate Intervals** | **4,256** | Duplicate intervals across multi-channel logs (e.g. W and WQ logged identical gap). Safely deduplicated. |
| **Overlapping Intervals** | **13** | Compound issues overlapping in time on the same meter. Safely unified via interval matching. |

---

## 9. Issue Type / Category Semantics

The 148,968 issue records span 6 distinct semantic categories:

| Reason / Category | Count | Sensor Phenomenon | Recommended Action in Source |
|---|:---:|---|---|
| `gap` | 142,207 | Data interruption, logger offline, power outage | `interpolate` / `integrate_pw` |
| `zero` | 6,752 | Erroneous zero drop during active consumption | `delete` |
| `transformer_factor` | 4 | Incorrect CT ratio (400:5 vs 500:5) or stray magnetic pickup | `transformer_factor` scaling |
| `single_leap` | 3 | Instantaneous voltage / power jump anomaly | `delete` |
| `lasting_leap` | 1 | Multi-year level shift / step change | `normalize_leap` |
| `errors` | 1 | Known corrupted register range | `delete_range` |

**Scientific Interpretation & Protocol Policy**:
100% of the logged issue categories represent **genuine physical anomalies, sensor miscalibrations, or transmission failures** for which data correction or deletion was prescribed by dataset engineers. None of these categories represent administrative or harmless informational events.

Therefore, invalidating all observations intersecting these issue intervals (`has_issue = TRUE`, `is_valid_ground_truth = FALSE`) is **strictly mandated by Protocol v1.1 Invariant 0.6** ("Ground truth chỉ lấy từ clean segment: không thiếu, không có issue, không bị corrected"). This policy protects downstream imputation models from training on corrupted or uncalibrated readings.

---

## 10. Issue Interval Boundary Semantics

The 15-minute grid representation is defined as right-closed, right-labeled:
$$\text{Bin}(t) = (t - 900\text{s}, t]$$

The source template `1_issues_manual_template.yaml` defines:
- `time_start`: "start-time of the issue (first erroneous timestamp)"
- `time_end`: "end-time of the issue (last erroneous timestamp)"

An independent evaluation of the 9 required exact boundary conditions was conducted:

| Test Case | Boundary Parameters | Baseline (Interpretation A) | Set Intersection (Interpretation B) | Notes |
|---|---|:---:|:---:|---|
| **Case 1** | Issue starts at left boundary ($s = t-900, e = t-600$) | **TRUE** | **TRUE** | Overlaps interior of bin |
| **Case 2** | Issue starts at right boundary ($s = t, e = t+300$) | **FALSE** | **TRUE** | Boundary instant touch ($s = t$) |
| **Case 3** | Issue ends at left boundary ($s = t-1200, e = t-900$) | **FALSE** | **FALSE** | Left boundary is open; empty intersection |
| **Case 4** | Issue ends at right boundary ($s = t-300, e = t$) | **TRUE** | **TRUE** | Overlaps interior up to closed right edge |
| **Case 5** | Issue fully contains bin ($s = t-1200, e = t+300$) | **TRUE** | **TRUE** | Full containment |
| **Case 6** | Issue fully contained in bin ($s = t-600, e = t-300$) | **TRUE** | **TRUE** | Strict interior subset |
| **Case 7** | Issue crosses grid boundary ($s = t-300, e = t+300$) | **TRUE** | **TRUE** | Spans across boundary |
| **Case 8** | Point event interior ($s = e = t-600$) | **TRUE** | **TRUE** | Contained in $(t-900, t]$ |
| **Case 8b** | Point event at right boundary ($s = e = t$) | **TRUE** | **TRUE** | Right edge is closed ($t \in \text{Bin}(t)$) |
| **Case 8c** | Point event at left boundary ($s = e = t-900$) | **FALSE** | **FALSE** | Left edge is open ($t-900 \notin \text{Bin}(t)$) |
| **Case 9** | Open-ended issue ($s = t-600, e = \infty$) | **TRUE** | **TRUE** | Spans from interior onward |

---

## 11. Issue Boundary Sensitivity Analysis

An exhaustive sensitivity analysis was executed across all 148,968 issue intervals and all 13,981,597 grid bins, comparing:
- **Interpretation A (Executor Baseline)**: Positive-length continuous overlap ($\mu((t-900, t] \cap [s, e]) > 0 \iff s < t \land e > t - 900$). Point events flagged if $t-900 < s \le t$.
- **Interpretation B (Strict Set Intersection)**: Any non-empty intersection ($[s, e] \cap (t-900, t] \neq \emptyset \iff s \le t \land e > t - 900$).
- **Interpretation C (Fully Closed Bin)**: $[s, e] \cap [t-900, t] \neq \emptyset \iff s \le t \land e \ge t - 900$.

### Quantitative Results:

| Metric | Interpretation B vs Baseline | Interpretation C vs Baseline |
|---|:---:|:---:|
| **Total Bins Changed** | **1,143** | **2,433** |
| **Percentage of Dataset** | **0.0082%** | **0.0174%** |
| **Changed FALSE $\to$ TRUE** | +1,143 | +2,433 |
| **Changed TRUE $\to$ FALSE** | 0 | 0 |
| **Affected Meters Count** | 57 meters | 57 meters |
| **Affected Issue Types** | `gap` (1,141), `transformer_factor` (2) | `gap` (2,431), `transformer_factor` (2) |

### Concrete Boundary Examples (Interpretation B):
1. `H1.K11` at `2021-10-27 18:15:00 UTC`: Issue interval `[2021-10-27 18:15:00, 18:54:00 UTC]`. In Interpretation A, bin `(18:00, 18:15]` is FALSE (overlap measure is 0) and bin `(18:15, 18:30]` is TRUE. In Interpretation B, bin `18:15` touches the point `18:15:00` and flips to TRUE.
2. `H1.K11` at `2021-11-12 06:00:00 UTC`: Issue interval `[2021-11-12 06:00:00, 06:30:00 UTC]`. Bin `06:00` flips from FALSE to TRUE under Interpretation B.

### Governance Assessment:
- The delta is extremely small (0.008% of all observations).
- Interpretation A represents standard signal processing practice (temporal integration over $(t-15\text{min}, t]$ requires non-zero measure of overlap).
- This ambiguity is non-material to benchmark rankings. Per governance instructions, this finding is recorded as a **PASS WITH NOTES**.

---

## 12. Exhaustive `has_issue` Reconstruction

Using the independent interval matching engine, `has_issue` was recomputed for all 13,981,597 rows:
- **Total `has_issue = TRUE`**: Exactly **815,656**
- **Total `has_issue = FALSE`**: Exactly **13,165,941**
- **False Positives vs P1-T4**: **0**
- **False Negatives vs P1-T4**: **0**
- **Exact Match Rate**: **100.0000%**

---

## 13. Four-Quadrant Breakdown (Empty Bin $\neq$ Equipment Failure)

Reconciling missingness and issue logs yields the exact four quadrants:

| Quadrant | State | Condition | Row Count | Percentage | Semantic Definition |
|:---:|---|---|:---:|:---:|---|
| **Q1** | Clean Observed | `is_missing=F, has_issue=F` | **12,638,138** | **90.39%** | Pure authentic ground truth observations |
| **Q2** | Issue Observed | `is_missing=F, has_issue=T` | **695,439** | **4.97%** | Observed readings during sensor/transformer anomalies |
| **Q3** | Unrelated Gap | `is_missing=T, has_issue=F` | **527,803** | **3.77%** | Observation gaps outside issue intervals (**NOT failure**) |
| **Q4** | Corroborated Gap | `is_missing=T, has_issue=T` | **120,217** | **0.86%** | Missing readings corroborated by authoritative issue log |
| **Total**| **All Rows** | — | **13,981,597** | **100.00%** | Exact match with P1-T3 input |

### Invariant Checks:
- $Q_2 + Q_4 = 695,439 + 120,217 = \mathbf{815,656}$ (`has_issue = TRUE`)
- $Q_3 + Q_4 = 527,803 + 120,217 = \mathbf{648,020}$ (`is_missing = TRUE`)
- **Key Scientific Finding Confirmed**: Exactly 527,803 empty bins (3.77% of all bins) are uncorroborated observation gaps and were **NOT** reclassified as equipment failure.

---

## 14. Exhaustive `is_valid_ground_truth` Verification

The hard invariant:
$$\text{is\_valid\_ground\_truth} == (\neg \text{is\_missing}) \land (\neg \text{has\_issue}) \land (\neg \text{is\_corrected})$$
was verified for every row of the 13,981,597 rows:
- **`is_valid_ground_truth = TRUE`**: Exactly **12,638,138**
- **`is_valid_ground_truth = FALSE`**: Exactly **1,343,459**
- **Identity**: $\text{is\_valid\_ground\_truth} \equiv Q_1$ (12,638,138 rows).
- **Mismatches**: Exactly 0.

---

## 15. H1.Z19 Mapping Exception Audit

Forensic inspection of `issues/manual_issues/H1.Z19_issues_manual.yaml`:
- Issue: `H1.Z19@transformer_factor@removal`
- Range: `2022-02-28 23:00:00 UTC` to `2024-03-31 23:00:00 UTC` ($18,288$ hours)
- Impact on H1.Z19: Flagged 68,558 grid bins (`has_issue = TRUE`).
- Impact on H2.Z311: **Zero bins affected**. `H2.Z311` was evaluated strictly using its own issue files (`H2.Z311_issues_automatic.yaml` and `H2.Z311_issues_manual.yaml`).
- **No cross-meter contamination occurred**.

---

## 16. Outside-Population Issue Files

Four issue files in `/issues/` belong to meters outside the approved 79-meter core population:
1. `automatic_issues/H3.Z42_issues_automatic.yaml`: Meter `H3.Z42` (excluded in P1-T1 due to 0-byte raw file).
2. `automatic_issues/WeatherStation.Weather_issues_automatic.yaml`: Meteorological station (not electrical).
3. `manual_issues/H3.ZE50_issues_manual.yaml`: No meter `H3.ZE50` exists in raw dataset.
4. `manual_issues/H3.ZE51_issues_manual.yaml`: No meter `H3.ZE51` exists in raw dataset.

**Verification**: None of these outside issue files were applied to the 79 core meters. Specifically, `H4.ZE50` and `H4.ZE51` were processed using their own automatic issue logs (`H4.ZE50_issues_automatic.yaml` and `H4.ZE51_issues_automatic.yaml`), retaining 61,470 clean ground truth bins each.

---

## 17. Timezone / DST Integrity

1. **Explicit Offsets**: 100% of all 148,968 issue timestamps are either unix epoch integers (inherently UTC) or ISO 8601 strings with explicit numeric offsets (`+0100`, `+0200`, `+0300`, `Z`).
2. **Zero Naive Ambiguity**: No naive timestamps exist in the issue source.
3. **No Local Comparisons**: Grid timestamps and issue timestamps were converted to canonical integer UTC seconds prior to range matching. Europe/Berlin DST transitions (autumn repeated hour / spring skip) did not produce spurious boundary shifts.

---

## 18. H1.ZE20 Verification

- Installation Date: Commissioned `2022-11-30 08:18:47 UTC`.
- Grid Boundary: Grid starts at $\text{ceil\_15m}(08:18:47) = \text{2022-11-30 08:30:00 UTC}$.
- Grid Duration: Exactly 38,075 rows from `2022-11-30 08:30:00` to `2023-12-31 23:00:00 UTC`.
- Zero synthetic rows created prior to installation.

---

## 19. Corrected Raw Protection

Lineage analysis of `readings_15min_flagged.parquet` and `readings_utc.parquet`:
- Zero rows originated from `_corrected_raw` files.
- `is_corrected = FALSE` for 100% of rows (0 / 13,981,597).
- Ground truth is derived exclusively from uncontaminated primary raw observations.

---

## 20. Leakage Guardrails

- `raw_record_count`, `expected_record_count`, and `bin_completeness` remain purely descriptive metadata.
- No model feature columns were added.
- In masked evaluation windows in downstream stages, descriptive counts must remain withheld per `configs/default.yaml`.

---

## 21. Determinism Audit

- Production Output SHA-256: `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`
- Scratch Regeneration Output SHA-256: `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`
- Match: **100% bit-for-bit identical**.

---

## 22. Test Suite & Governance Gate Results

The independent auditor executed all automated tests and control tools:
1. `pytest tests/test_P1_T4.py -v`: **15 passed** in 16.35s
2. `pytest tests/`: **64 passed** in 46.23s
3. `python3 control/validate_state.py`: **[OK] Task state is valid**
4. `bash control/gate.sh`: **RESULT: GATE = PASS**
5. `python3 control/check_scope.py`: **ALLOWED: No modified files detected**

---

## 23. Limitations & Audit Notes

1. **Boundary Ambiguity**: Under Interpretation B (set intersection including point $s = t$), 1,143 bins would flip from False to True across 57 meters. The executor's implementation adopts positive-length continuous overlap ($\mu > 0$), which is standard in signal processing. This note is non-blocking.
2. **Upstream Annotation Typo**: `issues/manual_issues/H3.ZE50_issues_manual.yaml` and `H3.ZE51_issues_manual.yaml` appear to be upstream misnamings for Building 4 meters `H4.ZE50/51`. They were correctly left unmapped, preserving valid sensor history.

---

## 24. Governance Handoff

In strict accordance with AGENTS.md:
- The independent auditor has **NOT modified** `control/task_state.yaml`.
- `control/task_state.yaml` currently records `current_task: P1-T3` and `P1-T4: BLOCKED` (executor complete / awaiting gate).
- **Gating is a governance action performed by the human/orchestrator after reviewing this independent audit report, not an action performed by the auditor.**
- Task P1-T5 remains strictly **BLOCKED** until that separate administrative transition is executed.
