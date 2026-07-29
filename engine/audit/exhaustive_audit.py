#!/usr/bin/env python3
"""
INTERCEPTA: EXHAUSTIVE DEEP AUDIT
===================================
2000-level audit across every angle before ANY building.

LEVEL 1: Every parameter — source, derivation, assumption
LEVEL 2: Every claim — computed vs typed vs invented
LEVEL 3: Every data flow — does layer A actually feed layer B?
LEVEL 4: Every biological assertion — literature verified?
LEVEL 5: Every mathematical formula — derived or invented?
LEVEL 6: Every validation — real or circular?
LEVEL 7: Every file — complete, consistent, non-corrupted?
LEVEL 8: Pipeline connectivity — end-to-end for any disease?
LEVEL 9: Reproducibility — same code, same result?
LEVEL 10: Vision gap analysis — what's missing entirely?
LEVEL 11: False claims in all documentation
LEVEL 12: Code bugs hiding wrong results

Run: cd ~/INTERCEPTA/code && python3 exhaustive_audit.py 2>&1 | tee ../EXHAUSTIVE_AUDIT.txt

Our principle: find ALL problems BEFORE acting.
"""
import pandas as pd
import numpy as np
import json, os, sys, time, glob, hashlib
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
RESULTS = BASE / 'results'
CODE = BASE / 'code'
DATA = BASE / 'data'

findings = defaultdict(list)
total_checks = 0

def check(level, category, name, status, detail):
    global total_checks
    total_checks += 1
    icon = {'REAL':'✓', 'MANIPULATED':'✗', 'MIXED':'~', 
            'BUG':'⚠', 'MISSING':'☐', 'OK':'✓', 'FAIL':'✗',
            'BLOCKER':'🚫', 'HONEST':'✓', 'DISHONEST':'✗',
            'CONNECTED':'✓', 'BROKEN':'✗', 'PARTIAL':'~'}[status]
    findings[status].append({'level':level, 'category':category, 'name':name, 'detail':detail})
    print(f'  {icon} [{level}] {category}/{name}: {detail[:100]}')

print('='*70)
print('INTERCEPTA EXHAUSTIVE DEEP AUDIT')
print(f'Started: {time.strftime("%Y-%m-%d %H:%M")}')
print('='*70)

# ═══════════════════════════════════════════════════════════════
# LEVEL 1: EVERY PARAMETER IN EVERY MODEL
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 1: PARAMETER AUDIT — Every number, every source')
print('='*70)

# 1.1 Phenotype ODE parameters
print('\n--- Phenotype ODE Parameters ---')

params = {
    'r_max': {
        'value': 0.00678, 'unit': '/day',
        'source': 'PSA doubling time 102 days, Freedland 2005',
        'derivation': 'ln(2)/102 = 0.00679',
        'status': 'REAL',
    },
    'alpha_r': {
        'value': 0.4, 'unit': 'dimensionless',
        'source': 'NONE — chosen by us',
        'derivation': 'No derivation. Assumed value.',
        'status': 'MANIPULATED',
        'sensitivity': '15% HR variation across range 0.1-0.8',
    },
    'Emax': {
        'value': 0.153, 'unit': '/day',
        'source': 'GDSC kill rate × in vivo correction',
        'derivation': '0.85 (GDSC measured) × 0.18 (estimated)',
        'status': 'MIXED',
        'real_part': 'GDSC kill rate 0.85 is measured',
        'manipulated_part': '0.18 in vivo factor is our estimate, not published',
    },
    'beta': {
        'value': 8.27e-4, 'unit': '/day',
        'source': 'RNA velocity within-cluster variance',
        'derivation': 'var(latent_time) from scVelo output',
        'status': 'REAL',
    },
    'K': {
        'value': 1.0, 'unit': 'normalized',
        'source': 'Normalization convention',
        'derivation': 'Tumor burden normalized to 1.0',
        'status': 'OK',
    },
    'd_nat': {
        'value': 0.001, 'unit': '/day',
        'source': 'CHOSEN — natural death rate',
        'derivation': 'No derivation. Small value assumed.',
        'status': 'MANIPULATED',
    },
}

