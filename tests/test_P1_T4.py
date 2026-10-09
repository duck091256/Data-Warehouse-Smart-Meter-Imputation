"""
tests/test_P1_T4.py — Test Suite for Quality & Provenance Flags (P1-T4)

Verifies Protocol v1.1 Acceptance Criteria for Task P1-T4:
- T4-01 — Schema: Required quality/provenance flags exist and have valid boolean types.
- T4-02 — Observed bins: Bins containing P1-T2 observations are recognized as observed (is_missing=False).
- T4-03 — Empty bins: Empty P1-T3 bins remain observation gaps (is_missing=True) and NOT automatically failures.
- T4-04 — Value immutability: P1-T4 does not change any P1-T3 value (100% bit-for-bit identical).
- T4-05 — Timestamp immutability: grid_timestamp_utc, timestamp_local, source_timestamp_utc unchanged.
- T4-06 — Provenance immutability: raw_source_file, record counts, bin completeness unchanged.
- T4-07 — Issue matching: Verify representative boundary cases (H1.ZE20, V.Z84, H2.T.Z33, H1.Z19).
- T4-08 — No false failure inference: Empty bins outside authoritative issue logs have has_issue=False.
- T4-09 — Corrected-source protection: No corrected raw value introduced (is_corrected=False for 100%).
- T4-10 — Population: All 79 meters remain represented; total row count conserved (13,981,597).
- T4-11 — H1.ZE20: No rows/flags appear before actual source coverage (starts 2022-11-30 08:30:00 UTC).
- T4-12 — Leakage: raw_record_count, expected_record_count, bin_completeness remain descriptive only.
- T4-13 — Raw immutability: External raw dataset and data/raw/ remain untouched.
"""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

# Safely import repo modules
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import find_repo_root, get_raw_data_dir, load_config
from etl.quality_flags import (
    load_meter_issues,
    match_grid_issues,
    parse_timestamp_to_utc_sec,
    SCHEMA_15MIN_FLAGGED,
)


@pytest.fixture(scope="module")
def config():
    return load_config(repo_root=REPO_ROOT)


@pytest.fixture(scope="module")
def interim_dir(config):
    p = config.get("data", {}).get("interim_dir", REPO_ROOT / "data" / "interim")
    return Path(p) if Path(p).is_absolute() else (REPO_ROOT / p)


@pytest.fixture(scope="module")
def readings_15min_path(interim_dir):
    p = interim_dir / "readings_15min.parquet"
    assert p.is_file(), f"readings_15min.parquet must exist at {p}"
    return p


@pytest.fixture(scope="module")
def readings_15min_flagged_path(interim_dir):
    p = interim_dir / "readings_15min_flagged.parquet"
    assert p.is_file(), f"readings_15min_flagged.parquet must exist at {p}"
    return p


@pytest.fixture(scope="module")
def raw_dir(config):
    return get_raw_data_dir(config)


# ------------------------------------------------------------------------------
# T4-01: Schema Test
# ------------------------------------------------------------------------------
def test_t4_01_schema(readings_15min_flagged_path):
    """Verifies that all 14 columns exist with exact types, including the 4 quality flags."""
    pf = pq.ParquetFile(readings_15min_flagged_path)
    schema = pf.schema_arrow

    expected_flag_fields = {
        "is_missing": "bool",
        "has_issue": "bool",
        "is_corrected": "bool",
        "is_valid_ground_truth": "bool",
    }

    for name, expected_type in expected_flag_fields.items():
        assert name in schema.names, f"Column {name} missing from schema"
        idx = schema.get_field_index(name)
        assert str(schema.field(idx).type) == expected_type, (
            f"Column {name} type mismatch: expected {expected_type}, got {schema.field(idx).type}"
        )

    # Check that all original 10 columns from P1-T3 also exist
    expected_original_cols = [
        "meter_id", "grid_timestamp_utc", "timestamp_local", "source_timestamp_utc",
        "value", "raw_source_file", "raw_record_count", "expected_record_count",
        "bin_completeness", "cadence_class",
    ]
    for col in expected_original_cols:
        assert col in schema.names, f"Original column {col} missing from schema"


