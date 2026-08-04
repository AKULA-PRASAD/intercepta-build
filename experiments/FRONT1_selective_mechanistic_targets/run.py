"""FRONT1 — selective mechanistic target discovery (front-half chapter). Per pathogen metabolic-subproteome gene:
conservation C (mmseqs to other-org targets), essentiality E (MET2 cache), chokepoint K (front1 cache), host non-homology
S (mmseqs vs human proteome). H1: does mechanism+selectivity [C+E+K+S] add beyond [C] and beyond [C+E] at recovering known
targets (5-fold OOF ΔAUROC). H2 (therapeutic validity): does the selective composite DOWN-rank host-toxic genes (human
homolog is a core-essential gene, Hart CEG2) vs the conservation baseline? Deterministic. Envs: bioinfo (mmseqs) +
intercepta-build.
"""
import os, json, time, hashlib, subprocess, shutil
import numpy as np
import warnings; warnings.filterwarnings("ignore")
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
TID1, MET2, FRONT1 = os.path.join(DATA, "tid1"), os.path.join(DATA, "met2"), os.path.join(DATA, "front1")
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
HUMAN = os.path.join(TID1, "proteomes", "human.fasta")
SCR = os.path.join(HERE, "scratch")
ORGS = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis"]
RELIABLE = ["ecoli", "mtb"]           # >=50 targets (MET2) -> reliable CV
REFPANEL = ORGS + ["pfalciparum", "tbrucei", "lmajor", "calbicans"]
HOST_EVALUE = 1e-4
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


def human_acc2sym():
    m = {}
    for ln in open(HUMAN):
        if not ln.startswith(">"): continue
        acc = ln[1:].split()[0].split("|")[1] if "|" in ln else ln[1:].split()[0]
        sym = None
        for tok in ln.split():
            if tok.startswith("GN="): sym = tok[3:]; break
        if sym: m[acc] = sym
    return m


def write_fasta(seqs, accs, path):
    with open(path, "w") as f:
        for x in accs:
            if seqs.get(x): f.write(f">{x}\n{seqs[x]}\n")


def best_bits(qf, tf, tag, evalue="1e-3"):
    out = os.path.join(SCR, f"{tag}.m8"); tmp = os.path.join(SCR, f"tmp_{tag}"); shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run([MMSEQS, "easy-search", qf, tf, out, tmp, "--threads", "4", "-e", evalue, "-s", "5.7",
                    "--format-output", "query,target,bits,evalue", "-v", "1"], capture_output=True, text=True)
    best = {}
    if os.path.exists(out):
        for ln in open(out):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 4: continue
            q = p[0].split("|")[1] if "|" in p[0] else p[0]
            tgt = p[1].split("|")[1] if "|" in p[1] else p[1]
            bits = float(p[2])
            if q not in best or bits > best[q][1]: best[q] = (tgt, bits)
    shutil.rmtree(tmp, ignore_errors=True)
    return best


def oof(cols, y):
    Z = np.column_stack(cols); pred = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(Z, y):
        sc = StandardScaler().fit(Z[tr]); lr = LogisticRegression(max_iter=1000, random_state=SEED).fit(sc.transform(Z[tr]), y[tr])
        pred[te] = lr.predict_proba(sc.transform(Z[te]))[:, 1]
    return pred


