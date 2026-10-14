#!/usr/bin/env python3
"""Fail-closed Git scope validation; explicit --files is diagnostic only."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import List, Tuple, Optional


class ScopeError(ValueError):
    """Scope or its trusted inputs cannot be established."""


def git(repo_root, *args):
    try:
        env = os.environ.copy()
        # Inspect this checkout's real index/objects, not shell-selected ones.
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            env.pop(key, None)
        env["GIT_OPTIONAL_LOCKS"] = "0"
        result = subprocess.run(
            ["git", "-C", str(repo_root), *args], capture_output=True, check=True,
            env=env
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ScopeError(f"Git inspection failed: {exc}") from exc
    return result.stdout


def find_repo_root() -> Path:
    root = Path(__file__).resolve().parent.parent
    actual = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if actual != root:
        raise ScopeError("Control scripts must belong to the Git working-tree root")
    return actual


def parse_rules(text):
    rules = [line.strip() for line in text.splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    if not rules:
        raise ScopeError("Protected-path policy is empty")
    for rule in rules:
        validate_path(rule.rstrip("/"))
    return rules


def load_protected_rules(rules_path: Path) -> List[str]:
    return parse_rules(rules_path.read_text(encoding="utf-8"))


def validate_path(path):
    if not isinstance(path, str) or not path or "\x00" in path:
        raise ScopeError("Paths must be non-empty repository-relative strings")
    p = PurePosixPath(path)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in path.split("/")):
        raise ScopeError(f"Non-canonical repository path: {path!r}")
    if p.parts[0] == ".git":
        raise ScopeError("Git administrative paths cannot be authorized")
    return path


def is_path_protected(file_path: str, rules: List[str]) -> Tuple[bool, Optional[str]]:
    path = file_path[2:] if file_path.startswith("./") else file_path
    for rule in rules:
        prefix = rule.rstrip("/")
        if path == prefix or path.startswith(prefix + "/"):
            return True, rule
    return False, None


def validate_base(repo_root, base):
    actual_root = Path(os.fsdecode(git(repo_root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if actual_root != Path(repo_root).resolve():
        raise ScopeError("--repo-root must be the working-tree root")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", base or ""):
        raise ScopeError("--base must be an explicit full commit SHA")
    resolved = git(repo_root, "rev-parse", "--verify", base + "^{commit}").decode().strip()
    if resolved != base:
        raise ScopeError("Base must identify a commit directly")
    git(repo_root, "merge-base", "--is-ancestor", base, "HEAD")
    return base


def get_git_diff_files(repo_root: Path, base: str) -> List[str]:
    """Union of branch, index, working tree and non-ignored untracked paths.

    Disabling rename detection exposes both old and new names as delete/add.
    NUL separation preserves spaces, quotes, Unicode and newline filenames.
    """
    validate_base(repo_root, base)
    changed = set()
    commands = [
        ("diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", base, "HEAD", "--"),
        ("diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", "--cached", "--"),
        ("diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", "--"),
        ("ls-files", "--others", "--exclude-standard", "-z", "--"),
    ]
    for command in commands:
        changed.update(os.fsdecode(p) for p in git(repo_root, *command).split(b"\x00") if p)
    return sorted(changed)


def check_scope(files: List[str], rules: List[str]):
    allowed, forbidden = [], []
    for path in files:
        protected, rule = is_path_protected(path, rules)
        if protected:
            forbidden.append((path, rule))
        else:
            allowed.append(path)
    return allowed, forbidden


def load_scope_manifest(path, repo_root, base):
    """An operator-supplied approval record, never an authentication mechanism."""
    manifest_path = Path(path).resolve(strict=True)
    if manifest_path.is_relative_to(repo_root.resolve()):
        raise ScopeError("Scope manifest must be supplied outside the candidate checkout")
    def unique_keys(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ScopeError(f"Duplicate scope manifest key: {key}")
            obj[key] = value
        return obj

    data = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    keys = {"base_commit", "authority", "allowed_files", "protected_exceptions"}
    if not isinstance(data, dict) or set(data) != keys:
        raise ScopeError(f"Scope manifest requires exactly: {sorted(keys)}")
    if data["base_commit"] != base:
        raise ScopeError("Scope manifest base does not match --base")
    if not isinstance(data["authority"], str) or not data["authority"].strip():
        raise ScopeError("Scope manifest requires an approval reference")
    for key in ("allowed_files", "protected_exceptions"):
        paths = data[key]
        if not isinstance(paths, list):
            raise ScopeError(f"{key} must be a list of exact file paths")
        for entry in paths:
            validate_path(entry)
        if len(set(paths)) != len(paths):
            raise ScopeError(f"Duplicate paths in {key}")
    allowed = set(data["allowed_files"])
    exceptions = set(data["protected_exceptions"])
    if not allowed or not exceptions <= allowed:
        raise ScopeError("Allowlist must be non-empty and contain all exceptions")
    immutable = ["TASK_PLAN.md", "RESEARCH_PLAN.md", "data/raw/",
                 "control/task_state.yaml", "control/protected_paths.txt",
                 "control/protocol_hashes.txt"]
    if any(is_path_protected(p, immutable)[0] for p in exceptions):
        raise ScopeError("P0a cannot authorize protocol, raw, canonical state or policy exceptions")
    return allowed, exceptions


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
    if task_id not in TASK_REQUIRED_OUTPUTS:
        return [f"No output specification for task: {task_id}"]
    expected = TASK_REQUIRED_OUTPUTS[task_id]
    failures = []
    for rel_p in expected:
        full_p = repo_root / rel_p
        if not full_p.exists():
            failures.append(f"Missing required output artifact: '{rel_p}'")
        elif not full_p.is_file():
            failures.append(f"Output artifact is not a file: '{rel_p}'")
        elif full_p.stat().st_size == 0:
            failures.append(f"Output artifact is 0-byte empty: '{rel_p}'")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root")
    parser.add_argument("--base", help="Approved full commit SHA; never inferred")
    parser.add_argument("--scope-manifest", help="External operator-approved JSON record")
    parser.add_argument("--files", nargs="*", help="Diagnostic denylist check only (not a gate)")
    parser.add_argument("--rules", help="Policy override for explicit diagnostic --files only")
    parser.add_argument("--task")
    parser.add_argument("--check-outputs", action="store_true")
    args = parser.parse_args()
    try:
        root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
        if args.files is not None:
            if args.base or args.scope_manifest:
                raise ScopeError("Diagnostic --files cannot replace a Git scope check")
            rules = load_protected_rules(Path(args.rules) if args.rules else root / "control/protected_paths.txt")
            _, forbidden = check_scope(args.files, rules)
            print("DIAGNOSTIC ONLY: explicit paths; Git scope was not verified")
        else:
            if args.rules or not args.base or not args.scope_manifest:
                raise ScopeError("Git scope requires --base and --scope-manifest; policy overrides are forbidden")
            validate_base(root, args.base)
            rules = parse_rules(git(root, "show", args.base + ":control/protected_paths.txt").decode("utf-8"))
            allowed, exceptions = load_scope_manifest(args.scope_manifest, root, args.base)
            files = get_git_diff_files(root, args.base)
            forbidden = []
            for path in files:
                validate_path(path)
                protected, rule = is_path_protected(path, rules)
                if path not in allowed:
                    forbidden.append((path, "outside approved allowlist"))
                elif protected and path not in exceptions:
                    forbidden.append((path, rule))
                else:
                    print(f"ALLOWED: {path!r}")
            print(f"Git scope inspected {len(files)} changed paths against base {args.base}")
        for path, reason in forbidden:
            print(f"FORBIDDEN: {path!r} ({reason})")
        if forbidden:
            return 1
        task = args.task
        if args.check_outputs and not task:
            import yaml
            task = yaml.safe_load((root / "control/task_state.yaml").read_text())["current_task"]
        if task is not None:
            failures = verify_task_outputs(root, task)
            if failures:
                raise ScopeError("; ".join(failures))
            print(f"Output presence verified for {task}; task acceptance was not verified")
        print("Scope check PASSED" if args.files is None else "Diagnostic check PASSED")
        return 0
    except (ScopeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"[SCOPE ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
