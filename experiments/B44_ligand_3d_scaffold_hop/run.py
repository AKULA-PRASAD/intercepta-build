"""B44 — ligand-based 3D shape/pharmacophore (rdkit O3A) for scaffold hopping. Tests whether 3D O3A similarity to
known active templates retrieves NOVEL-SCAFFOLD actives (2D-dissimilar to the references) better than 2D Morgan
Tanimoto — the one retrieval task where 3D can beat 2D in principle. Implements prereg/B44_ligand_3d_scaffold_hop.md.
Deterministic (fixed embedding seed) -> reproduce x2. NO receptor docking (none installed); ligand-based 3D only.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
try:
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
except Exception:
    pass
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, rdMolAlign
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Scoring.Scoring import CalcAUC, CalcBEDROC, CalcEnrichment

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/kaalcura/data")
TARGET, K_REF, N_DECOY, EMBED_SEED = "hiv", 8, 2500, 0xB44


def largest_fragment(smi):
    m = Chem.MolFromSmiles(str(smi))
    if m is None:
        return None
    frags = Chem.GetMolFrags(m, asMols=True, sanitizeFrags=True)
    return max(frags, default=None, key=lambda f: f.GetNumHeavyAtoms()) if frags else m


def murcko(m):
    try:
        return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception:
        return ""


def morgan(m):
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)


def embed3d(m):
    """One ETKDGv3 conformer (fixed seed) + MMFF94 optimize; return (mol_with_H, MMFFProps) or None."""
    try:
        mh = Chem.AddHs(m)
        p = AllChem.ETKDGv3(); p.randomSeed = EMBED_SEED
        if AllChem.EmbedMolecule(mh, p) != 0:
            p.useRandomCoords = True
            if AllChem.EmbedMolecule(mh, p) != 0:
                return None
        AllChem.MMFFOptimizeMolecule(mh)
        props = AllChem.MMFFGetMoleculeProperties(mh)
        if props is None:
            return None
        return mh, props
    except Exception:
        return None


def score_set(labels, scores):
    order = np.argsort(-np.asarray(scores))
    ranked = [[int(labels[i])] for i in order]
    ef = CalcEnrichment(ranked, 0, [0.01, 0.05])
    return {"auroc": round(float(CalcAUC(ranked, 0)), 4), "bedroc_a80.5": round(float(CalcBEDROC(ranked, 0, 80.5)), 4),
            "ef_1pct": round(float(ef[0]), 3), "ef_5pct": round(float(ef[1]), 3), "n": int(len(labels)),
            "n_active": int(np.sum(labels))}


def main():
    from tdc.single_pred import HTS
    d = HTS(name=TARGET, path=os.path.join(DATA, "tdc_bio")).get_data().dropna(subset=["Y", "Drug"])
    act = d[d["Y"] == 1]
    inact = d[d["Y"] == 0].sample(n=min(N_DECOY, int((d["Y"] == 0).sum())), random_state=42)

    # parse + scaffold, largest fragment
    def prep(df):
        out = []
        for s in df["Drug"].tolist():
            m = largest_fragment(s)
            if m is not None:
                out.append((Chem.MolToSmiles(m), m, murcko(m)))
        return out
    A = prep(act); D = prep(inact)

    # references = 1 rep (first by canonical smiles) from each of the K_REF largest scaffold clusters
    from collections import defaultdict
    clusters = defaultdict(list)
    for smi, m, sc in A:
        if sc:
            clusters[sc].append((smi, m))
    big = sorted(clusters.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:K_REF]
    refs = []  # (smi, mol3d, props, morganfp, scaffold)
    ref_scaffolds = set()
    for sc, members in big:
        smi, m = sorted(members, key=lambda x: x[0])[0]
        e = embed3d(m)
        if e is None:
            continue
        refs.append((smi, e[0], e[1], morgan(m), sc)); ref_scaffolds.add(sc)
    print(f"references embedded: {len(refs)}/{K_REF} (scaffold clusters sizes: {[len(m) for _,m in big]})")

    ref_smis = {r[0] for r in refs}
    # query actives = non-reference actives; decoys = inactives
    queries = [(smi, m, sc, 1) for smi, m, sc in A if smi not in ref_smis] + [(smi, m, sc, 0) for smi, m, sc in D]

    rows = []  # (label, novel_scaffold, s2d, s3d, embedded)
    n_embed_fail = 0
    for i, (smi, m, sc, lab) in enumerate(queries):
        fp = morgan(m)
        s2d = max((DataStructs.TanimotoSimilarity(fp, r[3]) for r in refs), default=0.0)
        novel = int(bool(sc) and sc not in ref_scaffolds)
        e = embed3d(m)
        if e is None:
            n_embed_fail += 1
            rows.append((lab, novel, s2d, None)); continue
        qmol, qprops = e
        best = 0.0
        for _, rmol, rprops, _, _ in refs:
            try:
                o3a = rdMolAlign.GetO3A(qmol, rmol, qprops, rprops)
                best = max(best, float(o3a.Score()))
            except Exception:
                pass
        rows.append((lab, novel, s2d, best))
        if (i + 1) % 500 == 0:
            print(f"  scored {i+1}/{len(queries)} (embed_fail={n_embed_fail})")

    emb = [r for r in rows if r[3] is not None]  # only molecules with a 3D conformer (fair 2D-vs-3D comparison)
    lab = np.array([r[0] for r in emb]); nov = np.array([r[1] for r in emb])
    s2d = np.array([r[2] for r in emb]); s3d = np.array([r[3] for r in emb])

    def subset(mask):
        return score_set(lab[mask], s2d[mask]), score_set(lab[mask], s3d[mask])

    novel_mask = (lab == 0) | ((lab == 1) & (nov == 1))   # novel-scaffold actives vs all decoys
    full_mask = np.ones(len(lab), dtype=bool)              # all actives vs decoys (context; 2D expected to win)
    n2d, n3d = subset(novel_mask)
    f2d, f3d = subset(full_mask)

    d_auroc = round(n3d["auroc"] - n2d["auroc"], 4)
    h1 = bool(d_auroc > 0.03 and n3d["ef_1pct"] > n2d["ef_1pct"])
    h2 = bool(n3d["auroc"] > 0.60 and n3d["ef_1pct"] > 2)
    n_novel_act = int(((lab == 1) & (nov == 1)).sum())

    summary = {"target": TARGET, "n_refs": len(refs), "n_embedded": len(emb), "n_embed_fail": n_embed_fail,
               "n_novel_scaffold_actives": n_novel_act,
               "novel_scaffold_actives_vs_decoys": {"metric_2D_morgan": n2d, "metric_3D_o3a": n3d,
                                                     "delta_auroc_3D_minus_2D": d_auroc},
               "all_actives_vs_decoys_context": {"metric_2D_morgan": f2d, "metric_3D_o3a": f3d},
               "H1_3D_beats_2D_on_scaffold_hops": h1, "H2_3D_meaningful": h2,
               "verdict": (
                   f"POSITIVE — LIGAND-BASED 3D ADDS SCAFFOLD-HOPPING: on novel-scaffold actives vs decoys, 3D O3A "
                   f"AUROC {n3d['auroc']} vs 2D {n2d['auroc']} (delta {d_auroc:+}), EF@1% 3D {n3d['ef_1pct']}x vs 2D "
                   f"{n2d['ef_1pct']}x. 3D retrieves chemotype-hopped actives 2D misses. Retrospective, single "
                   f"conformer, 1 target, real-actives-vs-decoys — NOT wet-lab; heuristic overlay, not binding energy."
                   if h1 else
                   f"NEGATIVE (honest, first-class) — ligand-based 3D does NOT beat the 2D spine even on scaffold hops: "
                   f"novel-scaffold 3D AUROC {n3d['auroc']} vs 2D {n2d['auroc']} (delta {d_auroc:+}), EF@1% 3D "
                   f"{n3d['ef_1pct']}x vs 2D {n2d['ef_1pct']}x. Single-conformer O3A adds no retrieval capability over "
                   f"Morgan on {TARGET}; the 2D fingerprint spine is the operative retrieval tool. Bounds the rung."),
               }
    print("\nVERDICT:", summary["verdict"])

    prov = {"experiment": "B44_ligand_3d_scaffold_hop", "git_sha": os.popen("git rev-parse HEAD").read().strip(),
            "python": sys.version.split()[0], "libs": _libvers(), "target": TARGET, "k_ref": K_REF,
            "n_decoy_cap": N_DECOY, "embed_seed": EMBED_SEED,
            "protocol": "ETKDGv3(1 conf, fixed seed)+MMFF94; O3A max-over-refs vs Morgan-Tanimoto max-over-refs; "
                        "novel-Murcko-scaffold actives vs decoys; rdkit.ML.Scoring AUROC/BEDROC80.5/EF",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    full = {"provenance": prov, "summary": summary}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(full, open(os.path.join(HERE, "results", "B44_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": summary}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "B44_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/B44_metrics.json")


def _libvers():
    import sklearn, scipy, numpy, rdkit
    return {"numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__, "rdkit": rdkit.__version__}


if __name__ == "__main__":
    main()
