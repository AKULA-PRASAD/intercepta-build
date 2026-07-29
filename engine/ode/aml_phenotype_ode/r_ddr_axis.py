"""
r_ddr_axis.py
=============
KAALCURA R_ddr axis — DNA Damage Repair axis.

FROZEN: gene sets, weights, and formula defined here are never modified
after initial definition. All validation uses this exact definition.

Biological logic:
  High R_ddr (~1.0) = HRR pathway active = PARP inhibitor RESISTANT
  Low  R_ddr (~0.0) = HRR pathway deficient = PARP inhibitor SENSITIVE

Therapy domain: PARP inhibitors, platinum chemotherapy
Prediction direction: LOW R_ddr = sensitivity (opposite to R_prolif)

This creates a two-axis state space:
  R_prolif HIGH + R_ddr LOW  → chemotherapy AND PARP inhibitor benefit
  R_prolif HIGH + R_ddr HIGH → chemotherapy benefit, PARP resistant
  R_prolif LOW  + R_ddr LOW  → PARP inhibitor benefit, chemo-resistant
  R_prolif LOW  + R_ddr HIGH → neither (most therapy-resistant state)
"""

import numpy as np
import pandas as pd

# ═══════════════════════════════════════════════════════════
# FROZEN GENE SETS — DO NOT MODIFY AFTER THIS DATE
# Definition date: March 8, 2026
# ═══════════════════════════════════════════════════════════

# HRR_ACTIVE: genes whose expression indicates active, functional HRR
# High expression = repair machinery is present and working
HRR_ACTIVE = [
    'RAD51',   # core recombinase — the most direct marker of HRR activity
    'BRCA1',   # DSB signaling and end resection
    'BRCA2',   # RAD51 mediator, strand invasion
    'PALB2',   # BRCA1-BRCA2 bridge
    'BRIP1',   # FANCJ helicase, resolves stalled fork structures
    'RAD51C',  # RAD51 paralog, Holliday junction resolution
    'RAD51D',  # RAD51 paralog, forms RAD51C/D complex
    'FANCA',   # Fanconi anemia upstream, fork protection
    'FANCD2',  # FA pathway core, monoubiquitinated at stalled forks
]

# REPLICATION_STRESS: genes upregulated when HRR is failing
# High expression = replication stress is unresolved = repair is broken
REPLICATION_STRESS = [
    'RPA2',    # ssDNA accumulation at stalled forks
    'CHEK1',   # ATR-activated, chronic replication stress marker
    'H2AFX',   # gamma-H2AX pathway, unrepaired DSBs
]

# NHEJ_BACKUP: genes upregulated when NHEJ is compensating for HRR loss
# High expression = cell is using error-prone backup = HRR is deficient
NHEJ_BACKUP = [
    'PRKDC',  # DNA-PKcs, NHEJ catalytic subunit
    'LIG4',   # NHEJ ligation
    'XRCC6',  # Ku70, NHEJ end-binding
]

# Affymetrix probe mappings for HG-U133A/Plus2 arrays
PROBE_MAP_DDR = {
    # HRR_ACTIVE probes
    '205024_at':    'RAD51',
    '204531_s_at':  'BRCA1',
    '209186_at':    'BRCA2',
    '219530_at':    'PALB2',
    '204548_at':    'BRIP1',
    '219528_at':    'RAD51C',
    '209825_s_at':  'RAD51D',
    '209905_at':    'FANCA',
    '205569_at':    'FANCD2',
    # REPLICATION_STRESS probes
    '201435_s_at':  'RPA2',
    '203444_s_at':  'CHEK1',
    '201447_s_at':  'H2AFX',
    # NHEJ_BACKUP probes
    '201551_s_at':  'PRKDC',
    '204066_at':    'LIG4',
    '201205_at':    'XRCC6',
}

