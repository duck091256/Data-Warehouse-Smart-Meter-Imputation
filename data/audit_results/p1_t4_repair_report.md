# AUDIT & REPAIR REPORT: TASK P1-T4 TARGETED REPAIR

## Adopt Ratified Protocol v1.1 Amendment — Issue Interval Set Intersection

- **Project**: Beyond Synthetic Missingness — Smart-Meter Imputation
- **Task ID**: P1-T4 (Quality & Provenance Flags)
- **Protocol**: Protocol v1.1 + Ratified Targeted Amendment (P1-T4 Issue-Interval Overlap Semantics)
- **Decision Ratified**: Strict Interpretation B ($\text{Bin}(t) \cap I \neq \emptyset$)
- **Execution Timestamp (UTC)**: 2026-10-07T18:08:07Z
- **Repair Status**: **REPAIR COMPLETED / ALL HARD DELTA INVARIANTS PASSED 100%**

---

## 1. Old Artifact SHA-256

- **File Path**: `data/interim/readings_15min_flagged.parquet`
- **Old Checksum (SHA-256)**:
  `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`
- **Old Row Count**: 13,981,597 rows

---

## 2. New Artifact SHA-256

- **File Path**: `data/interim/readings_15min_flagged.parquet`
- **New Checksum (SHA-256)**:
  `c672d5a4efc6cb636708480675e6a2947c436373b05f1bfb8e3307dc9299d279`
- **New Row Count**: 13,981,597 rows (conserved 100.00%)
- **Compression**: SNAPPY (Parquet v2.6, 79 row groups)

---

## 3. Exact Changed-Row Count

Comparing the pre-repair production artifact against the repaired production artifact across all 13,981,597 rows:

```text
has_issue transitions:
    FALSE → TRUE :    1,143
    TRUE  → FALSE :        0
    Unchanged     : 13,980,454
    Total Rows    : 13,981,597

Pre-repair has_issue TRUE :   815,656
Post-repair has_issue TRUE:   816,799
Net Delta                 :    +1,143 (+0.140%)
```

---

## 4. Changed-Row Classification

Every one of the 1,143 differing bins satisfies:
$$\text{issue\_start} == \text{grid\_timestamp\_utc} \quad (s == t) \quad \land \quad \text{issue\_start} < \text{issue\_end} \quad (s < e)$$

The 1,143 rows span **57 core meters** and classify into two distinct groups:

1. **Occupied Bins (`is_missing == False`)**: **1,096 bins**
   - **Subcase 1 (`source_timestamp_utc == t`)**: **923 bins (84.22%)**
     - Raw sensor reading selected by deterministic `LAST` operator was recorded at the exact integer second $t$.
     - Authoritative issue logs explicitly define $s = t$ as the *"first erroneous timestamp"*.
     - Under the old $A_{\text{code}}$ rule, these 923 corrupted readings were admitted into Clean Ground Truth ($Q_1$).
     - Under Ratified Interpretation B, they are safely identified as active failures and moved to $Q_2$.
   - **Subcase 2 (`source_timestamp_utc < t`)**: **173 bins (15.78%)**
     - Raw sensor reading recorded within $(t - 900\text{s}, t - 1\text{s}]$.
     - Conservatively excluded from Clean Ground Truth into $Q_2$.
2. **Empty Bins (`is_missing == True`, `value == NaN`, `raw_record_count == 0`)**: **47 bins**
   - Reclassified from $Q_3$ (Unrelated Gap) to $Q_4$ (Corroborated Outage Gap).
   - Neither rule admits empty bins into ground truth.

---

## 5. Q1–Q4 Before and After

The four-quadrant distribution across all 13,981,597 grid rows:

| Quadrant | Semantic State | Flag Condition | Old Artifact ($A_{\text{code}}$) | New Artifact (Ratified B) | Exact Delta | Direction |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **$Q_1$** | **Clean Observed** | `!missing & !issue` | 12,638,138 | **12,637,042** | **-1,096** | Move to $Q_2$ |
| **$Q_2$** | **Issue Observed** | `!missing & issue` | 695,439 | **696,535** | **+1,096** | From $Q_1$ |
| **$Q_3$** | **Unrelated Gap** | `missing & !issue` | 527,803 | **527,756** | **-47** | Move to $Q_4$ |
| **$Q_4$** | **Corroborated Gap** | `missing & issue` | 120,217 | **120,264** | **+47** | From $Q_3$ |
| **Total** | **All Grid Rows** | — | **13,981,597** | **13,981,597** | **0** | **Conserved 100%** |

### Invariant Balances Verified:
- Total rows conserved: $\sum Q_i = 13,981,597$
- Occupied bins conserved: $Q_1 + Q_2 = 13,333,577$
- Empty bins conserved: $Q_3 + Q_4 = 648,020$
- Issue flag delta: $\Delta Q_2 + \Delta Q_4 = +1,096 + 47 = \mathbf{+1,143}$

---

## 6. Ground-Truth Count Before and After

- **Pre-Repair (`is_valid_ground_truth = True`)**: `12,638,138` bins (90.39%)
- **Post-Repair (`is_valid_ground_truth = True`)**: `12,637,042` bins (90.38%)
- **Exact Delta**: **-1,096 bins**
- **Validation**: `is_valid_ground_truth` changes **exclusively** on the 1,096 occupied bins; 0 empty bins changed ground truth flag.

