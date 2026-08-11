#!/usr/bin/env python
"""CANCERCLASS1 — cancer-LINEAGE deployment envelope for zero-data functional-dependency target-ID.
Per lineage: do the lineage-SELECTIVE dependencies (DepMap Chronos, pan-essential-guarded) recover IntOGen
cancer drivers above a permutation null? Grades FULL/CAPPED/ABSTAIN per the locked gate. Deterministic
(perm seed 42); reproduces byte-identical. Data cached (figshare DepMap 22Q2 + IntOGen); NEVER committed."""
import os, json, hashlib
import numpy as np, pandas as pd

D = os.path.expanduser("/Users/kalki/intercepta_data")
DEP = os.path.join(D, "depmap_cancer_envelope"); INTOGEN = os.path.join(D, "f3clin1", "2024-06-18_IntOGen-Drivers")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
MIN_LINES, K, B, SEED, PAN_EFF, PAN_FRAC = 15, 20, 1000, 42, -0.5, 0.90

def main():
    ce = pd.read_csv(os.path.join(DEP, "CRISPR_gene_effect.csv"), index_col=0)
    ce = ce.dropna(axis=1, how="any")                       # genes measured in all lines (clean matrix)
    genes = np.array([c.split(" (")[0] for c in ce.columns])
    M = ce.values.astype(np.float32); lines = np.array(ce.index)
    meta = pd.read_csv(os.path.join(DEP, "sample_info.csv"), low_memory=False).set_index("DepMap_ID")
    lineage = meta["lineage"].reindex(lines).values
    drivers = set(pd.read_csv(os.path.join(INTOGEN, "Compendium_Cancer_Genes.tsv"), sep="\t")["SYMBOL"].dropna())

    # pan-essential guard: drop genes essential (<PAN_EFF) in >=PAN_FRAC of lines
    pan = (M < PAN_EFF).mean(0) >= PAN_FRAC
    keep = ~pan
    M = M[:, keep]; genes = genes[keep]
    is_driver = np.array([g in drivers for g in genes])
    overall = M.mean(0)                                     # per-gene overall mean gene-effect

    def recovery_at_K(idx):
        sel = overall - M[idx].mean(0)                      # higher = more selectively essential in this subset
        top = np.argpartition(sel, -K)[-K:]
        return float(is_driver[top].mean())

    rng = np.random.default_rng(SEED); n = M.shape[0]
    lineages = pd.Series(lineage).value_counts()
    lineages = [l for l, c in lineages.items() if isinstance(l, str) and c >= MIN_LINES]
    per = {}
    for lin in sorted(lineages):
        idx = np.where(lineage == lin)[0]; size = len(idx)
        obs = recovery_at_K(idx)
        null = np.array([recovery_at_K(rng.integers(0, n, size)) for _ in range(B)])
        nullm = float(null.mean())
        enr = round(obs / nullm, 3) if nullm > 0 else float("inf")
        p = float((np.sum(null >= obs) + 1) / (B + 1))
        grade = ("FULL" if (enr >= 3.0 and p < 0.05) else
                 "CAPPED" if (enr >= 1.5 or p < 0.05) else "ABSTAIN")
        per[lin] = {"n_lines": int(size), "recovery_at20": round(obs, 4), "null_recovery": round(nullm, 4),
                    "enrichment": enr, "perm_p": round(p, 4), "GRADE": grade}
        print(f"{lin:26s} n={size:3d} rec@20 {obs:.3f} null {nullm:.3f} enr {enr:5.2f} p {p:.4f} -> {grade}")
    grades = [v["GRADE"] for v in per.values()]
    out = {"n_lineages": len(per), "n_lines_total": int(n), "n_genes_after_pan_guard": int(M.shape[1]),
           "n_pan_essential_excluded": int(pan.sum()), "K": K, "B_perm": B, "seed": SEED,
           "gate": "FULL: enrichment>=3 & p<0.05; CAPPED: enrichment>=1.5 or p<0.05; else ABSTAIN",
           "per_lineage": per, "envelope_discriminates": bool("FULL" in grades and any(g != "FULL" for g in grades)),
           "transfer_table": {l: v["GRADE"] for l, v in per.items()},
           "scope": "DepMap 22Q2 CRISPR (cell-line) selective-dependency recovery of IntOGen drivers per lineage; "
                    "target-RELEVANCE, NOT patient/clinical; deployment-envelope characterization of a validated "
                    "arm (DEPEND1), not a new method."}
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "CANCERCLASS1_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    open(os.path.join(RES, "cancer_lineage_transfer_table.json"), "w").write(
        json.dumps(out["transfer_table"], indent=2, sort_keys=True) + "\n")
    from collections import Counter
    print("\ngrades:", dict(Counter(grades)), "| discriminates:", out["envelope_discriminates"])
    print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
