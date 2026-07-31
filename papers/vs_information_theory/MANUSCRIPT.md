# Where does predictive information come from in ligand-based virtual screening, and when can a model be trusted? A reproducible decomposition

**Draft — 2026-07-31.** A standalone synthesis of a pre-registered, byte-identically-reproduced (×2) experimental
program on open data. Every quantitative claim traces to a committed metrics JSON with a payload SHA-256 (referenced as
`[payload …]`); the experiment ledger and code accompany this document. **This is a working draft, not a submission —
it makes no clinical and no novel-drug claim, and it has not been disseminated.**

---

## Abstract

Ligand-based virtual screening (VS) and quantitative structure–activity/potency modelling are evaluated on retrospective
benchmarks whose headline numbers are widely trusted. Through a chain of pre-registered, twice-reproduced experiments on
multiple open benchmark families (LIT-PCBA, the Butkiewicz PubChem-HTS panel, DUD-E, MoleculeACE), we ask three
questions — *how much of reported enrichment is real signal versus benchmark artifact; whether combining or enriching
model inputs adds information; and when a ligand-based model's prediction can be trusted* — and answer them with a small
set of falsifiable principles. **(1)** On standard benchmarks roughly **half of ligand-based enrichment is bias**, split
into two **independent and additive** components — *analogue* (train/test chemical similarity) and *physicochemical/decoy*
— of comparable size, a decomposition that **replicates across two benchmark families** with an interaction ≈ 0. **(2)**
A **small, strongly target-dependent binding signal survives** removing both biases (median AUROC ≈ 0.63, versus a biased
≈ 0.79), but *what makes it survive is not explained* by landscape roughness, activity-cliff density, chemical diversity,
assay format, or data size. **(3)** Landscape roughness **governs interpolation (within known chemistry) but not
extrapolation (to novel chemistry)** — resolving why the surviving signal is small and hard to predict. **(4)** Neither
scalar fusion, feature fusion, a shallow learned representation, a deep 77M-molecule foundation model, an orthogonal
3D-shape channel, nor an orthogonal physics-based docking channel robustly beats a raw-structure baseline on held-out
outcomes: **the bottleneck is information, not representation or combination.** **(5)** The constructive corollary: value
comes not from combining fixed scores but from **choosing which data to acquire** — uncertainty-guided active learning
recovers real actives far faster than random. We state each principle with its supporting evidence, its boundary
conditions, alternative explanations, and confidence level, and we flag several first-class negatives that the field's
incentives usually suppress.

---

## 1. Motivation

Two facts sit uneasily together. Retrospective VS/QSAR benchmarks report strong performance; yet prospective hit rates
and out-of-distribution generalisation are frequently disappointing. A large literature attributes this to *benchmark
bias* (analogue bias — Wallach & Heifets 2018; decoy/physicochemical bias — Mysinger 2012, Chen 2019, Sieg 2019) and to
*activity cliffs / rough landscapes* (van Tilborg 2022). These effects are usually studied **one at a time and on one
benchmark**. We instead build a coherent, quantitative, cross-benchmark picture of **where the predictive information
actually is** and **when a model can be trusted**, using a fixed rigor protocol so that negatives are as credible as
positives.

## 2. Method — the rigor protocol (shared by every experiment)

Each experiment (i) **pre-registers** its hypotheses, competing hypotheses, and a fixed decision rule *before results*;
(ii) fixes random seeds; (iii) compares against **honest baselines** and, where available, the published leaderboard;
(iv) uses **splits that control chemical similarity** — Bemis–Murcko scaffold splits, and a **novel-chemistry lens**
(restricting held-out compounds to nearest-neighbour Tanimoto < 0.40 versus training); (v) controls **leakage** (exact
and cross-label duplicate removal); (vi) judges **effect size, not only p-value**; (vii) records **negatives as
first-class**; and (viii) is **reproduced twice byte-identically** (a payload SHA-256 over the deterministic metrics).
Two mid-study methodology self-corrections were made and documented rather than hidden. A recurring, generalisable
lesson enforced throughout: **before designing a novel-chemistry-controlled experiment, verify that novel chemistry
exists** (measure the fraction of compounds with NN-Tanimoto < 0.40); *distinct scaffolds are not chemical diversity*.

## 3. Results — a set of working principles

Confidence labels follow a promotion rule: a claim is a **Scientific/Replicated principle** only if supported by
multiple independent experiments across target classes with a mechanistic rationale; otherwise it is a **Working
principle** (single benchmark / partial support).

