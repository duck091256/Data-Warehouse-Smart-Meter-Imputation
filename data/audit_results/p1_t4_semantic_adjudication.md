# Semantic Adjudication & Governance Review Report — Task P1-T4: Quality & Provenance Flags

- **Target Task**: Task P1-T4 — Build Quality & Provenance Flags
- **Protocol**: Protocol v1.1 (Official) — `TASK_PLAN.md`, `RESEARCH_PLAN.md`
- **Role**: Semantic Adjudicator & Governance Reviewer (Independent Scientific Review)
- **Review Date**: 2026-10-07
- **Target Artifact**: `data/interim/readings_15min_flagged.parquet`
- **Predecessor Artifact (P1-T3)**: `data/interim/readings_15min.parquet`
- **Governing Charter**: `AGENTS.md` (Sections 1–9)

---

## 1. Executive Summary & Final Verdict

### Final Adjudication Verdict: **`AMENDMENT_REQUIRED`**

#### Core Determination:
1. **Source & Protocol Silence**: Protocol v1.1 (`TASK_PLAN.md`, `RESEARCH_PLAN.md`, `reports/protocol_v1_1_amendment.md`) rigorously specifies the regular 15-minute grid representation as half-open, right-closed intervals $\text{Bin}(t) = (t - 15\text{min}, t]$ with the deterministic `LAST` operator. However, Protocol v1.1 is **genuinely silent** regarding the mathematical definition of issue-interval overlap for setting `has_issue`: it does not explicitly specify whether overlap requires positive Lebesgue measure ($\mu(B(t) \cap I) > 0$, **Interpretation A**) or any non-empty set intersection ($B(t) \cap I \neq \emptyset$, **Interpretation B**).
2. **Empirical Materiality (1,143 Bins)**: Independent reconstruction confirms that Interpretation A and Interpretation B produce differing boolean labels across **1,143 grid bins** (0.0082% of the dataset) spanning **57 core meters**.
3. **Physical Sensor Contamination Under A**: Forensics on the 1,143 differing bins reveal that **923 occupied bins** contain a raw observation whose physical timestamp equals the exact second $t$ ($\text{source\_timestamp\_utc} == t$). According to authoritative issue metadata (`1_issues_manual_template.yaml`), timestamp $s$ is explicitly defined as the *"first erroneous timestamp"*. Consequently, Interpretation A retains **923 physical observations recorded during sensor/system failures** as authentic ground truth ($Q_1$), in tension with Protocol v1.1 Invariant 0.6 (*"Ground truth chỉ lấy từ clean segment: không thiếu, không có issue, không bị corrected"*).
4. **Governance Rule Against Silent Production Decisions**: In accordance with `AGENTS.md` Rule 1 and Rule 8, an adjudicator cannot unilaterally alter or invent a protocol rule without formal ratification. Because the source and protocol are silent and the empirical divergence is non-empty, **no production rule may be silently chosen**. A targeted **Protocol v1.1 Amendment** must be formally enacted by the Protocol Owner to ratify Interpretation B (or explicitly confirm A) before final gating.
5. **Artifact Status**: The existing P1-T4 artifact (`SHA-256: 4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`), which implements Interpretation A, remains unmodified. Gating of P1-T4 is held in abeyance pending Protocol Owner amendment officialization.

---

## 2. Pre-Declared Decision Hierarchy

In strict adherence to governance instructions, the following decision hierarchy was pre-declared prior to empirical evaluation:

### Priority 1 — Source & Protocol Evidence
An explicit mathematical rule from the governing documents takes supreme precedence:
- Protocol v1.1 amendments (`reports/protocol_v1_1_amendment.md`)
- `TASK_PLAN.md` (Protocol v1.1)
- `RESEARCH_PLAN.md` (Protocol v1.1)
- Raw issue ticket documentation & YAML templates (`issues/manual_issues/1_issues_manual_template.yaml`)
- Source dataset documentation (Honda Research Institute)

