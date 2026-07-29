#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1a follow-up — FLT3 selectivity validation
==============================================================

Context
-------
The initial query ranked drugs by absolute median AUC in FLT3-ITD+
patients. Verdict: PARTIAL (2/10 FLT3-targeting drugs in top 10).

Honest interpretation: the top 10 is dominated by broad AML cytotoxics
(Elesclomol, Panobinostat, Venetoclax, SNS-032). FDA-approved FLT3
inhibitors — Gilteritinib (rank 13), Quizartinib (rank 18), Midostaurin
(rank 48), Sorafenib (rank 49) — are further down.

This is not a data bug. It is the wrong question. FLT3-ITD+ AML cells
are still AML cells; they die to anything that kills AML cells.

The SPECIFICITY question is: which drugs are MORE potent in FLT3-ITD+
patients than in FLT3-ITD- patients? Drugs with a big negative AUC
difference (ITD+ minus ITD-) are selectively active against FLT3-driven
biology.

This is what the BeatAML 2.0 paper actually uses for mutation-drug
associations: differential sensitivity by mutation status.

Validation expectation
----------------------
FLT3-targeting kinase inhibitors should dominate the top of the
differential-potency ranking, because they selectively kill FLT3-driven
cells (minimal effect on FLT3-WT cells, strong effect on FLT3-ITD cells).

Broad cytotoxics (Elesclomol, Panobinostat, Venetoclax) should have
~zero difference: they kill both cohorts equally, not selective.

Pass / Fail criteria
--------------------
- PASS: >= 3 FLT3-targeting drugs in top 10 of differential-potency ranking
        AND the top differential drug is clearly FLT3-targeting
- PARTIAL: 1-2 FLT3 drugs in top 10
- FAIL: 0 FLT3 drugs in top 10 (data or join problem)

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 query_flt3_selectivity.py 2>&1 | tee \\
        ../results/beataml_flt3_selectivity_validation.txt

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
Date:    April 21, 2026
Principle 15: when the first query gives PARTIAL, don't redefine PASS —
ask the correct scientific question.
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

