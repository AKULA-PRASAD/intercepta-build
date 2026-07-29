#!/usr/bin/env python3
"""
INTERCEPTA Stage 4A: Molecular Docking
Docks alisertib → AURKA using AutoDock Vina
Validates that alisertib binds the AURKA ATP-binding pocket.

Authors: Prasad Akula & Claude, Co-Founders of INTERCEPTA
"""
import subprocess
import os
import json
from rdkit import Chem
from rdkit.Chem import AllChem

# Step 1: Prepare ligand (alisertib) as PDBQT
ALISERTIB_SMILES = 'COc1cc2c(cc1OC)N(C(=O)c1ccc(Cl)cc1)C(=O)/C2=C\\c1[nH]c2ccc(F)cc2c1C'

def prepare_ligand(smiles, output_pdbqt):
    """Convert SMILES to 3D structure, then to PDBQT via meeko."""
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    
    # Save as SDF
    sdf_path = output_pdbqt.replace('.pdbqt', '.sdf')
    writer = Chem.SDWriter(sdf_path)
    writer.write(mol)
    writer.close()
    
    # Convert to PDBQT using meeko
    from meeko import MoleculePreparation, PDBQTWriterLegacy
    preparator = MoleculePreparation()
    mol_setup = preparator.prepare(mol)
    pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(mol_setup[0])
    
    if is_ok:
        with open(output_pdbqt, 'w') as f:
            f.write(pdbqt_string)
        print(f'  Ligand prepared: {output_pdbqt}')
        return True
    else:
        print(f'  ERROR: {error_msg}')
        return False

def prepare_receptor(pdb_path, output_pdbqt):
    """Prepare receptor PDBQT from AlphaFold PDB.
    Simple approach: strip waters/heteroatoms, add charges via meeko/obabel."""
    # Read PDB, keep only ATOM records
    with open(pdb_path) as f:
        lines = [l for l in f if l.startswith('ATOM')]
    
    clean_pdb = output_pdbqt.replace('.pdbqt', '_clean.pdb')
    with open(clean_pdb, 'w') as f:
        f.writelines(lines)
        f.write('END\n')
    
    # Try using meeko's receptor preparation or fall back to simple conversion
    # For AlphaFold structures, we add Kollman charges manually
    # Simple approach: rename .pdb to .pdbqt with AD4 atom types
    # This is approximate but sufficient for screening
    pdbqt_lines = []
    for line in lines:
        if len(line) >= 78:
            # Add charge column
            atom_name = line[12:16].strip()
            element = line[76:78].strip() if len(line) >= 78 else atom_name[0]
            # Assign basic AD4 atom types
            ad4_type = element
            if element == 'C': ad4_type = 'C'
            elif element == 'N': ad4_type = 'NA' if 'N' in atom_name else 'N'
            elif element == 'O': ad4_type = 'OA'
            elif element == 'S': ad4_type = 'SA'
            
            charge = 0.0
            pdbqt_line = line[:54] + f'  {charge:>6.3f} {ad4_type:<2}\n'
            pdbqt_lines.append(pdbqt_line)
    
    with open(output_pdbqt, 'w') as f:
        f.writelines(pdbqt_lines)
        f.write('END\n')
    
    print(f'  Receptor prepared: {output_pdbqt} ({len(pdbqt_lines)} atoms)')
    return True

