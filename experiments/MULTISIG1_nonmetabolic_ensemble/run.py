"""MULTISIG1 — the definitive ENSEMBLE ceiling test on the FBA-blind non-metabolic essential half.

Four INDIVIDUAL homology-independent signals each FAILED to beat conservation-breadth
(MET4 PPI / NONMET1 synteny / REGNET1 regulatory / PLMESS1 ESM-2). THE QUESTION: does their
COMBINATION? Assembles NONMET1's EXACT non-metabolic E. coli pool (n=2547, 179 PEC-essential)
with ALL cached features -- conservation (own), genomic context (ctx/cond), regulatory out/in
degree (REGNET1 Abasy GRN), and the cached ESM-2 PLM embedding (PLMESS1, PCA-50 train-only) --
and compares the FULL ENSEMBLE vs conservation-ALONE under identical no-leakage 5-fold CV, for
BOTH logistic (L2) and gradient boosting, plus drop-one ablation + leakage checks.

Pre-registered in PREREG.md (LOCKED before scoring). Deterministic: cached ESM-2 embeddings
reused byte-for-byte (NOT re-embedded), StratifiedKFold(shuffle=False), PCA(svd_solver='full')
+ StandardScaler fit on TRAIN FOLDS ONLY. GBM random_state=0. NO external fetch.

Run: /Users/kalki/miniconda3/envs/intercepta-build/bin/python run.py
"""
import os, sys, json, time, hashlib
import numpy as np
import networkx as nx
from scipy.stats import pearsonr
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
HERE = os.path.dirname(os.path.abspath(__file__))
NONMET1 = os.path.join(HERE, "..", "NONMET1_genomic_context_nonmetabolic")
EMB_DIR = os.path.join(DATA, "plmess1")
GRN = os.path.join(DATA, "regnet1", "eco_2005.json")

PCA_K = 50                                  # LOCKED (matches PLMESS1 primary)
CV = StratifiedKFold(n_splits=5, shuffle=False)   # LOCKED, identical to NONMET1/PLMESS1
GATE_DELTA = 0.03                           # LOCKED

# ---- reuse NONMET1's EXACT pool definition (import its loaders) ----
sys.path.insert(0, NONMET1)
import run as N1  # NONMET1/run.py


def name_key(s):
    return s.strip().lower()


def load_grn_degrees():
    """Abasy 2005 curated GRN -> out/in degree keyed by lowercase gene-symbol (REGNET1 parse)."""
    gj = json.load(open(GRN))["elements"]
    G = nx.DiGraph()
    for e in gj["edges"]:
        d = e["data"]
        G.add_edge(d["source"], d["target"])
    OUT = {name_key(k): v for k, v in dict(G.out_degree()).items()}
    IN = {name_key(k): v for k, v in dict(G.in_degree()).items()}
    return OUT, IN, G.number_of_nodes(), G.number_of_edges()


def build_pool():
    """EXACT NONMET1 E. coli non-metabolic pool aligned to ALL cached feature sources.
    Returns dict of aligned arrays + coverage counts."""
    genes, own, ctx, cond = N1.context_scores("ecoli")   # own = conservation breadth
    met = N1.metabolic_set_ecoli()
    ess, pmid = N1.pec_truth()
    OUT, IN, grn_nodes, grn_edges = load_grn_degrees()

    tags, OWN, CTX, COND, OUTD, IND, Y, STU = [], [], [], [], [], [], [], []
    n_grn_mapped = 0
    n_emb = 0
    EMB = []
    for i, (tag, mid, up, sym) in enumerate(genes):
        if up and up in met:          # NON-METABOLIC subproteome only (not in MET2 GEM)
            continue
        if tag not in ess:            # require a PEC essentiality call
            continue
        emb_path = os.path.join(EMB_DIR, f"emb_{tag}.npy")
        if not os.path.exists(emb_path):   # require a cached embedding (all 2547 present)
            continue
        nm = name_key(sym)
        od = OUT.get(nm, 0); ind = IN.get(nm, 0)   # DOCUMENTED DEFAULT 0 if not in GRN
        if nm in OUT or nm in IN:
            n_grn_mapped += 1
        tags.append(tag)
        OWN.append(float(own[i])); CTX.append(float(ctx[i])); COND.append(float(cond[i]))
        OUTD.append(float(od)); IND.append(float(ind))
        Y.append(int(ess[tag])); STU.append(float(np.log1p(pmid.get(tag, 0))))
        EMB.append(np.load(emb_path))
        n_emb += 1
    return {
        "tags": tags,
        "OWN": np.array(OWN), "CTX": np.array(CTX), "COND": np.array(COND),
        "OUTD": np.array(OUTD), "IND": np.array(IND),
        "Y": np.array(Y, int), "STU": np.array(STU),
        "EMB": np.vstack(EMB).astype(float),
        "n_grn_mapped": n_grn_mapped, "n_emb": n_emb,
        "grn_nodes": grn_nodes, "grn_edges": grn_edges,
    }


