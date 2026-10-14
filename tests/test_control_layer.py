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


# P0a regressions use disposable repositories only. Commits/worktrees below are
# fixture history, never project history or existing user worktrees.
import hashlib
import json
import shutil

from control.check_scope import ScopeError, get_git_diff_files


def clean_git_env():
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("GIT_"):
            env.pop(key)
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    return env


def fixture_git(root, *args):
    return subprocess.run(
        ["git", "-c", "core.hooksPath=" + os.devnull, "-C", str(root), *args],
        check=True, capture_output=True, text=True, env=clean_git_env()
    ).stdout.strip()


def fixture_commit(root):
    fixture_git(root, "add", "--all")
    fixture_git(root, "-c", "user.name=Scope Fixture", "-c",
                "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
    return fixture_git(root, "rev-parse", "HEAD")


def write_approval(path, base, allowed, exceptions=()):
    path.write_text(json.dumps({
        "base_commit": base, "authority": "P0a regression fixture approval",
        "allowed_files": list(allowed), "protected_exceptions": list(exceptions)
    }), encoding="utf-8")
    return path


@pytest.fixture
def git_fixture(tmp_path):
    repo = tmp_path / "repository with spaces"
    repo.mkdir()
    fixture_git(repo, "init", "-q", "--initial-branch=main")
    (repo / "control").mkdir()
    (repo / "tests").mkdir()
    for name in ("gate.sh", "check_scope.py", "protocol_hash.sh", "validate_state.py"):
        shutil.copyfile(REPO_ROOT / "control" / name, repo / "control" / name)
    (repo / "control/protected_paths.txt").write_text(
        "TASK_PLAN.md\nRESEARCH_PLAN.md\ndata/raw/\ntests/\ncontrol/\n")
    (repo / "TASK_PLAN.md").write_text("fixture protocol\n")
    (repo / "RESEARCH_PLAN.md").write_text("fixture research\n")
    (repo / "control/task_state.yaml").write_text(
        'protocol_version: v1.1\ncurrent_stage: SETUP\ncurrent_task: CONTROL_LAYER\n'
        'tasks:\n  CONTROL_LAYER:\n    status: GATED\n')
    (repo / "tests/test_control_layer.py").write_text("def test_fixture():\n    assert True\n")
    lines = []
    for name in ("TASK_PLAN.md", "RESEARCH_PLAN.md", "control/protected_paths.txt"):
        digest = hashlib.sha256((repo / name).read_bytes()).hexdigest()
        lines.append(f"{digest}  {name}\n")
    (repo / "control/protocol_hashes.txt").write_text("".join(lines))
    (repo / "ordinary.txt").write_text("baseline\n")
    base = fixture_commit(repo)
    return repo, base


def scope_cli(repo, base, manifest, *extra):
    return subprocess.run(
        [sys.executable, "-B", str(repo / "control/check_scope.py"),
         "--repo-root", str(repo), "--base", base, "--scope-manifest", str(manifest), *extra],
        capture_output=True, text=True, env=clean_git_env(), cwd=repo
    )


def gate_cli(repo, base, manifest, **env_changes):
    env = clean_git_env()
    env["PYTHON"] = sys.executable
    env.update(env_changes)
    return subprocess.run(
        ["bash", str(repo / "control/gate.sh"), "--base", base,
         "--scope-manifest", str(manifest)], capture_output=True, text=True,
        env=env, cwd=repo.parent
    )


@pytest.mark.parametrize("layer", ["committed", "staged", "unstaged", "untracked"])
def test_scope_covers_every_git_layer(git_fixture, tmp_path, layer):
    repo, base = git_fixture
    path = "new.txt" if layer == "untracked" else "ordinary.txt"
    (repo / path).write_text("changed\n")
    if layer == "committed":
        fixture_commit(repo)
    elif layer == "staged":
        fixture_git(repo, "add", path)
    assert path in get_git_diff_files(repo, base)
    approval = write_approval(tmp_path / "approval.json", base, ["other.txt"])
    rejected = scope_cli(repo, base, approval)
    assert rejected.returncode == 1
    assert "outside approved allowlist" in rejected.stdout
    write_approval(approval, base, [path])
    assert scope_cli(repo, base, approval).returncode == 0


def test_union_includes_all_layers_at_once(git_fixture):
    repo, base = git_fixture
    (repo / "committed.txt").write_text("committed")
    fixture_commit(repo)
    (repo / "staged.txt").write_text("staged")
    fixture_git(repo, "add", "staged.txt")
    (repo / "ordinary.txt").write_text("unstaged")
    (repo / "untracked.txt").write_text("untracked")
    assert set(get_git_diff_files(repo, base)) == {
        "committed.txt", "staged.txt", "ordinary.txt", "untracked.txt"}


@pytest.mark.parametrize("layer", ["committed", "staged", "unstaged"])
def test_deleted_paths_are_checked(git_fixture, layer):
    repo, base = git_fixture
    (repo / "ordinary.txt").unlink()
    if layer == "staged":
        fixture_git(repo, "add", "-u")
    elif layer == "committed":
        fixture_commit(repo)
    assert "ordinary.txt" in get_git_diff_files(repo, base)


@pytest.mark.parametrize("layer", ["committed", "staged", "unstaged"])
def test_renames_check_old_and_new_path(git_fixture, tmp_path, layer):
    repo, base = git_fixture
    (repo / "tests/test_control_layer.py").rename(repo / "renamed.py")
    if layer == "committed":
        fixture_commit(repo)
    elif layer == "staged":
        fixture_git(repo, "add", "--all")
    changed = get_git_diff_files(repo, base)
    assert "tests/test_control_layer.py" in changed and "renamed.py" in changed
    approval = write_approval(tmp_path / "approval.json", base,
                              ["tests/test_control_layer.py", "renamed.py"])
    result = scope_cli(repo, base, approval)
    assert result.returncode == 1
    assert "tests/test_control_layer.py" in result.stdout


@pytest.mark.parametrize("name", [' spaced name.txt ', 'quote"name.txt',
                                  "Unicode-điện.txt", "line\nbreak.txt", "tab\tname.txt"])
def test_nul_safe_paths(git_fixture, tmp_path, name):
    repo, base = git_fixture
    (repo / name).write_text("new")
    assert get_git_diff_files(repo, base) == [name]
    approval = write_approval(tmp_path / "approval.json", base, [name])
    assert scope_cli(repo, base, approval).returncode == 0


def test_exact_protected_exception_is_required(git_fixture, tmp_path):
    repo, base = git_fixture
    path = "control/README.md"
    (repo / path).write_text("authorized governance update")
    approval = write_approval(tmp_path / "approval.json", base, [path])
    assert scope_cli(repo, base, approval).returncode == 1
    write_approval(approval, base, [path], [path])
    assert scope_cli(repo, base, approval).returncode == 0
    (repo / "control/unapproved.py").write_text("outside exception")
    assert scope_cli(repo, base, approval).returncode == 1


def test_base_policy_cannot_be_replaced_by_candidate(git_fixture, tmp_path):
    repo, base = git_fixture
    (repo / "control/protected_paths.txt").write_text("data/raw/\n")
    (repo / "tests/test_control_layer.py").write_text("changed")
    approval = write_approval(tmp_path / "approval.json", base,
        ["control/protected_paths.txt", "tests/test_control_layer.py"])
    result = scope_cli(repo, base, approval)
    assert result.returncode == 1
    assert "FORBIDDEN: 'tests/test_control_layer.py'" in result.stdout


@pytest.mark.parametrize("base_arg", ["HEAD", "HEAD~1", "0" * 40, "bad"])
def test_invalid_or_symbolic_base_fails(git_fixture, tmp_path, base_arg):
    repo, base = git_fixture
    approval = write_approval(tmp_path / "approval.json", base_arg, ["ordinary.txt"])
    assert scope_cli(repo, base_arg, approval).returncode == 1


def test_nonancestor_base_fails(git_fixture, tmp_path):
    repo, base = git_fixture
    fixture_git(repo, "checkout", "--orphan", "other-history")
    # A distinct tree makes the orphan root different even when both commits
    # have the same author, message and second-resolution timestamp.
    (repo / "other-history.txt").write_text("independent root")
    unrelated = fixture_commit(repo)
    assert unrelated != base
    fixture_git(repo, "checkout", "main")
    for first, second in ((base, unrelated), (unrelated, base)):
        probe = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", first, second],
            capture_output=True, env=clean_git_env()
        )
        assert probe.returncode == 1
    approval = write_approval(tmp_path / "approval.json", unrelated, ["ordinary.txt"])
    assert scope_cli(repo, unrelated, approval).returncode == 1