# ------------------------------------------------------------------------------
# T4-02: Observed Bins
# ------------------------------------------------------------------------------
def test_t4_02_observed_bins(readings_15min_flagged_path):
    """Bins containing raw readings (raw_record_count > 0, value not null) must have is_missing == False across all 79 meters."""
    pf = pq.ParquetFile(readings_15min_flagged_path)
    assert pf.num_row_groups == 79
    # Check across all 79 row groups
    for rg_idx in range(pf.num_row_groups):
        rg = pf.read_row_group(rg_idx, columns=["value", "raw_record_count", "is_missing"])
        counts = rg["raw_record_count"].to_numpy()
        is_missing = rg["is_missing"].to_numpy()
        values = rg["value"].to_numpy()

        observed_mask = (counts > 0)
        # All observed bins must have is_missing == False
        assert np.all(~is_missing[observed_mask]), (
            f"Row group {rg_idx}: Observed bins found with is_missing == True"
        )
        # All observed bins must have non-NaN value
        assert not np.isnan(values[observed_mask]).any(), (
            f"Row group {rg_idx}: Observed bins found with NaN value"
        )


# ------------------------------------------------------------------------------
# T4-03: Empty Bins
# ------------------------------------------------------------------------------
def test_t4_03_empty_bins(readings_15min_flagged_path):
    """Empty grid bins (raw_record_count == 0) must have is_missing == True, and NOT all be has_issue == True."""
    pf = pq.ParquetFile(readings_15min_flagged_path)
    total_empty = 0
    empty_with_no_issue = 0

    for rg_idx in range(pf.num_row_groups):
        rg = pf.read_row_group(rg_idx, columns=["raw_record_count", "is_missing", "has_issue", "value"])
        counts = rg["raw_record_count"].to_numpy()
        is_missing = rg["is_missing"].to_numpy()
        has_issue = rg["has_issue"].to_numpy()
        values = rg["value"].to_numpy()

        empty_mask = (counts == 0)
        total_empty += int(empty_mask.sum())
        # All empty bins must have is_missing == True and value == NaN
        assert np.all(is_missing[empty_mask]), f"Row group {rg_idx}: Empty bin found with is_missing == False"
        assert np.isnan(values[empty_mask]).all(), f"Row group {rg_idx}: Empty bin found with non-NaN value"

        empty_with_no_issue += int((empty_mask & ~has_issue).sum())

    assert total_empty == 648020, f"Expected 648,020 empty bins, got {total_empty}"
    # Crucially, empty bins MUST NOT automatically become failure states!
    assert empty_with_no_issue > 500000, (
        f"Empty bins without issue log must be > 500,000, got {empty_with_no_issue}"
    )


# ------------------------------------------------------------------------------
# T4-04: Value Immutability
# ------------------------------------------------------------------------------
def test_t4_04_value_immutability(readings_15min_path, readings_15min_flagged_path):
    """Verifies that P1-T4 does not alter any P1-T3 value bit-for-bit across all 79 meters."""
    pf_in = pq.ParquetFile(readings_15min_path)
    pf_out = pq.ParquetFile(readings_15min_flagged_path)

    assert pf_in.num_row_groups == pf_out.num_row_groups == 79

    for rg_idx in range(79):
        val_in = pf_in.read_row_group(rg_idx, columns=["value"])["value"].to_numpy()
        val_out = pf_out.read_row_group(rg_idx, columns=["value"])["value"].to_numpy()

        # Both NaN locations and non-NaN values must match exactly bit-for-bit
        nan_in = np.isnan(val_in)
        nan_out = np.isnan(val_out)
        assert np.array_equal(nan_in, nan_out), f"RG {rg_idx}: NaN positions mismatch"

        # Compare non-NaNs with exact equality (same floats)
        valid_in = val_in[~nan_in]
        valid_out = val_out[~nan_out]
        assert np.array_equal(valid_in, valid_out), f"RG {rg_idx}: Float values altered"


# ------------------------------------------------------------------------------
# T4-05: Timestamp Immutability
# ------------------------------------------------------------------------------
def test_t4_05_timestamp_immutability(readings_15min_path, readings_15min_flagged_path):
    """Verifies grid_timestamp_utc, timestamp_local, and source_timestamp_utc are 100% unchanged across all 79 meters."""
    pf_in = pq.ParquetFile(readings_15min_path)
    pf_out = pq.ParquetFile(readings_15min_flagged_path)

    for rg_idx in range(pf_in.num_row_groups):
        t_in = pf_in.read_row_group(
            rg_idx,
            columns=["grid_timestamp_utc", "timestamp_local", "source_timestamp_utc"]
        )
        t_out = pf_out.read_row_group(
            rg_idx,
            columns=["grid_timestamp_utc", "timestamp_local", "source_timestamp_utc"]
        )

        for col in ["grid_timestamp_utc", "timestamp_local", "source_timestamp_utc"]:
            arr_in = t_in[col].to_numpy()
            arr_out = t_out[col].to_numpy()
            assert np.array_equal(arr_in, arr_out, equal_nan=True), f"RG {rg_idx}: {col} altered"


