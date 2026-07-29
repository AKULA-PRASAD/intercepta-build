# INTERCEPTA — April 8, 2026 End of Marathon

## BUILD STATUS (9 blocking items → 7 remaining)
| Build | Status |
|-------|--------|
| Scout 4 v1 | Dependency works, compensation WRONG |
| Scout 4 v2 | NEEDS: Boolean network + directed edges |
| Unified ODE | NOT STARTED |
| Synergy scoring | NOT STARTED |
| AML ODE | NOT STARTED |
| ADMET complete | PARTIAL (RDKit only) |
| Synthesizability | NOT STARTED |
| Pareto ranking | NOT STARTED |

## WHAT SCOUT 4 v2 NEEDS (from research)
1. Directed edges from Signor 3.0 (33K causal relationships)
   or KEGG pathway direction info
2. Boolean logic rules: gene ON if (activator1 OR activator2) AND NOT inhibitor
3. Steady-state attractors: disease state vs healthy state
4. Perturbation: set target OFF, find new attractor
5. Compensation = genes that flip ON in new attractor
6. Expression filter: DICE hematopoietic for AML, GTEx prostate for mCRPC
7. Validate: FLT3 perturbation → compensators match BeatAML resistance

## References for proper implementation
- Montagud et al. eLife 2022: Boolean models for prostate cancer
- PDGrapher Nature BME 2025: GNN for combinatorial perturbations
- NetPert PLOS CompBio 2024: network perturbation theory
- Signor 3.0: 33K directed causal relationships

## TWO-DISEASE FINDINGS (honest)
- mCRPC: enza+alisertib (escape route validated)
- AML: p38 MAPK in DNMT3A/IDH2 (patient data, 165+100 patients)
- AML: DNMT3A→EZH2 escape (biologically correct)
- AML: TET2→JAK2 escape (biologically correct)
