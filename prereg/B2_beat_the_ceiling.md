# Pre-registration — B2: can verified biology beat the +0.212 ceiling? (FINALIZED 2026-07-29, pre-run)

## Question
Does adding **verified biology** to the B1 transcriptome-only model raise STRICT cross-dataset per-drug
Spearman ρ above the ceiling (+0.212)? Two additions, each a separately verified signal:
(R) the frozen proliferation axis R_prolif as a feature; (M) somatic non-silent driver-gene mutation
indicators. Or is +0.212 the real ceiling of public cell-line generalization?

## Hypothesis (assumed FALSE until it survives)
- H1_R: expression + R_prolif beats Arm 0 by Δρ ≥ +0.02, paired Wilcoxon p<0.05.
- H1_M: expression + driver mutations beats its matched control by Δρ ≥ +0.02, paired Wilcoxon p<0.05.
- H0: neither addition beats transcriptome-only; +0.212 stands.

## Data
B1 inputs + DepMap MAF `depmap_mut_try1.csv` (sha256 in data/MANIFEST.md). Non-silent = {Missense, Nonsense,
Frame_Shift_Del/Ins, Splice_Site, In_Frame_Del/Ins, Nonstop, Start_Codon_SNP, De_novo_Start_OutOfFrame};
Silent/Intron excluded. All public.

## Design (locked)
Same STRICT disjoint-cell-line, per-drug RidgeCV protocol and 100-drug set as B1.
- **Arm 0** — control: top-2000 z-expression genes (= B1 ceiling).
- **Arm R** — Arm 0 features + R_prolif (frozen, appended as one z-scored feature).
- **Arm M** — Arm 0 features + K=50 binary damaging-mutation columns. To avoid a missing-data confound, Arm M
  is restricted to cells with a DepMap mutation profile, and its control (**Arm 0M**) is recomputed on that
  SAME restricted cell/drug set → the paired comparison is Arm M vs Arm 0M (never vs the full-set +0.212).
  The 50 genes are the most frequently mutated among each drug's TRAINING cells only (data-driven,
  drug-agnostic within a drug, computed on train → no test leakage, no manual panel DOF).

## Baselines / the bar
Arm 0 = +0.212 (Arm R compared to it). Arm 0M = matched-subset control (Arm M compared to it). LEAKY design
not re-reported.

## Primary metric + decision rule (fixed in advance)
Per arm: STRICT mean per-drug ρ, and paired Wilcoxon of per-drug ρ vs its matched control. An arm is a
**candidate PASS** iff Δρ ≥ +0.02 AND Wilcoxon p<0.05 after **BH-FDR** across the 2 arms.

## Falsification battery (all required for a POSITIVE — not just a candidate PASS)
1. BH-FDR across arms (above).
2. Leakage audit: mutation panel selected on training cells only; test cells never seen in feature selection.
3. **External replication (GATE): a candidate PASS is only called real if the gain also replicates on
   GDSC1 → CCLE/PRISM** (same protocol, GDSC1_fitted_dose_response.xlsx). A gain that does not replicate
   externally is logged PROVISIONAL/failed, NOT a result. If NO arm is a candidate PASS, external replication
   is moot and B2 is recorded as a well-powered null → +0.212 confirmed as the public-data ceiling.

## Honest prior
R_prolif's ~15 genes are already inside the 2000-gene expression matrix → Arm R almost certainly null.
Mutations are sparse and test n≈20/drug → Arm M likely weak. Prior that any arm beats the ceiling: ~20–30%.
A null here is a first-class result and the expected one.

## Reproducibility
Ridge closed-form; mutation-frequency ranking deterministic (stable sort, gene-name tiebreak). Reproduce ×2 =
identical metrics JSON (timestamp aside). Output: `experiments/B2_beat_ceiling/results/B2_metrics.json`.

## Amendments
- 2026-07-29 (pre-run): dropped the exploratory ElasticNet-vs-Ridge arm from the B1 draft (ElasticNetCV
  runtime intractable on this laptop; a modeling-form question, not "verified biology") → deferred to a
  separate prereg. Arms locked to {0, R, M}. No results seen at time of this amendment.
