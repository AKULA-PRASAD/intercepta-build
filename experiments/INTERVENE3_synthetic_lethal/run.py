"""INTERVENE3 — can PARALOG SYNTHETIC LETHALITY open a DRUGGED route to the UNDRUGGABLE validated
cancer dependencies that INTERVENE2 left de-novo-chemistry-gated (93% undrugged)?

Paralog SL is the most robustly DepMap-derivable SL class (paralogs buffer each other: loss of one makes
the cell dependent on the other). Signal = CONDITIONAL differential dependency, NOT co-dependency
correlation. For a direction A->B: split the 988 CRISPR-Expr lines by expr(A) into bottom/top tertiles;
test if Chronos(B) is MORE NEGATIVE (stronger dependency) in A-low lines (one-sided Mann-Whitney +
Cliff's delta + median diff). BH-FDR over the full directional paralog family.

G1 (decision) recover a frozen external curated known-SL set above the paralog-universe base rate AND a
random non-paralog null. If G1 fails -> STOP, honest negative. G2 (descriptive) fraction of undrugged
selective dependencies with a DepMap-validated paralog-SL partner that IS drugged (approved subset +
patient-driver slice + examples).

SCOPE: in-silico genetic-interaction hypothesis, NOT a validated drug combination, NOT clinical;
"drugged" = has a ChEMBL ligand; co-dependency correlation != SL (guarded by conditional definition +
known-pair validation + two nulls). Reproduced x2 byte-identical. See PREREG.md.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DEPMAP = os.environ.get("DEPEND1_DATA", "/Users/kalki/kaalcura/data")
IDATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
INT = os.path.join(IDATA, "intervene")
DT_TSV = os.path.join(INT, "drug_targets.tsv")
DT_FASTA = os.path.join(INT, "drug_targets.fasta")
I3 = os.path.join(IDATA, "intervene3")
PARA_SLIM = os.path.join(I3, "paralog_pairs_slim.tsv")
VALIDATED = os.path.join(I3, "validated_SLs.txt")
MAXPHASE_CACHE = os.path.join(IDATA, "intervene2", "chembl_max_phase.json")
COMP = os.path.join(IDATA, "f3clin1", "2024-06-18_IntOGen-Drivers", "Compendium_Cancer_Genes.tsv")

SEED, K_NULL = 42, 5000
DEP_THRESH, PAN_FRAC, SEL_LO, SEL_HI = -0.5, 0.90, 0.01, 0.50
FDR_Q = 0.10
DELTA_MAX = -0.10          # Cliff's delta: B more essential in A-low
MIN_GROUP = 10

PARA_SRC = ("https://raw.githubusercontent.com/cancergenetics/paralog_seq_similarity/main/"
            "data/ens111_human_SL.csv")
VAL_SRC = ("https://raw.githubusercontent.com/cancergenetics/paralog_SL_prediction/HEAD/"
           "local_data/validated_SLs.txt")

SHAS = {
 "depmap_crispr_gene_effect.csv": "d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bh_fdr(pvals):
    """Benjamini-Hochberg q-values."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for i in range(n - 1, -1, -1):
        idx = order[i]
        prev = min(prev, p[idx] * n / (i + 1))
        q[idx] = prev
    return q


