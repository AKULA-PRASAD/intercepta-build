"""B17 — does inferred-FLT3-dependency mark a SURVIVAL benefit from FLT3 inhibitors in BeatAML?
Implements prereg/B17_clinical_outcome.md. Cox PH interaction (dep x FLT3i) on overall survival.
Honest by design: BeatAML has no treatment dates/first-line FLT3i, so immortal-time + indication bias
push toward a spurious positive => a NULL interaction is the cleanly interpretable result; a positive is
confounded and NOT a clinical claim. Reproduce x2. Aggregate outputs only.
"""
import os, sys, json, time
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.duration.hazard_regression import PHReg
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta import data as D
from intercepta.engine import InterceptaEngine
from intercepta.axes import compute_r_prolif

HERE = os.path.dirname(os.path.abspath(__file__))
FLT3I_EXVIVO = ["sorafenib", "quizartinib", "gilteritinib", "crenolanib"]
FLT3I_DRUGNAMES = ["sorafenib", "midostaurin", "gilteritinib", "quizartinib", "crenolanib", "lestaurtinib", "sunitinib"]
TX_COLS = ["cumulativeTreatmentRegimens", "cumulativeTreatmentTypes", "currentRegimen", "mostRecentTreatmentType", "analysisDrug", "totalDrug"]

def z(a):
    a = np.asarray(a, float); s = a.std(); return (a - a.mean()) / s if s > 0 else a - a.mean()

def pos(x):
    s = str(x).strip().lower()
    return 1.0 if s in ("positive", "yes", "mutated", "pos") else (0.0 if s in ("negative", "no", "wildtype", "wt", "neg") else np.nan)

# --- inferred FLT3 dependency on BeatAML patient RNA (same layer as V19/B16) ---
eng = InterceptaEngine().fit(drugs=FLT3I_EXVIVO, compute_calibration=False, label_source="prism")
eng.fit_dependency(["FLT3"])
bx = D.load_beataml_expression()
inf = eng.infer_dependency(bx)["FLT3"]              # more negative = more dependent
dep_score = -inf                                    # higher = more FLT3-dependent
Rp = compute_r_prolif(bx)

# --- clinical: OS, vital, ITD, FLT3i exposure, age (raw xlsx has fields the packaged loader subsets out) ---
BEATAML_DIR = os.environ.get("INTERCEPTA_BEATAML", "/Users/kalki/INTERCEPTA/data/beataml")
clin = pd.read_excel(os.path.join(BEATAML_DIR, "beataml_wv1to4_clinical.xlsx"))
clin = clin.dropna(subset=["dbgap_rnaseq_sample"]).drop_duplicates("dbgap_rnaseq_sample").set_index("dbgap_rnaseq_sample")
age_col = next((c for c in clin.columns if "age" in c.lower() and "diagnos" in c.lower()), None) \
          or next((c for c in clin.columns if c.lower() == "ageatdiagnosis"), None)
os_days = pd.to_numeric(clin["overallSurvival"], errors="coerce")
vital = clin["vitalStatus"].astype(str).str.lower()
event = vital.map({"dead": 1.0, "alive": 0.0})       # NaN for Unknown -> dropped
itd = clin["FLT3-ITD"].map(pos)
blob = clin[[c for c in TX_COLS if c in clin.columns]].astype(str).agg(" | ".join, axis=1).str.lower()
flt3i = blob.apply(lambda s: 1.0 if any(nm in s for nm in FLT3I_DRUGNAMES) else 0.0)
age = pd.to_numeric(clin[age_col], errors="coerce") if age_col else pd.Series(np.nan, index=clin.index)

# --- assemble analysis frame (patients with RNA + usable OS) ---
samples = [s for s in dep_score.index if s in clin.index]
df = pd.DataFrame({
    "dep": dep_score.reindex(samples).values,
    "prolif": Rp.reindex(samples).values,
    "os": os_days.reindex(samples).values,
    "event": event.reindex(samples).values,
    "itd": itd.reindex(samples).values,
    "flt3i": flt3i.reindex(samples).values,
    "age": age.reindex(samples).values,
}, index=samples)
df = df[np.isfinite(df["os"]) & (df["os"] > 0) & df["event"].isin([0.0, 1.0])].copy()
have_age = bool(np.isfinite(df["age"]).sum() > 0.8 * len(df))
have_itd = True
df_model = df.dropna(subset=["dep", "prolif", "os", "event", "itd"] + (["age"] if have_age else []))

