# INTERCEPTA — State of the Vision (honest, evidence-tiered map against the 11-layer architecture)

*Living CSO audit. Every claim cites a committed experiment (see `LEDGER.md`). Purpose: know exactly where we
are vs the fullest vision — "Any disease → understand → reason → intervene → learn → improve" — so each parallel
wave attacks a real gap, not a checkbox. Updated 2026-08-05.*

## Evidence tiers (never blurred)
- **VERIFIED** — reproduced ×2 byte-identical AND tested against *external/experimental* truth.
- **COMPUTED** — reproduced ×2 in-silico; internally sound; no external ground truth yet.
- **ENGINEERING** — built/shipped/works; not a scientific claim.
- **HYPOTHESIS** — plausible, provenance-tagged; untested.
- **GATED** — cannot be advanced by CPU/open-data; needs data or wet-lab/clinical access we don't have.
- **ABSENT** — not built.

---

## The one-paragraph truth
The **front half for bacterial pathogens is genuinely VERIFIED**: label-free FBA gene-essentiality predicts
*experimental* essentiality across **6 curated organisms spanning 3 phyla** and — the strongest evidence — a
**prospective-blind, pre-registered** test on a never-seen WHO pathogen (*N. gonorrhoeae*), plus two held-out
pathogens. That is a real, rare, honest result. **Everything downstream of "which target" degrades sharply in
evidence:** the intervention half works only as *repurposing* and only for the narrow slice of targets with an
already-drugged homolog; de-novo chemistry is a demonstrated ceiling; and the "any disease" claim beyond
bacteria is *just now* being probed (virus: sequence fails, structure bridges in principle but is DB-coverage
gated). **The vision's center of mass — real therapeutic discovery, validated in the lab/clinic — is
EVIDENCE-GATED, not compute-gated.** No parallelism changes that; parallelism gets us to the honest edge faster.

---

## Layer-by-layer

### Layer 0 — Knowledge foundation
**ENGINEERING (broad) / GATED (deep).** We use open genomes, proteomes (UniProt), AlphaFold DB, BiGG curated
GEMs, ChEMBL drug-mechanisms, DEG/PEC/DeJesus/CRISPRi essentiality, PDB. Honest gaps: **AlphaFold DB excludes
viral structures** (GENERALIZE2 boundary); clinical/real-world/proprietary omics are inaccessible zero-budget.

### Layer 1 — Disease understanding
**PARTIAL.** For bacteria/eukaryotic-pathogens we infer essential machinery & metabolism from genome alone. We
do **not** do organism-ID from raw/environmental samples, imaging, or clinical symptoms — those are ABSENT.

### Layer 2 — Representation
**ENGINEERING.** Genome→proteome→GEM (CarveMe de-novo / curated BiGG), sequence & structure homology graphs,
drug-target maps. Dynamic/causal/temporal/patient models: ABSENT.

### Layer 3 — Biological reasoning
**VERIFIED (essentiality) / COMPUTED (rest).**
- Essentiality via FBA — **VERIFIED** vs experiment in 6 organisms (VAL-ESS OR 64 E.coli; CROSSVAL 6/6; SAUREUS
  Gram+ ; VAL-ESS-KP/DEG held-out). Honest bound: **binary enrichment only, recall low (metabolic-scoped);
  fine ranking does NOT generalize** (AUROC ~0.6; chance in Mtb).
- Synthetic lethality / metabolic bypass — **COMPUTED** (SYNLETH1/2; double-deletion-confirmed sets).
- Chokepoints, conservation breadth — **COMPUTED/VERIFIED-for-recall** (REACH1 AUROC 0.86 for non-metabolic
  essentials, at a precision cost).
