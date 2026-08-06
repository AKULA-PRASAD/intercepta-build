"""F3CLIN1 — Do DEPEND1 SELECTIVE cell-line CRISPR dependencies bridge to PATIENT-tumor DRIVER biology?

TARGET-RELEVANCE test (cell-line -> patient driver genes), DISTINCT from the failed human drug-RESPONSE line
(B20 FIMM FAIL, B10 TCGA confounded, B17 BeatAML null). Implements PREREG.md.
- Re-derive DEPEND1's SELECTIVE set (dep_frac 0.01-0.50; pan-essential >0.90 excluded) -> must reproduce 3664.
- Primary: Fisher 2x2 {selective} x {IntOGen patient driver} over the 17931-gene DepMap universe.
- Guards: (a) random-gene null; (b) publication-matched null (CancerMine NUM_PAPERS); (c) Mantel-Haenszel OR
  stratified by NUM_PAPERS decile. Supporting: recurrence dose-response + reverse-direction sanity.
Public data (DepMap; IntOGen CC0). CPU-only. Reproduce x2 byte-identical. Aggregate outputs only. NEVER commit data/push.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

SEED, K = 42, 10000
DEP_THRESH = -0.5
PAN_FRAC = 0.90
SEL_LO, SEL_HI = 0.01, 0.50
N_DECILES = 10
RECUR_MIN_COHORTS = 5          # frozen recurrence tier (PREREG §2)
TOP_N = [50, 100, 200]         # reverse-direction sanity depths
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("DEPEND1_DATA", "/Users/kalki/kaalcura/data")
IDIR = os.environ.get("F3CLIN1_INTOGEN",
                      "/Users/kalki/intercepta_data/f3clin1/2024-06-18_IntOGen-Drivers")

SHAS = {
 "depmap_crispr_gene_effect.csv": "d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00",
 "Compendium_Cancer_Genes.tsv":   "7c1982aa1fae1ff8200f4c2811cdb1707ea3f778b5e95782798d09e792ddb5e8",
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()

def verify(path, name):
    got = sha256(path)
    if got != SHAS[name]:
        raise RuntimeError(f"sha256 mismatch {name}: expected {SHAS[name]} got {got}")
    return path

def fisher_or_p(a, b, c, d):
    """OR + two-sided p for 2x2 [[a,b],[c,d]]."""
    orr, p = stats.fisher_exact([[a, b], [c, d]], alternative="two-sided")
    return float(orr), float(p)

print("F3CLIN1 | numpy", np.__version__, "| seed", SEED, flush=True)

# ---------------- 1. selective-dependency set (DEPEND1 exact definition) ----------------
ce_path = verify(os.path.join(DATA, "depmap_crispr_gene_effect.csv"), "depmap_crispr_gene_effect.csv")
ce = pd.read_csv(ce_path, index_col=0)
ce = ce.rename(columns={c: c.split(" (")[0] for c in ce.columns if " (" in c})
ce = ce.loc[:, ~ce.columns.duplicated()]
genes = list(ce.columns)
E = ce.values.astype(float)                         # n_lines x n_genes
n_lines, n_genes = E.shape
dep = (E < DEP_THRESH)
dep_frac = dep.mean(0)
pan_mask = dep_frac > PAN_FRAC
sel_mask = (dep_frac >= SEL_LO) & (dep_frac <= SEL_HI)
genes_arr = np.array(genes)
selective = set(genes_arr[sel_mask])
n_sel = int(sel_mask.sum())
n_pan = int(pan_mask.sum())
print(f"universe genes={n_genes}  SELECTIVE[{SEL_LO},{SEL_HI}]={n_sel}  PAN-ESSENTIAL(>{PAN_FRAC:.0%})={n_pan}", flush=True)
assert n_sel == 3664, f"selective set {n_sel} != DEPEND1's 3664 — definition drift"

universe = list(genes)                               # 17931 screened genes
uni_set = set(universe)

# ---------------- 2. IntOGen patient driver ground truth (+ recurrence) ----------------
comp_path = verify(os.path.join(IDIR, "Compendium_Cancer_Genes.tsv"), "Compendium_Cancer_Genes.tsv")
comp = pd.read_csv(comp_path, sep="\t", low_memory=False)
drivers_all = set(comp["SYMBOL"].unique())
recur = comp.groupby("SYMBOL").agg(n_cohorts=("COHORT", "nunique"),
                                   n_ctypes=("CANCER_TYPE", "nunique"),
                                   tot_samples=("SAMPLES", "sum"))
drivers = drivers_all & uni_set                      # drivers screened in DepMap
n_drv = len(drivers)
n_drv_not_screened = len(drivers_all - uni_set)
recurrent = {g for g in drivers if recur.loc[g, "n_cohorts"] >= RECUR_MIN_COHORTS}
focal = drivers - recurrent
print(f"IntOGen drivers total={len(drivers_all)}  in-universe={n_drv}  not-screened={n_drv_not_screened}  "
      f"recurrent(n_cohorts>={RECUR_MIN_COHORTS})={len(recurrent)}  focal={len(focal)}", flush=True)

drv_mask = np.array([g in drivers for g in universe])

# ---------------- 3. PRIMARY 2x2 Fisher ----------------
a = int(np.sum(sel_mask & drv_mask))                 # selective & driver
b = int(np.sum(sel_mask & ~drv_mask))                # selective & not-driver
c = int(np.sum(~sel_mask & drv_mask))                # not-selective & driver
d = int(np.sum(~sel_mask & ~drv_mask))               # not-selective & not-driver
OR, P = fisher_or_p(a, b, c, d)
sel_driver_rate = a / (a + b)
nonsel_driver_rate = c / (c + d)
print(f"\n2x2  selective&driver={a}  selective&~driver={b}  ~selective&driver={c}  ~selective&~driver={d}")
print(f"Fisher OR={OR:.3f}  p={P:.3g}  | driver-rate: selective={sel_driver_rate:.4f} vs "
      f"non-selective={nonsel_driver_rate:.4f}", flush=True)

# ---------------- 4a. random-gene null (full universe) ----------------
rng = np.random.default_rng(SEED)
drv_idx = np.where(drv_mask)[0]
N = n_genes
null_overlap = np.empty(K, dtype=int)
for k in range(K):
    pick = rng.choice(N, n_sel, replace=False)
    null_overlap[k] = np.sum(drv_mask[pick])
p_rand = float((np.sum(null_overlap >= a) + 1) / (K + 1))
# null OR distribution (same fixed marginals)
xo = null_overlap.astype(float)
null_or = (xo * (N - n_sel - n_drv + xo)) / (np.maximum(n_sel - xo, 1e-9) * np.maximum(n_drv - xo, 1e-9))
print(f"\n[guard a] random-gene null: expected overlap={xo.mean():.1f} (95pct={np.percentile(xo,95):.0f}) "
      f"observed={a}  emp p={p_rand:.4g}  null OR mean={null_or.mean():.3f}", flush=True)

# ---------------- study-bias proxy: CancerMine NUM_PAPERS ----------------
unf = pd.read_csv(os.path.join(IDIR, "Unfiltered_drivers.tsv"), sep="\t", low_memory=False)
papers = unf.groupby("SYMBOL")["NUM_PAPERS"].max()
pb_genes = [g for g in universe if g in papers.index]        # universe genes with a NUM_PAPERS value
pb_idx = np.array([universe.index(g) for g in pb_genes])
pb_papers = papers.reindex(pb_genes).values.astype(float)
pb_sel = sel_mask[pb_idx]
pb_drv = drv_mask[pb_idx]
n_pb = len(pb_genes)
# rank-based deciles (deterministic; secondary sort by gene name to break paper-count ties stably)
order = sorted(range(n_pb), key=lambda i: (pb_papers[i], pb_genes[i]))
decile = np.empty(n_pb, dtype=int)
for rank, i in enumerate(order):
    decile[i] = min(N_DECILES - 1, rank * N_DECILES // n_pb)
print(f"\nstudy-bias subset: {n_pb} universe genes with NUM_PAPERS; selective={int(pb_sel.sum())} "
      f"drivers={int(pb_drv.sum())}", flush=True)

# ---------------- 4b. publication-matched null ----------------
obs_pb_overlap = int(np.sum(pb_sel & pb_drv))
# per-decile: how many selective genes, and the pool of gene-indices (into pb arrays) to draw from
dec_pool = {s: np.where(decile == s)[0] for s in range(N_DECILES)}
dec_nsel = {s: int(np.sum(pb_sel[dec_pool[s]])) for s in range(N_DECILES)}
matched_overlap = np.empty(K, dtype=int)
for k in range(K):
    tot = 0
    for s in range(N_DECILES):
        pool = dec_pool[s]; m = dec_nsel[s]
        if m == 0: continue
        pick = rng.choice(pool, m, replace=False)
        tot += int(np.sum(pb_drv[pick]))
    matched_overlap[k] = tot
p_matched = float((np.sum(matched_overlap >= obs_pb_overlap) + 1) / (K + 1))
print(f"[guard b] publication-matched null: observed sel-driver overlap(pb)={obs_pb_overlap}  "
      f"matched-null mean={matched_overlap.mean():.1f} (95pct={np.percentile(matched_overlap,95):.0f})  "
      f"emp p={p_matched:.4g}", flush=True)

# ---------------- 4c. Mantel-Haenszel OR stratified by NUM_PAPERS decile ----------------
num = den = 0.0
cmh_num = 0.0; cmh_var = 0.0
strata_rows = []
for s in range(N_DECILES):
    idx = dec_pool[s]
    sm = pb_sel[idx]; dm = pb_drv[idx]
    a_s = int(np.sum(sm & dm)); b_s = int(np.sum(sm & ~dm))
    c_s = int(np.sum(~sm & dm)); d_s = int(np.sum(~sm & ~dm))
    n_s = a_s + b_s + c_s + d_s
    if n_s == 0: continue
    num += a_s * d_s / n_s
    den += b_s * c_s / n_s
    row1 = a_s + b_s; row2 = c_s + d_s; col1 = a_s + c_s; col2 = b_s + d_s
    cmh_num += a_s - row1 * col1 / n_s
    if n_s > 1:
        cmh_var += (row1 * row2 * col1 * col2) / (n_s * n_s * (n_s - 1))
    strata_rows.append({"decile": s, "n": n_s, "a_sel_drv": a_s, "sel": row1, "drv": col1})
mh_or = float(num / den) if den > 0 else float("inf")
cmh_chi2 = float((abs(cmh_num) - 0.5) ** 2 / cmh_var) if cmh_var > 0 else 0.0
mh_p = float(stats.chi2.sf(cmh_chi2, 1))
print(f"[guard c] Mantel-Haenszel OR (NUM_PAPERS-decile stratified)={mh_or:.3f}  CMH p={mh_p:.4g}", flush=True)

# ---------------- 5. recurrence dose-response (supporting) ----------------
def or_for(subset):
    m = np.array([g in subset for g in universe])
    aa = int(np.sum(sel_mask & m)); bb = int(np.sum(sel_mask & ~m))
    cc = int(np.sum(~sel_mask & m)); dd = int(np.sum(~sel_mask & ~m))
    o, pp = fisher_or_p(aa, bb, cc, dd)
    return {"OR": round(o, 4), "p": pp, "sel_hits": aa, "n_set": int(m.sum())}
or_recurrent = or_for(recurrent)
or_focal = or_for(focal)
print(f"\n[recurrence] recurrent-driver OR={or_recurrent['OR']} (p={or_recurrent['p']:.3g})  "
      f"focal-driver OR={or_focal['OR']} (p={or_focal['p']:.3g})", flush=True)

# ---------------- 6. reverse-direction sanity ----------------
sel_cols = np.where(sel_mask)[0]
k5 = max(1, int(np.ceil(0.05 * n_lines)))
strength = {}
for j in sel_cols:
    col = E[:, j]; col = col[np.isfinite(col)]
    if col.size == 0: continue
    bottom = np.sort(col)[:k5]                       # most-dependent 5% (most negative)
    strength[genes[j]] = float(col.mean() - bottom.mean())
ranked = sorted(strength, key=lambda g: -strength[g])
base_rate = n_drv / n_genes
rev = {}
for t in TOP_N:
    top = ranked[:t]
    hits = sum(g in drivers for g in top)
    rev[t] = {"driver_frac": round(hits / t, 4), "n_driver": hits}
top_examples = [{"gene": g, "strength": round(strength[g], 3), "is_driver": g in drivers,
                 "dep_frac": round(float(dep_frac[genes.index(g)]), 4)} for g in ranked[:15]]
print(f"[reverse] universe driver base-rate={base_rate:.4f}; top-selective driver fractions: "
      + ", ".join(f"top{t}={rev[t]['driver_frac']:.3f}" for t in TOP_N))
print("  top-15 selectively-essential genes:",
      ", ".join(f"{e['gene']}{'*' if e['is_driver'] else ''}" for e in top_examples))

# ---------------- gate verdict ----------------
above_null = bool(OR > 2 and P < 0.01 and p_rand < 0.01)
survives_bias = bool(p_matched < 0.01 and mh_or > 2 and mh_p < 0.01)
if above_null and survives_bias:
    gate = "PASS"
elif above_null:
    gate = "PARTIAL"
else:
    gate = "NEGATIVE"

verdict = (f"F3CLIN1 dependency->patient-driver relevance = {gate}. "
           f"SELECTIVE cell-line dependencies (n={n_sel}) vs IntOGen patient drivers (n={n_drv} in universe): "
           f"Fisher OR={OR:.2f} p={P:.1e}, above random-gene null (emp p={p_rand:.3g}); "
           f"study-bias controls: publication-matched null p={p_matched:.3g}, Mantel-Haenszel OR={mh_or:.2f} "
           f"(CMH p={mh_p:.3g}). Recurrence dose-response: recurrent-driver OR={or_recurrent['OR']} > "
           f"focal-driver OR={or_focal['OR']}. "
           f"SCOPE: cell-line->patient TARGET-RELEVANCE only. Does NOT rescue drug-RESPONSE prediction "
           f"(B20/B10/B17 negative), is NOT clinical outcome, and carries a study/annotation-bias caveat.")
print("\n================ VERDICT ================\n" + verdict)
print(f"gate={gate}  (above_null={above_null}, survives_study_bias={survives_bias})")

# ---------------- payload (numeric only; EXCLUDES verdict/provenance) ----------------
payload = {
 "seed": SEED, "K": K, "dep_thresh": DEP_THRESH, "pan_frac": PAN_FRAC, "sel_band": [SEL_LO, SEL_HI],
 "n_deciles": N_DECILES, "recur_min_cohorts": RECUR_MIN_COHORTS, "top_n": TOP_N,
 "n_lines": int(n_lines), "n_genes_universe": int(n_genes),
 "n_selective": n_sel, "n_pan_essential": n_pan,
 "n_drivers_total": len(drivers_all), "n_drivers_in_universe": n_drv,
 "n_drivers_not_screened": n_drv_not_screened,
 "n_recurrent_drivers": len(recurrent), "n_focal_drivers": len(focal),
 "fisher_2x2": {"a_sel_drv": a, "b_sel_nondrv": b, "c_nonsel_drv": c, "d_nonsel_nondrv": d,
                "OR": round(OR, 4), "p": P,
                "sel_driver_rate": round(sel_driver_rate, 5),
                "nonsel_driver_rate": round(nonsel_driver_rate, 5)},
 "guard_a_random_null": {"expected_overlap": round(float(xo.mean()), 3),
                         "overlap_p95": float(np.percentile(xo, 95)),
                         "observed_overlap": a, "emp_p": p_rand,
                         "null_or_mean": round(float(null_or.mean()), 4)},
 "guard_b_publication_matched_null": {"n_pb_genes": n_pb, "observed_overlap_pb": obs_pb_overlap,
                                      "matched_null_mean": round(float(matched_overlap.mean()), 3),
                                      "matched_null_p95": float(np.percentile(matched_overlap, 95)),
                                      "emp_p": p_matched},
 "guard_c_mantel_haenszel": {"mh_or": round(mh_or, 4), "cmh_chi2": round(cmh_chi2, 4), "cmh_p": mh_p,
                             "strata": strata_rows},
 "recurrence_dose_response": {"recurrent": or_recurrent, "focal": or_focal},
 "reverse_sanity": {"universe_driver_base_rate": round(base_rate, 5), "top_n_driver_frac": rev,
                    "top15_examples": top_examples},
 "gate": {"above_null": above_null, "survives_study_bias": survives_bias, "verdict": gate},
}
payload_json = json.dumps(payload, sort_keys=True)
sha = hashlib.sha256(payload_json.encode()).hexdigest()

out = dict(payload)
out["verdict"] = verdict
out["input_sha256"] = SHAS
out["intogen_release"] = "2024-06-18 (IntOGen-Drivers-20240920.zip, CC0)"
out["git_sha"] = os.popen("git rev-parse HEAD").read().strip()
out["python"] = sys.version.split()[0]
out["pandas"] = pd.__version__; out["scipy"] = stats.__name__ and __import__("scipy").__version__
out["timestamp_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
out["payload_sha256"] = sha

os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "F3CLIN1_metrics.json"), "w"), indent=2, sort_keys=True)
open(os.path.join(HERE, "results", "payload.sha256"), "w").write(sha + "\n")
print("\npayload_sha256:", sha)
print("wrote results/F3CLIN1_metrics.json + results/payload.sha256")
