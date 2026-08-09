# AFFINITY1 benchmark fixtures (small, versioned INPUTS)

These are the tiny (<420 KB total) INPUT fixtures the AFFINITY1 zero-shot co-folding benchmark needs,
committed so the experiment runs anywhere (HPC/CI) with no external staging. This is deliberate and
distinct from the large GENERATED data (boltz structures, MSAs, affinity JSONs) which stays out of
git in $INTERCEPTA_DATA.

- `thrombin_vina.tsv`  — HIT2 AutoDock Vina docking baseline on the 553 MoleculeACE thrombin test
  compounds (idx, active, pact, vina, smiles). The head-to-head baseline (full-set docking AUROC 0.4285).
- `test_novelty.csv`   — derived novelty split (idx, smiles, pact, active, nn_tan, novelty[analog|novel]).
- `CHEMBL204_Ki.csv`   — public MoleculeACE thrombin Ki dataset (provenance/source; not read at runtime).

run.py reads test_novelty.csv + thrombin_vina.tsv from here; all outputs go to
$INTERCEPTA_DATA/affinity1 (scratch on HPC).
