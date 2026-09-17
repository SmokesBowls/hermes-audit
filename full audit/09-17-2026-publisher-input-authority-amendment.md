# Amendment: Publisher input authority (closes §6 of the Publisher design)

Amends `09-17-2026-narrative-publisher-design-v1.md` §6, which left open
whether the Publisher reads the raw vault directly or Mettaext's tagged
`out_pass1_*.txt` output. Resolved, not left implicit.

## Rule (locked)

> **Canonical Publisher input is the raw admitted narrative vault
> source, never Mettaext- or Tier1-derived artifacts.**
>
> Derived artifacts may be crosswalked back to Publisher coordinates
> (exactly what `09-17-2026-crosswalk-layer-design-v1.md` already does).
> They may never define those coordinates.

## Why, grounded in what's already been proven this session

§0.2 of the original Publisher design suggested reusing Mettaext's
`{type:narration|dialogue|blank}` tagging as a convenience, since it
already marks paragraph boundaries. That convenience is now explicitly
rejected: Mettaext's own tagging sits downstream of its own scene
boundary decision, which its own artifacts already admit is mechanical
and unproven (`@boundary_method: mechanical_word_chunk`,
`@authored_scene_boundaries_proven: false` — real, verified this
session). If the Publisher's canonical coordinates were derived from
that tagging even partially, the "one canonical ruler" the tokenizer
rule exists to protect would silently inherit Mettaext's own admitted
unreliability. A canonical coordinate system cannot be downstream of a
system that documents itself as not-yet-authoritative.

## Consequence

The Publisher performs its own independent paragraph/dialogue-block
detection directly on raw prose (per the boundary priority already
locked in the base design, §4: scene break > paragraph boundary >
dialogue/action block > sentence boundary > hard limit) — it does not
reuse Mettaext's `{type:blank}` markers or scene boundaries as
authoritative input. This is strictly more work than the convenience
originally floated, chosen deliberately over convenience.

## What does not change

- The worked example in §5 of the base design (the five real Act 3
  passages, split on real paragraph breaks) is unaffected — those
  breaks were identified directly from the real prose's own blank-line
  structure, which the Publisher would detect independently either way.
- Mettaext's own pipeline is untouched. It keeps ingesting and producing
  `out_pass1_*.txt` exactly as it does today, for its own purposes.
- The crosswalk layer (`09-17-2026-crosswalk-layer-design-v1.md`) is
  unaffected — it already treats Mettaext/MrLore output as read-only,
  derived evidence to be mapped onto Publisher coordinates after the
  fact, never as the source of those coordinates. This amendment states
  explicitly, as a standing rule, what the crosswalk design already did
  in practice.

## Status

Amendment locked. `09-17-2026-narrative-publisher-design-v1.md` §6 is
closed by this document; the base design's text is not rewritten in
place, per this project's standing amendment convention (see
`6a37272`, the Mettaext door's own stem-collision amendment, same
pattern). No code written.
