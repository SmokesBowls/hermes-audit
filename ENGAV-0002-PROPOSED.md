# ENGAV-0002 — Hermes B Runtime Perception Proof

**Status:** Proposed
**Project:** `/mnt/data-drive/engain_avatar`
**Predecessor:** `ENGAV-0001` Hermes embodiment and persistent-memory proof
**Primary objective:** Give the existing runtime Hermes B session genuine, current, read-only perception of the running Godot scene.

## 1. Purpose

Extend the working Avatar pilot so the same persistent Hermes B conversation that currently receives player text can also receive:

1. a structured snapshot of the current runtime state; and
2. an actual viewport image through a genuinely supported image-ingestion mechanism.

The ticket proves that Hermes B can accurately answer:

> “What do you see?”

It must remain the same Hermes B conversation already proven to retain memory.

## 2. Starting State

The existing proven route is:

```text
Player message
    ↓
Godot runtime
    ↓
EngAInBridge
    ↓
request artifact
    ↓
Hermes session adapter
    ↓
persistent Hermes B session
    ↓
response artifact
    ↓
dragon speech
```

Already proven:

```text
player-to-dragon conversation
persistent Hermes session continuity
multi-turn memory
request/response correlation
timeout fallback
stale-response rejection
```

Not yet proven:

```text
structured runtime awareness
actual viewport-image awareness
grounded visual description
current-versus-remembered perception distinction
```

## 3. Governing Boundary

This ticket begins at:

```text
existing running Avatar scene
    ↓
current runtime snapshot and viewport capture
    ↓
existing Hermes B session
```

It ends at:

```text
grounded read-only description returned through the dragon
```

This ticket does **not** authorize:

```text
GodotOllama modification
editor-dock conversion
Agent Portal implementation
world or scene mutation
movement-code changes
automatic project editing
new companion identities
replacement of Hermes B
new provider sessions when the existing session can be resumed
generalized host/driver architecture
```

## 4. Required Discovery Before Editing

Inspect the actual current implementation of:

```text
EngAInBridge.gd
EngAInDragon.gd
SnapshotManager and its current public outputs
hermes_session_adapter.py
any session_agent implementation actually used
request and response artifact formats
Hermes B session persistence records
viewport and screenshot facilities already present
the exact Hermes/provider invocation mechanism
```

Determine and record:

```text
how the current Hermes B session ID is stored and resumed
what snapshot data already exists
whether snapshots are already captured but not transmitted
how a viewport frame can be captured without changing scene behavior
whether the active Hermes invocation genuinely supports image input
what provider/model receives the image
how image input must be attached to that invocation
```

Do not assume method names, endpoints, image APIs, or transport mechanisms from prior discussion.

## 5. Implementation Requirements

The existing working bridge must remain the baseline. Do not replace the proven file-based route with HTTP or another transport merely for convenience.

Each perception-bearing request must associate:

```text
request identity
Hermes B provider-session identity
player message
snapshot capture time
viewport capture time
structured runtime snapshot
actual viewport image or supported image attachment
project and scene identity where available
```

Hermes B must be able to distinguish:

```text
facts supplied by structured runtime data
facts genuinely observed from the image
facts remembered from earlier conversation
facts that are unavailable or unverified
```

A saved pathname written into a text prompt does not constitute visual ingestion.

Base64 encoding, a temporary PNG, or another image representation is acceptable only when the active Hermes/provider invocation actually consumes that image as image input.

## 6. Snapshot Requirements

Use the existing Snapshot Manager rather than inventing a parallel scene-observation system.

The ticket does not prescribe the Snapshot Manager’s schema before inspection. At minimum, the supplied snapshot should identify whatever the existing manager can truthfully provide about:

```text
current scene
visible or active runtime objects
relevant node identities
object positions or transforms
current runtime state
recent relevant events
capture timestamp
```

Missing information must remain missing. The adapter must not invent scene facts to make the response appear complete.

## 7. Viewport Requirements

