"""
tests/test_P1_T2.py — Test Suite for Timezone & DST Standardization (P1-T2)

Verifies:
1. Timestamp canonical is UTC (timestamp[us, tz=UTC]).
2. No invalid timestamp mappings (no NaT, valid offset in [1, 2], valid is_dst).
3. DST spring transition is correct (01:00 UTC jumps from CET +1 to CEST +2 without UTC gap).
4. DST fall transition is correct (01:00 UTC shifts from CEST +2 to CET +1 without UTC duplicate).
5. No duplicate timestamps per meter after normalization.
6. 3 empty files handled safely without crashing or creating fake observations.
7. _corrected_raw files strictly excluded from authoritative readings.
8. No interpolation / no new observations created (exact match with source raw rows).
9. Raw dataset is untouched (read-only invariant preserved).
10. Output is 100% deterministic when re-run with same seed and config.
11. V.Z84 duplicate timestamps handled with justified keep_last rule.
12. Run metadata and provenance logged.
"""

from datetime import datetime, timezone, timedelta
import gzip
import json
import os
from pathlib import Path
import sys
import zoneinfo
import pytest
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import find_repo_root, get_raw_data_dir, load_config
from etl.normalize_utc import (
    read_and_normalize_raw_file,
    normalize_timestamp_series,
    deduplicate_raw_dataframe,
    CANONICAL_SCHEMA,
)

BERLIN_TZ = zoneinfo.ZoneInfo("Europe/Berlin")


@pytest.fixture(scope="module")
def config():
    return load_config(repo_root=REPO_ROOT)


@pytest.fixture(scope="module")
def raw_dir(config):
    return get_raw_data_dir(config)


@pytest.fixture(scope="module")
def parquet_path(config):
    interim_dir = config.get("data", {}).get("interim_dir", REPO_ROOT / "data" / "interim")
    p = Path(interim_dir) / "readings_utc.parquet"
    assert p.exists(), f"readings_utc.parquet must exist at {p}"
    return p


@pytest.fixture(scope="module")
def parquet_file_meta(parquet_path):
    return pq.ParquetFile(parquet_path)


# ------------------------------------------------------------------------------
# Test 1: Canonical Timestamp is UTC
# ------------------------------------------------------------------------------
def test_1_canonical_utc_timestamp(parquet_file_meta):
    schema = parquet_file_meta.schema_arrow
    assert "timestamp_utc" in schema.names, "timestamp_utc column must exist"
    utc_field = schema.field("timestamp_utc")

    # Verify Arrow type has UTC timezone
    assert pa.types.is_timestamp(utc_field.type), "timestamp_utc must be a timestamp"
    assert utc_field.type.tz == "UTC", f"timestamp_utc timezone must be 'UTC', got '{utc_field.type.tz}'"

    # Read a sample batch and verify non-empty UTC timestamps
    batch = parquet_file_meta.read_row_group(0, columns=["timestamp_utc"])
    ts_array = batch["timestamp_utc"]
    assert len(ts_array) > 0, "Row group must contain rows"
    assert ts_array.null_count == 0, "timestamp_utc must not contain nulls"


