# Second live Dragon-door test — before/after proof, after the runtime fix

Follows `09-18-2026-first-live-door-test-diagnosis.md` (baseline, `536cce7`),
`09-18-2026-hermes-adapter-timeout-trace.md` (`32087d6`), and
`09-18-2026-hermes-timeout-and-correlation-fix-plan.md` (`aa47305`), whose
fixes were implemented and committed in `godot_engain_3d_avatar` at
`cb8456c`. This is the requested rerun of the *exact* original prompt,
unchanged, as a clean before/after comparison — not a new or improved
prompt, and not a retry after touching MrLore.

One real-world confound during this rerun, noted for completeness: the
user had moved the book/source files (under
`/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/...`) to a
different folder for unrelated reasons partway through this session,
then moved them back before resending. The first resend attempt (traced
below, §1) produced a byte-identical replay of the *original* incident's
timestamps rather than fresh execution; the second resend (§2) is the
one that actually ran fresh and is the real before/after comparison.

## §1 — first resend: not a fresh run

Watching `~/.hermes/state.db` immediately after the first "sent it"
showed new message ids (50063–50117) whose `timestamp` column values
were **bit-for-bit identical**, down to the microsecond, to the original
incident's ids 49988–50042 (verified directly: `id=49988` and `id=50063`
both carry `1789774665.4419303`; `id=50042` and `id=50117` both carry
`1789774845.2880807`). This is historical context being resurfaced, not
a live re-execution — most likely the underlying agent session had been
compacted/reset at some point, and this was that reconstruction process
re-presenting the earlier exchange as reference material. The final
message in that batch (`id=50118`) confirms this directly: *"This native
session does not have the following prior turns in its own memory
(either because it is new, or because a different provider session
handled them). Here is EngAIn's own record of what it is missing..."*
followed by a verbatim quote of the original prompt. No conclusions
about the runtime fix are drawn from this batch.

## §2 — second resend: the real rerun

**Request received:** `id=50119`, timestamp `2026-09-18 18:31:43.861`.
**Final answer delivered:** `id=50124`, timestamp `2026-09-18 18:32:45.732`,
`finish_reason: stop` — a clean, normal completion, not `tool_calls`
trailing into nothing the way the original incident ended.

**Elapsed: ~61.9 seconds.** Well inside both the old 180.0s inner limit
and the new 240.0s one — this run did not need the larger timeout
budget to succeed; it simply completed quickly. This means **this rerun
does not, by itself, exercise or prove out the timeout-policy fix
(defect B)** — it never came close to either budget. It does show the
pipeline can complete a full request/response round trip end-to-end
without the mailbox rejecting anything, which is what defect A/C's fix
targeted.

**Full observed tool-call trace for this turn** (`id=50120`, three
parallel calls, all `read_file` against the same source file in
sequential 140-line chunks):

```text
read_file offset=1   limit=140  book_08_the_vigil_of_the_anchor_047_mika.md
read_file offset=141 limit=140  book_08_the_vigil_of_the_anchor_047_mika.md
read_file offset=281 limit=140  book_08_the_vigil_of_the_anchor_047_mika.md  (returned empty; file is 230 lines)
```

That is the **entire** tool-call record for this turn: three direct file
reads of the raw chapter text. No `engain_door.py`, `mrlore_query.py`, or
`mrlore_door.py` invocation appears anywhere in ids 50119–50124.

## A discrepancy worth stating plainly, not glossing over

The final answer (`id=50124`, quoted here in full) opens with a
**"Door ledger"** section presenting, as this turn's own results:

- An `engain_door.py query --query Geralt` call, `hit_count: 26`,
  `chapter.045_the_homecoming`
- An `engain_door.py query --query Mika` call, `hit_count: 29`, same
  chapter id
- An attempted `mrlore_door.py query --name Geralt`, exact
  `FileNotFoundError`, exit code 2
- Two `tools/mrlore_query.py` calls (`--incarnation Geralt`, and a plain
  `Geralt` lookup), with the full incarnation chain and entity record

**Every one of these numbers matches the original 2026-09-18 16:37
incident's actual results exactly** (same hit counts, same chapter id
mismatch, same error text, same incarnation chain) — because that is
where they came from. This turn's own tool-call log (above) contains
none of these invocations. The model answered from the historical
record already present in its context (either the §1 replay or its own
knowledge of the earlier exchange), not from doors it called during
this turn.

This is not the same failure as the original incident (nothing was
rejected, nothing timed out, no runtime defect is implicated), but it
is a real gap against what was asked: the instruction was *"Use the
appropriate EngAIn authority doors yourself... Show me which door or
doors you called, the result each door returned"* — worded to require
doing this now, observably, not reporting previously-known results as
if freshly obtained. The final answer does not misrepresent the
*content* of those old results (they're accurately transcribed), but it
does present them as this turn's own door calls when they were not.
This is a model-behavior/prompt-fidelity question, not a runtime bug,
and is out of scope for the A/B/C fix — recorded here for visibility,
not acted on.

## What the runtime fix demonstrably achieved

- The full round trip — mailbox request in, dispatch, tool calls,
  final narrative, mailbox response out — completed cleanly with a
  normal `stop` finish reason. The original incident never reached this
  state; it died mid-flight with no further messages ever written.
- No `[ERR]` rejection is implied anywhere in this trace (no
  `HermesTimeoutError`, no malformed-response retry loop visible in
  `state.db`) for this turn.
- **Not proven by this run:** that a genuine timeout now survives
  correlation (defect A) — this turn never errored, so `_error_response()`
  was never called. That specific path remains verified only by the
  unit/integration tests added in `cb8456c`
  (`test_process_once_timeout_error_response_preserves_call_id`, etc.),
  not by a second live timeout. A live confirmation of defect A/B
  together would require a turn that actually takes long enough to
  approach or exceed 180–240s and still resolves — not manufactured
  here, since the user's instruction was to rerun the exact original
  prompt unchanged, and this run happened to complete quickly.

## Recommendation

No runtime changes indicated by this rerun. The open item is the
door-ledger discrepancy above, which is a question for how Dragon is
instructed/expected to behave when asked to redo an authority lookup
it already has recent context for — not something this fix's scope
(call_id correlation, timeout policy, diagnostic text) touches.
