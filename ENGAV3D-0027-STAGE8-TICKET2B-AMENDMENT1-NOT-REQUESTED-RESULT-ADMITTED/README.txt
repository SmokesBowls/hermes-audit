ENGAV3D-0027 canonically admits Stage 8 Ticket 2B Amendment 1 as a
response-wire value-combination contract only.

The exact response top-level and perception_result key sets remain unchanged.
No response routing_mode field is introduced.

New route-coupled successful result:

text_only originating request
+ requested_state=not_requested
+ effective_state=not_requested
+ all capture/image identity null
+ structured_snapshot_supplied=false
+ viewport_image_attached=false
+ failure_code=null
=> accepted successful text-only response

The verifier preserves the exact 0021 full request/response bytes, preserves an
existing current-perception unavailable request/response pair, and rejects all
cross-route combinations and capture/image contamination.

The originating request remains route authority. Both request_id and
client_request_id remain mandatory response correlation identities.

This evidence does not modify production code and does not authorize Ticket 2C,
adapter dispatch, response construction, Godot validation, persistent worker
behavior, or provider execution.

Provider executions: 0
Runtime implementation: NOT AUTHORIZED