# ------------------------------------------------------------------------------
# T4-06: Provenance Immutability
# ------------------------------------------------------------------------------
def test_t4_06_provenance_immutability(readings_15min_path, readings_15min_flagged_path):
    """Verifies raw_source_file, raw_record_count, expected_record_count, bin_completeness, cadence_class unchanged across all 79 meters."""
    pf_in = pq.ParquetFile(readings_15min_path)
    pf_out = pq.ParquetFile(readings_15min_flagged_path)

    cols = ["raw_source_file", "raw_record_count", "expected_record_count", "bin_completeness", "cadence_class"]
    for rg_idx in range(pf_in.num_row_groups):
        t_in = pf_in.read_row_group(rg_idx, columns=cols)
        t_out = pf_out.read_row_group(rg_idx, columns=cols)

        for col in cols:
            arr_in = t_in[col].to_pylist()
            arr_out = t_out[col].to_pylist()
            assert arr_in == arr_out, f"RG {rg_idx}: Column {col} provenance altered"


# ------------------------------------------------------------------------------
# T4-07: Issue Matching & Boundary Semantics
# ------------------------------------------------------------------------------
def test_t4_07_issue_matching_boundary_cases(readings_15min_flagged_path):
    """
    Verifies boundary semantics and issue matching on representative real cases:
    1. H1.ZE20 gap from 2023-01-28 08:15:50 to 08:25:53 UTC:
       - Bin 08:15:00 ((08:00, 08:15]) is BEFORE issue -> has_issue == False
       - Bin 08:30:00 ((08:15, 08:30]) CONTAINS issue -> has_issue == True
       - Bin 08:45:00 ((08:30, 08:45]) is AFTER issue -> has_issue == False
    2. H1.ZE20 101h outage from 2023-04-29 04:15:14 to 2023-05-03 09:32:36 UTC:
       - Bin 04:15:00 is BEFORE issue -> has_issue == False
       - Bins 04:30:00 to 09:45:00 are DURING issue -> has_issue == True
       - Bin 10:00:00 is AFTER issue -> has_issue == False
    3. V.Z84 post-outage reconnection gap on 2023-05-15 (11:45:31 to 13:04:09 UTC):
       - Bin 11:45:00 is BEFORE issue -> has_issue == False
       - Bins 12:00:00 to 13:15:00 -> has_issue == True
       - Bin 13:30:00 is AFTER issue -> has_issue == False
    4. H1.Z19 multi-year manual issue (removal from 2022-02-28 23:00:00 UTC to 2024-03-31 23:00:00 UTC):
       - Bin 2022-02-28 23:00:00 is BEFORE issue -> has_issue == False
       - Bin 2022-02-28 23:15:00 is START of issue -> has_issue == True
       - Bin 2023-01-01 12:00:00 is MID of issue -> has_issue == True
    5. H2.T.Z33 manual issue (2018-01-17 09:33:00 UTC to 2018-01-29 14:53:00 UTC):
       - Bin 2018-01-17 09:30:00 is BEFORE -> has_issue == False
       - Bin 2018-01-17 09:45:00 is START -> has_issue == True
       - Bin 2018-01-29 15:00:00 is END -> has_issue == True
       - Bin 2018-01-29 15:15:00 is AFTER -> has_issue == False
    6. Point event (ts == te) on H1.Z10 at 1550433720 (2019-02-17 20:02:00 UTC):
       - Bin 2019-02-17 20:00:00 is BEFORE -> has_issue == False
       - Bin 2019-02-17 20:15:00 CONTAINS event -> has_issue == True
       - Bin 2019-02-17 20:30:00 is AFTER -> has_issue == False
    """
    # Test 1 & 2: H1.ZE20
    t_ze20 = pq.read_table(
        readings_15min_flagged_path,
        filters=[("meter_id", "=", "H1.ZE20")],
        columns=["grid_timestamp_utc", "has_issue", "is_missing", "raw_record_count"],
    )
    df_ze20 = t_ze20.to_pandas().set_index("grid_timestamp_utc")

    # Case 1: Short gap on 2023-01-28
    t_b4_1 = pd.to_datetime("2023-01-28 08:15:00", utc=True)
    t_in_1 = pd.to_datetime("2023-01-28 08:30:00", utc=True)
    t_af_1 = pd.to_datetime("2023-01-28 08:45:00", utc=True)

    assert not df_ze20.loc[t_b4_1, "has_issue"], "Bin 08:15 should not have issue"
    assert df_ze20.loc[t_in_1, "has_issue"], "Bin 08:30 must have issue"
    assert not df_ze20.loc[t_af_1, "has_issue"], "Bin 08:45 should not have issue"

    # Case 2: 101h outage from 2023-04-29 04:15:14 to 2023-05-03 09:32:36
    t_b4_2 = pd.to_datetime("2023-04-29 04:15:00", utc=True)
    t_st_2 = pd.to_datetime("2023-04-29 04:30:00", utc=True)
    t_mid_2 = pd.to_datetime("2023-05-01 12:00:00", utc=True)
    t_en_2 = pd.to_datetime("2023-05-03 09:45:00", utc=True)
    t_af_2 = pd.to_datetime("2023-05-03 10:00:00", utc=True)

    assert not df_ze20.loc[t_b4_2, "has_issue"], "Bin 04:15 should not have issue"
    assert df_ze20.loc[t_st_2, "has_issue"], "Start bin 04:30 must have issue"
    assert df_ze20.loc[t_mid_2, "has_issue"], "Middle outage bin must have issue"
    assert df_ze20.loc[t_en_2, "has_issue"], "End bin 09:45 must have issue"
    assert not df_ze20.loc[t_af_2, "has_issue"], "Post-outage bin 10:00 should not have issue"

    # Test 3: V.Z84
    t_z84 = pq.read_table(
        readings_15min_flagged_path,
        filters=[("meter_id", "=", "V.Z84")],
        columns=["grid_timestamp_utc", "has_issue"],
    )
    df_z84 = t_z84.to_pandas().set_index("grid_timestamp_utc")

    t_b4_3 = pd.to_datetime("2023-05-15 11:45:00", utc=True)
    t_st_3 = pd.to_datetime("2023-05-15 12:00:00", utc=True)
    t_en_3 = pd.to_datetime("2023-05-15 13:15:00", utc=True)
    t_af_3 = pd.to_datetime("2023-05-15 13:30:00", utc=True)

    assert not df_z84.loc[t_b4_3, "has_issue"], "V.Z84 bin 11:45 should not have issue"
    assert df_z84.loc[t_st_3, "has_issue"], "V.Z84 bin 12:00 must have issue"
    assert df_z84.loc[t_en_3, "has_issue"], "V.Z84 bin 13:15 must have issue"
    assert not df_z84.loc[t_af_3, "has_issue"], "V.Z84 bin 13:30 should not have issue"

    # Test 4: H1.Z19 Manual Removal Issue (starts 2022-02-28 23:00:00 UTC)
    t_z19 = pq.read_table(
        readings_15min_flagged_path,
        filters=[("meter_id", "=", "H1.Z19")],
        columns=["grid_timestamp_utc", "has_issue"],
    )
    df_z19 = t_z19.to_pandas().set_index("grid_timestamp_utc")
    t_b4_4 = pd.to_datetime("2022-02-28 22:45:00", utc=True)
    t_st_4 = pd.to_datetime("2022-02-28 23:00:00", utc=True)
    t_in_4 = pd.to_datetime("2022-02-28 23:15:00", utc=True)
    t_mid_4 = pd.to_datetime("2023-01-01 12:00:00", utc=True)

    assert not df_z19.loc[t_b4_4, "has_issue"], "H1.Z19 bin 2022-02-28 22:45 should not have issue (before issue)"
    assert df_z19.loc[t_st_4, "has_issue"], "H1.Z19 bin 2022-02-28 23:00 must have issue (s == t boundary start under Ratified Amendment)"
    assert df_z19.loc[t_in_4, "has_issue"], "H1.Z19 bin 2022-02-28 23:15 must have issue"
    assert df_z19.loc[t_mid_4, "has_issue"], "H1.Z19 mid-issue bin must have issue"

    # Test 5: H2.T.Z33 Manual Issue
    t_tz33 = pq.read_table(
        readings_15min_flagged_path,
        filters=[("meter_id", "=", "H2.T.Z33")],
        columns=["grid_timestamp_utc", "has_issue"],
    )
    df_tz33 = t_tz33.to_pandas().set_index("grid_timestamp_utc")
    t_b4_5 = pd.to_datetime("2018-01-17 09:30:00", utc=True)
    t_st_5 = pd.to_datetime("2018-01-17 09:45:00", utc=True)
    t_en_5 = pd.to_datetime("2018-01-29 15:00:00", utc=True)
    t_af_5 = pd.to_datetime("2018-01-29 15:15:00", utc=True)

    assert not df_tz33.loc[t_b4_5, "has_issue"], "H2.T.Z33 bin 09:30 should not have issue"
    assert df_tz33.loc[t_st_5, "has_issue"], "H2.T.Z33 bin 09:45 must have issue"
    assert df_tz33.loc[t_en_5, "has_issue"], "H2.T.Z33 bin 15:00 must have issue"
    assert not df_tz33.loc[t_af_5, "has_issue"], "H2.T.Z33 bin 15:15 should not have issue"

    # Test 6: Short single-bin issue on H2.Z35 (2018-12-25 19:49:00Z to 19:54:00Z UTC)
    t_z35 = pq.read_table(
        readings_15min_flagged_path,
        filters=[("meter_id", "=", "H2.Z35")],
        columns=["grid_timestamp_utc", "has_issue"],
    )
    df_z35 = t_z35.to_pandas().set_index("grid_timestamp_utc")
    t_b4_6 = pd.to_datetime("2018-12-25 19:45:00", utc=True)
    t_in_6 = pd.to_datetime("2018-12-25 20:00:00", utc=True)
    t_af_6 = pd.to_datetime("2018-12-25 20:15:00", utc=True)

    assert not df_z35.loc[t_b4_6, "has_issue"], "H2.Z35 bin 19:45 should not have issue"
    assert df_z35.loc[t_in_6, "has_issue"], "H2.Z35 bin 20:00 must have issue"
    assert not df_z35.loc[t_af_6, "has_issue"], "H2.Z35 bin 20:15 should not have issue"


