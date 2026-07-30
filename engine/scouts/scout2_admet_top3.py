#!/usr/bin/env python3
"""
INTERCEPTA: ADMET Analysis for Top 3 Novel AURKA Candidates
============================================================
Computes comprehensive drug-likeness and ADMET indicators
using RDKit descriptors. Honest about what RDKit can and
cannot predict (no false claims about toxicity).

Author: Prasad Akula
"""
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, Fragments, Crippen
import json

def full_admet(smiles, name=''):
    """Comprehensive ADMET profiling from RDKit descriptors."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'error': f'Cannot parse SMILES: {smiles}'}
    
    # Basic properties
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rotatable = Descriptors.NumRotatableBonds(mol)
    rings = rdMolDescriptors.CalcNumRings(mol)
    aromatic_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()
    
    # Lipinski Rule of 5
    lipinski_violations = sum([mw>500, logp>5, hbd>5, hba>10])
    
    # Veber rules (oral bioavailability)
    veber_pass = tpsa <= 140 and rotatable <= 10
    
    # Ghose filter
    ghose_pass = (160 <= mw <= 480 and -0.4 <= logp <= 5.6 
                  and 40 <= heavy_atoms <= 130 and 20 <= Descriptors.MolMR(mol) <= 130)
    
    # Egan filter (absorption)
    egan_pass = tpsa <= 131.6 and logp <= 5.88
    
    # Muegge filter
    muegge_pass = (200 <= mw <= 600 and -2 <= logp <= 5 
                   and tpsa <= 150 and rings <= 7 and hba <= 10 
                   and hbd <= 5 and rotatable <= 15)
    
    # PAINS (pan-assay interference) — check for common problematic substructures
    # RDKit doesn't have built-in PAINS, check for known alerts manually
    alerts = []
    alert_smarts = {
        'Michael_acceptor': '[C]=[C]-[C]=[O]',
        'Epoxide': 'C1OC1',
        'Aldehyde': '[CH]=O',
        'Acyl_halide': 'C(=O)[F,Cl,Br,I]',
        'Sulfonyl_halide': 'S(=O)(=O)[F,Cl,Br,I]',
        'Hydroxamic_acid': 'C(=O)NO',
        'Hydrazine': 'NN',
        'Quinone': 'O=C1C=CC(=O)C=C1',
    }
    for alert_name, smarts in alert_smarts.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            alerts.append(alert_name)
    
    # Metabolic soft spots
    soft_spots = []
    # Primary alcohol (rapidly oxidized by ADH)
    if Chem.MolFromSmarts('[CH2]O') and mol.HasSubstructMatch(Chem.MolFromSmarts('[CH2]O')):
        soft_spots.append('primary_alcohol_ADH_substrate')
    # Phenol (glucuronidation)
    if Chem.MolFromSmarts('c[OH]') and mol.HasSubstructMatch(Chem.MolFromSmarts('c[OH]')):
        soft_spots.append('phenol_glucuronidation')
    # Ester (hydrolysis)
    if Chem.MolFromSmarts('C(=O)OC') and mol.HasSubstructMatch(Chem.MolFromSmarts('C(=O)OC')):
        soft_spots.append('ester_hydrolysis')
    # N-dealkylation
    if Chem.MolFromSmarts('[#7]C') and mol.HasSubstructMatch(Chem.MolFromSmarts('cN(C)C')):
        soft_spots.append('N_dealkylation')
    
    # Predicted absorption
    gut_absorption = 'HIGH' if tpsa < 140 and logp > -1 else 'LOW'
    bbb_penetration = 'YES' if tpsa < 90 and logp > 1 else 'NO'
    pgp_substrate = 'LIKELY' if mw > 400 and hbd > 2 else 'UNLIKELY'
    
    # Solubility estimate (ESOL)
    log_s = 0.16 - 0.63*logp - 0.0062*mw + 0.066*rotatable - 0.74*aromatic_rings
    solubility_class = ('HIGH' if log_s > -2 else 'MODERATE' if log_s > -4 
                        else 'LOW' if log_s > -6 else 'VERY LOW')
    
    return {
        'name': name,
        'smiles': smiles,
        'basic': {
            'mw': round(mw, 1), 'logp': round(logp, 2),
            'hbd': hbd, 'hba': hba, 'tpsa': round(tpsa, 1),
            'rotatable_bonds': rotatable, 'rings': rings,
            'aromatic_rings': aromatic_rings, 'heavy_atoms': heavy_atoms,
        },
        'drug_likeness': {
            'lipinski_violations': lipinski_violations,
            'lipinski': 'PASS' if lipinski_violations <= 1 else 'FAIL',
            'veber': 'PASS' if veber_pass else 'FAIL',
            'ghose': 'PASS' if ghose_pass else 'FAIL',
            'egan': 'PASS' if egan_pass else 'FAIL',
            'muegge': 'PASS' if muegge_pass else 'FAIL',
        },
        'absorption': {
            'gut_absorption': gut_absorption,
            'bbb_penetration': bbb_penetration,
            'pgp_substrate': pgp_substrate,
            'solubility_logS': round(log_s, 2),
            'solubility_class': solubility_class,
        },
        'metabolism': {
            'soft_spots': soft_spots if soft_spots else ['none_detected'],
            'n_soft_spots': len(soft_spots),
        },
        'toxicity_alerts': {
            'structural_alerts': alerts if alerts else ['none_detected'],
            'n_alerts': len(alerts),
        },
    }

def main():
    print('INTERCEPTA ADMET: TOP 3 NOVEL AURKA CANDIDATES')
    print('='*60)
    
    with open('../results/scout2_docked_novel_corrected.json') as f:
        novel = json.load(f)
    
    # Also profile alisertib for comparison
    alisertib_smi = 'COc1cc2c(cc1OC)N(C(=O)c1ccc(Cl)cc1)C(=O)/C2=C\\c1[nH]c2ccc(F)cc2c1C'
    
    candidates = [
        ('Alisertib (reference)', alisertib_smi),
    ]
    for i, cand in enumerate(novel[:3]):
        candidates.append((f'INTC-{i+1:03d}', cand['smiles']))
    
    all_results = []
    for name, smi in candidates:
        result = full_admet(smi, name)
        all_results.append(result)
        
        print(f'\n{"="*55}')
        print(f'{name}')
        print(f'  SMILES: {smi[:60]}...' if len(smi)>60 else f'  SMILES: {smi}')
        b = result['basic']
        print(f'  MW={b["mw"]} LogP={b["logp"]} HBD={b["hbd"]} HBA={b["hba"]} TPSA={b["tpsa"]}')
        
        dl = result['drug_likeness']
        filters = [f'{k}={v}' for k,v in dl.items() if k != 'lipinski_violations']
        print(f'  Drug-likeness: {", ".join(filters)}')
        
        ab = result['absorption']
        print(f'  Absorption: gut={ab["gut_absorption"]} BBB={ab["bbb_penetration"]} PgP={ab["pgp_substrate"]}')
        print(f'  Solubility: {ab["solubility_class"]} (logS={ab["solubility_logS"]})')
        
        met = result['metabolism']
        print(f'  Metabolic soft spots: {met["soft_spots"]}')
        
        tox = result['toxicity_alerts']
        print(f'  Structural alerts: {tox["structural_alerts"]}')
    
    # Side-by-side comparison
    print(f'\n{"="*60}')
    print(f'SIDE-BY-SIDE COMPARISON')
    print(f'{"":>15} {"Alisertib":>12} {"INTC-001":>12} {"INTC-002":>12} {"INTC-003":>12}')
    print('-'*65)
    
    metrics = [
        ('MW', lambda r: r['basic']['mw']),
        ('LogP', lambda r: r['basic']['logp']),
        ('TPSA', lambda r: r['basic']['tpsa']),
        ('HBD', lambda r: r['basic']['hbd']),
        ('HBA', lambda r: r['basic']['hba']),
        ('Lipinski', lambda r: r['drug_likeness']['lipinski']),
        ('Gut Absorb', lambda r: r['absorption']['gut_absorption']),
        ('BBB', lambda r: r['absorption']['bbb_penetration']),
        ('Solubility', lambda r: r['absorption']['solubility_class']),
        ('Soft spots', lambda r: r['metabolism']['n_soft_spots']),
        ('Alerts', lambda r: r['toxicity_alerts']['n_alerts']),
    ]
    
    for label, fn in metrics:
        vals = [str(fn(r)) for r in all_results]
        print(f'{label:>15} {vals[0]:>12} {vals[1]:>12} {vals[2]:>12} {vals[3]:>12}')
    
    # Overall assessment
    print(f'\nOVERALL ASSESSMENT:')
    for r in all_results:
        name = r['name']
        issues = []
        if r['drug_likeness']['lipinski'] == 'FAIL': issues.append('Lipinski fail')
        if r['absorption']['gut_absorption'] == 'LOW': issues.append('poor absorption')
        if r['metabolism']['n_soft_spots'] > 0: issues.append(f'{r["metabolism"]["n_soft_spots"]} metabolic soft spots')
        if r['toxicity_alerts']['n_alerts'] > 0: issues.append(f'{r["toxicity_alerts"]["n_alerts"]} structural alerts')
        if r['basic']['logp'] > 5: issues.append('high LogP (poor solubility)')
        
        if not issues:
            print(f'  {name}: NO ISSUES DETECTED — drug-like ✓')
        else:
            print(f'  {name}: {", ".join(issues)}')
    
    # Save
    with open('../results/scout2_admet_top3.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f'\nSaved: results/scout2_admet_top3.json')
    
    print(f'\nHONEST LIMITATIONS OF THIS ADMET:')
    print(f'  - RDKit descriptors are PREDICTIONS, not measurements')
    print(f'  - No CYP inhibition prediction (needs specialized models)')
    print(f'  - No hERG (cardiac) liability prediction')
    print(f'  - No hepatotoxicity prediction')
    print(f'  - Metabolic soft spots are heuristic, not comprehensive')
    print(f'  - SwissADME or pkCSM would give more complete profiles')
    print(f'  - NONE of this replaces experimental ADMET testing')

if __name__ == '__main__':
    main()
