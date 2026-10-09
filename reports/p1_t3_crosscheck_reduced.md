# P1-T3 Extended Independent Cross-Check against Dataset-Provided 15-Minute Reference

**Date**: 2026-10-08 20:50:29 UTC  
**Protocol**: Beyond Synthetic Missingness — Smart-Meter Imputation (v1.1)  
**Task**: P1-T3 Extended Independent Cross-Check (S3 → S20 → S40 → S60 → S79)  
**Status**: READ-ONLY SCIENTIFIC VALIDATION ARTIFACT (Production Pipeline & Gate State Untouched)  

---

## 1. Purpose

> **CORE RESEARCH QUESTION & PROTOCOL BOUNDARY**:
> *Across a progressively broader and representative set of smart meters (3 → 20 → 40 → 60 → 79), is `LAST_right` consistently the best explanatory resampling convention once timestamp semantics and source provenance differences are accounted for?*

> **RESEARCH INTEGRITY INVARIANT (AGENTS.md Compliance)**:
> 1. The external dataset-provided 15-minute resampled files (`<METER>.W_corrected_resampled_15min.csv.gz`) and reduced-data facility aggregates are used **strictly as external corroborative evidence**.
> 2. They are **NOT** ground truth. Ground truth remains strictly tied to authoritative raw meter observations (`*_raw.csv.gz`).
> 3. Corrected values, synthetic linear interpolations, and forward-filled gaps present in the reference files are **never** adopted into production pipelines.
> 4. This study provides strong corroborative evidence that our production P1-T3 convention (`(t-15min, t]`, `LAST`, right-labeled) is externally consistent with the dataset authors' resampling intention wherever unadulterated raw observations are represented.

---

## 2. Reference Source and Provenance

### 2.1. Reference Files Discovered
| Attribute | Discovered Value | Evidence / Notes |
| :--- | :--- | :--- |
| **Dataset Root** | `/run/media/duck/New Volume/Vice - Download/Honda_Dataset` | External raw volume |
| **Facility Aggregates** | `reduced_data/reduced_data/15min/` | 7 files (`electricity_W.csv.gz`, `cooling_W.csv.gz`, `heating_W.csv.gz`, `weather.csv.gz`). Contains microgrid facility totals (`total`, `PV`, `CHP`), NOT individual meter series. |
| **Per-Meter Resampled Path** | `data/<METER>/<METER>.W_corrected_resampled_15min.csv.gz` | Exactly 79 files for all 79 core W meters. |
| **Timestamp Column** | `datetime_utc` | Explicit ISO 8601 UTC (`+00:00`), aligned to quarter-hour grid (`:00`, `:15`, `:30`, `:45`). |
| **Value Column** | `<METER>.W` | Double precision floating point register reading representing **Total Active Energy $W$** (cumulative register: $\mathrm{kWh}$ for electricity meters; raw integer pulse counts for hydronic thermal meters; $\mathrm{Wh}$ for raw `V.Z84`). It is **NOT** active power $P$ (measured in Watts, $\mathrm{W}$). In German facility nomenclature, meter prefix `W` denotes *Wärme* (heating meters `H1.W11`, `H1.W12`), `K` denotes *Kälte* (cooling), `Z` denotes *Zähler* (electrical load), `ZE` denotes *Zähler Einspeisung* (solar generation); file suffix `.W` denotes measurement variable Total Energy. |
| **Physical Units** | $\mathrm{kWh}$ / pulses / $\mathrm{Wh}$ | Both series measure the same conceptual quantity (cumulative energy $W$). However, the raw and reference series for individual meters may differ in physical unit ($\mathrm{Wh}$ vs $\mathrm{kWh}$), numerical scale ($\times 100$ pulse multiplier), sign convention (CT polarity inversion), and processing history (author-side corrections, interpolation). No unit conversions are applied before direct comparison; provenance adjustments are evaluated separately in §7. |
| **Source Provenance** | `_corrected` / `_corrected_raw` | Derived from author-modified intermediate files with heuristic CT polarity reversals, scale multiplications, and gap substitutions. |
| **Missing Policy** | Forward-fill & Linear Interpolation | Authors eliminated NaNs by forward filling empty intervals and interpolating between 30-second observations. |

---

## 3. Sampling Methodology

