#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1b — net skeleton encoding fix + extended validation
========================================================================

Bug found in initial build_aml_net_skeleton.py run
--------------------------------------------------
Reviewing the run output, RUNX1 / ASXL1 / TP53 came back with 0 positive
patients. That's biologically impossible — TP53 mutations are ~10% of
AML, ASXL1 ~5-10%, RUNX1 ~5-15%.

Root cause: clinical.xlsx encodes mutations two different ways:
  * FLT3-ITD, NPM1: 'positive' / 'negative' string values
  * RUNX1, ASXL1, TP53, CEBPA_Biallelic: free-text mutation descriptions
    (e.g., 'RUNX1 (p.R166*; 40.0%)') if mutation present, NaN if absent.

My first skeleton collapsed any non-'positive' string to 'negative', so
all the free-text mutations were wrongly marked negative.

Fix
---
Auto-detect encoding per column. For each mutation column:
  - If the column's unique non-null values are in {'positive', 'negative'},
    treat as binary.
  - Else, treat any non-null as 'positive' (the non-null value is the
    mutation detail string).

Extended validation
-------------------
Re-run the FLT3-ITD+/NPM1+ query to confirm the fix doesn't break it.
Then add a SECOND ground-truth query using TP53 as test case:

  Expected (Walter 2012 Blood, Döhner 2022 Blood, VIALE-A post-hoc):
    TP53-mutated AML is broadly drug-resistant, especially to standard
    chemotherapy and targeted agents. The EFFECTIVE top drugs should
    differ from FLT3/NPM1 cases. In particular:
    - FLT3 inhibitors should NOT be top (TP53 AML is often FLT3-WT)
    - Decitabine/Azacitidine (HMAs) may rank higher (TP53-AML often
      still responds to HMAs in first-line, VIALE-A showed benefit)
    - Venetoclax response in TP53+ is attenuated but present

  Minimum test: the TP53+ and FLT3-ITD+/NPM1+ top-10 lists should
  meaningfully DIFFER. If they're identical, the genotype isn't
  actually filtering the cohort — join is broken.

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 build_aml_net_skeleton_v2.py 2>&1 | tee \\
        ../results/aml_net_skeleton_v2_build.txt

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date:    April 21, 2026
Principle 15: found a real bug, fixing it, re-testing on DIFFERENT genotype
             to prove the join is working on more than one case.
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

MUTATION_COLUMNS = ['FLT3-ITD', 'NPM1', 'RUNX1', 'ASXL1', 'TP53']

MIN_GENOTYPE_MATCH = 10
MIN_N_FOR_DRUG_SCORE = 5
TOP_N = 15


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def collapse_mutation_column(df, col):
    """Auto-detect encoding and collapse to per-patient positive/negative.

    Encoding 1 (FLT3-ITD, NPM1): values are already 'positive'/'negative'.
    Encoding 2 (RUNX1, ASXL1, TP53): value is mutation description or NaN.
    """
    import pandas as pd
    non_null = df[col].dropna()
    if len(non_null) == 0:
        return pd.Series(dtype=object), 'empty'
    uniq_lower = set(non_null.astype(str).str.lower().unique())
    if uniq_lower.issubset({'positive', 'negative'}):
        # Binary encoding
        encoding = 'binary'
        series = (
            df.dropna(subset=[col])
              .groupby('dbgap_subject_id')[col]
              .apply(lambda s: 'positive' if (s == 'positive').any()
                     else 'negative')
        )
    else:
        # Free-text encoding: non-null == positive.
        # Patients with no row having a value for this column are ABSENT
        # (missing data), not necessarily negative. For the skeleton we
        # mark: positive if any sample has non-null; negative if all
        # samples have been characterized and all are null; unknown
        # if the patient has no records in this sheet at all.
        encoding = 'free_text'
        all_patients = set(df['dbgap_subject_id'].unique())
        pos_patients = set(
            df.dropna(subset=[col])['dbgap_subject_id'].unique()
        )
        # For this skeleton, treat 'not positive' as 'negative' so every
        # patient can enter genotype queries. This is a simplification
        # documented in Round 2.1b closure.
        status_map = {pid: ('positive' if pid in pos_patients else 'negative')
                      for pid in all_patients}
        series = pd.Series(status_map)
    return series, encoding


