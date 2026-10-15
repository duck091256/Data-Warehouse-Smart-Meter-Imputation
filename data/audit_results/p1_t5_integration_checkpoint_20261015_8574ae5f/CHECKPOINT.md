# P1-T5 final integration checkpoint — BLOCKED

Researcher Final Human Gate is accepted in the current direct instruction.
Approved HEAD, L48/seed731, input/config SHA-256, production artifacts, candidate
and the entire63-file final evidence package remain exact and verified.
Original evidence package was not modified or overwritten.

Canonical state remains unchanged:

```yaml
current_stage: P1
current_task: P1-T4
P1-T5:
  status: BLOCKED
  test: NOT_RUN
  audit: NOT_REQUIRED
```

The proposed P1-T5-only GATED/PASSED/PASSED snapshot passes state-machine
validation **in memory only**. No mandatory prior commit or tracked-artifact
requirement for P1-T5 was found in the authoritative protocol/state validator.

**Actual blocker:** `control/check_scope.py` includes `control/task_state.yaml`
in an unconditional immutable-exception list. Directly calling the existing
scope loader on the explicit Researcher-authorized Integrator proposal rejects
it with:

```text
P0a cannot authorize protocol, raw, canonical state or policy exceptions
```

The external proposal is preserved as `proposed_state_scope.json`.
Human authorization is real, but the current checker provides no accepted
Integrator route for this canonical file. Writing it would force a forbidden
path/failing scope gate. No canonical write, checker edit, alternate base,
policy override or weakened gate was attempted. Earlier historical guidance
about separately recording protected approvals does not bypass current P0a
machine enforcement.

Existing canonical-state control gate: **PASS**, **68 tests passed**,0failed;
this verifies the unchanged snapshot, not a proposed state transition.
Command and identities are in `checkpoint.json`; full output in
`control_gate.log`. Scope includes the prior accepted evidence and these five
new checkpoint files; the proposed state exception was deliberately not passed
as if it were an accepted exception.

Final Git status:

```text
?? configs/p1_t5.yaml
?? data/audit_results/p1_t5_final_gate_20261015_607ccd82/
?? data/audit_results/p1_t5_integration_checkpoint_20261015_8574ae5f/
?? etl/clean_segments.py
?? reports/p1_t5_log.md
?? tests/test_P1_T5.py
```

Tracked/index diffs are empty. HEAD remains
`fe21132f0a40863646bf23971cfca49a7444be67`. New files in this phase exist only
inside this checkpoint directory. No production/audit rerun, ETL/test/scientific
criteria/artifact mutation, commit/merge/push, P1-T6 execution or intervention
in the separate Research Task Orchestrator worktree occurred.

Remaining decision: narrowly authorize a machine-policy-compatible Integrator
state-recording mechanism. Current authority does not permit changing
`control/check_scope.py` or protected policy, and this task does not silently
expand that scope. Scientific acceptance is complete; only canonical recording
is blocked. **STOP.**
