# Independent final audit: P1-T5

- Auditor identity: `/root/p1_t5_independent_final_audit`; fresh reviewer context, no executor conversation inherited. Only explicit handoff facts were accepted as audit scope, then independently checked.
- Audit time: 2026-10-14T22:00:45.585713+00:00 through 2026-10-14T22:00:51.722316+00:00; report finalized 2026-10-14T22:02:18.685966+00:00.
- Reviewed Git commit: `fe21132f0a40863646bf23971cfca49a7444be67`.
- Conclusion: **VERIFIED — scientifically and technically READY_FOR_FINAL_GATE**.
- Final package control gate: **PENDING at audit time**, to be performed by parent after exact package file-list freeze and an external scope record grounded in Researcher authority.
- Human gate/state promotion: **NOT PERFORMED / NOT AUTHORIZED**. Canonical P1-T5 remains BLOCKED/NOT_RUN/NOT_REQUIRED; current_task remains P1-T4. This audit is evidence readiness, not GATED or whole-stage P1 acceptance.

## Authority and independent method

Read AGENTS.md, AUDITOR.md, Research Protocol v1.1 RESEARCH_PLAN.md, TASK_PLAN.md P1-T5 and P1 audit checklist, state, gate/check_scope implementation, protected policy, control README, candidate implementation/tests/log, preservation manifest and original production/reproduction evidence. Researcher authority is separately recorded in `../authorization_record.md`: L=48, seed731, inclusive UTC grid labels, length in 15-minute bins, maximal runs, existing production/reproduction sets, sidecar PENDING pre-warehouse. No protocol or assertion changes were made. The existing exact test exception is acknowledged and no new protected exception is inferred.

The final independent harness `independent_verify_v3.py` does **not import candidate implementation**. It reads every source row, derives clean eligibility directly from the three exclusion flags, checks agreement with GT and missing/value flags, then independently derives maximal run boundaries from boolean transitions and adjacent UTC timestamps. It compares the complete ordered segment table and complete per-meter statistics to actual live output, rather than using the expected counts as truth. Every retained source bin is checked. Counts are compared with acceptance targets only after exact oracle equality.

Command: `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -B data/audit_results/p1_t5_final_gate_20261015_607ccd82/audit/independent_verify_v3.py`.

Contemporaneous execution identity: `verification_v3_start.json`, recorded before execution; final harness SHA-256 `a872c5993d1d6c21c82c16f9b1e2c0d7fadace8c318a8e3c3cd0f960b238b5a7`. Machine evidence: `independent_verification_v3.json`, SHA-256 `cc3996c874ddb2e5ceddf8d8f72c9016b7d707139c61883327bdd60a14055d18`. Approved input SHA-256 `c672d5a4efc6cb636708480675e6a2947c436373b05f1bfb8e3307dc9299d279`.

## Invariants and scientific acceptance

| Check | Independent observed result | Verdict |
|---|---|---|
| Entire source census | 13,981,597 bins, 79 meters; 12,637,042 clean bins; 132,721 maximal clean runs | PASS |
| Complete eligible maximal-run extraction | 7,135 segments, 12,021,273 retained bins, exact full-table oracle match | PASS |
| L and inclusive UTC boundaries | min length48, max130717; exact UTC timestamp schema, 900s grid; every retained interval continuous and length=end-start/900s+1 | PASS |
| Corrected/issue/missing exclusion | No covered bin has any bad flag; all covered values finite; no corrected raw filenames; original timestamps within right-closed bins | PASS |
| Duplicates, ordering, overlap, maximality, completeness | Per-meter source timestamps strictly increasing; output exactly equals all maximal eligible runs, ordered deterministically | PASS |
| Per-meter statistics | Exact segment_count/total/min/median/max for all79 meters; zero-yield list empty; exact stats schema checked | PASS |
| No fabricated observations | Output stores segment coordinates/length only; references authenticated source bins without creating or transforming values | PASS |
| Leakage/split/scaler/feature checks | Candidate introduces no masking, features, normalization, training or splits | N/A for P1-T5 |
| Downstream warehouse/hierarchy/Meta_Run/DST source reconstruction | P1-T6+ warehouse ingestion and P1-T3/P1-T4 representation assurances outside this task | N/A for P1-T5 |

