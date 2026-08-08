"""PLMESS1 — does a learned ESM-2 protein-language-model embedding predict NON-METABOLIC
essentiality AND add BEYOND conservation breadth? (4th principled attempt on the FBA-blind half.)

Pre-registered in PREREG.md (LOCKED before scoring). Reuses NONMET1's exact non-metabolic pool
+ own-conservation-breadth baseline for an apples-to-apples comparison. Truth = PEC.
Deterministic: cached ESM-2 embeddings, StratifiedKFold(shuffle=False), PCA(svd_solver='full'),
train-fold-only PCA+scaler (no leakage). Env: miniforge intercepta (torch 2.10 + transformers 4.41).

Run:  /Users/kalki/miniforge3/envs/intercepta/bin/python run.py
"""
import os, sys, json, time, hashlib
import numpy as np
from scipy.stats import fisher_exact, pearsonr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
HERE = os.path.dirname(os.path.abspath(__file__))
NONMET1 = os.path.join(HERE, "..", "NONMET1_genomic_context_nonmetabolic")
EMB_DIR = os.path.join(DATA, "plmess1"); os.makedirs(EMB_DIR, exist_ok=True)
FAA = os.path.join(DATA, "nonmet1", "prot", "ecoli.faa")

ESM_MODEL = "facebook/esm2_t30_150M_UR50D"
TRUNC = 1022                 # residues (LOCKED)
PCA_K_PRIMARY = 50           # LOCKED primary
PCA_K_SENS = [10, 100]       # sensitivity only (not gate)
CV = StratifiedKFold(n_splits=5, shuffle=False)   # LOCKED, identical to NONMET1
GATE_DELTA = 0.03            # LOCKED
GATE_STUDYBIAS_DELTA = 0.02  # LOCKED

# ---- reuse NONMET1's exact pool definition (import its loaders) ----
sys.path.insert(0, NONMET1)
import run as N1  # NONMET1/run.py  (openpyxl imported lazily inside dejesus_truth → safe)


def load_fasta():
    seqs = {}; acc = None
    for ln in open(FAA):
        ln = ln.rstrip("\n")
        if ln.startswith(">"):
            acc = ln[1:].strip()
        elif acc is not None:
            seqs[acc] = seqs.get(acc, "") + ln.strip()
    return seqs


def build_pool():
    """EXACT NONMET1 E. coli non-metabolic pool: (locus_tag, own_conservation, y, study, seq)."""
    genes, own, ctx, cond = N1.context_scores("ecoli")   # own = conservation breadth
    met = N1.metabolic_set_ecoli()
    ess, pmid = N1.pec_truth()
    fasta = load_fasta()
    rows = []
    for i, (tag, mid, up, sym) in enumerate(genes):
        if up and up in met:            # NON-METABOLIC only (not in MET2 GEM)
            continue
        if tag not in ess:              # require a PEC essentiality call
            continue
        if tag not in fasta:            # require a sequence to embed
            continue
        rows.append((tag, float(own[i]), int(ess[tag]), float(np.log1p(pmid.get(tag, 0))), fasta[tag]))
    return rows


def esm_embed(tags_seqs):
    """Deterministic CPU mean-pooled last-layer ESM-2 embedding, cached per locus_tag."""
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import torch
    from transformers import AutoTokenizer, AutoModel
    torch.manual_seed(0)
    need = [(t, s) for t, s in tags_seqs if not os.path.exists(os.path.join(EMB_DIR, f"emb_{t}.npy"))]
    if need:
        tok = AutoTokenizer.from_pretrained(ESM_MODEL, cache_dir=os.path.join(DATA, "hf_cache"))
        model = AutoModel.from_pretrained(ESM_MODEL, cache_dir=os.path.join(DATA, "hf_cache")).eval()
        t0 = time.time()
        with torch.no_grad():
            for k, (t, s) in enumerate(need):
                enc = tok(s[:TRUNC], return_tensors="pt", truncation=True, max_length=TRUNC + 2)
                h = model(**enc).last_hidden_state[0]
                mask = enc["attention_mask"][0].bool()
                v = h[mask].mean(0).cpu().numpy().astype(np.float32)
                np.save(os.path.join(EMB_DIR, f"emb_{t}.npy"), v)
                if (k + 1) % 250 == 0:
                    print(f"  embedded {k+1}/{len(need)}  ({round(time.time()-t0,1)}s)", flush=True)
        print(f"  embedding wall-clock: {round(time.time()-t0,1)}s for {len(need)} new proteins", flush=True)
    E = {t: np.load(os.path.join(EMB_DIR, f"emb_{t}.npy")) for t, _ in tags_seqs}
    return E


# ---------- CV scorers (train-fold-only PCA+scaler → NO leakage) ----------
def cv_auroc_scalar(X, y):
    """pooled OOF AUROC for low-dim scalar/vector features (StandardScaler on train only)."""
    X = np.asarray(X, float); y = np.asarray(y, int); oof = np.zeros(len(y))
    for tr, te in CV.split(X, y):
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs").fit(sc.transform(X[tr]), y[tr])
        oof[te] = clf.predict_proba(sc.transform(X[te]))[:, 1]
    return float(roc_auc_score(y, oof)), oof


