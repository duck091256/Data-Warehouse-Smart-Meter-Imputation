"""P1-T5: maximal clean runs; L is mandatory, never inferred.

Contract proposed for review: inclusive UTC grid labels, length in 15-minute
bins, including both endpoints. Missing grid rows break runs. No values are
imputed, no masks/splits are constructed, no warehouse/state is modified.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import yaml

STEP_US = 900_000_000
SCHEMA = pa.schema([
    ('meter_id', pa.string()), ('start', pa.timestamp('us', tz='UTC')),
    ('end', pa.timestamp('us', tz='UTC')), ('length', pa.int64()),
])
COLUMNS = ['meter_id', 'grid_timestamp_utc', 'value', 'is_missing',
           'has_issue', 'is_corrected', 'is_valid_ground_truth']
STATS_SCHEMA = pa.schema([
    ('meter_id', pa.string()), ('segment_count', pa.int64()),
    ('total_length', pa.int64()), ('min_length', pa.int64()),
    ('median_length', pa.float64()), ('max_length', pa.int64()),
])


def validate_l(min_length):
    if type(min_length) is not int or min_length < 1:
        raise ValueError('min_length_steps must be an explicit positive integer')


def extract_segments(batches, min_length):
    """Consume Arrow batches in per-meter chronological order, across boundaries.

    Interleaved meters are supported. Duplicate/reversed timestamps, invalid
    flags and inconsistent missing/value or GT flags fail closed. Each input
    meter appears in stats, including meters with zero retained runs.
    """
    validate_l(min_length)
    states, segments = {}, []

    def close(meter, state):
        if state['length'] >= min_length:
            segments.append(dict(meter_id=meter, start=state['start'],
                                 end=state['last'], length=state['length']))
        state['length'] = 0

    for batch in batches:
        table = pa.Table.from_batches([batch]) if isinstance(batch, pa.RecordBatch) else batch
        for name in COLUMNS:
            if name not in table.column_names:
                raise ValueError(f'Missing column: {name}')
            if name != 'value' and table[name].null_count:
                raise ValueError(f'Null column: {name}')
        for name in COLUMNS[3:]:
            if table[name].type != pa.bool_():
                raise ValueError(f'Non-boolean flag: {name}')
        ts_type = table['grid_timestamp_utc'].type
        if not pa.types.is_timestamp(ts_type) or ts_type.tz != 'UTC':
            raise ValueError('grid_timestamp_utc must be timezone-aware UTC')
        times = table['grid_timestamp_utc'].cast(pa.timestamp('us', tz='UTC'), safe=True).cast(pa.int64()).to_numpy()
        if np.any(times % STEP_US):
            raise ValueError('Off-grid timestamp')
        flags = [table[c].to_numpy() for c in COLUMNS[3:]]
        good = ~(flags[0] | flags[1] | flags[2])
        if not np.array_equal(good, flags[3]):
            raise ValueError('Inconsistent is_valid_ground_truth')
        values = table['value'].to_numpy()
        if not np.array_equal(np.isnan(values), flags[0]):
            raise ValueError('Inconsistent is_missing/value')
        if np.any(good & ~np.isfinite(values)):
            raise ValueError('Non-finite clean value')
        meters = table['meter_id'].to_numpy()
        for meter in sorted(set(meters)):
            if not isinstance(meter, str) or not meter:
                raise ValueError('Invalid meter_id')
            ix = np.flatnonzero(meters == meter)
            ts, clean = times[ix], good[ix]
            if not len(ts):
                continue
            state = states.setdefault(meter, dict(last=None, start=None, length=0))
            if np.any(np.diff(ts) <= 0) or (state['last'] is not None and ts[0] <= state['last']):
                raise ValueError(f'Duplicate or reversed timestamps for {meter}')
            # Vectorize internal run boundaries, preserve only a tiny cross-batch state.
            cuts = np.flatnonzero((np.diff(ts) != STEP_US) | (clean[1:] != clean[:-1])) + 1
            starts = np.r_[0, cuts]
            ends = np.r_[cuts, len(ts)]
            for a, b in zip(starts, ends):
                contiguous = state['last'] is not None and ts[a] - state['last'] == STEP_US
                if not clean[a] or not contiguous:
                    close(meter, state)
                if clean[a]:
                    if state['length'] == 0:
                        state['start'] = int(ts[a])
                    state['length'] += int(b - a)
                state['last'] = int(ts[b - 1])
    for meter, state in states.items():
        close(meter, state)
    segments.sort(key=lambda x: (x['meter_id'], x['start']))
    result = pa.Table.from_pylist(segments, schema=SCHEMA)
    lengths = {m: [] for m in states}
    for segment in segments:
        lengths[segment['meter_id']].append(segment['length'])
    stats = []
    for meter, values in sorted(lengths.items()):
        stats.append(dict(meter_id=meter, segment_count=len(values), total_length=sum(values),
                          min_length=min(values) if values else None,
                          median_length=float(np.median(values)) if values else None,
                          max_length=max(values) if values else None))
    return result, pa.Table.from_pylist(stats, schema=STATS_SCHEMA)


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(config_path, seed):
    """Explicit execution only; metadata is created before extraction, never backfilled.

    Config paths are relative to the config file. Output files must not exist.
    Sidecar carries input/config/code hashes and working-tree identity because
    git_commit alone cannot identify an uncommitted implementation.
    """
    config_path = Path(config_path).resolve(strict=True)
    config_bytes = config_path.read_bytes()
    config = yaml.safe_load(config_bytes)
    cfg = config['clean_segments']
    validate_l(cfg['min_length_steps'])
    if type(seed) is not int:
        raise ValueError('seed must be an integer')
    def resolve(value):
        path = Path(value)
        return (path if path.is_absolute() else config_path.parent / path).resolve()
    source, output_dir = resolve(cfg['input']), resolve(cfg['output_dir'])
    root = Path(__file__).resolve().parents[1]
    if output_dir.is_relative_to(root) and not output_dir.is_relative_to(root / 'data/processed'):
        raise ValueError('Repository outputs must be under data/processed')
    # Avoid any write through the input directory, including external raw locations.
    if source.is_relative_to(output_dir) or output_dir.is_relative_to(source.parent):
        raise ValueError('Output must be separate from input directory')
    paths = [output_dir / name for name in ['clean_segments.parquet',
             'clean_segments_stats.parquet', 'clean_segments_metadata.json']]
    if any(path.exists() for path in paths):
        raise FileExistsError('Refusing to overwrite existing artifacts or provenance')
    pf = pq.ParquetFile(source)
    if pf.metadata.num_rows == 0:
        raise ValueError('Empty input')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    started = datetime.now(timezone.utc).isoformat()
    metadata = dict(run_id=str(uuid.uuid4()), task_id='P1-T5', seed=seed, timestamp=started,
                    log_path=str(paths[2]),
                    data_version=file_hash(source), config_hash=hashlib.sha256(config_bytes).hexdigest(),
                    git_commit=git('rev-parse', 'HEAD'), git_status=git('status', '--porcelain'),
                    implementation_sha256=file_hash(__file__), input_path=str(source),
                    min_length_steps=cfg['min_length_steps'], length_unit='15min_bins',
                    endpoints='inclusive_UTC_grid_labels', status='STARTED',
                    meta_run_reconciliation='PENDING; no warehouse record written')
    output_dir.mkdir(parents=True, exist_ok=True)
    def save_metadata():
        paths[2].write_text(json.dumps(metadata, indent=2) + '\n')
    # Exclusive create ensures an existing historical record cannot be overwritten.
    with paths[2].open('x') as stream:
        stream.write(json.dumps(metadata, indent=2) + '\n')
    try:
        segments, stats = extract_segments(pf.iter_batches(columns=COLUMNS), cfg['min_length_steps'])
        if file_hash(source) != metadata['data_version']:
            raise ValueError('Input changed during execution')
        pq.write_table(segments, paths[0], compression='zstd')
        pq.write_table(stats, paths[1], compression='zstd')
        metadata.update(status='COMPLETED', segment_count=segments.num_rows,
                        meter_count=stats.num_rows,
                        output_sha256={p.name: file_hash(p) for p in paths[:2]})
    except Exception as exc:
        metadata.update(status='FAILED', error=str(exc))
        raise
    finally:
        metadata['finished_at'] = datetime.now(timezone.utc).isoformat()
        save_metadata()
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', required=True, type=int)
    parser.add_argument('--config', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.seed), indent=2))


if __name__ == '__main__':
    main()
