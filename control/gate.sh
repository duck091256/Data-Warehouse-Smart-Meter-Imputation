#!/usr/bin/env bash
# ==============================================================================
# control/gate.sh — Research Quality & Governance Gate
# ==============================================================================
# Runs mandatory invariant, scope, protocol hash, and control test checks.
# If any condition fails, outputs GATE = FAIL and exits with non-zero status.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "============================================================"
echo " Starting Research Control Gate Check"
echo " Time: $(date -u '+%Y-%m-%d %H:%M:%SZ')"
echo " Repo: ${REPO_ROOT}"
echo "============================================================"

# Flag to track overall failure
GATE_FAILED=0

fail_gate() {
  local reason="$1"
  echo "" >&2
  echo "[GATE ERROR] ${reason}" >&2
  GATE_FAILED=1
}

# ------------------------------------------------------------------------------
# 1. Repository Path & Basic Structure Validation
# ------------------------------------------------------------------------------
echo ""
echo "[1/5] Validating repository structure..."
if [[ ! -d "${REPO_ROOT}/.git" ]]; then
  fail_gate "Repository is not a valid git working tree (.git missing)."
fi

if [[ ! -f "${REPO_ROOT}/TASK_PLAN.md" ]]; then
  fail_gate "Missing required protocol specification: TASK_PLAN.md"
fi

if [[ ! -d "${REPO_ROOT}/control" ]]; then
  fail_gate "Missing required governance directory: control/"
fi

echo "  -> Repository structure check OK."

# ------------------------------------------------------------------------------
# 2. Scope & Protected Paths Enforcement
# ------------------------------------------------------------------------------
echo ""
echo "[2/5] Checking scope against protected paths..."
if ! python3 "${SCRIPT_DIR}/check_scope.py" --repo-root "${REPO_ROOT}"; then
  fail_gate "Scope check failed! Protected paths have been modified."
fi
echo "  -> Scope check OK."

# ------------------------------------------------------------------------------
# 3. Protocol Hash Verification
# ------------------------------------------------------------------------------
echo ""
echo "[3/5] Verifying protocol file hashes..."
if [[ -f "${SCRIPT_DIR}/protocol_hashes.txt" ]]; then
  if ! bash "${SCRIPT_DIR}/protocol_hash.sh" --verify; then
    fail_gate "Protocol hash verification failed! Protocol was modified unauthorizedly."
  fi
  echo "  -> Protocol integrity OK."
else
  echo "  -> Note: protocol_hashes.txt not found yet. Generating initial manifest..."
  bash "${SCRIPT_DIR}/protocol_hash.sh" --save
  echo "  -> Protocol hash manifest generated."
fi

# ------------------------------------------------------------------------------
# 4. Task State Machine Validation
# ------------------------------------------------------------------------------
echo ""
echo "[4/5] Validating task state machine..."
if ! python3 "${SCRIPT_DIR}/validate_state.py" --state-file "${SCRIPT_DIR}/task_state.yaml"; then
  fail_gate "Task state validation or progression order failed."
fi
echo "  -> Task state machine OK."

# ------------------------------------------------------------------------------
# 5. Control-Layer Automated Tests
# ------------------------------------------------------------------------------
echo ""
echo "[5/5] Running control-layer test suite..."
if [[ -f "${REPO_ROOT}/tests/test_control_layer.py" ]]; then
  if ! pytest "${REPO_ROOT}/tests/test_control_layer.py" -q; then
    fail_gate "Control layer tests failed."
  fi
  echo "  -> Control-layer tests OK."
else
  fail_gate "Missing tests/test_control_layer.py"
fi

# ------------------------------------------------------------------------------
# Final Verdict
# ------------------------------------------------------------------------------
echo ""
echo "============================================================"
if [[ ${GATE_FAILED} -ne 0 ]]; then
  echo "RESULT: GATE = FAIL"
  echo "============================================================"
  exit 1
else
  echo "RESULT: GATE = PASS"
  echo "============================================================"
  exit 0
fi
