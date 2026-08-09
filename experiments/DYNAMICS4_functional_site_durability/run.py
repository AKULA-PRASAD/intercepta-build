#!/usr/bin/env python
"""DYNAMICS4 — durability from UniProt-annotated FUNCTIONAL-SITE residues (Active/Binding/catalytic
Site), solving DYNAMICS3's wrong-pocket problem (fpocket's blind top pocket usually != the real drug
site). Drugs bind functional sites; for a characterized enzyme those sites are already annotated.

FROZEN METRIC: `masked_marginal` (ESM-2 t30 150M masked-marginal Shannon entropy) is copied VERBATIM
from DYNAMICS1/2/3, incl. the 1022-window pre-slice + drop-out-of-window logic (verbatim DYNAMICS3).
The metric is NOT changed. The ONLY change is the RESIDUE SET = UniProt-annotated functional site.

Deterministic, CPU-only, offline ESM. UniProt JSON fetch is cached (permitted, computational).
Run: ~/miniforge3/envs/intercepta/bin/python run.py
"""
import os, json, hashlib, time, urllib.request
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.metrics import roc_auc_score

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["TRANSFORMERS_OFFLINE"] = "1"

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
D4   = os.path.join(DATA, "dynamics4")
UNP  = os.path.join(D4, "uniprot"); LOGD = os.path.join(D4, "esm_logits")
for d in (UNP, LOGD): os.makedirs(d, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)
DYN2 = os.path.join(HERE, "..", "DYNAMICS2_durability_scaleup", "results", "DYNAMICS2_metrics.json")
DYN3 = os.path.join(HERE, "..", "DYNAMICS3_predicted_pocket_durability", "results", "DYNAMICS3_metrics.json")

ESM_MODEL = "facebook/esm2_t30_150M_UR50D"
HF_CACHE  = os.path.join(DATA, "hf_cache")
MAXLEN = 1022; AA20 = "ACDEFGHIKLMNPQRSTVWY"
FTYPES = ("Active site", "Binding site", "Site")

# ---- FROZEN accession + crystal-domain-span map (verbatim from DYNAMICS3 SIFTS resolution) ----
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
ISPE = ("ispE", "P62615", (1, 283))
MIN_FUNC_RES = 3; FEAS_MIN = 15
G1_RHO = 0.50; G1_P = 0.05; G2_AUROC = 0.75
OVERLAP_MIN_ABS = 0.25; OVERLAP_MIN_DELTA = 0.10
DYN3_FPOCKET_RHO = 0.714286
# Numbering-aligned bacterial/eukaryotic targets for the crystal-site-overlap head-to-head vs fpocket
# (DYNAMICS3-feasible with crystal auth_seq == UniProt numbering). Frozen in FEASIBILITY.md.
OVERLAP_SET = {"folP","inhA","parC","CYP51_Ca","HSV1_TK","alr","ddlB","dxr","glmU","mraY",
               "murA","murB","murD","murE","murF","murG"}

# ---------- UniProt fetch (cached) + functional-site residue extraction ----------
def get_uniprot(acc):
    path = os.path.join(UNP, f"{acc}.json")
    if os.path.exists(path) and os.path.getsize(path) > 500:
        return json.load(open(path))
    req = urllib.request.Request(f"https://rest.uniprot.org/uniprotkb/{acc}.json",
                                 headers={"User-Agent": "Mozilla/5.0 (research)"})
    data = urllib.request.urlopen(req, timeout=60).read()
    open(path, "wb").write(data)
    return json.loads(data)

def functional_residues(d, span):
    """Union of Active site + Binding site + catalytic Site residue positions within [span]."""
    res = set(); bytype = {t: set() for t in FTYPES}
    for f in d.get("features", []):
        if f["type"] in FTYPES:
            s = f["location"]["start"]["value"]; e = f["location"]["end"]["value"]
            if s is None or e is None: continue
            for p in range(s, e + 1):
                if span[0] <= p <= span[1]:
                    res.add(p); bytype[f["type"]].add(p)
    return sorted(res), {t: len(v) for t, v in bytype.items()}

# ---------- ESM-2 masked-marginal entropy (VERBATIM from DYNAMICS1/2/3) ----------
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