def run_genotype_query(G, mut_frame, query_genotype, tag=''):
    """Given a mutation filter dict, traverse the graph to predict drugs."""
    import pandas as pd

    matched = set()
    for pid in mut_frame.index:
        row = mut_frame.loc[pid]
        if all(row.get(mut) == status for mut, status in query_genotype.items()):
            matched.add(pid)

    print(f"\n  [{tag}] Query genotype: {query_genotype}")
    print(f"  Patients matching genotype: {len(matched)}")
    if len(matched) < MIN_GENOTYPE_MATCH:
        print(f"  WARN: only {len(matched)} patients matching; results may be noisy")

    drug_scores = {}
    for pid in matched:
        pnode = f"patient::{pid}"
        if pnode not in G:
            continue
        for _, dnode, edata in G.out_edges(pnode, data=True):
            if edata.get('edge_kind') == 'patient_drug_sensitivity':
                drug_name = dnode.replace('drug::', '')
                drug_scores.setdefault(drug_name, []).append(edata['auc'])

    ranked = []
    for drug, aucs in drug_scores.items():
        if len(aucs) < MIN_N_FOR_DRUG_SCORE:
            continue
        ranked.append({'drug': drug, 'median_auc': float(pd.Series(aucs).median()),
                       'n_patients': len(aucs)})
    ranked_df = pd.DataFrame(ranked).sort_values('median_auc').reset_index(drop=True)
    ranked_df.index = ranked_df.index + 1

    flt3_targeters = {e[0].replace('drug::', '')
                      for e in G.in_edges('gene::FLT3', data=False)}
    ranked_df['is_flt3_targeter'] = ranked_df['drug'].isin(flt3_targeters)

    print(f"  Top {TOP_N} drugs:")
    print(f"  {'Rank':<5}{'Drug':<32}{'median_AUC':>11}{'n':>5}  FLT3?  tag")
    for rank, row in ranked_df.head(TOP_N).iterrows():
        is_flt3 = 'YES' if row['is_flt3_targeter'] else ' '
        drug = str(row['drug'])
        tag_str = ''
        dl = drug.lower()
        if 'venetoclax' in dl:
            tag_str = '← BCL2 SOC'
        elif 'decitabine' in dl or 'azacit' in dl:
            tag_str = '← HMA'
        print(f"  {rank:<5}{drug[:30]:<32}{row['median_auc']:>11.1f}"
              f"{int(row['n_patients']):>5d}  {is_flt3}    {tag_str}")
    return ranked_df, len(matched)


