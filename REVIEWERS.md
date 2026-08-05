# For reviewers (AI or human) — how to read this repository

This is a **rigor-first, falsify-first** computational-oncology program. It is not a product pitch: it reports where
transcriptomic drug-response prediction genuinely works, where it fails, and two decisive negatives — all
pre-registered and reproduced. If you are evaluating it, here is the honest map and how to verify every claim.

## 30-second orientation
- **Repo:** https://github.com/AKULA-PRASAD/intercepta-build (public). Default branch `main`.
- **Authoritative record:** [`LEDGER.md`](LEDGER.md) — every finding tiered as verified / refined / falsified /
  underpowered / **first-class negative**. Where any other doc conflicts with the ledger, **the ledger wins.**
- **The paper:** [`papers/intercepta_engine/MANUSCRIPT.md`](papers/intercepta_engine/MANUSCRIPT.md) — the honest arc
  end-to-end, with figures in [`figures/`](papers/intercepta_engine/figures) generated from committed metrics.
- **Governing rules:** [`CONSTITUTION.md`](CONSTITUTION.md) — truth over vision; every positive guilty until it
  survives permutation + leakage + multiple-testing + confound + external replication; reproduce ×2; never fabricate.

## What is actually claimed (and what is not)
**Verified (reproduced ×2, provenance on file):**
- A leakage-corrected cell-line→cell-line transfer map (mean per-drug ρ=+0.212) with a **hard ceiling** — adding
  proliferation, 50 driver mutations, or a whole second modality (proteomics, B22) does not beat it.
- Textbook AML mutation→drug biology (FLT3-ITD→FLT3 inhibitors, RAS→MEK inhibitors).
- A weak but genuine, proliferation-independent, drug-specific ex-vivo transfer signal (ρ≈0.07), replicated across
  training screens.

**Two decisive first-class NEGATIVES (the core contribution):**
1. **No human clinical prediction** — the apparent TCGA signal is entirely cancer-type confounding (within-cancer
   AUROC 0.504, p=0.43; B10).
2. **A promising functional-inference layer failed external replication** — inferring CRISPR gene-dependency from
   expression beat the FLT3-ITD biomarker *within BeatAML* (V19/V20) but did **not** replicate in an independent
   AML cohort (FIMM/Malani, B20/B21); the known biology replicated, our refinement did not.

**Explicitly NOT claimed:** any validated clinical predictor, novel-molecule, or "any-disease" capability. Earlier
such claims in this project's history were falsified/retracted and are quarantined (see `INTEGRITY_SWEEP.md` and the
banner-flagged `docs/aspirational_original/`, `docs/status/`, `docs/project/` — historical working corpus, not results).

## How to verify (reproduce)
- Every quantitative claim maps to a committed metrics JSON in [`experiments/*/results/`](experiments) and each is
  reproduced twice (byte-identical). Pre-registrations (written before results) are in [`prereg/`](prereg).
- Public inputs (GDSC, DepMap/CCLE incl. proteomics, PRISM, PDXE, TCGA/Xena, FIMM/Malani) are sha256/MD5-listed in
  [`data/MANIFEST.md`](data/MANIFEST.md). **BeatAML is controlled-access (dbGaP phs001657) and is not
  redistributed** — BeatAML-dependent results require your own access, but the aggregate metrics are committed so
  the findings remain inspectable.
- Engine + tests: `pip install -e .`; `pytest` (data-free unit tests); figures: `python
  papers/intercepta_engine/figures/make_figures.py`.

## The recurring lesson, and the forward path
Across five independent fronts, **signals that recover known biology generalize; novel single-cohort refinements do
not** — and no baseline molecular profile (RNA or protein) resolves within-lineage drug specificity. The
evidence-forced conclusion: a transferable functional layer must be **measured in patients, not inferred**. The
de-risked, pre-registered prospective design is in [`docs/BREAKTHROUGH_ROADMAP.md`](docs/BREAKTHROUGH_ROADMAP.md),
[`docs/TRACK1_PROTOCOL.md`](docs/TRACK1_PROTOCOL.md), and the frozen analysis plan
[`prereg/TRACK1_SAP.md`](prereg/TRACK1_SAP.md) (design target N≈200; power reproduced ×2).

## The second arc — zero-data / "any disease" discovery + the extensible substrate
Beyond the cancer engine, the governing north star ([`VISION.md`](VISION.md)) is zero-data discovery for **any** disease.
That arc is built and, in the same falsify-first spirit, honestly bounded (full map:
[`papers/zero_data_discovery/REPORT.md`](papers/zero_data_discovery/REPORT.md); every chapter in `LEDGER.md`, reproduced ×2):
- **What it maps:** an **information ceiling** — zero-data target-ID from sequence ≈ generic conservation (TID1–4); the
  molecule half is analog-bound (HIT1) with a weak physics floor (C1/HIT2). Crossing it needs new experimental data.
- **The one signal that breaks it:** mechanistic **FBA gene-essentiality** adds *beyond* conservation (MET1–3, replicated);
  the non-metabolic extension (PPI-centrality) was caught as a **study-bias artifact** (MET4) — a representative example of
  the falsify-first discipline killing a tempting positive before it was recorded (see also the HIT1 tautology and E2E2/
  SUBSTRATE5 corrections, all pre-commit).
- **The engine:** an extensible, disease-agnostic **"any disease → a query" substrate** (`src/intercepta/substrate.py`,
  [`docs/SUBSTRATE.md`](docs/SUBSTRATE.md); `intercepta substrate`) with provenance-tiered governance (hard safety filter,
  abstention, self-generated-evidence quarantine). Data-free unit tests in `tests/test_substrate.py`; demonstrations in
  `experiments/SUBSTRATE1–5` (bacteria / virus / molecules / human cancer). Honest bound: **architecture universal; answer
  quality disease-class-specific** (strong for pathogens, a real ceiling for human single-disease queries).
- **Concrete falsifiable predictions + how to check them for $0:** the method's novel safe bacterial predictions are the
  canonical antibacterial target landscape (murB/murG/mraY, MEP dxr/isp*, CoA, folate, riboflavin; EXPVAL/BROADSPEC/PANBACT/
  DRUGGABLE). The pre-registered truth-test ([`docs/EXPERIMENTAL_VALIDATION.md`](docs/EXPERIMENTAL_VALIDATION.md)) is a
  turnkey validator (`experiments/VALIDATE_essentiality`) that scores FBA-predicted vs experimental essentiality the instant
  an essential-gene list is provided. To reproduce the arc: run any `experiments/{TID,MET,HIT,FRONT,E2E,SUBSTRATE,PANBACT,
  BROADSPEC,DRUGGABLE}*/run.py` (needs `INTERCEPTA_DATA`; deterministic, reproduce ×2).

## Scope note
This is the clean **Phase-B build** — the validated, honest core of the broader INTERCEPTA vision, plus the
evidence-forced roadmap to the rest. It is a rigorous module and an honest map, **not a finished platform**. That
distinction is deliberate and stated wherever the fuller vision is discussed.

*Questions / collaboration (functional-precision oncology partners especially welcome — see
[`docs/COLLABORATION_BRIEF.md`](docs/COLLABORATION_BRIEF.md)): Prasad Akula, akula.pra@northeastern.edu.*