---

## 7. Value and Provenance Integrity

The following 12 inherited columns are **100% bit-for-bit identical** between the old and repaired artifact:
- `meter_id`
- `grid_timestamp_utc`
- `timestamp_local`
- `source_timestamp_utc`
- `value`
- `raw_source_file`
- `raw_record_count`
- `expected_record_count`
- `bin_completeness`
- `cadence_class`
- `is_missing`
- `is_corrected` (False for 100% of rows; 0 corrected files)

### Cryptographic Buffer Checksums:
- **Value Buffer SHA-256**: `8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe` (bit-for-bit identical)
- **NaN Count**: Exactly `648,020` NaN positions match bit-for-bit.
- Zero values created, deleted, interpolated, or shifted.

---

## 8. Issue-Boundary Validation

1. **Boundary-Start Inclusion ($s == t$)**:
   - Evaluated under $s \le t \land e > t - 900\text{s}$.
   - Every bin where an issue interval starts at the exact second $t$ evaluates to `has_issue = True`.
   - Verified on representative real cases (e.g. `H1.Z19` manual removal issue starting at `2022-02-28 23:00:00 UTC`).
2. **Left-Boundary Exclusion ($e == t - 15\text{min}$)**:
   - Evaluated under $e > t - 900\text{s}$ (strict inequality).
   - Because the left boundary of $\text{Bin}(t) = (t - 900\text{s}, t]$ is open, an issue ending at $t - 900\text{s}$ evaluates to `False`.
   - Verified via unit test and empirical scan (all 10 issue intervals in dataset ending at $e = t - 900\text{s}$ correctly exclude the open-left bin).

---

## 9. Zero-Duration Validation

- Authoritative issue logs contain 5,937 zero-duration records ($s == e$) across the 79 core meters.
- Deduplication yields 1,683 unique $(meter, timestamp, reason)$ point events.
- In **1,639 bins**, a positive-duration interval already covers the bin.
- In **44 bins**, only isolated zero-duration point events exist.
- Under unified Interpretation B ($s \le t \land e > t - 900\text{s}$), all 44 isolated interior bins evaluate to `has_issue = True`.
- Zero zero-duration events were added, removed, or double-counted.

---

## 10. Test Execution Results

- `pytest tests/test_P1_T4.py -v`: **16 passed in 25.83s (100%)**
  - Includes dedicated tests for boundary-start ($s = t$), open left boundary ($e = t - 15\text{min}$), interior zero-duration, label zero-duration, and regression delta.
- `pytest tests/`: **65 passed in 47.46s (100%)**
  - Full project test suite passed with zero errors or regressions.

---

## 11. Control Gate Execution

Running `bash control/gate.sh`: **RESULT: GATE = PASS** (100% checks passed).

---

## 12. Scope Verification

- `python3 control/check_scope.py`: **ALLOWED / PASSED**
- Protected paths (`data/raw/*`) remained 100% untouched and read-only.
- Task boundaries strictly respected; no downstream P1-T5/P2 modules modified.

---

## 13. Implementation Files Modified

1. **`etl/quality_flags.py`**:
   - Replaced old $A_{\text{code}}$ branching in `match_grid_issues` with unified ratified non-empty set intersection formula ($s \le t \land e > t - 900\text{s}$).
   - Updated audit report generation text to dynamic metric formatting and ratified protocol notes.
2. **`tests/test_P1_T4.py`**:
   - Updated `test_t4_07b_match_grid_issues_boundary_unit` to assert ratified set intersection semantics.
   - Updated `test_t4_07_issue_matching_boundary_cases` H1.Z19 test to reflect $s = t$ boundary start inclusion (`2022-02-28 23:00:00 UTC`).
   - Updated `test_t4_08_no_false_failure_inference` to verify 527,756 unrelated gaps.
   - Added `test_t4_15_regression_ratified_delta` validating exact 1,143 delta, quadrant counts, and ground truth yield.
3. **`TASK_PLAN.md`**:
   - Synchronized Task P1-T4 specification and added Detailed P1-T4 Acceptance Criteria section with ratified counts.
4. **`RESEARCH_PLAN.md`**:
   - Added Section 8 P1-T4 Acceptance Criteria & Verification Matrix matching ratified numbers.
5. **`configs/default.yaml`**:
   - Added `etl.issue_overlap` configuration block declaring non-empty intersection semantics.
6. **`reports/protocol_v1_1_amendment.md`**:
   - Appended Section 10 officially recording ratification of the P1-T4 Issue Overlap Semantics amendment.
7. **`control/protocol_hashes.txt`**:
   - Recomputed and saved via `control/protocol_hash.sh --save`. Verified via `control/protocol_hash.sh --verify`.
8. **Artifacts Regenerated**:
   - `data/interim/readings_15min_flagged.parquet`
   - `data/interim/readings_15min_flagged_metadata.json`
   - `data/audit_results/p1_t4_report.md`
   - `reports/p1_t4_log.md`

---

## 14. Deviations

- **Zero deviations** from ratified protocol specifications or invariant requirements.
- `control/task_state.yaml` was **NOT modified** (remains in previous state per governance mandate).
- Task P1-T4 was **NOT marked GATED**.
- Task P1-T5 remains **BLOCKED** pending independent re-audit.
