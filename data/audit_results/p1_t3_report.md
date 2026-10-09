# P1-T3 Audit Report — 15-Minute Regular Grid Representation

- **Task**: P1-T3 (Build 15-Minute Regular Grid)
- **Protocol Version**: v1.1 (Official)
- **Execution Timestamp (UTC)**: 2026-10-06T18:11:39.878987+00:00
- **Seed**: 42
- **Config Hash**: `d2d17337de0d0b2e0fe36b4430c5a34b063549ccb2dc78203ecb9bef2d8b843a`
- **Git Commit**: `uncommitted`
- **Execution Duration**: 32.19 s

## 1. File Artifacts & Provenance
- **Input File**: `/home/duck/Downloads/Vice - Download/StudyWithVKU/StudyWithVKU/ThirdYear/data-warehousing/data/interim/readings_utc.parquet`
- **Output File**: `/home/duck/Downloads/Vice - Download/StudyWithVKU/StudyWithVKU/ThirdYear/data-warehousing/data/interim/readings_15min.parquet`
- **Output File Size**: 394,072,801 bytes (375.82 MB)
- **Output SHA-256**: `f50a2ff27b142a895a8cabfbc0bcf3750aad28d5dcd5af2cb51a13628dce22dd`

## 2. Quantitative Summary
- **Total Meters**: 79 / 79 Core Population
- **Total Input Rows**: 208,224,479
- **Total Output Grid Rows**: 13,981,597
- **Total Occupied Bins**: 13,333,577
- **Total Empty Bins (NaN)**: 648,020 (4.63%)

## 3. Mandatory Protocol v1.1 Invariants
- **Invariant 1 — Strict 15-Minute Regularity**: [PASS] Consecutive grid timestamps differ by exactly 15 minutes (:00, :15, :30, :45).
- **Invariant 2 — Grid Boundary Rules**: [PASS] `grid_start = ceil_to_15min(min(t))` and `grid_end = ceil_to_15min(max(t))` per meter. Never floored.
- **Invariant 3 — Representative Operator LAST**: [PASS] Chronologically last observation selected inside each occupied bin.
- **Invariant 4 — Empty Bin Representation**: [PASS] Empty bins have `value = NaN`, `source_timestamp_utc = NULL`, `raw_source_file = NULL`, `raw_record_count = 0`, `bin_completeness = 0.0`.
- **Invariant 5 — Occupied-Bin Preservation**: [PASS] Every occupied source 15-minute bin maps to exactly one non-null grid row across 100% of meters.
- **Invariant 6 — Zero Synthetic Observations**: [PASS] Every non-null value matches authentic P1-T2 observation.
- **Invariant 7 — Uniqueness**: [PASS] (meter_id, grid_timestamp_utc) is strictly unique.
- **Invariant 8 — Corrected Raw Exclusion**: [PASS] Input derived solely from authoritative P1-T2 readings without `_corrected_raw`.
- **Invariant 9 — External Raw Immutability**: [PASS] `data/raw/` untouched.
- **Invariant 10 — H1.ZE20 Temporal Coverage**: [PASS] Grid begins at true installation (2022-11-30 08:30:00 UTC); no pre-installation rows.

## 4. Cadence Classification Distribution
| Cadence Class | Thresholds | Meter Count | Percentage |
|---|---|---|---|
| C15S | <= 22.5s | 1 | 1.3% |
| C30S | > 22.5s - 45s | 25 | 31.6% |
| C1M | > 45s - 90s | 44 | 55.7% |
| C2M | > 90s - 180s | 1 | 1.3% |
| C6M | > 180s - 540s | 8 | 10.1% |
| C10M_PLUS | > 540s - 900s | 0 | 0.0% |
| SPARSE_GT15M | > 900s | 0 | 0.0% |

## 5. Schema Specification
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

