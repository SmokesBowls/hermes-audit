# ENGAV3D-STAGE8-TICKET-3A
# HUD Status / Capture Order Reconciliation

Status: FROZEN CONTRACT AMENDMENT; RUNTIME IMPLEMENTATION NOT AUTHORIZED
Date: 2026-08-11
Provider executions: 0

## 1. Authority and priority

This amendment reconciles:

1. sealed Stage 7 Amendment 5, especially Section 11, which forbids deliberate
   visible player-view mutation until `capture_for_submission()` returns; and
2. Stage 8 Ticket 1 Sections 15.2, 15.3, and 16, which describe current-perception
   HUD feedback as `looking` followed by capture and then `thinking`.

Stage 7 capture ordering remains authoritative and unchanged. This amendment has
priority over Ticket 1 only where Ticket 1 can be read as requiring a visible
`Dragon is looking...` mutation in the same viewport before capture completes.
Ticket 1 routing, worker ownership, correlation, one-in-flight behavior, and
terminal-status-clearing rules remain unchanged.

Ticket 2F authority is:

```text
ENGAV3D-0031-STAGE8-TICKET2F-EXPLICIT-WORKER-STOP-GREEN
```

Ticket 3A changes no runtime file and authorizes no provider execution.

## 2. Problem statement

The Stage 7 perception event is:

```text
capture_event = message_received
capture_phase = pre_dispatch_player_view.v1
```

The captured viewport must represent the player-visible view at message receipt,
before submission presentation changes it. If the same captured viewport visibly
renders `Dragon is looking...` before capture, the perception evidence contains a
status message caused by the request itself. That violates the sealed Stage 7
no-visible-mutation boundary.

Therefore internal lifecycle truth and visible HUD presentation are distinct.

## 3. Status classes

### 3.1 LOOKING_INTERNAL

`LOOKING_INTERNAL` means a current-perception submission has been reserved and is
inside its required capture boundary.

It is local lifecycle state. It may exist before capture. It is not provider prose,
not conversation history, and not permission to mutate the captured viewport.

```text
LOOKING_INTERNAL=ALLOWED_BEFORE_CAPTURE
```

### 3.2 LOOKING_VISIBLE

`LOOKING_VISIBLE` means any visible `Dragon is looking...` presentation or equivalent
visible mutation.

Before current-perception capture returns, it is forbidden on every surface included
in the perception capture.

```text
LOOKING_VISIBLE_IN_CAPTURED_VIEWPORT=FORBIDDEN_BEFORE_CAPTURE
```

A future UI may show looking status before capture only on a surface independently
proved to be excluded from the perception capture. Ticket 3A neither requires nor
implements such a surface.

### 3.3 THINKING_VISIBLE

`THINKING_VISIBLE` means temporary visible `Dragon is thinking...` presentation or
equivalent thinking state. It begins only after successful request commit. It is local
lifecycle feedback, never provider content or history.

```text
THINKING_BEGINS_AFTER_REQUEST_COMMIT=DEFINED
```

Request commit means the exact request has been successfully published and its active
`request_id + client_request_id` correlation is retained. Capture completion without
successful publication is not commit.

## 4. Current-perception submission lifecycle

The authoritative full or valid-unavailable current-perception sequence is:

```text
1. player submits
2. reserve the one-in-flight lifecycle and allocate client_request_id
3. internal lifecycle state = LOOKING_INTERNAL
4. visible captured viewport remains unchanged
5. capture_for_submission(client_request_id) occurs
6. exact full evidence is persisted/admitted, or one valid unavailable result returns
7. construct and successfully publish the exact correlated request
8. retain active request_id + client_request_id (+ capture_id)
9. emit submission commit acknowledgment
10. visible HUD may now show Dragon is thinking...
11. correlated terminal response or terminal failure arrives
12. clear thinking status
13. render the response or terminal failure presentation as authorized
```

No visible looking or thinking mutation may enter the captured viewport before Step 5
returns. For full perception, exact persisted image admission remains the Stage 7
authority. For valid unavailable perception, a real capture attempt with producer-owned
`capture_id` remains required; it does not become text-only.

## 5. Text-only submission lifecycle

The authoritative text-only sequence is:

```text
1. player submits
2. reserve one-in-flight lifecycle
3. classify/admit text_only locally
4. do not invoke capture and do not allocate capture_id
5. construct and successfully publish the exact correlated text-only request
6. retain active request_id + client_request_id
7. emit submission commit acknowledgment
8. visible HUD may now show Dragon is thinking...
9. correlated terminal response or terminal failure arrives
10. clear thinking status
11. render the response or terminal failure presentation as authorized
```

Text-only cannot enter `LOOKING_INTERNAL`, cannot invoke capture, and cannot attach
current image identity.

## 6. Correlated status ownership

Every temporary visible thinking status is owned by one active lifecycle generation and
its exact:

```text
request_id + client_request_id
```

