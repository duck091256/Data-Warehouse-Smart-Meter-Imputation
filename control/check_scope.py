#!/usr/bin/env python3
"""
control/check_scope.py — Enforce Scope Discipline & Protected Path Invariants

Inspects modified files (via `git diff --name-only` or explicit arguments)
against protected path rules defined in `control/protected_paths.txt`.

Exit code:
  0: All changes are within allowed scope.
  1: One or more forbidden (protected) files were modified.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def find_repo_root() -> Path:
    """Safely determines the repository root directory without hardcoded paths."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        git_root = res.stdout.strip()
        if git_root and os.path.isdir(git_root):
            return Path(git_root).resolve()
    except Exception:
        pass
    # Fallback: parent directory of `control/` directory
    return Path(__file__).resolve().parent.parent


def load_protected_rules(rules_path: Path) -> List[str]:
    """Loads and normalizes protected path rules from file."""
    if not rules_path.is_file():
        return []
    rules = []
    with open(rules_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Normalize path separators
            norm = os.path.normpath(line).replace("\\", "/")
            if line.endswith("/"):
                norm += "/"
            rules.append(norm)
    return rules


def is_path_protected(file_path: str, rules: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Checks if a given relative file path matches any protected path rule.
    Returns (is_protected, matching_rule).
    """
    # Normalize path
    norm_path = os.path.normpath(file_path).replace("\\", "/")
    if norm_path.startswith("./"):
        norm_path = norm_path[2:]

    for rule in rules:
        if rule.endswith("/"):
            rule_prefix = rule.rstrip("/")
            if norm_path == rule_prefix or norm_path.startswith(rule_prefix + "/"):
                return True, rule
        else:
            if norm_path == rule or norm_path.startswith(rule + "/"):
                return True, rule

    return False, None


def get_git_diff_files(repo_root: Path, check_cached: bool = True) -> List[str]:
    """Retrieves list of changed files from git diff --name-only."""
    changed_files = set()
    try:
        # Check unstaged changes
        res = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True
        )
        for line in res.stdout.splitlines():
            line = line.strip()
            if line:
                changed_files.add(line)

        # Check staged changes if requested
        if check_cached:
            res_cached = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True
            )
            for line in res_cached.stdout.splitlines():
                line = line.strip()
                if line:
                    changed_files.add(line)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Warning: git diff execution failed: {e}\n")
    except FileNotFoundError:
        sys.stderr.write("Warning: git binary not found.\n")

    return sorted(list(changed_files))


def check_scope(files: List[str], rules: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Classifies files into allowed and forbidden.
    Returns (allowed_files, forbidden_files_with_rules).
    """
    allowed = []
    forbidden = []
    for f in files:
        protected, rule = is_path_protected(f, rules)
        if protected:
            forbidden.append((f, rule or "UNKNOWN"))
        else:
            allowed.append(f)
    return allowed, forbidden


TASK_REQUIRED_OUTPUTS = {
    "P1-T1": [
        "data/interim/inventory.csv",
        "data/interim/inventory_by_file.csv",
        "data/interim/inventory_metadata.json",
        "reports/p1_inventory.md",
        "reports/p1_t1_log.md",
    ],
    "P1-T2": [
        "data/interim/readings_utc.parquet",
        "data/interim/readings_utc_metadata.json",
        "reports/p1_t2_log.md",
        "reports/p1_t2_reconciliation.md",
        "reports/v_z84_duplicate_evidence.md",
    ],
}


def verify_task_outputs(repo_root: Path, task_id: str) -> List[str]:
    """
    Verifies that required output artifacts for a task exist and are non-empty.
    Returns list of failure messages.
    """
    expected = TASK_REQUIRED_OUTPUTS.get(task_id, [])
    failures = []
    for rel_p in expected:
        full_p = repo_root / rel_p
        if not full_p.exists():
            failures.append(f"Missing required output artifact: '{rel_p}'")
        elif full_p.stat().st_size == 0:
            failures.append(f"Output artifact is 0-byte empty: '{rel_p}'")
    return failures


def main():
    parser = argparse.ArgumentParser(description="Check modified files against protected paths.")
    parser.add_argument("--files", nargs="*", help="Explicit list of files to check instead of git diff.")
    parser.add_argument("--rules", type=str, default=None, help="Path to protected_paths.txt.")
    parser.add_argument("--repo-root", type=str, default=None, help="Explicit repository root.")
    parser.add_argument("--unstaged-only", action="store_true", help="Only check unstaged git diff.")
    parser.add_argument("--task", type=str, default=None, help="Task ID to verify required output artifacts.")
    parser.add_argument("--check-outputs", action="store_true", help="Verify required outputs for current task.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    rules_file = Path(args.rules).resolve() if args.rules else (repo_root / "control" / "protected_paths.txt")

    if not rules_file.exists():
        sys.stderr.write(f"Error: Protected paths file not found at {rules_file}\n")
        sys.exit(1)

    rules = load_protected_rules(rules_file)

    if args.files is not None:
        files_to_check = args.files
    else:
        files_to_check = get_git_diff_files(repo_root, check_cached=not args.unstaged_only)

    task_to_check = args.task
    if args.check_outputs and not task_to_check:
        state_file = repo_root / "control" / "task_state.yaml"
        if state_file.exists():
            try:
                import yaml
                with open(state_file, "r", encoding="utf-8") as sf:
                    st = yaml.safe_load(sf)
                    task_to_check = st.get("current_task")
            except Exception:
                pass

    if task_to_check:
        output_failures = verify_task_outputs(repo_root, task_to_check)
        if output_failures:
            print(f"\n[OUTPUT VERIFICATION FAILED] for task '{task_to_check}':")
            for fail_msg in output_failures:
                print(f"  FAILED: {fail_msg}")
            sys.exit(1)
        else:
            print(f"OUTPUT VERIFICATION PASSED: All required artifacts for '{task_to_check}' are present and non-empty.")

    if not files_to_check:
        print("ALLOWED: No modified files detected.")
        sys.exit(0)

    allowed, forbidden = check_scope(files_to_check, rules)

    for f in allowed:
        print(f"ALLOWED: {f}")

    if forbidden:
        print("\n[SCOPE VIOLATION] Protected files detected:")
        for f, rule in forbidden:
            print(f"FORBIDDEN: {f} (violates rule: '{rule}')")
        sys.exit(1)

    print("\nScope check PASSED: All modified files are permitted.")
    sys.exit(0)


if __name__ == "__main__":
    main()
