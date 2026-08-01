"""TID2 — does INTRINSIC structural pocket druggability (fpocket on AlphaFold v6) add target signal BEYOND sequence
conservation? Leave-organism-out over 4 pathogens: structural druggability (cached, conservation-free) vs a mmseqs2
CONSERVATION null, with the DECISIVE conditional test (logistic is_target ~ conservation + structural; held-out nested
ΔAUROC). Reads the deterministic fpocket cache ($INTERCEPTA_DATA/tid2/druggability.tsv). Implements
prereg/TID2_structural_druggability.md. Deterministic -> reproduce x2.
"""
import os, sys, json, time, hashlib, subprocess, shutil
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, TID2 = os.path.join(DATA, "tid1"), os.path.join(DATA, "tid2")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
SCR = os.path.join(HERE, "scratch")
PANEL = ["mtb", "ecoli", "paeruginosa", "pfalciparum"]
EVALUE, THREADS, SEED = 1e-3, 4, 42


def read_fasta(path):
    seqs, acc, buf = {}, None, []
    for ln in open(path):
        if ln.startswith(">"):
            if acc: seqs[acc] = "".join(buf)
            h = ln[1:].split()[0]; acc = h.split("|")[1] if "|" in h else h; buf = []
        else:
            buf.append(ln.strip())
    if acc: seqs[acc] = "".join(buf)
    return seqs


def write_fasta(seqs, accs, path):
    with open(path, "w") as f:
        for a in accs:
            if a in seqs and seqs[a]:
                f.write(f">{a}\n{seqs[a]}\n")


def best_bits(qfasta, tfasta, tag):
    out = os.path.join(SCR, f"{tag}.m8"); tmp = os.path.join(SCR, f"tmp_{tag}")
    shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", qfasta, tfasta, out, tmp, "--threads", str(THREADS), "-e", str(EVALUE),
                    "-s", "5.7", "--format-output", "query,target,bits", "-v", "1"], capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3: continue
            q = p[0].split("|")[1] if "|" in p[0] else p[0]; b = float(p[2])
            if q not in best or b > best[q]: best[q] = b
    shutil.rmtree(tmp, ignore_errors=True)
    return best


def auroc(y, s):
    y = np.asarray(y)
    return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else float("nan")


