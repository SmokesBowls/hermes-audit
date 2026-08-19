# Item 3 Amendment — Durable Frame and Record Shape

Written 2026-08-19, following the storage-model decision: **framed
append-only journal, one file per `shared_session_id`, rejecting SQLite**
because `RESPONSE_COMMITTED` already carries response + cursor evidence
as one physical record — there is no independent-tables problem left for
a transactional database to solve. **Design only — no runtime code, no
implementation.**

One correction carried into this pass: the prior document's reference to
`hermes_session_adapter.py`'s `_atomic_write_no_replace` is evidence of
established low-level filesystem discipline in this codebase (descriptor-
based, no-clobber writes) — not proof that journal *appending* is
already solved. Atomic replacement and append-only journaling have
different failure mechanics; only the low-level technique is borrowed
here, not the conclusion.

## 1–3. Frame boundaries, separate from record encoding, with integrity information

Two layers, matching the user's own diagram, kept strictly separate so
the record encoding (JSON-ish today, potentially ZW-shaped later) can
change without touching the durability mechanism at all:

```
FILE HEADER
    magic + format version
    shared_session_id (the original, caller-supplied string — see §11)
    header checksum

FRAME
    magic/version
    record_length
    record_bytes        <- opaque to the framing layer entirely
    checksum

FRAME
    ...
```

**No newline-delimited JSON.** Confirmed understood and followed: a
frame is a self-describing, length-delimited, checksummed binary unit —
never "one JSON object per line," which conflates the durability
boundary with the record encoding exactly as flagged.

**Checksum scope**: covers the *entire* frame preceding it — magic +
length + record_bytes together, not just the record content. Reasoning:
a corrupted `record_length` field would otherwise go undetected by a
checksum scoped to record_bytes alone (the reader would read the wrong
number of bytes, but might not know it) — covering the whole frame means
a corrupted length is caught the same way a corrupted body is: the
checksum comparison fails.

**Per-frame magic, in addition to the file header's own magic.** The
header establishes "this file is an EngAIn continuity journal, version
N, for session S" once. Per-frame magic serves a different, narrower
purpose: cheap frame-boundary sanity-checking during sequential reads,
catching a class of corruption (garbage that isn't even trying to look
like a frame) before the more expensive checksum comparison runs.

Exact byte widths (magic length, endianness, checksum algorithm/size)
are left for the implementation pass, per instruction not to invent the
binary layout casually here — the *shape* above (self-describing,
length-delimited, whole-frame-checksummed, versioned) is what this pass
commits to.

## 4–5. Tail recovery: torn tail is safe, mid-journal corruption is not

Precise rule, replacing "discard the bad tail" with two genuinely
different cases:

- **Torn final frame** — reading the next frame's fixed prefix, or its
  declared `record_length` worth of bytes, or its checksum field, runs
  out of file *before* a complete frame is available. This is the
  *only* case treated as "safe, discard, use everything before it, no
  error." It's indistinguishable from — and is handled identically to —
  a crash landing mid-write (windows 5/6 of the crash-consistency
  design), which is exactly what it is.
- **Anything else** — a frame's magic doesn't match while there is
  *still enough trailing data* for what should have been a complete
  frame, or a frame reads its full declared length but its checksum
  doesn't match. Both mean the same thing: there is a hole or corruption
  *inside* otherwise-committed history, not an interrupted final write.
  **This must halt replay for the whole session, not skip the bad frame
  and continue.** Silently resuming after a mid-file gap risks
  reconstructing a Ledger/Cursor pair that looks complete and ordered
  but isn't — manufacturing continuity across a hole is exactly the
  failure named and explicitly ruled out.

On detecting mid-file corruption: **quarantine that one session's
journal only** — move/rename it out of the active path (e.g. a
`corrupt/` subdirectory or a `.corrupt` suffix, with the detected
position logged), and refuse to serve `/dispatch` for that
`shared_session_id` until a human resolves it, returning a distinct,
clearly-labeled error rather than silently starting that session with an
empty or partial reconstruction. This mirrors item 1/2's own established
isolation principle: one session's problem must never affect any other
session's availability — corruption in session A's journal has no
bearing on B's, C's, or the rest of the server.

**A semantic check beyond the physical checksum**: during replay, verify
`turn_id` values form the exact contiguous `0..N-1` sequence in file
order (item 2's own proven invariant). A gap or out-of-order value —
even across individually checksum-valid frames — is *also* treated as
corruption and quarantined the same way. This catches a class of problem
checksums alone can't (e.g. frames spliced from two different partial
files, each individually intact).

## 6. Durability point, including first-creation semantics

For an append to an **already-existing** journal file:

```
write complete frame bytes
        ↓
flush
        ↓
fsync(file descriptor)
        ↓
NOW durable
```

