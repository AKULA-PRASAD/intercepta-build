#!/usr/bin/env python
"""MR1 step 2 (v2) — transparent single-instrument cis-MR (Wald ratio) per (gene, disease), evaluated on the
GENETICS1 GENOME-WIDE universe (20,596 NCBI protein-coding symbols x 5 diseases; OT scores where present else 0).
Reports the OT POSITIVE CONTROL (genassoc>0 vs clinical>0, must reproduce OR>1) BEFORE the MR verdict.
Deterministic (seed 42); reproduces byte-identical. Implements prereg/MR1.md (incl. the 2026-08-10 correction).

Wald-ratio insight: for a single instrument, MR significance = disease-GWAS p at the gene's strongest cis-eQTL
SNP (the eQTL magnitude cancels); causal direction = sign(GWAS beta aligned to the expression-increasing allele).
Palindromic (A/T,C/G) SNPs dropped. GWAS instrument-SNP rows are cached to hits/ so re-runs are fast + identical.
"""
import os, sys, json, gzip, hashlib
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

D = os.environ.get("INTERCEPTA_DATA", os.path.expanduser("~/intercepta_data"))
MR = os.path.join(D, "mr1"); GW = os.path.join(MR, "gwas"); HITS = os.path.join(MR, "hits")
G1 = os.path.join(D, "genetics1")
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
SEED = 42
PANEL = {  # GENETICS1 disease_id -> gwas file (asthma dropped pre-scoring, see DATA.md CORRECTION)
    "MONDO_0005010": "CAD.h.tsv.gz", "MONDO_0005148": "T2D.h.tsv.gz",
    "MONDO_0005265": "IBD.h.tsv.gz", "MONDO_0005180": "PARKINSON.h.tsv.gz",
    "MONDO_0008383": "RA.h.tsv.gz",
}
PALINDROME = {frozenset("AT"), frozenset("CG")}
COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}

def _col(cols, *cands):
    low = {c.lower(): c for c in cols}
    for c in cands:
        if c in low: return low[c]
    return None

def stream_hits(path, snps):
    head = pd.read_csv(path, sep="\t", nrows=0, compression="gzip"); cols = list(head.columns)
    c_rs = _col(cols, "hm_rsid", "rsid", "variant_id", "rs_id", "snp")
    c_ea = _col(cols, "hm_effect_allele", "effect_allele", "alt", "a1")
    c_oa = _col(cols, "hm_other_allele", "other_allele", "ref", "a2")
    c_b = _col(cols, "hm_beta", "beta", "effect"); c_or = _col(cols, "hm_odds_ratio", "odds_ratio", "or")
    c_p = _col(cols, "p_value", "pvalue", "p", "p-value", "pval")
    use = [x for x in [c_rs, c_ea, c_oa, c_b, c_or, c_p] if x]
    rows = {}
    for ch in pd.read_csv(path, sep="\t", usecols=use, compression="gzip", chunksize=500_000, dtype=str, low_memory=False):
        m = ch[ch[c_rs].isin(snps)]
        for _, r in m.iterrows():
            rs = r[c_rs]
            if rs in rows or pd.isna(rs): continue
            try: p = float(r[c_p])
            except Exception: continue
            beta = np.nan
            if c_b and pd.notna(r[c_b]) and str(r[c_b]) not in ("", "NA"):
                try: beta = float(r[c_b])
                except Exception: beta = np.nan
            if np.isnan(beta) and c_or and pd.notna(r[c_or]) and str(r[c_or]) not in ("", "NA"):
                try: beta = np.log(float(r[c_or]))
                except Exception: beta = np.nan
            rows[rs] = (str(r[c_ea]).upper(), str(r[c_oa]).upper(), beta, p)
    return rows

def get_hits(did, fname, snps):
    hp = os.path.join(HITS, f"{did}.parquet")
    if os.path.exists(hp):
        h = pd.read_parquet(hp)
    else:
        os.makedirs(HITS, exist_ok=True)
        d = stream_hits(os.path.join(GW, fname), snps)
        h = pd.DataFrame([(k, *v) for k, v in d.items()], columns=["rsid", "ea", "oa", "beta", "p"])
        h.to_parquet(hp, index=False)
    return {r.rsid: (r.ea, r.oa, r.beta, r.p) for r in h.itertuples()}

def build_universe():
    pc = set()
    with gzip.open(os.path.join(G1, "Homo_sapiens.gene_info.gz"), "rt") as f:
        hdr = f.readline().rstrip("\n").split("\t"); si = hdr.index("Symbol"); ti = hdr.index("type_of_gene")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[ti] == "protein-coding": pc.add(p[si])
    universe = sorted(pc)
    pub = json.load(open(os.path.join(G1, "gene_pubcounts.json")))
    logpub = {s: float(np.log1p(pub.get(s, 0.0))) for s in universe}
    df = pd.read_parquet(os.path.join(G1, "genetics1_dataset.parquet"))
    df = df[df.biotype == "protein_coding"]
    return universe, logpub, df

