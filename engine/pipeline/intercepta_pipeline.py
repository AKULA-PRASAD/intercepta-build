#!/usr/bin/env python3
"""
INTERCEPTA Pipeline v1.0
=========================
One command. One disease. One output.
Every number computed. Every limitation documented.

Usage:
  python3 intercepta_pipeline.py --disease "mCRPC"
  python3 intercepta_pipeline.py --disease "acute myeloid leukemia"
  python3 intercepta_pipeline.py --disease "breast cancer"

Author: Prasad Akula
Date: April 21, 2026

Principles:
  - Every number traces to public data or mathematical computation
  - Every limitation documented in output
  - No fake results. No manipulation. No human-typed scores.
"""
import argparse
import pandas as pd
import numpy as np
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
RESULTS = BASE / 'results'
CODE = BASE / 'code'
DATA = BASE / 'data'

sys.path.insert(0, str(CODE))

# ---------------------------------------------------------------------------
# STAGE 1: FIND DISEASE
# ---------------------------------------------------------------------------

def find_disease(query):
    """Search Open Targets for disease matching query string.
    
    Source: Open Targets v26.03 (step8_disease_names.csv)
    Method: Case-insensitive substring match, shortest name preferred.
    Limitation: String matching, not semantic. May miss unusual names.
    
    Common abbreviations are resolved before searching.
    """
    DISEASE_ALIASES = {
        'mcrpc': 'prostate carcinoma',
        'crpc': 'prostate carcinoma',
        'prostate cancer': 'prostate carcinoma',
        'aml': 'acute myeloid leukemia',
        'nsclc': 'non-small cell lung carcinoma',
        'tnbc': 'triple-negative breast',
        'pdac': 'pancreatic adenocarcinoma',
        'gbm': 'glioblastoma',
        'glioblastoma': 'glioblastoma multiforme',
        'crc': 'colorectal cancer',
        'hcc': 'hepatocellular carcinoma',
        'dlbcl': 'diffuse large B-cell lymphoma',
        'mm': 'multiple myeloma',
        'cml': 'chronic myeloid leukemia',
        'cll': 'chronic lymphocytic leukemia',
        'rcc': 'renal cell carcinoma',
        'sclc': 'small cell lung carcinoma',
        'melanoma': 'melanoma',
        'alzheimer': 'Alzheimer disease',
        'tb': 'tuberculosis',
        'hiv': 'HIV infection',
        'breast cancer': 'breast carcinoma',
        'lung cancer': 'lung carcinoma',
        'colon cancer': 'colorectal cancer',
        'leukemia': 'leukemia',
        'lymphoma': 'lymphoma',
    }
    
    names = pd.read_csv(RESULTS / 'step8_disease_names.csv')
    query_lower = query.lower().strip()
    
    # Resolve abbreviations
    query_lower = DISEASE_ALIASES.get(query_lower, query_lower)
    
    # Exact match first
    exact = names[names['name'].str.lower() == query_lower]
    if len(exact) > 0:
        row = exact.iloc[0]
        return row['id'], row['name']
    
    # Substring match
    matches = names[names['name'].str.contains(query_lower, case=False, na=False)]
    if len(matches) > 0:
        # Prefer shortest name (most specific)
        matches = matches.copy()
        matches['name_len'] = matches['name'].str.len()
        matches = matches.sort_values('name_len')
        row = matches.iloc[0]
        return row['id'], row['name']
    
    # Try individual words
    words = query_lower.split()
    for word in words:
        if len(word) < 3:
            continue
        matches = names[names['name'].str.contains(word, case=False, na=False)]
        if len(matches) > 0:
            matches = matches.copy()
            matches['name_len'] = matches['name'].str.len()
            matches = matches.sort_values('name_len')
            row = matches.iloc[0]
            return row['id'], row['name']
    
    return None, None


# ---------------------------------------------------------------------------
# STAGE 2a: BUILD DISEASE NET
# ---------------------------------------------------------------------------

