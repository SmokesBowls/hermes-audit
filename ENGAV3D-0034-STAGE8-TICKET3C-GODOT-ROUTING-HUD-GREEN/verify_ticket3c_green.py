#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPO = Path('/mnt/data-drive/godot_engain_3d_avatar')
HEAD = '77593c205851c97a1b0b46ebdb6ade270309f81a'
STATUS_SHA = '0a5bad930b64de2d69e5a0c6c51420aa5f4b821c672377f00676651eab3fd1f6'
TRACKED_DIFF_SHA = '4f3eb7f0b4f538b810ef9fc33f54c7a0345e2375403c6c55ae712b4310241b28'
DIRTY = {'hermes_session_adapter.py': 'fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542', 'scenes/ControlHUD.tscn': 'd20e7e87dd5121f20a29cee865e5e9ef2cf4bc916addcd5cc3dc5559ea74ddc1', 'scripts/ControlHUD.gd': '96afd4f81669830d69e541a6e26e843a41eda6c9c642c18de7e6d50aa68fcd81', 'scripts/DragonAvatar3D.gd': 'ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38', 'scripts/EngAInBridge3D.gd': '021b7838d8984e4c55f10a226f70319a1b53bf2101b5a70e9889a72cda7167e1', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json': 'c5588884a45c6ab6ab7be7df1a102d3411431d488a25cca01c8dc240f26028aa', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png': 'ddbca6833ba8f8a44c733e2a2feceabbac96d5a238b1a360ae2da690268fc858', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import': '12ce78ab051d67ce9200edd6a0f46cc067b10cce548bcc41cc6c24fbdf8b75b8', 'tests/test_stage8_ticket2c_text_only_adapter_red.py': '17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af', 'tests/test_stage8_ticket2c_text_only_bridge_red.py': 'fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465', 'tests/test_stage8_ticket2e_persistent_worker_red.py': 'db705f501187709b55f927faa589bafad93a3cb6e72368387b0a4dcc5914d068', 'tests/test_stage8_ticket3b_godot_routing_red.py': '0b7f189de9864588fcc8e273e5e64b3824e36e6ec7331a34049fb1c171c1c973', 'tests/test_stage8_ticket3b_hud_lifecycle_red.py': 'da9533c8c83f20cf15037c4723ecfb495603c4661887eb9eb4f180fe15bf0f8c', 'tests/test_stage8_ticket3b_worker_ownership_red.py': '7868afe8cd4fc09a839de746f28f9bd2e9fcbeb42fdc78a0bb8b5fc542b29787'}
FOCUSED = ['tests/test_stage8_ticket3b_godot_routing_red.py', 'tests/test_stage8_ticket3b_hud_lifecycle_red.py']
WORKER = 'tests/test_stage8_ticket3b_worker_ownership_red.py'
EXPECTED_FAILURES = {'test_ticket3b_runtime_boundary_makes_exactly_one_persistent_worker_available', 'test_ticket3b_multiple_submissions_share_one_observed_worker_identity', 'test_ticket3b_runtime_shutdown_requests_ticket2f_explicit_stop'}
FORBIDDEN_GODOT = ('SCRIPT ERROR', 'Parse Error', 'Failed to load script', 'Cannot load source code')
def digest_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def digest(path: Path) -> str: return digest_bytes(path.read_bytes())
def reject(detail: str) -> None:
    print('STAGE8_TICKET3C_GREEN_REJECTED: ' + detail)
    raise SystemExit(1)
def run(args, timeout=600):
    return subprocess.run(args, cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
if run(['git','rev-parse','HEAD']).stdout.strip() != HEAD: reject('HEAD differs')
status = run(['git','status','--porcelain=v1','-uall']).stdout
if digest_bytes(status.encode()) != STATUS_SHA: reject('working-tree status identity differs')
diff = run(['git','diff','--binary']).stdout.encode()
if digest_bytes(diff) != TRACKED_DIFF_SHA: reject('tracked diff identity differs')
for relative, expected in DIRTY.items():
    path = REPO / relative
    if not path.is_file() or digest(path) != expected: reject('dirty path identity differs: ' + relative)
for relative in ['scenes/ControlHUD.tscn', 'scripts/ControlHUD.gd', 'scripts/EngAInBridge3D.gd', 'tests/test_stage8_ticket3b_godot_routing_red.py', 'tests/test_stage8_ticket3b_hud_lifecycle_red.py']:
    if (REPO / relative).read_bytes() != (ROOT / 'working-tree' / relative).read_bytes(): reject('evidence copy differs: ' + relative)
focused = run([sys.executable,'-m','pytest','-q',*FOCUSED])
if focused.returncode != 0 or '10 passed' not in focused.stdout: reject('focused Ticket 3C differs')
protected = run([sys.executable,'-m','pytest','-q','--ignore=' + WORKER])
if protected.returncode != 0 or '206 passed' not in protected.stdout: reject('protected non-worker suite differs')
complete = run([sys.executable,'-m','pytest','-q'])
failed = set(re.findall(r'^FAILED .*::([^\s]+)', complete.stdout, re.MULTILINE))
if complete.returncode == 0 or '3 failed, 207 passed' not in complete.stdout or failed != EXPECTED_FAILURES: reject('complete expected-worker-RED result differs')
godot = run(['/home/mytruelove/.local/bin/godot','--headless','--path',str(REPO),'--editor','--quit'], timeout=120)
if godot.returncode != 0 or any(token in godot.stdout for token in FORBIDDEN_GODOT): reject('Godot parse/load differs')
if run(['git','diff','--check']).returncode != 0: reject('git diff check differs')
print('STAGE8_TICKET3C_GODOT_ROUTING_HUD_GREEN')
print('FOCUSED_TICKET3C=10_PASSED')
print('PROTECTED_NON_WORKER=206_PASSED')
print('COMPLETE_COLLECTION=207_PASSED_3_EXPECTED_WORKER_OWNERSHIP_RED')
print('EXPECTED_WORKER_FAILURE_IDENTITIES=PASS')
print('GODOT_PARSE_LOAD=PASS')
print('WORKING_TREE_IDENTITIES=PRESERVED')
print('PROVIDER_EXECUTIONS=0')
print('WORKER_OWNERSHIP=UNTOUCHED')
