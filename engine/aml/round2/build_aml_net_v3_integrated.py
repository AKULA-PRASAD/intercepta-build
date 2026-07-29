#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1d — AML Net Integration (Layer 2: transcriptome)
=====================================================================

Purpose
-------
Extend the Round 2.1b AML net skeleton with single-cell transcriptome
data from Round 2.1c Van Galen AnnData, producing a multi-layer net
that connects cell types to genes to drugs.

Builds on
---------
Round 2.1b: aml_net_skeleton_v2.gpickle — patients, mutations, drugs,
            gene targets, drug sensitivity edges
Round 2.1c: vangalen_aml.h5ad — 44,823 cells, 21 cell types, validated
            LSC signature biology preserved (6/6 LSC genes PASS)

Scope additions in 2.1d
-----------------------
Layer 2 (transcriptome):
  - 21 cell-type nodes (HSC, HSC-like, Prog, Prog-like, GMP, GMP-like,
    ProMono, ProMono-like, Mono, Mono-like, cDC, cDC-like, pDC, T, CTL,
    NK, B, ProB, Plasma, earlyEry, lateEry)
  - cell-type -> gene edges for top 50 enriched genes per cell type
  - edge weight = mean log-normalized expression z-score vs all other
    cell types (from scanpy.rank_genes_groups Wilcoxon)

Drug <-> cell-type transitive connections:
  - For each (drug, cell-type) pair: if drug targets gene G and cell-type
    is enriched in gene G, add drug -> cell-type edge weighted by
    expression z-score
  - This is the mechanism for "which drugs kill which cell populations"

Validation — three queries before saving
----------------------------------------
Query A (LSC biology): for HSC-like cell type, top 10 drugs
  should include venetoclax (BCL2 dependency in LSCs is well-established
  from Konopleva et al., JCO 2022; VIALE-A) and NOT be dominated by
  FLT3 inhibitors (HSC-like is the LSC-enriched population; FLT3-ITD
  signal localizes in progenitor-like cells per Van Galen 2019 Fig 6).
  PASS: venetoclax in top 10 AND <= 1 FLT3 inhibitor in top 10.

Query B (progenitor biology): for Prog-like cell type, top 10 drugs
  should include multiple FLT3 inhibitors (Van Galen 2019 explicitly
  shows FLT3-ITD associates with abundant progenitor-like cells; their
  Fig 5 shows this cluster expresses FLT3 most highly).
  PASS: >= 2 FLT3 inhibitors in top 10.

Query C (differential biology): top 10 drugs for HSC-like vs Prog-like
  must be distinguishable — different cell populations should have
  different drug profiles.
  PASS: Jaccard overlap < 0.6.

Scope — what 2.1d does NOT do
------------------------------
- No RNA velocity (deferred to Round 2.1e with Naldini 2023 10X data)
- No patient-level join between Van Galen samples and BeatAML patients
  (they are different cohorts; no patient ID overlap)
- No novel molecule generation (Round 2.3+)
- No combination drug predictions (Round 2.2+)