The acceptance threshold is configurable and explicitly approved as L=48. Forty-eight covered right-closed bins span12h even though first-to-last grid labels differ by11h45m. This extraction threshold is not a downstream context or mask-feasibility guarantee. The filtering discards 615,769 clean bins in runs shorter than48; selection toward longer uninterrupted periods remains a disclosed limitation. No performance selection or core-meter exclusion occurs.

Raw access/provenance boundary: no raw write was performed by this audit or candidate, no tracked baseline changes occurred, and the entire flagged source SHA matches the Researcher-approved P1-T4 dependency. `stat` reports `data/raw` as mode775; that is **not** evidence of OS-enforced read-only protection. This P1-T5 audit does not re-establish historical byte identity for the entire external raw collection. That assurance remains an upstream P1-T4/raw provenance boundary, not an unresolved P1-T5 scientific acceptance check. Do not convert Git scope or directory permissions into a broader raw-immutability claim.

## Reproducibility and provenance reconciliation

All manifest-preserved files and all134 original-tree entries were independently checked against the archive contents, including original symlink target; archive SHA and preserved production/reproduction/candidate/execution hashes match. The two existing actual Parquet sets are directly byte-identical. Live production outputs, including metadata, equal their preserved production copies. No production/reproduction ETL was rerun.

Production run `fe805a9d-d5c6-4513-a87b-6ed6dfb6a210` and reproduction run `105681f8-fda8-4c3b-8b1b-32035d1c5b12` are distinct UUID4 executions. Original stdout equals each preserved metadata file, stderr is empty, UTC times are ordered, production/reproduction paths are semantically correct. Source/config/implementation/seed/HEAD/dirty-code identity and output hashes reconcile. Run ID/timestamps/log_path differences correctly identify separate executions; metadata is not expected to be byte-identical across separate runs.

Execution-time Git status contains exactly four preexisting untracked candidates. Audit-time Git status additionally contains only files under the explicitly authorized package directory. These are different times and the historical status was not backfilled. Config changed from the historical null-L candidate to approved48 before production; exact approved bytes hash matches production and isolated reproduction. Existing report `reports/p1_t5_log.md` is a preserved **pre-production decision snapshot**, including historical statements that extraction was pending; this final report and preserved original production logs supply later execution findings without rewriting history.

Current canonical environment equals recorded production/reproduction environment: Python3.12.14, PyArrow25.0.1, NumPy2.5.3, PyYAML6.0.3 and the recorded Linux platform, same canonical `.venv/bin/python`. Original reproduction script, archive candidate config/code/test bytes, metadata and direct actual outputs all reconcile. Existing reproduction is established by original preserved execution records plus independently equal actual bytes; no second historical execution is fabricated.

Meta_Run reconciliation remains explicitly `PENDING; no warehouse record written`, as approved for this pre-warehouse stage. This is not a warehouse Meta_Run row and does not satisfy future ingestion requirements. Later ingestion must preserve original execution timestamp, dirty-code identity and hashes rather than substitute an integration commit.

