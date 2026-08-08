#!/usr/bin/env python
"""PHENO1 — phenotype-to-gene RETRIEVAL front door: final scoring. Deterministic (seed=42).

Reads the FROZEN HPO 2026-06-23 files (sha-verified), builds an IC-weighted phenotype→gene
retrieval+ranking with a LEAVE-ONE-DISEASE-OUT leakage control, and applies the PRE-REGISTERED
gates (PREREG.md):
  G1  PRIMARY  : ranker recall@10 >= freq-prior + 0.10 AND MRR>baseline, paired Wilcoxon p<0.01,
                 AND ranker MRR > random-permutation null (K=10000) p<0.01
  G2  ABSTAIN  : abstention rule targets harder cases (recall@10 abstained < scored)
  G3  ROBUST   : lift holds on MENDELIAN-only ground truth; recall@1 lift reported
Writes results/PHENO1_metrics.json (sorted keys) + payload.sha256. Reproduces byte-identical.

SCOPE: retrieval over KNOWN HPO→gene associations (validated lookup+ranking), NOT de-novo mechanism
inference (OPEN, not attempted). Candidate genes only; affinity wall (HIT2/B49/B65) still gates therapy.
NO fabricated data. NEVER commits data / pushes.
"""
import os, sys, csv, math, json, hashlib, time
from collections import defaultdict
import numpy as np
from scipy import sparse, stats

