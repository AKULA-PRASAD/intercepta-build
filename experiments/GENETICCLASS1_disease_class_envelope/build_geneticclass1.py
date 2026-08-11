#!/usr/bin/env python
"""GENETICCLASS1 — disease-class deployment envelope for zero-data genetic target-ID.
Rebuilds the GENETICS1/MR1 genome-wide universe (20,596 protein-coding genes x 27 diseases; full universe is
mandatory — the parquet subset is collider-biased), groups diseases into 6 frozen classes, and per class computes:
Fisher OR + Mantel-Haenszel OR (disease-stratified) + genassoc-AUROC + a fame-adjusted logistic genassoc coef.
Applies the locked FULL/CAPPED/ABSTAIN gate. Deterministic (seed 42); reproduces byte-identical. See PREREG."""
import os, json, gzip, hashlib
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm

G1 = os.path.expanduser("/Users/kalki/intercepta_data/genetics1")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results"); os.makedirs(RES, exist_ok=True)
SEED = 42

CLASS_MAP = {  # disease_id -> class (frozen, PREREG)
    "MONDO_0005083": "immune_inflammatory", "MONDO_0005265": "immune_inflammatory",
    "MONDO_0005301": "immune_inflammatory", "MONDO_0005306": "immune_inflammatory",
    "MONDO_0007915": "immune_inflammatory", "MONDO_0008383": "immune_inflammatory",
    "MONDO_0011849": "immune_inflammatory", "MONDO_0004980": "immune_inflammatory",
    "MONDO_0005147": "immune_inflammatory", "MONDO_0004979": "immune_inflammatory",
    "MONDO_0002009": "neuro_psychiatric", "MONDO_0004975": "neuro_psychiatric",
    "MONDO_0004976": "neuro_psychiatric", "MONDO_0005027": "neuro_psychiatric",
    "MONDO_0005090": "neuro_psychiatric", "MONDO_0005180": "neuro_psychiatric",
    "HP_0000822": "cardiovascular", "MONDO_0005010": "cardiovascular", "MONDO_0005252": "cardiovascular",
    "HP_0001513": "metabolic", "MONDO_0005148": "metabolic", "MONDO_0013209": "metabolic",
    "MONDO_0005002": "respiratory_fibrotic", "EFO_0000768": "respiratory_fibrotic",
    "MONDO_0005178": "musculoskeletal_renal", "MONDO_0005298": "musculoskeletal_renal",
    "MONDO_0005300": "musculoskeletal_renal",
}

def build_universe():
    pc = set()
    with gzip.open(os.path.join(G1, "Homo_sapiens.gene_info.gz"), "rt") as f:
        hdr = f.readline().rstrip("\n").split("\t"); si = hdr.index("Symbol"); ti = hdr.index("type_of_gene")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[ti] == "protein-coding": pc.add(p[si])
    universe = sorted(pc)
    pub = json.load(open(os.path.join(G1, "gene_pubcounts.json")))
    logpub = np.array([np.log1p(pub.get(s, 0.0)) for s in universe])
    df = pd.read_parquet(os.path.join(G1, "genetics1_dataset.parquet"))
    df = df[df.biotype == "protein_coding"]
    return universe, logpub, df

def woolf_ci(a, b, c, d):
    OR, p = stats.fisher_exact([[a, b], [c, d]])
    aa, bb, cc, dd = a + .5, b + .5, c + .5, d + .5
    ln = np.log((aa * dd) / (bb * cc)); se = np.sqrt(1/aa + 1/bb + 1/cc + 1/dd)
    return float(OR), float(p), float(np.exp(ln - 1.96 * se)), float(np.exp(ln + 1.96 * se))

def mantel_haenszel(strata):
    """strata: list of (a,b,c,d). MH-OR + Robins-Breslow-Greenland 95% CI."""
    num = sum(a * d / (a + b + c + d) for a, b, c, d in strata if (a+b+c+d) > 0)
    den = sum(b * c / (a + b + c + d) for a, b, c, d in strata if (a+b+c+d) > 0)
    if den == 0: return float("inf"), 0.0, float("inf")
    mh = num / den
    # RBG variance of ln(MH-OR)
    R = num; S = den; sumPR = sumPS_QR = sumQS = 0.0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n == 0: continue
        P = (a + d) / n; Q = (b + c) / n; Rk = a * d / n; Sk = b * c / n
        sumPR += P * Rk; sumPS_QR += P * Sk + Q * Rk; sumQS += Q * Sk
    var = sumPR / (2 * R**2) + sumPS_QR / (2 * R * S) + sumQS / (2 * S**2) if R > 0 and S > 0 else 0.0
    se = np.sqrt(var)
    return float(mh), float(np.exp(np.log(mh) - 1.96*se)), float(np.exp(np.log(mh) + 1.96*se))

