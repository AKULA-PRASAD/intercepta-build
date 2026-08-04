"""HIT1 — the novel-chemotype ceiling of zero/low-data ligand-based hit-finding (molecule half, opening chapter).
Per MoleculeACE target: SEED = train actives (known binders), LIBRARY = test compounds. Two rankers — similarity-transfer
(max Tanimoto to seeds) and learned QSAR (RandomForest on ECFP4). Measure enrichment OVERALL and for NOVEL-chemotype actives
(scaffold-disjoint from seeds). The decisive, non-tautological test: does LEARNED QSAR recover novel chemotypes that raw
similarity cannot, or do both hit the ceiling? Deterministic. Env: intercepta-build (rdkit/sklearn).
"""
import os, csv, json, time, glob, hashlib, random
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.ML.Scoring import Scoring
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "hit1", "moleculeace")
ACT_CUT = 6.5          # pActivity >= 6.5 (~<=316 nM) = potent "hit"
NOVEL_TAN = 0.4        # nearest-seed-active Tanimoto < 0.4 => novel chemotype
MIN_CLASS = 20         # require >=20 test actives and >=20 test inactives
SEED = 42


def fp(mol):
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)


def to_np(bv):
    a = np.zeros((2048,), dtype=np.uint8); DataStructs.ConvertToNumpyArray(bv, a); return a


def load_target(path):
    rows = list(csv.DictReader(open(path)))
    out = []
    for r in rows:
        m = Chem.MolFromSmiles(r["smiles"])
        if m is None: continue
        try: pa = float(r["y [pEC50/pKi]"])
        except Exception: continue
        out.append({"fp": fp(m), "pa": pa, "active": int(pa >= ACT_CUT),
                    "cliff": int(r.get("cliff_mol", "0") or 0), "split": r["split"]})
    return out


def bedroc(y, score):
    order = np.argsort(-np.asarray(score), kind="stable")
    lab = [[int(y[i])] for i in order]
    return float(Scoring.CalcBEDROC(lab, 0, 20.0))


def ef(y, score, fracs=(0.01, 0.05)):
    order = np.argsort(-np.asarray(score), kind="stable")
    lab = [[int(y[i])] for i in order]
    e = Scoring.CalcEnrichment(lab, 0, list(fracs))
    return [float(x) for x in e]


def auroc(y, score):
    y = np.asarray(y)
    return float(roc_auc_score(y, score)) if 0 < y.sum() < len(y) else float("nan")


def sub_auroc(mask_pos, mask_neg, score):
    """AUROC separating a chosen positive subset (mask_pos) from negatives (mask_neg)."""
    idx = np.where(mask_pos | mask_neg)[0]
    if mask_pos.sum() < 5 or mask_neg.sum() < 5: return float("nan")
    return auroc(mask_pos[idx].astype(int), np.asarray(score)[idx])


