"""
r_ddr_axis.py  — VERSION 2
===========================
KAALCURA R_ddr axis. Structural HRR genes only — cell-cycle independent.

v1 PROBLEM: RAD51/BRCA1/BRCA2 are cell-cycle regulated. In pan-cancer they
correlate with proliferation, making R_ddr measure quiescence not HRD.

v2 FIX: Use only structural scaffold genes specifically silenced in HRD tumors
regardless of cell cycle state. PALB2, RAD51C, RAD51D are epigenetically
suppressed in HRD tumors but NOT regulated by cell cycle phase.

High R_ddr (~1.0) = HRR intact = PARP inhibitor RESISTANT
Low  R_ddr (~0.0) = HRR deficient = PARP inhibitor SENSITIVE

Therapy domain: PARP inhibitors, platinum chemotherapy
Frozen: March 8, 2026
"""

import numpy as np
import pandas as pd

# ═══ FROZEN GENE SETS — DO NOT MODIFY ═══

# Structural HRR scaffold genes — specifically downregulated in HRD tumors
# via promoter methylation / epigenetic silencing / pathway suppression
# NOT cell-cycle regulated (key distinction from RAD51/BRCA1/BRCA2)
HRR_STRUCTURAL = [
    'PALB2',   # BRCA1-BRCA2 bridge, silenced in ~20% BRCA-wt HRD tumors
    'RAD51C',  # RAD51 paralog, promoter methylation in sporadic HRD
    'RAD51D',  # RAD51 paralog, germline/somatic mutations cause HRD
    'BRIP1',   # FANCJ helicase, biallelic = Fanconi anemia, monoallelic = HRD
    'FANCA',   # FA pathway upstream, not cell-cycle driven
    'FANCD2',  # FA pathway core, suppressed in HRD independent of cycling
    'BRCA2',   # Less cell-cycle variable than BRCA1, direct RAD51 loader
]

# NHEJ backup pathway genes — upregulated when HRR is absent
# Only the two with cleanest HRD-specific signal (PRKDC excluded, wrong direction)
NHEJ_COMPENSATORY = [
    'LIG4',   # NHEJ ligation, upregulated when cells rely on NHEJ
    'XRCC6',  # Ku70, NHEJ end-binding initiation
]

# Affymetrix probe mappings (HG-U133A / HG-U133 Plus 2.0)
PROBE_MAP_DDR = {
    '219530_at':   'PALB2',
    '219528_at':   'RAD51C',
    '209825_s_at': 'RAD51D',
    '204548_at':   'BRIP1',
    '209905_at':   'FANCA',
    '205569_at':   'FANCD2',
    '209186_at':   'BRCA2',
    '204066_at':   'LIG4',
    '201205_at':   'XRCC6',
}

# Entrez ID mapping for RNA-seq
ENTREZ_MAP_DDR = {
    '79728': 'PALB2', '5889': 'RAD51C', '5892': 'RAD51D',
    '83990': 'BRIP1', '2175': 'FANCA',  '2177': 'FANCD2',
    '675':   'BRCA2', '3981': 'LIG4',   '2547': 'XRCC6',
}


def zscore(s):
    mu, sd = s.mean(), s.std()
    return (s - mu) / sd if sd > 1e-10 else pd.Series(0.0, index=s.index)


def compute_r_ddr(expr_df):
    """
    Compute R_ddr. genes as rows, samples as columns.
    Returns pd.Series of R_ddr scores (0-1) per sample.
    High = HRR proficient. Low = HRR deficient = PARP sensitive.
    """
    hrr  = [g for g in HRR_STRUCTURAL    if g in expr_df.index]
    nhej = [g for g in NHEJ_COMPENSATORY if g in expr_df.index]

    if len(hrr) < 3:
        raise ValueError(f"Too few HRR_STRUCTURAL genes found ({len(hrr)}): {hrr}")

    Z_hrr  = zscore(expr_df.loc[hrr].mean(axis=0))
    Z_nhej = zscore(expr_df.loc[nhej].mean(axis=0)) if nhej else pd.Series(0.0, index=expr_df.columns)

    S = Z_hrr - Z_nhej
    return 1.0 / (1.0 + np.exp(-S))


def get_gene_counts(expr_df):
    found   = {k: [g for g in v if g in expr_df.index]     for k, v in [('HRR_STRUCTURAL', HRR_STRUCTURAL), ('NHEJ_COMPENSATORY', NHEJ_COMPENSATORY)]}
    missing = {k: [g for g in v if g not in expr_df.index] for k, v in [('HRR_STRUCTURAL', HRR_STRUCTURAL), ('NHEJ_COMPENSATORY', NHEJ_COMPENSATORY)]}
    return found, missing


if __name__ == '__main__':
    print(f"R_ddr v2: {len(HRR_STRUCTURAL)} HRR_STRUCTURAL + {len(NHEJ_COMPENSATORY)} NHEJ_COMPENSATORY genes")
    print(f"Formula: sigmoid(Z_hrr_structural - Z_nhej_compensatory)")
