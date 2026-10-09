# P1-T4 Audit Report — Quality & Provenance Flags

- **Task ID**: P1-T4 (Build Quality Flags)
- **Protocol Version**: v1.1 (Official)
- **Execution Timestamp (UTC)**: 2026-10-07T18:08:07.564500+00:00
- **Seed**: 42
- **Execution Duration**: 20.73 s
- **Peak RSS Memory**: 514.4 MB

## 1. Input Artifact
- **File Path**: `/home/duck/Downloads/Vice - Download/StudyWithVKU/StudyWithVKU/ThirdYear/data-warehousing/data/interim/readings_15min.parquet`
- **File Size**: 394,072,801 bytes (375.82 MB)
- **Total Input Rows**: 13,981,597
- **Meter Count**: 79 meters

## 2. Output Artifact
- **File Path**: `/home/duck/Downloads/Vice - Download/StudyWithVKU/StudyWithVKU/ThirdYear/data-warehousing/data/interim/readings_15min_flagged.parquet`
- **File Size**: 394,798,308 bytes (376.51 MB)
- **Output SHA-256**: `c672d5a4efc6cb636708480675e6a2947c436373b05f1bfb8e3307dc9299d279`
- **Compression**: SNAPPY (Parquet format v2.6, 79 row groups)

## 3. Schema Specification
```sql
CREATE TABLE readings_15min_flagged (
    meter_id              VARCHAR(50) NOT NULL,
    grid_timestamp_utc    TIMESTAMP NOT NULL,
    timestamp_local       TIMESTAMP NOT NULL,
    source_timestamp_utc  TIMESTAMP,
    value                 DOUBLE,
    raw_source_file       VARCHAR(255),
    raw_record_count      INTEGER NOT NULL,
    expected_record_count INTEGER NOT NULL,
    bin_completeness      DOUBLE NOT NULL,
    cadence_class         VARCHAR(20) NOT NULL,
    is_missing            BOOLEAN NOT NULL,
    has_issue             BOOLEAN NOT NULL,
    is_corrected          BOOLEAN NOT NULL,
    is_valid_ground_truth BOOLEAN NOT NULL
);
```

## 4. Flag Definitions
1. **`is_missing`** (`BOOLEAN NOT NULL`):
   - `TRUE` when `raw_record_count == 0` and `value IS NULL` (observation gap).
   - `FALSE` when an authentic raw reading exists in the right-closed bin $(t-15\text{min}, t]$.
2. **`has_issue`** (`BOOLEAN NOT NULL`):
   - `TRUE` when the 15-minute grid bin $(t-15\text{min}, t]$ intersects an authoritative issue interval from `issues/automatic_issues/*.yaml` or `issues/manual_issues/*.yaml` per Ratified Protocol v1.1 Amendment ($s \le t \land e > t - 15\text{min}$).
   - `FALSE` otherwise. Empty bins are NOT marked as issue-affected unless corroborated by an authoritative issue interval.
3. **`is_corrected`** (`BOOLEAN NOT NULL`):
   - `TRUE` if observation originated from a corrected source file (`_corrected_raw`).
   - `FALSE` for 100% of rows (0 / 13,981,597) because corrected files are strictly excluded by Protocol v1.1.
4. **`is_valid_ground_truth`** (`BOOLEAN NOT NULL`):
   - Hard invariant protection flag: `is_valid_ground_truth = (NOT is_missing) AND (NOT has_issue) AND (NOT is_corrected)`.
   - Identifies pure, uncontaminated real meter observations suitable for ground truth.

## 5. Issue-Source Provenance
- **Authoritative Location**: `/run/media/duck/New Volume/Vice - Download/Honda_Dataset/issues`
- **Automatic Issues**: 81 YAML files (`issues/automatic_issues/*_issues_automatic.yaml`), containing 148,958 logged issue intervals across meters.
- **Manual Issues**: 7 YAML files (`issues/manual_issues/*_issues_manual.yaml`), containing 10 curated issue intervals.
- **Timezone Semantics**: All issue timestamps parsed deterministically to canonical integer UTC seconds. Local ISO timestamps with explicit UTC offsets (`+0100`, `+0200`) converted to UTC.
- **Manual Transcription Handling**: In `issues/manual_issues/H1.Z19_issues_manual.yaml`, file naming and key prefix `H1.Z19@...` correctly map to meter `H1.Z19`, overriding the internal copy-pasted `reference: H2.Z311`.

