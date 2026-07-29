# Pre-registration — B27: does LINCS signature-reversal (connectivity) predict drug efficacy? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (genuinely-new direction; open data; just us)
Connectivity-Map / LINCS repurposing hypothesis: a drug that **reverses** a cell's expression state (down-regulates
what the cell has up, and vice versa) should be more effective in that cell. We test the decisive, falsifiable
version against efficacy data we hold: **within a cell line, does signature-reversal rank drugs by sensitivity
better than chance?** (the repurposing use case: given a tumor's expression, does "reverse my signature" pick
effective drugs). Honest prior: connectivity→efficacy is historically weak/mixed; a null or small effect is
expected and first-class.

## Data (OPEN; downloaded by us)
- LINCS L1000 consensus drug signatures: dhimmel/lincs v2.0 (Zenodo 47223), 1,170 DrugBank compounds × 7,467 genes
  (consensus z-scores). DrugBank-ID→name via dhimmel/drugbank slim (GitHub). Gene Entrez→symbol via genes.tsv.
- Efficacy: PRISM secondary screen AUC (DepMap cell lines) — 239 drugs overlap LINCS∩PRISM by name.
- Cell state: DepMap expression, z-scored per gene across cell lines (each cell's deviation from the panel mean).
- Genes: intersection of L1000 signature genes and DepMap expression symbols.

## Reversal / connectivity score
For drug d and cell c over shared genes G: standardize each drug signature (across genes) and each cell state
(across genes); **reversal(d,c) = − Pearson(drug_sig_d, cell_state_c)** (high = drug opposes the cell's up/down
program). Efficacy oriented as **sensitivity = −AUC** (higher = more sensitive).

## Hypotheses (assumed FALSE)
- **H1 (repurposing — within-cell):** within each cell line, Spearman(reversal, sensitivity) across the ~239 drugs
  is > 0, pooled (sample-size-weighted Fisher-z) across cells, with a within-cell drug-label permutation null
  (≥2,000) p<0.05.
- **H2 (within-drug):** within each drug, Spearman(reversal, sensitivity) across cells is > 0, pooled across drugs.
- **H3 (robustness, only if H1/H2 positive):** the effect survives excluding proliferation/cell-cycle genes and
  within-cancer-type stratification (not a proliferation/lineage confound).
- H0: reversal does not predict sensitivity beyond chance → connectivity-based repurposing does not work on this
  data (honest negative, consistent with the mixed literature).

## Decision rule & interpretation (fixed)
- **H1 (and/or H2) PASS + H3 holds** → signature-reversal genuinely predicts efficacy, proliferation/lineage-
  independent → a real (if modest) repurposing signal; report effect size honestly (expected small).
- **H1/H2 PASS but H3 fails** → the "signal" is proliferation/lineage confounding (drugs that hit fast-growing
  cells), not true connectivity — honest bound.
- **H1/H2 FAIL** → connectivity-based repurposing does not predict efficacy here — first-class negative, consistent
  with the recurring program theme that generic transcriptomic signals are weak.

## Honesty / scope
Cell-line PRISM efficacy (not clinical). Consensus L1000 signatures average across cell lines/doses (not
cell-matched), so this tests average-reversal→efficacy — a real but coarse connectivity test. Drug/gene matching is
partial (239 drugs, ~7k genes). A null is fully expected and first-class.

## Reproducibility
Deterministic (seed=42); reproduce ×2. Data provenance/sha in results. Output:
experiments/B27_lincs_connectivity/results/B27_metrics.json.