## 6. Per-Meter Coverage Summary (All 79 Core Meters)
| Meter ID | Cadence | Source Min | Source Max | Grid Start | Grid End | Grid Rows | Occupied | Empty | Occupied Preservation |
|---|---|---|---|---|---|---|---|---|---|
| H1.K11 | C6M | 2018-01-04T11:30 | 2023-12-31T22:54 | 2018-01-04T11:30 | 2023-12-31T23:00 | 209,999 | 156,082 | 53,917 | PASS |
| H1.K12 | C6M | 2018-01-03T21:55 | 2023-12-31T22:54 | 2018-01-03T22:00 | 2023-12-31T23:00 | 210,053 | 156,667 | 53,386 | PASS |
| H1.K14 | C6M | 2018-01-03T12:36 | 2023-12-31T22:54 | 2018-01-03T12:45 | 2023-12-31T23:00 | 210,090 | 157,411 | 52,679 | PASS |
| H1.K15 | C6M | 2018-01-03T10:39 | 2023-12-31T22:54 | 2018-01-03T10:45 | 2023-12-31T23:00 | 210,098 | 162,943 | 47,155 | PASS |
| H1.K16 | C6M | 2018-11-26T10:06 | 2023-12-31T22:54 | 2018-11-26T10:15 | 2023-12-31T23:00 | 178,708 | 156,607 | 22,101 | PASS |
| H1.W11 | C6M | 2017-12-31T23:11 | 2023-12-31T22:54 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 185,064 | 25,272 | PASS |
| H1.W12 | C2M | 2017-12-31T23:16 | 2023-12-31T22:58 | 2017-12-31T23:30 | 2023-12-31T23:00 | 210,335 | 178,874 | 31,461 | PASS |
| H1.Z10 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z11 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z12 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z13 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z14 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z15 | C30S | 2017-12-31T23:00 | 2023-12-31T22:59 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 206,846 | 3,490 | PASS |
| H1.Z16 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z17 | C30S | 2017-12-31T23:00 | 2023-12-31T22:59 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 206,834 | 3,502 | PASS |
| H1.Z18 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z19 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z20 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z21 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z22 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H1.Z23 | C1M | 2018-01-22T16:57 | 2023-12-31T22:42 | 2018-01-22T17:00 | 2023-12-31T22:45 | 208,248 | 208,248 | 0 | PASS |
| H1.Z24 | C1M | 2018-01-22T16:57 | 2023-12-31T22:42 | 2018-01-22T17:00 | 2023-12-31T22:45 | 208,248 | 208,248 | 0 | PASS |
| H1.Z25 | C1M | 2018-01-22T16:57 | 2023-12-31T22:42 | 2018-01-22T17:00 | 2023-12-31T22:45 | 208,248 | 208,248 | 0 | PASS |
| H1.Z26 | C30S | 2017-12-31T23:47 | 2023-12-31T22:59 | 2018-01-01T00:00 | 2023-12-31T23:00 | 210,333 | 204,269 | 6,064 | PASS |
| H1.Z27 | C1M | 2017-12-31T23:00 | 2023-12-31T22:58 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 204,442 | 5,894 | PASS |
| H1.Z28 | C30S | 2017-12-31T23:00 | 2023-12-31T22:59 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 206,839 | 3,497 | PASS |
| H1.Z29 | C30S | 2017-12-31T23:00 | 2023-12-31T22:59 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 203,456 | 6,880 | PASS |
| H1.Z310 | C30S | 2020-06-25T22:00 | 2023-12-31T15:14 | 2020-06-25T22:15 | 2023-12-31T15:15 | 123,237 | 68,355 | 54,882 | PASS |
| H1.ZE20 | C30S | 2022-11-30T08:18 | 2023-12-31T22:59 | 2022-11-30T08:30 | 2023-12-31T23:00 | 38,075 | 27,980 | 10,095 | PASS |
| H2.K21 | C6M | 2018-01-03T18:03 | 2023-12-31T22:55 | 2018-01-03T18:15 | 2023-12-31T23:00 | 210,068 | 149,169 | 60,899 | PASS |
| H2.T.Z30 | C1M | 2018-11-10T06:57 | 2023-12-31T22:42 | 2018-11-10T07:00 | 2023-12-31T22:45 | 180,256 | 180,256 | 0 | PASS |
| H2.T.Z31 | C1M | 2018-11-10T06:57 | 2023-12-31T22:42 | 2018-11-10T07:00 | 2023-12-31T22:45 | 180,256 | 180,256 | 0 | PASS |
| H2.T.Z32 | C1M | 2018-11-10T06:57 | 2023-12-31T22:42 | 2018-11-10T07:00 | 2023-12-31T22:45 | 180,256 | 180,256 | 0 | PASS |
| H2.T.Z33 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.T.Z34 | C1M | 2018-11-10T06:57 | 2023-12-31T22:42 | 2018-11-10T07:00 | 2023-12-31T22:45 | 180,256 | 180,256 | 0 | PASS |
| H2.Z311 | C30S | 2020-06-24T22:00 | 2023-12-31T15:14 | 2020-06-24T22:15 | 2023-12-31T15:15 | 123,333 | 64,538 | 58,795 | PASS |
| H2.Z35 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z351 | C30S | 2020-09-15T10:00 | 2023-12-31T22:59 | 2020-09-15T10:15 | 2023-12-31T23:00 | 115,444 | 114,207 | 1,237 | PASS |
| H2.Z36 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z361 | C30S | 2020-09-15T10:00 | 2023-12-31T22:59 | 2020-09-15T10:15 | 2023-12-31T23:00 | 115,444 | 114,203 | 1,241 | PASS |
| H2.Z61 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z62 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z63 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z64 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z65 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z66 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z67 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z68 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z69 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.Z70 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H2.ZE64 | C30S | 2022-03-22T14:54 | 2023-12-31T22:59 | 2022-03-22T15:00 | 2023-12-31T23:00 | 62,337 | 61,479 | 858 | PASS |
| H2.ZE65 | C30S | 2022-03-22T14:54 | 2023-12-09T21:08 | 2022-03-22T15:00 | 2023-12-09T21:15 | 60,218 | 59,449 | 769 | PASS |
| H2.ZE66 | C30S | 2022-03-22T14:54 | 2023-12-31T22:59 | 2022-03-22T15:00 | 2023-12-31T23:00 | 62,337 | 61,319 | 1,018 | PASS |
| H2.ZE67 | C30S | 2022-03-22T14:54 | 2023-12-31T22:55 | 2022-03-22T15:00 | 2023-12-31T23:00 | 62,337 | 58,393 | 3,944 | PASS |
| H2.ZE74 | C30S | 2022-03-18T14:02 | 2023-12-31T22:59 | 2022-03-18T14:15 | 2023-12-31T23:00 | 62,724 | 61,857 | 867 | PASS |
| H3.Z312 | C30S | 2020-06-25T22:00 | 2023-12-31T15:17 | 2020-06-25T22:00 | 2023-12-31T15:30 | 123,239 | 65,242 | 57,997 | PASS |
| H3.Z40 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z41 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z43 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z44 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z45 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z46 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z47 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z48 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z49 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.Z71 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H3.ZE40 | C30S | 2022-03-18T09:24 | 2023-12-31T22:59 | 2022-03-18T09:30 | 2023-12-31T23:00 | 62,743 | 60,661 | 2,082 | PASS |
| H3.ZE41 | C30S | 2022-03-18T09:24 | 2023-12-31T22:59 | 2022-03-18T09:30 | 2023-12-31T23:00 | 62,743 | 60,661 | 2,082 | PASS |
| H3.ZE43 | C30S | 2022-03-18T09:24 | 2023-12-31T22:59 | 2022-03-18T09:30 | 2023-12-31T23:00 | 62,743 | 60,574 | 2,169 | PASS |
| H3.ZE44 | C30S | 2022-03-18T09:24 | 2023-12-31T22:59 | 2022-03-18T09:30 | 2023-12-31T23:00 | 62,743 | 59,656 | 3,087 | PASS |
| H4.Z50 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H4.Z51 | C1M | 2018-01-01T00:00 | 2024-01-01T00:00 | 2018-01-01T00:00 | 2024-01-01T00:00 | 210,337 | 210,337 | 0 | PASS |
| H4.ZE50 | C30S | 2022-03-22T11:37 | 2023-12-31T22:59 | 2022-03-22T11:45 | 2023-12-31T23:00 | 62,350 | 61,492 | 858 | PASS |
| H4.ZE51 | C30S | 2022-03-22T11:37 | 2023-12-31T22:59 | 2022-03-22T11:45 | 2023-12-31T23:00 | 62,350 | 61,492 | 858 | PASS |
| V.K21 | C6M | 2018-01-03T11:03 | 2023-12-31T22:54 | 2018-01-03T11:15 | 2023-12-31T23:00 | 210,096 | 158,635 | 51,461 | PASS |
| V.Z81 | C30S | 2017-12-31T23:00 | 2023-12-31T22:59 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 206,414 | 3,922 | PASS |
| V.Z82 | C30S | 2017-12-31T23:00 | 2023-12-31T22:59 | 2017-12-31T23:15 | 2023-12-31T23:00 | 210,336 | 206,419 | 3,917 | PASS |
| V.Z84 | C15S | 2019-06-28T22:00 | 2023-12-31T22:59 | 2019-06-28T22:15 | 2023-12-31T23:00 | 158,116 | 156,153 | 1,963 | PASS |
| V.ZE84 | C30S | 2022-11-23T15:57 | 2023-12-31T22:40 | 2022-11-23T16:00 | 2023-12-31T22:45 | 38,716 | 30,995 | 7,721 | PASS |

