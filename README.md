# Stale by Context: ATT&CK version drift in retrieval-augmented CTI assistants

This repository accompanies the paper *"Stale by Context: How Superseded MITRE ATT&CK Passages and Their Labels Mislead Retrieval-Augmented CTI Assistants"* (under review). It contains the version-paired benchmark, every prompt, all raw model outputs, the scored results, the analysis plan with its full version history, and the notebooks that produced them.

Notebook comments and printed messages are partly in Vietnamese. Code, file names and result columns are in English.

## Contents

| Path | What it is |
|---|---|
| `01_thay_doi_phien_ban_ATTACK.ipynb` | Diff of ATT&CK Enterprise releases from the official STIX 2.1 bundles (changes per transition, Appendix/Fig. data) |
| `02_benchmark_theo_phien_ban.ipynb` | Passage corpora per release (`benchmark/attack-*`) |
| `03_cap_cau_hoi_truoc_sau.ipynb` | Version-paired questions and lineage (`benchmark/drift-*`), scorer `ctidrift_scoring.py` |
| `04_pilot_llm_rag.ipynb` | Exploratory pilot with BM25 retrieval (paper Sec. V-A) → `results/pilot-18.1-19.2` |
| `05_ngu_canh_kiem_soat.ipynb` | Exploratory oracle-context experiment E1 → `results/ctx-18.1-19.2` |
| `06_co_che_nhan_phien_ban.ipynb` | Exploratory label-mechanism experiment E2 → `results/mech-18.1-19.2`; stricter scorer `ctidrift_scoring_v13.py` |
| `07_khang_dinh.ipynb` | Confirmatory study, branch A and branch B → `results/conf-18.1-19.2`, `results/conf-6.3-7.2` |
| `08_mo_rong_qwen14b.ipynb` | Pre-specified extension to Qwen3-14B → `results/ext14b-*` |
| `ctidrift_infer_v2.py` | vLLM inference module used by notebooks 07–08 |
| `build_*.py` | Builders that generate the notebooks; their SHA-256 hashes are pinned in the analysis plan |
| `docs/` | Analysis plan with version history (v1.0–v1.4 addendum), annotation guideline and annotation files |
| `FILES.sha256` | SHA-256 of every file in this repository |

Each `results/<run>/` folder contains `prompts/` (one JSONL per condition), `raw/` (model outputs), `scored.csv` (one row per response), summary and confirmatory CSVs, `manifest.json` (input/output hashes, model revisions, library versions) and `logs/`.

## Reproducing the runs

Hardware and software used: one NVIDIA RTX 4070 (12 GB), vLLM 0.31.0, PyTorch 2.13.0 (CUDA 13.0), Python 3.11. Model revisions are pinned in each `manifest.json`. Run the notebooks in order from the repository root. Inference is greedy but GPU batching makes it not fully deterministic; see the paper (Sec. VII).

To check the statistics without rerunning inference, start from `results/<run>/scored.csv` (one row per response, with the lineage cluster of each item); the test functions are in the analysis cells of notebooks 07–08.

## Analysis plan

The confirmatory analysis plan was **pre-specified but not pre-registered**: each version was kept in a dated project record and pinned the analysis code by hash, but it was not deposited in a public registry before the runs. `docs/` contains the full version history, including the one deviation reported in the paper.

## Licences and attribution

- Code: MIT licence (`LICENSE`).
- Derived data (questions, prompts, model outputs, scores): CC BY 4.0.
- ATT&CK content: see `ATTACK_NOTICE.md`.