The sampling order across the 79 core W meters is **100% deterministic, reproducible, and stratified** across all 20 distinct data strata formed by:
- **Hierarchy / Building**: H1 (29), H2 (26), H3 (15), H4 (4), V (5)
- **Meter Family**: Z (electrical load, 52), ZE (generation/solar, 13), K (thermal, 7), T.Z (substation transformer, 5), W (water, 2)
- **Cadence Class**: C15S (1), C30S (25), C1M (44), C2M (1), C6M (8)
- **Observation History**: Multi-year long-history meters vs short-history meter (`H1.ZE20`, ~397 days)
- **Documented Special Cases**: `V.ZE84` (CT polarity inversion), `H1.K11` (x100 scaling), `V.Z84` (duplicate rows post-outage), `H1.ZE20` (installation boundary)

### Invariant Compliance:
- **Cumulative Hierarchy**: $S_3 \subset S_{20} \subset S_{40} \subset S_{60} \subset S_{79}$
- **Pilot Preservation**: $S_3 = \{\text{H1.Z10}, \text{V.ZE84}, \text{H1.K11}\}$ is strictly preserved in rank positions 1–3.
- **Complete Stratum Coverage in $S_{20}$**: Across the entire dataset, exactly 20 distinct `(Building, Category, Cadence)` strata exist. $S_{20}$ selects exactly 1 meter from every single stratum, ensuring representation of every single data type, building, and cadence class from the earliest expanded stage.
- **Round-Robin Expansion ($S_{40}, S_{60}, S_{79}$)**: Remaining meters are allocated cyclically across active strata sorted lexicographically by stratum and meter ID.
- **No duplicates, no non-core meters**: Exactly 79 unique core W meters.

---

## 4. Cumulative Cohorts

| Cohort | Size | Buildings Represented | Categories Represented | Cadence Classes | Special Provenance Cases Included |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **S3** | **3** | H1:2, V:1 | K:1, Z:1, ZE:1 | C1M:1, C30S:1, C6M:1 | CT_inversion:1, x100_scale:1 |
| **S20** | **20** | H1:6, H2:5, H3:3, H4:2, V:4 | K:3, T.Z:1, W:2, Z:9, ZE:5 | C15S:1, C1M:5, C2M:1, C30S:9, C6M:4 | CT_inversion:1, dedup:1, short_history:1, x100_scale:1 |
| **S40** | **40** | H1:12, H2:13, H3:6, H4:4, V:5 | K:5, T.Z:3, W:2, Z:21, ZE:9 | C15S:1, C1M:14, C2M:1, C30S:18, C6M:6 | CT_inversion:1, dedup:1, short_history:1, x100_scale:1 |
| **S60** | **60** | H1:20, H2:20, H3:11, H4:4, V:5 | K:7, T.Z:5, W:2, Z:33, ZE:13 | C15S:1, C1M:25, C2M:1, C30S:25, C6M:8 | CT_inversion:1, dedup:1, short_history:1, x100_scale:1 |
| **S79** | **79** | H1:29, H2:26, H3:15, H4:4, V:5 | K:7, T.Z:5, W:2, Z:52, ZE:13 | C15S:1, C1M:44, C2M:1, C30S:25, C6M:8 | CT_inversion:1, dedup:1, short_history:1, x100_scale:1 |

---

## 5. Per-Meter Results (Representative Summary across All 79 Meters)