Capture the actual current rendered viewport corresponding as closely as practical to the snapshot timestamp.

The capture must:

```text
represent the running game view
be correlated to the player request
avoid stale-image reuse
avoid silently substituting an earlier capture
remain evidence-linked to the response
```

A failed or absent capture must be represented explicitly.

## 8. Failure Behavior

The system must fail honestly.

When structured perception is unavailable:

```text
Hermes may state that runtime data is unavailable.
```

When image perception is unavailable:

```text
Hermes must not claim to see the artwork.
```

When both are unavailable:

```text
Hermes must answer from conversation memory only
and clearly identify that it cannot currently see the runtime.
```

If the active Hermes invocation has no genuine multimodal image path, stop after discovery and report the exact unsupported boundary. Do not simulate successful vision.

## 9. Acceptance Tests

### A. Baseline continuity

1. Resume the existing Hermes B session.
2. Ask a memory-dependent question.
3. Confirm prior conversational continuity remains intact.

### B. Initial perception

1. Run the Avatar scene.

2. Ask:

   > “What do you see?”

3. Hermes B must accurately describe the major visible artwork and runtime objects.

4. Claims derived from snapshot data must agree with the current runtime state.

5. Claims about appearance must be grounded in actual image ingestion.

### C. Changed-view test

1. Produce a materially different visible state without modifying project source solely to fake the test.

2. Ask again:

   > “What do you see now?”

3. The response must materially change to reflect the current viewport.

4. The system must not reuse the prior description as though it were current.

### D. Follow-up grounding

Ask a follow-up about a visible property, such as:

```text
“What color is the background?”
“Where is the dragon?”
“What objects are visible near it?”
```

The answer must remain grounded in the current perception inputs.

### E. Perception-denial test

1. Disable, remove, or deliberately withhold the perception inputs.

2. Ask:

   > “What do you see?”

3. Hermes B must admit that it cannot currently see the runtime.

4. It may recall what it saw earlier, but must label that as memory rather than current observation.

### F. Memory-plus-perception test

1. Restore perception.
2. Ask Hermes B to compare the current view with the earlier view.
3. It must combine current perception with remembered prior observation without confusing the two.

## 10. Required Evidence

Produce a durable evidence record containing:

```text
pre-work repository state
files inspected
files modified
actual request schema before and after
actual response schema before and after
Hermes B session identity used for every test
snapshot samples
viewport capture references and hashes
test prompts
raw responses
timestamps
provider/image-ingestion path
failure-path evidence
runtime logs
repository diff
final hashes
```

Evidence must demonstrate that the same Hermes B session was used throughout.

## 11. Protected Areas

Do not modify:

```text
/mnt/data-drive/godotollama
Ob-Scene contracts
Trixel
MettaExt
movement behavior
editor mutation systems
neutral Agent Portal code
```

Do not commit unrelated import noise or pre-existing changes.

## 12. Stop Conditions

Stop and report rather than broadening scope when:

```text
Hermes image ingestion is unsupported
the existing Hermes B session cannot be resumed safely
Snapshot Manager cannot provide usable current data
viewport capture requires an architectural replacement of the proven bridge
the implementation would require touching GodotOllama
the work would introduce runtime mutation
```

Any such finding becomes evidence for a follow-up ticket. It is not permission to redesign the system inside this ticket.

## 13. Closure Standard

This ticket closes only when all of the following are proven:

```text
same Hermes B session retained
structured runtime snapshot delivered
actual viewport image genuinely ingested
current view accurately described
changed view produces changed description
missing perception produces honest denial
conversation memory remains intact
no runtime mutation added
GodotOllama remains untouched
```

A response that merely sounds visually plausible is not acceptance.

## 14. Deferred Successor

After this ticket closes, create a separate ticket for:

```text
GodotOllama
    ↓
Session Agent Hermes editor host
    ↓
same Hermes B session identity
    ↓
runtime-to-editor memory proof
```

That work is explicitly outside `ENGAV-0002`.
