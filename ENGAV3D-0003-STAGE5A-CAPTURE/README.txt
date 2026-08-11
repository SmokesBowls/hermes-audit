ENGAV3D-0003 Stage 5A capture evidence

Stage 5A PASS:
one real rendered 3D frame produced one persisted,
request-correlated perception artifact bundle whose
PNG structure, dimensions, identities, paths and
persisted-byte SHA-256 were independently verified,
including fail-closed toxic cases, with zero Hermes
or provider execution.

capture_id=cap_3adeef61cc885c35200be389b975c8d9_1
request_id=req_172deebb27e9096a2e4623590bd9d951
client_request_id=dragon3d_a0122b9cfa997888a7a149c50b9361db_1
session_id=20260731_065008_63a62d
image_sha256=9dc5f0ba825f6193b15e329948a9b3e4754dfe59c22f43c09594bd7bf97fb660
metadata_sha256=dad3fc45fe9fc9e008870aec9034c1ef9ec41615fc7e8bf173782b1cf3e2fac5
viewport=1152x648
stage5a_tests=26 passed
stage4_adapter_regression=37 passed
toxic_tests=22 passed, 4 deselected
ad_hoc_toxic_cases=10 passed
provider_requests_launched_by_stage5a=0
new_hermes_or_adapter_pids=[]

The failed-attempt logs preserve implementation diagnostics. They are not accepted
capture bundles. Only the PNG/JSON pair named by capture_id above is accepted.
No commit or push was performed.
