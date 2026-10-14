# Datasheet — CTI version-drift pairs v1.3 (ATT&CK v6.3 → v7.2)

## Motivation
Measure whether LLM/RAG CTI assistants answer according to the outdated or the current ATT&CK release when
the underlying knowledge changed between releases, broken down by change type.

## Composition
- 1512 paired items over 4 templates (technique→tactic, sub-technique→parent by name,
  technique→mitigations, technique-ID currency), each with gold answers for v6.3 and v7.2.
- 3718 queries (item × framing: unversioned / current / historical).
- Pilot subset: 656 items / 1728 queries (all change classes, capped at 80,
  plus 40 STABLE controls per template).
- Mixed-version RAG corpus: 4642 chunks (3175 shared, the rest version-specific).

| template           |   STABLE |   ANSWER_CHANGED |   ANCHOR_RENAMED |   REVOKED_ANCHOR |   NEW_ONLY |   TỔNG |
|:-------------------|---------:|-----------------:|-----------------:|-----------------:|-----------:|-------:|
| D1_tech_tactic     |      103 |               10 |               13 |              129 |        302 |    557 |
| D2_subtech_parent  |        0 |                0 |                0 |                0 |        264 |    264 |
| D3_tech_mitigation |       68 |                6 |               10 |              100 |        252 |    436 |
| D4_id_currency     |      109 |                0 |               17 |              129 |          0 |    255 |
| TỔNG               |      280 |               16 |               40 |              358 |        818 |   1512 |

## Collection process
Gold answers derived deterministically from MITRE ATT&CK STIX 2.1 (attack-stix-data) for both releases.
Revoked IDs resolved through official `revoked-by` chains, cross-checked against the revocation table of the
ATT&CK v19 release notes (17/17 identical, no one-to-many replacements). An optional manual table for
one-to-many splits exists for future releases (0 entries used here).
Change-type labels come from the release-diff ground truth (notebook 01). No LLM was used to write questions or answers.

## Preprocessing / exclusions
{
 "D1_tech_tactic:deprecated_no_successor": 11,
 "D2_subtech_parent:name_not_unique": 8,
 "D3_tech_mitigation:deprecated_no_successor": 11,
 "D3_tech_mitigation:mitigation_count_out_of_range": 121,
 "D4_id_currency:deprecated_no_successor": 11
}

## Uses
Measuring stale/anachronistic answers and stale labels by change type; evaluating version-aware retrieval.
Not intended as a general ATT&CK knowledge benchmark.

## Known limitations
- Gold follows MITRE's official one-to-one/many-to-one replacements. Scope dispersion (e.g. Impair Defenses'
  former sub-techniques now spread over T1685/T1686/T1688/T1689/T1690) is not encoded as a split.
- Revoked IDs never appear in the v7.2 corpus (0 mentions), so
  current-only RAG cannot link old IDs to replacements lexically; this is a property being measured, not a defect.
- Questions cite entities as named in v6.3 (analyst holding an older document); NEW_ONLY items use v7.2 names.

## Maintenance
Regenerate with notebook 03 for any (old, new) release pair; manifest records SHA-256 of all inputs and outputs.
