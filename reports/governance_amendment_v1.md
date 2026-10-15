# Governance Amendment v1 — READY_FOR_GOVERNANCE_REVIEW

Implementation/test authorization only. Preserved detached workspace:
`/home/duck/.codex/worktrees/governance-transition-v1/data-warehousing`.
Approved base/HEAD: `fe21132f0a40863646bf23971cfca49a7444be67`.
No main integration, project commit/merge/push, actual P1-T5 transition or P1-T6 work.

## Exact change scope

- Modified `control/check_scope.py`: separate pinned, read-only FINALIZE_TASK verification;
  default canonical-state exception refusal retained. Git replacement reads disabled.
- Modified `control/gate.sh`: optional transition arguments, isolated/fail-fast transition checks,
  mandatory transition regressions when present in candidate/base; existing default checks retained.
- Modified `control/README.md`: approval/evidence schemas, trust boundaries and safe operator workflow.
- Added `tests/test_state_transition.py`: 77 synthetic compatibility/security regressions.
- Added `reports/governance_amendment_v1.md`: this checkpoint.

Existing `tests/test_control_layer.py` assertions, `control/validate_state.py`, canonical state,
protocol, policy/hash manifests and Research Task Orchestrator are unchanged. No scientific
protocol definitions or acceptance criteria were amended.

## State-machine/dependency findings

Canonical current_task is P1-T4 because its approved human-gate checkpoint was recorded, while
later P1-T5 recording stopped at the unconditional immutable-state exception in the old checker.
CONTROL_LAYER and every predecessor P1-T1 through P1-T4 are already GATED. No preceding transition
is missing. P1-T5 and P1-T6 remain BLOCKED/NOT_RUN/NOT_REQUIRED. No mandatory commit/tracking rule
for scientific P1-T5 acceptance was found in the task protocol; the old blocker was machine policy.

All 62 final-evidence package entries were hash/size checked, plus actual P1-T5 production,
config, implementation, test and state identities against FINAL_GATE.json. This verifies identity,
not a fresh ETL/scientific audit. The prior integration checkpoint records Researcher acceptance;
this implementation request grants no new canonical state-write authority.

The existing validator checks snapshots/linear prerequisite ordering, not transition history.
The new narrow rule permits explicitly accepted finalization of one task from BLOCKED, READY,
IN_PROGRESS, TEST_PASSED or AUDIT_PASSED to GATED/PASSED/PASSED, only with all prior tasks present
and GATED and the pointer at the target or immediate gated predecessor. BLOCKED -> GATED handles
recording lag after final acceptance; it does not infer science or skip final-gate evidence.
Other transitions, failed/already-GATED tasks and any next-task changes remain forbidden.

## Authorization and safety contract

Default P0a scope schema and immutable rejection remain unchanged. Opt-in finalization requires:

```bash
"$PYTHON" -I -B control/check_scope.py --base "$BASE_SHA" --scope-manifest "$SCOPE_JSON" \
  --state-transition "$TRANSITION_JSON" --authorization-sha256 "$RESEARCHER_PIN"
PYTHON="$PYTHON" bash control/gate.sh --base "$BASE_SHA" --scope-manifest "$SCOPE_JSON" \
  --state-transition "$TRANSITION_JSON" --authorization-sha256 "$RESEARCHER_PIN"
```

The Researcher/operator must pin the exact record digest through actual human authorization,
not accept a worker's recomputed pin as approval. The strict external record binds task, full
HEAD/base, exact state before/after byte hashes, complete semantic delta, exact scope-file hash,
actual human-approval reference/evidence, final-acceptance evidence and validity timestamps.
Only the target status/test/audit and current pointer/stage may change. Frozen existing Git paths
bind exact bytes/permissions; mode rejects unused scope expansion, unrelated staging and extra
control/protocol/raw/tracked-protected mutations. A previously accepted untracked protected test
can only be preserved with its pinned identity and historical exact exception.

Gate verifies source/control trust before running downstream checks, forbids hidden index flags,
filters/fsmonitor callbacks and replacement-object identity substitution, checks physical tracked
bytes/Git executable flags, and uses isolated Python with verified-source compilation and cold
critical caches. Default aggregated diagnostics remain; transition checks fail immediately.
No state/approval/hash manifest is written, token consumed or research experiment run by the gate.

## Actual verification and evidence

Evidence directory: `/tmp/governance-amendment-v1/`.

- Executor stable regression command: `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
  <canonical .venv>/bin/python -B -m pytest tests/test_control_layer.py tests/test_state_transition.py
  -q -p no:cacheprovider`. Result **145 passed in 16.32s**, including **68 unchanged** and **77 new**.
  Full log: `full-regressions-final-stable.log`.