**For the *first* frame ever written to a brand-new journal** (a
`shared_session_id` with no prior journal file), content durability
alone is not sufficient — derived, not hand-waved: creating a new file
also creates a new **directory entry** (the filename → inode mapping),
and on POSIX filesystems that directory metadata is durable
*independently* of the file's own content durability. A crash
immediately after `fsync`ing the file's content, but before the
directory entry itself is durable, can — depending on filesystem and
mount options — leave the file's *existence* itself unrecoverable even
though its bytes were flushed to storage. The correct sequence for
first-creation:

```
create file (O_CREAT | O_EXCL, matching the no-clobber
             discipline already used elsewhere in this codebase)
        ↓
write file header + first frame
        ↓
flush + fsync(file descriptor)          <- content durable
        ↓
open the containing directory, fsync(directory descriptor)   <- the
        ↓                                                        new
NOW durable, including existence                              directory
                                                                entry is
                                                                durable
```

This directory-fsync is a **one-time cost per `shared_session_id`, at
that session's first-ever write** — not a per-append cost. Every
subsequent append to the same, already-existing file only needs the
file's own content `fsync`; the directory entry linking that filename to
that inode was already made durable at creation time and doesn't change
on ordinary appends.

## 7. Payload stays opaque and encoding-extensible

Prohibited explicitly, per instruction: `json.dumps(turn.payload)` (or
equivalent) as *the* persistence contract for payload/snapshot content.
Both are represented as a discriminated, opaque triple inside
`record_bytes`:

```
payload_encoding   (short tag: what encoding payload_bytes uses — e.g.
                     "utf8-text" today; room for others, including a
                     project-shaped ZW encoding, later — see §15)
payload_length
payload_bytes       (exactly payload_length bytes, never parsed or
                     interpreted by the framing layer, or even by the
                     record's own metadata-reading logic — only a
                     payload_encoding-aware consumer ever looks inside)
```

The same triple pattern applies to `snapshot` (also currently JSON-
shaped per the `engain.runtime_perception.v1` convention, also with no
reason to hard-wire that forever): `snapshot_present` flag, and if
present, `snapshot_encoding` / `snapshot_length` / `snapshot_bytes`.
Metadata fields that are small, simple, and stable in shape today
(`turn_id`, `origin_body`, `actor`, `provider_id`, `provider_session_id`,
`timestamp`) may use a constrained, simple text encoding directly — the
opacity requirement is specifically about payload/snapshot, the fields
whose *content model* the review is protecting, not every field in the
record.

## 8–10. Concrete field shape

### `TURN_APPENDED` (request)

```
turn_id             (integer)
origin_body         (short text)
payload_encoding / payload_length / payload_bytes   (opaque, §7)
snapshot_present, and if present:
    snapshot_encoding / snapshot_length / snapshot_bytes  (opaque, §7)
timestamp           (optional, non-authoritative — kept as audit
                     metadata; confirmed again, nothing in replay logic
                     reads it for correctness)
```

No `actor` field — confirmed no contradiction with the prior derivation:
still a stable, contract-level constant ("player") for every request,
reconstructed at replay time, not stored. No `direction` field — still
implicit in being a `TURN_APPENDED` frame. No `shared_session_id` field
per-record — the file header (§1, §11) already carries and verifies it
once per journal; repeating it on every frame would be redundant weight
with no new guarantee.

### `RESPONSE_COMMITTED` (response + cursor evidence, one record)

```
turn_id             (integer — also, implicitly, the cursor-through
                     value for (provider_id, provider_session_id); see
                     the prior pass's §2a derivation, re-confirmed here:
                     no contradiction found while defining the concrete
                     field shape)
origin_body         (short text)
actor               (short text — variable, required, unlike the request
                     case)
provider_id         (short text — required; the field genuinely new
                     relative to today's in-memory Turn dataclass)
provider_session_id (text — required, same reason)
payload_encoding / payload_length / payload_bytes   (opaque, §7)
snapshot_present, and if present:
    snapshot_encoding / snapshot_length / snapshot_bytes  (opaque, §7)
timestamp           (optional, non-authoritative)
```

No separate `cursor_through`/`CURSOR_ADVANCED` field or record —
re-confirmed: `turn_id` on this same record already is the cursor-
through value, by the same derivation as the prior pass. Defining the
concrete field shape did not surface any contradiction with keeping
`RESPONSE_COMMITTED` as one physical record; if anything it reinforces
it, since `provider_id`/`provider_session_id` sit naturally alongside
`turn_id` in the same record rather than needing a second one.

### Turn/event identity — re-confirmed, no new identifier added

