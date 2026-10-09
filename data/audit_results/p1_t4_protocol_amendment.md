# PROTOCOL v1.1 TARGETED AMENDMENT — PROPOSAL

## Issue-Interval Overlap Semantics for Task P1-T4: Quality & Provenance Flags

- **Project**: Beyond Synthetic Missingness — Smart-Meter Imputation
- **Target Task**: Task P1-T4 — Build Quality & Provenance Flags
- **Protocol**: Protocol v1.1 (Official) — Targeted Amendment
- **Amendment Title**: Protocol v1.1 Amendment — P1-T4 Issue Overlap Semantics
- **Author**: Protocol Governance Reviewer
- **Date**: 2026-10-08
- **Status**: **`PROPOSED / READY FOR HUMAN RATIFICATION`**
- **Affected Artifact**: `data/interim/readings_15min_flagged.parquet`
- **Target Artifact Current SHA-256**: `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`
- **Governing Charter**: `AGENTS.md` (Sections 1–9)

---

## 1. Reason for Amendment

During the independent adjudication of Task P1-T4 (`Quality & Provenance Flags`), a formal semantic ambiguity was discovered regarding how a standardized 15-minute grid bin is determined to be issue-affected:

1. **Protocol Silence**: Protocol v1.1 (`TASK_PLAN.md`, `RESEARCH_PLAN.md`, `reports/protocol_v1_1_amendment.md`) defines the regular 15-minute grid intervals as half-open, right-closed windows $\text{Bin}(t) = (t - 15\text{min}, t]$ with the deterministic `LAST` representative observation operator. However, the protocol text is silent on the mathematical definition of issue-interval overlap for assigning `has_issue`. Specifically, it does not specify whether overlap requires positive Lebesgue measure ($\mu(\text{Bin}(t) \cap I) > 0$, **Strict Interpretation A**) or any non-empty set intersection ($\text{Bin}(t) \cap I \neq \emptyset$, **Strict Interpretation B**).
2. **Current Production Implementation Discrepancy**: The production implementation in `etl/quality_flags.py` utilized a hybrid rule ($A_{\text{code}}$): positive Lebesgue measure for non-instantaneous intervals ($s < e$), combined with an ad-hoc point-containment rule for instantaneous events ($s == e$).
3. **Contamination of Ground Truth Under Interpretation A**: Under Interpretation A, exactly 1,143 grid bins spanning 57 core meters are treated as clean. Among these, **923 occupied bins** contain physical raw sensor observations recorded at the exact integer second $t$ ($\text{source\_timestamp\_utc} == t$). Because authoritative source logs define $s = t$ as the *"first erroneous timestamp"*, retaining these 923 bins admits known corrupted measurements into the authoritative Clean Ground Truth ($Q_1$), violating Protocol v1.1 Invariant 0.6 (*"Ground truth chỉ lấy từ clean segment: không thiếu, không có issue, không bị corrected"*).
4. **Governance Mandate**: Under `AGENTS.md` Rules 1 and 8, neither executors nor auditors may silently alter or choose protocol rules. Resolving this ambiguity and unblocking P1-T4/P1-T5 requires a formal targeted protocol amendment ratified by the Protocol Owner / Orchestrator.

---

## 2. Source Evidence

Authoritative evidence from the raw dataset repository and issue metadata defines the temporal semantics of issue intervals:

### 2.1 Issue Source Template (`issues/manual_issues/1_issues_manual_template.yaml`)
```yaml
10:   time_end: 1532098560  # end-time of the issue (last erroneous timestamp) as unix time stamp
11:   time_start: 1532000040  # start-time of the issue (first erroneous timestamp) as unix time stamp
```

And in the automatic issue logs (`issues/automatic_issues/*_issues_automatic.yaml`):
```yaml
H1.Z10.W@zero@1550433720:
  reason: zero
  time_start: 1550433720
  time_end: 1550433720
```

### 2.2 Semantic Implications of Source Evidence:
1. `time_start` ($s$) is explicitly defined by the source data provider as the **first erroneous timestamp**.
2. `time_end` ($e$) is explicitly defined by the source data provider as the **last erroneous timestamp**.
3. Therefore, issue timestamps are closed and timestamp-inclusive:
   $$\text{Issue Interval } I = [s, e]$$