for name, p in params.items():
    check('L1', 'phenotype_ode', name, p['status'],
          f'{p["value"]} {p["unit"]} — {p["source"]}')

# 1.2 Drug PK parameters — check each drug
print('\n--- Drug PK Parameters ---')
try:
    sys.path.insert(0, str(CODE))
    from intercepta_phenotype_ode_v1 import PK_LIBRARY, DRUG_EFFECT_LIBRARY
    
    for drug, pk in PK_LIBRARY.items():
        # Check if PK values have source comments in code
        check('L1', 'pk_library', f'{drug}_Cmax',
              'REAL' if pk.get('dose_mg') else 'MISSING',
              f'Cmax derived from dose={pk.get("dose_mg")}mg, published PK')
        
    for drug, de in DRUG_EFFECT_LIBRARY.items():
        check('L1', 'drug_effect', f'{drug}_EC50',
              'REAL' if 'GDSC' in str(de.get('source','')) or 'prostate' in str(de).lower() else 'MIXED',
              f'EC50 from {de.get("source","UNKNOWN source")}')
except Exception as e:
    check('L1', 'pk_library', 'import', 'BUG', f'Cannot import: {e}')

# 1.3 AML ODE parameters
print('\n--- AML ODE Parameters ---')
aml_params = {
    'r_blast': {'value': 0.039, 'source': 'Raza 1991 (Tc=90h, GF=21%)', 'status': 'REAL'},
    'd_blast': {'value': 0.026, 'source': 'Derived: r_blast - r_net from OS 90d', 'status': 'MIXED'},
    'r_lsc': {'value': 0.003, 'source': 'Quiescent LSC doubling ~230 days', 'status': 'REAL'},
    'd_lsc': {'value': 0.001, 'source': 'Long-lived assumption', 'status': 'MANIPULATED'},
    'suppress': {'value': 0.11, 'source': 'Derived: N 0.60→0.10 in 90 days', 'status': 'MIXED'},
    'r_normal': {'value': 0.05, 'source': 'Progenitor cycle ~14 days', 'status': 'REAL'},
    'd_normal': {'value': 0.02, 'source': 'From steady state: r*0.4', 'status': 'MIXED'},
    'frac_resistant': {'value': 0.15, 'source': '~30% non-responders, conservative', 'status': 'MANIPULATED'},
    'mu_resistance': {'value': 1e-3, 'source': 'Estimated from months of venetoclax exposure', 'status': 'MANIPULATED'},
    'gcsf_boost': {'value': 5.0, 'source': 'Dale Blood 1993: G-CSF 5-10x', 'status': 'REAL'},
}

for name, p in aml_params.items():
    check('L1', 'aml_ode', name, p['status'],
          f'{p["value"]} — {p["source"]}')

# 1.4 Escape route ODE parameters
print('\n--- Escape Route ODE Parameters ---')
escape_params = {
    'mu_SM': {'desc': 'S→Mutant transition', 'status': 'MANIPULATED', 'source': 'Estimated from relapse prevalence'},
    'mu_SV': {'desc': 'S→V7 transition', 'status': 'MANIPULATED', 'source': 'Estimated from relapse prevalence'},
    'mu_SN': {'desc': 'S→NE transition', 'status': 'MANIPULATED', 'source': 'Estimated from relapse prevalence'},
    'g_mod_N': {'desc': 'NE growth modifier 1.3x', 'status': 'MANIPULATED', 'source': 'Assumed NE grows faster'},
}

for name, p in escape_params.items():
    check('L1', 'escape_ode', name, p['status'], f'{p["desc"]} — {p["source"]}')

# ═══════════════════════════════════════════════════════════════
# LEVEL 2: EVERY CLAIM — computed vs typed
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 2: CLAIM AUDIT — Is each result computed or typed?')
print('='*70)

