# GOVERNING NORTH STAR (strategic correction, 2026-07-31) — read this first, every planning cycle

**This section governs. The 2026-07-29 charter below is a validated but NARROW branch (cancer drug-response
prediction); it remains true and is kept, but it is NOT the north star.** The north star is:

> **A computational system capable of discovering the best therapeutic intervention for ANY disease — including
> diseases humanity has never seen before.**

Benchmark scores, AUROC, "better QSAR," another molecular-ML paper are **supporting tools only**, never the objective.

**The stress test (the only one that counts).** Tomorrow a new pandemic appears: no activity dataset, no IC50 labels,
no known inhibitors, no medchem campaigns, no training data. **Can INTERCEPTA begin producing scientifically credible
drug candidates within hours?** If the answer is "no, we need labeled data," we are optimizing the wrong thing.

**Evaluation filter for every proposed experiment/chapter:** (1) "Does this move us closer to the ZERO-DATA disease
problem?" (2) "Would this capability still matter if the disease had never existed before?" If no → supporting work.

**The 11 fundamental capabilities (think in these, not in models):** disease understanding · mechanism inference ·
target prioritization · structure prediction when unknown · binding reasoning · molecule generation · multi-objective
optimization · ADMET reasoning · manufacturability · experimental prioritization · continuous learning from new
evidence. **ML is one tool inside this pipeline, never the foundation.**

**Reconciliation with our hard-won evidence (why this is not backsliding).** The ceilings we proved (the +0.212 wall,
the six-front intrinsic-ceiling proof, B54–B65) are all about *predicting from labeled molecular profiles / activity
data*. The zero-data discovery front is **orthogonal** to those falsifications — it is label-FREE (physics / structure
/ transferred knowledge), a front our evidence never tested. The label-dependent line (ligand-based VS, QSAR roughness,
active learning) is now explicitly **supporting work**.

**What deep research (2026-07-31) establishes as the honest shape of the solution — and its limits.**
- "Zero-data" never means zero *knowledge*: a new pathogen's proteins usually have homologs, and the system's power is
  **how well it TRANSFERS** known druggability, scaffolds, and reference chemistry to the unseen target
  (Paxlovid/nirmatrelvir was homology transfer from a 2003 SARS-CoV-1 inhibitor; SARS-CoV-2 Mpro/RdRp were prioritized
  in weeks because they were ~96% identical to SARS-CoV-1).
- The credible label-free pipeline is **homology-anchored, physics-filtered**: sequence → fold (AlphaFold/ESMFold, gate
  on pLDDT/PAE) → pocket/druggability (reliable zero-shot) → **transfer inhibitor scaffolds/reference ligands from the
  nearest homolog** → structure-based generation + ultra-large docking for *pose-plausible* hits → transfer-ADMET/synth.
- **The weakest link is binding-affinity RANKING:** no method ranks affinity credibly with zero target data (docking is
  near-random prospectively; FEP needs a reference series). So the honest zero-data OUTPUT is *pose-plausible,
  homology-anchored candidate hypotheses*, explicitly requiring assay confirmation — NOT potency-ranked leads.
- **The hard failure case** (state it, never hide it): a truly novel fold with no sequence/structure homolog and no
  reference ligand breaks target-ID, affinity-ranking, and scaffold transfer simultaneously. Advancing *this* frontier
  (the "dark proteome" case) is the deepest version of the vision.
- **Assets already in-house for the label-free path:** AutoDock Vina 1.2.7 + Open Babel (`docking` env), ESM-2/ESMFold
  via transformers, real target structures (LIT-PCBA `.mol2`), and the generate/admet/synth modules.

**The honest stress test we can run at zero budget:** a **target-level zero-data holdout** — take a target with a known
answer (e.g. SARS-CoV-2 Mpro), DELETE every inhibitor/label, and measure whether the homology-anchored label-free
pipeline recovers scientifically credible candidates from sequence alone. That is the vision's true benchmark, and it
is cheaply evaluable.

**Method mandate:** repeated deep literature review + first-principles reasoning + multiple *fundamentally different*
solution families before coding; optimize for long-term capability, not benchmark performance. (See memory
`north-star-zero-data-disease`.)

