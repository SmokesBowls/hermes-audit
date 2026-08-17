ENGAV3D-0020 — Stage 7 dimension-normalization offline GREEN

RED authority:
ENGAV3D-0019-STAGE7-DIMENSION-NORMALIZATION-RED

Baseline:
cfcea38d97fb6d3ad06a1319a1214bf7698a5df4

Committed GREEN HEAD:
77593c205851c97a1b0b46ebdb6ade270309f81a

Production correction:
PerceptionCapture3D restores persisted viewport width and height to their
frozen integer wire types after JSON parsing and before forwarding the
persisted metadata object.

Frozen regression:
2 passed

Complete protected suite:
180 passed

Godot headless editor initialization:
PASS

Post-headless observation:
Godot reproduced a DragonAvatar3D.gd working-tree rewrite whose diff is
byte-for-byte identical to the unrelated rewrite already preserved in 0018.
That rewrite is outside this correction scope. It was preserved here and the
Dragon source was restored to committed HEAD before final repository admission.

The earlier git-status-final.txt records the deliberate STOP caused by that
post-headless rewrite. git-status-after-restore.txt records the final admitted
clean repository state.

Committed scope:
M scripts/PerceptionCapture3D.gd
A tests/test_stage7_dimension_normalization.py

Final repository state:
CLEAN

Finalized request mailbox:
ABSENT

Finalized response mailbox:
ABSENT

Provider executions:
0

Live HUD submissions:
0

No live crossing is authorized by this gate.
