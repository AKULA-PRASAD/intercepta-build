"""B49 — proteochemometric pan-target model: can we rank actives for UNSEEN proteins? ESM-2 protein embeddings +
Morgan ligand features, leave-PROTEIN-out CV on 15 LIT-PCBA target-sets (14 UniProt proteins), vs a ligand-only
baseline. Implements prereg/B49_proteochemometric_pantarget.md. Deterministic (ESM CPU inference, HGB seed=42) ->
reproduce x2.
"""
import os, sys, json, time, hashlib, urllib.request
import numpy as np
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.ML.Scoring.Scoring import CalcAUC
from sklearn.ensemble import HistGradientBoostingClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
LIT = os.path.join(DATA, "lit_pcba")
CACHE = os.path.join(DATA, "esm_cache"); os.makedirs(CACHE, exist_ok=True)
ESM_MODEL = "facebook/esm2_t30_150M_UR50D"
UNIPROT = {"ADRB2": "P07550", "ALDH1": "P00352", "ESR1_ago": "P03372", "ESR1_ant": "P03372", "FEN1": "P39748",
           "GBA": "P04062", "IDH1": "O75874", "KAT2A": "Q92830", "MAPK1": "P28482", "MTORC1": "P42345",
           "OPRK1": "P41145", "PKM2": "P14618", "PPARG": "P37231", "TP53": "P04637", "VDR": "P11473"}
MAX_ACT, MAX_DEC, SEED = 300, 600, 42


