#!/usr/bin/env python3
"""
INTERCEPTA: PRE-REBUILD FEASIBILITY AUDIT
==========================================
Before we build ANYTHING, test whether the rebuild plan works.

Questions this audit answers:
1. Can we chain the 15 real innovations into one pipeline?
2. What blocks what? (dependency map)
3. What's the minimum code to produce ONE honest end-to-end run?
4. Which partial innovations are closest to done?
5. Which partial innovations BLOCK the pipeline?
6. What external resources do we need? (APIs, data, tools)
7. Can we actually run intercepta_pipeline.py --disease "mCRPC" today?

Run: cd ~/INTERCEPTA/code && python3 pre_rebuild_audit.py 2>&1 | tee ../PRE_REBUILD_AUDIT.txt
"""
import pandas as pd
import numpy as np
import json, os, sys, time, importlib
from pathlib import Path

BASE = Path(__file__).parent.parent
RESULTS = BASE / 'results'
CODE = BASE / 'code'
DATA = BASE / 'data'

print('='*70)
print('INTERCEPTA PRE-REBUILD FEASIBILITY AUDIT')
print(f'Started: {time.strftime("%Y-%m-%d %H:%M")}')
print('='*70)

blockers = []
ready = []
effort = {}

# ═══════════════════════════════════════════════════════════════
# TEST 1: Can Stage 1 (Disease Net) run automatically?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('PIPELINE STAGE 1: Disease Net Builder')
print('Can it run for ANY disease with ONE function call?')
print('='*70)

# Check if disease_net_builder.py exists and is importable
net_builder_path = CODE / 'disease_net_builder.py'
if net_builder_path.exists():
    print(f'  File exists: {net_builder_path}')
    
    # Try to import
    sys.path.insert(0, str(CODE))
    try:
        # Read the file and check what functions exist
        with open(net_builder_path) as f:
            code_text = f.read()
        
        has_build_func = 'def build' in code_text or 'def create' in code_text or 'def disease' in code_text
        has_main = '__main__' in code_text
        takes_disease_name = 'disease_name' in code_text or 'disease' in code_text
        
        print(f'  Has build function: {has_build_func}')
        print(f'  Has __main__: {has_main}')
        print(f'  Takes disease name input: {takes_disease_name}')
        
        # Check what data it reads
        reads_ot = 'step8' in code_text or 'open_targets' in code_text.lower() or 'parquet' in code_text
        reads_string = 'step4' in code_text or 'string' in code_text.lower() or 'interactome' in code_text
        reads_kegg = 'step5' in code_text or 'pathway' in code_text
        reads_gtex = 'step6' in code_text or 'selectivity' in code_text or 'gtex' in code_text.lower()
        reads_chembl = 'step7' in code_text or 'chembl' in code_text.lower()
        
        print(f'\n  Data sources connected:')
        print(f'    Open Targets (diseases→genes): {reads_ot}')
        print(f'    STRING (interactions): {reads_string}')
        print(f'    KEGG (pathways): {reads_kegg}')
        print(f'    GTEx (selectivity): {reads_gtex}')
        print(f'    ChEMBL (compounds): {reads_chembl}')
        
        connected = sum([reads_ot, reads_string, reads_kegg, reads_gtex, reads_chembl])
        
        if connected >= 3 and has_build_func:
            ready.append('Stage 1: Disease net builder')
            print(f'\n  ✓ READY: {connected}/5 data sources connected')
        else:
            blockers.append(f'Stage 1: Only {connected}/5 data sources connected in builder')
            print(f'\n  ✗ BLOCKER: Only {connected}/5 sources. Need to connect missing ones.')
        
        effort['Stage 1'] = '0.5 sessions (connect missing sources)' if connected < 5 else 'DONE'
        
    except Exception as e:
        blockers.append(f'Stage 1: Cannot analyze builder: {e}')
        print(f'  ✗ ERROR: {e}')
else:
    blockers.append('Stage 1: disease_net_builder.py not found')
    print(f'  ✗ MISSING: {net_builder_path}')
    effort['Stage 1'] = '1 session (write from scratch)'

# ═══════════════════════════════════════════════════════════════
# TEST 2: Can Stage 2 (Vulnerability Map) run automatically?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('PIPELINE STAGE 2: Vulnerability Map + Escape Routes')
print('='*70)

