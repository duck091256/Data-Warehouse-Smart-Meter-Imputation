#!/usr/bin/env python3
"""
etl/normalize_utc.py — Timezone & DST Standardization (P1-T2)

Normalizes raw smart-meter time series to canonical UTC while preserving:
1. Canonical UTC timestamp (timestamp[us, tz=UTC]).
2. Local wall-clock timestamp (Europe/Berlin naive timestamp[us]).
3. Timezone / DST metadata (utc_offset_hours: int16, is_dst: bool).
4. Full provenance back to raw authoritative files.
5. Invariant enforcement:
   - Excludes _corrected_raw files completely.
   - Gracefully handles empty files without crashing or generating fake data.
   - Deterministic and justified deduplication for within-file duplicates (e.g. V.Z84).
   - Zero interpolation / zero synthetic observations.
   - Safe streaming write to data/interim/readings_utc.parquet using PyArrow.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.parquet as pq

# Safely import repo config
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import find_repo_root, get_raw_data_dir, load_config

# Canonical PyArrow Schema for readings_utc
CANONICAL_SCHEMA = pa.schema([
    ("meter_id", pa.string()),
    ("variable", pa.string()),
    ("timestamp_utc", pa.timestamp("us", tz="UTC")),
    ("timestamp_local", pa.timestamp("us")),
    ("utc_offset_hours", pa.int16()),
    ("is_dst", pa.bool_()),
    ("value", pa.float64()),
    ("raw_source_file", pa.string()),
])


def normalize_timestamp_series(
    ts_series: pd.Series,
    local_timezone: str = "Europe/Berlin",
) -> Tuple[pd.Series, pd.Series, np.ndarray, np.ndarray]:
    """
    Standardizes UTC timestamp series and computes Europe/Berlin local time,
    UTC offset in hours (+1 or +2), and is_dst boolean flag in a vectorized,
    microsecond-accurate manner.

    Returns:
        (ts_utc, ts_local, offset_hours, is_dst)
    """
    if len(ts_series) == 0:
        empty_utc = pd.Series([], dtype="datetime64[us, UTC]")
        empty_local = pd.Series([], dtype="datetime64[us]")
        return empty_utc, empty_local, np.array([], dtype=np.int16), np.array([], dtype=bool)

    # 1. Parse UTC timestamp
    if not pd.api.types.is_datetime64_any_dtype(ts_series):
        ts_utc = pd.to_datetime(ts_series, utc=True)
    elif ts_series.dt.tz is None:
        ts_utc = ts_series.dt.tz_localize("UTC")
    else:
        ts_utc = ts_series.dt.tz_convert("UTC")

    # 2. Convert to target local timezone (Europe/Berlin)
    ts_local_tz = ts_utc.dt.tz_convert(local_timezone)
    ts_local_naive = ts_local_tz.dt.tz_localize(None)

    # 3. Vectorized integer offset hours and DST calculation
    # Strip timezone with pandas prior to conversion to avoid numpy UserWarning
    utc_us = ts_utc.dt.tz_localize(None).to_numpy(dtype="datetime64[us]").astype("int64")
    local_us = ts_local_naive.to_numpy(dtype="datetime64[us]").astype("int64")
    offset_hours = ((local_us - utc_us) // 3_600_000_000).astype(np.int16)
    is_dst = (offset_hours == 2)

    return ts_utc, ts_local_naive, offset_hours, is_dst


def deduplicate_raw_dataframe(
    df: pd.DataFrame,
    timestamp_col: str = "datetime_utc",
    value_col: Optional[str] = None,
    strategy: str = "keep_last",
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Identifies and resolves within-file duplicate timestamps with full provenance.
    Differentiates between same timestamp + same value and same timestamp + diff value.
    Applies the justified strategy ('keep_last').

    Returns:
        (deduped_df, stats_dict)
    """
    if len(df) == 0:
        return df, {
            "initial_rows": 0,
            "deduped_rows": 0,
            "duplicate_count": 0,
            "same_ts_same_val": 0,
            "same_ts_diff_val": 0,
            "strategy_applied": strategy,
        }

    dup_count = int(df.duplicated(subset=[timestamp_col], keep="first").sum())

    if dup_count == 0:
        return df, {
            "initial_rows": len(df),
            "deduped_rows": len(df),
            "duplicate_count": 0,
            "same_ts_same_val": 0,
            "same_ts_diff_val": 0,
            "strategy_applied": strategy,
        }

    val_c = value_col if value_col else [c for c in df.columns if c != timestamp_col][0]

    # Vectorized duplicate counting: handles both adjacent and interleaved duplicates
    same_val = int(df.duplicated(subset=[timestamp_col, val_c], keep="first").sum())
    diff_val = dup_count - same_val

    # Apply deduplication
    keep_arg = "last" if strategy == "keep_last" else "first"
    deduped_df = df.drop_duplicates(subset=[timestamp_col], keep=keep_arg).copy()

    stats = {
        "initial_rows": len(df),
        "deduped_rows": len(deduped_df),
        "duplicate_count": dup_count,
        "same_ts_same_val": same_val,
        "same_ts_diff_val": diff_val,
        "strategy_applied": strategy,
    }

    return deduped_df, stats


