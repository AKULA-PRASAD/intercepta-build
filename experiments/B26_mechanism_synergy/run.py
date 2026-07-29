"""B26 — mechanism-anchored synergy: do TARGET-DEPENDENCY (CRISPR) features generalize to NOVEL drugs where
chemical fingerprints fail (B25)? O'Neil synergy + DepMap CRISPR/expression. Implements
prereg/B26_mechanism_synergy.md. Reproduce x2.
"""
import os, sys, json, time, re
import numpy as np, pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold
import sklearn, warnings; warnings.filterwarnings("ignore")
from rdkit import Chem
from rdkit.Chem import AllChem

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D

SEED, KF, NBITS = 42, 5, 1024
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
rng = np.random.default_rng(SEED)

# curated O'Neil drug -> target gene(s) (established pharmacology; genes must be in DepMap CRISPR).
# pure DNA-alkylators/antimetabolites w/o a clean gene target are EXCLUDED a priori (out of mechanism scope).
TARGETS = {
    "5-FU": ["TYMS"], "ABT-888": ["PARP1", "PARP2"], "AZD1775": ["WEE1"], "BEZ-235": ["PIK3CA", "MTOR"],
    "BORTEZOMIB": ["PSMB5"], "DASATINIB": ["ABL1", "SRC"], "DEXAMETHASONE": ["NR3C1"],
    "DINACICLIB": ["CDK1", "CDK2", "CDK9"], "DOXORUBICIN": ["TOP2A"], "ERLOTINIB": ["EGFR"],
    "ETOPOSIDE": ["TOP2A"], "GELDANAMYCIN": ["HSP90AA1"], "GEMCITABINE": ["RRM1"], "L778123": ["FNTA", "FNTB"],
    "LAPATINIB": ["EGFR", "ERBB2"], "METHOTREXATE": ["DHFR"], "MK-2206": ["AKT1", "AKT2"], "MK-4541": ["AR"],
    "MK-4827": ["PARP1"], "MK-5108": ["AURKA"], "MK-8669": ["MTOR"], "MK-8776": ["CHEK1"],
    "PACLITAXEL": ["TUBB"], "PD325901": ["MAP2K1", "MAP2K2"], "SN-38": ["TOP1"], "SORAFENIB": ["BRAF", "RAF1"],
    "SUNITINIB": ["KIT", "KDR"], "TOPOTECAN": ["TOP1"], "VINBLASTINE": ["TUBB"], "VINORELBINE": ["TUBB"],
    "ZOLINZA": ["HDAC1", "HDAC2"],
}

syn = pd.read_parquet(os.path.join(DATA, "oneil_synergy.parquet"))
smi = pd.read_parquet(os.path.join(DATA, "oneil_smiles.parquet")).set_index("id")["smiles"].to_dict()
cr = D.load_depmap_crispr(); rna = D.load_depmap_expression()
m = pd.read_csv(os.path.join(DATA, "depmap_meta.csv"))
def norm(x): return re.sub(r"[^a-z0-9]", "", str(x).lower())
name2ach = {}
for _, r in m.iterrows():
    for col in ["stripped_cell_line_name", "CCLE_Name", "cell_line_name"]:
        v = r.get(col)
        if pd.notna(v): name2ach[norm(str(v).split("_")[0] if col == "CCLE_Name" else v)] = r["DepMap_ID"]

syn = syn.copy(); syn["ach"] = syn["Cell_Line_ID"].map(lambda c: name2ach.get(norm(c)))
# keep rows with mapped CRISPR cell + both drugs curated + targets present in CRISPR
crispr_genes = set(cr.columns)
def tgt_ok(d): return d in TARGETS and any(g in crispr_genes for g in TARGETS[d])
syn = syn[syn["ach"].isin(set(cr.index)) & syn["Drug1_ID"].map(tgt_ok) & syn["Drug2_ID"].map(tgt_ok)].reset_index(drop=True)
cells = sorted(syn["ach"].unique())
y = syn["Synergy_Loewe"].values.astype(float)
pair_key = (syn["Drug1_ID"] + "|" + syn["Drug2_ID"]).apply(lambda s: "|".join(sorted(s.split("|")))).values
print(f"B26 mechanism-synergy | n={len(y)} pairs={len(set(pair_key))} drugs={len(set(syn['Drug1_ID'])|set(syn['Drug2_ID']))} cells={len(cells)}", flush=True)

