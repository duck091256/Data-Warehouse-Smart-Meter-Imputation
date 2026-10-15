# P1-T5 — technical candidate and L decision evidence

2026-10-15 (Asia/Ho_Chi_Minh). Base and current HEAD:
`fe21132f0a40863646bf23971cfca49a7444be67`. No production extraction,
canonical-state update, commit, push, merge, or P1-T6 work.

## Implementation and exact scope

Four candidate files only:

- `etl/clean_segments.py`: maximal clean runs, required L, inclusive UTC grid
  labels `start`/`end`, `length` in 15-minute bins, per-meter stats including
  zero-yield meters. Gaps break runs; duplicate/reversed/off-grid timestamps,
  null/non-boolean/inconsistent flags and invalid clean values fail closed.
  Batch boundaries and interleaved meters preserve results. Input is read only.
- `configs/p1_t5.yaml`: candidate config; `min_length_steps: null` intentionally
  prevents production until L is approved. Paths resolve relative to config.
- `tests/test_P1_T5.py`: synthetic examples, independent scalar oracle,
  input byte preservation, invalid inputs, CLI, failed-run provenance,
  overwrite refusal and identical output Parquet bytes on repeat runs.
- `reports/p1_t5_log.md`: this technical log and decision evidence.

The user explicitly authorized this P1-T5 implementation and the exact test
exception. `/tmp/p1_t5_scope.json` serializes that authorization for the existing
machine checker; it does not alter protected policy or confer additional rights.
Only `tests/test_P1_T5.py` is a protected-path exception. No control files change.

Proposed technical conventions require review with L: a segment is maximal,
never chopped into windows; start/end are inclusive grid labels; length is
`(end-start)/15min + 1`. The covered bins form `(start-15min, end]`, so 48 bins
cover 12 hours although the first-to-last label difference is 11h45m.
No mask, train/test split, failure-episode definition or model feature is added.

## Verification evidence

Command in the canonical checkout:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
.venv/bin/python -B -m pytest tests/test_P1_T5.py -q -p no:cacheprovider
```

Final result: **31 passed**, 1.31s. Control gate also **PASS**, including
**68 control regression tests passed** (6.05s), exact four-file Git scope,
protocol integrity and unchanged valid canonical-state snapshot:

```bash
PYTHON="$PWD/.venv/bin/python" bash control/gate.sh \
  --base fe21132f0a40863646bf23971cfca49a7444be67 \
  --scope-manifest /tmp/p1_t5_scope.json
```

This is synthetic technical evidence, not
P1-T5 production acceptance. Execution-time metadata:
`/tmp/p1_t5_synthetic_test_metadata.json` (seed 731, fixture/code/config hashes,
HEAD and timestamp). No historical metadata was reconstructed.

Initial result was 30 passed / 1 failed: dict equality incorrectly treated NaN
as a change (`NaN != NaN`). Independent Auditor `audit_nan_assertion` reproduced
this on an unchanged table and approved replacing only that assertion with
Arrow IPC byte equality before/after. All segment/stat/schema assertions stayed
unchanged. This narrow audit does not constitute independent P1-T5 acceptance.

Runner sidecar is created as STARTED before extraction, then records COMPLETED
or FAILED. Fields include run_id, seed, data_version (input SHA-256), config_hash
(exact config bytes), git_commit, git_status, implementation hash, UTC timestamp,
log_path and output hashes. No existing outputs/provenance are overwritten.
Meta_Run reconciliation is explicitly PENDING: future ingestion must preserve
these original fields, including execution timestamp and dirty-code identity;
it must not substitute an integration commit or fabricate older provenance.
Parquet outputs are repeatable byte-for-byte; run IDs/timestamps in metadata
intentionally identify different executions.

## Read-only L diagnostic, not production extraction

Specification: TASK_PLAN.md P1-T5 requires continuous clean runs of at least
configurable L; it supplies no numerical L, window/context horizon, or endpoint
convention. P2-T3/T4/T5b/T6 require mask feasibility and multi-meter alignment;
P3-T3/T4 and the P3 boundary checklist require usable observed context; P5-T2
requires temporal/episode separation. P6 forecasting is conditional and does
not justify preemptively discarding short clean runs. The draft P1-T6 schema's
`length_steps >= 96` is unapproved and is not authority for L here.

A separate read-only census computed run-length distributions from existing
P1-T4 flags. It checked regular 15-minute timestamps, missing/value agreement
and GT/quality-flag agreement, producing no segment coordinates or processed
artifacts. Live input: 13,981,597 rows, 79 meters, 12,637,042 clean bins.
SHA-256: `c672d5a4efc6cb636708480675e6a2947c436373b05f1bfb8e3307dc9299d279`.

Reproducible evidence (temporary files; preserve these before /tmp cleanup):

```bash
.venv/bin/python -B /tmp/p1_t5_length_diagnostic.py \
  --seed 731 --config /tmp/p1_t5_length_diagnostic_config.json