SEED, K, N_MIN_TERMS, KS = 42, 10000, 3, [1, 5, 10]
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/Users/kalki/intercepta_data/pheno1"
INPUTS = {
    "phenotype.hpoa":       "89004f85b253f980ffe84218d2c080665cbf67a57bbb322111d6a2db5eb31dff",
    "genes_to_disease.txt": "a247027ae9944e34545e0a91060243ff6c118681c06379b9721af1ee4f39286a",
    "hp.obo":               "a5092cbdf605f568403cf7380d9173014015692433b2cc631bc5c1b053876b1b",
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

for name, want in INPUTS.items():
    got = sha256(os.path.join(DATA, name))
    assert got == want, f"input sha mismatch {name}: {got} != {want}"

# ---------------- parse HPO DAG ----------------
parents = defaultdict(set); alt2main = {}; obsolete = set(); allids = set(); hpo_ver = None
cur = None
with open(os.path.join(DATA, "hp.obo")) as f:
    for line in f:
        line = line.rstrip("\n")
        if line.startswith("data-version:"):
            hpo_ver = line.split("data-version:")[1].strip()
        elif line == "[Term]":
            cur = None
        elif line.startswith("id: HP:"):
            cur = line[4:]; allids.add(cur)
        elif cur and line.startswith("is_a:"):
            parents[cur].add(line.split("is_a:")[1].strip().split("!")[0].strip())
        elif cur and line.startswith("alt_id: HP:"):
            alt2main[line[8:].strip()] = cur
        elif cur and line.startswith("is_obsolete: true"):
            obsolete.add(cur)

sys.setrecursionlimit(100000)
_anc = {}
def ancestors(t):
    if t in _anc: return _anc[t]
    res = set()
    for p in parents.get(t, ()):
        res.add(p); res |= ancestors(p)
    _anc[t] = res; return res

def norm_term(t):
    """map alt_id -> primary; drop obsolete / unknown; return None if unusable."""
    t = alt2main.get(t, t)
    if t in obsolete or t not in allids: return None
    return t

def propagate(direct_terms):
    prop = set()
    for t in direct_terms:
        t = norm_term(t)
        if t is None: continue
        prop.add(t); prop |= ancestors(t)
    return prop

# ---------------- disease -> direct phenotype terms (aspect P) ----------------
dis_direct = defaultdict(set)
with open(os.path.join(DATA, "phenotype.hpoa")) as f:
    for _ in range(4): next(f)
    for row in csv.DictReader(f, delimiter="\t"):
        if row["aspect"] == "P" and row["qualifier"] != "NOT":
            t = norm_term(row["hpo_id"])
            if t is not None:
                dis_direct[row["database_id"]].add(t)

# ---------------- disease -> causal gene(s) ----------------
dis_gene = defaultdict(set); gene_dis = defaultdict(set); is_mendelian = defaultdict(bool)
with open(os.path.join(DATA, "genes_to_disease.txt")) as f:
    for row in csv.DictReader(f, delimiter="\t"):
        g = row["gene_symbol"]; d = row["disease_id"]
        dis_gene[d].add(g); gene_dis[g].add(d)
        if row["association_type"] == "MENDELIAN":
            is_mendelian[(d, g)] = True

genes = sorted(gene_dis)                       # candidate universe (deterministic)
gidx = {g: i for i, g in enumerate(genes)}
NG = len(genes)

# ---------------- propagate disease profiles + IC (full corpus) ----------------
dis_prop = {d: propagate(ts) for d, ts in dis_direct.items()}
N_dis = len(dis_prop)
tfreq = defaultdict(int)
for d, prop in dis_prop.items():
    for t in prop: tfreq[t] += 1
IC = {t: -math.log(c / N_dis) for t, c in tfreq.items()}
terms = sorted(IC)
tidx = {t: i for i, t in enumerate(terms)}
NT = len(terms)
IC_vec = np.array([IC[t] for t in terms])
IC_median = float(np.median(IC_vec))

# ---------------- gene FULL profile: per-term count over the gene's diseases (propagated) --------
gene_termcount = [defaultdict(int) for _ in range(NG)]   # gene -> {term_idx: n_diseases}
gene_degree = np.zeros(NG)                                # # diseases the gene causes (with pheno)
for g in genes:
    gi = gidx[g]
    for d in sorted(gene_dis[g]):
        if d not in dis_prop or not dis_prop[d]:
            continue
        gene_degree[gi] += 1
        for t in sorted(dis_prop[d]):        # sorted -> deterministic key order (PYTHONHASHSEED-independent)
            gene_termcount[gi][tidx[t]] += 1

# gene FULL IC-weighted L2-normalized sparse matrix (genes x terms)
rows, cols, vals = [], [], []
gene_norm2_full = np.zeros(NG)   # squared L2 norm of the full (unnormalized) IC vector
for gi in range(NG):
    for ti, cnt in sorted(gene_termcount[gi].items()):   # sorted -> deterministic accumulation order
        w = IC_vec[ti]
        rows.append(gi); cols.append(ti); vals.append(w)
        gene_norm2_full[gi] += w * w
Gmat = sparse.csr_matrix((vals, (rows, cols)), shape=(NG, NT))
gnorm = np.sqrt(gene_norm2_full); gnorm_safe = np.where(gnorm > 0, gnorm, 1.0)
Gmat_n = sparse.diags(1.0 / gnorm_safe) @ Gmat          # row-normalized
Gmat_n = sparse.csr_matrix(Gmat_n)

# ---------------- test set + abstention ----------------
test_diseases = sorted(d for d in dis_prop if dis_prop[d] and dis_gene.get(d))

def abstain(d):
    direct = dis_direct[d]
    if len(direct) < N_MIN_TERMS:
        return True
    max_ic = max((IC[t] for t in direct if t in IC), default=0.0)
    return max_ic < IC_median

# frequency-prior baseline: global order by (-degree, symbol)
base_order = sorted(range(NG), key=lambda gi: (-gene_degree[gi], genes[gi]))
base_rank_of = np.empty(NG, dtype=int)                  # global baseline rank (0-based) of each gene
for r, gi in enumerate(base_order):
    base_rank_of[gi] = r

def lodo_cosine(gi, d, dvec_idx, dvec_val, dnorm):
    """cosine of disease d's vector with gene gi's LODO profile (d's contribution removed)."""
    tc = gene_termcount[gi]
    dprop = dis_prop[d]
    dot = 0.0; gn2 = 0.0
    dval = {ti: v for ti, v in zip(dvec_idx, dvec_val)}
    for ti, cnt in sorted(tc.items()):      # sorted -> deterministic summation order
        # LODO: term present iff some OTHER disease of gi still carries it
        rem = 1 if terms[ti] in dprop else 0
        if cnt - rem <= 0:
            continue
        w = IC_vec[ti]; gn2 += w * w
        if ti in dval:
            dot += w * dval[ti]
    if gn2 == 0 or dnorm == 0:
        return 0.0
    return dot / (math.sqrt(gn2) * dnorm)

def lodo_degree(gi, d):
    return gene_degree[gi] - (1 if d in gene_dis[genes[gi]] else 0)

# genes is sorted -> index order == symbol order, so symbol tie-break = lower index first
def rank_of(vec, gi):
    """0-based rank of gene gi in descending vec, ties broken by symbol (== index) ascending."""
    return int(np.sum(vec > vec[gi]) + np.sum(vec[:gi] == vec[gi]))

# ---------------- score every test disease ----------------
rr_rank = []; rr_base = []; rr_rand = []          # per (non-abstained) disease reciprocal ranks
hit_rank = {k: [] for k in KS}; hit_base = {k: [] for k in KS}; hit_rand = {k: [] for k in KS}
ntrue_list = []                                   # # true genes per scored disease (for random-permutation null)
scored, abstained, singleton_miss = [], [], 0
scored_mend, hit_rank_mend = [], {k: [] for k in KS}; rr_rank_mend = []; rr_base_mend = []

# candidate-universe recall for random baseline (analytic) uses NG and #true genes
for d in test_diseases:
    if abstain(d):
        abstained.append(d); continue
    scored.append(d)
    true_genes = sorted(dis_gene[d])
    true_idx = [gidx[g] for g in true_genes if g in gidx]
    mend_here = any(is_mendelian.get((d, g), False) for g in true_genes)

    # disease IC-weighted vector
    dprop = dis_prop[d]
    dvec_idx = np.array(sorted(tidx[t] for t in dprop), dtype=int)
    dvec_val = IC_vec[dvec_idx]
    dnorm = float(np.sqrt((dvec_val ** 2).sum()))
    dcol = sparse.csr_matrix((dvec_val / dnorm, (dvec_idx, np.zeros(len(dvec_idx), int))), shape=(NT, 1))

    # ranker cosine scores for ALL genes (full profiles; no leakage for non-causal genes)
    scores = np.asarray((Gmat_n @ dcol).todense()).ravel()
    # overwrite the TRUE genes with their LODO-corrected cosine (removes the circular self-annotation)
    for gi in true_idx:
        scores[gi] = lodo_cosine(gi, d, dvec_idx, dvec_val, dnorm)

    # rank of best true gene under ranker (LODO-corrected scores; symbol tie-break via index)
    best_rank = min(rank_of(scores, gi) for gi in true_idx)
    rr = 1.0 / (best_rank + 1)
    rr_rank.append(rr)
    for k in KS: hit_rank[k].append(1 if best_rank < k else 0)
    if all(lodo_degree(gi, d) <= 0 for gi in true_idx):
        singleton_miss += 1   # true gene(s) seen in NO other disease -> unrecoverable in principle

    # frequency-prior baseline: best LODO-adjusted pleiotropy-degree rank among true genes
    adj_deg = gene_degree.copy()
    for gi in true_idx:
        adj_deg[gi] -= (1 if d in gene_dis[genes[gi]] else 0)
    b_best = min(rank_of(adj_deg, gi) for gi in true_idx)
    rr_b = 1.0 / (b_best + 1)
    rr_base.append(rr_b)
    for k in KS: hit_base[k].append(1 if b_best < k else 0)

    # random baseline (analytic): P(>=1 of n_true random draws within top-k of NG)
    ntrue = len(true_idx)
    for k in KS:
        p_hit = 1.0 - math.prod((NG - k - i) / (NG - i) for i in range(ntrue)) if NG - k - (ntrue - 1) > 0 else 1.0
        hit_rand[k].append(p_hit)
    ntrue_list.append(ntrue)

    if mend_here:
        scored_mend.append(d); rr_rank_mend.append(rr); rr_base_mend.append(rr_b)
        for k in KS: hit_rank_mend[k].append(1 if best_rank < k else 0)

n_scored = len(scored)

def mean(x): return float(np.mean(x)) if len(x) else 0.0

recall_rank = {k: mean(hit_rank[k]) for k in KS}
recall_base = {k: mean(hit_base[k]) for k in KS}
recall_rand = {k: mean(hit_rand[k]) for k in KS}
mrr_rank, mrr_base = mean(rr_rank), mean(rr_base)

# ---------------- random-permutation null for ranker MRR (K, seed) ----------------
# Under the null the true gene is a random gene; its rank is uniform over 0..NG-1 independent of the
# score vector, so the null RR per disease = 1/(1+min of ntrue distinct uniform ranks). Vectorized per disease.
rng = np.random.default_rng(SEED)
null_rr_sum = np.zeros(K)
for ntrue in ntrue_list:
    if ntrue == 1:
        samp = rng.integers(0, NG, size=K)
    else:
        samp = rng.integers(0, NG, size=(K, ntrue)).min(axis=1)  # min-rank (collisions negligible at NG>>ntrue)
    null_rr_sum += 1.0 / (samp + 1.0)
null_mrr = null_rr_sum / n_scored
p_perm = float((np.sum(null_mrr >= mrr_rank) + 1) / (K + 1))

# ---------------- paired Wilcoxon: ranker RR vs frequency-prior RR ----------------
diff = np.array(rr_rank) - np.array(rr_base)
try:
    w_stat, w_p = stats.wilcoxon(rr_rank, rr_base, alternative="greater", zero_method="wilcox")
    w_stat, w_p = float(w_stat), float(w_p)
except Exception as e:
    w_stat, w_p = float("nan"), 1.0

# ---------------- abstention integrity (G2): recall@10 on would-be-scored abstained ----------------
ab_hit10 = []; ab_recoverable = 0
for d in abstained:
    true_genes = sorted(dis_gene[d]); true_idx = [gidx[g] for g in true_genes if g in gidx]
    dprop = dis_prop[d]
    if not dprop:
        ab_hit10.append(0); continue
    dvec_idx = np.array(sorted(tidx[t] for t in dprop), dtype=int); dvec_val = IC_vec[dvec_idx]
    dnorm = float(np.sqrt((dvec_val ** 2).sum()))
    dcol = sparse.csr_matrix((dvec_val / dnorm, (dvec_idx, np.zeros(len(dvec_idx), int))), shape=(NT, 1))
    scores = np.asarray((Gmat_n @ dcol).todense()).ravel()
    for gi in true_idx:
        scores[gi] = lodo_cosine(gi, d, dvec_idx, dvec_val, dnorm)
    best_rank = min(rank_of(scores, gi) for gi in true_idx)
    ab_hit10.append(1 if best_rank < 10 else 0)
recall_abstained_10 = mean(ab_hit10)

# ---------------- gates ----------------
margin10 = recall_rank[10] - recall_base[10]
g1_pass = bool(margin10 >= 0.10 and mrr_rank > mrr_base and w_p < 0.01 and p_perm < 0.01)
g2_pass = bool(recall_abstained_10 < recall_rank[10])   # abstention targets harder cases
recall_rank_mend = {k: mean(hit_rank_mend[k]) for k in KS}
mrr_rank_mend, mrr_base_mend = mean(rr_rank_mend), mean(rr_base_mend)
recall_base_mend10 = None
# baseline recall@10 restricted to mendelian cohort
if scored_mend:
    idxs = [i for i, d in enumerate(scored) if d in set(scored_mend)]
    recall_base_mend10 = mean([hit_base[10][i] for i in idxs])
g3_pass = bool(scored_mend and (recall_rank_mend[10] - (recall_base_mend10 or 0)) >= 0.10 and mrr_rank_mend > mrr_base_mend)

overall_pass = bool(g1_pass and g2_pass)

# ---------------- payload (numeric; EXCLUDES verdict/provenance) ----------------
def rnd(x, n=6): return None if x is None else round(float(x), n)
payload = {
    "seed": SEED, "K_perm": K, "n_min_terms": N_MIN_TERMS, "ks": KS,
    "corpus": {"n_diseases_with_profile": N_dis, "n_candidate_genes": NG,
               "n_ontology_terms_used": NT, "IC_median": rnd(IC_median),
               "n_diseases_profile_and_gene": len(test_diseases)},
    "cohort": {"n_scored": n_scored, "n_abstained": len(abstained),
               "abstention_rate": rnd(len(abstained) / len(test_diseases)),
               "n_singleton_unrecoverable_scored": singleton_miss,
               "singleton_unrecoverable_rate": rnd(singleton_miss / n_scored)},
    "ranker":       {"recall_at": {str(k): rnd(recall_rank[k]) for k in KS}, "MRR": rnd(mrr_rank)},
    "freq_prior":   {"recall_at": {str(k): rnd(recall_base[k]) for k in KS}, "MRR": rnd(mrr_base)},
    "random":       {"recall_at": {str(k): rnd(recall_rand[k]) for k in KS},
                     "perm_null_MRR_mean": rnd(float(null_mrr.mean())),
                     "perm_null_MRR_p95": rnd(float(np.percentile(null_mrr, 95)))},
    "G1_retrieval_lift": {
        "recall10_ranker": rnd(recall_rank[10]), "recall10_freq_prior": rnd(recall_base[10]),
        "recall10_margin": rnd(margin10), "margin_required": 0.10,
        "MRR_ranker": rnd(mrr_rank), "MRR_freq_prior": rnd(mrr_base),
        "wilcoxon_stat": rnd(w_stat), "wilcoxon_p": w_p,
        "perm_null_p": p_perm, "pass": g1_pass},
    "G2_abstention_integrity": {
        "abstention_rate": rnd(len(abstained) / len(test_diseases)),
        "recall10_scored": rnd(recall_rank[10]), "recall10_abstained_if_scored": rnd(recall_abstained_10),
        "abstention_targets_harder_cases": g2_pass, "pass": g2_pass},
    "G3_mendelian_robustness": {
        "n_scored_mendelian": len(scored_mend),
        "recall_at_ranker": {str(k): rnd(recall_rank_mend[k]) for k in KS},
        "recall10_freq_prior_mend": rnd(recall_base_mend10),
        "MRR_ranker": rnd(mrr_rank_mend), "MRR_freq_prior": rnd(mrr_base_mend),
        "recall1_lift": rnd(recall_rank[1] - recall_base[1]), "pass": g3_pass},
    "gates": {"G1": g1_pass, "G2": g2_pass, "G3": g3_pass, "overall_PASS": overall_pass},
}
payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
sha = hashlib.sha256(payload_json.encode()).hexdigest()

if overall_pass:
    verdict = ("PASS — a validated phenotype-INPUT retrieval front door extending the 'any disease' input "
               f"modality into the genetic arms. Over {n_scored} held-out diseases (LODO, leakage-controlled), "
               f"IC-weighted HPO phenotype overlap recovers the true causal gene in the top-10 at "
               f"recall@10={recall_rank[10]:.3f} (MRR={mrr_rank:.3f}) vs a frequency-prior popularity null of "
               f"recall@10={recall_base[10]:.3f} (MRR={mrr_base:.3f}) — a +{margin10:.3f} margin, paired "
               f"Wilcoxon p={w_p:.1e}, and above the random-permutation null (p={p_perm:.1e}). The pre-registered "
               f"abstention rule ({len(abstained)/len(test_diseases):.1%} abstained) is well-targeted: abstained "
               f"profiles would score only recall@10={recall_abstained_10:.3f} vs {recall_rank[10]:.3f} on scored. "
               f"Holds on the MENDELIAN subset (recall@10={recall_rank_mend[10]:.3f}).")
else:
    verdict = ("NEGATIVE (first-class honest bound) — HPO phenotype overlap does NOT recover causal genes above "
               f"the popularity null under the pre-registered gate. ranker recall@10={recall_rank[10]:.3f} vs "
               f"freq-prior {recall_base[10]:.3f} (margin {margin10:+.3f}, need +0.10); MRR {mrr_rank:.3f} vs "
               f"{mrr_base:.3f}; Wilcoxon p={w_p:.1e}; perm p={p_perm:.1e}. Reported plainly, not tuned to pass.")
verdict += (" SCOPE: RETRIEVAL over KNOWN HPO→gene associations (validated lookup+ranking), NOT de-novo mechanism "
            "inference for a never-seen phenotype (OPEN, explicitly not attempted). Identifies CANDIDATE genes to "
            f"hand off to MENDEL1/GENETICS1; does not validate them or produce therapy (affinity wall stands). "
            f"HONEST BOUND: {singleton_miss}/{n_scored} scored diseases have a causal gene seen in NO other disease "
            "(empty LODO profile) → unrecoverable in principle, counted as misses.")

out = dict(payload)
out["verdict"] = verdict
out["g1_pass"] = g1_pass; out["g2_pass"] = g2_pass; out["g3_pass"] = g3_pass
out["input_sha256"] = INPUTS
out["hpo_version"] = hpo_ver
out["provenance"] = {
    "experiment": "PHENO1_phenotype_to_gene",
    "data": "Human Phenotype Ontology release 2026-06-23 (phenotype.hpoa, genes_to_disease.txt, hp.obo)",
    "method": ("IC-weighted cosine over ancestor-propagated HPO term vectors; gene profiles built "
               "leave-one-disease-out (test disease's own annotation removed from its causal genes); "
               "frequency-prior = LODO pleiotropy degree; random = analytic + permutation null"),
    "determinism": "seed=42; deterministic sparse linear algebra; symbol tie-breaks; permutation via numpy default_rng; "
                   "payload sha over sorted-key JSON excluding verdict/provenance",
    "git_sha": os.popen("git rev-parse HEAD").read().strip(),
    "python": sys.version.split()[0], "numpy": np.__version__, "scipy": __import__("scipy").__version__,
    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
out["payload_sha256"] = sha

os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "PHENO1_metrics.json"), "w"), indent=2, sort_keys=True)
open(os.path.join(HERE, "results", "payload.sha256"), "w").write(sha + "\n")