- Fresh independent review: **145 passed in 15.89s**, plus **7 adversarial probes passed**.
  Report: `independent-review/final-review.md`. Reviewed implementation hashes were stable.
- Mandatory development gate: **PASS**; **68 passed in 6.24s**, **77 passed in 9.94s**.
  Log `development-gate.log`; external exact-scope authorization `development-scope.json`.
  Command: `PYTHON=<canonical .venv>/bin/python bash control/gate.sh --base
  fe21132f0a40863646bf23971cfca49a7444be67 --scope-manifest
  /tmp/governance-amendment-v1/development-scope.json`.
- Preserved positive/negative gate demonstration: `demonstrate_gate.py`,
  `synthetic-gate-proof.json`, `synthetic-gate-demonstration/{approved,default_deny,wrong_approval_digest}.log`.
  An actual disposable **P1-T1 fixture** candidate passes the mandatory gate with exact approval;
  default mode and incorrect operator digest both return 1/FAIL. Gate leaves fixture state bytes
  unchanged in every case. The synthetic gate uses the existing one-test fixture stub to avoid
  recursive test execution; the full real suites run separately above. No real P1-T5 transition.
- Coverage includes invalid approval/role/decision, hashes, scope/evidence fingerprints, expiry,
  stale base, wrong task, missing prerequisites, unrelated state deltas, state/index contradictions,
  scope expansion, extra protected writes, frozen drift and runtime/code-identity attacks.
- `git diff --check` and shell syntax validation PASS. Final scope checks cover these exact five
  paths. Original validator/test/protocol/state/policy bytes equal BASE.
- `canonical-preservation.json` and `preservation-after.json`: 89 canonical files/artifacts retain
  hashes; main HEAD/status unchanged, including installed orchestrator. Neither actual canonical
  nor isolated task_state.yaml was modified.

Independent review found and reproduced hidden-index bypass, unsafe continuation after rejected
scope, ignored bytecode/dependency execution and Git filtering/replacement tricks; fixes were
regression-tested and independently rechecked. A newly authored assertion that Git100644 implies
physical0644 was corrected with Auditor approval: Git stores executable flags, not umask-specific
write bits. Existing tests were not weakened; frozen approvals still bind exact permission bits.

## Minimal safe integration procedure — NOT executed

1. Researcher reviews and separately authorizes integration of these exact five files, including
   protected checker/gate/docs and the new test. Revalidate target collisions, originals and dirty
   accepted P1-T5/orchestrator identities; preserve them with exact cumulative scope/hash checks.
2. Integrate only the reviewed governance files, run both regression suites and unchanged-mode
   mandatory gate against the explicitly approved development scope. Obtain independent review.
3. Establish the reviewed amended controls as a trusted Git baseline through **separately approved
   commit/integration**. Transition mode deliberately rejects uncommitted control-code differences.
   This is a trust requirement of the new mechanism, not a scientific P1-T5 commit prerequisite.
4. Revalidate P1-T5 final evidence and live state. Prepare proposed state bytes and acceptance wrapper
   externally; do not edit the original evidence package. Have Researcher approve exact task/delta,
   before/after hashes, scope, evidence, expiry and record digest for the new trusted baseline.
5. Only a separately authorized Integrator may apply those exact bytes. Run mandatory transition-mode
   gate and independent review on that candidate. Commit/merge/push require their own authorization.
   P1-T6 remains unchanged; readiness/execution need a later explicit decision.

## Limits and remaining authorization

Approval hashes bind bytes, not cryptographic human identity. The operator/reviewer must authenticate
actual approval/pin provenance and scientific evidence sufficiency; a role string/JSON wrapper alone
is not authority. The selected Python environment, command tools and executable checker/gate must be
trusted. This is an offline, operator-trusted verifier, not an OS sandbox or signing service.
Rechecking the identical candidate within its approval window is idempotent; read-only gates do not
maintain a spent-token database. A new HEAD/state/scope/evidence/expired window requires fresh approval.
Concurrent malicious writers and ignored/external data need filesystem isolation/read-only controls.
Transformed, sparse, symlink/submodule or warm critical-cache workspaces intentionally fail closed;
no automatic cleanup is performed. Other scientific/state transitions are unsupported by this v1.

Remaining: explicit governance integration/trusted-baseline authorization, followed by exact P1-T5
transition authorization. None is implied by this implementation checkpoint. STOP at
**READY_FOR_GOVERNANCE_REVIEW**; isolated changes and evidence are preserved.