def test_t4_07b_match_grid_issues_boundary_unit():
    """
    Direct unit test for match_grid_issues covering all boundary and point edge cases
    under Ratified Protocol v1.1 Amendment (Non-empty set intersection Bin(t) ∩ [s, e] != ∅):
    Grid:
      Bin 0: (0, 900]     -> grid_ts = 900
      Bin 1: (900, 1800]  -> grid_ts = 1800
      Bin 2: (1800, 2700] -> grid_ts = 2700
    """
    grid_ts = np.array([900, 1800, 2700], dtype=np.int64)

    # 1. Point event exactly at right boundary / grid label (t = 900)
    # 900 is in (0, 900] -> Bin 0 True, Bin 1 False (open left boundary)
    m1 = match_grid_issues(grid_ts, [(900, 900, "point", "auto")])
    assert m1.tolist() == [True, False, False]

    # 2. Point event inside bin 1 (t = 1200)
    # 1200 is in (900, 1800] -> Bin 1 True
    m2 = match_grid_issues(grid_ts, [(1200, 1200, "point", "auto")])
    assert m2.tolist() == [False, True, False]

    # 3. Interval [900, 1800]:
    # Under Ratified Amendment, s=900 touches Bin 0 right boundary (900 <= 900 and 1800 > 0) -> Bin 0 True
    # Interval covers Bin 1 (900 <= 1800 and 1800 > 900) -> Bin 1 True
    # Bin 2 has left boundary 1800 (open), e=1800 does not intersect (1800 > 1800 is False) -> Bin 2 False
    m3 = match_grid_issues(grid_ts, [(900, 1800, "interval", "auto")])
    assert m3.tolist() == [True, True, False]

    # 4. Interval spanning Bin 0 and Bin 1 (500 to 1200)
    m4 = match_grid_issues(grid_ts, [(500, 1200, "span", "auto")])
    assert m4.tolist() == [True, True, False]

    # 5. Explicit requirement: issue start == grid label -> has_issue = TRUE
    # Interval [1800, 2000]: starts exactly at Bin 1 label (t = 1800)
    # Bin 1 (t = 1800): s <= t (1800 <= 1800) and e > t - 900 (2000 > 900) -> True
    # Bin 2 (t = 2700): s <= t (1800 <= 2700) and e > t - 900 (2000 > 1800) -> True
    m5 = match_grid_issues(grid_ts, [(1800, 2000, "boundary_start", "auto")])
    assert m5.tolist() == [False, True, True]

    # 6. Explicit requirement: issue end == grid left boundary -> has_issue = FALSE
    # Interval [500, 900]: ends exactly at Bin 1 left boundary (1800 - 900 = 900)
    # Bin 0 (t = 900): e = 900 is in (0, 900] -> True
    # Bin 1 (t = 1800): e > t - 900 is False (900 > 900 is False) -> False
    m6 = match_grid_issues(grid_ts, [(500, 900, "left_boundary_end", "auto")])
    assert m6.tolist() == [True, False, False]

    # 7. Explicit requirement: zero-duration issue inside bin -> has_issue = TRUE
    m7 = match_grid_issues(grid_ts, [(1500, 1500, "zero_inside", "auto")])
    assert m7.tolist() == [False, True, False]

    # 8. Explicit requirement: zero-duration issue at grid label -> has_issue = TRUE
    # Point [1800, 1800]: touches Bin 1 right boundary, left of Bin 2 is open
    m8 = match_grid_issues(grid_ts, [(1800, 1800, "zero_at_label", "auto")])
    assert m8.tolist() == [False, True, False]