def test_git_failure_is_not_empty_success(tmp_path, monkeypatch):
    with pytest.raises(ScopeError):
        get_git_diff_files(tmp_path, "0" * 40)
    monkeypatch.setenv("PATH", "")
    with pytest.raises(ScopeError):
        get_git_diff_files(tmp_path, "0" * 40)


@pytest.mark.parametrize("kind", ["missing", "empty", "malformed", "wrong_base", "in_checkout",
                                  "wildcard_exception", "immutable_exception", "traversal"])
def test_invalid_scope_inputs_fail(git_fixture, tmp_path, kind):
    repo, base = git_fixture
    approval = write_approval(tmp_path / "approval.json", base, ["ordinary.txt"])
    if kind == "missing":
        approval.unlink()
    elif kind == "empty":
        approval.write_text("")
    elif kind == "malformed":
        approval.write_text("{}")
    elif kind == "wrong_base":
        write_approval(approval, "0" * 40, ["ordinary.txt"])
    elif kind == "in_checkout":
        approval = write_approval(repo / "approval.json", base, ["ordinary.txt"])
    elif kind == "wildcard_exception":
        write_approval(approval, base, ["ordinary.txt"], ["control/"])
    elif kind == "immutable_exception":
        write_approval(approval, base, ["control/task_state.yaml"], ["control/task_state.yaml"])
    else:
        write_approval(approval, base, ["../outside"])
    assert scope_cli(repo, base, approval).returncode == 1


