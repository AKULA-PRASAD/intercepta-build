# INTERCEPTA engine v1 — honest mechanism-anchored drug-response ranking

`src/intercepta/engine.py` · validated in `experiments/engine_v1_validation/` (reproduced ×2).

## What it is
The first runnable INTERCEPTA engine that wires together **only the verified signals** (`../LEDGER.md`):
1. **Transfer (V1/V9):** per-drug Ridge trained on DepMap RNA-seq → GDSC LN_IC50, applied to a query tumor's
   expression → predicted per-drug resistance (z).
2. **Mechanism markers (genome-wide-robust, from B5):** NRAS→MEK (trametinib/selumetinib), FLT3-ITD→FLT3i
   (sorafenib, cabozantinib). Sourced from the B5 genome-wide screen (BH-FDR + deconfounded + split-replicated).
   NOTE: NPM1→Cabo and DNMT3A→Dasatinib were DROPPED — they did not survive genome-wide correction (LEDGER V4/V6 refinement).
3. **Integration (V10):** `combined_score = −transfer_z + marker_bonus` (higher = predicted more sensitive).

## Usage
```python
from intercepta.engine import InterceptaEngine, load_beataml_mutation_matrix
from intercepta import data as D
eng = InterceptaEngine().fit(drugs=["trametinib","sorafenib",...])   # trains on cell lines
ranked = eng.rank(D.load_beataml_expression(), mutations=load_beataml_mutation_matrix())
# -> [sample, drug, transfer_z, marker, marker_present, combined_score, confidence]
```

## Validation (engine_v1_metrics.json, reproduced ×2)
Combining markers with transfer beats transfer-alone at predicting BeatAML ex-vivo response in **4/4** testable
verified pairs (e.g. sorafenib ρ=−0.47 vs −0.39; selumetinib −0.31 vs −0.25). The engine faithfully embodies
V10 — this re-demonstrates an already-validated result through the shipped code, it is not a new claim.

## HONEST SCOPE — read before trusting any output
- **Confidence is LOW on every prediction, by design.** Most of the ranking correlation is the *generic
  proliferation/chemosensitivity* axis (V8/N1); the *drug-specific, beyond-proliferation* component is weak
  (ρ≈0.04–0.07, V9). Treat outputs as ranked HYPOTHESES, not decisions.
- **Validated on ONE cohort (BeatAML/AML).** Cross-cohort and cross-cancer validity are UNPROVEN — this is the
  next gate (a second patient cohort).
- **Marker adjustments apply only to the verified pairs;** all other drugs are transfer-only.
- **The engine does NOT:** select therapy, generate molecules, or predict trial outcomes (all falsified or
  untested — see `../LEDGER.md`, `../INTEGRITY_SWEEP.md`).
- Cabozantinib (NPM1, V4) is not rankable here — GDSC2 has no cabozantinib to train the transfer model.

## Confidence (B6-validated)
Each prediction carries `ood_distance` + `drug_cv_reliability` + a `confidence` tier. Only the **OOD** axis is
validated (B6/LEDGER V13): samples closer to the cell-line training distribution are measurably more accurate
(+0.051, p=0.0055), so confidence = MODERATE for low-OOD samples, LOW otherwise — **capped at MODERATE** because
absolute accuracy is weak. Per-drug CV reliability did NOT calibrate (B6 H1 null, confirms B3e) and is descriptive
only. No prediction is ever HIGH confidence on current single-cohort evidence.

## Next
`engine v1` is the validated floor. It becomes clinically meaningful only after external replication on a
**second independent patient drug-response cohort** (see repo README "what's next"). Until then it is an honest,
reproducible research engine, not a clinical tool.
