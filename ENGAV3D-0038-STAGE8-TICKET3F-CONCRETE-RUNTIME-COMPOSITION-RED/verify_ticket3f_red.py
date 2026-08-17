#!/usr/bin/env python3
import hashlib,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; REPO=Path('/mnt/data-drive/godot_engain_3d_avatar'); TEST='tests/test_stage8_ticket3f_runtime_composition_red.py'; T3E='tests/test_stage8_ticket3e_launcher_supervision_red.py'; HEAD='77593c205851c97a1b0b46ebdb6ade270309f81a'; DIFF='4f3eb7f0b4f538b810ef9fc33f54c7a0345e2375403c6c55ae712b4310241b28'; TEST_HASH='1b3961ec020fa56ddacf5099abdd761e0d7df5592f9eee04a32616c100acba4a'; LAUNCH_HASH='e2388f74953a452f5626565fcde7d6e5abc4c92eb01187570d9cf03abd62ec96'; T3E_HASH='c89aa2153d2a7bb1db50a6b1cf901ef8cefa655f8d0244a1911b56e26e78d68d'; DIRTY={'hermes_session_adapter.py': 'fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542', 'scenes/ControlHUD.tscn': 'd20e7e87dd5121f20a29cee865e5e9ef2cf4bc916addcd5cc3dc5559ea74ddc1', 'scripts/ControlHUD.gd': '96afd4f81669830d69e541a6e26e843a41eda6c9c642c18de7e6d50aa68fcd81', 'scripts/DragonAvatar3D.gd': 'ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38', 'scripts/EngAInBridge3D.gd': '021b7838d8984e4c55f10a226f70319a1b53bf2101b5a70e9889a72cda7167e1', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json': 'c5588884a45c6ab6ab7be7df1a102d3411431d488a25cca01c8dc240f26028aa', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png': 'ddbca6833ba8f8a44c733e2a2feceabbac96d5a238b1a360ae2da690268fc858', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import': '12ce78ab051d67ce9200edd6a0f46cc067b10cce548bcc41cc6c24fbdf8b75b8', 'tests/test_stage8_ticket2c_text_only_adapter_red.py': '17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af', 'tests/test_stage8_ticket2c_text_only_bridge_red.py': 'fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465', 'tests/test_stage8_ticket2e_persistent_worker_red.py': 'db705f501187709b55f927faa589bafad93a3cb6e72368387b0a4dcc5914d068', 'tests/test_stage8_ticket3b_godot_routing_red.py': '0b7f189de9864588fcc8e273e5e64b3824e36e6ec7331a34049fb1c171c1c973', 'tests/test_stage8_ticket3b_hud_lifecycle_red.py': 'da9533c8c83f20cf15037c4723ecfb495603c4661887eb9eb4f180fe15bf0f8c', 'tests/test_stage8_ticket3b_worker_ownership_red.py': '7868afe8cd4fc09a839de746f28f9bd2e9fcbeb42fdc78a0bb8b5fc542b29787'}; EXPECTED=['tests/test_stage8_ticket3f_runtime_composition_red.py::test_ticket3f_concrete_binding_owns_one_real_adapter_shape_and_exclusive_generation', 'tests/test_stage8_ticket3f_runtime_composition_red.py::test_ticket3f_ready_and_persistent_servicing_precede_and_outlive_godot', 'tests/test_stage8_ticket3f_runtime_composition_red.py::test_ticket3f_non_ready_generation_fails_closed_before_godot', 'tests/test_stage8_ticket3f_runtime_composition_red.py::test_ticket3f_godot_launch_failure_completes_same_worker_stop_and_releases_ownership', 'tests/test_stage8_ticket3f_runtime_composition_red.py::test_ticket3f_non_editor_process_and_executable_entry_are_concrete_but_injected']
def d(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a): return subprocess.run(a,cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
def reject(s): print('STAGE8_TICKET3F_RED_REJECTED: '+s); raise SystemExit(1)
def sp(line):
 x=line.strip().split(maxsplit=1); return x[1] if len(x)==2 else ''
if run(['git','rev-parse','HEAD']).stdout.strip()!=HEAD: reject('HEAD differs')
x=subprocess.run('git diff --binary | sha256sum',cwd=REPO,shell=True,text=True,stdout=subprocess.PIPE)
if x.stdout.split()[0]!=DIFF: reject('tracked diff differs')
if d(REPO/TEST)!=TEST_HASH or d(ROOT/Path(TEST).name)!=TEST_HASH: reject('Ticket 3F test differs')
if d(REPO/'runtime_launcher.py')!=LAUNCH_HASH or d(REPO/T3E)!=T3E_HASH: reject('upstream bytes differ')
for rel,h in DIRTY.items():
 p=REPO/rel
 if not p.is_file() or d(p)!=h: reject('dirty identity differs: '+rel)
known=set(DIRTY)|{'runtime_launcher.py',T3E,TEST}
for line in run(['git','status','--porcelain=v1','-uall']).stdout.splitlines():
 if sp(line) not in known: reject('unauthorized path: '+line)
compile=run([sys.executable,'-m','py_compile',TEST])
if compile.returncode: reject('test compile failed')
r=run([sys.executable,'-m','pytest','-q',TEST]); ids=re.findall(r'^FAILED\s+([^\s]+)',r.stdout,re.M)
if r.returncode==0 or '5 failed, 3 passed' not in r.stdout or ids!=EXPECTED: reject('focused RED differs')
if r.stdout.count('QUALIFYING_CONCRETE_RUNTIME_COMPOSITION_BOUNDARY_DOES_NOT_EXIST')<5: reject('missing-boundary identity differs')
for toxic in ('ERROR collecting','ERROR at setup','SyntaxError','INTERNALERROR',"fixture '"):
 if toxic in r.stdout: reject('malformed RED: '+toxic)
g=run([sys.executable,'-m','pytest','-q',T3E])
if g.returncode or '7 passed' not in g.stdout: reject('Ticket 3E preservation differs')
print('STAGE8_TICKET3F_CONCRETE_RUNTIME_COMPOSITION_RED')
print('TICKET_3F_RED=CONFIRMED')
print('RED_FAILURE_REASON=QUALIFYING_CONCRETE_RUNTIME_COMPOSITION_BOUNDARY_DOES_NOT_EXIST')
print('FOCUSED_RESULT=5_FAILED_3_PASSED')
print('TICKET3E_PRESERVATION=7_PASSED')
print('RUNTIME_LAUNCHER_CHANGED=0')
print('ADAPTER_CHANGED=0')
print('OTHER_PRODUCTION_FILES_CHANGED=0')
print('GODOT_EXECUTIONS=0')
print('WORKER_EXECUTIONS=0')
print('PROVIDER_EXECUTIONS=0')
print('TICKET_3F_GREEN=NOT_BEGUN')
print('LIVE_VALIDATION=NOT_BEGUN')
print('NEXT_TICKET=NOT_BEGUN')
