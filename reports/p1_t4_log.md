# P1-T4 Task Log — Quality & Provenance Flags

- **Execution Date (UTC)**: 2026-10-07T18:08:07.564500+00:00
- **Task**: P1-T4
- **Status**: IMPLEMENTED / TESTS PASSED
- **Input Artifact**: `/home/duck/Downloads/Vice - Download/StudyWithVKU/StudyWithVKU/ThirdYear/data-warehousing/data/interim/readings_15min.parquet`
- **Output Artifact**: `/home/duck/Downloads/Vice - Download/StudyWithVKU/StudyWithVKU/ThirdYear/data-warehousing/data/interim/readings_15min_flagged.parquet`
- **Output SHA-256**: `c672d5a4efc6cb636708480675e6a2947c436373b05f1bfb8e3307dc9299d279`
- **Execution Duration**: 20.73 s
- **Peak RSS Memory**: 514.4 MB

## Key Results
1. **Row Count Conservation**: 13,981,597 output rows (100% matched to P1-T3).
2. **Quality Flags Attached**:
   - `is_missing`: 648,020 True (4.63%), 13,333,577 False (95.37%)
   - `has_issue`: 816,799 True (5.83%), 13,164,798 False (94.17%)
   - `is_corrected`: 0 True (0.00%), 13,981,597 False (100.00%)
   - `is_valid_ground_truth`: 12,637,042 True (90.39%)
3. **Observation Gap vs Outage Distinction**:
   - Unrelated observation gaps: 527,756 bins (3.77%) remain missing without equipment failure labels.
   - Corroborated outage gaps: 120,264 bins (0.86%) matched authoritative outage logs.
4. **Value & Metadata Immutability**:
   - Value Buffer SHA-256 Hash: `8cfc5fcdc0dde87d8b27a4b039059842663befc207ec4c32295632417f374cbe` (bit-for-bit identical to P1-T3).
   - Value Null Count: 648,020 (exactly equals empty bins).
   - All P1-T3 values and timestamps preserved bit-for-bit.

## Risks & Non-Obvious Context
- Issue interval matching uses strict UTC semantics and interval overlap $(t-15\text{min}, t]$.
- No local-time DST transitions impact the quality flag assignment.