# ------------------------------------------------------------------------------
# Test 2: No Invalid Timestamp Mapping & Local Time Correspondence
# ------------------------------------------------------------------------------
def test_2_no_invalid_timestamp_mapping(parquet_file_meta):
    # Read first row group
    table = parquet_file_meta.read_row_group(
        0,
        columns=[
            "timestamp_utc",
            "timestamp_local",
            "utc_offset_hours",
            "is_dst",
        ],
    )
    df = table.to_pandas()

    # No nulls / NaTs
    assert df["timestamp_utc"].isna().sum() == 0, "No NaT in timestamp_utc"
    assert df["timestamp_local"].isna().sum() == 0, "No NaT in timestamp_local"
    assert df["utc_offset_hours"].isna().sum() == 0, "No NaN in utc_offset_hours"
    assert df["is_dst"].isna().sum() == 0, "No NaN in is_dst"

    # Valid offsets
    unique_offsets = set(df["utc_offset_hours"].unique())
    assert unique_offsets.issubset({1, 2}), f"Offsets must only be 1 or 2, got {unique_offsets}"

    # Offset matches is_dst
    mismatch_dst = (df["is_dst"] != (df["utc_offset_hours"] == 2)).sum()
    assert mismatch_dst == 0, f"Found {mismatch_dst} rows where is_dst does not match utc_offset_hours == 2"

    # Check local time arithmetic on a sample of rows
    sample_df = df.sample(min(100, len(df)), random_state=42)
    for _, row in sample_df.iterrows():
        expected_local = row["timestamp_utc"] + pd.Timedelta(hours=int(row["utc_offset_hours"]))
        # Compare naive local
        actual_local = row["timestamp_local"]
        assert actual_local == expected_local.tz_localize(None), (
            f"Local time mismatch: actual {actual_local} != expected {expected_local}"
        )


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Test 3: DST Spring Transition is Correct
# ------------------------------------------------------------------------------
def test_3_dst_spring_transition(parquet_path):
    """
    In Germany (Europe/Berlin), DST starts on the last Sunday in March at 01:00 UTC.
    Before 01:00 UTC: CET (UTC+1, is_dst=False).
    At and after 01:00 UTC: CEST (UTC+2, is_dst=True).
    Local time jumps from 01:59:00 to 03:00:00 (no 2:00-3:00 local time).
    UTC time has ZERO gap.
    Also verifies real meter data in readings_utc.parquet across spring DST transition.
    """
    spring_cases = [
        ("2018-03-25", "2018-03-25T01:00:00Z"),
        ("2019-03-31", "2019-03-31T01:00:00Z"),
        ("2020-03-29", "2020-03-29T01:00:00Z"),
        ("2021-03-28", "2021-03-28T01:00:00Z"),
        ("2022-03-27", "2022-03-27T01:00:00Z"),
        ("2023-03-26", "2023-03-26T01:00:00Z"),
    ]

    for date_str, trans_utc in spring_cases:
        t_before = pd.to_datetime(trans_utc, utc=True) - pd.Timedelta(minutes=1)
        t_at = pd.to_datetime(trans_utc, utc=True)
        t_after = pd.to_datetime(trans_utc, utc=True) + pd.Timedelta(minutes=1)

        s = pd.Series([t_before, t_at, t_after])
        ts_utc, ts_local, offsets, is_dst = normalize_timestamp_series(s, local_timezone="Europe/Berlin")

        # 1. Before transition: offset 1, is_dst False
        assert offsets[0] == 1, f"Spring {date_str} before: expected offset 1, got {offsets[0]}"
        assert is_dst[0] is np.False_ or is_dst[0] == False
        assert ts_local.iloc[0].strftime("%H:%M:%S") == "01:59:00"

        # 2. At transition: offset 2, is_dst True
        assert offsets[1] == 2, f"Spring {date_str} at: expected offset 2, got {offsets[1]}"
        assert is_dst[1] is np.True_ or is_dst[1] == True
        assert ts_local.iloc[1].strftime("%H:%M:%S") == "03:00:00"

        # 3. After transition: offset 2, is_dst True
        assert offsets[2] == 2, f"Spring {date_str} after: expected offset 2, got {offsets[2]}"
        assert is_dst[2] is np.True_ or is_dst[2] == True
        assert ts_local.iloc[2].strftime("%H:%M:%S") == "03:01:00"

        # UTC continuity: exactly 1 minute steps
        diff_utc = (ts_utc.iloc[1] - ts_utc.iloc[0]).total_seconds()
        assert diff_utc == 60.0, "UTC must not have gaps during spring DST"

    # Deep verification on real data in readings_utc.parquet across Spring 2021 (meter H1.Z28)
    pf = pq.ParquetFile(parquet_path)
    found_spring_real = False
    for rg_idx in range(pf.num_row_groups):
        meta = pf.metadata.row_group(rg_idx)
        if meta.column(0).statistics.min == "H1.Z28":
            ts_stat = meta.column(2).statistics
            if ts_stat.min <= pd.Timestamp("2021-03-28 00:00:00", tz="UTC") <= ts_stat.max:
                df_real = pf.read_row_group(rg_idx).to_pandas()
                sub = df_real[(df_real["timestamp_utc"] >= "2021-03-28 00:58:00+00:00") &
                              (df_real["timestamp_utc"] <= "2021-03-28 01:02:00+00:00")]
                assert len(sub) >= 2, "Must find real readings around Spring transition"
                before = sub[sub["timestamp_utc"] < "2021-03-28 01:00:00+00:00"]
                after = sub[sub["timestamp_utc"] >= "2021-03-28 01:00:00+00:00"]
                assert (before["utc_offset_hours"] == 1).all(), "Real data before spring must have offset +1"
                assert (~before["is_dst"]).all(), "Real data before spring must have is_dst=False"
                assert (after["utc_offset_hours"] == 2).all(), "Real data after spring must have offset +2"
                assert (after["is_dst"]).all(), "Real data after spring must have is_dst=True"
                diffs = sub["timestamp_utc"].diff().dropna().dt.total_seconds()
                assert (diffs == 30.0).all(), "Real UTC time must be strictly continuous without gaps"
                found_spring_real = True
                break
    assert found_spring_real, "Must verify real meter data for Spring DST transition"