## 6. Row-Count Reconciliation
| Metric | Input (P1-T3) | Output (P1-T4) | Delta | Conservation Rate |
|---|:---:|:---:|:---:|:---:|
| **Total Rows** | 13,981,597 | 13,981,597 | 0 | 100.00% |
| **Meter Count** | 79 | 79 | 0 | 100.00% |
| **Occupied Bins** | 13,333,577 | 13,333,577 | 0 | 100.00% |
| **Empty Bins** | 648,020 | 648,020 | 0 | 100.00% |
| **Row Groups** | 79 | 79 | 0 | 100.00% |

## 7. Value-Integrity Verification
- **Bit-for-Bit Float Match**: 100% of non-NaN float values in P1-T4 match P1-T3 bit-for-bit across all 79 meters.
- **NaN Mask Match**: 100% of NaN positions (648,020 positions) match P1-T3 bit-for-bit.
- **Value Buffer SHA-256 Hash**: `8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe` (identical between P1-T3 and P1-T4).
- **Null Count Reconciliation**:
  - `value`: 648,020 (4.63%)
  - `source_timestamp_utc`: 648,020 (4.63%)
  - `raw_source_file`: 648,020 (4.63%)
  - All other 11 columns (`meter_id`, `grid_timestamp_utc`, `timestamp_local`, counts, completeness, cadence, flags): **0 nulls**.

## 8. Issue Matching Statistics
| Quadrant | State | Flag Condition | Count | Percentage | Semantic Description |
|:---:|---|---|:---:|:---:|---|
| **Q1** | **Clean Observed** | `is_missing=F, has_issue=F` | **12,637,042** | **90.38%** | Pure authentic ground truth observations |
| **Q2** | **Issue Observed** | `is_missing=F, has_issue=T` | **696,535** | **4.98%** | Observed readings during equipment/transformer anomalies |
| **Q3** | **Unrelated Gap** | `is_missing=T, has_issue=F` | **527,756** | **3.77%** | Observation gaps outside issue intervals (**NOT failure**) |
| **Q4** | **Corroborated Gap** | `is_missing=T, has_issue=T` | **120,264** | **0.86%** | Observation gaps corroborated by authoritative issue log |
| — | **Total Grid Rows** | — | **13,981,597** | **100.00%** | Row count perfectly matches P1-T3 |

## 9. Empty-Bin Treatment
- Exactly **527,756 empty bins** (3.77%) are observation gaps outside issue intervals (`has_issue = FALSE`).
- Protocol v1.1 invariant strictly enforced: Empty bins (`is_missing = TRUE`) are NOT automatically classified as equipment failures.
- Only **120,264 empty bins** (0.86%) with direct corroboration from authoritative issue logs receive `has_issue = TRUE`.

## 10. H1.ZE20 Handling
- Temporal grid boundary: coverage strictly begins at true installation: `2022-11-30 08:30:00 UTC`.
- Exactly 38,075 grid rows preserved; zero rows created prior to installation.
- Issue intervals for H1.ZE20 matched within active sensor history only.

## 11. Leakage Controls
- Descriptive metadata fields (`raw_record_count`, `expected_record_count`, `bin_completeness`) remain non-feature descriptive fields per `configs/default.yaml` (`feature_governance.forbidden_as_imputation_inputs`).
- No post-mask source information is exposed as a model feature.
- Quality flags reflect pre-existing source and issue provenance only.

## 12. Raw Immutability
- External Honda dataset directory (`/run/media/duck/New Volume/Vice - Download/Honda_Dataset/issues`) and `data/raw/` are strictly read-only and unmutated.
- Zero raw files created, modified, or deleted.