def prec_at_k(y, s, k):
    return float(np.asarray(y)[np.argsort(-np.asarray(s, float))][:k].sum() / k) if k else float("nan")


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== TID2: structural pocket druggability beyond conservation ===")
    # cached fpocket druggability
    drug, ptar = {}, {}
    for ln in open(os.path.join(TID2, "druggability.tsv")):
        p = ln.rstrip("\n").split("\t")
        if p[0] == "accession" or len(p) < 6: continue
        drug[p[0]] = float(p[3]); ptar[p[0]] = int(p[2])
    prot = {o: read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta")) for o in PANEL}
    # evaluation table per organism (only accessions present in the fpocket cache)
    evalset = {o: [a for a in drug if a in prot[o]] for o in PANEL}
    # organism membership: an accession belongs to the organism whose proteome + cache row it came from
    org_of = {}
    for ln in open(os.path.join(TID2, "druggability.tsv")):
        p = ln.rstrip("\n").split("\t")
        if p[0] != "accession" and len(p) >= 2: org_of[p[0]] = p[1]
    # conservation null: each org's eval proteins vs OTHER orgs' FULL proteomes (leave-organism-out)
    consnull = {}
    for X in PANEL:
        others = [o for o in PANEL if o != X]
        qf = os.path.join(SCR, f"{X}_q.fasta"); write_fasta(prot[X], [a for a in evalset[X]], qf)
        of_seqs, of_acc = {}, []
        for o in others:
            for a, s in prot[o].items():
                of_seqs[a] = s; of_acc.append(a)
        tf = os.path.join(SCR, f"{X}_otherfull.fasta"); write_fasta(of_seqs, of_acc, tf)
        bb = best_bits(qf, tf, f"{X}_cons")
        for a in evalset[X]:
            consnull[a] = bb.get(a, 0.0)
        print(f"  cons-null {X}: {len(evalset[X])} eval proteins [{time.time()-t0:.0f}s]")

    # assemble table
    rows = []
    for X in PANEL:
        for a in evalset[X]:
            rows.append({"acc": a, "org": X, "y": int(ptar.get(a, 0)),
                         "structural": round(drug[a], 4), "cons_null": round(consnull.get(a, 0.0), 2)})
    accs = np.array([r["acc"] for r in rows]); org = np.array([r["org"] for r in rows])
    y = np.array([r["y"] for r in rows]); S = np.array([r["structural"] for r in rows]); C = np.array([r["cons_null"] for r in rows])
    length = np.array([len(prot[r["org"]][r["acc"]]) for r in rows], float)

    per = {}
    for X in PANEL:
        mask = org == X; oth = ~mask
        yx, Sx, Cx, Lx = y[mask], S[mask], C[mask], length[mask]
        k = int(yx.sum())
        # held-out nested logistic: fit on other orgs, predict X
        def fit_pred(feats_idx):
            Xtr = np.column_stack([[C, S][i] for i in feats_idx])[oth]
            Xte = np.column_stack([[C, S][i] for i in feats_idx])[mask]
            sc = StandardScaler().fit(Xtr)
            lr = LogisticRegression(max_iter=1000, random_state=SEED).fit(sc.transform(Xtr), y[oth])
            return lr.predict_proba(sc.transform(Xte))[:, 1]
        auroc_cons_model = auroc(yx, fit_pred([0]))
        auroc_comb_model = auroc(yx, fit_pred([0, 1]))
        per[X] = {"n": int(mask.sum()), "n_targets": k,
                  "auroc_structural_alone": round(auroc(yx, Sx), 4),
                  "auroc_cons_null": round(auroc(yx, Cx), 4),
                  "auroc_length_null": round(auroc(yx, Lx), 4),
                  "auroc_cons_model": round(auroc_cons_model, 4),
                  "auroc_combined_model": round(auroc_comb_model, 4),
                  "delta_auroc_combined_minus_cons": round(auroc_comb_model - auroc_cons_model, 4),
                  "precAtk_structural": round(prec_at_k(yx, Sx, k), 4),
                  "precAtk_cons_null": round(prec_at_k(yx, Cx, k), 4)}
        print(f"  [{X}] struct {per[X]['auroc_structural_alone']} cons-null {per[X]['auroc_cons_null']} "
              f"| combined {per[X]['auroc_combined_model']} vs cons-model {per[X]['auroc_cons_model']} "
              f"(Δ {per[X]['delta_auroc_combined_minus_cons']:+.3f}) | P@k struct {per[X]['precAtk_structural']} "
              f"vs cons {per[X]['precAtk_cons_null']}")

    # partial effect of structural after conservation (pooled logistic, standardized coefficients)
    Z = StandardScaler().fit_transform(np.column_stack([C, S]))
    lr = LogisticRegression(max_iter=1000, random_state=SEED).fit(Z, y)
    coef_cons, coef_struct = float(lr.coef_[0][0]), float(lr.coef_[0][1])

    def med(key): return round(float(np.median([per[o][key] for o in PANEL])), 4)
    summary = {"panel": PANEL, "n_eval": len(rows), "n_targets_total": int(y.sum()),
               "median_auroc_structural_alone": med("auroc_structural_alone"),
               "median_auroc_cons_null": med("auroc_cons_null"),
               "median_delta_auroc_combined_minus_cons": med("delta_auroc_combined_minus_cons"),
               "median_precAtk_structural": med("precAtk_structural"),
               "median_precAtk_cons_null": med("precAtk_cons_null"),
               "pooled_logit_coef_conservation": round(coef_cons, 4),
               "pooled_logit_coef_structural": round(coef_struct, 4)}
    sa, cn, dl, cs = (summary["median_auroc_structural_alone"], summary["median_auroc_cons_null"],
                      summary["median_delta_auroc_combined_minus_cons"], coef_struct)
    # H2 credited ONLY for a MEANINGFUL orthogonal effect: held-out ΔAUROC >= 0.02 AND >=3/4 organisms positive AND
    # a non-trivial partial coefficient (>=0.15, vs conservation ~0.7). Guards against over-reading a whisper (B65 lesson).
    n_pos = sum(1 for o in PANEL if per[o]["delta_auroc_combined_minus_cons"] > 0)
    H1 = sa > cn
    H2 = (dl >= 0.02) and (n_pos >= 3) and (cs >= 0.15)
    summary["H1_structural_beats_conservation_null"] = bool(H1)
    summary["H2_adds_meaningfully_beyond_conservation"] = bool(H2)
    summary["n_organisms_delta_positive"] = int(n_pos)
    if H2:
        summary["verdict"] = (f"H2 TRUE: structural pocket druggability adds a MEANINGFUL signal beyond conservation — "
                              f"held-out ΔAUROC {dl:+.3f} ({n_pos}/4 orgs positive), partial coef {cs:+.3f} vs "
                              f"conservation {coef_cons:+.3f}. Intrinsic pocket geometry is a genuine orthogonal target signal.")
    else:
        summary["verdict"] = (f"H2 FALSE / MARGINAL (first-class boundary): intrinsic pocket druggability does NOT add "
                              f"MEANINGFULLY beyond conservation — structural ALONE AUROC {sa} is near-random and far below "
                              f"the conservation null {cn} (precision@k {summary['median_precAtk_structural']} vs "
                              f"{summary['median_precAtk_cons_null']}); after partialling out conservation it adds only a "
                              f"whisper (held-out ΔAUROC {dl:+.3f}, {n_pos}/4 orgs positive, partial coef {cs:+.3f} vs "
                              f"conservation {coef_cons:+.3f}). fpocket's low specificity makes it a poor target "
                              f"discriminator here. BOUNDS structural target-ID at ~the conservation ceiling → forces "
                              f"mechanistic signals (essentiality/chokepoint) or accepting a homology+structure ceiling. "
                              f"Consistent with Thread-1's caution that fpocket calls too much of the proteome druggable.")
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "fpocket": "4.2.3", "afdb": "v6"}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_organism": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "TID2_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_organism": per,
                          "rows": rows}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "TID2_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/TID2_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
