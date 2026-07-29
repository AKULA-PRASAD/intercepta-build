#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1d v4 — AML Net Integration, corrected drug-celltype mechanism
==================================================================================

Diagnosis of v3 failure
-----------------------
v3 used scanpy.rank_genes_groups (differentially-expressed genes) for the
transitive drug -> cell-type join:
  - For each cell type, take top-50 DE genes
  - Link drugs that target those DE genes to the cell type
  - Score = sum of log-fold-changes across shared targets

This produced a pathological result: HSC-like top 10 was 10 FLT3
inhibitors all with identical score, Prog-like top 10 had only 2 drugs.

Root cause
----------
Differential expression finds LINEAGE MARKERS (HLF, HOPX, CD34 in HSCs;
MPO, ELANE, LYZ in myeloid). These are almost never drug targets.

Drug targets are narrow: kinases, GPCRs, nuclear receptors, etc.
BeatAML's drug_gene annotation covers only 265 genes (mostly kinases).
These targets are NOT the most differentially-expressed genes in any
cell type — they are broadly expressed across hematopoietic lineages.

So the v3 mechanism was asking the wrong question:
  "Is this drug's target differentially enriched in this cell type?"
but the biologically correct question is:
  "Does this cell type EXPRESS this drug's target at all?"

v4 correction
-------------
For each (drug, cell_type) pair:
  score = mean expression of drug's target genes in that cell type

Then the cell types differ because their expression of kinases/receptors
differs — even if these genes aren't in the top-50 DE list. This is
biologically correct: FLT3 inhibitors should link to cells that express
FLT3, venetoclax should link to cells that express BCL2, etc.

Principle 4: fixed the mechanism (use mean expression, not DE), not the
            threshold.
Principle 15: no retuning of pass thresholds to hide the bug. The same
            three validation queries with the same pass criteria are
            applied to the corrected mechanism. If it passes now,
            it passes honestly.

Validation queries (unchanged from v3)
--------------------------------------
Query A (LSC): HSC-like top 10 must include venetoclax AND <=1 FLT3 inhib
Query B (Prog): Prog-like top 10 must include >=2 FLT3 inhibitors
Query C (distinguishability): Jaccard(HSC top10, Prog top10) < 0.6

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_v4_integrated.py 2>&1 | tee \\
        ../results/aml_net_v4_build.txt

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
OUT_NET_PATH  = RESULTS_DIR / 'aml_net_v4_integrated.gpickle'
OUT_SUMMARY   = RESULTS_DIR / 'aml_net_v4_summary.json'

TOP_N_DRUGS = 15

# FLT3 inhibitor detection fallback (same as v3)
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
    if drug_name in flt3_targeting_set:
        return True
    low = drug_name.lower()
    for kw in KNOWN_FLT3_DRUG_NAMES:
        if kw in low:
            return True
    return False


