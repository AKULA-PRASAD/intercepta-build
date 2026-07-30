#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1a — BeatAML 2.0 FLT3-ITD validation query
===============================================================

Written AFTER inspecting the real BeatAML 2.0 files. Every column name in
this script was verified in the schema inspection output. No guesses.

Verified schema (from inspect_beataml.py output):
  beataml_probit_curve_fits_v4_dbgap.txt:
      63,395 rows. Key cols: dbgap_subject_id (int), inhibitor (str),
      auc (float, primary potency measure — LOWER = MORE POTENT),
      converged (bool), curve_type ('decreasing'|'increasing'),
      all_gt_50 (bool — tumor resistant), all_lt_50 (bool — tumor sensitive).
  beataml_wv1to4_clinical.xlsx (sheet 'summary'):
      942 rows × 95 cols. Key cols: dbgap_subject_id (int),
      FLT3-ITD (str: 'positive'|'negative'), NPM1, allelic_ratio.
  beataml_drug_families.xlsx (sheet 'drug_gene'):
      651 rows. Key cols: inhibitor (str), Symbol (gene symbol, e.g. 'FLT3').

Validation query
----------------
Rank drugs by median AUC across FLT3-ITD+ patients. Lower AUC = more
potent. BeatAML's own drug_gene sheet tells us which drugs target FLT3.
If FLT3-targeting drugs cluster at the top of our ranking, the data
layer is working and Round 2.1a validation PASSES.

Pass / Partial / Fail criteria
------------------------------
- PASS: >= 3 FLT3-targeting drugs in top 10 of ranking
- PARTIAL: 1-2 FLT3-targeting drugs in top 10
- FAIL: 0 FLT3-targeting drugs in top 10

