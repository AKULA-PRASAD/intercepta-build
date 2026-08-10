#!/usr/bin/env python
"""DYNAMICS5 - within-protein paired resistance-site mutational-tolerance test.

Question (PREREG.md, LOCKED): is ESM-2 masked-marginal Shannon entropy HIGHER at documented
resistance-conferring positions than at matched-control positions in the SAME protein?
Each protein is its own control -> firms DYNAMICS1's n-fragile (n=15) target-level demonstration
at position scale (n~1162, within-protein-controlled).

FROZEN metric == the DYNAMICS1-4 arc: facebook/esm2_t30_150M_UR50D, CPU, deterministic eval.
Per position i: mask i, softmax over the 20 standard AA at i, Shannon entropy H = -sum(p*logp)
computed with torch.log_softmax (NATURAL LOG) => entropy in NATS (max = ln20 ~ 2.9957).
1022-residue windowing verbatim from DYNAMICS1 (window centred on median of sites-of-interest,
clamped to [0, L-1022]). Entropy is computed BLIND to labels, THEN compared -> non-circular.

Data: CARD card.json protein-variant-model entries (target-alteration resistance). Reference
protein sequence + WT-verified positions from model_param.snp.param_value ([WT][pos][mut], kept
iff 1<=pos<=L and seq[pos-1]==WT). Reproduces 198 targets / 1162 WT-verified positions.

Inference is cached to $INTERCEPTA_DATA/dynamics5/ent_<ARO>.npz so downstream scoring is
deterministic and byte-reproducible. Re-running is idempotent (resume-safe).

Run: ~/miniforge3/envs/intercepta/bin/python run.py
PREREG is FROZEN; this script does not tune to pass. CPU-only, offline. Never git-committed.
"""
import os, sys, re, json, time, hashlib
import numpy as np

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

DATA     = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
CARD     = os.path.join(DATA, "card", "card.json")
STAGED   = os.path.join(DATA, "card", "dynamics5_high_targets.json")
D5       = os.path.join(DATA, "dynamics5")
HF_CACHE = os.path.join(DATA, "hf_cache")
HERE     = os.path.dirname(os.path.abspath(__file__))
RES      = os.path.join(HERE, "results")
os.makedirs(D5, exist_ok=True)
os.makedirs(RES, exist_ok=True)

ESM_MODEL  = "facebook/esm2_t30_150M_UR50D"
MAXLEN     = 1022
AA20       = "ACDEFGHIKLMNPQRSTVWY"
TERM_GUARD = 5      # exclude 5 residues from each end of the encoded window (termini artefact)
LOCAL_W    = 10     # +/- window for local-context sensitivity control
N_DRAWS    = 20     # size-matched control draws averaged, per PREREG
N_PERM     = 2000   # protein-clustered permutation null, per PREREG
RNG_SEED   = 0

def ctrl_size(n):   # PREREG-locked control-pool size: min(available, max(20, 4*n_res))
    return max(20, 4 * n)

def sanitize(s):
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(s))

# ----------------------------------------------------------------------------- parse CARD
def parse_targets():
    c = json.load(open(CARD))
    targets = []
    for _, v in c.items():
        if not (isinstance(v, dict) and v.get("model_type") == "protein variant model"):
            continue
        seqs = v["model_sequences"]["sequence"]
        skey = sorted(seqs.keys())[0]
        seq  = seqs[skey]["protein_sequence"]["sequence"]
        pv   = (v.get("model_param", {}).get("snp", {}) or {}).get("param_value", {})
        pos  = set()
        for mut in pv.values():
            m = re.match(r"^([A-Z])(\d+)", mut)
            if not m:
                continue
            wt, p = m.group(1), int(m.group(2))
            if wt in AA20 and 1 <= p <= len(seq) and seq[p - 1] == wt:
                pos.add(p)
        if pos:
            targets.append({
                "aro":   str(v["ARO_accession"]),
                "short": v.get("CARD_short_name"),
                "name":  v.get("ARO_name"),
                "seq":   seq,
                "res1":  sorted(pos),          # 1-based verified resistance positions
            })
    targets.sort(key=lambda t: t["aro"])       # fixed order -> deterministic
    return targets