@pytest.mark.parametrize("kind", ["missing", "empty", "comments", "missing_entry", "duplicate",
                                  "malformed", "extra", "mismatch", "missing_protocol"])
def test_hash_manifest_fails_closed_without_writes(git_fixture, kind):
    repo, _ = git_fixture
    manifest = repo / "control/protocol_hashes.txt"
    original = manifest.read_text()
    if kind == "missing":
        manifest.unlink()
    elif kind == "empty":
        manifest.write_text("")
    elif kind == "comments":
        manifest.write_text("# comment only\n")
    elif kind == "missing_entry":
        manifest.write_text("\n".join(original.splitlines()[1:]))
    elif kind == "duplicate":
        manifest.write_text(original + original.splitlines()[0] + "\n")
    elif kind == "malformed":
        manifest.write_text(original + "not a valid entry\n")
    elif kind == "extra":
        manifest.write_text(original + "0" * 64 + "  unexpected.txt\n")
    elif kind == "mismatch":
        (repo / "TASK_PLAN.md").write_text("modified")
    else:
        (repo / "RESEARCH_PLAN.md").unlink()
    before = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    result = subprocess.run(["bash", str(repo / "control/protocol_hash.sh"), "--verify"],
                            capture_output=True, text=True, env=clean_git_env())
    assert result.returncode != 0
    assert "[FAIL]" in result.stderr
    assert "unbound variable" not in result.stderr
    after = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    assert after == before


@pytest.mark.parametrize("linked", [False, True])
def test_actual_gate_passes_regular_and_linked_worktree(git_fixture, tmp_path, linked):
    repo, base = git_fixture
    if linked:
        destination = tmp_path / "linked checkout"
        fixture_git(repo, "worktree", "add", "--detach", str(destination), base)
        repo = destination
        assert (repo / ".git").is_file()
    approval = write_approval(tmp_path / "approval.json", base, ["ordinary.txt"])
    result = gate_cli(repo, base, approval)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RESULT: GATE = PASS" in result.stdout
    assert not (repo / ".pytest_cache").exists()
    assert not list(repo.rglob("__pycache__"))
    assert fixture_git(repo, "status", "--porcelain") == ""


@pytest.mark.parametrize("kind", ["scope", "hash_missing", "hash_mismatch", "state", "tests"])
def test_actual_gate_fails_and_never_logs_failed_step_ok(git_fixture, tmp_path, kind):
    repo, base = git_fixture
    allowed = ["ordinary.txt"]
    exceptions = []
    label = {"scope": "Approved Git scope", "hash_missing": "Protocol integrity",
             "hash_mismatch": "Protocol integrity", "state": "Task state snapshot",
             "tests": "Control regression tests"}[kind]
    if kind == "scope":
        (repo / "outside.txt").write_text("not approved")
    elif kind == "hash_missing":
        (repo / "control/protocol_hashes.txt").unlink()
    elif kind == "hash_mismatch":
        (repo / "TASK_PLAN.md").write_text("changed")
    elif kind == "state":
        (repo / "control/task_state.yaml").write_text("invalid: state")
    else:
        path = "tests/test_control_layer.py"
        (repo / path).write_text("def test_failure():\n    assert False\n")
        allowed.append(path)
        exceptions.append(path)
    approval = write_approval(tmp_path / "approval.json", base, allowed, exceptions)
    result = gate_cli(repo, base, approval)
    assert result.returncode == 1
    assert "RESULT: GATE = FAIL" in result.stdout
    assert f"[FAIL] {label}" in result.stderr
    assert f"[OK] {label}" not in result.stdout
    if kind == "hash_missing":
        assert not (repo / "control/protocol_hashes.txt").exists()


