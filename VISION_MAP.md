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
**prospective-blind, pre-registered** SUITE across never-seen organisms spanning ALL THREE DOMAINS OF LIFE (BLIND1-7: bacteria N. gonorrhoeae 6.1/C. jejuni 3.9/B. thetaiotaomicron-new-phylum 8.0 + archaeon M. maripaludis 4.2 PASS; FAIL S. pneumoniae 3.0 sparse-GEM + T. brucei 0.6 host-scavenging kinetoplastid; K. phaffii eukaryote pending = the transfer boundary), plus two held-out
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

**Human-disease / oncology status (F3, consolidated — honest):** the human line has TWO separable claims and
they land very differently. **(a) Patient drug-RESPONSE prediction = TESTED-AND-LARGELY-NEGATIVE** — external
replication on a 2nd patient cohort (B20/FIMM) FAILS, TCGA outcome (B10) is cancer-type-confounded, clinical
outcome (B17) is negative, PDXE-PRISM (B9) is null. This claim is **downgraded to NEGATIVE/gated**; the clinical
endpoint needs prospective data (≡ F0). **(b) Dependency TARGET-ID = COMPUTED-validated (cell-line), with a patient-relevance
bridge** — DEPEND1 generalizes across held-out cell lines and recovers known cancer targets, and **F3CLIN1
(PASS, verified)** shows its selective dependencies are enriched for patient-tumor drivers (OR 2.55, surviving
study-bias controls) — a genuine cell-line→patient *target-relevance* bridge. The composite fires dependency
for human/cancer as *target-ID*, and makes **no** patient-response claim (that's (a), negative). This is the program's weakest disease area, stated as such — not at parity with the
validated bacterial result.

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
  stays flat 2.43 (<3), robust ×3 a-priori media, no precision collapse. On *Plasmodium*, plain + expression +
  boundary FBA all fail.
- **⚠ CORRECTED by HARDENP1 (Wave 4, n=2):** the tempting conclusion "metabolic essentiality is the WRONG signal
  for host-embedded biology" is **FALSIFIED as a universal rule** — a second host-dependent parasite,
  *Toxoplasma gondii*, PASSES FBA strongly (OR 14.10, recall 0.51). Corrected statement: **FBA-essentiality's
  reach is GEM/organism-specific — NOT determined by host-embeddedness.** **PARARESOLVE1 (3487e6c) partially
  resolved the confound:** the GEM axis is a major driver (independent Pf GEMs span OR 0.86→3.07; iAM-Pf480
  *passes* at 3.07), but GEM choice does NOT close the Pf↔Toxo gap (base-rate/biology residual survives), and
  the specific salvage-topology mechanism is **FALSIFIED** (salvage-FN fraction iPfal19 0.907 ≈ Toxo 0.867).
  **PARARESOLVE2 (ebd2771) probed the screen-tech axis** (Bushell barseq-KO, since no Pf CRISPR screen exists):
  the pass/fail verdict flips across GEM×screen (not tech-robust) but the failure *mechanism* is (recall ~0.2
  everywhere). **Sharpened: the OR>3 gate is knife-edge at Plasmodium's noise floor** — verdict flips are
  largely a base-rate artifact, so "Plasmodium passes/fails" is not a stable fact; what IS stable is that
  Plasmodium sits at the noise floor (recall ~0.2) while Toxoplasma is robustly strong (0.51), and the Pf↔Toxo
  gap never closes. Functional dependency (DEPEND1) remains a valid host-embedded signal *where a screen
  exists*, and FBA *also* works on host-embedded organisms with a good GEM — complementary,
  not one-replaces-the-other.
- **DEPEND1 (Wave 3, VERIFIED G1/G2/G3 PASS, 5b3cb7a) — the redirection realized:** the functional-dependency
  target-ID layer (DepMap CRISPR) recovers known cancer targets (0.80, p 5.6e-21), **generalizes to held-out
  disjoint cell lines** (0.80, p 9e-21 — closing the F3 single-cohort gap for the target-ID layer), and a
  **label-free expr→dependency** arm beats baseline (ρ 0.36 vs 0.20) — the zero-data case a novel host-embedded
  organism represents. So where metabolic FBA failed host-embedded biology ×3, functional dependency
  **succeeds and generalizes**. Honest bounds: cancer cell-line (not clinical); label-free validated on
  held-out DepMap lines, not yet on a true zero-screen organism; lineage-level misses mutation-subset
  dependencies (FLT3).
- **TRANSFER1 (37caa0d) — the honest boundary of zero-data host-embedded discovery:** tested whether the
  label-free dependency signal transfers to a NOVEL/zero-screen host-embedded organism (P. falciparum, held-out
  Zhang). Verdict PARTIAL → **it does not** beyond conservation: the SELECTIVE signal fails organism-transfer
  (OR 0.90, chance); only conserved-core transfers (redundant with REACH1 conservation), at ~28% orthology
  coverage. **So for a novel host-embedded pathogen with no screen we can honestly offer only the conserved-core
  (via conservation), never selective targets — and the composite router correctly ABSTAINS there.** A real
  North-Star limit, empirically established, not hidden.

### Layer 4 — Target discovery
**VERIFIED (bacterial essential-target enrichment) / COMPUTED (multi-axis).** DiscoveryEngine composes 7 signals
+ hard host-safety filter + calibrated confidence + abstention (ENGINE; CALIB1 confidence monotonic). Multi-axis
best-intervention score (BESTINT1 Spearman 0.69 vs #organisms-essential). Per-target scorecard (PREDVAL: cell-wall
+ MEP cores essential in all 3 organisms). **Bounds:** targets are *hypotheses with provenance*; "druggable/novel"
axes weaker than "essential"; confidence saturates at genome scale (use rank_score).

### Layer 5 — Intervention discovery
**HYPOTHESIS / GATED — the first hard wall, now mapped for BOTH validated arms.** The target→intervention loop
(does a validated target have an *existing drug*?) is closed and validated for two disease classes, with the
same shape: mapping recovers known pharmacology, but the undrugged fraction is a hard ceiling.
- **Bacteria (INTERVENE1):** 9/9 canonical antibacterial MoA recovered; but only **1/32** of a novel pathogen's
  essential targets has an existing-drug candidate.
- **Human/cancer (INTERVENE2, verified):** 10/10 canonical cancer drug-targets recovered (BRAF→vemurafenib class,
  MDM2→nutlin, KRAS→sotorasib, BCL2→venetoclax…); but only **6.8%** of validated selective dependencies are
  drugged (4.6% approved), **93.2% undrugged** (20% for the patient-driver subset — still 80% undrugged).
Biologics/RNA/CRISPR/vaccine/phage/host-directed interventions: **ABSENT.** The large undrugged majority in both
arms needs de-novo chemistry (the F4 ceiling) or new experiments — the vision's "intervene" half is validated
as a *mapping* but is fundamentally bounded by existing-drug coverage.

### Layer 6 — Molecule discovery
**ENGINEERING (pipeline) / GATED (real potency) — a demonstrated ceiling.** End-to-end shape exists (ENGINE-MOL:
genome→target→fpocket→Vina dock→ADMET); the whole B30–B65 cheminformatics line is built. **Honest ceiling
(HIT1/HIT2/B48/B65):** docking is a heuristic, not ΔG; within-series potency prediction is at/near chance without
target activity data; de-novo generation produces developable *hypotheses*, not validated inhibitors. This half
cannot be closed by compute alone.

### Layer 7 — Validation
**COMPUTED-tier is STRONG; experimental/clinical is GATED.** Computational: cross-validation, **held-out species,
a genuine prospective-blind SUITE** (BLIND1-7 across all 3 domains of life; 4 pass / 3 fail (prokaryotes pass, both blind eukaryotes sub-gate) with a mechanistically-explained transfer boundary; BLIND3-7 git-committed-before-reveal), external experimental datasets (PEC/DEG/DeJesus/CRISPRi) — this is
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
where none does) — not a universal model. **COMPOSITE2 (58f9e5d) wired in the DEPEND1 dependency layer:** the
router now FIRES functional-dependency for the human/cancer class (skin→SOX10, KRAS→KRAS rank #1). **COMPOSITE3
(b1021ae, router v3) refined host-dependent handling** per the HARDENP1 correction: a host-dependent organism
*with a curated GEM* now fires FBA at **capped confidence + an explicit uncertainty flag** (rather than
blanket-abstaining — which would have wrongly refused Toxoplasma), abstains only when no signal exists, and the
advisory GEM-topology descriptor is honestly labeled non-predictive (it doesn't separate pass/fail a-priori).
The router thus admits what it cannot know rather than overclaiming. See `COMPOSITE_ARCHITECTURE.md`.

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
