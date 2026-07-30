"""B38 — deep molecular foundation model: does a pretrained ChemBERTa (77M-molecule RoBERTa) embedding beat/augment
raw structure (Morgan+physchem) on held-out outcomes? The deepest integration test. Implements
prereg/B38_deep_foundation_model.md. FM embeddings deterministic (eval, rounded) -> reproduce x2.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
os.environ.setdefault("HF_HOME", "/Users/kalki/kaalcura/data/hf_cache")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
from intercepta.admet import featurize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
TOXP = os.path.join(DATA, "tdc_tox")
FM_NAME = "DeepChem/ChemBERTa-77M-MLM"
OUTCOMES = [("clintox", None), ("skin_reaction", None), ("carcinogens_lagunin", None),
            ("tox21", "NR-AR"), ("tox21", "NR-ER"), ("tox21", "SR-MMP"), ("tox21", "SR-p53")]
SEEDS = [1, 2, 3]
MOL_CAP = 4000
BOOT = 2000
GBT = dict(random_state=42, max_iter=200, learning_rate=0.06, max_depth=6)

_TOK = _MDL = None
def _fm():
    global _TOK, _MDL
    if _MDL is None:
        import torch
        from transformers import AutoTokenizer, AutoModel
        torch.manual_seed(42)
        _TOK = AutoTokenizer.from_pretrained(FM_NAME)
        _MDL = AutoModel.from_pretrained(FM_NAME).eval()
    return _TOK, _MDL


def fm_embed(smiles, batch=64):
    import torch
    tok, mdl = _fm()
    out = []
    with torch.no_grad():
        for i in range(0, len(smiles), batch):
            chunk = [str(s) for s in smiles[i:i + batch]]
            enc = tok(chunk, padding=True, truncation=True, max_length=128, return_tensors="pt")
            h = mdl(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1)
            emb = (h * m).sum(1) / m.sum(1).clamp(min=1)
            out.append(emb.cpu().numpy())
    return np.round(np.vstack(out).astype(np.float64), 5)          # round -> deterministic reproduce x2


def canon(s):
    m = Chem.MolFromSmiles(str(s)); return Chem.MolToSmiles(m) if m else None
def murcko(s):
    try: return MurckoScaffold.MurckoScaffoldSmiles(smiles=str(s), includeChirality=False)
    except Exception: return ""


def load_outcome(name, label):
    from tdc.single_pred import Tox
    df = Tox(name=name, label_name=label, path=TOXP).get_data() if label else Tox(name=name, path=TOXP).get_data()
    df = df.dropna(subset=["Y", "Drug"]).copy(); df["canon"] = [canon(s) for s in df["Drug"]]
    df = df.dropna(subset=["canon"]).drop_duplicates("canon").reset_index(drop=True)
    if len(df) > MOL_CAP:
        df = df.iloc[np.random.default_rng(42).permutation(len(df))[:MOL_CAP]].reset_index(drop=True)
    return df


def per_outcome_stats(A, B, C, y, scaff):
    idx = np.arange(len(y))
    dCA, dBA, aA, aB, aC = [], [], [], [], []
    for seed in SEEDS:
        uniq = np.array(sorted(set(scaff))); perm = np.random.default_rng(seed).permutation(uniq)
        tsc = set(perm[:int(0.2 * len(perm))]); te = np.array([s in tsc for s in scaff]); tr = ~te
        if len(np.unique(y[te])) < 2 or len(np.unique(y[tr])) < 2: continue
        def fit(Z): return roc_auc_score(y[te], HistGradientBoostingClassifier(**GBT).fit(Z[tr], y[tr]).predict_proba(Z[te])[:, 1])
        a, b, c = fit(A), fit(B), fit(C); aA.append(a); aB.append(b); aC.append(c); dCA.append(c - a); dBA.append(b - a)
    # molecule-level pooled OOF bootstrap for C vs A
    uniq = np.array(sorted(set(scaff))); perm = np.random.default_rng(0).permutation(uniq)
    fol = {s: i % 5 for i, s in enumerate(perm)}; fof = np.array([fol[s] for s in scaff])
    oA = np.full(len(y), np.nan); oC = np.full(len(y), np.nan)
    for f in range(5):
        te = fof == f; tr = ~te
        if len(np.unique(y[tr])) < 2: continue
        oA[te] = HistGradientBoostingClassifier(**GBT).fit(A[tr], y[tr]).predict_proba(A[te])[:, 1]
        oC[te] = HistGradientBoostingClassifier(**GBT).fit(C[tr], y[tr]).predict_proba(C[te])[:, 1]
    ok = np.isfinite(oA) & np.isfinite(oC); rng = np.random.default_rng(7); n = int(ok.sum()); bd = []
    for _ in range(BOOT):
        bi = rng.integers(0, n, n)
        if len(np.unique(y[ok][bi])) < 2: continue
        bd.append(roc_auc_score(y[ok][bi], oC[ok][bi]) - roc_auc_score(y[ok][bi], oA[ok][bi]))
    lo, hi = np.percentile(bd, [2.5, 97.5])
    return (round(float(np.mean(aA)), 4), round(float(np.mean(aB)), 4), round(float(np.mean(aC)), 4),
            round(float(np.mean(dCA)), 4), round(float(np.mean(dBA)), 4), round(float(lo), 4), round(float(hi), 4))


def main():
    per = []
    for name, label in OUTCOMES:
        key = f"{name}:{label}" if label else name
        df = load_outcome(name, label); y = df["Y"].values.astype(int)
        if len(np.unique(y)) < 2 or int(y.sum()) < 15:
            per.append({"outcome": key, "skipped": True}); continue
        S, _ = featurize(df["Drug"].tolist()); B = fm_embed(df["Drug"].tolist()); C = np.hstack([S, B])
        scaff = np.array([murcko(s) for s in df["Drug"]], dtype=object)
        aA, aB, aC, dCA, dBA, lo, hi = per_outcome_stats(S, B, C, y, scaff)
        per.append({"outcome": key, "n": int(len(df)), "n_positive": int(y.sum()),
                    "auroc_structure_A": aA, "auroc_FM_B": aB, "auroc_both_C": aC,
                    "delta_C_minus_A": dCA, "delta_B_minus_A": dBA, "oof_C_minus_A_ci95": [lo, hi],
                    "oof_significant": bool(lo > 0)})
        print(f"  {key:22s} n={len(df):5d} pos={int(y.sum()):4d} | A {aA:.3f} FM {aB:.3f} C {aC:.3f} | ΔC-A {dCA:+.4f} ΔB-A {dBA:+.4f} sig={per[-1]['oof_significant']}")

    scored = [p for p in per if "delta_C_minus_A" in p]
    dCA = np.array([p["delta_C_minus_A"] for p in scored]); dBA = np.array([p["delta_B_minus_A"] for p in scored])
    frac_pos = float(np.mean(dCA > 0)); n_sig = int(sum(p["oof_significant"] for p in scored))
    wp = float(stats.wilcoxon(dCA, alternative="greater")[1]) if len(dCA) >= 6 and np.any(dCA != 0) else float("nan")
    rng = np.random.default_rng(42); boot = np.array([rng.choice(dCA, len(dCA), replace=True).mean() for _ in range(5000)])
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
    h1 = bool(dCA.mean() > 0 and np.isfinite(wp) and wp < 0.05 and frac_pos >= 2/3 and ci_lo > 0)
    meta = {"n_outcomes": len(scored), "mean_delta_C_minus_A": round(float(dCA.mean()), 4),
            "mean_delta_B_minus_A": round(float(dBA.mean()), 4), "fraction_outcomes_C_gt_A": round(frac_pos, 3),
            "n_outcomes_oof_significant": n_sig, "wilcoxon_p": round(wp, 5),
            "bootstrap_delta_CI95": [round(float(ci_lo), 4), round(float(ci_hi), 4)],
            "H1_deep_FM_beats_structure": h1,
            "verdict": (
                f"DEEP FM ADDS VALUE: ChemBERTa embeddings augment raw structure across held-out outcomes (mean "
                f"ΔAUROC(C−A) +{dCA.mean():.4f}, {frac_pos:.0%} positive, {n_sig}/{len(scored)} significant, Wilcoxon "
                f"p={wp:.4f}, CI [{ci_lo:.4f},{ci_hi:.4f}] excludes 0) — the first representation to beat raw structure; "
                f"the deep-FM integration path is real. Effect size honest; scale-up = FM fine-tuning."
            ) if h1 else (
                f"DEEP FM DOES NOT BEAT RAW STRUCTURE (decisive; closes the integration ladder B32→B38): ChemBERTa "
                f"(77M-molecule pretrained) embeddings do NOT robustly augment Morgan+physchem across {len(scored)} "
                f"held-out outcomes (mean ΔC−A {dCA.mean():+.4f}, FM-alone ΔB−A {dBA.mean():+.4f}, {frac_pos:.0%} "
                f"positive, {n_sig}/{len(scored)} significant, Wilcoxon p={wp:.4f}, CI [{ci_lo:.4f},{ci_hi:.4f}]). Even "
                f"a deep foundation model adds nothing general beyond classical fingerprints here — consistent with "
                f"the literature (ChemBERTa ≈/< fingerprints on ADMET/tox). The bottleneck is INFORMATION/DATA, not "
                f"representation. INTERCEPTA's value is its STANDALONE validated modules; integration is bounded at "
                f"every level tried. Honest boundary."
            )}
    print("\nVERDICT:", meta["verdict"])

    prov = {"experiment": "B38_deep_foundation_model", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "seeds": SEEDS, "foundation_model": FM_NAME,
            "embedding": "mean-pooled last_hidden_state (384-d), eval mode, rounded 5dp",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "meta_analysis": meta, "per_outcome": per}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B38_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"meta_analysis": meta, "per_outcome": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B38_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B38_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit, torch, transformers
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__, "torch": torch.__version__,
            "transformers": transformers.__version__}


if __name__ == "__main__":
    main()
