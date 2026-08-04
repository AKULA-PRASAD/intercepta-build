"""MET4 — mechanism BEYOND metabolism: does PPI-network centrality add target-ID signal beyond conservation for the
NON-metabolic (FBA-blind) drug targets, and does it survive the two confounds it must beat — (1) HOMOLOGY circularity and
(2) STUDY/ANNOTATION BIAS (drug targets studied more -> more experimental edges)? E. coli, in-domain existence test.
Networks: FULL (combined>=700, homology+study laden), EXP (experiments>=400, non-homology but study-biased), COEXP
(coexpression>=400, non-homology AND not study-effort-biased -> the clean arbiter). Study-intensity covariate = textmining
degree. Genuine signal iff the lift survives beyond [conservation + study-intensity] AND on the coexpression network.
Deterministic. Envs: bioinfo (mmseqs) + intercepta-build (networkx/sklearn).
"""
import os, json, time, gzip, hashlib, subprocess, shutil
import numpy as np
import warnings; warnings.filterwarnings("ignore")
import networkx as nx
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, MET2, MET4 = os.path.join(DATA, "tid1"), os.path.join(DATA, "met2"), os.path.join(DATA, "met4")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
SCR = os.path.join(HERE, "scratch")
REFPANEL = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis",
            "pfalciparum", "tbrucei", "lmajor", "calbicans"]
# STRING full-file column indices (0-based): combined=15, experiments(direct)=9, coexpression(direct)=7, textmining(direct)=13
COL = {"full": 15, "exp": 9, "coexp": 7, "tm": 13}
THRESH = {"full": 700, "exp": 400, "coexp": 400, "tm": 400}
SEED = 42


def read_fasta(p):
    seqs, a, b = {}, None, []
    for ln in open(p):
        if ln.startswith(">"):
            if a: seqs[a] = "".join(b)
            h = ln[1:].split()[0]; a = h.split("|")[1] if "|" in h else h; b = []
        else: b.append(ln.strip())
    if a: seqs[a] = "".join(b)
    return seqs


def write_fasta(seqs, accs, path):
    with open(path, "w") as f:
        for x in accs:
            if seqs.get(x): f.write(f">{x}\n{seqs[x]}\n")


def best_bits(qf, tf, tag):
    out = os.path.join(SCR, f"{tag}.m8"); tmp = os.path.join(SCR, f"tmp_{tag}"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", qf, tf, out, tmp, "--threads", "4", "-e", "1e-3", "-s", "5.7",
                    "--format-output", "query,target,bits", "-v", "1"], capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3: continue
            q = p[0].split("|")[1] if "|" in p[0] else p[0]; v = float(p[2])
            if q not in best or v > best[q]: best[q] = v
    shutil.rmtree(tmp, ignore_errors=True)
    return best


def odds_ratio(y, x):
    thr = np.quantile(x, 0.75); hi = x >= thr if thr > 0 else x > 0
    a = float(((hi) & (y == 1)).sum()); b = float(((hi) & (y == 0)).sum())
    c = float(((~hi) & (y == 1)).sum()); d = float(((~hi) & (y == 0)).sum())
    return round(((a + .5) * (d + .5)) / ((b + .5) * (c + .5)), 3), [int(a), int(b), int(c), int(d)]