## The development PATH is not the destination (2026-07-31 refinement)
We cannot directly prove a system works on a disease that does not yet exist — science does not work that way. We
build confidence **progressively**, up a ladder. Known diseases are the **PROVING GROUND, not the destination**; each
success on a known disease increases confidence that the underlying scientific reasoning (not the memorized labels) is
correct.

**The confidence ladder:** (1) build each fundamental capability independently → (2) validate each on well-understood
diseases with reliable ground truth → (3) demonstrate the system solves MANY diverse known diseases across different
mechanisms/targets/classes → (4) **progressively remove information** to simulate the unknown: fewer labels → unseen
chemistry → unseen targets → temporal splits → cold-start → (5) solve diseases with NO disease-specific activity data →
(6) prospectively predict candidates before new experimental results are public → (7) validate experimentally where
possible → (8) only then claim rising confidence that the SAME system can respond to a future unknown disease.

This re-values the "information-removal" experiments as **rungs, not detours**: label-efficiency under scarcity (B65),
temporal/prospective splits, unseen-chemistry (NN<0.4), unseen-target holdouts are all steps 4–6 of the ladder — the
supporting-work label applies only to work that does NOT ladder toward the zero-data goal.

## The standard every major experiment must meet (answer before starting)
1. Which capability of the ultimate system does this improve? 2. Does it generalize beyond today's benchmark? 3. Will
it still matter for a disease humanity has never seen? 4. If it succeeds, does it increase confidence INTERCEPTA could
respond to a future pandemic faster/better than today's approaches? 5. If it fails, what fundamental assumption about
the system does it eliminate? — Choose experiments that strengthen the COMPLETE discovery system, not just one model.
**Long-term success = INTERCEPTA repeatedly takes a disease it was never trained on, reasons from first principles +
all computational evidence, generates scientifically credible candidates, and has them independently validated.** That
is the only metric that ultimately matters.