def read_and_normalize_raw_file(
    file_path: Union[str, Path],
    meter_id: str,
    variable: str,
    local_timezone: str = "Europe/Berlin",
    dedup_strategy: str = "keep_last",
    raw_root: Optional[Path] = None,
) -> Tuple[pa.Table, Dict[str, Any]]:
    """
    Reads an authoritative raw .csv.gz file, applies guard clauses, normalizes
    timestamps to UTC/local time, and returns a PyArrow Table with the canonical schema.

    Guard Clauses:
    - Enforces exclusion of _corrected_raw files (raises ValueError).
    - Safely detects empty files (0 data rows) and returns empty table without crashing.
    """
    fpath = Path(file_path).resolve()
    fname = fpath.name

    # Invariant Guard 1: Reject _corrected_raw
    if "_corrected_raw" in fname:
        raise ValueError(
            f"Protocol Invariant Violation: '_corrected_raw' file '{fname}' cannot be loaded into "
            "authoritative readings."
        )

    # Compute relative source path for provenance
    if raw_root:
        try:
            rel_source = str(fpath.relative_to(raw_root))
        except ValueError:
            rel_source = f"{meter_id}/{fname}"
    else:
        rel_source = f"{meter_id}/{fname}"

    # Read CSV with PyArrow
    try:
        read_opts = pv.ReadOptions(use_threads=True)
        parse_opts = pv.ParseOptions(delimiter=",")
        table = pv.read_csv(fpath, read_options=read_opts, parse_options=parse_opts)
    except Exception as e:
        # Check if empty CSV/gzip caused exception (0-byte, empty stream, or ArrowInvalid)
        if fpath.stat().st_size == 0 or "Empty CSV file" in str(e) or isinstance(e, pa.ArrowInvalid):
            return pa.Table.from_batches([], schema=CANONICAL_SCHEMA), {
                "file_name": fname,
                "meter_id": meter_id,
                "variable": variable,
                "is_empty": True,
                "raw_rows": 0,
                "output_rows": 0,
                "duplicates_removed": 0,
            }
        raise IOError(f"Failed to read raw file '{fpath}': {e}") from e

    # Guard Clause 2: Empty files with 0 data rows
    if len(table) == 0:
        return pa.Table.from_batches([], schema=CANONICAL_SCHEMA), {
            "file_name": fname,
            "meter_id": meter_id,
            "variable": variable,
            "is_empty": True,
            "raw_rows": 0,
            "output_rows": 0,
            "duplicates_removed": 0,
        }

    # Extract columns
    col_names = table.column_names
    ts_col_name = col_names[0]
    val_col_name = col_names[1]

    # Convert to pandas for fast deduplication & timezone handling
    df = table.to_pandas()
    initial_rows = len(df)

    # Deduplication
    df, dedup_stats = deduplicate_raw_dataframe(
        df, timestamp_col=ts_col_name, value_col=val_col_name, strategy=dedup_strategy
    )
    duplicates_removed = dedup_stats["duplicate_count"]

    # Normalize timestamps
    ts_utc, ts_local, offset_hours, is_dst = normalize_timestamp_series(
        df[ts_col_name], local_timezone=local_timezone
    )

    values = pd.to_numeric(df[val_col_name], errors="coerce").to_numpy(dtype=np.float64)

    # Construct canonical Arrow Table
    num_rows = len(df)
    arrow_table = pa.Table.from_arrays(
        [
            pa.array([meter_id] * num_rows, type=pa.string()),
            pa.array([variable] * num_rows, type=pa.string()),
            pa.array(ts_utc.dt.tz_convert("UTC"), type=pa.timestamp("us", tz="UTC")),
            pa.array(ts_local, type=pa.timestamp("us")),
            pa.array(offset_hours, type=pa.int16()),
            pa.array(is_dst, type=pa.bool_()),
            pa.array(values, type=pa.float64()),
            pa.array([rel_source] * num_rows, type=pa.string()),
        ],
        schema=CANONICAL_SCHEMA,
    )

    stats = {
        "file_name": fname,
        "meter_id": meter_id,
        "variable": variable,
        "is_empty": False,
        "raw_rows": initial_rows,
        "output_rows": num_rows,
        "duplicates_removed": duplicates_removed,
        "dedup_stats": dedup_stats,
    }

    return arrow_table, stats


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash of a file deterministically in binary chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def run_p1_t2_normalization(
    config: Optional[Dict[str, Any]] = None,
    config_path: Optional[Union[str, Path]] = None,
    target_variable: Optional[str] = None,
    meter_filter: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Main execution pipeline for P1-T2:
    - Scans authoritative raw dataset for target variable across all meters.
    - Streams normalized records into data/interim/readings_utc.parquet.
    - Emits execution metadata to data/interim/readings_utc_metadata.json.
    - Returns comprehensive summary statistics.
    """
    start_time = time.time()
    root = find_repo_root()
    cfg = config or load_config(config_path, repo_root=root)

    etl_cfg = cfg.get("etl", {})
    var_to_process = target_variable or etl_cfg.get("target_variable", "W")
    local_tz = etl_cfg.get("local_timezone", "Europe/Berlin")
    dedup_cfg = etl_cfg.get("deduplication", {})
    dedup_strat = dedup_cfg.get("strategy", "keep_last")

    exp_seed = seed if seed is not None else cfg.get("experiment", {}).get("seed", 42)
    raw_dir = get_raw_data_dir(cfg)

    # Determine destination paths
    interim_dir = cfg.get("data", {}).get("interim_dir", root / "data" / "interim")
    if not isinstance(interim_dir, Path):
        interim_dir = Path(interim_dir).resolve()
    interim_dir.mkdir(parents=True, exist_ok=True)

    out_file = (
        Path(output_path).resolve()
        if output_path
        else (interim_dir / "readings_utc.parquet").resolve()
    )

    data_subdir = raw_dir / "data"
    if not data_subdir.is_dir():
        data_subdir = raw_dir

    # Find meter directories
    meter_dirs = sorted([d for d in data_subdir.iterdir() if d.is_dir()])
    if meter_filter:
        meter_dirs = [d for d in meter_dirs if d.name == meter_filter]

    print("============================================================")
    print(" P1-T2: Chuẩn hóa múi giờ và DST -> UTC & Local Time")
    print(f" Target variable:   {var_to_process}")
    print(f" Local timezone:    {local_tz}")
    print(f" Dedup strategy:    {dedup_strat}")
    print(f" Output Parquet:    {out_file}")
    print(f" Raw dataset dir:   {raw_dir}")
    print(f" Meters to scan:    {len(meter_dirs)}")
    print("============================================================")

    # Open Parquet writer for streaming batches
    writer = pq.ParquetWriter(out_file, schema=CANONICAL_SCHEMA, compression="snappy")

    total_meters_found = len(meter_dirs)
    meters_with_data = 0
    total_raw_rows = 0
    total_output_rows = 0
    total_duplicates_removed = 0
    empty_files_logged = []
    processed_meters = []

    try:
        for idx, mdir in enumerate(meter_dirs, 1):
            meter_id = mdir.name
            target_fname = f"{meter_id}.{var_to_process}_raw.csv.gz"
            fpath = mdir / target_fname

            if not fpath.exists():
                # Meter does not have this variable (e.g. WeatherStation.Weather for W)
                continue

            # Read and normalize
            table, file_stats = read_and_normalize_raw_file(
                file_path=fpath,
                meter_id=meter_id,
                variable=var_to_process,
                local_timezone=local_tz,
                dedup_strategy=dedup_strat,
                raw_root=raw_dir,
            )

            raw_rows = file_stats["raw_rows"]
            out_rows = file_stats["output_rows"]
            dups = file_stats["duplicates_removed"]

            total_raw_rows += raw_rows
            total_output_rows += out_rows
            total_duplicates_removed += dups

            if file_stats["is_empty"]:
                empty_files_logged.append(target_fname)
            else:
                meters_with_data += 1
                writer.write_table(table)

            processed_meters.append(meter_id)

            if idx % 10 == 0 or idx == len(meter_dirs):
                elapsed = time.time() - start_time
                print(
                    f"  [{idx:2d}/{len(meter_dirs)}] Processed '{meter_id}': "
                    f"raw={raw_rows:,}, out={out_rows:,}, dups={dups:,} (Elapsed: {elapsed:.1f}s)"
                )
    finally:
        writer.close()

    duration = round(time.time() - start_time, 2)
    out_sha256 = compute_file_sha256(out_file)
    cfg_path = Path(cfg.get("_config_path", root / "configs" / "local.yaml"))
    cfg_hash = compute_file_sha256(cfg_path) if cfg_path.exists() else "unknown"

    git_commit = "uncommitted_initial"
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            git_commit = res.stdout.strip()
    except Exception:
        pass

    metadata = {
        "task_id": "P1-T2",
        "task_name": "Chuẩn hóa múi giờ và DST",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seed": exp_seed,
        "data_version": "Honda-SmartMeter-2018-2023-v1.0",
        "config_path": str(cfg_path),
        "config_hash": cfg_hash,
        "git_commit": git_commit,
        "raw_data_dir": str(raw_dir),
        "target_variable": var_to_process,
        "local_timezone": local_tz,
        "dedup_strategy": dedup_strat,
        "output_file": str(out_file),
        "output_sha256": out_sha256,
        "output_file_size_bytes": out_file.stat().st_size,
        "execution_duration_sec": duration,
        "uniqueness_key": ["meter_id", "variable", "timestamp_utc"],
        "summary": {
            "total_meters_scanned": total_meters_found,
            "meters_with_target_file": len(processed_meters),
            "meters_with_data": meters_with_data,
            "total_raw_rows": total_raw_rows,
            "total_output_rows": total_output_rows,
            "total_rows": total_output_rows,
            "total_duplicates_removed": total_duplicates_removed,
            "empty_files_count": len(empty_files_logged),
            "empty_files": empty_files_logged,
            "excluded_meters_no_target_file": [m.name for m in meter_dirs if m.name not in processed_meters],
            "excluded_meters_empty_file": [f.replace(f".{var_to_process}_raw.csv.gz", "") for f in empty_files_logged],
            "excluded_meters_total": sorted(
                list(
                    set(
                        [m.name for m in meter_dirs if m.name not in processed_meters]
                        + [f.replace(f".{var_to_process}_raw.csv.gz", "") for f in empty_files_logged]
                    )
                )
            ),
        },
    }

    # Write metadata JSON (alongside out_file if custom path, otherwise interim_dir default)
    if output_path:
        meta_path = out_file.parent / f"{out_file.stem}_metadata.json"
    else:
        meta_path = interim_dir / "readings_utc_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n============================================================")
    print(" P1-T2 NORMALIZATION COMPLETE")
    print(f" Total rows written:      {total_output_rows:,}")
    print(f" Duplicates removed:      {total_duplicates_removed:,}")
    print(f" Empty files safely:      {len(empty_files_logged)}")
    print(f" Parquet SHA-256:         {out_sha256}")
    print(f" Execution duration:      {duration}s")
    print(f" Metadata written to:     {meta_path}")
    print("============================================================")

    return metadata


def main():
    parser = argparse.ArgumentParser(description="P1-T2: Normalize smart-meter timestamps to UTC & local time.")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    parser.add_argument("--seed", type=int, default=None, help="Experiment seed")
    parser.add_argument("--variable", type=str, default=None, help="Target variable (default: W)")
    parser.add_argument("--meter", type=str, default=None, help="Normalize specific meter only")
    parser.add_argument("--output", type=str, default=None, help="Path to output parquet file")
    args = parser.parse_args()

    run_p1_t2_normalization(
        config_path=args.config,
        seed=args.seed,
        target_variable=args.variable,
        meter_filter=args.meter,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
