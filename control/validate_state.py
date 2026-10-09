#!/usr/bin/env python3
"""
control/validate_state.py — Task State Machine Validator

Enforces state machine integrity for research tasks:
- Validates schema and allowed status enum values.
- Enforces linear gating rule: a task cannot be started or progressed
  unless all prerequisite tasks have reached GATED status.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    import yaml
except ImportError:
    sys.stderr.write("Error: PyYAML is required. Please install pyyaml.\n")
    sys.exit(1)

ALLOWED_STATUSES = {
    "BLOCKED",
    "READY",
    "IN_PROGRESS",
    "TEST_FAILED",
    "TEST_PASSED",
    "AUDIT_FAILED",
    "AUDIT_PASSED",
    "GATED",
}

# Linear workflow task sequence
DEFAULT_TASK_SEQUENCE = [
    "CONTROL_LAYER",
    "P1-T1", "P1-T2", "P1-T3", "P1-T4", "P1-T5", "P1-T6", "P1-T7", "P1-T8",
    "P2-T1", "P2-T2", "P2-T3", "P2-T4", "P2-T5a", "P2-T5b", "P2-T6", "P2-T7", "P2-T8",
    "P3-T1", "P3-T2", "P3-T3", "P3-T4", "P3-T5", "P3-T6", "P3-T7",
    "P4-T1", "P4-T2", "P4-T3", "P4-T4", "P4-T5", "P4-T6", "P4-T7", "P4-T8",
    "P5-T1", "P5-T2", "P5-T3", "P5-T4", "P5-T5", "P5-T6",
    "P6-T1", "P6-T2", "P6-T3", "P6-T4", "P6-T5", "P6-T6",
    "P7-T1", "P7-T2", "P7-T3", "P7-T4", "P7-T5",
]


def load_task_state(state_file: Path) -> Dict[str, Any]:
    if not state_file.exists():
        raise FileNotFoundError(f"State file not found at {state_file}")
    with open(state_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Root of state file must be a dictionary.")
    return data


def validate_task_state(data: Dict[str, Any]) -> List[str]:
    """
    Validates task state dictionary.
    Returns list of error messages (empty if valid).
    """
    errors = []

    for required_key in ["protocol_version", "current_stage", "current_task", "tasks"]:
        if required_key not in data:
            errors.append(f"Missing required top-level key: '{required_key}'")

    if errors:
        return errors

    tasks = data.get("tasks", {})
    if not isinstance(tasks, dict):
        return ["'tasks' field must be a dictionary of task entries."]

    current_task = data.get("current_task")
    if current_task not in tasks:
        errors.append(f"current_task '{current_task}' is not defined in tasks map.")

    # Validate individual task statuses
    for task_id, task_info in tasks.items():
        if not isinstance(task_info, dict):
            errors.append(f"Task '{task_id}' definition must be a dictionary.")
            continue
        status = task_info.get("status")
        if not status:
            errors.append(f"Task '{task_id}' is missing 'status' field.")
        elif status not in ALLOWED_STATUSES:
            errors.append(
                f"Task '{task_id}' has invalid status '{status}'. "
                f"Allowed values: {sorted(list(ALLOWED_STATUSES))}"
            )

    if errors:
        return errors

    # Enforce Gate Progression Rule:
    # A task can only be READY, IN_PROGRESS, TEST_PASSED, etc., if all preceding tasks in sequence are GATED.
    active_statuses = {"READY", "IN_PROGRESS", "TEST_FAILED", "TEST_PASSED", "AUDIT_FAILED", "AUDIT_PASSED", "GATED"}

    for idx, task_id in enumerate(DEFAULT_TASK_SEQUENCE):
        if task_id not in tasks:
            continue
        status = tasks[task_id].get("status")
        # If this task has moved past BLOCKED, check that all predecessors are GATED
        if status in active_statuses and status != "BLOCKED":
            for prev_idx in range(idx):
                prev_task_id = DEFAULT_TASK_SEQUENCE[prev_idx]
                if prev_task_id in tasks:
                    prev_status = tasks[prev_task_id].get("status")
                    if prev_status != "GATED":
                        errors.append(
                            f"Progression violation: Task '{task_id}' has status '{status}', "
                            f"but prerequisite task '{prev_task_id}' is '{prev_status}' (must be 'GATED')."
                        )
                        break

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate task_state.yaml integrity.")
    parser.add_argument("--state-file", type=str, default=None, help="Path to task_state.yaml")
    args = parser.parse_args()

    if args.state_file:
        state_path = Path(args.state_file).resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent
        state_path = repo_root / "control" / "task_state.yaml"

    try:
        data = load_task_state(state_path)
        errors = validate_task_state(data)
        if errors:
            print("[FAIL] Task state validation failed:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        print(f"[OK] Task state '{state_path}' is valid.")
        sys.exit(0)
    except Exception as e:
        print(f"[FAIL] Error loading/validating task state: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
