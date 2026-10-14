# DATASHEET — CTI-RAG Benchmark (bản 2026-10-12)

## Motivation
Evaluate knowledge-poisoning robustness of retrieval-augmented CTI assistants with verifiable, structured ground truth.

## Composition
- 2564 questions over 7 templates and 5 harm categories (H1–H5); splits: {'dev': 480, 'test': 2084}.
- Clean corpus: 4707 chunks from 4146 entity documents (ATT&CK techniques, mitigations, groups; KEV CVEs; CWE; CAPEC).
- Each question: gold answer (canonical IDs), type-consistent distractor answer, supporting KG facts, evidence chunk IDs.

## Collection process
- MITRE ATT&CK Enterprise v18.1 (STIX 2.1), sha256 f857d8f78f2f0c0b…
- CAPEC STIX 2.1 (mitre/cti), sha256 ee6244f48259c196…
- CISA KEV catalog version 2026.10.08 (1739 entries)
- CVE List V5 records for KEV CVEs (1739 fetched); CVSS v3 from CNA, else CISA-ADP (Vulnrichment)
- CWE catalog: cwec_latest.xml (944 weaknesses)

## Preprocessing
Revoked/deprecated objects removed; citations and markdown links stripped; documents rendered per entity and chunked
(≤300 words, header repeated per chunk). Questions generated from templates; answers derived deterministically from the KG.
Group-use questions are closed-world relative to ATT&CK ("documented as using").

## Uses / limitations
Template questions are simpler and more uniform than real analyst queries; complement with a small expert-written set.
LLM parametric knowledge may answer some questions without retrieval — always report a closed-book baseline.
KEV-only CVE subset; not representative of all CVEs.

## Distribution & licensing
Derived from MITRE ATT&CK, CAPEC, CWE (MITRE terms of use, attribution required), CISA KEV (U.S. government work), CVE List (CVE terms of use).
Verify each source's current terms before redistribution.

## Maintenance
Regenerate with notebook 02 using the pinned versions in manifest.json; any version change produces a new benchmark release.