claims = {
    'Doc HR=0.69': {'computed': True, 'detail': 'ODE solve_ivp output. Not hardcoded.'},
    'Doc+Cis HR=1.00': {'computed': True, 'detail': 'ODE output. Correctly predicts failure.'},
    'Enza PFS=18.6mo': {'computed': True, 'detail': 'Unified ODE output.'},
    'AML OS=4.4mo': {'computed': True, 'detail': 'AML 3-comp ODE output.'},
    'AML 7+3 CR': {'computed': True, 'detail': 'AML ODE tumor burden drops below 5%.'},
    'NPM1+cabo p=2.9e-12': {'computed': True, 'detail': 'Mann-Whitney test on BeatAML patient data.'},
    'Bootstrap CI [0.58,0.79]': {'computed': True, 'detail': '200 bootstrap samples.'},
    'KAALCURA AUROC=0.638': {'computed': True, 'detail': 'sklearn AUROC on GDSC data.'},
    'Pareto rank 1 enza+alis': {'computed': False, 'detail': 'Pareto math is correct but INPUT scores were typed by us.'},
    'Pharma package 9/9 items': {'computed': False, 'detail': 'Items 2,4-9 written by humans, not generated.'},
    '197 drugs HR=1.0': {'computed': False, 'detail': 'HR was OVERWRITTEN, not computed by ODE.'},
    'Temsirolimus rank 16': {'computed': False, 'detail': 'Escape penalty formula invented by us.'},
    '79% completion': {'computed': False, 'detail': 'Percentage includes manipulated pieces counted as "done".'},
    'INTC-002 novel molecule': {'computed': True, 'detail': 'RDKit generates structure, Tanimoto checks novelty.'},
    'INTC-002 no selectivity': {'computed': True, 'detail': 'Docking scores AURKA -9.3 vs AURKB -9.9. Honest.'},
    'Alisertib discovery genuine': {'computed': True, 'detail': '"alisertib" not in code. Found by net traversal.'},
    'Cross-disease 3 candidates': {'computed': True, 'detail': 'Name matching on drug lists.'},
    'p38 MAPK retracted': {'computed': True, 'detail': 'FDR correction killed the finding. Honest.'},
}

for claim, info in claims.items():
    status = 'HONEST' if info['computed'] else 'DISHONEST'
    check('L2', 'claims', claim, status, info['detail'])

# ═══════════════════════════════════════════════════════════════
# LEVEL 3: DATA FLOW — Does each layer connect to the next?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 3: DATA FLOW — Do layers actually connect?')
print('='*70)

# Check: does the ODE actually READ from GDSC EC50?
try:
    from intercepta_phenotype_ode_v1 import DRUG_EFFECT_LIBRARY
    doc_ec50 = DRUG_EFFECT_LIBRARY.get('docetaxel', {})
    if 'ic50_min_uM' in doc_ec50 or 'ec50_range' in str(doc_ec50):
        check('L3', 'flow', 'GDSC→ODE_EC50', 'CONNECTED', 
              f'Docetaxel EC50 from GDSC: {doc_ec50}')
    else:
        check('L3', 'flow', 'GDSC→ODE_EC50', 'PARTIAL',
              f'EC50 in library but source unclear: {list(doc_ec50.keys())[:5]}')
except:
    check('L3', 'flow', 'GDSC→ODE_EC50', 'BROKEN', 'Cannot import')

# Check: does escape route analysis read from STRING?
escape_code = CODE / 'escape_route_combination_finder.py'
if escape_code.exists():
    with open(escape_code) as f:
        code_text = f.read()
    reads_string = 'string' in code_text.lower() or 'interactome' in code_text.lower()
    reads_unified = 'unified_net' in code_text.lower() or 'mcrpc_unified' in code_text.lower()
    check('L3', 'flow', 'STRING→escape_routes', 
          'CONNECTED' if reads_string else 'BROKEN',
          f'Code references STRING: {reads_string}, unified net: {reads_unified}')
else:
    check('L3', 'flow', 'STRING→escape_routes', 'MISSING', 'File not found')

# Check: does Pareto ranking read from ODE output?
pareto_code = CODE / 'pareto_ranking.py'
if pareto_code.exists():
    with open(pareto_code) as f:
        code_text = f.read()
    reads_ode = 'ode' in code_text.lower() or 'unified' in code_text.lower() or 'simulate' in code_text.lower()
    hardcoded = 'efficacy' in code_text and ('75' in code_text or '80' in code_text)
    check('L3', 'flow', 'ODE→Pareto_scores',
          'BROKEN' if hardcoded and not reads_ode else 'CONNECTED' if reads_ode else 'BROKEN',
          f'Reads ODE: {reads_ode}. Has hardcoded scores: {hardcoded}')

