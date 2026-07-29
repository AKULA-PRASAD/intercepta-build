"""B21 (POST-HOC / EXPLORATORY) — does the functional-inference signal survive for FLT3-SELECTIVE inhibitors,
CONSISTENTLY across BeatAML AND FIMM? Implements prereg/B21_selectivity_crosscohort.md. The last honest
computational question on the functional layer: is there a narrow cross-cohort-consistent slice, or is the door
closed? Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.axes import compute_r_prolif

SEED, MIN_N, NPERM = 42, 25, 20000
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
FIMM = os.path.join(DATA, "fimm_aml", "Functional_Precision_Medicine_Tumor_Board_AML")
SELECTIVE = {"quizartinib", "crenolanib", "gilteritinib"}     # a-priori FLT3-dominant
PROMISCUOUS = {"sorafenib", "sunitinib", "midostaurin", "dovitinib", "tandutinib"}  # a-priori multi-kinase
BEATAML_DRUGS = ["sorafenib", "quizartinib", "gilteritinib", "crenolanib"]
FIMM_DRUGS = ["sorafenib", "quizartinib", "crenolanib", "midostaurin", "sunitinib", "tandutinib", "dovitinib"]
rng = np.random.default_rng(SEED)

def resid(x, c):
    x = np.asarray(x, float); c = np.asarray(c, float); A = np.column_stack([np.ones_like(c), c])
    b, *_ = np.linalg.lstsq(A, x, rcond=None); return x - A @ b
def padj(dv, y, rp):  # prolif-adjusted Spearman; + = sensitizing (y already oriented higher=sensitive)
    return float(stats.spearmanr(resid(dv, rp), resid(y, rp))[0])

# ---- shared engine + inferred FLT3 dependency ----
eng = InterceptaEngine().fit(drugs=BEATAML_DRUGS, compute_calibration=False, label_source="prism")
eng.fit_dependency(["FLT3"])

def cohort_effects(expr, resp_long, drugs, sens_sign):
    """resp_long: DataFrame [sample, drug, value]; sens_sign=+1 if value already higher=sensitive (DSS),
    -1 if higher=resistant (AUC). Returns {drug: (n, effect)} with + = sensitizing."""
    dep = -eng.infer_dependency(expr)["FLT3"]           # higher = more dependent
    Rp = compute_r_prolif(expr)
    out = {}
    for drug in drugs:
        a = resp_long[resp_long["drug"] == drug].groupby("sample")["value"].mean()
        S = [s for s in a.index if s in dep.index and s in Rp.index]
        if len(S) < MIN_N: continue
        sens = sens_sign * a[S].values.astype(float)     # orient: higher = sensitive
        out[drug] = (len(S), padj(dep[S].values, sens, Rp[S].values))
    return out

# ---- BeatAML (AUC: higher=resistant -> sens_sign=-1) ----
bx = D.load_beataml_expression()
bauc = D.load_beataml_auc(); bauc = bauc[bauc["sample"].isin(set(bx.columns))]
b_long = bauc.rename(columns={"auc": "value"})[["sample", "drug", "value"]]
eff_beat = cohort_effects(bx, b_long, BEATAML_DRUGS, sens_sign=-1)

# ---- FIMM (DSS: higher=sensitive -> sens_sign=+1) ----
m = pd.read_csv(os.path.join(DATA, "ensg2symbol.tsv"), sep="\t").set_index("ensg")["symbol"].to_dict()
cpm = pd.read_csv(os.path.join(FIMM, "File_7_RNA_seq_CPM_163S_4Healthy.csv")).rename(columns={"Unnamed: 0": "ensg"})
cpm["sym"] = cpm["ensg"].str.split(".").str[0].map(m); cpm = cpm.dropna(subset=["sym"]).drop(columns=["ensg"])
fexpr = cpm.groupby("sym").max(numeric_only=True); fexpr = fexpr[[c for c in fexpr.columns if str(c).startswith("AML")]]
dss = pd.read_excel(os.path.join(FIMM, "File_3.2_Drug_response_DSS_sDSS_164S_17Healthy.xlsx"), skiprows=2)
dss["drug"] = dss["Chemical_compound"].astype(str).str.lower()
f_long = dss.rename(columns={"Sample_ID": "sample", "DSS": "value"})[["sample", "drug", "value"]].dropna()
eff_fimm = cohort_effects(fexpr, f_long, FIMM_DRUGS, sens_sign=+1)

def tag(d): return "selective" if d in SELECTIVE else ("promiscuous" if d in PROMISCUOUS else "?")
print("Per-drug prolif-adjusted effect (+ = sensitizing):")
print("  BeatAML:", {d: (n, round(e, 3), tag(d)) for d, (n, e) in eff_beat.items()})
print("  FIMM   :", {d: (n, round(e, 3), tag(d)) for d, (n, e) in eff_fimm.items()})

# ---- H1: cross-cohort per-drug consistency (shared drugs) ----
shared = sorted(set(eff_beat) & set(eff_fimm))
pairs = [(d, eff_beat[d][1], eff_fimm[d][1]) for d in shared]
same_sign = sum(1 for _, b, f in pairs if np.sign(b) == np.sign(f))
sel_pos_both = all(eff_beat.get(d, (0, -1))[1] > 0 and eff_fimm.get(d, (0, -1))[1] > 0
                   for d in (SELECTIVE & set(eff_beat) & set(eff_fimm)))
H1 = bool(same_sign >= 2 and sel_pos_both)

# ---- H2: selective vs promiscuous, label-permutation within EACH cohort ----
def sel_gap(eff):
    sel = [e for d, (n, e) in eff.items() if d in SELECTIVE]; pro = [e for d, (n, e) in eff.items() if d in PROMISCUOUS]
    if not sel or not pro: return None, None, None
    gap = float(np.mean(sel) - np.mean(pro))
    labels = [d for d in eff]; vals = np.array([eff[d][1] for d in labels]); nsel = sum(d in SELECTIVE for d in labels)
    perm = []
    for _ in range(NPERM):
        p = rng.permutation(vals); perm.append(np.mean(p[:nsel]) - np.mean(p[nsel:]))
    perm = np.array(perm); pv = float((1 + np.sum(perm >= gap)) / (1 + len(perm)))
    return gap, pv, (float(np.mean(sel)), float(np.mean(pro)))
gap_b, p_b, ms_b = sel_gap(eff_beat); gap_f, p_f, ms_f = sel_gap(eff_fimm)
H2 = bool(gap_b is not None and gap_f is not None and gap_b > 0 and gap_f > 0 and p_b < 0.05 and p_f < 0.05)

print(f"\nH1 cross-cohort consistency: shared={shared} same_sign={same_sign}/{len(pairs)} selective_pos_both={sel_pos_both} -> {H1}")
for d, b, f in pairs: print(f"    {d:<12} BeatAML {b:+.3f} | FIMM {f:+.3f}  {'AGREE' if np.sign(b)==np.sign(f) else 'CONTRADICT'} ({tag(d)})")
print(f"H2 selective>promiscuous: BeatAML gap={gap_b:+.3f} p={p_b:.3g} (sel {ms_b[0]:+.3f} vs pro {ms_b[1]:+.3f}) | "
      f"FIMM gap={gap_f:+.3f} p={p_f:.3g} (sel {ms_f[0]:+.3f} vs pro {ms_f[1]:+.3f}) -> {H2}")

if H1 and H2:
    verdict = ("NARROW SIGNAL SURVIVES: FLT3-selective inhibitors show a cross-cohort-consistent inferred-dependency "
               "effect (hypothesis-generating, NOT validated; post-hoc). Justifies a focused prospective look.")
else:
    verdict = ("DOOR CLOSED: no stable cross-cohort slice — per-drug effects are inconsistent across cohorts "
               "(notably sorafenib flips sign) and selectivity does not separate them consistently. B20 non-"
               "replication confirmed at the per-drug level; the functional-inference computational avenue is "
               "exhausted. Path forward = prospective functional data (Track-1).")
print("\nVERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "seed": SEED, "n_perm": NPERM,
       "post_hoc": True,
       "beataml_effects": {d: {"n": n, "effect": round(e, 4), "class": tag(d)} for d, (n, e) in eff_beat.items()},
       "fimm_effects": {d: {"n": n, "effect": round(e, 4), "class": tag(d)} for d, (n, e) in eff_fimm.items()},
       "shared_drugs": shared, "same_sign_count": same_sign, "H1_consistency_pass": H1,
       "beataml_sel_gap": gap_b, "beataml_sel_p": p_b, "fimm_sel_gap": gap_f, "fimm_sel_p": p_f, "H2_selectivity_pass": H2,
       "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B21_metrics.json"), "w"), indent=2)
print("wrote results/B21_metrics.json")
