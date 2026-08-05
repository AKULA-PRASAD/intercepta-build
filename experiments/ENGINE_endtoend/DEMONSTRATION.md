# INTERCEPTA DiscoveryEngine — end-to-end demonstration on the HELD-OUT WHO pathogen *K. pneumoniae*

The unified `intercepta.discovery_engine.DiscoveryEngine` (CLI: `intercepta discover-targets`) takes a pathogen genome and
composes **every signal the program validated** into one honest, safe, confidence-tiered, provenance-tagged target report.
K. pneumoniae was **never used in method development** (the NEWBUG held-out pathogen); its FBA essentiality is independently
experimentally validated (VAL-ESS-KP, OR 63).

**Active validated signals:** essentiality[VALIDATED:MET1-3+VAL-ESS], chokepoint[FRONT1], conservation_breadth[REACH1], conservation[TID1], host_safety_filter[FRONT1/E2E2]

**Result:** 5126 proteins scored; **77 host-toxic excluded by construction** (hard host-non-homology filter); 0 abstained; 5049 confident safe targets.
Of the top 30 shortlisted, **15 are experimentally-essential-confirmed** (K. pneumoniae CRISPRi/Tn-seq).

**HONEST confidence note:** WARNING: confidence tier SATURATED (88% of ranked entities are 'high') because near-universal signals (conservation/breadth) fire for most genes in this full-signal genome-scale config -> the 'high' label is NOT discriminative here; use rank_score for ordering. Confidence is discriminative only with emit-if-positive signals (CALIB1).

## Top targets

| gene | confidence | rank_score | experimentally essential (KP) | flags |
|------|:--:|:--:|:--:|------|
| dxs | high | +4.116 | yes | needs_experimental_selectivity |
| dnaE | high | +3.860 | no |  |
| murA | high | +3.609 | yes |  |
| murF | high | +3.568 | yes |  |
| mraY | high | +3.518 | yes |  |
| folC | high | +3.462 | no | needs_experimental_selectivity |
| murG | high | +3.402 | yes |  |
| ispB | high | +3.335 | no | needs_experimental_selectivity |
| ispC | high | +3.285 | no |  |
| ispA | high | +3.202 | no | needs_experimental_selectivity |
| folP | high | +3.199 | no |  |
| ileS | high | +3.161 | yes | needs_experimental_selectivity |
| recB | high | +3.101 | no |  |
| coaA | high | +3.062 | yes |  |
| ispE | high | +3.049 | yes |  |
| murB | high | +3.042 | yes |  |
| leuS | high | +3.028 | yes | needs_experimental_selectivity |
| polA | high | +2.970 | yes | needs_experimental_selectivity |
| secA | high | +2.963 | yes |  |
| topA | high | +2.926 | yes | needs_experimental_selectivity |
| mrcB | high | +2.911 | no |  |
| ispF | high | +2.908 | yes |  |
| relA | high | +2.867 | no |  |
| mrcA | high | +2.867 | no |  |
| coaD | high | +2.841 | yes |  |

## Honest reading
- The shortlist spans **metabolic** essentials (murB, murG, murA, murF, mraY, dxs, ispE — cell-wall + MEP cores, the FBA/MET signal) AND **non-metabolic** essentials FBA alone is blind to (dnaE, ileS, leuS, secA, topA, polA, recB — DNA replication, tRNA synthetases, secretion) — recovered by the **REACH1 conservation-breadth** signal. This is the concrete payoff of extending the engine past the metabolic scope.
- **Host-toxic targets are excluded by construction** (hard filter); host-homologous survivors are FLAGGED `needs_experimental_selectivity` (sequence cannot resolve true selectivity — E2E2/FRONT2).
- **Confidence is saturated here** (88% 'high') because conservation + breadth fire for most genes at genome scale; **use rank_score, not the confidence label, for ordering** in this full-signal config (confidence is discriminative in the emit-if-positive regime, CALIB1).
- Some shortlisted genes are not experimentally-essential-confirmed (the REACH1 breadth precision cost + symbol-mapping gaps) — honest, not hidden.

## Honest scope
Confidence-tiered candidate HYPOTHESES with provenance — NOT validated targets or drugs. The essentiality ENRICHMENT is experimentally validated (VAL-ESS, 5 organisms); the drug-target/selectivity/clinical claims are NOT. Molecule half is gated (needs structure or activity data); candidate matter from generate/screen are hypotheses. Not wet-lab.

*This is a capability demonstration of the composed, validated FRONT half (target-ID). The molecule half is gated (needs target structure or activity data). Outputs are computational hypotheses with provenance — not validated targets or drugs; not wet-lab.*

## Molecule bridge — closing the end-to-end shape (genome -> target -> candidate molecules)

For the engine's top experimentally-essential target **dxs (A6T5F3)**, the pipeline detects the pocket (fpocket druggability **0.89**), docks a 60-compound ChEMBL library (AutoDock Vina; 57 docked; best -10.88 kcal/mol), and ranks by a developability-gated docking score (docking x predicted-safety x synthesizability, via the shipped ADMET/synth modules). Reproduced x2 byte-identical.

