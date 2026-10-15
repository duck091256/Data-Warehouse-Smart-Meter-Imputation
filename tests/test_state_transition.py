"""Finalization verification in disposable repositories; no real P1-T5 writes."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from test_control_layer import git_fixture, fixture_git, fixture_commit, write_approval, clean_git_env
from control.check_scope import semantic_delta


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def frozen_identity(path):
    return {'sha256': sha(path.read_bytes()), 'mode': path.stat().st_mode & 0o777}


def ref(path):
    return {"path": str(path.resolve()), "sha256": sha(path.read_bytes())}


@pytest.fixture
def transition_fixture(git_fixture, tmp_path):
    repo, _ = git_fixture
    before = dict(protocol_version="v1.1", current_stage="SETUP", current_task="CONTROL_LAYER", tasks={
        "CONTROL_LAYER": dict(status="GATED", test="PASSED", audit="NOT_REQUIRED"),
        "P1-T1": dict(status="BLOCKED", test="NOT_RUN", audit="NOT_REQUIRED"),
        "P1-T2": dict(status="BLOCKED", test="NOT_RUN", audit="NOT_REQUIRED")})
    state = repo / "control/task_state.yaml"
    state.write_text(yaml.safe_dump(before, sort_keys=False))
    base = fixture_commit(repo)
    old_raw = state.read_bytes()
    after = copy.deepcopy(before)
    after.update(current_stage="P1", current_task="P1-T1")
    after["tasks"]["P1-T1"].update(status="GATED", test="PASSED", audit="PASSED")
    state.write_text(yaml.safe_dump(after, sort_keys=False))
    scope = write_approval(tmp_path / "scope.json", base, ["control/task_state.yaml"], ["control/task_state.yaml"])
    human = tmp_path / "human-approval.md"
    human.write_text("SYNTHETIC Researcher approval: finalize fixture P1-T1 only, exact record digest pinned by test operator. Not P1-T5 authorization.")
    evidence = tmp_path / "final-audit.md"
    evidence.write_text("SYNTHETIC accepted fixture: task tests and independent audit PASSED.")
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text(json.dumps(dict(task_id="P1-T1", verdict="ACCEPTED", test="PASSED", audit="PASSED", evidence=[ref(evidence)])))
    now = datetime.datetime.now(datetime.timezone.utc)
    record = dict(version=1, operation="FINALIZE_TASK", role="Researcher", decision="APPROVE_CANONICAL_TRANSITION",
                  reference="Synthetic task-specific human authorization", approved_at=(now-datetime.timedelta(minutes=1)).isoformat().replace('+00:00','Z'),
                  expires_at=(now+datetime.timedelta(hours=1)).isoformat().replace('+00:00','Z'),
                  task_id="P1-T1", base_commit=base, before_sha256=sha(old_raw), after_sha256=sha(state.read_bytes()),
                  delta=semantic_delta(before, after), scope_sha256=sha(scope.read_bytes()),
                  authorization_evidence=ref(human), final_acceptance=ref(acceptance), frozen_files={})
    approval = tmp_path / "transition.json"
    approval.write_text(json.dumps(record))
    return dict(repo=repo, base=base, before=before, after=after, old_raw=old_raw, state=state, scope=scope,
                record=record, approval=approval, acceptance=acceptance, evidence=evidence, human=human,
                tmp=tmp_path)


def save(f):
    f['approval'].write_text(json.dumps(f['record']))
    return sha(f['approval'].read_bytes())


def cli(f, gate=False, pin=None, options=True):
    args = (["bash", str(f['repo']/"control/gate.sh")] if gate else
            [sys.executable, "-I", "-B", str(f['repo']/"control/check_scope.py")])
    args += ["--base", f['base'], "--scope-manifest", str(f['scope'])]
    if options:
        args += ["--state-transition", str(f['approval']), "--authorization-sha256", pin or sha(f['approval'].read_bytes())]
    env = clean_git_env();env['PYTHON'] = sys.executable
    return subprocess.run(args, cwd=f['repo'].parent, env=env, capture_output=True, text=True)


def assert_rejected(f, expected=None, gate=False, **kwargs):
    result = cli(f, gate=gate, **kwargs)
    assert result.returncode != 0, result.stdout + result.stderr
    if expected:
        assert expected in result.stdout + result.stderr
    return result


def test_approved_finalization_passes_scope_and_mandatory_gate_read_only(transition_fixture):
    f = transition_fixture
    before = {str(p.relative_to(f['repo'])): p.read_bytes() for p in f['repo'].rglob('*') if p.is_file()}
    approved_bytes = f['approval'].read_bytes()
    for gate in (False, True):
        result = cli(f, gate=gate)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "State transition VERIFIED (read-only): P1-T1 -> GATED" in result.stdout
        if gate:
            assert "RESULT: GATE = PASS" in result.stdout
    after = {str(p.relative_to(f['repo'])): p.read_bytes() for p in f['repo'].rglob('*') if p.is_file()}
    assert before == after
    assert f['approval'].read_bytes() == approved_bytes
    assert not list(f['repo'].rglob('__pycache__'))
    assert not (f['repo']/'.pytest_cache').exists()


def test_default_scope_and_gate_still_reject_state_exception(transition_fixture):
    f = transition_fixture
    for gate in (False, True):
        assert_rejected(f, "P0a cannot authorize", gate=gate, options=False)


@pytest.mark.parametrize('field,value', [
    ('role','Executor'), ('decision','APPROVE_IMPLEMENTATION_ONLY'), ('reference',' '),
    ('task_id','P1-T2'), ('task_id','UNKNOWN'), ('base_commit','0'*40),
    ('before_sha256','0'*64), ('after_sha256','0'*64), ('scope_sha256','0'*64),
    ('approved_at','2999-01-01T00:00:00Z'), ('expires_at','2000-01-01T00:00:00Z'),
    ('expires_at','not UTC'), ('operation','ADVANCE_NEXT_TASK'), ('version',True),
    ('delta',[]), ('frozen_files',{'extra.txt':'0'*64}),
])
def test_invalid_approval_fails_even_when_operator_pins_its_bytes(transition_fixture, field, value):
    f=transition_fixture; f['record'][field]=value;save(f)
    assert_rejected(f)


def test_worker_cannot_replace_operator_pinned_record(transition_fixture):
    f=transition_fixture;pin=sha(f['approval'].read_bytes())
    f['record']['reference']='replacement';save(f)
    assert_rejected(f,'authorization digest mismatch',pin=pin)


@pytest.mark.parametrize('kind',['missing','wrong_digest','blank','only_record','only_digest','diagnostic'])
def test_operator_approval_inputs_required(transition_fixture, kind):
    f=transition_fixture
    if kind=='wrong_digest':
        assert_rejected(f,'authorization digest mismatch',pin='0'*64);return
    args=[sys.executable,'-I','-B',str(f['repo']/'control/check_scope.py'),'--base',f['base'],'--scope-manifest',str(f['scope'])]
    if kind in ('only_record','blank','diagnostic'):
        args+=['--state-transition',str(f['approval'])]
    if kind in ('only_digest','blank','diagnostic'):
        args+=['--authorization-sha256','' if kind=='blank' else sha(f['approval'].read_bytes())]
    if kind=='diagnostic':args+=['--files','control/task_state.yaml']
    result=subprocess.run(args,capture_output=True,text=True,env=clean_git_env())
    assert result.returncode != 0


@pytest.mark.parametrize('kind',['human','acceptance','audit','missing_audit','wrong_task','not_accepted'])
def test_acceptance_and_human_evidence_are_bound(transition_fixture,kind):
    f=transition_fixture
    if kind=='human':f['human'].write_text('changed approval')
    elif kind=='acceptance':f['acceptance'].write_text('{}')
    elif kind=='audit':f['evidence'].write_text('changed audit')
    elif kind=='missing_audit':f['evidence'].unlink()
    else:
        data=json.loads(f['acceptance'].read_text())
        if kind=='wrong_task':data['task_id']='P1-T2'
        else:data['verdict']='READY_FOR_FINAL_GATE'
        f['acceptance'].write_text(json.dumps(data));f['record']['final_acceptance']=ref(f['acceptance']);save(f)
    assert_rejected(f)


@pytest.mark.parametrize('kind',['other_task','protocol_version','pointer','bad_status','removed_task','test_failure'])
def test_unrelated_or_invalid_state_change_rejected_even_with_new_posthash(transition_fixture,kind):
    f=transition_fixture;after=copy.deepcopy(f['after'])
    if kind=='other_task':after['tasks']['P1-T2']['status']='READY'
    elif kind=='protocol_version':after['protocol_version']='changed'
    elif kind=='pointer':after['current_task']='P1-T2'
    elif kind=='bad_status':after['tasks']['P1-T1']['status']='DONE'
    elif kind=='removed_task':del after['tasks']['P1-T2']
    else:after['tasks']['P1-T1']['test']='FAILED'
    f['state'].write_text(yaml.safe_dump(after));f['record']['after_sha256']=sha(f['state'].read_bytes())
    f['record']['delta']=semantic_delta(f['before'],after);save(f)
    assert_rejected(f)


@pytest.mark.parametrize('kind',['missing','not_gated','wrong_pointer','already_gated'])
def test_prerequisite_and_transition_history_rejected(transition_fixture,kind):
    f=transition_fixture
    before=copy.deepcopy(f['before'])
    if kind=='missing':del before['tasks']['CONTROL_LAYER'];before['current_task']='P1-T1';before['current_stage']='P1'
    elif kind=='not_gated':before['tasks']['CONTROL_LAYER']['status']='READY'
    elif kind=='wrong_pointer':before['current_task']='P1-T2'
    else:before=copy.deepcopy(f['after'])
    f['state'].write_text(yaml.safe_dump(before));base=fixture_commit(f['repo']);f['base']=base
    f['state'].write_text(yaml.safe_dump(f['after']))
    write_approval(f['scope'],base,['control/task_state.yaml'],['control/task_state.yaml'])
    f['record'].update(base_commit=base,before_sha256=sha(yaml.safe_dump(before).encode()),
                       after_sha256=sha(f['state'].read_bytes()),scope_sha256=sha(f['scope'].read_bytes()),delta=semantic_delta(before,f['after']))
    save(f);assert_rejected(f)


def test_stale_git_baseline_rejected(transition_fixture):
    f=transition_fixture
    # Synthetic commit only; production/project HEAD never changes.
    (f['repo']/'ordinary.txt').write_text('new baseline')
    fixture_commit(f['repo'])
    assert_rejected(f,'HEAD must equal')


@pytest.mark.parametrize('kind',['extra_allowlist','extra_exception','protected_file','raw','scope_changed','unfrozen','frozen_changed','staged_other','state_index_third'])
def test_scope_expansion_and_index_smuggling_rejected(transition_fixture,kind):
    f=transition_fixture
    if kind=='extra_allowlist':write_approval(f['scope'],f['base'],['control/task_state.yaml','unused.txt'],['control/task_state.yaml'])
    elif kind=='extra_exception':write_approval(f['scope'],f['base'],['control/task_state.yaml','control/README.md'],['control/task_state.yaml','control/README.md'])
    elif kind in ('protected_file','raw'):
        name='tests/test_control_layer.py' if kind=='protected_file' else 'data/raw/new.txt'
        p=f['repo']/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('changed')
        write_approval(f['scope'],f['base'],['control/task_state.yaml',name],['control/task_state.yaml',name])
        f['record']['frozen_files']={name:frozen_identity(p)}
    elif kind=='scope_changed':
        write_approval(f['scope'],f['base'],['control/task_state.yaml','unused.txt'],['control/task_state.yaml'])
        assert_rejected(f,'scope fingerprint mismatch');return
    elif kind=='unfrozen':(f['repo']/'new.txt').write_text('unapproved')
    elif kind=='frozen_changed':
        p=f['repo']/'new.txt';p.write_text('before')
        f['record']['frozen_files']={'new.txt':frozen_identity(p)}
        write_approval(f['scope'],f['base'],['control/task_state.yaml','new.txt'],['control/task_state.yaml']);p.write_text('after')
    elif kind=='staged_other':
        (f['repo']/'ordinary.txt').write_text('changed');fixture_git(f['repo'],'add','ordinary.txt')
    else:
        f['state'].write_text('unapproved third state');fixture_git(f['repo'],'add','control/task_state.yaml')
        f['state'].write_text(yaml.safe_dump(f['after'],sort_keys=False))
    f['record']['scope_sha256']=sha(f['scope'].read_bytes());save(f);assert_rejected(f)


def test_frozen_preexisting_approved_untracked_test_can_be_preserved(transition_fixture):
    f=transition_fixture;name='tests/test_previous_task.py';p=f['repo']/name;p.write_text('historically approved test; never executed')
    f['record']['frozen_files']={name:frozen_identity(p)}
    write_approval(f['scope'],f['base'],['control/task_state.yaml',name],['control/task_state.yaml',name])
    f['record']['scope_sha256']=sha(f['scope'].read_bytes());save(f)
    result=cli(f);assert result.returncode==0,result.stdout+result.stderr
    p.write_text('mutation after approval');assert_rejected(f,'frozen baseline fingerprint/mode mismatch')


@pytest.mark.parametrize('kind',['duplicate_json','extra_key','approval_inside','symlink','duplicate_yaml','state_symlink','executable_state','changed_control'])
def test_ambiguous_or_unsafe_records_fail_closed(transition_fixture,kind):
    f=transition_fixture
    if kind=='duplicate_json':f['approval'].write_text(f['approval'].read_text().replace('"role":','"role":"Executor","role":'))
    elif kind=='extra_key':f['record']['bypass']=True;save(f)
    elif kind=='approval_inside':
        p=f['repo']/'approval.json';p.write_bytes(f['approval'].read_bytes());f['approval']=p
    elif kind=='symlink':
        p=f['tmp']/'alias.json';p.symlink_to(f['approval']);f['approval']=p
    elif kind=='duplicate_yaml':
        f['state'].write_bytes(f['state'].read_bytes()+b'current_task: P1-T1\n');f['record']['after_sha256']=sha(f['state'].read_bytes());save(f)
    elif kind=='state_symlink':
        p=f['tmp']/'state.yaml';p.write_bytes(f['state'].read_bytes());f['state'].unlink();f['state'].symlink_to(p)
    elif kind=='executable_state':f['state'].chmod(0o755)
    else:(f['repo']/'control/validate_state.py').write_text('raise RuntimeError("must not execute changed validator")')
    assert_rejected(f)


def test_invalid_transition_makes_mandatory_gate_fail(transition_fixture):
    f=transition_fixture;f['record']['after_sha256']='0'*64;save(f)
    result=assert_rejected(f,'state preimage/postimage mismatch',gate=True)
    assert 'RESULT: GATE = FAIL' in result.stdout
    assert '[OK] Approved Git scope' not in result.stdout


@pytest.mark.parametrize('flag', ['--assume-unchanged', '--skip-worktree'])
def test_hidden_index_flags_cannot_hide_protected_changes(transition_fixture, flag):
    f=transition_fixture
    fixture_git(f['repo'], 'update-index', flag, 'tests/test_control_layer.py')
    (f['repo']/'tests/test_control_layer.py').write_text('def test_fake():\n    assert True\n')
    result=assert_rejected(f,'index flags forbidden',gate=True)
    assert 'RESULT: GATE = FAIL' in result.stdout
    assert '[OK] Control regression tests' not in result.stdout


def test_transition_gate_does_not_execute_rejected_validator(transition_fixture):
    f=transition_fixture;marker=f['tmp']/'untrusted-validator-ran'
    (f['repo']/'control/validate_state.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("executed")\n')
    result=assert_rejected(f,'controls differ from approved baseline',gate=True)
    assert not marker.exists()
    assert '[OK] Task state snapshot' not in result.stdout
    assert '[OK] Control regression tests' not in result.stdout


def test_frozen_permission_change_is_rejected(transition_fixture):
    f=transition_fixture;name='ordinary.txt';p=f['repo']/name
    p.write_text('approved preexisting change')
    f['record']['frozen_files']={name:frozen_identity(p)}
    write_approval(f['scope'],f['base'],['control/task_state.yaml',name],['control/task_state.yaml'])
    f['record']['scope_sha256']=sha(f['scope'].read_bytes());save(f)
    assert cli(f).returncode==0
    p.chmod(0o755)
    assert_rejected(f,'frozen baseline fingerprint/mode mismatch')


def test_intent_to_add_cannot_hide_nonstate_index_change(transition_fixture):
    f=transition_fixture;(f['repo']/'intent.txt').write_text('new')
    fixture_git(f['repo'],'add','-N','intent.txt')
    assert_rejected(f,'non-state index differs')


@pytest.mark.parametrize('kind',['pyc','shadow','without_isolation'])
def test_untrusted_ignored_runtime_code_never_executes(transition_fixture,kind):
    f=transition_fixture;marker=f['tmp']/'untrusted-runtime-ran'
    if kind=='pyc':
        import importlib.util
        import marshal
        import struct
        source=f['repo']/'control/validate_state.py';st=source.stat()
        cache=Path(importlib.util.cache_from_source(str(source)));cache.parent.mkdir(exist_ok=True)
        payload=compile('from pathlib import Path\nPath('+repr(str(marker))+').write_text("bad")\n',str(source),'exec')
        cache.write_bytes(importlib.util.MAGIC_NUMBER+struct.pack('<III',0,int(st.st_mtime),st.st_size)+marshal.dumps(payload))
        assert_rejected(f,'bytecode caches forbidden',gate=True)
    else:
        (f['repo']/'control/yaml.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("bad")\nraise RuntimeError("shadow")\n')
        if kind=='without_isolation':
            args=[sys.executable,'-B',str(f['repo']/'control/check_scope.py'),'--base',f['base'],'--scope-manifest',str(f['scope']),'--state-transition',str(f['approval']),'--authorization-sha256',sha(f['approval'].read_bytes())]
            result=subprocess.run(args,capture_output=True,text=True,env=clean_git_env())
            assert result.returncode!=0 and 'isolated Python' in result.stderr
        else:
            assert_rejected(f,gate=True)  # -I prevents execution; unknown control code fails scope.
    assert not marker.exists()


@pytest.mark.parametrize('kind',['filter','fsmonitor','ignored_control','ignored_conftest'])
def test_untrusted_git_callbacks_and_ignored_control_code(transition_fixture,kind):
    f=transition_fixture;marker=f['tmp']/'untrusted-callback-ran'
    if kind=='filter':
        fixture_git(f['repo'],'config','filter.hide.clean','touch '+str(marker)+'; cat')
        (f['repo']/'.git/info/attributes').write_text('tests/test_control_layer.py filter=hide\n')
        assert_rejected(f,'Git clean/process filters forbidden',gate=True)
    elif kind=='fsmonitor':
        fixture_git(f['repo'],'config','core.fsmonitor','touch '+str(marker))
        assert_rejected(f,'fsmonitor callbacks forbidden',gate=True)
    elif kind=='ignored_control':
        (f['repo']/'.git/info/exclude').write_text('control/hidden.py\n')
        (f['repo']/'control/hidden.py').write_text('raise RuntimeError("unapproved")')
        assert_rejected(f,'unapproved executable Python',gate=True)
    else:
        (f['repo']/'.git/info/exclude').write_text('conftest.py\n')
        (f['repo']/'conftest.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("bad")\n')
        assert_rejected(f,'unapproved executable Python',gate=True)
    assert not marker.exists()


def test_git_nonexec_mode_allows_group_writable_checkout(transition_fixture):
    f=transition_fixture
    # Auditor-confirmed correction: BASE100644 binds nonexec, not umask-specific write bits.
    (f['repo']/'tests/test_control_layer.py').chmod(0o664)
    result=cli(f,gate=True)
    assert result.returncode==0,result.stdout+result.stderr


@pytest.mark.parametrize('kind',['root_python','root_bytecode'])
def test_root_import_shadow_rejected(transition_fixture,kind):
    f=transition_fixture
    name='shutil.py' if kind=='root_python' else 'shadow.pyc'
    (f['repo']/'.git/info/exclude').write_text(name+'\n')
    (f['repo']/name).write_bytes(b'untrusted ignored runtime code')
    assert_rejected(f,gate=True)


def test_git_replacement_cannot_change_baseline_identity(transition_fixture):
    f=transition_fixture;source=f['repo']/'control/validate_state.py';marker=f['tmp']/'replacement-ran'
    old_oid=fixture_git(f['repo'],'rev-parse',f['base']+':control/validate_state.py')
    payload=source.read_text()+'\nfrom pathlib import Path\nPath('+repr(str(marker))+').write_text("bad")\n'
    replacement=f['tmp']/'replacement.py';replacement.write_text(payload)
    new_oid=fixture_git(f['repo'],'hash-object','-w',str(replacement))
    fixture_git(f['repo'],'replace',old_oid,new_oid)
    source.write_text(payload)
    assert_rejected(f,'controls differ from approved baseline',gate=True)
    assert not marker.exists()