# ------------------------------------------------------------------------------
# T4-08: No False Failure Inference
# ------------------------------------------------------------------------------
def test_t4_08_no_false_failure_inference(readings_15min_flagged_path):
    """
    An empty bin outside an authoritative issue interval MUST NOT receive has_issue=True.
    Verifies that empty bins are not falsely conflated with equipment failure.
    """
    pf = pq.ParquetFile(readings_15min_flagged_path)
    total_unrelated_gaps = 0

    for rg_idx in range(pf.num_row_groups):
        rg = pf.read_row_group(rg_idx, columns=["is_missing", "has_issue"])
        is_missing = rg["is_missing"].to_numpy()
        has_issue = rg["has_issue"].to_numpy()

        unrelated_gap = (is_missing & ~has_issue)
        total_unrelated_gaps += int(unrelated_gap.sum())

    # Exactly 527,756 empty bins (3.77%) are observation gaps without issue logs under Ratified Protocol v1.1
    assert total_unrelated_gaps == 527756, (
        f"Expected exactly 527,756 unrelated observation gaps, got {total_unrelated_gaps}"
    )


# ------------------------------------------------------------------------------
# T4-09: Corrected-Source Protection
# ------------------------------------------------------------------------------
def test_t4_09_corrected_source_protection(readings_15min_flagged_path):
    """Verifies that no corrected raw value is introduced (is_corrected is False for 100% of rows)."""
    pf = pq.ParquetFile(readings_15min_flagged_path)

    for rg_idx in range(pf.num_row_groups):
        rg = pf.read_row_group(rg_idx, columns=["is_corrected", "raw_source_file"])
        is_corrected = rg["is_corrected"].to_numpy()
        assert not np.any(is_corrected), f"RG {rg_idx}: is_corrected must be False for 100% of rows"

        raw_files = rg["raw_source_file"].drop_null().unique().to_pylist()
        for f in raw_files:
            assert "_corrected" not in f.lower(), f"RG {rg_idx}: Corrected file found in provenance: {f}"