Honest limitation acknowledged up front
---------------------------------------
The drug -> cell-type transitive join equates "drug has target in
cell-type" with "drug has activity against cell-type." This is a
first-order approximation used widely in pharmacogenomics network
analysis. It does not account for (a) drug delivery/penetration per
cell type, (b) target saturation, (c) compensatory pathway activation.
These refinements are later-round work. For v1 the approximation is
defensible and enables validation against known LSC biology.

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_v3_integrated.py 2>&1 | tee \\
        ../results/aml_net_v3_build.txt

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date:    April 22, 2026
"""
import os
import sys
import json
import pickle
import time
from pathlib import Path


DATA_ROOT    = Path(__file__).resolve().parent.parent / 'data'
RESULTS_DIR  = Path(__file__).resolve().parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SKELETON_PATH = RESULTS_DIR / 'aml_net_skeleton_v2.gpickle'
ANNDATA_PATH  = DATA_ROOT / 'vangalen2019' / 'vangalen_aml.h5ad'
OUT_NET_PATH  = RESULTS_DIR / 'aml_net_v3_integrated.gpickle'
OUT_SUMMARY   = RESULTS_DIR / 'aml_net_v3_summary.json'

# Number of top enriched genes to take per cell type
N_TOP_GENES_PER_CELLTYPE = 50

# Minimum z-score / log-fold-change for inclusion
# Using log-fold-change because scanpy's rank_genes_groups returns lfc
MIN_LOGFC = 0.5

# Drug ranking: sum of expression z-scores across shared genes,
# weighted by drug-target-gene edge count
TOP_N_DRUGS = 15

# FLT3 inhibitor detection: drugs with "drug_targets_gene" edge to FLT3
# will be flagged. Plus known FLT3-specific drug names for redundancy.
KNOWN_FLT3_DRUG_NAMES = {
    'midostaurin', 'gilteritinib', 'quizartinib', 'sorafenib',
    'crenolanib', 'lestaurtinib', 'tandutinib', 'sunitinib',
    'foretinib', 'dovitinib', 'linifanib', 'ponatinib',
    'cabozantinib', 'vargetef', 'kw-2449', 'mgcd-265',
    'jnj-28312141', 'ac220',
}


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def is_flt3_drug(drug_name, flt3_targeting_set):
    """Returns True if drug is FLT3-targeting by either the graph
    annotation or a name-based match as fallback."""
    if drug_name in flt3_targeting_set:
        return True
    low = drug_name.lower()
    for kw in KNOWN_FLT3_DRUG_NAMES:
        if kw in low:
            return True
    return False


def main():
    # ---------------------------------------------------------
    # Step 0: Dependencies
    # ---------------------------------------------------------
    banner("Step 0: Dependency check")
    try:
        import numpy as np
        import pandas as pd
        import networkx as nx
        import anndata as ad
        print(f"  numpy     : {np.__version__}")
        print(f"  pandas    : {pd.__version__}")
        print(f"  networkx  : {nx.__version__}")
        try:
            import scanpy as sc
            print(f"  scanpy    : {sc.__version__}")
        except ImportError:
            print("  scanpy    : MISSING")
            print("  Install with: pip install scanpy")
            sys.exit(1)
    except ImportError as e:
        print(f"  MISSING: {e}")
        sys.exit(1)

    import numpy as np
    import pandas as pd
    import networkx as nx
    import anndata as ad
    import scanpy as sc

    # ---------------------------------------------------------
    # Step 1: Load inputs
    # ---------------------------------------------------------
    banner("Step 1: Load Round 2.1b skeleton and Round 2.1c AnnData")
    if not SKELETON_PATH.exists():
        print(f"  MISSING: {SKELETON_PATH}")
        sys.exit(2)
    if not ANNDATA_PATH.exists():
        print(f"  MISSING: {ANNDATA_PATH}")
        sys.exit(2)

    print(f"  Loading skeleton: {SKELETON_PATH}")
    with open(SKELETON_PATH, 'rb') as f:
        G = pickle.load(f)
    print(f"    {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    print(f"  Loading AnnData: {ANNDATA_PATH}")
    t0 = time.time()
    adata = ad.read_h5ad(str(ANNDATA_PATH))
    print(f"    loaded in {time.time()-t0:.1f}s, {adata.n_obs:,} cells x {adata.n_vars:,} genes")

    # Inventory existing node layers
    layer_inventory_before = {}
    for _, data in G.nodes(data=True):
        l = data.get('layer', 'unknown')
        layer_inventory_before[l] = layer_inventory_before.get(l, 0) + 1
    print(f"  Skeleton layer inventory:")
    for k, v in sorted(layer_inventory_before.items()):
        print(f"    {k}: {v:,} nodes")

    # ---------------------------------------------------------
    # Step 2: Compute top-enriched genes per cell type
    # ---------------------------------------------------------
    banner("Step 2: Compute top enriched genes per cell type (scanpy Wilcoxon)")
    print(f"  Using scanpy.rank_genes_groups with Wilcoxon test")
    print(f"  Top {N_TOP_GENES_PER_CELLTYPE} genes per cell type, log fc > {MIN_LOGFC}")

    # Make sure CellType is the grouping variable
    adata.obs['CellType'] = adata.obs['CellType'].astype('category')

    # scanpy rank_genes_groups is memory-intensive; it runs on the .X matrix
    # which is already log-normalized from Round 2.1c
    t0 = time.time()
    sc.tl.rank_genes_groups(
        adata,
        groupby='CellType',
        method='wilcoxon',
        use_raw=False,  # use adata.X which is log-normalized
        n_genes=N_TOP_GENES_PER_CELLTYPE * 2,  # get extra, filter by lfc
    )
    print(f"  Wilcoxon completed in {time.time()-t0:.1f}s")

    # Extract per-cell-type gene enrichment into a dict of dicts
    # gene_by_celltype: { cell_type: [ (gene, lfc, z_score), ... ] }
    gene_by_celltype = {}
    celltypes = list(adata.obs['CellType'].cat.categories)
    rgg = adata.uns['rank_genes_groups']

    for ct in celltypes:
        names_arr = rgg['names'][ct]
        lfc_arr = rgg['logfoldchanges'][ct]
        scores_arr = rgg['scores'][ct]
        pvals_arr = rgg['pvals_adj'][ct]

        enriched = []
        for i in range(len(names_arr)):
            gene = str(names_arr[i])
            lfc = float(lfc_arr[i])
            score = float(scores_arr[i])
            padj = float(pvals_arr[i])
            if lfc >= MIN_LOGFC and padj < 0.01:
                enriched.append((gene, lfc, score))
            if len(enriched) >= N_TOP_GENES_PER_CELLTYPE:
                break
        gene_by_celltype[ct] = enriched

    print(f"\n  Per-cell-type enriched gene counts:")
    for ct in sorted(celltypes):
        print(f"    {ct:20s}  {len(gene_by_celltype[ct])} genes")

    # ---------------------------------------------------------
    # Step 3: Add Layer 2 nodes and edges to the graph
    # ---------------------------------------------------------
    banner("Step 3: Add Layer 2 (transcriptome) to the net")
    n_celltype_nodes = 0
    n_celltype_gene_edges = 0
    n_new_gene_nodes = 0

    for ct in celltypes:
        ct_node = f"celltype::{ct}"
        G.add_node(
            ct_node,
            layer='L2_transcriptome',
            node_kind='cell_type',
            malignant='-like' in ct or ct in {'HSC-like', 'Prog-like', 'GMP-like',
                                              'ProMono-like', 'Mono-like', 'cDC-like'},
        )
        n_celltype_nodes += 1

        # Add edges to enriched genes (create gene nodes if missing)
        for gene, lfc, score in gene_by_celltype[ct]:
            gene_node = f"gene::{gene.upper()}"
            if gene_node not in G:
                G.add_node(gene_node, layer='L2_transcriptome',
                           node_kind='gene_transcriptome')
                n_new_gene_nodes += 1
            G.add_edge(ct_node, gene_node,
                       edge_kind='celltype_enriched_in_gene',
                       log_fc=float(lfc),
                       z_score=float(score))
            n_celltype_gene_edges += 1

    print(f"  Added {n_celltype_nodes} cell-type nodes")
    print(f"  Added {n_new_gene_nodes} new gene nodes (not in skeleton)")
    print(f"  Added {n_celltype_gene_edges} cell-type -> gene edges")

    # ---------------------------------------------------------
    # Step 4: Transitive drug -> cell-type edges via gene targets
    # ---------------------------------------------------------
    banner("Step 4: Add transitive drug -> cell-type edges")
    # Build a lookup: gene -> list of drugs that target it
    gene_to_drugs = {}
    for u, v, data in G.edges(data=True):
        if data.get('edge_kind') == 'drug_targets_gene':
            drug = u.replace('drug::', '')
            gene = v.replace('gene::', '').upper()
            gene_to_drugs.setdefault(gene, []).append(drug)
    print(f"  Gene -> drug index: {len(gene_to_drugs):,} targeted genes, "
          f"{sum(len(v) for v in gene_to_drugs.values()):,} drug-gene relationships")

    # For each cell type, find drugs that target its enriched genes
    n_drug_celltype_edges = 0
    drug_celltype_scores = {}  # for debugging / inspection

    for ct in celltypes:
        ct_node = f"celltype::{ct}"
        enriched_genes = {g.upper() for g, _, _ in gene_by_celltype[ct]}
        gene_lfc = {g.upper(): lfc for g, lfc, _ in gene_by_celltype[ct]}

        # For each enriched gene, find drugs targeting it
        drug_link_scores = {}  # drug -> summed score
        for gene in enriched_genes:
            if gene not in gene_to_drugs:
                continue
            lfc = gene_lfc[gene]
            for drug in gene_to_drugs[gene]:
                drug_link_scores[drug] = drug_link_scores.get(drug, 0.0) + lfc

        # Add drug -> cell-type edges
        for drug, total_score in drug_link_scores.items():
            drug_node = f"drug::{drug}"
            if drug_node not in G:
                continue
            G.add_edge(drug_node, ct_node,
                       edge_kind='drug_active_on_celltype',
                       transitive_score=float(total_score),
                       n_shared_genes=sum(1 for g in enriched_genes
                                          if g in gene_to_drugs
                                          and drug in gene_to_drugs[g]))
            n_drug_celltype_edges += 1

        drug_celltype_scores[ct] = drug_link_scores

    print(f"  Added {n_drug_celltype_edges} drug -> cell-type edges")
    total_edges_now = G.number_of_edges()
    print(f"  Net now has {G.number_of_nodes():,} nodes, {total_edges_now:,} edges")

    # Layer inventory after
    layer_inventory_after = {}
    for _, data in G.nodes(data=True):
        l = data.get('layer', 'unknown')
        layer_inventory_after[l] = layer_inventory_after.get(l, 0) + 1
    print(f"\n  Final layer inventory:")
    for k, v in sorted(layer_inventory_after.items()):
        print(f"    {k}: {v:,} nodes")

    # ---------------------------------------------------------
    # Step 5: Validation queries
    # ---------------------------------------------------------
    banner("Step 5: Validation queries")

    # Helper: rank drugs by transitive score for a given cell type
    def top_drugs_for_celltype(ct, top_n=TOP_N_DRUGS):
        scores = drug_celltype_scores.get(ct, {})
        return sorted(scores.items(), key=lambda x: -x[1])[:top_n]

    # FLT3-targeting drug set (from graph annotation, i.e. drug_gene sheet)
    flt3_from_graph = {
        e[0].replace('drug::', '')
        for e in G.in_edges('gene::FLT3', data=False)
    }
    print(f"  FLT3-targeting drugs per graph: {len(flt3_from_graph)}")

    # Query A: HSC-like top 10 — venetoclax in, FLT3 NOT dominant
    banner("Query A: HSC-like cell-type top drugs (LSC biology)")
    hsc_like_top = top_drugs_for_celltype('HSC-like')
    print(f"  {'Rank':<5}{'Drug':<32}{'Score':>8}  FLT3?")
    hsc_top10 = hsc_like_top[:10]
    for i, (drug, score) in enumerate(hsc_top10, 1):
        is_flt3 = is_flt3_drug(drug, flt3_from_graph)
        flt3_tag = 'YES' if is_flt3 else '   '
        tag = ' ← BCL2 SOC' if 'venetoclax' in drug.lower() else ''
        print(f"  {i:<5}{drug[:30]:<32}{score:>8.2f}  {flt3_tag}   {tag}")

    venetoclax_in_A = any('venetoclax' in d.lower() for d, _ in hsc_top10)
    flt3_count_A = sum(1 for d, _ in hsc_top10 if is_flt3_drug(d, flt3_from_graph))
    print(f"\n  Venetoclax in top 10: {venetoclax_in_A}")
    print(f"  FLT3 inhibitors in top 10: {flt3_count_A}")
    query_A_pass = venetoclax_in_A and flt3_count_A <= 1

    # Query B: Prog-like top 10 — multiple FLT3 inhibitors expected
    banner("Query B: Prog-like cell-type top drugs (progenitor biology)")
    prog_like_top = top_drugs_for_celltype('Prog-like')
    print(f"  {'Rank':<5}{'Drug':<32}{'Score':>8}  FLT3?")
    prog_top10 = prog_like_top[:10]
    for i, (drug, score) in enumerate(prog_top10, 1):
        is_flt3 = is_flt3_drug(drug, flt3_from_graph)
        flt3_tag = 'YES' if is_flt3 else '   '
        print(f"  {i:<5}{drug[:30]:<32}{score:>8.2f}  {flt3_tag}")

    flt3_count_B = sum(1 for d, _ in prog_top10 if is_flt3_drug(d, flt3_from_graph))
    print(f"\n  FLT3 inhibitors in top 10: {flt3_count_B}")
    query_B_pass = flt3_count_B >= 2

    # Query C: HSC-like vs Prog-like — must be distinguishable
    banner("Query C: HSC-like vs Prog-like distinguishability")
    hsc_set = {d for d, _ in hsc_top10}
    prog_set = {d for d, _ in prog_top10}
    intersection = hsc_set & prog_set
    union = hsc_set | prog_set
    jaccard = len(intersection) / len(union) if union else 1.0
    print(f"  HSC-like top 10 drugs:  {sorted(hsc_set)}")
    print(f"  Prog-like top 10 drugs: {sorted(prog_set)}")
    print(f"  Overlap ({len(intersection)}): {sorted(intersection)}")
    print(f"  Jaccard: {jaccard:.2f}")
    query_C_pass = jaccard < 0.6

    # ---------------------------------------------------------
    # Step 6: Verdict
    # ---------------------------------------------------------
    banner("Step 6: Verdict")
    print(f"  Query A (LSC biology, venetoclax+/FLT3 not dominant):  "
          f"{'PASS' if query_A_pass else 'FAIL'}")
    print(f"  Query B (Prog biology, >=2 FLT3 inhibitors):          "
          f"{'PASS' if query_B_pass else 'FAIL'}")
    print(f"  Query C (HSC/Prog distinguishable, Jaccard<0.6):      "
          f"{'PASS' if query_C_pass else 'FAIL'}")

    all_pass = query_A_pass and query_B_pass and query_C_pass
    verdict = 'PASS' if all_pass else 'FAIL'
    print(f"\n  VERDICT: {verdict}")

    if not all_pass:
        print("\n  One or more validation queries failed.")
        print("  Graph NOT saved — investigate before proceeding.")
        # Still write a summary JSON for diagnostic purposes
        diagnostic = {
            'verdict': verdict,
            'query_A': {
                'celltype': 'HSC-like',
                'venetoclax_in_top10': venetoclax_in_A,
                'flt3_in_top10': flt3_count_A,
                'top_10': [{'drug': d, 'score': float(s)} for d, s in hsc_top10],
                'pass': query_A_pass,
            },
            'query_B': {
                'celltype': 'Prog-like',
                'flt3_in_top10': flt3_count_B,
                'top_10': [{'drug': d, 'score': float(s)} for d, s in prog_top10],
                'pass': query_B_pass,
            },
            'query_C': {
                'jaccard': float(jaccard),
                'overlap_drugs': sorted(intersection),
                'pass': query_C_pass,
            },
        }
        with open(OUT_SUMMARY, 'w') as f:
            json.dump(diagnostic, f, indent=2, default=str)
        print(f"  Diagnostic summary: {OUT_SUMMARY}")
        sys.exit(3)

    # ---------------------------------------------------------
    # Step 7: Save integrated net
    # ---------------------------------------------------------
    banner("Step 7: Save integrated net")
    print(f"  Pickling net to {OUT_NET_PATH}")
    with open(OUT_NET_PATH, 'wb') as f:
        pickle.dump(G, f)
    size_mb = OUT_NET_PATH.stat().st_size / (1024 * 1024)
    print(f"  Size: {size_mb:.1f} MB")

    # Summary JSON for machine-readable record
    summary = {
        'verdict': verdict,
        'graph_stats': {
            'n_nodes': G.number_of_nodes(),
            'n_edges': G.number_of_edges(),
            'layers': layer_inventory_after,
        },
        'query_A_HSC_like': {
            'venetoclax_in_top10': venetoclax_in_A,
            'flt3_inhibitors_in_top10': flt3_count_A,
            'top_15': [{'drug': d, 'score': float(s)} for d, s in hsc_like_top],
            'pass': query_A_pass,
        },
        'query_B_Prog_like': {
            'flt3_inhibitors_in_top10': flt3_count_B,
            'top_15': [{'drug': d, 'score': float(s)} for d, s in prog_like_top],
            'pass': query_B_pass,
        },
        'query_C_distinguishability': {
            'jaccard_top10': float(jaccard),
            'overlap_drugs': sorted(intersection),
            'pass': query_C_pass,
        },
        'celltypes_covered': celltypes,
        'top_genes_per_celltype_n': {ct: len(gs) for ct, gs in gene_by_celltype.items()},
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Summary JSON: {OUT_SUMMARY}")
    print(f"\n  Round 2.1d net integration complete. Ready for closure memo.")


if __name__ == '__main__':
    main()
