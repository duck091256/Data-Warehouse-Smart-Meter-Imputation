"""
tests/test_control_layer.py — Test Suite for Research Control & Governance Layer

Verifies:
1. Protected-path detection logic.
2. data/raw/ is strictly recognized as protected.
3. Protocol hashing is deterministic and reproducible.
4. Gate / Scope check fails upon protected-file violation.
5. Linear progression enforcement (cannot advance task if predecessor is not GATED).
6. Invalid task states are rejected.
7. Portability check: No machine-dependent absolute paths in control scripts.
"""

import copy
import os
import re
import subprocess
import sys
from pathlib import Path
import pytest
import yaml

# Add repo root to sys.path so we can import control modules
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from control.check_scope import (
    load_protected_rules,
    is_path_protected,
    check_scope,
)
from control.validate_state import (
    validate_task_state,
    load_task_state,
    ALLOWED_STATUSES,
)


# ------------------------------------------------------------------------------
# Test 1: Protected-path detection hoạt động
# ------------------------------------------------------------------------------
def test_1_protected_path_detection():
    rules_file = REPO_ROOT / "control" / "protected_paths.txt"
    assert rules_file.exists(), "protected_paths.txt must exist"
    rules = load_protected_rules(rules_file)

    # Protected cases
    is_prot, matched = is_path_protected("TASK_PLAN.md", rules)
    assert is_prot and matched == "TASK_PLAN.md"

    is_prot, matched = is_path_protected("control/gate.sh", rules)
    assert is_prot and matched == "control/"

    is_prot, matched = is_path_protected("tests/test_something.py", rules)
    assert is_prot and matched == "tests/"

    # Allowed cases (normal research files)
    is_prot, _ = is_path_protected("models/baseline.py", rules)
    assert not is_prot

    is_prot, _ = is_path_protected("etl/preprocess.py", rules)
    assert not is_prot

    is_prot, _ = is_path_protected("data/interim/readings.parquet", rules)
    assert not is_prot

    is_prot, _ = is_path_protected("reports/p1_inventory.md", rules)
    assert not is_prot


# ------------------------------------------------------------------------------
# Test 2: data/raw/ được coi là protected
# ------------------------------------------------------------------------------
def test_2_raw_data_is_protected():
    rules_file = REPO_ROOT / "control" / "protected_paths.txt"
    rules = load_protected_rules(rules_file)

    raw_test_paths = [
        "data/raw/readings.csv",
        "data/raw/honda/meters.parquet",
        "data/raw/sub/dir/issue_log.json",
        "data/raw",
        "./data/raw/readings.csv",
    ]

    for p in raw_test_paths:
        is_prot, matched = is_path_protected(p, rules)
        assert is_prot, f"Path '{p}' should be protected!"
        assert matched == "data/raw/", f"Matched rule for '{p}' should be 'data/raw/'"

    # Conversely, data/interim/ and data/processed/ must NOT match data/raw/
    assert not is_path_protected("data/interim/readings.parquet", rules)[0]
    assert not is_path_protected("data/processed/clean_segments.parquet", rules)[0]


