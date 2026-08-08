# MODALITY1 — Intervention-Modality Recommender (cross-class, fail-safe) — SUMMARY

**Verdict: PASS** — a validated cross-class intervention-modality recommender arm for the INTERVENTION half. Reproduced x2 byte-identical (payload sha256 `57b85479e2e72bf1e6c1020242a278b378f32aa5c878c8556c37a7228f492eac`).

## What this is
A mechanism-first, **fail-safe** recommender that, from OBJECTIVE target/disease features alone — subcellular **localization** (UniProt), disease **mechanism**, protein-class **druggability**, causal-gene-vs-downstream — recommends a credible intervention MODALITY over the full taxonomy: SMALL_MOLECULE_INHIBITOR, SMALL_MOLECULE_ACTIVATOR/CHAPERONE, MONOCLONAL_ANTIBODY/BIOLOGIC, ASO/siRNA, ENZYME/PROTEIN_REPLACEMENT, GENE_THERAPY, or ABSTAIN. Generalizes MENDEL1 (germline-monogenic, 3 SM-centric modes) to 6 modalities across monogenic / cancer / autoimmune / cardiometabolic / neuro / ophthalmic / hematologic disease.

## Ground truth (cited, n=43, no fabricated triple)
Every row is a REAL (target, disease, mechanism, APPROVED modality) fact from an FDA/EMA approval or landmark trial (several PubMed-verified during assembly). Modality balance: SM_INHIBITOR 8, ANTIBODY 7, ASO/siRNA 7, ENZYME/PROTEIN_REPLACEMENT 7, SM_ACTIVATOR 6, GENE_THERAPY 6, ABSTAIN 2. Multi-modality targets (a real phenomenon) carry the landmark modality as truth and list alternatives in `also_feasible`.

## Pre-registered gates and results
- **G1 — top-modality accuracy >= 0.386 (majority 0.186 + 0.20): PASS.** Accuracy **0.814 (35/43)**, balanced accuracy 0.830. Beats majority by **+0.628** and the mechanism-only ablation (0.558) by +0.256. Perfect recall on SM_INHIBITOR, SM_ACTIVATOR, ENZYME/PROTEIN_REPLACEMENT, ABSTAIN; 0.857 antibody; 0.667 gene therapy; **0.286 ASO/siRNA** (honest weak spot).
- **G2 — FAIL-SAFE (hard): PASS.** **0/43** infeasible confident recommendations. All 8 misses are SAFE (predicted modality is itself feasible / a real co-approved alternative, or a conservative ABSTENTION). Zero unsafe misses. No SM-for-secreted-deficiency, no antibody-for-intracellular, no ERT-for-gain-of-function, no gene-addition-for-dominant-toxic ever emitted.
- **G3 — localization is load-bearing: PASS.** The mechanism-only (localization-blind) ablation commits **5 infeasible recommendations** (enzyme replacement for intracellular/CNS targets RPE65, DDC, HBB_betathal, HEXA, ARSA); adding localization drives it to **0**. The composed localization feature — not the mechanism restatement — is what makes the recommender fail-safe.

## Load-bearing finding (not a tautology)
Modality feasibility is set by **mechanism x localization**, not by structural druggability. Supplementary cross-check (MENDEL1 fpocket AlphaFold-v6 cache, 21 overlapping targets): fpocket pocket score separates SM vs non-SM modalities at **AUROC 0.579** — near chance — replicating MENDEL1's G3 negative at the modality level.

## Honest negative / boundary (first-class)
The clean failure mode is the **ASO/siRNA class (recall 0.286)**: RNA-therapy is rarely UNIQUELY feature-determined — for over-abundant secreted targets (APOB, APOC3) an antibody is co-feasible; for druggable over-active intracellular enzymes (ALAS1, HAO1) a SM inhibitor is co-feasible; the recommender predicts those co-feasible alternatives (all SAFE) and misses that RNA-lowering was the historical choice. Honest bound: **the recommender delivers FEASIBILITY (never an infeasible rec), not perfect pinpointing of the single historical modality among co-feasible options.**

## Scope (binds every claim)
Recommends a MODALITY CLASS, not a molecule; the SMALL_MOLECULE branch still hits the affinity wall (AFFINITY1/HIT2/B49/B65); triage-not-therapy; in-silico; n=43 cited seed; `causal_node` uniform here (downstream-node reasoning is MENDEL1's). Contribution = fail-safe feasibility triage + honest abstention, not new pharmacology. Reproduce x2 byte-identical.

## LEDGER verdict (one line)
**MODALITY1 (PASS): a cross-class, mechanism+localization-first intervention-MODALITY recommender — top-modality accuracy 0.814 vs 0.186 baseline, 0/43 infeasible confident recommendations (hard fail-safe holds; localization enforces it, proven by a 5->0 ablation), with an honest first-class negative that RNA-therapy is not uniquely feature-determined among co-feasible modalities; recommends a modality CLASS not a molecule (SM branch still hits the affinity wall); reproduced x2 byte-identical sha 57b85479.**