def cv_embed(Emb, y, k, extra=None, C=1.0):
    """PCA(k)+L2 logistic; PCA+scaler fit on TRAIN folds only. `extra` = pre-scaled scalar cols
    (own / study) concatenated AFTER PCA so they are always retained. Returns (auroc, oof)."""
    y = np.asarray(y, int); n = len(y); oof = np.zeros(n)
    Emb = np.asarray(Emb, float)
    extra = None if extra is None else np.asarray(extra, float)
    for tr, te in CV.split(Emb, y):
        esc = StandardScaler().fit(Emb[tr])
        pca = PCA(n_components=k, svd_solver="full", random_state=0).fit(esc.transform(Emb[tr]))
        Ztr = pca.transform(esc.transform(Emb[tr])); Zte = pca.transform(esc.transform(Emb[te]))
        if extra is not None:
            xsc = StandardScaler().fit(extra[tr])
            Ztr = np.column_stack([Ztr, xsc.transform(extra[tr])])
            Zte = np.column_stack([Zte, xsc.transform(extra[te])])
        # standardize the PCA block on train too (PCA comps already ~unit-var but be safe/consistent)
        zsc = StandardScaler().fit(Ztr)
        clf = LogisticRegression(C=C, max_iter=2000, solver="lbfgs").fit(zsc.transform(Ztr), y[tr])
        oof[te] = clf.predict_proba(zsc.transform(Zte))[:, 1]
    return float(roc_auc_score(y, oof)), oof


def enrichment(score, y):
    thr = float(np.median(score)); hi = score >= thr
    a = int(np.sum(hi & (y == 1))); b = int(np.sum(hi & (y == 0)))
    c = int(np.sum(~hi & (y == 1))); d = int(np.sum(~hi & (y == 0)))
    orr, p = fisher_exact([[a, b], [c, d]], alternative="greater")
    return thr, {"both": a, "hi_noness": b, "lo_ess": c, "neither": d}, float(orr), float(p)


