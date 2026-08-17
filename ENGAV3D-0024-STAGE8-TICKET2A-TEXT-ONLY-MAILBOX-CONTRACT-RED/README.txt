ENGAV3D-0024 canonically preserves the expected Stage 8 Ticket 2A RED.

Question:
What exact mailbox bytes honestly represent a text_only request without
pretending that current perception exists?

Current Stage 7 answer:
No admitted representation exists.

The provider-free RED verifier proves:
- additional_context.perception omission is rejected;
- perception=null is rejected;
- perception_state=text_only is rejected;
- routing_mode at context level is rejected;
- routing_mode at request level is rejected;
- unavailable perception validates only with capture identity and capture
  failure semantics;
- intentional text_only and failed current perception cannot be structurally
  distinguished by the current request contract;
- provider executions remained zero.

The RED verifier intentionally exits 1 and emits:
STAGE8_TEXT_ONLY_MAILBOX_CONTRACT_GAP

verify_red_evidence.py independently replays that verifier, requires the exact
exit and byte-identical log, and exits 0 to admit the RED evidence itself.

This is not a GREEN text-only mailbox contract. It does not authorize runtime
implementation. A separately authorized schema amendment must define an honest
tagged text-only branch while preserving sealed Stage 7 current perception.
