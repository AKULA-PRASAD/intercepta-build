#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1b — AML Disease Net Skeleton
=================================================

Purpose
-------
Build the first version of the AML disease knowledge graph using the
BeatAML 2.0 data layer validated in Round 2.1a. Run one ground-truth
query against the graph to prove it encodes treatment-relevant biology.

Scope — what 2.1b does
----------------------
Three layers, all from the validated BeatAML clinical + drug data:

  L1 (genome):      mutation nodes (FLT3-ITD, NPM1, TP53, RUNX1, ASXL1,
                    CEBPA_Biallelic). Edge: patient → mutation if patient
                    carries that mutation.

  L7 (pharmacome):  drug nodes (166 inhibitors from BeatAML panel).
                    Drug → gene edges from drug_gene sheet (651 edges).
                    Patient → drug edges labeled with AUC (lower = more
                    potent).

  L9 (disease map): patient nodes (805 AML patients), connected to
                    mutations (L1) and drugs (L7). Patient nodes carry
                    ELN 2017 risk, diagnosis, age.

Validation — the 2.1b pass criterion
------------------------------------
For each simulated "query patient" with genotype {FLT3-ITD+, NPM1+},
predict top drugs by a simple graph-based score:

  score(drug | genotype) =
      -median AUC over all real patients matching genotype, for that drug

Expected result (2024-2025 ELN / literature standard-of-care):
  TOP predictions should include:
    - FLT3 inhibitors (gilteritinib, quizartinib, midostaurin, sorafenib,
      or any BeatAML-annotated FLT3 targeter)
    - Venetoclax (BCL2 — standard partner for FLT3 AML per VIALE-A,
      JCO 2024 triplet data)

Pass criterion:
  PASS: >= 1 FLT3-targeting drug AND venetoclax both in top 10
  PARTIAL: one but not both
  FAIL: neither

Scope — what 2.1b does NOT do
------------------------------
- No scRNA-seq (Van Galen), that's 2.1c
- No ODE, that's 2.2
- No novel molecule generation, that's 2.3
- No combinations, that's 2.2+
- No Layer 2 (expression), Layer 3 (proteome), Layer 15 (selectivity)
- Uses networkx; not yet Neo4j. Scale is fine for 805 patients x 166 drugs.

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_skeleton.py 2>&1 | tee \\
        ../results/aml_net_skeleton_build.txt

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date:    April 21, 2026
Principle 3: standard-of-care verified against 2024-2025 literature
             before writing the pass criterion.