def fetch_seq(acc):
    fp = os.path.join(CACHE, f"{acc}.fasta")
    if not os.path.exists(fp):
        urllib.request.urlretrieve(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", fp)
    lines = open(fp).read().splitlines()
    return "".join(l for l in lines if not l.startswith(">"))


def esm_embed(seqs):
    """Deterministic CPU mean-pooled ESM-2 embedding per unique sequence (cached by acc)."""
    import torch
    from transformers import AutoTokenizer, AutoModel
    torch.manual_seed(0)
    tok = AutoTokenizer.from_pretrained(ESM_MODEL, cache_dir=os.path.join(DATA, "hf_cache"))
    model = AutoModel.from_pretrained(ESM_MODEL, cache_dir=os.path.join(DATA, "hf_cache")).eval()
    out = {}
    with torch.no_grad():
        for acc, seq in seqs.items():
            cf = os.path.join(CACHE, f"emb_{acc}.npy")
            if os.path.exists(cf):
                out[acc] = np.load(cf); continue
            enc = tok(seq[:1022], return_tensors="pt", truncation=True, max_length=1024)
            h = model(**enc).last_hidden_state[0]           # (L, 640)
            mask = enc["attention_mask"][0].bool()
            v = h[mask].mean(0).cpu().numpy().astype(np.float32)
            np.save(cf, v); out[acc] = v
    return out


def morgan(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None:
        return None
    fr = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    big = max(fr, key=lambda f: f.GetNumHeavyAtoms()) if fr else m
    a = np.zeros(1024, dtype=np.float32)
    from rdkit import DataStructs
    DataStructs.ConvertToNumpyArray(AllChem.GetMorganFingerprintAsBitVect(big, 2, nBits=1024), a)
    return a


def read_smi(p):
    return [l.split()[0] for l in open(p) if l.split()]


def build():
    seqs = {acc: fetch_seq(acc) for acc in set(UNIPROT.values())}
    emb = esm_embed(seqs)
    rows = []  # (target, protein_acc, ligand_vec, protein_vec, label)
    rng = np.random.default_rng(SEED)
    for tgt, acc in UNIPROT.items():
        td = os.path.join(LIT, tgt)
        if not os.path.isdir(td):
            continue
        acts = [morgan(s) for s in read_smi(os.path.join(td, "actives.smi"))]
        acts = [a for a in acts if a is not None]
        decs = [morgan(s) for s in read_smi(os.path.join(td, "inactives.smi"))]
        decs = [d for d in decs if d is not None]
        if len(acts) > MAX_ACT:
            acts = [acts[i] for i in sorted(rng.permutation(len(acts))[:MAX_ACT])]
        if len(decs) > MAX_DEC:
            decs = [decs[i] for i in sorted(rng.permutation(len(decs))[:MAX_DEC])]
        pv = emb[acc]
        for a in acts:
            rows.append((tgt, acc, a, pv, 1))
        for d in decs:
            rows.append((tgt, acc, d, pv, 0))
    return rows, emb


def auroc(labels, scores):
    ranked = [[int(labels[i])] for i in np.argsort(-np.asarray(scores))]
    return round(float(CalcAUC(ranked, 0)), 4)


def main():
    rows, emb = build()
    tgts = np.array([r[0] for r in rows]); accs = np.array([r[1] for r in rows])
    Xlig = np.vstack([r[2] for r in rows]); Xprot = np.vstack([r[3] for r in rows])
    y = np.array([r[4] for r in rows], dtype=int)
    Xpcm = np.hstack([Xlig, Xprot])
    print(f"rows={len(y)} actives={int(y.sum())} proteins={len(set(accs))} targets={len(set(tgts))}")

    def loo(X):
        res = {}
        for acc in sorted(set(accs)):
            te = accs == acc; tr = ~te
            if len(np.unique(y[tr])) < 2:
                continue
            m = HistGradientBoostingClassifier(random_state=42, max_iter=200, learning_rate=0.06,
                                               max_depth=6).fit(X[tr], y[tr])
            p = m.predict_proba(X[te])[:, 1]
            for tgt in sorted(set(tgts[te])):
                sub = tgts[te] == tgt
                yt = y[te][sub]
                if len(np.unique(yt)) == 2 and yt.sum() >= 3:
                    res[tgt] = auroc(yt, p[sub])
        return res

    pcm = loo(Xpcm); lig = loo(Xlig)
    common = sorted(set(pcm) & set(lig))
    print("\n  target        PCM    ligand-only   d")
    for t in common:
        print(f"  {t:12s} {pcm[t]:.4f}   {lig[t]:.4f}    {pcm[t]-lig[t]:+.4f}")

    pcm_m = round(float(np.mean([pcm[t] for t in common])), 4)
    lig_m = round(float(np.mean([lig[t] for t in common])), 4)
    delta = round(pcm_m - lig_m, 4)
    n_gt60 = int(sum(1 for t in common if pcm[t] > 0.60))
    h1 = bool(pcm_m > 0.55)
    h2 = bool(delta >= 0.02)

    summary = {"n_targets_evaluated": len(common), "n_proteins": len(set(accs)), "n_rows": int(len(y)),
               "pcm_mean_auroc": pcm_m, "ligand_only_mean_auroc": lig_m, "delta_pcm_minus_ligand": delta,
               "n_targets_pcm_gt0.60": n_gt60, "per_target": {t: {"pcm": pcm[t], "ligand_only": lig[t]} for t in common},
               "H1_pcm_generalizes_unseen_targets": h1, "H2_protein_features_add_value": h2,
               "verdict": (
                   f"PCM GENERALIZES TO UNSEEN TARGETS{' + PROTEIN FEATURES HELP' if h2 else ' BUT PROTEIN FEATURES ADD LITTLE'}: "
                   f"leave-protein-out mean PCM AUROC {pcm_m} ({n_gt60}/{len(common)} unseen targets >0.60), vs "
                   f"ligand-only {lig_m} (delta {delta:+}). "
                   + ("The ESM-2 protein embedding adds genuine target-specificity for unseen targets." if h2 else
                      "Protein embeddings add ~no usable target-specific signal over pooled ligand structure "
                      "(literature-consistent) — cross-target generalization here is carried by ligand structure, not "
                      "the protein representation. Honest first-class result.")
                   + " Retrospective, in-silico, 14 proteins, seq truncated to 1022; enrichment != proven activity; not wet-lab."
                   if h1 else
                   f"NO CROSS-TARGET GENERALIZATION (honest negative): leave-protein-out mean PCM AUROC {pcm_m} (<=0.55), "
                   f"ligand-only {lig_m} (delta {delta:+}). Predicting activity for proteins whose ligands were never "
                   f"seen does NOT work above chance with this PCM setup — the 'any target' axis is not yet reachable "
                   f"this way. First-class negative; 14 proteins, seq truncated; not wet-lab."),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B49_proteochemometric_pantarget", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "esm_model": ESM_MODEL, "max_act": MAX_ACT,
            "max_dec": MAX_DEC, "seed": SEED, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = {"provenance": prov, "summary": summary}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "B49_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B49_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B49_metrics.json")


def _libvers():
    import rdkit, numpy, sklearn, torch, transformers
    return {"rdkit": rdkit.__version__, "numpy": numpy.__version__, "scikit-learn": sklearn.__version__,
            "torch": torch.__version__, "transformers": transformers.__version__}


if __name__ == "__main__":
    main()