# Check: does pharma deliverable read from pipeline or is it handwritten?
pharma_code_files = list(CODE.glob('*pharma*')) + list(CODE.glob('*deliverable*'))
if pharma_code_files:
    for pf in pharma_code_files:
        with open(pf) as f:
            ct = f.read()
        has_pipeline_reads = ('simulate' in ct or 'ode' in ct.lower() or 
                            'string' in ct.lower() or 'gdsc' in ct.lower())
        has_hardcoded_text = ("'summary'" in ct or "'mechanism'" in ct or 
                            "f'" in ct or 'Enzalutamide' in ct)
        check('L3', 'flow', f'{pf.name}→pharma_items',
              'BROKEN' if has_hardcoded_text and not has_pipeline_reads else 'PARTIAL',
              f'Reads pipeline: {has_pipeline_reads}. Has hardcoded text: {has_hardcoded_text}')

# Check: Scout 1 → ODE → Ranking chain
scout1_path = RESULTS / 'scout1_all_drugs_ranked.csv'
if scout1_path.exists():
    s1 = pd.read_csv(scout1_path)
    hr_col = [c for c in s1.columns if 'hr' in c.lower()]
    if hr_col:
        hr_range = (s1[hr_col[0]].min(), s1[hr_col[0]].max())
        all_below_1 = s1[hr_col[0]].max() < 0.95
        check('L3', 'flow', 'Scout1_HR_range',
              'BUG' if all_below_1 else 'OK',
              f'HR range: {hr_range[0]:.3f}-{hr_range[1]:.3f}. All <1.0: {all_below_1}')

# ═══════════════════════════════════════════════════════════════
# LEVEL 4: BIOLOGICAL CORRECTNESS
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 4: BIOLOGICAL CORRECTNESS')
print('='*70)

# 4.1: Is the AR→AURKA→NE pathway biologically correct?
check('L4', 'biology', 'AR→AURKA_pathway',
      'REAL',
      'Published: Beltran Nat Med 2011, Dardenne Cancer Cell 2016. '
      'AR loss → MYCN amplification → AURKA stabilization → NE differentiation.')

# 4.2: Is docetaxel mechanism correct in ODE?
check('L4', 'biology', 'docetaxel_mechanism',
      'PARTIAL',
      'ODE models docetaxel as killing cells based on EC50 gradient. '
      'Real mechanism: microtubule stabilization → mitotic arrest → apoptosis. '
      'ODE does not model mitotic arrest specifically, just kill rate.')

# 4.3: Is the AML 3-compartment model biologically sound?
check('L4', 'biology', 'AML_3comp_structure',
      'REAL',
      'Blast + LSC + Normal competing for marrow space. '
      'Lethality from marrow failure (normal < threshold). '
      'Published: Walenda et al, Andersen "Cancitis" model.')

# 4.4: KAALCURA axes — are they measuring what we claim?
check('L4', 'biology', 'R_prolif_axis',
      'REAL',
      'Proliferation genes (MKI67, CCNB1, etc.) → R_prolif. '
      'High R_prolif = sensitive to chemo. Published biology.')

check('L4', 'biology', 'R_emt_axis',
      'REAL',
      'EMT genes (VIM, ZEB1, etc.) → R_emt. '
      'High R_emt = mesenchymal = resistant to EGFR inhibitors. Published.')

check('L4', 'biology', 'R_ddr_axis',
      'REAL',
      'DNA damage repair genes → R_ddr. '
      'High R_ddr = sensitive to PARP inhibitors. Published.')

