# TID4 — Fixing the silent failure: can a LABEL-FREE, query-time signal predict when zero-data target-ID will fail? (finalized 2026-08-02, PRE-RESULT)

(TID4 = Target-ID chapter 4 — addresses the real flaw TID3 exposed: zero-data target-ID silently fails on
phylogenetically-isolated pathogens because its per-protein abstention does NOT flag organism-level failure.)

## Why (fix a demonstrated flaw in a founding capability)
TID3 showed zero-data target-ID degrades across kingdoms and FAILS on the isolated fungus — yet per-protein abstention
did NOT catch it (the fungus abstained at the same rate but recovered nothing = confidently wrong). Calibrated
self-awareness ("know when you're out of your depth") is a founding principle. TID4 asks: is there a LABEL-FREE,
query-time signal — computable for a brand-new organism with NO target labels — that predicts whether the pipeline's
target-ID will work, so the system can ABSTAIN AT THE ORGANISM LEVEL when it is too phylogenetically isolated?

## Data (OPEN; consistency-first; the data's honest limit)
ChEMBL drug-target ground truth is sparse/strain-fragmented for most pathogens → a large powered panel is NOT available
(stated limitation). Consistent methodology (avoids TID3's strain mismatch): per organism, UniProt **reviewed**
proteome + ChEMBL-xref targets by the SAME organism_id (targets ⊆ proteome by construction). Panel = organisms with
reviewed proteome ≥100 proteins AND ≥5 in-proteome targets: **7 bacteria** (mtb/ecoli/paeruginosa/saureus/hpylori/
ngonorrhoeae/kpneumoniae) + **2 parasites** (pfalciparum/tcruzi) + **2 fungi** (calbicans/afumigatus). n=11 across 3
kingdoms (bacteria-weighted — a data-imposed limit, reported).

## Design (TID3 leave-organism-out target-ID + LABEL-FREE organism-level confidence signals)
For each held-out organism X: druggability transfer (mmseqs2 homology to OTHER organisms' targets) → per-organism
recovery = **precision@k** of known targets. Compute, for X, LABEL-FREE query-time signals (NO target labels; use only
X's proteome vs the reference proteomes): (S1) **median best-homology-bits** of X's proteome to the reference full
proteomes (overall homological connectedness); (S2) **fraction of X's proteome with ANY homolog** in the reference;
(S3) **same-kingdom reference count**; (S4) **mean best-bits of X's proteome to its NEAREST reference organism**
(closest-relative proximity). Test whether these predict recovery across the 11 organisms.

## Metrics / test
- Per-organism: precision@k (recovery), S1–S4 (label-free confidence signals).
- **Spearman correlation** across organisms between each label-free signal and recovery (precision@k). Leave-one-out
  cross-validated: can S predict a held-out organism's recovery rank?
- Proposed organism-level abstention rule: flag "low-confidence organism" when the label-free signal is below a
  threshold; report how well it separates high- vs low-recovery organisms (AUROC of signal vs a binarised
  recovery-success label).

## Hypotheses (pre-registered)
- **H1 (a label-free signal predicts failure):** at least one of S1–S4 has **Spearman > +0.5** with per-organism recovery
  (precision@k) across the 11 organisms → the system CAN know, at query time with no labels, when target-ID will work →
  organism-level abstention FIXES TID3's silent failure. (Direction: more homological connectedness / closer relatives
  → better recovery.)
- **H2 (which signal):** rank S1–S4 by predictive strength; the closest-relative proximity (S4) and same-kingdom count
  (S3) are expected strongest (TID3's monotonic kingdom trend).
- **H0 (first-class):** no label-free signal predicts recovery (all |Spearman| < 0.5) → organism-level failure is NOT
  predictable from homological distance alone → the silent failure is HARD to fix cheaply; honest boundary.

## Honesty / scope
Retrospective; reviewed proteomes (enriched for studied proteins → precision@k higher than TID1/TID3's full proteomes,
but CONSISTENT within TID4 — the correlation is the test, not the absolute level); **n=11, bacteria-weighted (data-imposed;
stated)** → an organism-level correlation at modest power (report Spearman + CI + the per-organism scatter, not just a
threshold); not a large-panel study (ChEMBL target sparsity is the limit); not wet-lab.

## Reproducibility
Deterministic (mmseqs fixed params, fixed panel). Reproduce ×2 byte-identical (payload over per-organism recovery +
signals + correlations). Output: `experiments/TID4_organism_confidence/results/TID4_metrics.json`. Env: bioinfo(mmseqs2)
+ intercepta-build. Data: UniProt reviewed (MANIFEST). Smoke-test 1 held-out organism before the full panel.