| Audited live identity | SHA-256 |
|---|---|
| `configs/p1_t5.yaml` | `4277ec90e5ec29c91dab10e49e36f19a9d411b8c6f4cff9e7208b0567ff5366c` |
| `etl/clean_segments.py` | `af75261d1d1cf0cd73e1f325bea3a215e41559a553f452c27c479e59ee15e950` |
| `tests/test_P1_T5.py` | `55de7f60264b74f386626b3392f5b407a4377661111ecb4711659de45628bf56` |
| `reports/p1_t5_log.md` | `405ad1a701af9ec375a4709f8cf957c916b65de30e59a4ff569e5193f566a6cc` |
| `control/task_state.yaml` | `e60c2acb655985c71c1dc89c78dbb6a425f4ac1cd39c74a0bbe745716cb60660` |
| `data/processed/clean_segments.parquet` | `b110505eed14acbcb60f68abf8902c0674f8ecf3e5c509f679de5e98082ba0aa` |
| `data/processed/clean_segments_stats.parquet` | `a1b50e601522b704473287bbdac82eceff103d7d0ced59136a6f670eb8ddb538` |
| `data/processed/clean_segments_metadata.json` | `6666c65d8853191e31c89e7879764b7bf3d4e4cf529aad65864304100eb6644f` |

## Implementation, tests and governance

Implementation review found fail-closed checks for missing flags/value agreement, nonboolean/null/inconsistent flags, nonfinite clean values, off-grid/duplicate/reversed timestamps and missing-grid gaps. Streaming batch continuity and interleaved meters are handled; retained runs are maximal and never chopped into windows. CLI requires seed/config; L has no implementation fallback. Source/output directories are separated; existing artifacts are refused. No failure episodes, raw transformation, masks, splits, model fitting, warehouse writes, state update or downstream P1-T6 work is introduced.

Existing P1-T5 synthetic tests were independently executed **once** in canonical `.venv`, with bytecode/cache/plugin autoload disabled: **31 passed in1.54s**, exit0. Command is saved in result JSON; `synthetic_tests.log` SHA-256 `a738ebe858e73f92c9cf6686cd8eaa779cd4ebbe210f1ce35045cb3282c7e3d2`. Tests include scalar oracle comparisons, invalid inputs, batch boundaries, flag exclusions, schema, source immutability, no-overwrite, failed-run metadata and synthetic reproducibility. The prior approved NaN assertion correction remains unchanged. Code/config/test hashes were rechecked after the synthetic tests and equal pre-execution identity.

`gate.sh` and `check_scope.py` are unchanged baseline tooling. They validate union of committed/staged/unstaged/nonignored untracked paths against exact external approved paths and base protected policy, plus protocol hashes, state snapshot and control regression tests. They do not validate ignored production files or grant integration/state authority; ignored outputs are separately bound above. Final exact package-scope/control result remains PENDING for parent. Prior preserved control-gate PASS predates this expanded package and is not represented as the final gate.

Harness diagnostics are preserved transparently: v1 failed before scientific checks because archive member lookup omitted its top-level root prefix; v2 passed archive/provenance reconciliation then stopped on PyArrow nullable Array.to_numpy default zero_copy_only=True. v3 normalized the archive prefix and permitted copies for Arrow-to-NumPy audit conversions. These are resolved **auditor-harness errors**, not candidate/scientific failures. No artifact, source, implementation or test was changed to resolve them. Parent explicitly authorized preserving and correcting the audit harness in new files. Earlier FAILED JSON files describe those aborted harness executions; final acceptance is solely v3 VERIFIED. No debug rerun reached the synthetic tests before v3.

## Readiness and handoff

No scientific/technical P1-T5 failure or unresolved current-task blocker found. Recommend **READY_FOR_FINAL_GATE**, contingent on parent completing final exact package scope freeze, final control gate and fingerprint reconciliation. Do not label GATED, promote state, commit/merge/push, start P1-T6 or claim whole-P1 warehouse completion. Human research approval and separate Integrator state authorization remain required.

Audit-created filenames (all exclusively created, none overwritten):

- `independent_verification.json`
- `independent_verification_v2.json`
- `independent_verification_v3.json`
- `independent_verify.py`
- `independent_verify_v2.py`
- `independent_verify_v3.py`
- `synthetic_tests.log`
- `verification_v2_start.json`
- `verification_v3_start.json`
- `AUDIT_P1_T5_FINAL.md`