def test_gate_uses_selected_python_not_standalone_pytest(git_fixture, tmp_path):
    repo, base = git_fixture
    bin_dir = tmp_path / "fake-bin"
    bin_dir.mkdir()
    fake = bin_dir / "pytest"
    fake.write_text("#!/bin/sh\nexit 88\n")
    fake.chmod(0o755)
    approval = write_approval(tmp_path / "approval.json", base, ["ordinary.txt"])
    result = gate_cli(repo, base, approval, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"])
    assert result.returncode == 0, result.stdout + result.stderr


def test_gate_requires_explicit_base_and_scope(git_fixture):
    repo, _ = git_fixture
    result = subprocess.run(["bash", str(repo / "control/gate.sh")],
                            capture_output=True, text=True, env=clean_git_env())
    assert result.returncode != 0 and "Usage:" in result.stderr


def test_unknown_output_spec_is_not_success(git_fixture, tmp_path):
    repo, base = git_fixture
    approval = write_approval(tmp_path / "approval.json", base, ["ordinary.txt"])
    result = scope_cli(repo, base, approval, "--check-outputs")
    assert result.returncode == 1
    assert "No output specification" in result.stderr


def test_missing_and_empty_policy_fail(git_fixture, tmp_path):
    repo, base = git_fixture
    policy = repo / "control/protected_paths.txt"
    policy.unlink()
    with pytest.raises(OSError):
        load_protected_rules(policy)
    policy.write_text("# no rules")
    with pytest.raises(ScopeError):
        load_protected_rules(policy)
    # A malformed policy committed into a proposed base must also fail closed.
    bad_base = fixture_commit(repo)
    approval = write_approval(tmp_path / "approval.json", bad_base, ["ordinary.txt"])
    assert scope_cli(repo, bad_base, approval).returncode == 1


@pytest.mark.parametrize("kind", ["duplicate_key", "extra_key", "duplicate_path", "blank_authority", "not_list"])
def test_scope_manifest_rejects_ambiguous_records(git_fixture, tmp_path, kind):
    repo, base = git_fixture
    approval = write_approval(tmp_path / "approval.json", base, ["ordinary.txt"])
    data = json.loads(approval.read_text())
    if kind == "duplicate_key":
        approval.write_text(approval.read_text().replace(
            '"authority":', '"authority": "other", "authority":', 1))
    else:
        if kind == "extra_key":
            data["unreviewed_override"] = True
        elif kind == "duplicate_path":
            data["allowed_files"].append("ordinary.txt")
        elif kind == "blank_authority":
            data["authority"] = " "
        else:
            data["allowed_files"] = "ordinary.txt"
        approval.write_text(json.dumps(data))
    assert scope_cli(repo, base, approval).returncode == 1


def test_checkout_and_real_index_cannot_be_redirected(git_fixture, tmp_path, monkeypatch):
    repo, base = git_fixture
    (repo / "staged.txt").write_text("index-only change")
    fixture_git(repo, "add", "staged.txt")
    # The worktree no longer has this file; it must still be found in the real index.
    (repo / "staged.txt").unlink()
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "unrelated-index"))
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "unrelated-git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path))
    assert "staged.txt" in get_git_diff_files(repo, base)


def test_repo_root_must_not_be_a_subdirectory(git_fixture):
    repo, base = git_fixture
    with pytest.raises(ScopeError, match="working-tree root"):
        get_git_diff_files(repo / "control", base)


def test_git_scope_cannot_use_diagnostic_overrides(git_fixture, tmp_path):
    repo, base = git_fixture
    approval = write_approval(tmp_path / "approval.json", base, ["ordinary.txt"])
    assert scope_cli(repo, base, approval, "--rules", str(repo / "control/protected_paths.txt")).returncode == 1
    assert scope_cli(repo, base, approval, "--files", "ordinary.txt").returncode == 1


def test_output_presence_rejects_directories(git_fixture):
    from control.check_scope import TASK_REQUIRED_OUTPUTS, verify_task_outputs
    repo, _ = git_fixture
    for rel in TASK_REQUIRED_OUTPUTS["P1-T1"]:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture")
    path = repo / TASK_REQUIRED_OUTPUTS["P1-T1"][0]
    path.unlink()
    path.mkdir()
    assert any("not a file" in error for error in verify_task_outputs(repo, "P1-T1"))
