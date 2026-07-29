"""engine v1 validation — does the shipped InterceptaEngine combined score beat its transfer part on real
patients (reproduce V10 through the engine API)? Implements prereg/engine_v1_validation.md. Reproduce x2.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine, VERIFIED_MARKERS, load_beataml_mutation_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = ["trametinib", "selumetinib", "dasatinib", "sorafenib", "cabozantinib"]
print("engine v1 validation | sklearn", sklearn.__version__, flush=True)

eng = InterceptaEngine().fit(drugs=PAIRS)
print("fitted transfer models for:", eng.fitted_drugs_, flush=True)

bx = D.load_beataml_expression()
auc = D.load_beataml_auc()
mut = load_beataml_mutation_matrix()
ranked = eng.rank(bx, mutations=mut)      # long: sample, drug, transfer_z, marker, marker_present, combined_score

rows = []
for dk in eng.fitted_drugs_:
    if dk not in VERIFIED_MARKERS:
        continue
    a = auc[auc["drug"] == dk].groupby("sample")["auc"].mean()
    sub = ranked[ranked["drug"] == dk].set_index("sample")
    common = [s for s in a.index if s in sub.index]
    if len(common) < 15:
        continue
    y = a[common].values
    comb = sub.loc[common, "combined_score"].values
    tz = sub.loc[common, "transfer_z"].values
    rho_comb = stats.spearmanr(comb, y)[0]          # expect negative (higher score -> lower AUC)
    rho_tr = stats.spearmanr(-tz, y)[0]             # transfer-only sensitivity predictor
    beats = bool(rho_comb < rho_tr)                 # more negative = better sensitivity prediction
    rows.append({"drug": dk, "marker": VERIFIED_MARKERS[dk][0], "n": len(common),
                 "rho_combined": round(float(rho_comb), 4), "rho_transfer_only": round(float(rho_tr), 4),
                 "combined_beats_transfer": beats})

n_beat = sum(r["combined_beats_transfer"] for r in rows)
valid = bool(n_beat >= (len(rows) + 1) // 2) if rows else False
print(f"\ntestable verified pairs: {len(rows)}")
for r in rows:
    print(f"  {r['drug']:<13}~{r['marker']:<7} n={r['n']:>3}  rho_combined={r['rho_combined']:+.4f}  "
          f"rho_transfer_only={r['rho_transfer_only']:+.4f}  combined_better={r['combined_beats_transfer']}")
print(f"combined beats transfer-only in {n_beat}/{len(rows)} pairs -> ENGINE VALID (embodies V10)? {valid}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "fitted_drugs": eng.fitted_drugs_, "pairs": rows, "n_pairs": len(rows), "n_combined_beats": n_beat,
       "engine_valid": valid,
       "note": "Re-demonstrates LEDGER V10 through the shipped engine API. Weak effects; one cohort; confidence=LOW."}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "engine_v1_metrics.json"), "w"), indent=2)
print("wrote results/engine_v1_metrics.json")
