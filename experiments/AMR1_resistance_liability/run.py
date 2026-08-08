#!/usr/bin/env python
"""AMR1 — zero-data RESISTANCE-LIABILITY predictor for antibacterial targets.

Composes four objective, zero-data target-biology features (mutational tolerance = 1-conservation,
prodrug-activator dispensability, paralog redundancy, metabolic bypass) into an unweighted-mean
liability score and tests (pre-registered) whether it separates documented HIGH- from LOW-liability
targets WITHOUT using any resistance rate/MIC as input. See PREREG.md.

Deterministic. mmseqs --threads 1. Data cached to $INTERCEPTA_DATA/amr1/. NEVER git-commit; NEVER commit data.
"""
import os, sys, json, hashlib, subprocess, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
PROT = os.path.join(DATA_ROOT, "tid1", "proteomes")
OUT = os.path.join(DATA_ROOT, "amr1"); os.makedirs(os.path.join(OUT, "queries"), exist_ok=True)
MMSEQS = os.path.expanduser("~/miniconda3/envs/bioinfo/bin/mmseqs")
SYNLETH_CLASSES = os.path.join(DATA_ROOT, "synleth", "ecoli_resistance_classes.tsv")

PANEL = ["ecoli", "mtb", "paeruginosa", "bsubtilis", "hpylori", "salmonella", "efaecalis"]
PARALOG_MIN_FIDENT = 0.30
EVALUE = "1e-5"

