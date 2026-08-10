#!/usr/bin/env python
"""AFFINITY2 step 2 — generate Boltz-2 co-folding YAMLs (protein sequence + ligand SMILES + affinity head)
for every benchmark compound. One YAML per compound, grouped per target. Deterministic. Run locally (no GPU);
the YAMLs are copied to Explorer and run with `boltz predict` (see HPC_RELAY.md)."""
import os, glob, csv

HERE = os.path.dirname(os.path.abspath(__file__))
BM = os.path.join(HERE, "benchmark"); REC = os.path.join(BM, "receptors")
YAMLS = os.path.join(BM, "yamls"); os.makedirs(YAMLS, exist_ok=True)
PDB = {"ALDH1": "4wp7", "PKM2": "3gqy", "FEN1": "5fv7"}

def load_seq(pdb):
    seq = []
    with open(os.path.join(REC, f"{pdb}.fasta")) as f:
        for line in f:
            if line.startswith(">"):
                if seq: break          # first sequence (monomer) only
                continue
            seq.append(line.strip())
    return "".join(seq)

def yaml_for(seq, smiles):
    # escape nothing needed; SMILES has no YAML-special leading chars we use quotes to be safe
    return (f"version: 1\nsequences:\n  - protein:\n      id: A\n      sequence: {seq}\n"
            f"  - ligand:\n      id: L\n      smiles: '{smiles}'\nproperties:\n  - affinity:\n      binder: L\n")

def main():
    total = 0
    for tgt, pdb in PDB.items():
        seq = load_seq(pdb); od = os.path.join(YAMLS, tgt); os.makedirs(od, exist_ok=True)
        n = 0
        with open(os.path.join(BM, f"{tgt}_compounds.csv")) as f:
            for row in csv.DictReader(f):
                with open(os.path.join(od, f"{row['cmpd_id']}.yaml"), "w") as y:
                    y.write(yaml_for(seq, row["smiles"]))
                n += 1
        print(f"{tgt} ({pdb}, {len(seq)}aa): {n} YAMLs -> {od}")
        total += n
    print("total YAMLs:", total)

if __name__ == "__main__":
    main()
