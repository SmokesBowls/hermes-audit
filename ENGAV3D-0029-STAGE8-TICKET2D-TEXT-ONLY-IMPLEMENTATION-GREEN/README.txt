ENGAV3D-0029 canonically admits Stage 8 Ticket 2D as the minimal offline
request/response implementation GREEN.

Exactly two production files changed for Ticket 2D:

- hermes_session_adapter.py
- scripts/EngAInBridge3D.gd

One authorized Ticket 2C test received a separately documented one-line harness
correction to establish the frozen session identity before direct command construction.
The other Ticket 2C test remains byte-identical.

Focused result: 11 passed.
Protected result: 191 passed.
Provider executions: 0.

The adapter admits a closed current-perception/text-only request union, avoids image
preparation and image argv for text-only, and emits the admitted
not_requested/not_requested response combination. The bridge admits that combination
only from retained originating-request state with no active capture identity.

No persistent worker, HUD routing, queueing, retries, memory behavior, or provider
execution was implemented.

The pre-existing DragonAvatar3D.gd and cb1d snapshot dirty bytes remain unchanged.
