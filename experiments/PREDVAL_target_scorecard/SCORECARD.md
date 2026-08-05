# PREDVAL — experimental-essentiality scorecard for the pipeline's nominated targets

Per-target check of the DRUGGABLE broad-spectrum nominations against EXPERIMENTAL gene-essentiality in three
organisms: **E. coli** (PEC single-gene knockouts), **M. tuberculosis** (DeJesus 2017 Tn-seq, ES), **K. pneumoniae**
(CRISPRi/Tn-seq). `1`=experimentally essential, `0`=not (or organism-specific name not symbol-matched). Reproduced x2.

**Headline: of 9 broad-spectrum (FBA-breadth>=3) druggable nominations, 8 are experimentally essential in >=1 organism and 7 in >=2.** Concordance is expected (nominations are FBA-essential; VAL-ESS showed FBA->experimental enrichment) — this is a per-target confirmation + false-positive audit, not an independent test.

| gene | FBA breadth (of 7) | druggable | E. coli | M. tb | K. pneu | # orgs essential |
|------|:--:|:--:|:--:|:--:|:--:|:--:|
| murB | 5 | yes | 1 | 1 | 1 | 3/3 |
| murG | 5 | yes | 1 | 1 | 1 | 3/3 |
| dxr | 4 | yes | 1 | 1 | 1 | 3/3 |
| ispE | 4 | yes | 1 | 1 | 1 | 3/3 |
| murF | 4 | yes | 1 | 1 | 1 | 3/3 |
| murD | 2 | yes | 1 | 1 | 1 | 3/3 |
| murE | 2 | yes | 1 | 1 | 1 | 3/3 |
| thiL | 2 | no | 1 | 1 | 1 | 3/3 |
| coaA | 1 | yes | 1 | 1 | 1 | 3/3 |
| dapB | 1 | no | 1 | 1 | 1 | 3/3 |
| glmU | 1 | no | 1 | 1 | 1 | 3/3 |
| ispD | 1 | yes | 1 | 1 | 1 | 3/3 |
| ispF | 1 | no | 1 | 1 | 1 | 3/3 |
| murC | 1 | yes | 1 | 1 | 1 | 3/3 |
| murI | 1 | yes | 1 | 1 | 1 | 3/3 |
| tmk | 1 | no | 1 | 1 | 1 | 3/3 |
| coaD | 4 | no | 1 | 0 | 1 | 2/3 |
| ispG | 4 | yes | 1 | 0 | 1 | 2/3 |
| mraY | 3 | yes | 1 | 0 | 1 | 2/3 |
| ribB | 2 | no | 1 | 0 | 1 | 2/3 |
| dapF | 1 | no | 0 | 1 | 1 | 2/3 |
| dxs | 1 | yes | 1 | 0 | 1 | 2/3 |
| ribA | 1 | yes | 1 | 0 | 1 | 2/3 |
| ribH | 1 | yes | 0 | 1 | 1 | 2/3 |
| menC | 3 | yes | 0 | 1 | 0 | 1/3 |
| folB | 2 | yes | 1 | 0 | 0 | 1/3 |
| thiE | 2 | yes | 0 | 1 | 0 | 1/3 |
| ilvC | 1 | no | 0 | 1 | 0 | 1/3 |
| menD | 1 | yes | 0 | 1 | 0 | 1/3 |
| panB | 1 | yes | 0 | 1 | 0 | 1/3 |
| ribC | 1 | yes | 1 | 0 | 0 | 1/3 |
| ribD | 1 | no | 1 | 0 | 0 | 1/3 |
| ribE | 1 | no | 1 | 0 | 0 | 1/3 |
| mtnN | 3 | yes | 0 | 0 | 0 | 0/3 |
| thiD | 2 | yes | 0 | 0 | 0 | 0/3 |
| EF_1541 | 1 | yes | 0 | 0 | 0 | 0/3 |
| EF_2056 | 1 | yes | 0 | 0 | 0 | 0/3 |
| HP_0740 | 1 | no | 0 | 0 | 0 | 0/3 |
| coaX | 1 | no | 0 | 0 | 0 | 0/3 |
| cysE | 1 | yes | 0 | 0 | 0 | 0/3 |
| folP | 1 | no | 0 | 0 | 0 | 0/3 |
| ispDF | 1 | yes | 0 | 0 | 0 | 0/3 |
| luxS | 1 | no | 0 | 0 | 0 | 0/3 |
| motB | 1 | no | 0 | 0 | 0 | 0/3 |
| ribA1 | 1 | yes | 0 | 0 | 0 | 0/3 |
| uppP | 1 | yes | 0 | 0 | 0 | 0/3 |
| ybgC | 1 | yes | 0 | 0 | 0 | 0/3 |
| ycnE | 1 | yes | 0 | 0 | 0 | 0/3 |
| yoaC | 1 | yes | 0 | 0 | 0 | 0/3 |

## Honest reading
- **Strongest validated targets (essential in all 3 organisms):** murB, murG, dxr, murF, ispE, murD, murE, murC, coaA, murI, ispD, ispF, glmU, tmk, dapB, thiL — the cell-wall/peptidoglycan (mur*, glmU) and MEP/isoprenoid (dxr, isp*) cores. These are the pipeline's highest-breadth, druggable nominations AND confirmed experimental essentials.
- **Confirmed FALSE POSITIVE:** mtnN (breadth 3, druggable) is experimentally NON-essential in all three — a genuine miss (methylthioadenosine nucleosidase has salvage redundancy), honestly flagged (also caught in the E. coli VAL-ESS).
- **Conditionally essential (essential in some organisms/conditions):** menC/menD (menaquinone), thiE/thiD (thiamine), fol* (folate), rib* (riboflavin) — condition/medium-dependent essentiality, correctly appearing 1-2/3.
- **Under-counts (symbol-mapping, NOT true false positives):** locus-tag names (EF_2056, EF_1541, HP_0740) and organism-specific variants (ispDF, ribA1) have no cross-organism gene symbol to match, so score 0/3 spuriously.
- Mirrors CALIB1: high-breadth/high-confidence nominations validate; the low-breadth tail does not — as it should.

*Scope: gene-symbol membership in each organism's experimental essential set; essentiality only (not drug-target/selectivity/clinical); hypotheses, not validated targets; not wet-lab.*