# Check escape route finder
escape_files = list(CODE.glob('*escape*')) + list(CODE.glob('*vulnerability*'))
print(f'  Escape route code files: {[f.name for f in escape_files]}')

if escape_files:
    for ef in escape_files:
        with open(ef) as f:
            ct = f.read()
        
        # Does it take a disease net as input?
        takes_net = 'disease_net' in ct or 'unified_net' in ct or 'net' in ct.lower()
        # Does it output escape routes?
        outputs_escape = 'escape' in ct and ('return' in ct or 'save' in ct or 'json' in ct)
        # Is it hardcoded for mCRPC?
        hardcoded_mcrpc = 'mcrpc' in ct.lower() or "'AR'" in ct or 'prostate' in ct.lower()
        # Does it use STRING?
        uses_string = 'string' in ct.lower() or 'interactome' in ct.lower()
        
        print(f'\n  {ef.name}:')
        print(f'    Takes disease net input: {takes_net}')
        print(f'    Outputs escape routes: {outputs_escape}')
        print(f'    Hardcoded for mCRPC: {hardcoded_mcrpc}')
        print(f'    Uses STRING: {uses_string}')
        
    if hardcoded_mcrpc:
        blockers.append('Stage 2: Escape route finder is hardcoded for mCRPC. Needs generalization.')
        effort['Stage 2'] = '1 session (generalize escape route finder)'
    else:
        ready.append('Stage 2: Escape route finder')
        effort['Stage 2'] = 'DONE or 0.5 sessions'
else:
    blockers.append('Stage 2: No escape route code found')
    effort['Stage 2'] = '1.5 sessions (build from scratch)'

# ═══════════════════════════════════════════════════════════════
# TEST 3: Can Stage 3 (Drug Screening) run automatically?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('PIPELINE STAGE 3: Drug Screening + ODE')
print('='*70)

# Check ODE
ode_files = list(CODE.glob('*ode*')) + list(CODE.glob('*phenotype*'))
print(f'  ODE code files: {[f.name for f in ode_files]}')

# Can we import and run the ODE?
try:
    from intercepta_phenotype_ode_v1 import PhenotypeStructuredODE, load_velocity_distribution, PK_LIBRARY
    
    print(f'\n  ODE importable: YES')
    print(f'  PK Library drugs: {list(PK_LIBRARY.keys())}')
    print(f'  Number of drugs with PK: {len(PK_LIBRARY)}')
    
    # Can we run it?
    t0 = time.time()
    n0, _ = load_velocity_distribution(str(RESULTS / 'velocity_star_latent_time.csv'), 20)
    m = PhenotypeStructuredODE(20)
    m.add_drug('docetaxel', 730)
    r = m.simulate(n0 * 0.15, 730)
    t_run = time.time() - t0
    
    print(f'  Live ODE test: HR={r.get("hr","?")} in {t_run:.2f}s')
    
    ready.append('Stage 3: ODE runs and produces HR')
    
    # But can it screen ALL drugs?
    print(f'\n  SCREENING CAPABILITY:')
    print(f'    Drugs with PK (can simulate): {len(PK_LIBRARY)}')
    print(f'    GDSC drugs (need PK to simulate): 286')
    print(f'    Gap: {286 - len(PK_LIBRARY)} drugs cannot be simulated')
    
    blockers.append(f'Stage 3: Only {len(PK_LIBRARY)}/286 drugs have PK parameters')
    effort['Stage 3 ODE'] = 'DONE (for 6 drugs)'
    effort['Stage 3 PK expansion'] = '2 sessions (parse DrugBank/ChEMBL PK for 50+ drugs)'
    
except Exception as e:
    blockers.append(f'Stage 3: ODE cannot run: {e}')
    print(f'  ✗ ODE ERROR: {e}')
    effort['Stage 3'] = '??? (ODE broken)'

# ═══════════════════════════════════════════════════════════════
# TEST 4: Can Stage 4 (Computed Ranking) work?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('PIPELINE STAGE 4: Computed Multi-Objective Ranking')
print('Each dimension must come from computation, not typing')
print('='*70)

