# ENGAV3D-0001 Amendment 1 — Stage 5B Preparation Boundary

## Purpose

This amendment defines the missing no-dispatch preparation boundary required
for Stage 5B image-bearing provider proof.

It does NOT modify, replace, or weaken the original frozen artifact:

ENGAV3D-0001-IDENTITY-MAILBOX-PERCEPTION-FREEZE.md

It does NOT modify the frozen mailbox request, mailbox response,
runtime-perception, runtime-snapshot, or runtime-perception-result schemas.

## Existing frozen identities remain authoritative

project_id:
godot_3d_avatar

scene_path:
res://scenes/Main.tscn

dragon_scene_path:
res://scenes/DragonAvatar3D.tscn

Hermes profile:
default

session_id:
20260731_065008_63a62d

companion:
hermes_b

provider:
openai-codex

model:
gpt-5.6-sol

## dragon_scene_path clarification

dragon_scene_path is NOT added to the frozen mailbox request or metadata
schemas.

For Stage 5B it is a required local pre-dispatch preparation-context identity.

The preparation boundary MUST receive or otherwise expose this identity as a
separately validated local preparation value.

The accepted value is exactly:

res://scenes/DragonAvatar3D.tscn

Any different value MUST be rejected before provider execution.

This establishes Stage 5B dispatch-context binding to the frozen nested Dragon
presentation without changing the already-frozen serialized mailbox schemas.

This amendment does not retroactively claim that dragon_scene_path was serialized
inside the accepted Stage 5A PNG or metadata artifact.

## Required public no-dispatch boundary

hermes_session_adapter.py MUST expose a public preparation-only boundary named:

prepare_image_dispatch

The preparation boundary MUST:

1. consume the normal frozen mailbox/perception evidence through the existing
   validation machinery rather than bypassing it;

2. validate the accepted persisted perception image from disk;

3. validate the persisted image SHA-256 against the correlated metadata;

4. validate the frozen request, client-request, capture, project, scene,
   session, provider, model, and perception identities already required by
   ENGAV3D-0001;

5. separately validate:

   dragon_scene_path =
   res://scenes/DragonAvatar3D.tscn

6. construct the frozen contract-level Hermes command representation;

7. translate that command to the actually supported Hermes CLI representation;

8. append or preserve the exact validated canonical image path as the value of
   --image;

9. return both the contract representation and the actual executable
   representation to the caller;

10. perform ZERO subprocess, Hermes, provider, network, HTTP, or mailbox
    dispatch operations.

## Command representations

The contract representation retains the frozen profile selector:

--profile default

The executable representation uses the already-proven supported selector:

-p default

The executable image-bearing command must contain the semantic equivalent of:

-p default
chat
--resume 20260731_065008_63a62d
--no-restore-cwd
--provider openai-codex
-m gpt-5.6-sol
--image <validated canonical persisted PNG path>

The path following --image MUST be the exact canonical validated image path.
Presence of an arbitrary --image argument is insufficient.

## Fail-closed rule

prepare_image_dispatch MUST return no executable dispatch preparation when any
required identity, hash, path, PNG structure, dimension, session correlation,
or dragon_scene_path validation fails.

Provider execution remains forbidden during preparation.

## Stage 5A authority

The accepted Stage 5A PNG and JSON remain immutable evidence.

No recapture or rewritten metadata may be substituted merely to satisfy
Stage 5B.

## Test chronology

After this amendment is sealed:

1. Stage 5B tests are written first.
2. They are run against the current adapter.
3. RED caused by the absent preparation boundary is preserved.
4. Only then may hermes_session_adapter.py be modified.
5. Stage 4 and Stage 5A protected tests remain byte-identical.
6. The same Stage 5B test bytes must turn GREEN through implementation.

## Provider allowance

This amendment authorizes ZERO provider requests.

A live Stage 5B image-bearing provider request requires a separate explicit
authorization after the complete offline preparation gate is green.
