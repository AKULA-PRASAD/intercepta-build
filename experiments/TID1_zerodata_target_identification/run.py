"""TID1 — Zero-data target identification by leave-organism-out homology transfer (druggability), on a minimal living
substrate. For each held-out pathogen X, transfer druggability from the OTHER panel organisms' known drug targets
(UniProt ChEMBL xref) via mmseqs2 homology, subtract human homology for selectivity, abstain where no homolog, and
measure recovery of X's OWN drug targets vs THREE nulls (random, a CONSERVATION null = homology to other organisms' full
proteomes, and human-homolog-only). Implements prereg/TID1_zerodata_target_identification.md (+ 2026-07-31 amendment).
Analysis in intercepta-build; homology via the isolated `bioinfo` mmseqs2. Deterministic -> reproduce x2.
"""
import os, sys, json, time, hashlib, subprocess, shutil, glob
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data"), "tid1")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
SCR = os.path.join(HERE, "scratch");
PANEL = ["mtb", "ecoli", "paeruginosa", "pfalciparum"]      # powered (leave-one-out); sarscov2 = qualitative only
EVALUE, THREADS, SEED = 1e-3, 4, 42


def read_fasta(path):
    seqs, acc, buf = {}, None, []
    for ln in open(path):
        if ln.startswith(">"):
            if acc:
                seqs[acc] = "".join(buf)
            h = ln[1:].split()[0]
            acc = h.split("|")[1] if "|" in h else h
            buf = []
        else:
            buf.append(ln.strip())
    if acc:
        seqs[acc] = "".join(buf)
    return seqs


def write_fasta(seqs, accs, path):
    with open(path, "w") as f:
        for a in accs:
            if a in seqs:
                f.write(f">{a}\n{seqs[a]}\n")


