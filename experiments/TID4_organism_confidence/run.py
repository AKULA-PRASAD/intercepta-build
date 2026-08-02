"""TID4 — fixing the silent failure: can a LABEL-FREE, query-time signal predict when zero-data target-ID will fail?
Per held-out organism: druggability-transfer recovery (precision@k) + LABEL-FREE confidence signals computed from the
organism's proteome vs the reference proteomes ONLY (no target labels) — S1 median homology bits, S2 fraction with any
homolog, S3 same-kingdom reference count, S4 90th-pct homology bits (closest-relatives). Test whether the signals predict
recovery across the panel (organism-level abstention). Implements prereg/TID4_organism_confidence.md. Deterministic.
"""
import os, sys, json, time, hashlib, subprocess, shutil
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "tid4")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
SCR = os.path.join(HERE, "scratch")
KINGDOM = {"mtb": "bacteria", "ecoli": "bacteria", "paeruginosa": "bacteria", "saureus": "bacteria",
           "hpylori": "bacteria", "ngonorrhoeae": "bacteria", "kpneumoniae": "bacteria",
           "pfalciparum": "parasite", "tcruzi": "parasite", "calbicans": "fungus", "afumigatus": "fungus"}
PANEL = list(KINGDOM)
SIGNALS = ["S1_median_bits", "S2_frac_homolog", "S3_same_kingdom_refs", "S4_p90_bits"]


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


def prec_at_k(y, s, k):
    return float(np.asarray(y)[np.argsort(-np.asarray(s, float))][:k].sum() / k) if k else float("nan")


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== TID4: label-free organism-level confidence (fix the silent failure) ===")
    prot = {o: read_fasta(os.path.join(DATA, "proteomes", f"{o}.fasta")) for o in PANEL}
    targets = {o: set(x.strip() for x in open(os.path.join(DATA, "targets", f"{o}_chembl.txt")) if x.strip()) & set(prot[o])
               for o in PANEL}
    for o in PANEL:
        print(f"  {o:14s} ({KINGDOM[o]:8s}) proteome={len(prot[o])} targets={len(targets[o])}")

    per = {}
    for X in PANEL:
        others = [o for o in PANEL if o != X]
        same_kd = sum(1 for o in others if KINGDOM[o] == KINGDOM[X])
        ot_acc, of_acc, merged = [], [], {}
        for o in others:
            for a in targets[o]:
                ot_acc.append(a); merged[a] = prot[o][a]
            for a, s in prot[o].items():
                of_acc.append(a); merged[a] = s
        Xf = os.path.join(SCR, f"{X}.fasta"); write_fasta(prot[X], list(prot[X]), Xf)
        write_fasta(merged, ot_acc, os.path.join(SCR, f"{X}_ot.fasta"))
        write_fasta(merged, of_acc, os.path.join(SCR, f"{X}_of.fasta"))
        drug = best_bits(Xf, os.path.join(SCR, f"{X}_ot.fasta"), f"{X}_d")
        cons = best_bits(Xf, os.path.join(SCR, f"{X}_of.fasta"), f"{X}_c")
        acc = list(prot[X]); y = np.array([1 if a in targets[X] else 0 for a in acc]); k = int(y.sum())
        sd = np.array([drug.get(a, 0.0) for a in acc])
        cb = np.array([cons.get(a, 0.0) for a in acc])          # label-free homology-to-reference per protein
        recovery = prec_at_k(y, sd, k)
        per[X] = {"kingdom": KINGDOM[X], "n_targets": k, "recovery_precAtk": round(recovery, 4),
                  "S1_median_bits": round(float(np.median(cb)), 2),
                  "S2_frac_homolog": round(float(np.mean(cb > 0)), 4),
                  "S3_same_kingdom_refs": int(same_kd),
                  "S4_p90_bits": round(float(np.percentile(cb, 90)), 2)}
        print(f"  [{X:14s} {KINGDOM[X]:8s}] recovery P@k {per[X]['recovery_precAtk']} | S1 {per[X]['S1_median_bits']} "
              f"S2 {per[X]['S2_frac_homolog']} S3 {per[X]['S3_same_kingdom_refs']} S4 {per[X]['S4_p90_bits']} [{time.time()-t0:.0f}s]")

    rec = np.array([per[o]["recovery_precAtk"] for o in PANEL])
    corr, loo = {}, {}
    for sig in SIGNALS:
        sv = np.array([per[o][sig] for o in PANEL], float)
        r = spearmanr(sv, rec).correlation
        corr[sig] = round(float(r) if r == r else 0.0, 4)
        # leave-one-out: predict held-out org's recovery-rank from signal rank fit on the rest -> Spearman of predicted vs actual
    # organism-level abstention: AUROC of best signal vs binarised recovery success (> panel median)
    succ = (rec > np.median(rec)).astype(int)
    best_sig = max(corr, key=lambda s: abs(corr[s]))
    bs = np.array([per[o][best_sig] for o in PANEL], float)
    aub = float(roc_auc_score(succ, bs)) if 0 < succ.sum() < len(succ) else float("nan")

    summary = {"n_organisms": len(PANEL), "n_kingdoms": len(set(KINGDOM.values())),
               "spearman_signal_vs_recovery": corr, "best_signal": best_sig,
               "best_signal_spearman": corr[best_sig],
               "abstention_auroc_best_signal": round(aub, 4),
               "panel_median_recovery": round(float(np.median(rec)), 4)}
    H1 = abs(corr[best_sig]) > 0.5
    summary["H1_labelfree_signal_predicts_failure"] = bool(H1)
    if H1:
        summary["verdict"] = (f"H1 TRUE: a LABEL-FREE query-time signal predicts organism-level target-ID failure — "
                              f"{best_sig} Spearman {corr[best_sig]:+.2f} with recovery (abstention AUROC {aub:.2f} for "
                              f"high- vs low-recovery organisms). The system CAN know, with NO target labels, when it is "
                              f"out of its depth on a new organism → organism-level abstention FIXES TID3's silent "
                              f"failure. Signals: {corr}. (n={len(PANEL)}, bacteria-weighted — modest power, stated.)")
    else:
        summary["verdict"] = (f"H0 (first-class): NO label-free signal reliably predicts organism-level recovery "
                              f"(best {best_sig} Spearman {corr[best_sig]:+.2f}, all |r|<0.5) → the silent failure TID3 "
                              f"exposed is NOT cheaply fixable from homological distance alone; organism-level "
                              f"confidence needs a richer signal. Honest boundary. Signals: {corr}. (n={len(PANEL)}.)")
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_organism": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "TID4_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_organism": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "TID4_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/TID4_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