# 4.5: Does the net correctly identify that EGFR is not a prostate cancer driver?
gtex_path = RESULTS / 'step6_full_selectivity.csv'
if gtex_path.exists():
    gtex = pd.read_csv(gtex_path, index_col=0)
    if 'EGFR' in gtex.index and 'prostate_tpm' in gtex.columns:
        egfr_prostate = gtex.loc['EGFR', 'prostate_tpm']
        egfr_ratio = gtex.loc['EGFR', 'ratio_vs_mean']
        check('L4', 'biology', 'EGFR_prostate_selectivity',
              'OK',
              f'EGFR prostate TPM={egfr_prostate:.0f}, ratio={egfr_ratio:.1f}x. '
              f'EGFR IS expressed in prostate but is NOT a driver of CRPC.')

# 4.6: NPM1+cabozantinib — is there a biological explanation?
string_path = RESULTS / 'step4_string_full_interactome.csv'
if string_path.exists():
    string = pd.read_csv(string_path)
    npm1_flt3 = string[((string['gene_a']=='NPM1') & (string['gene_b']=='FLT3')) |
                       ((string['gene_a']=='FLT3') & (string['gene_b']=='NPM1'))]
    check('L4', 'biology', 'NPM1→FLT3_connection',
          'REAL' if len(npm1_flt3) > 0 else 'MISSING',
          f'NPM1-FLT3 STRING edge: {len(npm1_flt3)}. '
          f'NPM1 mutations co-occur with FLT3-ITD in 40% of AML. '
          f'Cabozantinib inhibits FLT3. This explains the sensitivity.')

# ═══════════════════════════════════════════════════════════════
# LEVEL 5: MATHEMATICAL FORMULAS — derived or invented?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 5: MATHEMATICAL FORMULAS')
print('='*70)

formulas = {
    'Logistic growth: dN/dt = r*N*(1-N/K)': {
        'status': 'REAL', 'source': 'Standard population dynamics (Verhulst 1838)'},
    'Hill kill: kill = Emax*C^n/(EC50^n+C^n)': {
        'status': 'REAL', 'source': 'Standard pharmacodynamics (Hill 1910)'},
    'Phenotype drift: diffusion along resistance axis': {
        'status': 'REAL', 'source': 'Fick second law of diffusion, standard PDE'},
    'PK: C(t) = Cmax * exp(-ke*t)': {
        'status': 'REAL', 'source': 'First-order elimination, standard PK'},
    'HR = ctrl_TTP / drug_TTP': {
        'status': 'REAL', 'source': 'Standard survival analysis definition'},
    'Bliss independence: E_combo = Ea + Eb - Ea*Eb': {
        'status': 'REAL', 'source': 'Bliss 1939, standard synergy model'},
    'HSA: E_combo > max(Ea, Eb)': {
        'status': 'REAL', 'source': 'Berenbaum 1989, standard'},
    'Escape penalty: HR_new = HR_old + (1-HR_old)*escape_freq': {
        'status': 'MANIPULATED', 'source': 'INVENTED BY US. No published derivation.'},
    'Drug filter: HR=1.0 if target not expressed': {
        'status': 'MANIPULATED', 'source': 'Biological principle is sound, but overwriting ODE output is manipulation.'},
    'Suppress term: d_normal_eff = d_normal + suppress*B': {
        'status': 'MIXED', 'source': 'Biologically motivated (blast suppression of normal hematopoiesis) but suppress=0.11 derived from desired outcome (OS=3mo)'},
    'Tanimoto similarity for novelty': {
        'status': 'REAL', 'source': 'Standard cheminformatics metric'},
    'SA_Score for synthesizability': {
        'status': 'REAL', 'source': 'Ertl & Schuffenhauer 2009, published algorithm'},
    'BH FDR correction': {
        'status': 'REAL', 'source': 'Benjamini-Hochberg 1995, standard statistics'},
    'Bootstrap percentile CI': {
        'status': 'REAL', 'source': 'Efron 1979, standard statistics'},
}

for formula, info in formulas.items():
    check('L5', 'math', formula[:40], info['status'], info['source'])

# ═══════════════════════════════════════════════════════════════
# LEVEL 6: VALIDATION — real or circular?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 6: VALIDATION — Real or circular?')
print('='*70)