def best_bits(qfasta, tfasta, tag):
    """mmseqs2 easy-search; return {query_acc: best_bitscore} (deterministic: max over hits)."""
    out = os.path.join(SCR, f"{tag}.m8"); tmp = os.path.join(SCR, f"tmp_{tag}")
    if os.path.exists(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    cmd = [MMSEQS, "easy-search", qfasta, tfasta, out, tmp, "--threads", str(THREADS), "-e", str(EVALUE),
           "-s", "5.7", "--format-output", "query,target,pident,evalue,bits", "-v", "1"]
    subprocess.run(cmd, capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            q, b = p[0].split("|")[1] if "|" in p[0] else p[0], float(p[4])
            if q not in best or b > best[q]:
                best[q] = b
    shutil.rmtree(tmp, ignore_errors=True)
    return best


def auroc(y, s):
    y = np.asarray(y)
    if y.sum() == 0 or y.sum() == len(y):
        return float("nan")
    return float(roc_auc_score(y, s))


def prec_at_k(y, s, k):
    order = np.argsort(-np.asarray(s, float)); yk = np.asarray(y)[order][:k]
    return float(yk.sum() / k)


def main():
    t0 = time.time()
    if os.path.exists(SCR):
        shutil.rmtree(SCR, ignore_errors=True)
    os.makedirs(SCR, exist_ok=True)
    print("=== TID1: zero-data target ID by leave-organism-out druggability transfer ===")
    prot = {o: read_fasta(os.path.join(DATA, "proteomes", f"{o}.fasta")) for o in PANEL}
    human = read_fasta(os.path.join(DATA, "proteomes", "human.fasta"))
    targets = {o: set(x.strip() for x in open(os.path.join(DATA, "targets", f"{o}_chembl.txt")) if x.strip())
               for o in PANEL}
    targets = {o: (targets[o] & set(prot[o])) for o in PANEL}                    # keep only in-proteome
    for o in PANEL:
        print(f"  {o}: proteome={len(prot[o])} targets={len(targets[o])}")
    write_fasta(human, list(human), os.path.join(SCR, "human.fasta"))

    per, records = {}, []
    for X in PANEL:
        others = [o for o in PANEL if o != X]
        # reference DBs (leave-organism-out): other orgs' TARGET proteins, and other orgs' FULL proteomes
        ot_acc, of_acc = [], []
        merged_seqs = {}
        for o in others:
            for a in targets[o]:
                ot_acc.append(a); merged_seqs[a] = prot[o][a]
            for a, s in prot[o].items():
                of_acc.append(a); merged_seqs[a] = s
        Xf = os.path.join(SCR, f"{X}.fasta"); write_fasta(prot[X], list(prot[X]), Xf)
        otf = os.path.join(SCR, f"{X}_othertgt.fasta"); write_fasta(merged_seqs, ot_acc, otf)
        off = os.path.join(SCR, f"{X}_otherfull.fasta"); write_fasta(merged_seqs, of_acc, off)
        drug = best_bits(Xf, otf, f"{X}_drug")            # druggability transfer (target homology)
        cons = best_bits(Xf, off, f"{X}_cons")            # CONSERVATION null (any-protein homology)
        hum = best_bits(Xf, os.path.join(SCR, "human.fasta"), f"{X}_hum")   # human homology (selectivity)
        acc = list(prot[X])
        y = np.array([1 if a in targets[X] else 0 for a in acc])
        sd = np.array([drug.get(a, 0.0) for a in acc])
        sc = np.array([cons.get(a, 0.0) for a in acc])
        sh = np.array([hum.get(a, 0.0) for a in acc])
        length = np.array([len(prot[X][a]) for a in acc], float)
        armA = sd                                          # druggability
        armB = sd - sh                                     # + human-subtraction (selectivity)
        rng = np.random.default_rng(SEED); rand = rng.permutation(len(acc)).astype(float)
        abst = sd <= 0.0                                   # no target homolog -> abstain
        k = int(y.sum())
        m = {"n_proteins": len(acc), "n_targets": int(y.sum()),
             "auroc_armA_druggability": round(auroc(y, armA), 4),
             "auroc_armB_human_subtracted": round(auroc(y, armB), 4),
             "auroc_conservation_null": round(auroc(y, sc), 4),
             "auroc_length_null": round(auroc(y, length), 4),
             "auroc_human_only_null": round(auroc(y, sh), 4),
             "auroc_random_null": round(auroc(y, rand), 4),
             "precAtk_armA": round(prec_at_k(y, armA, k), 4),
             "precAtk_conservation_null": round(prec_at_k(y, sc, k), 4),
             "precAtk_armB": round(prec_at_k(y, armB, k), 4),
             "abstain_rate": round(float(abst.mean()), 4),
             "target_rate_predicted": round(float(y[~abst].mean()) if (~abst).sum() else 0.0, 4),
             "target_rate_abstained": round(float(y[abst].mean()) if abst.sum() else 0.0, 4)}
        per[X] = m
        print(f"  [{X}] armA {m['auroc_armA_druggability']} armB {m['auroc_armB_human_subtracted']} "
              f"| cons-null {m['auroc_conservation_null']} len-null {m['auroc_length_null']} "
              f"| P@k armA {m['precAtk_armA']} vs cons {m['precAtk_conservation_null']} "
              f"| abstain {m['abstain_rate']} [{time.time()-t0:.0f}s]")
        # LIVING SUBSTRATE: provenance/confidence-tiered records for the top predicted targets (demo the loop)
        order = np.argsort(-armA)
        for i in order[:15]:
            a = acc[i]
            tier = "high" if sd[i] >= 100 else ("medium" if sd[i] >= 50 else "low")
            records.append({"organism": X, "protein": a, "druggability_bits": round(float(sd[i]), 1),
                            "human_homology_bits": round(float(sh[i]), 1), "confidence_tier": tier,
                            "abstained": bool(abst[i]), "is_known_target": bool(y[i])})

    def med(key):
        return round(float(np.median([per[o][key] for o in PANEL])), 4)
    summary = {
        "panel": PANEL, "n_organisms": len(PANEL),
        "median_auroc_armA_druggability": med("auroc_armA_druggability"),
        "median_auroc_armB_human_subtracted": med("auroc_armB_human_subtracted"),
        "median_auroc_conservation_null": med("auroc_conservation_null"),
        "median_auroc_length_null": med("auroc_length_null"),
        "median_precAtk_armA": med("precAtk_armA"),
        "median_precAtk_conservation_null": med("precAtk_conservation_null"),
        "median_abstain_rate": med("abstain_rate"),
    }
    a, c = summary["median_auroc_armA_druggability"], summary["median_auroc_conservation_null"]
    H1 = a > 0.55 and a > c + 0.03
    H3 = med("precAtk_armB") >= med("precAtk_armA")
    H4 = np.median([per[o]["target_rate_predicted"] - per[o]["target_rate_abstained"] for o in PANEL]) > 0
    summary["H1_target_specific_transfer"] = bool(H1)
    summary["H3_human_subtraction_helps_precision"] = bool(H3)
    summary["H4_abstention_calibrated"] = bool(H4)
    if H1:
        summary["verdict"] = (f"H1 TRUE: druggability transfers zero-data across organisms — leave-organism-out AUROC "
                              f"{a} recovers known drug targets ABOVE the conservation null {c} (target-specific, not "
                              f"just conservation). Abstention {'calibrated' if H4 else 'not calibrated'}; "
                              f"human-subtraction {'helps' if H3 else 'neutral'} precision. First front-half capability "
                              f"shows real zero-data signal on the proving ground.")
    else:
        summary["verdict"] = (f"H1 FALSE/weak (first-class): druggability transfer AUROC {a} is not clearly above the "
                              f"conservation null {c} — homology-to-targets is largely generic conservation here; "
                              f"forces structure/mechanistic capabilities earlier. Honest boundary on homology-only "
                              f"target-ID.")
    print("\nPANEL:", json.dumps(summary, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "mmseqs": "18", "evalue": EVALUE}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_organism": per, "substrate_records_sample": records, "provenance": prov,
           "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "TID1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"},
                          "per_organism": per, "records": records}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "TID1_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest); print("wrote results/TID1_metrics.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