### Priority 2 — Protocol-Consistent Scientific Interpretation
If the source does not provide an explicit algebraic intersection formula, inspect whether existing protocol conventions imply a preferred rule:
- A grid timestamp $t$ represents the aggregation window $(t - 15\text{min}, t]$ with the `LAST` representative observation operator.
- If an issue begins at $s = t$, determine whether the physical reading mapped to $t$ is contaminated by the failure event.

### Priority 3 — Conservative Ground-Truth Criterion
If the source and protocol remain silent:
- Consider the scientific asymmetry of the error:
  - Retaining a contaminated bin into ground truth ($Q_1$) violates scientific integrity by training downstream models on corrupted readings (false negative error for `has_issue`).
  - Excluding an extra bin at the instantaneous boundary $s = t$ acts conservatively by shielding clean ground truth from potential contamination (false positive error for `has_issue`, safe for ground truth).
- Neither A nor B shall be labeled "standard"; both are mathematically precise hypotheses evaluated under scientific prudence.

### Final Governance Requirement
Whatever rule is ultimately selected must be justified with complete empirical evidence and formally incorporated into the protocol. Because the protocol is silent, this requires a formal Protocol Amendment.

---

## 3. Cryptographic Baseline & Environment Snapshot

Before executing substantive forensic analysis, an independent cryptographic snapshot was established:

| Component / Artifact | Path | SHA-256 Checksum | Immutability Status |
|---|---|---|:---:|
| Research Protocol | `TASK_PLAN.md` | `81cfbc3dba93574c6721c63d5974fa97bd6655d80b8f99dc1af365fd33b243fa` | Verified Unchanged |
| Research Plan | `RESEARCH_PLAN.md` | `73da22372c587c72a1e546e1584f734502d1dbd7d04756cad6ba7f1e0027ba93` | Verified Unchanged |
| Pipeline Config | `configs/default.yaml` | `6651f81c1ee8cf77a7b6786345f83cc96924f35c391f92da88d33170dc85abac` | Verified Unchanged |
| Unit Test Suite | `tests/test_P1_T4.py` | `3f90096bdc00ac620565949705c724033355fea6aa9a69d9907dfb179fd1bc6e` | Verified Unchanged |
| P1-T3 Input Artifact | `data/interim/readings_15min.parquet` | `f50a2ff27b142a895a8cabfbc0bcf3750aad28d5dcd5af2cb51a13628dce22dd` | Verified Unchanged |
| P1-T4 Production Target | `data/interim/readings_15min_flagged.parquet` | `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705` | Verified Unchanged |
| Control State | `control/task_state.yaml` | `75d45e9b1cd2c78ef0a9a1f82c620ba6db34e6c4f8afd84a631c0d901011ee88` | Verified Unchanged |

Working tree modifications check:
- `git status --short`: Zero tracked files modified; repository working tree pristine.
- `git diff --name-only`: Empty.
- Scratch environment: Isolated in dedicated external scratch space (`/home/duck/.gemini/antigravity/brain/c311eef3-7d1a-40b2-a6e6-dd1520d5376e/scratch/`).

---

## 4. CHECK 1 — Source & Protocol Evidence

An exhaustive textual and legal inspection of all protocol specifications and source metadata was performed:

### 1. Does Protocol v1.1 explicitly define issue interval semantics?
**No.** `TASK_PLAN.md` mentions P1-T4 in Section P1 as:
> *`P1-T4 | Đánh dấu cờ chất lượng từng điểm: missing, có issue log, corrected | readings + issue logs + correction logs | cột cờ is_missing, has_issue, is_corrected | Tổng điểm có cờ khớp số dòng trong issue/correction logs`*

In `RESEARCH_PLAN.md` Section 6, P1-T4 is described as:
> *`quality flags marking (P1-T4), clean segments extraction (P1-T5)...`*

In `reports/protocol_v1_1_amendment.md` Section 7:
> *`2. P1-T4 Quality Flags: Flags (is_missing, flatline, spike, etc.) operate on the standardized 15-minute grid.`*

Nowhere in the protocol is an explicit mathematical set-overlap formula provided for `has_issue`.

