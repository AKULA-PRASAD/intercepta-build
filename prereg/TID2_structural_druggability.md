# TID2 — Does INTRINSIC structural pocket druggability add target signal BEYOND sequence conservation? (finalized 2026-07-31, PRE-RESULT)

(TID2 = Target-IDentification chapter 2; a NEW ADAPTER on the TID1 living substrate — extensibility in action.)

## Vision alignment (front-half; the filter, answered)
Directly attacks the boundary TID1 exposed: homology-to-known-targets ≈ generic conservation (druggability AUROC 0.64 <
conservation null 0.72). TID2 tests the ONE signal the 4-paradigm investigation found genuinely ORTHOGONAL to
conservation: **intrinsic pocket druggability scored on the protein's OWN predicted structure** (conservation-free by
construction). Zero-data-native (structure predicted from sequence; AlphaFold DB), disease-agnostic, a new adapter on the
same substrate. Q5: a NULL (structure doesn't add beyond conservation) is first-class — it would bound structural
target-ID and force mechanistic capabilities.

## Phase-0 provenance (4 threads → this selection)
Investigation verdict: more HOMOLOGY — structural (Foldseek) or learned (ESM-2 embeddings) — mostly RE-ENCODES the
conservation null; mechanistic essentiality (GEM/FBA) is reconstruction-fragile + blind to non-metabolic targets, its
orthogonal part being host-nonhomology (a selectivity constraint, not a druggability score — TID1 confirmed naive
subtraction hurts). The genuinely orthogonal, feasible, and scientifically OPEN signal is **intrinsic pocket geometry**:
structure-based druggability is established as *complementary* to sequence (DrugPred: structure & sequence target calls
overlap little), but **no published study does the clean test — does it BEAT a conservation null on leave-organism-out
target-ID?** That gap is what our rigor fills.

## Data (OPEN, feasibility-verified 2026-07-31)
- **Structures:** AlphaFold DB **v6** per-accession models (`https://alphafold.ebi.ac.uk/files/AF-{ACC}-F1-model_v6.pdb`,
  HTTP 200 verified for all 4 organisms; free). Cached + MANIFEST'd; NO folding needed.
- **Panel + ground truth:** SAME as TID1 — 4 pathogens (M.tuberculosis, E.coli, P.aeruginosa, P.falciparum); positives =
  UniProt ChEMBL-xref drug targets (131/182/46/52). Evaluation set per organism (for compute tractability): ALL targets +
  a seeded sample of ~400 non-targets (fpocket on the full ~20k-protein panel is unnecessary for enrichment estimation).
- **Tool:** fpocket 4.2.3 (conda-forge, in the isolated `bioinfo` env; C, no Java). P2Rank deferred (needs a Java runtime)
  — a clean future second adapter. mmseqs2 (TID1) for the conservation scores.

## Design — structural-druggability adapter + the decisive conservation-conditioned test
Per protein in the evaluation set: fetch AF v6 structure → **fpocket → max "Druggability Score" across pockets** (the
conservation-free geometric signal; proteins with no structure/pocket → score 0 + abstain flag). Compute, on the SAME
proteins, the TID1 signals via mmseqs2 (leave-organism-out): **conservation-transfer** (best bits to other orgs' drug
targets) and the **CONSERVATION NULL** (best bits to other orgs' FULL proteomes).

## Metrics (leave-organism-out; per organism + panel; positives-only → precision@k + AUROC + enrichment)
- **AUROC / precision@k / enrichment** of: (i) conservation null, (ii) structural druggability (fpocket), (iii) their
  combination, on recovery of known targets.
- **DECISIVE — residual after partialling out conservation:** logistic regression `is_target ~ conservation_null +
  structural_druggability`; test whether the structural coefficient is significant AND the model's AUROC exceeds a
  conservation-only model (nested ΔAUROC). Only residual lift is genuine new signal (guards the positives-are-conserved
  circularity).
- **Nulls/controls:** degree/length null (protein length); random. Abstention rate + precision-on-abstained-vs-predicted.

## Hypotheses (pre-registered)
- **H1 (structural beats conservation null):** panel-median structural-druggability AUROC > conservation-null AUROC (and
  precision@k >).
- **H2 (DECISIVE — orthogonal signal):** structural druggability retains a **significant conditional effect after
  partialling out conservation** (positive structural coefficient; nested ΔAUROC > 0 over conservation-only) → genuine
  beyond-conservation signal.
- **H3 (combination helps):** conservation + structural combined beats conservation alone (ΔAUROC > 0 at matched recall).
- **H4 (abstention calibrated):** proteins with no confident pocket have lower target-rate than scored ones.
- **H0 (first-class):** structural druggability adds NO significant signal beyond conservation (H2 fails) → structural
  target-ID is capped at the conservation ceiling (low specificity / re-labeled conservation); bounds the capability and
  forces mechanistic signals. Honest, expected-allowed.

## Honesty / scope
Retrospective recovery of KNOWN targets (proving ground). fpocket druggability model trained on CRYSTAL structures →
apply to apo AlphaFold models (a stated approximation; apo pockets are more closed). **Static structures miss ~40% of
cryptic/allosteric pockets → a SYSTEMATIC bias against allosteric targets, not random noise (stated).** Evaluation set =
targets + seeded non-target sample (not full proteome). Leave-ORGANISM-out (leave-superfamily/cluster-out is the ideal
against family leakage — noted as a limitation + future hardening). Positives are conserved/well-studied → the
residual-AUROC (H2) test is the circularity guard. fpocket only (P2Rank/MD deferred). Not wet-lab.

## Reproducibility
Deterministic (fpocket geometric + deterministic; mmseqs fixed params; non-target sample seed=42; cached AF structures
w/ sha256). Reproduce ×2 byte-identical (payload over per-organism metrics + per-protein scores). Output:
`experiments/TID2_structural_druggability/results/TID2_metrics.json`. Envs: `bioinfo` (fpocket 4.2.3, mmseqs2 18),
`intercepta-build` (analysis). Feasibility-gated: (1) tools verified ✓; (2) fetch AF structures for the eval set (cache +
MANIFEST); (3) smoke-test fpocket parsing on ~10 proteins before the full run (B63 no-blind-run lesson).
