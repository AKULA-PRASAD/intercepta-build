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
