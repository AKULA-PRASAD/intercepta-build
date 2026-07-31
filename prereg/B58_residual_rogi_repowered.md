# Pre-registration — B58: re-powered residual-mechanism test with ROGI (FINALIZED 2026-07-31, PRE-RESULT)

## Why (re-power B57's null with a principled metric + more targets)
B57 found no target property explains the doubly-debiased residual (A1B1), but was underpowered (n=13) and used a crude
single-threshold activity-cliff density (Spearman −0.36, right sign, below the −0.5 bar). B58 re-tests the SAR-ruggedness
mechanism properly: (a) a **principled, continuous, multi-scale roughness index (ROGI**, Aldeghi/Graff/Coley 2022 —
reimplemented dependency-free and validated: rough synthetic landscape 0.42 > smooth 0.17), and (b) an **expanded target
panel** (~18–20) to improve power. Question unchanged: *does landscape roughness predict which targets retain real
ligand-based signal after both biases are removed?*

## ROGI (our reimplementation — exact formula, no external dependency)
Standardize the property y (binary active=1/decoy=0); complete-linkage hierarchical clustering on Tanimoto distance
(1−sim); at each distance threshold t∈[0,1] assign each molecule its cluster-mean y, SD(t)=std of those; **roughness =
1 − ∫₀¹ SD(t) dt / SD(0)** (0=smooth, →1=rough). Computed on a seeded balanced sample (≤200 actives + ≤200 random
decoys) per target. Validated to separate rough (0.42) from smooth (0.17) landscapes; deterministic.

## Data (OPEN; reuse committed residuals + compute new ones identically)
- **Residual (A1B1)** = property-matched decoys + novel-chemistry (NN<0.4) test, Morgan-1024 HGB, 5 seeds — the SAME
  method as B54/B56. **Read from committed JSON for the 13 done targets** (B54: ALDH1,VDR,PKM2,FEN1,MAPK1,GBA,KAT2A,
  ESR1_ant; B56: hiv,m1_antag,orexin1,kir2.1,stk33). **Computed here (identical code) for NEW TDC/Butkiewicz targets:**
  m1_agonists, kcnq2, cav3_t-type, choline_transporter, tyrosyl-dna_phosphodiesterase, sarscov2_3clpro, sarscov2_vitro.
- A target is included only if its novel-chemistry (NN<0.4) test arm has ≥15 actives (the B55 lesson, enforced;
  skipped targets reported).
- Predictors (ROGI, cliff density, active diversity, n_actives) computed uniformly for all included targets.

## Analysis & hypotheses (Phase 9; same style/threshold as B57)
Spearman(residual, predictor) across the panel; rank by |Spearman|.
- **H1 (ROGI mechanism):** ROGI is the **strongest** correlate of the residual AND **negative** (Spearman ≤ −0.5) —
  rougher landscape ⇒ lower irreducible signal ⇒ we can PREDICT when ligand-based VS is trustworthy.
- **H2 (ROGI beats crude cliff):** |Spearman(ROGI)| > |Spearman(cliff density)| (the principled metric is more
  explanatory than B57's threshold metric).
- **H0 / null:** no predictor reaches |Spearman| ≥ 0.5 → the residual's target-dependence is still unexplained even
  with a principled metric + more power (a stronger, first-class null that meaningfully bounds the question).
- **Reported regardless:** all correlations, the ranking, and per-target residual/ROGI/predictor table.

## Honesty / scope
Retrospective, in-silico meta-analysis. ROGI is a faithful reimplementation of the published concept (stated formula),
NOT the reference package (which conflicts with our pinned numpy) — validated on synthetic landscapes, not bit-checked
against the original. n≈18–20 (still modest; report effect sizes + rank, note power). Binary-label ROGI depends on the
decoy sample (random, seeded). Correlation ≠ causation across targets. Enrichment ≠ proven activity; not wet-lab.

## Reproducibility
Deterministic: seeds fixed (residual 5-seed same as B54/B56; ROGI/predictor samples seed=42; clustering deterministic).
Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B58_residual_rogi_repowered/results/B58_metrics.json`. Env: intercepta-build (RESTORED, verified
byte-identical); INTERCEPTA_DATA owned.