### P2 — Similarity inflation (Replicated; high confidence)
Reported VS performance is systematically inflated by train/test chemical similarity; the honest generalisation estimate
requires a novel-chemistry (low nearest-neighbour) lens. On six diverse targets, panel enrichment falls from a
scaffold-split AUROC of 0.837 to 0.786 when held-out actives are restricted to NN < 0.40, and for one target (an
antiviral phenotypic screen) it collapses to near-chance — its enrichment was similarity-driven, an observation that
independently reproduces in a separate experiment. *Boundary:* NN < 0.40 is one threshold; the effect is monotone in
similarity. `[payload e437713b]`

### P6 — Bias independence and additivity (Replicated; moderate–high confidence)
A 2×2 factorial that crosses **decoy matching** (random vs physicochemically property-matched decoys) with **analogue
control** (random vs novel-chemistry actives) decomposes enrichment cleanly. On eight LIT-PCBA targets, standard AUROC
**0.790** falls to **0.628** with both controls; the decoy-bias and analogue-bias main effects are comparable (**+0.075**
and **+0.087**) and their **interaction is ≈ 0 (−0.019)** — the two biases are *independent and additive*. This
**replicates on a different benchmark family** (a PubChem-HTS panel of a different curation and target set): interaction
**−0.0005**, main effects **+0.050 / +0.100**. Quantitatively, of the enrichment head-room above chance, **≈ 56 % is
bias** (analogue ⊕ decoy) and **≈ 44 % is an irreducible binding signal**; the two artifacts are separable, so honest
evaluation requires controlling **both**. *Mechanistic rationale:* the two biases act on geometrically distinct axes
(chemical-space *similarity* vs *physicochemical-property* distribution), so independence is expected. *Refinement:*
analogue bias ≥ decoy bias consistently. *Boundary (honest):* both families are PubChem-HTS-derived; P6 has **not** been
tested against a fundamentally different *decoy paradigm* (property-matched-yet-topology-dissimilar decoys) on
*diverse-active* data, because no benchmark offers both — DUD-E has such decoys but its actives are so analogue-clustered
(mean NN-Tanimoto 0.71) that a novel-chemistry arm is empty, so the test cannot be run there. `[payload 494d30c7,
32469564, 09a0eb27]`

### P1 — Structure-recoverability / integration negative envelope (Replicated; moderate–high confidence)
When labelled actives are plentiful, the accessible discriminative information is largely recoverable from **raw
molecular structure (2D fingerprints)**; enriching or combining inputs does not add information. Across escalating tests
— scalar late-fusion of module outputs, feature-level fusion, a shallow learned multi-task representation, a **deep
77M-molecule foundation model (ChemBERTa)**, a **ligand 3D-shape/pharmacophore channel**, and an **orthogonal
physics-based docking channel** — none robustly beats a raw-structure baseline on held-out outcomes. The docking case is
the sharpest: docking is genuinely *orthogonal* to the ligand model (rank correlation ≈ 0.27), yet a leakage-controlled
fusion of the two does **not** exceed the stronger single channel (0.821 vs 0.835). *Interpretation:* orthogonality in
score space is not complementarity in information; the ligand model already captures the accessible signal. *Boundary:*
GPU-scale co-folding/affinity models were not tested (infeasible on the available hardware) — a representation of
fundamentally greater capacity remains an untested caveat. `[payload 68c5b043 and the B32–B38 series]`

### P5 — Docking-fidelity gating (Working; low confidence)
Structure-based information helps in the **scarce-data** regime only where the docking model is itself informative for
that target. Sweeping the number of known actives N, an N-independent docking channel beats the ligand model at small N
**only on the one target (a kinase) where docking exceeded chance**; on two others docking fell *below* chance, so the
crossover was absent and the ligand model won by docking's failure, not its own strength. The crossover is therefore
real but conditional on docking fidelity — frequently unmet with an accessible protocol. `[payload 1ba9729c]`

### P7 — Roughness governs interpolation, not extrapolation (Working→refined; moderate confidence)
Structure–activity **landscape roughness** (a continuous, multi-scale roughness index computed on real potency) predicts
a model's **interpolation** generalisation strongly (rank correlation **−0.55** with random-split performance across 30
ChEMBL targets — reproducing the known roughness↔modellability result) but predicts **extrapolation** to novel chemistry
only weakly (**−0.33, n.s.**). A prior experiment using binary labels gave the same weak extrapolation signal (−0.42),
so the weak result is **not** a binary-label artifact. *Consequence:* because the surviving VS binding signal (P6) is an
*extrapolation* quantity, roughness cannot explain it — resolving a string of null attempts to predict the
target-dependent residual from roughness, activity-cliff density, chemical diversity, assay format, or data size. `[payload
bb2b03d3]`

