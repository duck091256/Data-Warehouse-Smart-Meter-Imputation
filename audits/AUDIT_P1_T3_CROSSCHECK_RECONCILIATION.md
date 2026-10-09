# AUDIT DELIVERABLE: P1-T3 Cross-Check Evidence Audit and Final Report Reconciliation

> **Protocol Version**: Beyond Synthetic Missingness — Smart-Meter Imputation Protocol v1.1  
> **Audited Task**: P1-T3 Extended Independent Cross-Check against Dataset-Provided 15-Minute Reference  
> **Target Report Audited**: `reports/p1_t3_crosscheck_reduced.md`  
> **Associated Artifacts**: `analysis/crosscheck_reduced_15min.py`, `reports/p1_t3_crosscheck_sampling.json`, `reports/p1_t3_crosscheck_reduced.csv`  
> **Date**: 2026-10-09  
> **Governance Adherence**: Read-only evidence audit. Zero cross-check runs executed; zero pipeline, interim, or raw data modified.  

---

## 1. Executive Verdict

1. **Artifact Cryptographic Baseline**: All 4 expected SHA-256 hashes match the repository files bit-for-bit:
   - `analysis/crosscheck_reduced_15min.py`: `fef605106e53e94a66fd32207c545d33bd98e3c50c7657874c3a2fba25fa4452` (**MATCH**)
   - `reports/p1_t3_crosscheck_sampling.json`: `0693c1a2ed8b13e8d60c65b275f2df70916f01e16c584bbda6001d26e7cd7bae` (**MATCH**)
   - `reports/p1_t3_crosscheck_reduced.csv`: `42755e5f906c982d787f982187b6ff0e13f4ca0d09f3acc6bf1590308f87239f` (**MATCH**)
   - `reports/p1_t3_crosscheck_reduced.md`: `ec08c7dad36e40781ed56a5461ba7cc68a0ec6eba55e2d2b32b9e3005fe565bb` (**MATCH at audit start**)
2. **Variable & Physical Unit Verdict**: **`SAME_QUANTITY_CONFIRMED`** *(scoped to underlying measurement semantics)*.
   - Both raw column `<METER>.W` (ingested as `value` with `variable = "W"` in `readings_utc.parquet`) and reference column `<METER>.W` (in `<METER>.W_corrected_resampled_15min.csv.gz`) represent the **same physical quantity: Total Active Energy $W$** (cumulative register, unit: $\mathrm{kWh}$ for electricity meters; raw integer pulse counts for hydronic thermal meters; $\mathrm{Wh}$ for raw `V.Z84`).
   - They do **NOT** represent Active Power $P$ (which is measured in Watts, $\mathrm{W}$, and stored in separate `*.P_raw.csv.gz` files).
   - **Measurement-semantics vs numerical comparability**: While both series measure the same conceptual quantity, individual meters may differ in physical unit ($\mathrm{Wh}$ vs $\mathrm{kWh}$), numerical scale (×100 pulse multiplier), sign convention (CT polarity inversion), and processing history (author-side corrections). Direct numerical comparison without adjustment is valid only for meters where no such transformation has been applied. The cross-check evaluates both direct and provenance-adjusted comparisons separately.
   - Pervasive nomenclature error in prior report versions—where the unit symbol $\mathrm{W}$ (Watts) was mistakenly attached to energy error metrics (e.g. $\text{MAE} \le 2.4 \times 10^{-11}\ \mathrm{W}$)—has been identified and corrected to $\mathrm{kWh}$, $\mathrm{Wh}$, or pulses.
3. **Metric Definitions & Quantifications**: All 8 reported quantitative claims are **`VERIFIED_FROM_EXISTING_ARTIFACTS`** against `reports/p1_t3_crosscheck_reduced.csv`.
4. **Reconciliation of the 11 `DIFFERENT` Meters**:
   - 5 Scale $\times 100$ meters (`H1.K11`, `H1.K12`, `H1.K14`, `H2.K21`, `H1.W11`) and 1 CT inversion meter (`V.ZE84` polarity sign) are **`VERIFIED`**.
   - 5 meters (`V.K21`, `H1.ZE20`, `H1.Z15`, `H1.Z28`, `V.Z84`) are **`SUPPORTED`** as documented author modifications (submeter gap substitution, C30S sub-minute linear interpolation, outage duplicate resolution).
   - The reported metric `n_unexplained = 0` is an operational categorization artifact of script logic (`is_unexplained = False`), not experimental closure for all 11 meters.
