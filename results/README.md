# results/ — aggregate outputs (safe subset)

Non-patient, non-binary aggregate outputs of the INTERCEPTA pipeline (net layers, ODE validations, scout
rankings, molecule lists, audit JSONs). **Excluded:** all per-patient/per-cell matrices, all controlled-data-
derived tables, and bulky binaries (.parquet/.gpickle/.arrow/.h5ad/.rds) — reproduce those from
`../data/MANIFEST.md`. Every file here was scanned to contain no patient identifiers.

> ⚠️ **Read filenames against `../LEDGER.md` and `../docs/audits/` — several are historically MISLABELED:**
> - `*denovo*molecules*.csv` → these are **scaffold-hopped** analogues, NOT de novo generated molecules.
> - `phase1_5trial_VALIDATED.*` → the "5/5 validated" claim was **retracted**; real result is 2/6 (Cox PH).
> - `pharma_deliverable_*.json`, `INTERCEPTA_FINAL_package.json` → MoA/safety/synthesis text was **hand-written**, not model-derived (VISION_AUDIT).
> - `pareto_ranking_*.json` → some ranking dimensions were **human-assigned** inputs.
> - `lead_candidate_INTC002.json` → a **computational hypothesis** (ChEMBL novelty 0.266), not a validated drug.
> The authoritative, verified results are in `../LEDGER.md`, `../verification/`, and `../experiments/`.

## Excluded large derived outputs (regenerable)
A few "net" graph JSONs are too large to commit and are **regenerable** from `../engine/net/` + `../data/MANIFEST.md`:
`mcrpc_unified_net.json` (51 MB), `round3_gbm/gbm_disease_net_action1.json` (12 MB), and gbm `phase2b/c/d`
(3.8–5.7 MB). The smaller disease-net outputs (AML, NSCLC, pancreatic, PDAC, Alzheimer, TB, GBM base/phase2a)
ARE included here.
