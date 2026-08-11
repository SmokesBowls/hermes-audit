# ENGAV3D-0001 Amendment 2
# Stage 6 Mailbox Filesystem Lifecycle

## 1. Purpose

This amendment freezes the concrete Godot-side filesystem lifecycle required
to replace the orphaned 3D HTTP bridge with the already-frozen local JSON
mailbox.

It does not alter the original mailbox wire schemas.

It does not authorize Hermes/provider execution.

It does not authorize HUD, Dragon-speech, movement, world, canon,
GodotOllama, or donor-project changes.

The following remain authoritative:

request schema:
engain.hermes_mailbox_request.v1

response schema:
engain.hermes_mailbox_response.v1

project:
godot_3d_avatar

root scene:
res://scenes/Main.tscn

Dragon scene:
res://scenes/DragonAvatar3D.tscn

Hermes session:
20260731_065008_63a62d

companion:
hermes_b

provider:
openai-codex

model:
gpt-5.6-sol


## 2. Final mailbox paths

Project root:

/mnt/data-drive/godot_engain_3d_avatar

Final request mailbox:

/mnt/data-drive/godot_engain_3d_avatar/engain_request.json

Final response mailbox:

/mnt/data-drive/godot_engain_3d_avatar/engain_response.json

There is exactly one serialized in-flight request.

Neither finalized mailbox may ever be overwritten.


## 3. Request temporary path

Before publication, Godot writes one request temporary file in the project
root.

Exact basename format:

.engain_request.<request_id>.tmp

Example:

.engain_request.req_0123456789abcdef0123456789abcdef.tmp

The request_id must already satisfy:

^req_[0-9a-f]{32}$

No directory scan, newest-file lookup, fallback filename, or substitution is
permitted.

If the exact temporary path already exists, publication fails closed.

The temporary path must not be a symlink and must resolve inside the exact
3D project root.


## 4. Request creation

Godot owns construction of the frozen request wire object.

Godot must:

1. serialize exactly one strict JSON request;
2. write it to the exact temporary request path;
3. flush FileAccess;
4. close FileAccess;
5. invoke the local adapter's publication-only helper.

Godot must not publish directly with a normal rename operation because a
rename capable of replacing engain_request.json would violate the frozen
no-overwrite property.


## 5. Publication-only adapter helper

hermes_session_adapter.py shall expose a provider-free CLI helper:

--publish-request <absolute-temporary-request-path>

This helper is a local filesystem-safety operation only.

It must not:

- invoke Hermes;
- invoke a provider;
- use HTTP;
- process the request conversationally;
- create a response.

The helper must validate:

- the exact project root;
- the exact temporary basename format;
- no symlink;
- regular-file type;
- bounded file size;
- strict UTF-8 JSON;
- duplicate-key rejection;
- non-finite-number rejection;
- exact frozen request schema;
- request_id correlation with the temporary filename.


## 6. Atomic no-replace request publication

The publication helper must use a no-replace filesystem primitive.

Required Linux publication lifecycle:

1. open the temporary request without following symlinks;
2. fstat and require a regular file;
3. validate its exact bytes;
4. fsync the temporary file descriptor;
5. create engain_request.json with an atomic hard-link/no-replace operation;
6. if engain_request.json already exists, publication fails with EEXIST
   semantics and the existing final inode is untouched;
7. fsync the project-root directory after successful publication;
8. unlink the temporary path;
9. fsync the project-root directory again.

A replace-style rename to engain_request.json is forbidden.

The finalized request must contain the exact inode/bytes that were validated
from the temporary request.


## 7. Request publication collision

Before creating a new temporary request, the Godot bridge must check whether
either finalized mailbox exists:

engain_request.json
engain_response.json

If either exists, submission fails locally as MAILBOX_BUSY.

This preliminary check is not considered sufficient for race safety.

The publication helper's atomic no-replace operation is authoritative.

If a publication-time EEXIST collision occurs:

- the existing finalized request remains untouched;
- the new temporary request is removed;
- no automatic retry occurs;
- no second request_id is generated automatically;
- no provider operation occurs;
- the bridge reports MAILBOX_BUSY;
- the bridge does not enter an active in-flight lifecycle.


## 8. Failed request publication cleanup

If publication fails before creation of engain_request.json, the helper must
attempt to remove only the exact temporary file it was given.

It must never delete or replace engain_request.json.

If safe temporary-file cleanup itself fails, the helper returns failure and
the bridge remains fail-closed.

No directory scan or wildcard cleanup is allowed.


## 9. Ownership after request publication

After engain_request.json is successfully published:

Godot no longer owns that finalized file.

Godot must not:

- delete it;
- rename it;
- restore it;
- rewrite it;
- truncate it.

The Python adapter owns request claiming, processing, replay reservation,
restoration after interrupted claiming, and finalized-request cleanup.


## 10. Response polling

The Godot bridge polls only this exact finalized response path:

/mnt/data-drive/godot_engain_3d_avatar/engain_response.json

Runtime polling interval:

100 milliseconds

Polling uses monotonic elapsed time.

No response directory scan is permitted.

No alternative response filename is permitted.


## 11. Response claiming

Godot must not directly open and then delete engain_response.json.

Godot must claim the response through the already-existing local adapter
helper:

--claim-response
/mnt/data-drive/godot_engain_3d_avatar/engain_response.json

This helper is a local filesystem-safety operation.