Data quality filters applied
----------------------------
- converged == True   (excludes non-converged curve fits)
- curve_type == 'decreasing'   (standard dose-response, ignore paradoxical)
- paper_inclusion == True   (BeatAML's own QC pass flag)
- all_gt_50 == False   (not fully resistant — otherwise AUC bounded high)
- Drug must have >= 10 FLT3-ITD+ patients tested (statistical reasonableness)

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 query_flt3_itd_drugs.py 2>&1 | tee \\
        ../results/beataml_flt3_itd_validation.txt

Author: Prasad Akula
Date:    April 21, 2026
Principle 15: report what the data shows, not what we want it to show.
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

# Min FLT3-ITD+ patient count per drug for the drug to enter the ranking.
# Rationale: drugs tested in only 2-3 FLT3-ITD+ patients would give noisy
# medians and could bias the top-10 artificially. 10 is a conservative floor.
MIN_N_PATIENTS = 10
TOP_N = 20


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def main():
    import pandas as pd

    # --------------------------------------------------------------
    # Step 1: Load clinical and find FLT3-ITD+ patients
    # --------------------------------------------------------------
    banner("Step 1: Identify FLT3-ITD+ patients from clinical annotations")
    clin = pd.read_excel(CLINICAL, sheet_name='summary')
    print(f"Clinical summary rows: {len(clin):,}")
    print(f"Unique patients (dbgap_subject_id): {clin['dbgap_subject_id'].nunique():,}")

    # Verify the column is as expected
    if 'FLT3-ITD' not in clin.columns:
        print(f"ERROR: column 'FLT3-ITD' missing from clinical summary sheet.")
        print(f"Available columns containing 'FLT3': "
              f"{[c for c in clin.columns if 'FLT3' in c.upper()]}")
        sys.exit(1)

    # Value distribution — one patient can appear multiple times (longitudinal
    # samples), so we collapse to unique patient status
    flt3_itd_per_sample = clin['FLT3-ITD'].value_counts(dropna=False)
    print(f"\nFLT3-ITD values across rows (patient-samples, not unique patients):")
    for v, n in flt3_itd_per_sample.items():
        print(f"  {str(v):<15s} {n:>5d}")

    # Collapse to unique patients: if any row says positive, patient is positive
    patient_flt3_itd = (
        clin[['dbgap_subject_id', 'FLT3-ITD']]
        .dropna(subset=['FLT3-ITD'])
        .groupby('dbgap_subject_id')['FLT3-ITD']
        .apply(lambda s: 'positive' if (s == 'positive').any() else 'negative')
    )
    itd_pos_patients = set(
        patient_flt3_itd[patient_flt3_itd == 'positive'].index.tolist()
    )
    itd_neg_patients = set(
        patient_flt3_itd[patient_flt3_itd == 'negative'].index.tolist()
    )
    print(f"\nUnique patients with FLT3-ITD annotation: "
          f"{len(patient_flt3_itd):,}")
    print(f"  FLT3-ITD positive: {len(itd_pos_patients):,}")
    print(f"  FLT3-ITD negative: {len(itd_neg_patients):,}")

    if len(itd_pos_patients) < 5:
        print(f"\nERROR: too few FLT3-ITD+ patients ({len(itd_pos_patients)}) "
              f"for meaningful ranking.")
        sys.exit(2)

    # --------------------------------------------------------------
    # Step 2: Load curve fits and filter for QC
    # --------------------------------------------------------------
    banner("Step 2: Load curve fits and apply quality filters")
    fits = pd.read_csv(CURVE_FITS, sep='\t', low_memory=False)
    print(f"Raw rows: {len(fits):,}")
    print(f"Unique inhibitors: {fits['inhibitor'].nunique():,}")
    print(f"Unique patients with drug data: "
          f"{fits['dbgap_subject_id'].nunique():,}")

    # Apply filters one at a time and report attrition
    n0 = len(fits)
    fits = fits[fits['paper_inclusion']]
    print(f"  After paper_inclusion==True:    {len(fits):,} (dropped {n0-len(fits):,})")
    n1 = len(fits)
    fits = fits[fits['converged']]
    print(f"  After converged==True:          {len(fits):,} (dropped {n1-len(fits):,})")
    n2 = len(fits)
    fits = fits[fits['curve_type'] == 'decreasing']
    print(f"  After curve_type=='decreasing': {len(fits):,} (dropped {n2-len(fits):,})")
    n3 = len(fits)
    fits = fits[~fits['all_gt_50']]
    print(f"  After all_gt_50==False:         {len(fits):,} (dropped {n3-len(fits):,})")

    # --------------------------------------------------------------
    # Step 3: Filter to FLT3-ITD+ patient subset
    # --------------------------------------------------------------
    banner("Step 3: Restrict to FLT3-ITD+ patient drug measurements")
    itd_fits = fits[fits['dbgap_subject_id'].isin(itd_pos_patients)].copy()
    print(f"Rows in FLT3-ITD+ subset: {len(itd_fits):,}")
    print(f"Unique FLT3-ITD+ patients with usable drug data: "
          f"{itd_fits['dbgap_subject_id'].nunique():,}")
    print(f"Unique inhibitors tested in FLT3-ITD+ cohort: "
          f"{itd_fits['inhibitor'].nunique():,}")

    # --------------------------------------------------------------
    # Step 4: Rank drugs by median AUC
    # --------------------------------------------------------------
    banner("Step 4: Rank drugs by median AUC (lower = more potent)")
    per_drug = (
        itd_fits.groupby('inhibitor')['auc']
        .agg(median_auc='median', mean_auc='mean', std_auc='std',
             n_patients='count', min_auc='min', max_auc='max')
        .reset_index()
    )
    per_drug = per_drug[per_drug['n_patients'] >= MIN_N_PATIENTS]
    per_drug = per_drug.sort_values('median_auc', ascending=True).reset_index(drop=True)
    per_drug.index = per_drug.index + 1  # 1-based rank
    print(f"Drugs with >= {MIN_N_PATIENTS} FLT3-ITD+ patients: {len(per_drug):,}")

    print(f"\nTop {TOP_N} most potent drugs vs FLT3-ITD+ cohort:")
    print(f"{'Rank':<6}{'Drug':<40}{'median_AUC':>12}{'n':>6}{'std':>10}")
    for rank, row in per_drug.head(TOP_N).iterrows():
        print(f"{rank:<6}{str(row['inhibitor'])[:38]:<40}"
              f"{row['median_auc']:>12.2f}{int(row['n_patients']):>6d}"
              f"{row['std_auc']:>10.2f}")

    # --------------------------------------------------------------
    # Step 5: Compare against BeatAML's own FLT3-inhibitor annotation
    # --------------------------------------------------------------
    banner("Step 5: Validate against BeatAML drug_gene FLT3-targeting list")
    drug_gene = pd.read_excel(DRUG_FAM, sheet_name='drug_gene')
    flt3_drugs_bam = set(
        drug_gene.loc[drug_gene['Symbol'].astype(str).str.upper() == 'FLT3',
                      'inhibitor'].tolist()
    )
    print(f"BeatAML-annotated FLT3-targeting drugs: {len(flt3_drugs_bam)}")
    for d in sorted(flt3_drugs_bam):
        print(f"  - {d}")

    # Intersect with our ranking
    per_drug['is_flt3_targeter'] = per_drug['inhibitor'].isin(flt3_drugs_bam)
    flt3_ranked = per_drug[per_drug['is_flt3_targeter']].copy()

    print(f"\nFLT3-targeting drugs in our ranking (any rank):")
    print(f"{'Rank':<6}{'Drug':<40}{'median_AUC':>12}{'n':>6}")
    for rank, row in flt3_ranked.iterrows():
        in_top = ''
        if rank <= 10:
            in_top = '*** TOP 10 ***'
        elif rank <= 20:
            in_top = '(top 20)'
        print(f"{rank:<6}{str(row['inhibitor'])[:38]:<40}"
              f"{row['median_auc']:>12.2f}{int(row['n_patients']):>6d} {in_top}")

    # --------------------------------------------------------------
    # Step 6: Verdict
    # --------------------------------------------------------------
    banner("Step 6: Validation verdict")
    flt3_in_top10 = (flt3_ranked.index <= 10).sum()
    flt3_in_top20 = (flt3_ranked.index <= 20).sum()
    print(f"FLT3-targeting drugs in top 10: {flt3_in_top10}")
    print(f"FLT3-targeting drugs in top 20: {flt3_in_top20}")
    print(f"FLT3-targeting drugs total in ranking: {len(flt3_ranked)}")

    if flt3_in_top10 >= 3:
        verdict = 'PASS'
        message = (f"{flt3_in_top10} FLT3-targeting drugs in top 10. "
                   f"Expected FLT3-ITD biology is recovered from BeatAML "
                   f"data. Round 2.1a data foundation works.")
    elif flt3_in_top10 >= 1:
        verdict = 'PARTIAL'
        message = (f"Only {flt3_in_top10} FLT3 inhibitor in top 10 "
                   f"(expected 3+). Check drug family assignments, cohort "
                   f"size, and whether quality filters were too strict.")
    else:
        verdict = 'FAIL'
        message = (f"Zero FLT3-targeting drugs in top 10. Either the join "
                   f"is broken, the FLT3-ITD filter is wrong, or AUC "
                   f"direction is inverted. DO NOT proceed to Round 2.1b.")

    print(f"\nVERDICT: {verdict}")
    print(f"  {message}")

    # --------------------------------------------------------------
    # Step 7: Save results
    # --------------------------------------------------------------
    banner("Step 7: Save outputs")
    ranking_csv = RESULTS_DIR / 'beataml_flt3_itd_drug_ranking.csv'
    per_drug.to_csv(ranking_csv)
    print(f"Full ranking:     {ranking_csv}")

    summary = {
        'validation_query': 'drugs most potent vs FLT3-ITD+ BeatAML 2.0 cohort',
        'verdict': verdict,
        'message': message,
        'n_flt3_itd_positive_patients': len(itd_pos_patients),
        'n_flt3_itd_negative_patients': len(itd_neg_patients),
        'n_drugs_tested_in_itd_cohort': int(itd_fits['inhibitor'].nunique()),
        'n_drugs_after_min_n_filter': len(per_drug),
        'min_n_patients_required': MIN_N_PATIENTS,
        'flt3_targeting_drugs_beataml': sorted(flt3_drugs_bam),
        'flt3_in_top_10': int(flt3_in_top10),
        'flt3_in_top_20': int(flt3_in_top20),
        'top_10': [
            {'rank': int(r), 'drug': str(row['inhibitor']),
             'median_auc': float(row['median_auc']),
             'n_patients': int(row['n_patients']),
             'is_flt3_targeter': bool(row['is_flt3_targeter'])}
            for r, row in per_drug.head(10).iterrows()
        ],
        'flt3_drugs_ranked': [
            {'rank': int(r), 'drug': str(row['inhibitor']),
             'median_auc': float(row['median_auc']),
             'n_patients': int(row['n_patients'])}
            for r, row in flt3_ranked.iterrows()
        ],
    }
    summary_json = RESULTS_DIR / 'beataml_flt3_itd_validation_summary.json'
    with open(summary_json, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary:          {summary_json}")


if __name__ == '__main__':
    main()
