#!/usr/bin/env bash
# Strict SHA-256 protocol manifest; verification never writes repository files.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HASH_FILE="${SCRIPT_DIR}/protocol_hashes.txt"
PROTOCOL_FILES=("RESEARCH_PLAN.md" "TASK_PLAN.md" "control/protected_paths.txt")
compute_hashes() {
  local file
  for file in "${PROTOCOL_FILES[@]}"; do
    [[ -f "$REPO_ROOT/$file" ]] || { echo "[FAIL] Missing protocol file: $file" >&2; return 1; }
  done
  (cd "$REPO_ROOT" && sha256sum -- "${PROTOCOL_FILES[@]}")
}
if [[ $# -gt 1 ]]; then echo "Too many arguments" >&2; exit 1; fi
case "${1:-}" in
  "") echo "Protocol file hashes (SHA-256):"; compute_hashes ;;
  --help|-h) echo "Usage: protocol_hash.sh [--verify | --save]" ;;
  --save)
    # Administrative operation requiring separate human approval. Gate never calls this.
    hashes="$(compute_hashes)"
    { echo "# Protocol Hash Manifest — Auto-generated";
      echo "# Generated at: $(date -u '+%Y-%m-%d %H:%M:%SZ')";
      echo "$hashes"; } > "$HASH_FILE"
    echo "Saved protocol hashes to $HASH_FILE" ;;
  --verify)
    [[ -f "$HASH_FILE" ]] || { echo "[FAIL] Missing protocol hash manifest" >&2; exit 1; }
    declare -A expected=()
    entry_count=0
    while IFS= read -r line || [[ -n "$line" ]]; do
      [[ "$line" =~ ^[[:space:]]*$ || "$line" =~ ^[[:space:]]*# ]] && continue
      if [[ ! "$line" =~ ^([0-9a-f]{64})[[:space:]]+([^[:space:]]+)$ ]]; then
        echo "[FAIL] Malformed protocol manifest entry" >&2; exit 1
      fi
      sha="${BASH_REMATCH[1]}"
      file="${BASH_REMATCH[2]}"
      case "$file" in RESEARCH_PLAN.md|TASK_PLAN.md|control/protected_paths.txt) ;;
        *) echo "[FAIL] Unexpected protocol manifest path: $file" >&2; exit 1 ;; esac
      [[ ! -v "expected[$file]" ]] || { echo "[FAIL] Duplicate manifest path: $file" >&2; exit 1; }
      expected["$file"]="$sha"
      entry_count=$((entry_count + 1))
    done < "$HASH_FILE"
    [[ "$entry_count" -eq ${#PROTOCOL_FILES[@]} ]] || {
      echo "[FAIL] Manifest must contain every required protocol file exactly once" >&2; exit 1;
    }
    for file in "${PROTOCOL_FILES[@]}"; do
      [[ -f "$REPO_ROOT/$file" ]] || { echo "[FAIL] Missing protocol file: $file" >&2; exit 1; }
      actual="$(sha256sum -- "$REPO_ROOT/$file")"
      actual="${actual%% *}"
      [[ "$actual" == "${expected[$file]}" ]] || { echo "[FAIL] Protocol hash mismatch: $file" >&2; exit 1; }
      echo "[OK] $file"
    done
    echo "Protocol verification PASSED" ;;
  *) echo "Unknown option: $1" >&2; exit 1 ;;
esac