It is not a Hermes/provider execution.

On successful claim, the helper returns the exact claimed strict JSON bytes as:

ENGAIN_RESPONSE_JSON_BASE64=<base64>

Godot decodes and validates only those claimed bytes.

The adapter helper owns its private claim-path implementation and cleanup.
The private claim filename is not a Godot wire identity and is not searched
or inferred by Godot.


## 12. Unsafe response mailbox objects

If engain_response.json is:

- a symlink;
- not a regular file;
- inaccessible because of unsafe permissions or replacement;
- outside the exact project-root identity;

the response claim fails closed.

Godot must not delete an unsafe unclaimed filesystem object merely to recover
the mailbox.

The bridge reports an error and does not treat the response as accepted.


## 13. Response strictness

Claimed response bytes must satisfy the exact frozen response contract.

Godot must reject:

- malformed UTF-8;
- malformed JSON;
- duplicate JSON keys;
- non-finite JSON numbers;
- unknown top-level keys;
- missing required keys;
- wrong request_id;
- wrong client_request_id;
- wrong provider session identity;
- wrong capture correlation where perception is not rejected;
- action_type other than OBSERVATION;
- nonempty state_changes;
- entropy_impact other than 0.0.

Rejected responses never mutate game, movement, world, canon, inventory, or
Dragon authority.


## 14. Correlation mismatch disposition

A regular response successfully claimed from the exact response mailbox is
consumed by the claim helper.

If its request_id, client_request_id, session identity, or required perception
correlation does not match the active lifecycle:

- reject it;
- do not display it as Dragon/lore speech;
- do not apply state;
- keep the legitimate active request lifecycle waiting;
- continue polling until a valid correlated response arrives or timeout occurs.

No automatic provider retry occurs.


## 15. Malformed claimed-response disposition

If a regular response was safely claimed but its contents are malformed or
fail strict-schema validation:

- reject it;
- emit an error;
- keep the active request lifecycle waiting;
- continue polling until a valid correlated response arrives or timeout.

The claimed malformed file is not restored to engain_response.json.


## 16. Successful response consumption

A response is successfully consumed only after:

- strict JSON validation;
- exact request correlation;
- exact client-request correlation;
- exact frozen session/provider/model validation;
- observation-only authority validation;
- applicable perception correlation validation.

On successful consumption:

- the active request lifecycle ends;
- bridge busy state becomes false;
- dragon_speaking(false) is emitted;
- the accepted narrative may be emitted through the existing presentation
  signal boundary;
- state_changes remain empty;
- no world/canon/movement mutation occurs.

Godot performs no additional response-file deletion because the claim helper
already owns claim cleanup.


## 17. Timeout

The Godot host wait timeout is exactly:

180 seconds

The bridge uses monotonic elapsed time, not wall-clock timestamps.

At timeout:

- active request lifecycle ends;
- busy state becomes false;
- dragon_speaking(false) is emitted;
- an explicit bounded timeout error is emitted;
- no provider retry is initiated;
- no request or response file is overwritten;
- no response is accepted after that lifecycle has ended.


## 18. Late response cleanup

A response arriving after the corresponding active lifecycle has ended is
stale.

When engain_response.json exists and there is no matching active lifecycle:

- claim it through --claim-response;
- validate enough identity to classify it as stale;
- never emit it as Dragon/lore speech;
- never mutate state;
- discard the claimed response;
- emit a bounded stale-response diagnostic.

This prevents a late unread response from permanently blocking later mailbox
work.


## 19. Request collision with unread response

If engain_response.json already exists when new submission is attempted:

- reject new submission as MAILBOX_BUSY;
- do not create a request temporary file;
- do not generate a provider call;
- do not overwrite or delete the unread response.

Stale-response cleanup is a separate polling/claim operation.


## 20. Local helper execution boundary

Stage 6 distinguishes two kinds of process execution.

Allowed local filesystem helpers:

hermes_session_adapter.py --publish-request ...
hermes_session_adapter.py --claim-response ...

Forbidden during Stage 6A fixture proof:

- Hermes chat execution;
- provider execution;
- --resume provider dispatch;
- --image provider dispatch;
- HTTP;
- sockets;
- /v1/engain/parse.

The local publication and claim helpers must be independently testable with
provider execution monkeypatched to fail if called.


## 21. Legacy HTTP removal

The completed Stage 6 bridge must contain no active dependency on:

http://127.0.0.1:8081

/v1/engain/parse

HTTPRequest

HTTPClient

The legacy bridge-local session generator:

S_<timestamp>_<random>

must not be used as Hermes session authority.

The frozen Hermes session remains:

20260731_065008_63a62d


## 22. Stage 6A RED chronology

After this amendment is sealed:

1. write Stage 6A tests before modifying production bridge/helper code;
2. preserve intentional RED;
3. freeze the Stage 6A test bytes;
4. only then implement the smallest mailbox filesystem/helper surface;
5. do not alter RED-era test bytes to manufacture GREEN;
6. run all Stage 4, Stage 5A, Stage 5B, and Stage 6 regressions.

Stage 6A consumes zero provider requests.


## 23. Out of scope

Stage 6A does not authorize:

- a live Hermes request;
- HUD lifecycle redesign;
- final Dragon speech acceptance;
- movement changes;
- world/canon mutation;
- continuous vision;
- GodotOllama changes;
- changes to /mnt/data-drive/engain_avatar;
- HTTP revival.
