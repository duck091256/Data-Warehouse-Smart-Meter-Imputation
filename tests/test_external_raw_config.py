"""
tests/test_external_raw_config.py — Test Suite for External Raw Dataset Configuration

Validates:
1. Config is loaded successfully.
2. data.raw_dir resolves correctly to a pathlib.Path.
3. Paths with spaces (e.g. 'New Volume/Vice - Download') are handled safely.
4. Target raw path exists and is readable.
5. Raw dataset is untouched (zero writes, no modifications).
6. No machine-specific physical paths are hardcoded in core research source code.
7. Authentic Honda dataset structure is verified via metadata inspection.
"""

import os
import re
import sys
import tempfile
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import (
    load_config,
    get_raw_data_dir,
    validate_honda_dataset,
    parse_cli_config_arg,
    find_repo_root,
)


def test_1_config_loaded_successfully():
    """Verify configs/local.yaml and configs/default.yaml load properly."""
    local_cfg_path = REPO_ROOT / "configs" / "local.yaml"
    assert local_cfg_path.exists(), "configs/local.yaml must exist for local runs"

    cfg = load_config(local_cfg_path)
    assert isinstance(cfg, dict)
    assert "data" in cfg
    assert "raw_dir" in cfg["data"]
    assert "protocol_version" in cfg


def test_2_raw_dir_resolves_correctly():
    """Verify data.raw_dir resolves to a valid Path instance."""
    cfg = load_config(REPO_ROOT / "configs" / "local.yaml")
    raw_dir = get_raw_data_dir(cfg)
    assert isinstance(raw_dir, Path)
    assert raw_dir.is_absolute()
    assert str(raw_dir).endswith("Honda_Dataset")


def test_3_path_with_spaces_works(tmp_path):
    """Verify that path resolution works reliably with whitespace."""
    # Test on synthetic dir with spaces
    spaced_dir = tmp_path / "My Folder With Spaces" / "Sub Dir 123"
    spaced_dir.mkdir(parents=True)
    test_file = spaced_dir / "sample.txt"
    test_file.write_text("sample content", encoding="utf-8")

    dummy_cfg = {
        "protocol_version": "v1",
        "data": {
            "raw_dir": str(spaced_dir)
        }
    }
    resolved = get_raw_data_dir(dummy_cfg)
    assert resolved == spaced_dir
    assert (resolved / "sample.txt").read_text() == "sample content"

    # Test on actual local config path which contains spaces ('New Volume', 'Vice - Download')
    local_cfg = load_config(REPO_ROOT / "configs" / "local.yaml")
    actual_path = get_raw_data_dir(local_cfg)
    assert " " in str(actual_path), "Expected test path to contain spaces"
    assert actual_path.exists(), "Spaced path must resolve and exist"


def test_4_raw_path_exists_and_readable():
    """Verify target external raw dataset exists and is accessible for reading."""
    local_cfg = load_config(REPO_ROOT / "configs" / "local.yaml")
    raw_dir = get_raw_data_dir(local_cfg, validate_exists=True)
    assert raw_dir.is_dir()
    assert os.access(raw_dir, os.R_OK)


def test_5_raw_directory_not_modified():
    """Ensure accessing and validating raw dataset does not alter any files or directories."""
    local_cfg = load_config(REPO_ROOT / "configs" / "local.yaml")
    raw_dir = get_raw_data_dir(local_cfg)

    # Record directory state before
    stat_before = raw_dir.stat()
    entries_before = set(p.name for p in raw_dir.iterdir())

    # Perform validation
    info = validate_honda_dataset(raw_dir)
    assert info["is_valid_honda_dataset"] is True

    # Record directory state after
    stat_after = raw_dir.stat()
    entries_after = set(p.name for p in raw_dir.iterdir())

    assert entries_before == entries_after, "Dataset entries must remain identical"
    assert stat_before.st_mtime == stat_after.st_mtime, "Raw directory mtime must not change"


def test_6_no_hardcoded_physical_paths_in_source():
    """Verify no machine-dependent physical path is hardcoded in source code or default config."""
    # Pattern matching machine-specific mount point
    forbidden_pattern = re.compile(r"/run/media/[a-zA-Z0-9_\-\.]+/")

    files_to_check = [
        REPO_ROOT / "src" / "config.py",
        REPO_ROOT / "etl" / "config.py",
        REPO_ROOT / "configs" / "default.yaml",
        REPO_ROOT / "control" / "gate.sh",
        REPO_ROOT / "control" / "check_scope.py",
        REPO_ROOT / "tests" / "test_control_layer.py",
    ]

    for file_path in files_to_check:
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8")
            matches = forbidden_pattern.findall(text)
            assert not matches, (
                f"Forbidden machine-specific physical path hardcoded in '{file_path.name}': {matches}"
            )


def test_7_honda_dataset_authenticity():
    """Verify authentic Honda dataset metadata without modifying files."""
    local_cfg = load_config(REPO_ROOT / "configs" / "local.yaml")
    raw_dir = get_raw_data_dir(local_cfg)
    info = validate_honda_dataset(raw_dir)

    assert info["is_valid_honda_dataset"] is True
    assert info["meter_count"] == 81, f"Expected 81 meters, got {info['meter_count']}"
    assert info["auto_issues_count"] > 0
    assert "H1.K11" in info["sample_meters"] or "H2.Z311" in [p.name for p in (raw_dir / "data").iterdir()]


def test_8_cli_arg_parsing():
    """Verify --config argument parsing."""
    parsed = parse_cli_config_arg(["--config", "configs/local.yaml", "--other", "val"])
    assert parsed == Path("configs/local.yaml")

    parsed_none = parse_cli_config_arg(["--verbose", "true"])
    assert parsed_none is None
