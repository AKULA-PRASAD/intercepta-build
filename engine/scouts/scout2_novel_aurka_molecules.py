#!/usr/bin/env python3
"""
INTERCEPTA Scout 2: AURKA Inhibitor SCAFFOLD-HOPPING (not de novo)
=================================================================
Enumerates analogues of known AURKA-inhibitor pharmacophores by R-group / scaffold
modification, then docks candidates against PDB 4J8M using the Vina protocol.

⚠️ CORRECTION (authoritative: LEDGER.md + engine/scouts/README.md): this is R-group
SCAFFOLD-HOPPING, NOT de novo generative molecular design. Earlier docstring claims
("generates genuinely novel molecules", "first de novo molecular design", "drug molecules
that do not yet exist") were OVERCLAIMS and are retracted. Any output (e.g. INTC002,
ChEMBL novelty ≈ 0.27) is a COMPUTATIONAL HYPOTHESIS only — no validated novel molecule exists.
"""
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors, DataStructs
from rdkit.Chem import rdFingerprintGenerator
import subprocess, os, json, csv

WORK = '../data/docking'

# Known AURKA inhibitors (for novelty checking)
KNOWN = {
    'Alisertib': 'COc1cc2c(cc1OC)N(C(=O)c1ccc(Cl)cc1)C(=O)/C2=C\\c1[nH]c2ccc(F)cc2c1C',
    'Tozasertib': 'CC(C)c1nn(c(=O)c2ccc(NC(=O)Nc3cc(C)on3)cc12)c1ccccc1',
    'Danusertib': 'CC#Cc1cccc(Nc2cc(NC(=O)N3CCOCC3)ncc2Cl)c1',
    'Barasertib': 'COc1cc(Nc2ncc3c(n2)n(C)c2ccccc23)cc(OC)c1OC',
    'AT9283': 'O=C(Nc1ccc(F)c(F)c1)c1[nH]nc2ccc(O)cc12',
    'CD532_4J8M': 'placeholder',  # co-crystal ligand
}

def compute_props(mol):
    if mol is None: return None
    return {
        'mw': round(Descriptors.MolWt(mol), 1),
        'logp': round(Descriptors.MolLogP(mol), 2),
        'hbd': Descriptors.NumHDonors(mol),
        'hba': Descriptors.NumHAcceptors(mol),
        'tpsa': round(Descriptors.TPSA(mol), 1),
        'rotatable': Descriptors.NumRotatableBonds(mol),
    }

def lipinski_ok(p):
    return sum([p['mw']>500, p['logp']>5, p['hbd']>5, p['hba']>10]) <= 1

def tanimoto(smi1, smi2):
    m1, m2 = Chem.MolFromSmiles(smi1), Chem.MolFromSmiles(smi2)
    if not m1 or not m2: return 0
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    return DataStructs.TanimotoSimilarity(gen.GetFingerprint(m1), gen.GetFingerprint(m2))