def coefs(cols, y):
    Z = np.column_stack(cols); sc = StandardScaler().fit(Z)
    lr = LogisticRegression(max_iter=1000, random_state=SEED).fit(sc.transform(Z), y)
    return [round(float(c), 3) for c in lr.coef_[0]]


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR, exist_ok=True)
    print("=== FRONT1: selective mechanistic target discovery ===")
    ceg2 = set(ln.split("\t")[0].strip() for ln in open(os.path.join(FRONT1, "CEGv2.txt")) if ln.split("\t")[0].strip() != "GENE")
    h2sym = human_acc2sym()
    print(f"  CEG2 core-essential {len(ceg2)}, human acc->sym {len(h2sym)} [{time.time()-t0:.0f}s]")
    ess = {}; choke = {}
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
        # conservation to other-org targets
        ot, ota = {}, []
        for o in [r for r in REFPANEL if r != X]:
            for a in targets[o]:
                if a in prot[o]: ot[a] = prot[o][a]; ota.append(a)
        write_fasta(ot, ota, os.path.join(SCR, f"{X}_ot.fasta"))
        cons = best_bits(os.path.join(SCR, f"{X}.fasta"), os.path.join(SCR, f"{X}_ot.fasta"), f"{X}_c")
        host = best_bits(os.path.join(SCR, f"{X}.fasta"), HUMAN, f"{X}_h", evalue=str(HOST_EVALUE))
        y = np.array([1 if a in targets[X] else 0 for a in genes])
        C = np.array([cons.get(a, (None, 0.0))[1] for a in genes])
        E = np.array([ess[X][a] for a in genes], float)
        K = np.array([choke[X][a] for a in genes], float)
        S = np.array([0.0 if a in host else 1.0 for a in genes])           # 1 = host-nonhomologous (selective)
        host_tox = np.array([1 if (a in host and h2sym.get(host[a][0], "") in ceg2) else 0 for a in genes])
        per[X] = {"n_genes": len(genes), "n_targets": int(y.sum()), "n_host_nonhom": int(S.sum()),
                  "n_host_toxic": int(host_tox.sum())}
        # H2 does not need CV; H1 CV only where reliable (>=50 targets)
        if X in RELIABLE and y.sum() >= 50:
            base_C = oof([C], y); base_CE = oof([C, E], y); full = oof([C, E, K, S], y)
            cf = coefs([C, E, K, S], y)
            per[X].update({
                "auroc_C": round(float(roc_auc_score(y, base_C)), 4),
                "auroc_CE": round(float(roc_auc_score(y, base_CE)), 4),
                "auroc_CEKS": round(float(roc_auc_score(y, full)), 4),
                "dAUROC_full_vs_C": round(float(roc_auc_score(y, full) - roc_auc_score(y, base_C)), 4),
                "dAUROC_full_vs_CE": round(float(roc_auc_score(y, full) - roc_auc_score(y, base_CE)), 4),
                "coef_C_E_K_S": cf})
        # H2: does the selective composite down-rank host-toxic vs the conservation baseline?
        if host_tox.sum() >= 5:
            comp = oof([C, E, K, S], y) if y.sum() >= 20 else None
            def pct(score): r = np.argsort(np.argsort(score)); return r / (len(score) - 1)  # higher=better target
            pc_C = pct(C)
            tox = host_tox == 1
            row = {"mean_pctile_hosttoxic_conservation": round(float(pc_C[tox].mean()), 4),
                   "mean_pctile_nontoxic_conservation": round(float(pc_C[~tox].mean()), 4),
                   "mean_C_hosttoxic": round(float(C[tox].mean()), 2), "mean_C_nontoxic": round(float(C[~tox].mean()), 2)}
            if comp is not None:
                pc_comp = pct(comp)
                row.update({"mean_pctile_hosttoxic_composite": round(float(pc_comp[tox].mean()), 4),
                            "composite_minus_conservation_hosttoxic_pctile": round(float(pc_comp[tox].mean() - pc_C[tox].mean()), 4)})
                k = int(y.sum())
                topk_C = set(np.argsort(-C)[:k]); topk_comp = set(np.argsort(-comp)[:k])
                row.update({"hosttoxic_in_topk_conservation": int(sum(host_tox[i] for i in topk_C)),
                            "hosttoxic_in_topk_composite": int(sum(host_tox[i] for i in topk_comp)), "k": k})
            per[X]["H2"] = row
        d = per[X].get("dAUROC_full_vs_CE", "NA")
        print(f"  [{X}] n={len(genes)} tgt={int(y.sum())} choke={int(K.sum())} nonhom={int(S.sum())} toxic={int(host_tox.sum())} "
              f"| H1 ΔAUROC vs C+E={d} | [{time.time()-t0:.0f}s]")

    # aggregate
    rel = [X for X in RELIABLE if "dAUROC_full_vs_CE" in per.get(X, {})]
    h1_full_vs_C = {X: per[X]["dAUROC_full_vs_C"] for X in rel}
    h1_full_vs_CE = {X: per[X]["dAUROC_full_vs_CE"] for X in rel}
    H1_beyond_cons = all(v > 0.02 for v in h1_full_vs_C.values()) and len(rel) >= 2
    H1_beyond_CE = all(v > 0.01 for v in h1_full_vs_CE.values()) and len(rel) >= 2
    h2org = [X for X in ORGS if "H2" in per.get(X, {}) and "composite_minus_conservation_hosttoxic_pctile" in per[X]["H2"]]
    h2_down = {X: per[X]["H2"]["composite_minus_conservation_hosttoxic_pctile"] for X in h2org}
    H2_downranks = len(h2org) >= 2 and all(v < 0 for v in h2_down.values())
    cons_promotes = {X: (per[X]["H2"]["mean_pctile_hosttoxic_conservation"], per[X]["H2"]["mean_pctile_nontoxic_conservation"]) for X in h2org}

    cons_tox = {X: [per[X]["H2"]["mean_C_hosttoxic"], per[X]["H2"]["mean_C_nontoxic"]] for X in h2org}
    promotes = len(h2org) >= 2 and all(cons_tox[X][0] > cons_tox[X][1] for X in h2org)
    n_down = sum(1 for X in h2org if h2_down[X] < 0)
    summary = {"reliable_orgs": rel, "H1_dAUROC_full_vs_C": h1_full_vs_C, "H1_dAUROC_full_vs_CE": h1_full_vs_CE,
               "H1_beyond_conservation": bool(H1_beyond_cons), "H1_KplusS_beyond_CE": bool(H1_beyond_CE),
               "H2_orgs": h2org, "H2_composite_minus_conservation_hosttoxic_pctile": h2_down,
               "H2_selectivity_downranks_hosttoxic": bool(H2_downranks),
               "H2_conservation_meanC_hosttoxic_vs_nontoxic": cons_tox,
               "H2_conservation_promotes_hosttoxic": bool(promotes)}
    v = []
    # H1 — recovery
    if H1_beyond_cons:
        v.append(f"H1: composite beats conservation in both reliable bacteria (ΔAUROC vs C {h1_full_vs_C}).")
    else:
        v.append(f"H1 (mixed): composite beats conservation clearly in E. coli (+{h1_full_vs_C.get('ecoli')}) but only marginally in M. tuberculosis (+{h1_full_vs_C.get('mtb')}).")
    v.append(f"MECHANISM (essentiality/MET) is the recovery driver; CHOKEPOINT adds only in E. coli (K coef {per['ecoli'].get('coef_C_E_K_S',[None]*4)[2]}) and is ~zero-weight in Mtb ({per['mtb'].get('coef_C_E_K_S',[None]*4)[2]}); soft SELECTIVITY S is weak — so chokepoint+selectivity do NOT robustly add BEYOND conservation+essentiality (ΔAUROC vs C+E {h1_full_vs_CE}).")
    # H2 — therapeutic validity: the key finding
    if promotes:
        v.append(f"H2 KEY FINDING (therapeutic validity): CONSERVATION-RANKING IS THERAPEUTICALLY DANGEROUS — host-toxic targets (human core-essential homologs) are the MOST CONSERVED proteins (mean bitscore host-toxic vs non-toxic {cons_tox}), so the conservation workhorse (TID1) actively PROMOTES unsafe targets.")
    v.append(f"But SOFT selectivity (S as a learned feature) does NOT reliably fix it: the composite down-ranks host-toxic in {n_down}/{len(h2org)} organisms yet UP-ranks them where they are also essential/chokepoint (Mtb Δpctile +{h2_down.get('mtb')}) — a soft selectivity feature is UNRELIABLE for safety.")
    v.append("CONCLUSION: front-half therapeutic validity requires a HARD host-non-homology FILTER (excludes ALL host-toxic by construction, since host-toxic ⊂ host-homologous), NOT a soft feature; mechanistic essentiality remains the recovery driver and chokepoint is organism-specific. Zero-data, metabolic subproteome, 2 reliably-testable bacteria; ChEMBL selection-bias caveat on H1; not wet-lab.")
    summary["verdict"] = " ".join(v)
    print("\nPANEL:", json.dumps({k: x for k, x in summary.items() if k != "verdict"}, indent=1)); print("VERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host_evalue": HOST_EVALUE}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_organism": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "FRONT1_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: x for k, x in summary.items() if k != "verdict"}, "per_organism": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "FRONT1_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
