#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent
REPO = Path('/mnt/data-drive/godot_engain_3d_avatar')
CONTRACT_NAME = 'ENGAV3D-STAGE8-TICKET-3D-LAUNCHER-OWNED-WORKER-SUPERVISION.md'
CONTRACT_HASH = '1112646314d862e688e906699b201722d1aef18481e98a0a71d0f56ad685a8cd'
HEAD = '77593c205851c97a1b0b46ebdb6ade270309f81a'
STATUS_SHA = '0a5bad930b64de2d69e5a0c6c51420aa5f4b821c672377f00676651eab3fd1f6'
DIFF_SHA = '4f3eb7f0b4f538b810ef9fc33f54c7a0345e2375403c6c55ae712b4310241b28'
DIRTY = {'hermes_session_adapter.py': 'fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542', 'scenes/ControlHUD.tscn': 'd20e7e87dd5121f20a29cee865e5e9ef2cf4bc916addcd5cc3dc5559ea74ddc1', 'scripts/ControlHUD.gd': '96afd4f81669830d69e541a6e26e843a41eda6c9c642c18de7e6d50aa68fcd81', 'scripts/DragonAvatar3D.gd': 'ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38', 'scripts/EngAInBridge3D.gd': '021b7838d8984e4c55f10a226f70319a1b53bf2101b5a70e9889a72cda7167e1', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json': 'c5588884a45c6ab6ab7be7df1a102d3411431d488a25cca01c8dc240f26028aa', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png': 'ddbca6833ba8f8a44c733e2a2feceabbac96d5a238b1a360ae2da690268fc858', 'snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import': '12ce78ab051d67ce9200edd6a0f46cc067b10cce548bcc41cc6c24fbdf8b75b8', 'tests/test_stage8_ticket2c_text_only_adapter_red.py': '17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af', 'tests/test_stage8_ticket2c_text_only_bridge_red.py': 'fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465', 'tests/test_stage8_ticket2e_persistent_worker_red.py': 'db705f501187709b55f927faa589bafad93a3cb6e72368387b0a4dcc5914d068', 'tests/test_stage8_ticket3b_godot_routing_red.py': '0b7f189de9864588fcc8e273e5e64b3824e36e6ec7331a34049fb1c171c1c973', 'tests/test_stage8_ticket3b_hud_lifecycle_red.py': 'da9533c8c83f20cf15037c4723ecfb495603c4661887eb9eb4f180fe15bf0f8c', 'tests/test_stage8_ticket3b_worker_ownership_red.py': '7868afe8cd4fc09a839de746f28f9bd2e9fcbeb42fdc78a0bb8b5fc542b29787'}
UPSTREAM = {'ENGAV3D-0023-STAGE8-TICKET1-PERSISTENT-WORKER-ROUTING-CONTRACT-ADMITTED.sha256': '5cf9e4dfdbb1a04ebd68439cdc535a78029abb3c30e6fab2f49f48d199bfcb79', 'ENGAV3D-0031-STAGE8-TICKET2F-EXPLICIT-WORKER-STOP-GREEN.sha256': '7f7fe8b649c4516006a7fc50860c1f015943a09ca761c1782b9ffd446cb90425', 'ENGAV3D-0032-STAGE8-TICKET3A-HUD-CAPTURE-ORDER-ADMITTED.sha256': '22a3b56795a010b178d8ad7ab4c641841534b4613dd3c616433406d59273f0ac', 'ENGAV3D-0034-STAGE8-TICKET3C-GODOT-ROUTING-HUD-GREEN.sha256': 'de27976642f6807a984052c5c93bcb4d18d2d26803b7ab051fff1494ac43820e'}
REQUIRED = ['WORKER_SUPERVISION_OWNER=RUNTIME_LAUNCHER', 'GODOT_SPAWNS_PYTHON=FORBIDDEN', 'worker.prepare()', 'worker state == READY', 'BEFORE\nGodot runtime becomes available', 'request_stop() on that same worker instance', 'worker state == STOPPED', 'Ticket 3D deliberately does not choose an external readiness representation.', 'No status JSON, readiness mailbox, socket, health endpoint, PID observation', 'invoke adapter `--once` per submission', 'invoke `process_once()` as its runtime worker', 'call `OS.create_process()` to construct the adapter', 'restart a `STOPPED` worker instance', 'infer worker identity or readiness merely because mailbox files exist', 'Ticket 3E may add the minimum launcher/runtime surface']
EXPECTED_FAILURES = {'test_ticket3b_runtime_boundary_makes_exactly_one_persistent_worker_available', 'test_ticket3b_multiple_submissions_share_one_observed_worker_identity', 'test_ticket3b_runtime_shutdown_requests_ticket2f_explicit_stop'}
def digest_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def digest(path: Path) -> str: return digest_bytes(path.read_bytes())
def reject(detail: str) -> None:
    print('STAGE8_TICKET3D_CONTRACT_REJECTED: ' + detail)
    raise SystemExit(1)