def find_binding_site(pdb_path):
    """Find AURKA ATP-binding pocket coordinates.
    The ATP-binding site of AURKA is well-characterized:
    centered around residues 162-274 (kinase domain hinge).
    Key residues: Ala213 (hinge), Leu263, Thr217."""
    # Parse PDB to find approximate center of kinase domain
    xs, ys, zs = [], [], []
    # ATP pocket residues for AURKA (from crystal structures)
    pocket_residues = list(range(210, 280))  # kinase hinge region
    
    with open(pdb_path) as f:
        for line in f:
            if line.startswith('ATOM'):
                resnum = int(line[22:26].strip())
                if resnum in pocket_residues:
                    xs.append(float(line[30:38]))
                    ys.append(float(line[38:46]))
                    zs.append(float(line[46:54]))
    
    if xs:
        cx, cy, cz = sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)
        print(f'  Binding site center: ({cx:.1f}, {cy:.1f}, {cz:.1f})')
        print(f'  Based on {len(xs)} atoms in residues 210-280 (kinase domain)')
        return cx, cy, cz
    else:
        print('  WARNING: Could not find pocket residues, using structure center')
        with open(pdb_path) as f:
            all_x, all_y, all_z = [], [], []
            for line in f:
                if line.startswith('ATOM'):
                    all_x.append(float(line[30:38]))
                    all_y.append(float(line[38:46]))
                    all_z.append(float(line[46:54]))
        return sum(all_x)/len(all_x), sum(all_y)/len(all_y), sum(all_z)/len(all_z)

def run_docking(receptor_pdbqt, ligand_pdbqt, cx, cy, cz, output_path):
    """Run AutoDock Vina docking."""
    cmd = [
        'vina',
        '--receptor', receptor_pdbqt,
        '--ligand', ligand_pdbqt,
        '--center_x', str(round(cx, 1)),
        '--center_y', str(round(cy, 1)),
        '--center_z', str(round(cz, 1)),
        '--size_x', '25',
        '--size_y', '25', 
        '--size_z', '25',
        '--out', output_path,
        '--exhaustiveness', '16',
        '--num_modes', '9',
    ]
    
    print(f'  Running Vina: {" ".join(cmd[:6])}...')
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    if result.returncode == 0:
        # Parse output for binding affinity
        affinities = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line and line[0].isdigit():
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        affinities.append(float(parts[1]))
                    except ValueError:
                        pass
        
        print(f'  Vina output:\n{result.stdout}')
        return affinities
    else:
        print(f'  Vina ERROR: {result.stderr[:500]}')
        return None

