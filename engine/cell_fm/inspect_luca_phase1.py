#!/usr/bin/env python
"""
INTERCEPTA Workstream B Phase 1 Inspection
Pre-Phase 1 diagnostic: do KAALCURA-3 and NSCLC selectivity genes exist
in the LuCA atlas's 6,000 HVG subset?
Author: Prasad Akula, 2026-05-08
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LUCA_ATLAS = "/scratch/akula.pra/INTERCEPTA/data/nsclc/luca_salcher2022/data/20_build_atlas/annotate_datasets/35_final_atlas/full_atlas_hvg_integrated_scvi_integrated_scanvi.h5ad"
NSCLC_GENES_CONFIG = "/scratch/akula.pra/INTERCEPTA/configs/genes_nsclc.json"
OUTPUT = "/scratch/akula.pra/INTERCEPTA/results/luca_kaalcura_gene_coverage.json"

KAALCURA_GENES = {
    "prolif": ["MKI67","TOP2A","PCNA","CDK1","CCNB1","AURKA","BUB1","PLK1","MCM2","MCM6","FOXM1","BIRC5","NUSAP1","TPX2","CDC20","CENPF"],
    "emt_pos": ["VIM","CDH2","SNAI1","SNAI2","ZEB1","ZEB2","TWIST1","FN1"],
    "emt_neg": ["CDH1","CLDN1","TJP1"],
    "ddr": ["BRCA1","BRCA2","RAD51","ATM","ATR","CHEK1","CHEK2","PARP1","PARP2","XRCC1","MLH1","MSH2","FANCA","FANCD2","RPA1"],
}

def banner(msg):
    print("=" * 70); print(msg); print("=" * 70)

def main():
    print("INTERCEPTA Workstream B Phase 1 Inspection")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}\n")

    banner("[1/4] Loading config genes")
    with open(NSCLC_GENES_CONFIG) as f:
        nsclc_config = json.load(f)
    nsclc_genes = nsclc_config["key_target_genes"]
    print(f"  NSCLC selectivity genes: {len(nsclc_genes)}")
    total_kaalcura = sum(len(v) for v in KAALCURA_GENES.values())
    print(f"  KAALCURA-3 genes: {total_kaalcura} across 4 signatures")
    for sig, genes in KAALCURA_GENES.items():
        print(f"    {sig}: {len(genes)}")
    print()

    banner("[2/4] Loading LuCA atlas")
    import scanpy as sc
    import time
    t0 = time.time()
    ad = sc.read_h5ad(LUCA_ATLAS, backed='r')
    print(f"  Atlas shape: {ad.shape}")
    print(f"  Load time: {time.time()-t0:.1f}s")
    print(f"  Total HVGs: {ad.n_vars}\n")
    atlas_genes = set(ad.var_names)

    banner("[3/4] KAALCURA-3 gene coverage")
    kaalcura_results = {}
    for sig_name, gene_list in KAALCURA_GENES.items():
        present = [g for g in gene_list if g in atlas_genes]
        absent = [g for g in gene_list if g not in atlas_genes]
        coverage_pct = 100.0 * len(present) / len(gene_list)
        kaalcura_results[sig_name] = {
            "n_total": len(gene_list), "n_present": len(present),
            "n_absent": len(absent), "coverage_pct": round(coverage_pct, 1),
            "present": present, "absent": absent,
        }
        print(f"  {sig_name}: {len(present)}/{len(gene_list)} ({coverage_pct:.1f}%)")
        if absent:
            print(f"    MISSING: {', '.join(absent)}")

    all_kaalcura_unique = set()
    for genes in KAALCURA_GENES.values():
        all_kaalcura_unique.update(genes)
    n_kaalcura_present = len(all_kaalcura_unique & atlas_genes)
    overall_kaalcura_coverage = 100.0 * n_kaalcura_present / len(all_kaalcura_unique)
    print(f"\n  OVERALL: {n_kaalcura_present}/{len(all_kaalcura_unique)} = {overall_kaalcura_coverage:.1f}%\n")

    banner("[4/4] NSCLC selectivity coverage")
    nsclc_present = [g for g in nsclc_genes if g in atlas_genes]
    nsclc_absent = [g for g in nsclc_genes if g not in atlas_genes]
    nsclc_coverage = 100.0 * len(nsclc_present) / len(nsclc_genes)
    print(f"  Coverage: {len(nsclc_present)}/{len(nsclc_genes)} ({nsclc_coverage:.1f}%)")
    if nsclc_absent:
        print(f"  MISSING: {', '.join(nsclc_absent)}")
    print()

    banner("DECISION")
    if overall_kaalcura_coverage >= 90:
        decision = "PROCEED_INTEGRATED_ATLAS"
        rationale = f"Coverage {overall_kaalcura_coverage:.1f}% excellent. Use atlas directly."
    elif overall_kaalcura_coverage >= 80:
        decision = "PROCEED_INTEGRATED_ATLAS_WITH_CAVEAT"
        rationale = f"Coverage {overall_kaalcura_coverage:.1f}% acceptable. Document gaps."
    else:
        decision = "FALLBACK_SOURCE_STUDIES"
        rationale = f"Coverage {overall_kaalcura_coverage:.1f}% < 80%. Need source-study h5ads (full gene set)."
    print(f"  DECISION: {decision}")
    print(f"  RATIONALE: {rationale}\n")

    banner("Atlas obs summary")
    print(f"  obs columns ({len(ad.obs.columns)}): {list(ad.obs.columns)}\n")
    if 'condition' in ad.obs.columns:
        print(f"  condition counts:")
        for v, c in ad.obs['condition'].value_counts().head(10).items():
            print(f"    {v}: {c}")
        print()
    if 'cell_type_coarse' in ad.obs.columns:
        print(f"  cell_type_coarse top 10:")
        for v, c in ad.obs['cell_type_coarse'].value_counts().head(10).items():
            print(f"    {v}: {c}")
        print()
    if 'dataset' in ad.obs.columns:
        print(f"  dataset counts (top 15):")
        for v, c in ad.obs['dataset'].value_counts().head(15).items():
            print(f"    {v}: {c}")
        print()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "atlas_shape": list(ad.shape), "atlas_total_genes": ad.n_vars,
        "kaalcura_coverage": {
            "by_signature": kaalcura_results,
            "overall_n_total": len(all_kaalcura_unique),
            "overall_n_present": n_kaalcura_present,
            "overall_coverage_pct": round(overall_kaalcura_coverage, 1),
        },
        "nsclc_selectivity_coverage": {
            "n_total": len(nsclc_genes), "n_present": len(nsclc_present),
            "n_absent": len(nsclc_absent), "coverage_pct": round(nsclc_coverage, 1),
            "present": nsclc_present, "absent": nsclc_absent,
        },
        "atlas_metadata": {
            "obs_columns": list(ad.obs.columns), "var_columns": list(ad.var.columns),
            "obsm_keys": list(ad.obsm.keys()) if hasattr(ad, 'obsm') else [],
        },
        "decision": decision, "rationale": rationale,
    }
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  Report: {OUTPUT}\n")
    print(f"Finished: {datetime.now(timezone.utc).isoformat()}")

    if decision == "PROCEED_INTEGRATED_ATLAS": sys.exit(0)
    elif decision == "PROCEED_INTEGRATED_ATLAS_WITH_CAVEAT": sys.exit(1)
    else: sys.exit(2)

if __name__ == "__main__":
    main()
