"""B5 — systematic mutation->drug marker discovery in BeatAML. Implements prereg/B5_marker_discovery.md.
OLS AUC ~ mutation + FLT3_ITD + R_prolif per (gene,drug); BH-FDR across all pairs; split-half direction
replication; positive-control check. Deterministic; reproduce x2. Aggregate outputs only (no patient IDs).
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import sklearn, warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.metrics import bh_fdr
from intercepta.axes import compute_r_prolif

MIN_GENE_SUBJ, MIN_DRUG_SUBJ, MIN_MUT = 20, 30, 8
NONSILENT = D.NONSILENT_VEP
HERE = os.path.dirname(os.path.abspath(__file__))
print("B5 marker discovery | sklearn", sklearn.__version__, flush=True)

# --- load, key everything by dbgap_subject_id ---
probit = pd.read_csv(D._bp("beataml_probit_curve_fits_v4_dbgap.txt"), sep="\t",
                     usecols=["dbgap_subject_id", "dbgap_dnaseq_sample", "dbgap_rnaseq_sample", "inhibitor", "auc"]).dropna(subset=["dbgap_subject_id", "inhibitor", "auc"])
probit["drug"] = probit["inhibitor"].str.split(" (", regex=False).str[0].str.strip().str.lower()
auc = probit.groupby(["dbgap_subject_id", "drug"])["auc"].median()

clin = D.load_beataml_clinical()
def pos(x):
    s = str(x).strip().lower(); return 1.0 if s in ("positive","yes","mutated","pos") else (0.0 if s in ("negative","no","wildtype","wt","neg") else np.nan)
clin_s = clin.dropna(subset=["dbgap_subject_id"]).drop_duplicates("dbgap_subject_id").set_index("dbgap_subject_id")
itd = clin_s["FLT3-ITD"].map(pos); npm1_clin = clin_s["NPM1"].map(pos)

# WES non-silent -> gene -> set(dnaseq_sample); map dnaseq->subject via probit
wes = pd.read_csv(D._bp("beataml_wes_wv1to4_mutations_dbgap.txt"), sep="\t", usecols=["dbgap_sample_id","symbol","variant_classification"])
wes = wes[wes["variant_classification"].isin(NONSILENT)]
dna2subj = probit.dropna(subset=["dbgap_dnaseq_sample"]).drop_duplicates("dbgap_dnaseq_sample").set_index("dbgap_dnaseq_sample")["dbgap_subject_id"].to_dict()
wes["subject"] = wes["dbgap_sample_id"].map(dna2subj)
wes = wes.dropna(subset=["subject"])
wes_tested_subj = set(wes["subject"].unique())                      # subjects with WES
gene_subj = wes.groupby("symbol")["subject"].apply(set)
genes = [g for g in gene_subj.index if len(gene_subj[g]) >= MIN_GENE_SUBJ]
# clinical markers as pseudo-genes (NPM1 clinical, FLT3_ITD clinical) added to the tested set
print(f"recurrent genes (>={MIN_GENE_SUBJ} subj): {len(genes)}", flush=True)

# R_prolif per subject (expression rnaseq_sample -> subject)
bx = D.load_beataml_expression()
rp_samp = compute_r_prolif(bx)                                       # by rnaseq_sample
samp2subj = probit.dropna(subset=["dbgap_rnaseq_sample"]).drop_duplicates("dbgap_rnaseq_sample").set_index("dbgap_rnaseq_sample")["dbgap_subject_id"].to_dict()
rp = pd.Series({samp2subj[s]: rp_samp[s] for s in rp_samp.index if s in samp2subj})

drugs = [d for d in auc.index.get_level_values(1).unique() if auc.xs(d, level=1).shape[0] >= MIN_DRUG_SUBJ]
print(f"drugs (>={MIN_DRUG_SUBJ} subj): {len(drugs)} | testing up to {len(genes)}x{len(drugs)} pairs", flush=True)

def mut_series(gene):
    if gene == "FLT3_ITD": return itd
    if gene == "NPM1_clin": return npm1_clin
    gs = gene_subj[gene]
    return pd.Series({s: (1.0 if s in gs else 0.0) for s in wes_tested_subj})

test_genes = genes + ["FLT3_ITD", "NPM1_clin"]
rng_half = lambda s: int(hashlib.md5(str(s).encode()).hexdigest(), 16) % 2
rows = []
for gene in test_genes:
    ms = mut_series(gene)
    for drug in drugs:
        ad = auc.xs(drug, level=1)
        subj = [s for s in ad.index if s in ms.index and np.isfinite(ms.get(s, np.nan)) and s in rp.index]
        if len(subj) < MIN_DRUG_SUBJ: continue
        y = ad[subj].values; m = ms[subj].values.astype(float)
        if m.sum() < MIN_MUT or (len(m) - m.sum()) < MIN_MUT: continue
        itv = itd.reindex(subj).values.astype(float); pv = rp[subj].values.astype(float)
        cov = [m, pv] if gene == "FLT3_ITD" else [m, itv, pv]
        X = np.column_stack(cov); ok = np.all(np.isfinite(X), 1)
        if ok.sum() < MIN_DRUG_SUBJ or m[ok].sum() < MIN_MUT: continue
        res = sm.OLS(y[ok], sm.add_constant(X[ok], has_constant="add")).fit()
        b = float(res.params[1]); p = float(res.pvalues[1])
        # split-half direction
        h = np.array([rng_half(s) for s in subj])[ok]
        def bhalf(mask):
            if mask.sum() < 12 or m[ok][mask].sum() < 4: return np.nan
            r = sm.OLS(y[ok][mask], sm.add_constant(X[ok][mask], has_constant="add")).fit(); return float(r.params[1])
        b0, b1 = bhalf(h == 0), bhalf(h == 1)
        rep = bool(np.isfinite(b0) and np.isfinite(b1) and np.sign(b0) == np.sign(b) and np.sign(b1) == np.sign(b))
        rows.append({"gene": gene, "drug": drug, "n": int(ok.sum()), "n_mut": int(m[ok].sum()),
                     "beta": round(b, 3), "p": p, "direction": "sensitizing" if b < 0 else "resistance",
                     "split_replicates": rep})

df = pd.DataFrame(rows)
df["BHq"] = bh_fdr(df["p"].values)
disc = df[df["BHq"] < 0.05].copy().sort_values("BHq")
verified_grade = disc[disc["split_replicates"]].copy()
# positive controls present among DISCOVERED?
def has(g, d): return bool(((disc["gene"] == g) & (disc["drug"] == d)).any())
pc = {"NPM1_clin~cabozantinib": has("NPM1_clin", "cabozantinib"),
      "NRAS~trametinib": has("NRAS", "trametinib"), "NRAS~selumetinib": has("NRAS", "selumetinib"),
      "DNMT3A~dasatinib": has("DNMT3A", "dasatinib")}
pc_ok = sum(pc.values()) >= 2

print(f"\ntested pairs: {len(df)} | DISCOVERED (BHq<0.05): {len(disc)} | VERIFIED-GRADE (split-replicates): {len(verified_grade)}")
print("positive controls among discovered:", pc, "-> pipeline valid?", pc_ok)
print("\nTop verified-grade markers (sensitizing shown, |beta| desc):")
for _, r in verified_grade[verified_grade.direction == "sensitizing"].reindex(verified_grade[verified_grade.direction=="sensitizing"].beta.sort_values().index).head(15).iterrows():
    print(f"  {r['gene']:<10}->{r['drug']:<16} n={r['n']:>3} mut={r['n_mut']:>3} beta={r['beta']:+.1f} BHq={r['BHq']:.2e}")

if not pc_ok:
    raise SystemExit("POSITIVE CONTROLS MISSING — results void, not written.")

# emit
verified_grade_out = [{"gene": r["gene"], "drug": r["drug"], "direction": r["direction"], "n": r["n"],
                       "n_mut": r["n_mut"], "beta": r["beta"], "BHq": round(float(r["BHq"]), 6)}
                      for _, r in verified_grade.iterrows()]
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump({"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "provenance": "BeatAML B5; BH-FDR<0.05 + FLT3-ITD/prolif-deconfounded + split-replicated; ONE cohort, external replication still required",
           "markers": verified_grade_out}, open(os.path.join(HERE, "results", "discovered_markers.json"), "w"), indent=2)
out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "sklearn": sklearn.__version__, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "min_gene_subj": MIN_GENE_SUBJ, "min_drug_subj": MIN_DRUG_SUBJ, "n_genes": len(test_genes), "n_drugs": len(drugs),
       "n_pairs_tested": len(df), "n_discovered_BHq05": len(disc), "n_verified_grade": len(verified_grade),
       "positive_controls": pc, "pipeline_valid": pc_ok,
       "verified_grade_markers": verified_grade_out}
json.dump(out, open(os.path.join(HERE, "results", "B5_metrics.json"), "w"), indent=2)
print("wrote results/B5_metrics.json + discovered_markers.json")