A response clears status only when both IDs correlate with the active request and the
response is otherwise admitted by the existing route-coupled response contract.

Consequences:

```text
response for wrong request_id
→ must not clear active status

response for wrong client_request_id
→ must not clear active status

old response after a newer committed submission
→ must not clear newer status

malformed, stale, duplicate, or route-incompatible response
→ must not clear active status
```

Generation guards may be used, but they do not replace exact ID correlation.

## 7. Terminal failure and clearing

Temporary status must not survive a terminal lifecycle. Clear it on:

- successful correlated response;
- valid correlated terminal adapter/provider failure response;
- capture-result contract failure;
- capture failure that terminates locally rather than publishing valid unavailable;
- request construction or publication failure;
- image preparation/admission failure;
- timeout;
- explicit worker shutdown;
- runtime shutdown;
- unrecoverable integrity shutdown.

Pre-commit capture or publication failure must not begin visible thinking as though the
request had committed. Internal `LOOKING_INTERNAL` terminates without becoming
`THINKING_VISIBLE`.

## 8. Fail-closed admission matrix

The following matrix is normative:

| Case | Required verdict |
|---|---|
| current-perception internal LOOKING before capture, no visible mutation | ACCEPT |
| visible HUD mutation in captured viewport before current-perception capture | REJECT |
| visible thinking in captured viewport before capture | REJECT |
| visible looking on independently proven capture-excluded surface | MAY ACCEPT in later contract; not required here |
| current-perception exact capture then successful publication then thinking | ACCEPT |
| current-perception skips required capture | REJECT |
| valid current-perception unavailable attempt with capture identity then commit | ACCEPT |
| text-only invokes capture | REJECT |
| text-only allocates capture/image identity | REJECT |
| text-only successful publication then thinking | ACCEPT |
| capture fails before commit but thinking begins | REJECT |
| publication fails but thinking begins/persists | REJECT |
| wrong request_id clears status | REJECT |
| wrong client_request_id clears status | REJECT |
| old response clears newer lifecycle status | REJECT |
| correlated terminal response clears its own status | ACCEPT |
| timeout leaves transient status | REJECT |
| runtime or explicit worker shutdown leaves transient status | REJECT |

## 9. Amendment to Ticket 1 Sections 15 and 16

Ticket 1 Sections 15.2 and 15.3 are read as follows:

```text
submission admitted internally
→ LOOKING_INTERNAL while captured viewport remains visibly unchanged
→ Stage 7 capture boundary returns full or valid unavailable perception
→ exact request successfully publishes and becomes committed
→ Dragon is thinking... may become visible
→ correlated response OR explicit terminal failure
→ temporary status absent
```

Ticket 1 Section 16 answer 5 is amended from visible `looking then thinking` to:

```text
HUD lifecycle:
  text_only:
    no looking; visible thinking only after request commit

  current_perception:
    internal looking before/during capture with no captured-viewport mutation;
    visible thinking only after request commit

  every terminal outcome:
    transient status absent
```

No routing predicate, route result, capture permission, image permission, worker owner,
or worker lifetime answer is changed.

## 10. Explicit non-goals

Ticket 3A does not authorize:

- edits to any repository production or test file;
- Godot worker process ownership or lifecycle wiring;
- `ControlHUD.gd` or `EngAInBridge3D.gd` implementation;
- route-aware signal names or API spelling;
- visible looking UI on a capture-excluded surface;
- HUD layout or presentation design;
- provider execution;
- queueing, concurrency, retry, restart, or active-request cancellation;
- changes to Stage 7 capture bytes, capture timing, schemas, or correlation;
- changes to Tickets 2A through 2F implementation authority.

## 11. Canonical admission target

```text
STAGE8_TICKET3A_HUD_CAPTURE_ORDER_ADMITTED

CURRENT_PERCEPTION_INTERNAL_LOOKING=DEFINED
VISIBLE_LOOKING_BEFORE_CAPTURE=FORBIDDEN
CAPTURE_PRECEDES_VISIBLE_HUD_MUTATION=PRESERVED
THINKING_BEGINS_AFTER_REQUEST_COMMIT=DEFINED

TEXT_ONLY_CAPTURE=FORBIDDEN
TEXT_ONLY_THINKING_AFTER_COMMIT=DEFINED

CORRELATED_RESPONSE_CLEARS_STATUS=DEFINED
UNRELATED_RESPONSE_CANNOT_CLEAR_STATUS=DEFINED
TERMINAL_FAILURE_CLEARS_STATUS=DEFINED

STAGE7_CAPTURE_ORDER=UNCHANGED
TICKET1_ROUTING=UNCHANGED
PROVIDER_EXECUTIONS=0
RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED
```

## 12. Final invariant

Internal lifecycle state may truthfully say the Dragon is looking before capture.
Nothing visible inside the captured player viewport may say so until the sealed Stage 7
capture boundary has returned. Visible thinking begins only after successful request
commit, and only the correlated lifecycle or a terminal local shutdown/failure may clear
it.