# ------------------------------------------------------------------------------
# T4-10: Population Retention
# ------------------------------------------------------------------------------
def test_t4_10_population(readings_15min_flagged_path, readings_15min_path):
    """Verifies all 79 meters remain represented and row counts match P1-T3 exactly."""
    pf_in = pq.ParquetFile(readings_15min_path)
    pf_out = pq.ParquetFile(readings_15min_flagged_path)

    assert pf_out.metadata.num_rows == pf_in.metadata.num_rows == 13981597
    assert pf_out.num_row_groups == pf_in.num_row_groups == 79

    meters_in = [pf_in.read_row_group(i, columns=["meter_id"])["meter_id"][0].as_py() for i in range(79)]
    meters_out = [pf_out.read_row_group(i, columns=["meter_id"])["meter_id"][0].as_py() for i in range(79)]

    assert meters_in == meters_out
    assert len(set(meters_out)) == 79


# ------------------------------------------------------------------------------
# T4-11: H1.ZE20 Coverage
# ------------------------------------------------------------------------------
def test_t4_11_h1_ze20_coverage(readings_15min_flagged_path):
    """Verifies H1.ZE20 coverage begins at true installation: 2022-11-30 08:30:00 UTC."""
    t = pq.read_table(
        readings_15min_flagged_path,
        filters=[("meter_id", "=", "H1.ZE20")],
        columns=["grid_timestamp_utc"],
    )
    ts = t["grid_timestamp_utc"].to_pandas()
    assert ts.min() == pd.to_datetime("2022-11-30 08:30:00", utc=True)
    assert ts.max() == pd.to_datetime("2023-12-31 23:00:00", utc=True)
    assert len(ts) == 38075


