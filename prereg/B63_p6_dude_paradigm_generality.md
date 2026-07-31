# Pre-registration — B63: does P6 (bias independence/additivity) hold under a DIFFERENT decoy paradigm? (FINALIZED 2026-07-31, PRE-RESULT)

## Why (close P6's one honest boundary — its most consequential test)
P6 (analogue-bias and decoy-bias are INDEPENDENT and ADDITIVE; interaction ≈ 0) is our most novel, replicated principle
— but B54/B56 both used the **HTS decoy paradigm** (decoys = assay inactives), and B55 could not test the DUD-E paradigm
(property-matched-yet-topology-dissimilar decoys) because real DUD-E's actives are too analogue-clustered to populate a
novel-chemistry arm. B63 CONSTRUCTS the missing instrument — **diverse ChEMBL actives + DUD-E-style decoys built from a
2M-compound ChEMBL background** — and re-runs the factorial. If the interaction is still ≈ 0, P6 graduates toward a
**general law of VS bias** (holds across both major decoy paradigms and multiple curations); if it changes, P6 is
paradigm-specific. Either result is decisive for our most field-relevant claim.

## Data (OPEN; MoleculeACE actives + ChEMBL background decoys; cached)
Actives = MoleculeACE compounds per target (diverse ChEMBL medchem; ≤400, seeded). Decoy background = a seeded
8,000-compound sample of ChEMBL (`$INTERCEPTA_DATA/tdc_gen/chembl.tab`, 1.96M rows). Targets whose novel-chemistry
(NN<0.4) arm has <15 test actives are skipped and reported (the B55 lesson; ~19–24 MoleculeACE targets expected usable).

## Design (the B54/B56 2×2 factorial, with a NEW decoy paradigm on the A-axis)
- **A — decoy paradigm:** A0 = random background decoys; **A1 = DUD-E-style decoys** = property-matched (nearest in
  z-scored 6-D physchem) AND topology-dissimilar (max Tanimoto to any active < 0.5), greedy no-replacement, 3:1
  (Mysinger 2012 recipe, built from the ChEMBL background).
- **B — analogue control:** B0 random active split; B1 novel-chemistry (scaffold-disjoint AND test-active NN<0.4 vs train).
- Classifier: Morgan-1024 → HGB (active vs decoy); AUROC per cell; 3 seeds.
- Decompose: decoy-effect = mean_B(A0−A1); analogue-effect = mean_A(B0−B1); **interaction = (A0B0−A1B0)−(A0B1−A1B1)**;
  residual = A1B1.

## Hypotheses (pre-registered; SAME threshold as B54/B56)
- **H1 (P6 GENERALISES across decoy paradigms):** panel-mean **|interaction| < 0.03** under the DUD-E paradigm too →
  analogue and decoy bias are independent/additive regardless of decoy construction (a general law).
- **H2 (P6 is paradigm-specific):** |interaction| ≥ 0.03 → the additive-independence structure does NOT transfer to the
  DUD-E decoy paradigm; P6 is HTS-paradigm-specific (first-class boundary, demotes P6's generality).
- **Reported regardless:** full 2×2 per target + panel, the three decomposition terms vs the B54/B56 reference
  (interaction −0.019 / −0.0005; decoy +0.075/+0.050; analogue +0.087/+0.100), and per-target counts. NOTE the decoy
  main-effect sign may differ (DUD-E decoys are property-matched AND topology-dissimilar); the INTERACTION is the test,
  and it is valid regardless of the main-effect direction.

## Honesty / scope
Retrospective, in-silico. Decoys are CONSTRUCTED by us (faithful DUD-E recipe: property-matched + topology-dissimilar
from a ChEMBL background) — a legitimate "different decoy paradigm," but our construction, documented. MoleculeACE
"actives" are potent ChEMBL compounds treated as the active class (standard for constructed-decoy VS). Same 6-descriptor
matching + NN<0.4 thresholds as B54/B56 for comparability. n≈19–24 targets. Not wet-lab. H2 (P6 fails to generalise) is
an expected-allowed, valuable outcome.

## Reproducibility
Deterministic (active cap seed=42, background sample seed=42, split/decoy seeds [1,2,3], greedy matching deterministic,
model seed=42). Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B63_p6_dude_paradigm_generality/results/B63_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned.

---

## AMENDMENT (2026-07-31, pre-run — decoy-construction bug fixed; NOTHING was committed)
The first execution of the DUD-E decoy builder did **not** implement the pre-registered 3:1 ratio: the greedy loop
(`for _ in range(k): for ai in act_idx:`) appended up to one decoy *per active per round*, i.e. up to k×(#actives)
decoys — capped only by the 8,000-compound background — so the A1 (DUD-E) arm selected essentially ALL eligible
background (~32:1+), while the A0 (random) arm was correctly 3:1. This (a) violated the pre-registered 3:1 design, (b)
**confounded the A0-vs-A1 factorial contrast** the experiment exists to measure, and (c) recomputed an 8,000-wide
`argsort` k times per active (~185k argsorts/target), which made the run pathologically slow (killed at 64 CPU-min
before producing any output — profiled via `sample`, 95% in list-membership + redundant argsort). The builder was
rewritten to the pre-registered intent: **exactly k = RATIO×(#actives) decoys TOTAL, round-robin across actives,
nearest-first physchem order computed once per active (resume pointer), plain-int set membership** — deterministic and
correct. No B63 result/payload was ever committed prior to this fix, so nothing is retracted. The corrected run is the
first and only committed B63.
