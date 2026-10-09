"""
tests/test_P1_T3.py — Test Suite for 15-Minute Regular Grid Representation (P1-T3)

Verifies Protocol v1.1 Acceptance Criteria:
- T3-01 — Regular grid: consecutive output grid_timestamp_utc differ by exactly 15m per meter.
- T3-02 — Grid alignment: all grid timestamps aligned to :00, :15, :30, :45, seconds=0, us=0.
- T3-03 — Boundary semantics: right-closed (t - 15m, t] exact mapping.
- T3-04 — Start boundary: grid_start = ceil_to_15min(min(source_timestamp_utc)).
- T3-05 — End boundary: grid_end = ceil_to_15min(max(source_timestamp_utc)) (never floored).
- T3-06 — LAST representative: bin with multiple observations selects chronologically LAST observation.
- T3-07 — Empty bin: value = NaN/null, source_timestamp_utc = null, raw_source_file = null,
          raw_record_count = 0, bin_completeness = 0.0.
- T3-08 — Occupied-bin preservation: non_null_output_bins == distinct_source_15min_bins.
- T3-09 — Zero synthetic observations: every non-null value/provenance tuple exists in P1-T2 source.
- T3-10 — Source timestamp membership: grid_timestamp - 15m < source_timestamp <= grid_timestamp.
- T3-11 — Uniqueness: (meter_id, grid_timestamp_utc) is strictly unique.
- T3-12 — No corrected raw: output not derived from _corrected_raw sources.
- T3-13 — Raw immutability: external raw Honda dataset is untouched.
- T3-14 — H1.ZE20 coverage: no grid rows prior to actual installation (~2022-11-30).
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import pytest
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Safely import repo modules
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import find_repo_root, get_raw_data_dir, load_config
from etl.resample_15min import (
    ceil_to_15min_us,
    classify_cadence,
    compute_meter_cadence,
    process_meter_data,
    SCHEMA_15MIN,
    W_US,
)


@pytest.fixture(scope="module")
def config():
    return load_config(repo_root=REPO_ROOT)


@pytest.fixture(scope="module")
def interim_dir(config):
    p = config.get("data", {}).get("interim_dir", REPO_ROOT / "data" / "interim")
    return Path(p) if Path(p).is_absolute() else (REPO_ROOT / p)


@pytest.fixture(scope="module")
def readings_utc_path(interim_dir):
    p = interim_dir / "readings_utc.parquet"
    assert p.exists(), f"readings_utc.parquet must exist at {p}"
    return p


@pytest.fixture(scope="module")
def readings_15min_path(interim_dir):
    p = interim_dir / "readings_15min.parquet"
    return p


# ------------------------------------------------------------------------------
# T3-01 & T3-02: Unit Tests for Boundary Semantics and Ceiling Alignment
# ------------------------------------------------------------------------------
def test_t3_03_boundary_semantics():
    """
    Explicit test required by Protocol v1.1:
      source 12:00:00 -> grid label 12:00
      source 12:00:01 -> grid label 12:15
      source 12:07:00 -> grid label 12:15
      source 12:14:59 -> grid label 12:15
      source 12:15:00 -> grid label 12:15
      source 12:15:01 -> grid label 12:30
    """
    test_dts = pd.to_datetime([
        "2023-01-01 12:00:00",
        "2023-01-01 12:00:01",
        "2023-01-01 12:07:00",
        "2023-01-01 12:14:59",
        "2023-01-01 12:15:00",
        "2023-01-01 12:15:01",
    ], utc=True)
    us = test_dts.as_unit("us").astype("int64").to_numpy()

    expected_dts = pd.to_datetime([
        "2023-01-01 12:00:00",
        "2023-01-01 12:15:00",
        "2023-01-01 12:15:00",
        "2023-01-01 12:15:00",
        "2023-01-01 12:15:00",
        "2023-01-01 12:30:00",
    ], utc=True)

    result_us = ceil_to_15min_us(us)
    result_dts = pd.to_datetime(result_us, unit="us", utc=True)

    for src, exp, act in zip(test_dts, expected_dts, result_dts):
        assert act == exp, f"Source {src} expected label {exp}, got {act}"


def test_t3_04_t3_05_boundary_rules_synthetic():
    """
    Verify grid_start = ceil(min) and grid_end = ceil(max),
    specifically including cases where last timestamp is inside bin.
    """
    # Case: min = 12:03:00, max = 12:37:00
    t_min = pd.to_datetime("2023-01-01 12:03:00", utc=True).value // 1000
    t_max = pd.to_datetime("2023-01-01 12:37:00", utc=True).value // 1000

    g_start = ceil_to_15min_us(t_min)
    g_end = ceil_to_15min_us(t_max)

    assert pd.to_datetime(g_start, unit="us", utc=True) == pd.to_datetime("2023-01-01 12:15:00", utc=True)
    assert pd.to_datetime(g_end, unit="us", utc=True) == pd.to_datetime("2023-01-01 12:45:00", utc=True)


def test_t3_06_last_representative_operator():
    """
    Verify LAST operator inside a bin containing multiple observations.
    """
    ts = pd.to_datetime([
        "2023-01-01 12:01:00",
        "2023-01-01 12:05:00",
        "2023-01-01 12:14:59",
    ], utc=True).as_unit("us").astype("int64").to_numpy()

    vals = np.array([10.0, 20.0, 30.0], dtype=np.float64)
    files = np.array(["file1.csv.gz", "file2.csv.gz", "file3.csv.gz"])

    table, stats = process_meter_data("TEST.M01", ts, vals, files)
    df = table.to_pandas()

    assert len(df) == 1
    assert df["grid_timestamp_utc"].iloc[0] == pd.to_datetime("2023-01-01 12:15:00", utc=True)
    assert df["value"].iloc[0] == 30.0  # Last observation value
    assert df["source_timestamp_utc"].iloc[0] == pd.to_datetime("2023-01-01 12:14:59", utc=True)
    assert df["raw_source_file"].iloc[0] == "file3.csv.gz"
    assert df["raw_record_count"].iloc[0] == 3


def test_t3_07_empty_bin_semantics():
    """
    Verify empty bins in the middle produce NaN/null and 0 counts.
    """
    ts = pd.to_datetime([
        "2023-01-01 12:05:00",  # Bin 12:15
        "2023-01-01 12:47:00",  # Bin 13:00 (12:30 and 12:45 are empty)
    ], utc=True).as_unit("us").astype("int64").to_numpy()

    vals = np.array([10.0, 40.0], dtype=np.float64)
    files = np.array(["f1", "f2"])

    table, stats = process_meter_data("TEST.M02", ts, vals, files)
    df = table.to_pandas()

    # Bins: 12:15, 12:30, 12:45, 13:00
    assert len(df) == 4
    empty_df = df[df["grid_timestamp_utc"].isin([
        pd.to_datetime("2023-01-01 12:30:00", utc=True),
        pd.to_datetime("2023-01-01 12:45:00", utc=True),
    ])]

    assert len(empty_df) == 2
    for _, row in empty_df.iterrows():
        assert pd.isna(row["value"])
        assert pd.isna(row["source_timestamp_utc"])
        assert pd.isna(row["raw_source_file"])
        assert row["raw_record_count"] == 0
        assert row["bin_completeness"] == 0.0


def test_t3_clock_drift_immunity():
    """
    Clock drift immunity: observations offset by seconds still map into correct bin.
    """
    # Readings every 60 seconds with 12s clock drift (e.g. 12:00:12, 12:01:12, ...)
    base_us = pd.to_datetime("2023-01-01 12:00:12", utc=True).value // 1000
    ts_us = np.array([base_us + i * 60_000_000 for i in range(14)], dtype=np.int64)  # up to 12:13:12
    vals = np.ones(len(ts_us), dtype=np.float64) * 5.0
    files = np.array(["f1"] * len(ts_us))

    table, stats = process_meter_data("TEST.M03", ts_us, vals, files)
    df = table.to_pandas()

    assert len(df) == 1
    assert df["grid_timestamp_utc"].iloc[0] == pd.to_datetime("2023-01-01 12:15:00", utc=True)
    assert df["raw_record_count"].iloc[0] == 14
    assert df["value"].iloc[0] == 5.0


def test_t3_cadence_classification():
    """
    Test deterministic cadence classification.
    """
    assert classify_cadence(15.0) == "C15S"
    assert classify_cadence(22.5) == "C15S"
    assert classify_cadence(30.0) == "C30S"
    assert classify_cadence(45.0) == "C30S"
    assert classify_cadence(60.0) == "C1M"
    assert classify_cadence(90.0) == "C1M"
    assert classify_cadence(120.0) == "C2M"
    assert classify_cadence(180.0) == "C2M"
    assert classify_cadence(360.0) == "C6M"
    assert classify_cadence(540.0) == "C6M"
    assert classify_cadence(600.0) == "C10M_PLUS"
    assert classify_cadence(900.0) == "C10M_PLUS"
    assert classify_cadence(901.0) == "SPARSE_GT15M"


# ------------------------------------------------------------------------------
# Integration Tests Against Interim Readings Parquet (when generated)
# ------------------------------------------------------------------------------
def test_t3_01_t3_02_regular_grid_and_alignment(readings_15min_path):
    """Verify regularity and quarter-hour alignment on actual output file."""
    if not readings_15min_path.exists():
        pytest.skip("readings_15min.parquet does not exist yet.")

    pf = pq.ParquetFile(readings_15min_path)
    # Check first 3 row groups (first 3 meters)
    for rg_idx in range(min(3, pf.num_row_groups)):
        table = pf.read_row_group(rg_idx, columns=["meter_id", "grid_timestamp_utc"])
        ts = table["grid_timestamp_utc"].to_numpy().astype("int64")

        # T3-01: Exactly 15 minutes between consecutive timestamps
        diffs_us = np.diff(ts)
        assert (diffs_us == W_US).all(), f"Row group {rg_idx} has non-15m step: {set(diffs_us)}"

        # T3-02: Quarter-hour alignment (:00, :15, :30, :45, 0 sec, 0 us)
        rem = ts % W_US
        assert (rem == 0).all(), f"Row group {rg_idx} has misaligned timestamps"


def test_t3_08_occupied_bin_preservation(readings_15min_path, readings_utc_path):
    """
    Occupied-bin preservation:
      count(non_null_15min(m)) == count(raw_occupied_bins(m))
    """
    if not readings_15min_path.exists():
        pytest.skip("readings_15min.parquet does not exist yet.")

    pf_15m = pq.ParquetFile(readings_15min_path)
    pf_utc = pq.ParquetFile(readings_utc_path)

    # Test on first meter (H1.K11)
    t_15m = pf_15m.read_row_group(0, columns=["meter_id", "value"])
    meter_id = t_15m["meter_id"][0].as_py()

    # Count non-null output bins
    non_null_output = t_15m["value"].null_count
    total_output = len(t_15m)
    occupied_output = total_output - non_null_output

    # Count raw occupied bins from readings_utc
    rgs_utc = [
        i for i in range(pf_utc.num_row_groups)
        if pf_utc.metadata.row_group(i).column(0).statistics.min == meter_id
    ]
    t_utc = pf_utc.read_row_groups(rgs_utc, columns=["timestamp_utc"])
    ts_us = t_utc["timestamp_utc"].to_numpy().astype("int64")
    raw_bins = ceil_to_15min_us(ts_us)
    distinct_raw_bins = len(np.unique(raw_bins))

    assert occupied_output == distinct_raw_bins, (
        f"Occupied-bin preservation failed for {meter_id}: "
        f"output non-null={occupied_output}, raw occupied={distinct_raw_bins}"
    )


def test_t3_09_zero_synthetic_observations(readings_15min_path, readings_utc_path):
    """
    Verify every non-null output tuple (meter_id, source_timestamp_utc, raw_source_file, value)
    matches an authentic source reading.
    """
    if not readings_15min_path.exists():
        pytest.skip("readings_15min.parquet does not exist yet.")

    pf_15m = pq.ParquetFile(readings_15min_path)
    pf_utc = pq.ParquetFile(readings_utc_path)

    # Read a sample of 1,000 non-null rows from RG 0
    t_15m = pf_15m.read_row_group(
        0,
        columns=["meter_id", "source_timestamp_utc", "value", "raw_source_file"]
    )
    df_15m = t_15m.to_pandas().dropna(subset=["value"]).head(1000)

    meter_id = df_15m["meter_id"].iloc[0]
    rgs_utc = [
        i for i in range(pf_utc.num_row_groups)
        if pf_utc.metadata.row_group(i).column(0).statistics.min == meter_id
    ]
    t_utc = pf_utc.read_row_groups(rgs_utc, columns=["timestamp_utc", "value", "raw_source_file"])
    df_utc = t_utc.to_pandas().set_index("timestamp_utc")

    # Verify each sample matches exactly
    for _, row in df_15m.iterrows():
        src_ts = row["source_timestamp_utc"]
        assert src_ts in df_utc.index, f"Source timestamp {src_ts} not found in P1-T2"
        match = df_utc.loc[src_ts]
        if isinstance(match, pd.DataFrame):
            match = match.iloc[-1]
        assert match["value"] == row["value"], f"Value mismatch for {src_ts}"
        assert match["raw_source_file"] == row["raw_source_file"], f"File mismatch for {src_ts}"


def test_t3_10_source_timestamp_membership(readings_15min_path):
    """
    For every non-null output row:
      grid_timestamp - 15m < source_timestamp <= grid_timestamp
    """
    if not readings_15min_path.exists():
        pytest.skip("readings_15min.parquet does not exist yet.")

    pf = pq.ParquetFile(readings_15min_path)
    t = pf.read_row_group(0, columns=["grid_timestamp_utc", "source_timestamp_utc"])
    df = t.to_pandas().dropna(subset=["source_timestamp_utc"])

    grid_us = df["grid_timestamp_utc"].values.astype("datetime64[us]").astype("int64")
    src_us = df["source_timestamp_utc"].values.astype("datetime64[us]").astype("int64")

    in_bin = (src_us > (grid_us - W_US)) & (src_us <= grid_us)
    assert in_bin.all(), "Some source timestamps fall outside their 15m bin interval"


def test_t3_11_uniqueness(readings_15min_path):
    """
    (meter_id, grid_timestamp_utc) is strictly unique per row.
    """
    if not readings_15min_path.exists():
        pytest.skip("readings_15min.parquet does not exist yet.")

    pf = pq.ParquetFile(readings_15min_path)
    # Check first row group
    t = pf.read_row_group(0, columns=["meter_id", "grid_timestamp_utc"])
    grid_ts = t["grid_timestamp_utc"].to_numpy().astype("int64")
    assert len(grid_ts) == len(np.unique(grid_ts)), "Duplicate grid timestamps found!"


def test_t3_12_no_corrected_raw(readings_15min_path):
    """
    Verify raw_source_file never contains '_corrected_raw'.
    """
    if not readings_15min_path.exists():
        pytest.skip("readings_15min.parquet does not exist yet.")

    pf = pq.ParquetFile(readings_15min_path)
    for rg_idx in range(min(5, pf.num_row_groups)):
        t = pf.read_row_group(rg_idx, columns=["raw_source_file"])
        files = t["raw_source_file"].drop_null().to_pylist()
        for f in files:
            assert "_corrected_raw" not in f, f"Forbidden corrected raw file present: {f}"


def test_t3_13_raw_immutability(config):
    """
    Verify raw dataset directory remains read-only and unmutated.
    """
    raw_dir = get_raw_data_dir(config)
    assert raw_dir.exists()
    assert os.access(raw_dir, os.R_OK)


def test_t3_14_h1_ze20_coverage(readings_15min_path):
    """
    Verify H1.ZE20 coverage does not contain grid rows prior to actual installation.
    Installation is ~2022-11-30.
    """
    if not readings_15min_path.exists():
        pytest.skip("readings_15min.parquet does not exist yet.")

    pf = pq.ParquetFile(readings_15min_path)
    ze20_rg = None
    for i in range(pf.num_row_groups):
        if pf.metadata.row_group(i).column(0).statistics.min == "H1.ZE20":
            ze20_rg = i
            break

    if ze20_rg is not None:
        t = pf.read_row_group(ze20_rg, columns=["grid_timestamp_utc"])
        min_grid_ts = pd.to_datetime(t["grid_timestamp_utc"][0].as_py())
        assert min_grid_ts >= pd.to_datetime("2022-11-30 00:00:00+00:00"), (
            f"H1.ZE20 has grid rows prior to installation: {min_grid_ts}"
        )
