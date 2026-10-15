"""P1-T5 synthetic acceptance: independent examples and scalar oracle, no real input."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from etl.clean_segments import COLUMNS, SCHEMA, extract_segments, run

BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)


def row(step, meter='A', bad=None):
    return dict(meter_id=meter, grid_timestamp_utc=BASE + timedelta(minutes=15 * step),
                value=float('nan') if bad == 'is_missing' else float(step),
                is_missing=bad == 'is_missing', has_issue=bad == 'has_issue',
                is_corrected=bad == 'is_corrected', is_valid_ground_truth=bad is None)


def table(rows):
    schema = pa.schema([(n, pa.string() if n == 'meter_id' else
                         pa.timestamp('us', tz='UTC') if n == 'grid_timestamp_utc' else
                         pa.float64() if n == 'value' else pa.bool_()) for n in COLUMNS])
    return pa.Table.from_pylist(rows, schema=schema)


def brief(result):
    return [(r['meter_id'], int((r['start'] - BASE).total_seconds() / 900),
             int((r['end'] - BASE).total_seconds() / 900), r['length'])
            for r in result.to_pylist()]


def test_exact_boundaries_flags_and_no_input_mutation():
    t = table([row(i, bad={2:'is_missing', 5:'has_issue', 8:'is_corrected'}.get(i))
               for i in range(12)])
    # Independent Auditor approved this correction: dict equality rejects NaN.
    def ipc_bytes(value):
        sink = pa.BufferOutputStream()
        with pa.ipc.new_stream(sink, value.schema) as writer:
            writer.write_table(value)
        return sink.getvalue().to_pybytes()
    before = ipc_bytes(t)
    segments, stats = extract_segments(t.to_batches(max_chunksize=2), 2)
    assert brief(segments) == [('A',0,1,2), ('A',3,4,2), ('A',6,7,2), ('A',9,11,3)]
    assert stats.to_pylist() == [dict(meter_id='A', segment_count=4, total_length=9,
                                    min_length=2, median_length=2.0, max_length=3)]
    assert segments.schema == SCHEMA
    assert ipc_bytes(t) == before
    for segment in segments.to_pylist():
        assert segment['length'] == (segment['end']-segment['start']).total_seconds()/900+1
        selected = [r for r in t.to_pylist() if segment['start'] <= r['grid_timestamp_utc'] <= segment['end']]
        assert all(not r['is_missing'] and not r['has_issue'] and not r['is_corrected'] for r in selected)


@pytest.mark.parametrize('batch_size', [1,2,3,7,100])
def test_gap_interleaved_meters_cross_batch_and_zero_stats(batch_size):
    rows = []
    for i in [0,1,3,4,5]:
        rows.extend([row(i,'B'), row(i,'A',bad='has_issue')])
    segments, stats = extract_segments(table(rows).to_batches(max_chunksize=batch_size), 3)
    assert brief(segments) == [('B',3,5,3)]
    assert stats.to_pylist()[0] == dict(meter_id='A', segment_count=0, total_length=0,
                                       min_length=None, median_length=None, max_length=None)
    assert stats['meter_id'].to_pylist() == ['A','B']


@pytest.mark.parametrize('L', [None,0,-1,1.5,True,'96'])
def test_invalid_l(L):
    with pytest.raises(ValueError, match='positive integer'):
        extract_segments([], L)


def test_empty_and_single_bin():
    segments, stats = extract_segments([], 1)
    assert segments.num_rows == stats.num_rows == 0
    assert segments.schema == SCHEMA
    assert brief(extract_segments([table([row(0)])],1)[0]) == [('A',0,0,1)]
    assert extract_segments([table([row(0)])],2)[0].num_rows == 0


@pytest.mark.parametrize('steps', [[0,0],[1,0]])
def test_duplicate_and_reverse_across_batches(steps):
    with pytest.raises(ValueError, match='Duplicate or reversed'):
        extract_segments(table([row(i) for i in steps]).to_batches(max_chunksize=1),1)


@pytest.mark.parametrize('mutation,match', [
    ({'has_issue':None}, 'Null column'),
    ({'is_valid_ground_truth':False}, 'Inconsistent is_valid_ground_truth'),
    ({'value':float('nan')}, 'Inconsistent is_missing/value'),
    ({'value':float('inf')}, 'Non-finite'),
    ({'grid_timestamp_utc':BASE+timedelta(seconds=1)}, 'Off-grid'),
    ({'meter_id':None}, 'Null column'),
])
def test_fail_closed(mutation, match):
    r = row(0)
    r.update(mutation)
    with pytest.raises(ValueError, match=match):
        extract_segments([table([r])],1)


def test_schema_validation():
    t = table([row(0)])
    with pytest.raises(ValueError, match='Missing column'):
        extract_segments([t.drop(['has_issue'])],1)
    t = t.set_column(t.schema.get_field_index('has_issue'),'has_issue',pa.array([0]))
    with pytest.raises(ValueError, match='Non-boolean'):
        extract_segments([t],1)
    t = table([row(0)])
    t = t.set_column(1,'grid_timestamp_utc',pa.array([BASE.replace(tzinfo=None)]))
    with pytest.raises(ValueError, match='timezone-aware UTC'):
        extract_segments([t],1)


def scalar_oracle(rows, L):
    found = []
    for meter in sorted({r['meter_id'] for r in rows}):
        active = []
        previous = None
        def flush():
            if len(active) >= L:
                found.append((meter, active[0], active[-1], len(active)))
            active.clear()
        for r in [r for r in rows if r['meter_id']==meter]:
            step = int((r['grid_timestamp_utc']-BASE).total_seconds()/900)
            if previous is not None and step != previous+1:
                flush()
            if r['is_missing'] or r['has_issue'] or r['is_corrected']:
                flush()
            else:
                active.append(step)
            previous=step
        flush()
    return found


@pytest.mark.parametrize('L', [1,2,5,48,96])
def test_deterministic_randomized_scalar_oracle(L):
    rng = np.random.default_rng(731)
    rows=[]
    for step in range(250):
        for meter in ['A','B','C']:
            if rng.random()<0.07:
                continue
            bad = rng.choice([None, 'is_missing','has_issue','is_corrected'],p=[.85,.05,.05,.05])
            rows.append(row(step,meter,bad))
    expected=scalar_oracle(rows,L)
    for batch_size in [1,17,1000]:
        actual,_=extract_segments(table(rows).to_batches(max_chunksize=batch_size),L)
        assert brief(actual)==expected


def fixture_config(tmp_path, name='out', L=2):
    source=tmp_path/'input'/'flagged.parquet'
    source.parent.mkdir(exist_ok=True)
    pq.write_table(table([row(i) for i in range(5)]),source,row_group_size=2)
    cfg=tmp_path/(name+'.yaml')
    cfg.write_text(yaml.safe_dump({'clean_segments':dict(input=str(source),
                  output_dir=str(tmp_path/name), min_length_steps=L)}))
    return cfg,source,tmp_path/name


def test_cli_provenance_reproducibility_and_overwrite_refusal(tmp_path):
    cfg, source, out=fixture_config(tmp_path)
    input_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    subprocess.run([sys.executable,'-B',str(ROOT/'etl/clean_segments.py'),
                    '--seed','731','--config',str(cfg)],check=True,capture_output=True)
    meta=json.loads((out/'clean_segments_metadata.json').read_text())
    assert meta['seed']==731 and meta['status']=='COMPLETED'
    assert meta['data_version']==input_hash
    assert meta['config_hash']==hashlib.sha256(cfg.read_bytes()).hexdigest()
    assert meta['implementation_sha256']==hashlib.sha256((ROOT/'etl/clean_segments.py').read_bytes()).hexdigest()
    assert len(meta['git_commit'])==40 and meta['timestamp'] <= meta['finished_at']
    assert 'PENDING' in meta['meta_run_reconciliation']
    assert brief(pq.read_table(out/'clean_segments.parquet'))==[('A',0,4,5)]
    assert hashlib.sha256(source.read_bytes()).hexdigest()==input_hash
    # Same exact config, seed and data, rerun after moving the prior output aside.
    archived=tmp_path/'archive'
    out.rename(archived)
    run(cfg,731)
    for name,expected in meta['output_sha256'].items():
        assert hashlib.sha256((out/name).read_bytes()).hexdigest()==expected
        assert (out/name).read_bytes()==(archived/name).read_bytes()
    historical=(out/'clean_segments_metadata.json').read_bytes()
    with pytest.raises(FileExistsError):
        run(cfg,731)
    assert (out/'clean_segments_metadata.json').read_bytes()==historical


def test_failed_run_has_contemporaneous_metadata(tmp_path):
    cfg,source,out=fixture_config(tmp_path)
    bad=row(0)
    bad['is_valid_ground_truth']=False
    pq.write_table(table([bad]),source)
    with pytest.raises(ValueError,match='Inconsistent'):
        run(cfg,731)
    meta=json.loads((out/'clean_segments_metadata.json').read_text())
    assert meta['status']=='FAILED' and meta['timestamp']<=meta['finished_at']
    assert not (out/'clean_segments.parquet').exists()


def test_unapproved_l_and_empty_input_write_nothing(tmp_path):
    cfg,source,out=fixture_config(tmp_path,L=None)
    with pytest.raises(ValueError,match='positive integer'):
        run(cfg,731)
    assert not out.exists()
    cfg,source,out=fixture_config(tmp_path,L=2)
    pq.write_table(table([]),source)
    with pytest.raises(ValueError,match='Empty input'):
        run(cfg,731)
    assert not out.exists()


def test_reject_input_output_overlap(tmp_path):
    cfg,source,out=fixture_config(tmp_path)
    data=yaml.safe_load(cfg.read_text())
    data['clean_segments']['output_dir']=str(source.parent)
    cfg.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError,match='separate from input'):
        run(cfg,731)
