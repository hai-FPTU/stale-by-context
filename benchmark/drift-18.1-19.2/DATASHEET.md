# Datasheet — CTI version-drift pairs v1.2 (ATT&CK v18.1 → v19.2)

## Motivation
Measure whether LLM/RAG CTI assistants answer according to the outdated or the current ATT&CK release when
the underlying knowledge changed between releases, broken down by change type.

## Composition
- 2415 paired items over 4 templates (technique→tactic, sub-technique→parent by name,
  technique→mitigations, technique-ID currency), each with gold answers for v18.1 and v19.2.
- 7190 queries (item × framing: unversioned / current / historical).
- Pilot subset: 435 items / 1250 queries (all change classes, capped at 80,
  plus 40 STABLE controls per template).
- Mixed-version RAG corpus: 5206 chunks (4239 shared, the rest version-specific).

```
pair_class          STABLE  ANSWER_CHANGED  LABEL_CHANGED  ANCHOR_RENAMED  REVOKED_ANCHOR  NEW_ONLY  TỔNG
template                                                                                                 
D1_tech_tactic         475              72            126               1              17        23   714
D2_subtech_parent      410               0              0               3               8        12   433
D3_tech_mitigation     539               0              0               4              14        20   577
D4_id_currency         670               0              0               4              17         0   691
TỔNG                  2094              72            126              12              56        55  2415
```

## Collection process
Gold answers derived deterministically from MITRE ATT&CK STIX 2.1 (attack-stix-data) for both releases.
Revoked IDs resolved through official `revoked-by` chains, cross-checked against the revocation table of the
ATT&CK v19 release notes (17/17 identical, no one-to-many replacements). An optional manual table for
one-to-many splits exists for future releases (0 entries used here).
Change-type labels come from the release-diff ground truth (notebook 01). No LLM was used to write questions or answers.

## Preprocessing / exclusions
{
 "D2_subtech_parent:PROMOTED": 6,
 "D2_subtech_parent:already_asked_by_old_name": 2,
 "D2_subtech_parent:name_not_unique": 48,
 "D3_tech_mitigation:mitigation_count_out_of_range": 137
}

## Uses
Measuring stale/anachronistic answers and stale labels by change type; evaluating version-aware retrieval.
Not intended as a general ATT&CK knowledge benchmark.

## Known limitations
- Gold follows MITRE's official one-to-one/many-to-one replacements. Scope dispersion (e.g. Impair Defenses'
  former sub-techniques now spread over T1685/T1686/T1688/T1689/T1690) is not encoded as a split.
- Revoked IDs never appear in the v19.2 corpus (0 mentions), so
  current-only RAG cannot link old IDs to replacements lexically; this is a property being measured, not a defect.
- Questions cite entities as named in v18.1 (analyst holding an older document); NEW_ONLY items use v19.2 names.

## Maintenance
Regenerate with notebook 03 for any (old, new) release pair; manifest records SHA-256 of all inputs and outputs.