# cell context: DepMap expression PCA
cpca = PCA(n_components=min(20, len(cells) - 1), random_state=SEED).fit(rna.loc[cells].values)
CELLPC = pd.DataFrame(cpca.transform(rna.loc[cells].values), index=cells)
# cross-cell co-dependency corr between two genes (over all DepMap cells)
crc = cr.copy()
def codep(g1, g2):
    if g1 not in crc.columns or g2 not in crc.columns: return 0.0
    a = crc[g1]; b = crc[g2]; ok = a.notna() & b.notna()
    return float(np.corrcoef(a[ok], b[ok])[0, 1]) if ok.sum() > 20 else 0.0
def dep_in_cell(drug, ach):  # strongest (most negative) target dependency of the drug in the cell
    vals = [cr.loc[ach, g] for g in TARGETS[drug] if g in crc.columns and np.isfinite(cr.loc[ach, g])]
    return min(vals) if vals else 0.0

# --- MECH features ---
mech = []
for i in range(len(syn)):
    d1, d2, a = syn["Drug1_ID"].iloc[i], syn["Drug2_ID"].iloc[i], syn["ach"].iloc[i]
    x1, x2 = dep_in_cell(d1, a), dep_in_cell(d2, a)
    cd = codep(TARGETS[d1][0], TARGETS[d2][0])
    mech.append([x1, x2, x1 * x2, x1 + x2, abs(x1 - x2), min(x1, x2), max(x1, x2), cd])
mech = np.array(mech, float)
CELL = CELLPC.loc[syn["ach"]].values

# --- FP features ---
def morgan(s):
    mo = Chem.MolFromSmiles(str(s))
    if mo is None: return np.zeros(NBITS, np.int8)
    return np.frombuffer(AllChem.GetMorganFingerprintAsBitVect(mo, 2, nBits=NBITS).ToBitString().encode(), "u1").astype(np.int8) - ord("0")
FP = {d: morgan(s) for d, s in smi.items()}
fp1 = np.vstack([FP[d] for d in syn["Drug1_ID"]]); fp2 = np.vstack([FP[d] for d in syn["Drug2_ID"]])
FPX = np.hstack([(fp1 + fp2).astype(np.int8), (fp1 & fp2).astype(np.int8)])

FEAT = {"FP": np.hstack([CELL, FPX]), "MECH": np.hstack([CELL, mech]),
        "FP+MECH": np.hstack([CELL, FPX, mech]), "cell_only": CELL}
def model(): return HistGradientBoostingRegressor(random_state=SEED, max_iter=300, learning_rate=0.06, max_depth=6)
def sp(a, b): return float(stats.spearmanr(a, b)[0])

def eval_split(groups):
    out = {}
    splitter = GroupKFold(min(KF, len(set(groups))))
    for name, Xf in FEAT.items():
        oof = np.full(len(y), np.nan)
        for tr, te in splitter.split(Xf, y, groups): oof[te] = model().fit(Xf[tr], y[tr]).predict(Xf[te])
        out[name] = round(sp(oof, y), 4)
    return out

