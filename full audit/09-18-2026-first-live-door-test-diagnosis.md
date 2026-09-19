# First live Dragon-door test — diagnosis only, nothing changed

Scope discipline honored throughout: **no code, config, or runtime
behavior was modified.** This traces the exact request through existing
receipts/logs/databases only. Sources consulted, all read-only:

- `/mnt/data-drive/godot_engain_3d_avatar/scripts/EngAInBridge3D.gd`
  (the bridge/mailbox client, live source)
- `/mnt/data-drive/godot_engain_3d_avatar/hermes_session_adapter.py`
  (the CLI adapter the bridge subprocess-invokes)
- `/mnt/data-drive/engain-runtime-mailboxes/dragon3d/` (the filesystem
  mailbox: `request.json`/`response.json` are absent right now —
  confirmed ephemeral, not a discovery of tampering; see §5)
- `/home/mytruelove/.hermes/state.db` (`sessions`/`messages` tables) —
  the actual Hermes agent-loop conversation log for session
  `20260731_065008_63a62d` (= `FROZEN_SESSION_ID`), the durable record
  this diagnosis is built from
- `/home/mytruelove/.local/share/godot/app_userdata/engain_parser/logs/godot2026-09-18T16.35.35.log`
  (Godot's own stdout capture — see §5, contributes almost nothing)

## Answers to the eight questions

**1. Did Dragon receive the request? YES, directly confirmed.**
`state.db`, message id `49988`, session `20260731_065008_63a62d`,
`role=user`, timestamp `1789774665.4419303` = **2026-09-18 16:37:45.441
PDT**. Content is character-for-character the request quoted in the
task (verified below in §4, verbatim).

**2. Did Dragon decide to call an authority? YES, directly confirmed.**
The very next message (`49989`, 16:37:55.344) is an assistant tool call
to its own `todo` tracker creating a 3-item plan: locate the chapter and
door interfaces, invoke the doors read-only, then separate scene
evidence from prior identity/continuity in the answer. It then spent
roughly two minutes (49991–50027) reading `engain_door.py`,
`engain_door_client.py`, the `09-16-2026-mrlore-door-design-v1.md`
design doc from this repo, and `MRLORE_LONG_TERM_CONTINUATION_MEMO.md`
before calling anything.

**3. Did it attempt Mettaext? YES, directly confirmed, and it
succeeded.** Message `50028` (16:39:45.022) issued two real subprocess
calls:

```bash
ENGAIN_ROOT=/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn \
  python engain_door.py query \
  --source /home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/mrlore/raw/chapters/book_08_the_vigil_of_the_anchor_047_mika.md \
  --query Geralt

ENGAIN_ROOT=/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn \
  python engain_door.py query \
  --source /home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/mrlore/raw/chapters/book_08_the_vigil_of_the_anchor_047_mika.md \
  --query Mika
```

Both returned real, contract-shaped `{"ok": true, "operation": "query",
"authority": "evidence_only", ...}` payloads (26 hits for "Geralt", 29
for "Mika" — full text in §4). Worth flagging as a real, separate
observation, not part of this failure: the queried source resolves to
`chapter_id: "chapter.045_the_homecoming"` — the file's own internal
title (confirmed: line 1 of that file literally reads `CHAPTER 45: THE
HOMECOMING`) disagrees with its filename-based chapter number
(`047_mika`). Not investigated further here; noted for whoever owns
chapter/scene ID derivation.

**4. Did it attempt MrLore? YES, directly confirmed, in two forms.**
First it discovered (message `50034`) that `tools/mrlore_query.py`
exists and is runnable, then ran two real queries against it
(`50037`–`50039`, both `exit_code: 0`, real output — the exact
incarnation chain and entity record already found independently in this
session's own `entities.yaml` audit). **In the same batch it also
explicitly attempted a formal door mirroring `engain_door.py`'s shape**:

```bash
python /mnt/data-drive/godot_engain_3d_avatar/mrlore_door.py query --name Geralt
```

Result (`50040`, 16:40:27.810): `exit_code: 2`, `"python: can't open
file '/mnt/data-drive/godot_engain_3d_avatar/mrlore_door.py': [Errno 2]
No such file or directory"`. This is not a bug in what Dragon did — it
correctly tried the door, got a real OS-level failure, and did not hide
or paper over it. It confirms directly, from a live run rather than
just this repo's design doc, that **`mrlore_door.py` does not exist**.

**5. What exact door invocation, if any, was issued? Answered fully in
§3–4 for the two real invocations (Mettaext ×2, attempted MrLore door
×1) plus two `mrlore_query.py` CLI calls.** One honest gap: the
mailbox-level envelope GDScript builds to hand the message *to* Hermes
in the first place (`request_id`/`call_id`/`client_request_id`,
constructed in `_build_mailbox_request`) is not visible anywhere in
Hermes's own conversation log — by design, the model only ever sees the
natural-language text (message `49988`), not the mailbox JSON wrapper
around it. `request.json`/`response.json` in
`/mnt/data-drive/engain-runtime-mailboxes/dragon3d/` are both absent
right now. Given the mailbox protocol's own code (`hermes_session_
adapter.py`) actively `unlink()`s stale/consumed files rather than
archiving them, this is expected, not evidence of tampering — but it
does mean the literal `request_id`/`call_id` GUIDs and the literal
bytes of whatever `response.json` briefly existed **cannot be
recovered**. This report cannot preserve envelopes that were never
durably written in the first place; §7 recommends fixing that
separately from this diagnosis.

**6. What exact response came back?**
From the two doors that were actually reachable: real, contract-valid
JSON (§4). From the mailbox itself (the thing Dragon's bridge was
waiting on): **nothing durable survives to inspect** (see §5). What can
be said with high confidence from the timing evidence (§7) is that
*something* arrived at `response.json` that JSON-parsed successfully
(ruling out "Claimed response is malformed", `EngAInBridge3D.gd:530`)
and was not treated as a stale leftover (ruling out `:533`) — it reached
and failed the detailed `_validate_correlated_response()` check, which
is the only path to the exact line 536 message reported.

**7. Which validation condition classified the response as malformed,
mismatched, or stale?** `_validate_correlated_response()`
(`EngAInBridge3D.gd:562`) has roughly a dozen independent conditions
that all funnel into the same generic rejection message — it does not
log *which* one failed. Candidates, in the order the function checks
them: exact-key-set match against `RESPONSE_SCHEMA`, `call_id`/
`request_id`/`client_request_id` correlation, `narrative_response`
being a non-empty string, `action_type == "OBSERVATION"` exactly,
`state_changes` being an empty dict, `entropy_impact` being exactly
`0.0`, `timestamp` finite, `provider_session_ref` matching all four
fixed values, and `perception_result` passing its own nested schema.
**Given the strong timing evidence in the next answer — the underlying
agent process appears to have been cut off before producing a real
final answer — the most likely single explanation is that whatever
constructed the fallback `response.json` did not have a genuine
`narrative_response` to put in it,** but this is inference, not
something logged explicitly anywhere found. This is the one place this
diagnosis is not fully closed; §7 below is the load-bearing evidence for
why that inference is strong.

**8. Was the 180s timeout caused by the rejected response being the
only response, or was another component hanging?**
**Strong evidence for a specific, narrower answer than either option as
posed: the underlying Hermes agent process itself appears to have been
terminated by a ~180-second limit, one step before it could produce its
actual answer** — not a Dragon-side component idly hanging with nothing
happening. The full message timeline for this request:

```text
16:37:45.441  user request received (id 49988)
16:37:55.344  todo created: locate / invoke / answer (all "pending"/"in_progress")
16:37:55–16:39:45  extensive read-only exploration (49991-50027):
                    engain_door.py, engain_door_client.py, this repo's
                    09-16-2026-mrlore-door-design-v1.md,
                    MRLORE_LONG_TERM_CONTINUATION_MEMO.md, tier1/mrlore tree
16:39:45.022  engain_door.py query --query Geralt   -> real success
16:39:46.805  engain_door.py query --query Mika     -> real success
16:39:56–16:40:11  discovers and reads tools/mrlore_query.py
16:40:23.265  three parallel terminal calls issued (incarnation chain,
              entity summary, attempted mrlore_door.py)
16:40:24.511  mrlore_query.py --incarnation Geralt  -> real success
16:40:26.732  mrlore_query.py Geralt                -> real success
16:40:27.810  mrlore_door.py query --name Geralt    -> real ENOENT failure
16:40:45.283  assistant issues final tool call: todo update marking
              ALL THREE items ("locate", "invoke", "answer") "completed"
16:40:45.288  tool result recorded (finish_reason on the preceding
              assistant turn: "tool_calls" — a completely normal,
              non-error stopping reason)

              <<< nothing after this point exists anywhere in the
                  entire messages table, any session, any id >29999999>
```

**16:40:45.288 minus 16:37:45.441 = 179.847 seconds** — within 153
milliseconds of exactly 180.000 seconds after the request was received.
`EngAInBridge3D.gd` hardcodes `180.0` as its own mailbox-timeout
constant (lines 234/240) — the same number. The `todo` update marking
"answer" as `"completed"` is itself strong secondary evidence Dragon
believed it had (or was about to) produce the actual narrative answer
next — that is the normal next step after a tool result in this kind of
agent loop, and `finish_reason: "tool_calls"` on that last assistant
turn confirms the API call itself completed cleanly, with no error,
truncation, or refusal — it simply never got a next turn.

**Conclusion for Q8: not a Dragon-side component idling with nothing to
show — a real investigation ran, called both doors successfully (plus
correctly surfacing the missing MrLore door as a hard failure), and was
almost certainly cut off by a ~180-second process/subprocess limit one
turn short of producing its final answer.** Whatever received that
cutoff (most plausibly `hermes_session_adapter.py`, which owns the
subprocess call into `hermes`) then appears to have written *some*
fallback into `response.json` rather than leaving the mailbox empty —
that fallback is what failed `_validate_correlated_response()` and
produced the first `[ERR]` line; the bridge's own independent 180s
watchdog then separately expired shortly after with no valid response
ever having arrived, producing the second `[ERR]` line. The exact code
path that constructs that fallback was not located in this pass (would
require reading more of `hermes_session_adapter.py`'s subprocess/
timeout handling, which this diagnosis did not do, in keeping with
"diagnosis only, do not modify or chase further right now").

## Timing coincidence, stated plainly

Two independently-configured `180.0` values (the GDScript's mailbox
watchdog, and whatever cut the agent loop off at T+179.847s) landing
within 153ms of each other is either the same underlying timeout
constant used in two places by design, or a real coincidence worth
treating with suspicion either way. Not resolved here — flagged as the
single highest-value next read if this is pursued further.

## What was not attempted

Per instruction: nothing was rerun, no code was read with intent to
fix, and no fallback-response-construction code path was traced to
completion. This stops at diagnosis.