- Condition-robustness — **COMPUTED** (CONDROB1; core-robust essentials 79% PEC-essential vs 48%).
- Regulation, expression, epistasis, immune escape, causal mechanism: **ABSENT/HYPOTHESIS.**
- **Cross-disease-class generalization (GENERALIZE1–5, fused — see `experiments/GENERALIZE_SYNTHESIS.md`):**
  the method generalizes across classes but NOT uniformly, and the *right signal differs by class*.
  FBA-essentiality: bacteria STRONG (OR 5–64) → yeast/eukaryote TRANSFERS weaker (OR 4.65, PASS) → malaria
  parasite FAILS the bar (OR 2.47 — host-salvage metabolism breaks it). Virus: FBA inapplicable + sequence
  fails, but **blind structural homology recovers both approved targets** (PASS). Governing principle:
  FBA's reach ∝ how self-contained the metabolism is; where metabolism can't carry the signal, structure can.
  **Boundary: host-dependent organisms need host-context-aware modeling, not plain FBA.**
- **Host-context wall, attack #1 (HOSTCTX1, E-Flux) — NEGATIVE, verified:** adding expression context to the
  malaria GEM does NOT rescue the signal (essential set byte-identical, OR unchanged 2.47, robust ×6 variants).
  Mechanism: single-gene essentiality = GPR **bypass topology**, not flux magnitude; expressed salvage routes
  stay usable however throttled. **Refined boundary: the wall is network *content/boundary* (which reactions/
  exchanges exist), not regulatory *state* — so the indicated fix is host-exchange/medium curation (HOSTCTX2),
  not transcriptomics.** Directly relevant to the whole host-embedded class (intracellular pathogens, cancer).
- **HOSTCTX2 (exchange/medium curation) — also NEGATIVE, verified:** moves the set (recall 0.20→0.30) but OR
  stays flat 2.43 (<3), robust ×3 a-priori media, no precision collapse. **UNIFIED CONCLUSION (3 negatives —
  plain + expression + boundary FBA all fail on host-dependent biology): metabolic essentiality is the WRONG
  signal for host-embedded systems (parasite→intracellular→cancer). Evidence-based redirection: pivot to a
  functional-DEPENDENCY layer (CRISPR fitness) — exactly what the human/oncology line's best result (V15–18)
  already uses. For host-embedded target-ID, dependency > metabolic essentiality.**
- **DEPEND1 (Wave 3, VERIFIED G1/G2/G3 PASS, 5b3cb7a) — the redirection realized:** the functional-dependency
  target-ID layer (DepMap CRISPR) recovers known cancer targets (0.80, p 5.6e-21), **generalizes to held-out
  disjoint cell lines** (0.80, p 9e-21 — closing the F3 single-cohort gap for the target-ID layer), and a
  **label-free expr→dependency** arm beats baseline (ρ 0.36 vs 0.20) — the zero-data case a novel host-embedded
  organism represents. So where metabolic FBA failed host-embedded biology ×3, functional dependency
  **succeeds and generalizes**. Honest bounds: cancer cell-line (not clinical); label-free validated on
  held-out DepMap lines, not yet on a true zero-screen organism; lineage-level misses mutation-subset
  dependencies (FLT3).

### Layer 4 — Target discovery
**VERIFIED (bacterial essential-target enrichment) / COMPUTED (multi-axis).** DiscoveryEngine composes 7 signals
+ hard host-safety filter + calibrated confidence + abstention (ENGINE; CALIB1 confidence monotonic). Multi-axis
best-intervention score (BESTINT1 Spearman 0.69 vs #organisms-essential). Per-target scorecard (PREDVAL: cell-wall
+ MEP cores essential in all 3 organisms). **Bounds:** targets are *hypotheses with provenance*; "druggable/novel"
axes weaker than "essential"; confidence saturates at genome scale (use rank_score).

### Layer 5 — Intervention discovery
**HYPOTHESIS / GATED — the first hard wall.** INTERVENE1: repurposing mapping is real (**9/9** canonical
antibacterial MoA recovered) but **narrow — only 1/32** of a novel pathogen's essential targets has an
existing-drug candidate. Biologics/RNA/CRISPR/vaccine/phage/host-directed interventions: **ABSENT.** The
majority of targets need de-novo chemistry (ceiling) or new experiments.

