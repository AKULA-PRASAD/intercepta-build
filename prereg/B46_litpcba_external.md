# Pre-registration — B46: our ligand-based channel on the unbiased LIT-PCBA benchmark (FINALIZED 2026-07-30, PRE-RESULT)

## Why (honest external footing; "bar before boast" on a community benchmark)
So far our enrichment is on TDC HTS targets with our own splits. LIT-PCBA (Tran-Nguyen et al., JCIM 2020) is the
community's **unbiased** virtual-screening benchmark: 15 targets, realistic 1:1000–1:20000 active:inactive ratios,
built so that no single method (2D fingerprint / 3D shape / docking) trivially wins. B46 evaluates INTERCEPTA's
ligand-based QSAR channel here, under our honest NN<0.4 novel-chemistry lens (B45), and reports the numbers **in the
context of published baselines** — expecting MODEST results, because that is the honest reality of unbiased data.

## Data (OPEN; LIT-PCBA full_data, cached at $INTERCEPTA_DATA/lit_pcba; MANIFEST logged, sha 93467a5b)
Per target: `actives.smi`, `inactives.smi` (SMILES + PubChem CID). Preprocessing (fixed a priori): take the largest
organic fragment, canonicalize (RDKit), **drop cross-label duplicates** (a canonical SMILES appearing as both active
and inactive is removed from both — leakage control) and within-set duplicates. Extreme inactive counts → a **seeded
inactive subsample (≤8,000; random_state=42)** per target to bound memory/runtime; documented, and AUROC (the
ratio-independent metric) is the primary comparison. Targets with **<60 actives** after cleaning are **reported as
skipped** (ADRB2 17, ESR1_ago 13, IDH1 39, OPRK1 24, PPARG 24) — too few for a supervised scaffold split; not forced.

## Method (identical model + honest lens to B43/B45)
For each evaluable target: featurize (Morgan2048+physchem); **Bemis–Murcko scaffold split ×3**; train `admet._TaskModel`
(roc-auc) on train, score test. Report **AUROC, BEDROC(α=80.5), EF@1%, EF@5%** (rdkit.ML.Scoring) on the full test,
and — applying the B45 lens — the **novel-chemistry (cross-set NN-Tanimoto to train < 0.40) AUROC**. Also report the
mean cross-set NN-Tanimoto (leakage indicator).

## Metrics & aggregate
Per target: AUROC, BEDROC, EF@1%, EF@5% (mean over 3 seeds), novel<0.4 AUROC, mean NN-Tanimoto, n_actives.
Panel (evaluable targets): median & mean full-test AUROC; number with AUROC>0.70; panel-mean novel<0.4 AUROC;
median EF@1% (reported at our subsampled ratio, explicitly NOT directly comparable to full-ratio published EF).

## Published context (for honest comparison, not re-run here)
LIT-PCBA is hard: published median EF@1% ≈ Vina docking 0.9, GNINA ≈2.1, best supervised ML ≈4–5 (arXiv:2605.01681);
the original paper's 2D-fingerprint/3D-shape/docking baselines enrich the top 1% by ≥2× on at least one method per
target by construction. We compare our AUROC/EF to this published envelope and state plainly where we land.

## Hypotheses (pre-registered; modest & honest)
- **H1 (we enrich on unbiased external data):** on the evaluable targets, **median full-test AUROC > 0.70** AND
  **≥6 targets with AUROC > 0.70**. (If FALSE: our ligand-based channel does not transfer to the unbiased benchmark —
  a first-class negative, reported honestly.)
- **H2 (survives to novel chemistry):** panel-mean novel(NN<0.4) AUROC **> 0.60** (enrichment is not purely
  analog-memorization on this benchmark either).
- **Reported regardless:** per-target AUROC/EF and where we sit vs the published LIT-PCBA baseline envelope.

## Honesty / scope
Retrospective, in-silico, real-actives-vs-decoys on an unbiased public benchmark. Inactive subsampling makes EF
ratio-dependent (AUROC is the fair metric). Decoys are assay-inactives (not property-matched — LIT-PCBA design).
Enrichment ≠ proven activity; not wet-lab. Skipped low-active targets are stated, not hidden. No SOTA claim — an
honest placement of our channel on the community benchmark.

## Reproducibility
Deterministic: seed=42 (model + inactive subsample), scaffold seeds fixed [1,2,3]. Reproduce ×2 byte-identical
(payload sha256 over summary+per-target). Output: `experiments/B46_litpcba_external/results/B46_metrics.json`.
Env: intercepta-build; INTERCEPTA_DATA owned path.