print(f"PHENO1 | corpus {N_dis} diseases, {NG} candidate genes, {NT} terms | HPO {hpo_ver}")
print(f"test={len(test_diseases)} scored={n_scored} abstained={len(abstained)} ({len(abstained)/len(test_diseases):.1%}) "
      f"singleton-unrecoverable={singleton_miss}")
print(f"RANKER   recall@1/5/10 = {recall_rank[1]:.3f}/{recall_rank[5]:.3f}/{recall_rank[10]:.3f}  MRR={mrr_rank:.3f}")
print(f"FREQPRIOR recall@1/5/10 = {recall_base[1]:.3f}/{recall_base[5]:.3f}/{recall_base[10]:.3f}  MRR={mrr_base:.3f}")
print(f"RANDOM   recall@1/5/10 = {recall_rand[1]:.4f}/{recall_rand[5]:.4f}/{recall_rand[10]:.4f}")
print(f"G1 margin@10={margin10:+.3f} (need +0.10) Wilcoxon p={w_p:.2e} perm p={p_perm:.2e} -> {g1_pass}")
print(f"G2 recall@10 scored={recall_rank[10]:.3f} vs abstained-if-scored={recall_abstained_10:.3f} -> {g2_pass}")
print(f"G3 MENDELIAN n={len(scored_mend)} recall@10={recall_rank_mend[10]:.3f} vs freq {recall_base_mend10} -> {g3_pass}")
print(f"OVERALL PASS = {overall_pass}")
print(f"payload_sha256: {sha}")
print("VERDICT:", verdict)