### Layer 6 — Molecule discovery
**ENGINEERING (pipeline) / GATED (real potency) — a demonstrated ceiling.** End-to-end shape exists (ENGINE-MOL:
genome→target→fpocket→Vina dock→ADMET); the whole B30–B65 cheminformatics line is built. **Honest ceiling
(HIT1/HIT2/B48/B65):** docking is a heuristic, not ΔG; within-series potency prediction is at/near chance without
target activity data; de-novo generation produces developable *hypotheses*, not validated inhibitors. This half
cannot be closed by compute alone.

### Layer 7 — Validation
**COMPUTED-tier is STRONG; experimental/clinical is GATED.** Computational: cross-validation, **held-out species,
a genuine prospective-blind test** (BLIND1), external experimental datasets (PEC/DEG/DeJesus/CRISPRi) — this is
our strongest layer and it's honest. **Experimental (KO/CRISPRi/assays) and Clinical (cohorts/outcomes): ABSENT
and un-fundable zero-budget.** This is the true gate on "real therapeutic discovery."

### Layer 8 — Decision engine
**ENGINEERING / COMPUTED.** Multi-axis ranking, calibrated confidence, abstention, provenance tiers, explicit
failure-mode reporting are shipped (ENGINE/CALIB1/BESTINT1). Bayesian/causal/clinical evidence fusion: ABSENT.
**COMPOSITE1 (verified, 759c8b7) — the explicit biology-class-aware ROUTER** now wraps the engine with a
transfer-condition gate: it fires the right validated signal per class and ABSTAINS where none transfers.
Verified on 3 classes (bacterium→FBA shortlist == committed ENGINE; virus→structural, FBA not fired;
host-dependent parasite→ABSTENTION). This is the composite "spine" that turns many validated models into one
system delivering **honest decision coverage** (a real answer where a signal transfers, an explicit abstention
where none does) — not a universal model. See `COMPOSITE_ARCHITECTURE.md`.

### Layer 9 — Autonomous scientist
**EMERGING (this is what today's parallel waves are).** Hypothesis generation, prereg, self-critique, honest
negatives, roadmap redesign, gap detection are operational as *practice* (this map + the audits + the wave loop).
Automated literature analysis / active experiment design: partial (B51 active-learning) / mostly ABSENT.

### Layer 10 — Deployment
**ABSENT (honestly).** No hospital/public-health/pandemic deployment. The realistic near-term deployment is
*computational target-prioritization for a novel bacterial pathogen* — which is validated — delivered as
hypotheses to an experimental group.

### Cross-cutting principles
**STRONG.** Scientific honesty, reproducibility (×2 byte-identical), provenance tiers, auditability, abstention,
uncertainty, negatives-first-class are enforced throughout and are the program's genuine differentiator. Privacy/
security/scalability: not yet stressed (no real patient data or scale).

---

## What parallelism CAN and CANNOT accelerate
- **CAN (parallel waves now):** Layers 1–4 breadth (more disease classes, more reasoning signals), Layer-6
  compute, Layer-9 self-audit. The generalization frontier (virus/fungus/parasite) is the current wave.
- **CANNOT (no amount of compute):** Layer-6 real potency (needs activity data), Layer-7 experimental/clinical
  validation, Layer-5 novel-target chemistry. These are **evidence-gated** — the honest ceiling of a zero-budget
  computational program.

## Consequences, not objectives
Publications/collaborations/funding are *downstream* of a real result. The honest asset today: a **validated,
prospective-blind, reproducible computational target-ID engine for bacterial (and being-tested eukaryotic)
pathogens**, with every limit stated. That is fundable/publishable *as what it is* — not as a drug-discovery
claim it hasn't earned.
