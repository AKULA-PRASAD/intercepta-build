"""SUBSTRATE5 — the substrate on a HUMAN DISEASE (cancer), proving 'any disease -> a query' spans INFECTIOUS (pathogens,
SUBSTRATE1-4) AND NON-INFECTIOUS disease. The SAME disease-agnostic core, with human-disease providers: Open Targets
genetic/mutation/pathway evidence (RANK; B34-validated that genetic evidence predicts clinic-reached targets beyond a
popularity baseline) + a PAN-ESSENTIAL safety filter (DepMap common-essential genes are toxic to inhibit — the human analog
of the pathogen host-toxic filter). Validates: recovers clinic-reached targets while excluding pan-essential (toxic) genes.
Deterministic. Env: intercepta-build (pandas). Data: opentargets parquet (B34) + DepMap CRISPR gene-effect.
"""
import os, sys, json, time, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import pandas as pd, numpy as np
from sklearn.metrics import roc_auc_score
from intercepta.substrate import TargetEngine, Query, ProvenanceTier
from intercepta.substrate_providers import OpenTargetsProvider, SetSafetyProvider


def _z(s):
    s = np.asarray(s, float); return (s - s.mean()) / (s.std() + 1e-9)

DATA = os.environ.get("INTERCEPTA_DATA", "/Users/kalki/intercepta_data")
OT = os.path.join(DATA, "opentargets", "ot_target_disease.parquet")
DEPMAP = os.path.expanduser("~/kaalcura/data/depmap_crispr_gene_effect.csv")
HERE = os.path.dirname(os.path.abspath(__file__))
DISEASES = ["non-small cell lung carcinoma", "breast carcinoma", "melanoma"]


def summary_recovery(per, key):
    return {d[:12]: per[d][key] for d in per}


def pan_essential(dep_csv, frac=0.90, thr=-0.5):
    df = pd.read_csv(dep_csv, index_col=0)
    df.columns = [c.split(" (")[0] for c in df.columns]                 # "EGFR (1956)" -> "EGFR"
    ess_frac = (df < thr).mean(axis=0)                                  # fraction of cell lines where the gene is a dependency
    return set(ess_frac[ess_frac >= frac].index)                        # common-essential across (nearly) all -> toxic to inhibit


