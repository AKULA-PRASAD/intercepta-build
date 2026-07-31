# Pre-registration — B55: external replication of P6 (bias independence/additivity) on DUD-E (FINALIZED 2026-07-31, PRE-RESULT)

## Scientific question (Phase 1) — does a working principle survive a different benchmark family?
B54 found, on LIT-PCBA, that analog-bias and physicochemical/decoy-bias are **independent and additive** sources of VS
enrichment inflation (interaction ≈ 0), leaving a small irreducible signal — this is **working principle P6**. A
principle must survive an external dataset of *different construction* before graduating. **DUD-E** (Mysinger 2012) is
that test: ChEMBL actives (clustered → strong analog bias) with ZINC decoys that are property-matched **but
deliberately topology-dissimilar** (top-75%-similar removed) — a *different bias regime* than LIT-PCBA's arbitrary-HTS
decoys. B55 replicates the B54 factorial **verbatim** on DUD-E. If the additive-independence structure (interaction ≈ 0)
replicates, P6 strengthens toward a scientific principle; if the interaction is large, P6 is LIT-PCBA-specific
(falsified as general).

## Literature-map note (Phase 2)
DUD-E's analog + decoy bias is documented (Chen 2019 PLoS ONE; Sieg 2019). Property-matched decoys (DUD-E, DeepCoy) and
analog/AVE bias (Wallach-Heifets, MUV) are studied separately; the **independence/additivity of the two axes** is the
unresolved claim B54 introduced — B55 tests its external validity, which no prior work reports.

## Data (OPEN; DUD-E, cached $INTERCEPTA_DATA/dude; downloaded from dude.docking.org)
8 class-diverse targets: **egfr, vgfr2, akt1 (kinase); aa2ar (GPCR); fa10, hivpr (protease); ppara, gcr (nuclear
receptor)**. Per target: actives (col-0 SMILES of `actives.ism`) + own decoys (`decoys.ism`, property-matched
ZINC, topology-dissimilar). ≤400 actives (seeded); decoy pool subsampled to 8,000 (seeded) to mirror B54; ratio 1:3.

## Design (identical to B54; Phase 9)
2×2 factorial, held-out AUROC (Morgan-1024 → HGB, 5 seeds):
- **A — decoy matching:** A0 random decoys from the pool · A1 greedy property-matched decoys (NN in z-scored 6-D
  physchem: MolWt, Crippen logP, HBD, HBA, TPSA, rot-bonds; 3/active).
- **B — analog control:** B0 random active split · B1 novel-chemistry (scaffold-disjoint AND test-active Morgan-Tanimoto
  NN < 0.40 vs train actives). A target is used only if its B1 test set has ≥15 actives (DUD-E's heavy analog
  clustering may leave few — reported).
Decompose: decoy-effect = mean_B(A0−A1); analog-effect = mean_A(B0−B1); **interaction** = (A0B0−A1B0)−(A0B1−A1B1);
residual = A1B1.

## Hypotheses (pre-registered; the SAME thresholds as B54)
- **H1 (P6 REPLICATES — biases independent/additive):** panel-mean **|interaction| < 0.03** on DUD-E.
- **H2 (P6 FAILS externally — overlap):** interaction ≤ −0.03 (biases largely the same on DUD-E → P6 is benchmark-specific).
- **H3 (residual):** A1B1 panel-mean reported. **Pre-registered caveat:** on DUD-E the residual is NOT a clean binding
  signal — the ChEMBL-actives-vs-ZINC-decoys *source* bias is constant across both A-arms (so it does not confound the
  interaction test) but inflates A1B1; the residual magnitude is therefore benchmark-specific and interpreted only as
  "signal + source-artifact," not binding signal.
- **Reported regardless:** full 2×2 per target + panel, the three decomposition terms, residual, and the physchem gap
  A0 vs A1 (to confirm A1 is more property-matched).

## Honesty / scope
Retrospective, in-silico. Same 6-descriptor matching + NN<0.4 thresholds as B54 (for comparability, not exhaustiveness).
DUD-E residual carries source bias (stated). 8 targets. Not wet-lab. Any outcome (replicates / fails / mixed) is
first-class and pre-committed; a FAILURE to replicate is an equally valuable, first-class result that would demote P6.

## Reproducibility
Deterministic: active cap seed=42, pool/decoy/split/scaffold seeds [1..5] fixed, greedy matching deterministic, model
seed=42. Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B55_p6_external_dude/results/B55_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned. DUD-E in MANIFEST.

---

## AMENDMENT (2026-07-31, after RUN_A — the pre-registered factorial could not run)
The pre-registered 2×2 factorial requires a novel-chemistry (NN<0.4) analog-control arm with ≥15 test actives. On DUD-E
this arm is **empty for all 8 targets**: DUD-E actives are so analog-clustered (panel mean leave-one-out NN-Tanimoto
≈0.71; only ~5% of actives NN<0.4) that no target reaches 15 novel test actives. Therefore P6 **cannot be tested on
DUD-E** and any "P6 fails/replicates" verdict would be unsupported (the original run emitted a NaN — discarded, not
committed). The runner is refocused to the honest first-class finding it revealed: **quantify DUD-E's analog clustering
and establish that scaffold-splitting does not control analog similarity on DUD-E** (distinct Murcko scaffolds despite
mean NN 0.71). P6's status is UNCHANGED (externally untested — neither replicated nor falsified); its external
replication is deferred to a chemically-diverse benchmark (MUV). This amendment is dated and the original design above
is left intact as the record.
