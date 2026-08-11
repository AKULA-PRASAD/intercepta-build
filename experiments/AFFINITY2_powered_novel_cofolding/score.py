#!/usr/bin/env python
"""AFFINITY2 step 3 — score the powered novel-chemotype benchmark + apply the pre-registered TWO-TIER gate.
Baselines (property RF, ligand QSAR RF) are computed locally (no GPU). Co-folding scores are read from the
Boltz outputs (benchmark/boltz_out/**/affinity_<cmpd_id>.json -> affinity_pred_value; score = -value, i.e.
lower predicted log-affinity = stronger binder). Deterministic (seed 42); reproduces byte-identical.
Implements PREREG.md incl. the 2026-08-11 hardening (paired-bootstrap TIER2 delta CI; fail-loud coverage;
gate on the identical co-folding-scored subset).
"""
import os, json, glob, hashlib, math
import numpy as np, pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem, DataStructs
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__)); BM = os.path.join(HERE, "benchmark")
R3 = os.path.join(HERE, "..", "R3_data_ingestion", "results")
RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
SEED, NBITS, RADIUS, ACT_CUT, B = 42, 2048, 2, 6.5, 2000
PANEL = ["ALDH1", "PKM2", "FEN1"]
DESC = [Descriptors.MolWt, Descriptors.MolLogP, Descriptors.NumHDonors, Descriptors.NumHAcceptors, Descriptors.TPSA,
        Descriptors.NumRotatableBonds, lambda m: m.GetNumHeavyAtoms(), Descriptors.RingCount, Descriptors.FractionCSP3,
        Descriptors.NumAromaticRings, Descriptors.NumAliphaticRings, Descriptors.NHOHCount, Descriptors.NOCount,
        Descriptors.qed, Descriptors.HeavyAtomMolWt]

def ecfp(s):
    m = Chem.MolFromSmiles(s); return None if m is None else AllChem.GetMorganFingerprintAsBitVect(m, RADIUS, nBits=NBITS)
def to_np(bvs):
    X = np.zeros((len(bvs), NBITS), np.int8)
    for i, b in enumerate(bvs): DataStructs.ConvertToNumpyArray(b, X[i])
    return X
def props(s):
    m = Chem.MolFromSmiles(s); return [f(m) for f in DESC] if m else None
def boot_ci(sc, y, seed=SEED):
    sc = np.asarray(sc, float); y = np.asarray(y, int); rng = np.random.default_rng(seed); o = []
    for _ in range(B):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2: continue
        o.append(roc_auc_score(y[idx], sc[idx]))
    return float(np.mean(o)), float(np.percentile(o, 2.5)), float(np.percentile(o, 97.5))

def paired_delta_ci(cofold, baseline, y, seed=SEED):
    """Paired bootstrap of (AUROC_cofold - AUROC_baseline) with SHARED resample indices."""
    cofold = np.asarray(cofold, float); baseline = np.asarray(baseline, float); y = np.asarray(y, int)
    rng = np.random.default_rng(seed); d = []
    for _ in range(B):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2: continue
        d.append(roc_auc_score(y[idx], cofold[idx]) - roc_auc_score(y[idx], baseline[idx]))
    return float(np.mean(d)), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))

def cofold_scores(ids):
    """Return (scores{cid:-affinity}, missing[list], invalid[list]) or None if no boltz_out at all.
    FAIL LOUD on schema mismatch (a present JSON lacking 'affinity_pred_value' => raise, not silent-drop)."""
    base = os.path.join(BM, "boltz_out")
    if not os.path.isdir(base):
        return None
    scores, missing, invalid = {}, [], []
    for cid in ids:
        hits = glob.glob(os.path.join(base, "**", f"affinity_{cid}.json"), recursive=True)
        if not hits:
            missing.append(cid); continue
        j = json.load(open(hits[0]))
        if "affinity_pred_value" not in j:
            raise KeyError(f"SCHEMA MISMATCH: {hits[0]} has no 'affinity_pred_value' (keys={list(j)[:8]})")
        try:
            v = float(j["affinity_pred_value"])
        except Exception:
            invalid.append(cid); continue
        if not math.isfinite(v):
            invalid.append(cid); continue
        scores[cid] = -v
    return scores, missing, invalid