### P8 — The extrapolation gap (Working; moderate confidence)
Ligand-based potency models **interpolate well but extrapolate poorly**: across 19 targets, random-split rank correlation
≈ 0.8 versus novel-chemistry ≈ 0.3, with several targets near zero. What governs this gap is *not* landscape roughness
(P7) and *not* assay format (below); the dominant driver is unidentified and may be largely irreducible (label/assay
noise, distribution shift beyond roughness). This is the sharpest open question the program has produced. `[payload
bb2b03d3]`

### P4 — Acquisition dominates combination (Working; moderate confidence)
Given fixed information, the highest-leverage action is not combining or re-representing it but **choosing which labels
to acquire**. In a closed-loop simulation against a hidden real-bioactivity oracle, model-guided active learning recovers
**≈ 2.8× more real actives than random** at a fixed testing budget; uncertainty-guided acquisition wins model
generalisation while exploitation wins hit recall (the classic explore/exploit trade-off, characterised). This is the
constructive counterpart to the integration negatives: value is created by *deciding what to measure next*, not by fusing
existing scores. `[payload e71129f4]`

### Two clean negatives that bound the theory
- **Protein-representation null (P3; low–moderate).** In a proteochemometric model, ESM-2 protein-sequence embeddings add
  **no** usable target-specific signal over pooled ligand structure for held-out-target prediction; cross-target transfer
  is carried by ligand chemistry, not the protein representation. `[payload 755706ee]`
- **Assay format does not explain the residual.** A biochemical (isolated-protein) versus cell-based (functional +
  phenotypic) contrast on the surviving binding signal is **null** (medians 0.597 vs 0.646; Mann–Whitney p = 0.71); a
  suggestive phenotypic signal seen earlier was driven by two antiviral datapoints and does not generalise. `[payload
  2d7628c5]`

## 4. Discussion — the coherent picture

The results assemble into one narrative about *how predictive information behaves in ligand-based VS*:

1. **Half of what standard benchmarks reward is bias** — and the bias has two separable, additive parts (analogue ⊕
   decoy). Controlling one is not enough; honest evaluation needs both (P6, P2).
2. **A modest, target-dependent binding signal is real** and survives both controls (P6) — but it is an *extrapolation*
   quantity, and extrapolation is the hard part.
3. **Roughness explains interpolation, not extrapolation** (P7); the extrapolation gap (P8) is large and its cause is
   unresolved, plausibly dominated by irreducible measurement noise and distribution shift.
4. **You cannot combine or re-represent your way past the information ceiling** (P1) — not with fusion, not with a
   foundation model, not with orthogonal physics.
5. **The lever that works is data acquisition** (P4): use calibrated predictions to decide what to measure next.

The through-line: **model sophistication and channel fusion are not the bottleneck in small-molecule VS; accessible
information — and honest evaluation of it — is.** Raw structure is a strong, hard-to-beat baseline, most reported
enrichment is half artifact, the real signal is small and lives mostly in the interpolation regime, and progress comes
from acquiring better data, not from combining existing scores.

## 5. Limitations (global)

All results are **retrospective and in-silico**; none is prospectively confirmed — the single most important caveat.
Benchmarks are open bioactivity data with presumed-negative label noise. The roughness index is a validated
reimplementation, not the reference package. Several meta-analyses are modestly powered (n ≈ 13–30 targets) and report
effect sizes over p-values. GPU-scale representations were not tested. Correlational cross-target analyses are not causal.
Property-matching uses six descriptors (a lower bound on decoy artifact). No claim here bears on clinical efficacy or
safety.

## 6. What would move this forward (ranked)
1. **What governs extrapolation error** at the *compound* level (applicability-domain distance vs local roughness vs
   scaffold novelty vs potency shift vs irreducible noise) — a high-power, multi-mechanism decomposition (pre-registered,
   ready). Distinguishes several hypotheses at once and yields, if positive, a *trust rule* for novel-chemistry
   predictions.
2. **Prospective confirmation** of the surviving binding signal / of active-learning hit-rate gains — the only step that
   crosses the retrospective wall; requires wet-lab resources.
3. **A different-decoy-paradigm test of P6** on diverse-active data — requires constructing a new benchmark.

## 7. Reproducibility

Every numerical claim above is a committed, twice-reproduced metrics artifact identified by its payload SHA-256; the
experiment ledger, pre-registrations, and deterministic code accompany this draft. Independent re-execution should
reproduce each payload byte-for-byte under the pinned environment.