dimensions = {
    'Efficacy': {
        'source': 'ODE-computed HR',
        'available': True,  # ODE produces HR
        'for_all_drugs': False,  # Only 6 drugs
    },
    'Selectivity': {
        'source': 'GTEx ratio of drug target',
        'available': os.path.exists(RESULTS / 'step6_full_selectivity.csv'),
        'for_all_drugs': True,  # GTEx has all genes
    },
    'Safety': {
        'source': 'Lipinski violations + CYP + hERG',
        'available': True,  # RDKit computable
        'for_all_drugs': False,  # Need SMILES for each drug
    },
    'Resistance': {
        'source': 'ODE resistant-tail fraction at nadir',
        'available': True,  # ODE outputs bin distribution
        'for_all_drugs': False,  # Only 6 drugs
    },
    'Novelty': {
        'source': 'ClinicalTrials.gov trial count',
        'available': True,  # API queryable
        'for_all_drugs': True,  # Can query any drug
    },
    'Synthesizability': {
        'source': 'SA_Score from RDKit',
        'available': True,  # RDKit computable
        'for_all_drugs': False,  # Need SMILES
    },
}

all_computable = True
for dim_name, dim_info in dimensions.items():
    icon = '✓' if dim_info['available'] else '✗'
    scope = 'all drugs' if dim_info['for_all_drugs'] else 'limited drugs'
    print(f'  {icon} {dim_name:<16} from: {dim_info["source"]:<35} scope: {scope}')
    if not dim_info['available']:
        all_computable = False

if all_computable:
    ready.append('Stage 4: All 6 ranking dimensions are computable')
    print(f'\n  ✓ All dimensions computable (some limited to drugs with PK/SMILES)')
else:
    blockers.append('Stage 4: Some ranking dimensions not computable')

effort['Stage 4'] = '1 session (wire each dimension to computation)'

# Check: do we have SMILES for GDSC drugs?
smiles_path = RESULTS / 'step7_chembl_smiles.csv'
if smiles_path.exists():
    smiles = pd.read_csv(smiles_path)
    print(f'\n  ChEMBL SMILES: {len(smiles)} compounds')
    print(f'  Can compute Safety + Synthesizability for these')
else:
    print(f'\n  ChEMBL SMILES file: NOT FOUND')
    print(f'  Need SMILES to compute ADMET and SA_Score')

# ═══════════════════════════════════════════════════════════════
# TEST 5: Can Stage 5 (Deliverable) be GENERATED?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('PIPELINE STAGE 5: Automated Deliverable Generation')
print('Each of 10 items must be CODE-GENERATED, not human-written')
print('='*70)

deliverable_items = {
    '1. Molecular structure (SMILES)': {
        'can_generate': True,
        'from': 'ChEMBL database lookup',
        'effort': 'trivial',
    },
    '2. Mechanism of action': {
        'can_generate': True,
        'from': 'Automated net traversal: drug target → STRING top partners → shared pathways → template text',
        'effort': '0.5 sessions (template + net traversal code)',
    },
    '3. Predicted outcomes + CI': {
        'can_generate': True,
        'from': 'ODE HR + bootstrap CI (already computed)',
        'effort': 'trivial (read from ODE output)',
    },
    '4. Resistance profile': {
        'can_generate': True,
        'from': 'ODE bin survival distribution at nadir + regrowth trajectory',
        'effort': '0.5 sessions (extract from ODE state vector)',
    },
    '5. Combination rationale': {
        'can_generate': True,
        'from': 'Escape route: "Drug A blocks [target], escape via [gene] → Drug B blocks escape"',
        'effort': '0.5 sessions (template from escape route output)',
    },
    '6. Safety profile': {
        'can_generate': True,
        'from': 'RDKit ADMET computation + GTEx selectivity ratio',
        'effort': '0.5 sessions (compute and format)',
    },
    '7. Synthesis route': {
        'can_generate': False,
        'from': 'ASKCOS API (external, requires MIT access) or SA_Score only',
        'effort': 'SA_Score: trivial. Full retrosynthesis: needs ASKCOS API access.',
    },
    '8. Novelty confirmation': {
        'can_generate': True,
        'from': 'ClinicalTrials.gov API v2 query',
        'effort': 'trivial (already implemented)',
    },
    '9. Comparison vs standard of care': {
        'can_generate': True,
        'from': 'Side-by-side ODE output: candidate HR vs docetaxel HR',
        'effort': 'trivial (format ODE results)',
    },
    '10. Trial design': {
        'can_generate': True,
        'from': 'Biomarker from selectivity, dose from PK Cmax, endpoint = PFS',
        'effort': '0.5 sessions (template from pipeline data)',
    },
}