# drug-out grouping (both drugs held out)
drugs_all = sorted(set(syn["Drug1_ID"]) | set(syn["Drug2_ID"]))
dfold = {d: i % KF for i, d in enumerate(rng.permutation(drugs_all))}
d1f = syn["Drug1_ID"].map(dfold).values; d2f = syn["Drug2_ID"].map(dfold).values
def eval_drugout():
    out = {}
    for name, Xf in FEAT.items():
        pred = np.full(len(y), np.nan)
        for k in range(KF):
            te = np.where((d1f == k) & (d2f == k))[0]; tr = np.where((d1f != k) & (d2f != k))[0]
            if len(te) < 20 or len(tr) < 200: continue
            pred[te] = model().fit(Xf[tr], y[tr]).predict(Xf[te])
        mask = np.isfinite(pred); out[name] = {"spearman": round(sp(pred[mask], y[mask]), 4), "n": int(mask.sum()),
                                               "_pred": pred, "_mask": mask}
    return out

loco = eval_split(pair_key)
ldo = eval_drugout()
# bootstrap CI + MECH-vs-FP delta on leave-drug-out
mask = ldo["MECH"]["_mask"] & ldo["FP"]["_mask"]; idx = np.where(mask)[0]
dmech, dfp = ldo["MECH"]["_pred"], ldo["FP"]["_pred"]
boot = np.array([sp(dmech[b], y[b]) - sp(dfp[b], y[b]) for b in (rng.choice(idx, len(idx), replace=True) for _ in range(2000))])
mech_ci = (round(float(np.percentile([sp(dmech[b], y[b]) for b in (rng.choice(idx, len(idx), True) for _ in range(1000))], 2.5)), 4),)
delta_p = float(2 * min((boot <= 0).mean(), (boot >= 0).mean()))
for k in ldo: ldo[k] = {"spearman": ldo[k]["spearman"], "n": ldo[k]["n"]}

H_mech = bool(ldo["MECH"]["spearman"] > ldo["FP"]["spearman"] and ldo["MECH"]["spearman"] > 0 and delta_p < 0.05)
H_add = bool(loco["FP+MECH"] > loco["FP"])
H_sanity = bool(loco["MECH"] > loco["cell_only"] and ldo["MECH"]["spearman"] > ldo["cell_only"]["spearman"])

print("\nleave-combination-out Spearman:", loco)
print("LEAVE-DRUG-OUT Spearman:", {k: v["spearman"] for k, v in ldo.items()})
print(f"  MECH vs FP (novel drugs): {ldo['MECH']['spearman']} vs {ldo['FP']['spearman']}  delta_p={delta_p:.4g}")
print(f"H_mech (MECH>FP for novel drugs): {H_mech} | H_add (FP+MECH>FP combos): {H_add} | H_sanity: {H_sanity}")
if H_mech:
    verdict = (f"MECHANISM-ANCHORING GENERALIZES TO NOVEL DRUGS: target-dependency features give leave-drug-out "
               f"Spearman {ldo['MECH']['spearman']} vs fingerprints {ldo['FP']['spearman']} (delta p={delta_p:.1e}) "
               f"-> biology-grounded features transfer to novel drugs where chemistry fails. Novel, mechanistic advance.")
else:
    verdict = (f"HONEST NEGATIVE: mechanism (target-dependency) features do NOT beat fingerprints for novel drugs "
               f"(MECH {ldo['MECH']['spearman']} vs FP {ldo['FP']['spearman']}) -> target co-dependency does not encode "
               f"transferable synergy beyond chemistry. The known-drug-combination capability (V23) stands.")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0], "sklearn": sklearn.__version__,
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED,
       "data": {"source": "O'Neil (TDC) + DepMap CRISPR/expr", "n": int(len(y)), "n_pairs": int(len(set(pair_key))),
                "n_drugs": len(drugs_all), "n_cells": len(cells)},
       "leave_combination_out_spearman": loco, "leave_drug_out": ldo, "mech_vs_fp_drugout_delta_p": delta_p,
       "H_mech_novel_drug": H_mech, "H_add": H_add, "H_sanity": H_sanity, "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B26_metrics.json"), "w"), indent=2)
print("wrote results/B26_metrics.json")