def main():
    t0 = time.time(); random.seed(SEED); np.random.seed(SEED)
    print("=== HIT1: novel-chemotype ceiling of ligand-based hit-finding (MoleculeACE) ===")
    per = {}
    for path in sorted(glob.glob(os.path.join(DATA, "*.csv"))):
        tgt = os.path.basename(path).replace(".csv", "")
        compounds = load_target(path)
        train = [c for c in compounds if c["split"] == "train"]
        test = [c for c in compounds if c["split"] == "test"]
        seed_act = [c for c in train if c["active"]]
        y_test = np.array([c["active"] for c in test])
        if len(seed_act) < 5 or y_test.sum() < MIN_CLASS or (len(y_test) - y_test.sum()) < MIN_CLASS:
            continue
        seed_fps = [c["fp"] for c in seed_act]
        # ranker 1: similarity-transfer (max Tanimoto to seed actives)
        sim = np.array([max(DataStructs.BulkTanimotoSimilarity(c["fp"], seed_fps)) for c in test])
        # ranker 2: learned QSAR (RF on ECFP4 over all train compounds)
        Xtr = np.vstack([to_np(c["fp"]) for c in train]); ytr = np.array([c["active"] for c in train])
        rf = RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=4).fit(Xtr, ytr)
        qsar = rf.predict_proba(np.vstack([to_np(c["fp"]) for c in test]))[:, 1]
        # novelty split of TEST compounds by nearest-seed-active Tanimoto
        novelty = sim.copy()  # sim IS the nearest-seed-active Tanimoto
        is_act = y_test == 1; is_inact = y_test == 0
        novel_act = is_act & (novelty < NOVEL_TAN)
        analog_act = is_act & (novelty >= NOVEL_TAN)
        # NULL: label-shuffled similarity ranking
        yperm = y_test.copy(); rng = np.random.RandomState(SEED); rng.shuffle(yperm)
        e_sim = ef(y_test, sim); e_qsar = ef(y_test, qsar)
        per[tgt] = {
            "n_seed_act": len(seed_act), "n_test": len(test), "n_test_act": int(y_test.sum()),
            "n_novel_act": int(novel_act.sum()), "n_analog_act": int(analog_act.sum()),
            "frac_test_act_novel": round(float(novel_act.sum() / max(is_act.sum(), 1)), 3),
            "overall": {"sim_BEDROC": round(bedroc(y_test, sim), 4), "qsar_BEDROC": round(bedroc(y_test, qsar), 4),
                        "sim_AUROC": round(auroc(y_test, sim), 4), "qsar_AUROC": round(auroc(y_test, qsar), 4),
                        "sim_EF1": round(e_sim[0], 3), "qsar_EF1": round(e_qsar[0], 3),
                        "null_BEDROC": round(bedroc(yperm, sim), 4)},
            "analog_vs_inactive_AUROC": {"sim": round(sub_auroc(analog_act, is_inact, sim), 4),
                                         "qsar": round(sub_auroc(analog_act, is_inact, qsar), 4)},
            "novel_vs_inactive_AUROC": {"sim": round(sub_auroc(novel_act, is_inact, sim), 4),
                                        "qsar": round(sub_auroc(novel_act, is_inact, qsar), 4)},
        }
        print(f"  {tgt:16s} act {int(y_test.sum()):3d} (novel {int(novel_act.sum()):3d}) | overall AUROC sim "
              f"{per[tgt]['overall']['sim_AUROC']:.2f} qsar {per[tgt]['overall']['qsar_AUROC']:.2f} | "
              f"NOVEL-vs-inact AUROC sim {per[tgt]['novel_vs_inactive_AUROC']['sim']} qsar "
              f"{per[tgt]['novel_vs_inactive_AUROC']['qsar']} [{time.time()-t0:.0f}s]")

    def med(vals):
        v = [x for x in vals if x == x]; return round(float(np.median(v)), 4) if v else float("nan")
    T = list(per)
    ov_sim = med([per[t]["overall"]["sim_AUROC"] for t in T]); ov_qsar = med([per[t]["overall"]["qsar_AUROC"] for t in T])
    an_sim = med([per[t]["analog_vs_inactive_AUROC"]["sim"] for t in T])
    an_qsar = med([per[t]["analog_vs_inactive_AUROC"]["qsar"] for t in T])
    # NOVEL axis: only targets where it is COMPUTABLE (>=5 novel actives). Judge QSAR vs RANDOM (0.5), NOT vs the
    # tautologically-handicapped similarity baseline (novel := low sim => sim ranks novel low by construction).
    comp = [t for t in T if per[t]["novel_vs_inactive_AUROC"]["qsar"] == per[t]["novel_vs_inactive_AUROC"]["qsar"]]
    nv_sim = med([per[t]["novel_vs_inactive_AUROC"]["sim"] for t in comp])
    nv_qsar = med([per[t]["novel_vs_inactive_AUROC"]["qsar"] for t in comp])
    frac_qsar_novel_above = round(float(np.mean([per[t]["novel_vs_inactive_AUROC"]["qsar"] > 0.55 for t in comp])), 3) if comp else float("nan")
    degradation = round(ov_qsar - nv_qsar, 4)          # overall -> novel (QSAR); the honest ceiling magnitude
    med_novel_act = int(np.median([per[t]["n_novel_act"] for t in T]))
    med_null = med([per[t]["overall"]["null_BEDROC"] for t in T])

    H1_aggregate = ov_sim > 0.7 and ov_qsar > 0.7      # aggregate potency-ranking works (AUROC; prevalence-independent)
    # partial residual novel signal iff QSAR novel recovery is meaningfully above random in the majority of testable targets
    partial_novel = bool(nv_qsar >= 0.60 and frac_qsar_novel_above >= 0.6)
    hard_ceiling = bool(nv_qsar < 0.55)
    summary = {"n_targets": len(T), "n_targets_novel_testable": len(comp), "median_novel_actives_per_target": med_novel_act,
               "median_overall_AUROC_sim": ov_sim, "median_overall_AUROC_qsar": ov_qsar,
               "median_analog_vs_inactive_AUROC_sim": an_sim, "median_analog_vs_inactive_AUROC_qsar": an_qsar,
               "median_novel_vs_inactive_AUROC_qsar": nv_qsar, "frac_targets_qsar_novel_above_0.55": frac_qsar_novel_above,
               "overall_to_novel_degradation_qsar": degradation,
               "median_novel_vs_inactive_AUROC_sim_TAUTOLOGICAL": nv_sim,
               "H1_aggregate_potency_ranking_works": H1_aggregate,
               "novel_chemotype_partial_residual_signal": partial_novel,
               "novel_chemotype_hard_ceiling": hard_ceiling}
    caveat = (f"CAVEATS: (i) actives = a LARGE fraction (potency-ranking, not needle-in-haystack VS) so AUROC — not BEDROC/EF "
              f"(null BEDROC {med_null}) — is the valid metric; (ii) NOVEL actives are RARE (median {med_novel_act}/target; "
              f"only {len(comp)}/{len(T)} targets testable) => novel estimates are LOW-POWERED; (iii) the similarity baseline's "
              f"novel AUROC ({nv_sim}) is TAUTOLOGICALLY < 0.5 (novel := low sim) and does NOT anchor the comparison; "
              f"(iv) novelty is defined vs SEED actives only, so 'novel' test actives may still resemble other train "
              f"compounds — a permissive novelty bar. Ligand-only; MoleculeACE potency data; not wet-lab.")
    if partial_novel:
        summary["verdict"] = (f"SOFT CEILING with RESIDUAL novel signal (honest, non-over-read): aggregate ligand-based "
                              f"potency-ranking works (median overall AUROC sim {ov_sim} / qsar {ov_qsar}) and is ANALOG-DRIVEN "
                              f"(analog-vs-inactive AUROC sim {an_sim}). On SCAFFOLD-NOVEL chemotypes, a learned QSAR degrades "
                              f"SUBSTANTIALLY — from {ov_qsar} (overall) to {nv_qsar} (novel), −{degradation} — but retains "
                              f"MODEST ABOVE-RANDOM recovery (>0.55 in {frac_qsar_novel_above} of the {len(comp)} testable "
                              f"targets). So ligand-based hit-finding rides mostly on chemical ANALOGY, yet — UNLIKE the "
                              f"target-ID conservation ceiling (where nothing beat conservation for novel targets) — a learned "
                              f"ligand model keeps a partial, noisy signal for novel chemotypes. NOT a hard ceiling, NOT a clean "
                              f"'learning solves novel'. The tautological sim-vs-qsar 'gain' is REJECTED as the basis. " + caveat)
    else:
        summary["verdict"] = (f"{'NOVEL-CHEMOTYPE CEILING' if hard_ceiling else 'MIXED'}: aggregate potency-ranking works "
                              f"(overall AUROC sim {ov_sim}/qsar {ov_qsar}, analog-driven, analog AUROC {an_sim}) but novel-"
                              f"chemotype recovery for a learned QSAR is {'~random ('+str(nv_qsar)+')' if hard_ceiling else 'weak/inconsistent ('+str(nv_qsar)+')'} "
                              f"— the molecule-half information ceiling for novel chemistry. " + caveat)
    print("\nPANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "act_cut": ACT_CUT, "novel_tan": NOVEL_TAN}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_target": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "HIT1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_target": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "HIT1_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/HIT1_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