4. Sensor readings recorded at physical timestamp $s$ or $e$ are contaminated measurements recorded during active system/meter failure.
5. Standardized 15-minute grid intervals are defined as half-open, right-closed:
   $$\text{Bin}(t) = (t - 15\text{min}, t] = (t - 900\text{s}, t]$$
6. Because $\text{Bin}(t)$ includes its right boundary point $t$, any issue interval starting at $s = t$ touches $\text{Bin}(t)$ at its representative endpoint.

---

## 3. Formal Mathematical Rule

The formal text of the Targeted Amendment is specified as follows:

```text
================================================================================
Targeted Amendment to Protocol v1.1: P1-T4 Issue Overlap Semantics
================================================================================

Given:
    Standardized Grid Bin:  Bin(t) = (t - 15 minutes, t] = (t - 900s, t]
    Authoritative Issue:    I = [s, e]

A grid bin Bin(t) is issue-affected (has_issue(t) = TRUE) if and only if
the set of timestamps represented by the bin has a non-empty intersection
with the issue interval:

    has_issue(t) = TRUE  <===>  Bin(t) ∩ I != ∅

For finite issue intervals [s, e], this set-theoretic condition is algebraically
equivalent to:

    s <= t  AND  e > t - 900s  (equivalently: e > t - 15min)

Formal Consequences:
1. Boundary-start inclusion: An issue starting exactly at grid label s = t
   is included (s <= t is satisfied; e >= s = t > t - 900 is satisfied).
2. Left-boundary exclusion: An issue ending exactly at e = t - 15min is excluded
   because the grid bin is open on the left ((t - 900, t] ∩ [s, t - 900] = ∅).
3. Zero-duration consistency: An instantaneous point event [s, s] is included
   whenever t - 15min < s <= t, naturally unified without special branching.
4. Set union evaluation: Multiple overlapping or consecutive issue intervals
   are evaluated via standard set union (⋃); boolean evaluation is idempotent.
5. Multi-channel duplicate invariance: Duplicate records from multi-channel
   recorders do not alter the boolean outcome.
================================================================================
```

### Note on Production State:
The current production artifact (`readings_15min_flagged.parquet`) was generated using $A_{\text{code}}$. Adopting this amendment requires a targeted repair of `has_issue` and dependent `is_valid_ground_truth` flags before Task P1-T4 can transition to `GATED`.

---

## 4. Scientific Rationale for Interpretation B

The adoption of **Interpretation B** ($\text{Bin}(t) \cap I \neq \emptyset$) is governed by the following core principles:

> **Principle**: A grid bin is issue-affected whenever the set of timestamps represented by the bin has any non-empty intersection with an authoritative issue interval.

This is a **protocol-specific scientific design decision supported by the source timestamp semantics and Ground Truth cleanliness invariant**, not a generic "standard":

1. **Source Semantic Fidelity**: The source documentation explicitly defines `time_start` as the *"first erroneous timestamp"* and `time_end` as the *"last erroneous timestamp"*. The endpoint timestamps are themselves corrupted physical points.
2. **Right-Closed Boundary Alignment**: The standardized grid bin $\text{Bin}(t) = (t - 900, t]$ contains its right endpoint $t$. The representative observation chosen by the deterministic `LAST` operator often lands exactly at second $t$.
3. **Contamination Prevention at Boundary**: If an issue starts at $s = t$, a sensor reading recorded at $t$ is an active failure reading. Labeling `has_issue = False` would directly admit this erroneous measurement into the authoritative Ground Truth ($Q_1$), violating Invariant 0.6.
4. **Unified Mathematical Treatment of Point Events**: Zero-duration issue records $[s, s]$ (singleton sets $\{s\}$) are naturally handled by non-empty intersection ($s \in (t - 900, t]$) without requiring ad-hoc conditional code branching.
5. **Elimination of Arbitrary Code Heuristics**: Adopting Interpretation B completely eliminates the artificial hybrid logic of $A_{\text{code}}$, unifying all intervals (whether $s < e$ or $s == e$) under a single rigorous set-theoretic formula.
6. **Open-Left Semantics Conservation**: Because $\text{Bin}(t)$ is strictly open on the left boundary ($t - 900$), an issue terminating at $e = t - 900$ does not touch the bin, avoiding false contamination from past resolved outages.
7. **Conservative Ground-Truth Invariant**: In scientific machine learning benchmarking, ground-truth cleanliness is strictly conservative. The asymmetry of error strongly favors excluding a borderline boundary reading over admitting a known failure observation into ground truth.