### 2. Does it define issue intervals as $[s,e]$, $[s,e)$, $(s,e]$, or $(s,e)$?
**No.** Protocol v1.1 does not define the topological openness or closedness of issue intervals.

### 3. Does it define what it means for a grid bin to be issue-affected?
**No.** Protocol v1.1 defines the grid bin as half-open, right-closed: $\text{Bin}(t) = (t - 15\text{min}, t]$, and mandates that clean ground truth cannot have issues (`~has_issue`), but leaves the mapping between continuous issue intervals and grid bins algebraically unspecified.

### 4. Does it specify whether boundary-point contact counts?
**No.** Protocol v1.1 is silent on whether contact at boundary point $s = t$ constitutes an issue intersection.

### 5. Does source documentation state that `start` is the first erroneous timestamp and `end` is the last erroneous timestamp?
**Yes.** Authoritative evidence from `issues/manual_issues/1_issues_manual_template.yaml`:
```yaml
10:   time_end: 1532098560  # end-time of the issue (last erroneous timestamp) as unix time stamp
11:   time_start: 1532000040  # start-time of the issue (first erroneous timestamp) as unix time stamp
```
This is the only explicit authoritative statement regarding issue timestamp semantics in the entire dataset.

### 6. Does any documentation imply whether the endpoint is inclusive?
**Yes.** By defining `time_start` as the *"first erroneous timestamp"* and `time_end` as the *"last erroneous timestamp"*, the source documentation indicates that the timestamps $s$ and $e$ are themselves part of the erroneous episode. Therefore, physical sensor readings recorded at $s$ or $e$ are contaminated.

---

## 5. CHECK 2 — Exhaustive 1,143-Bin Assertion

Both candidate semantics were independently implemented from first principles and executed across all 13,981,597 rows of `readings_15min_flagged.parquet`:
- **Interpretation A (Positive-Duration Continuous Overlap)**:
  $$\text{has\_issue}_A(t) \iff \mu((t - 900, t] \cap [s, e]) > 0 \iff (s < t) \land (e > t - 900)$$
  *(For point events $s == e$: $t - 900 < s \le t$)*
- **Interpretation B (Non-Empty Set Intersection)**:
  $$\text{has\_issue}_B(t) \iff (t - 900, t] \cap [s, e] \neq \emptyset \iff (s \le t) \land (e > t - 900)$$

### Exhaustive Quantitative Verification:
- **Total Differing Bins**: Exactly **1,143**
- **False $\to$ True Changes (A $\to$ B)**: Exactly **+1,143**
- **True $\to$ False Changes (A $\to$ B)**: Exactly **0**
- **Affected Core Meters**: Exactly **57 meters**
- **Count Where $s == t$**: Exactly **1,143** (100.000%)
- **Count Where $e == t - 15\text{min}$ Causes Difference**: Exactly **0**
  *(Note: In 10 of the 1,143 bins, an earlier issue interval happened to end at $e = t - 900$, but detailed investigation proved that the $e = t - 900$ boundary was not responsible for the difference; the difference in all 10 cases was entirely driven by an active interval starting at $s = t$)*
- **Interior Overlap Differences**: Exactly **0**
- **Other Boundary Exceptions**: Exactly **0**

### Mandatory Assertion Result:
$$\mathbf{all}(A \neq B \text{ rows}) \implies \text{issue\_start} == \text{grid\_timestamp\_utc}$$
**VERDICT: TRUE (Exhaustively verified 1,143 out of 1,143 differences).**

### Affected Issue Types Across Differing Bins:
- `gap`: 1,141 intervals
- `transformer_factor`: 2 intervals (`H2.Z311` at `2020-06-25 07:00:00 UTC` and `H1.Z19` at `2022-02-28 23:00:00 UTC`)

---

## 6. CHECK 3 — Special Issue Intervals Inventory

An exhaustive audit of all 148,968 issue records across all issue files yielded the following complete taxonomy:

