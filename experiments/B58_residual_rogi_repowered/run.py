"""B58 — re-powered residual-mechanism test with ROGI. Correlates a principled landscape-roughness index (ROGI,
reimplemented) against the doubly-debiased VS residual (A1B1) across an expanded target panel (LIT-PCBA + TDC/Butkiewicz
HTS). Reuses committed B54/B56 residuals; computes A1B1 for new targets with identical method. Implements
prereg/B58_residual_rogi_repowered.md. Deterministic -> reproduce x2. No docking.
"""
import os, sys, json, time, hashlib
import numpy as np
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors, Crippen
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Scoring.Scoring import CalcAUC
from sklearn.ensemble import HistGradientBoostingClassifier
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
LIT = os.path.join(DATA, "lit_pcba")
RATIO, SEEDS, NN_NOVEL, MIN_NOVEL, MAX_ACT, POOL_CAP = 3, [1, 2, 3, 4, 5], 0.40, 15, 400, 8000
ROGI_ACT, ROGI_DEC, CLIFF_SIM = 200, 200, 0.40
PHENO = {"hiv", "sarscov2_3clpro_diamond", "sarscov2_vitro_touret"}

LITP = ["ALDH1", "VDR", "PKM2", "FEN1", "MAPK1", "GBA", "KAT2A", "ESR1_ant"]                 # residual from B54
HTS_DONE = ["hiv", "m1_muscarinic_receptor_antagonists_butkiewicz", "orexin1_receptor_butkiewicz",
            "potassium_ion_channel_kir2.1_butkiewicz", "serine_threonine_kinase_33_butkiewicz"]  # residual from B56
HTS_NEW = ["m1_muscarinic_receptor_agonists_butkiewicz", "kcnq2_potassium_channel_butkiewicz",
           "cav3_t-type_calcium_channels_butkiewicz", "choline_transporter_butkiewicz",
           "tyrosyl-dna_phosphodiesterase_butkiewicz", "sarscov2_3clpro_diamond", "sarscov2_vitro_touret"]


def largest(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None: return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m
def murcko(m):
    try: return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception: return ""
def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
def arr(fp):
    a = np.zeros(1024, dtype=np.float32); DataStructs.ConvertToNumpyArray(fp, a); return a
def physchem6(m):
    return np.array([Descriptors.MolWt(m), Crippen.MolLogP(m), Descriptors.NumHDonors(m),
                     Descriptors.NumHAcceptors(m), Descriptors.TPSA(m), Descriptors.NumRotatableBonds(m)], float)
def auroc(y, s):
    r = [[int(y[i])] for i in np.argsort(-np.asarray(s))]; return float(CalcAUC(r, 0))


def load_lit(tgt):
    def rd(f): return [l.split()[0] for l in open(os.path.join(LIT, tgt, f)) if l.split()]
    a = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in rd("actives.smi")) if m}.values())
    d = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in rd("inactives.smi")) if m}.values())
    return a, d
def load_hts(tgt):
    from tdc.single_pred import HTS
    df = HTS(name=tgt, path=os.path.join(DATA, "tdc_bio")).get_data().dropna(subset=["Y", "Drug"])
    a = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in df[df["Y"] == 1]["Drug"].tolist()) if m}.values())
    dd = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in df[df["Y"] == 0]["Drug"].tolist()) if m}.values())
    aset = set(Chem.MolToSmiles(m) for m in a); dd = [m for m in dd if Chem.MolToSmiles(m) not in aset]
    return a, dd


def rogi(y, fps):
    y = np.asarray(y, float); s = y.std()
    if s < 1e-9 or len(y) < 4: return float("nan")
    y = (y - y.mean()) / s; n = len(y)
    D = np.zeros((n, n))
    for i in range(n):
        D[i] = 1.0 - np.array(DataStructs.BulkTanimotoSimilarity(fps[i], fps))
    np.fill_diagonal(D, 0.0); Z = linkage(squareform(D, checks=False), method="complete")
    ts = np.linspace(0.0, 1.0, 101); sds = []
    for t in ts:
        lab = fcluster(Z, t, criterion="distance")
        means = {c: y[lab == c].mean() for c in np.unique(lab)}
        sds.append(np.array([means[c] for c in lab]).std())
    return float(1.0 - np.trapz(sds, ts) / (y.std() + 1e-12))


