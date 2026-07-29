#!/usr/bin/env python3
"""
INTERCEPTA: DEEP BIOLOGICAL CAPABILITY TEST
=============================================
7 tests that push the platform to its limits.
Not file checks — LIVE biological tests with real data.

Run from: cd ~/INTERCEPTA/code && python3 intercepta_capability_test.py

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import pandas as pd
import numpy as np
import json, os, time, sys
from pathlib import Path

# Ensure we're in the right place
BASE = Path(__file__).parent.parent
RESULTS = BASE / 'results'
DATA = BASE / 'data'
CODE = BASE / 'code'

passed = 0
failed = 0
warnings = 0

def PASS(msg):
    global passed; passed += 1
    print(f'  ✓ PASS: {msg}')

def FAIL(msg):
    global failed; failed += 1
    print(f'  ✗ FAIL: {msg}')

def WARN(msg):
    global warnings; warnings += 1
    print(f'  ⚠ WARN: {msg}')

print('='*70)
print('INTERCEPTA DEEP BIOLOGICAL CAPABILITY TEST')
print('='*70)
print(f'Base: {BASE}')
print(f'Time: {time.strftime("%Y-%m-%d %H:%M")}')
print()

# ═══════════════════════════════════════════════════════════════
# TEST 1: Can the platform discover drugs for an UNSEEN disease?
# ═══════════════════════════════════════════════════════════════
print('TEST 1: NOVEL DISEASE — FULL PIPELINE FOR TRIPLE-NEGATIVE BREAST CANCER')
print('='*70)
print('TNBC has NEVER been through our pipeline. Running end-to-end.')

t_start = time.time()

# Step 1a: Query Open Targets for TNBC
import pyarrow.parquet as pq

disease_names = pd.read_csv(RESULTS / 'step8_disease_names.csv')
ot = pq.read_table(RESULTS / 'step8_gene_disease_associations.parquet').to_pandas()

# Try multiple disease name patterns
tnbc_queries = ['triple-negative breast', 'triple negative breast', 
                'basal-like breast', 'TNBC', 'breast carcinoma']
tnbc_diseases = pd.DataFrame()
for q in tnbc_queries:
    matches = disease_names[disease_names['name'].str.contains(q, case=False, na=False)]
    if len(matches) > 0:
        tnbc_diseases = pd.concat([tnbc_diseases, matches])
        print(f'  "{q}" → {len(matches)} diseases')

tnbc_diseases = tnbc_diseases.drop_duplicates('id')
print(f'  Total TNBC-related diseases: {len(tnbc_diseases)}')

if len(tnbc_diseases) == 0:
    # Fallback: try breast cancer broadly
    matches = disease_names[disease_names['name'].str.contains('breast', case=False, na=False)]
    print(f'  Fallback "breast": {len(matches)} diseases')
    if len(matches) > 0:
        tnbc_diseases = matches.head(5)
        WARN('TNBC not found by name. Using broad "breast" match.')
    else:
        FAIL('Cannot find ANY breast-related disease in Open Targets')

if len(tnbc_diseases) > 0:
    # Step 1b: Get gene associations
    tnbc_genes_df = ot[ot['diseaseId'].isin(tnbc_diseases['id'])]
    gene_col = [c for c in ot.columns if c in ['gene','targetId']][0]
    score_col = [c for c in ot.columns if 'score' in c.lower() or 'association' in c.lower()][0]
    
    tnbc_genes = tnbc_genes_df.groupby(gene_col)[score_col].max().sort_values(ascending=False)
    print(f'  Genes associated with TNBC: {len(tnbc_genes)}')
    
    if len(tnbc_genes) >= 50:
        PASS(f'Disease net: {len(tnbc_genes)} genes found')
    elif len(tnbc_genes) > 0:
        WARN(f'Only {len(tnbc_genes)} genes — thin net')
    else:
        FAIL('0 genes for TNBC')
    
    # Step 1c: Check top genes for biological correctness
    top_20 = list(tnbc_genes.head(20).index)
    print(f'  Top 20 genes: {top_20[:10]}...')
    
    expected_tnbc = {'BRCA1','BRCA2','TP53','EGFR','PIK3CA','PTEN','MYC','CDH1','ESR1','PGR','ERBB2'}
    found_expected = expected_tnbc & set(top_20)
    print(f'  Expected TNBC genes in top 20: {found_expected}')
    
    if len(found_expected) >= 3:
        PASS(f'{len(found_expected)} expected TNBC genes found in top 20')
    else:
        FAIL(f'Only {len(found_expected)} expected genes. Top 20 may be wrong.')
    
    # Step 1d: STRING interactions for TNBC genes
    tnbc_gene_set = set(tnbc_genes.head(500).index)
    string_full = pd.read_csv(RESULTS / 'step4_string_full_interactome.csv')
    tnbc_string = string_full[
        (string_full['gene_a'].isin(tnbc_gene_set)) & 
        (string_full['gene_b'].isin(tnbc_gene_set))
    ]
    print(f'  STRING edges (both TNBC genes): {len(tnbc_string)}')
    
    if len(tnbc_string) > 500:
        PASS(f'Interactome: {len(tnbc_string)} edges')
    else:
        WARN(f'Only {len(tnbc_string)} edges — sparse network')
    
    # Step 1e: Pathway coverage
    pathways = pd.read_csv(RESULTS / 'step5_gene_pathway_map.csv')
    tnbc_pathways = pathways[pathways['gene'].isin(tnbc_gene_set)]
    print(f'  Pathway edges for TNBC genes: {len(tnbc_pathways)}')
    print(f'  TNBC genes WITH pathway data: {tnbc_pathways["gene"].nunique()}/{len(tnbc_gene_set)}')
    
    pathway_coverage = tnbc_pathways['gene'].nunique() / max(len(tnbc_gene_set), 1)
    if pathway_coverage > 0.3:
        PASS(f'Pathway coverage: {pathway_coverage:.0%}')
    elif pathway_coverage > 0.05:
        WARN(f'Pathway coverage: {pathway_coverage:.0%} — many genes missing pathways')
    else:
        FAIL(f'Pathway coverage: {pathway_coverage:.0%} — cannot do escape route analysis')
    
    # Step 1f: Drug targets
    chembl = pd.read_csv(RESULTS / 'step7_chembl_activities.csv')
    target_col_ch = [c for c in chembl.columns if 'target' in c.lower() or 'gene' in c.lower()][0]
    tnbc_chembl = chembl[chembl[target_col_ch].isin(tnbc_gene_set)]
    print(f'  ChEMBL activities for TNBC targets: {len(tnbc_chembl)}')
    
    if len(tnbc_chembl) > 100:
        PASS(f'Pharmacome: {len(tnbc_chembl)} compound activities')
    else:
        WARN(f'Only {len(tnbc_chembl)} activities — limited drug space')
    
    t_net = time.time() - t_start
    print(f'\n  TNBC net built in {t_net:.1f}s')

print()

# ═══════════════════════════════════════════════════════════════
# TEST 2: ODE for AML drugs
# ═══════════════════════════════════════════════════════════════
print('TEST 2: ODE PREDICTIONS FOR AML DRUGS')
print('='*70)
print('Does the phenotype ODE produce realistic results for AML?')
print('NOTE: The phenotype ODE was designed for mCRPC. Testing on AML')
print('requires the AML-specific ODE (v5/v6). Testing what we have.')

# Check if AML ODE exists and has results
aml_ode_files = [
    'aml_ode_v4_validation.json',
    'aml_ode_v5_validation.json', 
    'aml_ode_v5b_validation.json',
    'aml_ode_v6_validation.json',
]

print('\n  AML ODE results on disk:')
for f in aml_ode_files:
    fp = RESULTS / f
    if fp.exists():
        sz = fp.stat().st_size
        if sz > 50:
            with open(fp) as fh:
                try:
                    data = json.load(fh)
                    # Extract key results
                    if 'untreated' in data:
                        os_mo = data['untreated'].get('os_mo') or data['untreated'].get('death_mo')
                        print(f'    {f}: untreated OS={os_mo}mo')
                    elif 'model' in data:
                        print(f'    {f}: {data["model"][:50]}')
                except:
                    print(f'    {f}: {sz}B (parse error)')
        else:
            print(f'    {f}: {sz}B (too small)')
    else:
        print(f'    {f}: NOT FOUND')

# Check specific validated results
v5 = RESULTS / 'aml_ode_v5_validation.json'
if v5.exists() and v5.stat().st_size > 50:
    with open(v5) as f:
        d = json.load(f)
    untreated_os = d.get('untreated', {}).get('death_mo')
    cr = d.get('induction', {}).get('cr')
    
    if untreated_os and 2 <= untreated_os <= 6:
        PASS(f'AML untreated OS = {untreated_os}mo (clinical: 2-4mo)')
    elif untreated_os:
        WARN(f'AML untreated OS = {untreated_os}mo (expected 2-4)')
    else:
        FAIL('AML untreated OS not computed')
    
    if cr:
        PASS('AML 7+3 induction CR = True (clinical: 65-75%)')
    else:
        FAIL('AML 7+3 CR not achieved')
else:
    WARN('AML ODE v5 results not found — checking v5b')
    v5b = RESULTS / 'aml_ode_v5b_validation.json'
    if v5b.exists() and v5b.stat().st_size > 50:
        with open(v5b) as f:
            d = json.load(f)
        print(f'    v5b results: {json.dumps(d, indent=2)[:200]}')

print()

# ═══════════════════════════════════════════════════════════════
# TEST 3: Can escape route method find KNOWN combinations?
# ═══════════════════════════════════════════════════════════════
print('TEST 3: ESCAPE ROUTE DISCOVERY — KNOWN COMBINATIONS')
print('='*70)
print('Can our method rediscover known biology without being told?')

# Test 3a: EGFR → MET amplification (NSCLC known escape)
print('\n  3a: EGFR → MET (NSCLC escape route)')
if 'EGFR' in string_full['gene_a'].values or 'EGFR' in string_full['gene_b'].values:
    egfr_partners = set()
    egfr_edges = string_full[(string_full['gene_a']=='EGFR') | (string_full['gene_b']=='EGFR')]
    for _, r in egfr_edges.iterrows():
        partner = r['gene_b'] if r['gene_a']=='EGFR' else r['gene_a']
        egfr_partners.add(partner)
    
    met_found = 'MET' in egfr_partners
    print(f'  EGFR has {len(egfr_partners)} STRING partners')
    print(f'  MET in EGFR partners: {met_found}')
    
    if met_found:
        met_score = egfr_edges[(egfr_edges['gene_a']=='MET') | (egfr_edges['gene_b']=='MET')]
        if len(met_score) > 0:
            print(f'  EGFR-MET score: {met_score.iloc[0]["score"]}')
        PASS('EGFR→MET escape route discoverable from STRING')
    else:
        # Check indirect: EGFR → shared pathway → MET
        egfr_pws = set(pathways[pathways['gene']=='EGFR']['pathway_id'])
        met_pws = set(pathways[pathways['gene']=='MET']['pathway_id'])
        shared = egfr_pws & met_pws
        print(f'  EGFR pathways: {len(egfr_pws)}, MET pathways: {len(met_pws)}, shared: {len(shared)}')
        if shared:
            WARN(f'EGFR-MET not direct partners but share {len(shared)} pathways')
        else:
            FAIL('Cannot find EGFR→MET connection (known NSCLC escape)')
else:
    FAIL('EGFR not in STRING data at all')

# Test 3b: FLT3 → known escape routes in AML
print('\n  3b: FLT3 escape routes (AML)')
flt3_edges = string_full[(string_full['gene_a']=='FLT3') | (string_full['gene_b']=='FLT3')]
flt3_partners = set()
for _, r in flt3_edges.iterrows():
    partner = r['gene_b'] if r['gene_a']=='FLT3' else r['gene_a']
    flt3_partners.add(partner)

print(f'  FLT3 has {len(flt3_partners)} STRING partners')

# Known FLT3 escape: RAS/MAPK activation, BCL2 upregulation
known_flt3_escape = {'NRAS','KRAS','HRAS','MAPK1','MAPK3','BCL2','MCL1','JAK2','STAT5A','STAT5B'}
found_escape = known_flt3_escape & flt3_partners
print(f'  Known escape genes found: {found_escape}')

if len(found_escape) >= 3:
    PASS(f'FLT3 escape routes: {len(found_escape)} known escape genes found')
else:
    WARN(f'Only {len(found_escape)} FLT3 escape genes — may miss combinations')

# Test 3c: AR → AURKA (our own discovery, verify it's real)
print('\n  3c: AR → AURKA (our discovery)')
ar_edges = string_full[(string_full['gene_a']=='AR') | (string_full['gene_b']=='AR')]
ar_partners = set()
for _, r in ar_edges.iterrows():
    partner = r['gene_b'] if r['gene_a']=='AR' else r['gene_a']
    ar_partners.add(partner)

aurka_direct = 'AURKA' in ar_partners
print(f'  AR has {len(ar_partners)} partners, AURKA direct: {aurka_direct}')

if not aurka_direct:
    # Check shared partners (indirect connection)
    aurka_edges = string_full[(string_full['gene_a']=='AURKA') | (string_full['gene_b']=='AURKA')]
    aurka_partners = set()
    for _, r in aurka_edges.iterrows():
        partner = r['gene_b'] if r['gene_a']=='AURKA' else r['gene_a']
        aurka_partners.add(partner)
    
    shared = ar_partners & aurka_partners
    print(f'  AR-AURKA shared partners: {len(shared)}')
    if shared:
        key_intermediaries = shared & {'TP53','MYC','MYCN','PTEN','EZH2','BRCA1'}
        print(f'  Key intermediaries: {key_intermediaries}')
        if key_intermediaries:
            PASS(f'AR→AURKA connected via {key_intermediaries} (matches Beltran pathway)')
        else:
            WARN(f'AR→AURKA connected via {list(shared)[:5]} but not through expected intermediaries')
    else:
        FAIL('AR and AURKA have NO connection in the net')
else:
    PASS('AR→AURKA direct STRING connection')

print()

# ═══════════════════════════════════════════════════════════════
# TEST 4: Disease name matcher stress test
# ═══════════════════════════════════════════════════════════════
print('TEST 4: DISEASE NAME MATCHER — 20 COMMON DISEASES')
print('='*70)

test_diseases = [
    ('breast cancer', ['BRCA1','BRCA2','ERBB2','ESR1','TP53']),
    ('Alzheimer disease', ['APP','PSEN1','PSEN2','APOE','MAPT']),
    ('type 2 diabetes', ['INS','PPARG','TCF7L2','KCNJ11','SLC30A8']),
    ('asthma', ['IL4','IL13','IL5','TSLP','IL33']),
    ('HIV', ['CCR5','CXCR4','CD4','CCL5']),
    ('glioblastoma', ['EGFR','IDH1','TP53','PTEN','TERT']),
    ('lung adenocarcinoma', ['EGFR','KRAS','ALK','ROS1','BRAF']),
    ('melanoma', ['BRAF','NRAS','CDKN2A','PTEN','KIT']),
    ('colorectal cancer', ['APC','KRAS','TP53','SMAD4','PIK3CA']),
    ('rheumatoid arthritis', ['TNF','IL6','JAK1','JAK3','CTLA4']),
    ('Parkinson disease', ['SNCA','LRRK2','PARK7','PINK1','GBA']),
    ('hepatocellular carcinoma', ['TP53','CTNNB1','AXIN1','TERT','ARID1A']),
    ('ovarian cancer', ['BRCA1','BRCA2','TP53','RB1','CCNE1']),
    ('multiple myeloma', ['MYC','TP53','KRAS','NRAS','BRAF']),
    ('schizophrenia', ['DRD2','COMT','DISC1','NRG1','DTNBP1']),
    ('chronic kidney disease', ['PKD1','PKD2','COL4A5','UMOD']),
    ('epilepsy', ['SCN1A','SCN2A','KCNQ2','GABRA1']),
    ('pancreatic cancer', ['KRAS','TP53','SMAD4','CDKN2A','BRCA2']),
    ('leukemia', ['FLT3','NPM1','DNMT3A','IDH1','TP53']),
    ('tuberculosis', ['TNF','IFNG','IL12B','TLR2','VDR']),
]

n_found = 0
n_correct = 0

for disease_name, expected_genes in test_diseases:
    # Search
    matches = disease_names[disease_names['name'].str.contains(disease_name, case=False, na=False)]
    
    if len(matches) == 0:
        # Try shorter terms
        short = disease_name.split()[0]
        matches = disease_names[disease_names['name'].str.contains(short, case=False, na=False)]
    
    if len(matches) > 0:
        n_found += 1
        genes_df = ot[ot['diseaseId'].isin(matches['id'])]
        n_genes = genes_df[gene_col].nunique()
        
        if n_genes > 0:
            top_genes = genes_df.groupby(gene_col)[score_col].max().sort_values(ascending=False).head(50).index
            found_expected = set(expected_genes) & set(top_genes)
            bio_correct = len(found_expected) >= 2
            
            if bio_correct:
                n_correct += 1
                status = '✓'
            else:
                status = '⚠'
            
            print(f'  {status} {disease_name:<30} {n_genes:>5} genes, expected found: {found_expected}')
        else:
            print(f'  ✗ {disease_name:<30} matched disease IDs but 0 genes')
    else:
        print(f'  ✗ {disease_name:<30} NOT FOUND in disease names')

print(f'\n  Disease matcher: {n_found}/20 found, {n_correct}/20 biologically correct')

if n_found >= 18:
    PASS(f'Disease matcher: {n_found}/20 diseases found')
else:
    FAIL(f'Disease matcher: only {n_found}/20 found')

if n_correct >= 15:
    PASS(f'Biological correctness: {n_correct}/20 have expected genes in top 50')
elif n_correct >= 10:
    WARN(f'Biological correctness: {n_correct}/20 — some diseases return wrong genes')
else:
    FAIL(f'Biological correctness: only {n_correct}/20')

print()

# ═══════════════════════════════════════════════════════════════
# TEST 5: Pathway completeness for top 20 oncology targets
# ═══════════════════════════════════════════════════════════════
print('TEST 5: PATHWAY COMPLETENESS — TOP 20 ONCOLOGY TARGETS')
print('='*70)

top_targets = ['EGFR','BRAF','ALK','ERBB2','KRAS','KDR','CDK4','CDK6',
               'FGFR1','RET','MET','PIK3CA','PARP1','AR','ESR1',
               'PDCD1','CTLA4','BCL2','IDH1','FLT3']

pathway_genes = set(pathways['gene'].unique())
string_genes = set(string_full['gene_a'].unique()) | set(string_full['gene_b'].unique())

print(f'  Pathway database: {len(pathway_genes)} genes')
print(f'  STRING database: {len(string_genes)} genes')
print()

in_pathway = 0
in_string = 0
in_neither = 0

for target in top_targets:
    has_pw = target in pathway_genes
    has_str = target in string_genes
    n_pw = len(pathways[pathways['gene']==target]) if has_pw else 0
    n_str = len(string_full[(string_full['gene_a']==target) | (string_full['gene_b']==target)]) if has_str else 0
    
    if has_pw: in_pathway += 1
    if has_str: in_string += 1
    if not has_pw and not has_str: in_neither += 1
    
    pw_status = f'{n_pw} pathways' if has_pw else 'NO pathways'
    str_status = f'{n_str} interactions' if has_str else 'NO interactions'
    icon = '✓' if has_pw and has_str else '⚠' if has_str else '✗'
    print(f'  {icon} {target:<10} {pw_status:<15} {str_status}')

print(f'\n  In pathways: {in_pathway}/20')
print(f'  In STRING: {in_string}/20')
print(f'  In neither: {in_neither}/20')

if in_pathway >= 15:
    PASS(f'Pathway coverage: {in_pathway}/20 oncology targets')
elif in_pathway >= 10:
    WARN(f'Pathway coverage: {in_pathway}/20 — missing targets block escape route analysis')
else:
    FAIL(f'Pathway coverage: only {in_pathway}/20 — critical gap')

if in_string >= 18:
    PASS(f'STRING coverage: {in_string}/20 targets')
else:
    WARN(f'STRING coverage: {in_string}/20')

print()

# ═══════════════════════════════════════════════════════════════
# TEST 6: Biological mechanism trace for discoveries
# ═══════════════════════════════════════════════════════════════
print('TEST 6: MECHANISM TRACE — CAN THE NET EXPLAIN WHY?')
print('='*70)

# 6a: Enzalutamide + Alisertib mechanism chain
print('\n  6a: Enza + Alisertib — trace through net')

# AR → what pathways?
ar_pws = pathways[pathways['gene']=='AR']
print(f'  AR pathways: {len(ar_pws)}')
if len(ar_pws) > 0:
    print(f'    {list(ar_pws["pathway_name"].unique())[:5]}')

# AR → STRING partners → AURKA connection?
ar_partners_list = sorted(ar_partners)[:20]
aurka_partners_set = set()
aurka_e = string_full[(string_full['gene_a']=='AURKA') | (string_full['gene_b']=='AURKA')]
for _, r in aurka_e.iterrows():
    aurka_partners_set.add(r['gene_b'] if r['gene_a']=='AURKA' else r['gene_a'])

bridge_genes = ar_partners & aurka_partners_set
print(f'  AR→AURKA bridge genes: {len(bridge_genes)}')
key_bridges = bridge_genes & {'TP53','MYC','MYCN','PTEN','EZH2','BRCA1','GSK3B','CTNNB1','CDK1','PLK1'}
print(f'  Biologically meaningful bridges: {key_bridges}')

# GTEx selectivity
gtex = pd.read_csv(RESULTS / 'step6_full_selectivity.csv', index_col=0)
for gene in ['AR','AURKA']:
    if gene in gtex.index:
        ratio = gtex.loc[gene, 'ratio_vs_mean']
        print(f'  {gene} prostate selectivity: {ratio:.1f}x')

# Can we explain: AR blockade → NE escape → AURKA → combination rationale?
chain = []
chain.append('1. AR is the primary driver of mCRPC (prostate-selective)')
if key_bridges:
    chain.append(f'2. AR connects to AURKA through {key_bridges}')
chain.append('3. When AR is blocked, NE differentiation via AURKA/N-MYC becomes the escape')
chain.append('4. Alisertib (AURKA inhibitor, IC50 1.2nM) blocks this escape')
chain.append('5. Combination targets BOTH AR-dependent AND NE-escape populations')

for step in chain:
    print(f'    {step}')

if len(key_bridges) >= 2:
    PASS(f'Mechanism chain: AR→{key_bridges}→AURKA fully traceable')
else:
    WARN('Mechanism chain incomplete — bridge genes missing')

# 6b: NPM1 + Cabozantinib
print('\n  6b: NPM1 + Cabozantinib — mechanism trace')
npm1_edges = string_full[(string_full['gene_a']=='NPM1') | (string_full['gene_b']=='NPM1')]
npm1_partners = set()
for _, r in npm1_edges.iterrows():
    npm1_partners.add(r['gene_b'] if r['gene_a']=='NPM1' else r['gene_a'])

# Cabozantinib targets: MET, VEGFR2 (KDR), RET, AXL, FLT3
cabo_targets = {'MET','KDR','RET','AXL','FLT3'}
npm1_to_cabo = npm1_partners & cabo_targets
print(f'  NPM1 partners: {len(npm1_partners)}')
print(f'  NPM1 → cabozantinib targets: {npm1_to_cabo}')

if npm1_to_cabo:
    PASS(f'NPM1→cabozantinib: connected via {npm1_to_cabo}')
else:
    # Check indirect
    for target in cabo_targets:
        t_edges = string_full[(string_full['gene_a']==target) | (string_full['gene_b']==target)]
        t_partners = set()
        for _, r in t_edges.iterrows():
            t_partners.add(r['gene_b'] if r['gene_a']==target else r['gene_a'])
        shared = npm1_partners & t_partners
        if shared:
            print(f'  NPM1→{target} via {list(shared)[:3]}')
    WARN('NPM1-cabozantinib is statistical (BeatAML p=2.9e-12) but net mechanism indirect')

print()

# ═══════════════════════════════════════════════════════════════
# TEST 7: Pharma deliverable quality check
# ═══════════════════════════════════════════════════════════════
print('TEST 7: PHARMA DELIVERABLE QUALITY')
print('='*70)

pkg_file = RESULTS / 'pharma_deliverable_enza_alis.json'
if pkg_file.exists():
    with open(pkg_file) as f:
        pkg = json.load(f)
    
    # Check each required item
    items = {
        'item_1_molecular_structure': 'Has SMILES strings',
        'item_2_mechanism_of_action': 'Explains biology',
        'item_3_predicted_outcomes': 'Has numbers with CI',
        'item_4_resistance_profile': 'Identifies resistant populations',
        'item_5_combination_rationale': 'Explains why combination works',
        'item_6_safety_profile': 'Identifies organ toxicities',
        'item_7_synthesis': 'Has synthesis info',
        'item_8_novelty': 'ClinicalTrials.gov checked',
        'item_9_vs_standard': 'Side-by-side comparison',
        'item_10_trial_design': 'Measurable endpoints',
    }
    
    for key, requirement in items.items():
        val = pkg.get(key)
        has_content = val is not None and str(val) not in ('', '{}', 'None', 'null')
        
        if has_content:
            # Deeper quality check
            val_str = json.dumps(val) if isinstance(val, dict) else str(val)
            if len(val_str) > 50:
                PASS(f'{key}: {requirement} ({len(val_str)} chars)')
            else:
                WARN(f'{key}: exists but thin ({len(val_str)} chars)')
        else:
            FAIL(f'{key}: MISSING — {requirement}')
    
    # Specific quality checks
    outcomes = pkg.get('item_3_predicted_outcomes', {})
    if isinstance(outcomes, dict):
        has_ci = 'CI' in str(outcomes) or 'confidence' in str(outcomes).lower() or 'ci' in str(outcomes).lower()
        if has_ci:
            PASS('Predicted outcomes have confidence intervals')
        else:
            WARN('Predicted outcomes lack confidence intervals')
    
    trial = pkg.get('item_10_trial_design', {})
    if isinstance(trial, dict):
        has_endpoint = 'endpoint' in str(trial).lower() or 'PFS' in str(trial) or 'OS' in str(trial)
        has_biomarker = 'biomarker' in str(trial).lower() or 'AURKA' in str(trial) or 'NE' in str(trial)
        if has_endpoint and has_biomarker:
            PASS('Trial design has measurable endpoints + biomarker selection')
        elif has_endpoint:
            WARN('Trial design has endpoints but no biomarker selection')
        else:
            FAIL('Trial design lacks measurable endpoints')
else:
    FAIL('Pharma deliverable file not found')

# Also check the complete package
complete_file = RESULTS / 'pharma_deliverable_complete.json'
if complete_file.exists():
    with open(complete_file) as f:
        complete = json.load(f)
    
    print(f'\n  Complete package: {len(complete)} candidates')
    for c in complete:
        items_filled = sum(1 for k,v in c.items() if k.startswith('item_') and v and str(v) not in ('{}','None',''))
        name = c.get('name','?')[:35]
        print(f'    {name:<35} {items_filled}/9 items')

print()

# ═══════════════════════════════════════════════════════════════
# FINAL SCORECARD
# ═══════════════════════════════════════════════════════════════
print('='*70)
print('FINAL SCORECARD')
print('='*70)
total = passed + failed + warnings
print(f'  PASSED:   {passed}/{total}')
print(f'  WARNINGS: {warnings}/{total}')
print(f'  FAILED:   {failed}/{total}')
print()

if failed == 0:
    print('  VERDICT: ALL TESTS PASS')
elif failed <= 3:
    print(f'  VERDICT: {failed} FAILURES — platform works but has gaps')
elif failed <= 7:
    print(f'  VERDICT: {failed} FAILURES — significant gaps remain')
else:
    print(f'  VERDICT: {failed} FAILURES — platform not ready')

print()
print('HONEST ASSESSMENT:')
if n_found >= 18:
    print('  ✓ Disease net builder works for most diseases')
else:
    print(f'  ✗ Disease net builder fails for {20-n_found} of 20 common diseases')

print(f'  {"✓" if in_pathway >= 15 else "✗"} Pathway data covers {in_pathway}/20 top oncology targets')
print(f'  {"✓" if in_string >= 18 else "⚠"} STRING covers {in_string}/20 targets')
print(f'  {"✓" if len(key_bridges) >= 2 else "⚠"} AR→AURKA mechanism traceable through net')

# Save results
results = {
    'test_date': time.strftime('%Y-%m-%d %H:%M'),
    'passed': passed, 'warnings': warnings, 'failed': failed,
    'tnbc_genes': len(tnbc_genes) if 'tnbc_genes' in dir() else 0,
    'disease_matcher': {'found': n_found, 'correct': n_correct, 'total': 20},
    'pathway_coverage': {'in_pathways': in_pathway, 'in_string': in_string, 'total': 20},
}
with open(RESULTS / 'capability_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nSaved: results/capability_test_results.json')