# ----------------------------------------------------------------------------- windowing + sets
def build_sets(t):
    """Return the within-window resistance / random-control / local-control 0-based GLOBAL indices."""
    seq = t["seq"]; L = len(seq)
    idx0 = np.array([p - 1 for p in t["res1"]], dtype=np.int64)   # 0-based
    off = 0
    if L > MAXLEN:                                                # verbatim DYNAMICS1 windowing
        med  = int(np.median(idx0))
        half = MAXLEN // 2
        off  = min(max(0, med - half), L - MAXLEN)
    winlen = min(MAXLEN, L)
    lo, hi = off, off + winlen                                   # encoded window [lo, hi)
    res     = [int(i) for i in idx0 if lo <= i < hi]
    dropped = [int(i) + 1 for i in idx0 if not (lo <= i < hi)]   # 1-based, out-of-window (reported)
    glo, ghi = lo + TERM_GUARD, hi - TERM_GUARD                  # guarded window (drop terminal artefact)
    resset = set(res)
    nres = len(res)

    avail = [i for i in range(glo, ghi) if i not in resset]
    rng = np.random.default_rng(RNG_SEED)
    psize = min(len(avail), ctrl_size(nres)) if nres > 0 else 0
    pool = sorted(int(x) for x in rng.choice(np.array(avail), size=psize, replace=False)) if psize > 0 else []

    localset = set()
    for r in res:
        for d in range(-LOCAL_W, LOCAL_W + 1):
            j = r + d
            if glo <= j < ghi and j not in resset:
                localset.add(j)
    lavail = sorted(localset)
    rng2 = np.random.default_rng(RNG_SEED)
    lsize = min(len(lavail), ctrl_size(nres)) if nres > 0 else 0
    local = sorted(int(x) for x in rng2.choice(np.array(lavail), size=lsize, replace=False)) if lsize > 0 else []

    return {"off": off, "L": L, "lo": lo, "hi": hi, "seq_window": seq[lo:hi],
            "res": res, "pool": pool, "local": local, "dropped": dropped}

# ----------------------------------------------------------------------------- ESM-2 entropy
_ESM = {}
def get_esm():
    if _ESM:
        return _ESM
    import torch
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True, warn_only=True)
    tok = AutoTokenizer.from_pretrained(ESM_MODEL, cache_dir=HF_CACHE)
    mod = AutoModelForMaskedLM.from_pretrained(ESM_MODEL, cache_dir=HF_CACHE).eval()
    aa_ids = torch.tensor([tok.get_vocab()[a] for a in AA20])
    _ESM.update(tok=tok, mod=mod, torch=torch, aa_ids=aa_ids)
    return _ESM

def entropy_at(seq_window, rel_positions):
    """Masked-marginal Shannon entropy (nats) at window-relative 0-based positions. Verbatim DYNAMICS1."""
    E = get_esm(); tok, mod, torch, aa_ids = E["tok"], E["mod"], E["torch"], E["aa_ids"]
    enc = tok(seq_window, return_tensors="pt")
    ids = enc["input_ids"][0]; am = enc["attention_mask"]; mask_id = tok.mask_token_id
    out = {}
    with torch.no_grad():
        for i in rel_positions:
            tpos = i + 1                                          # +1 for CLS/BOS
            b = ids.clone(); b[tpos] = mask_id
            logits = mod(input_ids=b.unsqueeze(0), attention_mask=am).logits[0, tpos]
            aa_logits = logits[aa_ids]
            logp = torch.log_softmax(aa_logits, dim=0)
            p = logp.exp()
            H = float(-(p * logp).sum())
            out[i] = round(H, 6)
    return out

def ensure_cache(t, i, ntot):
    cache = os.path.join(D5, f"ent_{sanitize(t['aro'])}.npz")
    if os.path.exists(cache):
        return cache, False
    S = build_sets(t)
    union = sorted(set(S["res"]) | set(S["pool"]) | set(S["local"]))
    rel = [g - S["off"] for g in union]
    t0 = time.time()
    Hmap = entropy_at(S["seq_window"], rel)                      # keyed by window-relative index
    ent = {g: Hmap[g - S["off"]] for g in union}
    np.savez(cache,
             res=np.array(S["res"], dtype=np.int64),
             pool=np.array(S["pool"], dtype=np.int64),
             local=np.array(S["local"], dtype=np.int64),
             ent_res=np.array([ent[g] for g in S["res"]], dtype=np.float64),
             ent_pool=np.array([ent[g] for g in S["pool"]], dtype=np.float64),
             ent_local=np.array([ent[g] for g in S["local"]], dtype=np.float64),
             dropped=np.array(S["dropped"], dtype=np.int64),
             L=np.int64(S["L"]), off=np.int64(S["off"]))
    print(f"[{i+1:3d}/{ntot}] {t['aro']:>8s} {str(t['short'])[:22]:22s} "
          f"L={S['L']:4d} nres={len(S['res']):3d} pool={len(S['pool']):3d} "
          f"local={len(S['local']):3d} npass={len(union):4d} {time.time()-t0:5.1f}s", flush=True)
    return cache, True

