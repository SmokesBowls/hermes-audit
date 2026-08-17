ENGAV3D-0025 canonically admits Stage 8 Ticket 2A Amendment 1 as a
request-wire contract only.

The admitted closed union has exactly two branches:

A. Current perception
   additional_context={client_request_id, companion_ref, perception}
   routing_mode absent
   sealed Stage 7 full/unavailable validation retained

B. Text only
   additional_context={client_request_id, companion_ref, routing_mode}
   routing_mode=text_only
   perception and every capture/snapshot/viewport/image key forbidden

The canonical verifier proves the complete fail-closed matrix, validates the
exact mandatory text-only JSON bytes, admits the exact sealed 0021 full request
without byte changes, admits an unchanged-shape unavailable request, and keeps
intentional text-only absence distinct from current-perception failure.

This evidence does not modify or test production runtime support for the new
branch. It does not authorize adapter dispatch, Godot/HUD routing, persistent
worker behavior, response-wire behavior, or provider execution.

Provider executions: 0
Runtime implementation: NOT AUTHORIZED