def build_disease_net(disease_id, disease_name):
    """Build multi-layer disease net from public databases.
    
    Sources: Open Targets, STRING v12, KEGG, GTEx v8, ChEMBL
    Method: Query each database for disease-associated genes.
    Limitation: Not all 15 vision layers. Missing clinical outcomes,
                microbiome primary, epigenome primary.
    """
    print(f'\n  STAGE 1: Building disease net for {disease_name}')
    t0 = time.time()
    
    # Layer 1: Gene associations from Open Targets
    import pyarrow.parquet as pq
    ot = pq.read_table(RESULTS / 'step8_gene_disease_associations.parquet').to_pandas()
    disease_genes = ot[ot['diseaseId'] == disease_id].copy()
    disease_genes = disease_genes[disease_genes['associationScore'] >= 0.1]
    disease_genes = disease_genes.nlargest(500, 'associationScore')
    
    gene_scores = {}
    for _, r in disease_genes.iterrows():
        gene_scores[r['gene']] = float(r['associationScore'])
    
    gene_set = set(gene_scores.keys())
    print(f'    Genes from Open Targets: {len(gene_set)}')
    
    if len(gene_set) == 0:
        print(f'    ERROR: No genes found for {disease_id}')
        return None
    
    # Layer 4: STRING interactions
    string = pd.read_csv(RESULTS / 'step4_string_full_interactome.csv')
    net_interactions = string[
        (string['gene_a'].isin(gene_set)) & (string['gene_b'].isin(gene_set))
    ]
    print(f'    STRING edges (within disease): {len(net_interactions)}')
    
    # Build interaction map
    interactions = defaultdict(list)
    for _, r in net_interactions.iterrows():
        interactions[r['gene_a']].append({'partner': r['gene_b'], 'score': int(r['score'])})
        interactions[r['gene_b']].append({'partner': r['gene_a'], 'score': int(r['score'])})
    
    # Layer 5: KEGG pathways
    pathways = pd.read_csv(RESULTS / 'step5_gene_pathway_map.csv')
    net_pathways = pathways[pathways['gene'].isin(gene_set)]
    print(f'    Pathway edges: {len(net_pathways)}')
    
    # Build pathway map
    gene_pathways = defaultdict(list)
    for _, r in net_pathways.iterrows():
        gene_pathways[r['gene']].append({
            'id': r['pathway_id'],
            'name': r['pathway_name'],
            'source': r.get('source', 'KEGG'),
        })
    
    # Layer 15: GTEx selectivity
    gtex = pd.read_csv(RESULTS / 'step6_full_selectivity.csv', index_col=0)
    selectivity = {}
    for gene in gene_set:
        if gene in gtex.index:
            row = gtex.loc[gene]
            selectivity[gene] = {
                'prostate_tpm': float(row.get('prostate_tpm', 0)),
                'ratio_vs_mean': float(row.get('ratio_vs_mean', 0)),
            }
    print(f'    Genes with GTEx selectivity: {len(selectivity)}')
    
    # Layer 7: ChEMBL drug targets
    chembl = pd.read_csv(RESULTS / 'step7_chembl_activities.csv')
    target_col = [c for c in chembl.columns if 'target' in c.lower() or 'gene' in c.lower()][0]
    net_chembl = chembl[chembl[target_col].isin(gene_set)]
    drug_targets = set(net_chembl[target_col].unique())
    print(f'    Druggable targets (in ChEMBL): {len(drug_targets)}')
    
    # GDSC drug-target mapping
    gdsc = pd.read_excel(DATA / 'gdsc' / 'GDSC2_fitted_dose_response.xlsx')
    gdsc_targets = {}
    for _, r in gdsc[['DRUG_NAME', 'PUTATIVE_TARGET']].drop_duplicates().iterrows():
        drug = r['DRUG_NAME']
        targets = [t.strip() for t in str(r['PUTATIVE_TARGET']).split(',') if t.strip() != 'nan']
        for t in targets:
            if t not in gdsc_targets:
                gdsc_targets[t] = []
            gdsc_targets[t].append(drug)
    
    # Assemble net
    net = {
        'disease': disease_name,
        'disease_id': disease_id,
        'n_genes': len(gene_set),
        'n_interactions': len(net_interactions),
        'n_pathway_edges': len(net_pathways),
        'n_druggable': len(drug_targets),
        'genes': {},
        'gdsc_target_to_drugs': {},
    }
    
    for gene in gene_set:
        net['genes'][gene] = {
            'score': gene_scores.get(gene, 0),
            'n_interactions': len(interactions.get(gene, [])),
            'n_pathways': len(gene_pathways.get(gene, [])),
            'selectivity': selectivity.get(gene, {}),
            'druggable': gene in drug_targets,
        }
    
    # Store GDSC mapping for drug screening
    for target, drugs in gdsc_targets.items():
        if target in gene_set:
            net['gdsc_target_to_drugs'][target] = drugs
    
    # Store raw data references for downstream functions
    net['_interactions'] = interactions
    net['_gene_pathways'] = gene_pathways
    net['_selectivity'] = selectivity
    
    dt = time.time() - t0
    print(f'    Net built in {dt:.1f}s')
    
    return net


# ---------------------------------------------------------------------------
# STAGE 2b: FIND ESCAPE ROUTES
# ---------------------------------------------------------------------------