5. **Set Reconciliation**: Reconciled strictly via explicit set arithmetic:
   - Full union: $|\text{PROV}_{12} \cup \text{C30S}| = 12 + 25 - 5 = \mathbf{32\text{ meters}}$.
   - Non-identical union: $|\text{PROV}_{12} \cup \text{C30S}_{\text{non-ident}}| = 12 + 24 - 5 = \mathbf{31\text{ meters}}$ (since `H1.Z17` has 99.967% match rate, classified as `IDENTICAL`).
   - Total non-identical meters: $31 + 4\text{ residuals} = \mathbf{35\text{ meters}}$ (24 PARTIAL + 11 DIFFERENT).
   - Discrepancy total ($< 100.0000\%$ tolerance match): $35 + 1\text{ (`H1.Z17`)} = \mathbf{36\text{ meters}}$ ($79 - 43 = 36$).

---

## 2. Inspected Artifacts & Cryptographic Verification

| Artifact | SHA-256 Hash | Repository Path | Line / Row Reference | Status |
| :--- | :--- | :--- | :--- | :---: |
| Cross-Check Script | `fef605106e53e94a66fd32207c545d33bd98e3c50c7657874c3a2fba25fa4452` | `analysis/crosscheck_reduced_15min.py` | Lines 1–1179 | Verified Bit-for-Bit |
| Sampling Order JSON | `0693c1a2ed8b13e8d60c65b275f2df70916f01e16c584bbda6001d26e7cd7bae` | `reports/p1_t3_crosscheck_sampling.json`| Keys: `ordered_meters` (79 items) | Verified Bit-for-Bit |
| Results Dataset CSV | `42755e5f906c982d787f982187b6ff0e13f4ca0d09f3acc6bf1590308f87239f` | `reports/p1_t3_crosscheck_reduced.csv` | 395 rows (79 meters × 5 variants) | Verified Bit-for-Bit |
| Cross-Check Report (Initial) | `ec08c7dad36e40781ed56a5461ba7cc68a0ec6eba55e2d2b32b9e3005fe565bb` | `reports/p1_t3_crosscheck_reduced.md` | Lines 1–312 | Verified Bit-for-Bit |
| ETL Resample Script | `26b3bfdf815bc062b1bdfaa73c734992925b42d70e70a316c05a109a4d257a6e` | `etl/resample_15min.py` | Lines 50–75, 331–348 | Reference Read-Only |
| ETL Normalize UTC Script | `a3f5f3e9b06c547842ba5e1d51a66ff52243d944e8bcfeeb03bb379b392237eb` | `etl/normalize_utc.py` | Lines 218–253, 298 | Reference Read-Only |

---

## 3. Investigation A — Verification of Variable and Physical Unit

### 3.1. Code Lineage Tracing
1. **Raw Column Traced**:
   - In `etl/normalize_utc.py` (lines 218–220, 241–253): Reads `<raw_dir>/data/<METER>/<METER>.<var>_raw.csv.gz` where `target_variable = "W"`. Column 0 is `datetime_utc`, Column 1 is named `<METER>.W`. Ingested into `readings_utc.parquet` under column `value` with metadata column `variable = "W"`.
   - In `etl/resample_15min.py` (lines 331–348): Streams `readings_utc.parquet` filtered by `variable == "W"`, downsampling `value` into `readings_15min.parquet` column `value`.
   - In `analysis/crosscheck_reduced_15min.py` (lines 357–363, 389–399): Loads `readings_15min.parquet` column `value` as `s_ours`, and `readings_utc.parquet` column `value` (filtered by `variable == "W"`) as `s_raw`.
   - **Finding**: The exact raw column read is Column 1 (`<METER>.W`) of the raw files, held as `value` in interim parquet tables.
2. **Reference Column Traced**:
   - In `analysis/crosscheck_reduced_15min.py` (lines 367–376): Locates `<raw_dir>/data/<METER>/<METER>.W_corrected_resampled_15min.csv.gz`. Selects `val_col = f"{meter_id}.W"`. Loads `usecols=["datetime_utc", val_col]` as `s_ref`.
   - **Finding**: The exact reference column read is `<METER>.W`.

