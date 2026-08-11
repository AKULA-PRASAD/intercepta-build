# GENETICCLASS1 — disease-class deployment envelope for zero-data genetic target-ID: RESULT

**Reproduced ×2 byte-identical (`payload.sha256` = ffaa351…). Genome-wide universe (20,596 protein-coding genes
× 27 diseases), 6 frozen disease classes, validated on cached Open Targets clinical-precedence.** Extends the
transfer-condition principle from ORGANISM classes (the FBA arm) to DISEASE classes for the human-genetics arm.
**Hypothesis (non-uniform transfer across classes): PASS** — the envelope discriminates.

## The disease-class transfer table (the deliverable)
| class (n diseases) | Mantel–Haenszel OR (95% CI) | fame-adjusted genassoc coef (95% CI) | GRADE |
|---|---|---|---|
| respiratory_fibrotic (2) | **3.19** [2.25, 4.54] | +0.138 [+0.095, +0.182] | FULL* |
| cardiovascular (3) | **2.50** [1.95, 3.21] | +0.090 [+0.052, +0.128] | FULL |
| neuro_psychiatric (6) | **2.17** [1.82, 2.58] | +0.125 [+0.098, +0.151] | FULL |
| immune_inflammatory (10) | **2.13** [1.85, 2.46] | +0.100 [+0.078, +0.122] | FULL |
| metabolic (3) | 1.61 [1.26, 2.06] | +0.085 [+0.041, +0.129] | CAPPED |
| musculoskeletal_renal (3) | 1.32 [0.94, 1.86] | +0.040 [−0.012, +0.091] | ABSTAIN |

Grades per the pre-registered gate (FULL: MH-OR CI-lo>1.5 AND fame-coef CI-lo>0; CAPPED: MH-OR CI-lo>1.0;
ABSTAIN: MH-OR CI-lo≤1.0). Result: **4 FULL, 1 CAPPED, 1 ABSTAIN.**

## Honest reading
- **Zero-data genetic target-ID transfers robustly (FULL, fame-adjusted) in cardiovascular, immune/inflammatory,
  neuro-psychiatric, and respiratory/fibrotic disease classes** — genetic support enriches ~2–3× for clinical
  drug-target precedence, and the signal survives the fame (publication-bias) confound GENETICS1 flagged.
- **metabolic = CAPPED:** real and fame-robust, but weaker (MH-OR CI-lower 1.26 < 1.5) → fire at reduced confidence.
- **musculoskeletal_renal = ABSTAIN:** no robust class-level signal (MH-OR CI includes ~1; fame-adjusted coef CI
  includes 0) → the router should abstain (or flag low-confidence) for genetic target-ID here.

## Where my pre-registered guess was WRONG (reported first-class)
I predicted psychiatric/neuro would be the WEAK class. **It is not** — neuro_psychiatric is FULL (fame-coef
+0.125, the second-strongest). The genuine weak/abstain class is **musculoskeletal_renal**. The core hypothesis
(non-uniformity) held; my directional guess about *which* class fails did not. Stated honestly, not hidden.

## Caveats (bind the claim)
- **AUROC ≈ 0.51–0.53 per class is expected, not a failure:** genome-wide, ~79% of genes have genassoc=0, so the
  continuous-score AUROC is near-0.5 (the MR1 pattern); the meaningful metric is the binary genassoc>0 → drug
  enrichment (MH-OR), which is what the gate uses.
- **respiratory_fibrotic FULL rests on only 2 diseases (COPD, IPF)** → wide CI; treat as provisional-FULL (marked *).
- Coverage-characterization of an existing validated arm across disease classes — **not a new method**, and OT
  clinical-precedence (retrospective) is the ground truth, not clinical validation.

## Contribution / integration
`disease_class_transfer_table.json` makes the human-genetics target-ID arm **disease-class-aware** (the analog of
the FBA arm's organism-class transfer table) with cited per-class abstention — a genuine extension of the
composite's honest decision-coverage across the human-disease universe. Reproduce: `python build_geneticclass1.py`.