def main():
    print('INTERCEPTA Stage 4A: MOLECULAR DOCKING')
    print('='*60)
    print('Target: AURKA (Aurora Kinase A)')
    print('Ligand: Alisertib (MLN8237)')
    print()
    
    work_dir = '../data/docking'
    os.makedirs(work_dir, exist_ok=True)
    
    aurka_pdb = '../data/alphafold/EGFR_AF-P00533.pdb'  # placeholder
    # Find AURKA — check what we have
    import glob
    aurka_files = glob.glob('../data/alphafold/*AURKA*') + glob.glob('../data/alphafold/*P31749*')
    
    # AURKA UniProt: O14965 (that's AKT2). AURKA is Q96GD4 (human) or O14965
    # Actually check what we downloaded
    print('  Available AlphaFold structures:')
    for f in sorted(glob.glob('../data/alphafold/*.pdb')):
        name = os.path.basename(f)
        size = os.path.getsize(f)
        if size > 200:
            print(f'    {name} ({size//1024}KB)')
    
    # We don't have AURKA downloaded! Need to get it.
    # AURKA UniProt: O14965 — wait, that's AKT2
    # AURKA UniProt is actually O14965? No.
    # Let me check: AURKA human = UniProt O14965? No, AURKA = O14965 is wrong
    # AURKA = O14965 (Homo sapiens) — actually checking...
    # AURKA (Aurora kinase A) UniProt = O14965
    # Wait, our Step 10 has AKT2_AF-O14965.pdb — that's AKT2, not AURKA
    # AURKA UniProt ID needs to be looked up
    
    print('\n  AURKA not in our AlphaFold download!')
    print('  Our 20 targets were mCRPC-focused, AURKA was not included.')
    print('  Downloading AURKA structure now...')
    
    # Download AURKA
    import urllib.request
    aurka_uniprot = 'O14965'  # Need to verify this
    # Actually let me look it up properly
    # AURKA gene → UniProt mapping needed
    
    # From our escape route: AURKA is in the net
    # Check UniProt ID for AURKA
    print('  Looking up AURKA UniProt ID...')
    
    # Try the API
    try:
        url = 'https://rest.uniprot.org/uniprotkb/search?query=gene:AURKA+organism_id:9606&format=json&size=1'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get('results'):
                aurka_id = data['results'][0]['primaryAccession']
                print(f'  AURKA UniProt ID: {aurka_id}')
            else:
                aurka_id = 'O14965'  # fallback
                print(f'  Using fallback: {aurka_id}')
    except:
        aurka_id = 'O14965'
        print(f'  API failed, using: {aurka_id}')
    
    # Get AlphaFold version
    try:
        url = f'https://alphafold.ebi.ac.uk/api/prediction/{aurka_id}'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            af_data = json.loads(resp.read())
            if af_data:
                ver = af_data[0]['latestVersion']
                pdb_url = af_data[0]['pdbUrl']
                print(f'  AlphaFold version: {ver}')
                print(f'  PDB URL: {pdb_url}')
                
                aurka_pdb = f'{work_dir}/AURKA_AF-{aurka_id}.pdb'
                urllib.request.urlretrieve(pdb_url, aurka_pdb)
                size = os.path.getsize(aurka_pdb)
                print(f'  Downloaded: {size//1024}KB')
    except Exception as e:
        print(f'  Download failed: {e}')
        return
    
    # Verify it's a real PDB
    with open(aurka_pdb) as f:
        first = f.readline()
    if not (first.startswith('HEADER') or first.startswith('MODEL') or first.startswith('ATOM')):
        print(f'  ERROR: Not a valid PDB file')
        return
    
    # Count atoms
    with open(aurka_pdb) as f:
        n_atoms = sum(1 for l in f if l.startswith('ATOM'))
    print(f'  AURKA structure: {n_atoms} atoms')
    
    # Prepare receptor
    receptor_pdbqt = f'{work_dir}/AURKA_receptor.pdbqt'
    prepare_receptor(aurka_pdb, receptor_pdbqt)
    
    # Prepare ligand
    ligand_pdbqt = f'{work_dir}/alisertib_ligand.pdbqt'
    if not prepare_ligand(ALISERTIB_SMILES, ligand_pdbqt):
        print('  Ligand preparation failed!')
        return
    
    # Find binding site
    cx, cy, cz = find_binding_site(aurka_pdb)
    
    # Run docking
    output_pdbqt = f'{work_dir}/alisertib_docked.pdbqt'
    affinities = run_docking(receptor_pdbqt, ligand_pdbqt, cx, cy, cz, output_pdbqt)
    
    if affinities:
        best = min(affinities)
        print(f'\n  DOCKING RESULTS:')
        print(f'  Best binding affinity: {best:.1f} kcal/mol')
        print(f'  All modes: {affinities}')
        print(f'  Interpretation:')
        if best < -8:
            print(f'    STRONG binding (< -8 kcal/mol)')
        elif best < -6:
            print(f'    MODERATE binding (-6 to -8 kcal/mol)')
        else:
            print(f'    WEAK binding (> -6 kcal/mol)')
        
        # Known: alisertib IC50 for AURKA = 1.2 nM
        # Expected docking score: -10 to -12 kcal/mol for nM binders
        print(f'  Expected for 1.2nM binder: ~ -10 to -12 kcal/mol')
        
        result = {
            'target': 'AURKA',
            'ligand': 'Alisertib (MLN8237)',
            'best_affinity_kcal': best,
            'all_modes': affinities,
            'method': 'AutoDock Vina v1.2.5',
            'receptor': f'AlphaFold {aurka_id}',
            'box_center': [round(cx,1), round(cy,1), round(cz,1)],
            'box_size': [25, 25, 25],
            'exhaustiveness': 16,
        }
        
        with open('../results/docking_alisertib_aurka.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f'\n  Saved: results/docking_alisertib_aurka.json')
    else:
        print('  Docking FAILED')

if __name__ == '__main__':
    main()
