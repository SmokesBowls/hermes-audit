Stage 6B pre-provider abort 1.

Reason:
The execution wrapper incorrectly required the optional project-local file:

.godot/engain_hermes_session.json

The run stopped before:
- Godot startup;
- HUD submission;
- request publication;
- adapter --once execution;
- Hermes execution;
- provider execution.

Provider accounting:
authorized: 1
attempted: 0
remaining: 1
retry_authorized_after_provider_attempt: false

This abort does not consume the single Stage 6B live provider crossing.
