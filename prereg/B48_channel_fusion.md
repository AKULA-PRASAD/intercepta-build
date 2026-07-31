# Pre-registration — B48: does fusing the orthogonal channels beat the best single channel? (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the payoff; the new-information test of our integration ceiling)
Our integration negative-envelope (B32→B38) concluded "no fusion beats raw structure — the bottleneck is INFORMATION,
not representation." But that study never had a genuinely new information source. B47 just added one: a **structure-based
docking channel**, shown orthogonal to the ligand channel (Spearman 0.27). B48 is the decisive test: does fusing the
**ligand-based QSAR** channel with the **structure-based docking** channel (and ligand-similarity) beat the **best
single channel**? A YES is the program's first genuine "whole > parts" win, driven by new information; a NO extends the
negative envelope even to orthogonal structural information — either is first-class.

## Data (OPEN; LIT-PCBA, cached; same targets/ligands as B47 for consistency)
3 targets with co-crystal receptors: FEN1, MAPK1, ESR1_ant. Per target, the **identical** seeded eval set as B47
(60 actives + 120 decoys, random_state=42). QSAR training uses that target's OTHER actives + a seeded inactive sample
(≤8,000), with the eval ligands **held out** (leakage control).

## Method (docking env: rdkit 2025.09.5 + vina 1.2.7 + sklearn 1.9.0; deterministic)
Three per-ligand channels on the eval set:
1. **Ligand-QSAR (supervised, strongest):** `admet._TaskModel` (Morgan2048+physchem, roc-auc) trained on
   (all target actives − eval actives) + (≤8,000 inactive sample − eval decoys); predict the eval ligands. Record each
   eval ligand's cross-set NN-Tanimoto to the QSAR training set (for the novel<0.4 lens).
2. **Ligand-similarity (unsupervised):** max ECFP4 Tanimoto to the co-crystal ligand(s).
3. **Structure-docking:** AutoDock Vina (seed=42, cpu=8, exhaustiveness 8) score = −affinity (as B47).
**Fusion (primary):** leakage-controlled logistic regression over the 3 channel scores, evaluated by **3-fold
Bemis–Murcko scaffold-CV out-of-fold** on the eval set (no ligand contributes to its own fusion weight). **Secondary:**
parameter-free mean-percentile-rank fusion. **Metrics (rdkit.ML.Scoring):** AUROC + EF@5% for each single channel and
each fusion, on the full eval set AND the novel<0.4 (NN-Tanimoto to QSAR train) subset.

## Hypotheses (pre-registered)
- **H1 (whole > parts — the payoff):** panel-mean AUROC of the primary (logistic) fusion exceeds the panel-mean AUROC
  of the **best single channel** by **≥ +0.02** on the full eval set. (If TRUE: new structural information breaks the
  integration ceiling — the program's first fusion win. If FALSE: the ceiling holds even with orthogonal 3D info.)
- **H2 (holds on novel chemistry):** on the novel<0.4 subset, fusion AUROC ≥ best-single AUROC (not similarity-driven).
- **Reported regardless:** per-target and panel AUROC/EF for QSAR / ligsim / docking / logistic-fusion / rank-fusion,
  full and novel; the ΔAUROC(fusion − best single); and which channel is best per target.

## Honesty / scope
Retrospective, in-silico, 3 targets, subsampled eval set — AUROC is the fair metric. Fusion is leakage-controlled via
scaffold-CV OOF; the logistic is fit on only 3 features so overfitting risk is low but the small n is a caveat. Docking
is a heuristic score (rigid receptor, obabel prep). Enrichment ≠ proven activity; not wet-lab; no SOTA claim. A NULL
result (no fusion gain) is expected-allowed and reported as first-class, consistent with B32→B38.

## Reproducibility
Deterministic: QSAR seed=42, Vina seed=42/cpu=8 (verified), scaffold-CV folds fixed [1,2,3], seeded eval subsample (42).
Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B48_channel_fusion/results/B48_metrics.json`. Env: `docking`; INTERCEPTA_DATA owned path.