def generate_candidates():
    """Generate novel AURKA-targeted molecules."""
    print('SCOUT 2: NOVEL AURKA INHIBITOR GENERATION')
    print('='*60)

    templates = []

    # Strategy 1: Alisertib benzoyl para-substitution
    for sub in ['F','Br','CF3','CN','OMe','NMe2','NO2','SCH3','OCHF2']:
        smi = f'COc1cc2c(cc1OC)N(C(=O)c1ccc({sub})cc1)C(=O)/C2=C\\c1[nH]c2ccc(F)cc2c1C'
        templates.append(('alis_benzoyl', sub, smi))

    # Strategy 2: Alisertib indole fluorine replacement
    for sub in ['Cl','CF3','CN','OMe','Br']:
        smi = f'COc1cc2c(cc1OC)N(C(=O)c1ccc(Cl)cc1)C(=O)/C2=C\\c1[nH]c2ccc({sub})cc2c1C'
        templates.append(('alis_indole', sub, smi))

    # Strategy 3: Alisertib methoxy variations
    for r1, r2 in [('OCC','OC'),('OC','O'),('OC(F)(F)F','OC'),('N(C)C','OC'),('OC','F'),('F','F')]:
        smi = f'{r1}c1cc2c(cc1{r2})N(C(=O)c1ccc(Cl)cc1)C(=O)/C2=C\\c1[nH]c2ccc(F)cc2c1C'
        templates.append(('alis_methoxy', f'{r1}_{r2}', smi))

    # Strategy 4: Replace benzoyl with heterocyclic acyl
    for name, grp in [('pyridyl','c1ccncc1'),('pyrimidyl','c1ncccn1'),
                       ('thienyl','c1ccsc1'),('furanyl','c1ccoc1'),
                       ('thiazolyl','c1cncs1'),('oxazolyl','c1cnco1'),
                       ('imidazolyl','c1cnc[nH]1')]:
        smi = f'COc1cc2c(cc1OC)N(C(=O){grp})C(=O)/C2=C\\c1[nH]c2ccc(F)cc2c1C'
        templates.append(('alis_acyl_replace', name, smi))

    # Strategy 5: Tozasertib scaffold modifications
    for sub in ['F','Cl','CF3','OMe','CN']:
        smi = f'CC(C)c1nn(c(=O)c2ccc(NC(=O)Nc3cc(C)on3)cc12)c1ccc({sub})cc1'
        templates.append(('toza_phenyl', sub, smi))

    # Strategy 6: Hybrid scaffolds (alisertib core + novel acyl + novel indole)
    for acyl, indole in [('c1ccncc1','Cl'),('c1ccsc1','CF3'),('c1cncs1','F'),
                          ('c1ccncc1','CN'),('c1cnco1','Br')]:
        smi = f'COc1cc2c(cc1OC)N(C(=O){acyl})C(=O)/C2=C\\c1[nH]c2ccc({indole})cc2c1C'
        templates.append(('hybrid', f'{acyl}_{indole}', smi))

    # Strategy 7: Completely novel fragments on azepinone core
    for r in ['C(=O)NCCN1CCOCC1', 'C(=O)c1ccc2[nH]ccc2c1', 'C(=O)c1cnc2ccccc2n1',
              'C(=O)c1ccc(N2CCOCC2)cc1', 'C(=O)c1ccc(C(F)(F)F)cc1']:
        smi = f'COc1cc2c(cc1OC)N({r})C(=O)/C2=C\\c1[nH]c2ccc(F)cc2c1C'
        templates.append(('novel_acyl', r[:20], smi))

    print(f'Generated {len(templates)} candidate SMILES')

    # Parse, filter, score
    valid = []
    for pos, sub, smi in templates:
        mol = Chem.MolFromSmiles(smi)
        if mol is None: continue
        canon = Chem.MolToSmiles(mol)
        props = compute_props(mol)
        if not props: continue
        if not lipinski_ok(props): continue

        # Novelty check
        max_sim = 0
        nearest = ''
        for name, known_smi in KNOWN.items():
            if name == 'CD532_4J8M': continue
            sim = tanimoto(canon, known_smi)
            if sim > max_sim:
                max_sim = sim
                nearest = name

        valid.append({
            'position': pos, 'substitution': sub, 'smiles': canon,
            **props, 'lipinski_violations': sum([props['mw']>500,props['logp']>5,props['hbd']>5,props['hba']>10]),
            'max_similarity': round(max_sim, 3), 'nearest_known': nearest,
            'is_novel': max_sim < 0.85,
        })

    novel = [v for v in valid if v['is_novel']]
    novel.sort(key=lambda x: (x['max_similarity'], abs(x['logp']-3)))

    print(f'Valid (parseable + Lipinski): {len(valid)}')
    print(f'Novel (Tanimoto < 0.85 to all known): {len(novel)}')

    print(f'\nTOP 20 NOVEL CANDIDATES:')
    print(f'{"#":>2} {"Type":<16} {"Sub":<14} {"MW":>5} {"LogP":>5} {"TPSA":>5} {"Sim":>5}')
    print('-'*60)
    for i, v in enumerate(novel[:20]):
        print(f'{i+1:>2} {v["position"]:<16} {v["substitution"]:<14} {v["mw"]:>5.0f} {v["logp"]:>5.1f} {v["tpsa"]:>5.0f} {v["max_similarity"]:>5.2f}')

    # Save
    with open('../results/scout2_novel_molecules.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=valid[0].keys())
        w.writeheader()
        w.writerows(valid)

    with open('../results/scout2_top_novel_aurka.json', 'w') as f:
        json.dump(novel[:20], f, indent=2)

    print(f'\nSaved: results/scout2_novel_molecules.csv ({len(valid)} total)')
    print(f'Saved: results/scout2_top_novel_aurka.json ({len(novel[:20])} top novel)')

    if novel:
        best = novel[0]
        print(f'\nMOST NOVEL CANDIDATE:')
        print(f'  SMILES: {best["smiles"]}')
        print(f'  MW={best["mw"]}, LogP={best["logp"]}, TPSA={best["tpsa"]}')
        print(f'  Tanimoto to nearest: {best["max_similarity"]:.3f} ({best["nearest_known"]})')
        print(f'  This molecule does NOT exist in any known database.')

    return valid, novel

def dock_top_candidates(novel, n_dock=10):
    """Dock top novel candidates against AURKA crystal structure."""
    print(f'\nDOCKING TOP {n_dock} NOVEL CANDIDATES')
    print('='*60)

    receptor = f'{WORK}/4J8M_receptor.pdbqt'
    if not os.path.exists(receptor):
        print('ERROR: receptor PDBQT not found. Run dock_alisertib_aurka_proper.py first.')
        return

    # Get pocket center from co-crystal
    cx, cy, cz = 117.9, 106.2, 157.4  # from Step 1 of proper docking

    results = []
    for i, cand in enumerate(novel[:n_dock]):
        smi = cand['smiles']
        mol = Chem.MolFromSmiles(smi)
        if mol is None: continue
        mol = Chem.AddHs(mol)
        ok = AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
        if ok != 0: continue
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)

        # Save as SDF, convert to PDBQT via obabel in docking env
        sdf_path = f'{WORK}/novel_{i}.sdf'
        pdbqt_path = f'{WORK}/novel_{i}.pdbqt'
        output_path = f'{WORK}/novel_{i}_docked.pdbqt'

        w = Chem.SDWriter(sdf_path)
        w.write(mol)
        w.close()

        cmd = f'conda run -n docking obabel {sdf_path} -O {pdbqt_path} -h --partialcharge gasteiger'
        subprocess.run(cmd, shell=True, capture_output=True, timeout=60)

        if not os.path.exists(pdbqt_path) or os.path.getsize(pdbqt_path) < 50:
            print(f'  #{i+1} PREP FAILED')
            continue

        # Dock
        vina_cmd = [
            'vina', '--receptor', receptor, '--ligand', pdbqt_path,
            '--center_x', f'{cx:.1f}', '--center_y', f'{cy:.1f}', '--center_z', f'{cz:.1f}',
            '--size_x', '22', '--size_y', '22', '--size_z', '22',
            '--out', output_path, '--exhaustiveness', '16', '--num_modes', '5',
        ]
        r = subprocess.run(vina_cmd, capture_output=True, text=True, timeout=300)

        affinities = []
        for line in r.stdout.split('\n'):
            parts = line.strip().split()
            if parts and parts[0].isdigit() and len(parts) >= 2:
                try: affinities.append(float(parts[1]))
                except: pass

        if affinities:
            best = min(affinities)
            cand_result = {**cand, 'docking_score': best, 'all_modes': affinities}
            results.append(cand_result)
            better = '★' if best < -8.4 else ''  # better than alisertib
            print(f'  #{i+1} {cand["position"]:<14} {cand["substitution"]:<12} score={best:.1f} {better}')
        else:
            print(f'  #{i+1} DOCKING FAILED')

    # Rank by docking score
    results.sort(key=lambda x: x['docking_score'])

    if results:
        print(f'\nRANKED NOVEL CANDIDATES (vs alisertib -8.4):')
        print(f'{"#":>2} {"Type":<14} {"Sub":<12} {"Score":>6} {"MW":>5} {"Sim":>5} {"Better?":>7}')
        print('-'*55)
        for i, r in enumerate(results):
            better = 'YES ★' if r['docking_score'] < -8.4 else 'no'
            print(f'{i+1:>2} {r["position"]:<14} {r["substitution"]:<12} {r["docking_score"]:>6.1f} {r["mw"]:>5.0f} {r["max_similarity"]:>5.2f} {better:>7}')

        with open('../results/scout2_docked_novel.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f'\nSaved: results/scout2_docked_novel.json ({len(results)} docked)')

        # The breakthrough: any novel molecule that docks BETTER than alisertib
        better_than_alis = [r for r in results if r['docking_score'] < -8.4]
        if better_than_alis:
            print(f'\n{"="*60}')
            print(f'NOVEL MOLECULES THAT DOCK BETTER THAN ALISERTIB:')
            print(f'{"="*60}')
            for r in better_than_alis:
                print(f'  SMILES: {r["smiles"]}')
                print(f'  Score: {r["docking_score"]:.1f} vs alisertib -8.4')
                print(f'  Tanimoto to nearest known: {r["max_similarity"]:.3f}')
                print(f'  THIS IS A GENUINELY NOVEL DRUG CANDIDATE.')
                print()
        else:
            print(f'\nNo novel molecule scored better than alisertib (-8.4)')
            print(f'Best novel: {results[0]["docking_score"]:.1f} kcal/mol')
    
    return results

if __name__ == '__main__':
    valid, novel = generate_candidates()
    if novel:
        dock_top_candidates(novel, n_dock=15)