---

## 5. Comparative Evaluation: Strict A vs $A_{\text{code}}$ vs Amended B

Three distinct candidate formulations were rigorously analyzed across the entire 13,981,597 grid rows:

1. **Strict Interpretation A (Positive Lebesgue Measure)**:
   $$\text{has\_issue}_A(t) \iff \mu(\text{Bin}(t) \cap I) > 0 \iff (s < t) \land (e > t - 900)$$
   *(Evaluates to FALSE for all singleton point events $s == e$)*
2. **$A_{\text{code}}$ (Current Production Implementation in Artifact)**:
   $$\text{has\_issue}_{A\text{code}}(t) \iff \begin{cases} (s < t) \land (e > t - 900) & \text{if } s < e \\ t - 900 < s \le t & \text{if } s == e \end{cases}$$
3. **Amended Interpretation B (Non-Empty Set Intersection)**:
   $$\text{has\_issue}_B(t) \iff \text{Bin}(t) \cap I \neq \emptyset \iff (s \le t) \land (e > t - 900)$$
   *(Unified for all intervals $s \le e$)*

### Comparative Yield Summary:

| Rule Formulation | `has_issue` Total | Difference vs Strict B | Difference vs Current Artifact ($A_{\text{code}}$) |
|---|:---:|:---:|:---:|
| **Strict Interpretation A** | 815,612 | -1,187 | -44 |
| **Current Implementation ($A_{\text{code}}$)** | 815,656 | -1,143 | **0 (Baseline)** |
| **Amended Interpretation B** | **816,799** | **0** | **+1,143** |

---

## 6. Exact 1,143-Bin Current-Artifact Delta Decomposition

The current production artifact differs from Amended Interpretation B by **exactly 1,143 bins**.

### Forensic Decomposition:
- **Total Flag Differences ($A_{\text{code}} \to B$)**: Exactly **+1,143** (`False` $\to$ `True`).
- **Reverse Differences ($B \to A_{\text{code}}$)**: Exactly **0** (`True` $\to$ `False`).
- **Meters Affected**: Exactly **57 core meters**.
- **Boundary Condition**: 100.000% of the 1,143 differing bins satisfy:
  $$s == t \quad (\text{issue\_start} == \text{grid\_timestamp\_utc}) \quad \land \quad s < e$$
- **Interior Differences**: Exactly **0**.
- **Left Boundary Differences ($e == t - 900$)**: Exactly **0**.

### Sensor Observation Breakdown of the 1,143 Differing Bins:
- **Empty Bins (`is_missing == True`, `raw_record_count == 0`, `value == NaN`)**: **47 bins**
  - Reclassified from $Q_3$ (Unrelated Gap) to $Q_4$ (Corroborated Gap).
  - Neither rule admits empty bins into ground truth.
- **Occupied Bins (`is_missing == False`)**: **1,096 bins**
  - **Subcase 1: Observation at exact second $t$ ($\text{source\_timestamp\_utc} == t$)**: **923 bins (84.22%)**
    - The raw sensor observation selected by the `LAST` operator was recorded at the exact integer second $t$.
    - Because the source logs define $s = t$ as the *"first erroneous timestamp"*, **these 923 readings were recorded during active failure**.
    - $A_{\text{code}}$ incorrectly admits them into Clean Ground Truth ($Q_1$).
    - Interpretation B safely excludes them into $Q_2$.
  - **Subcase 2: Observation strictly before second $t$ ($\text{source\_timestamp\_utc} < t$)**: **173 bins (15.78%)**
    - The sensor reading occurred between $t - 900\text{s}$ and $t - 1\text{s}$.
    - Interpretation B conservatively excludes these boundary-window bins from Clean Ground Truth.

---

## 7. Zero-Duration Point Events Clarification

An exhaustive audit of all 148,968 issue records across all 88 issue YAML files was conducted:

1. **Inventory**: Exactly **6,755 zero-duration records** ($s == e$) exist across the dataset.
   - 818 records belong to non-core meter `H3.Z42` (excluded in P1-T1 due to 0-byte file).
   - 5,937 records belong to the 79 Core Meters (5,934 `zero` instantaneous drops and 3 `single_leap` anomalies).