## 13. Tests
- All unit tests in `tests/test_P1_T4.py` pass 100%:
  - `T4-01 Schema`: All 14 columns exist with exact types; quality flags are boolean.
  - `T4-02 Observed bins`: Bins with raw observations have `is_missing = FALSE` (verified across all 79 meters).
  - `T4-03 Empty bins`: Empty bins have `is_missing = TRUE`, `value = NaN` (648,020 total empty bins).
  - `T4-04 Value immutability`: 100% bit-for-bit identical floats to P1-T3 across all 79 meters.
  - `T4-05 Timestamp immutability`: 100% identical grid, local, and source timestamps across all 79 meters.
  - `T4-06 Provenance immutability`: 100% identical source files, record counts, completeness, cadence across all 79 meters.
  - `T4-07 Issue matching`: Verified on real boundary cases and Ratified Amendment semantics.
  - `T4-08 No false failure inference`: 527,756 empty bins outside issue logs maintain `has_issue = FALSE`.
  - `T4-09 Corrected-source protection`: `is_corrected = FALSE` for 100% of rows (zero corrected values).
  - `T4-10 Population`: All 79 meters preserved, exactly 13,981,597 rows.
  - `T4-11 H1.ZE20 coverage`: Coverage preserved starting at 2022-11-30 08:30:00 UTC.
  - `T4-12 Anti-leakage mandate`: Descriptive metadata strictly forbidden from imputation model feature sets.
  - `T4-13 Raw immutability`: External Honda dataset remains untouched.
- Full repository test suite passing.

## 14. Output SHA-256
`c672d5a4efc6cb636708480675e6a2947c436373b05f1bfb8e3307dc9299d279`

## 15. Limitations & Notes
1. **Manual Issue Transcriptions**: In `issues/manual_issues/H1.Z19_issues_manual.yaml`, internal field `reference: H2.Z311` was transcribed due to upstream copy-paste, while filename and key prefix `H1.Z19@...` correctly indicate meter `H1.Z19`. Matching associates the issue with `H1.Z19`.
2. **Clean Ground Truth Yield**: Across the 79 core meters, 12,637,042 bins (90.38%) satisfy all cleanliness criteria (`is_valid_ground_truth = TRUE`), providing the authoritative foundation for Stage P1-T5 clean-segment extraction.
3. **Resource Consumption**: Pipeline executed out-of-core with peak RSS of 514.4 MB and runtime of 20.73 s.

