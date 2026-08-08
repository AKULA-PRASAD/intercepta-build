# For reviewers (AI or human) — how to read this repository

This is a **rigor-first, falsify-first** computational-discovery program with two arcs: a computational-oncology engine
(the first arc, below) and — the governing north star ([`VISION.md`](VISION.md)) — **zero-data / "any disease" target
discovery** (the second arc, which the current flagship manuscript reports). It is not a product pitch: it reports where
each capability genuinely works, where it fails, and its decisive negatives — all pre-registered and reproduced. If you
are evaluating it, here is the honest map and how to verify every claim.

## 30-second orientation
- **Repo:** https://github.com/AKULA-PRASAD/intercepta-build (public). Default branch `main`.
- **Authoritative record:** [`LEDGER.md`](LEDGER.md) — every finding tiered as verified / refined / falsified /
  underpowered / **first-class negative**. Where any other doc conflicts with the ledger, **the ledger wins.**
- **The current flagship paper** (governing arc): [`papers/zero_data_discovery/REPORT.md`](papers/zero_data_discovery/REPORT.md)
  — zero-data discovery + the generalization frontier + the abstaining router; pre-submission red-team in
  [`papers/zero_data_discovery/ANTICIPATED_REVIEWS.md`](papers/zero_data_discovery/ANTICIPATED_REVIEWS.md). **See "The
  second arc" below.**
- **The first-arc (oncology) paper:** [`papers/intercepta_engine/MANUSCRIPT.md`](papers/intercepta_engine/MANUSCRIPT.md) —
  the honest drug-response arc end-to-end, with figures in [`figures/`](papers/intercepta_engine/figures) generated from
  committed metrics.
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

## The second arc — zero-data / "any disease" discovery, generalization, and the abstaining router
Beyond the cancer engine, the governing north star ([`VISION.md`](VISION.md)) is zero-data discovery for **any** disease.
That arc is built and, in the same falsify-first spirit, honestly bounded. **The authoritative write-up is the manuscript
[`papers/zero_data_discovery/REPORT.md`](papers/zero_data_discovery/REPORT.md)** (Part I bacterial arc + Part II
generalization/composite); every chapter is in `LEDGER.md`, reproduced ×2. A pre-submission adversarial self-review —
the sharpest objections stated at full strength, with honest responses and the revisions to make before submitting — is in
[`papers/zero_data_discovery/ANTICIPATED_REVIEWS.md`](papers/zero_data_discovery/ANTICIPATED_REVIEWS.md); **read it first
if you are here to critique the paper — we have very likely already stated your objection.**
- **What it maps:** an **information ceiling** — zero-data target-ID from sequence ≈ generic conservation (TID1–4); the
  molecule half is analog-bound (HIT1) with a weak physics floor (C1/HIT2). Crossing it needs new experimental data.
- **The one signal that breaks it, now experimentally anchored:** mechanistic **FBA gene-essentiality** adds *beyond*
  conservation (MET1–3, replicated) and is enriched for **experimental** knockout essentiality across **six curated
  cross-phylum GEMs (OR 4–45)** + two held-out WHO pathogens (VAL-ESS/CROSSVAL/PREDVAL). The non-metabolic extension
  (PPI-centrality) was caught as a **study-bias artifact** (MET4) — falsify-first killing a tempting positive pre-commit
  (see also the HIT1 tautology and E2E2 corrections).
- **Prospective (analyst-blind, lock-before-reveal) suite across all three domains of life** (BLIND1–7, **4 pass / 3
  fail**; 5 git-committed before reveal): every prokaryote with an adequate GEM passes — three bacterial phyla + an
  **archaeon** — while both strictly-blind eukaryotes sit sub-gate; failures fall *predictably* on invariant/model
  boundaries (host-scavenging kinetoplastid; sparse de-novo model; a fungus with real p≈4×10⁻⁵ but sub-gate OR). Honest
  boundary, not a clean sweep. (Note: "blind" = version-control-enforced *analyst* blindness against existing public data,
  **not** a wet-lab prospective test — see ANTICIPATED_REVIEWS R2.)
- **The transfer-condition principle + abstaining router:** each label-free signal transfers only as far as the biological
  invariant it rides on is conserved; realized as a **biology-class-aware router** (`src/intercepta/composite_router.py`;
  `intercepta route`) that fires validated signals per class and **abstains** where none is — proven fail-safe at the
  dark-proteome edge (DARK1: 22/22 abstain, 0 false calls). "Any disease" = **honest decision coverage, not a universal
  model.** Data-free unit tests (`pytest`, 67 passing); demonstrations in `experiments/{GENERALIZE,HARDEN,DEPEND,TRANSFER,
  COMPOSITE,CAPSTONE,DARK}*`.
- **Concrete falsifiable predictions + the turnkey wet-lab path:** the method's novel safe bacterial predictions are the
  canonical antibacterial target landscape (murB/murG/mraY, MEP dxr/isp*, CoA, folate, riboflavin). The pre-registered
  truth-test ([`docs/EXPERIMENTAL_VALIDATION.md`](docs/EXPERIMENTAL_VALIDATION.md)) is DONE and exceeded (Tier 0); the next
  rung is a single ~$300 CRISPRi essentiality test, and the **ready-to-execute experiment design** (targets + in-silico
  sgRNA sequences + controls + pre-registered readout) is in `experiments/CRISPRIDESIGN1_wetlab_ready/`. To reproduce the
  arc: run any `experiments/{TID,MET,HIT,FRONT,E2E,GENERALIZE,HARDEN,DEPEND,COMPOSITE,BLIND,META,FAIRGATE}*/run.py` (needs
  `INTERCEPTA_DATA`; deterministic, reproduce ×2).

## Scope note
This is the clean **Phase-B build** — the validated, honest core of the broader INTERCEPTA vision, plus the
evidence-forced roadmap to the rest. It is a rigorous module and an honest map, **not a finished platform**. That
distinction is deliberate and stated wherever the fuller vision is discussed.

*Questions / collaboration (functional-precision oncology partners especially welcome — see
[`docs/COLLABORATION_BRIEF.md`](docs/COLLABORATION_BRIEF.md)): Prasad Akula, akula.pra@northeastern.edu.*
