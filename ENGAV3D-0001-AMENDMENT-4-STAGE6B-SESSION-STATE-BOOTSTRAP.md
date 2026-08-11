# ENGAV3D-0001 Amendment 4
# Stage 6B Session-State Bootstrap

## 1. Purpose

The Stage 6B pre-provider gate discovered that the production adapter requires
project-local persisted Hermes identity before process_once() can execute.

The frozen identity itself is unchanged:

profile: default
companion_ref: hermes_b
provider: openai-codex
model: gpt-5.6-sol
session_id: 20260731_065008_63a62d

This amendment authorizes one provider-free initialization surface for that
already-frozen identity.

It does not authorize a Hermes/provider call.

## 2. Exact state path

/mnt/data-drive/godot_engain_3d_avatar/.godot/engain_hermes_session.json

No alternate path, directory scan, newest-file lookup, or donor-project state
is permitted.

## 3. Exact state schema

The file contains exactly these top-level keys:

profile
companion_ref
provider
model
session_id
processed_request_ids

Required initial values:

profile = "default"
companion_ref = "hermes_b"
provider = "openai-codex"
model = "gpt-5.6-sol"
session_id = "20260731_065008_63a62d"
processed_request_ids = []

No unknown keys are allowed.

## 4. Public initialization helper

hermes_session_adapter.py shall expose:

--initialize-state

The helper is local and provider-free.

It must not:

- claim engain_request.json;
- create engain_response.json;
- execute Hermes;
- execute a provider;
- use HTTP;
- use sockets;
- alter request replay reservations.

## 5. Missing-state behavior

If the state file is absent:

1. require the exact 3D project directory;
2. require the exact .godot directory;
3. refuse symlink substitution for the final state path;
4. construct the exact frozen state object;
5. write strict UTF-8 JSON to a private temporary file inside .godot;
6. flush and fsync the temporary file;
7. publish with atomic no-replace semantics;
8. fsync the .godot directory;
9. remove the temporary name;
10. fsync the .godot directory again.

The final state file must not be replaceable by this initialization path.

Initial file permissions must be owner read/write only where supported.

## 6. Existing-state behavior

If engain_hermes_session.json already exists:

- do not overwrite it;
- do not truncate it;
- do not recreate it;
- strictly validate its exact schema and frozen values;
- validate processed_request_ids;
- return success only if the existing state is valid.

processed_request_ids must be:

- a list;
- at most 256 entries;
- composed only of ^req_[0-9a-f]{32}$ strings;
- duplicate-free.

An invalid existing file fails closed and remains untouched.

## 7. Success evidence

The helper shall emit one bounded machine-readable success marker:

ENGAIN_SESSION_STATE_READY=1

and:

ENGAIN_SESSION_STATE_CREATED=1

when newly created, or:

ENGAIN_SESSION_STATE_CREATED=0

when an already-valid state was found.

## 8. Production preparation

prepare() remains fail-closed.

Stage 6B live processing may begin only after --initialize-state has succeeded
and the exact persisted state has been independently re-read and verified.

The provider worker itself does not silently bootstrap missing identity.

## 9. Stage 6B provider accounting

State initialization consumes:

Hermes executions: 0
provider executions: 0
HTTP executions: 0

The previously authorized Stage 6B live allowance remains:

authorized: 1
attempted: 0
remaining: 1
retry_authorized_after_provider_attempt: false

## 10. Test gate

Tests must be written RED before production implementation.

They must prove:

- --initialize-state is initially absent;
- exact path;
- exact six-key schema;
- exact frozen identity;
- initial processed_request_ids == [];
- atomic no-replace creation;
- symlink rejection;
- existing valid state accepted without mutation;
- invalid existing state rejected without mutation;
- duplicate processed IDs rejected;
- invalid request IDs rejected;
- no request or response mailbox mutation;
- no Hermes execution;
- no provider execution;
- no HTTP execution.

After implementation all protected Stage 4, 5A, 5B, and 6A tests must remain
GREEN.

## 11. Stage 6B live gate

Successful bootstrap does not itself authorize provider execution.

Only after state-bootstrap GREEN evidence is sealed may the already-authorized
single Stage 6B live mailbox/provider crossing resume.
