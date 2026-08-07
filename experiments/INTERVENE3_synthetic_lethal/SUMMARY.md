# INTERVENE3 — Paralog synthetic lethality as a DRUGGED route around cancer undruggability — SUMMARY

**Verdict: G1 PASS (SL signal is real & recovered) · G2 reported honestly (small route, low per-hit
precision).** Reproduced x2 byte-identical.
Payload SHA-256: `ae8535da02857c8be4aebe10d232793169b337a0646c5cac23fb563365f331b8`.

INTERVENE2 left **93.2% (3416/3664)** of DEPEND1's validated selective cancer dependencies UNDRUGGED
(de-novo-chemistry-gated). Synthetic lethality is the one clinically-validated route *around*
undruggability (PARP/BRCA). This module tests whether a DepMap-derivable **paralog-SL** signal opens a
DRUGGED route to those undruggable targets. **Headline: the SL signal is real (known paralog-SL pairs are
recovered ~10x above background), but at application scale it opens an existing-drug route hypothesis to
only ~0.5-1% of the undruggable set — synthetic lethality does NOT dissolve the 93% ceiling; it yields a
handful of credible combination hypotheses.**

## SL signal source + paralog list (open; SHA in results/provenance)
- **Paralog universe:** Ryan/De Kegel lab `cancergenetics/paralog_seq_similarity`, `data/ens111_human_SL.csv`
  (Ensembl-111-derived, 23,734 human paralog pairs + entrez IDs + min sequence identity). Downloaded once
  to `$INTERCEPTA_DATA/intervene3/` (ens111 SHA `b59d672f...`, slim SHA `52c46716...`). Its own `SL` column is
  NOT used as our signal (would be circular) — reported only as secondary cross-reference.
- **Known-SL ground truth (G1):** the lab's frozen, externally-curated `validated_SLs.txt` (12 pairs;
  SHA `9173ddce...`) — not chosen by us.
