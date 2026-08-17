#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; AUDIT=ROOT.parent; REPO=Path('/mnt/data-drive/godot_engain_3d_avatar')
HEAD='77593c205851c97a1b0b46ebdb6ade270309f81a'; LAUNCHER_REL='runtime_launcher.py'; LAUNCHER_HASH='e2388f74953a452f5626565fcde7d6e5abc4c92eb01187570d9cf03abd62ec96'; TEST_REL='tests/test_stage8_ticket3e_launcher_supervision_red.py'; TEST_HASH='c89aa2153d2a7bb1db50a6b1cf901ef8cefa655f8d0244a1911b56e26e78d68d'; DIFF_HASH='4f3eb7f0b4f538b810ef9fc33f54c7a0345e2375403c6c55ae712b4310241b28'; DIRTY={'hermes_session_adapter.py': 'fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542', 'scenes/ControlHUD.tscn': 'd20e7e87dd5121f20a29cee865e5e9ef2cf4bc916addcd5cc3dc5559ea74ddc1', 'scripts/ControlHUD.gd': '96afd4f81669830d69e541a6e26e843a41eda6c9c642c18de7e6d50aa68fcd81', 'scripts/DragonAvatar3D.gd': 'ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38', 'scripts/EngAInBridge3D.gd': '021b7838d8984e4c55f10a226f70319a1b53bf2101b5a70e9889a72cda7167e1', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json': 'c5588884a45c6ab6ab7be7df1a102d3411431d488a25cca01c8dc240f26028aa', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png': 'ddbca6833ba8f8a44c733e2a2feceabbac96d5a238b1a360ae2da690268fc858', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import': '12ce78ab051d67ce9200edd6a0f46cc067b10cce548bcc41cc6c24fbdf8b75b8', 'tests/test_stage8_ticket2c_text_only_adapter_red.py': '17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af', 'tests/test_stage8_ticket2c_text_only_bridge_red.py': 'fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465', 'tests/test_stage8_ticket2e_persistent_worker_red.py': 'db705f501187709b55f927faa589bafad93a3cb6e72368387b0a4dcc5914d068', 'tests/test_stage8_ticket3b_godot_routing_red.py': '0b7f189de9864588fcc8e273e5e64b3824e36e6ec7331a34049fb1c171c1c973', 'tests/test_stage8_ticket3b_hud_lifecycle_red.py': 'da9533c8c83f20cf15037c4723ecfb495603c4661887eb9eb4f180fe15bf0f8c', 'tests/test_stage8_ticket3b_worker_ownership_red.py': '7868afe8cd4fc09a839de746f28f9bd2e9fcbeb42fdc78a0bb8b5fc542b29787'}; RED_SIDECAR_HASH='15beb36e3264485a210b92020e67e4220a86a1cd55c680b45e981f717b8973ae'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def reject(s): print('STAGE8_TICKET3E_GREEN_REJECTED: '+s); raise SystemExit(1)
def run(a): return subprocess.run(a,cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180,check=False)
def status_path(line):
 parts=line.strip().split(maxsplit=1); return parts[1] if len(parts)==2 else ''
if run(['git','rev-parse','HEAD']).stdout.strip()!=HEAD: reject('HEAD differs')
if digest(REPO/LAUNCHER_REL)!=LAUNCHER_HASH or digest(ROOT/Path(LAUNCHER_REL).name)!=LAUNCHER_HASH: reject('launcher identity differs')
if digest(REPO/TEST_REL)!=TEST_HASH or digest(ROOT/Path(TEST_REL).name)!=TEST_HASH: reject('RED test identity differs')
d=subprocess.run('git diff --binary | sha256sum',cwd=REPO,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if d.returncode or d.stdout.split()[0]!=DIFF_HASH: reject('tracked production diff differs')
for rel,expected in DIRTY.items():
 p=REPO/rel
 if not p.is_file() or digest(p)!=expected: reject('dirty identity differs: '+rel)
status=run(['git','status','--porcelain=v1','-uall']).stdout.splitlines(); known=set(DIRTY)|{TEST_REL,LAUNCHER_REL}
for line in status:
 if status_path(line) not in known: reject('unauthorized path: '+line)
if LAUNCHER_REL not in {status_path(x) for x in status}: reject('launcher absent')
if digest(AUDIT/'ENGAV3D-0036-STAGE8-TICKET3E-LAUNCHER-SUPERVISION-RED.sha256')!=RED_SIDECAR_HASH: reject('RED sidecar differs')
source=(REPO/LAUNCHER_REL).read_text(encoding='utf-8'); tree=ast.parse(source,filename=LAUNCHER_REL)
if 'ENGAV3D_STAGE8_TICKET3E_LAUNCHER_SUPERVISION_V1' not in source: reject('marker absent')
functions={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
if not {'run_runtime_generation','_stop_worker'} <= functions: reject('launcher API incomplete')
imports={alias.name for node in ast.walk(tree) if isinstance(node,(ast.Import,ast.ImportFrom)) for alias in node.names}
if any(x.startswith(('subprocess','socket','urllib','http')) for x in imports): reject('launcher widened into execution/network mechanics')
for rel in ('scripts/EngAInBridge3D.gd','scripts/ControlHUD.gd','scripts/Main.gd'):
 godot=(REPO/rel).read_text(encoding='utf-8')
 if 'OS.create_process' in godot or 'request_stop' in godot: reject('Godot ownership differs: '+rel)
if run([sys.executable,'-m','py_compile',LAUNCHER_REL,TEST_REL]).returncode: reject('compile failed')
f=run([sys.executable,'-m','pytest','-q',TEST_REL]); r=run([sys.executable,'-m','pytest','-q','tests/test_stage8_ticket2e_persistent_worker_red.py',TEST_REL])
if f.returncode or '7 passed' not in f.stdout: reject('focused GREEN differs')
if r.returncode or '12 passed' not in r.stdout: reject('regression differs')
print('STAGE8_TICKET3E_LAUNCHER_SUPERVISION_GREEN')
print('TICKET_3E_GREEN=CONFIRMED')
print('LAUNCHER_ENTRY_POINT='+LAUNCHER_REL)
print('LAUNCHER_MARKER=ENGAV3D_STAGE8_TICKET3E_LAUNCHER_SUPERVISION_V1')
print('FOCUSED_RESULT=7_PASSED')
print('REGRESSION_RESULT=12_PASSED')
print('PRODUCTION_FILES_CREATED='+LAUNCHER_REL)
print('PRODUCTION_FILES_CHANGED=0')
print('TEST_FILES_CHANGED=0')
print('GODOT_EXECUTIONS=0')
print('WORKER_EXECUTIONS=0')
print('PROVIDER_EXECUTIONS=0')
print('LIVE_VALIDATION=NOT_BEGUN')
print('NEXT_TICKET=NOT_BEGUN')