# ------------------------------------------------------------------------------
# Test 3: Protocol hash được tính deterministic
# ------------------------------------------------------------------------------
def test_3_protocol_hash_deterministic():
    script_path = REPO_ROOT / "control" / "protocol_hash.sh"
    assert script_path.exists(), "protocol_hash.sh must exist"

    # Run script multiple times and compare output
    res1 = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(REPO_ROOT),
    )
    res2 = subprocess.run(
        ["bash", str(script_path)],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(REPO_ROOT),
    )

    assert res1.stdout == res2.stdout, "Protocol hash output must be 100% deterministic"
    assert "TASK_PLAN.md" in res1.stdout, "TASK_PLAN.md must be included in protocol hash"

    # Test that verify mode succeeds with valid manifest
    verify_res = subprocess.run(
        ["bash", str(script_path), "--verify"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert verify_res.returncode == 0, f"Protocol verify should pass: {verify_res.stderr}"


# ------------------------------------------------------------------------------
# Test 4: Gate fail khi có protected-file violation
# ------------------------------------------------------------------------------
def test_4_gate_fails_on_protected_violation():
    rules_file = REPO_ROOT / "control" / "protected_paths.txt"
    rules = load_protected_rules(rules_file)

    # check_scope with a forbidden file
    violating_files = ["models/baseline.py", "data/raw/tampered.csv"]
    allowed, forbidden = check_scope(violating_files, rules)

    assert len(forbidden) == 1
    assert forbidden[0][0] == "data/raw/tampered.csv"
    assert len(allowed) == 1
    assert allowed[0] == "models/baseline.py"

    # Run check_scope.py CLI with explicit forbidden file -> must exit with code 1
    check_script = REPO_ROOT / "control" / "check_scope.py"
    res = subprocess.run(
        [sys.executable, str(check_script), "--files", "data/raw/tampered.csv"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert res.returncode == 1, "check_scope CLI must exit with code 1 upon violation"
    assert "FORBIDDEN" in res.stdout


# ------------------------------------------------------------------------------
# Test 5: Gate không cho chuyển sang task tiếp theo khi task trước chưa qua gate
# ------------------------------------------------------------------------------
def test_5_progression_rejected_if_predecessor_not_gated():
    valid_state = {
        "protocol_version": "v1",
        "current_stage": "SETUP",
        "current_task": "CONTROL_LAYER",
        "tasks": {
            "CONTROL_LAYER": {"status": "IN_PROGRESS", "test": "NOT_RUN", "audit": "NOT_REQUIRED"},
            "P1-T1": {"status": "BLOCKED", "test": "NOT_RUN", "audit": "NOT_REQUIRED"},
            "P1-T2": {"status": "BLOCKED", "test": "NOT_RUN", "audit": "NOT_REQUIRED"},
        },
    }
    # Initial state should pass
    assert validate_task_state(valid_state) == []

    # Case A: P1-T1 set to IN_PROGRESS while CONTROL_LAYER is still IN_PROGRESS (not GATED)
    invalid_state_a = copy.deepcopy(valid_state)
    invalid_state_a["current_task"] = "P1-T1"
    invalid_state_a["tasks"]["P1-T1"]["status"] = "IN_PROGRESS"
    errors = validate_task_state(invalid_state_a)
    assert len(errors) > 0, "Advancing to P1-T1 before CONTROL_LAYER is GATED must fail"
    assert any("CONTROL_LAYER" in e and "GATED" in e for e in errors)

    # Case B: P1-T2 set to READY while P1-T1 is TEST_PASSED but not GATED
    invalid_state_b = copy.deepcopy(valid_state)
    invalid_state_b["tasks"]["CONTROL_LAYER"]["status"] = "GATED"
    invalid_state_b["tasks"]["P1-T1"]["status"] = "TEST_PASSED"
    invalid_state_b["tasks"]["P1-T2"]["status"] = "READY"
    errors_b = validate_task_state(invalid_state_b)
    assert len(errors_b) > 0, "P1-T2 cannot be READY if P1-T1 is not GATED"
    assert any("P1-T1" in e and "GATED" in e for e in errors_b)

    # Case C: Proper gated state passes
    gated_state = copy.deepcopy(valid_state)
    gated_state["tasks"]["CONTROL_LAYER"]["status"] = "GATED"
    gated_state["tasks"]["P1-T1"]["status"] = "READY"
    gated_state["current_task"] = "P1-T1"
    assert validate_task_state(gated_state) == []


# ------------------------------------------------------------------------------
# Test 6: Invalid task state bị reject
# ------------------------------------------------------------------------------
def test_6_invalid_task_state_rejected():
    base_state = {
        "protocol_version": "v1",
        "current_stage": "SETUP",
        "current_task": "CONTROL_LAYER",
        "tasks": {
            "CONTROL_LAYER": {"status": "IN_PROGRESS"},
            "P1-T1": {"status": "BLOCKED"},
        },
    }

    # Test unknown status like 'DONE', 'FINISHED', 'COMPLETE'
    for bogus_status in ["DONE", "FINISHED", "COMPLETE", "PASS", "SKIPPED"]:
        bad_state = copy.deepcopy(base_state)
        bad_state["tasks"]["CONTROL_LAYER"]["status"] = bogus_status
        errors = validate_task_state(bad_state)
        assert len(errors) > 0, f"Status '{bogus_status}' should be rejected"
        assert any("invalid status" in e for e in errors)

    # Test missing required keys
    for req_key in ["protocol_version", "current_stage", "current_task", "tasks"]:
        bad_state = copy.deepcopy(base_state)
        del bad_state[req_key]
        errors = validate_task_state(bad_state)
        assert len(errors) > 0, f"Missing '{req_key}' should cause validation error"


# ------------------------------------------------------------------------------
# Test 7: Không có absolute path phụ thuộc máy developer
# ------------------------------------------------------------------------------
def test_7_no_developer_specific_absolute_paths():
    control_dir = REPO_ROOT / "control"
    files_to_scan = [
        control_dir / "check_scope.py",
        control_dir / "gate.sh",
        control_dir / "protocol_hash.sh",
        control_dir / "validate_state.py",
        control_dir / "task_state.yaml",
        control_dir / "protected_paths.txt",
        REPO_ROOT / "tests" / "test_control_layer.py",
    ]

    home_pattern = re.compile(r"/home/[a-zA-Z0-9_\-\.]+")

    for file_path in files_to_scan:
        assert file_path.exists(), f"File {file_path} must exist"
        content = file_path.read_text(encoding="utf-8")
        matches = home_pattern.findall(content)
        assert not matches, (
            f"File '{file_path.name}' contains hardcoded developer home path: {matches}"
        )