n = len(df_model); n_treat = int(df_model["flt3i"].sum()); n_event = int(df_model["event"].sum())
print(f"B17 clinical-outcome | patients w/ RNA+OS+covars={n}  FLT3i-treated={n_treat}  deaths={n_event}  age_col={age_col}", flush=True)

# --- Cox PH interaction model (primary) ---
d = df_model
X = pd.DataFrame({
    "dep": z(d["dep"]), "flt3i": d["flt3i"].values,
    "dep_x_flt3i": z(d["dep"]) * d["flt3i"].values,
    "itd": d["itd"].values, "prolif": z(d["prolif"]),
})
if have_age: X["age"] = z(d["age"])
cox = PHReg(d["os"].values, X.values, status=d["event"].values, ties="efron").fit()
names = list(X.columns)
params = dict(zip(names, cox.params)); pvals = dict(zip(names, cox.pvalues)); ses = dict(zip(names, cox.bse))
b3 = float(params["dep_x_flt3i"]); p3 = float(pvals["dep_x_flt3i"]); se3 = float(ses["dep_x_flt3i"])
H1 = bool(b3 < 0 and p3 < 0.05)

# --- secondary descriptive: dep->OS within treated vs untreated (univariable + ITD/prolif-adjusted) ---
def sub_cox(sub):
    if len(sub) < 20 or sub["event"].sum() < 8: return None
    Xs = pd.DataFrame({"dep": z(sub["dep"]), "itd": sub["itd"].values, "prolif": z(sub["prolif"])})
    if have_age: Xs["age"] = z(sub["age"])
    m = PHReg(sub["os"].values, Xs.values, status=sub["event"].values, ties="efron").fit()
    return {"n": int(len(sub)), "events": int(sub["event"].sum()),
            "dep_logHR": round(float(m.params[0]), 4), "dep_HR": round(float(np.exp(m.params[0])), 3),
            "dep_p": float(m.pvalues[0])}
treated = sub_cox(d[d["flt3i"] == 1.0]); untreated = sub_cox(d[d["flt3i"] == 0.0])

print(f"\nPRIMARY interaction dep_score x FLT3i:  logHR={b3:+.4f}  HR={np.exp(b3):.3f}  p={p3:.4g}  (H1<0 & p<.05: {H1})")
print(f"  main dep_score logHR={params['dep']:+.3f} p={pvals['dep']:.3g} | FLT3i logHR={params['flt3i']:+.3f} p={pvals['flt3i']:.3g} | ITD logHR={params['itd']:+.3f} p={pvals['itd']:.3g}")
print(f"  within FLT3i-TREATED : {treated}")
print(f"  within UNTREATED     : {untreated}")

if H1:
    verdict = ("HYPOTHESIS-CONSISTENT but CONFOUNDED: interaction favors FLT3i benefit in more-dependent patients, "
               "but BeatAML immortal-time/indication bias favors this a priori -> NOT a clinical claim; motivates Track-1.")
else:
    verdict = ("HONEST NEGATIVE: no interpretable interaction (inferred-FLT3-dependency does not mark FLT3i SURVIVAL "
               "benefit here). Robust given biases favor a positive; the clinical endpoint requires prospective Track-1 data.")
print("VERDICT:", verdict)

out = {"git_sha": os.popen("git rev-parse HEAD").read().strip(), "python": sys.version.split()[0],
       "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "n_patients": n, "n_flt3i_treated": n_treat, "n_deaths": n_event, "age_covariate": have_age,
       "cox_terms": {k: {"logHR": round(float(params[k]), 4), "HR": round(float(np.exp(params[k])), 3),
                         "se": round(float(ses[k]), 4), "p": float(pvals[k])} for k in names},
       "primary_interaction": {"term": "dep_score x FLT3i", "logHR": round(b3, 4), "HR": round(float(np.exp(b3)), 3),
                               "se": round(se3, 4), "p": p3, "H1_pass": H1},
       "within_flt3i_treated": treated, "within_untreated": untreated,
       "verdict": verdict}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "B17_metrics.json"), "w"), indent=2)
print("wrote results/B17_metrics.json")
