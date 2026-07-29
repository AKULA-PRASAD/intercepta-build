"""B2 — can verified biology beat the +0.212 ceiling? Implements prereg/B2_beat_the_ceiling.md.

Arm 0  : top-2000 z-expression (= B1 ceiling).
Arm R  : + frozen R_prolif feature.
Arm M  : + K=50 damaging-mutation indicators (panel = top-mutated genes among each drug's TRAIN cells);
         restricted to mutation-profiled cells, compared to a matched-subset control Arm 0M.
Decision: candidate PASS iff Delta-rho >= +0.02 AND paired Wilcoxon p<0.05 after BH across arms.
External replication (GDSC1) is only triggered if an arm is a candidate PASS. Deterministic; reproduce x2.
"""
import os, sys, json, time
import numpy as np
from sklearn.linear_model import RidgeCV
import sklearn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.splits import disjoint_train_cosmics
from intercepta.metrics import per_drug_spearman, paired_wilcoxon, bh_fdr
from intercepta.axes import compute_r_prolif

TOPN, KMUT, DELTA = 2000, 50, 0.02
HERE = os.path.dirname(os.path.abspath(__file__))
print("B2 beat-the-ceiling | sklearn", sklearn.__version__, flush=True)

cos2dep, dep2cos = D.load_cosmic_depmap_map()
gdsc = D.load_gdsc_response()
prism = D.load_prism()
gx = D.load_gdsc_expression()
dx = D.load_depmap_expression()
Rp_ccle = compute_r_prolif(dx.T)
mut = D.load_damaging_mutations()   # dict DepMap_ID -> set(genes)

shared_genes = [g for g in gx.index if g in set(dx.columns)]
v = gx.loc[shared_genes].var(1).sort_values(ascending=False)
genes = list(v.head(TOPN).index)
gxz = D.z_rows(gx.loc[genes]).fillna(0.0)      # genes x cells (COSMIC)
dxz = D.z_rows(dx[genes].T).fillna(0.0)        # genes x cells (DepMap)
# R_prolif per GDSC cell (gx is already genes x cells) -> Series indexed by COSMIC id
Rp_gdsc = compute_r_prolif(gx)

gl = {d.lower(): d for d in gdsc["DRUG_NAME"].unique()}
pl = {d.lower(): d for d in prism["name"].unique()}
shared = sorted(set(gl) & set(pl))
gdsc_cos = set(gx.columns)
shared_cells = (set(cos2dep.get(c) for c in gdsc["COSMIC_ID"].unique() if c in cos2dep)
                & set(dx.index) & set(Rp_ccle.index) & set(prism["depmap_id"].unique()))
prism_g = prism[prism["depmap_id"].isin(shared_cells)].copy()
prism_g["k"] = prism_g["name"].str.lower()
obs = prism_g[prism_g["k"].isin(shared)].groupby(["depmap_id", "k"])["auc"].mean()


def ridge_rho(Xtr, ytr, Xte, yte):
    m = RidgeCV(alphas=[10.0, 100.0, 1000.0]).fit(Xtr, ytr)
    return per_drug_spearman(m.predict(Xte), yte)


