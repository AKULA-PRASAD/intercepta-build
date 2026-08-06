"""TRANSFER1 — Label-free zero-screen dependency prediction for a host-embedded organism.

Treat P. falciparum as a SIMULATED zero-screen organism. Predict its essential genes LABEL-FREE by transferring
the essentiality/dependency status of its human (DepMap) / yeast (DEG) RBH orthologs. Validate against its
held-out real screen (Zhang 2018), NEVER used to build the prediction. DECISIVE guard: the transfer must BEAT
a conservation-only null (NULL-A) and carry signal beyond the pan-essential/conserved-core fraction (NULL-B).

Implements PREREG.md. Deterministic (seed 42). Reproduce x2 byte-identical. CPU-only. NEVER commit data/push.
"""
import os, sys, csv, re, json, time, hashlib
import numpy as np, pandas as pd
from scipy.stats import fisher_exact

csv.field_size_limit(sys.maxsize)
SEED = 42
NBOOT = 2000
DEP_THRESH = -0.5
PAN_FRAC = 0.90
SEL_LO, SEL_HI = 0.01, 0.50

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
T1 = os.path.join(DATA, "transfer1")
PF_FASTA = os.path.join(DATA, "tid1/proteomes/pfalciparum.fasta")
HU_FASTA = os.path.join(DATA, "tid1/proteomes/human.fasta")
YE_FASTA = os.path.join(T1, "scerevisiae.fasta")
ANNOT = os.path.join(DATA, "generalize5/Pf3D7_gene_annotations.csv")
DEG = os.path.join(DATA, "generalize4/deg_euk/deg_annotation_e.csv")
RBH_H = os.path.join(T1, "rbh_pf_human.tsv")
RBH_Y = os.path.join(T1, "rbh_pf_yeast.tsv")
DEPMAP = "/Users/kalki/kaalcura/data/depmap_crispr_gene_effect.csv"
DEPMAP_SHA = "d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fasta_acc2gn(path):
    """UniProt acc -> gene symbol (GN=) from a UniProt FASTA."""
    m = {}
    for line in open(path):
        if line.startswith(">"):
            ma = re.match(r">\w+\|([^|]+)\|", line)
            g = re.search(r"GN=(\S+)", line)
            if ma and g:
                m[ma.group(1)] = g.group(1).upper()
    return m


def fisher(a, b, c, d):
    orr, p = fisher_exact([[a, b], [c, d]], alternative="greater")
    return float(orr), float(p)


def contingency(pred_set, ess_set, universe):
    a = b = c = d = 0
    for g in universe:
        pe = g in pred_set
        ee = g in ess_set
        if pe and ee: a += 1
        elif pe and not ee: b += 1
        elif (not pe) and ee: c += 1
        else: d += 1
    return a, b, c, d


def score(pred_set, ess_set, universe, label):
    a, b, c, d = contingency(pred_set, ess_set, universe)
    orr, p = fisher(a, b, c, d)
    prec = a / (a + b) if (a + b) else None
    rec = a / (a + c) if (a + c) else None
    return {"predictor": label, "contingency": {"both": a, "pred_only": b, "ess_only": c, "neither": d},
            "n_pred_pos": a + b, "odds_ratio": (round(orr, 4) if np.isfinite(orr) else None),
            "fisher_p_greater": float(f"{p:.3e}"),
            "precision": round(prec, 4) if prec is not None else None,
            "recall": round(rec, 4) if rec is not None else None}