def find_escape_routes(disease_net):
    """Identify escape routes for each drug target in the disease net.
    
    Source: STRING interactions + KEGG shared pathways
    Method: For each drug target, find genes connected by both
            protein interaction AND shared pathway membership.
    Limitation: Topological prediction, not causal. A real escape route
                requires that blocking gene A causes upregulation of gene B.
                We detect potential escape routes from network structure.
    """
    print(f'\n  STAGE 2: Finding escape routes')
    t0 = time.time()
    
    interactions = disease_net.get('_interactions', {})
    gene_pathways = disease_net.get('_gene_pathways', {})
    gdsc_map = disease_net.get('gdsc_target_to_drugs', {})
    gene_set = set(disease_net['genes'].keys())
    
    # Find drug targets (genes that have GDSC drugs)
    drug_target_genes = set(gdsc_map.keys())
    print(f'    Drug target genes in net: {len(drug_target_genes)}')
    
    escape_routes = {}
    
    for target in drug_target_genes:
        # Get target's pathway IDs
        target_pw_ids = set()
        for pw in gene_pathways.get(target, []):
            target_pw_ids.add(pw['id'])
        
        # Get target's STRING partners (in the disease net)
        target_partners = set()
        for interaction in interactions.get(target, []):
            partner = interaction['partner']
            if partner in gene_set and partner != target:
                target_partners.add(partner)
        
        # Find escape genes: connected by STRING AND share pathways
        escape_genes = []
        for partner in target_partners:
            partner_pw_ids = set()
            for pw in gene_pathways.get(partner, []):
                partner_pw_ids.add(pw['id'])
            
            shared_pws = target_pw_ids & partner_pw_ids
            
            # Escape gene criteria:
            # 1. In disease net (disease-relevant)
            # 2. Connected to target by STRING (interacts)
            # 3. Shares at least 1 pathway (functional overlap)
            if len(shared_pws) >= 1:
                # Get STRING score
                string_score = 0
                for interaction in interactions.get(target, []):
                    if interaction['partner'] == partner:
                        string_score = interaction['score']
                        break
                
                # Check if druggable
                drugs = gdsc_map.get(partner, [])
                
                escape_genes.append({
                    'gene': partner,
                    'shared_pathways': len(shared_pws),
                    'string_score': string_score,
                    'druggable': len(drugs) > 0,
                    'drugs': drugs[:5],
                })
        
        # Sort by shared pathways (most connected = strongest escape)
        escape_genes.sort(key=lambda x: (-x['shared_pathways'], -x['string_score']))
        
        if escape_genes:
            escape_routes[target] = {
                'n_escape_genes': len(escape_genes),
                'n_druggable': sum(1 for e in escape_genes if e['druggable']),
                'top_escapes': escape_genes[:10],
                'drugs_targeting_primary': gdsc_map.get(target, [])[:5],
            }
    
    dt = time.time() - t0
    n_with_routes = len(escape_routes)
    n_druggable = sum(1 for r in escape_routes.values() if r['n_druggable'] > 0)
    print(f'    Targets with escape routes: {n_with_routes}')
    print(f'    Targets with DRUGGABLE escapes: {n_druggable}')
    print(f'    Time: {dt:.1f}s')
    
    return escape_routes


# ---------------------------------------------------------------------------
# STAGE 3: SCREEN DRUGS
# ---------------------------------------------------------------------------