def func_site_durability(gene, acc, span):
    """Full pipeline for one accession -> feasibility + functional-site durability."""
    r = {"gene": gene, "acc": acc, "crystal_domain_span": list(span)}
    d = get_uniprot(acc)
    seq = d["sequence"]["value"]; r["seq_len"] = len(seq)
    fres, bytype = functional_residues(d, span)
    r["n_func_residues"] = len(fres); r["func_residues"] = fres
    r["func_by_type"] = {"active_site": bytype["Active site"],
                         "binding_site": bytype["Binding site"], "catalytic_site": bytype["Site"]}
    if len(fres) < MIN_FUNC_RES:
        r.update(feasible=False, reason=f"{len(fres)} functional-site residues (<{MIN_FUNC_RES})")
        return r
    cidx = sorted(p - 1 for p in fres)  # UniProt pos -> canonical seq index
    # frozen 1022-window pre-slice + drop-out-of-window (VERBATIM logic from DYNAMICS3)
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
    r.update(feasible=True, reason="functional site annotated",
             n_func_residues_scored=len(ents), n_func_residues_dropped_outofwindow=n_dropped,
             func_entropies=[round(e, 6) for e in ents],
             functional_site_durability=round(float(np.mean(ents)), 6),
             functional_site_max_entropy=round(float(np.max(ents)), 6))
    return r