def run(args, timeout=300):
    return subprocess.run(args, cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
contract = ROOT / CONTRACT_NAME
if digest(contract) != CONTRACT_HASH: reject('contract identity differs')
if (AUDIT / CONTRACT_NAME).read_bytes() != contract.read_bytes(): reject('audit contract copy differs')
sidecar = subprocess.run(['sha256sum','-c',CONTRACT_NAME + '.sha256'], cwd=AUDIT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
if sidecar.returncode != 0: reject('contract sidecar failed')
for name, expected in UPSTREAM.items():
    path = AUDIT / name
    if digest(path) != expected: reject('upstream sidecar identity differs: ' + name)
    checked = subprocess.run(['sha256sum','-c',name], cwd=AUDIT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if checked.returncode != 0: reject('upstream authority failed: ' + name)
if run(['git','rev-parse','HEAD']).stdout.strip() != HEAD: reject('HEAD differs')
status = run(['git','status','--porcelain=v1','-uall']).stdout
if digest_bytes(status.encode()) != STATUS_SHA: reject('repository status differs')
diff = run(['git','diff','--binary']).stdout.encode()
if digest_bytes(diff) != DIFF_SHA: reject('tracked diff differs')
for relative, expected in DIRTY.items():
    path = REPO / relative
    if not path.is_file() or digest(path) != expected: reject('dirty identity differs: ' + relative)
text = contract.read_text(encoding='utf-8')
for token in REQUIRED:
    if token not in text: reject('required contract token absent: ' + token)
worker = run([sys.executable,'-m','pytest','-q','tests/test_stage8_ticket3b_worker_ownership_red.py'])
failed = set(re.findall(r'^FAILED .*::([^\s]+)', worker.stdout, re.MULTILINE))
if worker.returncode == 0 or '3 failed, 1 passed' not in worker.stdout or failed != EXPECTED_FAILURES: reject('worker ownership RED identity differs')
for forbidden in ('ERROR collecting','ERROR at setup','SyntaxError','INTERNALERROR'):
    if forbidden in worker.stdout: reject('invalid worker RED class: ' + forbidden)
bridge = (REPO / 'scripts/EngAInBridge3D.gd').read_text(encoding='utf-8')
main = (REPO / 'scripts/Main.gd').read_text(encoding='utf-8')
if 'OS.create_process' in bridge or 'OS.create_process' in main: reject('Godot Python spawning appeared')
print('STAGE8_TICKET3D_LAUNCHER_WORKER_OWNERSHIP_ADMITTED')
print('WORKER_SUPERVISION_OWNER=RUNTIME_LAUNCHER')
print('READY_BEFORE_GODOT=DEFINED')
print('ONE_LAUNCHER_GENERATION_ONE_WORKER_GENERATION=DEFINED')
print('SAME_WORKER_ACROSS_SUBMISSIONS=DEFINED')
print('GODOT_EXIT_REQUEST_STOP_STOPPED=DEFINED')
print('EXTERNAL_READINESS_REPRESENTATION=DEFERRED')
print('GODOT_PYTHON_SPAWN=FORBIDDEN')
print('WORKER_OWNERSHIP_RED=3_FAILED_1_PASSED_PRESERVED')
print('REPOSITORY_WORKING_TREE=BYTE_IDENTICAL_TO_TICKET3C_SEAL')
print('PROVIDER_EXECUTIONS=0')
print('TICKET3E_IMPLEMENTATION=NOT_AUTHORIZED')
