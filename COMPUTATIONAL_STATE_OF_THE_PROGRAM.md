# COMPUTATIONAL_STATE_OF_THE_PROGRAM.md
*What is objectively known today, verified from code/results (not from prior reviews). Objective:
maximize the probability that the ultimate vision — "effective drugs for any disease with minimal
experimental data" — becomes **computationally** achievable. Assumes no wet lab exists. Evidence is
cited to result files / ledger rows; where code and prose disagree, code wins.*

## The single unifying finding (the whole program reduces to this)
Every frontier failure in this repository is the **same failure**: inability to predict biological
function **beyond the manifold spanned by conserved invariants and training-set neighborhoods.** The
program's own name for it is the **transfer-condition principle** — a label-free signal transfers only
as far as the biological invariant it rides on is conserved. Read as a computational statement, this is a
**no-free-lunch result for zero-data biology: you cannot extract information the available data does not
contain**, and label-free / public data contains *conservation + structure + known-target neighborhoods*,
**not** novel-target efficacy. Three independent, code-verified instances of the identical wall:

1. **Target-ID beyond metabolism — CLOSED (information wall).** Own-sequence-conservation breadth reaches
   AUROC **0.9078** on the FBA-blind essential proteome, and **no** homology-independent signal beats it by
   the +0.03 pre-registered margin: PLMESS1 Δ**+0.0082**, NONMET1 Δ**+0.021**, REGNET1 Δ**−0.0056**,
   MULTISIG1 ensemble ~0.908, PLMSTRUCT1 (structure-aware) Δ**+0.008** *(all from the result JSONs;
   `experiments/{PLMESS1,NONMET1,REGNET1,MULTISIG1}/results/*.json`)*. Six signal classes, one ceiling.
2. **Novel-target / novel-chemotype affinity — UNSOLVED (extrapolation wall).** Docking AUROC **0.428**
   (worse than chance, `HIT2/results`); QSAR analog-driven, novel-chemotype **0.90→0.67** (`HIT1`);
   PCM ligand-driven, protein features add nothing (`B49`); active-learning label-efficiency collapses on
   novel chemistry (`B65`); SOTA co-folding (Boltz-2) on the one runnable benchmark was **training-leaked**
   and **novel-split n=5 ≈ 0.52** (`AFFINITY1`, verified from `results/scored.csv`).
3. **Human single-agent drug-response — CLOSED (information wall).** Cross-dataset transfer ceiling
   ρ**+0.212**; within-cancer clinical AUROC **0.504** (p=0.43); an inferred functional layer **fails
   external replication** (`ENG §2.1/2.7/2.8`). The drug-specific-response information is **not in baseline
   molecular profiles**.

## What is computationally ACHIEVABLE today (the conserved-invariant subset)
- **Zero-data TARGET identification for pathogens with an adequate metabolic model.** FBA gene-essentiality
  is enriched for *experimental* knockout essentiality: E. coli OR **64.3** (p 3.1e-24), held-out WHO
  pathogens OR 13–63, 6 GEMs OR 4.3–45, analyst-blind 4/7 novel organisms (`VALIDATE_essentiality`,
  `CROSSVAL`, `BLIND1-7`). **Caveat (code):** binary *enrichment* only — precision 0.77, **recall 0.22**,
  continuous ranking AUROC **0.63**; it finds *some* real targets and misses most. Not "the target list."
- **Structural target-class ID for viruses** where sequence homology fails (`GENERALIZE3/HARDENV1`).
- **Honest ABSTENTION** where no validated invariant applies (`COMPOSITE*/CAPSTONE*/DARK1`) — coverage, not a
  universal model.
- **A base-rate-fair transfer gate** (`FAIRGATE1/META1`): the naïve OR>3 gate is base-rate-confounded (flips
  on the same GEM); the risk-ratio gate is the correct primitive. This is the program's one genuine method.

## What is NOT computationally achievable on today's data (proven walls, above)
The **molecule half** ("effective drug", not just a target) for novel targets; **non-metabolic mechanism**;
**drug-specific human response**; and therefore **"any disease"** — only the conserved-invariant subset is reachable.

## The decisive reframe of the vision's feasibility
The binding constraint is **information, not compute.** More GPU-hours on the *same paradigms and the same
public data* cannot create signal the data lacks — the repo has demonstrated this six independent ways. The
achievable frontier therefore **grows with the world's public experimental data** (deep mutational scans,
perturbation atlases, structural genomics, activity databases), **not** with our compute. Consequence:
- **Achievable now, computationally:** zero-data *target prioritization* for conserved-invariant disease
  subsets, with calibrated abstention. **[F]**
- **Not achievable by our compute on today's data:** end-to-end "effective drug for any disease." **[F, from the walls]**
- **Not proven eternally impossible:** as public functional data accumulates, the reachable subset expands.
  The vision is **data-asymptotic, not compute-solvable.** **[Inference from the transfer-condition principle]**

## Integrity status (must accompany any state claim)
The repo documents (and removed) prior **fabricated artifacts** (`INTEGRITY_SWEEP.md`, `docs/audits/VISION_AUDIT.txt`:
"9 fake claims", 10% of 92 requirements). Trust only post-Constitution, pre-registered, reproduced-×2 results;
this document relies only on those + independently re-verified numbers.

---
## UPDATE 2026-08-10 — a FOURTH code-verified wall: durability falsified at scale
DYNAMICS5 (reproduced ×2, sha `caea6b90`; `experiments/DYNAMICS5_resistance_site_entropy/results/`) tested the
DYNAMICS1 durability premise at proper power: n=198 targets, **1,143** CARD-documented resistance positions,
within-protein paired design (each protein its own control). **Result: masked-PLM entropy does NOT mark
resistance sites** — one-sided Wilcoxon p=**0.99997** (opposite direction), mean ΔH=**−0.22**, positive-fraction
**0.41** (<0.5), position-level AUROC **0.446** (below chance), clustered-permutation p=**1.0**; verdict **CEILING**.
DYNAMICS1's n=15 AUROC 0.84 was a small-n artifact and did not survive powering. **Consequence:** the program's
one remaining "live positive" is now falsified; the surviving computational positives are ONLY (a) conserved-
invariant target-ID enrichment and (b) the base-rate-fair gate (FAIRGATE1). This is a fourth instance of the
same information wall — even the durability axis, properly powered, is chance. It also *vindicates the rigor*:
a within-protein powered test overturned an underpowered positive, exactly as it should.