`(shared_session_id, turn_id)` — the journal file's own verified identity
(§11) plus the record's own `turn_id` — already uniquely identifies a
durable turn within its canonical stream, exactly as the review restated.
Nothing in defining the concrete frame/record shape surfaced a need for
a separate record ID: frame-level integrity is the checksum's job (§1–3,
"are these bytes intact"), not an identity concern; `turn_id`'s job is
ordering/identity ("which logical position is this"). Those are
non-overlapping concerns, and neither one implies a need for a third
identifier. The journal is replayed, never re-applied as new turns —
same reasoning as before, unchanged by concretizing the shape.

## 11. Safe filename mapping — `shared_session_id` never touches a path directly

```
shared_session_id (arbitrary, caller-supplied, untrusted for
                    filesystem purposes — could contain "../", null
                    bytes, OS-reserved names, unbounded length)
        ↓ deterministic hash (e.g. SHA-256 over the UTF-8 bytes,
        ↓ hex-encoded, fixed-length output)
<journal_root>/<hex_digest>.journal
```

Fixed-length, fixed-character-set (`[0-9a-f]`) output — never
path-traversal-capable, never OS-reserved, deterministic (the same
`shared_session_id` always resolves to the same file, required for a
later `/dispatch` to find its own session's prior history).

**The original `shared_session_id` is retained inside the file header**
(§1) specifically so recovery can verify agreement: on open, compute the
expected hash for the `shared_session_id` being requested, read the
header from the file found at that path, and require
`header.shared_session_id == requested shared_session_id`. A mismatch is
treated as corruption (§4–5's quarantine path) — with a well-distributed
hash at this scale, a mismatch here is far more likely to indicate a bug
or filesystem-level problem than a genuine collision, but the check
catches either case identically and safely, which is the point: it
doesn't need to distinguish "coincidence" from "bug," only "trustworthy"
from "not."

## 12. One ordering authority — reusing item 2's lock, not adding a second one

Item 2 already gave `SessionLedger` a per-`session_id` `threading.Lock`
(`_lock_for`). This design does **not** introduce an independent
persistence-specific lock — the durable write is folded into the *same*
critical section that already exists, for both paths:

```
request:
  acquire SessionLedger's existing per-session_id lock
      turn_id = len(turns)                     (unchanged from item 2)
      construct the TURN_APPENDED record (fully, in memory, first —
          so any construction failure happens BEFORE durability, not
          after — see §13)
      write frame, flush, fsync              <- durable
      turns.append(turn)                      <- then, and only then,
                                                   in-memory
  release

response (after Gate 11 validation, unchanged):
  acquire SessionLedger's existing per-session_id lock
      turn_id = len(turns)
      construct the RESPONSE_COMMITTED record (fully, in memory, first)
      write frame, flush, fsync              <- durable
      turns.append(turn)                      <- then in-memory
      cursor.advance(provider_id, provider_session_id, turn.turn_id)
                                                <- then in-memory
  release
```

**`ContinuityCursorTracker` still doesn't need its own lock.** Checked,
not assumed: `cursor.advance()` is only ever reached as part of a
successful `handle_turn()` completion for one `(provider_id,
provider_session_id)` pair, and item 1's own claim mechanism already
guarantees no two concurrent dispatches can be in flight for that same
pair — so no two writers can race `cursor.advance()`'s dict mutation for
the same key today, independent of this journal design. Nothing here
changes that guarantee or needs to duplicate it.

**Real, named cost**: the per-session lock's hold time now includes one
synchronous `fsync` (bounded, single-digit-milliseconds class on typical
storage) where item 2's own version was purely in-memory
(sub-microsecond). This is categorically different from — and vastly
shorter than — a provider dispatch (seconds, up to item 1's own 90–120s
timeouts), so the "never hold across a provider call" invariant is
unaffected. It's a real, measurable change worth benchmarking at
implementation time, not something to leave unstated.

## 13. Disk-ahead-of-RAM divergence while the process stays alive

The process-crash case is, as the review notes, actually the easy one —
the journal is canonical, a restart's replay reconstructs correctly.
The harder case: the process **survives**, the frame is durably
`fsync`ed, and *then* the in-memory mutation that's supposed to follow
raises before completing — a `MemoryError`, an asynchronously-delivered
signal landing at an unlucky instruction, or any other rare-but-real
failure in ordinary Python execution.

Two complementary mitigations, not one instead of the other:

- **Shrink the window structurally.** Fully construct the `Turn` object
  (and, for the response path, everything `cursor.advance()` needs)
  *before* the durable write, not after — so the only work remaining
  once the frame is durable is a bare `list.append()` of an
  already-built object (for the Ledger) and a bare dict-assignment (for
  the cursor) — about as close to "cannot meaningfully fail" as ordinary
  Python gets, without claiming it's literally impossible.
- **Treat the residual risk as fatal to that one session, not to the
  whole process.** If the post-durability in-memory step ever does
  raise, the correct response is **not** to let that session continue
  serving requests against a Ledger/Cursor that both authority and
  reality now disagree about. The narrower of the review's two offered
  options is the right one here, not the process-wide one: crashing the
  entire server over one session's freak failure would violate the same
  isolation principle §4–5 and §12 both already rely on (one session's
  problem must not affect any other session). Instead: mark that one
  `shared_session_id`'s in-memory state as poisoned (a small, new,
  explicit mechanism — not something that exists today) and refuse
  further requests for it with a distinct error until the process
  restarts or that session's state is explicitly reloaded from its
  (still-correct) journal. This is honestly bounded, not a permanent
  loss: the durable journal is untouched and correct, so recovery is a
  restart away, exactly as the review itself observed.

## 14. Startup replay, concretely

Lazy, per-session, on first touch after a fresh process start — matches
how `PresenceRegistry`/`SessionLedger`/`ContinuityCursorTracker` are
already populated today (nothing pre-loads all sessions eagerly; entries
appear on first real use). Eagerly scanning and replaying every journal
at process start is a legitimate alternative with different tradeoffs
(predictable, front-loaded startup cost vs. lazy, per-session cost and
lazy error surfacing) — left as an open implementation-time question,
not resolved here, since both are equally *correct*, only different in
when cost/failure is paid.

Procedure, once a `shared_session_id` is first touched:

1. Resolve its journal path (§11).
2. No file present → fresh session, in-memory state starts empty —
   identical to today's behavior for a session with no history.
3. File present → read and verify the header (magic, version, checksum,
   declared `shared_session_id` matches the one being opened) — any
   failure here is corruption, not a torn tail (it's the *first* thing
   in the file) — quarantine (§4–5), refuse to serve this session.
4. Read frames sequentially per the strict rule in §4–5: a clean
   insufficient-bytes tail stops safely, using everything read so far;
   anything else — bad magic with data still present, a checksum
   mismatch on a full-length frame, or a `turn_id` sequence gap/
   out-of-order value — halts and quarantines the whole session's
   journal, never partially applies past the problem.
5. For each valid frame, reconstruct the corresponding in-memory `Turn`
   (request: `direction="request"`, `actor="player"` — reconstructed
   constants, not read from the record; response: fields taken directly
   from the record) and append it to the in-progress reconstruction, in
   file order.
6. For each valid `RESPONSE_COMMITTED`, additionally derive
   `cursor[(provider_id, provider_session_id)] = max(existing, turn_id)`
   (§2a of the prior pass).
7. Install the fully reconstructed Ledger list and cursor entries as
   this session's live state; resume normal operation, appending further
   turns to the same durable file.

## 15. ZW conventions, checked again at this concrete layer — same negative result

Re-confirmed a fourth time (item 2's own check, the prior encoding
pass's check, and now this frame/record-shape pass), specifically
against the concretized field list above: nothing in the established ZW
material defines a shape for `turn_id`/`origin_body`/`actor`/
`provider_id`/`provider_session_id`/payload-as-content — there is still
no established, project-specific convention to show. The
`payload_encoding`/`snapshot_encoding` discriminators in §7 are exactly
what keeps this open honestly: if a genuinely project-shaped ZW
convention for this content is ever established, it becomes a new
`payload_encoding` value, requiring no change to the frame format, the
header, or any of the metadata fields above. Nothing here invents ZW
syntax to claim compliance with something the project hasn't actually
defined for this role.

## Status

- Storage model: **framed append-only file, one per `shared_session_id`
  — decided**, not merely leaned toward.
- Frame shape: self-describing, length-delimited, whole-frame-checksummed,
  versioned, with a separate one-time file header carrying the verified
  `shared_session_id` — derived, exact byte widths deferred to
  implementation.
- Record shape: two event types, fields fully enumerated for both,
  payload/snapshot kept opaque and encoding-extensible — derived, no
  contradiction found with the prior pass's simplification.
- Turn identity: `(shared_session_id, turn_id)` — re-confirmed
  sufficient, no new identifier added.
- Filename mapping: deterministic hash, verified against a header-
  carried original ID — derived, not deferred.
- Ordering: reuses item 2's existing per-session lock; no independent
  persistence-specific lock introduced; `ContinuityCursorTracker`'s lack
  of its own lock re-confirmed still safe, via item 1's claim mechanism.
- Disk/RAM divergence while alive: named explicitly, two complementary
  mitigations (shrink the window structurally; poison-and-refuse the one
  affected session as the fallback, not a process-wide crash).
- Replay procedure: fully specified, including the semantic
  `turn_id`-contiguity check beyond raw checksum validity.
- ZW: checked again, same honest negative result, door deliberately left
  open via the encoding discriminators rather than closed or faked.

Not yet implemented. Next pass, per the review's own closing framing,
is implementation — still wanting its own review before any code is
written, same sequence as every prior item in this session.