### 3.2. Dataset Grounding in Official Literature (Engel et al., 2025)
Documented in *Scientific Data* 12, 864 (2025) / arXiv:2503.11469 (*A comprehensive multi-energy dataset of a commercial facility*):
- **Table 3** (*Measurements collected from all thermal meters*):
  - `P`: Heating/cooling power, Unit: $\mathrm{W}$ (Watts).
  - `W`: Total energy, Unit: $\mathrm{kWh}$ (Kilowatt-hours).
- **Table 4** (*Measurements collected from electricity meters*):
  - `P`: Total electric power, Unit: $\mathrm{W}$ (Watts).
  - `W`: Total active energy, Unit: $\mathrm{kWh}$ (Kilowatt-hours).
  - `WQ`: Total reactive energy, Unit: $\mathrm{kvarh}$.
- **Figure 9 caption**:
  - Defines the relation $\epsilon(t) = P(t) - \frac{\Delta W}{\Delta t}(t)$, explicitly establishing that $P$ is instantaneous active power ($\mathrm{W}$) and $W$ is cumulative active energy ($\mathrm{kWh}$).

### 3.3. Nomenclature & German Facility Naming Conventions
1. **Physical Meaning of $W$**: In `*.W_raw.csv.gz` and column `<METER>.W`, $W$ denotes **Total Active Energy** (physics work/energy $W$, German *Arbeit*). It is **NOT** the SI unit Watt ($\mathrm{W}$).
2. **Dual Meaning of $W$ in Filenames**: In German facility engineering at Honda Research Institute Europe:
   - `Z`: *Zähler* (electrical submeters)
   - `ZE`: *Zähler Einspeisung* (generation / solar PV)
   - `T.Z`: *Trafo-Zähler* (substation transformer electricity meters)
   - `K`: *Kälte* (hydronic cooling thermal meters)
   - `W`: *Wärme* (hydronic heating thermal meters, e.g. `H1.W11`, `H1.W12`)
   *(In `H1.W11.W_raw.csv.gz`, the first `W` is the meter prefix Wärme; the second `W` is the measurement variable Energy).*
3. **Physical Units**:
   - Electricity meters (`Z`, `ZE`, `T.Z`): Total active energy in **$\mathrm{kWh}$**.
   - Thermal meters (`K`, `W`): Total thermal energy in **$\mathrm{kWh}$** (in calibrated reference files; raw registers are integer pulse counts / deca-pulses, explaining the $\times 100$ scale factor in `H1.K11`..`K14`, `H2.K21`, `H1.W11`).
   - Transformer meter `V.Z84`: Raw series is in **$\mathrm{Wh}$** (Watt-hours); reference series is in **$\mathrm{kWh}$** (scaled by $1000\times$ and sign-inverted).
4. **Transformations Applied**: In direct raw comparisons (`OURS_P1_T3`, `LAST_right`, `MEAN_right`, `LAST_left`, `MEAN_left`), **zero unit conversions, zero sign flips, and zero scalings are applied**. Exploratory adjustments are restricted to diagnostic provenance evaluation.
5. **Physical Compatibility**: Both series represent cumulative energy $W$ (same measurand). Direct numerical comparison is valid for meters where the raw and reference series share the same unit, scale, and sign. For meters with documented transformations (unit scaling, sign inversion, author corrections), the cross-check evaluates direct and provenance-adjusted classifications separately.

### Verdict:
**`SAME_QUANTITY_CONFIRMED`** *(scoped to underlying measurement semantics)*

---

## 4. Investigation B — Exact Matching and Tolerance Rules

### 4.1. Implementation Rules in `crosscheck_reduced_15min.py`
Tracing lines 380–471, 494–548:
1. **Timestamp Alignment**: $\mathcal{T}_{\text{cand}} \cap \mathcal{T}_{\text{ref}}$ on UTC quarter-hour marks. $\text{ts\_coverage} = \frac{|\mathcal{T}_{\text{cand}} \cap \mathcal{T}_{\text{ref}}|}{\max(|\mathcal{T}_{\text{cand}}|, |\mathcal{T}_{\text{ref}}|)}$. This evaluates interior-grid alignment; subtle start/end boundary truncation differences (1–6 bins differing at the 6-year boundaries due to `ceil_to_15min` in P1-T3 vs flooring in reference files) are excluded from the intersecting grid and do not represent interior timestamp offset defects.
2. **Common Valid Subset**: $N_{\text{both\_valid}} = \sum (~np.isnan(c_{\text{cand}})) \land (~np.isnan(c_{\text{ref}}))$.
3. **Exact Floating-Point Numeric Equality**: $\sum (c_{\text{cand}} == c_{\text{ref}}) / N_{\text{both\_valid}}$ using the IEEE-754 `==` operator on 64-bit float arrays (note: this treats `+0.0 == -0.0` as equal and `NaN == NaN` as not equal; it is exact floating-point numeric equality, not bitwise comparison).
4. **Value Tolerances**:
   - Direct comparison (line 433): `np.isclose(c_cand, c_ref, atol=1e-5, rtol=1e-5)` $\iff |c_{\text{cand}} - c_{\text{ref}}| \le 10^{-5} + 10^{-5} \times |c_{\text{ref}}|$.
   - Provenance diagnostic (line 503): $|c_{\text{cand}} - c_{\text{ref}}| \le 10^{-5}$ (pure absolute tolerance).