2. **Multi-Channel Deduplication**: Multi-channel recorders logged point events simultaneously on sub-channels (active power, reactive power, export). Deduplication yields **1,683 unique $(meter, timestamp, reason)$ point events**.
3. **Co-Occurrence**:
   - In **1,639 bins** (97.39%), a positive-duration issue interval ($s < e$) already covers the bin.
   - In **44 bins** (2.61%), only isolated zero-duration point events exist.
4. **Behavior Across Rules**:
   - Under Strict A: Measure is zero ($\mu = 0$); all 44 bins evaluate to `has_issue = False`.
   - Under Strict B: Singleton $\{s\}$ intersects $(t-900, t]$; all 44 bins evaluate to `has_issue = True`.
   - Under $A_{\text{code}}$: The executor implemented a special branch for $s == e$; all 44 bins evaluate to `has_issue = True`.
5. **Repair Consequence**: Because $A_{\text{code}}$ already captured these 44 isolated interior bins, **zero-duration point events require zero additional repair to the current artifact**. The required repair is strictly limited to the **1,143 boundary-start bins**.

---

## 8. Left-Boundary Clarification ($e == t - 15\text{min}$)

Because the standardized 15-minute grid bin is defined as half-open on the left:
$$\text{Bin}(t) = (t - 900, t]$$
any issue interval ending exactly at the open left boundary $e = t - 900$ has an empty intersection with $\text{Bin}(t)$:
$$(t - 900, t] \cap [s, t - 900] = \emptyset$$

### Empirical Audit:
- Across all 13.98M grid rows, exactly **10 issue intervals** terminate at $e = t - 900$.
- In all 10 instances, both Interpretation A and Interpretation B evaluate the left-boundary interval as non-intersecting.
- In all 10 instances, the bin's boolean flag is governed entirely by subsequent intervals; **0 bins differ due to $e == t - 900$**.
- Left-boundary open semantics are strictly preserved under Amended Interpretation B.

---

## 9. Expected Four-Quadrant Distribution Under Amended Interpretation B

The complete downstream four-quadrant distribution across all 13,981,597 grid rows is recomputed as follows:

| Quadrant | Description | Strict Interpretation A | Current Artifact ($A_{\text{code}}$) | Amended Interpretation B | Delta ($B - A_{\text{code}}$) |
|---|---|:---:|:---:|:---:|:---:|
| **$Q_1$** | Clean Observed (`!missing & !issue`) | 12,638,182 | 12,638,138 | **12,637,042** | **-1,096** |
| **$Q_2$** | Issue Observed (`!missing & issue`) | 695,395 | 695,439 | **696,535** | **+1,096** |
| **$Q_3$** | Unrelated Gap (`missing & !issue`) | 527,803 | 527,803 | **527,756** | **-47** |
| **$Q_4$** | Corroborated Gap (`missing & issue`) | 120,217 | 120,217 | **120,264** | **+47** |
| **Total** | All Grid Rows | 13,981,597 | 13,981,597 | **13,981,597** | **0** |

### Fundamental Invariant Balances:
1. **Total Grid Rows Conserved**: $\sum Q_i = 13,981,597$
2. **Occupied Bins Conserved**: $Q_1 + Q_2 = 13,333,577$ (Observed readings invariant)
3. **Empty Bins Conserved**: $Q_3 + Q_4 = 648,020$ (Grid gap invariant)
4. **Issue Flag Balance**: $\Delta Q_2 + \Delta Q_4 = +1,096 + 47 = \mathbf{+1,143} = \Delta \text{has\_issue}$

---

## 10. Expected Ground-Truth Yield

Under Protocol v1.1 Invariant 0.6, Ground Truth eligibility is strictly defined as:
$$\text{is\_valid\_ground\_truth} \iff (\neg \text{is\_missing}) \land (\neg \text{has\_issue}) \land (\neg \text{is\_corrected}) \equiv Q_1$$

- **Current Production Artifact ($A_{\text{code}}$)**:
  $$\text{is\_valid\_ground\_truth} = 12,638,138 \text{ bins}$$
- **Amended Interpretation B**:
  $$\mathbf{\text{is\_valid\_ground\_truth} = 12,637,042 \text{ bins}}$$
- **Net Ground-Truth Delta**: Exactly **-1,096 bins** (-0.0087%).
- **Scientific Impact**: Excludes 923 known contaminated sensor readings and 173 boundary-contact observations from downstream model training and benchmarking, ensuring pristine ground-truth integrity.

---