| Category | Count | Meters Affected | Semantics & Impact Under A vs B |
|---|:---:|:---:|---|
| **Zero-Duration Point Events** (`s == e`) | **6,755** | 38 meters | Composed of 6,752 `zero` drops and 3 `single_leap` spikes. Under A: flagged if $t - 900 < s \le t$. Under B: $(t-900, t] \cap \{s\} \neq \emptyset \iff t - 900 < s \le t$. **A and B treat zero-duration intervals identically.** Zero differences between A and B arise from point events. |
| **Missing / Open-Ended End** (`end IS NULL`) | **0** | 0 meters | All 148,968 records possess explicit, finite numeric or ISO timestamp bounds. No open-ended ambiguity exists. |
| **Reversed Intervals** (`e < s`) | **0** | 0 meters | Zero reversed intervals exist in the dataset. |
| **Malformed / Unparseable Records** | **0** | 0 meters | 100% of records parsed successfully. |
| **Exact Duplicate Intervals** | **4,869** | Multi-channel | Exact identical intervals generated by multi-channel power analyzers (e.g. logging active power `W`, reactive power `WQ`, export `Wexp` simultaneously). Deduplication is idempotent; duplicate matching does not alter boolean flags. |
| **Overlapping Intervals (Non-Identical)** | **2,726** | 6 meters | Occurs on `H1.W12`, `H1.Z19`, `H1.Z310`, `H2.Z311`, `H3.Z312`, `V.K21`. Notably on `H1.W12`, a multi-year lasting leap (`2020-12-21 23:09:00` to `2023-12-31 23:00:00 UTC`) overlaps short communication gaps. Both A and B evaluate boolean flags via set union ($\bigcup$), so presence of multiple overlapping intervals evaluates to `True` without requiring priority/precedence. |

---

## 7. CHECK 4 — Physical Sensor Timestamps in the 1,143 Differing Bins

To evaluate Priority 2 (Scientific Interpretation) and Priority 3 (Conservative Ground-Truth), the actual raw readings residing in the 1,143 differing bins were forensically inspected:

### Breakdown of the 1,143 Differing Bins:
- **Empty Bins (`is_missing == True`)**: **47 bins**
  - These bins have `raw_record_count == 0` and `value = NaN`.
  - Under A: classified as $Q_3$ (Unrelated Gap: `is_missing=T, has_issue=F`).
  - Under B: classified as $Q_4$ (Corroborated Gap: `is_missing=T, has_issue=T`).
  - Neither A nor B ever admits empty bins into ground truth.
- **Occupied Bins (`is_missing == False`)**: **1,096 bins**
  - **Case 1: Observation at exact boundary ($\text{source\_timestamp\_utc} == t$)**: **923 bins (84.22%)**
    - The raw sensor observation selected by the `LAST` operator was recorded at the exact integer second $t$.
    - Because the issue ticket states that $s = t$ is the *"first erroneous timestamp"*, **these 923 physical observations were captured during active sensor/system failure**.
    - **Under Interpretation A**: `has_issue = False` $\implies$ admitted into Clean Ground Truth ($Q_1$).
    - **Under Interpretation B**: `has_issue = True` $\implies$ safely excluded from Ground Truth ($Q_2$).
  - **Case 2: Observation strictly before boundary ($\text{source\_timestamp\_utc} < t$)**: **173 bins (15.78%)**
    - The raw observation was recorded between $t - 900\text{s}$ and $t - 1\text{s}$ (time delta $t - \text{src\_t}$ ranging from $1\text{s}$ to $600\text{s}$, median $15\text{s}$).
    - The sensor reading occurred strictly prior to the issue start.
    - Under Interpretation A: admitted into $Q_1$.
    - Under Interpretation B: excluded from $Q_1$ (conservative exclusion of the boundary bin).

### Scientific Implication:
Interpretation A fails to protect Clean Ground Truth from 923 known erroneous sensor readings, directly violating Protocol v1.1 Invariant 0.6. Interpretation B successfully isolates these 923 contaminated readings while conservatively excluding 173 borderline readings and reclassifying 47 empty bins.

---

## 8. CHECK 6 — Downstream Impact of Interpretation A vs Interpretation B

The complete downstream four-quadrant distribution and ground-truth yield were independently calculated:

