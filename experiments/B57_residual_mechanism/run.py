"""B57 — mechanism of the target-dependent irreducible VS residual. Across the 13 targets with a reproduced A1B1
(doubly-debiased) residual (B54 LIT-PCBA + B56 TDC-HTS), test which target-level structural property explains it —
hypothesis: activity-cliff density (SAR ruggedness). Implements prereg/B57_residual_mechanism.md. Deterministic -> x2.
"""
import os, sys, json, time, hashlib
import numpy as np
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
LIT = os.path.join(DATA, "lit_pcba")
CLIFF_SIM, N_INACT_SAMPLE, N_ACT_SAMPLE = 0.40, 2000, 300
PHENOTYPIC = {"hiv", "sarscov2_3clpro_diamond"}
# (source, target-key-in-metrics, loader-name)
LITP = ["ALDH1", "VDR", "PKM2", "FEN1", "MAPK1", "GBA", "KAT2A", "ESR1_ant"]
HTS = ["hiv", "m1_muscarinic_receptor_antagonists_butkiewicz", "orexin1_receptor_butkiewicz",
       "potassium_ion_channel_kir2.1_butkiewicz", "serine_threonine_kinase_33_butkiewicz"]


def largest(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None: return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m
def bit(m): return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)


def load_litpcba(tgt):
    def rd(f): return [l.split()[0] for l in open(os.path.join(LIT, tgt, f)) if l.split()]
    a = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in rd("actives.smi")) if m}.values())
    d = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in rd("inactives.smi")) if m}.values())
    return a, d


def load_hts(tgt):
    from tdc.single_pred import HTS as H
    df = H(name=tgt, path=os.path.join(DATA, "tdc_bio")).get_data().dropna(subset=["Y", "Drug"])
    a = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in df[df["Y"] == 1]["Drug"].tolist()) if m}.values())
    d = list({Chem.MolToSmiles(m): m for m in (largest(s) for s in df[df["Y"] == 0]["Drug"].tolist()) if m}.values())
    aset = set(Chem.MolToSmiles(m) for m in a)
    d = [m for m in d if Chem.MolToSmiles(m) not in aset]
    return a, d


def predictors(acts, decs, tgt):
    rng = np.random.default_rng(42)
    amols = [acts[i] for i in sorted(rng.permutation(len(acts))[:min(N_ACT_SAMPLE, len(acts))])]
    dmols = [decs[i] for i in sorted(rng.permutation(len(decs))[:min(N_INACT_SAMPLE, len(decs))])]
    aFP = [bit(m) for m in amols]; dFP = [bit(m) for m in dmols]
    # activity-cliff density: frac of actives with a similar inactive (NN-inactive Tanimoto >= CLIFF_SIM)
    cliff = np.mean([max(DataStructs.BulkTanimotoSimilarity(fp, dFP)) >= CLIFF_SIM for fp in aFP])
    # active internal diversity: mean pairwise Tanimoto among sampled actives (higher = tighter cluster)
    sims = []
    for i in range(len(aFP)):
        s = DataStructs.BulkTanimotoSimilarity(aFP[i], aFP[i + 1:])
        sims.extend(s)
    mean_pair = float(np.mean(sims)) if sims else 0.0
    return {"activity_cliff_density": round(float(cliff), 4),
            "active_mean_pairwise_tanimoto": round(mean_pair, 4),
            "n_actives": len(acts),
            "assay_type_phenotypic": int(tgt in PHENOTYPIC)}


