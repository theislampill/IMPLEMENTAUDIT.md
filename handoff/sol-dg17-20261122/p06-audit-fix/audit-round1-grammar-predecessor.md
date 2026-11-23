# P06 final audit round 1

AUDIT_START
Audit candidate input SHA-256 786ba0e43edaf113a7a594a0ee3df387e23c36d392c238d618f3e6635a2ed2f5.
AUDIT_GAPS
P06-CASEFOLD-01. Both actual roles resolve to support.zip on a case-folded reader.
Andon:
  status: STOPPED
  blocker: Two role names collide when normalized.
  failing_check: evidence/l5-round1.json
  owner_source: release-catalog.json
  next_action: Preserve the exact failing manifest, repair only the conflicting filename, then repeat the same audit.
ANDON_PROBE
claim: cross-role-filenames | surface: source | status: failed | evidence-surface: source | evidence-digest: 98b554c9f5e158831c4c22665139e8de287322fdec945718650d8057542669c8