def sha256_payload(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

def acc_of(header_id):
    return header_id.split("|")[1] if header_id.count("|") >= 2 else header_id

def read_fasta(path):
    """yield (header_line_without_>, seq)"""
    hdr, seq = None, []
    for ln in open(path):
        if ln.startswith(">"):
            if hdr is not None:
                yield hdr, "".join(seq)
            hdr, seq = ln[1:].rstrip("\n"), []
        else:
            seq.append(ln.strip())
    if hdr is not None:
        yield hdr, "".join(seq)

def gn_of(header):
    for tok in header.split():
        if tok.startswith("GN="):
            return tok[3:]
    return None

def extract_target_seqs(targets):
    """map each target -> (query_id 'gene|org|acc', seq). Deterministic: first GN match in the proteome."""
    # index each needed proteome once
    needed_orgs = sorted({t["source_org"] for t in targets})
    org_gn = {}
    for org in needed_orgs:
        idx = {}
        for hdr, seq in read_fasta(os.path.join(PROT, f"{org}.fasta")):
            gn = gn_of(hdr)
            if gn is None:
                continue
            acc = acc_of(hdr.split()[0])
            idx.setdefault(gn.lower(), (acc, seq))  # first occurrence wins (deterministic by file order)
        org_gn[org] = idx
    out = {}
    for t in targets:
        gene = t["gene"]; org = t["source_org"]
        hit = org_gn[org].get(gene.lower())
        if hit is None:
            raise SystemExit(f"FATAL: gene {gene} not found in {org} proteome")
        acc, seq = hit
        qid = f"{gene}|{org}|{acc}"
        out[t["gene"]] = (qid, acc, org, seq)
    return out

def write_queries(seqmap):
    path = os.path.join(OUT, "queries", "targets.fasta")
    with open(path, "w") as f:
        for gene in sorted(seqmap):
            qid, acc, org, seq = seqmap[gene]
            f.write(f">{qid}\n{seq}\n")
    return path

def run_mmseqs_search(query_fasta, target_fasta, out_m8, fmt):
    tmp = os.path.join(OUT, "tmp_" + os.path.basename(out_m8)); shutil.rmtree(tmp, ignore_errors=True)
    r = subprocess.run([MMSEQS, "easy-search", query_fasta, target_fasta, out_m8, tmp,
                        "--threads", "1", "-e", EVALUE, "-s", "7.5",
                        "--format-output", fmt, "-v", "1"],
                       capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.exists(out_m8):
        raise SystemExit(f"FATAL mmseqs failed: {r.stderr[-2000:]}")

def build_panel_db(seqmap):
    combined = os.path.join(OUT, "panel_tagged.fasta")
    with open(combined, "w") as out:
        for org in PANEL:
            for hdr, seq in read_fasta(os.path.join(PROT, f"{org}.fasta")):
                acc = acc_of(hdr.split()[0])
                out.write(f">{org}__{acc}\n{seq}\n")
    return combined

def compute_conservation(seqmap, query_fasta):
    """conservation = mean over the 6 panel orgs != source_org of best fraction-identity (0 if no hit)."""
    combined = build_panel_db(seqmap)
    m8 = os.path.join(OUT, "targets_vs_panel.m8")
    run_mmseqs_search(query_fasta, combined, m8, "query,target,fident,evalue")
    # best fident per (query, org)
    best = {}  # qid -> org -> fident
    for ln in open(m8):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        qid, tgt, fident = p[0], p[1], float(p[2])
        org = tgt.split("__")[0]
        d = best.setdefault(qid, {})
        if org not in d or fident > d[org]:
            d[org] = fident
    cons = {}
    for gene in seqmap:
        qid, acc, src_org, seq = seqmap[gene]
        others = [o for o in PANEL if o != src_org]
        vals = [best.get(qid, {}).get(o, 0.0) for o in others]
        cons[gene] = round(sum(vals) / len(others), 6)
    return cons

def compute_paralogs(seqmap):
    """paralogs = count of same-proteome hits with fident>=0.30, e<=1e-5, excluding self accession."""
    # group queries by source org
    by_org = {}
    for gene in seqmap:
        qid, acc, org, seq = seqmap[gene]
        by_org.setdefault(org, []).append((gene, qid, acc, seq))
    paras = {}
    for org, items in sorted(by_org.items()):
        qf = os.path.join(OUT, "queries", f"q_{org}.fasta")
        with open(qf, "w") as f:
            for gene, qid, acc, seq in sorted(items):
                f.write(f">{qid}\n{seq}\n")
        m8 = os.path.join(OUT, f"selfsearch_{org}.m8")
        run_mmseqs_search(qf, os.path.join(PROT, f"{org}.fasta"), m8, "query,target,fident,evalue")
        counts = {gene: 0 for gene, _, _, _ in items}
        qid2gene = {qid: gene for gene, qid, acc, seq in items}
        qid2acc = {qid: acc for gene, qid, acc, seq in items}
        seen = {gene: set() for gene, _, _, _ in items}
        for ln in open(m8):
            p = ln.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            qid, tgt, fident, ev = p[0], acc_of(p[1].split()[0]), float(p[2]), float(p[3])
            if qid not in qid2gene:
                continue
            if tgt == qid2acc[qid]:
                continue  # self
            if fident >= PARALOG_MIN_FIDENT and ev <= float(EVALUE) and tgt not in seen[qid2gene[qid]]:
                seen[qid2gene[qid]].add(tgt)
                counts[qid2gene[qid]] += 1
        paras.update(counts)
    return paras

def load_bypass(targets):
    cls = {}
    for ln in open(SYNLETH_CLASSES):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 2 or p[0] == "gene":
            continue
        cls[p[0].lower()] = p[1]
    bypass = {}; classname = {}
    for t in targets:
        c = cls.get(t["gene"].lower())
        classname[t["gene"]] = c if c else "not_in_metabolic_model"
        # bypassable (=higher liability) if isozyme-buffered or dispensable; monotherapy_robust or non-metabolic -> 0
        bypass[t["gene"]] = 1 if c in ("combination_required", "non_essential") else 0
    return bypass, classname

# ---- metrics (deterministic, no external stats deps required for AUROC/MWU) ----
def auroc(scores, labels):
    """AUROC with tie handling via Mann-Whitney rank formula. labels: 1=positive(HIGH)."""
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return float("nan")
    # rank all
    allv = sorted([(v, i) for i, v in enumerate(scores)])
    ranks = [0.0] * len(scores)
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # average rank (1-based)
        for k in range(i, j + 1):
            ranks[allv[k][1]] = avg
        i = j + 1
    sum_pos = sum(ranks[i] for i, l in enumerate(labels) if l == 1)
    n1 = len(pos); n2 = len(neg)
    u = sum_pos - n1 * (n1 + 1) / 2.0
    return round(u / (n1 * n2), 6)

def mannwhitney_p(scores, labels):
    """Two-sided Mann-Whitney U p-value via normal approx with tie & continuity correction."""
    import math
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    n1, n2 = len(pos), len(neg)
    allv = sorted(scores)
    ranks = {}
    i = 0
    ranklist = sorted([(v, i) for i, v in enumerate(scores)])
    r = [0.0] * len(scores)
    while i < len(ranklist):
        j = i
        while j + 1 < len(ranklist) and ranklist[j + 1][0] == ranklist[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[ranklist[k][1]] = avg
        i = j + 1
    sum_pos = sum(r[i] for i, l in enumerate(labels) if l == 1)
    u1 = sum_pos - n1 * (n1 + 1) / 2.0
    u = min(u1, n1 * n2 - u1)
    mu = n1 * n2 / 2.0
    # tie correction
    from collections import Counter
    tie = Counter([round(s, 9) for s in scores])
    n = n1 + n2
    tie_term = sum(t**3 - t for t in tie.values())
    sigma = math.sqrt((n1 * n2 / 12.0) * ((n + 1) - tie_term / (n * (n - 1))))
    if sigma == 0:
        return 1.0
    z = (abs(u - mu) - 0.5) / sigma
    p = 2.0 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
    return round(p, 8)

def minmax(d):
    vals = list(d.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 0.0 for k in d}
    return {k: round((v - lo) / (hi - lo), 6) for k, v in d.items()}

def main():
    t0 = time.time()
    gt = json.load(open(os.path.join(HERE, "ground_truth.json")))
    targets = gt["targets"]
    seqmap = extract_target_seqs(targets)
    qf = write_queries(seqmap)

    conservation = compute_conservation(seqmap, qf)
    paralogs = compute_paralogs(seqmap)
    bypass, classname = load_bypass(targets)
    paralog_norm = minmax(paralogs)

    rows = []
    for t in targets:
        g = t["gene"]
        f1 = round(1.0 - conservation[g], 6)                 # mutational tolerance
        f2 = int(t["prodrug_activator_dispensable"])          # activator dispensability
        f3 = paralog_norm[g]                                  # redundancy (normalized)
        f4 = bypass[g]                                         # metabolic bypass
        composite = round((f1 + f2 + f3 + f4) / 4.0, 6)
        composite_noF2 = round((f1 + f3 + f4) / 3.0, 6)
        rows.append({
            "gene": g, "drug": t["drug"], "source_org": t["source_org"],
            "liability": t["liability"], "label": 1 if t["liability"] == "HIGH" else 0,
            "ordinal": t["ordinal"], "clinical_exposure": t["clinical_exposure"],
            "conservation": conservation[g], "paralog_count": paralogs[g],
            "bypass_class": classname[g],
            "F1_mut_tolerance": f1, "F2_activator_dispensable": f2,
            "F3_redundancy": f3, "F4_bypass": f4,
            "composite_liability": composite, "composite_noF2": composite_noF2,
        })
    rows.sort(key=lambda x: (-x["composite_liability"], x["gene"]))

    labels = [r["label"] for r in rows]
    comp = [r["composite_liability"] for r in rows]
    comp_noF2 = [r["composite_noF2"] for r in rows]

    auroc_composite = auroc(comp, labels)
    p_composite = mannwhitney_p(comp, labels)
    auroc_noF2 = auroc(comp_noF2, labels)

    ablation = {
        "F1_mut_tolerance": auroc([r["F1_mut_tolerance"] for r in rows], labels),
        "F2_activator_dispensable": auroc([r["F2_activator_dispensable"] for r in rows], labels),
        "F3_redundancy": auroc([r["F3_redundancy"] for r in rows], labels),
        "F4_bypass": auroc([r["F4_bypass"] for r in rows], labels),
    }

    # drugged-only sensitivity: drop undrugged LOW cores
    drug_rows = [r for r in rows if r["clinical_exposure"] != "undrugged"]
    auroc_drugged = auroc([r["composite_liability"] for r in drug_rows],
                          [r["label"] for r in drug_rows])
    p_drugged = mannwhitney_p([r["composite_liability"] for r in drug_rows],
                              [r["label"] for r in drug_rows])

    GATE_AUROC = 0.70
    passed = (not (auroc_composite != auroc_composite)) and auroc_composite >= GATE_AUROC and p_composite < 0.05
    verdict = "PASS" if passed else "NEGATIVE"

    payload = {
        "n_total": len(rows), "n_high": sum(labels), "n_low": len(labels) - sum(labels),
        "gate_auroc_threshold": GATE_AUROC,
        "auroc_composite": auroc_composite,
        "mannwhitney_p_composite": p_composite,
        "auroc_composite_noF2": auroc_noF2,
        "ablation_per_feature_auroc": ablation,
        "drugged_only_auroc": auroc_drugged,
        "drugged_only_p": p_drugged,
        "drugged_only_n": len(drug_rows),
        "rows": rows,
    }
    payload_sha = sha256_payload(payload)

    metrics = {
        "experiment": "AMR1_resistance_liability",
        "payload": payload,
        "verdict": verdict,
        "pass": passed,
        "provenance": {
            "prereg_sha256": file_sha(os.path.join(HERE, "PREREG.md")),
            "ground_truth_sha256": file_sha(os.path.join(HERE, "ground_truth.json")),
            "mmseqs": subprocess.run([MMSEQS, "version"], capture_output=True, text=True).stdout.strip(),
            "panel": PANEL, "paralog_min_fident": PARALOG_MIN_FIDENT, "evalue": EVALUE,
            "synleth_classes": os.path.basename(SYNLETH_CLASSES),
            "runtime_sec": round(time.time() - t0, 2),
        },
    }
    resdir = os.path.join(HERE, "results"); os.makedirs(resdir, exist_ok=True)
    with open(os.path.join(resdir, "AMR1_metrics.json"), "w") as f:
        json.dump(metrics, f, sort_keys=True, indent=2)
    with open(os.path.join(resdir, "payload.sha256"), "w") as f:
        f.write(payload_sha + "\n")

    print(f"VERDICT={verdict}  AUROC_composite={auroc_composite}  p={p_composite}  "
          f"AUROC_noF2={auroc_noF2}  drugged_only_AUROC={auroc_drugged}")
    print("ablation:", json.dumps(ablation))
    print("payload_sha256:", payload_sha)
    for r in rows:
        print(f"  {r['liability']:4s} {r['gene']:6s} comp={r['composite_liability']:.3f} "
              f"F1={r['F1_mut_tolerance']:.2f} F2={r['F2_activator_dispensable']} "
              f"F3={r['F3_redundancy']:.2f} F4={r['F4_bypass']} "
              f"(cons={r['conservation']:.2f} par={r['paralog_count']} {r['bypass_class']})")

if __name__ == "__main__":
    main()
