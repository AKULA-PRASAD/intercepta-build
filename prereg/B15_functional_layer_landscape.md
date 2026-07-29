# Pre-registration — B15: how broadly does the functional-inference layer rescue drug prediction? (FINALIZED 2026-07-29, PRE-RESULT)

## Rationale
B14/V17: for FLT3 inhibitors and venetoclax, expression→inferred-dependency predicts BeatAML ex-vivo response
where the direct transfer fails. Is this a broad principle (targeted/oncogene-addicted agents) or specific to
FLT3/BCL2? B15 maps it systematically across ALL actionable BeatAML drugs with a clean primary target — to learn
WHERE the functional layer helps and where it doesn't. Honest generalization, not cherry-picking.

## Pre-declared drug → primary target gene (established pharmacology; frozen before results)
FLT3: sorafenib, quizartinib, gilteritinib, crenolanib, kw-2449, dovitinib, tandutinib, midostaurin.
BCL2: venetoclax. BTK: ibrutinib. SYK: entospletinib, prt062607. JAK: ruxolitinib(JAK2), tofacitinib(JAK1).
MEK(MAP2K1): trametinib, selumetinib. MET: crizotinib, foretinib. EGFR: erlotinib, gefitinib, afatinib.
ABL1: nilotinib, dasatinib, ponatinib, imatinib. KIT: sunitinib. KDR: axitinib, cediranib. AURKA: alisertib.
XPO1: selinexor. CDK9: sns-032, flavopiridol(alvocidib). ERBB2: lapatinib.
(Only tested where: target∈CRISPR, expr→dep learnable [CV ρ≥0.15], drug in BeatAML with ≥15 patients.)

## Method (identical to B14)
Train expr→dependency(target) on DepMap; apply to BeatAML RNA → inferred dependency per patient. Per drug:
Spearman(inferred-dep, ex-vivo AUC) and Spearman(direct engine transfer, AUC), both proliferation-residualized.

## Hypotheses (assumed FALSE)
- **H1 (broad rescue):** pooled across the actionable-target set, |ρ(inferred-dep)| > |ρ(direct transfer)|,
  paired permutation p<0.05 (the functional layer helps broadly, not just FLT3/BCL2).
- **Per-drug "rescued":** inferred-dep ρ significant (BH<0.05, correct direction) AND |inferred| > |direct|.
- H0: no broad advantage; the rescue is confined to a few targets (still reported — it maps the landscape).

## Decision rule (fixed)
Pooled paired |ρ_inferred| vs |ρ_direct| across all tested drugs, sign-flip permutation (k=2000, seed=42), BH per
drug on inferred-dep one-sided p. Report the full landscape: which target classes are rescued, which aren't.

## Interpretation (fixed)
- H1 pass → the functional-inference layer is a BROAD advance for actionable targets (major, honest, translatable).
- H1 fail but a coherent subset rescued → the layer helps specifically for strong-addiction targets (FLT3/BCL2/…)
  — a precise, honest, clinically-actionable map (still valuable; guides Track-1 drug panel).
- Null everywhere → V17 was fragile; honest bound.

## Honesty / scope
BeatAML ex-vivo (AML). dep̂ trained on pan-cancer DepMap. Multi-target drugs mapped to primary target (noise
source, stated). No cherry-picking: the full pre-declared set is tested and reported, wins AND nulls.

## Reproducibility
Deterministic (seed=42, k=2000); reproduce ×2. Output: experiments/B15_functional_landscape/results/B15_metrics.json.