## Enduring intent (recovered from the founding docs) vs disposable architecture
The destination has been CONSTANT since the founding Universal Net Spec (2026-03-29): *"a universal computational engine
that, for ANY disease — past, present, or future — discovers novel drug molecules… The key word is ANY. This includes
diseases that do not yet exist."* The enduring PRINCIPLES (permanent): (1) **universality via extensibility** — Charter
law **U2: "no disease-specific code paths in the core engine; all disease-awareness through configuration"**; the system
must *compose many evidence types and absorb new capabilities/methods that do not exist yet* ("any disease becomes a
query against the net"; "we develop novel approaches when the vision demands it"); (2) **abstention as a first-class
output** — refuse/flag when the input is unlike anything known (epistemic vs aleatoric vs OOD); (3) **selectivity/safety
as a design constraint, not a final filter**; (4) **validation-first / self-improving** — reproduce known ground truth
before trusting novelty; every disease solved adds reusable knowledge; (5) the **Constitution** (truth over vision;
disposable everything-but-the-destination); (6) **CONTINUOUS KNOWLEDGE ABSORPTION — the system is LIVING, not a snapshot
(2026-07-31, Prasad).** It is not built *around* current knowledge; it is built to continuously absorb, on two
timescales: (a) EXTERNAL/FUTURE science — new databases, evidence types, and methods that do not exist yet plug in over
time; (b) SELF-GENERATED findings WHILE WORKING — every result it produces (predicted target, docking outcome, validated
hit, or NEGATIVE) becomes new evidence that improves both the current problem and every future one ("the net grows with
every query"). **GUARDRAIL (non-negotiable, or the self-improving loop becomes a self-deception loop):** all absorbed
knowledge is **provenance- and confidence-TIERED** — external-validated fact ≠ own-hypothesis ≠ own-reproduced-×2 result;
self-generated / low-tier records are QUARANTINED and down-weighted until they survive the falsification battery, never
treated as ground truth. Continuous absorption + falsify-first are the two halves that keep it honest (guards against the
curation-circularity + degree/popularity error-amplification the research flagged). DISPOSABLE (never defend): the 15-layer Neo4j Net, the 6 scouts, KAALCURA,
the RNA-velocity time-machine, the two-population ODE, cancer-first scoping — **and equally the current label-free /
homology / docking pipeline.** Docking, physics, ML, generative chemistry, knowledge graphs are candidate CAPABILITIES,
not the architecture.

## Capability map (2026-07-31) — what a universal any-disease system needs, and our HONEST status
Think in capabilities, held architecture-agnostically. Status: ✅ validated corner · ◑ partial · ✗ absent.
- **Foundational/cross-cutting:** extensible evidence substrate ("any disease → a query", U2) ✗ · uncertainty/abstention
  /applicability-domain ◑ (conformal+AD validated B30b) · continuous learning / evidence integration ✗ · **validation-
  first proving-ground methodology ✅ (our strongest asset: Constitution + prereg + reproduce×2 + information-removal ladder).**
- **Front half (disease → target) — the biggest gap:** disease understanding ✗ · mechanism inference ✗ · target
  identification + essentiality + selectivity ◑ (B34 genetic-evidence target-ID, not zero-data/homology yet).
- **Structure & binding:** structure-from-sequence when unknown ✗ (assets present, unused) · binding/interaction
  reasoning ◑ (C1: weak-but-real zero-data docking signal on Mpro).
- **Back half (target → candidate):** molecule generation ◑ (B33 optimization over known chemistry, not de novo) ·
  combination/synergy ✅ (generalizes to unseen combos of known drugs, 2 corpora) · multi-objective optimization ◑ ·
  ADMET/safety ✅ (B30, disease-agnostic → survives zero-data) · synthesizability ✅ (B31, disease-agnostic) ·
  experimental prioritization / active learning ◑ (B51; B65 bounded — acquisition *strategy* is not the lever).
- **Meta:** architecture extensibility (absorb capabilities/methods not yet invented) ✗ — a design principle to bake in.

**Recalibration verdict:** we have built strong BACK-HALF capabilities (score/generate a molecule against a GIVEN
target) and world-class *validation methodology*, but the vision's hardest and most-missing part — the **FRONT HALF
(disease → mechanism → target)** and the **extensible substrate** that makes "any disease becomes a query" real and lets
new capabilities plug in — is largely absent. That gap, not another molecule-scoring module, is where the leverage is.
Held loosely: the *principle* (extensible multi-evidence front-half reasoning) is enduring; its *implementation* (KG vs
retrieval-augmented reasoning vs tool-composition vs something new) is entirely open and to be chosen by evidence. The
substrate must be **LIVING** — append-only, provenance- and confidence-tiered — so both external/future science and the
system's OWN findings-while-working are continuously absorbed (principle 6), without ever letting unvalidated
self-generated records masquerade as ground truth.

## Zero-data arc — honest state (2026-08, consolidated in `papers/zero_data_discovery/REPORT.md`)
The first pass at the north star built + validated each capability on proving-ground pathogens, then mapped its honest
boundary: **target-ID** from sequence is dominated by generic conservation (~0.73 AUROC) — neither target-homology (TID1)
nor structural pocket druggability (TID2) beats it; the recipe is rank-by-conservation + host-nonhomology + calibrated
abstention. **Binding** carries a real-but-weak zero-data signal (C1; the GNINA rescoring lever is Linux/CUDA-only,
infeasible here). The pieces **compose end-to-end** from a proteome (E2E1, on M. tuberculosis, zero TB data → ranked
candidate *hypotheses*). The **self-improving loop** (principle 6) genuinely helps + is guarded by calibrated conformal
confidence WHERE the model has signal (SIL1, in-domain), but its benefit does NOT reliably cross to novel chemistry
(SIL2 — near-domain only). **Net honest position:** sequence-and-transfer-only discovery reaches pose-plausible,
conservation-ranked candidate HYPOTHESES with calibrated confidence and a self-improving loop that knows its limits; the
ceiling beyond is an INFORMATION ceiling (novel chemistry/targets) that needs NEW data — prospective/wet-lab/3D — to
cross, which is resource-gated, not a computation. Every claim traces to a pre-registered, reproduced-×2 experiment
(LEDGER.md). This bounds where in-silico reaches; it does not shrink the destination.

---

# INTERCEPTA — the fullest vision that is real (reconstructed 2026-07-29)

This replaces the original founding vision as the working charter. The original is not deleted — it is
*reconstructed* under the Constitution (truth over vision; pivot the vision when evidence demands). Written by
the CSO with full mandate. Every claim of "achievable" below is conditioned on a falsifiable gate, not hope.

## Why reconstruct
The original ultimate vision — "a universal computational engine that discovers novel drug molecules and
selects therapy for ANY disease" — has been tested against our own evidence and, in its most novel claims,
falsified or shown untestable (see LEDGER.md):
- Therapy-**selection** coordinate system: falsified at power (<5%).
- Novel coordinate beyond Ki67+TILs: falsified (it is known biology, better measured).
- **De novo** generative molecule design: was scaffold-hopping, not generation.
- "Any disease / universal" and "novel molecules": no evidence yet earns these.
Refusing to reconstruct would mean shipping claims we know are false. That is the one thing the Constitution
forbids absolutely. So we make the vision **bigger by making it true**, and we grow it only as far as evidence
carries it.

## The reconstructed fullest vision (one sentence)
> **A rigorously validated, mechanism-anchored cancer drug-response engine that earns each capability through a
> falsifiable milestone ladder — from verified cross-dataset drug-response transfer and verified mutation→drug
> mechanism, to genuine patient-level prediction, and, only if those hold, to calibrated clinical
> decision-support and mechanism-anchored drug *repurposing* ranking.**

Not "any disease, novel molecules, therapy selection" as a promise. Cancer-first, prediction-and-mechanism
first, and every outward expansion is a hypothesis that must survive the battery before it becomes a claim.

## What we KEEP (verified, real — the foundation, LEDGER V1–V7)
- A leakage-free cross-dataset cell-line drug-response signal (**ρ=+0.212**, reproduced ×2), with a clean
  reproducible engine (Constitution + prereg + sha256 + reproduce-×2 infrastructure).
- Verified, deconfounded, split-replicated **mutation→drug mechanism** in AML (NPM1→Cabozantinib,
  NRAS→MEK, DNMT3A→Dasatinib).
- A robust prognostic proliferation+immune model (known biology, honestly framed).

## What we CHANGE / REDO / RECONSTRUCT
| Original claim | Verdict | Reconstructed into |
|---|---|---|
| Therapy-**selection** coordinate | falsified at power | prognostic + **transfer** prediction (earn selection only with L2 data) |
| **De novo** generative design | scaffold-hopping | mechanism-anchored **repurposing / target ranking** (evidence-adjacent) |
| "**Any disease**, universal" | unevidenced | **cancer-first**; generalization is a later gate, not a premise |
| RNA-velocity "time machine" | untestable now | parked with exact missing-data spec; not in the build path |
| I-SPY2 "validated RCT" | over-claim | bounded reproduced association, stated as such |

## The milestone ladder — the vision's size = how far up we honestly climb
Each rung is a pre-registered, falsifiable experiment with the full battery (permutation, leakage, BH-FDR,
confound, external/independent replication). We do not narrate a rung as done until its metrics are committed
and reproduced ×2.

- **L0 — Engine + verified core.** [DONE] ρ=+0.212 (B1); ceiling confirmed (B2); AML mechanism verified.
- **L1 — Cell-line → PATIENT transfer.** [B3 DONE — PARTIAL] GDSC *array* map reaches real patients (diag
  ρ=+0.054, perm p=0.0005) but non-specific on the mismatched platform (diag≈off, p=0.12).
- **L1b — matched-platform, proliferation-independent drug-specificity.** [B3b + B3c DONE — PASS, replicated]
  Fixing the platform (train on DepMap **RNA-seq**) and residualizing proliferation reveals a **weak but
  genuinely drug-specific** cell-line→patient signal: prolif-residualized diag−off = +0.040, perm p=0.010
  (GDSC2 labels); **replicates with independent GDSC1 labels** +0.051, perm p=0.0015 (59 drugs). This is the
  first evidence in the program that the engine carries *drug-level* (not just proliferation) information into
  real patients. **Robust (B3d):** survives drug jackknife, bootstrap-over-drugs CI (excludes 0), and internal
  patient split-half. **But NOT mechanistically explained (B3e, pre-registered NULL):** the signal is not
  higher for AML driver-signaling drugs (RTK+ERK MAPK, MWU p=0.29) and does not track cell-line predictability
  (p=0.36) — B3d's exploratory "AML-relevant drugs transfer best" impression did not survive a rigorous test,
  so that coherence claim is withdrawn. **Caveats (honest):** effect small (ρ≈0.07–0.08); one patient cohort
  (BeatAML/AML); mechanism unexplained. Needs a SECOND patient cohort + other cancers for external validity
  (the next real gate).
- **L2 — Controlled clinical cohorts.** [B4, human-gated: dbGaP/EGA] Treatment×biomarker RCT designs to
  revisit the *selection* question with adequate power in non-ER / metastatic settings.
- **L3 — Calibrated decision support + repurposing ranking.** [conditional on L1 (and ideally L2)] A ranked,
  mechanism-anchored, uncertainty-calibrated output; pharma/clinical partnership for prospective test.
  **First evidence (B4/V10):** combining the verified mutation markers (V4–V6) with the expression transfer
  (V9) beats either alone — combined 5-fold CV Spearman > both single predictors in all 4 testable drug–marker
  pairs (e.g. sorafenib 0.469 vs marker 0.271 / transfer 0.383), transfer adds independently in 3/4 (BHq<5e-8).
  The mechanism-anchored engine is more than the sum of its verified parts. Bounded: DL meta null (p=0.21,
  heterogeneous — dasatinib transfer inverted), NPM1→cabozantinib untestable (no GDSC2 cabo), 4 pairs, one
  cohort → needs an independent patient cohort before this is "validated decision support."
- **L4 — Generalization beyond the first cancer(s).** [conditional on L1–L3] Only then is "broader disease"
  an evidenced direction, not a slogan.

## Honest probabilities (subjective, evidence-conditioned)
- Original ultimate vision as literally written (universal, de novo, selection): **<5%**.
- Reconstructed vision reaching **L1 (patient transfer real)**: unknown until B3 — that is exactly why B3 is
  next; prior ~30–50% for *some* significant drug-specific transfer given the +0.212 cell-line signal.
- Reconstructed vision reaching **L3 (calibrated decision support in cancer)**: real and fundable **conditional
  on L1 holding**; this is the honest "fullest vision" we build toward.

## The rule that makes this succeed
Success is defined as **a true engine that clinicians/pharma can trust**, not a big claim. We win by climbing
rungs that hold. If a rung fails, that failure is a first-class result and it re-sizes the vision honestly —
which is the only kind of success worth the years. Next action: run L1 (B3).

## Current frontier — the functional-inference arc, tested to the end (B12–B22, V15–V21)
The deepest honest finding of the whole program: **what transcriptomics transfers is proliferation/cancer-type,
not drug-specific vulnerability** — so baseline-expression drug prediction is intrinsically capped (and clinically
null under confound control, B10). We pivoted to a **functional** readout and pushed it all the way to
falsification (us-only, public + BeatAML + an independent cohort):
- **Functional gene-dependency (CRISPR) predicts drug response far better than baseline expression** (V15), is
  **learnable from expression** (V16), and on BeatAML ex-vivo the inferred layer **rescued** the actionable
  targets FLT3/BCL2/CDK9/AURKA (V17/V18) — inferred-FLT3-dependency even beat the FLT3-ITD biomarker
  (beyond-mutation, in ITD-wildtype patients, proliferation- and lineage-independent; V19/V20, robust B19).
- **But it FAILED external replication (B20/B21):** in an independent AML cohort (FIMM/Malani) the known
  FLT3-mutation→inhibitor biology replicated while our *inferred* refinement did not (pooled ρ=+0.05, p=0.08).
  A second baseline modality — proteomics — does not break the ceiling either (B22/V21): the limit is
  **modality-general.**
- **The corrected lesson (evidence-forced):** V19/V20 are **BeatAML-specific**, not a generalizable lead. No
  static/baseline profile (RNA or protein) resolves within-lineage drug specificity, and a functional layer
  *inferred from cell lines* does not transfer between patient cohorts.
**Reorientation:** the breakthrough requires **functional/perturbation response MEASURED in the patients
themselves** — not inferred. That is exactly what Track-1 measures (`docs/BREAKTHROUGH_ROADMAP.md`,
`prereg/TRACK1_SAP.md`). Honest and hard-won: the computational avenues on public data are now exhausted and
truthfully mapped, and the one real path left is prospective functional data — not a breakthrough yet, but a
credibly-earned direction.