## Appendix: Per-Meter Flag Summary (All 79 Core Meters)
| Meter ID | Grid Rows | Occupied | Empty | Issues Logged | Has Issue | Clean GT | Unrelated Gap | Corroborated Gap |
|---|---|---|---|---|---|---|---|---|
| H1.K11 | 209,999 | 156,082 | 53,917 | 872 | 4,852 | 152,956 | 52,191 | 1,726 |
| H1.K12 | 210,053 | 156,667 | 53,386 | 1,065 | 5,340 | 153,178 | 51,535 | 1,851 |
| H1.K14 | 210,090 | 157,411 | 52,679 | 3,463 | 14,748 | 144,715 | 50,627 | 2,052 |
| H1.K15 | 210,098 | 162,943 | 47,155 | 537 | 3,320 | 161,169 | 45,609 | 1,546 |
| H1.K16 | 178,708 | 156,607 | 22,101 | 49 | 1,713 | 156,486 | 20,509 | 1,592 |
| H1.W11 | 210,336 | 185,064 | 25,272 | 32 | 1,565 | 185,017 | 23,754 | 1,518 |
| H1.W12 | 210,335 | 178,874 | 31,461 | 379 | 107,645 | 75,885 | 26,805 | 4,656 |
| H1.Z10 | 210,337 | 210,337 | 0 | 2,519 | 8,682 | 201,655 | 0 | 0 |
| H1.Z11 | 210,337 | 210,337 | 0 | 2,520 | 8,756 | 201,581 | 0 | 0 |
| H1.Z12 | 210,337 | 210,337 | 0 | 2,522 | 8,760 | 201,577 | 0 | 0 |
| H1.Z13 | 210,337 | 210,337 | 0 | 2,516 | 8,752 | 201,585 | 0 | 0 |
| H1.Z14 | 210,337 | 210,337 | 0 | 2,518 | 8,756 | 201,581 | 0 | 0 |
| H1.Z15 | 210,336 | 206,846 | 3,490 | 2,355 | 8,162 | 202,171 | 3 | 3,487 |
| H1.Z16 | 210,337 | 210,337 | 0 | 2,461 | 4,753 | 205,584 | 0 | 0 |
| H1.Z17 | 210,336 | 206,834 | 3,502 | 2,405 | 8,275 | 202,061 | 0 | 3,502 |
| H1.Z18 | 210,337 | 210,337 | 0 | 2,519 | 8,727 | 201,610 | 0 | 0 |
| H1.Z19 | 210,337 | 210,337 | 0 | 2,519 | 68,562 | 141,775 | 0 | 0 |
| H1.Z20 | 210,337 | 210,337 | 0 | 2,515 | 8,758 | 201,579 | 0 | 0 |
| H1.Z21 | 210,337 | 210,337 | 0 | 2,511 | 8,715 | 201,622 | 0 | 0 |
| H1.Z22 | 210,337 | 210,337 | 0 | 2,508 | 8,754 | 201,583 | 0 | 0 |
| H1.Z23 | 208,248 | 208,248 | 0 | 2,508 | 8,712 | 199,536 | 0 | 0 |
| H1.Z24 | 208,248 | 208,248 | 0 | 2,508 | 8,755 | 199,493 | 0 | 0 |
| H1.Z25 | 208,248 | 208,248 | 0 | 2,511 | 8,759 | 199,489 | 0 | 0 |
| H1.Z26 | 210,333 | 204,269 | 6,064 | 2,395 | 8,250 | 199,603 | 2,480 | 3,584 |
| H1.Z27 | 210,336 | 204,442 | 5,894 | 2,406 | 8,264 | 199,697 | 2,375 | 3,519 |
| H1.Z28 | 210,336 | 206,839 | 3,497 | 2,403 | 8,259 | 202,069 | 8 | 3,489 |
| H1.Z29 | 210,336 | 203,456 | 6,880 | 2,256 | 7,972 | 198,970 | 3,394 | 3,486 |
| H1.Z310 | 123,237 | 68,355 | 54,882 | 227 | 2,113 | 68,085 | 53,039 | 1,843 |
| H1.ZE20 | 38,075 | 27,980 | 10,095 | 12 | 876 | 27,964 | 9,235 | 860 |
| H2.K21 | 210,068 | 149,169 | 60,899 | 8,749 | 40,372 | 122,518 | 47,178 | 13,721 |
| H2.T.Z30 | 180,256 | 180,256 | 0 | 2,550 | 7,450 | 172,806 | 0 | 0 |
| H2.T.Z31 | 180,256 | 180,256 | 0 | 2,522 | 7,435 | 172,821 | 0 | 0 |
| H2.T.Z32 | 180,256 | 180,256 | 0 | 2,515 | 7,490 | 172,766 | 0 | 0 |
| H2.T.Z33 | 210,337 | 210,337 | 0 | 2,939 | 13,082 | 197,255 | 0 | 0 |
| H2.T.Z34 | 180,256 | 180,256 | 0 | 2,728 | 11,765 | 168,491 | 0 | 0 |
| H2.Z311 | 123,333 | 64,538 | 58,795 | 218 | 23,640 | 52,422 | 47,271 | 11,524 |
| H2.Z35 | 210,337 | 210,337 | 0 | 5 | 17 | 210,320 | 0 | 0 |
| H2.Z351 | 115,444 | 114,207 | 1,237 | 211 | 1,648 | 113,796 | 0 | 1,237 |
| H2.Z36 | 210,337 | 210,337 | 0 | 5 | 17 | 210,320 | 0 | 0 |
| H2.Z361 | 115,444 | 114,203 | 1,241 | 210 | 1,651 | 113,793 | 0 | 1,241 |
| H2.Z61 | 210,337 | 210,337 | 0 | 2,723 | 11,729 | 198,608 | 0 | 0 |
| H2.Z62 | 210,337 | 210,337 | 0 | 2,724 | 11,731 | 198,606 | 0 | 0 |
| H2.Z63 | 210,337 | 210,337 | 0 | 2,731 | 11,818 | 198,519 | 0 | 0 |
| H2.Z64 | 210,337 | 210,337 | 0 | 2,710 | 11,759 | 198,578 | 0 | 0 |
| H2.Z65 | 210,337 | 210,337 | 0 | 2,657 | 13,899 | 196,438 | 0 | 0 |
| H2.Z66 | 210,337 | 210,337 | 0 | 2,601 | 13,942 | 196,395 | 0 | 0 |
| H2.Z67 | 210,337 | 210,337 | 0 | 2,595 | 13,898 | 196,439 | 0 | 0 |
| H2.Z68 | 210,337 | 210,337 | 0 | 2,593 | 13,882 | 196,455 | 0 | 0 |
| H2.Z69 | 210,337 | 210,337 | 0 | 2,591 | 13,924 | 196,413 | 0 | 0 |
| H2.Z70 | 210,337 | 210,337 | 0 | 2,593 | 13,895 | 196,442 | 0 | 0 |
| H2.ZE64 | 62,337 | 61,479 | 858 | 13 | 878 | 61,459 | 0 | 858 |
| H2.ZE65 | 60,218 | 59,449 | 769 | 10 | 783 | 59,435 | 0 | 769 |
| H2.ZE66 | 62,337 | 61,319 | 1,018 | 14 | 879 | 61,301 | 157 | 861 |
| H2.ZE67 | 62,337 | 58,393 | 3,944 | 18 | 1,407 | 58,374 | 2,556 | 1,388 |
| H2.ZE74 | 62,724 | 61,857 | 867 | 21 | 898 | 61,826 | 0 | 867 |
| H3.Z312 | 123,239 | 65,242 | 57,997 | 217 | 1,665 | 64,990 | 56,584 | 1,413 |
| H3.Z40 | 210,337 | 210,337 | 0 | 2,935 | 11,868 | 198,469 | 0 | 0 |
| H3.Z41 | 210,337 | 210,337 | 0 | 2,934 | 11,906 | 198,431 | 0 | 0 |
| H3.Z43 | 210,337 | 210,337 | 0 | 2,805 | 11,907 | 198,430 | 0 | 0 |
| H3.Z44 | 210,337 | 210,337 | 0 | 2,722 | 11,909 | 198,428 | 0 | 0 |
| H3.Z45 | 210,337 | 210,337 | 0 | 2,712 | 11,865 | 198,472 | 0 | 0 |
| H3.Z46 | 210,337 | 210,337 | 0 | 2,458 | 4,450 | 205,887 | 0 | 0 |
| H3.Z47 | 210,337 | 210,337 | 0 | 2,701 | 8,655 | 201,682 | 0 | 0 |
| H3.Z48 | 210,337 | 210,337 | 0 | 2,700 | 8,654 | 201,683 | 0 | 0 |
| H3.Z49 | 210,337 | 210,337 | 0 | 2,699 | 8,612 | 201,725 | 0 | 0 |
| H3.Z71 | 210,337 | 210,337 | 0 | 5,653 | 8,473 | 201,864 | 0 | 0 |
| H3.ZE40 | 62,743 | 60,661 | 2,082 | 13 | 2,102 | 60,641 | 0 | 2,082 |
| H3.ZE41 | 62,743 | 60,661 | 2,082 | 13 | 2,102 | 60,641 | 0 | 2,082 |
| H3.ZE43 | 62,743 | 60,574 | 2,169 | 14 | 2,104 | 60,554 | 85 | 2,084 |
| H3.ZE44 | 62,743 | 59,656 | 3,087 | 43 | 2,623 | 59,613 | 507 | 2,580 |
| H4.Z50 | 210,337 | 210,337 | 0 | 154 | 4,994 | 205,343 | 0 | 0 |
| H4.Z51 | 210,337 | 210,337 | 0 | 154 | 4,994 | 205,343 | 0 | 0 |
| H4.ZE50 | 62,350 | 61,492 | 858 | 14 | 880 | 61,470 | 0 | 858 |
| H4.ZE51 | 62,350 | 61,492 | 858 | 14 | 880 | 61,470 | 0 | 858 |
| V.K21 | 210,096 | 158,635 | 51,461 | 99 | 56,773 | 128,339 | 24,984 | 26,477 |
| V.Z81 | 210,336 | 206,414 | 3,922 | 1,881 | 7,643 | 202,693 | 0 | 3,922 |
| V.Z82 | 210,336 | 206,419 | 3,917 | 2,413 | 8,699 | 201,628 | 9 | 3,908 |
| V.Z84 | 158,116 | 156,153 | 1,963 | 535 | 2,706 | 155,399 | 11 | 1,952 |
| V.ZE84 | 38,716 | 30,995 | 7,721 | 17 | 891 | 30,975 | 6,850 | 871 |