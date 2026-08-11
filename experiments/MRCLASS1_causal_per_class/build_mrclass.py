#!/usr/bin/env python
"""MRCLASS1 — PRELIMINARY per-disease cis-MR enrichment, grouped by GENETICCLASS1 disease class, on the 5
diseases MR1 already downloaded (CACHED hits + instruments; NO new GWAS downloads). Tests whether the
transparent self-computed cis-MR causal signal CORROBORATES GENETICCLASS1's OT-based per-class envelope.
HONEST SCOPE: 5 diseases / 4 classes (1-2 each) -> per-DISEASE with class labels, NOT a powered per-class
envelope (that needs ~10-15 more throttled GWAS downloads). Deterministic; reproduces byte-identical."""
import os, json, gzip, hashlib, math
import numpy as np, pandas as pd
from scipy import stats

D = os.path.expanduser("/Users/kalki/intercepta_data"); MR = os.path.join(D, "mr1"); G1 = os.path.join(D, "genetics1")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
PALINDROME = {frozenset("AT"), frozenset("CG")}; COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}
PANEL = {"MONDO_0005010": ("CAD", "cardiovascular", "FULL"), "MONDO_0005148": ("T2D", "metabolic", "CAPPED"),
         "MONDO_0005265": ("IBD", "immune_inflammatory", "FULL"), "MONDO_0005180": ("Parkinson", "neuro_psychiatric", "FULL"),
         "MONDO_0008383": ("RA", "immune_inflammatory", "FULL")}  # class + GENETICCLASS1 OT grade

def build_universe():
    pc = set()
    with gzip.open(os.path.join(G1, "Homo_sapiens.gene_info.gz"), "rt") as f:
        hdr = f.readline().rstrip("\n").split("\t"); si = hdr.index("Symbol"); ti = hdr.index("type_of_gene")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[ti] == "protein-coding": pc.add(p[si])
    df = pd.read_parquet(os.path.join(G1, "genetics1_dataset.parquet")); df = df[df.biotype == "protein_coding"]
    return sorted(pc), df

def align(row):
    ea, oa, beta, p = row["ea"], row["oa"], row["beta"], row["p"]
    if pd.isna(ea) or pd.isna(beta): return 0.0, 0
    inc, dec = row["expr_inc"], row["expr_dec"]
    if frozenset({ea, oa}) in PALINDROME or frozenset({inc, dec}) in PALINDROME: return 0.0, 0
    if ea == inc or COMP.get(ea) == inc or oa == inc or COMP.get(oa) == inc:
        return (float(-np.log10(p)) if p > 0 else 0.0), 1
    return 0.0, 0

def woolf(a, b, c, d):
    OR, p = stats.fisher_exact([[a, b], [c, d]])
    aa, bb, cc, dd = a+.5, b+.5, c+.5, d+.5; ln = np.log((aa*dd)/(bb*cc)); se = np.sqrt(1/aa+1/bb+1/cc+1/dd)
    return float(OR), float(p), float(np.exp(ln-1.96*se)), float(np.exp(ln+1.96*se))

def main():
    inst = pd.read_parquet(os.path.join(MR, "instruments.parquet"))
    inst["expr_inc"] = np.where(inst.Zscore > 0, inst.AssessedAllele, inst.OtherAllele)
    inst["expr_dec"] = np.where(inst.Zscore > 0, inst.OtherAllele, inst.AssessedAllele)
    inst = inst.sort_values("Pvalue").drop_duplicates("GeneSymbol", keep="first").set_index("GeneSymbol")[["SNP", "expr_inc", "expr_dec"]]
    universe, df = build_universe()
    per = {}
    for did, (name, cls, ot_grade) in PANEL.items():
        sub = df[df.disease_id == did].groupby("target_symbol").agg({"genetic_association": "max", "clinical": "max"})
        u = pd.DataFrame({"symbol": universe})
        u["drug"] = u.symbol.map(lambda s: int(sub.at[s, "clinical"] > 0) if s in sub.index else 0)
        u = u.join(inst, on="symbol")
        H = pd.read_parquet(os.path.join(MR, "hits", f"{did}.parquet")).rename(columns={"rsid": "SNP"})
        u = u.merge(H, on="SNP", how="left")
        res = u.apply(align, axis=1, result_type="expand"); u["mr_score"], u["tested"] = res[0], res[1]
        nt = int(u.tested.sum()); thr = 0.05 / max(nt, 1)
        u["mr_sig"] = ((u.tested == 1) & (np.power(10.0, -u.mr_score) < thr)).astype(int)
        y = u.drug.values; ms = u.mr_sig.values
        a = int(((ms == 1) & (y == 1)).sum()); b = int(((ms == 1) & (y == 0)).sum())
        c = int(((y == 1) & (ms == 0)).sum()); d = int(((y == 0) & (ms == 0)).sum())
        OR, p, lo, hi = woolf(a, b, c, d)
        # corroboration: does MR OR CI-lower>1 agree with GENETICCLASS1 OT grade (FULL/CAPPED = signal present)?
        mr_signal = lo > 1.0
        agree = (mr_signal == (ot_grade in ("FULL", "CAPPED")))
        per[name] = {"disease_id": did, "class": cls, "OT_class_grade": ot_grade, "n_tested": nt, "n_mr_sig": int(ms.sum()),
                     "MRsig_clinical": [a, b, c, d], "MR_OR": round(OR, 3), "MR_OR_95CI": [round(lo, 3), round(hi, 3)],
                     "MR_signal_present": bool(mr_signal), "corroborates_GENETICCLASS1": bool(agree)}
        print(f"{name:10s} {cls:22s} OT={ot_grade:7s} | MR OR {OR:5.2f} CI[{lo:.2f},{hi:.2f}] "
              f"sig={int(ms.sum())} | MR-signal={mr_signal} corroborates={agree}")
    out = {"panel_n": len(per), "note": "PRELIMINARY: 5 cached diseases / 4 classes (1-2 each); per-DISEASE with "
           "class labels, NOT a powered per-class envelope. Powered version needs ~10-15 more throttled GWAS "
           "downloads and (per MR1 H2 redundancy) would likely mirror GENETICCLASS1.",
           "per_disease": per, "n_corroborate": sum(v["corroborates_GENETICCLASS1"] for v in per.values()),
           "seed": 42}
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "MRCLASS1_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    print(f"\ncorroborates GENETICCLASS1: {out['n_corroborate']}/{len(per)} diseases")
    print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
