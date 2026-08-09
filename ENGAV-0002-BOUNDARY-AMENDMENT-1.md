# ENGAV-0002 Boundary Amendment 1 — Workload 3 Historical RED Adjudication

**Status:** AUTHORIZED OPERATOR ADJUDICATION  
**Ticket:** ENGAV-0002 — Hermes B Runtime Perception Proof  
**Scope:** Workload 3 only  
**Artifact class:** Boundary amendment; not an implementation workload  
**Project:** `/mnt/data-drive/engain_avatar`  
**Audit/evidence root:** `/mnt/data-drive/engain-avatar-audit`  

## 1. Normative lineage

This amendment is governed by and lineage-linked to the following exact artifacts:

```text
ticket path: /mnt/data-drive/engain-avatar-audit/ENGAV-0002-PROPOSED.md
ticket sha256: 570f185043b04b3e16c27707eda6ac507e988872eb3c75ea10ecf841c8de6651

freeze path: /mnt/data-drive/engain-avatar-audit/ENGAV-0002-WORKLOAD-2-BOUNDARY-FREEZE.md
freeze sha256: 1351dd7ef540d7158c244707ff8c1a73f1630789fe3f0a4bf1f1f39273f36b51
```

Both hashes were verified against the current bytes before this amendment was written.

The freeze remains frozen at its stated hash and is not edited. This separate document supersedes only the application to ENGAV-0002 Workload 3 of the historical RED-before-original-implementation requirement in freeze section 17, lines 793–797. Every other boundary, proof requirement, stop condition, authorization limit, and present-state review requirement remains in force.

## 2. Clause A — R01-R17 historical RED gate

The frozen requirement that every applicable R01-R17 proof be observed RED
before its corresponding original implementation is WAIVED for ENGAV-0002
Workload 3 by operator adjudication.

It is waived, not satisfied. No evidence establishes the original
pre-implementation history, and later repair-cycle RED/GREEN evidence
cannot establish it retroactively. The gap is permanent and is accepted
knowingly.

Basis for acceptance: the current bytes carry a durable green suite,
independently reviewed repairs, correlated graphical runtime evidence, and
verified Hermes B session continuity. Present-state verification is
accepted in place of unrecoverable process history.

The waiver is scoped to Workload 3 of ENGAV-0002 only. It does not extend
to Workload 4, to any later workload, or to any other ticket.

RED-before-implementation discipline applies prospectively and strictly
from Workload 4 forward. For every proof from that point on, the RED
observation must be captured in a durable timestamped artifact before the
corresponding implementation byte is written.

## 3. Effect and non-effect

This amendment removes only the historical R01-R17 RED-sequence gap as a Workload 3 closure blocker.

It does not:

- assert that the historical requirement was satisfied;
- reconstruct or fabricate missing process history;
- waive any current implementation, security, logic, runtime, provenance, repository-integrity, or exact-byte review blocker;
- declare Workload 3 closed;
- authorize Workload 4 or any implementation activity;
- authorize source, test, evidence, repository, transport, provider, or runtime changes;
- modify the ticket or the frozen boundary artifact.

Any Workload 3 closure decision must still adjudicate the exact-current implementation and evidence against all non-waived requirements.

## 4. Final invariant

```text
For ENGAV-0002 Workload 3 only:
historical R01-R17 RED sequence = permanently unproven, knowingly waived
present-state requirements = not waived
Workload 4 and later RED discipline = prospective, strict, and durable
implementation authorization from this amendment = none
```