# Entrez ID mapping for RNA-seq datasets
ENTREZ_MAP_DDR = {
    '5888':  'RAD51',
    '672':   'BRCA1',
    '675':   'BRCA2',
    '79728': 'PALB2',
    '83990': 'BRIP1',
    '5889':  'RAD51C',
    '5892':  'RAD51D',
    '2175':  'FANCA',
    '2177':  'FANCD2',
    '6117':  'RPA2',
    '1111':  'CHEK1',
    '3014':  'H2AFX',
    '5591':  'PRKDC',
    '3981':  'LIG4',
    '2547':  'XRCC6',
}


def zscore(s):
    """Z-score a pandas Series within dataset."""
    mu, sd = s.mean(), s.std()
    return (s - mu) / sd if sd > 1e-10 else pd.Series(0.0, index=s.index)


def compute_r_ddr(expr_df):
    """
    Compute R_ddr from gene expression matrix.

    Parameters
    ----------
    expr_df : pd.DataFrame — genes as rows, samples as columns

    Returns
    -------
    pd.Series — R_ddr score (0-1) per sample

    Interpretation
    --------------
    High (~0.8-1.0) : HRR active, PARP inhibitor resistant
    Low  (~0.0-0.3) : HRR deficient, PARP inhibitor sensitive
    """
    hrr   = [g for g in HRR_ACTIVE         if g in expr_df.index]
    rs    = [g for g in REPLICATION_STRESS if g in expr_df.index]
    nhej  = [g for g in NHEJ_BACKUP        if g in expr_df.index]

    if len(hrr) < 3:
        raise ValueError(f"Too few HRR_ACTIVE genes found: {hrr}. "
                         f"Need at least 3. Check gene name format.")

    Z_hrr  = zscore(expr_df.loc[hrr].mean(axis=0))
    Z_rs   = zscore(expr_df.loc[rs].mean(axis=0))   if rs   else pd.Series(0.0, index=expr_df.columns)
    Z_nhej = zscore(expr_df.loc[nhej].mean(axis=0)) if nhej else pd.Series(0.0, index=expr_df.columns)

    S = Z_hrr - Z_rs - Z_nhej
    return 1.0 / (1.0 + np.exp(-S))


def get_gene_counts(expr_df):
    """Report which genes were found vs missing."""
    found = {
        'HRR_ACTIVE':         [g for g in HRR_ACTIVE         if g in expr_df.index],
        'REPLICATION_STRESS': [g for g in REPLICATION_STRESS if g in expr_df.index],
        'NHEJ_BACKUP':        [g for g in NHEJ_BACKUP         if g in expr_df.index],
    }
    missing = {
        'HRR_ACTIVE':         [g for g in HRR_ACTIVE         if g not in expr_df.index],
        'REPLICATION_STRESS': [g for g in REPLICATION_STRESS if g not in expr_df.index],
        'NHEJ_BACKUP':        [g for g in NHEJ_BACKUP         if g not in expr_df.index],
    }
    return found, missing


if __name__ == '__main__':
    print("R_ddr Axis Definition")
    print(f"  HRR_ACTIVE ({len(HRR_ACTIVE)} genes):         {HRR_ACTIVE}")
    print(f"  REPLICATION_STRESS ({len(REPLICATION_STRESS)} genes): {REPLICATION_STRESS}")
    print(f"  NHEJ_BACKUP ({len(NHEJ_BACKUP)} genes):       {NHEJ_BACKUP}")
    print(f"  Total unique genes: {len(set(HRR_ACTIVE + REPLICATION_STRESS + NHEJ_BACKUP))}")
    print(f"\n  Formula: R_ddr = sigmoid(Z_hrr_active - Z_replication_stress - Z_nhej_backup)")
    print(f"  Therapy domain: PARP inhibitors, platinum chemotherapy")
    print(f"  High R_ddr = HRR intact = PARP resistant")
    print(f"  Low  R_ddr = HRR deficient = PARP sensitive")
