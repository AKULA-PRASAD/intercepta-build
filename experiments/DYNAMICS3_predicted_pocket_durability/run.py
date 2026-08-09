#!/usr/bin/env python
"""DYNAMICS3 — does the durability signal extend from DRUG-BOUND-crystal contact residues to
fpocket-PREDICTED pockets on apo AlphaFold structures (so it applies to novel/undrugged targets)?

FROZEN METRIC: `masked_marginal` (ESM-2 t30 150M masked-marginal Shannon entropy) is copied VERBATIM
from DYNAMICS1/2. The metric is NOT changed. The ONLY change is the RESIDUE SET: the top fpocket
pocket-lining residues of the AlphaFold model, instead of crystal drug-contact residues.

Deterministic, CPU-only, offline ESM. AlphaFold fetch is cached (permitted, computational).
Run: ~/miniforge3/envs/intercepta/bin/python run.py   (needs fpocket on PATH or FPOCKET_BIN set)
"""
import os, sys, json, hashlib, time, subprocess, urllib.request
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.metrics import roc_auc_score

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["TRANSFORMERS_OFFLINE"] = "1"

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D3   = os.path.join(DATA, "dynamics3")
AFD  = os.path.join(D3, "af"); FPD = os.path.join(D3, "fpocket"); LOGD = os.path.join(D3, "esm_logits")
for d in (AFD, FPD, LOGD): os.makedirs(d, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)
DYN2 = os.path.join(HERE, "..", "DYNAMICS2_durability_scaleup", "results", "DYNAMICS2_metrics.json")

ESM_MODEL = "facebook/esm2_t30_150M_UR50D"
HF_CACHE  = os.path.join(DATA, "hf_cache")
MAXLEN = 1022; AA20 = "ACDEFGHIKLMNPQRSTVWY"
FPOCKET = os.environ.get("FPOCKET_BIN", os.path.expanduser("~/miniconda3/envs/bioinfo/bin/fpocket"))
MIN_POCKET_RES = 5; COVERAGE_MIN = 0.5; FEAS_MIN = 18
G1_RHO = 0.50; G1_P = 0.05; G2_AUROC = 0.70

# ---- FROZEN accession map (largest-span SIFTS rule) + crystal domain span [min_unp_start,max_unp_end] ----
ACC = {
 "embB":("P9WNL7",(1,1098)), "folP":("P0AC13",(1,282)), "gyrA":("Q99XG5",(2,491)),
 "inhA":("P9WGR1",(2,269)), "parC":("Q59961",(404,647)), "rpoB":("Q9KWU7",(1,1119)),
 "rpsL":("Q5SHN3",(1,132)), "CYP51_Ca":("P10613",(49,528)), "FLU_NA":("Q6DPL2",(63,449)),
 "FLU_PA":("C3W5S0",(1,198)), "HCV_NS3":("A8DG50",(1013,1208)), "HIV1_PR":("Q9Q288",(1,99)),
 "HIV1_RT":("P04585",(588,1147)), "HSV1_TK":("P0DTH5",(46,376)), "alr":("P10724",(2,388)),
 "ddlB":("P07862",(1,306)), "dxr":("P45568",(1,398)), "glmU":("P0ACC7",(1,456)),
 "mraY":("O66465",(1,359)), "murA":("P0A749",(1,419)), "murB":("P08373",(3,342)),
 "murD":("P14900",(2,438)), "murE":("P22188",(2,495)), "murF":("Q8DNV6",(1,454)),
 "murG":("P17443",(2,355)), "HCV_NS5B":("Q99IB8",(2443,3012)),
}
ISPE = ("ispE", "P62615", (1, 283))  # DURABLETARGETS1 NA core: E. coli IspE

AA3 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G',
 'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S',
 'THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

