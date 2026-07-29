# Pre-registration — B9: PRISM-powered PDXE external validation (FINALIZED 2026-07-29, pre-run)

## Question
B7 externally replicated the drug-specific transfer in PDXE but was underpowered on overall magnitude (9 GDSC
drugs, H1 p=0.14). Does training the transfer on **PRISM** (public, ~1400 drugs on DepMap cells) — which covers
**12** PDXE drugs — reproduce/strengthen the external replication with more power?

## Data (public; no gate)
Train: DepMap RNA-seq + **PRISM AUC** (label_source='prism'). Test: PDXE RNAseq_fpkm + BestAvgResponse. Drugs:
all PDXE single-agents trainable via PRISM (≥15 PDX models, ≥30 PRISM cells) = 12 — ribociclib, buparlisib,
alpelisib, cgm097, paclitaxel, everolimus, tamoxifen, trametinib, gemcitabine, sonidegib, dacarbazine, erlotinib.
(Data-driven set, not hand-picked.)

## Hypotheses (assumed FALSE) — identical tests to B7, more drugs
- **H1 (transfer):** mean diagonal per-drug ρ(transfer_pred, BestAvgResponse) > 0, permutation p<0.05.
- **H2 (drug-specific beyond proliferation):** prolif-residualized diagonal ρ > off-diagonal ρ AND >0, perm p<0.05.

## Decision rule (fixed)
Per drug (≥15 PDX models): diagonal ρ = Spearman(transfer_pred, BAR); off-diagonal = mean over other drugs.
Residualize on R_prolif for H2. Permutation k=2000, seed=42. H1 PASS iff diag>0 & p<0.05; H2 PASS iff
resid(diag−off)>0 & p<0.05. This is a POWERED replication of B7 (12 vs 9 drugs, PRISM vs GDSC training) — a
positive strengthens V14; a null bounds it honestly.

## Honesty
PDXE = patient-proxy (xenograft). PRISM AUC vs GDSC LN_IC50 are different response scales but both = resistance
(z-scored). 12 drugs still modest. Direction: higher predicted resistance → higher BAR → positive ρ.

## Reproducibility
Engine deterministic; seed=42, k=2000; reproduce ×2. Output: `experiments/B9_pdxe_prism/results/B9_metrics.json`.