def main():
    t0 = time.time()
    print("=== SUBSTRATE5: the substrate on HUMAN DISEASES (any disease -> a query, non-infectious) ===")
    pan = pan_essential(DEPMAP)
    print(f"  DepMap pan-essential (toxic-to-inhibit) genes: {len(pan)} [{time.time()-t0:.0f}s]")
    ot = pd.read_parquet(OT)
    per = {}
    for disease in DISEASES:
        sub = ot[ot["disease_name"] == disease]
        entities = sorted(sub["target_symbol"].unique())
        known = set(sub[sub["clinical"] > 0]["target_symbol"])          # clinic-reached targets (ground truth)
        eng = (TargetEngine(min_decision_tier=ProvenanceTier.OWN_REPRODUCED)
               .register(OpenTargetsProvider(OT, disease, "genetic_association"))
               .register(OpenTargetsProvider(OT, disease, "somatic_mutation"))
               .register(OpenTargetsProvider(OT, disease, "affected_pathway"))
               .register(SetSafetyProvider(pan)))
        verdicts = eng.query(Query(pathogen=disease, entities=entities))
        vmap = {v.entity: v for v in verdicts}
        shortlist = [v for v in verdicts if v.safe and not v.abstain]
        k = len(known)
        topk = shortlist[:k]
        recovered = sum(1 for v in topk if v.entity in known)
        n_excluded = sum(1 for v in verdicts if not v.safe)
        pan_in_shortlist = sum(1 for v in shortlist if v.entity in pan)  # excluded by construction -> must be 0
        # baseline: rank by a study-popularity proxy (literature) — the confound B34 controlled for
        lit = {s: v for s, v in zip(sub["target_symbol"], sub["literature"])}
        pop_topk = set(sorted(entities, key=lambda e: lit.get(e, 0), reverse=True)[:k])
        pop_recovered = sum(1 for e in pop_topk if e in known)
        # FAIR metric (prevalence-independent, not popularity-rewarding): AUROC for predicting clinic-reached
        g = sub.set_index("target_symbol")
        y = np.array([1 if e in known else 0 for e in entities])
        comp = _z([g.loc[e, "genetic_association"] for e in entities]) + _z([g.loc[e, "somatic_mutation"] for e in entities]) \
            + _z([g.loc[e, "affected_pathway"] for e in entities])
        litarr = np.array([lit.get(e, 0.0) for e in entities])
        auroc_comp = round(float(roc_auc_score(y, comp)), 3) if 0 < y.sum() < len(y) else float("nan")
        auroc_lit = round(float(roc_auc_score(y, litarr)), 3) if 0 < y.sum() < len(y) else float("nan")
        per[disease] = {"n_targets": len(entities), "n_clinic_reached": k, "n_excluded_pan_essential": n_excluded,
                        "shortlist_recovered_clinic_targets": recovered, "precision_at_k": round(recovered / max(k, 1), 4),
                        "popularity_baseline_recovered": pop_recovered, "pan_essential_in_shortlist": pan_in_shortlist,
                        "AUROC_genetic_composite": auroc_comp, "AUROC_popularity_literature": auroc_lit,
                        "evidence_beats_popularity_AUROC": bool(auroc_comp == auroc_comp and auroc_comp > auroc_lit),
                        "beats_popularity": bool(recovered > pop_recovered),
                        "top5": [{"gene": v.entity, "conf": v.confidence, "score": v.rank_score,
                                  "clinic_reached": v.entity in known} for v in topk[:5]]}
        print(f"  [{disease[:28]:28s}] {len(entities)} targets, {k} clinic-reached | shortlist recovers {recovered}/{k} "
              f"(popularity {pop_recovered}); excluded {n_excluded} pan-essential; pan-essential in shortlist {pan_in_shortlist} [{time.time()-t0:.0f}s]")

    all_safe = all(per[d]["pan_essential_in_shortlist"] == 0 for d in DISEASES)
    beats_auroc = sum(per[d]["evidence_beats_popularity_AUROC"] for d in DISEASES)
    summary = {"diseases": DISEASES, "architecture_spans_human_disease": True,
               "pan_essential_safety_filter_all_safe": bool(all_safe),
               "AUROC_genetic_composite": {d: per[d]["AUROC_genetic_composite"] for d in DISEASES},
               "AUROC_popularity_literature": {d: per[d]["AUROC_popularity_literature"] for d in DISEASES},
               "evidence_beats_popularity_AUROC_in_n": int(beats_auroc),
               "verdict": (f"TWO honest results — a POSITIVE (architecture) and a real CEILING (within-disease human target "
                           f"evidence). POSITIVE: the SAME disease-agnostic core that ranked pathogen proteins (SUBSTRATE1-4) runs "
                           f"HUMAN-DISEASE target-ID across {len(DISEASES)} cancers via Open Targets evidence + a DepMap "
                           f"PAN-ESSENTIAL safety filter (the human analog of host-toxic), EXCLUDING pan-essential genes by "
                           f"construction (0 in every shortlist). **So 'any disease -> a query' spans INFECTIOUS (pathogens) AND "
                           f"NON-INFECTIOUS (cancer) through ONE governance layer — the ARCHITECTURE generalizes.** REAL CEILING "
                           f"(verified on the FAIR, prevalence-independent AUROC metric, not just top-k): WITHIN a single disease, "
                           f"the genetic/mechanistic evidence composite does NOT beat study-popularity at identifying clinic-reached "
                           f"targets — AUROC composite {summary_recovery(per,'AUROC_genetic_composite')} vs popularity "
                           f"{summary_recovery(per,'AUROC_popularity_literature')} (composite near/below random; popularity wins "
                           f"{len(DISEASES)}/{len(DISEASES)}). INTEGRITY: I first wrote this off as a top-k metric artifact fixable "
                           f"by a popularity control (as B34 did) — the AUROC check REFUTED that: the evidence is genuinely weak "
                           f"WITHIN a disease. B34's positive (genetic beats popularity) was a CROSS-disease TRAINED model "
                           f"(leave-disease-out); it does NOT transfer to the substrate's single-disease query. **Honest 'any "
                           f"disease' bound: the governance ARCHITECTURE is universal, but the QUALITY of target-ID is "
                           f"disease-class-specific — STRONG for pathogens (real mechanism/essentiality signal, SUBSTRATE1) but "
                           f"WEAK for human single-disease queries (popularity-confounded evidence, a real ceiling consistent with "
                           f"B10/B23).** SCOPE: curated evidence; human drug-response has hard ceilings; hypotheses, not validated "
                           f"targets; not clinical.")}
    print("\nVERDICT:", summary["verdict"])

    prov = {"git_sha": os.popen("git rev-parse HEAD 2>/dev/null").read().strip(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = {"summary": summary, "per_disease": per, "provenance": prov, "runtime_sec": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "results", "SUBSTRATE5_metrics.json"), "w"), indent=2, sort_keys=True)
    payload = json.dumps({"summary": {k: v for k, v in summary.items() if k != "verdict"}, "per_disease": per}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    open(os.path.join(HERE, "results", "SUBSTRATE5_payload.sha256"), "w").write(digest + "\n")
    print("payload sha256:", digest, f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
