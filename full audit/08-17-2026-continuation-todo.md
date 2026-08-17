# Continuation TODO — Avatar Continuity Integration, Next Phase

Written 2026-08-17, immediately after the avatar continuity integration
proof (`08-17-2026-avatar-continuity-integration-proof.md`) and its four
commits (EngAIn `1073a63`, `engain_avatar` `1b2c111`,
`godot_engain_3d_avatar` `57122cd`, this repo `f57eae9` — none pushed).
This is the todo list and resumption pointer for whoever (human or a
future session of me) picks this up next.

## State as of this writing

- All four repos: clean working trees, committed, **not pushed**. Push
  only on explicit instruction — established pattern all session.
- Offline suites green: EngAIn 215/215, `engain_avatar` 86/86,
  `godot_engain_3d_avatar` 260/263 (3 pre-existing, unrelated `RED`
  failures in `test_stage8_ticket3b_worker_ownership_red.py` — confirmed
  not caused by this work, same failures the last full audit recorded).
- `ENGAIN_CONTINUITY_DISPATCH` is opt-in and unset by default in both
  avatar repos — today's actual game runtime, if launched normally right
  now, uses none of this new path. It exists, is proven live, and is
  inert until someone deliberately turns it on.
- No stray processes: the one orphaned `dragon2d` worker found during
  this pass was stopped cleanly (see that day's receipt).

## Open items, in the order they'd naturally get picked up

1. **Concurrent-`/dispatch` mutex for overridden bindings.** Today's
   `/dispatch` handler has no lock of its own; protection against two
   concurrent callers racing the same native provider session only
   exists for the *default* frozen-Hermes binding, via the pre-existing
   worker-level claim (keyed on `self.client.session_id`, unrelated to
   `/dispatch`'s own routing). A caller submitting an explicit override
   (as the Claude Code leg of the proof does) has no equivalent guard.
   Options worth weighing before building: (a) have `/dispatch` itself
   acquire/release a claim internally, keyed on
   `(provider_id, provider_session_id)` rather than the old
   `session_id`-only key, reusing `SessionClaimRegistry` as-is; (b) some
   other scheme. Not yet decided — flag for review before implementing,
   this changes a contract other things depend on.

2. **Ledger/cursor persistence or reconstruction across a restart.**
   Explicitly deferred, explicitly named as a real (safe-direction) loss
   in both this phase's receipts. "For the first composed runtime, the
   same central EngAIn process can own it [in-memory]" was the original
   scope-setting instruction; before restart *durability* can be claimed,
   this needs either real persistence (append-only Ledger writes, cursor
   snapshot) or a documented reconstruction-from-receipts scheme. Given
   this pass's own discovery — a recap, once dispatched, becomes
   permanent native-side state regardless of what EngAIn does — worth
   re-deriving from first principles what's actually still missing after
   that fact is accounted for, rather than assuming the original framing
   still applies unmodified.

3. **Production cutover decision, not yet made.** `ENGAIN_CONTINUITY_DISPATCH`
   is opt-in specifically so this phase couldn't regress the existing,
   working, more-thoroughly-validated direct-Hermes path (image/viewport
   perception handling, the single-use provider-receipt binding
   `_sanitize_response()` still does for that path, etc. — none of that
   machinery is exercised by the new path at all). Turning this on by
   default, or retiring the old path, is a real, separate decision with
   real feature-coverage tradeoffs (named explicitly in the integration
   receipt) — not something to do by accident or as a quiet follow-on.

4. **Real Godot launch through this same integration**, if wanted —
   this proof deliberately ran both avatar workers as standalone,
   file-mailbox-driven subprocesses, not through `runtime_composition.py`
   /`SupervisedPresenceAuthority`'s full launcher (which does start real
   Godot for the 3D side). Composing this new `/dispatch` path with that
   existing supervised-launch machinery hasn't been attempted.

5. **`provider_session_ref`'s frozen-identity limitation** — named, not
   fixed. If anything downstream ever starts reading `provider`/`model`/
   `session_id` from that field as ground truth (nothing does today),
   it would need a real fix, not just `director_analysis`'s honest
   side-channel.

## Where to look first when resuming

- `tier1/engainos/server/presence_authority_server.py` — `/dispatch`
  handler, `_PROVIDER_DISPATCHERS`, module-level `ledger`/`cursor`.
- `engain_continuity_client.py` (identical in both avatar repos) — the
  vendored client; `hermes_session_adapter.py`'s
  `_engain_continuity_binding_fields` / `_dispatch_via_engain_continuity`
  / `_engain_continuity_response` are the three new methods per repo.
- `tier1/engainos/tools/live_avatar_continuity_integration_proof.py` —
  the live proof; rerunnable as-is (mints fresh Claude/Hermes sessions
  each run, no manual state needed beyond the two repos' existing frozen
  Hermes session and a real `hermes`/`claude` CLI on PATH).
- This audit repo's `full audit/08-17-2026-*.md` files, chronologically,
  for the full design reasoning behind every choice above.