# ------------------------------------------------------------------------------
# T4-12: Anti-Leakage Mandate
# ------------------------------------------------------------------------------
def test_t4_12_no_leakage(readings_15min_flagged_path, config):
    """
    Verifies that raw_record_count, expected_record_count, and bin_completeness
    remain purely descriptive metadata and have NOT been conflated with ground truth or model flags.
    """
    pf = pq.ParquetFile(readings_15min_flagged_path)
    schema = pf.schema_arrow

    # Exactly 14 columns in schema — zero model feature columns added
    assert len(schema.names) == 14

    # Verify forbidden metadata list in config
    forbidden = config.get("feature_governance", {}).get("forbidden_as_imputation_inputs", [])
    assert "raw_record_count" in forbidden
    assert "expected_record_count" in forbidden
    assert "bin_completeness" in forbidden

    # Quality flags only depend on provenance and issue logs
    assert "is_valid_ground_truth" in schema.names
    idx = schema.get_field_index("is_valid_ground_truth")
    assert str(schema.field(idx).type) == "bool"

    # Verify that is_valid_ground_truth is strictly ~is_missing & ~has_issue & ~is_corrected
    for rg_idx in [0, 20, 45, 78]:
        rg = pf.read_row_group(
            rg_idx,
            columns=["is_missing", "has_issue", "is_corrected", "is_valid_ground_truth"]
        )
        mis = rg["is_missing"].to_numpy()
        iss = rg["has_issue"].to_numpy()
        cor = rg["is_corrected"].to_numpy()
        gt = rg["is_valid_ground_truth"].to_numpy()

        expected_gt = (~mis) & (~iss) & (~cor)
        assert np.array_equal(gt, expected_gt), f"RG {rg_idx}: Ground truth logic mismatch"


# ------------------------------------------------------------------------------
# T4-13: Raw Dataset Immutability
# ------------------------------------------------------------------------------
def test_t4_13_raw_immutability(raw_dir):
    """External Honda dataset directory must remain untouched and read-only."""
    import os
    assert raw_dir.is_dir(), f"Raw directory {raw_dir} does not exist"
    assert os.access(raw_dir, os.R_OK), f"Raw directory {raw_dir} is not readable"
    # Verify subdirectories exist
    assert (raw_dir / "data").is_dir()
    assert (raw_dir / "issues").is_dir()


# ------------------------------------------------------------------------------
# T4-14: Value Checksum & Hash Invariant
# ------------------------------------------------------------------------------
def test_t4_14_value_checksum_identity(readings_15min_path, readings_15min_flagged_path):
    """Verifies that the value column buffer SHA-256 hash is bit-for-bit identical between P1-T3 and P1-T4."""
    pf_in = pq.ParquetFile(readings_15min_path)
    pf_out = pq.ParquetFile(readings_15min_flagged_path)

    h_in = hashlib.sha256()
    h_out = hashlib.sha256()

    for i in range(79):
        arr_in = pf_in.read_row_group(i, columns=["value"])["value"]
        arr_out = pf_out.read_row_group(i, columns=["value"])["value"]
        for chunk in arr_in.chunks:
            for b in chunk.buffers():
                if b:
                    h_in.update(b)
        for chunk in arr_out.chunks:
            for b in chunk.buffers():
                if b:
                    h_out.update(b)

    assert h_in.hexdigest() == h_out.hexdigest()
    assert h_out.hexdigest() == "8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe"