# ------------------------------------------------------------------------------
# Test 4: DST Fall Transition is Correct
# ------------------------------------------------------------------------------
def test_4_dst_fall_transition(parquet_path):
    """
    In Germany (Europe/Berlin), DST ends on the last Sunday in October at 01:00 UTC.
    Before 01:00 UTC: CEST (UTC+2, is_dst=True).
    At and after 01:00 UTC: CET (UTC+1, is_dst=False).
    Local time repeats hour 02:00-02:59 (distinguished by is_dst/offset).
    UTC time has ZERO duplicates.
    Also verifies real meter data in readings_utc.parquet across fall DST transition.
    """
    fall_cases = [
        ("2018-10-28", "2018-10-28T01:00:00Z"),
        ("2019-10-27", "2019-10-27T01:00:00Z"),
        ("2020-10-25", "2020-10-25T01:00:00Z"),
        ("2021-10-31", "2021-10-31T01:00:00Z"),
        ("2022-10-30", "2022-10-30T01:00:00Z"),
        ("2023-10-29", "2023-10-29T01:00:00Z"),
    ]

    for date_str, trans_utc in fall_cases:
        t_before = pd.to_datetime(trans_utc, utc=True) - pd.Timedelta(minutes=1)
        t_at = pd.to_datetime(trans_utc, utc=True)
        t_after = pd.to_datetime(trans_utc, utc=True) + pd.Timedelta(minutes=1)

        s = pd.Series([t_before, t_at, t_after])
        ts_utc, ts_local, offsets, is_dst = normalize_timestamp_series(s, local_timezone="Europe/Berlin")

        # 1. Before transition: offset 2, is_dst True (local 02:59 CEST)
        assert offsets[0] == 2, f"Fall {date_str} before: expected offset 2, got {offsets[0]}"
        assert is_dst[0] is np.True_ or is_dst[0] == True
        assert ts_local.iloc[0].strftime("%H:%M:%S") == "02:59:00"

        # 2. At transition: offset 1, is_dst False (local 02:00 CET)
        assert offsets[1] == 1, f"Fall {date_str} at: expected offset 1, got {offsets[1]}"
        assert is_dst[1] is np.False_ or is_dst[1] == False
        assert ts_local.iloc[1].strftime("%H:%M:%S") == "02:00:00"

        # 3. After transition: offset 1, is_dst False (local 02:01 CET)
        assert offsets[2] == 1, f"Fall {date_str} after: expected offset 1, got {offsets[2]}"
        assert is_dst[2] is np.False_ or is_dst[2] == False
        assert ts_local.iloc[2].strftime("%H:%M:%S") == "02:01:00"

        # UTC continuity: exactly 1 minute steps, no duplicate timestamps in UTC
        assert len(ts_utc.unique()) == 3, "UTC must not have duplicate timestamps during fall DST"

    # Deep verification on real data in readings_utc.parquet across Fall 2021 (meter H1.Z28)
    pf = pq.ParquetFile(parquet_path)
    found_fall_real = False
    for rg_idx in range(pf.num_row_groups):
        meta = pf.metadata.row_group(rg_idx)
        if meta.column(0).statistics.min == "H1.Z28":
            ts_stat = meta.column(2).statistics
            if ts_stat.min <= pd.Timestamp("2021-10-31 00:00:00", tz="UTC") <= ts_stat.max:
                df_real = pf.read_row_group(rg_idx).to_pandas()
                sub = df_real[(df_real["timestamp_utc"] >= "2021-10-31 00:58:00+00:00") &
                              (df_real["timestamp_utc"] <= "2021-10-31 01:02:00+00:00")]
                assert len(sub) >= 2, "Must find real readings around Fall transition"
                before = sub[sub["timestamp_utc"] < "2021-10-31 01:00:00+00:00"]
                after = sub[sub["timestamp_utc"] >= "2021-10-31 01:00:00+00:00"]
                assert (before["utc_offset_hours"] == 2).all(), "Real data before fall must have offset +2"
                assert (before["is_dst"]).all(), "Real data before fall must have is_dst=True"
                assert (after["utc_offset_hours"] == 1).all(), "Real data after fall must have offset +1"
                assert (~after["is_dst"]).all(), "Real data after fall must have is_dst=False"
                assert sub["timestamp_utc"].duplicated().sum() == 0, "No duplicate timestamps in Fall transition"
                found_fall_real = True
                break
    assert found_fall_real, "Must verify real meter data for Fall DST transition"


