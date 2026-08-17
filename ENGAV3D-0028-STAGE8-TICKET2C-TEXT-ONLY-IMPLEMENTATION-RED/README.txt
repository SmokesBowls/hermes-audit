ENGAV3D-0028 canonically admits Stage 8 Ticket 2C as an offline,
test-only intentional repository RED.

Authorized repository changes are exactly two new test files. Production code
remains unchanged and unauthorized. The focused suite intentionally returns:

    3 failed, 8 passed

The exact expected failures prove three implementation gaps:

1. the adapter rejects the admitted `routing_mode=text_only` request branch;
2. the explicit zero-image text-only dispatch requirement is unreachable because
   request admission fails first;
3. the bridge rejects the admitted `not_requested/not_requested` result branch.

All Stage 7 request/response preservation checks and route-coupled toxic cases
pass. Hermes/provider execution is mocked forbidden and remains zero.

Persistent-worker lifecycle behavior is explicitly outside Ticket 2C.

The modified DragonAvatar3D.gd and three cb1d snapshot artifacts are pre-existing,
unrelated dirty state. Their exact bytes are frozen in REPOSITORY-IDENTITY.txt and
the canonical verifier confirms they remain unchanged. They were not cleaned,
staged, restored, or absorbed.

Canonical admission is the combination of this evidence root, its SHA256SUMS,
the adjacent root sidecar, and a successful run of verify_ticket2c_red.py.