def main():
    t0 = time.time()
    rows = build_pool()
    tags = [r[0] for r in rows]
    OWN = np.array([r[1] for r in rows]); Y = np.array([r[2] for r in rows])
    STU = np.array([r[3] for r in rows]); SEQ = [r[4] for r in rows]
    Emb_map = esm_embed(list(zip(tags, SEQ)))
    EMB = np.vstack([Emb_map[t] for t in tags])
    n = len(Y); npos = int(Y.sum())

    # --- baselines & primary test (PCA-50) ---
    au_m1, _ = cv_auroc_scalar(OWN.reshape(-1, 1), Y)                       # conservation only
    au_emb, oof_emb = cv_embed(EMB, Y, PCA_K_PRIMARY)                       # embedding standalone
    au_m2, _ = cv_embed(EMB, Y, PCA_K_PRIMARY, extra=OWN.reshape(-1, 1))    # own + embed
    d_beyond_own = au_m2 - au_m1

    # --- study-bias control ---
    au_m3, _ = cv_auroc_scalar(np.column_stack([OWN, STU]), Y)              # own + study
    au_m4, _ = cv_embed(EMB, Y, PCA_K_PRIMARY, extra=np.column_stack([OWN, STU]))  # own + study + embed
    d_beyond_own_study = au_m4 - au_m3
    r_study_emb = float(pearsonr(STU, oof_emb)[0])

    # --- enrichment on the standalone-embedding OOF probability ---
    thr, cont, orr, p_fish = enrichment(oof_emb, Y)

    # --- sensitivity sweep (NOT part of the gate) ---
    sens = {}
    for k in PCA_K_SENS:
        a_e, _ = cv_embed(EMB, Y, k)
        a_2, _ = cv_embed(EMB, Y, k, extra=OWN.reshape(-1, 1))
        sens[f"pca_k{k}"] = {"auroc_embed_standalone": round(a_e, 6),
                             "auroc_own_plus_embed": round(a_2, 6),
                             "delta_embed_beyond_own": round(a_2 - au_m1, 6)}
    # raw-640 strong-L2 (C=0.1), no PCA: standardize on train only
    def cv_raw(C):
        oof = np.zeros(n)
        for tr, te in CV.split(EMB, Y):
            sc = StandardScaler().fit(EMB[tr])
            clf = LogisticRegression(C=C, max_iter=3000, solver="lbfgs").fit(sc.transform(EMB[tr]), Y[tr])
            oof[te] = clf.predict_proba(sc.transform(EMB[te]))[:, 1]
        return float(roc_auc_score(Y, oof))
    a_raw = cv_raw(0.1)
    # own + raw640 (concat, standardized on train)
    def cv_own_raw(C):
        oof = np.zeros(n); X = np.column_stack([OWN, EMB])
        for tr, te in CV.split(X, Y):
            sc = StandardScaler().fit(X[tr])
            clf = LogisticRegression(C=C, max_iter=3000, solver="lbfgs").fit(sc.transform(X[tr]), Y[tr])
            oof[te] = clf.predict_proba(sc.transform(X[te]))[:, 1]
        return float(roc_auc_score(Y, oof))
    a_own_raw = cv_own_raw(0.1)
    sens["raw640_L2_C0.1"] = {"auroc_embed_standalone": round(a_raw, 6),
                              "auroc_own_plus_embed": round(a_own_raw, 6),
                              "delta_embed_beyond_own": round(a_own_raw - au_m1, 6)}

    # --- gate ---
    passA = bool(d_beyond_own >= GATE_DELTA)
    passB = bool(d_beyond_own_study >= GATE_STUDYBIAS_DELTA)
    passed = bool(passA and passB)

    payload = {
        "experiment": "PLMESS1_plm_nonmetabolic",
        "hypothesis": "a learned ESM-2 protein-language-model embedding predicts non-metabolic "
                      "essentiality AND adds BEYOND conservation breadth (own) on the E. coli "
                      "non-metabolic subproteome",
        "params": {"esm_model": ESM_MODEL, "embedding": "mean_pooled_last_hidden_dim640",
                   "truncation_residues": TRUNC, "pca_k_primary": PCA_K_PRIMARY,
                   "logreg_C_primary": 1.0, "cv": "StratifiedKFold_5_shuffleFalse",
                   "leakage_guard": "PCA+StandardScaler fit on train folds only"},
        "pool": {"n_nonmetabolic_tested": n, "n_experimental_essential": npos,
                 "prevalence": round(npos / n, 6), "truth_source": "PEC_class1",
                 "subproteome": "non_metabolic (uniprot NOT in MET2 GEM)", "organism": "E_coli"},
        "results": {
            "auroc_M1_own_only": round(au_m1, 6),
            "auroc_embed_standalone_pca50": round(au_emb, 6),
            "auroc_M2_own_plus_embed": round(au_m2, 6),
            "delta_auroc_embed_beyond_own": round(d_beyond_own, 6),
            "studybias_auroc_M3_own_plus_study": round(au_m3, 6),
            "studybias_auroc_M4_own_study_embed": round(au_m4, 6),
            "delta_auroc_embed_beyond_own_study": round(d_beyond_own_study, 6),
            "study_proxy_pearson_with_embed_oof": round(r_study_emb, 6),
            "enrichment_embed_median_thr": round(thr, 6),
            "enrichment_contingency": cont,
            "enrichment_odds_ratio": round(orr, 6),
            "enrichment_fisher_p": round(p_fish, 12),
            "sensitivity": sens,
        },
        "gate": {"require_delta_auroc_beyond_own_ge": GATE_DELTA,
                 "require_studybias_delta_ge": GATE_STUDYBIAS_DELTA},
        "gate_eval": {"passA_delta_beyond_own": passA,
                      "passB_survives_studybias": passB, "PASS": passed},
    }
    core = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    sha = hashlib.sha256(core.encode()).hexdigest()

    r = payload["results"]
    if passed:
        verdict = (f"PASS — a learned ESM-2 PLM embedding is the FIRST homology-independent mechanistic "
                   f"signal for the FBA-blind non-metabolic essential half: ΔAUROC beyond conservation "
                   f"{r['delta_auroc_embed_beyond_own']:+.3f} (>= +{GATE_DELTA}), survives study-bias "
                   f"({r['delta_auroc_embed_beyond_own_study']:+.3f}). LEAKAGE TRIPLE-CHECK REQUIRED before ceiling-break claim.")
    else:
        verdict = (f"FAIL (first-class NEGATIVE) — a learned ESM-2 PLM embedding does NOT add a decisive "
                   f"signal beyond conservation breadth on the E. coli non-metabolic subproteome "
                   f"(ΔAUROC {r['delta_auroc_embed_beyond_own']:+.3f} vs gate +{GATE_DELTA}; standalone embed "
                   f"AUROC {r['auroc_embed_standalone_pca50']:.3f} < conservation {r['auroc_M1_own_only']:.3f}). "
                   f"FOURTH principled closure of the non-metabolic-mechanism door — now spanning LEARNED "
                   f"representations, not just network/conservation. Conservation breadth (AUROC {r['auroc_M1_own_only']:.3f}) "
                   f"remains the unbeaten baseline.")
    payload["verdict"] = verdict
    payload["provenance"] = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                             "runtime_s": round(time.time() - t0, 1),
                             "python": sys.version.split()[0], "emb_dir": EMB_DIR}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "PLMESS1_metrics.json"), "w") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
    with open(os.path.join(HERE, "results", "payload.sha256"), "w") as f:
        f.write(sha + "\n")
    print(json.dumps(payload["results"], indent=2, sort_keys=True))
    print("\nPOOL n=%d pos=%d" % (n, npos))
    print("PAYLOAD_SHA256:", sha)
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
