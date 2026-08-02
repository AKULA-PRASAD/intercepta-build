"""MET1 Step B — does FBA gene-essentiality enrich for drug targets BEYOND conservation? Gene-level test on E. coli's
metabolic subproteome (iML1515): per GEM gene, FBA-essential (cached) + is_drug_target (ChEMBL-xref) + conservation
(mmseqs2 homology to OTHER organisms' targets). H1 enrichment; H2 (decisive) essentiality additive over conservation
(5-fold-CV nested ΔAUROC + pooled partial coefficient). Implements prereg/MET1_fba_essentiality_targets.md.
Deterministic -> reproduce x2. (S. aureus/K. pneumoniae GEMs lacked UniProt gene annotations -> E. coli only; stated.)
"""
import os, sys, json, time, hashlib, subprocess, shutil
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, MET1 = os.path.join(DATA, "tid1"), os.path.join(DATA, "met1")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
SCR = os.path.join(HERE, "scratch")
ORG = "ecoli"
OTHERS = ["mtb", "paeruginosa", "pfalciparum", "tbrucei", "lmajor", "calbicans"]   # reference orgs' targets (leave-ecoli-out)
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
        for a in accs:
            if seqs.get(a): f.write(f">{a}\n{seqs[a]}\n")


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


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== MET1: FBA essentiality vs conservation for target-ID (E. coli) ===")
    # FBA essentiality (cached)
    ess = {}
    for ln in open(os.path.join(MET1, "essentiality.tsv")):
        p = ln.rstrip().split("\t")
        if p[0] == ORG:
            ess[p[1]] = int(p[3])
    prot = read_fasta(os.path.join(TID1, "proteomes", f"{ORG}.fasta"))
    targets = set(x.strip() for x in open(os.path.join(TID1, "targets", f"{ORG}_chembl.txt")) if x.strip())
    genes = [a for a in ess if a in prot]                    # GEM genes with a sequence
    print(f"GEM genes (with seq) {len(genes)}; FBA-essential {sum(ess[a] for a in genes)}; "
          f"drug targets in-GEM {len(set(genes) & targets)} / {len(targets)} total")
    # conservation: gene seqs vs OTHER orgs' targets
    write_fasta(prot, genes, os.path.join(SCR, "genes.fasta"))
    ot_seqs, ot_acc = {}, []
    for o in OTHERS:
        op = read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta"))
        for a in (x.strip() for x in open(os.path.join(TID1, "targets", f"{o}_chembl.txt")) if x.strip()):
            if a in op: ot_seqs[a] = op[a]; ot_acc.append(a)
    write_fasta(ot_seqs, ot_acc, os.path.join(SCR, "othertgt.fasta"))
    cons = best_bits(os.path.join(SCR, "genes.fasta"), os.path.join(SCR, "othertgt.fasta"), "cons")

    y = np.array([1 if a in targets else 0 for a in genes])
    E = np.array([ess[a] for a in genes], float)
    C = np.array([cons.get(a, 0.0) for a in genes], float)
    # H1: enrichment
    tr_ess = float(y[E == 1].mean()) if (E == 1).any() else 0.0
    tr_non = float(y[E == 0].mean()) if (E == 0).any() else 0.0
    a_, b_, c_, d_ = int(((E == 1) & (y == 1)).sum()), int(((E == 1) & (y == 0)).sum()), \
                     int(((E == 0) & (y == 1)).sum()), int(((E == 0) & (y == 0)).sum())
    odds = (a_ * d_) / max(b_ * c_, 1)
    auroc_ess = float(roc_auc_score(y, E)) if 0 < y.sum() < len(y) else float("nan")
    auroc_cons = float(roc_auc_score(y, C))
    # H2: 5-fold-CV nested ΔAUROC (cons+ess vs cons) + pooled partial coef
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    dpc, dcomb = [], []
    for tr, te in skf.split(C, y):
        for feats, store in (([C], dpc), ([C, E], dcomb)):
            Xtr = np.column_stack(feats)[tr]; Xte = np.column_stack(feats)[te]
            sc = StandardScaler().fit(Xtr)
            lr = LogisticRegression(max_iter=1000, random_state=SEED).fit(sc.transform(Xtr), y[tr])
            store.append(roc_auc_score(y[te], lr.predict_proba(sc.transform(Xte))[:, 1]))
    auroc_cv_cons = float(np.mean(dpc)); auroc_cv_comb = float(np.mean(dcomb))
    d_auroc = auroc_cv_comb - auroc_cv_cons
    Z = StandardScaler().fit_transform(np.column_stack([C, E]))
    lr = LogisticRegression(max_iter=1000, random_state=SEED).fit(Z, y)
    coef_cons, coef_ess = float(lr.coef_[0][0]), float(lr.coef_[0][1])

    summary = {"organism": ORG, "n_genes": len(genes), "n_fba_essential": int((E == 1).sum()),
               "n_drug_targets_in_gem": int(y.sum()),
               "H1_target_rate_essential": round(tr_ess, 4), "H1_target_rate_nonessential": round(tr_non, 4),
               "H1_odds_ratio": round(odds, 3), "auroc_essentiality": round(auroc_ess, 4),
               "auroc_conservation": round(auroc_cons, 4),
               "cv_auroc_conservation_only": round(auroc_cv_cons, 4),
               "cv_auroc_conservation_plus_essentiality": round(auroc_cv_comb, 4),
               "cv_delta_auroc_essentiality_adds": round(d_auroc, 4),
               "pooled_logit_coef_conservation": round(coef_cons, 4),
               "pooled_logit_coef_essentiality": round(coef_ess, 4)}
    H1 = odds > 1.5 and tr_ess > tr_non
    H2 = d_auroc > 0.02 and coef_ess > 0.1
    summary["H1_essentiality_enriches_targets"] = bool(H1)
    summary["H2_adds_beyond_conservation"] = bool(H2)
    if H2:
        summary["verdict"] = (f"H2 TRUE — CEILING BROKEN (on E. coli metabolic subproteome): FBA essentiality adds "
                              f"target-ID signal BEYOND conservation — 5-fold-CV ΔAUROC {d_auroc:+.3f} (cons {auroc_cv_cons} "
                              f"-> cons+ess {auroc_cv_comb}), partial coef {coef_ess:+.3f} vs conservation {coef_cons:+.3f}. "
                              f"The FIRST orthogonal, non-homology signal that beats the conservation ceiling. "
                              f"H1: essential genes {summary['H1_target_rate_essential']} vs non {summary['H1_target_rate_nonessential']} "
                              f"drug-target rate (OR {odds}).")
    else:
        summary["verdict"] = (f"H2 FALSE (first-class): FBA essentiality does NOT add beyond conservation (CV ΔAUROC "
                              f"{d_auroc:+.3f}, coef {coef_ess:+.3f}) — even a mechanistic, non-homology signal is largely "
                              f"captured by conservation (essential genes ARE conserved). The ceiling is DEEPER than "
                              f"homology. H1 enrichment {'holds' if H1 else 'weak'} (essential target-rate "
                              f"{summary['H1_target_rate_essential']} vs {summary['H1_target_rate_nonessential']}, OR {odds}) "
                              f"but its signal overlaps conservation. Single organism (E. coli); stated scope.")
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "gem": "iML1515"}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "MET1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({k: v for k, v in summary.items() if k != "verdict"}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "MET1_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/MET1_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
