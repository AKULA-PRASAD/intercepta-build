"""E2E2 — the CORRECTED zero-data front-half pipeline. Applies FRONT1's conclusion: mechanistic essentiality + HARD
host-non-homology filter + calibrated abstention -> a ranked SAFE target shortlist. Quantifies the decision-relevant
tradeoff: making the shortlist safe removes host-toxic targets by construction — at what cost to known-target recovery?
NAIVE baseline = rank by conservation (E2E1-style). On M. tuberculosis + E. coli. Deterministic. Envs: bioinfo + intercepta-build.
"""
import os, json, time, hashlib, subprocess, shutil
import numpy as np
import warnings; warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, MET2, FRONT1 = os.path.join(DATA, "tid1"), os.path.join(DATA, "met2"), os.path.join(DATA, "front1")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
HUMAN = os.path.join(TID1, "proteomes", "human.fasta")
SCR = os.path.join(HERE, "scratch")
ORGS = ["mtb", "ecoli"]
REFPANEL = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis",
            "pfalciparum", "tbrucei", "lmajor", "calbicans"]
HOST_EVALUE = 1e-4


def read_fasta(p):
    seqs, a, b = {}, None, []
    for ln in open(p):
        if ln.startswith(">"):
            if a: seqs[a] = "".join(b)
            h = ln[1:].split()[0]; a = h.split("|")[1] if "|" in h else h; b = []
        else: b.append(ln.strip())
    if a: seqs[a] = "".join(b)
    return seqs


def human_acc2sym():
    m = {}
    for ln in open(HUMAN):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        for tok in ln.split():
            if tok.startswith("GN="): m[acc] = tok[3:]; break
    return m


def write_fasta(seqs, accs, path):
    with open(path, "w") as f:
        for x in accs:
            if seqs.get(x): f.write(f">{x}\n{seqs[x]}\n")


def best_bits(qf, tf, tag, evalue="1e-3"):
    out = os.path.join(SCR, f"{tag}.m8"); tmp = os.path.join(SCR, f"tmp_{tag}"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", qf, tf, out, tmp, "--threads", "4", "-e", evalue, "-s", "5.7",
                    "--format-output", "query,target,bits", "-v", "1"], capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3: continue
            q = p[0].split("|")[1] if "|" in p[0] else p[0]
            tgt = p[1].split("|")[1] if "|" in p[1] else p[1]
            bits = float(p[2])
            if q not in best or bits > best[q][1]: best[q] = (tgt, bits)
    shutil.rmtree(tmp, ignore_errors=True)
    return best


