ENGAV3D-0023 canonically admits Stage 8 Ticket 1 as a contract-only boundary.

Preserved exact authorities:
- original Ticket 1 contract and SHA-256 sidecar;
- Amendment 1 explicit-no-current-image priority and SHA-256 sidecar.

Lineage:
- ENGAV3D-0022 failed closed because the original routing policy classified the
  mandatory memory fixture as current_perception (`this` + `scene`).
- Amendment 1 adds a higher-priority explicit no-current-image Rule 0 without
  rewriting the original contract bytes.
- The 0023 verifier independently checks both pinned artifacts, both sidecars,
  the closed routing table, repeated deterministic results, all normative
  examples, the mandatory memory fixture, and all six admission answers.

Canonical verdict:
STAGE8_TICKET1_CONTRACT_ADMITTED

Provider executions: 0
Runtime implementation: NOT AUTHORIZED BY THIS GATE
Text-only wire-schema gap: still blocking implementation