def main():
    per_target, tier1_targets, tier2_targets = {}, 0, 0
    for tgt in PANEL:
        comp = pd.read_csv(os.path.join(BM, f"{tgt}_compounds.csv"))
        tr = pd.read_csv(os.path.join(R3, tgt, "r2input.csv"))
        tr["active"] = (tr["y [pEC50/pKi]"] >= ACT_CUT).astype(int); tr = tr[tr.split == "train"]
        tr_fp = [ecfp(s) for s in tr.smiles]; tr_ok = [i for i, f in enumerate(tr_fp) if f is not None]
        Xtr_e = to_np([tr_fp[i] for i in tr_ok]); ytr = tr.active.values[tr_ok]
        Xtr_p = np.array([props(s) for s in tr.smiles.values[tr_ok]], float)
        y = comp.active.values
        te_fp = [ecfp(s) for s in comp.smiles]; te_p = np.array([props(s) for s in comp.smiles], float)
        qsar = RandomForestClassifier(300, random_state=SEED, n_jobs=1).fit(Xtr_e, ytr).predict_proba(to_np(te_fp))[:, 1]
        prop = RandomForestClassifier(300, random_state=SEED, n_jobs=1).fit(Xtr_p, ytr).predict_proba(te_p)[:, 1]
        qa_full = boot_ci(qsar, y); pa_full = boot_ci(prop, y)
        rec = {"n_expected": int(len(y)), "n_active_expected": int(y.sum()),
               "QSAR_AUROC_full": round(qa_full[0], 4), "property_AUROC_full": round(pa_full[0], 4)}

        cfres = cofold_scores(list(comp.cmpd_id))
        if cfres is not None:
            cf, missing, invalid = cfres
            mask = comp.cmpd_id.isin(cf).values
            cfs = np.array([cf[c] for c in comp.cmpd_id[mask]]); yc = y[mask]
            qs = qsar[mask]; ps = prop[mask]        # SAME subset for a fair paired comparison
            cov = {"scored": int(mask.sum()), "expected": int(len(y)),
                   "scored_active": int(yc.sum()), "scored_inactive": int((yc == 0).sum()),
                   "missing_ids": missing, "invalid_ids": invalid,
                   "coverage_frac": round(mask.sum() / len(y), 4)}
            rec["coverage"] = cov
            rec["cofold_raw_affinity_pred_value"] = {  # sign/sanity diagnostic (NOT used for gating)
                "active_mean": round(float(np.mean(-cfs[yc == 1])), 4),
                "inactive_mean": round(float(np.mean(-cfs[yc == 0])), 4),
                "note": "score=-affinity_pred_value; if actives truly bind stronger, active_mean should be LOWER"}
            ca = boot_ci(cfs, yc)
            qa = boot_ci(qs, yc); pa = boot_ci(ps, yc)
            base_name = "QSAR" if qa[0] >= pa[0] else "property"; base_arr = qs if qa[0] >= pa[0] else ps
            best_base = max(qa[0], pa[0])
            dmean, dlo, dhi = paired_delta_ci(cfs, base_arr, yc)
            tier1 = bool(ca[1] > 0.60)
            tier2 = bool(tier1 and (ca[0] - best_base) > 0.10 and dlo > 0.0)
            rec.update({"cofold_AUROC": round(ca[0], 4), "cofold_CI": [round(ca[1], 4), round(ca[2], 4)],
                        "QSAR_AUROC_subset": round(qa[0], 4), "property_AUROC_subset": round(pa[0], 4),
                        "best_baseline": base_name, "cofold_minus_best": round(ca[0] - best_base, 4),
                        "paired_delta_mean": round(dmean, 4), "paired_delta_95CI": [round(dlo, 4), round(dhi, 4)],
                        "TIER1_zero_data_signal": tier1, "TIER2_beats_ligand_ml": tier2})
            tier1_targets += int(tier1); tier2_targets += int(tier2)
            print(f"{tgt}: cofold {ca[0]:.3f} CI[{ca[1]:.3f},{ca[2]:.3f}] | best {base_name} {best_base:.3f} | "
                  f"delta {dmean:+.3f} CI[{dlo:+.3f},{dhi:+.3f}] | cov {cov['scored']}/{cov['expected']} | "
                  f"T1 {tier1} T2 {tier2}")
        else:
            rec.update({"cofold_AUROC": None, "TIER1_zero_data_signal": None,
                        "TIER2_beats_ligand_ml": None, "status": "PENDING_GPU_RUN"})
            print(f"{tgt}: QSAR {qa_full[0]:.3f} | property {pa_full[0]:.3f} | cofold PENDING")
        per_target[tgt] = rec

    if any(v.get("cofold_AUROC") is None for v in per_target.values()):
        verdict = "PENDING_GPU_RUN"
    else:
        # integrity gate: any target with <100% coverage is flagged (MAR -> still scored on the subset)
        incomplete = [t for t, v in per_target.items() if v["coverage"]["coverage_frac"] < 1.0]
        base = ("TIER1+TIER2: co-folding breaks the wall AND beats ligand-ML (R5 OPENS, strong)"
                if tier1_targets >= 2 and tier2_targets >= 2 else
                "TIER1: zero-data co-folding signal (R5 OPENS)" if tier1_targets >= 2 else
                "WALL HOLDS -> D2 CLOSED DEFINITIVELY AT POWER (co-folding fails zero-data novel-chemotype)")
        verdict = base + (f" [COVERAGE<100% on {incomplete}: subset-scored, MAR]" if incomplete else "")
    out = {"panel": PANEL,
           "gate": "TIER1: cofold subset AUROC CI-lo>0.60 on >=2 targets; TIER2: also cofold-best_baseline>0.10 "
                   "AND paired-delta CI-lo>0 on >=2 targets",
           "per_target": per_target, "n_targets_tier1": tier1_targets, "n_targets_tier2": tier2_targets,
           "VERDICT": verdict, "seed": SEED,
           "caveats": "target-side leakage (LIT-PCBA receptors predate Boltz cutoff) -> TIER1 optimistic; "
                      "compound leakage vs Boltz ChEMBL/BindingDB training NOT excluded; per-compound server MSAs; "
                      "single diffusion sample. Internal go/no-go signal, NOT a publication claim (see REVIEW/SUMMARY)."}
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "AFFINITY2_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print("\nVERDICT:", verdict); print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
