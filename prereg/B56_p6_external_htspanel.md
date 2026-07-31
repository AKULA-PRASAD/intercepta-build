# Pre-registration — B56: external replication of P6 (bias independence/additivity) on the TDC/Butkiewicz HTS panel (FINALIZED 2026-07-31, PRE-RESULT)

## Why (graduation test, correct instrument; Phase 2/4)
P6 (analog-bias and decoy-bias are independent/additive inflation sources, B54) was derived on LIT-PCBA. A Phase-2
review disqualified two candidate external benchmarks: **DUD-E** (B55: actives too analog-clustered — mean NN 0.71,
only ~5% NN<0.4 — the novel-chemistry arm is empty) and **MUV** (designed to remove BOTH biases → nothing to decompose;
only ~30 actives/target). The correct instrument must have (i) enough diverse actives to populate a novel-chemistry
(NN<0.4) arm, and (ii) *natural* (non-debiased) construction so both biases are present. The **TDC/Butkiewicz
PubChem-HTS single-target panel** passes a pre-check (m1-muscarinic 46% NN<0.4, orexin-1 54%, HIV 47%; 233–1443
actives) and is a **different curation and target set** than LIT-PCBA. B56 runs the B54 factorial verbatim on it.

## Honest scope of "external" (stated up front)
This is a *partial* external replication: different targets and curation (Butkiewicz vs LIT-PCBA/Tran-Nguyen), but both
are PubChem-HTS-derived — NOT a fundamentally different decoy paradigm (e.g. DUD-E's property-matched ZINC). It tests
whether P6's independence *structure* transfers across curation + target set; a fully independent-source replication
(diverse ChEMBL actives + a different decoy paradigm) is a documented limitation of the question.

## Data (OPEN; TDC HTS, cached $INTERCEPTA_DATA/tdc_bio)
6 diverse targets: `hiv`, `m1_muscarinic_receptor_antagonists_butkiewicz`, `orexin1_receptor_butkiewicz`,
`potassium_ion_channel_kir2.1_butkiewicz`, `serine_threonine_kinase_33_butkiewicz`, `sarscov2_3clpro_diamond`
(antiviral/GPCR/GPCR/ion-channel/kinase/protease). Per target: ≤400 actives (seeded); decoy pool = HTS inactives
subsampled to 8,000 (seeded); ratio 1:3. Targets whose novel-chemistry (NN<0.4) test arm has <15 actives are reported
and excluded (the B55 lesson, enforced).

## Design (IDENTICAL to B54; same thresholds — no moving goalposts)
2×2 factorial, held-out AUROC (Morgan-1024 → HGB, 5 seeds): A0 random vs A1 property-matched decoys (greedy NN in
z-scored 6-D physchem); B0 random split vs B1 novel-chemistry (scaffold-disjoint AND test-active Morgan-Tanimoto
NN<0.40). Decompose: decoy-effect = mean_B(A0−A1); analog-effect = mean_A(B0−B1); interaction = (A0B0−A1B0)−(A0B1−A1B1);
residual = A1B1.

## Hypotheses (pre-registered; the SAME thresholds as B54)
- **H1 (P6 REPLICATES — independent/additive):** panel-mean **|interaction| < 0.03** on the HTS panel (matching B54's
  −0.019) → P6 graduates toward a scientific principle (holds across LIT-PCBA + a different HTS curation).
- **H2 (P6 FAILS — benchmark-specific):** interaction ≤ −0.03 (or ≥ +0.03) → the independence law does not transfer;
  P6 demoted (first-class negative).
- **H3 (residual):** A1B1 panel-mean reported (the honest doubly-controlled ligand signal on this panel).
- **Reported regardless:** full 2×2 per target + panel, the three decomposition terms vs the B54 reference
  (decoy +0.075, analog +0.087, interaction −0.019, residual 0.628), and how many targets support the novel arm.

## Honesty / scope
Retrospective, in-silico. Same 6-descriptor matching + NN<0.4 thresholds as B54 (comparability). Partial externality
(stated). Decoys are HTS inactives (presumed-negative noise). Not wet-lab. Any outcome is first-class and pre-committed;
a failure to replicate would demote P6, which is the point of the test.

## Reproducibility
Deterministic: active cap seed=42, pool/decoy/split/scaffold seeds [1..5] fixed, greedy matching deterministic, model
seed=42. Reproduce ×2 byte-identical (payload sha256 over summary+per-target). Output:
`experiments/B56_p6_external_htspanel/results/B56_metrics.json`. Env: intercepta-build; INTERCEPTA_DATA owned.
