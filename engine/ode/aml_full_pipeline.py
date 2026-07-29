#!/usr/bin/env python3
"""
INTERCEPTA: AML Full Pipeline — Prove Universality
====================================================
Same pipeline that found enza+alisertib for mCRPC,
now applied to AML using BeatAML patient data.

Stage 1: Disease Net (DONE — 498 genes)
Stage 2: Escape Routes + Vulnerability
Stage 3: Drug Screening (BeatAML 166 drugs)
Stage 4: Combination Predictions
Stage 5: Novel Molecule Generation

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import pandas as pd
import numpy as np
import json
import os

# ═══════════════════════════════════════════
# STAGE 1: Load AML Disease Net
# ═══════════════════════════════════════════
def stage1_load_net():
    print('STAGE 1: AML DISEASE NET')
    print('='*55)
    
    with open('../results/disease_net_acute_myeloid_leukemia.json') as f:
        aml = json.load(f)
    
    print(f'  Genes: {aml["n_genes"]}')
    print(f'  Drug targets: {len(aml["drug_targets"])}')
    print(f'  Immune genes: {len(aml["immune_relevant"])}')
    
    # Top genes
    top = sorted(aml['genes'].items(), key=lambda x: -x[1]['association_score'])[:10]
    print(f'\n  Top 10 AML genes:')
    for gene, data in top:
        print(f'    {gene:<12} score={data["association_score"]:.3f}')
    
    return aml

# ═══════════════════════════════════════════
# STAGE 2: Build AML Escape Routes
# ═══════════════════════════════════════════
def stage2_escape_routes(aml):
    print(f'\nSTAGE 2: AML ESCAPE ROUTES')
    print('='*55)
    
    # Load unified net for pathway and interaction data
    with open('../results/mcrpc_unified_net.json') as f:
        net = json.load(f)
    
    # AML driver genes (top targets for therapy)
    aml_drivers = ['FLT3', 'IDH1', 'IDH2', 'DNMT3A', 'NPM1', 'KIT', 
                   'TP53', 'NRAS', 'KRAS', 'RUNX1', 'CEBPA']
    
    # For each driver, find escape routes via shared pathways
    escape_routes = {}
    
    for driver in aml_drivers:
        driver_data = net['genes'].get(driver, {})
        driver_pathways = driver_data.get('pathways', [])
        driver_interactions = driver_data.get('interactions', [])
        
        if not driver_pathways and not driver_interactions:
            continue
        
        # Find genes that share pathways with driver
        # (these could compensate when driver is blocked)
        escape_genes = set()
        
        # From pathway sharing
        driver_pw_ids = set()
        for p in driver_pathways:
            if isinstance(p, dict):
                driver_pw_ids.add(p.get('id', ''))
            elif isinstance(p, str):
                driver_pw_ids.add(p)
        
        if driver_pw_ids:
            for gene, gdata in net['genes'].items():
                if gene == driver: continue
                gene_pws = gdata.get('pathways', [])
                gene_pw_ids = set()
                for p in gene_pws:
                    if isinstance(p, dict):
                        gene_pw_ids.add(p.get('id', ''))
                    elif isinstance(p, str):
                        gene_pw_ids.add(p)
                shared = driver_pw_ids & gene_pw_ids
                if len(shared) >= 2:
                    escape_genes.add(gene)
        
        # From direct interactions
        if isinstance(driver_interactions, list):
            for interact in driver_interactions:
                if isinstance(interact, dict):
                    partner = interact.get('partner', interact.get('gene', ''))
                elif isinstance(interact, str):
                    partner = interact
                else:
                    continue
                if partner and partner != driver:
                    escape_genes.add(partner)
        
        # Filter to genes in AML net
        aml_gene_set = set(aml['genes'].keys())
        escape_in_aml = escape_genes & aml_gene_set
        
        if escape_in_aml:
            escape_routes[driver] = {
                'n_escape_genes': len(escape_in_aml),
                'escape_genes': sorted(list(escape_in_aml))[:30],
                'n_shared_pathways': len(driver_pw_ids),
            }
    
    print(f'  Escape routes found for {len(escape_routes)} AML drivers:')
    for driver, data in escape_routes.items():
        print(f'    {driver:<10} → {data["n_escape_genes"]} escape genes')
        if data['escape_genes'][:5]:
            print(f'      Top: {data["escape_genes"][:5]}')
    
    return escape_routes

# ═══════════════════════════════════════════
# STAGE 3: Drug Sensitivity from BeatAML
# ═══════════════════════════════════════════
def stage3_drug_sensitivity():
    print(f'\nSTAGE 3: BeatAML DRUG SENSITIVITY')
    print('='*55)
    
    ds = pd.read_csv('../data/beataml/beataml_probit_curve_fits_v4_dbgap.txt', sep='\t')
    mut = pd.read_csv('../data/beataml/beataml_wes_wv1to4_mutations_dbgap.txt', sep='\t')
    clin = pd.read_excel('../data/beataml/beataml_wv1to4_clinical.xlsx')
    
    print(f'  Patients: {ds["dbgap_subject_id"].nunique()}')
    print(f'  Drugs: {ds["inhibitor"].nunique()}')
    
    # Map mutations to subjects
    mut_subjects = {}
    for _, r in clin.iterrows():
        if pd.notna(r.get('dbgap_dnaseq_sample')):
            mut_subjects[r['dbgap_dnaseq_sample']] = r['dbgap_subject_id']
    
    # For each AML driver gene, find mutation-drug sensitivity associations
    drivers = ['FLT3', 'IDH1', 'IDH2', 'DNMT3A', 'NPM1', 'TP53', 'NRAS']
    
    results = {}
    for driver in drivers:
        # Get patients with this mutation
        mut_patients = set()
        for sample in mut[mut['symbol']==driver]['dbgap_sample_id'].unique():
            if sample in mut_subjects:
                mut_patients.add(mut_subjects[sample])
        
        wt_patients = set(ds['dbgap_subject_id'].unique()) - mut_patients
        
        if len(mut_patients) < 5:
            continue
        
        # Find drugs where mutant is MORE sensitive
        drug_effects = []
        for drug in ds['inhibitor'].unique():
            dd = ds[ds['inhibitor']==drug]
            mut_auc = dd[dd['dbgap_subject_id'].isin(mut_patients)]['auc']
            wt_auc = dd[dd['dbgap_subject_id'].isin(wt_patients)]['auc']
            
            if len(mut_auc) >= 5 and len(wt_auc) >= 10:
                diff = wt_auc.median() - mut_auc.median()
                drug_effects.append({
                    'drug': drug,
                    'mut_auc': round(mut_auc.median(), 1),
                    'wt_auc': round(wt_auc.median(), 1),
                    'diff': round(diff, 1),
                    'n_mut': len(mut_auc),
                    'n_wt': len(wt_auc),
                    'direction': 'MORE_SENSITIVE' if diff > 10 else 'MORE_RESISTANT' if diff < -10 else 'SIMILAR',
                })
        
        drug_effects.sort(key=lambda x: -x['diff'])
        results[driver] = {
            'n_mut_patients': len(mut_patients),
            'top_sensitive': [d for d in drug_effects if d['direction']=='MORE_SENSITIVE'][:5],
            'top_resistant': [d for d in drug_effects if d['direction']=='MORE_RESISTANT'][:3],
        }
        
        print(f'\n  {driver} ({len(mut_patients)} mut patients):')
        for d in results[driver]['top_sensitive'][:3]:
            print(f'    SENSITIVE: {d["drug"][:25]:<25} mut={d["mut_auc"]:.0f} wt={d["wt_auc"]:.0f} diff={d["diff"]:+.0f}')
        for d in results[driver]['top_resistant'][:2]:
            print(f'    RESISTANT: {d["drug"][:25]:<25} mut={d["mut_auc"]:.0f} wt={d["wt_auc"]:.0f} diff={d["diff"]:+.0f}')
    
    return results

# ═══════════════════════════════════════════
# STAGE 4: Escape Route Combination Design
# ═══════════════════════════════════════════
def stage4_combinations(escape_routes, drug_sensitivity):
    print(f'\nSTAGE 4: AML ESCAPE ROUTE COMBINATIONS')
    print('='*55)
    
    # Load GDSC drug targets
    gdsc = pd.read_excel('../data/gdsc/GDSC2_fitted_dose_response.xlsx')
    drug_targets = gdsc[['DRUG_NAME','PUTATIVE_TARGET']].drop_duplicates()
    target_to_drugs = {}
    for _, r in drug_targets.iterrows():
        for t in str(r['PUTATIVE_TARGET']).split(','):
            t = t.strip()
            if t not in target_to_drugs: target_to_drugs[t] = []
            target_to_drugs[t].append(r['DRUG_NAME'])
    
    # Also map BeatAML drug families
    try:
        families = pd.read_excel('../data/beataml/beataml_drug_families.xlsx')
        print(f'  BeatAML drug families loaded: {len(families)} drugs')
    except:
        families = None
    
    # For each driver with escape route, find rational combinations
    combinations = []
    
    for driver, esc_data in escape_routes.items():
        # Drug A: targets the driver
        driver_drugs = target_to_drugs.get(driver, [])
        
        # Also check BeatAML sensitivity
        driver_sens = drug_sensitivity.get(driver, {})
        sensitive_drugs = [d['drug'] for d in driver_sens.get('top_sensitive', [])]
        
        # Drug B: targets escape gene
        for escape_gene in esc_data['escape_genes'][:10]:
            escape_drugs = target_to_drugs.get(escape_gene, [])
            
            for drug_a in (driver_drugs[:3] + sensitive_drugs[:3]):
                for drug_b in escape_drugs[:3]:
                    if drug_a != drug_b:
                        combinations.append({
                            'driver': driver,
                            'escape_gene': escape_gene,
                            'drug_a': drug_a,
                            'drug_a_role': f'targets {driver}',
                            'drug_b': drug_b,
                            'drug_b_role': f'blocks {escape_gene} escape',
                            'rationale': f'When {driver} is blocked by {drug_a}, '
                                       f'{escape_gene} compensates. {drug_b} blocks this escape.',
                        })
    
    # Remove duplicates
    seen = set()
    unique_combos = []
    for c in combinations:
        key = tuple(sorted([c['drug_a'], c['drug_b']]))
        if key not in seen:
            seen.add(key)
            unique_combos.append(c)
    
    print(f'  Unique rational combinations: {len(unique_combos)}')
    print(f'\n  TOP COMBINATIONS:')
    for c in unique_combos[:10]:
        print(f'    {c["drug_a"][:20]:<20} + {c["drug_b"][:20]:<20}')
        print(f'      {c["rationale"][:70]}')
    
    return unique_combos

# ═══════════════════════════════════════════
# STAGE 5: Novelty Check
# ═══════════════════════════════════════════
def stage5_novelty(combinations):
    print(f'\nSTAGE 5: NOVELTY CHECK (ClinicalTrials.gov)')
    print('='*55)
    
    import urllib.request
    
    novel = []
    for c in combinations[:15]:
        d1 = c['drug_a'].split('(')[0].split(' ')[0].strip()
        d2 = c['drug_b'].split('(')[0].split(' ')[0].strip()
        query = f'{d1} {d2} AML leukemia'.replace(' ', '+')
        url = f'https://clinicaltrials.gov/api/v2/studies?query.term={query}&pageSize=3'
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                n_trials = data.get('totalCount', 0)
        except:
            n_trials = -1
        
        is_novel = n_trials == 0
        status = 'NOVEL ★' if is_novel else f'{n_trials} trials'
        print(f'  {d1[:15]:<15} + {d2[:15]:<15} → {status}')
        
        c['n_trials'] = n_trials
        c['is_novel'] = is_novel
        if is_novel:
            novel.append(c)
    
    print(f'\n  Novel combinations (not in trials for AML): {len(novel)}')
    return novel

# ═══════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════
def main():
    print('INTERCEPTA: AML FULL PIPELINE')
    print('Proving universality — same method, different disease')
    print('='*60)
    print()
    
    # Stage 1
    aml = stage1_load_net()
    
    # Stage 2
    escape_routes = stage2_escape_routes(aml)
    
    # Stage 3
    drug_sensitivity = stage3_drug_sensitivity()
    
    # Stage 4
    combinations = stage4_combinations(escape_routes, drug_sensitivity)
    
    # Stage 5
    novel = stage5_novelty(combinations)
    
    # Save everything
    output = {
        'disease': 'Acute Myeloid Leukemia',
        'pipeline_date': '2026-04-08',
        'n_genes': aml['n_genes'],
        'n_escape_routes': len(escape_routes),
        'escape_routes': escape_routes,
        'drug_sensitivity_drivers': {k: v['n_mut_patients'] for k, v in drug_sensitivity.items()},
        'n_combinations': len(combinations),
        'combinations': combinations[:20],
        'novel_combinations': novel,
    }
    
    with open('../results/aml_full_pipeline.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f'\n{"="*60}')
    print(f'AML PIPELINE COMPLETE')
    print(f'  Escape routes: {len(escape_routes)} drivers')
    print(f'  Combinations: {len(combinations)} rational pairs')
    print(f'  Novel (not in trials): {len(novel)}')
    print(f'  Saved: results/aml_full_pipeline.json')
    
    return output

if __name__ == '__main__':
    main()