- **Signal = CONDITIONAL differential dependency, deliberately NOT co-dependency correlation.** For a
  direction A->B: split the 988 CRISPR-intersect-expression lines by expr(A) into bottom/top tertiles; test
  whether Chronos(B) is MORE NEGATIVE in A-low lines (one-sided Mann-Whitney + Cliff's delta + median diff).
  Detected = >=1 direction with BH-FDR<0.1 (46,119-test family, p*=4.16e-3) AND median-diff<0 AND delta<=-0.10.

## G1 — recovery of known paralog-SL pairs vs null: PASS
**Recovery = 9/12 (75%)** of the curated known-SL set (all 12 testable), decisively above the
paralog-universe base rate **7.8%** (~10x) and a random non-paralog-pair null **7.4%** (K=5000, seed 42).
Recovered (delta, best direction): FAM50A/FAM50B (-0.97), MAGOH/MAGOHB (-0.54), VPS4A/VPS4B (-0.39),
ENO1/ENO2 (-0.38), DDX5/DDX17 (-0.36), STAG1/STAG2 (-0.35), SMARCA2/SMARCA4 (-0.37), UBB/UBC (-0.26),
SMARCC1/SMARCC2 (-0.13). **3 honest misses:** ARID1A/ARID1B (delta=-0.12, q=0.107 — a borderline near-miss),
CREBBP/EP300 (no effect, delta~0), ME2/ME3 (no effect) — the latter two are known to be context-specific
(metabolic/glutamine or complex-dependent), not captured by a lineage-agnostic expression-tertile split.

## MANDATORY honesty caveat (first-class) — the conditional test is pervasively CONFOUNDED
The paralog-universe base rate (**7.8%**) is essentially equal to the random **non-paralog** null
(**7.4%**), and both are **~15-1000x** above what independence predicts for our thresholds. Interpretation:
- The "detected" flag is **NOT paralog-specific in aggregate** — expression tertiles co-vary strongly with
  lineage / subtype / general fitness, so ~7-8% of *arbitrary* gene pairs show a spurious conditional
  differential-dependency effect. This is exactly the confounding the field is cautious about, and it is
  distinct from (but adjacent to) the co-dependency-correlation false equivalence we guarded against.
- G1 still holds because bona-fide curated SL pairs are recovered at **75% — ~10x the confounded
  background** — i.e., real SL carries signal well above even the inflated floor. But it means **per-hit
  precision at genome scale is low**: most genome-wide "detections" are confounds, not SL. The application
  numbers below must be read through this lens (why we add a sequence-identity credibility filter).

## G2 — drugged SL route to the undruggable set (DESCRIPTIVE) — the vision number
Of INTERVENE2's **3416** UNDRUGGED validated selective dependencies:
| stage | n | fraction of 3416 |
|---|---|---|
| has ANY paralog partner | 1077 | 31.5% |
| has a DepMap-detected paralog-SL partner | 406 | 11.9% |
| **...partner IS drugged (ChEMBL)** | **25** | **0.73%** |
| ...partner has an APPROVED drug (max_phase 4) | 16 | 0.47% |

**Sequence-identity credibility filter** (true buffering paralogs have higher identity; low-id hits are
likely lineage confounds): drugged-SL targets with partner seq-id >=0.20 = **16** (10 approved); >=0.30 =
**9** (6 approved). So the *credible* existing-drug SL-route count is ~**9-16 of 3416 undrugged targets
(~0.3-0.5%)**. Patient-driver (IntOGen) subset: **3/192 (1.6%)** undrugged drivers gain a drugged SL route.

**Most credible examples** (undrugged target -> drugged/approved SL partner; high identity, strong effect):
CCND2->CCND1 (id 0.62, CDK/cyclin-D inhibitor, p 1e-13, driver), CUL4B->CUL4A (0.69, CRL4 inhibitor,
p 2e-8), RPL22L1->RPL22 (0.70, p 7e-6), PIK3R2->PIK3R1 (0.59, PI3K inhibitor, p 8e-5),
PPP6C->PPP2CB (0.58, PP2A, p 4e-6, driver), TUBE1/TUBD1/TUBG2->alpha-tubulins (tubulin agents). Low-identity
hits (ATRN->LAMB3 0.09, LMTK2->DDR2 0.06, TNXB->ANGPT2 0.03) are most likely confounds, not SL — excluded by
the credibility filter.

## Honest verdict + scope
- **The SL signal is real** (G1: known pairs recovered ~10x above background) — a validated, reproducible
  DepMap paralog-SL test.
- **But it does NOT materially open the 93% undruggable ceiling.** Only ~0.5-1% (<=25, credibly ~9-16) of
  the 3416 undrugged validated dependencies gain an existing-drug SL-partner *hypothesis*; the rest have no
  paralog, no detected SL partner, or only an undrugged partner. Synthetic lethality is a **narrow,
  high-value supplement** (a few credible combination hypotheses such as CCND2->CDK4/6i, PIK3R2->PI3Ki), not
  a route around undruggability at scale.
- **HARD SCOPE:** DepMap paralog-SL is an **in-silico genetic-interaction signal**, NOT a validated drug
  combination and NOT clinical; a "drugged SL partner" is a **hypothesis for a combination/context
  experiment**. "Drugged" = has a ChEMBL ligand, NOT efficacious/selective/safe. **Co-dependency
  correlation != SL** (guarded by the conditional expression-tertile definition + curated known-pair
  validation + two nulls); AND the conditional test is itself confounded by lineage/expression structure
  (base rate ~= non-paralog null), which is why per-hit precision is low and the credibility filter is
  applied. Cancer cell-line Chronos layer; not wet-lab, not patient response, not a novel-pathogen result.

## Reproducibility
`run.py` -> `results/INTERVENE3_metrics.json` (sorted keys) + `results/INTERVENE3_payload.sha256`. Payload =
sorted-key JSON of numeric results (excludes verdict/provenance); run twice, byte-identical
(`ae8535da02857c8be4aebe10d232793169b337a0646c5cac23fb563365f331b8`). Seed 42, K=5000, CPU-only. Inputs
open (DepMap Chronos+expression, De Kegel paralog list, ChEMBL KB). No git commit/push; no data committed.