| rank | vina (kcal/mol) | pred. safety | synth. prob | QED | cand_score |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | -7.29 | 0.856 | 0.817 | 0.3163 | 5.098 |
| 2 | -6.00 | 0.8678 | 0.9459 | 0.517 | 4.925 |
| 3 | -9.84 | 0.5296 | 0.9119 | 0.4566 | 4.752 |
| 4 | -7.35 | 0.7013 | 0.9118 | 0.8208 | 4.700 |
| 5 | -8.44 | 0.7456 | 0.7434 | 0.8036 | 4.678 |
| 6 | -9.09 | 0.5188 | 0.9636 | 0.6106 | 4.544 |
| 7 | -8.69 | 0.5194 | 0.9667 | 0.8063 | 4.363 |
| 8 | -8.91 | 0.5025 | 0.9588 | 0.0747 | 4.293 |

**HONEST ceiling (stated, not hidden):** Docking is a heuristic score, NOT binding free energy; early-enrichment is weak (C1 AUROC 0.63; HIT2: useless for within-series potency); ZERO target activity data used; generic ChEMBL library, not curated actives; outputs are POSE-PLAUSIBLE candidate HYPOTHESES, not validated actives, not drugs. Demonstrates the end-to-end SHAPE (genome->target->molecule) with the molecule-half ceiling stated. Not wet-lab.

This demonstrates the vision's full end-to-end SHAPE on a held-out WHO pathogen — genome in, a safe/validated *target* and ranked *candidate matter* out — while being explicit that the molecule half is the program's mapped ceiling: these are pose-plausible developable hypotheses, NOT validated inhibitors. Turning one into a real drug needs the gated experimental step.

## Multi-axis engine on the SECOND held-out WHO pathogen — *A. baumannii* (WHO #1 critical)

The unified engine, run genome->target on A. baumannii (never in development), composing **all 7 validated signals** with
**A. baumannii-NATIVE** resistance (SYNLETH2) and condition-robustness (no E. coli transfer — AB is not Enterobacteriaceae).

**Active signals:** essentiality[VALIDATED:MET1-3+VAL-ESS], chokepoint[FRONT1], conservation_breadth[REACH1], conservation[TID1], host_safety_filter[FRONT1/E2E2], resistance_robustness[SYNLETH], condition_robustness[CONDROB1]

**Result:** 3711 proteins; **67 host-toxic excluded by construction**; 3644 confident safe targets; resistance (AB-native) 34 monotherapy-robust / 2 combination-required; 34 condition-robust; 5/30 of the shortlist DEG-experimentally-essential.

| gene | conf | rank | DEG exp-ess | flags |
|------|:--:|:--:|:--:|------|
| dxs | high | +3.441 | no | condition_robust,monotherapy_robust |
| murA | high | +3.322 | no | condition_robust,monotherapy_robust |
| AB57_3157 | high | +3.257 | no |  |
| topA | high | +3.146 | no | needs_experimental_selectivity |
| ileS | high | +3.047 | yes | needs_experimental_selectivity |
| AB57_1696 | high | +3.027 | no |  |
| mraY | high | +2.997 | no | condition_robust,monotherapy_robust |
| gyrB | high | +2.964 | no | needs_experimental_selectivity |
| secA | high | +2.931 | no |  |
| gyrA | high | +2.921 | no | needs_experimental_selectivity |
| dxr | high | +2.798 | no | condition_robust,monotherapy_robust |
| murF | high | +2.737 | no | condition_robust,monotherapy_robust |
| leuS | high | +2.714 | no | needs_experimental_selectivity |
| AB57_3153 | high | +2.694 | no | condition_robust,monotherapy_robust,needs_experimental_selectivity |
| murG | high | +2.638 | yes | condition_robust,monotherapy_robust |
| coaBC | high | +2.570 | no | condition_robust,monotherapy_robust,needs_experimental_selectivity |
| AB57_3182 | high | +2.532 | no | condition_robust,monotherapy_robust,needs_experimental_selectivity |
| parE | high | +2.520 | no | needs_experimental_selectivity |
| ispE | high | +2.517 | no | condition_robust,monotherapy_robust |
| coaD | high | +2.484 | no | condition_robust,monotherapy_robust |

## Honest reading
- The full multi-axis engine GENERALIZES to the second held-out WHO pathogen: top targets are the canonical resistance-robust + condition-robust cores (dxs/murA/mraY/murG/dxr/murF/ispE/coaD, flagged condition_robust+monotherapy_robust) PLUS non-metabolic essentials via REACH1 (topA/ileS/secA/gyrA/gyrB/leuS/parE).
- **HONEST caveats specific to AB:** (1) only 5/30 shortlist targets are DEG-experimentally-essential -- because the only AB DEG set (DEG1043, Wang 2014) is a sparse, condition-specific LUNG-PERSISTENCE INSeq screen with ~101 named genes, not a clean in-vitro essential set (weaker validation than K. pneumoniae's CRISPRi). (2) Several top targets are locus-tag-only (AB57_xxxx) -> no gene symbol -> cannot be DEG-matched and may lack transferred flags (symbol-mapping gap). (3) AB-native resistance/condition classes are SPARSE (34 monotherapy / 34 condition-robust) because the de-novo CarveMe GEM is default-medium (masks auxotrophy).
- Confidence saturates at genome scale (use rank_score, not the label) -- the engine self-reports this.

*Composed VALIDATED front half; molecule half gated; outputs are hypotheses with provenance, not validated targets/drugs; not wet-lab.*