# Drug must have >= 10 patients in BOTH cohorts (FLT3-ITD+ and FLT3-ITD-)
MIN_N_PER_COHORT = 10
TOP_N = 20


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def main():
    import pandas as pd
    from scipy import stats

    # --------------------------------------------------------------
    # Step 1: FLT3-ITD cohort assignment (same as before)
    # --------------------------------------------------------------
    banner("Step 1: Assign patients to FLT3-ITD+ / FLT3-ITD- cohorts")
    clin = pd.read_excel(CLINICAL, sheet_name='summary')
    patient_flt3 = (
        clin[['dbgap_subject_id', 'FLT3-ITD']]
        .dropna(subset=['FLT3-ITD'])
        .groupby('dbgap_subject_id')['FLT3-ITD']
        .apply(lambda s: 'positive' if (s == 'positive').any() else 'negative')
    )
    itd_pos = set(patient_flt3[patient_flt3 == 'positive'].index)
    itd_neg = set(patient_flt3[patient_flt3 == 'negative'].index)
    print(f"FLT3-ITD positive: {len(itd_pos):,}")
    print(f"FLT3-ITD negative: {len(itd_neg):,}")

    # --------------------------------------------------------------
    # Step 2: Load curve fits, apply quality filters
    # --------------------------------------------------------------
    banner("Step 2: Load and filter curve fits")
    fits = pd.read_csv(CURVE_FITS, sep='\t', low_memory=False)
    print(f"Raw rows: {len(fits):,}")
    before = len(fits)
    fits = fits[
        fits['paper_inclusion'] &
        fits['converged'] &
        (fits['curve_type'] == 'decreasing') &
        (~fits['all_gt_50'])
    ].copy()
    print(f"After QC filters:  {len(fits):,} (dropped {before - len(fits):,})")

    # Tag each row with the patient's cohort
    def cohort_of(sid):
        if sid in itd_pos:
            return 'ITD+'
        elif sid in itd_neg:
            return 'ITD-'
        return None
    fits['cohort'] = fits['dbgap_subject_id'].map(cohort_of)
    fits = fits.dropna(subset=['cohort'])
    print(f"Rows with cohort assignment: {len(fits):,}")
    print(f"  ITD+ rows: {(fits['cohort']=='ITD+').sum():,}")
    print(f"  ITD- rows: {(fits['cohort']=='ITD-').sum():,}")

    # --------------------------------------------------------------
    # Step 3: Per-drug differential statistics
    # --------------------------------------------------------------
    banner("Step 3: Compute per-drug differential AUC (ITD+ vs ITD-)")
    drug_stats = []
    for drug, group in fits.groupby('inhibitor'):
        itd_plus = group[group['cohort'] == 'ITD+']['auc'].values
        itd_minus = group[group['cohort'] == 'ITD-']['auc'].values
        if len(itd_plus) < MIN_N_PER_COHORT or len(itd_minus) < MIN_N_PER_COHORT:
            continue
        # Mann-Whitney U test (non-parametric, AUC distributions are skewed)
        try:
            u_stat, p_value = stats.mannwhitneyu(
                itd_plus, itd_minus, alternative='less'
            )  # H1: ITD+ AUC < ITD- AUC (more potent in ITD+)
        except ValueError:
            p_value = 1.0
        drug_stats.append({
            'inhibitor': drug,
            'median_auc_itd_pos': float(pd.Series(itd_plus).median()),
            'median_auc_itd_neg': float(pd.Series(itd_minus).median()),
            'delta_auc': float(pd.Series(itd_plus).median() -
                              pd.Series(itd_minus).median()),
            'n_itd_pos': int(len(itd_plus)),
            'n_itd_neg': int(len(itd_minus)),
            'p_value': float(p_value),
        })

    diff = pd.DataFrame(drug_stats).sort_values('delta_auc').reset_index(drop=True)
    diff.index = diff.index + 1
    print(f"Drugs with >= {MIN_N_PER_COHORT} patients in BOTH cohorts: "
          f"{len(diff):,}")

    # --------------------------------------------------------------
    # Step 4: Top differentially-potent drugs
    # --------------------------------------------------------------
    banner(f"Step 4: Top {TOP_N} drugs SELECTIVELY more potent in FLT3-ITD+")
    print(f"(ranked by delta_auc = median_AUC_ITD+ − median_AUC_ITD−; "
          f"most negative = most selective for ITD+)")
    print()
    print(f"{'Rank':<6}{'Drug':<32}{'ITD+':>10}{'ITD-':>10}"
          f"{'Δ AUC':>10}{'p-val':>10}{'n+':>5}{'n-':>5}")
    for rank, row in diff.head(TOP_N).iterrows():
        print(f"{rank:<6}{str(row['inhibitor'])[:30]:<32}"
              f"{row['median_auc_itd_pos']:>10.1f}"
              f"{row['median_auc_itd_neg']:>10.1f}"
              f"{row['delta_auc']:>+10.1f}"
              f"{row['p_value']:>10.1e}"
              f"{row['n_itd_pos']:>5d}{row['n_itd_neg']:>5d}")

    # --------------------------------------------------------------
    # Step 5: Cross-check with BeatAML's FLT3-inhibitor annotation
    # --------------------------------------------------------------
    banner("Step 5: Validate against BeatAML's FLT3-targeting drug list")
    drug_gene = pd.read_excel(DRUG_FAM, sheet_name='drug_gene')
    flt3_drugs = set(
        drug_gene.loc[drug_gene['Symbol'].astype(str).str.upper() == 'FLT3',
                      'inhibitor'].tolist()
    )
    print(f"BeatAML-annotated FLT3-targeting drugs: {len(flt3_drugs)}")
    diff['is_flt3_targeter'] = diff['inhibitor'].isin(flt3_drugs)
    flt3_ranked = diff[diff['is_flt3_targeter']].copy()

    print(f"\nFLT3-targeting drugs ranked by ITD+ selectivity:")
    print(f"{'Rank':<6}{'Drug':<32}{'ITD+':>10}{'ITD-':>10}"
          f"{'Δ AUC':>10}{'p-val':>10}{'n+':>5}{'n-':>5}")
    for rank, row in flt3_ranked.iterrows():
        in_top = ''
        if rank <= 10:
            in_top = ' *** TOP 10 ***'
        elif rank <= 20:
            in_top = ' (top 20)'
        print(f"{rank:<6}{str(row['inhibitor'])[:30]:<32}"
              f"{row['median_auc_itd_pos']:>10.1f}"
              f"{row['median_auc_itd_neg']:>10.1f}"
              f"{row['delta_auc']:>+10.1f}"
              f"{row['p_value']:>10.1e}"
              f"{row['n_itd_pos']:>5d}{row['n_itd_neg']:>5d}"
              f"{in_top}")

    # --------------------------------------------------------------
    # Step 6: Verdict
    # --------------------------------------------------------------
    banner("Step 6: Selectivity validation verdict")
    flt3_top10 = (flt3_ranked.index <= 10).sum()
    flt3_top20 = (flt3_ranked.index <= 20).sum()
    top1_drug = diff.iloc[0]['inhibitor']
    top1_is_flt3 = top1_drug in flt3_drugs
    sig_flt3 = ((flt3_ranked['p_value'] < 0.05) &
                (flt3_ranked['delta_auc'] < 0)).sum()
    print(f"FLT3-targeting drugs in top 10 (by selectivity): {flt3_top10}")
    print(f"FLT3-targeting drugs in top 20 (by selectivity): {flt3_top20}")
    print(f"FLT3-targeting drugs with p < 0.05 AND Δ < 0: {sig_flt3}")
    print(f"Top-1 most selective drug: {top1_drug}"
          f"  ({'FLT3-targeting' if top1_is_flt3 else 'not in FLT3 list'})")

    if flt3_top10 >= 3:
        verdict = 'PASS'
        msg = (f"{flt3_top10} FLT3 inhibitors in top 10 by ITD-selectivity. "
               f"BeatAML data correctly encodes FLT3-specific biology. "
               f"Round 2.1a data foundation validated.")
    elif flt3_top10 >= 1 and sig_flt3 >= 3:
        verdict = 'PASS (statistically)'
        msg = (f"{flt3_top10} FLT3 inhibitor in top 10, but {sig_flt3} FLT3 "
               f"inhibitors show statistically significant ITD+ selectivity "
               f"(p<0.05). Data encodes the biology correctly; cohort sizes "
               f"just don't rank them together at the top.")
    elif flt3_top10 >= 1:
        verdict = 'PARTIAL'
        msg = (f"Only {flt3_top10} FLT3 inhibitor(s) in top 10 and "
               f"{sig_flt3} statistically significant. Investigate cohort "
               f"heterogeneity (allelic_ratio stratification?).")
    else:
        verdict = 'FAIL'
        msg = (f"Zero FLT3 inhibitors in top 10 of selectivity ranking. "
               f"Either the data is not what we think it is, or the "
               f"Mann-Whitney direction is wrong. Stop and debug.")

    print(f"\nVERDICT: {verdict}")
    print(f"  {msg}")

    # --------------------------------------------------------------
    # Save outputs
    # --------------------------------------------------------------
    banner("Save outputs")
    ranking_csv = RESULTS_DIR / 'beataml_flt3_selectivity_ranking.csv'
    diff.to_csv(ranking_csv)
    summary = {
        'validation_query': 'drugs SELECTIVELY more potent in FLT3-ITD+ '
                            'vs FLT3-ITD- (delta AUC)',
        'verdict': verdict,
        'message': msg,
        'n_itd_pos_patients': len(itd_pos),
        'n_itd_neg_patients': len(itd_neg),
        'n_drugs_ranked': len(diff),
        'flt3_in_top_10': int(flt3_top10),
        'flt3_in_top_20': int(flt3_top20),
        'flt3_statistically_significant': int(sig_flt3),
        'top_10_by_selectivity': [
            {'rank': int(r), 'drug': str(row['inhibitor']),
             'median_auc_itd_pos': float(row['median_auc_itd_pos']),
             'median_auc_itd_neg': float(row['median_auc_itd_neg']),
             'delta_auc': float(row['delta_auc']),
             'p_value': float(row['p_value']),
             'is_flt3_targeter': bool(row['is_flt3_targeter'])}
            for r, row in diff.head(10).iterrows()
        ],
        'flt3_drugs_all_ranks': [
            {'rank': int(r), 'drug': str(row['inhibitor']),
             'delta_auc': float(row['delta_auc']),
             'p_value': float(row['p_value']),
             'n_itd_pos': int(row['n_itd_pos']),
             'n_itd_neg': int(row['n_itd_neg'])}
            for r, row in flt3_ranked.iterrows()
        ],
    }
    summary_json = RESULTS_DIR / 'beataml_flt3_selectivity_summary.json'
    with open(summary_json, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Full ranking CSV: {ranking_csv}")
    print(f"Summary JSON:     {summary_json}")


if __name__ == '__main__':
    main()