## 11. Affected Protocol Documents Requiring Synchronization

Upon official ratification of this amendment proposal, the following protocol-controlled documents must be synchronized:

1. **`TASK_PLAN.md`**:
   - Update Section P1 Task P1-T4 specification to include the algebraic formula:
     $$\text{has\_issue}(t) \iff \text{Bin}(t) \cap I \neq \emptyset \iff (s \le t) \land (e > t - 15\text{min})$$
   - Update acceptance criterion counts for P1-T4:
     - `has_issue`: 816,799
     - `is_valid_ground_truth`: 12,637,042
     - $Q_1$: 12,637,042, $Q_2$: 696,535, $Q_3$: 527,756, $Q_4$: 120,264
2. **`RESEARCH_PLAN.md`**:
   - Synchronize Section 6 (Quality Flags Marking) and Section 10 (Clean Ground Truth Invariants) with the non-empty intersection rule and updated quadrant numbers.
3. **`configs/default.yaml`**:
   - Update any configuration comments or issue overlap parameter definitions if exposed.
4. **Protocol Amendment Manifest / Control Records**:
   - Append targeted amendment entry to `reports/protocol_v1_1_amendment.md`.
   - Update `control/protocol_hashes.txt` once files are officially committed by the Protocol Owner.

### Explicit Non-Scope & Invariant Retention:
This amendment does **NOT** modify and leaves completely intact:
- Core Research Population (79 meters strictly preserved);
- Cadence classes and cadence stationary flags;
- P1-T3 regular grid representation and `LAST` aggregation semantics;
- Baseline model architectures;
- Benchmark evaluation branches;
- Feature-governance and leakage-prevention rules;
- Raw dataset immutability policy (`data/raw/` read-only).

---

## 12. Production Artifact Affected & Cryptographic Checksum

This amendment directly impacts the quality flag definitions of the Stage P1-T4 production output:

- **Target File**: `data/interim/readings_15min_flagged.parquet`
- **Current Production Checksum (SHA-256)**:
  `4866a6c512837e34cbaf1125cd8e7e30888fc6d518d25d18764056e750580705`
- **Expected Change**: Exactly 1,143 `has_issue` boolean values updated from `False` to `True`; exactly 1,096 `is_valid_ground_truth` values updated from `True` to `False`. All sensor measurement values, timestamps, and missingness flags remain 100% bit-identical.
- **Current State in Repository**: The current production file remains **UNTOUCHED**. No silent repair has been performed.

---

## 13. Governance Status

- **Status**: **`PROPOSED / READY FOR HUMAN RATIFICATION`**
- **Current Task State**:
  - P1-T1: `GATED`
  - P1-T2: `GATED`
  - P1-T3: `GATED`
  - P1-T4: `PASS WITH NOTES / AMENDMENT_REQUIRED` (in adjudication; `BLOCKED` in machine state)
  - P1-T5: `BLOCKED`
- **Governance Discipline**:
  - `control/task_state.yaml` has **NOT** been modified.
  - Production code in `etl/` has **NOT** been modified.
  - Test assertions in `tests/` have **NOT** been modified.
  - Protocol files have **NOT** been modified in the working tree.

---

## 14. Ratification Requirement & Next Steps

This document is a formal **Proposal for Targeted Amendment**. Before any implementation repair or state machine advancement can take place:

1. **Human / Orchestrator Ratification**: The Human Orchestrator must formally ratify this proposal to adopt **Strict Interpretation B** ($\text{Bin}(t) \cap I \neq \emptyset$).
2. **Authorized Protocol Synchronization**: If ratified, official updates to `TASK_PLAN.md` and `RESEARCH_PLAN.md` must be authorized and hashed.
3. **Targeted Implementation Repair**: A dedicated repair task must update `etl/quality_flags.py` to evaluate $s \le t \land e > t - 900$, regenerate `data/interim/readings_15min_flagged.parquet`, update tests in `tests/test_P1_T4.py`, and obtain independent audit sign-off.
4. **Gating Task P1-T4**: Once audited with 816,799 `has_issue` flags and 12,637,042 ground-truth rows, P1-T4 will transition to `GATED`, thereby unblocking P1-T5.

---

Protocol amendment prepared.  
P1-T4 production artifact NOT modified.  
P1-T4 task state NOT modified.  
P1-T5 remains BLOCKED.  
Human/orchestrator ratification required before repair.