def main():
    b54 = json.load(open(os.path.join(ROOT, "experiments/B54_decoy_artifact_discriminator/results/B54_metrics.json")))
    b56 = json.load(open(os.path.join(ROOT, "experiments/B56_p6_external_htspanel/results/B56_metrics.json")))
    rows = {}
    for tgt in LITP:
        res = b54["per_target"][tgt]["cells"]["A1B1"]
        a, d = load_litpcba(tgt); p = predictors(a, d, tgt); p["residual_A1B1"] = res; p["source"] = "LIT-PCBA"
        rows[tgt] = p
    for tgt in HTS:
        res = b56["per_target"][tgt]["cells"]["A1B1"]
        a, d = load_hts(tgt); p = predictors(a, d, tgt); p["residual_A1B1"] = res; p["source"] = "TDC-HTS"
        rows[tgt] = p

    for t, p in rows.items():
        print(f"  {t[:22]:22s} residual {p['residual_A1B1']:.3f} | cliff {p['activity_cliff_density']:.3f} "
              f"diversity {p['active_mean_pairwise_tanimoto']:.3f} nAct {p['n_actives']:4d} pheno {p['assay_type_phenotypic']}")

    resid = np.array([p["residual_A1B1"] for p in rows.values()])
    preds = ["activity_cliff_density", "active_mean_pairwise_tanimoto", "n_actives", "assay_type_phenotypic"]
    corrs = {}
    for pr in preds:
        x = np.array([rows[t][pr] for t in rows])
        rho, pval = spearmanr(x, resid)
        corrs[pr] = {"spearman": round(float(rho), 4), "p_value": round(float(pval), 4), "abs": round(abs(float(rho)), 4)}
    ranked = sorted(corrs.items(), key=lambda kv: -kv[1]["abs"])
    top_pred, top = ranked[0]
    cliff_rho = corrs["activity_cliff_density"]["spearman"]
    h1 = bool(top_pred == "activity_cliff_density" and cliff_rho <= -0.5)

    summary = {"n_targets": len(rows), "correlations_with_residual": corrs,
               "ranked_by_abs_spearman": [k for k, _ in ranked], "strongest_predictor": top_pred,
               "activity_cliff_density_spearman": cliff_rho,
               "H1_activity_cliff_mechanism": h1,
               "verdict": (
                   f"MECHANISM CONFIRMED — SAR RUGGEDNESS EXPLAINS THE RESIDUAL: activity-cliff density is the strongest "
                   f"correlate of the doubly-debiased residual (Spearman {cliff_rho}, p={corrs['activity_cliff_density']['p_value']}), "
                   f"and NEGATIVE: targets whose actives sit next to structurally-similar inactives (rugged SAR) retain "
                   f"LITTLE binding signal after debiasing, while smooth-SAR targets retain it. This turns 'how much "
                   f"enrichment is bias' into a predictive rule for WHEN ligand-based VS is trustworthy. Meta-analysis, "
                   f"n={len(rows)} targets (small -> effect size over p); one cliff operationalization; correlation not "
                   f"causation; not wet-lab."
                   if h1 else
                   f"ACTIVITY-CLIFF MECHANISM NOT CONFIRMED (honest): strongest correlate of the residual is "
                   f"'{top_pred}' (Spearman {top['spearman']}), and activity-cliff density is {cliff_rho} "
                   f"(pre-registered threshold <=-0.5 not met). The target-dependent residual is "
                   + ("better explained by another measured property (see ranking)" if top["abs"] >= 0.5 else
                      "NOT well explained by any of the four measured target properties (|Spearman|<0.5 for all) -> "
                      "a first-class null; the residual's target-dependence has a different or unmeasured cause")
                   + f". Meta-analysis, n={len(rows)} targets (small); not wet-lab."),
               }
    print("\nRanked predictors (|Spearman|):", [(k, corrs[k]['spearman']) for k in summary['ranked_by_abs_spearman']])
    print("VERDICT:", summary["verdict"])

    prov = {"experiment": "B57_residual_mechanism", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "cliff_sim": CLIFF_SIM,
            "residual_source": "B54_metrics.json (LIT-PCBA) + B56_metrics.json (TDC-HTS), cells.A1B1",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary, "per_target": rows}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B57_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary, "per_target": rows}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B57_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B57_metrics.json")


def _libvers():
    import rdkit, numpy, scipy
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scipy": scipy.__version__}


if __name__ == "__main__":
    main()