| Quadrant / Metric | Interpretation A (Baseline) | Interpretation B (Set Intersection) | Delta ($B - A$) | Relative Shift |
|---|:---:|:---:|:---:|:---:|
| **`has_issue` Total** | **815,656** | **816,799** | **+1,143** | +0.140% |
| **Q1 (Clean Observed)** | **12,638,138** | **12,637,042** | **-1,096** | -0.0087% |
| **Q2 (Issue Observed)** | **695,439** | **696,535** | **+1,096** | +0.158% |
| **Q3 (Unrelated Gap)** | **527,803** | **527,756** | **-47** | -0.0089% |
| **Q4 (Corroborated Gap)** | **120,217** | **120,264** | **+47** | +0.039% |
| **`is_valid_ground_truth`** | **12,638,138** | **12,637,042** | **-1,096** | -0.0087% |
| **Total Grid Rows** | **13,981,597** | **13,981,597** | **0** | 100.00% conserved |

### Invariant Balance Equations:
- $\Delta Q_1 + \Delta Q_2 = -1,096 + 1,096 = 0$ (Occupied bins conserved at 13,333,577)
- $\Delta Q_3 + \Delta Q_4 = -47 + 47 = 0$ (Empty bins conserved at 648,020)
- $\Delta Q_2 + \Delta Q_4 = +1,096 + 47 = \mathbf{+1,143} = \Delta \text{has\_issue}$

---

## 9. CHECK 7 — Reconciliation of the 64 vs 62 Test Count Discrepancy

An investigation of the discrepancy between the Executor report ("62/62 tests passing") and the Independent Auditor report ("64/64 tests passing") was conducted:

### Findings:
1. `pytest --collect-only -q` across the entire repository currently collects exactly **64 test items**:
   - `tests/test_P1_T1.py`: 8 tests
   - `tests/test_P1_T2.py`: 12 tests
   - `tests/test_P1_T3.py`: 14 tests
   - `tests/test_P1_T4.py`: 15 tests
   - `tests/test_control_layer.py`: 7 tests
   - `tests/test_external_raw_config.py`: 8 tests
   - **Total**: $8 + 12 + 14 + 15 + 7 + 8 = \mathbf{64}$ tests.
2. In `p1_t4_report.md` Section 13, the Executor initially documented 13 tests for P1-T4 (`T4-01` through `T4-13`), giving a repository total of $8 + 12 + 14 + 13 + 7 + 8 = \mathbf{62}$ tests.
3. Prior to final handoff, two additional rigorous unit tests were added to `tests/test_P1_T4.py`:
   - `test_t4_07b_match_grid_issues_boundary_unit` (direct unit test of boundary edge cases)
   - `test_t4_14_value_checksum_identity` (explicit value column buffer SHA-256 hash invariant)
4. This increased the test count in `test_P1_T4.py` from 13 to 15, and the full repository test suite from 62 to 64.
5. **Governance Conclusion**: Zero tests were skipped, lost, or deleted. The difference represents legitimate test suite hardening.

---

## 10. CHECK 8 — Reconciliation of the 88 vs 89 Issue YAML File Count

An exhaustive inventory of all filesystem objects under `/issues/` was executed:

### File Breakdown:
1. `issues/automatic_issues/*.yaml`: Exactly **81 files**
2. `issues/manual_issues/*.yaml`: Exactly **7 files**:
   - `1_issues_manual_template.yaml` (Documentation template)
   - `H1.Z19_issues_manual.yaml`
   - `H2.T.Z33_issues_manual.yaml`
   - `H2.Z311_issues_manual.yaml`
   - `H3.ZE50_issues_manual.yaml`
   - `H3.ZE51_issues_manual.yaml`
   - `V.K21_issues_manual.yaml`
3. Non-YAML files under `issues/`: **0 files**.

