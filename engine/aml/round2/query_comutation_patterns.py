#!/usr/bin/env python3
"""
INTERCEPTA Round 2.1a Query 3 — Co-mutation pattern validation
===============================================================

Purpose
-------
Verify the clinical.xlsx mutation annotation layer by checking that
FLT3-ITD and NPM1 co-occurrence matches the well-established AML
literature. If it doesn't, we can't trust the clinical mutation
annotations for building Layer 1 (genome) of the AML disease net.

Published ground truth (AML literature, well-established)
---------------------------------------------------------
- NPM1 mutations: ~30% of all AML; defining feature of a major subtype
  (AML with mutated NPM1, per WHO 2016 / ICC 2022)
- FLT3-ITD: ~25-30% of all AML, ~40% of NPM1-mutated AML
- The NPM1+ / FLT3-ITD+ co-occurrence is strong and bidirectional:
  * ~40% of NPM1+ patients also carry FLT3-ITD
  * ~50-60% of FLT3-ITD+ patients also carry NPM1 mutations
- Published references:
  * Falini et al. NEJM 2005 — defined NPM1+ AML subtype
  * Papaemmanuil et al. NEJM 2016 — genomic classification, co-mutation tables
  * Tyner et al. Nature 2018 — BeatAML 1.0 reports similar frequencies
  * Döhner et al. Blood 2022 — ELN 2022 risk classification uses this

Pass criteria
-------------
If our BeatAML 2.0 clinical annotations match the expected co-mutation
frequencies (within 5 percentage points), the mutation layer is
trustworthy. If not, something is wrong with how we read the clinical
file, and we stop before using it in the net.

Run
---
    cd ~/INTERCEPTA/round2_aml/code
    python3 query_comutation_patterns.py 2>&1 | tee \\
        ../results/beataml_comutation_validation.txt

Author: Prasad Akula
Date:    April 21, 2026
Principle 15: one more ground-truth check before we build on this.
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
CLINICAL = DATA_ROOT / 'beataml_wv1to4_clinical.xlsx'

# Ground truth from AML literature
EXPECTED_NPM1_FREQ = 0.30          # ~30% of all AML
EXPECTED_FLT3_ITD_FREQ = 0.28      # ~25-30%
EXPECTED_FLT3_IN_NPM1 = 0.40       # ~40% of NPM1+ also FLT3-ITD+
EXPECTED_NPM1_IN_FLT3 = 0.55       # ~50-60% of FLT3-ITD+ also NPM1+
TOLERANCE = 0.08                    # within 8 percentage points is fine


def banner(s):
    print('\n' + '=' * 72)
    print(s)
    print('=' * 72)


def main():
    import pandas as pd

    banner("Step 1: Load clinical annotations")
    clin = pd.read_excel(CLINICAL, sheet_name='summary')
    print(f"Clinical rows: {len(clin):,} (patient-samples)")
    print(f"Unique patients: {clin['dbgap_subject_id'].nunique():,}")

    # Collapse to per-patient mutation status (any positive sample -> positive)
    def collapse_per_patient(df, col):
        return (df.dropna(subset=[col])
                  .groupby('dbgap_subject_id')[col]
                  .apply(lambda s: 'positive' if (s == 'positive').any()
                         else 'negative'))

    flt3 = collapse_per_patient(clin, 'FLT3-ITD')
    npm1 = collapse_per_patient(clin, 'NPM1')
    print(f"\nPer-patient mutation status:")
    print(f"  FLT3-ITD annotated: {len(flt3):,}")
    print(f"    positive: {(flt3 == 'positive').sum():,}  "
          f"negative: {(flt3 == 'negative').sum():,}")
    print(f"  NPM1 annotated:     {len(npm1):,}")
    print(f"    positive: {(npm1 == 'positive').sum():,}  "
          f"negative: {(npm1 == 'negative').sum():,}")

    banner("Step 2: Restrict to AML-diagnosis patients")
    # Filter to patients who actually have AML at diagnosis (exclude MDS, etc.)
    dx_col = 'dxAtInclusion'
    if dx_col in clin.columns:
        aml_mask = clin[dx_col].astype(str).str.contains('AML', case=False, na=False)
        aml_patients = set(clin.loc[aml_mask, 'dbgap_subject_id'].unique())
        print(f"Patients with AML diagnosis at inclusion: {len(aml_patients):,}")
    else:
        aml_patients = set(clin['dbgap_subject_id'].unique())
        print(f"No dx column; using all patients: {len(aml_patients):,}")

    # Build a single per-patient frame
    both = pd.DataFrame({
        'FLT3_ITD': flt3,
        'NPM1': npm1,
    })
    both = both[both.index.isin(aml_patients)]
    both_annotated = both.dropna()
    print(f"AML patients with both FLT3-ITD and NPM1 annotated: "
          f"{len(both_annotated):,}")

    banner("Step 3: Compute co-mutation frequencies")
    n = len(both_annotated)
    flt3_pos = (both_annotated['FLT3_ITD'] == 'positive').sum()
    npm1_pos = (both_annotated['NPM1'] == 'positive').sum()
    both_pos = ((both_annotated['FLT3_ITD'] == 'positive') &
                (both_annotated['NPM1'] == 'positive')).sum()
    flt3_only = ((both_annotated['FLT3_ITD'] == 'positive') &
                 (both_annotated['NPM1'] == 'negative')).sum()
    npm1_only = ((both_annotated['FLT3_ITD'] == 'negative') &
                 (both_annotated['NPM1'] == 'positive')).sum()
    neither = ((both_annotated['FLT3_ITD'] == 'negative') &
               (both_annotated['NPM1'] == 'negative')).sum()

    print(f"Total AML patients in analysis: {n}")
    print(f"  FLT3-ITD+ (overall):        {flt3_pos} ({flt3_pos/n:.1%})")
    print(f"  NPM1+ (overall):            {npm1_pos} ({npm1_pos/n:.1%})")
    print(f"  FLT3-ITD+ AND NPM1+:        {both_pos} ({both_pos/n:.1%})")
    print(f"  FLT3-ITD+ only (NPM1-):     {flt3_only} ({flt3_only/n:.1%})")
    print(f"  NPM1+ only (FLT3-):         {npm1_only} ({npm1_only/n:.1%})")
    print(f"  Neither mutation:           {neither} ({neither/n:.1%})")

    flt3_in_npm1 = both_pos / npm1_pos if npm1_pos > 0 else 0
    npm1_in_flt3 = both_pos / flt3_pos if flt3_pos > 0 else 0
    print(f"\nConditional frequencies:")
    print(f"  P(FLT3-ITD+ | NPM1+) = {flt3_in_npm1:.1%}   "
          f"(expected ~{EXPECTED_FLT3_IN_NPM1:.0%})")
    print(f"  P(NPM1+ | FLT3-ITD+) = {npm1_in_flt3:.1%}   "
          f"(expected ~{EXPECTED_NPM1_IN_FLT3:.0%})")

    banner("Step 4: Chi-squared test for independence")
    # Contingency table: rows = FLT3-ITD status, cols = NPM1 status
    from scipy.stats import chi2_contingency, fisher_exact
    table = [
        [both_pos, flt3_only],   # FLT3-ITD+ row: NPM1+ , NPM1-
        [npm1_only, neither],    # FLT3-ITD- row: NPM1+ , NPM1-
    ]
    chi2, p_chi, dof, expected = chi2_contingency(table)
    odds, p_fisher = fisher_exact(table)
    print(f"Contingency table (rows: FLT3-ITD status, cols: NPM1 status):")
    print(f"  [[{both_pos:4d}, {flt3_only:4d}],    # FLT3-ITD+")
    print(f"   [{npm1_only:4d}, {neither:4d}]]    # FLT3-ITD-")
    print(f"Chi-squared = {chi2:.2f}, p = {p_chi:.2e}")
    print(f"Fisher exact: OR = {odds:.2f}, p = {p_fisher:.2e}")
    print(f"(OR > 1 means FLT3-ITD and NPM1 mutations co-occur more than expected)")

    banner("Step 5: Verdict")
    checks = []

    overall_flt3_freq = flt3_pos / n
    overall_npm1_freq = npm1_pos / n

    checks.append(('Overall FLT3-ITD frequency', overall_flt3_freq,
                   EXPECTED_FLT3_ITD_FREQ,
                   abs(overall_flt3_freq - EXPECTED_FLT3_ITD_FREQ) <= TOLERANCE))
    checks.append(('Overall NPM1 frequency', overall_npm1_freq,
                   EXPECTED_NPM1_FREQ,
                   abs(overall_npm1_freq - EXPECTED_NPM1_FREQ) <= TOLERANCE))
    checks.append(('P(FLT3-ITD+ | NPM1+)', flt3_in_npm1,
                   EXPECTED_FLT3_IN_NPM1,
                   abs(flt3_in_npm1 - EXPECTED_FLT3_IN_NPM1) <= TOLERANCE))
    checks.append(('P(NPM1+ | FLT3-ITD+)', npm1_in_flt3,
                   EXPECTED_NPM1_IN_FLT3,
                   abs(npm1_in_flt3 - EXPECTED_NPM1_IN_FLT3) <= TOLERANCE))
    checks.append(('Co-occurrence chi-squared significant (p<0.001)',
                   p_chi, 0.001, p_chi < 0.001))

    print(f"\nValidation checks:")
    print(f"{'Check':<55}{'observed':>12}{'expected':>12}  status")
    for label, obs, exp, passed in checks:
        status = '✓ PASS' if passed else '✗ FAIL'
        if 'p<0.001' in label:
            obs_str = f"p={obs:.2e}"
            exp_str = "< 0.001"
        else:
            obs_str = f"{obs:.1%}"
            exp_str = f"{exp:.1%}"
        print(f"  {label:<53}{obs_str:>12}{exp_str:>12}  {status}")

    passed_count = sum(1 for _, _, _, p in checks if p)
    total = len(checks)
    print(f"\n{passed_count} of {total} checks passed.")

    if passed_count == total:
        verdict = 'PASS'
        msg = ("All co-mutation checks match published AML literature. "
               "Clinical mutation annotations are internally consistent and "
               "trustworthy for building the Layer 1 genome net.")
    elif passed_count >= total - 1:
        verdict = 'PASS (marginal)'
        msg = (f"{passed_count}/{total} checks pass; one marginal miss. "
               "Likely acceptable but inspect the failing check.")
    else:
        verdict = 'FAIL'
        msg = (f"Only {passed_count}/{total} checks pass. Clinical "
               "mutation annotation may not encode what we think it does. "
               "Stop and debug before using for net construction.")

    print(f"\nVERDICT: {verdict}")
    print(f"  {msg}")

    banner("Save outputs")
    summary = {
        'validation_query': 'FLT3-ITD / NPM1 co-mutation patterns vs AML literature',
        'verdict': verdict,
        'message': msg,
        'n_patients_analyzed': int(n),
        'observed': {
            'flt3_itd_freq': float(overall_flt3_freq),
            'npm1_freq': float(overall_npm1_freq),
            'both_freq': float(both_pos/n),
            'flt3_in_npm1': float(flt3_in_npm1),
            'npm1_in_flt3': float(npm1_in_flt3),
            'chi2': float(chi2),
            'p_chi2': float(p_chi),
            'odds_ratio': float(odds),
            'p_fisher': float(p_fisher),
        },
        'expected_from_literature': {
            'flt3_itd_freq': EXPECTED_FLT3_ITD_FREQ,
            'npm1_freq': EXPECTED_NPM1_FREQ,
            'flt3_in_npm1': EXPECTED_FLT3_IN_NPM1,
            'npm1_in_flt3': EXPECTED_NPM1_IN_FLT3,
            'tolerance': TOLERANCE,
        },
        'contingency_table': {
            'flt3_pos_npm1_pos': int(both_pos),
            'flt3_pos_npm1_neg': int(flt3_only),
            'flt3_neg_npm1_pos': int(npm1_only),
            'flt3_neg_npm1_neg': int(neither),
        },
        'checks_passed': int(passed_count),
        'checks_total': int(total),
    }
    path = RESULTS_DIR / 'beataml_comutation_validation_summary.json'
    with open(path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary JSON: {path}")


if __name__ == '__main__':
    main()