def main():
    t0 = time.time()
    dyn2 = json.load(open(DYN2))
    crystal = {t["gene"]: {"y": t["y"], "label": t["label"], "cls": t["cls"],
                           "crystal_durability": t["mean_entropy"],
                           "crystal_contacts": t["contact_residues"]}
               for t in dyn2["payload"]["per_target"]}
    dyn3 = json.load(open(DYN3))
    fpocket = {t["gene"]: {"predicted_pocket_durability": t.get("predicted_pocket_durability"),
                           "crystal_site_overlap": t.get("crystal_site_overlap"),
                           "feasible": t.get("feasible")}
               for t in dyn3["payload"]["per_target"]}

    per = []
    for gene, (acc, span) in ACC.items():
        r = func_site_durability(gene, acc, span)
        c = crystal[gene]
        r.update(y=c["y"], label=c["label"], cls=c["cls"], crystal_durability=c["crystal_durability"])
        # annotated crystal-site overlap (only meaningful where numbering aligns -> OVERLAP_SET)
        r["crystal_site_overlap"] = None
        if r.get("feasible") and gene in OVERLAP_SET:
            cr = set()
            for res in c["crystal_contacts"]:
                num = ''.join(ch for ch in res if ch.isdigit())
                if num: cr.add(int(num))
            fs = set(r["func_residues"])
            if cr:
                r["crystal_site_overlap"] = {"n_crystal_contacts": len(cr),
                    "n_recovered": len(cr & fs),
                    "frac_recovered": round(len(cr & fs) / len(cr), 4)}
        per.append(r)
        tag = "FEAS" if r.get("feasible") else "----"
        ov = r["crystal_site_overlap"]
        print(f"{gene:10s} {acc} {tag} nfunc={r.get('n_func_residues'):>2} "
              f"funcH={r.get('functional_site_durability')} crysH={c['crystal_durability']} "
              f"ovl={ov['frac_recovered'] if ov else None} "
              f"{'' if r.get('feasible') else '('+r['reason']+')'}", flush=True)

    feas = [r for r in per if r.get("feasible")]
    n_feas = len(feas); feasibility_pass = n_feas >= FEAS_MIN

    def spear_auroc(rows):
        p = np.array([r["functional_site_durability"] for r in rows])
        c = np.array([r["crystal_durability"] for r in rows]); y = np.array([r["y"] for r in rows])
        rho, rp = spearmanr(p, c)
        au = float(roc_auc_score(y, p)) if len(set(y)) > 1 else float("nan")
        hi = p[y == 1]; lo = p[y == 0]
        mp = float(mannwhitneyu(hi, lo, alternative="two-sided").pvalue) if (len(hi) and len(lo)) else float("nan")
        return rho, rp, au, mp, len(rows), int(y.sum()), int((1 - y).sum())

    # ---- G1 + G2 over full feasible set ----
    rho, rp, au, mp, n, nh, nl = spear_auroc(feas)
    g1 = {"spearman_rho": round(float(rho), 6), "p": round(float(rp), 6), "n": n,
          "dynamics3_fpocket_rho": DYN3_FPOCKET_RHO, "beats_fpocket": bool(rho > DYN3_FPOCKET_RHO),
          "pass": bool(rho >= G1_RHO and rp < G1_P)}
    g2 = {"auroc": round(float(au), 6), "mwu_p": round(float(mp), 6), "n": n, "n_high": nh, "n_low": nl,
          "pass": bool(au >= G2_AUROC)}

    # ---- head-to-head vs fpocket on the numbering-aligned intersection ----
    inter = [r for r in feas if r["gene"] in OVERLAP_SET and fpocket.get(r["gene"], {}).get("feasible")]
    inter_genes = sorted(r["gene"] for r in inter)
    hro, hrp, hau, hmp, hn, hnh, hnl = spear_auroc(inter)
    # fpocket recomputed on the SAME intersection
    fp_pred = np.array([fpocket[r["gene"]]["predicted_pocket_durability"] for r in inter])
    fp_crys = np.array([r["crystal_durability"] for r in inter])
    fp_y = np.array([r["y"] for r in inter])
    fp_rho, fp_rp = spearmanr(fp_pred, fp_crys)
    fp_au = float(roc_auc_score(fp_y, fp_pred)) if len(set(fp_y)) > 1 else float("nan")
    # crystal-site overlap means on the intersection
    ann_ov = [r["crystal_site_overlap"]["frac_recovered"] for r in inter if r["crystal_site_overlap"]]
    fp_ov  = [fpocket[r["gene"]]["crystal_site_overlap"]["frac_recovered"]
              for r in inter if fpocket[r["gene"]].get("crystal_site_overlap")]
    ann_ov_mean = round(float(np.mean(ann_ov)), 6) if ann_ov else None
    fp_ov_mean  = round(float(np.mean(fp_ov)), 6) if fp_ov else None
    overlap_gate = bool(ann_ov_mean is not None and fp_ov_mean is not None
                        and ann_ov_mean >= OVERLAP_MIN_ABS
                        and ann_ov_mean >= fp_ov_mean + OVERLAP_MIN_DELTA)
    headtohead = {
        "intersection_genes": inter_genes, "n": hn, "n_high": hnh, "n_low": hnl,
        "annotated_rho": round(float(hro), 6), "annotated_rho_p": round(float(hrp), 6),
        "annotated_auroc": round(float(hau), 6), "annotated_auroc_mwu_p": round(float(hmp), 6),
        "fpocket_rho": round(float(fp_rho), 6), "fpocket_rho_p": round(float(fp_rp), 6),
        "fpocket_auroc": round(float(fp_au), 6),
        "annotated_mean_crystal_overlap": ann_ov_mean, "fpocket_mean_crystal_overlap": fp_ov_mean,
        "annotated_beats_fpocket_rho": bool(hro > fp_rho),
        "annotated_beats_fpocket_overlap": bool(ann_ov_mean is not None and fp_ov_mean is not None
                                                 and ann_ov_mean > fp_ov_mean),
    }
    overlap = {"annotated_mean_overlap": ann_ov_mean, "fpocket_mean_overlap": fp_ov_mean,
               "min_abs": OVERLAP_MIN_ABS, "min_delta": OVERLAP_MIN_DELTA, "pass": overlap_gate,
               "n_overlap_targets": len(ann_ov)}

    # ---- verdict ----
    blocks = [g1["pass"], overlap_gate, g2["pass"]]
    nblk = sum(blocks)
    if not feasibility_pass:
        verdict = "INFEASIBLE"
    elif nblk == 3:
        verdict = "SOLVED_STRONG" if bool(rho > DYN3_FPOCKET_RHO) else "SOLVED"
    elif nblk == 2:
        verdict = "PARTIAL"
    else:
        verdict = "NEGATIVE"

    # ---- APPLICATION: ispE ----
    gene, acc, span = ISPE
    ispe = func_site_durability(gene, acc, span)
    print(f"{gene:10s} {acc} {'FEAS' if ispe.get('feasible') else '----'} "
          f"nfunc={ispe.get('n_func_residues')} funcH={ispe.get('functional_site_durability')}", flush=True)

    payload = {
        "metric": "mean ESM-2 t30 150M masked-marginal Shannon entropy over UniProt-annotated "
                  "FUNCTIONAL-SITE residues (Active site + Binding site + catalytic Site) within the "
                  "crystal domain span [FROZEN metric from DYNAMICS1/2/3; residue set = annotated functional site]",
        "frozen_from": "DYNAMICS1/2/3 masked_marginal (verbatim); crystal durability from DYNAMICS2; fpocket baseline from DYNAMICS3",
        "gates": {"feasibility_min": FEAS_MIN, "min_func_residues": MIN_FUNC_RES,
                  "G1_rho_min": G1_RHO, "G1_p_max": G1_P, "G2_auroc_min": G2_AUROC,
                  "overlap_min_abs": OVERLAP_MIN_ABS, "overlap_min_delta": OVERLAP_MIN_DELTA,
                  "dynamics3_fpocket_rho": DYN3_FPOCKET_RHO},
        "n_targets": len(per),
        "feasibility": {"n_feasible": n_feas, "n_total": len(per), "pass": bool(feasibility_pass),
                        "infeasible": sorted([r["gene"] for r in per if not r.get("feasible")])},
        "G1_agreement_functional_vs_crystal": g1,
        "G2_discrimination_high_vs_low": g2,
        "crystal_site_overlap_vs_fpocket": overlap,
        "headtohead_vs_fpocket_intersection": headtohead,
        "ispE_application": {k: ispe.get(k) for k in
            ("gene", "acc", "feasible", "reason", "n_func_residues", "func_residues",
             "functional_site_durability", "functional_site_max_entropy", "func_entropies")},
        "per_target": sorted(per, key=lambda r: (0 if r.get("feasible") else 1, -r["y"], r["cls"], r["gene"])),
        "reference": {"dynamics2_crystal_auroc": dyn2["payload"]["primary_mean_entropy"]["auroc"],
                      "dynamics2_crystal_mwu_p": dyn2["payload"]["primary_mean_entropy"]["mwu_p"],
                      "dynamics3_fpocket_auroc": dyn3["payload"]["G2_discrimination_high_vs_low"]["auroc"],
                      "dynamics3_fpocket_rho": dyn3["payload"]["G1_agreement_predicted_vs_crystal"]["spearman_rho"]},
    }
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    sha = hashlib.sha256(payload_str.encode()).hexdigest()

    out = {"experiment": "DYNAMICS4_functional_site_durability", "verdict": verdict, "payload": payload,
           "provenance": {"esm_env": "intercepta (torch/transformers)", "model": ESM_MODEL,
                          "annotations": "UniProt REST .json (cached, per accession)",
                          "runtime_s": round(time.time() - t0, 1)}}
    json.dump(out, open(os.path.join(RES, "DYNAMICS4_metrics.json"), "w"), indent=2, sort_keys=True)
    open(os.path.join(RES, "payload.sha256"), "w").write(sha + "\n")

    print("\n=== DYNAMICS4 RESULT ===")
    print(f"FEASIBILITY: {n_feas}/{len(per)} annotated (need >={FEAS_MIN}) -> {'PASS' if feasibility_pass else 'FAIL'}"
          f"  infeasible={payload['feasibility']['infeasible']}")
    print(f"G1 agreement: rho={g1['spearman_rho']} p={g1['p']} (need rho>={G1_RHO},p<{G1_P}; fpocket 0.714, "
          f"beats={g1['beats_fpocket']}) -> {'PASS' if g1['pass'] else 'FAIL'}")
    print(f"CRYSTAL-SITE OVERLAP: annotated mean={overlap['annotated_mean_overlap']} vs fpocket "
          f"mean={overlap['fpocket_mean_overlap']} (need >={OVERLAP_MIN_ABS} & +{OVERLAP_MIN_DELTA}) -> "
          f"{'PASS' if overlap_gate else 'FAIL'}")
    print(f"G2 discrimination: AUROC={g2['auroc']} MWU_p={g2['mwu_p']} ({g2['n_high']}H/{g2['n_low']}L, "
          f"need >={G2_AUROC}) -> {'PASS' if g2['pass'] else 'FAIL'}")
    print(f"HEAD-TO-HEAD (n={hn} intersection): annotated rho={headtohead['annotated_rho']} "
          f"AUROC={headtohead['annotated_auroc']} overlap={headtohead['annotated_mean_crystal_overlap']}  |  "
          f"fpocket rho={headtohead['fpocket_rho']} AUROC={headtohead['fpocket_auroc']} "
          f"overlap={headtohead['fpocket_mean_crystal_overlap']}")
    print(f"ispE functional-site durability = {ispe.get('functional_site_durability')} "
          f"(DYNAMICS3 fpocket 1.89)")
    print(f"VERDICT: {verdict}")
    print(f"payload sha256: {sha}")

if __name__ == "__main__":
    main()