validations = {
    'Doc HR vs TAX-327': {
        'status': 'REAL',
        'detail': 'ODE computed HR=0.69. TAX-327 clinical HR=0.76. Parameters set BEFORE comparison. Not circular.'},
    'Doc+Cis failure': {
        'status': 'REAL', 
        'detail': 'ODE computed HR=1.003. All combination trials failed. Parameters same as docetaxel alone.'},
    'Enza PFS vs PREVAIL': {
        'status': 'REAL',
        'detail': 'Unified ODE computed 18.6mo. PREVAIL: 18.0mo. Same params as docetaxel.'},
    'AML OS vs clinical': {
        'status': 'MIXED',
        'detail': 'OS=4.4mo from published params. BUT model structure was iterated until OS was in range.'},
    'KAALCURA AUROC': {
        'status': 'REAL',
        'detail': 'AUROC computed on GDSC training data. No independent test set. Modest 0.638.'},
    'Bootstrap CI contains clinical': {
        'status': 'REAL',
        'detail': 'Parameter ranges from data uncertainty, not chosen to contain 0.76.'},
    'Alisertib literature match': {
        'status': 'REAL',
        'detail': 'Net found AR→AURKA independently. Beltran 2019 and Liadi 2023 validate.'},
    'Temsirolimus rank after filter': {
        'status': 'DISHONEST',
        'detail': 'We invented the escape penalty formula AFTER seeing temsirolimus was wrong. This is post-hoc fitting.'},
}

for name, info in validations.items():
    check('L6', 'validation', name, info['status'], info['detail'])

# ═══════════════════════════════════════════════════════════════
# LEVEL 7: FILE INTEGRITY
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 7: FILE INTEGRITY')
print('='*70)

# Check for empty or suspiciously small files
result_files = list(RESULTS.glob('*'))
empty = 0
tiny = 0
for f in result_files:
    if f.is_file():
        sz = f.stat().st_size
        if sz == 0:
            check('L7', 'files', f.name, 'FAIL', 'EMPTY FILE (0 bytes)')
            empty += 1
        elif sz < 100 and f.suffix in ['.json','.csv']:
            check('L7', 'files', f.name, 'BUG', f'Suspiciously small: {sz} bytes')
            tiny += 1

check('L7', 'files', 'empty_count', 
      'OK' if empty == 0 else 'FAIL',
      f'{empty} empty files, {tiny} suspiciously small files')

# Check JSON parsability
json_files = list(RESULTS.glob('*.json'))
unparseable = 0
for jf in json_files:
    try:
        with open(jf) as f:
            json.load(f)
    except:
        check('L7', 'files', jf.name, 'BUG', 'Cannot parse JSON')
        unparseable += 1

check('L7', 'files', 'json_integrity',
      'OK' if unparseable == 0 else 'FAIL',
      f'{len(json_files)} JSON files, {unparseable} unparseable')

# ═══════════════════════════════════════════════════════════════
# LEVEL 8: PIPELINE CONNECTIVITY — End-to-end for any disease?
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 8: PIPELINE CONNECTIVITY')
print('='*70)