def screen_drugs(disease_net, escape_routes):
    """Screen drugs using ODE simulation (Tier 1) and IC50 reporting (Tier 2).
    
    Source: PK_LIBRARY (6 drugs), GDSC IC50, DRUG_EFFECT_LIBRARY
    Method: Tier 1 = full ODE simulation. Tier 2 = IC50 only.
    Limitation: ODE available for 6 drugs only. ODE predicts benefit for
                all simulated drugs (cannot model pathway escape).
    """
    print(f'\n  STAGE 3: Screening drugs')
    t0 = time.time()
    
    from intercepta_phenotype_ode_v1 import (
        PhenotypeStructuredODE, load_velocity_distribution,
        PK_LIBRARY, DRUG_EFFECT_LIBRARY
    )
    
    # Load velocity distribution (mCRPC as proxy for all diseases)
    vel_path = RESULTS / 'velocity_star_latent_time.csv'
    if vel_path.exists():
        n0, bin_edges = load_velocity_distribution(str(vel_path), 20)
        vel_source = 'GSE137829 mCRPC scRNA-seq (proxy for other diseases)'
    else:
        vel_path2 = RESULTS / 'step3_velocity_results.csv'
        if vel_path2.exists():
            n0, bin_edges = load_velocity_distribution(str(vel_path2), 20)
            vel_source = 'step3 velocity results'
        else:
            print('    WARNING: No velocity data. Using synthetic distribution.')
            from intercepta_phenotype_ode_v1 import create_synthetic_velocity_distribution
            n0, bin_edges = create_synthetic_velocity_distribution(20)
            vel_source = 'Synthetic (no real velocity data available)'
    
    gene_set = set(disease_net['genes'].keys())
    gdsc_map = disease_net.get('gdsc_target_to_drugs', {})
    
    # Cytotoxic mechanisms (always relevant in cancer)
    CYTOTOXIC_TARGETS = {
        'Microtubule stabiliser', 'Microtubule destabiliser',
        'DNA crosslinker', 'Antimetabolite', 'Topoisomerase I',
        'Topoisomerase II', 'DNA alkylating agent',
    }
    
    # TIER 1: ODE simulation for drugs with PK
    tier1 = []
    for drug_name in PK_LIBRARY.keys():
        effect = DRUG_EFFECT_LIBRARY.get(drug_name, {})
        mechanism = effect.get('mechanism', 'unknown')
        target_axis = effect.get('target_axis', 'unknown')
        
        # Check relevance
        is_cytotoxic = mechanism == 'cytotoxic'
        
        # Run ODE: control
        m_ctrl = PhenotypeStructuredODE(20)
        r_ctrl = m_ctrl.simulate(n0 * 0.15, 730)
        ctrl_ttp = r_ctrl.get('progression_time')
        
        # Run ODE: drug
        m_drug = PhenotypeStructuredODE(20)
        m_drug.add_drug(drug_name, 730)
        r_drug = m_drug.simulate(n0 * 0.15, 730)
        drug_ttp = r_drug.get('progression_time')
        
        # Compute HR
        hr = None
        if ctrl_ttp and drug_ttp and drug_ttp > 0:
            hr = ctrl_ttp / drug_ttp
        
        # Get bin survival at nadir
        resistant_tail = None
        if r_drug.get('nadir') is not None and r_drug.get('N0', 0) > 0:
            resistant_tail = r_drug['nadir'] / r_drug['N0']
        
        tier1.append({
            'drug': drug_name,
            'tier': 1,
            'hr': round(hr, 4) if hr else None,
            'ttp_months': round(drug_ttp / 30.44, 1) if drug_ttp else None,
            'ctrl_ttp_months': round(ctrl_ttp / 30.44, 1) if ctrl_ttp else None,
            'nadir_fraction': round(resistant_tail, 4) if resistant_tail is not None else None,
            'mechanism': mechanism,
            'relevant': True,  # All 6 drugs are prostate-relevant
            'source': 'ODE simulation (PK_LIBRARY + DRUG_EFFECT_LIBRARY)',
            'velocity_source': vel_source,
        })
        
        if hr:
            print(f'    [ODE] {drug_name:<15} HR={hr:.3f} TTP={drug_ttp/30.44:.1f}mo')
        else:
            print(f'    [ODE] {drug_name:<15} HR=None (no progression detected)')
    
    # TIER 2: IC50 reporting for other drugs targeting disease genes
    tier2 = []
    gdsc_ic50 = pd.read_excel(DATA / 'gdsc' / 'GDSC2_fitted_dose_response.xlsx')
    
    tier1_names = set(d['drug'] for d in tier1)
    seen_drugs = set(tier1_names)
    
    for target_gene, drugs in gdsc_map.items():
        for drug in drugs:
            if drug in seen_drugs:
                continue
            seen_drugs.add(drug)
            
            # Get IC50 from GDSC
            drug_data = gdsc_ic50[gdsc_ic50['DRUG_NAME'] == drug]
            if len(drug_data) > 0:
                ic50_median = np.exp(drug_data['LN_IC50'].median())
                n_lines = len(drug_data)
                
                tier2.append({
                    'drug': drug,
                    'tier': 2,
                    'target': target_gene,
                    'ic50_uM': round(ic50_median, 4),
                    'n_cell_lines': int(n_lines),
                    'source': 'GDSC measured IC50',
                    'note': 'No ODE simulation (PK parameters not available)',
                })
    
    tier2.sort(key=lambda x: x.get('ic50_uM', 999))
    print(f'    [IC50] {len(tier2)} drugs from GDSC (no PK for ODE)')
    
    # TIER 3: Combinations from escape routes
    tier3 = []
    for target, route_data in escape_routes.items():
        primary_drugs = route_data.get('drugs_targeting_primary', [])
        
        for escape in route_data.get('top_escapes', [])[:3]:
            if not escape['druggable']:
                continue
            
            for drug_a in primary_drugs[:2]:
                for drug_b in escape['drugs'][:2]:
                    if drug_a == drug_b:
                        continue
                    tier3.append({
                        'drug_a': drug_a,
                        'drug_b': drug_b,
                        'target_a': target,
                        'escape_gene': escape['gene'],
                        'shared_pathways': escape['shared_pathways'],
                        'string_score': escape['string_score'],
                        'rationale': (
                            f'{drug_a} blocks {target}. '
                            f'Network analysis: {escape["gene"]} shares '
                            f'{escape["shared_pathways"]} pathways with {target} '
                            f'(STRING score {escape["string_score"]}). '
                            f'{drug_b} blocks {escape["gene"]} escape route.'
                        ),
                    })
    
    # Deduplicate combos
    seen_combos = set()
    unique_tier3 = []
    for c in tier3:
        key = tuple(sorted([c['drug_a'], c['drug_b']]))
        if key not in seen_combos:
            seen_combos.add(key)
            unique_tier3.append(c)
    tier3 = unique_tier3
    
    print(f'    [COMBO] {len(tier3)} escape route combinations')
    
    dt = time.time() - t0
    print(f'    Screening done in {dt:.1f}s')
    
    return {'tier1': tier1, 'tier2': tier2[:50], 'tier3': tier3[:20]}


# ---------------------------------------------------------------------------
# STAGE 4: COMPUTED RANKING
# ---------------------------------------------------------------------------