def align_mr(row):
    """row has: SNP, expr_inc, expr_dec, ea, oa, beta, p. Return (mr_score, direction, tested)."""
    ea, oa, beta, p = row["ea"], row["oa"], row["beta"], row["p"]
    if pd.isna(ea): return 0.0, 0, 0
    inc, dec = row["expr_inc"], row["expr_dec"]
    if frozenset({ea, oa}) in PALINDROME or frozenset({inc, dec}) in PALINDROME: return 0.0, 0, 0
    if pd.isna(beta): return 0.0, 0, 0
    if ea == inc: baln = beta
    elif oa == inc: baln = -beta
    elif COMP.get(ea) == inc: baln = beta
    elif COMP.get(oa) == inc: baln = -beta
    else: return 0.0, 0, 0
    score = float(-np.log10(p)) if p > 0 else 0.0
    return score, int(np.sign(baln)), 1

def fisher_ci(a, b, c, d):
    OR, p = stats.fisher_exact([[a, b], [c, d]])
    aa, bb, cc, dd = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    ln = np.log((aa * dd) / (bb * cc)); se = np.sqrt(1/aa + 1/bb + 1/cc + 1/dd)
    return float(OR), float(p), float(np.exp(ln - 1.96 * se)), float(np.exp(ln + 1.96 * se))