a0, aR, a0m, aM, drugs = [], [], [], [], []
for dk in shared:
    tr_all = gdsc[(gdsc["DRUG_NAME"] == gl[dk]) & (gdsc["COSMIC_ID"].isin(gdsc_cos))]
    if len(tr_all) < 30:
        continue
    cells = [c for c in shared_cells if (c, dk) in obs.index]
    if len(cells) < 20:
        continue
    tr = disjoint_train_cosmics(tr_all, cells, dep2cos)
    if len(tr) < 30:
        continue
    tr_cos = tr["COSMIC_ID"].values
    ytr = tr["LN_IC50"].values
    yte = np.array([obs[(c, dk)] for c in cells])
    # Arm 0 (expression only)
    Xtr0 = gxz[tr_cos].T.values
    Xte0 = dxz[cells].T.values
    r0 = ridge_rho(Xtr0, ytr, Xte0, yte)
    # Arm R (+ R_prolif feature, z within each dataset's used cells)
    rp_tr = np.array([float(Rp_gdsc.get(c, np.nan)) for c in tr_cos])
    rp_te = np.array([float(Rp_ccle[c]) for c in cells])
    if np.isfinite(rp_tr).all():
        zt = (rp_tr - rp_tr.mean()) / (rp_tr.std() or 1.0)
        ze = (rp_te - rp_te.mean()) / (rp_te.std() or 1.0)
        rR = ridge_rho(np.column_stack([Xtr0, zt]), ytr, np.column_stack([Xte0, ze]), yte)
    else:
        rR = np.nan
    # Arm M (+ K mutation indicators) on mutation-profiled subset, vs matched control Arm 0M
    tr_dep = [cos2dep.get(c) for c in tr_cos]                        # DepMap id for each train COSMIC
    tr_mask = np.array([(d in mut) for d in tr_dep])
    te_mask = np.array([(c in mut) for c in cells])
    rM = r0m = np.nan
    if tr_mask.sum() >= 30 and te_mask.sum() >= 20:
        trc = tr_cos[tr_mask]; trd = [d for d, m_ in zip(tr_dep, tr_mask) if m_]
        tec = [c for c, m_ in zip(cells, te_mask) if m_]
        ytr_m = ytr[tr_mask]; yte_m = yte[te_mask]
        # panel: top-K mutated genes among TRAIN cells only (deterministic: freq desc, gene name asc)
        from collections import Counter
        cnt = Counter()
        for d in trd:
            cnt.update(mut[d])
        panel = [g for g, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:KMUT]]
        Mtr = np.array([[1.0 if g in mut[d] else 0.0 for g in panel] for d in trd])
        Mte = np.array([[1.0 if g in mut[c] else 0.0 for g in panel] for c in tec])
        X0m_tr = gxz[trc].T.values; X0m_te = dxz[tec].T.values
        r0m = ridge_rho(X0m_tr, ytr_m, X0m_te, yte_m)
        rM = ridge_rho(np.column_stack([X0m_tr, Mtr]), ytr_m, np.column_stack([X0m_te, Mte]), yte_m)
    if np.isfinite(r0) and np.isfinite(rR):
        a0.append(r0); aR.append(rR); a0m.append(r0m); aM.append(rM); drugs.append(dk)

a0 = np.array(a0); aR = np.array(aR)
mmask = np.isfinite(np.array(aM)) & np.isfinite(np.array(a0m))
aM = np.array(aM)[mmask]; a0m = np.array(a0m)[mmask]

wR_stat, wR_p = paired_wilcoxon(aR, a0)
dR = float(aR.mean() - a0.mean())
if len(aM) >= 10:
    wM_stat, wM_p = paired_wilcoxon(aM, a0m); dM = float(aM.mean() - a0m.mean())
else:
    wM_stat, wM_p, dM = np.nan, np.nan, np.nan

qR, qM = bh_fdr([wR_p, wM_p])
passR = bool(dR >= DELTA and qR < 0.05)
passM = bool(np.isfinite(dM) and dM >= DELTA and qM < 0.05)

print(f"\ndrugs: Arm0/R n={len(a0)}  ArmM n={len(aM)} (mutation-profiled subset)")
print(f"Arm 0  (expr only) mean rho = {a0.mean():+.4f}   [ceiling +0.2124]")
print(f"Arm R  (+R_prolif) mean rho = {aR.mean():+.4f}   d={dR:+.4f}  Wilcoxon p={wR_p:.4g}  BHq={qR:.4g}  -> beats? {passR}")
if len(aM) >= 10:
    print(f"Arm 0M (matched)   mean rho = {a0m.mean():+.4f}")
    print(f"Arm M  (+mutations)mean rho = {aM.mean():+.4f}   d={dM:+.4f}  Wilcoxon p={wM_p:.4g}  BHq={qM:.4g}  -> beats? {passM}")
verdict = ("CANDIDATE PASS -> external replication required" if (passR or passM)
           else "NULL: no arm beats the ceiling -> +0.212 confirmed as the public-data ceiling")
print(f"VERDICT: {verdict}")

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "topN_genes": TOPN, "K_mut": KMUT, "delta_threshold": DELTA,
       "n_drugs_0R": len(a0), "n_drugs_M": int(len(aM)),
       "arm0_mean_rho": round(float(a0.mean()), 4), "armR_mean_rho": round(float(aR.mean()), 4),
       "armR_delta": round(dR, 4), "armR_wilcoxon_p": float(wR_p), "armR_BHq": float(qR), "armR_beats": passR,
       "arm0m_mean_rho": (round(float(a0m.mean()), 4) if len(aM) else None),
       "armM_mean_rho": (round(float(aM.mean()), 4) if len(aM) else None),
       "armM_delta": (round(dM, 4) if np.isfinite(dM) else None),
       "armM_wilcoxon_p": (float(wM_p) if np.isfinite(wM_p) else None),
       "armM_BHq": (float(qM) if np.isfinite(qM) else None), "armM_beats": passM,
       "candidate_pass": bool(passR or passM), "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B2_metrics.json"), "w"), indent=2)
print("wrote results/B2_metrics.json")