5. **Error Metrics**:
   - $\text{MAE} = \frac{1}{N_{\text{both\_valid}}} \sum |c_{\text{cand}} - c_{\text{ref}}|$
   - $\text{MaxAE} = \max |c_{\text{cand}} - c_{\text{ref}}|$
   - $\text{match\_rate} = N_{\text{close}} / N_{\text{both\_valid}}$
6. **Denominator Conditionality**: The denominator for match rate is strictly $N_{\text{both\_valid}}$. In thermal meters where reference files forward-filled tens of thousands of empty raw bins, $N_{\text{both\_valid}}$ represents only the occupied raw intervals.
7. **Tie-Breaking Rule**: Candidate aggregation variants are sorted by $(\text{match\_rate}\ \downarrow, -\text{MAE}\ \downarrow)$. When all variants yield $0.00\%$ match rate, the variant with minimal MAE is nominally designated the winner.

### 4.2. Verification of Reported Quantitative Results

| Claimed Result in Task Description | Artifact Evidence in `reports/p1_t3_crosscheck_reduced.csv` | Status |
|:--- |:--- |:---:|
| Direct classification: `IDENTICAL = 44`, `PARTIAL = 24`, `DIFFERENT = 11` | `ours['classification'].value_counts()` (via `cls_direct`): IDENTICAL: 44, PARTIAL: 24, DIFFERENT: 11 | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| Provenance-adjusted classification: `IDENTICAL = 44`, `PARTIAL = 34`, `DIFFERENT = 1` | `cls_prov` counts across S79: IDENTICAL: 44, PARTIAL: 34, DIFFERENT: 1 (10 of 11 DIFFERENT reclassified as PARTIAL under adjustment) | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| Positive direct agreement: `68/79` | Exactly $44 + 24 = 68$ meters have `match_rate > 0.0` | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| `LAST_right` wins direct ranking for `74/79` | `ours['best_raw_variant'].value_counts()['LAST_right'] == 74` | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| `MEAN_right` wins nominal ranking for `5/79` (zero match rate) | Exactly 5 meters (`V.ZE84`, `H1.Z15`, `H1.ZE20`, `V.Z84`, `H1.Z28`), all with `match_rate == 0.0` | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| `LAST_right` wins for `68/68` positive agreement meters | For all 68 meters with `match_rate > 0`, `best_raw_variant == 'LAST_right'` | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| Provenance-adjusted result: `78/79` overall, `78/78` non-duplicate | `ours['eff_best_variant'].value_counts()['LAST_right'] == 78`; only `V.Z84` has `MEAN_right` | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| 43 ordinary C1M meters: exact floating-point 81.8%–100%, tolerance 100%, max MAE $2.4\times 10^{-11}$, max AE $9.3\times 10^{-10}$ | 43 C1M IDENTICAL rows: exact rate [0.8184, 1.0], tolerance rate 1.0, max MAE $2.40285\times 10^{-11}\ \mathrm{kWh}$, max AE $9.31323\times 10^{-10}\ \mathrm{kWh}$ | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |
| `H1.Z10`: ts_coverage 100%, tolerance 100%, MAE $\approx 3.55\times 10^{-12}$ | Row 0: `ts_coverage = 1.0`, `match_rate = 1.0`, `exact_rate = 0.87326`, `mae = 3.54752e-12\ \mathrm{kWh}`, `max_ae = 5.82077e-11\ \mathrm{kWh}$ | **`VERIFIED_FROM_EXISTING_ARTIFACTS`** |

---

## 5. Investigation C — Reconciliation of the 11 `DIFFERENT` Meters

Each meter classified as `DIFFERENT` in direct raw comparison was audited from existing artifacts:

| Meter ID | Direct Match (%) | Observed Discrepancy (Direct MAE) | Proposed Cause | Evidence Source | Verification Status | Further Action |
|:--- |:---:|:---:|:---|:---|:---:|:---|
| **`H1.K11`** | 0.00% | $2.532 \times 10^5\ \text{pulses}$ | Scale $\times 100$ in reference + forward-fill across 53,917 empty bins | CSV row 10; `ref / 100` restores **99.83%** match on occupied bins | **`VERIFIED`** | Correct unit from $\mathrm{W}$ to pulses. Note denominator conditionality ($N_{\text{both\_valid}} = 156,081$). |
| **`H1.K12`** | 0.00% | $5.924 \times 10^5\ \text{pulses}$ | Scale $\times 100$ in reference + forward-fill across 53,386 empty bins | CSV row 105; `ref / 100` restores **99.64%** match | **`VERIFIED`** | Correct unit from $\mathrm{W}$ to pulses. |
| **`H1.K14`** | 0.00% | $5.153 \times 10^5\ \text{pulses}$ | Scale $\times 100$ in reference + forward-fill across 52,679 empty bins | CSV row 160; `ref / 100` restores **99.69%** match | **`VERIFIED`** | Correct unit from $\mathrm{W}$ to pulses. |
| **`H2.K21`** | 0.00% | $3.042 \times 10^5\ \text{pulses}$ | Scale $\times 100$ in reference + forward-fill across 60,898 empty bins | CSV row 35; `ref / 100` restores **99.86%** match | **`VERIFIED`** | Correct unit from $\mathrm{W}$ to pulses. |
| **`H1.W11`** | 0.00% | $8.104 \times 10^6\ \text{pulses}$ | Scale $\times 100$ in reference (raw 9599 vs ref 959900) + forward-fill across 25,272 empty bins | CSV row 22; `ref / 100` restores **95.67%** match | **`VERIFIED`** | Correct unit from $\mathrm{W}$ to pulses. Note meter prefix $W$ is Wärme. |
| **`V.ZE84`** | 0.00% | $7.827 \times 10^4\ \mathrm{kWh}$ | CT clamp inverted in raw (ref negative vs raw positive) + C30S linear interpolation | 21 `_corrected_raw` files; CSV row 5 computes **35.09%** match under $\text{atol}=10^{-5}$ | **`VERIFIED`** (CT polarity) / **`SUPPORTED`** (C30S interpolation) | Reconcile report text from 96.29% to measured 35.09%. |
| **`H1.ZE20`** | 0.00% | $1.107 \times 10^6\ \mathrm{kWh}$ | Polarity inversion in reference + C30S linear interpolation | CSV row 30; `-ref` restores **25.39%** match | **`SUPPORTED`** | Document that continuous linear interpolation limits exact tolerance match. |
| **`H1.Z15`** | 0.00% | $2.165 \times 10^6\ \mathrm{kWh}$ | CT polarity inversion + C30S linear interpolation | CSV row 25; `-ref` aligns sign; `eff_match_rate` is **0.0087%** | **`SUPPORTED`** | Explain that large register magnitude ($>10^6\ \mathrm{kWh}$) and continuous interpolation prevent numerical tolerance match. |
| **`H1.Z28`** | 0.00% | $9.870 \times 10^5\ \mathrm{kWh}$ | CT polarity inversion + C30S linear interpolation | CSV row 215; `-ref` aligns sign; `eff_match_rate` is **0.0087%** | **`SUPPORTED`** | Explain that continuous interpolation prevents numerical tolerance match. |
| **`V.K21`** | 0.00% | $1.461 \times 10^6\ \mathrm{kWh}$ | Scale $\times 100$ + multi-month gap substitution (`substitute_V.K21`) using submeters | Engel et al. (2025) Section "Substitution for V.K21"; CSV row 40 shows `eff_match_rate` is only **1.07%** | **`SUPPORTED`** | Document that `ref / 100` does not restore match because synthetic submeter model is non-invertible. |
| **`V.Z84`** | 0.00% | $2.957 \times 10^8\ \mathrm{Wh}$ | 61,790 post-outage duplicates + $1000\times$ scaling ($\mathrm{Wh}$ vs $\mathrm{kWh}$) + sign inversion + uncalibrated baseline offset shifts | Engel et al. (2025) line 270; CSV row 90; `eff_match_rate` remains **0.00%** | **`SUPPORTED`** | Document as an unresolved methodological limitation of published reference file. |

*(Case `H2.Z311`*: 0.8x CT scaling factor documented in `H2.Z311_issues_manual.yaml`. Direct match rate is $0.034\% > 0.00\%$, so it is classified as `PARTIAL`, NOT `DIFFERENT`. It is the 12th member of $\text{PROV}_{12}$).

---

## 6. Investigation D — Reconciliation of Provenance Group Counts

### 6.1. Exact Set Definitions & Memberships
1. **$\text{PROV}_{12}$ (12 meters)**:
   - Scale $\times 100$ (6): `{'H1.K11', 'H1.K12', 'H1.K14', 'H1.W11', 'H2.K21', 'V.K21'}`
   - Polarity Inversion (4): `{'H1.Z15', 'H1.Z28', 'H1.ZE20', 'V.ZE84'}`
   - Special Cases (2): `{'H2.Z311', 'V.Z84'}`
2. **$\text{C30S}$ (25 meters)**:
   `{'H1.Z15', 'H1.Z17', 'H1.Z26', 'H1.Z28', 'H1.Z29', 'H1.Z310', 'H1.ZE20', 'H2.Z311', 'H2.Z351', 'H2.Z361', 'H2.ZE64', 'H2.ZE65', 'H2.ZE66', 'H2.ZE67', 'H2.ZE74', 'H3.Z312', 'H3.ZE40', 'H3.ZE41', 'H3.ZE43', 'H3.ZE44', 'H4.ZE50', 'H4.ZE51', 'V.Z81', 'V.Z82', 'V.ZE84'}`
3. **Intersection**:
   $$\text{PROV}_{12} \cap \text{C30S} = \{\text{H1.Z15}, \text{H1.Z28}, \text{H1.ZE20}, \text{H2.Z311}, \text{V.ZE84}\} \quad (N = 5)$$

### 6.2. Explicit Set Arithmetic
$$|\text{PROV}_{12} \cup \text{C30S}| = |\text{PROV}_{12}| + |\text{C30S}| - |\text{PROV}_{12} \cap \text{C30S}| = 12 + 25 - 5 = \mathbf{32\text{ meters}}$$
In the C30S cohort, exactly 1 meter (`H1.Z17`) achieved a direct tolerance match rate of $99.967\% \ge 99.9\%$, causing it to be classified as `IDENTICAL`. The non-identical subset $\text{C30S}_{\text{non-ident}}$ contains 24 meters.
Therefore:
$$|\text{PROV}_{12} \cup \text{C30S}_{\text{non-ident}}| = 12 + 24 - 5 = \mathbf{31\text{ meters}}$$
Both numbers from prior summaries are reconciled:
- **32 meters** is the union of $\text{PROV}_{12}$ with the **entire** C30S cohort.
- **31 meters** is the union of $\text{PROV}_{12}$ with the **non-identical** C30S cohort.

### 6.3. Reconciliation of 35 Non-Identical and 36 Tolerant Discrepancy Meters
1. **The 35 Non-Identical Meters** (classification $\neq \text{IDENTICAL}$):
   $$\text{Non-Identical} = |\text{PROV}_{12} \cup \text{C30S}_{\text{non-ident}}| + \text{Residuals} = 31 + 4 = \mathbf{35\text{ meters}} \quad (24\text{ PARTIAL} + 11\text{ DIFFERENT})$$
   The 4 residual meters are:
   - `H1.W12` (C2M, match rate 98.35%, PARTIAL — clean 2-min cadence)
   - `H1.K15` (C6M, match rate 99.23%, PARTIAL — clean 6-min cadence)
   - `H1.K16` (C6M, match rate 99.10%, PARTIAL — clean 6-min cadence)
   - `H1.Z27` (C1M, match rate 0.61%, PARTIAL — persistent baseline drift of ~1094 kWh)
2. **The 36 Meters with $< 100.0000\%$ Tolerance Match Rate**:
   $$\text{Meters with match\_rate} < 1.0 = 79 - 43\text{ (ordinary C1M)} = \mathbf{36\text{ meters}}$$
   $$\text{Meters with match\_rate} < 1.0 = 35\text{ (non-identical)} + 1\text{ (`H1.Z17` at 99.967\%)} = \mathbf{36\text{ meters}}$$

---

## 7. Investigation E — Sampling Cadence Findings

1. **Full Cadence Inventory**:
   - `C15S`: 1 meter (1.27%, `V.Z84`)
   - `C30S`: 25 meters (31.65%, e.g. `V.ZE84`, `H1.Z15`, `H1.Z17`, `H2.ZE64`)
   - `C1M`: 44 meters (55.70%, e.g. `H1.Z10`..`Z14`, `H2.Z*`, `H3.Z*`, `H4.Z*`)
   - `C2M`: 1 meter (1.27%, `H1.W12`)
   - `C6M`: 8 meters (10.13%, `H1.K11`..`K16`, `H2.K21`, `V.K21`, `H1.W11`)
   Total = 79 meters.
2. **Periodic vs Change-of-Value**:
   - Engel et al. (2025) Section "Data collection" documents:
     - Periodic (1 min): ABB-B24 electricity meters and SensorStar thermal meters (forming the bulk of C1M).
     - Change-of-value: Janitza (UMG 96 RM-E, UMG 96 PA MID+) and Socomec submeters (forming the C30S group).
3. **Grid Cadence vs Raw Cadence**:
   - Raw acquisition cadences span 15s to 6m, but ALL cross-check comparisons occur on the standardized **15-minute grid** ($\Delta t = 900\text{s}$).
   - The statement "43 ordinary C1M meters" is strictly verified: 43 of the 44 C1M meters achieve 100.0000% tolerance match rate (the 44th being `H1.Z27` due to baseline drift).

---

## 8. Investigation F — Exact Aggregation Semantics

1. **Production P1-T3 Implementation**:
   - In `etl/resample_15min.py` (lines 63–75, 150–165):
     $$\text{Bin}(t) = (t - 15\text{min}, t] = (t - 900\text{s}, t]$$
   - Left-open, right-closed ceiling logic: an observation at $t - 15\text{min}$ belongs to $\text{Bin}(t - 15\text{min})$; an observation at $t$ belongs to $\text{Bin}(t)$.
   - Operator `LAST`: picks $\operatorname{argmax}_{\tau \in (t - 15\text{min}, t]} \tau$.
2. **Honda Reference Pipeline Semantics**:
   - Engel et al. (2025) Section "Data resampling" states that downsampling cumulative energy ($W$) was executed via **linear interpolation** (not `LAST`).
   - `LAST_right` achieves 100.0000% tolerance match rate on 1-min periodic meters because linear interpolation evaluated at `:15:00.000` grid marks evaluates identically to the interval-end sample at `:15:00.000`.
   - On C30S meters, linear interpolation between sub-minute samples diverges slightly from `LAST`.
   - **Conclusion**: The cross-check establishes **corroborative empirical consistency with the reference pipeline**, NOT proof that Honda literally ran `LAST_right`.

---

## 9. Findings Corrected in the Markdown Report

The following evidence-backed corrections have been applied to `reports/p1_t3_crosscheck_reduced.md`:
1. **Section 2.1**: Clarified that `<METER>.W` denotes Total Active Energy $W$ ($\mathrm{kWh}$, raw pulses, or $\mathrm{Wh}$), not active power $P$ ($\mathrm{W}$). Explained German facility naming prefixes (`W` = Wärme, `K` = Kälte, `Z` = Zähler, `ZE` = Zähler Einspeisung).
2. **Section 6**: Corrected unit labels on error metrics from $\mathrm{W}$ to $\mathrm{kWh}$ ($\text{atol} = 10^{-5}\ \mathrm{kWh}$, $\text{MAE} \le 2.4 \times 10^{-11}\ \mathrm{kWh}$, $\text{MaxAE} = 9.3 \times 10^{-10}\ \mathrm{kWh}$).
3. **Section 7.1 Category A**: Qualified `V.K21` as `SUPPORTED` rather than verified because dividing reference by 100 yields only 1.07% match rate due to multi-month synthetic submeter gap substitution (`substitute_V.K21`).
4. **Section 7.1 Category B**: Reconciled the reported match rate for `V.ZE84` under $\text{atol} = 10^{-5}\ \mathrm{kWh}$ to **35.09%**, strictly matching Table 5 (line 73) and removing the obsolete narrative citation of 96.29% from an unexecuted script template.
5. **Section 7.1 Set Union**: Explicitly clarified set algebra: 32 meters is the union with all C30S meters; 31 meters is the union with non-identical C30S meters.
6. **Section 9**: Added evidence standard qualification: `n_unexplained = 0` is an operational categorization artifact from script logic (`is_unexplained = False`), not experimental closure for all 11 meters.
7. **Section 10**: Corrected error metric units across all cases (Case 1: $\mathrm{kWh}$; Case 2: 35.09% match, $\mathrm{kWh}$; Case 3: pulses, noting $N_{\text{both\_valid}} = 156,081$ denominator conditionality; Case 4: $\mathrm{Wh}$ and $\mathrm{kWh}$).

### 9.1. Final Consistency Patch (2026-10-09)

The following additional terminology and qualification corrections were applied to both `reports/p1_t3_crosscheck_reduced.md` and this audit file:
1. **Measurand vs numerical comparability**: `SAME_QUANTITY_CONFIRMED` is now explicitly scoped to underlying measurement semantics. The distinction between the conceptual measurement variable, the physical unit/scale of each series, and whether direct numerical comparison is valid per meter is documented in §2.1 (report) and §3.3 (audit).
2. **Exact-equality terminology**: All references to "bitwise equality" corrected to "exact floating-point numeric equality (IEEE-754 `==`)" based on code inspection of `crosscheck_reduced_15min.py` line 431 (`c_cand == c_ref`). Tiny nonzero errors described as "consistent with" serialization effects rather than "strictly attributable to" them.
3. **Classification table labels**: Section 8 tables now explicitly labeled as provenance-adjusted classification (IDENTICAL=44, PARTIAL=34, DIFFERENT=1) and direct classification (IDENTICAL=44, PARTIAL=24, DIFFERENT=11) with notes clarifying they are not contradictory.
4. **Provenance and unexplained-discrepancy qualification**: `n_unexplained = 0` qualified as operational categorization, not experimental causal closure. `PROV_12 = 12` labeled as provenance-set membership count. VERIFIED (6 meters) and SUPPORTED (5 meters) evidence levels explicitly distinguished.
5. **Timestamp and numerical-precision language**: Distinguished interior-grid alignment from start/end boundary truncation. Qualified numerical tolerance descriptions.

---

## 10. Unresolved Questions & Smallest Next Actions

1. **Continuous Linear Interpolation Reconstruction for C30S Meters**:
   - *Question*: Does continuous linear interpolation between raw sub-minute timestamps strictly reproduce the reference series across all 25 C30S meters?
   - *Smallest Next Action*: A lightweight standalone verification script evaluating linear interpolation on a single clean C30S meter (`H2.ZE64`) would provide conclusive empirical closure without rerunning the full cross-check.
2. **Proprietary Author Algorithms for `V.Z84` and `V.K21`**:
   - *Question*: What exact piecewise calibration and synthetic submeter models were executed by Honda authors on `V.Z84` and `V.K21`?
   - *Smallest Next Action*: Formally accept these two meters as documented external reference limitations. No attempt should be made to reproduce proprietary, undocumented author scripts in production P1-T3.

---

## 11. Cryptographic Hashes (Before and After Audit & Consistency Patch)

| Modified / Created File | SHA-256 Before Audit | SHA-256 After Audit | SHA-256 After Final Consistency Patch | Status |
| :--- | :--- | :--- | :--- | :---: |
| `reports/p1_t3_crosscheck_reduced.md` | `ec08c7dad36e40781ed56a5461ba7cc68a0ec6eba55e2d2b32b9e3005fe565bb` | `353d29b312e5adc9946ce17897f47593c4d4b3db0a560c445efe30c120d6b58c` | `3e0a772a8165f4da1b72e0037dca7a56bfce6ec233365ef8958887541ae0db14` | Reconciled & Verified |
| `audits/AUDIT_P1_T3_CROSSCHECK_RECONCILIATION.md` | *(Did not exist)* | *(Newly created audit deliverable)* | *(Finalized deliverable)* | Completed |

---

## 12. Confirmation of Invariants & Protocol Adherence

- **Zero Pipeline Code Alterations**: Neither `analysis/crosscheck_reduced_15min.py` nor any file in `etl/`, `src/`, or `tests/` was modified.
- **Zero Cross-Check Re-Executions**: No 79-meter cross-check or pipeline resample was rerun.
- **Zero Research Data Mutations**: `data/raw/` and `data/interim/` were untouched.
- **Scope Compliance**: All file changes are strictly restricted to `reports/p1_t3_crosscheck_reduced.md` and `audits/AUDIT_P1_T3_CROSSCHECK_RECONCILIATION.md`.