## 7. Tests Executed
The following 14 Protocol v1.1 acceptance tests were executed via pytest and verified 100% PASS:
- **T3-01 — Regular grid**: [PASS] Consecutive grid timestamps differ by exactly 15 minutes (:00, :15, :30, :45).
- **T3-02 — Grid alignment**: [PASS] All grid timestamps aligned to quarter hours with seconds=0, microseconds=0.
- **T3-03 — Boundary semantics**: [PASS] Explicit boundary mappings verified: `12:00:00 -> 12:00`, `12:00:01 -> 12:15`, `12:14:59 -> 12:15`, `12:15:00 -> 12:15`, `12:15:01 -> 12:30`.
- **T3-04 — Start boundary**: [PASS] `grid_start = ceil_to_15min(min(source_timestamp_utc))` verified.
- **T3-05 — End boundary**: [PASS] `grid_end = ceil_to_15min(max(source_timestamp_utc))` verified; never floored.
- **T3-06 — LAST representative**: [PASS] Chronologically last observation selected within each occupied bin.
- **T3-07 — Empty bin semantics**: [PASS] Empty bins produce `value = NaN`, `source_timestamp_utc = NULL`, `raw_source_file = NULL`, `raw_record_count = 0`, `bin_completeness = 0.0`.
- **T3-08 — Occupied-bin preservation**: [PASS] `output_non_null_bin_count == source_distinct_15min_bin_count` holds across all 79 meters (0 mismatches).
- **T3-09 — Zero synthetic observations**: [PASS] Every non-null `(meter_id, source_timestamp_utc, raw_source_file, value)` matches source bit-for-bit.
- **T3-10 — Source timestamp membership**: [PASS] `grid_timestamp - 15m < source_timestamp <= grid_timestamp` verified across all rows.
- **T3-11 — Key uniqueness**: [PASS] `(meter_id, grid_timestamp_utc)` is strictly unique across all 13,981,597 grid rows.
- **T3-12 — No corrected raw**: [PASS] No records or filenames contain `_corrected_raw`.
- **T3-13 — Raw immutability**: [PASS] External raw Honda dataset directory remains untouched and read-only.
- **T3-14 — H1.ZE20 coverage**: [PASS] Grid begins at true deployment (2022-11-30 08:30:00 UTC); no pre-installation rows.

## 8. Performance & Runtime Observations
- **Processing Engine**: PyArrow streaming row groups with bounded memory per meter.
- **Total Duration**: 32.19 seconds (~6,468,608 raw rows/sec).
- **Peak RSS Memory**: Under 300 MB (constant memory footprint across all 208M raw rows).
- **Parquet Storage**: 375.82 MB snappy-compressed columnar layout across 79 row groups (1 row group per meter).

## 9. Deviations or Notes
- **Protocol Deviations**: None. Full conformance with Protocol v1.1.
- **Observation Gaps vs Equipment Failure**: Empty bins (4.63%) represent observation gaps on the regular grid; equipment failure semantics are established later in P1-T4 and P2 using issue logs.
- **Anti-Leakage Restriction**: Fields `raw_record_count`, `expected_record_count`, and `bin_completeness` are descriptive metadata and must NEVER be used as input features for imputation models.
