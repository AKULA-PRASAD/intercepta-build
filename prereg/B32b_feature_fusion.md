# Pre-registration — B32b: feature-level fusion — do the modules add TRANSFER value beyond raw structure? (FINALIZED 2026-07-30, PRE-RESULT)

## Why (follows directly from the B32 negative)
B32 showed that composing the modules' **scalar outputs** by late-fusion (logistic on 12 numbers) did NOT beat the
single best module on ClinTox — AND that a **direct raw-structure model** (Morgan GBT, AUROC 0.857) beat both the
composite (0.819) and the best single module (0.831). That points to the real question: the modules are trained on
EXTERNAL data (TDC ADMET, RAscore) disjoint from ClinTox, so their outputs are legitimate *transfer features*. Does
**fusing those transfer features with raw structure** beat raw structure alone? If yes, the integration genuinely
adds value (a platform win via feature-level fusion); if no, raw structure is sufficient here (honest negative).

## Data & leakage (identical to B32)
Held-out **ClinTox** (TDC/MoleculeNet; clinical-trial toxicity failure; 1,459 unique, ~103 positive). Modules
trained ONLY on their own data. Leakage-controlled: exclude every ClinTox molecule whose canonical SMILES appears in
any module's training set (B30 ADMET panel train_val ∪ B31 RAscore 50k subsample) → leakage-free evaluation set
(~1,039 molecules). Bemis–Murcko scaffold split, 5 seeds; report mean±sd.

## Feature sets (the crux — same model class for a fair comparison)
- **S = raw structure:** Morgan/ECFP4 2048-bit + 17 RDKit physchem (2,065-dim) — the strong structure baseline.
- **M = module transfer features (12):** predicted outputs of the B30 ADMET panel (herg, ames, dili, ld50_zhu,
  cyp3a4_veith, bioavailability_ma, bbb_martins, ppbr_az, clearance_microsome_az, half_life_obach) + B31
  solvable_prob + RDKit SAscore. (These are deterministic functions of structure via external-data-trained models —
  no within-ClinTox leakage; the 420 overlapping molecules are excluded above.)
- **S+M = feature-level fusion:** concatenation of S and M (2,077-dim).

## Model & baselines
- **Model:** HistGradientBoostingClassifier (seed=42, max_iter=300, lr=0.06, max_depth=6) — the SAME class fit on
  S, M, and S+M, so any difference is the feature effect, not the model.
- **Baselines/context:** S alone (structure), M alone (scalar late-fusion, HGB version), and the best single module
  output (from B32) — reported alongside.
- **Metric:** AUROC primary (imbalanced → AUPRC also). 5-seed scaffold CV mean±sd.

## Hypotheses (assumed FALSE)
- **H1 (modules add transfer value — the real claim):** AUROC(S+M) > AUROC(S) by more than 1 sd across the 5 seeds.
- **H2 (fusion is best overall):** AUROC(S+M) ≥ max(AUROC(S), AUROC(M), best-single-module).
- **H0:** S+M ≈ S → the ADMET/synth transfer features add nothing beyond raw structure for this outcome (raw
  structure is sufficient) — a first-class negative, consistent with B32.

## Decision rule & interpretation (fixed)
- **H1 PASS** → the modules add genuine transfer value on top of structure → feature-level fusion is a real
  integrated-platform improvement → SHIP it (`DevelopabilityPrioritizer` gains a validated `fusion=True` mode) and
  record a positive in the LEDGER (honest effect size; still scoped to this benchmark).
- **H1 FAIL** → raw structure is sufficient here; the modules are useful STANDALONE but do not augment structure for
  ClinTox → first-class negative, recorded; no fusion claim.

## Honesty / scope
Same as B32: a research developability signal on one benchmark; small positive class; scaffold-split;
survivorship-confounded; NOT a clinical/regulatory determination. Effect size governs the verdict, not just the sign.

## Reproducibility
Deterministic (seed=42; module fits seeded; scaffold split + CV seeded). Reproduce ×2 byte-identical (payload
sha256). Provenance JSON with git_sha, python, libs, seeds, leakage counts, timestamp. Output:
`experiments/B32b_feature_fusion/results/B32b_metrics.json`.