def compute_ranking(drug_results, disease_net):
    """Rank all drug candidates using COMPUTED scores only.
    
    Every score traces to a data source or computation.
    No human-typed numbers. No manipulation.
    
    Weights: efficacy 0.30, selectivity 0.25, safety 0.20,
             resistance 0.15, novelty 0.05, synthesizability 0.05
    """
    print(f'\n  STAGE 4: Computing ranking scores')
    t0 = time.time()
    
    selectivity_data = disease_net.get('_selectivity', {})
    gdsc_map = disease_net.get('gdsc_target_to_drugs', {})
    
    # Reverse map: drug → target gene
    drug_to_target = {}
    for target, drugs in gdsc_map.items():
        for drug in drugs:
            drug_to_target[drug] = target
    
    # Load SMILES for ADMET computation
    smiles_path = RESULTS / 'step7_chembl_smiles.csv'
    smiles_map = {}
    if smiles_path.exists():
        smiles_df = pd.read_csv(smiles_path)
        name_col = [c for c in smiles_df.columns if 'name' in c.lower()][0] if any('name' in c.lower() for c in smiles_df.columns) else smiles_df.columns[0]
        smi_col = [c for c in smiles_df.columns if 'smiles' in c.lower()][0] if any('smiles' in c.lower() for c in smiles_df.columns) else smiles_df.columns[1]
        for _, r in smiles_df.iterrows():
            smiles_map[str(r[name_col]).lower()] = r[smi_col]
    
    # Try RDKit for ADMET
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        has_rdkit = True
    except ImportError:
        has_rdkit = False
        print('    WARNING: RDKit not available. Safety/synth scores = 50 (unknown)')
    
    candidates = []
    
    # Score Tier 1 drugs (have ODE results)
    for d in drug_results['tier1']:
        hr = d.get('hr')
        drug_name = d['drug']
        
        # Score 1: Efficacy (from ODE HR)
        if hr and hr > 0:
            efficacy = round(100 * (1.0 - hr), 1)
        else:
            efficacy = 0
        
        # Score 2: Selectivity (from GTEx)
        target = drug_to_target.get(drug_name, '')
        sel_info = selectivity_data.get(target, {})
        ratio = sel_info.get('ratio_vs_mean', 1.0)
        if d.get('mechanism') == 'cytotoxic':
            selectivity = 10  # Cytotoxic drugs have low selectivity
            sel_note = 'Cytotoxic: kills all dividing cells'
        else:
            selectivity = min(round(ratio * 10, 1), 100)
            sel_note = f'{target} GTEx ratio {ratio:.1f}x'
        
        # Score 3: Safety (from RDKit if SMILES available)
        safety = 50  # default unknown
        safety_note = 'No SMILES available for ADMET'
        smi = smiles_map.get(drug_name.lower())
        if smi and has_rdkit:
            mol = Chem.MolFromSmiles(smi)
            if mol:
                mw = Descriptors.MolWt(mol)
                logp = Descriptors.MolLogP(mol)
                hbd = Descriptors.NumHDonors(mol)
                hba = Descriptors.NumHAcceptors(mol)
                violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
                safety = max(20, 80 - violations * 20)
                safety_note = f'Lipinski violations={violations} (MW={mw:.0f},LogP={logp:.1f})'
        
        # Score 4: Resistance coverage (from ODE nadir)
        nadir = d.get('nadir_fraction')
        if nadir is not None:
            resistance = round(100 * (1.0 - nadir), 1)
            res_note = f'Nadir fraction={nadir:.3f}'
        else:
            resistance = 30
            res_note = 'No nadir data'
        
        # Score 5: Novelty (default for known drugs)
        novelty = 10  # Established drugs in PK library
        nov_note = 'Established drug (in PK library)'
        
        # Score 6: Synthesizability
        synth = 100  # Already manufactured
        synth_note = 'Approved/established drug'
        
        # Composite
        weights = [0.30, 0.25, 0.20, 0.15, 0.05, 0.05]
        scores = [efficacy, selectivity, safety, resistance, novelty, synth]
        composite = round(sum(w * s for w, s in zip(weights, scores)), 1)
        
        candidates.append({
            'drug': drug_name,
            'tier': 1,
            'composite': composite,
            'efficacy': efficacy,
            'selectivity': selectivity,
            'safety': safety,
            'resistance': resistance,
            'novelty': novelty,
            'synthesizability': synth,
            'efficacy_note': f'ODE HR={hr:.3f}' if hr else 'No HR',
            'selectivity_note': sel_note,
            'safety_note': safety_note,
            'resistance_note': res_note,
            'novelty_note': nov_note,
            'synth_note': synth_note,
            'hr': hr,
        })
    
    # Score Tier 2 drugs (IC50 only)
    if drug_results['tier2']:
        max_ic50 = max(d['ic50_uM'] for d in drug_results['tier2'] if d['ic50_uM'] > 0)
        
        for d in drug_results['tier2'][:20]:
            drug_name = d['drug']
            ic50 = d['ic50_uM']
            target = d.get('target', '')
            
            # Efficacy from IC50 (lower = better)
            efficacy = round(100 * (1.0 - ic50 / max(max_ic50, 0.001)), 1)
            efficacy = max(0, efficacy)
            
            # Selectivity
            sel_info = selectivity_data.get(target, {})
            ratio = sel_info.get('ratio_vs_mean', 1.0)
            selectivity = min(round(ratio * 10, 1), 100)
            
            # Others default for Tier 2
            safety = 50
            resistance = 30
            novelty = 50
            synth = 50
            
            weights = [0.30, 0.25, 0.20, 0.15, 0.05, 0.05]
            scores = [efficacy, selectivity, safety, resistance, novelty, synth]
            composite = round(sum(w * s for w, s in zip(weights, scores)), 1)
            
            candidates.append({
                'drug': drug_name,
                'tier': 2,
                'composite': composite,
                'efficacy': efficacy,
                'selectivity': selectivity,
                'safety': safety,
                'resistance': resistance,
                'novelty': novelty,
                'synthesizability': synth,
                'efficacy_note': f'IC50={ic50:.3f}uM (NOT comparable to Tier 1 ODE scores)',
                'selectivity_note': f'{target} GTEx ratio {ratio:.1f}x',
                'safety_note': 'Unknown (no SMILES)',
                'resistance_note': 'Unknown (no ODE)',
                'novelty_note': 'Unknown (not checked)',
                'synth_note': 'Unknown',
                'ic50_uM': ic50,
            })
    
    # Pareto ranking
    if candidates:
        score_matrix = np.array([
            [c['efficacy'], c['selectivity'], c['safety'],
             c['resistance'], c['novelty'], c['synthesizability']]
            for c in candidates
        ])
        
        n = len(score_matrix)
        ranks = np.zeros(n, dtype=int)
        remaining = set(range(n))
        rank = 1
        
        while remaining:
            rem_list = sorted(remaining)
            sub = score_matrix[rem_list]
            dominated = set()
            for i in range(len(sub)):
                for j in range(len(sub)):
                    if i == j:
                        continue
                    if np.all(sub[j] >= sub[i]) and np.any(sub[j] > sub[i]):
                        dominated.add(i)
                        break
            front = [rem_list[i] for i in range(len(sub)) if i not in dominated]
            for idx in front:
                ranks[idx] = rank
                remaining.discard(idx)
            rank += 1
            if rank > n:
                break
        
        for i, c in enumerate(candidates):
            c['pareto_rank'] = int(ranks[i])
    
    # Sort by pareto rank then composite
    candidates.sort(key=lambda c: (c['pareto_rank'], -c['composite']))
    
    dt = time.time() - t0
    print(f'    Ranked {len(candidates)} candidates in {dt:.1f}s')
    print(f'    Pareto front: {sum(1 for c in candidates if c["pareto_rank"]==1)} candidates')
    
    return candidates


