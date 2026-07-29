# Examples & quickstart

## 0. Install
```bash
pip install -e .          # from the repo root
pytest -q                 # 12 data-free unit tests should pass
```

## 1. Zero-download demo (30 seconds, no data setup)
```bash
python examples/demo.py
```
Runs the **real** engine machinery on a small synthetic scenario and shows the three things that matter:
1. **Transfer ranking** recovers a planted sensitivity signal (separates sensitive vs resistant samples).
2. The **verified-marker bonus** (NRAS → MEK inhibitor) is additive and directional.
3. **OOD gating** flags samples far from the training distribution as low-trust — the engine's honest confidence.

It is an *illustration of the mechanics*, not a validation. Real, honestly-bounded performance is in
[`../LEDGER.md`](../LEDGER.md) and [`../papers/intercepta_engine/MANUSCRIPT.md`](../papers/intercepta_engine/MANUSCRIPT.md).

## 2. Run the real engine on public data
The engine trains on public cell-line data (DepMap RNA-seq + GDSC/PRISM labels). Point `INTERCEPTA_DATA` at a
directory holding the files listed in [`../data/MANIFEST.md`](../data/MANIFEST.md) (sha256-verified at load), then:

```python
from intercepta.engine import InterceptaEngine
import pandas as pd

eng = InterceptaEngine().fit(drugs=["trametinib", "selumetinib"], label_source="prism")
expr = pd.read_csv("my_cohort_expression.csv", index_col=0)     # genes (rows) x samples (columns)
ranking = eng.rank(expr)                                        # per-sample drug ranking + OOD confidence
print(ranking.sort_values(["sample", "combined_score"], ascending=[True, False]).head())
```

Or via the CLI:
```bash
intercepta info                                                 # version + honest scope
intercepta rank --expr my_cohort_expression.csv --drugs trametinib,selumetinib --out ranking.csv
```

## 3. Reproduce any headline result
Every result maps to a committed metrics JSON, reproduced ×2:
```bash
python experiments/B1_baseline_ceiling/run.py                   # the +0.212 transfer ceiling (Fig 1)
python experiments/B22_modality_ceiling/run.py                  # proteomics doesn't break it (V21)
python papers/intercepta_engine/figures/make_figures.py         # regenerate all figures from metrics
```
BeatAML-dependent experiments require your own dbGaP access (phs001657, controlled); all other inputs are public.

## Honest scope (read before using)
INTERCEPTA is a **research hypothesis-ranking tool**, validated only at the cell-line/ex-vivo level. It is **not**
a validated human clinical predictor — human clinical drug response was a well-powered null once cancer type was
controlled (B10), and the functional-inference refinement failed external replication (B20/B21). Every prediction
is LOW/MODERATE confidence by design. Do not use for clinical decisions.