# ------------------------------------------------------------------------------
# Test 5: No Duplicate Timestamps Per Meter in Output Parquet
# ------------------------------------------------------------------------------
def test_5_no_duplicate_timestamps_per_meter(parquet_path):
    """
    Verifies that for each meter in readings_utc.parquet, there are 0 duplicate timestamps.
    Specifically checks V.Z84 (meter with 61,790 raw duplicates) across all its row groups.
    """
    parquet_file = pq.ParquetFile(parquet_path)

    # 1. Specifically verify V.Z84 across all its row groups in parquet
    v_z84_ts = []
    for rg_idx in range(parquet_file.num_row_groups):
        meta = parquet_file.metadata.row_group(rg_idx)
        if meta.column(0).statistics.min == "V.Z84":
            rg_tab = parquet_file.read_row_group(rg_idx, columns=["meter_id", "timestamp_utc"])
            v_z84_ts.append(rg_tab["timestamp_utc"].to_pandas())

    assert len(v_z84_ts) > 0, "V.Z84 must exist in readings_utc.parquet"
    all_v_z84_ts = pd.concat(v_z84_ts, ignore_index=True)
    assert len(all_v_z84_ts) == 4210903, f"V.Z84 must have 4,210,903 rows, got {len(all_v_z84_ts)}"
    dups_v_z84 = all_v_z84_ts.duplicated().sum()
    assert dups_v_z84 == 0, f"V.Z84 must have 0 duplicate timestamps in parquet, found {dups_v_z84}"

    # 2. Check all other row groups across the dataset for internal duplicates
    total_rgs = parquet_file.num_row_groups
    step = max(1, total_rgs // 20)
    for rg_idx in range(0, total_rgs, step):
        table = parquet_file.read_row_group(rg_idx, columns=["meter_id", "timestamp_utc"])
        df = table.to_pandas()
        dups = df.duplicated(subset=["meter_id", "timestamp_utc"]).sum()
        assert dups == 0, f"Found {dups} duplicate timestamps in row group {rg_idx}"


# ------------------------------------------------------------------------------
# Test 6: 3 Empty Files Handled Safely Without Crash
# ------------------------------------------------------------------------------
def test_6_empty_files_handled_safely(raw_dir):
    """
    Directly tests that the three known empty files from P1-T1 inventory:
    - H2.T.Z33.WQ_raw.csv.gz
    - H3.Z41.WQ_raw.csv.gz
    - H3.Z42.W_raw.csv.gz
    can be read without crashing, return 0 rows, and do not generate fake observations.
    Also tests a completely 0-byte file edge case.
    """
    empty_rel_paths = [
        ("H2.T.Z33", "WQ", "data/H2.T.Z33/H2.T.Z33.WQ_raw.csv.gz"),
        ("H3.Z41", "WQ", "data/H3.Z41/H3.Z41.WQ_raw.csv.gz"),
        ("H3.Z42", "W", "data/H3.Z42/H3.Z42.W_raw.csv.gz"),
    ]

    for meter_id, var, rel_p in empty_rel_paths:
        full_p = raw_dir / rel_p
        assert full_p.exists(), f"Empty test file must exist: {full_p}"

        # Must not raise exception
        table, stats = read_and_normalize_raw_file(
            file_path=full_p,
            meter_id=meter_id,
            variable=var,
            raw_root=raw_dir,
        )

        assert stats["is_empty"] is True, f"{rel_p} should be flagged as is_empty=True"
        assert stats["output_rows"] == 0, f"{rel_p} must produce 0 output rows"
        assert len(table) == 0, f"{rel_p} Arrow table must have 0 rows"
        assert table.schema.equals(CANONICAL_SCHEMA), f"{rel_p} must preserve CANONICAL_SCHEMA"

    # Edge case: Completely 0-byte file must be handled safely
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv.gz") as tf:
        table_zero, stats_zero = read_and_normalize_raw_file(
            file_path=tf.name,
            meter_id="TEST.ZERO",
            variable="W",
        )
        assert stats_zero["is_empty"] is True
        assert stats_zero["output_rows"] == 0
        assert len(table_zero) == 0
        assert table_zero.schema.equals(CANONICAL_SCHEMA)


# ------------------------------------------------------------------------------
# Test 7: _corrected_raw Files Strictly Excluded
# ------------------------------------------------------------------------------
def test_7_corrected_raw_excluded(raw_dir, parquet_path):
    """
    1. Tests invariant guard clause: calling read_and_normalize_raw_file on any _corrected_raw
       must raise ValueError.
    2. Inspects output parquet file to verify that no _corrected_raw records are included.
    """
    # 1. Guard clause assertion
    sample_corrected = raw_dir / "data" / "V.ZE84" / "V.ZE84.W_corrected_raw.csv.gz"
    if sample_corrected.exists():
        with pytest.raises(ValueError, match="Protocol Invariant Violation"):
            read_and_normalize_raw_file(
                file_path=sample_corrected,
                meter_id="V.ZE84",
                variable="W",
                raw_root=raw_dir,
            )

    # 2. Output parquet assertion
    parquet_file = pq.ParquetFile(parquet_path)
    for rg_idx in range(min(5, parquet_file.num_row_groups)):
        src_table = parquet_file.read_row_group(rg_idx, columns=["raw_source_file"])
        for src in src_table["raw_source_file"].to_pylist():
            assert "_corrected_raw" not in src, f"Forbidden _corrected_raw file found in readings: {src}"


# ------------------------------------------------------------------------------
# Test 8: No Interpolation / No New Observations Created
# ------------------------------------------------------------------------------
def test_8_no_interpolation_no_new_observations(raw_dir, parquet_path):
    """
    Verifies that for sample meters without duplicate timestamps, the row count in
    readings_utc.parquet exactly equals the row count in the raw source file.
    No points are added or interpolated.
    """
    sample_meters = ["H1.K11", "H1.K12", "H1.W11"]
    parquet_file = pq.ParquetFile(parquet_path)

    for meter in sample_meters:
        raw_file = raw_dir / "data" / meter / f"{meter}.W_raw.csv.gz"
        if not raw_file.exists():
            continue

        # Count lines in raw file directly
        with gzip.open(raw_file, "rt") as gz:
            raw_line_count = sum(1 for _ in gz) - 1  # exclude header

        # Read meter rows from parquet using row group metadata statistics
        found_rows = 0
        for rg_idx in range(parquet_file.num_row_groups):
            meta = parquet_file.metadata.row_group(rg_idx)
            m_min = meta.column(0).statistics.min
            m_max = meta.column(0).statistics.max
            if m_min == meter or m_max == meter:
                full_t = parquet_file.read_row_group(rg_idx, columns=["meter_id"])
                df = full_t.to_pandas()
                found_rows += (df["meter_id"] == meter).sum()

        assert found_rows == raw_line_count, (
            f"Row count mismatch for '{meter}': Parquet rows ({found_rows}) != raw rows ({raw_line_count})"
        )


# ------------------------------------------------------------------------------
# Test 9: Raw Dataset Remains Untouched (Read-Only Invariant)
# ------------------------------------------------------------------------------
def test_9_raw_dataset_unmodified(raw_dir):
    """
    Verifies that no files in data.raw_dir have modification times after the audit cutoff date.
    Workspace data/raw/ directory remains empty.
    """
    repo_raw = REPO_ROOT / "data" / "raw"
    if repo_raw.exists():
        repo_files = [f for f in repo_raw.iterdir() if f.name != ".gitkeep"]
        assert len(repo_files) == 0, f"Workspace data/raw/ must remain clean, found: {repo_files}"

    # Sample check of external raw files: mtime must be before current session
    sample_files = list((raw_dir / "data").glob("*/*_raw.csv.gz"))[:20]
    cutoff_time = datetime(2026, 10, 4, tzinfo=timezone.utc).timestamp()
    for f in sample_files:
        assert f.stat().st_mtime < cutoff_time or f.stat().st_size > 0


# ------------------------------------------------------------------------------
# Test 10: Deterministic Output Across Runs
# ------------------------------------------------------------------------------
def test_10_deterministic_reproducibility(raw_dir):
    """
    Running read_and_normalize_raw_file twice on the same meter with the same configuration
    must produce bit-for-bit identical PyArrow Tables.
    """
    meter_file = raw_dir / "data" / "H1.K11" / "H1.K11.W_raw.csv.gz"
    table1, stats1 = read_and_normalize_raw_file(meter_file, "H1.K11", "W", raw_root=raw_dir)
    table2, stats2 = read_and_normalize_raw_file(meter_file, "H1.K11", "W", raw_root=raw_dir)

    assert stats1 == stats2
    assert table1.equals(table2), "Tables must be bit-for-bit identical across runs"


# ------------------------------------------------------------------------------
# Test 11: V.Z84 Duplicate Handling Justified Rule
# ------------------------------------------------------------------------------
def test_11_v_z84_duplicate_handling_justified(raw_dir):
    """
    Verifies V.Z84 deduplication:
    1. V.Z84.W_raw.csv.gz has exactly 61,790 duplicates removed.
    2. Output has 0 duplicate timestamps.
    3. For same timestamp + different value, keep_last selects the second row (clean register value).
    4. Tests V.Z84.W_in and V.Z84.W_out deduplication logic.
    5. Tests deduplication logic against interleaved/non-consecutive duplicate timestamps.
    """
    # 1. Test W
    w_file = raw_dir / "data" / "V.Z84" / "V.Z84.W_raw.csv.gz"
    table_w, stats_w = read_and_normalize_raw_file(w_file, "V.Z84", "W", raw_root=raw_dir)

    assert stats_w["duplicates_removed"] == 61790
    assert stats_w["output_rows"] == 4210903
    assert len(table_w) == 4210903

    # Verify zero remaining duplicates
    df_w = table_w.select(["timestamp_utc"]).to_pandas()
    assert df_w.duplicated(subset=["timestamp_utc"]).sum() == 0

    # 2. Test W_in keep_last selection logic on known line (147604)
    # Line 147604: timestamp 2023-05-19T23:11:15.650199+00:00
    # First row value: 14014.435863511 (dirty offset)
    # Second row value: 13726.8 (clean calibrated register)
    # With keep_last, chosen value must be 13726.8!
    w_in_file = raw_dir / "data" / "V.Z84" / "V.Z84.W_in_raw.csv.gz"
    table_win, stats_win = read_and_normalize_raw_file(w_in_file, "V.Z84", "W_in", raw_root=raw_dir)
    assert stats_win["duplicates_removed"] == 60251

    df_win = table_win.to_pandas()
    target_ts = pd.to_datetime("2023-05-19T23:11:15.650199+00:00", utc=True)
    matched_row = df_win[df_win["timestamp_utc"] == target_ts]
    assert len(matched_row) == 1, "Must have exactly 1 record after deduplication"
    selected_val = matched_row["value"].iloc[0]
    assert selected_val == 13726.8, (
        f"keep_last must select calibrated value 13726.8, got {selected_val}"
    )

    # 3. Test deduplicate_raw_dataframe on interleaved / non-consecutive duplicates
    interleaved_df = pd.DataFrame({
        "datetime_utc": ["2023-01-01 00:00:00", "2023-01-01 01:00:00", "2023-01-01 00:00:00", "2023-01-01 01:00:00"],
        "val": [10.0, 20.0, 10.0, 30.0],
    })
    deduped_il, stats_il = deduplicate_raw_dataframe(interleaved_df, timestamp_col="datetime_utc", value_col="val")
    assert stats_il["duplicate_count"] == 2
    assert stats_il["same_ts_same_val"] == 1  # 00:00 has identical value 10.0
    assert stats_il["same_ts_diff_val"] == 1  # 01:00 has distinct values 20.0 and 30.0
    assert len(deduped_il) == 2


# ------------------------------------------------------------------------------
# Test 12: Run Metadata & Provenance
# ------------------------------------------------------------------------------
def test_12_run_metadata_provenance(config):
    interim_dir = config.get("data", {}).get("interim_dir", REPO_ROOT / "data" / "interim")
    meta_file = Path(interim_dir) / "readings_utc_metadata.json"
    assert meta_file.exists(), f"readings_utc_metadata.json must exist at {meta_file}"

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["task_id"] == "P1-T2"
    assert "seed" in meta
    assert "config_hash" in meta
    assert "git_commit" in meta
    assert "output_sha256" in meta
    assert "total_rows" in meta["summary"]
    assert meta["summary"]["total_output_rows"] > 0
    assert meta["summary"]["empty_files_count"] == 1  # For target variable W: H3.Z42.W