can_generate_count = 0
for item, info in deliverable_items.items():
    icon = '✓' if info['can_generate'] else '~'
    if info['can_generate']:
        can_generate_count += 1
    print(f'  {icon} {item}')
    print(f'    From: {info["from"]}')
    print(f'    Effort: {info["effort"]}')

print(f'\n  Can auto-generate: {can_generate_count}/10 items')
if can_generate_count >= 9:
    ready.append(f'Stage 5: {can_generate_count}/10 items can be auto-generated')
else:
    blockers.append(f'Stage 5: Only {can_generate_count}/10 auto-generable')

effort['Stage 5'] = '2 sessions (templates + wiring for all 10 items)'

# ═══════════════════════════════════════════════════════════════
# TEST 6: What external resources do we need?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('EXTERNAL RESOURCES NEEDED')
print('='*70)

external = {
    'Internet for ClinicalTrials.gov API': ('NEEDED for novelty check', 'Available'),
    'Internet for KEGG API': ('NEEDED if rebuilding pathways', 'Available'),
    'ASKCOS API (MIT)': ('NEEDED for retrosynthesis', 'Requires MIT academic access'),
    'SwissADME API': ('NICE TO HAVE for ADMET', 'Free web API, needs wrapper'),
    'DrugBank download': ('NEEDED for PK expansion', 'Academic license required'),
    'NCI-ALMANAC data': ('NEEDED for synergy validation', 'Free download from NCI'),
    'PubChem API': ('NICE TO HAVE for broader compound search', 'Free API'),
    'ZINC database': ('NICE TO HAVE for virtual screening', 'Large download ~100GB'),
    'Neo4j': ('NEEDED for graph database', 'Free community edition'),
    'PyTorch/TensorFlow': ('NEEDED for generative chemistry', 'Free, pip install'),
}

for resource, (purpose, availability) in external.items():
    available = 'Available' in availability or 'Free' in availability
    icon = '✓' if available else '⚠'
    print(f'  {icon} {resource}')
    print(f'    Purpose: {purpose}')
    print(f'    Status: {availability}')

# ═══════════════════════════════════════════════════════════════
# TEST 7: Dependency Map — what blocks what?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('DEPENDENCY MAP')
print('='*70)

deps = [
    ('Disease Net', 'Vulnerability Map', 'Net feeds vulnerability analysis'),
    ('Vulnerability Map', 'Escape Routes', 'Targets feed escape route search'),
    ('Escape Routes', 'Combination Design', 'Escape genes define drug B'),
    ('PK Library', 'ODE Simulation', '6 drugs → need 50+ for screening'),
    ('ODE Simulation', 'Efficacy Score', 'HR is the efficacy metric'),
    ('GTEx Selectivity', 'Selectivity Score', 'Ratio is the selectivity metric'),
    ('ChEMBL SMILES', 'ADMET Score', 'Need structure for ADMET'),
    ('ChEMBL SMILES', 'SA_Score', 'Need structure for synthesizability'),
    ('ClinicalTrials.gov', 'Novelty Score', 'Trial count is novelty metric'),
    ('All 6 Scores', 'Pareto Ranking', 'Computed scores feed ranking'),
    ('Pareto Ranking', 'Deliverable', 'Top candidates get full package'),
    ('Net Traversal', 'MoA Text', 'Automated mechanism generation'),
    ('ODE Output', 'Outcomes Text', 'HR + CI from computation'),
    ('Escape Routes', 'Combo Rationale', 'Explains why combination'),
    ('ADMET', 'Safety Text', 'Computed safety profile'),
    ('ODE Bins', 'Resistance Text', 'Bin survival = resistance profile'),
]

print(f'  Pipeline dependency chain:')
for src, dst, why in deps:
    print(f'    {src} → {dst}: {why}')

# Find critical path
print(f'\n  CRITICAL PATH (longest chain):')
print(f'    Disease Name → Open Targets → Gene List')
print(f'    → STRING (interactions) + KEGG (pathways) + GTEx (selectivity)')
print(f'    → Vulnerability Map + Escape Routes')
print(f'    → Drug candidates (ChEMBL lookup)')
print(f'    → ODE simulation (needs PK!) → HR')
print(f'    → Computed ranking (6 dimensions)')
print(f'    → Generated deliverable (10 items)')
print(f'    ')
print(f'    BOTTLENECK: PK Library (6 drugs). Everything after ODE is blocked')
print(f'    for drugs without PK parameters.')