def main():
    t0 = time.time()
    # sha guard on the one frozen input
    got = sha256_file(DEPMAP)
    if got != DEPMAP_SHA:
        raise RuntimeError(f"DepMap sha mismatch: {got}")

    # ---------- P. falciparum proteome accessions ----------
    pf_acc = []
    for line in open(PF_FASTA):
        if line.startswith(">"):
            ma = re.match(r">\w+\|([^|]+)\|", line)
            if ma: pf_acc.append(ma.group(1))
    pf_acc = set(pf_acc)

    # ---------- annotation: pf UniProt acc -> PF3D7 gene id ; PF3D7 -> Zhang ----------
    uni2pf = {}
    pf2zhang = {}
    r = csv.DictReader(open(ANNOT, encoding="utf-8", errors="ignore"))
    for row in r:
        pf = row["Gene ID"].strip()
        ph = row["Zhang Phenotype"].strip()
        if ph:
            pf2zhang[pf] = ph
        for u in re.split(r"[;,\s]+", row["Uniprot IDs"].strip()):
            u = u.strip()
            if u and u.upper() != "N/A":
                uni2pf[u] = pf
    zhang_essential = set(pf for pf, ph in pf2zhang.items() if ph == "Non - Mutable in CDS")

    # ---------- reference labels ----------
    # HUMAN gene symbol -> {pan, selective} from DepMap
    ce = pd.read_csv(DEPMAP, index_col=0)
    ce = ce.rename(columns={c: c.split(" (")[0] for c in ce.columns if " (" in c})
    ce = ce.loc[:, ~ce.columns.duplicated()]
    E = ce.values.astype(float)
    dep_frac = (E < DEP_THRESH).mean(0)
    sym = np.array(ce.columns)
    human_pan = set(sym[dep_frac > PAN_FRAC])
    human_sel = set(sym[(dep_frac >= SEL_LO) & (dep_frac <= SEL_HI)])
    n_pan_dm, n_sel_dm = len(human_pan), len(human_sel)

    # YEAST essential gene names (DEG, S. cerevisiae only)
    yeast_ess_gn = set()
    with open(DEG, encoding="utf-8", errors="ignore") as f:
        for row in csv.reader(f, delimiter=";", quotechar='"'):
            if len(row) >= 8 and row[7].strip() == "Saccharomyces cerevisiae":
                gn = row[2].strip().upper()
                if gn and gn != "-":
                    yeast_ess_gn.add(gn)

    # proteome-acc -> gene symbol maps for reference proteomes
    hu_acc2gn = fasta_acc2gn(HU_FASTA)
    ye_acc2gn = fasta_acc2gn(YE_FASTA)

    # ---------- RBH orthology (pf acc -> reference acc) ----------
    def load_rbh(path):
        m = {}
        for line in open(path):
            f = line.rstrip("\n").split("\t")
            if len(f) >= 3:
                m.setdefault(f[0], []).append((f[1], float(f[2])))
        return m
    rbh_h = load_rbh(RBH_H)   # pf_acc -> [(human_acc, pident), ...]
    rbh_y = load_rbh(RBH_Y)

    pids = [p for v in rbh_h.values() for _, p in v] + [p for v in rbh_y.values() for _, p in v]
    pid_arr = np.array(pids)

    # ---------- build per-PF3D7-gene features over Universe U ----------
    # U = PF3D7 genes reachable from proteome that carry a Zhang label
    pf_genes_in_U = set()
    pf2accs = {}
    for a in pf_acc:
        pf = uni2pf.get(a)
        if pf and pf in pf2zhang:
            pf_genes_in_U.add(pf)
            pf2accs.setdefault(pf, []).append(a)
    U = sorted(pf_genes_in_U)

    has_human = set(); has_yeast = set()
    orth_human_pan = set(); orth_human_sel = set(); orth_yeast_ess = set()
    for pf in U:
        for a in pf2accs[pf]:
            for hacc, _ in rbh_h.get(a, []):
                has_human.add(pf)
                s = hu_acc2gn.get(hacc)
                if s in human_pan: orth_human_pan.add(pf)
                if s in human_sel: orth_human_sel.add(pf)
            for yacc, _ in rbh_y.get(a, []):
                has_yeast.add(pf)
                s = ye_acc2gn.get(yacc)
                if s in yeast_ess_gn: orth_yeast_ess.add(pf)
    has_any = has_human | has_yeast

    # prediction variants (label-free)
    var_common = orth_human_pan | orth_yeast_ess          # (a)
    var_selective = orth_human_sel                        # (b)
    var_combined = var_common | var_selective             # (c)

    ess = set(pf for pf in U if pf in zhang_essential)     # held-out truth restricted to U
    base_rate = len(ess) / len(U)

    # ---------- scoring over U ----------
    s_nullA = score(has_any, ess, U, "NULL-A: has ANY human/yeast ortholog (conservation-only)")
    s_a = score(var_common, ess, U, "(a) COMMON-essential transfer")
    s_b = score(var_selective, ess, U, "(b) SELECTIVE-dependency transfer")
    s_c = score(var_combined, ess, U, "(c) COMBINED transfer")

    # ---------- DECISIVE beyond-conservation: restrict to genes WITH an ortholog ----------
    U_orth = sorted(has_any)
    base_rate_orth = sum(1 for g in U_orth if g in ess) / len(U_orth)
    bc_combined = score(var_combined, ess, U_orth, "beyond-cons: (c) combined | among ortholog-havers")
    bc_common = score(var_common, ess, U_orth, "beyond-cons: (a) common | among ortholog-havers")
    # SELECTIVE-only = selective orthologs that are NOT also common/pan (isolate the non-conserved-core arm)
    sel_only = var_selective - var_common
    bc_sel_only = score(sel_only, ess, U_orth, "beyond-cons: SELECTIVE-only (excl. common) | among ortholog-havers")

    # ---------- NULL-B pan-essential triviality breakdown ----------
    n_combined = len(var_combined)
    n_from_common = len(var_combined & var_common)
    n_sel_only = len(sel_only)
    nullB = {"n_transfer_pos_combined": n_combined,
             "n_pan_common_core": n_from_common,
             "n_selective_only_beyond_core": n_sel_only,
             "frac_signal_that_is_conserved_core": round(n_from_common / n_combined, 4) if n_combined else None}

    # ---------- bootstrap 95% CI on OR_combined - OR_nullA over U ----------
    Uarr = np.array(U)
    y = np.array([1 if g in ess else 0 for g in U])
    p_any = np.array([1 if g in has_any else 0 for g in U])
    p_comb = np.array([1 if g in var_combined else 0 for g in U])

    def or_from_idx(idx, pred, yv):
        pp = pred[idx]; yy = yv[idx]
        a = int(((pp == 1) & (yy == 1)).sum()); b = int(((pp == 1) & (yy == 0)).sum())
        c = int(((pp == 0) & (yy == 1)).sum()); d = int(((pp == 0) & (yy == 0)).sum())
        # Haldane-Anscombe 0.5 correction for stable bootstrap ORs
        return ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))

    rng = np.random.default_rng(SEED)
    n = len(U); diffs = np.empty(NBOOT)
    for i in range(NBOOT):
        idx = rng.integers(0, n, n)
        diffs[i] = or_from_idx(idx, p_comb, y) - or_from_idx(idx, p_any, y)
    ci_lo = float(np.percentile(diffs, 2.5)); ci_hi = float(np.percentile(diffs, 97.5))
    or_diff_point = float(or_from_idx(np.arange(n), p_comb, y) - or_from_idx(np.arange(n), p_any, y))

    # ---------- GATES ----------
    G1 = bool(s_c["odds_ratio"] is not None and s_c["odds_ratio"] > 3 and s_c["fisher_p_greater"] < 0.01)
    g2i = bool(ci_lo > 0)  # transfer OR strictly above conservation OR (CI excludes 0)
    g2ii = bool(bc_sel_only["odds_ratio"] is not None and bc_sel_only["odds_ratio"] > 1
                and bc_sel_only["fisher_p_greater"] < 0.05)
    G2 = bool(g2i and g2ii)
    verdict_code = "PASS" if (G1 and G2) else ("PARTIAL" if G1 else "NEGATIVE")

    payload = {
        "seed": SEED, "nboot": NBOOT, "dep_thresh": DEP_THRESH, "pan_frac": PAN_FRAC,
        "sel_band": [SEL_LO, SEL_HI],
        "orthology": {"method": "mmseqs2 easy-rbh RBH", "params": "-e 1e-5 -c 0.5 --cov-mode 0 -s 5.7",
                      "n_rbh_human_pairs": sum(len(v) for v in rbh_h.values()),
                      "n_rbh_yeast_pairs": sum(len(v) for v in rbh_y.values()),
                      "median_pident": round(float(np.median(pid_arr)), 4),
                      "min_pident": round(float(pid_arr.min()), 4),
                      "max_pident": round(float(pid_arr.max()), 4)},
        "reference_labels": {"depmap_n_lines": int(E.shape[0]), "depmap_n_genes": int(E.shape[1]),
                             "human_pan_essential_n": n_pan_dm, "human_selective_n": n_sel_dm,
                             "yeast_deg_essential_n": len(yeast_ess_gn)},
        "universe": {"n_proteome_accessions": len(pf_acc), "n_U_pf3d7_genes_with_zhang": len(U),
                     "zhang_base_rate_in_U": round(base_rate, 4),
                     "n_with_any_ortholog": len(has_any),
                     "orthology_coverage_of_U": round(len(has_any) / len(U), 4),
                     "n_with_human_ortholog": len(has_human), "n_with_yeast_ortholog": len(has_yeast),
                     "base_rate_among_ortholog_havers": round(base_rate_orth, 4)},
        "counts_transfer": {"var_common_a": len(var_common), "var_selective_b": len(var_selective),
                            "var_combined_c": len(var_combined),
                            "orth_human_pan": len(orth_human_pan), "orth_human_sel": len(orth_human_sel),
                            "orth_yeast_ess": len(orth_yeast_ess)},
        "scoring_over_U": {"NULL_A_conservation": s_nullA, "a_common": s_a,
                           "b_selective": s_b, "c_combined": s_c},
        "decisive_beyond_conservation_among_ortholog_havers": {
            "c_combined": bc_combined, "a_common": bc_common, "selective_only": bc_sel_only},
        "null_B_pan_essential_triviality": nullB,
        "bootstrap_OR_combined_minus_OR_nullA": {
            "point": round(or_diff_point, 4), "ci95_lo": round(ci_lo, 4), "ci95_hi": round(ci_hi, 4),
            "ci_excludes_0": g2i, "note": "Haldane-Anscombe 0.5-corrected ORs; seed 42; 2000 resamples"},
        "gates": {"G1_transfer_OR_gt3_p_lt01": G1,
                  "G2i_transfer_above_conservation_CI": g2i,
                  "G2ii_selective_beyond_core": g2ii,
                  "G2_decisive": G2, "verdict": verdict_code},
    }

    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()

    import sklearn  # noqa
    verdict = (
        f"LABEL-FREE zero-screen transfer to P. falciparum (simulated zero-screen organism), validated vs "
        f"HELD-OUT Zhang 2018. Orthology coverage of U: {len(has_any)}/{len(U)} "
        f"({100*len(has_any)/len(U):.0f}%). Zhang base rate in U = {base_rate:.2f}. "
        f"G1 combined-transfer vs Zhang: OR={s_c['odds_ratio']} p={s_c['fisher_p_greater']} "
        f"(gate OR>3 & p<0.01: {G1}). CONSERVATION NULL-A OR={s_nullA['odds_ratio']}. "
        f"DECISIVE OR_transfer - OR_conservation = {or_diff_point:.2f} [95% CI {ci_lo:.2f},{ci_hi:.2f}] "
        f"(above conservation: {g2i}). SELECTIVE-only beyond conserved-core among ortholog-havers: "
        f"OR={bc_sel_only['odds_ratio']} p={bc_sel_only['fisher_p_greater']} (beyond-core: {g2ii}). "
        f"Conserved-core fraction of transfer signal = {nullB['frac_signal_that_is_conserved_core']}. "
        f"VERDICT: {verdict_code}. "
        f"{'Un-gate WITH caveats.' if verdict_code=='PASS' else ('Transfer works but is ONLY conserved-core -> router should KEEP abstaining (or offer only conserved-core, which conservation already provides); do NOT claim label-free selective-dependency prediction.' if verdict_code=='PARTIAL' else 'Transfer does not beat the bar -> keep abstaining.')} "
        f"SCOPE: in-silico orthology-transfer; held-out published screen (not wet-lab); one organism."
    )

    out = dict(payload)
    out["verdict"] = verdict
    out["provenance"] = {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
        "python": sys.version.split()[0], "sklearn": sklearn.__version__,
        "depmap_sha256": got, "runtime_sec": round(time.time() - t0, 1),
        "payload_sha256": sha}

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "TRANSFER1_metrics.json"), "w"),
              indent=2, sort_keys=True)
    open(os.path.join(HERE, "results", "payload.sha256"), "w").write(sha + "\n")

    print("VERDICT:", verdict)
    print("\n-- scoring over U --")
    for k, v in payload["scoring_over_U"].items():
        print(f"  {k}: OR={v['odds_ratio']} p={v['fisher_p_greater']} prec={v['precision']} rec={v['recall']} "
              f"n_pred_pos={v['n_pred_pos']} cont={v['contingency']}")
    print("\n-- decisive beyond-conservation (among ortholog-havers) --")
    for k, v in payload["decisive_beyond_conservation_among_ortholog_havers"].items():
        print(f"  {k}: OR={v['odds_ratio']} p={v['fisher_p_greater']} prec={v['precision']} rec={v['recall']}")
    print("\n-- NULL-B --", json.dumps(nullB))
    print("-- bootstrap OR diff --", json.dumps(payload["bootstrap_OR_combined_minus_OR_nullA"]))
    print("-- gates --", json.dumps(payload["gates"]))
    print("\npayload_sha256:", sha, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
