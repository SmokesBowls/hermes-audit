Post-abort diagnostic preservation for ENGAV3D-0018.

0018 failed before request publication.

Observed runtime failure:
Live capture failed its frozen result contract.

Subsequent provider-free diagnosis identified JSON numeric materialization:
persisted viewport width/height are parsed by Godot as floating-point values,
while the frozen bridge contract requires integer dimension fields.

Current repository state was preserved here before cleanup or commit.

The PerceptionCapture3D.gd working-tree modification is the candidate fix.

DragonAvatar3D.gd contains an unrelated pre-existing working-tree modification
and is not part of the Stage 7 fix.

Four capture artifact groups currently exist under snapshots/ and are preserved
by path, stat, metadata summary, and SHA-256 inventory.

No provider execution occurred during 0018 or the diagnosis.