def auroc(y, score):
    y = np.asarray(y, int); score = np.asarray(score, float)
    if len(set(y)) < 2: return float("nan")
    r = stats.rankdata(score); npos = y.sum()
    return float((r[y == 1].sum() - npos*(npos+1)/2) / (npos * (len(y)-npos)))

def main():
    universe, logpub, df = build_universe()
    U = len(universe)
    # genome-wide rows per disease
    frames = []
    for did in CLASS_MAP:
        sub = (df[df.disease_id == did].groupby("target_symbol")
               .agg({"genetic_association": "max", "clinical": "max"}))
        gen = pd.Series(0.0, index=universe); cli = pd.Series(0.0, index=universe)
        gi = sub.index.intersection(universe)
        gen.loc[gi] = sub.loc[gi, "genetic_association"].values
        cli.loc[gi] = sub.loc[gi, "clinical"].values
        frames.append(pd.DataFrame({"disease_id": did, "cls": CLASS_MAP[did], "gen": gen.values,
                                    "drug": (cli.values > 0).astype(int), "logpub": logpub}))
    G = pd.concat(frames, ignore_index=True)

    out = {"universe_protein_coding": U, "n_pairs": int(len(G)), "seed": SEED, "classes": {}}
    rng = np.random.default_rng(SEED)
    for cls in sorted(set(CLASS_MAP.values())):
        C = G[G.cls == cls]
        sel = (C.gen > 0).values; drug = (C.drug == 1).values
        a = int((sel & drug).sum()); b = int((sel & ~drug).sum())
        c = int((~sel & drug).sum()); d = int((~sel & ~drug).sum())
        OR, p, lo, hi = woolf_ci(a, b, c, d)
        strata = []
        for did in C.disease_id.unique():
            Cd = C[C.disease_id == did]; s = (Cd.gen > 0).values; dr = (Cd.drug == 1).values
            strata.append((int((s&dr).sum()), int((s&~dr).sum()), int((~s&dr).sum()), int((~s&~dr).sum())))
        mh, mhlo, mhhi = mantel_haenszel(strata)
        au = auroc(drug.astype(int), C.gen.values)
        # fame-adjusted logistic: drug ~ z(gen)+z(logpub) + intercept; analytic 95% CI on genassoc coef
        X = C[["gen", "logpub"]].values.astype(float); y = drug.astype(int)
        mu, sd = X.mean(0), X.std(0); sd[sd == 0] = 1; Xs = sm.add_constant((X - mu)/sd, has_constant="add")
        try:
            m = sm.Logit(y, Xs).fit(disp=0, method="newton", maxiter=200)
            cmean = float(m.params[1]); ci = m.conf_int(); clo = float(ci[1][0]); chi = float(ci[1][1])
        except Exception:
            cmean = clo = chi = float("nan")
        # locked gate
        if mhlo > 1.5 and clo > 0: grade = "FULL"
        elif mhlo > 1.0: grade = "CAPPED"
        else: grade = "ABSTAIN"
        out["classes"][cls] = {
            "n_diseases": int(C.disease_id.nunique()), "n_drug_pos": int(drug.sum()),
            "fisher_OR": round(OR, 3), "fisher_OR_95CI": [round(lo, 3), round(hi, 3)],
            "MH_OR": round(mh, 3), "MH_OR_95CI": [round(mhlo, 3), round(mhhi, 3)],
            "genassoc_AUROC": round(au, 4),
            "fame_adj_genassoc_coef": round(cmean, 4), "fame_adj_coef_95CI": [round(clo, 4), round(chi, 4)],
            "GRADE": grade,
        }
    grades = [v["GRADE"] for v in out["classes"].values()]
    out["envelope_discriminates"] = bool("FULL" in grades and any(g != "FULL" for g in grades))
    out["transfer_table"] = {c: v["GRADE"] for c, v in out["classes"].items()}
    payload = json.dumps(out, indent=2, sort_keys=True)
    open(os.path.join(RES, "GENETICCLASS1_metrics.json"), "w").write(payload + "\n")
    open(os.path.join(RES, "payload.sha256"), "w").write(hashlib.sha256(payload.encode()).hexdigest() + "\n")
    open(os.path.join(RES, "disease_class_transfer_table.json"), "w").write(
        json.dumps(out["transfer_table"], indent=2, sort_keys=True) + "\n")
    for c in sorted(out["classes"]):
        v = out["classes"][c]
        print(f"{c:22s} MH-OR {v['MH_OR']:5.2f} CI[{v['MH_OR_95CI'][0]:.2f},{v['MH_OR_95CI'][1]:.2f}] "
              f"AUROC {v['genassoc_AUROC']:.3f} fame-coef {v['fame_adj_genassoc_coef']:+.3f}"
              f"[{v['fame_adj_coef_95CI'][0]:+.3f},{v['fame_adj_coef_95CI'][1]:+.3f}] -> {v['GRADE']}")
    print("envelope discriminates:", out["envelope_discriminates"])
    print("sha256:", hashlib.sha256(payload.encode()).hexdigest())

if __name__ == "__main__":
    main()