Principle 15: passes or fails on real data, not my narrative.
"""
import os
import sys
import json
from pathlib import Path


DATA_ROOT = Path(os.environ.get(
    'BEATAML_DATA_DIR',
    str(Path(__file__).resolve().parent.parent / 'data' / 'beataml2.0_data-2.0')
))
RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CURVE_FITS = DATA_ROOT / 'beataml_probit_curve_fits_v4_dbgap.txt'
CLINICAL   = DATA_ROOT / 'beataml_wv1to4_clinical.xlsx'
DRUG_FAM   = DATA_ROOT / 'beataml_drug_families.xlsx'

# Six recurrent driver mutations available as columns in clinical summary.
# Verified from schema inspection: all are binary 'positive'/'negative'
# except CEBPA_Biallelic (object w/ {bi, ...}) and variantSummary (pipe-delim).
MUTATION_COLUMNS = ['FLT3-ITD', 'NPM1', 'RUNX1', 'ASXL1', 'TP53']

# Minimum patients matching genotype, for any prediction
MIN_GENOTYPE_MATCH = 10
MIN_N_FOR_DRUG_SCORE = 5     # a drug needs >=5 matched patients scored
TOP_N = 15


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def main():
    import pandas as pd
    import networkx as nx

    # --------------------------------------------------------------
    # Step 1: Load and filter input data
    # --------------------------------------------------------------
    banner("Step 1: Load validated BeatAML 2.0 data")
    clin = pd.read_excel(CLINICAL, sheet_name='summary')
    drug_gene = pd.read_excel(DRUG_FAM, sheet_name='drug_gene')
    fits = pd.read_csv(CURVE_FITS, sep='\t', low_memory=False)

    # QC filters (same as Round 2.1a validations)
    fits_ok = fits[
        fits['paper_inclusion'] &
        fits['converged'] &
        (fits['curve_type'] == 'decreasing') &
        (~fits['all_gt_50'])
    ].copy()

    print(f"  clinical rows: {len(clin):,} ({clin['dbgap_subject_id'].nunique():,} patients)")
    print(f"  drug-gene edges: {len(drug_gene):,} ({drug_gene['inhibitor'].nunique()} drugs)")
    print(f"  drug sensitivity rows after QC: {len(fits_ok):,}")

    # --------------------------------------------------------------
    # Step 2: Collapse clinical to one row per patient (mutations)
    # --------------------------------------------------------------
    banner("Step 2: Collapse clinical to per-patient mutation profiles")
    # For each mutation column, mark patient positive if any sample is positive
    patient_mut = {}
    for mut_col in MUTATION_COLUMNS:
        if mut_col not in clin.columns:
            print(f"  WARN: column {mut_col} missing from clinical")
            continue
        series = clin.dropna(subset=[mut_col]).groupby('dbgap_subject_id')[mut_col].apply(
            lambda s: 'positive' if (s == 'positive').any()
            else ('positive' if s.astype(str).str.lower().str.contains('bi').any()
                  else 'negative')
        )
        patient_mut[mut_col] = series
        pos = (series == 'positive').sum()
        neg = (series == 'negative').sum()
        print(f"  {mut_col:20s}  pos={pos:4d}  neg={neg:4d}  total_annotated={len(series):4d}")

    # Build a frame: rows=patient, cols=each mutation status
    mut_frame = pd.DataFrame(patient_mut)

    # Restrict to AML patients
    aml_patients = set(
        clin.loc[clin['dxAtInclusion'].astype(str).str.contains('AML', case=False, na=False),
                 'dbgap_subject_id'].unique()
    )
    mut_frame = mut_frame[mut_frame.index.isin(aml_patients)]
    print(f"\n  AML patients with mutation profiles: {len(mut_frame):,}")

    # --------------------------------------------------------------
    # Step 3: Build the networkx graph
    # --------------------------------------------------------------
    banner("Step 3: Construct the AML net skeleton")
    G = nx.MultiDiGraph()

    # Layer 1 nodes: mutations
    for mut in MUTATION_COLUMNS:
        G.add_node(f"mut::{mut}", layer='L1_genome', node_kind='mutation')

    # Layer 7 nodes: drugs
    all_drugs = set(fits_ok['inhibitor'].unique()) | set(drug_gene['inhibitor'].unique())
    for drug in all_drugs:
        G.add_node(f"drug::{drug}", layer='L7_pharmacome', node_kind='drug')

    # Layer 7: drug -> gene edges (from drug_gene sheet)
    gene_nodes = set(drug_gene['Symbol'].astype(str).str.upper().unique())
    for gene in gene_nodes:
        G.add_node(f"gene::{gene}", layer='L7_pharmacome', node_kind='gene_target')
    for _, row in drug_gene.iterrows():
        G.add_edge(f"drug::{row['inhibitor']}", f"gene::{str(row['Symbol']).upper()}",
                   edge_kind='drug_targets_gene',
                   family=row.get('family', None))

    # Layer 9: patient nodes with mutation edges
    for pid, mut_row in mut_frame.iterrows():
        G.add_node(f"patient::{pid}", layer='L9_disease_map', node_kind='patient',
                   eln2017=str(clin.loc[clin['dbgap_subject_id']==pid,
                                        'ELN2017'].iloc[0])
                            if pid in clin['dbgap_subject_id'].values else None)
        for mut_col, status in mut_row.items():
            if status == 'positive':
                G.add_edge(f"patient::{pid}", f"mut::{mut_col}",
                           edge_kind='patient_has_mutation')

    # Layer 9 -> Layer 7: patient -> drug sensitivity edges
    for _, row in fits_ok.iterrows():
        pid = row['dbgap_subject_id']
        if pid not in mut_frame.index:
            continue
        G.add_edge(f"patient::{pid}", f"drug::{row['inhibitor']}",
                   edge_kind='patient_drug_sensitivity',
                   auc=float(row['auc']),
                   ic50=float(row['ic50']))

    print(f"  Graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
    # Report by layer
    layer_counts = {}
    for _, data in G.nodes(data=True):
        l = data.get('layer', 'unknown')
        layer_counts[l] = layer_counts.get(l, 0) + 1
    for k, v in sorted(layer_counts.items()):
        print(f"    {k}: {v:,} nodes")

    # --------------------------------------------------------------
    # Step 4: Validation query
    # --------------------------------------------------------------
    banner("Step 4: Graph-based prediction for FLT3-ITD+ / NPM1+ genotype")
    # Find all patients matching this genotype via the graph
    query_genotype = {'FLT3-ITD': 'positive', 'NPM1': 'positive'}

    def patients_matching(genotype):
        matching = set()
        for pid in mut_frame.index:
            row = mut_frame.loc[pid]
            if all(row.get(mut) == status for mut, status in genotype.items()):
                matching.add(pid)
        return matching

    matched = patients_matching(query_genotype)
    print(f"  Query genotype: {query_genotype}")
    print(f"  Patients matching genotype: {len(matched)}")

    if len(matched) < MIN_GENOTYPE_MATCH:
        print(f"  ERROR: only {len(matched)} matching patients, need >= {MIN_GENOTYPE_MATCH}.")
        sys.exit(2)

    # For each drug, collect AUCs from matched patients via graph edges
    drug_scores = {}
    for pid in matched:
        pnode = f"patient::{pid}"
        if pnode not in G:
            continue
        # Traverse outgoing edges where edge_kind='patient_drug_sensitivity'
        for _, dnode, edata in G.out_edges(pnode, data=True):
            if edata.get('edge_kind') == 'patient_drug_sensitivity':
                drug_name = dnode.replace('drug::', '')
                drug_scores.setdefault(drug_name, []).append(edata['auc'])

    # Median AUC per drug (lower = better)
    ranked = []
    for drug, aucs in drug_scores.items():
        if len(aucs) < MIN_N_FOR_DRUG_SCORE:
            continue
        ranked.append({
            'drug': drug,
            'median_auc': float(pd.Series(aucs).median()),
            'n_patients': len(aucs),
        })
    ranked_df = pd.DataFrame(ranked).sort_values('median_auc').reset_index(drop=True)
    ranked_df.index = ranked_df.index + 1

    # Annotate FLT3-targeting drugs (from the graph)
    flt3_targeters = {e[0].replace('drug::', '')
                      for e in G.in_edges('gene::FLT3', data=False)}
    ranked_df['is_flt3_targeter'] = ranked_df['drug'].isin(flt3_targeters)

    print(f"\n  Top {TOP_N} drugs by net prediction (median AUC, lower=better):")
    print(f"  {'Rank':<6}{'Drug':<32}{'median_AUC':>12}{'n':>5}  FLT3?  tags")
    for rank, row in ranked_df.head(TOP_N).iterrows():
        is_flt3 = ' YES' if row['is_flt3_targeter'] else '    '
        drug = str(row['drug'])
        tag = ''
        if 'venetoclax' in drug.lower():
            tag = '← BCL2 / SOC partner'
        print(f"  {rank:<6}{drug[:30]:<32}{row['median_auc']:>12.1f}"
              f"{int(row['n_patients']):>5d} {is_flt3}  {tag}")

    # --------------------------------------------------------------
    # Step 5: Validation verdict
    # --------------------------------------------------------------
    banner("Step 5: 2.1b validation verdict")
    top10 = ranked_df.head(10)
    flt3_in_top10 = (top10['is_flt3_targeter']).sum()
    venetoclax_in_top10 = top10['drug'].str.lower().str.contains('venetoclax').any()

    print(f"  FLT3-targeting drugs in top 10:  {int(flt3_in_top10)}")
    print(f"  Venetoclax in top 10:            {'YES' if venetoclax_in_top10 else 'NO'}")

    # Pass criterion: both should be present (ELN + VIALE-A + JCO 2024 SOC)
    if flt3_in_top10 >= 1 and venetoclax_in_top10:
        verdict = 'PASS'
        msg = (f"Top 10 predictions for FLT3-ITD+/NPM1+ genotype include "
               f"both FLT3-targeting drug(s) ({int(flt3_in_top10)}) AND "
               f"venetoclax. Net reproduces ELN 2022 / 2024-2025 "
               f"standard-of-care signal. Round 2.1b skeleton validated.")
    elif flt3_in_top10 >= 1 or venetoclax_in_top10:
        verdict = 'PARTIAL'
        missing = 'venetoclax' if not venetoclax_in_top10 else 'FLT3 inhibitor'
        msg = (f"Top 10 has only one of the expected two components. "
               f"Missing: {missing}. Investigate cohort size or drug-panel "
               f"coverage.")
    else:
        verdict = 'FAIL'
        msg = (f"Top 10 missing BOTH FLT3 inhibitors AND venetoclax. Net "
               f"construction or traversal is broken. Stop and debug.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  {msg}")

    # --------------------------------------------------------------
    # Step 6: Persist the net
    # --------------------------------------------------------------
    banner("Step 6: Save graph and results")
    graph_path = RESULTS_DIR / 'aml_net_skeleton.gpickle'
    try:
        import pickle
        with open(graph_path, 'wb') as f:
            pickle.dump(G, f)
        print(f"  Graph pickled: {graph_path}")
    except Exception as e:
        print(f"  WARN: graph pickle failed: {e}")

    # Also save a JSON node list for inspection
    nodes_json = [{'id': n, **d} for n, d in G.nodes(data=True)]
    edges_sample = [
        {'src': u, 'dst': v, **d}
        for u, v, d in list(G.edges(data=True))[:500]
    ]
    with open(RESULTS_DIR / 'aml_net_skeleton_summary.json', 'w') as f:
        json.dump({
            'query_genotype': query_genotype,
            'n_matched_patients': len(matched),
            'verdict': verdict,
            'message': msg,
            'flt3_in_top10': int(flt3_in_top10),
            'venetoclax_in_top10': bool(venetoclax_in_top10),
            'node_counts_by_layer': layer_counts,
            'top_15_predictions': ranked_df.head(15).to_dict(orient='records'),
            'graph_stats': {
                'n_nodes': G.number_of_nodes(),
                'n_edges': G.number_of_edges(),
            },
        }, f, indent=2, default=str)
    print(f"  Summary JSON:  {RESULTS_DIR}/aml_net_skeleton_summary.json")


if __name__ == '__main__':
    main()