def cv_delta(base_cols, add_cols, y):
    """5-fold OOF ΔAUROC of adding `add_cols` on top of `base_cols`; + standardized coefs of the added cols."""
    Zb = np.column_stack(base_cols); Zf = np.column_stack(list(base_cols) + list(add_cols))
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED); base, full = np.zeros(len(y)), np.zeros(len(y))
    for tr, te in skf.split(Zf, y):
        sb = StandardScaler().fit(Zb[tr]); lb = LogisticRegression(max_iter=1000, random_state=SEED).fit(sb.transform(Zb[tr]), y[tr])
        base[te] = lb.predict_proba(sb.transform(Zb[te]))[:, 1]
        sf = StandardScaler().fit(Zf[tr]); lf = LogisticRegression(max_iter=1000, random_state=SEED).fit(sf.transform(Zf[tr]), y[tr])
        full[te] = lf.predict_proba(sf.transform(Zf[te]))[:, 1]
    sc = StandardScaler().fit(Zf); lr = LogisticRegression(max_iter=1000, random_state=SEED).fit(sc.transform(Zf), y)
    nb = Zb.shape[1]
    return {"auroc_base": round(float(roc_auc_score(y, base)), 4), "auroc_full": round(float(roc_auc_score(y, full)), 4),
            "cv_delta_auroc": round(float(roc_auc_score(y, full) - roc_auc_score(y, base)), 4),
            "coef_added": [round(float(c), 3) for c in lr.coef_[0][nb:]]}


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== MET4: PPI-network centrality for NON-metabolic targets, study-bias-controlled (E. coli) ===")
    proteome = read_fasta(os.path.join(TID1, "proteomes", "ecoli.fasta"))
    targets = set(x.strip() for x in open(os.path.join(TID1, "targets", "ecoli_chembl.txt")) if x.strip())
    gem = set(p.rstrip().split("\t")[1] for p in open(os.path.join(MET2, "essentiality.tsv")) if p.startswith("ecoli\t"))
    acc2sid = {}
    with gzip.open(os.path.join(MET4, "aliases.txt.gz"), "rt") as fh:
        for ln in fh:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3 or "UniProt_AC" not in p[2]: continue
            if p[1] in proteome and p[1] not in acc2sid: acc2sid[p[1]] = p[0]
    print(f"  proteome {len(proteome)}, targets {len(targets)}, GEM(metabolic) {len(gem)}, acc->STRING {len(acc2sid)} [{time.time()-t0:.0f}s]")
    # build the 4 channel networks in one pass
    edges = {k: [] for k in COL}
    with gzip.open(os.path.join(MET4, "links.full.txt.gz"), "rt") as fh:
        next(fh)
        for ln in fh:
            p = ln.rstrip("\n").split(" ")
            for k, ci in COL.items():
                if int(p[ci]) >= THRESH[k]: edges[k].append((p[0], p[1]))
    G = {k: nx.Graph() for k in COL}
    for k in COL: G[k].add_edges_from(edges[k])
    for k in COL: print(f"  {k:6s} graph: {G[k].number_of_nodes()} nodes / {G[k].number_of_edges()} edges")
    # centralities
    deg = {k: nx.degree_centrality(G[k]) for k in COL}
    btw = {}
    for k in ["full", "exp", "coexp"]:
        btw[k] = nx.betweenness_centrality(G[k], normalized=True); print(f"  betweenness {k} done [{time.time()-t0:.0f}s]")

    def C_(acc, d): sid = acc2sid.get(acc); return float(d.get(sid, 0.0)) if sid else 0.0

    def evaluate(accs, label):
        write_fasta(proteome, accs, os.path.join(SCR, f"q_{label}.fasta"))
        ot, ota = {}, []
        for o in [r for r in REFPANEL if r != "ecoli"]:
            tg = set(x.strip() for x in open(os.path.join(TID1, "targets", f"{o}_chembl.txt")) if x.strip())
            pr = read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta"))
            for a in tg:
                if a in pr: ot[a] = pr[a]; ota.append(a)
        write_fasta(ot, ota, os.path.join(SCR, f"ot_{label}.fasta"))
        cons = best_bits(os.path.join(SCR, f"q_{label}.fasta"), os.path.join(SCR, f"ot_{label}.fasta"), f"c_{label}")
        y = np.array([1 if a in targets else 0 for a in accs])
        C = np.array([cons.get(a, 0.0) for a in accs])
        SI = np.array([C_(a, deg["tm"]) for a in accs])  # study-intensity = textmining degree
        res = {"n": len(accs), "n_targets": int(y.sum()), "prevalence": round(float(y.mean()), 4),
               "auroc_conservation": round(float(roc_auc_score(y, C)), 4),
               "auroc_study_intensity_alone": round(float(roc_auc_score(y, SI)), 4),
               "nets": {}}
        for k in ["full", "exp", "coexp"]:
            dk = np.array([C_(a, deg[k]) for a in accs]); bk = np.array([C_(a, btw[k]) for a in accs])
            orv, tab = odds_ratio(y, dk)
            res["nets"][k] = {
                "H1_OR_topquartile_degree": orv, "H1_2x2": tab,
                "beyond_conservation": cv_delta([C], [dk, bk], y),                 # H2a
                "beyond_cons_plus_studyintensity": cv_delta([C, SI], [dk, bk], y)}  # H2b (the real test)
        print(f"  [{label}] n={len(accs)} tgt={int(y.sum())} | SI-alone AUROC {res['auroc_study_intensity_alone']:.3f} "
              f"| EXP Δ|cons {res['nets']['exp']['beyond_conservation']['cv_delta_auroc']:+.3f} "
              f"Δ|cons+SI {res['nets']['exp']['beyond_cons_plus_studyintensity']['cv_delta_auroc']:+.3f} "
              f"| COEXP Δ|cons+SI {res['nets']['coexp']['beyond_cons_plus_studyintensity']['cv_delta_auroc']:+.3f} [{time.time()-t0:.0f}s]")
        return res

    nonmet = sorted(a for a in proteome if a not in gem)
    per = {"nonmetabolic": evaluate(nonmet, "nonmet"), "fullproteome": evaluate(sorted(proteome), "all")}

    nm = per["nonmetabolic"]
    exp_b = nm["nets"]["exp"]["beyond_cons_plus_studyintensity"]
    cox_b = nm["nets"]["coexp"]["beyond_cons_plus_studyintensity"]
    exp_survives = exp_b["cv_delta_auroc"] > 0.02 and max((abs(c) for c in exp_b["coef_added"]), default=0) > 0.1
    cox_survives = cox_b["cv_delta_auroc"] > 0.02 and max((abs(c) for c in cox_b["coef_added"]), default=0) > 0.1
    genuine = bool(exp_survives and cox_survives)
    si_strong = nm["auroc_study_intensity_alone"] >= 0.6
    summary = {"organism": "ecoli", "population": "non-metabolic subproteome (FBA-blind)",
               "nonmet_n": nm["n"], "nonmet_targets": nm["n_targets"],
               "study_intensity_alone_auroc": nm["auroc_study_intensity_alone"],
               "EXP_delta_beyond_conservation": nm["nets"]["exp"]["beyond_conservation"]["cv_delta_auroc"],
               "EXP_delta_beyond_cons_plus_studyintensity": exp_b["cv_delta_auroc"],
               "COEXP_delta_beyond_cons_plus_studyintensity": cox_b["cv_delta_auroc"],
               "genuine_mechanistic_nonhomology_signal": genuine}
    if genuine:
        summary["verdict"] = (f"H2 TRUE (mechanism EXTENDS beyond metabolism, confound-robust): on the non-metabolic "
                              f"subproteome, PPI centrality adds beyond conservation AND survives BOTH controls — beyond "
                              f"[conservation+study-intensity] on the non-homology experimental network (ΔAUROC "
                              f"{exp_b['cv_delta_auroc']:+.3f}) AND on the study-bias-robust coexpression network "
                              f"({cox_b['cv_delta_auroc']:+.3f}). A genuine non-homology mechanistic signal for the FBA-blind "
                              f"half. **CAVEAT: requires a MEASURED PPI/coexpression network -> in-domain/well-studied-pathogen "
                              f"capability, NOT zero-data-novel.** E. coli, in-domain existence test.")
    else:
        why = []
        if nm["nets"]["exp"]["beyond_conservation"]["cv_delta_auroc"] > 0.02 and not exp_survives:
            why.append(f"the raw experimental lift (Δ|cons {nm['nets']['exp']['beyond_conservation']['cv_delta_auroc']:+.3f}) "
                       f"COLLAPSES once study-intensity is controlled (Δ|cons+SI {exp_b['cv_delta_auroc']:+.3f}); "
                       f"study-intensity alone already predicts targets at AUROC {nm['auroc_study_intensity_alone']:.3f}")
        if not cox_survives:
            why.append(f"the unbiased coexpression network shows no robust lift (Δ|cons+SI {cox_b['cv_delta_auroc']:+.3f})")
        summary["verdict"] = ("H0/CONFOUNDED (mechanism stays metabolism-bound as tested): the apparent PPI-centrality signal "
                              "for non-metabolic targets is NOT a confound-robust non-homology mechanism — " + "; ".join(why) +
                              ". Honest boundary: unlike FBA-essentiality (a genuine mechanism for METABOLIC targets), "
                              "PPI-network centrality target-ID for the FBA-blind half is largely a STUDY-BIAS artifact "
                              "(drug targets are studied more -> more edges). E. coli, in-domain.")
    print("\nPANEL:", json.dumps({k: v for k, v in summary.items() if k != "verdict"}, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "thresholds": THRESH,
            "graph": {k: {"nodes": G[k].number_of_nodes(), "edges": G[k].number_of_edges()} for k in COL}}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_population": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "MET4_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_population": per,
                          "graph": prov["graph"]}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "MET4_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/MET4_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