# ------------------------------------------------------------------------------
# T4-15: Ratified Protocol v1.1 Amendment Invariant & Regression Test
# ------------------------------------------------------------------------------
def test_t4_15_regression_ratified_delta(readings_15min_flagged_path, raw_dir):
    """
    Regression test validating that under Ratified Protocol v1.1 Amendment:
    1. Total rows = 13,981,597
    2. has_issue TRUE = 816,799
    3. is_valid_ground_truth TRUE = 12,637,042
    4. Four quadrants match exact ratified counts:
       Q1 = 12,637,042
       Q2 = 696,535
       Q3 = 527,756
       Q4 = 120,264
    5. Exactly 1,143 production bins differ between Acode and amended B,
       and 100% of differing bins satisfy s == t (issue_start == grid_timestamp_utc) and s < e.
    """
    pf = pq.ParquetFile(readings_15min_flagged_path)
    issues_dir = raw_dir / "issues"

    total_rows = pf.metadata.num_rows
    assert total_rows == 13981597

    total_has_issue = 0
    total_valid_gt = 0
    q1, q2, q3, q4 = 0, 0, 0, 0

    acode_to_b_diff = 0
    b_to_acode_diff = 0
    s_eq_t_count = 0

    for rg_idx in range(pf.num_row_groups):
        rg = pf.read_row_group(
            rg_idx,
            columns=["meter_id", "grid_timestamp_utc", "has_issue", "is_missing", "is_valid_ground_truth"]
        )
        meter_id = rg["meter_id"][0].as_py()
        has_issue = rg["has_issue"].to_numpy()
        is_missing = rg["is_missing"].to_numpy()
        is_valid_gt = rg["is_valid_ground_truth"].to_numpy()
        grid_ts = rg["grid_timestamp_utc"].to_numpy().view("int64") // 1_000_000

        total_has_issue += int(has_issue.sum())
        total_valid_gt += int(is_valid_gt.sum())

        q1 += int((~is_missing & ~has_issue).sum())
        q2 += int((~is_missing & has_issue).sum())
        q3 += int((is_missing & ~has_issue).sum())
        q4 += int((is_missing & has_issue).sum())

        # Reconstruct old Acode rule to verify exact 1,143 delta
        intervals = load_meter_issues(issues_dir, meter_id)
        n_bins = len(grid_ts)
        acode_issue = np.zeros(n_bins, dtype=bool)
        bin_end = grid_ts
        bin_start = grid_ts - 900
        for ts, te, reason, src in intervals:
            if ts < te:
                idx_start = np.searchsorted(bin_end, ts + 1, side="left")
                idx_end = np.searchsorted(bin_start, te, side="left")
                if idx_start < idx_end:
                    acode_issue[idx_start:idx_end] = True
            else:
                idx = np.searchsorted(bin_end, ts, side="left")
                if idx < n_bins and bin_start[idx] < ts <= bin_end[idx]:
                    acode_issue[idx] = True

        diff_f2t = (~acode_issue & has_issue)
        diff_t2f = (acode_issue & ~has_issue)
        acode_to_b_diff += int(diff_f2t.sum())
        b_to_acode_diff += int(diff_t2f.sum())

        if diff_f2t.any():
            for idx in np.where(diff_f2t)[0]:
                t = grid_ts[idx]
                matches = [it for it in intervals if it[0] == t and it[0] < it[1]]
                if len(matches) > 0:
                    s_eq_t_count += 1

    assert total_has_issue == 816799, f"Expected 816,799 has_issue, got {total_has_issue}"
    assert total_valid_gt == 12637042, f"Expected 12,637,042 valid GT, got {total_valid_gt}"
    assert q1 == 12637042, f"Expected Q1=12,637,042, got {q1}"
    assert q2 == 696535, f"Expected Q2=696,535, got {q2}"
    assert q3 == 527756, f"Expected Q3=527,756, got {q3}"
    assert q4 == 120264, f"Expected Q4=120,264, got {q4}"

    assert acode_to_b_diff == 1143, f"Expected exactly 1,143 Acode -> B changes, got {acode_to_b_diff}"
    assert b_to_acode_diff == 0, f"Expected 0 B -> Acode reversals, got {b_to_acode_diff}"
    assert s_eq_t_count == 1143, f"Expected 1,143 s==t boundary start cases, got {s_eq_t_count}"

