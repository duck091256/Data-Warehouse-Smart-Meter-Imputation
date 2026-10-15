#!/usr/bin/env python3
"""Fail-closed Git scope validation; explicit --files is diagnostic only."""

import sys
# Transition CLI must reject unsafe startup before importing candidate-shadowable modules.
if __name__ == "__main__" and any(a.split("=", 1)[0] in
        {"--state-transition", "--authorization-sha256"} for a in sys.argv[1:]) and not sys.flags.isolated:
    sys.stderr.write("[SCOPE ERROR] State transition requires isolated Python (-I)\n")
    sys.exit(1)

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
        env["GIT_NO_REPLACE_OBJECTS"] = "1"
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


def load_scope_manifest(path, repo_root, base, *, _state_exception=False):
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
    if _state_exception:
        immutable.remove("control/task_state.yaml")
    if any(is_path_protected(p, immutable)[0] for p in exceptions):
        raise ScopeError("P0a cannot authorize protocol, raw, canonical state or policy exceptions")
    return allowed, exceptions


# State transition v1 is a read-only, separately pinned Integrator verification.
STATE_PATH = "control/task_state.yaml"


def require_transition(condition, message):
    if not condition:
        raise ScopeError("State transition: " + message)


def sha256_bytes(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()


def checked_file(path, repo_root=None):
    """Reject symlink aliases; authorization records must be absolute and external."""
    p = Path(path)
    require_transition(p.is_absolute(), "evidence paths must be absolute")
    require_transition(not any(parent.is_symlink() for parent in [p, *p.parents]),
                       "symlink records/evidence are forbidden")
    resolved = p.resolve(strict=True)
    require_transition(resolved.is_file(), "record/evidence must be a regular file")
    if repo_root is not None:
        require_transition(not resolved.is_relative_to(Path(repo_root).resolve()),
                           "approval records must be outside checkout")
    return resolved.read_bytes()


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require_transition(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid_constant(value):
        raise ScopeError("State transition: non-finite JSON number: " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid_constant)


def strict_state(raw):
    import yaml
    class UniqueLoader(yaml.SafeLoader):
        pass
    def mapping(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            require_transition(isinstance(key, str) and key not in result,
                               "state keys must be unique strings")
            result[key] = loader.construct_object(value_node)
        return result
    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        require_transition(not any(isinstance(t, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken))
                                   for t in yaml.scan(raw)), "state aliases/anchors are forbidden")
        data = yaml.load(raw, Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise ScopeError("State transition: malformed state YAML") from exc
    def strings_or_maps(value):
        return isinstance(value, str) or (isinstance(value, dict) and
            all(isinstance(k, str) and strings_or_maps(v) for k, v in value.items()))
    require_transition(isinstance(data, dict) and strings_or_maps(data),
                       "state v1 accepts string scalars and mappings only")
    require_transition(set(data) == {"protocol_version", "current_stage", "current_task", "tasks"},
                       "unexpected state top-level fields")
    return data


def semantic_delta(before, after, path=()):
    """Stable JSON paths, including additions/deletions; no executable expression."""
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(set(before) | set(after)):
            result.extend(semantic_delta(before.get(key), after.get(key), (*path, key)))
        return result
    if type(before) is type(after) and before == after:
        return []
    return [{"path": list(path), "before": before, "after": after}]


def bound_reference(reference, root, external=False):
    require_transition(isinstance(reference, dict) and set(reference) == {"path", "sha256"},
                       "evidence reference requires exactly path and sha256")
    raw = checked_file(reference["path"], root if external else None)
    require_transition(sha256_bytes(raw) == reference["sha256"], "evidence fingerprint mismatch")
    return raw


def validate_state_transition(root, base, scope_path, record_path, pinned_sha256):
    """Return verified scope; never apply/consume approval or write canonical state.

    pinned_sha256 must come from the Researcher's trusted approval channel, not
    from worker-generated JSON. It binds bytes, not a cryptographic identity.
    """
    require_transition(sys.flags.isolated, "isolated Python (-I) required")
    import copy
    import datetime
    import types
    root = Path(root).resolve()
    validate_base(root, base)
    # Do not execute Git clean/process filters or fsmonitor callbacks during verification.
    for entry in git(root, "config", "--null", "--list").split(b"\x00"):
        key, _, value = entry.partition(b"\n")
        key = key.decode().lower()
        require_transition(not re.fullmatch(r"filter\..*\.(clean|process)", key),
                           "Git clean/process filters forbidden in transition mode")
        require_transition(key != "core.fsmonitor" or value.decode().lower() in {"", "false", "0"},
                           "Git fsmonitor callbacks forbidden in transition mode")
    require_transition(git(root, "rev-parse", "HEAD").decode().strip() == base,
                       "HEAD must equal explicitly approved baseline")
    require_transition(re.fullmatch(r"[0-9a-f]{64}", pinned_sha256 or "") is not None,
                       "Researcher-pinned authorization SHA-256 required")
    raw = checked_file(record_path, root)
    require_transition(sha256_bytes(raw) == pinned_sha256, "authorization digest mismatch")
    record = strict_json(raw)
    fields = {"version", "operation", "role", "decision", "reference", "approved_at", "expires_at",
              "task_id", "base_commit", "before_sha256", "after_sha256", "delta", "scope_sha256",
              "authorization_evidence", "final_acceptance", "frozen_files"}
    require_transition(isinstance(record, dict) and set(record) == fields, "authorization schema mismatch")
    require_transition(type(record["version"]) is int and record["version"] == 1 and
                       record["operation"] == "FINALIZE_TASK" and record["role"] == "Researcher" and
                       record["decision"] == "APPROVE_CANONICAL_TRANSITION" and
                       isinstance(record["reference"], str) and record["reference"].strip(),
                       "explicit task-specific Researcher transition approval required")
    require_transition(record["base_commit"] == base, "authorization baseline mismatch")
    def utc(value):
        require_transition(isinstance(value, str) and value.endswith("Z"), "UTC approval timestamps required")
        return datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    now = datetime.datetime.now(datetime.timezone.utc)
    require_transition(utc(record["approved_at"]) <= now < utc(record["expires_at"]),
                       "approval is not yet valid or has expired")
    scope_raw = checked_file(scope_path, root)
    require_transition(sha256_bytes(scope_raw) == record["scope_sha256"], "approved scope fingerprint mismatch")
    bound_reference(record["authorization_evidence"], root, external=True)
    acceptance = strict_json(bound_reference(record["final_acceptance"], root, external=True))
    require_transition(isinstance(acceptance, dict) and set(acceptance) ==
                       {"task_id", "verdict", "test", "audit", "evidence"}, "final acceptance schema mismatch")
    require_transition(acceptance["task_id"] == record["task_id"] and acceptance["verdict"] == "ACCEPTED"
                       and acceptance["test"] == "PASSED" and acceptance["audit"] == "PASSED",
                       "task final acceptance/test/audit required")
    require_transition(isinstance(acceptance["evidence"], list) and acceptance["evidence"],
                       "final acceptance evidence is empty")
    for reference in acceptance["evidence"]:
        bound_reference(reference, root)
    # Verify trusted control bytes before executing the snapshot validator.
    verified_sources = {}
    for name in ("control/check_scope.py", "control/gate.sh", "control/validate_state.py",
                 "control/protocol_hash.sh", "control/protected_paths.txt", "control/protocol_hashes.txt"):
        verified_sources[name] = checked_file(root / name)
        require_transition(verified_sources[name] == git(root, "show", base + ":" + name),
                           "transition controls differ from approved baseline: " + name)
    # No executable cache is trusted merely because its neighboring source hash matches.
    require_transition(not list(root.glob("*.pyc")) and not any(p.is_file() for directory in
                               (root / "control", root / "tests", root / "__pycache__")
                               for p in directory.rglob("*.pyc")), "control/test bytecode caches forbidden in transition mode")
    # Compile the exact verified source bytes; never consult ignored SourceFileLoader caches.
    validator = types.ModuleType("transition_snapshot_validator")
    validator.__file__ = str(root / "control/validate_state.py")
    exec(compile(verified_sources["control/validate_state.py"], validator.__file__, "exec"), validator.__dict__)
    old_raw = git(root, "show", base + ":" + STATE_PATH)
    new_raw = checked_file(root / STATE_PATH)
    require_transition(sha256_bytes(old_raw) == record["before_sha256"] and
                       sha256_bytes(new_raw) == record["after_sha256"], "state preimage/postimage mismatch")
    before, after = strict_state(old_raw), strict_state(new_raw)
    require_transition(not validator.validate_task_state(before) and not validator.validate_task_state(after),
                       "state snapshot validation failed")
    task = record["task_id"]
    sequence = validator.DEFAULT_TASK_SEQUENCE
    require_transition(isinstance(task, str) and task in sequence and task != "CONTROL_LAYER",
                       "unknown research task")
    idx = sequence.index(task)
    require_transition(task in before["tasks"] and all(p in before["tasks"] and
                       before["tasks"][p]["status"] == "GATED" for p in sequence[:idx]),
                       "all preceding tasks must exist and be GATED")
    require_transition(before["current_task"] in (sequence[idx - 1], task),
                       "current_task is not the target or immediate gated predecessor")
    old = before["tasks"][task]
    require_transition(old.get("status") in {"BLOCKED", "READY", "IN_PROGRESS", "TEST_PASSED", "AUDIT_PASSED"}
                       and old.get("test") in {"NOT_RUN", "PASSED"}
                       and old.get("audit") in {"NOT_REQUIRED", "PASSED"},
                       "task cannot be finalized from failed/already gated/unknown state")
    expected = copy.deepcopy(before)
    expected["current_task"] = task
    expected["current_stage"] = task.split("-", 1)[0]
    expected["tasks"][task].update(status="GATED", test="PASSED", audit="PASSED")
    require_transition(after == expected, "unrelated or invalid semantic state advancement")
    delta = semantic_delta(before, after)
    require_transition(delta and record["delta"] == delta, "exact approved semantic delta mismatch")
    # Hidden index flags must not suppress unrelated/protected working-tree changes.
    flagged = [p for p in git(root, "ls-files", "-v", "-z").split(b"\x00") if p]
    require_transition(all(p[:1] == b"H" for p in flagged),
                       "hidden/sparse/conflicted index flags forbidden")
    index_tree = {}
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\x00"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        entry_mode, entry_oid, entry_stage = metadata.decode().split()
        require_transition(entry_stage == "0", "unmerged index forbidden")
        if os.fsdecode(path) != STATE_PATH:
            index_tree[path] = (entry_mode, entry_oid)
    base_tree = {}
    for entry in git(root, "ls-tree", "-r", "-z", base).split(b"\x00"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        entry_mode, _, entry_oid = metadata.decode().split()
        if os.fsdecode(path) != STATE_PATH:
            base_tree[path] = (entry_mode, entry_oid)
    require_transition(index_tree == base_tree, "non-state index differs from approved baseline")
    # Index/worktree contradictions cannot hide a third, unapproved state payload.
    entries = git(root, "ls-files", "--stage", "-z", "--", STATE_PATH).split(b"\x00")
    entries = [e for e in entries if e]
    require_transition(len(entries) == 1, "state index entry missing/conflicted")
    mode, object_id, stage = entries[0].split(b"\t", 1)[0].decode().split()
    base_mode = git(root, "ls-tree", base, "--", STATE_PATH).decode().split()[0]
    require_transition(stage == "0" and mode == base_mode == "100644" and
                       not (root / STATE_PATH).stat().st_mode & 0o111, "state file/index mode mismatch")
    indexed = git(root, "cat-file", "blob", object_id)
    require_transition(sha256_bytes(indexed) in {record["before_sha256"], record["after_sha256"]},
                       "index contains an unapproved state")
    indexed_paths = {os.fsdecode(p) for p in git(root, "diff", "--cached", "--name-only", "-z", "--").split(b"\x00") if p}
    require_transition(indexed_paths <= {STATE_PATH}, "unrelated staged changes forbidden in transition mode")
    allowed, exceptions = load_scope_manifest(scope_path, root, base, _state_exception=True)
    require_transition(STATE_PATH in allowed and STATE_PATH in exceptions, "exact state scope exception required")
    changed = set(get_git_diff_files(root, base))
    require_transition(STATE_PATH in changed, "state transition has no candidate change")
    frozen = record["frozen_files"]
    require_transition(isinstance(frozen, dict) and set(frozen) == changed - {STATE_PATH},
                       "all preexisting Git changes must be exactly frozen; scope expansion rejected")
    require_transition(allowed == changed and exceptions <= changed,
                       "transition allowlist must equal actual state plus frozen scope")
    rules = parse_rules(git(root, "show", base + ":control/protected_paths.txt").decode())
    tracked_changes = {os.fsdecode(p) for p in git(root, "diff", "--name-only", "-z", base, "--").split(b"\x00") if p}
    for path, identity in frozen.items():
        validate_path(path)
        require_transition(not is_path_protected(path, ["control/", "TASK_PLAN.md", "RESEARCH_PLAN.md", "data/raw/"])[0],
                           "extra governance/protocol/raw mutation forbidden")
        require_transition(not (path in tracked_changes and is_path_protected(path, rules)[0]),
                           "extra tracked protected modification forbidden")
        require_transition(isinstance(identity, dict) and set(identity) == {"sha256", "mode"}
                           and type(identity["mode"]) is int and 0 <= identity["mode"] <= 0o777,
                           "frozen identity requires SHA-256 and exact permission mode")
        require_transition(sha256_bytes(checked_file(root / path)) == identity["sha256"]
                           and ((root / path).stat().st_mode & 0o777) == identity["mode"],
                           "frozen baseline fingerprint/mode mismatch")
    # Raw physical files, not Git clean-filter/index-cache output, are authoritative here.
    known_paths = {os.fsdecode(path) for path in base_tree} | {STATE_PATH} | set(frozen)
    for path, (entry_mode, entry_oid) in base_tree.items():
        name = os.fsdecode(path)
        validate_path(name)
        require_transition(entry_mode in {"100644", "100755"}, "non-regular tracked files unsupported")
        if name in frozen:
            continue
        physical = root / name
        require_transition(checked_file(physical) == git(root, "cat-file", "blob", entry_oid)
                           and (physical.stat().st_mode & 0o111) == (0o111 if entry_mode == "100755" else 0)
                           and not physical.stat().st_mode & 0o7000,
                           "physical tracked file differs from approved baseline: " + name)
    python_paths = list(root.glob("*.py")) + [p for directory in (root / "control", root / "tests") for p in directory.rglob("*.py")]
    for path in python_paths:
        require_transition(str(path.relative_to(root)) in known_paths,
                           "unapproved executable Python under root/control/tests")
    print("State transition VERIFIED (read-only): " + task + " -> GATED; no state was written")
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
    parser.add_argument("--state-transition", help="External exact finalization approval JSON")
    parser.add_argument("--authorization-sha256", help="Digest pinned through trusted Researcher approval")
    parser.add_argument("--files", nargs="*", help="Diagnostic denylist check only (not a gate)")
    parser.add_argument("--rules", help="Policy override for explicit diagnostic --files only")
    parser.add_argument("--task")
    parser.add_argument("--check-outputs", action="store_true")
    args = parser.parse_args()
    try:
        root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
        transition_requested = args.state_transition is not None or args.authorization_sha256 is not None
        if transition_requested and (not args.state_transition or not args.authorization_sha256 or args.files is not None or args.rules or args.task or args.check_outputs):
            raise ScopeError("State transition requires both approval inputs and cannot use diagnostic/output modes")
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
            if transition_requested:
                allowed, exceptions = validate_state_transition(root, args.base, args.scope_manifest, args.state_transition, args.authorization_sha256)
            else:
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
