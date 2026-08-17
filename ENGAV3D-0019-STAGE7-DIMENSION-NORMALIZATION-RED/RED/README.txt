ENGAV3D-0019 Stage 7 dimension-normalization intentional RED.

Baseline:
cfcea38d97fb6d3ad06a1319a1214bf7698a5df4

The regression contains two checks:

1. Runtime environment check:
   Godot JSON parsing materializes integer-looking JSON dimensions as floats.

2. Production regression check:
   PerceptionCapture3D._capture_persisted() must restore persisted
   viewport width and height to integer wire types before forwarding
   the persisted metadata object.

Expected baseline result:
1 passed
1 failed

The failure must specifically be the absence of persisted width
normalization in the unfixed production source.

Provider executions:
0
