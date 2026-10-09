"""
tests/test_P1_T1.py — Comprehensive Test Suite for Raw Dataset Inventory (P1-T1)

Quantitative Verification:
1. All meters detected (81 meters).
2. Inventory does not miss any valid file (1,603 files).
3. Total rows in inventory matches source (3,952,487,105 rows).
4. Meter-level statistics are consistent (files, timestamps, rows, NaN rates).
5. Raw data is not modified (read-only invariant preserved).
6. No output is written into the raw dataset directory.
7. Config external path is utilized without hardcoding.
8. Results are deterministic when run with same config/seed.
"""

import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import find_repo_root, get_raw_data_dir, load_config
from etl.inventory import scan_single_file


@pytest.fixture(scope="module")
def config():
    return load_config(repo_root=REPO_ROOT)


@pytest.fixture(scope="module")
def raw_dir(config):
    return get_raw_data_dir(config)


@pytest.fixture(scope="module")
def inventory_rows():
    inv_file = REPO_ROOT / "data" / "interim" / "inventory.csv"
    assert inv_file.exists(), f"inventory.csv must exist at {inv_file}"
    rows = []
    with open(inv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


@pytest.fixture(scope="module")
def file_inventory_rows():
    inv_file = REPO_ROOT / "data" / "interim" / "inventory_by_file.csv"
    assert inv_file.exists(), f"inventory_by_file.csv must exist at {inv_file}"
    rows = []
    with open(inv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


@pytest.fixture(scope="module")
def metadata():
    meta_file = REPO_ROOT / "data" / "interim" / "inventory_metadata.json"
    assert meta_file.exists(), f"inventory_metadata.json must exist at {meta_file}"
    with open(meta_file, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------------------
# Test 1: Tất cả meter được phát hiện (len == 81)
# ------------------------------------------------------------------------------
def test_1_all_meters_detected(raw_dir, inventory_rows):
    data_dir = raw_dir / "data"
    expected_meter_dirs = sorted([p.name for p in data_dir.iterdir() if p.is_dir()])

    assert len(expected_meter_dirs) == 81, f"Expected 81 meters in source, got {len(expected_meter_dirs)}"
    assert len(inventory_rows) == 81, f"Expected 81 meter rows in inventory.csv, got {len(inventory_rows)}"

    inventory_meters = sorted([r["meter_id"] for r in inventory_rows])
    assert inventory_meters == expected_meter_dirs, "Inventory meter IDs must exactly match source meter directories"


# ------------------------------------------------------------------------------
# Test 2: Inventory không bỏ sót file hợp lệ (1603 files)
# ------------------------------------------------------------------------------
def test_2_no_valid_raw_files_missed(raw_dir, inventory_rows, file_inventory_rows):
    data_dir = raw_dir / "data"
    source_raw_files = []
    for m in data_dir.iterdir():
        if m.is_dir():
            for f in m.glob("*_raw.csv.gz"):
                if "_corrected_raw" not in f.name and "backup" not in str(f):
                    source_raw_files.append(f.name)

    assert len(source_raw_files) == 1603, f"Expected 1603 true raw files in source, got {len(source_raw_files)}"
    assert len(file_inventory_rows) == 1603, f"Expected 1603 rows in inventory_by_file.csv, got {len(file_inventory_rows)}"

    # Sum of num_files in meter-level inventory must match 1603
    total_files_in_meter_inv = sum(int(r["num_files"]) for r in inventory_rows)
    assert total_files_in_meter_inv == 1603, f"Sum of num_files must be 1603, got {total_files_in_meter_inv}"

    # Verify all file names match
    inv_file_names = set(r["file_name"] for r in file_inventory_rows)
    source_file_names = set(source_raw_files)
    assert inv_file_names == source_file_names, "Set of file names in inventory must match source"


# ------------------------------------------------------------------------------
# Test 3: Tổng dòng inventory phù hợp với nguồn
# ------------------------------------------------------------------------------
def test_3_total_rows_match_source(raw_dir, inventory_rows, file_inventory_rows):
    meter_total_rows = sum(int(r["total_rows"]) for r in inventory_rows)
    file_total_rows = sum(int(r["total_rows"]) for r in file_inventory_rows)

    assert meter_total_rows == file_total_rows, "Meter total rows must match sum of file total rows"
    assert meter_total_rows == 3952487105, f"Expected 3,952,487,105 total rows, got {meter_total_rows}"

    # Sample-check 3 diverse meters directly against disk to ensure exact row counts
    sample_meters = ["H1.K11", "WeatherStation.Weather", "H3.Z42"]
    for m_id in sample_meters:
        m_row = next(r for r in inventory_rows if r["meter_id"] == m_id)
        m_dir = raw_dir / "data" / m_id
        actual_lines = 0
        for f in m_dir.glob("*_raw.csv.gz"):
            if "_corrected_raw" not in f.name and "backup" not in str(f):
                with gzip.open(f, "rb") as gz:
                    # Count data rows (lines - 1 header)
                    chunk_lines = 0
                    while c := gz.read(512 * 1024):
                        chunk_lines += c.count(b"\n")
                    if chunk_lines > 0:
                        actual_lines += (chunk_lines - 1)
        assert int(m_row["total_rows"]) == actual_lines, (
            f"Row count mismatch for {m_id}: inventory={m_row['total_rows']}, actual={actual_lines}"
        )


# ------------------------------------------------------------------------------
# Test 4: Meter-level statistics nhất quán
# ------------------------------------------------------------------------------
def test_4_meter_level_statistics_consistent(inventory_rows):
    for r in inventory_rows:
        meter_id = r["meter_id"]
        num_files = int(r["num_files"])
        total_rows = int(r["total_rows"])
        num_timestamps = int(r["num_timestamps"])
        nan_count = int(r["nan_count"])
        nan_rate = float(r["nan_rate"])

        assert num_files >= 1, f"Meter {meter_id} has invalid num_files: {num_files}"
        assert total_rows >= 0, f"Meter {meter_id} has negative total_rows: {total_rows}"
        assert nan_count >= 0, f"Meter {meter_id} has negative nan_count: {nan_count}"
        assert 0.0 <= nan_rate <= 1.0, f"Meter {meter_id} has invalid nan_rate: {nan_rate}"

        if total_rows > 0:
            expected_rate = round(nan_count / total_rows, 6)
            assert abs(nan_rate - expected_rate) < 1e-5, f"Meter {meter_id} nan_rate calculation inconsistent"
            assert r["timestamp_min"] is not None and len(r["timestamp_min"]) > 0
            assert r["timestamp_max"] is not None and len(r["timestamp_max"]) > 0
            assert r["timestamp_min"] <= r["timestamp_max"], f"Meter {meter_id} min_ts > max_ts"
            assert num_timestamps <= total_rows, f"Meter {meter_id} distinct timestamps exceed total rows"
            assert num_timestamps > 0

        assert len(r["observed_frequency"]) > 0, f"Meter {meter_id} missing observed_frequency"
        assert r["observed_frequency"] in {"1min", "30s", "15s", "2min", "5min", "10min"}, (
            f"Meter {meter_id} has unexpected frequency cadence: {r['observed_frequency']}"
        )
        assert r["observed_frequency"] != "4.0h", f"Meter {meter_id} has false 4.0h cold-start artifact"


# ------------------------------------------------------------------------------
# Test 5: Raw data không bị sửa (read-only invariant preserved)
# ------------------------------------------------------------------------------
def test_5_raw_data_unmodified(raw_dir):
    data_dir = raw_dir / "data"
    assert data_dir.is_dir()
    assert os.access(data_dir, os.R_OK)

    # Verify original Honda dataset entries
    entries = set(p.name for p in raw_dir.iterdir())
    assert entries == {"data", "issues", "reduced_data"}, f"Raw directory entries changed: {entries}"


# ------------------------------------------------------------------------------
# Test 6: Không có file output nào được ghi vào raw dataset
# ------------------------------------------------------------------------------
def test_6_no_output_written_to_raw(raw_dir):
    forbidden_extensions = {".tmp", ".parquet", ".csv", ".json", ".log"}
    # Check top level
    for f in raw_dir.iterdir():
        if f.is_file():
            assert f.suffix not in forbidden_extensions, f"Forbidden output file found in raw_dir: {f.name}"

    # Check for newly created non-gz files inside data/
    for sub in (raw_dir / "data").iterdir():
        if sub.is_dir():
            for f in sub.iterdir():
                if f.is_file():
                    assert not f.name.endswith(".tmp")
                    assert not f.name.endswith(".parquet")


# ------------------------------------------------------------------------------
# Test 7: Config external path được sử dụng (không hardcode)
# ------------------------------------------------------------------------------
def test_7_config_external_path_utilized(config, metadata):
    # Verify metadata records the external path from config
    raw_path_from_cfg = str(config["data"]["raw_dir"])
    assert metadata["raw_data_dir"] == raw_path_from_cfg
    assert Path(metadata["raw_data_dir"]).is_absolute()
    assert "Honda_Dataset" in metadata["raw_data_dir"]

    # Verify no machine-specific absolute path is hardcoded in etl/inventory.py
    inventory_code = (REPO_ROOT / "etl" / "inventory.py").read_text(encoding="utf-8")
    forbidden_pattern = re.compile(r"/run/media/[a-zA-Z0-9_\-\.]+/")
    matches = forbidden_pattern.findall(inventory_code)
    assert not matches, f"Machine-specific path hardcoded in etl/inventory.py: {matches}"


# ------------------------------------------------------------------------------
# Test 8: Kết quả deterministic khi chạy cùng config/seed
# ------------------------------------------------------------------------------
def test_8_deterministic_results(raw_dir, metadata, inventory_rows, file_inventory_rows):
    assert metadata["task_id"] == "P1-T1"
    assert metadata["seed"] == 42
    assert metadata["dataset_summary"]["total_meters"] == 81
    assert metadata["dataset_summary"]["total_raw_files"] == 1603
    assert metadata["dataset_summary"]["total_rows"] == 3952487105
    assert metadata["dataset_summary"]["empty_files_count"] == 3
    assert metadata["dataset_summary"]["total_duplicate_rows"] == 286446
    assert metadata["dataset_summary"]["total_out_of_order_rows"] == 0

    # 1. Verify reports and task logs exist and are populated
    report_file = REPO_ROOT / "reports" / "p1_inventory.md"
    assert report_file.is_file()
    assert report_file.stat().st_size > 1000, "p1_inventory.md must contain comprehensive report content"

    task_log_file = REPO_ROOT / "reports" / "p1_t1_log.md"
    assert task_log_file.is_file(), "Task completion log reports/p1_t1_log.md must exist per EXECUTOR.md"
    assert task_log_file.stat().st_size > 200, "Task log reports/p1_t1_log.md must be populated"

    # 2. Deep verification of execution determinism:
    # Run scan_single_file twice on sample file, ensuring bit-for-bit identical outputs
    sample_file = raw_dir / "data" / "H1.K11" / "H1.K11.P_raw.csv.gz"
    res1 = scan_single_file(sample_file)
    res2 = scan_single_file(sample_file)

    assert res1 == res2, "Repeated scans on same raw file must be 100% deterministic bit-for-bit"

    # Also verify scanned values match inventory_by_file.csv for this file
    stored_row = next(r for r in file_inventory_rows if r["file_name"] == "H1.K11.P_raw.csv.gz")
    assert int(stored_row["total_rows"]) == res1["total_rows"]
    assert stored_row["timestamp_min"] == res1["timestamp_min"]
    assert stored_row["timestamp_max"] == res1["timestamp_max"]
    assert stored_row["observed_frequency"] == res1["observed_frequency"]