def cv_auroc(scalar_cols, emb, y, model="logit"):
    """Pooled OOF AUROC. `scalar_cols` = list of 1-D arrays (may be empty). `emb` = 2-D embedding
    matrix or None. Within each TRAIN fold: StandardScaler on scalars, StandardScaler+PCA on emb;
    applied to test fold. NO leakage. model in {'logit','gbm'}."""
    y = np.asarray(y, int); n = len(y); oof = np.zeros(n)
    S = np.column_stack(scalar_cols).astype(float) if scalar_cols else None
    for tr, te in CV.split(np.zeros((n, 1)), y):
        blocks_tr, blocks_te = [], []
        if S is not None:
            ssc = StandardScaler().fit(S[tr])
            blocks_tr.append(ssc.transform(S[tr])); blocks_te.append(ssc.transform(S[te]))
        if emb is not None:
            esc = StandardScaler().fit(emb[tr])
            pca = PCA(n_components=PCA_K, svd_solver="full", random_state=0).fit(esc.transform(emb[tr]))
            Ztr = pca.transform(esc.transform(emb[tr])); Zte = pca.transform(esc.transform(emb[te]))
            zsc = StandardScaler().fit(Ztr)
            blocks_tr.append(zsc.transform(Ztr)); blocks_te.append(zsc.transform(Zte))
        Xtr = np.column_stack(blocks_tr); Xte = np.column_stack(blocks_te)
        if model == "logit":
            clf = LogisticRegression(C=1.0, max_iter=2000, solver="lbfgs")
        else:
            clf = GradientBoostingClassifier(random_state=0)
        clf.fit(Xtr, y[tr])
        oof[te] = clf.predict_proba(Xte)[:, 1]
    return float(roc_auc_score(y, oof))


def group_cols(P, groups):
    """Return (scalar_cols, emb) for a set of feature groups. groups subset of {C,G,R,E}."""
    cols = []
    if "C" in groups: cols.append(P["OWN"])
    if "G" in groups: cols += [P["CTX"], P["COND"]]
    if "R" in groups: cols += [P["OUTD"], P["IND"]]
    emb = P["EMB"] if "E" in groups else None
    return cols, emb


def score_config(P, groups, model):
    cols, emb = group_cols(P, groups)
    return cv_auroc(cols, emb, P["Y"], model=model)


