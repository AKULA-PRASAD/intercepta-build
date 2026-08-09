#!/usr/bin/env python
"""AFFINITY_IPTM1 scoring: structure-only co-folding interface confidence (ipTM,
complex pLDDT) as a zero-data binder proxy vs docking (0.4285) and random (0.5).

Reads cached boltz structure-only confidence JSONs. NO fabrication: if a JSON is
missing, that compound is dropped and the run is marked INFEASIBLE/partial.
Deterministic: pure rank statistics, floats rounded -> byte-identical SHA-256.
"""
import json, hashlib, os, glob, sys

DATA = "/Users/kalki/intercepta_data/affinity_iptm1"
PRED = os.path.join(DATA, "out_iptm", "boltz_results_yamls_structonly", "predictions")
OUT = "/Users/kalki/INTERCEPTA_BUILD/experiments/AFFINITY_IPTM1_structure_confidence/results"
DOCK_AUROC = 0.4285   # HIT2 thrombin docking baseline
RAND_AUROC = 0.5

# Pre-registered set: idx -> (pact/pKi, active)
SET = {
    21:  (8.7447, 1), 67:  (4.4318, 0), 167: (5.1701, 0), 217: (6.5229, 1),
    340: (8.4559, 1), 384: (6.2218, 0), 529: (6.7212, 1), 535: (4.0851, 0),
}

def find_conf(idx):
    tag = f"cmpd_{idx:04d}"
    cands = glob.glob(os.path.join(PRED, tag, f"confidence_{tag}_model_0.json"))
    cands += glob.glob(os.path.join(PRED, tag, f"confidence_{tag}*.json"))
    for c in sorted(cands):
        if os.path.exists(c):
            return c
    return None

def auroc(scores, labels):
    """Mann-Whitney AUROC with tie handling (rank-based). scores higher = predicted positive."""
    pairs = sorted(zip(scores, range(len(scores))))
    ranks = [0.0]*len(scores)
    i = 0
    while i < len(pairs):
        j = i
        while j+1 < len(pairs) and pairs[j+1][0] == pairs[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # 1-based average rank
        for k in range(i, j+1):
            ranks[pairs[k][1]] = avg
        i = j+1
    pos = [ranks[i] for i in range(len(labels)) if labels[i] == 1]
    n1 = len(pos); n2 = len(labels) - n1
    if n1 == 0 or n2 == 0:
        return None
    U = sum(pos) - n1*(n1+1)/2.0
    return U/(n1*n2)

def spearman(x, y):
    def rank(v):
        pairs = sorted(zip(v, range(len(v))))
        r = [0.0]*len(v); i = 0
        while i < len(pairs):
            j = i
            while j+1 < len(pairs) and pairs[j+1][0] == pairs[i][0]:
                j += 1
            avg = (i+j)/2.0 + 1.0
            for k in range(i, j+1):
                r[pairs[k][1]] = avg
            i = j+1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x); mx = sum(rx)/n; my = sum(ry)/n
    num = sum((a-mx)*(b-my) for a,b in zip(rx,ry))
    dx = sum((a-mx)**2 for a in rx)**0.5; dy = sum((b-my)**2 for b in ry)**0.5
    if dx == 0 or dy == 0:
        return None
    return num/(dx*dy)

def main():
    idxs = sorted(SET.keys())
    per = {}
    missing = []
    for idx in idxs:
        f = find_conf(idx)
        if f is None:
            missing.append(idx)
            continue
        with open(f) as fh:
            d = json.load(fh)
        per[idx] = {
            "iptm": d.get("iptm"),
            "ptm": d.get("ptm"),
            "complex_plddt": d.get("complex_plddt"),
            "ligand_iptm": d.get("ligand_iptm"),
            "confidence_score": d.get("confidence_score"),
            "pact": SET[idx][0],
            "active": SET[idx][1],
        }

    finished = sorted(per.keys())
    result = {
        "experiment": "AFFINITY_IPTM1_structure_confidence",
        "prereg_set_idx": idxs,
        "n_prereg": len(idxs),
        "n_finished": len(finished),
        "finished_idx": finished,
        "missing_idx": sorted(missing),
        "baseline_docking_auroc": DOCK_AUROC,
        "baseline_random_auroc": RAND_AUROC,
        "gate": "PROMISING if iptm_auroc>0.60 AND iptm_auroc>0.4285 else NEGATIVE; INFEASIBLE if boltz did not finish",
    }

    if len(finished) < len(idxs):
        result["status"] = "INFEASIBLE_OR_PARTIAL"
        result["iptm_auroc"] = None
        result["iptm_pact_spearman"] = None
        result["complex_plddt_auroc"] = None
        result["verdict"] = "INFEASIBLE: structure-only boltz did not emit all confidence JSONs on CPU"
    else:
        iptm = [per[i]["iptm"] for i in finished]
        plddt = [per[i]["complex_plddt"] for i in finished]
        pact = [per[i]["pact"] for i in finished]
        active = [per[i]["active"] for i in finished]
        a_iptm = auroc(iptm, active)
        a_plddt = auroc(plddt, active)
        s = spearman(iptm, pact)
        result["status"] = "SCORED"
        result["iptm_auroc"] = None if a_iptm is None else round(a_iptm, 4)
        result["complex_plddt_auroc"] = None if a_plddt is None else round(a_plddt, 4)
        result["iptm_pact_spearman"] = None if s is None else round(s, 4)
        promising = (a_iptm is not None) and (a_iptm > 0.60) and (a_iptm > DOCK_AUROC)
        result["verdict"] = "PROMISING" if promising else "NEGATIVE"

    # round per-compound floats for reproducibility
    per_r = {}
    for idx in finished:
        r = {}
        for k, v in per[idx].items():
            r[k] = round(v, 4) if isinstance(v, float) else v
        per_r[str(idx)] = r
    result["per_compound"] = per_r

    os.makedirs(OUT, exist_ok=True)
    payload = json.dumps(result, sort_keys=True, separators=(",", ":"))
    with open(os.path.join(OUT, "AFFINITY_IPTM1_metrics.json"), "w") as fh:
        json.dump(result, fh, sort_keys=True, indent=2)
        fh.write("\n")
    sha = hashlib.sha256(payload.encode()).hexdigest()
    with open(os.path.join(OUT, "payload.sha256"), "w") as fh:
        fh.write(sha + "\n")
    print("STATUS:", result["status"], "| n_finished:", len(finished), "/", len(idxs))
    print("iptm_auroc:", result.get("iptm_auroc"), "| spearman:", result.get("iptm_pact_spearman"),
          "| plddt_auroc:", result.get("complex_plddt_auroc"))
    print("VERDICT:", result["verdict"])
    print("SHA256:", sha)

if __name__ == "__main__":
    main()
