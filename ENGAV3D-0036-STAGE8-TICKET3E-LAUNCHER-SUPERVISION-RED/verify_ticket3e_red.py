#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; AUDIT=ROOT.parent; REPO=Path('/mnt/data-drive/godot_engain_3d_avatar')
TEST_REL='tests/test_stage8_ticket3e_launcher_supervision_red.py'; TEST_HASH='c89aa2153d2a7bb1db50a6b1cf901ef8cefa655f8d0244a1911b56e26e78d68d'; HEAD='77593c205851c97a1b0b46ebdb6ade270309f81a'; DIFF_HASH='4f3eb7f0b4f538b810ef9fc33f54c7a0345e2375403c6c55ae712b4310241b28'; DIRTY={'hermes_session_adapter.py': 'fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542', 'scenes/ControlHUD.tscn': 'd20e7e87dd5121f20a29cee865e5e9ef2cf4bc916addcd5cc3dc5559ea74ddc1', 'scripts/ControlHUD.gd': '96afd4f81669830d69e541a6e26e843a41eda6c9c642c18de7e6d50aa68fcd81', 'scripts/DragonAvatar3D.gd': 'ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38', 'scripts/EngAInBridge3D.gd': '021b7838d8984e4c55f10a226f70319a1b53bf2101b5a70e9889a72cda7167e1', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json': 'c5588884a45c6ab6ab7be7df1a102d3411431d488a25cca01c8dc240f26028aa', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png': 'ddbca6833ba8f8a44c733e2a2feceabbac96d5a238b1a360ae2da690268fc858', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import': '12ce78ab051d67ce9200edd6a0f46cc067b10cce548bcc41cc6c24fbdf8b75b8', 'tests/test_stage8_ticket2c_text_only_adapter_red.py': '17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af', 'tests/test_stage8_ticket2c_text_only_bridge_red.py': 'fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465', 'tests/test_stage8_ticket2e_persistent_worker_red.py': 'db705f501187709b55f927faa589bafad93a3cb6e72368387b0a4dcc5914d068', 'tests/test_stage8_ticket3b_godot_routing_red.py': '0b7f189de9864588fcc8e273e5e64b3824e36e6ec7331a34049fb1c171c1c973', 'tests/test_stage8_ticket3b_hud_lifecycle_red.py': 'da9533c8c83f20cf15037c4723ecfb495603c4661887eb9eb4f180fe15bf0f8c', 'tests/test_stage8_ticket3b_worker_ownership_red.py': '7868afe8cd4fc09a839de746f28f9bd2e9fcbeb42fdc78a0bb8b5fc542b29787'}; FAILURES={'test_ticket3e_ready_precedes_godot_and_one_worker_owns_generation', 'test_ticket3e_launcher_waits_boundedly_for_terminal_stopped', 'test_ticket3e_prepare_failure_prevents_godot_and_no_fallback_worker', 'test_ticket3e_godot_launch_failure_stops_the_same_ready_worker', 'test_ticket3e_non_ready_worker_prevents_godot_start'}; REASON='qualifying production launcher/supervision boundary does not exist; Ticket 3D requires exactly one production Python entry point marked ENGAV3D_STAGE8_TICKET3E_LAUNCHER_SUPERVISION_V1, but found 0'; UPSTREAM_HASH='4512c70719d26be7f2c3b6f32fc2b9f4934b5e29cd765f5712871bffddebf9ca'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def reject(s): print('STAGE8_TICKET3E_RED_REJECTED: '+s); raise SystemExit(1)
def run(a): return subprocess.run(a,cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180,check=False)
if run(['git','rev-parse','HEAD']).stdout.strip()!=HEAD: reject('HEAD differs')
if digest(REPO/TEST_REL)!=TEST_HASH or digest(ROOT/Path(TEST_REL).name)!=TEST_HASH: reject('test identity differs')
d=subprocess.run('git diff --binary | sha256sum',cwd=REPO,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if d.returncode or d.stdout.split()[0]!=DIFF_HASH: reject('tracked production diff differs')
for rel,expected in DIRTY.items():
 p=REPO/rel
 if not p.is_file() or digest(p)!=expected: reject('dirty identity differs: '+rel)
status=run(['git','status','--porcelain=v1','-uall']).stdout.splitlines(); known=set(DIRTY)|{TEST_REL}
if f'?? {TEST_REL}' not in status: reject('RED test absent')
for line in status:
 if line[3:] not in known: reject('unauthorized repository path: '+line)
up=AUDIT/'ENGAV3D-0035-STAGE8-TICKET3D-LAUNCHER-WORKER-OWNERSHIP-ADMITTED.sha256'
if digest(up)!=UPSTREAM_HASH: reject('Ticket 3D sidecar differs')
tree=ast.parse((REPO/TEST_REL).read_text(),filename=TEST_REL)
imports={alias.name for node in ast.walk(tree) if isinstance(node,(ast.Import,ast.ImportFrom)) for alias in node.names}
if any(x.startswith(('subprocess','socket','urllib','http')) for x in imports) or 'hermes_session_adapter' in imports: reject('test imports real execution surface')
if run([sys.executable,'-m','py_compile',TEST_REL]).returncode: reject('test compile failed')
r=run([sys.executable,'-m','pytest','-q',TEST_REL]); failed=set(re.findall(r'^FAILED .*::([^\s]+)',r.stdout,re.M))
if r.returncode==0 or failed!=FAILURES or '5 failed, 2 passed' not in r.stdout or REASON not in r.stdout: reject('focused semantic RED differs')
for bad in ('ERROR collecting','ERROR at setup','SyntaxError','INTERNALERROR',"fixture '"):
 if bad in r.stdout: reject('invalid RED class: '+bad)
print('STAGE8_TICKET3E_LAUNCHER_SUPERVISION_RED')
print('TICKET_3E_RED=CONFIRMED')
print('RED_FAILURE_REASON=QUALIFYING_PRODUCTION_LAUNCHER_SUPERVISION_BOUNDARY_DOES_NOT_EXIST')
print('FOCUSED_RESULT=5_FAILED_2_PASSED')
print('PRESERVATION_CONTROLS=2_PASSED')
print('PRODUCTION_FILES_CHANGED=0')
print('GODOT_EXECUTIONS=0')
print('WORKER_EXECUTIONS=0')
print('PROVIDER_EXECUTIONS=0')
print('TICKET_3E_GREEN=NOT_BEGUN')