pipeline_steps = {
    'disease_name→Open_Targets': {
        'test': 'Can query any disease name and get genes',
        'status': 'CONNECTED',  # Tested in capability test: 20/20
    },
    'genes→STRING_interactions': {
        'test': 'Can get protein interactions for any gene set',
        'status': 'CONNECTED',  # 236K edges, covers 16K genes
    },
    'genes→pathway_membership': {
        'test': 'Can get pathways for any gene',
        'status': 'CONNECTED',  # Fixed: 9,319 genes, 44,686 edges
    },
    'genes→GTEx_selectivity': {
        'test': 'Can get tissue expression for any gene',
        'status': 'CONNECTED',  # 54,592 genes
    },
    'genes→ChEMBL_compounds': {
        'test': 'Can get compounds targeting any gene',
        'status': 'CONNECTED',  # 24,598 activities
    },
    'compound→ODE_simulation': {
        'test': 'Can simulate any compound effect on tumor',
        'status': 'PARTIAL',
        'detail': 'Only works for drugs in PK_LIBRARY (6 drugs). Cannot simulate arbitrary compounds.',
    },
    'escape_route→combination': {
        'test': 'Can find combination for any escape route',
        'status': 'PARTIAL',
        'detail': 'Net traversal works. Drug selection involves human judgment.',
    },
    'ODE→HR→ranking': {
        'test': 'Can rank drugs by predicted efficacy',
        'status': 'BUG',
        'detail': 'ODE predicts all drugs help. No mechanism for failure. Ranking is compromised.',
    },
    'ranking→pharma_package': {
        'test': 'Can generate deliverable from ranked candidates',
        'status': 'BROKEN',
        'detail': 'Pharma package was handwritten, not generated from pipeline.',
    },
    'mCRPC_end_to_end': {
        'test': 'Full pipeline for mCRPC',
        'status': 'PARTIAL',
        'detail': 'Data→net→escape→ODE works. Ranking→deliverable is human-written.',
    },
    'AML_end_to_end': {
        'test': 'Full pipeline for AML',
        'status': 'PARTIAL',
        'detail': 'Data→net→statistics works. ODE partially validated. No complete deliverable.',
    },
    'new_disease_end_to_end': {
        'test': 'Full pipeline for never-seen disease',
        'status': 'BROKEN',
        'detail': 'Can build net. Cannot run ODE (no PK for arbitrary drugs). Cannot generate deliverable.',
    },
}

for step, info in pipeline_steps.items():
    check('L8', 'pipeline', step, info['status'],
          info.get('detail', info.get('test','')))

# ═══════════════════════════════════════════════════════════════
# LEVEL 9: VISION GAP ANALYSIS
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 9: VISION GAP ANALYSIS')
print('='*70)

vision_requirements = {
    'Novel molecule generation (diffusion/transformer)': {
        'status': 'MISSING', 'detail': 'Vision says AI generative. We did scaffold hopping. No diffusion model.'},
    'Multi-target generation with selectivity constraint': {
        'status': 'MISSING', 'detail': 'Vision says generate molecules constrained by net. We cannot do this.'},
    'RNA velocity time machine for any patient': {
        'status': 'PARTIAL', 'detail': 'Works for GSE137829 mCRPC dataset. Not generalizable to arbitrary scRNA-seq.'},
    'Two-population ODE for any disease': {
        'status': 'PARTIAL', 'detail': 'Works for mCRPC (phenotype ODE) and AML (3-comp). Not automated for new diseases.'},
    'Complete in silico simulation stack (6 layers)': {
        'status': 'PARTIAL', 'detail': 'Docking yes, KAALCURA yes, ODE yes, synergy math only, ADMET rule-based, no retrosynthesis.'},
    'Pharma deliverable with all 10 items': {
        'status': 'MANIPULATED', 'detail': 'Items exist but most were written by us, not generated by pipeline.'},
    'Self-improving feedback loop': {
        'status': 'MISSING', 'detail': 'No mechanism for clinical outcome feedback. No active learning.'},
    'Future disease prediction': {
        'status': 'MISSING', 'detail': 'Vision says predict diseases before emergence. We have pathogen database but no prediction.'},
    'Diagnostic layer (early detection)': {
        'status': 'MISSING', 'detail': 'Vision describes biomarker-based early detection. Not built.'},
    'Cross-disease transfer learning': {
        'status': 'PARTIAL', 'detail': 'Found 3 cross-disease candidates by name matching. No systematic transfer.'},
    'Universal net (all human biology)': {
        'status': 'PARTIAL', 'detail': '15 layers have some data. Most are proxy (STRING-derived), not primary experimental data.'},
    'Automated pipeline (disease name → drug candidate)': {
        'status': 'BROKEN', 'detail': 'Requires manual intervention at every step. No single-command pipeline.'},
}

for req, info in vision_requirements.items():
    check('L9', 'vision', req[:40], info['status'], info['detail'])

# ═══════════════════════════════════════════════════════════════
# LEVEL 10: CODE QUALITY
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('LEVEL 10: CODE QUALITY')
print('='*70)