# ---------- AlphaFold fetch (cached) ----------
def get_af(acc):
    path = os.path.join(AFD, f"AF-{acc}-F1.pdb")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    api = json.load(urllib.request.urlopen(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}", timeout=60))
    urllib.request.urlretrieve(api[0]["pdbUrl"], path)
    return path

def parse_af(path):
    """AlphaFold PDB (single chain A). Return seq, ordered resnums, resnum->seqindex."""
    seq = []; resnums = []
    for line in open(path):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            aa = AA3.get(line[17:20].strip(), "X"); rn = int(line[22:26])
            seq.append(aa); resnums.append(rn)
    idx_of = {rn: i for i, rn in enumerate(resnums)}
    return "".join(seq), resnums, idx_of

def af_meta(path):
    res = [int(l[22:26]) for l in open(path) if l.startswith("ATOM") and l[12:16].strip() == "CA"]
    return {"n_res": len(res), "res_min": min(res), "res_max": max(res),
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}

def coverage(res_min, res_max, span):
    s, e = span; ov = max(0, min(res_max, e) - max(res_min, s) + 1)
    return ov / (e - s + 1)

# ---------- fpocket top pocket (cached residue list) ----------
def top_pocket_residues(acc, path):
    cache = os.path.join(FPD, f"{acc}_pocket1.json")
    if os.path.exists(cache):
        return json.load(open(cache))
    work = os.path.join(FPD, f"AF-{acc}-F1.pdb")
    if not os.path.exists(work):
        import shutil; shutil.copy(path, work)
    outdir = os.path.join(FPD, f"AF-{acc}-F1_out")
    if not os.path.isdir(outdir):
        subprocess.run([FPOCKET, "-f", work], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p1 = os.path.join(outdir, "pockets", "pocket1_atm.pdb")
    resset = {}
    if os.path.exists(p1):
        for line in open(p1):
            if line.startswith("ATOM"):
                rn = int(line[22:26]); resset[rn] = AA3.get(line[17:20].strip(), "X")
    res = sorted(resset.keys())
    out = {"pocket1_resnums": res, "pocket1_resaa": [resset[r] for r in res],
           "n_pockets_exist": os.path.isdir(os.path.join(outdir, "pockets"))}
    json.dump(out, open(cache, "w"), sort_keys=True)
    return out

# ---------- ESM-2 masked-marginal entropy (VERBATIM from DYNAMICS1/2) ----------
_ESM = {}
def get_esm():
    if _ESM: return _ESM['tok'], _ESM['mod'], _ESM['tt']
    import torch
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    torch.manual_seed(0); torch.use_deterministic_algorithms(True, warn_only=True)
    tok = AutoTokenizer.from_pretrained(ESM_MODEL, cache_dir=HF_CACHE)
    mod = AutoModelForMaskedLM.from_pretrained(ESM_MODEL, cache_dir=HF_CACHE).eval()
    aa_ids = [tok.get_vocab()[a] for a in AA20]
    _ESM.update(tok=tok, mod=mod, tt=torch, aa_ids=aa_ids); _ESM['torch'] = torch
    return tok, mod, torch

def masked_marginal(gene, seq, contact_idx):
    """Return dict idx-> {entropy, sub_llr} via masked-marginal over 20 AA. Cached. VERBATIM metric."""
    cache = os.path.join(LOGD, f"{gene}_mm.json")
    if os.path.exists(cache):
        return {int(k): v for k, v in json.load(open(cache)).items()}
    tok, mod, torch = get_esm(); aa_ids = _ESM['aa_ids']
    L = len(seq); off = 0
    if L > MAXLEN:
        med = int(np.median(contact_idx)); half = MAXLEN // 2
        off = min(max(0, med - half), L - MAXLEN); seq = seq[off:off + MAXLEN]
    cidx = [i - off for i in contact_idx]
    enc = tok(seq, return_tensors="pt")
    ids = enc["input_ids"][0].clone()
    mask_id = tok.mask_token_id
    out = {}
    aa_ids_t = torch.tensor(aa_ids)
    with torch.no_grad():
        for ci, orig_i in zip(cidx, contact_idx):
            tpos = ci + 1
            batch = ids.clone(); wt_tok = int(batch[tpos]); batch[tpos] = mask_id
            logits = mod(input_ids=batch.unsqueeze(0),
                         attention_mask=enc["attention_mask"]).logits[0, tpos]
            aa_logits = logits[aa_ids_t]
            logp = torch.log_softmax(aa_logits, dim=0)
            p = logp.exp()
            H = float(-(p * logp).sum())
            wt_aa = AA20.find(tok.convert_ids_to_tokens(wt_tok))
            if wt_aa >= 0:
                mask = torch.ones(len(AA20), dtype=torch.bool); mask[wt_aa] = False
                sub_llr = float((logp[mask] - logp[wt_aa]).mean())
            else:
                sub_llr = float('nan')
            out[orig_i] = {'entropy': round(H, 6), 'sub_llr': round(sub_llr, 6)}
    json.dump({str(k): v for k, v in out.items()}, open(cache, 'w'))
    return out

def predicted_durability(gene, acc, span):
    """Full pipeline for one accession -> feasibility + predicted-pocket durability."""
    r = {"gene": gene, "acc": acc, "crystal_domain_span": list(span)}
    try:
        path = get_af(acc)
    except Exception as e:
        r.update(feasible=False, reason=f"AF-DB fetch failed ({type(e).__name__})"); return r
    m = af_meta(path); r.update(m)
    cov = coverage(m["res_min"], m["res_max"], span); r["domain_coverage"] = round(cov, 4)
    if cov < COVERAGE_MIN:
        r.update(feasible=False, reason=f"AF F1 model covers {cov:.0%} of crystal domain (<50%)"); return r
    pk = top_pocket_residues(acc, path)
    r["n_pocket_residues"] = len(pk["pocket1_resnums"])
    if len(pk["pocket1_resnums"]) < MIN_POCKET_RES:
        r.update(feasible=False, reason=f"pocket1 has {len(pk['pocket1_resnums'])} residues (<{MIN_POCKET_RES})"); return r
    seq, resnums, idx_of = parse_af(path)
    cidx = sorted(idx_of[rn] for rn in pk["pocket1_resnums"] if rn in idx_of)
    # Frozen-metric windowing: ESM t30 caps at 1022 residues. For proteins >1022 the frozen
    # masked_marginal centres a 1022 window on the median target index. A predicted pocket on a
    # large multidomain protein can span sequence positions wider than 1022, so out-of-window
    # residues cannot be scored -- pre-slice with the SAME frozen formula and DROP (count) them,
    # leaving masked_marginal byte-identical (it receives a <=MAXLEN sequence -> off=0).
    n_dropped = 0
    if len(seq) > MAXLEN:
        med = int(np.median(cidx)); half = MAXLEN // 2
        off = min(max(0, med - half), len(seq) - MAXLEN)
        win = seq[off:off + MAXLEN]
        kept = [i - off for i in cidx if off <= i < off + MAXLEN]
        n_dropped = len(cidx) - len(kept)
        mm = masked_marginal(f"{gene}_{acc}", win, kept)
        ents = [mm[i]["entropy"] for i in kept]
    else:
        mm = masked_marginal(f"{gene}_{acc}", seq, cidx)
        ents = [mm[i]["entropy"] for i in cidx]
    r.update(feasible=True, reason="usable top pocket", n_pocket_residues_scored=len(ents),
             n_pocket_residues_dropped_outofwindow=n_dropped,
             pocket1_resnums=pk["pocket1_resnums"], pocket1_resaa=pk["pocket1_resaa"],
             pocket1_entropies=[round(e, 6) for e in ents],
             predicted_pocket_durability=round(float(np.mean(ents)), 6),
             predicted_pocket_max_entropy=round(float(np.max(ents)), 6))
    return r

def main():
    t0 = time.time()
    dyn2 = json.load(open(DYN2))
    crystal = {t["gene"]: {"y": t["y"], "label": t["label"], "cls": t["cls"],
                           "crystal_durability": t["mean_entropy"],
                           "crystal_contacts": t["contact_residues"]}
               for t in dyn2["payload"]["per_target"]}

    per = []
    for gene, (acc, span) in ACC.items():
        r = predicted_durability(gene, acc, span)
        c = crystal[gene]
        r.update(y=c["y"], label=c["label"], cls=c["cls"], crystal_durability=c["crystal_durability"])
        per.append(r)
        tag = "FEAS" if r.get("feasible") else "----"
        pv = r.get("predicted_pocket_durability")
        print(f"{gene:10s} {acc} {tag} cov={r.get('domain_coverage')} "
              f"npk={r.get('n_pocket_residues')} predH={pv} crysH={c['crystal_durability']} "
              f"{'' if r.get('feasible') else '('+r['reason']+')'}", flush=True)

    feas = [r for r in per if r.get("feasible")]
    n_feas = len(feas)
    feasibility_pass = n_feas >= FEAS_MIN

    # ---- G1 agreement (Spearman predicted vs crystal durability, over feasible) ----
    pred = np.array([r["predicted_pocket_durability"] for r in feas])
    crys = np.array([r["crystal_durability"] for r in feas])
    yv   = np.array([r["y"] for r in feas])
    rho, rho_p = spearmanr(pred, crys)
    g1 = {"spearman_rho": round(float(rho), 6), "p": round(float(rho_p), 6),
          "n": n_feas, "pass": bool(rho >= G1_RHO and rho_p < G1_P)}

    # ---- G2 discrimination (AUROC predicted durability vs HIGH) ----
    hi = pred[yv == 1]; lo = pred[yv == 0]
    auroc = float(roc_auc_score(yv, pred))
    mwu_p = float(mannwhitneyu(hi, lo, alternative="two-sided").pvalue)
    g2 = {"auroc": round(auroc, 6), "mwu_p": round(mwu_p, 6),
          "n": n_feas, "n_high": int(yv.sum()), "n_low": int((1 - yv).sum()),
          "pass": bool(auroc >= G2_AUROC)}

    # ---- secondary: abx-only feasible subset ----
    fab = [r for r in feas if r["cls"] == "abx"]
    def sub(rows):
        if len({r["y"] for r in rows}) < 2 or len(rows) < 4: return None
        p = np.array([r["predicted_pocket_durability"] for r in rows])
        c = np.array([r["crystal_durability"] for r in rows]); y = np.array([r["y"] for r in rows])
        rr, rp = spearmanr(p, c)
        return {"n": len(rows), "spearman_rho": round(float(rr), 6), "spearman_p": round(float(rp), 6),
                "auroc": round(float(roc_auc_score(y, p)), 6)}
    abx_only = sub(fab)

    # ---- secondary: crystal-site overlap where numbering shared (descriptive) ----
    def crys_overlap(r):
        if not r.get("feasible"): return None
        cr = set()
        for res in crystal[r["gene"]]["crystal_contacts"]:
            num = ''.join(ch for ch in res if ch.isdigit())
            if num: cr.add(int(num))
        pk = set(r["pocket1_resnums"])
        if not cr: return None
        return {"n_crystal_contacts": len(cr), "n_recovered": len(cr & pk),
                "frac_recovered": round(len(cr & pk) / len(cr), 4)}
    for r in per:
        r["crystal_site_overlap"] = crys_overlap(r)

    # ---- verdict ----
    if not feasibility_pass:
        verdict = "INFEASIBLE"
    elif g1["pass"] and g2["pass"]:
        verdict = "PASS"
    elif g1["pass"] or g2["pass"]:
        verdict = "PARTIAL"
    else:
        verdict = "NEGATIVE"

    # ---- APPLICATION: fill DURABLETARGETS1 NA (ispE) ----
    gene, acc, span = ISPE
    ispe = predicted_durability(gene, acc, span)
    print(f"{gene:10s} {acc} {'FEAS' if ispe.get('feasible') else '----'} "
          f"predH={ispe.get('predicted_pocket_durability')}", flush=True)

    payload = {
        "metric": "mean ESM-2 t30 150M masked-marginal Shannon entropy over TOP-fpocket-pocket residues "
                  "of the apo AlphaFold structure [FROZEN metric from DYNAMICS1/2; residue set = predicted pocket]",
        "frozen_from": "DYNAMICS1/2 masked_marginal (verbatim); crystal durability read from DYNAMICS2 metrics",
        "gates": {"feasibility_min": FEAS_MIN, "G1_rho_min": G1_RHO, "G1_p_max": G1_P, "G2_auroc_min": G2_AUROC},
        "n_targets": len(per),
        "feasibility": {"n_feasible": n_feas, "n_total": len(per), "pass": bool(feasibility_pass),
                        "infeasible": sorted([r["gene"] for r in per if not r.get("feasible")])},
        "G1_agreement_predicted_vs_crystal": g1,
        "G2_discrimination_high_vs_low": g2,
        "secondary_abx_only": abx_only,
        "ispE_application": {k: ispe.get(k) for k in
            ("gene","acc","feasible","reason","domain_coverage","n_pocket_residues",
             "predicted_pocket_durability","predicted_pocket_max_entropy","pocket1_resnums","pocket1_entropies")},
        "per_target": sorted(per, key=lambda r: (0 if r.get("feasible") else 1, -r["y"], r["cls"], r["gene"])),
        "reference": {"dynamics2_crystal_auroc": dyn2["payload"]["primary_mean_entropy"]["auroc"],
                      "dynamics2_crystal_mwu_p": dyn2["payload"]["primary_mean_entropy"]["mwu_p"]},
    }
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    sha = hashlib.sha256(payload_str.encode()).hexdigest()

    out = {"experiment": "DYNAMICS3_predicted_pocket_durability", "verdict": verdict, "payload": payload,
           "provenance": {"esm_env": "intercepta (torch/transformers)", "model": ESM_MODEL,
                          "fpocket": FPOCKET, "structures": "AlphaFold DB F1 (cached, sha per target)",
                          "runtime_s": round(time.time() - t0, 1)}}
    json.dump(out, open(os.path.join(RES, "DYNAMICS3_metrics.json"), "w"), indent=2, sort_keys=True)
    open(os.path.join(RES, "payload.sha256"), "w").write(sha + "\n")

    print("\n=== DYNAMICS3 RESULT ===")
    print(f"FEASIBILITY: {n_feas}/{len(per)} usable (need >={FEAS_MIN}) -> {'PASS' if feasibility_pass else 'FAIL'}"
          f"  infeasible={payload['feasibility']['infeasible']}")
    print(f"G1 agreement: Spearman rho={g1['spearman_rho']} p={g1['p']} (need rho>={G1_RHO},p<{G1_P}) -> {'PASS' if g1['pass'] else 'FAIL'}")
    print(f"G2 discrimination: AUROC={g2['auroc']} MWU_p={g2['mwu_p']} ({g2['n_high']}H/{g2['n_low']}L, need AUROC>={G2_AUROC}) -> {'PASS' if g2['pass'] else 'FAIL'}")
    print(f"  abx-only feasible: {abx_only}")
    print(f"ispE (DURABLETARGETS1 NA) predicted-pocket durability = {ispe.get('predicted_pocket_durability')}")
    print(f"VERDICT: {verdict}")
    print(f"payload sha256: {sha}")

if __name__ == "__main__":
    main()