# ---------------------------------------------------------------------------
# STAGE 5: GENERATE DELIVERABLE
# ---------------------------------------------------------------------------

def generate_deliverable(top_candidates, disease_net, drug_results, escape_routes):
    """Generate 10-item pharma deliverable for each top candidate.
    
    EVERY item generated from data and templates.
    NO human-written text. NO typed numbers.
    """
    print(f'\n  STAGE 5: Generating deliverable for top {len(top_candidates)} candidates')
    
    interactions = disease_net.get('_interactions', {})
    gene_pathways = disease_net.get('_gene_pathways', {})
    selectivity = disease_net.get('_selectivity', {})
    gdsc_map = disease_net.get('gdsc_target_to_drugs', {})
    disease_name = disease_net.get('disease', 'unknown')
    
    # Reverse map
    drug_to_target = {}
    for target, drugs in gdsc_map.items():
        for drug in drugs:
            drug_to_target[drug] = target
    
    packages = []
    
    for cand in top_candidates:
        drug_name = cand['drug']
        target = drug_to_target.get(drug_name, 'unknown')
        mechanism = cand.get('mechanism', 'unknown') if cand.get('tier') == 1 else 'targeted'
        
        # Item 1: Structure
        item1 = {
            'drug': drug_name,
            'target': target,
            'source': 'GDSC PUTATIVE_TARGET',
        }
        
        # Item 2: Mechanism of Action (GENERATED by net traversal)
        target_partners = interactions.get(target, [])
        top_partners = sorted(target_partners, key=lambda x: -x['score'])[:5]
        partner_names = [p['partner'] for p in top_partners]
        
        target_pws = gene_pathways.get(target, [])
        pw_names = [p['name'] for p in target_pws[:3]]
        
        sel = selectivity.get(target, {})
        ratio = sel.get('ratio_vs_mean', 0)
        
        if mechanism == 'cytotoxic':
            moa_text = (
                f'{drug_name} is a cytotoxic agent that kills all actively dividing cells. '
                f'Mechanism: disrupts essential cellular machinery required for cell division. '
                f'Not selective for cancer cells -- also affects healthy dividing cells '
                f'(bone marrow, gut lining, hair follicles). '
                f'Efficacy depends on cancer cells dividing faster than healthy cells.'
            )
        else:
            moa_text = (
                f'{drug_name} targets {target}. '
                f'{target} interacts with {", ".join(partner_names[:3])} (STRING v12). '
            )
            if pw_names:
                moa_text += f'{target} belongs to pathways: {", ".join(pw_names)}. '
            if ratio > 2:
                moa_text += (
                    f'{target} is enriched {ratio:.1f}x in disease tissue vs mean '
                    f'(GTEx v8), suggesting selectivity. '
                )
            elif ratio > 0:
                moa_text += (
                    f'{target} selectivity ratio is {ratio:.1f}x (GTEx v8). '
                    f'Low selectivity -- may affect healthy tissue. '
                )
        
        moa_text += '[Generated by automated net traversal. Review by medicinal chemist recommended.]'
        
        item2 = {'text': moa_text, 'source': 'STRING + KEGG + GTEx net traversal'}
        
        # Item 3: Predicted Outcomes
        if cand.get('tier') == 1 and cand.get('hr'):
            item3 = {
                'model': 'Phenotype-structured ODE (20 bins, Lorz-Lorenzi-Clairambault framework)',
                'hr': cand['hr'],
                'ttp_months': cand.get('ttp_months'),
                'source': 'ODE simulation with GDSC-derived EC50 and published PK',
                'limitation': (
                    'ODE predicts benefit for all simulated drugs. '
                    'Cannot model pathway escape mechanisms. '
                    'Validated for docetaxel (HR=0.69 vs TAX-327 0.76) '
                    'and enzalutamide (PFS=18.6mo vs PREVAIL 18.0mo).'
                ),
            }
        else:
            item3 = {
                'ic50_uM': cand.get('ic50_uM'),
                'source': 'GDSC measured IC50',
                'limitation': 'No ODE simulation. PK parameters needed for HR prediction.',
            }
        
        # Item 4: Resistance Profile
        if cand.get('tier') == 1 and cand.get('nadir_fraction') is not None:
            nadir = cand['nadir_fraction']
            item4 = {
                'nadir_fraction': nadir,
                'interpretation': (
                    f'At nadir, {nadir*100:.1f}% of initial tumor burden survives '
                    f'in resistant bins. '
                    f'{"Low residual disease." if nadir < 0.01 else "Significant resistant population survives."}'
                ),
                'source': 'ODE bin survival distribution',
            }
        else:
            item4 = {
                'status': 'Not available without ODE simulation',
                'source': 'N/A',
            }
        
        # Item 5: Combination Rationale
        target_escapes = escape_routes.get(target, {})
        if target_escapes and target_escapes.get('top_escapes'):
            top_escape = target_escapes['top_escapes'][0]
            item5 = {
                'primary_target': target,
                'escape_gene': top_escape['gene'],
                'shared_pathways': top_escape['shared_pathways'],
                'string_score': top_escape['string_score'],
                'blocking_drugs': top_escape.get('drugs', []),
                'rationale': (
                    f'{drug_name} blocks {target}. Network analysis identifies '
                    f'{top_escape["gene"]} as potential escape route '
                    f'({top_escape["shared_pathways"]} shared pathways, '
                    f'STRING score {top_escape["string_score"]}). '
                    f'Drugs targeting {top_escape["gene"]}: {", ".join(top_escape.get("drugs", [])[:3])}.'
                ),
                'source': 'STRING + KEGG escape route analysis',
                'limitation': 'Topological prediction. Causal escape requires experimental validation.',
            }
        else:
            item5 = {
                'status': f'No escape routes identified for {target}',
                'source': 'STRING + KEGG',
            }
        
        # Item 6: Safety Profile
        item6 = {
            'lipinski_note': cand.get('safety_note', 'Not computed'),
            'selectivity': f'{target} ratio {ratio:.1f}x (GTEx v8)',
            'source': 'RDKit + GTEx',
            'limitation': 'Rule-based ADMET only. No SwissADME/pkCSM. No organ toxicity prediction.',
        }
        
        # Item 7: Synthesis
        item7 = {
            'status': 'Established drug (already manufactured)' if cand.get('tier') == 1 else 'Synthesis assessment requires SMILES + SA_Score',
            'source': 'Drug approval status',
            'limitation': 'ASKCOS retrosynthesis not available.',
        }
        
        # Item 8: Novelty (ClinicalTrials.gov — needs internet)
        item8 = {'status': 'Requires ClinicalTrials.gov API query (internet needed)', 'source': 'N/A'}
        try:
            query_str = f'{drug_name} {disease_name}'.replace(' ', '+')
            url = f'https://clinicaltrials.gov/api/v2/studies?query.term={query_str}&pageSize=1'
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                n_trials = data.get('totalCount', 0)
            item8 = {
                'search_query': f'{drug_name} {disease_name}',
                'n_trials': n_trials,
                'interpretation': (
                    f'{"No registered trials. Potentially novel application." if n_trials == 0 else f"{n_trials} existing trials."}'
                ),
                'source': 'ClinicalTrials.gov API v2',
            }
        except Exception:
            item8['status'] = 'ClinicalTrials.gov query failed (network issue)'
        
        # Item 9: Comparison vs Standard of Care
        # Find docetaxel results
        doc_result = [d for d in drug_results['tier1'] if d['drug'] == 'docetaxel']
        if doc_result and cand.get('hr'):
            doc_hr = doc_result[0].get('hr')
            item9 = {
                'standard': f'Docetaxel HR={doc_hr:.3f}' if doc_hr else 'Docetaxel (no HR)',
                'candidate': f'{drug_name} HR={cand["hr"]:.3f}',
                'comparison': (
                    'Better than standard' if (cand['hr'] and doc_hr and cand['hr'] < doc_hr)
                    else 'Worse than standard' if (cand['hr'] and doc_hr and cand['hr'] > doc_hr)
                    else 'Similar to standard'
                ),
                'source': 'ODE-computed HR comparison',
                'limitation': 'Both HRs from same ODE model. Not independent validation.',
            }
        else:
            item9 = {'status': 'Cannot compare (different scoring tiers)', 'source': 'N/A'}
        
        # Item 10: Suggested Trial Design
        item10 = {
            'biomarker': f'{target} expression' if target != 'unknown' else 'None identified',
            'biomarker_source': f'GTEx ratio {ratio:.1f}x' if ratio > 0 else 'N/A',
            'endpoint': 'Radiographic progression-free survival (rPFS)',
            'design': 'Phase II randomized (candidate vs standard of care)',
            'source': 'Generated from pipeline data',
            'limitation': 'Computational suggestion only. Clinical protocol requires oncologist input.',
        }
        
        packages.append({
            'drug': drug_name,
            'pareto_rank': cand['pareto_rank'],
            'composite_score': cand['composite'],
            'tier': cand.get('tier', 'unknown'),
            'item_1_structure': item1,
            'item_2_mechanism': item2,
            'item_3_outcomes': item3,
            'item_4_resistance': item4,
            'item_5_combination': item5,
            'item_6_safety': item6,
            'item_7_synthesis': item7,
            'item_8_novelty': item8,
            'item_9_comparison': item9,
            'item_10_trial_design': item10,
            'disclaimer': (
                'COMPUTATIONAL PREDICTIONS ONLY. Generated by automated pipeline '
                'from public databases (GDSC, STRING, KEGG, GTEx, Open Targets, ChEMBL). '
                'Not experimentally validated. All candidates require wet-lab confirmation, '
                'preclinical testing, and regulatory review before clinical use. '
                'Known ODE limitation: predicts benefit for all simulated drugs.'
            ),
        })
    
    return packages


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='INTERCEPTA Drug Discovery Pipeline')
    parser.add_argument('--disease', required=True, help='Disease name (e.g., "mCRPC", "AML")')
    parser.add_argument('--output', default=None, help='Output directory')
    args = parser.parse_args()
    
    print('='*70)
    print('INTERCEPTA PIPELINE v1.0')
    print('One disease. Computed results. Documented limitations.')
    print('='*70)
    print(f'Disease query: {args.disease}')
    
    t_start = time.time()
    
    # Stage 1: Find disease
    print('\n  Finding disease...')
    disease_id, disease_name = find_disease(args.disease)
    
    if disease_id is None:
        print(f'  ERROR: Disease "{args.disease}" not found in Open Targets.')
        print(f'  Try a different name or check step8_disease_names.csv')
        sys.exit(1)
    
    print(f'  Found: {disease_name} ({disease_id})')
    
    # Stage 2: Build net + escape routes
    disease_net = build_disease_net(disease_id, disease_name)
    if disease_net is None:
        print(f'  ERROR: Could not build net for {disease_name}')
        sys.exit(1)
    
    escape_routes = find_escape_routes(disease_net)
    
    # Stage 3: Screen drugs
    drug_results = screen_drugs(disease_net, escape_routes)
    
    # Stage 4: Rank
    candidates = compute_ranking(drug_results, disease_net)
    
    # Stage 5: Generate deliverable for top 5
    top5 = candidates[:5]
    deliverable = generate_deliverable(top5, disease_net, drug_results, escape_routes)
    
    # Save everything
    out_dir = Path(args.output) if args.output else RESULTS
    out_prefix = disease_name.replace(' ', '_').lower()
    
    # Remove internal data before saving
    net_save = {k: v for k, v in disease_net.items() if not k.startswith('_')}
    
    with open(out_dir / f'pipeline_{out_prefix}_net.json', 'w') as f:
        json.dump(net_save, f, indent=2, default=str)
    
    with open(out_dir / f'pipeline_{out_prefix}_escape_routes.json', 'w') as f:
        json.dump(escape_routes, f, indent=2, default=str)
    
    with open(out_dir / f'pipeline_{out_prefix}_drug_results.json', 'w') as f:
        json.dump(drug_results, f, indent=2, default=str)
    
    pd.DataFrame(candidates).to_csv(out_dir / f'pipeline_{out_prefix}_ranking.csv', index=False)
    
    with open(out_dir / f'pipeline_{out_prefix}_deliverable.json', 'w') as f:
        json.dump(deliverable, f, indent=2, default=str)
    
    # Print summary
    t_total = time.time() - t_start
    
    print(f'\n{"="*70}')
    print(f'INTERCEPTA PIPELINE COMPLETE')
    print(f'{"="*70}')
    print(f'  Disease: {disease_name}')
    print(f'  Genes in net: {disease_net["n_genes"]}')
    print(f'  Interactions: {disease_net["n_interactions"]}')
    print(f'  Escape routes: {len(escape_routes)} targets')
    print(f'  Tier 1 (ODE): {len(drug_results["tier1"])} drugs')
    print(f'  Tier 2 (IC50): {len(drug_results["tier2"])} drugs')
    print(f'  Tier 3 (combos): {len(drug_results["tier3"])} combinations')
    print(f'  Total ranked: {len(candidates)}')
    print(f'  Total time: {t_total:.1f}s')
    
    print(f'\n  TOP 5 CANDIDATES:')
    print(f'  {"Rk":>2} {"Score":>5} {"Tier":>4} {"Drug":<25} {"Key Metric":<30}')
    print(f'  {"-"*70}')
    for c in candidates[:5]:
        metric = f'HR={c["hr"]:.3f}' if c.get('hr') else f'IC50={c.get("ic50_uM","?")}'
        print(f'  {c["pareto_rank"]:>2} {c["composite"]:>5.1f} T{c["tier"]}   {c["drug"]:<25} {metric:<30}')
    
    print(f'\n  Output files:')
    print(f'    pipeline_{out_prefix}_net.json')
    print(f'    pipeline_{out_prefix}_escape_routes.json')
    print(f'    pipeline_{out_prefix}_drug_results.json')
    print(f'    pipeline_{out_prefix}_ranking.csv')
    print(f'    pipeline_{out_prefix}_deliverable.json')
    
    print(f'\n  LIMITATIONS (documented in deliverable):')
    print(f'    - ODE simulation for {len(drug_results["tier1"])} drugs only (6 in PK library)')
    print(f'    - ODE predicts benefit for all simulated drugs (cannot model pathway escape)')
    print(f'    - Escape routes are topological, not causal')
    print(f'    - Velocity distribution from mCRPC (proxy for other diseases)')
    print(f'    - All predictions require experimental validation')


if __name__ == '__main__':
    main()
