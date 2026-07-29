"""INTERCEPTA engine — self-contained, ZERO-DOWNLOAD demo.

Runs the REAL engine machinery (InterceptaEngine.rank / predict_transfer / ood_score) on a small SYNTHETIC
scenario so you can see, in seconds and with no data setup, exactly what the engine does and how it reports
confidence. This is an ILLUSTRATION of the mechanics, NOT a validation or a performance claim — real, honestly-
bounded performance is in LEDGER.md and papers/intercepta_engine/MANUSCRIPT.md (cell-line/ex-vivo only; NOT a
validated human clinical predictor).

Run:  python examples/demo.py
"""
import sys, os, warnings; warnings.filterwarnings("ignore")   # benign macOS BLAS matmul warnings
import numpy as np, pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine

rng = np.random.default_rng(42)
G, C = 200, 150                                   # 200 genes, 150 synthetic "training cell lines"
genes = [f"G{i}" for i in range(G)]
# reserve two real marker genes so the verified-marker bonus is demonstrable
genes[0], genes[1] = "NRAS", "FLT3"
SENS = list(range(2, 12))                         # genes 2..11 drive sensitivity to the two demo drugs

# ---- synthetic training cell lines (genes x cells), z-scored exactly as the engine does ----
train = pd.DataFrame(rng.normal(size=(G, C)), index=genes, columns=[f"cell{i}" for i in range(C)])
dxz = D.z_rows(train).fillna(0.0)                 # genes x cells (engine's internal representation)

# planted truth: higher expression of SENS genes -> LOWER IC50 (more sensitive) for both demo drugs
w = np.zeros(G); w[SENS] = rng.uniform(0.6, 1.0, len(SENS))
Xtrain = dxz.T.values                             # cells x genes
resp_trametinib = -(Xtrain @ w) + 0.3 * rng.normal(size=C)   # LN_IC50-like: lower = sensitive
resp_selumetinib = -(Xtrain @ w) + 0.3 * rng.normal(size=C)

# ---- assemble a REAL engine with this synthetic state (mirrors what .fit() builds) ----
eng = InterceptaEngine()
eng.genes_ = genes
eng._dxz = dxz
eng.models_ = {"trametinib": RidgeCV(alphas=eng.alphas).fit(Xtrain, resp_trametinib),
               "selumetinib": RidgeCV(alphas=eng.alphas).fit(Xtrain, resp_selumetinib)}
eng.fitted_drugs_ = sorted(eng.models_)
eng._pca = PCA(n_components=20, random_state=42).fit(Xtrain)          # OOD detector (as in .fit())
eng._nn = NearestNeighbors(n_neighbors=10).fit(eng._pca.transform(Xtrain))

# ---- query cohort: 4 "sensitive-like", 4 "resistant-like", + 2 out-of-distribution samples ----
def make_sample(sensitive, ood):
    if ood:                                        # genuinely off-distribution: different covariance structure
        return rng.normal(0.0, 4.0, G)             # (not just a mean shift, which per-query z-scoring would absorb)
    x = rng.normal(size=G)
    x[SENS] += (2.0 if sensitive else -2.0)        # push the sensitizer genes
    return x
cols, meta = [], []
for i in range(4): cols.append(make_sample(True, False));  meta.append(("sens", "S%d" % i))
for i in range(4): cols.append(make_sample(False, False)); meta.append(("res", "R%d" % i))
for i in range(2): cols.append(make_sample(True, True));   meta.append(("sens+OOD", "O%d" % i))
query = pd.DataFrame(np.array(cols).T, index=genes, columns=[m[1] for m in meta])

# NRAS mutation status (verified marker for trametinib/selumetinib): mark the sensitive samples NRAS-mutant
mutations = pd.DataFrame({"NRAS": [1 if g == "sens" else 0 for g, _ in meta]}, index=query.columns)

# ---- run the engine ----
ranking = eng.rank(query, mutations=mutations)
ood = eng.ood_score(query)

print(__doc__.splitlines()[0])
print("\n=== 1. Transfer ranking recovers the planted signal ===")
grp = {n: g for g, n in meta}
for drug in eng.fitted_drugs_:
    sub = ranking[ranking["drug"] == drug]
    sens = sub[sub["sample"].isin([n for g, n in meta if g.startswith("sens")])]["combined_score"].mean()
    res = sub[sub["sample"].isin([n for g, n in meta if g == "res"])]["combined_score"].mean()
    print(f"  {drug:<12} mean sensitivity-score  sensitive={sens:+.2f}  resistant={res:+.2f}  "
          f"-> {'correctly separates' if sens > res else 'FAILED'}")

print("\n=== 2. Verified-marker bonus (NRAS -> MEK inhibitor) is additive and directional ===")
tr = ranking[ranking["drug"] == "trametinib"].set_index("sample")
print("  sample  group      NRAS  combined_score")
for g, n in meta:
    print(f"  {n:<6}  {g:<9}  {int(mutations.loc[n,'NRAS'])}     {tr.loc[n,'combined_score']:+.2f}")

print("\n=== 3. OOD gating flags samples far from the training distribution (honest confidence) ===")
q1, q3 = np.percentile(ood.values, [25, 75]); thr = q3 + 1.5 * (q3 - q1)   # Tukey outlier rule
for g, n in meta:
    flag = "OUT-OF-DISTRIBUTION (low trust)" if ood[n] > thr else "in-distribution"
    print(f"  {n:<6}  {g:<9}  OOD-distance={ood[n]:.2f}  -> {flag}")
print(f"  (Tukey outlier threshold = {thr:.2f}; OOD samples were built with a different covariance structure.)")

print("\nHONEST SCOPE: synthetic illustration of the mechanics only. The engine is a research hypothesis-ranking "
      "tool validated at the cell-line/ex-vivo level; it is NOT a validated human clinical predictor "
      "(see LEDGER.md / MANUSCRIPT.md). Every real-world prediction is LOW/MODERATE confidence by design.")
