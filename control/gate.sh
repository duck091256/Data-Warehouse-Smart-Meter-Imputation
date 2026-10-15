#!/usr/bin/env bash
# Read-only control verification, not scientific acceptance or integration authority.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"
# Repository redirects from an interactive shell must not select another index.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
export GIT_OPTIONAL_LOCKS=0
export GIT_NO_REPLACE_OBJECTS=1
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
BASE=""
SCOPE_MANIFEST=""
TRANSITION=""
AUTHORIZATION_SHA256=""
usage() { echo "Usage: gate.sh --base FULL_SHA --scope-manifest EXTERNAL_APPROVED_JSON [--state-transition EXTERNAL_JSON --authorization-sha256 PINNED_SHA256]"; }
while [[ $# -gt 0 ]]; do
  case "$1" in
    --base|--scope-manifest|--state-transition|--authorization-sha256)
      if [[ $# -lt 2 || -z "$2" ]]; then usage >&2; exit 1; fi
      case "$1" in
        --base) BASE="$2" ;;
        --scope-manifest) SCOPE_MANIFEST="$2" ;;
        --state-transition) TRANSITION="$2" ;;
        --authorization-sha256) AUTHORIZATION_SHA256="$2" ;;
      esac
      shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 1 ;;
  esac
done
if [[ -z "$BASE" || -z "$SCOPE_MANIFEST" ]]; then usage >&2; exit 1; fi
TRANSITION_ARGS=()
PYTHON_ARGS=(-B)
TEST_ARGS=()
if [[ -n "$TRANSITION" || -n "$AUTHORIZATION_SHA256" ]]; then
  if [[ -z "$TRANSITION" || -z "$AUTHORIZATION_SHA256" ]]; then usage >&2; exit 1; fi
  PYTHON_ARGS=(-I -B)
  TEST_ARGS=(--noconftest --assert=plain)
  TRANSITION_ARGS=(--state-transition "$TRANSITION" --authorization-sha256 "$AUTHORIZATION_SHA256")
fi
cd "$REPO_ROOT"
GATE_FAILED=0
run_check() {
  local label="$1"
  shift
  if "$@"; then
    echo "[OK] $label"
  else
    echo "[FAIL] $label" >&2
    GATE_FAILED=1
    if [[ -n "$TRANSITION" ]]; then
      echo "RESULT: GATE = FAIL"
      exit 1
    fi
  fi
}
structure() {
  local top
  top="$(git -C "$REPO_ROOT" rev-parse --show-toplevel)" || return 1
  [[ "$(cd "$top" && pwd -P)" == "$(pwd -P)" ]] &&
    [[ "$(git -C "$REPO_ROOT" rev-parse --is-inside-work-tree)" == true ]] &&
    [[ -f TASK_PLAN.md && -d control ]]
}
echo "Control verification: $REPO_ROOT"
run_check "Repository structure" structure
run_check "Approved Git scope" "$PYTHON" "${PYTHON_ARGS[@]}" "$SCRIPT_DIR/check_scope.py" \
  --repo-root "$REPO_ROOT" --base "$BASE" --scope-manifest "$SCOPE_MANIFEST" "${TRANSITION_ARGS[@]}"
# Never bootstrap or rewrite a manifest during verification.
run_check "Protocol integrity" bash "$SCRIPT_DIR/protocol_hash.sh" --verify
run_check "Task state snapshot" "$PYTHON" "${PYTHON_ARGS[@]}" "$SCRIPT_DIR/validate_state.py" \
  --state-file "$SCRIPT_DIR/task_state.yaml"
run_check "Control regression tests" "$PYTHON" "${PYTHON_ARGS[@]}" -m pytest \
  "$REPO_ROOT/tests/test_control_layer.py" -q -p no:cacheprovider "${TEST_ARGS[@]}"
if [[ -f "$REPO_ROOT/tests/test_state_transition.py" ]] || git cat-file -e "$BASE:tests/test_state_transition.py" 2>/dev/null; then
  run_check "State transition regression tests" "$PYTHON" "${PYTHON_ARGS[@]}" -m pytest \
    "$REPO_ROOT/tests/test_state_transition.py" -q -p no:cacheprovider "${TEST_ARGS[@]}"
fi
if [[ "$GATE_FAILED" -ne 0 ]]; then
  echo "RESULT: GATE = FAIL"
  exit 1
fi
echo "RESULT: GATE = PASS"
echo "Control checks only; no research acceptance, state transition or integration authorization."