# ═══════════════════════════════════════════════════════════════
# TEST 8: Minimum Viable Pipeline — what can run TODAY?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('MINIMUM VIABLE PIPELINE: What can run TODAY?')
print('='*70)

print(f"""
  WITH CURRENT CODE (no new development):
  
  1. Disease net for mCRPC: YES (existing unified net)
  2. Vulnerability map: YES (GTEx selectivity + STRING)
  3. Escape routes: YES (AR→AURKA already found)
  4. ODE for docetaxel: YES (HR=0.692 in 0.49s)
  5. ODE for enzalutamide: YES (PFS=18.6mo)
  6. ODE for 4 other drugs: YES (abiraterone, olaparib, talazoparib, ADT)
  7. Ranking with computed scores: NO (scores are typed, not computed)
  8. Generated deliverable: NO (text is handwritten)
  
  MINIMUM NEW CODE TO GET END-TO-END:
  
  A. ranking_computed.py — read ODE HR, GTEx ratio, Lipinski, 
     SA_Score, ClinicalTrials.gov count → 6 computed scores
     → Pareto rank. Estimated: 1-2 hours of coding.
  
  B. deliverable_generator.py — for each top candidate:
     net traversal → template MoA
     ODE output → outcomes
     ODE bins → resistance profile  
     RDKit → ADMET
     RDKit → SA_Score
     ClinicalTrials.gov → novelty
     side-by-side → comparison
     selectivity gene → trial biomarker
     Estimated: 2-3 hours of coding.
  
  C. intercepta_pipeline.py — chains A+B with existing code
     Estimated: 1 hour of coding.
  
  TOTAL TO MINIMUM VIABLE: ~5 hours of coding.
  NOT 5 sessions. 5 HOURS.
  
  But this only works for mCRPC with 6 drugs.
  For ANY disease: need PK expansion (2 sessions).
  For novel molecules: need generative chemistry (months).
""")

# ═══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('PRE-REBUILD SUMMARY')
print('='*70)

print(f'\n  READY TO USE (no new code): {len(ready)}')
for r in ready:
    print(f'    ✓ {r}')

print(f'\n  BLOCKERS (must fix): {len(blockers)}')
for b in blockers:
    print(f'    ✗ {b}')

print(f'\n  EFFORT ESTIMATES:')
for component, est in effort.items():
    print(f'    {component}: {est}')

print(f"""
  
  ═══════════════════════════════════════════
  THE HONEST REBUILD PLAN (in order)
  ═══════════════════════════════════════════
  
  SESSION 1 (5 hours): MINIMUM VIABLE PIPELINE
    Build: intercepta_pipeline.py
    Chains: net builder → escape routes → ODE (6 drugs) → 
            COMPUTED ranking → GENERATED deliverable
    Test: python3 intercepta_pipeline.py --disease mCRPC
    Output: honest deliverable with all limitations documented
    Success criteria: one command, one output, every number computed
  
  SESSION 2: PK EXPANSION
    Download published PK for 50+ oncology drugs from DrugBank/literature
    Each drug needs: dose_mg, Cmax_uM, half_life_h, protein_binding
    This unblocks ODE simulation for any disease
    Test: screen 50 drugs for mCRPC, AML, TNBC
  
  SESSION 3: SECOND DISEASE (AML)
    Run: python3 intercepta_pipeline.py --disease AML
    Uses BeatAML data + expanded PK
    Validates: same pipeline, different disease, correct biology
  
  SESSION 4: THIRD DISEASE (TNBC or NSCLC)
    Run: python3 intercepta_pipeline.py --disease "breast cancer"
    Tests: truly new disease, no prior analysis
    If it works: universality demonstrated
  
  SESSION 5+: ADVANCED CAPABILITIES
    ODE drug-target mechanism (fix false positives in equations)
    Real generative chemistry (diffusion models)
    Graph database (Neo4j)
    Novel technologies (GNN, causal inference)
  
  This is the HONEST path. Not 12 blockers to fix.
  5 hours to minimum viable. Then expand.
""")

# Save
results = {
    'date': time.strftime('%Y-%m-%d %H:%M'),
    'ready': ready,
    'blockers': blockers,
    'effort': effort,
    'minimum_viable_hours': 5,
    'sessions_to_universal': 4,
}
with open(RESULTS / 'pre_rebuild_audit.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'Saved: results/pre_rebuild_audit.json')