# ----------------------------------------------------------------------------- scoring (deterministic)
def load_per(targets):
    per = []
    for t in targets:
        z = np.load(os.path.join(D5, f"ent_{sanitize(t['aro'])}.npz"))
        per.append({
            "aro": t["aro"], "short": t["short"], "L": int(z["L"]),
            "ent_res": z["ent_res"].astype(np.float64),
            "ent_pool": z["ent_pool"].astype(np.float64),
            "ent_local": z["ent_local"].astype(np.float64),
            "n_dropped": int(z["dropped"].size),
            "dropped": z["dropped"].astype(int).tolist(),
        })
    return per

def paired_delta(per, ctrl_key):
    """Protein-level paired test: mean H at resistance sites - mean H at size-matched control
    (avg over N_DRAWS draws, rng seed 0). Returns per-protein rows + aggregate stats."""
    from scipy.stats import wilcoxon
    rows = []
    for p in per:
        er = p["ent_res"]; ec = p[ctrl_key]
        nres = len(er)
        if nres == 0 or len(ec) == 0:
            continue
        mean_res = float(np.mean(er))
        rng = np.random.default_rng(RNG_SEED)
        k = min(nres, len(ec))
        draws = [float(np.mean(ec[rng.choice(len(ec), size=k, replace=False)])) for _ in range(N_DRAWS)]
        mean_ctrl = float(np.mean(draws))
        rows.append({"aro": p["aro"], "short": p["short"], "n_res": nres,
                     "mean_res_H": round(mean_res, 6), "mean_ctrl_H": round(mean_ctrl, 6),
                     "dH": round(mean_res - mean_ctrl, 6)})
    dH = np.array([r["dH"] for r in rows], dtype=np.float64)
    w = wilcoxon(dH, alternative="greater", zero_method="wilcox")
    return {
        "n_proteins": len(dH),
        "median_dH": round(float(np.median(dH)), 6),
        "mean_dH": round(float(np.mean(dH)), 6),
        "positive_fraction": round(float(np.mean(dH > 0)), 6),
        "wilcoxon_greater_p": float(w.pvalue),
        "wilcoxon_stat": float(w.statistic),
    }, rows

def position_level(per):
    """Pooled position-level AUROC (resistance vs random-control) with protein-CLUSTERED
    permutation null (shuffle labels WITHIN protein, N_PERM x)."""
    from sklearn.metrics import roc_auc_score
    scores, labels, groups = [], [], []
    for gi, p in enumerate(per):
        for h in p["ent_res"]:  scores.append(h); labels.append(1); groups.append(gi)
        for h in p["ent_pool"]: scores.append(h); labels.append(0); groups.append(gi)
    scores = np.array(scores, dtype=np.float64)
    labels = np.array(labels, dtype=np.int64)
    groups = np.array(groups, dtype=np.int64)
    obs = float(roc_auc_score(labels, scores))
    uniq = np.unique(groups)
    masks = {gi: (groups == gi) for gi in uniq}
    rng = np.random.default_rng(RNG_SEED)
    ge = 0
    for _ in range(N_PERM):
        perm = labels.copy()
        for gi in uniq:
            m = masks[gi]
            perm[m] = rng.permutation(labels[m])
        if float(roc_auc_score(perm, scores)) >= obs:
            ge += 1
    return {
        "auroc": round(obs, 6),
        "clustered_perm_p": round((1 + ge) / (N_PERM + 1), 6),
        "n_perm": N_PERM,
        "n_resistance_positions": int(labels.sum()),
        "n_control_positions": int((labels == 0).sum()),
    }

# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    targets = parse_targets()
    n_res_total = sum(len(t["res1"]) for t in targets)

    staged = json.load(open(STAGED)) if os.path.exists(STAGED) else []
    staged_ok = (len(staged) == len(targets) and
                 sum(s["n_res_sites"] for s in staged) == n_res_total)
    print(f"parsed: {len(targets)} targets, {n_res_total} WT-verified positions "
          f"(expected 198 / 1162) staged_multiset_match={staged_ok}", flush=True)

    # ---- inference (cached / resume-safe) ----
    n_new = 0
    for i, t in enumerate(targets):
        _, made = ensure_cache(t, i, len(targets))
        n_new += int(made)
    print(f"inference done: {n_new} newly computed, {len(targets)-n_new} from cache "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- scoring (pure, deterministic) ----
    per = load_per(targets)
    n_res_used = sum(len(p["ent_res"]) for p in per)
    n_dropped  = sum(p["n_dropped"] for p in per)

    primary, prim_rows       = paired_delta(per, "ent_pool")
    secondary                = position_level(per)
    sensitivity, sens_rows   = paired_delta(per, "ent_local")

    primary_pass = (primary["wilcoxon_greater_p"] < 0.01 and
                    primary["median_dH"] > 0 and
                    primary["positive_fraction"] >= 0.60)
    secondary_pass = (secondary["auroc"] >= 0.60 and
                      secondary["clustered_perm_p"] < 0.01)
    overall_pass = bool(primary_pass and secondary_pass)
    verdict = "FIRM" if overall_pass else "CEILING"

    payload = {
        "experiment": "DYNAMICS5_resistance_site_entropy",
        "metric": ("ESM-2 esm2_t30_150M masked-marginal Shannon entropy (NATS, "
                   "torch.log_softmax over 20 AA); 1022-residue windowing verbatim DYNAMICS1"),
        "entropy_units": "nats (natural log; max = ln20 = 2.995732)",
        "model": ESM_MODEL,
        "data_source": "CARD card.json protein-variant-model (target-alteration resistance)",
        "n_targets": len(targets),
        "n_resistance_positions_verified": n_res_total,
        "n_resistance_positions_used_in_window": n_res_used,
        "n_resistance_positions_dropped_out_of_window": n_dropped,
        "control_pool_size_rule": "min(available_in_guarded_window, max(20, 4*n_res))",
        "term_guard": TERM_GUARD, "local_window": LOCAL_W,
        "n_control_draws": N_DRAWS, "n_permutations": N_PERM, "rng_seed": RNG_SEED,
        "gate": {
            "primary_rule": "one-sided Wilcoxon signed-rank p<0.01 (res higher) AND median dH>0 AND positive_fraction>=0.60",
            "secondary_rule": "pooled AUROC>=0.60 AND clustered-permutation p<0.01",
        },
        "primary_protein_level_paired": primary,
        "secondary_position_level_clustered": secondary,
        "sensitivity_local_context_control_NOT_GATED": sensitivity,
        "primary_pass": bool(primary_pass),
        "secondary_pass": bool(secondary_pass),
        "overall_pass": overall_pass,
        "verdict": verdict,
        "per_protein_primary": sorted(prim_rows, key=lambda r: r["aro"]),
    }
    payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    sha = hashlib.sha256(payload_str.encode()).hexdigest()

    out = {
        "experiment": "DYNAMICS5_resistance_site_entropy",
        "pass": overall_pass, "verdict": verdict,
        "payload": payload,
        "payload_sha256": sha,
        "provenance": {"env": "intercepta (torch2.10/tf4.41)", "model": ESM_MODEL,
                       "runtime_s": round(time.time() - t0, 1)},
    }
    json.dump(out, open(os.path.join(RES, "DYNAMICS5_metrics.json"), "w"),
              indent=2, sort_keys=True)
    open(os.path.join(RES, "payload.sha256"), "w").write(sha + "\n")

    print("\n=== DYNAMICS5 RESULT ===")
    print(f"targets={len(targets)}  res_verified={n_res_total}  res_used={n_res_used}  "
          f"dropped_oow={n_dropped}  units=nats")
    print(f"PRIMARY (protein-level paired, n={primary['n_proteins']}): "
          f"Wilcoxon p={primary['wilcoxon_greater_p']:.3g}  median_dH={primary['median_dH']:+.4f}  "
          f"pos_frac={primary['positive_fraction']:.3f}  -> {'PASS' if primary_pass else 'FAIL'}")
    print(f"SECONDARY (position-level): AUROC={secondary['auroc']:.4f}  "
          f"clustered_perm_p={secondary['clustered_perm_p']:.4g}  -> {'PASS' if secondary_pass else 'FAIL'}")
    print(f"SENSITIVITY (local-context control, NOT gated): "
          f"median_dH={sensitivity['median_dH']:+.4f}  pos_frac={sensitivity['positive_fraction']:.3f}  "
          f"Wilcoxon p={sensitivity['wilcoxon_greater_p']:.3g}")
    print(f"GATE -> {verdict}  (durability MECHANISM {'FIRM' if overall_pass else 'CEILING'})")
    print(f"payload sha256: {sha}")

if __name__ == "__main__":
    main()
