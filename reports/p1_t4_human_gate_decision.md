# P1-T4 Human-Gate Decision

- **Decision:** APPROVED by the researcher on 2026-10-14 (Asia/Ho_Chi_Minh).
- **Scope:** P1-T4 human gate only. This decision does not start or approve implementation of P1-T5.
- **Recorded state:** P1-T4 `GATED`, test `PASSED`, audit `PASSED`; `current_task` is P1-T4. P1-T5 remains `BLOCKED`.

## Evidence reviewed

1. `audits/AUDIT_P1_T4_REPAIR.md`, §§5, 7–15, 18: independent post-repair audit `PASS`, 13,981,597 rows, 79 row groups, exactly 1,143 `has_issue` FALSE-to-TRUE transitions at issue starts on grid boundaries, no reverse transitions, and historical test/control-gate results.
2. `data/interim/readings_15min_flagged.parquet` in the original `main` checkout: current SHA-256 `c672d5a4efc6cb636708480675e6a2947c436373b05f1bfb8e3307dc9299d279`, matching the post-repair audit. `data/interim/readings_15min.parquet` SHA-256 `f50a2ff27b142a895a8cabfbc0bcf3750aad28d5dcd5af2cb51a13628dce22dd` also matches its audit. Both contain 13,981,597 rows and 79 row groups.
3. `tests/test_P1_T4.py`: 16/16 passed in 29.69 seconds in the original `main` checkout on 2026-10-14, with bytecode and pytest cache disabled. The test includes boundary, point-event, four-quadrant, and 1,143-transition regression checks.
4. `TASK_PLAN.md`, P1-T4 acceptance criteria, and `RESEARCH_PLAN.md`, §8: the ratified interval-intersection rule and quantitative yields match the audited implementation and output.
5. `control/task_state.yaml` and `control/validate_state.py`: all predecessors through P1-T3 are `GATED`; the validator permits P1-T4 to be `GATED`. The previous `BLOCKED/NOT_RUN` record was stale relative to completed tests and audit. The researcher explicitly approved its reconciliation.

## Limits

The 65-test suite and `control/gate.sh` results cited by the audit are historical; neither was rerun for this decision. The Codex worktree lacks interim data and stores `.git` as a file, while `gate.sh` requires `.git` to be a directory. The original `main` checkout has the audited artifacts and a `.git` directory. The pre-repair artifact is not present at the production path, so its identity was not reverified now.

## Protected-path authorization for checkpoint integration

- **Authority and date:** Direct researcher instruction in the integration chat, 2026-10-14 (Asia/Ho_Chi_Minh).
- **Approval:** "Tôi cho phép thay đổi `control/task_state.yaml` chỉ đối với checkpoint P1-T4 đã được human gate phê duyệt." The researcher also explicitly authorized a dedicated branch, checkpoint commit, and integration into `main`.
- **Authorized state delta:** `current_task: P1-T3 -> P1-T4`; P1-T4 `status: BLOCKED -> GATED`, `test: NOT_RUN -> PASSED`, `audit: NOT_REQUIRED -> PASSED`. P1-T5 remains `BLOCKED/NOT_RUN/NOT_REQUIRED`; all other task entries and the protocol version are unchanged.
- **File boundary:** Only `control/task_state.yaml` and this report are approved for integration.
- **Independent scope evidence:** The protected-path rules classify `control/task_state.yaml` under `control/`; this direct researcher approval is the authority for the administrative exception. No additional exception procedure was found in the repository governance documents reviewed for integration.
- **Gate distinction:** This approval is independent of `control/gate.sh`. The scope checker examines staged and unstaged differences, not committed history; a clean-tree gate result does not itself authorize or audit this protected-path change. Protection rules, gate scripts, protocol documents, tests, and raw data are not changed by this checkpoint.
