# First real scene-evidence result, and the spawnable-is-scene-scoped design principle

Write-up of the design discussion and the live result that followed it,
using the now-working continuation loop (`f1d873e`, `f11c900`, proven
live in the ninth-test receipt, `2872683`). Grounded directly in Hermes
`state.db`, session `20260731_065008_63a62d`, ids `50396`–`50573`.

## The design principle established

**`spawnable` is not a permanent property of an identity — it's scoped
to what a specific scene's evidence actually supports.** The
triggering case: Mettaext marking the Aeon Keepers `known: true,
spawnable: false`. The user's own framing, preserved verbatim because
it's the clearest statement of the rule:

> "entity exists in the story ≠ entity must physically instantiate in
> the game scene"

An ethereal being referenced only by name or spoken of in a scene can
correctly be `spawnable: false` there without that being wrong or a
defect — and the same identity can legitimately become `spawnable:
true` in a later chapter once the text actually describes a physical
manifestation. The same identity, different manifestation state per
scene. Collapsing this into one permanent flag on the identity record
would let an early `spawnable: false` "poison" it forever, blocking
Dragon from ever instantiating that entity even after the book
eventually justifies it.

This maps onto the three-layer model already established earlier in
this audit line (persistent identity vs. textual evidence vs. derived
inference — see `mrlore-audit`'s incarnation-chain pressure test) with
one further layer added on top, specific to game-building:

```text
MrLore:    Aeon Keepers = persistent identity / lore entity
Mettaext:  in THIS scene, how are they actually present?
Dragon:    given this scene-local evidence, should anything be
           instantiated in the game right now?
```

## The workflow this implies for automatic game construction

```text
Book evidence
  -> Mettaext: referenced here, no physical manifestation established
  -> Dragon auto-build: don't spawn them in this scene   (conservative default)
  -> [later, during first playthrough]
  -> "Dragon, I actually want the Aeon Keepers spawned in this scene."
  -> treated as a DIRECTOR/ADAPTATION decision, layered on top of
     source evidence -- never as a correction to the book
```

Stated as the general rule this generalizes to: *"Can this entity ever
spawn?"* and *"Should this entity spawn in this specific scene?"* are
two different questions, and only Dragon-as-director (acting on the
player's explicit instruction) should ever answer the second one when
the source itself doesn't. Source truth (what the book establishes)
and game truth (what the player wants the built scene to contain) stay
visibly distinct, with the director's own additions layered on top of,
never overwriting, the source-evidence layer. This is the same
discipline the whole `mrlore-audit` line already established for
identity/canon — extended here to cover *presentation* decisions during
automatic game construction.

## What actually happened live, using this exact reasoning

**The ingestion authorization** (`id=50396`, user; `id=50397`,
Dragon's `[EDITOR_REQUEST]`) is worth recording in full detail because
of how rigorously Dragon specified it — this is the first time in this
whole audit line that Dragon has proposed a *write* through this
channel, and it did so with an extremely narrow, pre-verified scope:
bound to the source's exact SHA-256, an itemized precondition-recheck
list (source hash, ingestion status, absence of every target path,
manifest hash, no other pipeline running, `PYTHONDONTWRITEBYTECODE=1`),
an explicit authorized-write allowlist (only the four preflight-listed
scene artifacts plus one named manifest overwrite), an explicit
not-authorized list (source mutation, MrLore writes, canon promotion,
avatar-project mutation, Godot execution, network/model access,
package installation, any second ingestion, any other source, and
explicitly *no follow-up scene query as part of this same request*),
and a full failure-rollback procedure (kill subprocesses, remove only
the preflight-listed artifacts, restore the manifest byte-for-byte to
its named SHA-256, never touch the source).

**The ingestion completed** (`id=50533`): source status flipped
`not_ingested` → `existing`, chapter ID
`chapter.book001.001_the_ethereal_vigil`, 4 mechanical scenes, source
SHA-256 unchanged (verified), 39 new evidence files created, one
manifest file modified, zero deletions, zero avatar/MrLore/canon/
runtime mutation.

**Dragon caught a real reporting-boundary mismatch on its own, and
flagged it instead of hiding it:**

> "There is a coordination-report inconsistency that should remain
> visible: the outer summary says `Created 0, modified 0, deleted 0`,
> while the detailed result reports 39 created files and one modified
> manifest. The aggregate wrapper clearly did not count the external
> EngAIn writes."

**This is not a bug in the `result_text` fix — it's the fix working
correctly, one layer up.** `execution_summary`/`files_created` in
`editor_report.v1` are built from `live_tree_changes`, which tracks
mutations to the *avatar project's own tree* (`godot_engain_3d_avatar`,
`res://` paths) — the boundary the authorization/staging system exists
to govern. A Mettaext ingestion writes into *EngAIn's own stageroom
directory*, a different location that mechanism was never built to
see. So the aggregate wrapper is telling the truth about the one tree
it watches, while the real 39-file write lived entirely in
`result_text` — which is exactly what let Dragon see it, quote it
precisely by path, and flag the mismatch rather than either hiding it
or getting confused. This is the same "self-report is not proof, go to
the receipt" discipline this whole audit has applied to Dragon's own
actions, now visibly operating on the Editor's report *from Dragon's
own side*. Left open, not fixed here: whether `files_created`/
`execution_summary` should eventually be widened to also account for
EngAIn-tree writes during a controlled ingestion, so the aggregate and
detailed views stop visibly disagreeing — a real design decision, not
something to change unilaterally.

## The first real scene-evidence result (`id=50573`, in full)

With the source now ingested, a fresh read-only `[EDITOR_REQUEST]`
(`id=50535`, `Request ID: read_first_scene_ethereal_vigil_04`) returned
a genuinely rich, well-organized evidence packet — the first time in
this entire audit line that a scene query has returned real narrative
content instead of `INGEST_REQUIRED`:

```text
Scene: scene.book001.001_the_ethereal_vigil.scene001 (of 4 generated scenes)

Setting: Ethereal Realm / Akashic Records (an orbiting library, "a moon
of pure knowledge," geosynchronous anchor, bridge between realms); the
Veil (friction-space between ethereal and physical reality). Formal
structured location remains "Unknown" -- not backfilled with an
inference; "Ethereal Realm"/"Akashic Records" come directly from
returned source text.

Characters present: six Aeon Keepers as consciousnesses/distributed
awareness -- five named (Lyaris, Theron, Vaelith, Mordain, Syreth), one
unidentified. Explicit qualification:
  Physically embodied characters: unsupported
  Scene-present consciousnesses: five named Keepers plus one unidentified

Pelagor: not co-located; observed remotely.
Tiamat, Marduk: historical references, not scene-present characters.

Objects/environment: temporal archives, observation channels, a
crystalline observation lattice, vrill currents, dimensional membrane,
a forming/healing planet, a sky clearing from debris and ash.

Events (11-step sequence): the vigil; Lyaris detects a shift; an
unattributed report ("The planetary core stabilizes"); Theron and
Vaelith extend awareness; the six consciousnesses converge; Mordain
recounts Marduk's collision shattering Tiamat and the Keepers entering
the Ethereal; Syreth reflects on missing physical embodiment ("Sometimes
I miss the sensation of stone beneath feet"); collective observation
toward the surface; detection of transformed Pelagor essence.

Unresolved, listed explicitly: exact source-line boundaries; whether the
generated boundary is authored; formal location/era; the sixth Keeper's
identity; whether any Keeper is embodied; two unattributed speaker
lines; Pelagor's exact location.
```

This is exactly the "physically embodied characters: unsupported,
scene-present consciousnesses: five named plus one unidentified" shape
the design discussion above was arguing for — a real, working instance
of Mettaext preserving *presence* without flattening it into a binary
spawn decision, giving Dragon enough to reasonably build a conservative
first pass (six voices, no character models) while leaving the door
open for a later player instruction to spawn them once the text (or
the player) justifies it.

## Two things preserved as explicit defects, not silently fixed

**1. Scene-boundary uncertainty.** The generated `scene001` chunk
contains two internal headings — `scene 001.1 — ethereal watch /
planetary stabilization` and `scene 001.2 — discovery of transformed
Pelagor` — and Dragon correctly refused to treat the mechanical chunk
boundary as an authored one: *"Those headings occur inside the first
generated scene; they do not establish authored scene boundaries."*
Matters before automatic game construction: a "scene" for build
purposes may actually be two authored beats.

**2. A real extraction bug, caught and correctly not papered over.** A
query for `Tran` returned substring hits on "transformed" and
"transformation" rather than a character. Dragon: *"It did not
establish a character named Tran in this scene."* The underlying
exact-name query still needs hardening (word-boundary matching, not
substring) — not fixed here, just flagged, per the same "leave it ugly"
discipline the whole live-test line has followed.

**3. Also worth tracking (from `id=50533`'s preserved warnings, not
re-verified independently here):** Pass 5 of the ingestion pipeline
reported `No module named 'semantic_environment_extractor'` for scenes
2 and 3 — caught, and the pipeline still produced its expected outputs
and returned success, but a missing module silently substituted for
real environment extraction on two of the four generated scenes is
worth someone's attention before those scenes are trusted the way
scene001 now can be.

## Where this leaves the project

The question this audit line was originally testing — *can Dragon get
real, correctly-bounded scene evidence out of the actual authority
chain, with failures preserved honestly rather than hidden* — is now
answered yes, on a real source, end to end. The next question, not yet
attempted, is architectural rather than diagnostic: how Dragon turns an
evidence packet like the one above into a *proposed* game scene while
keeping every addition it makes (spawned models, camera placement,
lighting, anything not directly in the evidence) visibly and durably
separate from what the source text actually established — so a later
review can always tell which parts are the book and which parts are
Dragon's own adaptation choice.