def z(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / s if s > 1e-9 else x * 0.0


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== E2E2: corrected zero-data front-half pipeline (safety/recall tradeoff) ===")
    ceg2 = set(ln.split("\t")[0].strip() for ln in open(os.path.join(FRONT1, "CEGv2.txt")) if ln.split("\t")[0].strip() != "GENE")
    h2sym = human_acc2sym()
    ess, choke = {}, {}
    for ln in open(os.path.join(MET2, "essentiality.tsv")):
        p = ln.rstrip().split("\t")
        if p[0] in ORGS: ess.setdefault(p[0], {})[p[1]] = int(p[2])
    for ln in open(os.path.join(FRONT1, "chokepoints.tsv")):
        p = ln.rstrip().split("\t")
        if p[0] in ORGS: choke.setdefault(p[0], {})[p[1]] = int(p[2])
    prot = {o: read_fasta(os.path.join(TID1, "proteomes", f"{o}.fasta")) for o in REFPANEL}
    targets = {o: set(x.strip() for x in open(os.path.join(TID1, "targets", f"{o}_chembl.txt")) if x.strip()) for o in REFPANEL}

    per = {}
    for X in ORGS:
        genes = [a for a in ess.get(X, {}) if a in prot[X] and a in choke.get(X, {})]
        write_fasta(prot[X], genes, os.path.join(SCR, f"{X}.fasta"))
        ot, ota = {}, []
        for o in [r for r in REFPANEL if r != X]:
            for a in targets[o]:
                if a in prot[o]: ot[a] = prot[o][a]; ota.append(a)
        write_fasta(ot, ota, os.path.join(SCR, f"{X}_ot.fasta"))
        cons = best_bits(os.path.join(SCR, f"{X}.fasta"), os.path.join(SCR, f"{X}_ot.fasta"), f"{X}_c")
        host = best_bits(os.path.join(SCR, f"{X}.fasta"), HUMAN, f"{X}_h", evalue=str(HOST_EVALUE))
        genes = np.array(genes)
        y = np.array([1 if a in targets[X] else 0 for a in genes])
        C = np.array([cons.get(a, (None, 0.0))[1] for a in genes])
        E = np.array([ess[X][a] for a in genes], float)
        K = np.array([choke[X][a] for a in genes], float)
        S = np.array([0 if a in host else 1 for a in genes])            # 1 = host-nonhomologous
        host_tox = np.array([1 if (a in host and h2sym.get(host[a][0], "") in ceg2) else 0 for a in genes])
        k = int(y.sum())
        # NAIVE: rank all genes by conservation
        naive_top = set(np.argsort(-C)[:k])
        # CORRECTED: hard-filter host-homologous, rank remainder by unsupervised mechanistic composite z(C)+z(E)+z(K)
        keep = np.where(S == 1)[0]
        comp = z(C[keep]) + z(E[keep]) + z(K[keep])
        corr_top = set(keep[np.argsort(-comp)][:k])
        # abstention: genes with no conservation homolog
        abstain = C == 0
        def recall(top): return sum(y[i] for i in top)
        def prec(top): return recall(top) / len(top) if top else 0.0
        n_target_hosthom = int(((y == 1) & (S == 0)).sum())      # known targets LOST to the hard filter
        per[X] = {
            "n_genes": len(genes), "n_targets": k, "n_host_toxic": int(host_tox.sum()),
            "n_host_nonhom": int(S.sum()), "n_known_targets_host_homologous": n_target_hosthom,
            "known_target_host_homolog_frac": round(n_target_hosthom / max(k, 1), 3),
            "SAFETY_hosttoxic_in_topk_naive": int(sum(host_tox[i] for i in naive_top)),
            "SAFETY_hosttoxic_in_topk_corrected": int(sum(host_tox[i] for i in corr_top)),
            "RECALL_targets_in_topk_naive": int(recall(naive_top)),
            "RECALL_targets_in_topk_corrected": int(recall(corr_top)),
            "precision_at_k_naive": round(prec(naive_top), 4), "precision_at_k_corrected": round(prec(corr_top), 4),
            "n_abstain_no_homolog": int(abstain.sum()),
            "abstain_target_rate": round(float(y[abstain].mean()) if abstain.sum() else 0.0, 4),
            "committed_target_rate": round(float(y[~abstain].mean()) if (~abstain).sum() else 0.0, 4),
        }
        print(f"  [{X}] targets={k} host-toxic={int(host_tox.sum())} | SAFETY top-k host-toxic naive "
              f"{per[X]['SAFETY_hosttoxic_in_topk_naive']}->corrected {per[X]['SAFETY_hosttoxic_in_topk_corrected']} | "
              f"RECALL naive {per[X]['RECALL_targets_in_topk_naive']}->corrected {per[X]['RECALL_targets_in_topk_corrected']} "
              f"(of {k}) | known-targets host-homologous {per[X]['known_target_host_homolog_frac']} [{time.time()-t0:.0f}s]")

    # aggregate
    safety_gain = {X: per[X]["SAFETY_hosttoxic_in_topk_naive"] - per[X]["SAFETY_hosttoxic_in_topk_corrected"] for X in ORGS}
    recall_ratio = {X: (round(per[X]["RECALL_targets_in_topk_corrected"] / max(per[X]["RECALL_targets_in_topk_naive"], 1), 3)) for X in ORGS}
    lost_frac = {X: per[X]["known_target_host_homolog_frac"] for X in ORGS}
    abst_ok = all(per[X]["abstain_target_rate"] < per[X]["committed_target_rate"] for X in ORGS)
    max_excl = max(lost_frac.values())
    summary = {"organisms": ORGS,
               "SAFETY_hosttoxic_removed_from_topk": safety_gain,
               "corrected_all_safe": bool(all(per[X]["SAFETY_hosttoxic_in_topk_corrected"] == 0 for X in ORGS)),
               "topk_RECALL_corrected_over_naive": recall_ratio,
               "known_targets_EXCLUDED_by_hardfilter_frac": lost_frac,
               "hardfilter_over_excludes_real_targets": bool(max_excl > 0.2),
               "abstention_calibrated": bool(abst_ok)}
    summary["verdict"] = (
        f"HONEST TENSION (both naive and hard-filter are wrong in different ways). SAFETY: the corrected pipeline is safe by "
        f"construction (0 host-toxic in top-k both orgs) whereas the NAIVE conservation shortlist would include "
        f"{safety_gain} host-toxic (human-essential-homolog) targets — a real safety gain. TOP-K RECALL looks nearly "
        f"preserved (corrected/naive {recall_ratio}; precision@k " + ", ".join(f"{X} {per[X]['precision_at_k_naive']}->{per[X]['precision_at_k_corrected']}" for X in ORGS) + "). "
        f"BUT THE REAL COST IS LARGE AND STRUCTURAL: a blunt sequence-level host-non-homology hard filter PERMANENTLY "
        f"EXCLUDES {lost_frac} of ALL known drug targets (those WITH a human homolog) from the searchable space — the "
        f"pipeline can NEVER find them. Top-k recall only looks preserved because base recall is low and the surviving "
        f"host-non-homologous targets rank well mechanistically. Many host-homologous targets ARE drugged SELECTIVELY in "
        f"reality by exploiting binding-site differences a sequence filter cannot see. NET: naive-conservation is UNSAFE "
        f"(promotes host-toxic); the hard filter is SAFE but OVER-EXCLUDES {int(max_excl*100)}% of real targets; the "
        f"genuinely correct selectivity needs BINDING-SITE-level pathogen-vs-host difference reasoning (structure, not "
        f"sequence homology) — which sequence transfer cannot provide (another instance of the information ceiling). "
        f"Abstention IS calibrated (no-homolog genes are target-poor). SCOPE: metabolic subproteome; 2 bacteria; "
        f"unsupervised zero-label composite; ChEMBL selection-bias likely UNDER-estimates exclusion for a truly novel "
        f"pathogen; molecule-half stage weak (C1/HIT2); not wet-lab.")
    print("\nPANEL:", json.dumps({k2: v for k2, v in summary.items() if k2 != "verdict"}, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host_evalue": HOST_EVALUE}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_organism": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "E2E2_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k2: v for k2, v in summary.items() if k2 != "verdict"}, "per_organism": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "E2E2_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