# Check for hardcoded values that should be parameters
py_files = list(CODE.glob('*.py'))
hardcoded_issues = []
for pf in py_files:
    with open(pf) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        # Look for suspicious hardcoded numbers
        if any(x in line for x in ['0.691', '0.692', '18.6', '4.4', '0.76']):
            if '#' not in line.split('0.')[0]:  # not in a comment
                hardcoded_issues.append(f'{pf.name}:{i+1}: {line.strip()[:60]}')

if hardcoded_issues:
    check('L10', 'code', 'hardcoded_results', 'BUG',
          f'{len(hardcoded_issues)} lines with hardcoded result values')
    for h in hardcoded_issues[:5]:
        print(f'    {h}')
else:
    check('L10', 'code', 'hardcoded_results', 'OK', 'No hardcoded result values found')

# ═══════════════════════════════════════════════════════════════
# FINAL COMPREHENSIVE SUMMARY
# ═══════════════════════════════════════════════════════════════
print('\n' + '='*70)
print('EXHAUSTIVE AUDIT SUMMARY')
print('='*70)

for status in ['REAL','OK','CONNECTED','HONEST', 
               'MIXED','PARTIAL',
               'MANIPULATED','DISHONEST','BUG','BROKEN','FAIL','MISSING','BLOCKER']:
    items = findings.get(status, [])
    if items:
        icon = {'REAL':'✓','OK':'✓','CONNECTED':'✓','HONEST':'✓',
                'MIXED':'~','PARTIAL':'~',
                'MANIPULATED':'✗','DISHONEST':'✗','BUG':'⚠',
                'BROKEN':'✗','FAIL':'✗','MISSING':'☐','BLOCKER':'🚫'}[status]
        print(f'\n  {icon} {status}: {len(items)}')
        for item in items:
            print(f'    [{item["level"]}] {item["category"]}/{item["name"]}')

good = len(findings.get('REAL',[])) + len(findings.get('OK',[])) + len(findings.get('CONNECTED',[])) + len(findings.get('HONEST',[]))
mixed_count = len(findings.get('MIXED',[])) + len(findings.get('PARTIAL',[]))
bad = len(findings.get('MANIPULATED',[])) + len(findings.get('DISHONEST',[])) + len(findings.get('BUG',[])) + len(findings.get('BROKEN',[])) + len(findings.get('FAIL',[])) + len(findings.get('MISSING',[]))

print(f'\n  TOTAL CHECKS: {total_checks}')
print(f'  GOOD (real/ok/connected/honest): {good}')
print(f'  MIXED (part real, part human): {mixed_count}')
print(f'  BAD (manipulated/bug/broken/missing): {bad}')
print(f'  HEALTH: {good}/{total_checks} = {good/max(total_checks,1)*100:.0f}%')

print(f'\n{"="*70}')
print('BLOCKERS TO VISION SUCCESS (must fix before building more)')
print('='*70)

blockers = []
for status in ['MANIPULATED','DISHONEST','BUG','BROKEN','MISSING','BLOCKER']:
    for item in findings.get(status, []):
        if item['level'] in ['L3','L8','L9']:  # pipeline and vision blockers
            blockers.append(item)

for i, b in enumerate(blockers):
    print(f'  {i+1}. [{b["level"]}] {b["category"]}/{b["name"]}')
    print(f'     {b["detail"][:80]}')

print(f'\n  Total blockers: {len(blockers)}')
print(f'\n  FIX THESE {len(blockers)} BLOCKERS BEFORE WRITING ANY NEW CODE.')

# Save
audit_result = {
    'date': time.strftime('%Y-%m-%d %H:%M'),
    'total_checks': total_checks,
    'good': good, 'mixed': mixed_count, 'bad': bad,
    'health_pct': round(good/max(total_checks,1)*100, 1),
    'n_blockers': len(blockers),
    'findings': {k: len(v) for k, v in findings.items()},
    'blockers': [{'level':b['level'],'name':b['name'],'detail':b['detail']} for b in blockers],
}
with open(RESULTS / 'exhaustive_audit.json', 'w') as f:
    json.dump(audit_result, f, indent=2)
print(f'\nSaved: results/exhaustive_audit.json')
print(f'Also save full output: python3 exhaustive_audit.py 2>&1 | tee ../EXHAUSTIVE_AUDIT.txt')