### Exact Reconciliation:
- Total YAML filesystem objects: $81 + 7 = \mathbf{88}$.
- Actual issue-bearing YAML files: $81 + 6 = \mathbf{87}$.
- Template files: $\mathbf{1}$ (`1_issues_manual_template.yaml`).
- **Explanation of the "89" Figure**: The reported total of 89 was an arithmetic double-counting error from calculating $(81 \text{ automatic} + 7 \text{ manual} + 1 \text{ template} = 89)$, overlooking that the template was already one of the 7 files inside `manual_issues/`.
- No issue YAML files were silently omitted.

---

## 11. CHECK 9 — Out-of-Population Issues Audit

Four YAML issue files in `/issues/` belong to meters outside the approved 79-meter Core Research Population:
1. `automatic_issues/H3.Z42_issues_automatic.yaml`: 3,525 issue records for meter `H3.Z42` (meter was excluded during P1-T1 due to a 0-byte raw data file).
2. `automatic_issues/WeatherStation.Weather_issues_automatic.yaml`: 28 issue records for meteorological sensor (excluded from electrical population).
3. `manual_issues/H3.ZE50_issues_manual.yaml`: 1 issue record for non-existent meter.
4. `manual_issues/H3.ZE51_issues_manual.yaml`: 1 issue record for non-existent meter.

### Contamination Audit:
- 100% of the 79 core meters were verified.
- None of these out-of-population issue records were applied to any of the 79 core meters.
- Core meters `H4.ZE50` and `H4.ZE51` were processed strictly with their own corresponding automatic files (`H4.ZE50_issues_automatic.yaml` and `H4.ZE51_issues_automatic.yaml`). Zero cross-meter leakage occurred.

---

## 12. Adjudication Analysis & Proposed Protocol Amendment

### Comparison of Options:

1. **Option A (Retain positive-duration overlap)**:
   - *Pros*: Matches current code in `etl/quality_flags.py` and current artifact SHA-256 (`4866a6c5...`).
   - *Cons*: Admits 923 raw observations recorded at the exact *"first erroneous timestamp"* into Clean Ground Truth ($Q_1$). Fails Invariant 0.6.
2. **Option B (Adopt non-empty set intersection)**:
   - *Pros*: Mathematically rigorous; protects Clean Ground Truth by excluding 923 verified erroneous sensor readings; conservative boundary protection.
   - *Cons*: Requires updating `etl/quality_flags.py` to search for `ts` instead of `ts + 1` in `match_grid_issues()`, regenerating the P1-T4 artifact, and conducting an independent re-audit.
3. **Option C / Verdict `AMENDMENT_REQUIRED`**:
   - Because Protocol v1.1 is silent, neither the executor nor the adjudicator has constitutional authority to unilaterally alter or finalize the semantic rule.
   - A formal Protocol Amendment must be officialized by the Protocol Owner.

### Proposed Protocol Amendment Text (For Protocol Owner Consideration):
> **Proposed Amendment to Protocol v1.1 — Section 0.1e / P1-T4**:  
> *"In determining whether a standardized 15-minute grid bin $\text{Bin}(t) = (t - 15\text{min}, t]$ intersects an authoritative issue interval $I = [s, e]$, the intersection condition shall be defined as any non-empty set intersection:*  
> $$\text{has\_issue}(t) \iff \text{Bin}(t) \cap I \neq \emptyset \iff (s \le t) \land (e > t - 15\text{min})$$  
> *Rationale: Physical observations occurring at $s = t$ are recorded during active failure episodes ('first erroneous timestamp'). Boundary-point inclusion conservatively prevents contaminated observations from entering the authoritative Clean Ground Truth ($Q_1$)."*

---

## 13. Governance Status & Handoff

In strict accordance with `AGENTS.md` and the governance instructions for this review:
1. The adjudicator has **NOT modified** any production code, tests, or artifacts.
2. The adjudicator has **NOT modified** `control/task_state.yaml`.
3. `control/task_state.yaml` currently maintains:
   - `current_task: P1-T3`
   - `P1-T4: BLOCKED`
   - `P1-T5: BLOCKED`
4. Current P1-T4 Artifact SHA-256 remains:
   `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`

---

P1-T4 gating remains a human/orchestrator governance action.  
P1-T5 remains BLOCKED.