def compute_a1b1(acts, decs):
    """A1B1 residual: property-matched decoys + novel-chemistry (NN<0.4) test, Morgan HGB, 5 seeds. Same as B54/B56."""
    rng = np.random.default_rng(42)
    if len(acts) > MAX_ACT: acts = [acts[i] for i in sorted(rng.permutation(len(acts))[:MAX_ACT])]
    if len(decs) > POOL_CAP: decs = [decs[i] for i in sorted(rng.permutation(len(decs))[:POOL_CAP])]
    if len(decs) < RATIO * len(acts) + 20: return None
    aX = np.vstack([arr(bit(m)) for m in acts]); aFP = [bit(m) for m in acts]
    aScaf = np.array([murcko(m) for m in acts], dtype=object)
    aDesc = np.vstack([physchem6(m) for m in acts]); iDesc = np.vstack([physchem6(m) for m in decs])
    dX = np.vstack([arr(bit(m)) for m in decs])
    alld = np.vstack([aDesc, iDesc]); mu = alld.mean(0); sd = alld.std(0); sd[sd == 0] = 1.0

    def match(a_idx, k, forbidden):
        A = (aDesc[a_idx] - mu) / sd; I = (iDesc - mu) / sd
        used = np.zeros(len(I), bool); used[list(forbidden)] = True; picks = []
        for _ in range(k):
            for a in A:
                d = np.sum((I - a) ** 2, 1); d[used] = np.inf; j = int(np.argmin(d))
                if np.isfinite(d[j]): used[j] = True; picks.append(j)
        return picks
    vals = []
    for seed in SEEDS:
        uniq = np.array(sorted(set(aScaf))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:max(1, int(0.3 * len(uniq)))]); te = np.array([s in tsc for s in aScaf])
        tr = np.where(~te)[0]; tec = np.where(te)[0]; trf = [aFP[i] for i in tr]
        te_a = np.array([i for i in tec if max(DataStructs.BulkTanimotoSimilarity(aFP[i], trf)) < NN_NOVEL], int)
        if len(te_a) < MIN_NOVEL or len(tr) < 5: return {"skip": True}
        trd = match(tr, RATIO, set())[:RATIO * len(tr)]; ted = match(te_a, RATIO, set(trd))[:RATIO * len(te_a)]
        trX = np.vstack([aX[tr], dX[trd]]); trY = np.array([1] * len(tr) + [0] * len(trd))
        teX = np.vstack([aX[te_a], dX[ted]]); teY = np.array([1] * len(te_a) + [0] * len(ted))
        if len(np.unique(trY)) < 2: continue
        m = HistGradientBoostingClassifier(random_state=42, max_iter=150, learning_rate=0.06, max_depth=6).fit(trX, trY)
        vals.append(auroc(teY, m.predict_proba(teX)[:, 1]))
    return {"a1b1": round(float(np.mean(vals)), 4)} if vals else None


def predictors(acts, decs, tgt):
    rng = np.random.default_rng(42)
    am = [acts[i] for i in sorted(rng.permutation(len(acts))[:min(ROGI_ACT, len(acts))])]
    dm = [decs[i] for i in sorted(rng.permutation(len(decs))[:min(ROGI_DEC, len(decs))])]
    aFP = [bit(m) for m in am]; dFP = [bit(m) for m in dm]
    y = [1] * len(am) + [0] * len(dm); fps = aFP + dFP
    rg = rogi(y, fps)
    cliff = float(np.mean([max(DataStructs.BulkTanimotoSimilarity(fp, dFP)) >= CLIFF_SIM for fp in aFP]))
    sims = []
    for i in range(len(aFP)): sims.extend(DataStructs.BulkTanimotoSimilarity(aFP[i], aFP[i + 1:]))
    return {"rogi": round(rg, 4), "activity_cliff_density": round(cliff, 4),
            "active_mean_pairwise_tanimoto": round(float(np.mean(sims)) if sims else 0.0, 4),
            "n_actives": len(acts), "assay_type_phenotypic": int(tgt in PHENO)}