def main():
    import pandas as pd
    import networkx as nx

    # --------------------------------------------------------------
    # Step 1: Load
    # --------------------------------------------------------------
    banner("Step 1: Load validated BeatAML 2.0 data")
    clin = pd.read_excel(CLINICAL, sheet_name='summary')
    drug_gene = pd.read_excel(DRUG_FAM, sheet_name='drug_gene')
    fits = pd.read_csv(CURVE_FITS, sep='\t', low_memory=False)
    fits_ok = fits[fits['paper_inclusion'] & fits['converged'] &
                   (fits['curve_type'] == 'decreasing') &
                   (~fits['all_gt_50'])].copy()
    print(f"  clinical rows: {len(clin):,} ({clin['dbgap_subject_id'].nunique():,} patients)")
    print(f"  drug-gene edges: {len(drug_gene):,} ({drug_gene['inhibitor'].nunique()} drugs)")
    print(f"  drug sensitivity rows after QC: {len(fits_ok):,}")

    # --------------------------------------------------------------
    # Step 2: Collapse mutations with encoding detection (THE FIX)
    # --------------------------------------------------------------
    banner("Step 2: Collapse mutations — auto-detect encoding per column")
    patient_mut = {}
    encodings = {}
    for mut_col in MUTATION_COLUMNS:
        if mut_col not in clin.columns:
            print(f"  WARN: column {mut_col} missing")
            continue
        series, enc = collapse_mutation_column(clin, mut_col)
        patient_mut[mut_col] = series
        encodings[mut_col] = enc
        pos = (series == 'positive').sum()
        neg = (series == 'negative').sum()
        print(f"  {mut_col:20s}  encoding={enc:10s}  "
              f"pos={pos:4d}  neg={neg:4d}  total={len(series):4d}")

    # Sanity check expected ranges from AML literature
    print(f"\n  Literature-expected frequencies:")
    print(f"    FLT3-ITD: ~25-30%; NPM1: ~30%; TP53: ~10%; "
          f"RUNX1: ~5-15%; ASXL1: ~5-10%")

    mut_frame = pd.DataFrame(patient_mut)
    aml_patients = set(
        clin.loc[clin['dxAtInclusion'].astype(str).str.contains('AML', case=False, na=False),
                 'dbgap_subject_id'].unique()
    )
    mut_frame = mut_frame[mut_frame.index.isin(aml_patients)]
    print(f"\n  AML patients with mutation profiles: {len(mut_frame):,}")

    # Report new frequency estimates (per-patient) to validate the fix
    print(f"\n  Observed per-patient frequencies:")
    for col in mut_frame.columns:
        pos = (mut_frame[col] == 'positive').sum()
        tot = mut_frame[col].notna().sum()
        pct = (pos/tot*100) if tot else 0
        print(f"    {col:20s}  {pos}/{tot}  =  {pct:.1f}%")

    # --------------------------------------------------------------
    # Step 3: Build graph (same as v1, just using correctly collapsed data)
    # --------------------------------------------------------------
    banner("Step 3: Build AML net skeleton")
    G = nx.MultiDiGraph()
    for mut in MUTATION_COLUMNS:
        G.add_node(f"mut::{mut}", layer='L1_genome', node_kind='mutation')
    all_drugs = set(fits_ok['inhibitor'].unique()) | set(drug_gene['inhibitor'].unique())
    for drug in all_drugs:
        G.add_node(f"drug::{drug}", layer='L7_pharmacome', node_kind='drug')
    gene_nodes = set(drug_gene['Symbol'].astype(str).str.upper().unique())
    for gene in gene_nodes:
        G.add_node(f"gene::{gene}", layer='L7_pharmacome', node_kind='gene_target')
    for _, row in drug_gene.iterrows():
        G.add_edge(f"drug::{row['inhibitor']}", f"gene::{str(row['Symbol']).upper()}",
                   edge_kind='drug_targets_gene')
    for pid, mut_row in mut_frame.iterrows():
        G.add_node(f"patient::{pid}", layer='L9_disease_map', node_kind='patient')
        for mut_col, status in mut_row.items():
            if status == 'positive':
                G.add_edge(f"patient::{pid}", f"mut::{mut_col}",
                           edge_kind='patient_has_mutation')
    for _, row in fits_ok.iterrows():
        pid = row['dbgap_subject_id']
        if pid not in mut_frame.index:
            continue
        G.add_edge(f"patient::{pid}", f"drug::{row['inhibitor']}",
                   edge_kind='patient_drug_sensitivity',
                   auc=float(row['auc']), ic50=float(row['ic50']))
    print(f"  Graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    # --------------------------------------------------------------
    # Step 4: Re-run FLT3-ITD+/NPM1+ query (regression check)
    # --------------------------------------------------------------
    banner("Step 4: QUERY A — FLT3-ITD+ / NPM1+ (regression check)")
    flt3npm1_ranked, n_flt3npm1 = run_genotype_query(
        G, mut_frame,
        {'FLT3-ITD': 'positive', 'NPM1': 'positive'},
        tag='FLT3-ITD+/NPM1+'
    )
    top10_a = flt3npm1_ranked.head(10)
    flt3_in_top10_a = int((top10_a['is_flt3_targeter']).sum())
    ven_in_top10_a = bool(top10_a['drug'].str.lower().str.contains('venetoclax').any())
    print(f"\n  QUERY A verdict: FLT3 drugs in top 10 = {flt3_in_top10_a}, "
          f"Venetoclax in top 10 = {ven_in_top10_a}")

    # --------------------------------------------------------------
    # Step 5: New query — TP53+ (ENCODING FIX TEST)
    # --------------------------------------------------------------
    banner("Step 5: QUERY B — TP53+ (tests encoding fix on a distinct genotype)")
    tp53_ranked, n_tp53 = run_genotype_query(
        G, mut_frame, {'TP53': 'positive'}, tag='TP53+'
    )
    top10_b = tp53_ranked.head(10)
    flt3_in_top10_b = int((top10_b['is_flt3_targeter']).sum())
    ven_in_top10_b = bool(top10_b['drug'].str.lower().str.contains('venetoclax').any())
    print(f"\n  QUERY B verdict: FLT3 drugs in top 10 = {flt3_in_top10_b}, "
          f"Venetoclax in top 10 = {ven_in_top10_b}")

    # --------------------------------------------------------------
    # Step 6: Comparative verdict
    # --------------------------------------------------------------
    banner("Step 6: Comparative verdict")
    # Test 1: Query A (FLT3-ITD+/NPM1+) still passes the original criterion
    a_pass = flt3_in_top10_a >= 1 and ven_in_top10_a
    # Test 2: TP53 cohort has a plausible number of patients
    b_has_cohort = n_tp53 >= MIN_GENOTYPE_MATCH
    # Test 3: Top 10 lists differ between cohorts (join is genotype-sensitive)
    top_a_drugs = set(top10_a['drug'].tolist())
    top_b_drugs = set(top10_b['drug'].tolist()) if len(top10_b) else set()
    jaccard = len(top_a_drugs & top_b_drugs) / len(top_a_drugs | top_b_drugs) \
              if top_b_drugs else 1.0
    top_lists_differ = jaccard < 0.8  # less than 80% overlap

    print(f"  Test 1 (Query A PASS regression):            "
          f"{'PASS' if a_pass else 'FAIL'}")
    print(f"  Test 2 (TP53 cohort size >= {MIN_GENOTYPE_MATCH}):            "
          f"{'PASS' if b_has_cohort else 'FAIL'} (n={n_tp53})")
    print(f"  Test 3 (top-10 lists differ, Jaccard<0.8):   "
          f"{'PASS' if top_lists_differ else 'FAIL'} (J={jaccard:.2f})")

    all_pass = a_pass and b_has_cohort and top_lists_differ
    if all_pass:
        verdict = 'PASS'
        msg = ("All three tests pass. Encoding fix works (TP53+ cohort "
               "is non-empty). Graph traversal is genotype-sensitive "
               "(different mutation profiles -> different drug rankings). "
               "Round 2.1b skeleton is validated on more than one biology.")
    else:
        verdict = 'PARTIAL/FAIL'
        reasons = []
        if not a_pass: reasons.append("Query A regression broken")
        if not b_has_cohort: reasons.append("TP53 cohort too small")
        if not top_lists_differ: reasons.append(
            "top-10 lists don't differ between genotypes — possible join problem")
        msg = f"Issues: {'; '.join(reasons)}. Investigate before proceeding."

    print(f"\n  VERDICT: {verdict}")
    print(f"  {msg}")

    # --------------------------------------------------------------
    # Step 7: Save
    # --------------------------------------------------------------
    banner("Step 7: Save")
    import pickle
    graph_path = RESULTS_DIR / 'aml_net_skeleton_v2.gpickle'
    with open(graph_path, 'wb') as f:
        pickle.dump(G, f)
    summary = {
        'verdict': verdict,
        'message': msg,
        'encodings_detected': encodings,
        'graph_stats': {'n_nodes': G.number_of_nodes(),
                        'n_edges': G.number_of_edges()},
        'query_A_FLT3_NPM1': {
            'n_matched': n_flt3npm1,
            'flt3_in_top10': flt3_in_top10_a,
            'venetoclax_in_top10': ven_in_top10_a,
            'top_15': flt3npm1_ranked.head(15).to_dict(orient='records'),
        },
        'query_B_TP53': {
            'n_matched': n_tp53,
            'flt3_in_top10': flt3_in_top10_b,
            'venetoclax_in_top10': ven_in_top10_b,
            'top_15': tp53_ranked.head(15).to_dict(orient='records'),
        },
        'jaccard_top10_overlap': float(jaccard),
    }
    with open(RESULTS_DIR / 'aml_net_skeleton_v2_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Graph pickled: {graph_path}")
    print(f"  Summary JSON:  {RESULTS_DIR}/aml_net_skeleton_v2_summary.json")


if __name__ == '__main__':
    main()
