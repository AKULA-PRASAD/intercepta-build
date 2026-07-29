"""B20 — INDEPENDENT external replication of V19 (beyond-mutation FLT3) + V20 (target-specificity) in the
FIMM/Malani AML cohort (Zenodo 7370747, CC-BY 4.0). Different institution/assay than BeatAML (DSS, higher=sensitive).
Implements prereg/B20_fimm_external_replication.md. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.axes import compute_r_prolif

SEED, MIN_N, MIN_WT, NPERM = 42, 25, 15, 10000
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
FIMM = os.path.join(DATA, "fimm_aml", "Functional_Precision_Medicine_Tumor_Board_AML")
FLT3I = ["sorafenib", "quizartinib", "crenolanib", "midostaurin", "sunitinib", "tandutinib", "dovitinib"]
BCL2I = ["venetoclax"]
rng = np.random.default_rng(SEED)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def z(a): a = np.asarray(a, float); s = a.std(); return (a - a.mean()) / s if s > 0 else a - a.mean()
def resid(x, c):
    x = np.asarray(x, float); c = np.asarray(c, float); A = np.column_stack([np.ones_like(c), c])
    b, *_ = np.linalg.lstsq(A, x, rcond=None); return x - A @ b
def padj_rho(dv, y, rp):  # proliferation-adjusted Spearman
    return float(stats.spearmanr(resid(dv, rp), resid(y, rp))[0])
def pooled(pairs):  # [(n,rho)] -> sample-size-weighted rho + one-sided Stouffer p (sensitizing = rho>0)
    if not pairs: return None
    ns = np.array([p[0] for p in pairs]); rs = np.array([p[1] for p in pairs])
    zc = np.arctanh(np.clip(rs, -.999, .999)); zmu = np.sum(zc * (ns - 3)) / np.sum(ns - 3); Z = zmu * np.sqrt(np.sum(ns - 3))
    return {"pooled_rho": round(float(np.sum(ns * rs) / np.sum(ns)), 4), "one_sided_p": float(stats.norm.sf(Z)), "n_drugs": len(pairs)}

# ---------- FIMM expression: Ensembl -> symbol, samples x genes ----------
m = pd.read_csv(os.path.join(DATA, "ensg2symbol.tsv"), sep="\t").set_index("ensg")["symbol"].to_dict()
cpm = pd.read_csv(os.path.join(FIMM, "File_7_RNA_seq_CPM_163S_4Healthy.csv")).rename(columns={"Unnamed: 0": "ensg"})
cpm["sym"] = cpm["ensg"].str.split(".").str[0].map(m)
cpm = cpm.dropna(subset=["sym"]).drop(columns=["ensg"])
expr = cpm.groupby("sym").max(numeric_only=True)             # symbol x sample (Log2CPM)
if float(np.nanmax(expr.values)) > 60: expr = np.log2(expr + 1)   # ensure log space (Zenodo: Log2CPM already)
aml_cols = [c for c in expr.columns if str(c).startswith("AML")]
expr = expr[aml_cols]
print(f"B20 FIMM replication | expr {expr.shape[0]} genes x {expr.shape[1]} AML samples", flush=True)

# ---------- engine + inferred dependency (unchanged from V19/V20) ----------
eng = InterceptaEngine().fit(drugs=FLT3I + BCL2I, compute_calibration=False, label_source="prism")
eng.fit_dependency(["FLT3", "BCL2"])
inf = eng.infer_dependency(expr)                              # samples x {FLT3,BCL2} gene-effect
dep_flt3 = -inf["FLT3"]; dep_bcl2 = -inf["BCL2"]              # higher = more dependent
Rp = compute_r_prolif(expr)

# ---------- DSS drug response ----------
dss = pd.read_excel(os.path.join(FIMM, "File_3.2_Drug_response_DSS_sDSS_164S_17Healthy.xlsx"), skiprows=2)
dss["drug"] = dss["Chemical_compound"].astype(str).str.lower()
dss = dss[["Sample_ID", "drug", "DSS"]].dropna()
def dvec(drug):  # sample -> mean DSS
    return dss[dss["drug"] == drug].groupby("Sample_ID")["DSS"].mean()

# ---------- FLT3 mutation (binary; predominantly ITD in AML) ----------
mut = pd.read_excel(os.path.join(FIMM, "File_6_Binary_mutation_225S_57G.xlsx")).set_index("Unnamed: 0")
flt3mut = mut.loc["FLT3"] if "FLT3" in mut.index else pd.Series(dtype=float)   # per-sample 0/1

# ---------- R1: FLT3-dep -> FLT3i sensitivity (prolif-adjusted, pooled) ----------
r1_pairs, matrix_cells, r3_meta, r3_wt = [], [], [], []
for drug in FLT3I:
    a = dvec(drug); S = [s for s in a.index if s in dep_flt3.index and s in Rp.index]
    if len(S) < MIN_N: continue
    y = a[S].values; d1 = dep_flt3[S].values; d2 = dep_bcl2[S].values; rp = Rp[S].values
    r1 = padj_rho(d1, y, rp); r1_pairs.append((len(S), r1))
    matrix_cells.append({"drug": drug, "target": "FLT3", "matched": True, "n": len(S), "rho": round(r1, 4)})
    matrix_cells.append({"drug": drug, "target": "BCL2", "matched": False, "n": len(S), "rho": round(padj_rho(d2, y, rp), 4)})
    # R3: beyond FLT3-mutation (OLS DSS ~ dep + mut + prolif) + within mut-negative
    mm = flt3mut.reindex(S).astype(float)
    if mm.notna().sum() >= MIN_N and mm.dropna().nunique() == 2:
        idx = [i for i, s in enumerate(S) if np.isfinite(mm[s])]
        yy = y[idx]; dd = d1[idx]; mv = mm.values[idx]; rpp = rp[idx]
        res = sm.OLS(yy, sm.add_constant(np.column_stack([z(dd), mv, z(rpp)]), has_constant="add")).fit()
        r3_meta.append((float(res.params[1]), float(res.bse[1])))
        wt = [i for i in range(len(idx)) if mv[i] == 0]
        if len(wt) >= MIN_WT:
            r3_wt.append((len(wt), padj_rho(dd[wt], yy[wt], rpp[wt])))
R1 = pooled(r1_pairs)

# venetoclax cells (for R2)
a = dvec("venetoclax"); S = [s for s in a.index if s in dep_flt3.index and s in Rp.index]
ven_flt3 = ven_bcl2 = None
if len(S) >= MIN_N:
    y = a[S].values; rp = Rp[S].values
    ven_flt3 = padj_rho(dep_flt3[S].values, y, rp); ven_bcl2 = padj_rho(dep_bcl2[S].values, y, rp)
    matrix_cells.append({"drug": "venetoclax", "target": "FLT3", "matched": False, "n": len(S), "rho": round(ven_flt3, 4)})
    matrix_cells.append({"drug": "venetoclax", "target": "BCL2", "matched": True, "n": len(S), "rho": round(ven_bcl2, 4)})

# ---------- R2: specificity permutation (diagonal vs off-diagonal) ----------
diag = [c["rho"] for c in matrix_cells if c["matched"]]; offd = [c["rho"] for c in matrix_cells if not c["matched"]]
gap_obs = float(np.mean(diag) - np.mean(offd))
rho_by = {(c["drug"], c["target"]): c["rho"] for c in matrix_cells}
drugs_present = sorted({c["drug"] for c in matrix_cells}); true_t = {d: ("BCL2" if d == "venetoclax" else "FLT3") for d in drugs_present}
perm = []
for _ in range(NPERM):
    pm = dict(zip(drugs_present, rng.permutation([true_t[d] for d in drugs_present])))
    dm = [rho_by[(d, pm[d])] for d in drugs_present if (d, pm[d]) in rho_by]
    om = [rho_by[(d, t)] for d in drugs_present for t in ("FLT3", "BCL2") if t != pm[d] and (d, t) in rho_by]
    if dm and om: perm.append(np.mean(dm) - np.mean(om))
perm = np.array(perm); p_r2 = float((1 + np.sum(perm >= gap_obs)) / (1 + len(perm)))
R2 = bool(gap_obs > 0 and p_r2 < 0.05 and ven_bcl2 is not None and ven_bcl2 > 0 and (ven_flt3 is None or ven_bcl2 > ven_flt3))

# ---------- R3 meta ----------
R3 = None
if r3_meta:
    b = np.array([x[0] for x in r3_meta]); se = np.array([x[1] for x in r3_meta]); w = 1 / se**2
    muf = np.sum(w * b) / np.sum(w); Q = np.sum(w * (b - muf)**2); k = len(b)
    tau2 = max(0, (Q - (k - 1)) / (np.sum(w) - np.sum(w**2) / np.sum(w))) if k > 1 else 0
    wr = 1 / (se**2 + tau2); mu = float(np.sum(wr * b) / np.sum(wr)); semu = float(np.sqrt(1 / np.sum(wr)))
    p3 = float(2 * stats.norm.sf(abs(mu / semu)))
    wtp = pooled(r3_wt)
    R3 = {"beyond_mut_meta_beta": round(mu, 4), "beyond_mut_p": p3, "beyond_mut_pass": bool(mu > 0 and p3 < 0.05),
          "mutneg_pooled": wtp, "pass": bool(mu > 0 and p3 < 0.05 and wtp and wtp["pooled_rho"] > 0 and wtp["one_sided_p"] < 0.05)}

r1_pass = bool(R1 and R1["pooled_rho"] > 0 and R1["one_sided_p"] < 0.05)
print(f"\nR1 (V19 core): FLT3-dep -> FLT3i sensitivity, prolif-adj pooled rho={R1['pooled_rho'] if R1 else None} p={R1['one_sided_p'] if R1 else None:.3g} ({len(r1_pairs)} drugs) -> {r1_pass}")
print("  per-drug prolif-adj rho:", {c["drug"]: c["rho"] for c in matrix_cells if c["target"] == "FLT3" and c["matched"]})
print(f"R2 (V20 specificity): diag={np.mean(diag):+.3f} off={np.mean(offd):+.3f} gap={gap_obs:+.3f} perm_p={p_r2:.4g}; venetoclax BCL2={ven_bcl2} FLT3={ven_flt3} -> {R2}")
print(f"R3 (beyond FLT3-mut): {R3}")

verdict = ("EXTERNAL REPLICATION: " + ", ".join(
    ([f"V19 core REPLICATES (FLT3-dep->FLT3i rho={R1['pooled_rho']}, p={R1['one_sided_p']:.1e})"] if r1_pass else ["V19 core FAILS to replicate"]) +
    ([f"target-specificity REPLICATES (perm p={p_r2:.1e})"] if R2 else ["specificity not replicated"]) +
    ([f"beyond-mutation REPLICATES"] if (R3 and R3["pass"]) else ["beyond-mutation not fully replicated"])) +
    " in the independent FIMM/Malani cohort (different institution + assay).")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED, "n_perm": int(len(perm)),
       "cohort": "FIMM/Malani AML (Zenodo 7370747, CC-BY 4.0)",
       "data_sha256": {"RNA_CPM": sha256(os.path.join(FIMM, "File_7_RNA_seq_CPM_163S_4Healthy.csv"))[:16],
                       "DSS": sha256(os.path.join(FIMM, "File_3.2_Drug_response_DSS_sDSS_164S_17Healthy.xlsx"))[:16]},
       "n_samples_expr": int(expr.shape[1]), "flt3_inhibitors": FLT3I,
       "R1_core": R1, "R1_pass": r1_pass, "matrix_cells": matrix_cells,
       "R2_gap": round(gap_obs, 4), "R2_perm_p": p_r2, "R2_venetoclax_bcl2_rho": ven_bcl2, "R2_venetoclax_flt3_rho": ven_flt3, "R2_pass": R2,
       "R3_beyond_mutation": R3, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B20_metrics.json"), "w"), indent=2)
print("wrote results/B20_metrics.json")