def main():
    banner("Step 0: Dependency check")
    try:
        import numpy as np
        import pandas as pd
        import networkx as nx
        import anndata as ad
        import scipy.sparse as sp
        print(f"  numpy     : {np.__version__}")
        print(f"  pandas    : {pd.__version__}")
        print(f"  networkx  : {nx.__version__}")
    except ImportError as e:
        print(f"  MISSING: {e}")
        sys.exit(1)

    import numpy as np
    import pandas as pd
    import networkx as nx
    import anndata as ad
    import scipy.sparse as sp

    # ---------------------------------------------------------
    # Step 1: Load inputs
    # ---------------------------------------------------------
    banner("Step 1: Load Round 2.1b skeleton and Round 2.1c AnnData")
    if not SKELETON_PATH.exists():
        sys.exit(f"MISSING: {SKELETON_PATH}")
    if not ANNDATA_PATH.exists():
        sys.exit(f"MISSING: {ANNDATA_PATH}")

    print(f"  Loading skeleton: {SKELETON_PATH}")
    with open(SKELETON_PATH, 'rb') as f:
        G = pickle.load(f)
    print(f"    {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    print(f"  Loading AnnData: {ANNDATA_PATH}")
    t0 = time.time()
    adata = ad.read_h5ad(str(ANNDATA_PATH))
    print(f"    loaded in {time.time()-t0:.1f}s, {adata.n_obs:,} cells x {adata.n_vars:,} genes")

    # Make sure CellType is categorical
    adata.obs['CellType'] = adata.obs['CellType'].astype('category')
    celltypes = list(adata.obs['CellType'].cat.categories)
    print(f"  Cell types: {len(celltypes)}")

    # ---------------------------------------------------------
    # Step 2: Compute mean expression per gene per cell type
    # ---------------------------------------------------------
    banner("Step 2: Compute per-celltype mean expression matrix")
    print("  Matrix: 21 cell types x 27,899 genes")
    print("  Using log-normalized data in adata.X")
    print("  This is the CORRECTED mechanism vs v3:")
    print("    v3 used rank_genes_groups DE scores (lineage markers bias)")
    print("    v4 uses raw mean expression (druggable-target biology)")

    gene_names = [str(g).upper() for g in adata.var_names]
    gene_to_idx = {g: i for i, g in enumerate(gene_names)}

    # Build mean expression per cell type
    # adata.X is sparse log-normalized (cells x genes)
    X = adata.X
    if not sp.issparse(X):
        X = sp.csr_matrix(X)

    t0 = time.time()
    mean_expr = {}  # cell_type -> np.array of length n_genes
    for ct in celltypes:
        mask = (adata.obs['CellType'] == ct).values
        n_cells_in_ct = int(mask.sum())
        if n_cells_in_ct == 0:
            continue
        X_sub = X[mask, :]
        # Column means (mean expression of each gene across cells in this cluster)
        col_means = np.asarray(X_sub.mean(axis=0)).flatten()
        mean_expr[ct] = col_means
        # Diagnostic on a handful of marker genes
    print(f"  Computed mean expression in {time.time()-t0:.1f}s")

    # Sanity check: verify LSC markers are higher in HSC-like than GMP-like
    # (this is the biology we proved in Round 2.1c, so it should replicate here)
    for marker in ['CD34', 'MEIS1', 'HOPX', 'FLT3', 'BCL2', 'MPO', 'ELANE']:
        if marker in gene_to_idx:
            idx = gene_to_idx[marker]
            hsc_like_mean = mean_expr.get('HSC-like', np.zeros(1))[idx]
            prog_like_mean = mean_expr.get('Prog-like', np.zeros(1))[idx]
            gmp_like_mean = mean_expr.get('GMP-like', np.zeros(1))[idx]
            mono_like_mean = mean_expr.get('Mono-like', np.zeros(1))[idx]
            print(f"    {marker:7s}  HSC-like={hsc_like_mean:.3f}  "
                  f"Prog-like={prog_like_mean:.3f}  "
                  f"GMP-like={gmp_like_mean:.3f}  "
                  f"Mono-like={mono_like_mean:.3f}")

    # ---------------------------------------------------------
    # Step 3: Build drug -> target genes map from the graph
    # ---------------------------------------------------------
    banner("Step 3: Build drug-target-gene map from graph")
    drug_to_targets = {}  # drug_name -> set of target gene symbols
    for u, v, data in G.edges(data=True):
        if data.get('edge_kind') == 'drug_targets_gene':
            drug = u.replace('drug::', '')
            gene = v.replace('gene::', '').upper()
            drug_to_targets.setdefault(drug, set()).add(gene)
    n_drugs = len(drug_to_targets)
    n_targets = sum(len(v) for v in drug_to_targets.values())
    print(f"  {n_drugs} drugs with target annotations, {n_targets} drug-gene edges")

    # ---------------------------------------------------------
    # Step 4: Score each drug for each cell type
    # ---------------------------------------------------------
    banner("Step 4: Score drug-celltype activity via target expression")
    print("  score(drug, celltype) = mean over drug's target genes of")
    print("                          expression of target in celltype")

    drug_celltype_scores = {}  # cell_type -> {drug -> score}
    for ct in celltypes:
        drug_celltype_scores[ct] = {}
        ct_expr = mean_expr[ct]
        for drug, targets in drug_to_targets.items():
            target_exprs = []
            for gene in targets:
                if gene in gene_to_idx:
                    target_exprs.append(float(ct_expr[gene_to_idx[gene]]))
            if not target_exprs:
                continue
            # Use mean target expression as the activity score
            score = float(np.mean(target_exprs))
            drug_celltype_scores[ct][drug] = score

    total_edges_added = sum(len(v) for v in drug_celltype_scores.values())
    print(f"  Computed {total_edges_added} drug-celltype scores")

    # ---------------------------------------------------------
    # Step 5: Add Layer 2 to the graph
    # ---------------------------------------------------------
    banner("Step 5: Add Layer 2 cell-type nodes and drug-celltype edges to net")
    n_celltype_nodes = 0
    for ct in celltypes:
        ct_node = f"celltype::{ct}"
        G.add_node(
            ct_node,
            layer='L2_transcriptome',
            node_kind='cell_type',
            malignant=('-like' in ct),
            n_cells=int((adata.obs['CellType'] == ct).sum()),
        )
        n_celltype_nodes += 1

    # Add drug -> celltype edges
    n_edges_added = 0
    for ct, scores in drug_celltype_scores.items():
        ct_node = f"celltype::{ct}"
        for drug, score in scores.items():
            drug_node = f"drug::{drug}"
            if drug_node not in G:
                continue
            G.add_edge(drug_node, ct_node,
                       edge_kind='drug_active_on_celltype',
                       mean_target_expression=score,
                       n_targets=len(drug_to_targets[drug]))
            n_edges_added += 1

    print(f"  Added {n_celltype_nodes} cell-type nodes")
    print(f"  Added {n_edges_added} drug -> cell-type edges")
    print(f"  Final graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    # Layer inventory
    layer_inv = {}
    for _, d in G.nodes(data=True):
        l = d.get('layer', 'unknown')
        layer_inv[l] = layer_inv.get(l, 0) + 1
    print(f"\n  Layer inventory:")
    for k, v in sorted(layer_inv.items()):
        print(f"    {k}: {v:,} nodes")

    # ---------------------------------------------------------
    # Step 6: Validation queries
    # ---------------------------------------------------------
    banner("Step 6: Validation queries")

    def top_drugs(ct, top_n=TOP_N_DRUGS):
        scores = drug_celltype_scores.get(ct, {})
        return sorted(scores.items(), key=lambda x: -x[1])[:top_n]

    flt3_from_graph = {
        e[0].replace('drug::', '')
        for e in G.in_edges('gene::FLT3', data=False)
    }
    print(f"  FLT3-targeting drugs per graph: {len(flt3_from_graph)}")

    # Query A: HSC-like
    banner("Query A: HSC-like top drugs (LSC biology)")
    hsc_like_top = top_drugs('HSC-like')
    print(f"  {'Rank':<5}{'Drug':<32}{'Score':>8}{'Nt':>4}  FLT3?  tag")
    hsc_top10 = hsc_like_top[:10]
    for i, (drug, score) in enumerate(hsc_top10, 1):
        n_t = len(drug_to_targets.get(drug, set()))
        is_flt3 = is_flt3_drug(drug, flt3_from_graph)
        flt3_tag = 'YES' if is_flt3 else '   '
        tag = ''
        if 'venetoclax' in drug.lower():
            tag = '← BCL2 SOC'
        print(f"  {i:<5}{drug[:30]:<32}{score:>8.3f}{n_t:>4}   {flt3_tag}   {tag}")

    venetoclax_A = any('venetoclax' in d.lower() for d, _ in hsc_top10)
    flt3_count_A = sum(1 for d, _ in hsc_top10 if is_flt3_drug(d, flt3_from_graph))
    print(f"\n  Venetoclax in top 10: {venetoclax_A}")
    print(f"  FLT3 inhibitors in top 10: {flt3_count_A}")
    query_A_pass = venetoclax_A and flt3_count_A <= 1

    # Query B: Prog-like
    banner("Query B: Prog-like top drugs (progenitor biology)")
    prog_like_top = top_drugs('Prog-like')
    print(f"  {'Rank':<5}{'Drug':<32}{'Score':>8}{'Nt':>4}  FLT3?")
    prog_top10 = prog_like_top[:10]
    for i, (drug, score) in enumerate(prog_top10, 1):
        n_t = len(drug_to_targets.get(drug, set()))
        is_flt3 = is_flt3_drug(drug, flt3_from_graph)
        flt3_tag = 'YES' if is_flt3 else '   '
        print(f"  {i:<5}{drug[:30]:<32}{score:>8.3f}{n_t:>4}   {flt3_tag}")

    flt3_count_B = sum(1 for d, _ in prog_top10 if is_flt3_drug(d, flt3_from_graph))
    print(f"\n  FLT3 inhibitors in top 10: {flt3_count_B}")
    query_B_pass = flt3_count_B >= 2

    # Query C: Distinguishability
    banner("Query C: HSC-like vs Prog-like distinguishability")
    hsc_set = {d for d, _ in hsc_top10}
    prog_set = {d for d, _ in prog_top10}
    intersection = hsc_set & prog_set
    union = hsc_set | prog_set
    jaccard = len(intersection) / len(union) if union else 1.0
    print(f"  HSC-like top 10:  {sorted(hsc_set)}")
    print(f"  Prog-like top 10: {sorted(prog_set)}")
    print(f"  Overlap ({len(intersection)}): {sorted(intersection)}")
    print(f"  Jaccard: {jaccard:.2f}")
    query_C_pass = jaccard < 0.6

    # ---------------------------------------------------------
    # Step 7: Verdict
    # ---------------------------------------------------------
    banner("Step 7: Verdict")
    print(f"  Query A (LSC, venetoclax+/FLT3 not dominant):  "
          f"{'PASS' if query_A_pass else 'FAIL'}")
    print(f"  Query B (Prog, >=2 FLT3):                      "
          f"{'PASS' if query_B_pass else 'FAIL'}")
    print(f"  Query C (distinguishable, Jaccard<0.6):         "
          f"{'PASS' if query_C_pass else 'FAIL'}")

    all_pass = query_A_pass and query_B_pass and query_C_pass
    verdict = 'PASS' if all_pass else 'FAIL'
    print(f"\n  VERDICT: {verdict}")

    summary = {
        'verdict': verdict,
        'mechanism': 'mean target gene expression per cell type (v4 correction)',
        'graph_stats': {
            'n_nodes': G.number_of_nodes(),
            'n_edges': G.number_of_edges(),
            'layers': layer_inv,
        },
        'query_A_HSC_like': {
            'venetoclax_in_top10': venetoclax_A,
            'flt3_in_top10': int(flt3_count_A),
            'top_15': [{'drug': d, 'score': float(s),
                        'n_targets': len(drug_to_targets.get(d, set()))}
                       for d, s in hsc_like_top],
            'pass': bool(query_A_pass),
        },
        'query_B_Prog_like': {
            'flt3_in_top10': int(flt3_count_B),
            'top_15': [{'drug': d, 'score': float(s),
                        'n_targets': len(drug_to_targets.get(d, set()))}
                       for d, s in prog_like_top],
            'pass': bool(query_B_pass),
        },
        'query_C_distinguishability': {
            'jaccard': float(jaccard),
            'overlap': sorted(intersection),
            'pass': bool(query_C_pass),
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Summary JSON: {OUT_SUMMARY}")

    if not all_pass:
        print(f"\n  Graph NOT saved.")
        sys.exit(3)

    # Save graph if all pass
    banner("Step 8: Save integrated net")
    print(f"  Pickling net to {OUT_NET_PATH}")
    with open(OUT_NET_PATH, 'wb') as f:
        pickle.dump(G, f)
    size_mb = OUT_NET_PATH.stat().st_size / (1024 * 1024)
    print(f"  Size: {size_mb:.1f} MB")
    print(f"\n  Round 2.1d v4 net integration complete. Ready for closure memo.")


if __name__ == '__main__':
    main()