def main():
    os.makedirs(RES, exist_ok=True)
    inst = pd.read_parquet(os.path.join(MR, "instruments.parquet"))
    inst["expr_inc"] = np.where(inst.Zscore > 0, inst.AssessedAllele, inst.OtherAllele)
    inst["expr_dec"] = np.where(inst.Zscore > 0, inst.OtherAllele, inst.AssessedAllele)
    # strongest instrument per SYMBOL (universe is symbol-keyed)
    inst = inst.sort_values("Pvalue").drop_duplicates("GeneSymbol", keep="first")
    inst_sym = inst.set_index("GeneSymbol")[["SNP", "expr_inc", "expr_dec"]]
    snps = set(inst.SNP)

    universe, logpub, df = build_universe()
    U = len(universe)

    frames = []
    for did, fname in PANEL.items():
        sub = (df[df.disease_id == did].groupby("target_symbol")
               .agg({"genetic_association": "max", "clinical": "max"}))
        gen = pd.Series(0.0, index=universe); cli = pd.Series(0.0, index=universe)
        gi = sub.index.intersection(universe)
        gen.loc[gi] = sub.loc[gi, "genetic_association"].values
        cli.loc[gi] = sub.loc[gi, "clinical"].values
        u = pd.DataFrame({"symbol": universe, "disease_id": did, "gen": gen.values,
                          "drug": (cli.values > 0).astype(int),
                          "logpub": [logpub[s] for s in universe]})
        u = u.join(inst_sym, on="symbol")  # SNP, expr_inc, expr_dec (NaN if no instrument)
        hits = get_hits(did, fname, snps)
        H = pd.DataFrame([(k, *v) for k, v in hits.items()], columns=["SNP", "ea", "oa", "beta", "p"])
        u = u.merge(H, on="SNP", how="left")
        res = u.apply(align_mr, axis=1, result_type="expand")
        u["mr_score"], u["mr_direction"], u["tested"] = res[0], res[1], res[2]
        nt = int(u.tested.sum()); thr = 0.05 / max(nt, 1)
        u["mr_p"] = np.where(u.tested == 1, np.power(10.0, -u.mr_score), np.nan)
        u["mr_sig"] = ((u.tested == 1) & (u.mr_p < thr)).astype(int)
        frames.append(u)
        print(f"{did} {fname}: universe={len(u)} tested={nt} bonf={thr:.2e} mr_sig={int(u.mr_sig.sum())} "
              f"drug+={int(u.drug.sum())} (rate {u.drug.mean():.4f})", flush=True)
    G = pd.concat(frames, ignore_index=True); y = G.drug.values

    # ---- POSITIVE CONTROL: OT genassoc>0 vs drug (must reproduce GENETICS1 OR~2) ----
    sel = (G.gen > 0).values
    a, b = int((sel & (y == 1)).sum()), int((sel & (y == 0)).sum())
    c, d = int((~sel & (y == 1)).sum()), int((~sel & (y == 0)).sum())
    OR_ot, p_ot, lo_ot, hi_ot = fisher_ci(a, b, c, d)
    pos_ok = bool(lo_ot > 1.0)

    # ---- H1: cis-MR-significant vs drug ----
    ms = (G.mr_sig == 1).values
    a1, b1 = int((ms & (y == 1)).sum()), int((ms & (y == 0)).sum())
    c1, d1 = int((~ms & (y == 1)).sum()), int((~ms & (y == 0)).sum())
    OR1, p1, lo1, hi1 = fisher_ci(a1, b1, c1, d1)
    h1_pass = bool(lo1 > 1.0)

    # ---- H2: does MR add beyond OT genassoc? grouped CV by disease (+ fame-adjusted context) ----
    diseases = list(PANEL); G = G.reset_index(drop=True)
    def grouped_oof(feats):
        oof = np.zeros(len(G))
        for held in diseases:
            tr = (G.disease_id != held).values; te = (G.disease_id == held).values
            if len(set(y[tr])) < 2: continue
            Xtr = G.loc[tr, feats].values.astype(float); Xte = G.loc[te, feats].values.astype(float)
            mu, sd = Xtr.mean(0), Xtr.std(0); sd[sd == 0] = 1
            m = LogisticRegression(max_iter=1000, random_state=SEED).fit((Xtr - mu) / sd, y[tr])
            oof[te] = m.predict_proba((Xte - mu) / sd)[:, 1]
        return oof
    def dAP(fa, fb):
        oa, ob = grouped_oof(fa), grouped_oof(fb)
        apa, apb = average_precision_score(y, oa), average_precision_score(y, ob)
        rng = np.random.default_rng(SEED); n = len(y); bo = []
        for _ in range(2000):
            idx = rng.integers(0, n, n)
            if len(set(y[idx])) < 2: continue
            bo.append(average_precision_score(y[idx], ob[idx]) - average_precision_score(y[idx], oa[idx]))
        return float(apa), float(apb), float(np.percentile(bo, 2.5)), float(np.percentile(bo, 97.5))
    ap_ot, ap_otmr, dlo, dhi = dAP(["gen"], ["gen", "mr_score"])
    ap_otf, ap_otfmr, dlo2, dhi2 = dAP(["gen", "logpub"], ["gen", "logpub", "mr_score"])
    # MR coef sign/CI in pooled standardized logistic (OT + MR)
    Xs = G[["gen", "mr_score"]].values.astype(float); mu, sd = Xs.mean(0), Xs.std(0); sd[sd == 0] = 1; Xs = (Xs - mu) / sd
    rng = np.random.default_rng(SEED); n = len(y); cb = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        if len(set(y[idx])) < 2: continue
        try: cb.append(LogisticRegression(max_iter=1000, random_state=SEED).fit(Xs[idx], y[idx]).coef_[0][1])
        except Exception: pass
    cb = np.array(cb); mrc, clo, chi = float(cb.mean()), float(np.percentile(cb, 2.5)), float(np.percentile(cb, 97.5))
    dAP_ot = ap_otmr - ap_ot
    h2_pass = bool(clo > 0 and dAP_ot >= 0.01 and dlo > 0)

    out = {
        "panel": PANEL, "universe_protein_coding": U, "n_pairs": int(len(G)),
        "n_tested_MR": int(G.tested.sum()), "drug_base_rate": round(float(y.mean()), 5),
        "POSITIVE_CONTROL_OT_genassoc>0_vs_drug": {
            "OR": round(OR_ot, 4), "OR_95CI": [round(lo_ot, 4), round(hi_ot, 4)], "fisher_p": p_ot,
            "reproduces_GENETICS1": pos_ok},
        "H1_MRsig_vs_drug": {"contingency": [a1, b1, c1, d1], "OR": round(OR1, 4),
            "OR_95CI": [round(lo1, 4), round(hi1, 4)], "fisher_p": p1,
            "precision_in_MRsig": round(a1 / max(a1 + b1, 1), 4), "PASS": h1_pass},
        "H2_MR_beyond_OT": {"grouped_cv_AUPRC_OT": round(ap_ot, 4), "grouped_cv_AUPRC_OT+MR": round(ap_otmr, 4),
            "delta_AUPRC": round(dAP_ot, 4), "delta_AUPRC_95CI": [round(dlo, 4), round(dhi, 4)],
            "mr_coef_mean": round(mrc, 4), "mr_coef_95CI": [round(clo, 4), round(chi, 4)], "PASS": h2_pass},
        "H2_context_fame_adjusted": {"grouped_cv_AUPRC_OT+fame": round(ap_otf, 4),
            "grouped_cv_AUPRC_OT+fame+MR": round(ap_otfmr, 4), "delta_AUPRC": round(ap_otfmr - ap_otf, 4),
            "delta_AUPRC_95CI": [round(dlo2, 4), round(dhi2, 4)]},
        "context": {"AUROC_MR_alone": round(float(roc_auc_score(y, G.mr_score.values)), 4),
            "AUROC_OT_alone": round(float(roc_auc_score(y, G.gen.values)), 4)},
        "seed": SEED,
    }
    with open(os.path.join(RES, "MR1_metrics.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    payload = json.dumps(out, sort_keys=True).encode()
    with open(os.path.join(RES, "payload.sha256"), "w") as f:
        f.write(hashlib.sha256(payload).hexdigest() + "\n")
    print("\n=== MR1 RESULT ==="); print(json.dumps(out, indent=2, sort_keys=True))
    print("sha256:", hashlib.sha256(payload).hexdigest())

if __name__ == "__main__":
    main()
