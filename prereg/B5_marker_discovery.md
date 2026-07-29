# Pre-registration — B5: systematic mutation→drug marker discovery in BeatAML (FINALIZED 2026-07-29, pre-run)

## Question
Beyond the 5 hand-picked verified pairs (V4–V6), which somatic-mutation→drug-sensitivity associations exist in
BeatAML that survive rigorous multiple-testing correction, deconfounding, AND internal split-replication —
i.e., which can be promoted to "verified-grade" markers for the engine?

## Hypothesis (assumed FALSE per pair)
For each (gene, drug): mutation status is associated with ex-vivo AUC beyond FLT3-ITD and proliferation.
H0 (global): after BH-FDR across all tested pairs, no association survives.

## Data (held; controlled — INTERCEPTA_BEATAML; results are aggregate gene×drug stats, no patient IDs)
BeatAML probit AUC (per subject×inhibitor), WES non-silent mutations (per subject), clinical FLT3-ITD/NPM1,
R_prolif from expression. Keyed by `dbgap_subject_id`.

## Design (locked)
- Genes tested: any gene non-silently mutated in **≥20 subjects** (recurrent; keeps the test space biologically
  meaningful and multiple-testing sane).
- Drugs tested: any inhibitor with AUC in **≥30 subjects**.
- Per (gene, drug) with ≥8 mutant subjects in the overlap: OLS `AUC ~ mutation + FLT3_ITD + R_prolif`; record
  the mutation partial p-value + β (sign) + n. (FLT3-ITD dropped when gene==FLT3.)
- Also Mann–Whitney AUC(mut) vs AUC(wt) for a nonparametric cross-check.

## Multiple testing + decision rule (fixed)
- **BH-FDR across ALL tested (gene,drug) pairs** on the OLS mutation partial p.
- **DISCOVERED** = BH-q < 0.05 AND ≥8 mutant subjects.
- **VERIFIED-GRADE (promotable)** = DISCOVERED AND direction (sign of β) replicates in BOTH deterministic
  md5-parity split-halves. Only these are added to a `discovered_markers.json` for the engine (the hardcoded
  V4–V6 core stays as-is).
- **Positive-control check:** NPM1→Cabozantinib, NRAS→(trametinib/selumetinib/…MEKi), DNMT3A→Dasatinib MUST
  appear among DISCOVERED, or the pipeline is flawed and results are void.

## Honesty / scope
BeatAML is ONE cohort (AML). BH-FDR survivors are internal discoveries; VERIFIED-GRADE adds internal split-
replication but NOT external replication — every marker still needs a 2nd cohort. Direction reported as
sensitizing (β<0, lower AUC) or resistance (β>0). No causal claim.

## Reproducibility
OLS deterministic; emitted p-values rounded; split by md5 parity; reproduce ×2 = identical metrics JSON.
Output: `experiments/B5_marker_discovery/results/B5_metrics.json` (+ `discovered_markers.json`).
