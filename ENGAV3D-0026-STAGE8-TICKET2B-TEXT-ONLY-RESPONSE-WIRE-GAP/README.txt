ENGAV3D-0026 canonically preserves the Stage 8 Ticket 2B response-wire
compatibility gap.

Findings:
- existing response correlation is sufficient and route-neutral;
- both request_id and client_request_id are mandatory and independently checked;
- response ordering is not the only correlation mechanism;
- routing_mode is not required on the response for correlation;
- perception_result is mandatory and perception-specific;
- every non-rejected result requires active capture correlation;
- the only existing no-capture shape is unavailable/rejected adapter failure;
- no honest successful text-only/no-perception response exists;
- exact sealed 0021 response bytes remain unchanged.

Fixture A is the exact successful 0021 response.
Fixture B is the admitted Ticket 2A text-only request.
Fixture C uses only existing response keys and correlates to Fixture B, but it
must say unavailable/rejected. It is contract analysis, not provider output.

Canonical verdict:
STAGE8_TEXT_ONLY_RESPONSE_WIRE_CONTRACT_GAP

Exact missing semantic:
SUCCESSFUL_NO_PERCEPTION_RESULT_BRANCH

Provider executions: 0
Runtime implementation: NOT AUTHORIZED
