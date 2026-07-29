"""B19 — is V19 genuine cross-lineage transfer or AML-lineage memorization?
Retrains the FLT3-dependency model EXCLUDING AML lines (S1) and all blood/lymphoid lines (S2), re-infers on
BeatAML, and re-runs the exact V19 tests (H1 beyond-ITD meta beta; H2 ITD-wildtype pooled rho, prolif-adjusted).
S0 (full DepMap) must reproduce V19. Implements prereg/B19_lineage_leakage.md. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.axes import compute_r_prolif

HERE = os.path.dirname(os.path.abspath(__file__))
FLT3I = ["sorafenib", "quizartinib", "gilteritinib", "crenolanib"]
META = "/Users/kalki/kaalcura/data/depmap_meta.csv"
MIN_N, MIN_WT = 25, 15

def z(a): a = np.asarray(a, float); s = a.std(); return (a - a.mean()) / s if s > 0 else a - a.mean()
def pos(x):
    s = str(x).strip().lower(); return 1.0 if s in ("positive","yes","mutated","pos") else (0.0 if s in ("negative","no","wildtype","wt","neg") else np.nan)

# fixed engine (feature genes + fit) reused across scenarios; only the dependency-training CRISPR set changes
eng = InterceptaEngine().fit(drugs=FLT3I, compute_calibration=False, label_source="prism")
ce_full = D.load_depmap_crispr()
meta = pd.read_csv(META).set_index("DepMap_ID")
aml_ids = set(meta.index[meta["Subtype"].astype(str).str.contains("AML", case=False, na=False)])
heme_ids = set(meta.index[meta["lineage"].astype(str).isin(["blood", "lymphocyte"])])

bx = D.load_beataml_expression()
Rp = compute_r_prolif(bx)
auc = D.load_beataml_auc(); auc = auc[auc["sample"].isin(set(bx.columns))]
clin = pd.read_excel(os.path.join(os.environ.get("INTERCEPTA_BEATAML", "/Users/kalki/INTERCEPTA/data/beataml"),
                                  "beataml_wv1to4_clinical.xlsx"))
clin = clin.dropna(subset=["dbgap_rnaseq_sample"]).drop_duplicates("dbgap_rnaseq_sample").set_index("dbgap_rnaseq_sample")
itd = clin["FLT3-ITD"].map(pos)

def v19_tests(dep):
    """dep: Series per BeatAML sample (gene-effect; more negative=more dependent). Returns H1/H2 like B16."""
    rows, itdwt = [], []
    for drug in FLT3I:
        a = auc[auc["drug"] == drug].groupby("sample")["auc"].mean()
        S = [s for s in a.index if s in dep.index and s in itd.index and np.isfinite(itd[s]) and s in Rp.index]
        if len(S) < MIN_N: continue
        y = a[S].values.astype(float); dv = dep[S].values.astype(float); it = itd[S].values.astype(float); rp = Rp[S].values.astype(float)
        res = sm.OLS(y, sm.add_constant(np.column_stack([z(dv), it, z(rp)]), has_constant="add")).fit()
        b, se = float(res.params[1]), float(res.bse[1])
        wt = [i for i in range(len(S)) if it[i] == 0]
        rwt = stats.spearmanr(dv[wt], y[wt])[0] if len(wt) >= MIN_WT else np.nan
        rows.append((b, se))
        if np.isfinite(rwt): itdwt.append((len(wt), float(rwt)))
    # H1 DL meta of dep coefficient
    b = np.array([r[0] for r in rows]); se = np.array([r[1] for r in rows]); w = 1 / se**2
    muf = np.sum(w*b)/np.sum(w); Q = np.sum(w*(b-muf)**2); k = len(b)
    tau2 = max(0, (Q-(k-1))/(np.sum(w)-np.sum(w**2)/np.sum(w))) if k > 1 else 0
    wr = 1/(se**2+tau2); mu = float(np.sum(wr*b)/np.sum(wr)); semu = float(np.sqrt(1/np.sum(wr)))
    p1 = float(2*stats.norm.sf(abs(mu/semu))); H1 = bool(mu > 0 and p1 < 0.05)
    # H2 pooled ITD-WT rho (Fisher-z, sample-size weighted, one-sided sensitizing)
    ns = np.array([x[0] for x in itdwt]); rs = np.array([x[1] for x in itdwt])
    zc = np.arctanh(np.clip(rs, -.999, .999)); zmu = np.sum(zc*(ns-3))/np.sum(ns-3); Z = zmu*np.sqrt(np.sum(ns-3))
    rho = float(np.sum(ns*rs)/np.sum(ns)); p2 = float(stats.norm.sf(Z)); H2 = bool(rho > 0 and p2 < 0.05)
    return {"H1_meta_beta": round(mu, 3), "H1_p": p1, "H1_pass": H1,
            "H2_itdwt_rho": round(rho, 4), "H2_p": p2, "H2_pass": H2, "n_drugs": int(k)}

scenarios = {
    "S0_full":        (set(),      "CONTROL: full DepMap (must reproduce V19)"),
    "S1_exclude_AML": (aml_ids,    "PRIMARY: AML lines removed (model never saw AML)"),
    "S2_exclude_heme":(heme_ids,   "STRINGENT: all blood/lymphoid removed (near FLT3 biological floor)"),
}
results = {}
for name, (excl, desc) in scenarios.items():
    ce = ce_full.drop(index=[i for i in excl if i in ce_full.index]) if excl else ce_full
    n_train = int(ce["FLT3"].notna().sum())
    eng.fit_dependency(["FLT3"], crispr_df=ce)
    dep = eng.infer_dependency(bx)["FLT3"]
    r = v19_tests(dep); r["n_train_cells_FLT3"] = n_train; r["desc"] = desc
    results[name] = r
    print(f"{name:<16} train={n_train:>4}  H1 beta={r['H1_meta_beta']:+.2f} p={r['H1_p']:.2e} ({r['H1_pass']}) | "
          f"H2 ITD-WT rho={r['H2_itdwt_rho']:+.3f} p={r['H2_p']:.2e} ({r['H2_pass']})  {desc}", flush=True)

s0 = results["S0_full"]; s1 = results["S1_exclude_AML"]
s0_ok = bool(s0["H1_pass"] and s0["H2_pass"])           # control sanity
H_primary = bool(s1["H1_pass"] and s1["H2_pass"])
if not s0_ok:
    verdict = "PIPELINE ERROR: control (full DepMap) did not reproduce V19 — halt, do not interpret."
elif H_primary:
    verdict = ("V19 SURVIVES an AML-naive dependency model (S1): inferred-FLT3-dependency predicts FLT3i response "
               "beyond ITD and within ITD-WT even when the model NEVER saw AML lines -> genuine CROSS-LINEAGE "
               "functional transfer, NOT AML-lineage memorization. Memorization critique defeated.")
else:
    verdict = ("HONEST DOWNGRADE: V19 signal depends on AML lines in dependency-model training (S1 fails) -> the "
               "inferred-dependency is partly AML-lineage-entangled, not purely cross-lineage transfer.")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "n_aml_excluded": len(aml_ids & set(ce_full.index)), "n_heme_excluded": len(heme_ids & set(ce_full.index)),
       "scenarios": results, "control_reproduces_V19": s0_ok, "H_primary_pass": H_primary, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B19_metrics.json"), "w"), indent=2)
print("wrote results/B19_metrics.json")