def main():
    b54 = json.load(open(os.path.join(ROOT, "experiments/B54_decoy_artifact_discriminator/results/B54_metrics.json")))
    b56 = json.load(open(os.path.join(ROOT, "experiments/B56_p6_external_htspanel/results/B56_metrics.json")))
    rows = {}
    for t in LITP:
        a, d = load_lit(t); p = predictors(a, d, t); p["residual_A1B1"] = b54["per_target"][t]["cells"]["A1B1"]
        p["source"] = "LIT-PCBA(B54)"; rows[t] = p
    for t in HTS_DONE:
        a, d = load_hts(t); p = predictors(a, d, t); p["residual_A1B1"] = b56["per_target"][t]["cells"]["A1B1"]
        p["source"] = "HTS(B56)"; rows[t] = p
    for t in HTS_NEW:
        a, d = load_hts(t); r = compute_a1b1(a, d)
        if r is None or r.get("skip"):
            rows[t] = {"note": "skipped (insufficient decoys or <15 novel test actives)", "source": "HTS(new)"}; continue
        p = predictors(a, d, t); p["residual_A1B1"] = r["a1b1"]; p["source"] = "HTS(new)"; rows[t] = p

    sc = {k: v for k, v in rows.items() if "residual_A1B1" in v and not np.isnan(v.get("rogi", np.nan))}
    for t, p in sc.items():
        print(f"  {t[:26]:26s} [{p['source']:13s}] residual {p['residual_A1B1']:.3f} | ROGI {p['rogi']:.3f} "
              f"cliff {p['activity_cliff_density']:.3f} div {p['active_mean_pairwise_tanimoto']:.3f} nAct {p['n_actives']}")
    for t, p in rows.items():
        if "note" in p: print(f"  {t[:26]:26s} SKIP ({p['note']})")

    resid = np.array([sc[t]["residual_A1B1"] for t in sc])
    preds = ["rogi", "activity_cliff_density", "active_mean_pairwise_tanimoto", "n_actives", "assay_type_phenotypic"]
    corrs = {}
    for pr in preds:
        rho, pv = spearmanr(np.array([sc[t][pr] for t in sc]), resid)
        corrs[pr] = {"spearman": round(float(rho), 4), "p_value": round(float(pv), 4), "abs": round(abs(float(rho)), 4)}
    ranked = sorted(corrs.items(), key=lambda kv: -kv[1]["abs"])
    top = ranked[0][0]; rogi_rho = corrs["rogi"]["spearman"]
    h1 = bool(top == "rogi" and rogi_rho <= -0.5)
    h2 = bool(corrs["rogi"]["abs"] > corrs["activity_cliff_density"]["abs"])

    summary = {"n_targets": len(sc), "correlations_with_residual": corrs,
               "ranked_by_abs_spearman": [k for k, _ in ranked], "strongest_predictor": top,
               "rogi_spearman": rogi_rho, "H1_rogi_mechanism": h1, "H2_rogi_beats_cliff": h2,
               "verdict": (
                   f"ROGI EXPLAINS THE RESIDUAL — SAR ROUGHNESS PREDICTS WHEN LIGAND-BASED VS IS TRUSTWORTHY: ROGI is "
                   f"the strongest correlate (Spearman {rogi_rho}, p={corrs['rogi']['p_value']}, n={len(sc)}) and "
                   f"negative — rougher landscapes retain LESS binding signal after debiasing. Beats crude cliff "
                   f"density ({corrs['activity_cliff_density']['spearman']}). B57's null was underpowered/crude-metric; "
                   f"a principled roughness index + more targets recovers the mechanism. Meta-analysis, n={len(sc)}; "
                   f"ROGI reimplemented (validated, not bit-exact); correlation != causation; not wet-lab."
                   if h1 else
                   f"RESIDUAL STILL NOT EXPLAINED (stronger null): even with a principled ROGI + n={len(sc)} targets, "
                   f"the strongest correlate is '{top}' (Spearman {ranked[0][1]['spearman']}); ROGI = {rogi_rho} "
                   f"(pre-registered <=-0.5 not met; "
                   + ("beats" if h2 else "does not beat") + f" cliff density). The target-dependence of the "
                   f"doubly-debiased residual resists explanation by landscape roughness / diversity / assay / "
                   f"data-richness -> a robust first-class null; the cause is subtler or unmeasured (e.g. needs 3D/"
                   f"pocket features or continuous potency). n={len(sc)}; not wet-lab."),
               }
    print("\nRanked (|Spearman|):", [(k, corrs[k]['spearman']) for k in summary['ranked_by_abs_spearman']])
    print("VERDICT:", summary["verdict"])

    prov = {"experiment": "B58_residual_rogi_repowered", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "cliff_sim": CLIFF_SIM, "nn_novel": NN_NOVEL,
            "rogi": "reimplemented: 1 - integral SD(t) dt / SD(0), complete-linkage Tanimoto, binary label",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": rows}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B58_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": rows}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B58_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B58_metrics.json")


def _libvers():
    import rdkit, numpy, scipy, sklearn
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scipy": scipy.__version__, "scikit-learn": sklearn.__version__}


if __name__ == "__main__":
    main()