```

Full per-meter results: `/tmp/p1_t5_length_diagnostic.json`.
Execution metadata: `/tmp/p1_t5_length_diagnostic_metadata.json`, recorded before
scan with input/config/script hashes, seed and HEAD. These are diagnostic
records for this execution, not historical production provenance.

| L (15-min bins) | Covered duration | Retained segments | Retained clean bins | % of all clean bins | Meters with segments | Median retained length |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 15 min | 132,721 | 12,637,042 | 100.00% | 79 | 1 |
| 48 | 12 h | 7,135 | 12,021,273 | 95.13% | 79 | 92 |
| 96 | 1 day | 3,407 | 11,783,486 | 93.25% | 78 | 610 |
| 192 | 2 days | 2,492 | 11,660,295 | 92.27% | 78 | 1,741 |
| 384 | 4 days | 1,930 | 11,508,288 | 91.07% | 78 | 2,593 |
| 672 | 1 week | 1,656 | 11,366,422 | 89.95% | 78 | 3,268 |
| 1,344 | 2 weeks | 1,319 | 11,026,652 | 87.26% | 76 | 4,834 |

Maximum run is unchanged at 130,717 bins for these thresholds. Increasing L
filters complete runs; it never lengthens or combines them. Median length
rises by selection, not by creating observations.

**Proposed default: L=48**, a data-informed extraction compromise, pending human
scientific approval. It retains 79/79 meters' opportunities for short-gap tests
while filtering the many tiny runs (the unrestricted median is 1 bin).
`H2.Z311` has a maximum clean run of only 69 bins; L=48 retains 568 runs / 33,148
bins, whereas L=96 or higher yields zero. It must remain in core population and
zero-yield reports even if a stricter L is selected. L=48 loses 4.87% of clean
bins and can still bias sampling toward longer uninterrupted periods; this
limitation must be disclosed. It is not a universal optimum or a guarantee that
every downstream benchmark can include all meters.

Alternatives: L=1 for maximum preservation and downstream-only feasibility
filtering (more tiny candidates); L=96 for at least one day per retained run
(with H2.Z311 zero yield); L=192 for a simple two-day minimum; L=672 for week-scale
experiments (stronger selection). L=1,344 additionally yields zero for H1.Z310
and H3.Z312. None of these thresholds is mandated by the protocol.

For a block of G bins with observed contexts C_left/C_right, a necessary
single-meter condition is `N >= G+C_left+C_right`. Context/seasonal-lag needs
must be declared by the downstream model, never supplied from masked truth.
A daily lag (96 bins) plus a G-bin block can require at least `96+G` bins;
a weekly lag can require `672+G`. Neither L=96 nor L=672 alone guarantees those
conditions. P1-T5's L is a minimum extraction filter, not the model window size.

At both L=48 and L=96, the census gives the same 11,184,323 possible contiguous
192-bin starts and 10,255,246 possible 672-bin starts, computed as
`sum(max(run_length-W+1,0))`. Thus L=48 preserves the same long-run opportunities
while retaining extra short ones. These overlapping starts are **not independent
samples, usable masks or benchmark sizes**. Calendar matching, correlated
cross-meter overlap, real episode shapes, context, split boundaries and
train-only normalization can reduce availability substantially. They are not
implemented here. Do not claim feasibility or equal branch counts from these
marginal run statistics; do not force H1.ZE20 into pre-installation windows.

## Remaining approvals and production conditions

No additional source/protected policy change is needed for this technical
candidate. Approve L and the proposed units/endpoints/maximal-run contract
before setting the numeric config. The future production write scope must name
exactly these generated files (currently absent and not produced here):

- `data/processed/clean_segments.parquet`
- `data/processed/clean_segments_stats.parquet`
- `data/processed/clean_segments_metadata.json`

These are ignored by Git; a scope PASS alone cannot certify their write scope
or content. Sidecar staging is approved in principle, but its production schema
and later Meta_Run reconciliation need scientific/technical review. Independent
P1-T5 audit and the corresponding human production gate remain pending.
Validate production artifact boundaries against source flags, per-meter
statistics including zero-yield meters, source identity and reproducibility
when execution is authorized. Canonical state remains solely Integrator-owned
after evidence, audit and the relevant human gate. Any future state change
requires separate Integrator authorization for `control/task_state.yaml`;
this candidate requests no such change. P1-T6 remains untouched.
