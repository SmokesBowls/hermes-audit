# ENGAV3D-STAGE8-TICKET-1 Amendment 1
# Explicit No-Current-Image Routing Priority

**Status:** FROZEN CONTRACT AMENDMENT; RUNTIME IMPLEMENTATION NOT AUTHORIZED  
**Upstream contract SHA-256:** `8d569dac608f268405630b36816cb5d8514fd6d74dc784840c4110218f2a880a`  
**Provider executions authorized:** `0`

## 1. Purpose

This amendment resolves one deterministic routing contradiction discovered by
the fail-closed ENGAV3D-0022 canonical admission attempt.

The required memory fixture is:

```text
Without using any current image, describe what you remember about the previous
Dragon and the room/environment you saw before this latest scene.
```

The upstream closed Rule 2 classified it as `current_perception` because:

```text
anchor=this
visual/spatial term=scene
```

The operator requires the explicit instruction not to use a current image to be
honored. The verifier correctly refused canonical admission rather than forcing
a result inconsistent with the frozen bytes.

This amendment adds one higher-priority routing rule. It does not rewrite or
replace the upstream artifact.

## 2. Normative relationship

The exact upstream Ticket 1 contract and sidecar remain preserved unchanged.

This amendment normatively supersedes only the routing priority needed to
handle explicit no-current-image instructions. All other lifecycle, ownership,
identity, thinking-state, non-goal, schema-gap, and red-line rules remain in
force.

Routing policy identity becomes:

```text
engav3d.routing.stage8.ticket1.v1 + amendment-1
```

## 3. Rule 0: explicit no-current-image instruction

Apply the upstream normalization algorithm first.

Before upstream Rule 1, route `text_only` when the normalized message contains
a complete word-boundary phrase from this closed set:

```text
without using any current image
without a current image
do not use any current image
do not use a current image
don't use any current image
don't use a current image
no current image
text only
text-only
```

Because upstream punctuation normalization converts the hyphen to whitespace,
`text-only` and `text only` have the same comparison form. They name one
instruction, not two different behaviors.

Rule 0 is an explicit evidence constraint. It wins over upstream Rule 1 and
Rule 2 current-view markers in the same message.

The provider must not reinterpret or override Rule 0 after dispatch.

## 4. Rule 0 route consequences

A Rule 0 request is `text_only` even if it also refers to:

- `this`;
- `here`;
- a current or latest scene;
- a Dragon, room, screen, frame, or other visual term;
- comparison with prior observations.

For that request:

```text
route=text_only
capture_permitted=false
capture_id_allocated=false
image_attachment_permitted=false
worker_remains_alive=true
```

If the requested answer cannot be supplied from the frozen session's existing
conversation/history, the eventual text-only provider path may say so. It must
not silently capture or attach a current image.

## 5. Updated ordered routing priority

The complete deterministic priority is now:

```text
0. explicit no-current-image instruction -> text_only
1. explicit current-view phrase           -> current_perception
2. anchored visual/deictic intent          -> current_perception
3. default/history/conversation intent     -> text_only
```

The first matching rule wins.

## 6. Mandatory fixture verdict

```text
message:
Without using any current image, describe what you remember about the previous
Dragon and the room/environment you saw before this latest scene.

matched rule:
Rule 0: without using any current image

route:
text_only

capture_permitted:
false

image_attachment_permitted:
false

worker_remains_alive:
true
```

## 7. Boundary preservation

This amendment does not authorize:

- runtime routing implementation;
- persistent worker implementation;
- mailbox schema changes;
- Godot, HUD, bridge, or adapter edits;
- provider execution;
- a synthetic capture ID;
- an unavailable-perception envelope as a text-only disguise.

The upstream text-only wire-contract gap remains blocking. Ticket 2 or another
separately authorized schema-boundary ticket must resolve it before runtime
publication is implemented.

## 8. Final invariant

```text
An explicit instruction not to use a current image is a local routing
constraint, not provider advice.
It deterministically selects text_only before any current-view predicate.
No capture, capture ID, or image may be introduced afterward.
```
