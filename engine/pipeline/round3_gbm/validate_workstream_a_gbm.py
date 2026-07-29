#!/usr/bin/env python3
"""
INTERCEPTA Workstream A Validation — GBM as primary test disease

Per Vision Part 7.1 ("validation-first principle"): every disease begins
with a validation phase. Workstream A built the data layer for any disease.
This script tests whether that layer produces clinically meaningful output
for GBM, our primary live-test disease.

Five tests, each compared against published GBM ground truth:
  1. Drug ranking vs NCCN GBM standard of care
  2. Trial novelty check vs known white-space targets
  3. BBB penetration of top-ranked compounds
  4. Undruggable priority list vs known GBM tumor suppressors
  5. Trial activity vs ChEMBL compound coverage cross-correlation

Output: validation report with PASS/FAIL/CHECK per test + diagnostic detail.
Saved as validation_workstream_a_gbm.md.
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

# ============================================================
# Ground truth for GBM (sourced from public, well-established references)
# ============================================================

# NCCN GBM Guidelines / FDA-approved GBM therapies as of 2024-2025
# Sources: NCCN.org Central Nervous System Cancers, FDA approval database
GBM_STANDARD_OF_CARE = {
    'Temozolomide': {
        'role': 'first_line_concurrent_adjuvant',
        'mechanism': 'DNA alkylation; MGMT-dependent',
        'fda_approved_year': 1999,
        'expected_pipeline_rank': 'top_5',
    },
    'Bevacizumab': {
        'role': 'recurrent',
        'mechanism': 'VEGFA inhibitor',
        'fda_approved_year': 2009,
        'expected_pipeline_rank': 'top_30',
    },
    'Lomustine': {
        'role': 'recurrent_alone_or_combo',
        'mechanism': 'DNA alkylation',
        'fda_approved_year': 1976,
        'expected_pipeline_rank': 'top_30',
    },
    'Carmustine': {
        'role': 'historical_recurrent',
        'mechanism': 'DNA alkylation',
        'fda_approved_year': 1977,
        'expected_pipeline_rank': 'top_50',
    },
}

# Known GBM tumor suppressors by mutation frequency in TCGA-GBM
# Source: TCGA-GBM PanCancer Atlas, Brennan et al. Cell 2013
GBM_TUMOR_SUPPRESSORS_BY_MUTATION = {
    'TP53': {'mutation_freq_pct': 28, 'role': 'tumor_suppressor', 'druggability': 'undruggable_direct'},
    'PTEN': {'mutation_freq_pct': 25, 'role': 'tumor_suppressor', 'druggability': 'undruggable_direct'},
    'NF1': {'mutation_freq_pct': 11, 'role': 'tumor_suppressor', 'druggability': 'undruggable_direct'},
    'RB1': {'mutation_freq_pct': 7, 'role': 'tumor_suppressor', 'druggability': 'undruggable_direct'},
    'ATRX': {'mutation_freq_pct': 8, 'role': 'tumor_suppressor', 'druggability': 'undruggable_direct'},
    'CDKN2A': {'mutation_freq_pct': 50, 'role': 'tumor_suppressor', 'druggability': 'undruggable_direct'},
}

# Known GBM oncogenic drivers with active drug development
# Source: TCGA-GBM, Wang et al. Cancer Cell 2017
GBM_ONCOGENIC_DRIVERS = {
    'EGFR': {'amp_or_mut_pct': 57, 'expected_compounds': '>100', 'has_clinical_trials_in_gbm': True},
    'PDGFRA': {'amp_or_mut_pct': 13, 'expected_compounds': '>20', 'has_clinical_trials_in_gbm': True},
    'IDH1': {'mutation_pct_recurrent': 5, 'expected_compounds': '>10', 'has_clinical_trials_in_gbm': True},
    'MET': {'amp_or_mut_pct': 4, 'expected_compounds': '>20', 'has_clinical_trials_in_gbm': True},
    'BRAF': {'mutation_pct': 2, 'expected_compounds': '>20', 'has_clinical_trials_in_gbm': True},
    'VEGFA': {'role': 'angiogenesis_target', 'expected_compounds': '>5', 'has_clinical_trials_in_gbm': True},
}

# Known GBM clinical white-space (high biological priority, no effective approved therapy)
GBM_WHITE_SPACE_TARGETS = ['NF1', 'ATRX', 'PTEN', 'RB1', 'TP53', 'CDKN2A', 'CDKN2B']

# BBB penetration heuristic: rule-of-five-like + Lipinski-CNS variant
# Source: Pajouhesh & Lenz Drug Discov Today 2005, Wager et al. ACS Chem Neurosci 2010
def bbb_penetration_likely(compound):
    """Heuristic BBB penetration based on available compound metadata.
    HONEST LIMITATION: This is a coarse heuristic, not a validated MPO score.
    Relies on data we may not have for every compound — returns 'unknown' if so.

    CNS MPO criteria (simplified): MW <= 500, logP 1-4, polar surface area <= 90, HBD <= 3.
    We don't have logP/PSA/HBD in our ChEMBL dump. We check what we can:
      - MW from standard_value if standard_units == 'g/mol' (rare; usually IC50)
    """
    # We genuinely do not have BBB-relevant properties in our current cache.
    # This validation surfaces that data gap honestly rather than papering over it.
    return 'data_unavailable'


# ============================================================
# Load the post-Action-1 GBM net
# ============================================================

def load_gbm_net():
    net_path = Path.home() / 'INTERCEPTA/round3_gbm_live_test/results/gbm_disease_net_action1.json'
    if not net_path.exists():
        print(f'ERROR: GBM net not found at {net_path}')
        print(f'Run intercepta_pipeline_v0.py first to generate it.')
        sys.exit(1)
    with open(net_path) as f:
        return json.load(f)


# ============================================================
# Test 1: Drug ranking vs NCCN GBM standard of care
# ============================================================

def test_1_soc_ranking(net):
    """
    Test whether rank_drugs_for_disease ranks GBM standard-of-care drugs
    in their expected positions.
    """
    print()
    print('=' * 70)
    print('Test 1: Drug ranking vs NCCN GBM standard of care')
    print('=' * 70)

    # Import and run the ranking
    sys.path.insert(0, str(Path(__file__).parent))
    from intercepta_pipeline_v0 import rank_drugs_for_disease

    ranked = rank_drugs_for_disease('glioblastoma', top_n=286)
    if ranked is None or len(ranked) == 0:
        print('  FAIL: rank_drugs_for_disease returned empty')
        return {'status': 'FAIL', 'reason': 'no_rankings_returned'}

    print(f'  Total drugs ranked: {len(ranked)}')

    findings = []
    soc_results = {}
    for drug, info in GBM_STANDARD_OF_CARE.items():
        # Match drug name (case-insensitive, allow partial)
        matches = ranked[ranked['DRUG_NAME'].str.lower().str.contains(drug.lower(), na=False)]
        if len(matches) == 0:
            soc_results[drug] = {'rank': None, 'present_in_gdsc': False, 'expected': info['expected_pipeline_rank']}
            findings.append(f'{drug}: NOT IN GDSC (expected {info["expected_pipeline_rank"]})')
            continue
        rank = matches.index[0] + 1  # 1-indexed
        soc_results[drug] = {
            'rank': int(rank),
            'present_in_gdsc': True,
            'expected': info['expected_pipeline_rank'],
            'composite_score': float(matches.iloc[0]['composite_score']),
        }
        findings.append(f'{drug}: rank {rank}/{len(ranked)} (expected {info["expected_pipeline_rank"]})')

    print()
    print('  GBM Standard of Care ranking results:')
    for f in findings:
        print(f'    {f}')

    # Determine pass/fail
    # Pass criteria: temozolomide in top 30 (lenient — GDSC is in vitro and won't capture MGMT)
    temo_rank = soc_results.get('Temozolomide', {}).get('rank')
    if temo_rank is None:
        verdict = 'FAIL'
        verdict_reason = 'Temozolomide not in GDSC — pipeline cannot rank it'
    elif temo_rank <= 30:
        verdict = 'PASS'
        verdict_reason = f'Temozolomide rank {temo_rank} (lenient threshold top 30)'
    elif temo_rank <= 100:
        verdict = 'CHECK'
        verdict_reason = f'Temozolomide rank {temo_rank} — surfaced but not top'
    else:
        verdict = 'FAIL'
        verdict_reason = f'Temozolomide rank {temo_rank} — pipeline does not surface GBM SOC'

    print()
    print(f'  VERDICT: {verdict}')
    print(f'  REASONING: {verdict_reason}')

    return {
        'status': verdict,
        'reason': verdict_reason,
        'soc_ranks': soc_results,
        'total_drugs_ranked': len(ranked),
    }


# ============================================================
# Test 2: Trial novelty check identifies white-space targets
# ============================================================

def test_2_white_space_targets(net):
    """
    Known GBM white-space targets (high biological priority, no effective
    approved therapy) should appear in our undruggable priority surfacing
    OR have very low chembl_compound counts.
    """
    print()
    print('=' * 70)
    print('Test 2: Trial novelty + white-space target identification')
    print('=' * 70)

    sys.path.insert(0, str(Path(__file__).parent))
    from intercepta_pipeline_v0 import surface_undruggable_priority_targets
    undruggable = surface_undruggable_priority_targets(net, top_n=30, score_threshold=0.2)
    undruggable_genes = {e['gene'] for e in undruggable}

    findings = []
    coverage = {'in_undruggable_list': 0, 'low_compounds': 0, 'in_net_at_all': 0}

    for gene in GBM_WHITE_SPACE_TARGETS:
        gene_data = net.get('genes', {}).get(gene, {})
        if not gene_data:
            findings.append(f'{gene}: NOT IN GBM net')
            continue
        coverage['in_net_at_all'] += 1
        score = gene_data.get('association_score', 0)
        n_compounds = gene_data.get('n_chembl_compounds', 0)
        n_trials = gene_data.get('n_clinical_trials', 0)
        in_undruggable = gene in undruggable_genes
        if in_undruggable:
            coverage['in_undruggable_list'] += 1
        if n_compounds <= 5:
            coverage['low_compounds'] += 1
        findings.append(
            f'{gene}: score={score:.3f} compounds={n_compounds} trials={n_trials} '
            f'undruggable_listed={in_undruggable}'
        )

    print()
    print('  GBM white-space target identification:')
    for f in findings:
        print(f'    {f}')

    n_targets = len(GBM_WHITE_SPACE_TARGETS)
    print()
    print(f'  Coverage:')
    print(f'    Present in net: {coverage["in_net_at_all"]}/{n_targets}')
    print(f'    Surfaced as undruggable: {coverage["in_undruggable_list"]}/{n_targets}')
    print(f'    Low compound count (<=5): {coverage["low_compounds"]}/{n_targets}')

    # Pass: at least 5/7 white-space targets are either undruggable-listed OR low-compound
    n_correctly_flagged = sum(1 for gene in GBM_WHITE_SPACE_TARGETS
                              if gene in undruggable_genes or
                                 net.get('genes', {}).get(gene, {}).get('n_chembl_compounds', 0) <= 5)
    if n_correctly_flagged >= 5:
        verdict = 'PASS'
        verdict_reason = f'{n_correctly_flagged}/{n_targets} white-space targets correctly flagged'
    elif n_correctly_flagged >= 3:
        verdict = 'CHECK'
        verdict_reason = f'{n_correctly_flagged}/{n_targets} flagged — partial coverage'
    else:
        verdict = 'FAIL'
        verdict_reason = f'{n_correctly_flagged}/{n_targets} flagged — most missed'

    print()
    print(f'  VERDICT: {verdict}')
    print(f'  REASONING: {verdict_reason}')

    return {
        'status': verdict,
        'reason': verdict_reason,
        'coverage': coverage,
    }


# ============================================================
# Test 3: BBB penetration of top compounds — surfaces data gap honestly
# ============================================================

def test_3_bbb_penetration(net):
    """
    GBM-specific reality: drug must cross blood-brain barrier.
    Test whether our ChEMBL compound data is rich enough to apply
    a BBB filter. If data gap exists, surface it honestly.
    """
    print()
    print('=' * 70)
    print('Test 3: BBB penetration data availability for top compounds')
    print('=' * 70)

    # Look at top 5 most-trialed targets and check what compound metadata we have
    genes_with_compounds = [(g, gd) for g, gd in net.get('genes', {}).items()
                            if gd.get('n_chembl_compounds', 0) > 0]
    top_5 = sorted(genes_with_compounds,
                   key=lambda x: -x[1].get('n_chembl_compounds', 0))[:5]

    bbb_data_check = {}
    for gene, gene_data in top_5:
        compounds = gene_data.get('chembl_compounds', [])
        if not compounds:
            continue

        # Inspect what fields we have on the first compound
        sample = compounds[0]
        bbb_relevant_fields_present = [
            f for f in ['logp', 'tpsa', 'mw', 'hba', 'hbd', 'molecular_weight', 'aromatic_rings']
            if f in sample or f.lower() in sample
        ]
        bbb_data_check[gene] = {
            'n_compounds': len(compounds),
            'top_compound_fields': list(sample.keys()),
            'bbb_relevant_fields_present': bbb_relevant_fields_present,
        }

    print()
    print('  BBB-relevant property availability in top-5 most-trialed gene compounds:')
    for gene, info in bbb_data_check.items():
        print(f'    {gene}: {info["n_compounds"]} compounds')
        print(f'      Available fields: {info["top_compound_fields"]}')
        print(f'      BBB-relevant fields present: {info["bbb_relevant_fields_present"] or "NONE"}')

    # Verdict: do we have enough property data to filter for BBB?
    n_with_bbb_data = sum(1 for v in bbb_data_check.values() if v['bbb_relevant_fields_present'])
    if n_with_bbb_data == len(bbb_data_check):
        verdict = 'PASS'
        verdict_reason = 'BBB-relevant compound properties available; filter implementable'
    elif n_with_bbb_data > 0:
        verdict = 'CHECK'
        verdict_reason = f'BBB data partial: {n_with_bbb_data}/{len(bbb_data_check)} genes'
    else:
        verdict = 'GAP'
        verdict_reason = (
            'BBB-relevant compound properties (logP, TPSA, MW, HBD/HBA) NOT in our '
            'ChEMBL dump. Our pipeline cannot currently filter for BBB penetration. '
            'This is a data-source gap, not a code bug. To address: extend ChEMBL '
            'fetcher to include molecule_properties endpoint, OR import RDKit '
            'descriptors from SMILES, OR query DrugBank for drug-likeness fields.'
        )

    print()
    print(f'  VERDICT: {verdict}')
    print(f'  REASONING: {verdict_reason}')

    return {
        'status': verdict,
        'reason': verdict_reason,
        'data_check': bbb_data_check,
    }


# ============================================================
# Test 4: Undruggable priority list vs known tumor suppressors
# ============================================================

def test_4_tumor_suppressor_recognition(net):
    """Known GBM tumor suppressors should be recognized as undruggable
    or have very few direct compounds in our pipeline output."""
    print()
    print('=' * 70)
    print('Test 4: Undruggable priority recognition for GBM tumor suppressors')
    print('=' * 70)

    sys.path.insert(0, str(Path(__file__).parent))
    from intercepta_pipeline_v0 import surface_undruggable_priority_targets
    undruggable = surface_undruggable_priority_targets(net, top_n=30, score_threshold=0.1)
    undruggable_genes = {e['gene'] for e in undruggable}

    findings = []
    n_correctly_handled = 0
    n_in_net = 0
    for gene, ts_info in GBM_TUMOR_SUPPRESSORS_BY_MUTATION.items():
        gene_data = net.get('genes', {}).get(gene, {})
        if not gene_data:
            findings.append(f'{gene} (mut {ts_info["mutation_freq_pct"]}%): NOT IN GBM NET')
            continue
        n_in_net += 1
        n_compounds = gene_data.get('n_chembl_compounds', 0)
        in_undruggable = gene in undruggable_genes

        # "Correctly handled" = either in undruggable list OR has <=5 compounds
        if in_undruggable or n_compounds <= 5:
            n_correctly_handled += 1
            verdict_per_gene = 'CORRECT'
        else:
            verdict_per_gene = 'MISSED'
        findings.append(
            f'{gene} (mut {ts_info["mutation_freq_pct"]}%): {n_compounds} compounds, '
            f'undruggable_listed={in_undruggable} [{verdict_per_gene}]'
        )

    print()
    print('  GBM tumor suppressor recognition:')
    for f in findings:
        print(f'    {f}')

    total = len(GBM_TUMOR_SUPPRESSORS_BY_MUTATION)
    print()
    print(f'  Coverage: {n_correctly_handled}/{total} correctly handled, {n_in_net}/{total} in net')

    if n_correctly_handled >= 5:
        verdict = 'PASS'
        verdict_reason = f'{n_correctly_handled}/{total} tumor suppressors correctly recognized'
    elif n_correctly_handled >= 3:
        verdict = 'CHECK'
        verdict_reason = f'{n_correctly_handled}/{total} recognized — partial'
    else:
        verdict = 'FAIL'
        verdict_reason = f'{n_correctly_handled}/{total} recognized — missing most'

    print()
    print(f'  VERDICT: {verdict}')
    print(f'  REASONING: {verdict_reason}')

    return {
        'status': verdict,
        'reason': verdict_reason,
        'n_correctly_handled': n_correctly_handled,
        'total': total,
    }


# ============================================================
# Test 5: Trial activity vs compound coverage cross-correlation
# ============================================================

def test_5_trial_compound_correlation(net):
    """For genes with many GBM trials, do we also have many ChEMBL compounds?
    Mismatches reveal where GBM clinical investigation outstrips
    measured molecular pharmacology — useful signal for novelty."""
    print()
    print('=' * 70)
    print('Test 5: GBM trial activity vs ChEMBL compound coverage')
    print('=' * 70)

    genes_with_trials = [
        (g, gd.get('n_clinical_trials', 0), gd.get('n_chembl_compounds', 0))
        for g, gd in net.get('genes', {}).items()
        if gd.get('n_clinical_trials', 0) > 0
    ]
    genes_with_trials.sort(key=lambda x: -x[1])

    print()
    print(f'  Top 10 genes by GBM trial count, with compound coverage:')
    print(f'    {"Gene":<10} {"Trials":>7} {"Compounds":>10} {"Pattern":<25}')
    for gene, n_trials, n_compounds in genes_with_trials[:10]:
        if n_trials >= 10 and n_compounds >= 20:
            pattern = 'Both rich'
        elif n_trials >= 10 and n_compounds < 5:
            pattern = 'Trials-rich, compound-poor'
        elif n_trials < 5 and n_compounds >= 20:
            pattern = 'Compounds-rich, trial-poor'
        elif n_trials >= 10:
            pattern = 'Trial-rich, compound-moderate'
        else:
            pattern = 'Both moderate'
        print(f'    {gene:<10} {n_trials:>7} {n_compounds:>10} {pattern:<25}')

    # Look for trial-rich, compound-poor genes — these are where biology has
    # outpaced our pipeline's coverage. Useful as novelty signals.
    novelty_signals = [
        (g, t, c) for g, t, c in genes_with_trials
        if t >= 10 and c < 5
    ]
    print()
    print(f'  Trial-rich, compound-poor (novelty/coverage gap signals): {len(novelty_signals)}')
    for g, t, c in novelty_signals[:5]:
        print(f'    {g}: {t} trials, {c} compounds')

    # Verdict: does trial count correlate with compound count for top genes?
    # We use a coarse check: of top-10 trial genes, how many have >=10 compounds?
    top_10_with_compounds = sum(1 for g, t, c in genes_with_trials[:10] if c >= 10)
    if top_10_with_compounds >= 7:
        verdict = 'PASS'
        verdict_reason = f'{top_10_with_compounds}/10 top-trialed genes also have rich compounds'
    elif top_10_with_compounds >= 4:
        verdict = 'CHECK'
        verdict_reason = f'{top_10_with_compounds}/10 — partial; investigate trial-rich compound-poor genes'
    else:
        verdict = 'FAIL'
        verdict_reason = f'{top_10_with_compounds}/10 — significant trial/compound mismatch'

    print()
    print(f'  VERDICT: {verdict}')
    print(f'  REASONING: {verdict_reason}')

    return {
        'status': verdict,
        'reason': verdict_reason,
        'novelty_signals': novelty_signals[:10],
    }


# ============================================================
# Run all tests and write report
# ============================================================

def main():
    print()
    print('=' * 70)
    print('INTERCEPTA Workstream A Validation: GBM as primary test disease')
    print(f'Run timestamp: {datetime.now().isoformat()}')
    print('Per Vision Part 7.1 (validation-first principle)')
    print('=' * 70)

    net = load_gbm_net()
    print(f'\nLoaded GBM net: {len(net.get("genes", {}))} genes, '
          f'{net.get("disease", "?")} ({net.get("disease_id", "?")})')

    results = {}
    results['test_1_soc_ranking'] = test_1_soc_ranking(net)
    results['test_2_white_space'] = test_2_white_space_targets(net)
    results['test_3_bbb_penetration'] = test_3_bbb_penetration(net)
    results['test_4_tumor_suppressors'] = test_4_tumor_suppressor_recognition(net)
    results['test_5_trial_compound_corr'] = test_5_trial_compound_correlation(net)

    # Summary
    print()
    print('=' * 70)
    print('VALIDATION SUMMARY')
    print('=' * 70)
    for test_name, result in results.items():
        status = result['status']
        reason = result['reason'][:100]
        print(f'  {test_name:30s} [{status:5s}] {reason}')

    # Overall verdict
    n_pass = sum(1 for r in results.values() if r['status'] == 'PASS')
    n_check = sum(1 for r in results.values() if r['status'] == 'CHECK')
    n_fail = sum(1 for r in results.values() if r['status'] == 'FAIL')
    n_gap = sum(1 for r in results.values() if r['status'] == 'GAP')
    print()
    print(f'  Total: {n_pass} PASS, {n_check} CHECK, {n_fail} FAIL, {n_gap} GAP')

    if n_fail >= 2:
        print(f'  OVERALL: WORKSTREAM A NOT VALIDATED for GBM. Fixes required before B/C.')
    elif n_fail >= 1 or n_gap >= 1:
        print(f'  OVERALL: WORKSTREAM A PARTIALLY VALIDATED. Specific gaps identified.')
    elif n_check >= 2:
        print(f'  OVERALL: WORKSTREAM A VALIDATED with caveats. Investigate CHECKs.')
    else:
        print(f'  OVERALL: WORKSTREAM A VALIDATED for GBM.')

    # Save results JSON
    out_json = Path.home() / 'INTERCEPTA/round3_gbm_live_test/results/validation_workstream_a_gbm.json'
    with open(out_json, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'disease': 'glioblastoma multiforme',
            'disease_id': 'EFO_0000519',
            'tests': results,
            'summary': {'PASS': n_pass, 'CHECK': n_check, 'FAIL': n_fail, 'GAP': n_gap},
        }, f, indent=2, default=str)
    print(f'\nValidation results saved: {out_json}')


if __name__ == '__main__':
    main()