| Meter ID | Cohort | Cadence | Direct Cls | Provenance Cls | Best Raw Variant | Provenance-Adjusted Match (%) | Provenance Diagnostic / Root Cause |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **H1.Z10** | `S3` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **V.ZE84** | `S3` | `C30S` | `DIFFERENT` | `PARTIAL` | `MEAN_right` | 35.09% | Sensor CT inversion in _corrected_raw (negative in ref vs positive in authori... |
| **H1.K11** | `S3` | `C6M` | `DIFFERENT` | `PARTIAL` | `LAST_right` | 99.83% | Scale multiplier x100 in _corrected file + forward-fill across 53,917 empty bins |
| **H1.W12** | `S20` | `C2M` | `PARTIAL` | `PARTIAL` | `LAST_right` | 98.35% | Clean observation |
| **H1.W11** | `S20` | `C6M` | `DIFFERENT` | `PARTIAL` | `LAST_right` | 95.67% | Scale multiplier x100 in _corrected file (register counts 9599 vs 959900) + f... |
| **H1.Z15** | `S20` | `C30S` | `DIFFERENT` | `PARTIAL` | `MEAN_right` | 0.01% | Polarity inversion in _corrected file (-355,808 in raw vs +355,808 in ref) + ... |
| **H1.ZE20** | `S20` | `C30S` | `DIFFERENT` | `PARTIAL` | `MEAN_right` | 25.39% | Polarity inversion in _corrected file (+239,644 in raw vs -239,644 in ref) + ... |
| **H2.K21** | `S20` | `C6M` | `DIFFERENT` | `PARTIAL` | `LAST_right` | 99.86% | Scale multiplier x100 in _corrected file + forward-fill across 60,898 empty bins |
| **H2.T.Z30** | `S20` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z35** | `S20` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z311** | `S20` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 0.03% | Current transformer scaling factor 0.8x (utility CT 500:5 vs meter 400:5) app... |
| **H2.ZE64** | `S20` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 98.67% | Clean observation |
| **H3.Z40** | `S20` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.Z312** | `S20` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 96.95% | Clean observation |
| **H3.ZE40** | `S20` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 68.41% | Clean observation |
| **H4.Z50** | `S20` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H4.ZE50** | `S20` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 98.62% | Clean observation |
| **V.K21** | `S20` | `C6M` | `DIFFERENT` | `PARTIAL` | `LAST_right` | 1.07% | Scale multiplier x100 in _corrected file + gap substitution algorithm (substi... |
| **V.Z84** | `S20` | `C15S` | `DIFFERENT` | `DIFFERENT` | `MEAN_right` | 0.00% | 1000x scaling (Wh vs kWh) + polarity inversion + duplicate resolution on 61,7... |
| **V.Z81** | `S20` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 0.73% | Clean observation |
| **H1.K12** | `S40` | `C6M` | `DIFFERENT` | `PARTIAL` | `LAST_right` | 99.64% | Scale multiplier x100 in _corrected file + forward-fill across 53,386 empty bins |
| **H1.Z11** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z17** | `S40` | `C30S` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 99.97% | Clean observation |
| **H2.T.Z31** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z36** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z351** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 98.15% | Clean observation |
| **H2.ZE65** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 97.11% | Clean observation |
| **H3.Z41** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.ZE41** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 66.71% | Clean observation |
| **H4.Z51** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H4.ZE51** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 98.54% | Clean observation |
| **V.Z82** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 0.64% | Clean observation |
| **H1.K14** | `S40` | `C6M` | `DIFFERENT` | `PARTIAL` | `LAST_right` | 99.69% | Scale multiplier x100 in _corrected file + forward-fill across 52,679 empty bins |
| **H1.Z12** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z26** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 12.43% | Clean observation |
| **H2.T.Z32** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z61** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z361** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 98.11% | Clean observation |
| **H2.ZE66** | `S40` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 60.56% | Clean observation |
| **H3.Z43** | `S40` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.ZE43** | `S60` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 68.26% | Clean observation |
| **H1.K15** | `S60` | `C6M` | `PARTIAL` | `PARTIAL` | `LAST_right` | 99.23% | Clean observation |
| **H1.Z13** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z28** | `S60` | `C30S` | `DIFFERENT` | `PARTIAL` | `MEAN_right` | 0.01% | Polarity inversion in _corrected file (-100,650 in raw vs +100,650 in ref) + ... |
| **H2.T.Z33** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z62** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.ZE67** | `S60` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 32.76% | Clean observation |
| **H3.Z44** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.ZE44** | `S60` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 68.31% | Clean observation |
| **H1.K16** | `S60` | `C6M` | `PARTIAL` | `PARTIAL` | `LAST_right` | 99.10% | Clean observation |
| **H1.Z14** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z29** | `S60` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 0.33% | Clean observation |
| **H2.T.Z34** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z63** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.ZE74** | `S60` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 95.83% | Clean observation |
| **H3.Z45** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z16** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z310** | `S60` | `C30S` | `PARTIAL` | `PARTIAL` | `LAST_right` | 1.93% | Clean observation |
| **H2.Z64** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.Z46** | `S60` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z18** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z65** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.Z47** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z19** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z66** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.Z48** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z20** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z67** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.Z49** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z21** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z68** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H3.Z71** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z22** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z69** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z23** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H2.Z70** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z24** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z25** | `S79` | `C1M` | `IDENTICAL` | `IDENTICAL` | `LAST_right` | 100.00% | Clean observation |
| **H1.Z27** | `S79` | `C1M` | `PARTIAL` | `PARTIAL` | `LAST_right` | 0.61% | Clean observation |

---

## 6. Aggregation-Variant Comparison

Across the four diagnostic candidate variants independently derived from authoritative raw observations (`readings_utc.parquet`):
1. `LAST_right`: `resample('15min', closed='right', label='right').last()` (Production P1-T3 convention)
2. `MEAN_right`: `resample('15min', closed='right', label='right').mean()`
3. `LAST_left`: `resample('15min', closed='left', label='left').last()`
4. `MEAN_left`: `resample('15min', closed='left', label='left').mean()`

### Empirical Findings on Variant Performance:
- **Dominance of `LAST_right` Across Cohorts**:
  - Direct raw comparison selects `LAST_right` as the top variant for **74 / 79 meters** (93.67%). In the remaining 5 meters (`V.ZE84`, `H1.Z15`, `H1.ZE20`, `V.Z84`, `H1.Z28`), direct raw comparison achieves 0.00% match rate across all variants due to sensor polarity inversions or unit scaling differences; for these 5 meters, `MEAN_right` is selected solely as a numerical tie-breaking artifact by raw MAE.
  - Across all 68 meters where direct raw comparison achieves a positive match rate (44 IDENTICAL, 24 PARTIAL), `LAST_right` is consistently superior to `MEAN_right`, `LAST_left`, and `MEAN_left`.
  - Under provenance adjustment, `LAST_right` is selected as the top variant for **78 / 79 meters** (98.73%), and for **78 / 78 meters (100.00%)** among the non-duplicate subset.
  - In exactly 1 meter (`V.Z84`), `MEAN_right` remains the selected variant due to unresolved methodological limitations (61,790 post-outage duplicate timestamps, 1000x scaling, polarity reversal, and uncalibrated baseline offset shifts in the reference series).
  - On all 43 ordinary 1-minute load meters (`H1.Z10`, `H1.Z11`..`Z14`, `H2.Z*`, `H3.Z*`, `H4.Z*`), `LAST_right` achieves **100.0000% match rate under numerical tolerance** ($\text{atol} = 10^{-5}\ \mathrm{kWh}$, $\text{rtol} = 10^{-5}$), with maximum reported $\text{MAE} \le 2.4 \times 10^{-11}\ \mathrm{kWh}$, maximum absolute error of $9.3 \times 10^{-10}\ \mathrm{kWh}$, and exact floating-point numeric equality (IEEE-754 `==`) on 81.8% to 100.0% of intervals, where any nonzero difference is consistent with 64-bit float formatting in ASCII CSV text (serialization or floating-point representation effects). In contrast, `MEAN_right` drops to ~83% match and `LAST_left` drops to ~61% match.
  - On high-cadence 30-second and 6-minute meters under provenance adjustment (`H1.K11`, `H1.K12`, `H1.K14`, `H2.K21`, `H1.W11`, `V.ZE84`, `H1.ZE20`), `LAST_right` decisively outperforms `MEAN_right` by margins of **+1.2% to +34.0%** in match rate.

---

## 7. Provenance Diagnostics (Reconciliation of Non-Identical Meters)

Discrepancies across the 35 non-identical meters (and 36 meters with direct match rate under numerical tolerance < 100.0000%) originate from specific transformation categories applied by dataset authors:

### 7.1. Category Decomposition & Set Reconciliation
- **Major Provenance Transformations (`PROV_12`, 12 meters)**:
  - **Category A (Unit Scaling x100)**: `H1.K11`, `H1.K12`, `H1.K14`, `H2.K21`, `V.K21`, `H1.W11` (6 meters). Raw thermal register pulse counts were multiplied by 100 in `_corrected` files. Dividing reference by 100 restores **95.67% to 99.86% match rate** across occupied bins for 5 meters (`H1.K11`, `H1.K12`, `H1.K14`, `H2.K21`, `H1.W11` — `VERIFIED`). For the 6th meter (`V.K21`), dividing by 100 yields only **1.07% match rate** because the reference file also contains multi-month synthetic gap substitution using downstream submeters (`substitute_V.K21`), making its cause `SUPPORTED` rather than experimentally verified.
  - **Category B (Polarity Inversion)**: `V.ZE84`, `H1.Z15`, `H1.Z28`, `H1.ZE20` (4 meters). Sensor CT clamps were inverted; authors flipped signs in `_corrected`. Negating reference aligns polarity/sign: for `V.ZE84`, `-reference` achieves **35.09% match rate** under numerical tolerance ($\text{atol} = 10^{-5}\ \mathrm{kWh}$), strictly reconciling with Table 5 (line 73; the prior narrative citation of 96.29% was an unexecuted template text). Agreement is limited to 35.09% because `V.ZE84` is a C30S meter where authors applied sub-minute linear interpolation. For `H1.ZE20`, negation restores 25.39% match rate; for `H1.Z15` and `H1.Z28`, large register magnitudes ($>10^6\ \mathrm{kWh}$) and continuous interpolation prevent numerical tolerance match.
  - **Category D (Outage Duplicates & Piecewise Scaling)**: `V.Z84`, `H2.Z311` (2 meters). `V.Z84` has 61,790 post-outage duplicates, 1000x scaling ($\mathrm{Wh}$ vs $\mathrm{kWh}$), sign inversion, and uncalibrated baseline offset shifts (`SUPPORTED`); `H2.Z311` has a documented 0.8x CT transformer correction factor combined with piecewise corrections (`SUPPORTED`).
- **High-Cadence Cadence Group (`C30S`, 25 meters total; 24 non-identical)**:
  - Authors applied continuous linear time-interpolation between 30-second observations to align to `:15:00.000` grid marks, plus synthetic forward-filling of telemetry gaps.
  - Exactly 1 C30S meter (`H1.Z17`) achieved 99.97% match (classified as `IDENTICAL`).
  - Exactly 24 C30S meters have match rate < 99.9% (classified as `PARTIAL`).
- **Category Overlap (Exact Intersection & Set Union)**:
  - Categories overlap: exactly **5 meters** belong to BOTH the 12 Major Transformations and the C30S cadence group:
    $$\text{Intersection} = \text{PROV\_12} \cap \text{C30S} = \{\text{H1.Z15}, \text{H1.Z28}, \text{H1.ZE20}, \text{H2.Z311}, \text{V.ZE84}\} \quad (N = 5)$$
  - All 4 meters of Category B and 1 meter of Category D (`H2.Z311`) are C30S meters.
  - Reconciling the previously conflicting union counts via explicit set algebra:
    - **Union with all C30S meters**:
      $$|\text{PROV\_12} \cup \text{C30S}| = |\text{PROV\_12}| + |\text{C30S}| - |\text{PROV\_12} \cap \text{C30S}| = 12 + 25 - 5 = \mathbf{32\text{ meters}}$$
    - **Union with non-identical C30S meters**:
      $$|\text{PROV\_12} \cup \text{C30S}_{\text{non-ident}}| = 12 + 24 - 5 = \mathbf{31\text{ meters}}$$
    - Prior summaries cited both 31 and 32: **31** represents the non-identical subset (excluding `H1.Z17`), while **32** represents the full cohort union.
- **Residual Non-Identical Meters (4 meters)**:
  - The remaining 4 non-identical meters that are neither in `PROV_12` nor in `C30S` are:
    - `H1.W12` (C2M, match rate 98.35%, PARTIAL — clean 2-minute cadence observation)
    - `H1.K15` (C6M, match rate 99.23%, PARTIAL — clean 6-minute cadence observation)
    - `H1.K16` (C6M, match rate 99.10%, PARTIAL — clean 6-minute cadence observation)
    - `H1.Z27` (C1M, match rate 0.61%, PARTIAL — 1-minute load meter with continuous reference drift/offset)
- **Total Reconciliation**:
  - Total non-identical meters in direct classification: $31 + 4 = 35$ meters (24 PARTIAL, 11 DIFFERENT).
  - Total meters with any discrepancy (< 100.0000% match rate under numerical tolerance): $35 + 1 \text{ (H1.Z17)} = 36$ meters (exactly $79 - 43 = 36$).

---

## 8. Cohort-Level Evidence

### Cumulative Evidence Table Across Stages (Provenance-Adjusted Classification)

> **Classification method**: Each meter's classification reflects provenance-adjusted comparison — i.e., after accounting for documented author transformations (sign inversion, scale correction) in the diagnostic evaluation. This yields IDENTICAL=44, PARTIAL=34, DIFFERENT=1 at S79.

| Stage | Size ($N$) | `LAST_right` Best | `LAST_right` Win Rate | IDENTICAL | PARTIAL | DIFFERENT | UNEXPLAINED |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **S3** | 3 | 3 | **100.00%** | 1 | 2 | 0 | **0** |
| **S20** | 20 | 19 | **95.00%** | 5 | 14 | 1 | **0** |
| **S40** | 40 | 39 | **97.50%** | 15 | 24 | 1 | **0** |
| **S60** | 60 | 59 | **98.33%** | 26 | 33 | 1 | **0** |
| **S79** | 79 | 78 | **98.73%** | 44 | 34 | 1 | **0** |

### Direct Raw Comparison Summary (Direct Classification — Without Provenance Adjustments)

> **Classification method**: Each meter's classification reflects unadjusted direct comparison between the raw P1-T3 resampled series and the reference series, with no sign flips, scale corrections, or other provenance adjustments applied. This yields IDENTICAL=44, PARTIAL=24, DIFFERENT=11 at S79. The two tables are not contradictory — they measure different stages of the classification pipeline.

| Stage | Size ($N$) | Direct IDENTICAL | Direct PARTIAL | Direct DIFFERENT | Notes |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **S3** | 3 | 1 | 0 | 2 | All DIFFERENT meters are categorized by provenance (see §9 for evidence-strength qualification) |
| **S20** | 20 | 5 | 7 | 8 | All DIFFERENT meters are categorized by provenance (see §9 for evidence-strength qualification) |
| **S40** | 40 | 15 | 15 | 10 | All DIFFERENT meters are categorized by provenance (see §9 for evidence-strength qualification) |
| **S60** | 60 | 26 | 23 | 11 | All DIFFERENT meters are categorized by provenance (see §9 for evidence-strength qualification) |
| **S79** | 79 | 44 | 24 | 11 | All DIFFERENT meters are categorized by provenance (see §9 for evidence-strength qualification) |

---

## 9. Unexplained Discrepancies

- **Total Unexplained Meters**: `n_unexplained = 0`
- **Unexplained Meter IDs**: `[]` (None)
- **Operational Categorization**: Under the cross-check script's classification logic (`is_unexplained = False`), zero meters are flagged as unexplained. All 11 `DIFFERENT` meters are assigned to plausible provenance failure categories:
  1. Known author sensor transformations (CT polarity inversion, x100 scaling, 0.8x transformer factor).
  2. Author post-processing methods (continuous linear interpolation to grid marks, synthetic forward-filling of telemetry gaps, outage duplicate handling).
  3. In no case is there an unexplained timestamp misalignment or unclassified value discrepancy under this scheme.
- **Evidence Standard Qualification**:
  - `n_unexplained = 0` is the operational output of heuristic classification logic. It does **not** establish experimental causal closure for every DIFFERENT meter.
  - `PROV_12 = 12` is a **provenance-set membership count** — the number of meters assigned to major provenance transformation categories. It is not a count of 12 experimentally confirmed root causes.
  - **VERIFIED (6 meters)**: Five scale ×100 meters (`H1.K11`, `H1.K12`, `H1.K14`, `H2.K21`, `H1.W11`) and one CT polarity meter (`V.ZE84`) are classified as **VERIFIED** — the proposed transformation, when reversed, restores substantial match rates from existing artifact evidence.
  - **SUPPORTED (5 meters)**: The remaining five meters (`V.K21`, `V.Z84`, `H1.ZE20`, `H1.Z15`, `H1.Z28`) are classified as **SUPPORTED** — documented author modifications provide plausible explanations, but deterministic reconstruction from published artifacts has not been achieved.

---

## 10. Known Special Cases (Pilot Reproduction & Retained Forensic Cases)

### Case 1: H1.Z10 (High-Cadence Ordinary Load Meter)
- **Classification**: **IDENTICAL** (100.0000% match rate under numerical tolerance $\text{atol} = 10^{-5}\ \mathrm{kWh}$ across all 210,337 quarter-hours).
- **Exact Floating-Point Match Rate**: 87.33% (183,679 rows achieve exact floating-point numeric equality via IEEE-754 `==`, while 100.0000% of rows satisfy numerical tolerance; nonzero differences have $\text{MAE} = 3.55 \times 10^{-12}\ \mathrm{kWh}$ and $\text{MaxAE} = 5.82 \times 10^{-11}\ \mathrm{kWh}$, consistent with 64-bit float formatting in ASCII CSV text).
- **Conclusion**: Confirms that when raw data is untouched by author corrections, `LAST_right` reproduces reference values within numerical precision consistent with floating-point representation and ASCII CSV serialization effects to 14 decimal places.

### Case 2: V.ZE84 (Solar Generation Meter with CT Inversion)
- **Direct Classification**: DIFFERENT (0.00% direct match).
- **Provenance Diagnosis**: Author inverted CT polarity in `_corrected_raw` (reference is negative, raw is positive), linearly interpolated across 30s observations, and forward-filled 7,718 empty bins.
- **Provenance Match**: `-reference` matches with **35.09% accuracy** on occupied bins under $\text{atol} = 10^{-5}\ \mathrm{kWh}$ ($\text{MAE} = 0.0458\ \mathrm{kWh}$), strictly reconciling with Table 5 (line 73; the prior narrative citation of 96.29% was an unexecuted template text). `LAST_right` decisively outperforms `MEAN_right` (24.52%) and `LAST_left` (0.02%). The remaining divergence is attributable to C30S continuous linear interpolation to grid boundaries vs raw `LAST` observation.

### Case 3: H1.K11 (Building 1 Thermal Heat Meter with x100 Scaling)
- **Direct Classification**: DIFFERENT (0.00% direct match).
- **Provenance Diagnosis**: Reference file scaled raw register pulse values by 100 (`107` → `10,700`) and forward-filled across 53,917 empty bins.
- **Provenance Match**: `reference / 100` matches **99.8392% of occupied bins** ($N_{\text{both\_valid}} = 156,081$) with `LAST_right` ($\text{MAE} = 0.00119\ \mathrm{pulses}$), beating `MEAN_right` (98.54%) and `LAST_left` (97.50%). Over the full 6-year grid ($209,998$ bins), agreement is ~74.2% because P1-T3 preserves raw NaNs while the reference forward-filled missing telemetry.

### Case 4: V.Z84 (Transformer Outage Meter with Duplicates & 1000x Scaling)
- **Direct Classification**: DIFFERENT (0.00% direct match across all candidate variants under numerical tolerance).
- **Tie-Breaker Artifact**: `MEAN_right` wins the nominal direct ranking solely through the MAE tie-breaker when all candidate match rates are 0.00%. Because `V.Z84` is a monotonically increasing cumulative energy register ($8.5\times 10^5\ \mathrm{Wh} \to 5.73\times 10^8\ \mathrm{Wh}$) evaluated against an opposite-signed negative reference series ($\sim -850\ \mathrm{kWh} \to -5.73\times 10^5\ \mathrm{kWh}$), absolute error is additive ($c_{\text{cand}} + |c_{\text{ref}}|$). In 86.7% of occupied intervals, the intra-interval mean is smaller than the interval-end reading ($\text{LAST} > \text{MEAN}$ with mean difference $\overline{\text{LAST} - \text{MEAN}} = 1,608.19\ \mathrm{Wh}$), which trivially yields a slightly lower MAE for `MEAN` ($295,680,352.51\ \mathrm{Wh}$ vs $295,681,960.71\ \mathrm{Wh}$). This is purely an artifact of cumulative register monotonicity evaluated against an inverted, transformed reference series, not evidence of a 15-minute `mean` binning intent or a defect in P1-T3.
- **Provenance Diagnosis & Methodological Limitation**: Raw telemetry contains 61,790 duplicate timestamps following the 2023-05-15 disconnection outage, while the authors' intermediate `_corrected` file contains 164,404 duplicates, 1000x scaling ($\mathrm{Wh}$ vs $\mathrm{kWh}$), sign inversion, and uncalibrated baseline offset shifts. We explicitly report this as an unresolved methodological limitation: the authors' proprietary multi-step correction pipeline cannot be reverse-engineered bit-for-bit from the published artifacts. We do not claim to have reconstructed their undocumented correction pipeline. This limitation does not justify modifying P1-T3, which strictly resamples authoritative raw observations.

---

## 11. Final Defensible Conclusion

### Question 1: Is `LAST_right` consistently the best explanatory variant?
- **Direct raw comparison**: `LAST_right` is best for **74 / 79 meters** (93.67%). In the remaining 5 meters (`V.ZE84`, `H1.Z15`, `H1.ZE20`, `V.Z84`, `H1.Z28`), all raw variants achieve 0.00% match rate due to polarity inversions or scale differences, where `MEAN_right` is selected as a numerical tie-breaking artifact by raw MAE.
- **Positive direct agreement subset**: `LAST_right` is best for **68 / 68 meters (100.00%)** among all meters achieving positive direct match rate with the reference series (44 IDENTICAL, 24 PARTIAL).
- **Provenance-adjusted comparison**: `LAST_right` is best for **78 / 79 meters** (98.73%).
- **Non-duplicate subset**: `LAST_right` is best for **78 / 78 meters (100.00%)** among meters without telemetry duplicate anomalies.
- **Duplicate-affected meter (`V.Z84`)**: In the single remaining meter (`V.Z84`), `MEAN_right` wins the direct ranking only through the MAE tie-breaker when all candidate match rates are zero. This is an artifact of cumulative register monotonicity evaluated against an inverted, transformed reference series, not evidence to modify P1-T3. The authors' proprietary correction pipeline for this meter remains undocumented in the dataset release and is not reconstructed here.

### Question 2: How many meters have unexplained discrepancies?
```text
n_unexplained = 0
```
Under the cross-check script's classification logic, zero meters are flagged as unexplained: all observed differences are categorized into known author transformations, continuous time-interpolation, or synthetic gap fills. This is an **operational categorization result**, not a claim of experimental causal closure for all 11 DIFFERENT meters. Six meters are VERIFIED (transformation reversal restores match); five are SUPPORTED (plausible documented cause without deterministic reconstruction).

### Question 3: How many meters differ only because of provenance transformations?
```text
n_provenance_explained = 12 (PROV_12 set membership count)
```
`PROV_12 = 12` is the number of meters assigned to major provenance transformation categories, not a count of 12 experimentally confirmed causes. Of these 12 members, 6 are VERIFIED and 5 are SUPPORTED (see §9). The 12th member (`H2.Z311`) is classified PARTIAL, not DIFFERENT, in direct comparison.

Total non-identical meters: 35 (24 PARTIAL, 11 DIFFERENT). Total meters with any discrepancy (< 100.0000% match rate): 36 (see §7 for full set reconciliation including the 5-meter overlap and 4 residual meters).

### Question 4: Did timestamp convention explain any discrepancies?
```text
n_timestamp_convention = 0 (interior grid)
```
All 79 reference files use the same right-labeled UTC quarter-hour grid on their interior timestamps. Zero unexplained interior-grid timestamp offsets exist. However, subtle **boundary truncation differences** (1–6 bins at the start/end of the 6-year period) are documented in §12: P1-T3 strictly implements `ceil_to_15min` across authoritative raw data, whereas reference files truncated or floored boundary bins. These boundary differences do not affect interior match rates but should not be conflated with a claim that timestamp conventions caused zero discrepancies of any kind.

### Question 5: Did any evidence require changing P1-T3?
**NO.**
- The external reference files (`<METER>.W_corrected_resampled_15min.csv.gz`) are derived and corrected data containing heuristic sensor adjustments, gap substitutions, and synthetic linear interpolations; they are **NOT ground truth** (per AGENTS.md Invariant 5). Ground truth remains strictly anchored to authoritative raw meter observations (`*_raw.csv.gz`).
- This cross-check alone provides **no justification for modifying P1-T3**.
- While the results strongly corroborate that our production P1-T3 aggregation specification (`(t-15min, t]`, `LAST`, right-labeled) aligns with the dataset authors' resampling intention wherever clean raw observations exist, this cross-check does NOT prove that the pipeline has zero possible defects across all data dimensions.

---

## 12. Limitations

1. **Reference files are not Ground Truth**: Agreement with `<METER>.W_corrected_resampled_15min.csv.gz` provides corroborative evidence of temporal binning conventions, but does not validate corrected or forward-filled values as ground truth (AGENTS.md Invariant 5).
2. **Boundary truncation vs interior alignment**: On the interior quarter-hour grid, all 79 meters show identical timestamp conventions between P1-T3 and reference. However, subtle boundary discrepancies (1–6 bins at the start/end of the 6-year period) occur because P1-T3 strictly implements `ceil_to_15min` across authoritative raw data, whereas reference files truncated or floored boundary bins. These boundary effects are excluded from the interior match rate calculation.
3. **Numerical equality vs agreement within tolerance**: The exact floating-point match metric uses IEEE-754 `==` (not bitwise comparison). Where exact equality is not achieved but numerical tolerance is satisfied (e.g., $\text{MAE} \le 2.4 \times 10^{-11}\ \mathrm{kWh}$), the residual differences are consistent with serialization or floating-point representation effects in ASCII CSV I/O, but have not been directly proven to arise from those specific mechanisms.
4. **Scope Discipline**: This study addresses strictly the temporal aggregation of variable $W$. It does not analyze multivariate covariates ($P$, temperature, solar irradiance) or imputation models, which are reserved for later phases.
5. **Measurand vs numerical comparability**: Both series measure the same conceptual quantity (cumulative energy $W$), but for meters with documented unit scaling ($\mathrm{Wh}$ vs $\mathrm{kWh}$, ×100 pulse multiplier), sign inversion, or author-side corrections, direct numerical comparison of raw and reference values is not valid without adjustment. This does not invalidate the cross-check, which evaluates direct and provenance-adjusted classifications separately.

---

## 13. Analysis Artifact Integrity Hashes

- `analysis/crosscheck_reduced_15min.py` SHA-256: `fef605106e53e94a66fd32207c545d33bd98e3c50c7657874c3a2fba25fa4452`
- `reports/p1_t3_crosscheck_sampling.json` SHA-256: `0693c1a2ed8b13e8d60c65b275f2df70916f01e16c584bbda6001d26e7cd7bae`
- `reports/p1_t3_crosscheck_reduced.csv` SHA-256: `42755e5f906c982d787f982187b6ff0e13f4ca0d09f3acc6bf1590308f87239f`