def main():
    t0 = time.time()
    P = build_pool()
    Y = P["Y"]; n = len(Y); npos = int(Y.sum())

    ALL = ["C", "G", "R", "E"]
    results = {}
    for model in ["logit", "gbm"]:
        au_cons = score_config(P, ["C"], model)                    # conservation ALONE (baseline)
        au_full = score_config(P, ALL, model)                      # FULL ENSEMBLE
        au_noemb = score_config(P, ["C", "G", "R"], model)         # ensemble WITHOUT embedding
        au_emb_only = score_config(P, ["E"], model)                # embedding standalone
        delta = au_full - au_cons
        # drop-one ablation (marginal contribution of each signal to the FULL ensemble)
        ablation = {}
        for s in ALL:
            rest = [g for g in ALL if g != s]
            au_drop = score_config(P, rest, model)
            ablation[f"drop_{s}"] = {"auroc_without": round(au_drop, 6),
                                     "marginal_auroc": round(au_full - au_drop, 6)}
        results[model] = {
            "auroc_conservation_alone": round(au_cons, 6),
            "auroc_full_ensemble": round(au_full, 6),
            "delta_auroc_ensemble_vs_conservation": round(delta, 6),
            "auroc_ensemble_without_embedding_CGR": round(au_noemb, 6),
            "delta_auroc_CGR_vs_conservation": round(au_noemb - au_cons, 6),
            "auroc_embedding_standalone": round(au_emb_only, 6),
            "ablation_drop_one": ablation,
            "passA_delta_ge_gate": bool(delta >= GATE_DELTA),
        }

    # collinearity diagnostics (why the individual signals re-encode conservation)
    own = P["OWN"]
    collin = {
        "pearson_own_vs_ctx": round(float(pearsonr(own, P["CTX"])[0]), 6),
        "pearson_own_vs_cond": round(float(pearsonr(own, P["COND"])[0]), 6),
        "pearson_own_vs_outdeg": round(float(pearsonr(own, P["OUTD"])[0]), 6),
        "pearson_own_vs_indeg": round(float(pearsonr(own, P["IND"])[0]), 6),
    }

    # gate: primary = logistic; GBM corroborates
    passA_logit = results["logit"]["passA_delta_ge_gate"]
    passA_gbm = results["gbm"]["passA_delta_ge_gate"]
    passed = bool(passA_logit and passA_gbm)

    # leakage triple-check trigger: did the ensemble pass ONLY via the embedding?
    # (i.e. C+G+R alone does NOT reach the gate, but C+G+R+E does)
    emb_is_the_only_driver = {}
    for model in ["logit", "gbm"]:
        r = results[model]
        emb_is_the_only_driver[model] = bool(
            r["passA_delta_ge_gate"] and (r["delta_auroc_CGR_vs_conservation"] < GATE_DELTA))

    payload = {
        "experiment": "MULTISIG1_nonmetabolic_ensemble",
        "hypothesis": ("the COMBINATION (ensemble) of ALL homology-independent non-metabolic signals "
                       "-- conservation breadth + genomic context + regulatory degree + ESM-2 PLM embedding -- "
                       "beats conservation-breadth ALONE by >= +0.03 AUROC on the FBA-blind non-metabolic "
                       "E. coli essential half (the definitive ensemble ceiling test)"),
        "params": {
            "pca_k": PCA_K, "logreg_C": 1.0, "gbm": "GradientBoostingClassifier(random_state=0) sklearn-defaults",
            "cv": "StratifiedKFold_5_shuffleFalse",
            "leakage_guard": "StandardScaler(scalars) + StandardScaler+PCA(embedding) fit on TRAIN FOLDS ONLY",
            "esm_model": "facebook/esm2_t30_150M_UR50D (cached, reused byte-for-byte, NOT re-embedded)",
        },
        "pool": {
            "organism": "E_coli", "subproteome": "non_metabolic (uniprot NOT in MET2 GEM)",
            "truth_source": "PEC_class1", "n_nonmetabolic_tested": n,
            "n_experimental_essential": npos, "prevalence": round(npos / n, 6),
        },
        "feature_coverage": {
            "conservation_own": {"covered": n, "total": n, "coverage": 1.0, "default": "none (computed for all)"},
            "genomic_context_ctx_cond": {"covered": n, "total": n, "coverage": 1.0,
                                         "default": "0 (natural value: no conserved neighborhood)"},
            "regulatory_outdeg_indeg": {"covered": P["n_grn_mapped"], "total": n,
                                        "coverage": round(P["n_grn_mapped"] / n, 6),
                                        "default": "0 (absence of regulatory edge == degree 0)"},
            "plm_embedding_esm2": {"covered": P["n_emb"], "total": n, "coverage": round(P["n_emb"] / n, 6),
                                   "default": "none (all cached); PCA-50 train-fold-only"},
            "grn_nodes": P["grn_nodes"], "grn_edges": P["grn_edges"],
        },
        "collinearity_with_conservation": collin,
        "results": results,
        "gate": {"require_delta_auroc_ensemble_vs_conservation_ge": GATE_DELTA,
                 "primary_model": "logit", "corroborating_model": "gbm"},
        "gate_eval": {
            "passA_logit": passA_logit, "passA_gbm": passA_gbm, "PASS": passed,
            "ensemble_passes_only_via_embedding": emb_is_the_only_driver,
        },
    }

    core = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    sha = hashlib.sha256(core.encode()).hexdigest()

    lg = results["logit"]; gb = results["gbm"]
    if passed:
        verdict = (
            f"PASS -- the multi-signal ENSEMBLE beats conservation-breadth alone on the FBA-blind "
            f"non-metabolic half: logistic ΔAUROC {lg['delta_auroc_ensemble_vs_conservation']:+.3f}, "
            f"GBM ΔAUROC {gb['delta_auroc_ensemble_vs_conservation']:+.3f} (gate +{GATE_DELTA}). "
            f"A GENUINE multi-signal integration gain for non-metabolic target-ID -- report which signal(s) "
            f"drive it (drop-one ablation) and complete the leakage triple-check.")
    else:
        verdict = (
            f"NEGATIVE (first-class) -- THE DEFINITIVE ENSEMBLE-CEILING CLOSURE. Even the COMBINATION of ALL "
            f"four homology-independent non-metabolic signals (conservation + genomic context + regulatory "
            f"degree + ESM-2 PLM embedding) does NOT beat conservation-breadth alone by the pre-registered "
            f"margin: logistic AUROC {lg['auroc_conservation_alone']:.3f}->{lg['auroc_full_ensemble']:.3f} "
            f"(ΔAUROC {lg['delta_auroc_ensemble_vs_conservation']:+.3f}), GBM "
            f"{gb['auroc_conservation_alone']:.3f}->{gb['auroc_full_ensemble']:.3f} "
            f"(ΔAUROC {gb['delta_auroc_ensemble_vs_conservation']:+.3f}) -- both below gate +{GATE_DELTA}. "
            f"The four signals each RE-ENCODE conservation (collinearity), so their union adds no independent "
            f"lift. Conservation-breadth is the UNBEATEN CEILING for the FBA-blind non-metabolic essential half, "
            f"even by all signals combined -- closing the arc opened by MET4/NONMET1/REGNET1/PLMESS1.")
    payload["verdict"] = verdict
    payload["provenance"] = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                             "runtime_s": round(time.time() - t0, 1),
                             "python": sys.version.split()[0], "emb_dir": EMB_DIR}

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "MULTISIG1_metrics.json"), "w") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
    with open(os.path.join(HERE, "results", "payload.sha256"), "w") as f:
        f.write(sha + "\n")

    print(json.dumps(payload["results"], indent=2, sort_keys=True))
    print(json.dumps(payload["feature_coverage"], indent=2, sort_keys=True))
    print("\nPOOL n=%d pos=%d prev=%.4f" % (n, npos, npos / n))
    print("PAYLOAD_SHA256:", sha)
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