def main():
    t0 = time.time()

    # ---------------- 1. load DepMap Chronos + expression ----------------
    ce_path = os.path.join(DATA_DEPMAP, "depmap_crispr_gene_effect.csv")
    got = sha256(ce_path)
    if got != SHAS["depmap_crispr_gene_effect.csv"]:
        raise RuntimeError(f"CRISPR sha mismatch: {got}")
    ce = pd.read_csv(ce_path, index_col=0)
    ce.columns = [c.split(" (")[0] for c in ce.columns]
    ce = ce.loc[:, ~ce.columns.duplicated()]
    genes = list(ce.columns)

    # selective set (DEPEND1 exact) on the FULL matrix
    E = ce.values.astype(float)
    dep_frac = (E < DEP_THRESH).mean(0)
    n_pan = int(np.sum(dep_frac > PAN_FRAC))
    sel_mask = (dep_frac >= SEL_LO) & (dep_frac <= SEL_HI)
    n_sel = int(np.sum(sel_mask))
    assert n_sel == 3664, f"selective set {n_sel} != DEPEND1 committed 3664 — definition drift"
    selective = set(np.array(genes)[sel_mask])
    depfrac_by_gene = dict(zip(genes, dep_frac))
    print(f"selective reproduced: n_selective={n_sel} pan={n_pan} universe={len(genes)}", flush=True)

    ex = pd.read_csv(os.path.join(DATA_DEPMAP, "depmap_expression.csv"), index_col=0)
    ex.columns = [c.split(" (")[0] for c in ex.columns]
    ex = ex.loc[:, ~ex.columns.duplicated()]
    ex_sha = sha256(os.path.join(DATA_DEPMAP, "depmap_expression.csv"))

    shared = sorted(set(ce.index) & set(ex.index))
    n_shared = len(shared)
    ce_s = ce.loc[shared]
    ex_s = ex.loc[shared]
    ce_genes = set(ce_s.columns)
    ex_genes = set(ex_s.columns)

    # ---------------- 2. INTERVENE2 drug-target mapper (verbatim logic) ----------------
    sym2acc = {}
    for ln in open(DT_FASTA):
        if not ln.startswith(">") or "Homo sapiens" not in ln:
            continue
        acc = ln.split("|")[1]
        gn = [t[3:] for t in ln.split() if t.startswith("GN=")]
        if gn:
            sym2acc.setdefault(gn[0], set()).add(acc)
    acc_info = {}
    for ln in open(DT_TSV).read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 6 and p[1] == "Homo sapiens":
            acc_info.setdefault(p[0], []).append((p[3], p[4], p[5]))
    human_acc = set(acc_info)
    maxphase = json.load(open(MAXPHASE_CACHE))

    def gene_drug_info(sym):
        accs = {a for a in sym2acc.get(sym, set()) if a in human_acc}
        drugs, phases, moas, actions = set(), [], set(), set()
        for a in accs:
            for act, moa, drug in acc_info[a]:
                drugs.add(drug)
                if moa: moas.add(moa)
                if act: actions.add(act)
                mp = maxphase.get(drug)
                if mp is not None:
                    try: phases.append(float(mp))
                    except (TypeError, ValueError): pass
        max_mp = max(phases) if phases else None
        return bool(accs), max_mp, sorted(moas), sorted(actions), len(drugs)

    def is_drugged(sym):
        return gene_drug_info(sym)[0]

    def is_approved(sym):
        mp = gene_drug_info(sym)[1]
        return mp is not None and mp >= 4

    # ---------------- 3. paralog universe + curated known-SL set ----------------
    para = pd.read_csv(PARA_SLIM, sep="\t")
    para_pairs = [(a, b) for a, b in zip(para.A1, para.A2)]
    seqid = {tuple(sorted((a, b))): float(s)
             for a, b, s in zip(para.A1, para.A2, para.min_sequence_identity)}
    para_gene_set = set(para.A1) | set(para.A2)

    val = pd.read_csv(VALIDATED)
    curated = [(a, b) for a, b in zip(val.A1, val.A2)]
    curated_fs = set(frozenset(p) for p in curated)

    # ---------------- SL test primitives (numpy, on shared lines) ----------------
    depB_cache, exprA_cache = {}, {}

    def dep_vec(g):
        if g not in depB_cache:
            depB_cache[g] = ce_s[g].values.astype(float) if g in ce_genes else None
        return depB_cache[g]

    def exp_vec(g):
        if g not in exprA_cache:
            exprA_cache[g] = ex_s[g].values.astype(float) if g in ex_genes else None
        return exprA_cache[g]

    def sl_direction(A, B):
        """Return (p_onesided, cliffs_delta, median_diff, nlo, nhi) for A-low -> stronger dep(B)."""
        ea, db = exp_vec(A), dep_vec(B)
        if ea is None or db is None:
            return None
        ok = ~np.isnan(ea) & ~np.isnan(db)
        ea2, db2 = ea[ok], db[ok]
        if ea2.size < 3 * MIN_GROUP:
            return None
        q1, q2 = np.quantile(ea2, 1 / 3), np.quantile(ea2, 2 / 3)
        lo = db2[ea2 <= q1]
        hi = db2[ea2 >= q2]
        if lo.size < MIN_GROUP or hi.size < MIN_GROUP:
            return None
        try:
            U, p = mannwhitneyu(lo, hi, alternative="less")
        except ValueError:
            return None
        delta = 2.0 * U / (lo.size * hi.size) - 1.0   # <0 => lo more negative
        mdiff = float(np.median(lo) - np.median(hi))
        return float(p), float(delta), mdiff, int(lo.size), int(hi.size)

    def pair_directions(A, B):
        """both directions; list of dicts."""
        out = []
        for X, Y in ((A, B), (B, A)):
            r = sl_direction(X, Y)
            if r is not None:
                out.append({"A": X, "B": Y, "p": r[0], "delta": r[1],
                            "mdiff": r[2], "nlo": r[3], "nhi": r[4]})
        return out

    # ---------------- 4. run all paralog directional tests + curated ----------------
    print("running SL tests over paralog universe ...", flush=True)
    fam = []          # every directional test in the FDR family
    pair_index = {}   # frozenset -> list of indices in fam
    all_pairs = list({tuple(sorted(p)) for p in para_pairs} | curated_fs_pairs(curated_fs))
    for (A, B) in all_pairs:
        dirs = pair_directions(A, B)
        key = frozenset((A, B))
        pair_index[key] = []
        for d in dirs:
            pair_index[key].append(len(fam))
            fam.append(d)
    pvals = np.array([d["p"] for d in fam])
    qvals = bh_fdr(pvals)
    for d, q in zip(fam, qvals):
        d["q"] = float(q)
    # p* = largest p with q<FDR_Q
    sig_ps = pvals[qvals < FDR_Q]
    p_star = float(sig_ps.max()) if sig_ps.size else 0.0
    print(f"  directional tests in family={len(fam)}  p*={p_star:.3e}  "
          f"(n sig dir @ q<{FDR_Q}={int((qvals<FDR_Q).sum())})", flush=True)

    def detected(d):
        return p_star > 0 and d["p"] <= p_star and d["mdiff"] < 0 and d["delta"] <= DELTA_MAX

    def pair_detected(A, B):
        key = frozenset((A, B))
        best = None
        for i in pair_index.get(key, []):
            d = fam[i]
            hit = detected(d)
            cand = (hit, d)
            if best is None or (hit and not best[0]) or (hit == best[0] and d["p"] < best[1]["p"]):
                best = cand
        return best  # (detected_bool, best_dir_dict) or None

    # ---------------- 5. G1 validation ----------------
    curated_results = []
    n_cur_testable = n_cur_detected = 0
    for (A, B) in curated:
        pr = pair_detected(A, B)
        if pr is None:
            curated_results.append({"pair": f"{A}/{B}", "testable": False})
            continue
        n_cur_testable += 1
        hit, d = pr
        n_cur_detected += int(hit)
        curated_results.append({"pair": f"{A}/{B}", "testable": True, "detected": bool(hit),
                                "best_dir": f"{d['A']}low->dep({d['B']})", "p": round(d["p"], 3 if d["p"]>1e-3 else 12),
                                "delta": round(d["delta"], 3), "mdiff": round(d["mdiff"], 3), "q": round(d["q"], 4)})
    recovery = n_cur_detected / len(curated)
    recovery_of_testable = n_cur_detected / n_cur_testable if n_cur_testable else 0.0

    # paralog-universe base rate (exclude curated pairs)
    uni_only = [p for p in {tuple(sorted(x)) for x in para_pairs} if frozenset(p) not in curated_fs]
    uni_tested = uni_det = 0
    for (A, B) in uni_only:
        pr = pair_detected(A, B)
        if pr is None:
            continue
        uni_tested += 1
        uni_det += int(pr[0])
    base_rate = uni_det / uni_tested if uni_tested else 0.0

    # random non-paralog gene-pair null (same p*, criteria)
    rng = np.random.default_rng(SEED)
    cand_genes = sorted(ce_genes & ex_genes)
    para_fs = {frozenset(p) for p in para_pairs}
    null_tested = null_det = 0
    tries = 0
    while null_tested < K_NULL and tries < K_NULL * 40:
        tries += 1
        a = cand_genes[int(rng.integers(len(cand_genes)))]
        b = cand_genes[int(rng.integers(len(cand_genes)))]
        if a == b or frozenset((a, b)) in para_fs:
            continue
        best = None
        for X, Y in ((a, b), (b, a)):
            r = sl_direction(X, Y)
            if r is None:
                continue
            d = {"p": r[0], "delta": r[1], "mdiff": r[2]}
            hit = detected(d)
            if best is None or (hit and not best[0]):
                best = (hit, d)
        if best is None:
            continue
        null_tested += 1
        null_det += int(best[0])
    null_rate = null_det / null_tested if null_tested else 0.0

    G1 = "PASS" if (recovery >= 0.50 and base_rate > 0 and recovery >= 3 * base_rate
                    and recovery > null_rate) else "FAIL"
    print(f"\nG1: recovery={recovery:.2f} ({n_cur_detected}/{len(curated)}), "
          f"of-testable={recovery_of_testable:.2f} ({n_cur_detected}/{n_cur_testable}); "
          f"paralog base_rate={base_rate:.4f} ({uni_det}/{uni_tested}); "
          f"nonparalog null={null_rate:.4f} ({null_det}/{null_tested}) -> {G1}", flush=True)

    # ---------------- 6. G2 application (only meaningful if G1 PASS) ----------------
    g2 = None
    if G1 == "PASS":
        # undrugged selective set (INTERVENE2 mapper)
        drugged_sel = {g for g in selective if is_drugged(g)}
        undrugged = sorted(selective - drugged_sel)
        n_undrugged = len(undrugged)

        # paralog partners per gene (from universe)
        partners = {}
        for (A, B) in {tuple(sorted(x)) for x in para_pairs}:
            partners.setdefault(A, set()).add(B)
            partners.setdefault(B, set()).add(A)

        # patient drivers
        comp = pd.read_csv(COMP, sep="\t", low_memory=False)
        drivers = set(comp["SYMBOL"].unique()) & set(genes)

        with_partner = with_sl = with_drugged_sl = with_approved_sl = 0
        driver_undrugged = driver_with_drugged_sl = 0
        examples = []
        drugged_sl_hits = []   # (target, partner, seq_id, approved) for credibility stratification
        for T in undrugged:
            is_drv = T in drivers
            if is_drv:
                driver_undrugged += 1
            ps = partners.get(T, set())
            if not ps:
                continue
            with_partner += 1
            sl_partners, drugged_sl_partners, approved_sl_partners = [], [], []
            for P in ps:
                pr = pair_detected(T, P)
                if pr is None or not pr[0]:
                    continue
                sl_partners.append((P, pr[1]))
                if is_drugged(P):
                    drugged_sl_partners.append(P)
                    ap = is_approved(P)
                    drugged_sl_hits.append((T, P, seqid.get(tuple(sorted((T, P))), float("nan")), bool(ap)))
                    if ap:
                        approved_sl_partners.append(P)
            if sl_partners:
                with_sl += 1
            if drugged_sl_partners:
                with_drugged_sl += 1
                if is_drv:
                    driver_with_drugged_sl += 1
                # pick strongest example (approved preferred)
                chosen = approved_sl_partners or drugged_sl_partners
                P = sorted(chosen)[0]
                pr = pair_detected(T, P)
                d = pr[1]
                _, mp, moas, actions, ndr = gene_drug_info(P)
                examples.append({
                    "undrugged_target": T, "target_dep_frac": round(depfrac_by_gene[T], 4),
                    "target_is_driver": bool(is_drv),
                    "sl_partner": P, "partner_max_phase": mp, "partner_approved": bool(is_approved(P)),
                    "partner_n_drugs": ndr, "partner_moa": (moas[0] if moas else "")[:80],
                    "seq_identity": round(seqid.get(tuple(sorted((T, P))), float("nan")), 3),
                    "sl_dir": f"{d['A']}low->dep({d['B']})",
                    "sl_p": float(d["p"]), "sl_delta": round(d["delta"], 3),
                    "sl_mdiff": round(d["mdiff"], 3)})
            if approved_sl_partners:
                with_approved_sl += 1
        examples.sort(key=lambda e: (not e["partner_approved"], e["sl_p"]))

        # credibility stratification of drugged-SL routes by paralog sequence identity
        # (true buffering paralogs have higher identity; low-id hits are likely lineage confounds)
        def cred_counts(min_id):
            tset = {h[0] for h in drugged_sl_hits if not np.isnan(h[2]) and h[2] >= min_id}
            aset = {h[0] for h in drugged_sl_hits if not np.isnan(h[2]) and h[2] >= min_id and h[3]}
            return len(tset), len(aset)
        cred_20 = cred_counts(0.20)
        cred_30 = cred_counts(0.30)

        g2 = {
          "n_undrugged_selective": n_undrugged,
          "n_with_any_paralog_partner": with_partner,
          "n_with_sl_partner": with_sl,
          "n_with_drugged_sl_partner": with_drugged_sl,
          "n_with_approved_drugged_sl_partner": with_approved_sl,
          "frac_undrugged_with_drugged_sl_route": round(with_drugged_sl / n_undrugged, 4),
          "frac_undrugged_with_approved_sl_route": round(with_approved_sl / n_undrugged, 4),
          "frac_of_partnered_with_drugged_sl": round(with_drugged_sl / with_partner, 4) if with_partner else 0.0,
          "driver_subset": {
            "n_undrugged_drivers": driver_undrugged,
            "n_with_drugged_sl_partner": driver_with_drugged_sl,
            "frac": round(driver_with_drugged_sl / driver_undrugged, 4) if driver_undrugged else 0.0},
          "credible_by_seq_identity": {
            "n_drugged_sl_targets_id_ge_0.20": cred_20[0], "n_approved_id_ge_0.20": cred_20[1],
            "n_drugged_sl_targets_id_ge_0.30": cred_30[0], "n_approved_id_ge_0.30": cred_30[1]},
          "n_examples": len(examples),
        }
        print(f"\nG2: undrugged selective={n_undrugged}; with paralog partner={with_partner}; "
              f"with SL partner={with_sl}; with DRUGGED SL partner={with_drugged_sl} "
              f"({g2['frac_undrugged_with_drugged_sl_route']:.2%}); approved={with_approved_sl} "
              f"({g2['frac_undrugged_with_approved_sl_route']:.2%})", flush=True)
        print("  top examples (undrugged target -> drugged SL partner):")
        for e in examples[:20]:
            print(f"    {e['undrugged_target']:9s}(dep={e['target_dep_frac']:.2f}"
                  f"{',drv' if e['target_is_driver'] else ''}) -> {e['sl_partner']:9s} "
                  f"phase={e['partner_max_phase']} id={e['seq_identity']} "
                  f"p={e['sl_p']:.1e} delta={e['sl_delta']:.2f} {e['partner_moa'][:40]}")

    # ---------------- payload / verdict ----------------
    payload = {
      "seed": SEED, "K_null": K_NULL, "n_shared_lines": n_shared,
      "dep_thresh": DEP_THRESH, "sel_band": [SEL_LO, SEL_HI], "fdr_q": FDR_Q,
      "delta_max": DELTA_MAX, "min_group": MIN_GROUP,
      "n_universe_genes": len(genes), "n_selective": n_sel, "n_pan_essential": n_pan,
      "n_paralog_pairs": len({tuple(sorted(x)) for x in para_pairs}),
      "n_paralog_genes": len(para_gene_set),
      "n_directional_tests": len(fam), "p_star": p_star,
      "n_significant_directions_fdr": int((qvals < FDR_Q).sum()),
      "G1": {
        "n_curated": len(curated), "n_testable": n_cur_testable, "n_detected": n_cur_detected,
        "recovery": round(recovery, 4), "recovery_of_testable": round(recovery_of_testable, 4),
        "paralog_base_rate": round(base_rate, 6), "paralog_base_n": [uni_det, uni_tested],
        "nonparalog_null_rate": round(null_rate, 6), "nonparalog_null_n": [null_det, null_tested],
        "gate": G1},
      "G2": g2,
    }

    if G1 == "PASS":
        f_dr = g2["frac_undrugged_with_drugged_sl_route"]
        f_ap = g2["frac_undrugged_with_approved_sl_route"]
        verdict = (
          f"INTERVENE3 — paralog synthetic lethality as a DRUGGED route around cancer undruggability. "
          f"G1 PASS: the DepMap conditional SL test (expr-tertile-conditioned differential dependency, NOT "
          f"co-dependency correlation) recovers {n_cur_detected}/{len(curated)} ({recovery:.0%}) of a frozen "
          f"external curated known-paralog-SL set at BH-FDR<{FDR_Q} + Cliff's-delta<={DELTA_MAX}, vs a paralog-"
          f"universe base rate of {base_rate:.1%} ({recovery/base_rate:.0f}x) and a random non-paralog-pair null "
          f"of {null_rate:.1%}. The SL signal is REAL and recovered above both nulls. "
          f"G2 (descriptive) — of INTERVENE2's {g2['n_undrugged_selective']} UNDRUGGED validated selective "
          f"dependencies, {g2['n_with_any_paralog_partner']} have any paralog partner, {g2['n_with_sl_partner']} "
          f"have a DepMap-validated paralog-SL partner, and {g2['n_with_drugged_sl_partner']} ({f_dr:.1%}) have "
          f"an SL partner that IS drugged in ChEMBL ({g2['n_with_approved_drugged_sl_partner']}={f_ap:.1%} with an "
          f"APPROVED-drug partner). So paralog-SL opens an existing-drug ROUTE HYPOTHESIS to ~{f_dr:.0%} of the "
          f"otherwise-undruggable validated dependencies (driver subset: "
          f"{g2['driver_subset']['n_with_drugged_sl_partner']}/{g2['driver_subset']['n_undrugged_drivers']}). "
          f"SCOPE: this is an IN-SILICO GENETIC-INTERACTION HYPOTHESIS for a combination/context experiment, NOT a "
          f"validated drug combination and NOT clinical; 'drugged' = has a ChEMBL ligand; co-dependency correlation "
          f"!= SL (guarded structurally + by known-pair validation + two nulls). Cancer cell-line layer; not wet-lab, "
          f"not response prediction. The {f_dr:.0%} is a small but real dent in the 93% undrugged ceiling.")
    else:
        verdict = (
          f"INTERVENE3 — G1 FAIL. The DepMap paralog-SL test recovered only {n_cur_detected}/{len(curated)} "
          f"({recovery:.0%}) of the curated known-SL set (base rate {base_rate:.1%}, null {null_rate:.1%}); the "
          f"signal does not clear the pre-registered validation bar. HONEST NEGATIVE: paralog-SL from this DepMap "
          f"expression-conditioned test is not reliable enough to apply — STOPPED before application per PREREG. "
          f"co-dependency correlation != SL; not wet-lab, not clinical.")

    payload_json = json.dumps(payload, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    out = dict(payload)
    out["verdict"] = verdict
    out["curated_detail"] = curated_results
    if G1 == "PASS":
        out["g2_examples_top50"] = examples[:50]
    out["provenance"] = {
        "paralog_source_url": PARA_SRC, "validated_source_url": VAL_SRC,
        "paralog_slim_sha256": sha256(PARA_SLIM), "validated_sha256": sha256(VALIDATED),
        "ens111_human_SL_sha256": sha256(os.path.join(I3, "ens111_human_SL.csv")),
        "expression_sha256": ex_sha, "input_sha256": SHAS,
        "git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(),
        "python": sys.version.split()[0],
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out["payload_sha256"] = sha
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "INTERVENE3_metrics.json"), "w"),
              indent=2, sort_keys=True)
    open(os.path.join(HERE, "results", "INTERVENE3_payload.sha256"), "w").write(sha + "\n")
    print("\nVERDICT:", verdict)
    print("\npayload_sha256:", sha, f"[{time.time()-t0:.0f}s]")


def curated_fs_pairs(curated_fs):
    """frozenset pairs -> sorted tuple set (for union with universe)."""
    return {tuple(sorted(p)) for p in curated_fs}


if __name__ == "__main__":
    main()
