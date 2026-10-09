#!/usr/bin/env bash
# ==============================================================================
# control/protocol_hash.sh — Deterministic Protocol File Hasher & Verifier
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HASH_FILE="${SCRIPT_DIR}/protocol_hashes.txt"

# Candidate protocol files to track
PROTOCOL_CANDIDATES=(
  "TASK_PLAN.md"
  "RESEARCH_PLAN.md"
  "control/protected_paths.txt"
)

compute_hashes() {
  local target_files=()
  for rel_file in "${PROTOCOL_CANDIDATES[@]}"; do
    if [[ -f "${REPO_ROOT}/${rel_file}" ]]; then
      target_files+=("${rel_file}")
    fi
  done

  if [[ ${#target_files[@]} -eq 0 ]]; then
    echo "Warning: No protocol files found in repository." >&2
    return 1
  fi

  # Sort files to guarantee deterministic order
  IFS=$'\n' sorted_files=($(sort <<<"${target_files[*]}"))
  unset IFS

  for rel_file in "${sorted_files[@]}"; do
    local abs_path="${REPO_ROOT}/${rel_file}"
    local sha
    sha=$(sha256sum "${abs_path}" | awk '{print $1}')
    echo "${sha}  ${rel_file}"
  done
}

ACTION="print"
if [[ $# -gt 0 ]]; then
  case "$1" in
    --save)
      ACTION="save"
      ;;
    --verify)
      ACTION="verify"
      ;;
    --help|-h)
      echo "Usage: $0 [--save | --verify]"
      echo "  (default): Calculate and display deterministic hashes for protocol files."
      echo "  --save   : Record current protocol hashes to control/protocol_hashes.txt"
      echo "  --verify : Verify that current protocol files match control/protocol_hashes.txt"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
fi

cd "${REPO_ROOT}"

if [[ "${ACTION}" == "print" ]]; then
  echo "Protocol file hashes (SHA-256):"
  compute_hashes
elif [[ "${ACTION}" == "save" ]]; then
  echo "# Protocol Hash Manifest — Auto-generated" > "${HASH_FILE}"
  echo "# Generated at: $(date -u '+%Y-%m-%d %H:%M:%SZ')" >> "${HASH_FILE}"
  compute_hashes >> "${HASH_FILE}"
  echo "Saved protocol hashes to ${HASH_FILE}"
elif [[ "${ACTION}" == "verify" ]]; then
  if [[ ! -f "${HASH_FILE}" ]]; then
    echo "Error: Protocol hash manifest not found at ${HASH_FILE}. Run with --save first." >&2
    exit 1
  fi

  echo "Verifying protocol integrity against manifest..."
  MISMATCH=0
  while read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue

    expected_sha=$(echo "$line" | awk '{print $1}')
    rel_file=$(echo "$line" | awk '{print $2}')

    if [[ ! -f "${REPO_ROOT}/${rel_file}" ]]; then
      echo "[FAIL] Missing protocol file: ${rel_file}" >&2
      MISMATCH=1
      continue
    fi

    actual_sha=$(sha256sum "${REPO_ROOT}/${rel_file}" | awk '{print $1}')
    if [[ "${expected_sha}" != "${actual_sha}" ]]; then
      echo "[FAIL] Protocol file modified: ${rel_file}" >&2
      echo "       Expected: ${expected_sha}" >&2
      echo "       Actual:   ${actual_sha}" >&2
      MISMATCH=1
    else
      echo "[OK] ${rel_file} matches (${actual_sha:0:12}...)"
    fi
  done < "${HASH_FILE}"

  if [[ ${MISMATCH} -ne 0 ]]; then
    echo "Protocol verification FAILED: Unauthorized modifications detected!" >&2
    exit 1
  fi
  echo "Protocol verification PASSED: All protocol files are intact."
  exit 0
fi
