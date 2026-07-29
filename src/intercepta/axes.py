"""
01_axis_definitions.py
=======================
Core KAALCURA axis computation functions.
These are FROZEN — never modified after initial definition.

R_prolif: Proliferation axis (15 genes, 4 modules)
R_emt: EMT/dedifferentiation axis (18 genes, 3 modules)
R_immune: Immune activity axis (23 genes, 4 modules) [Tier 2, not in manuscript]
"""
import numpy as np
import pandas as pd

# ═══ FROZEN GENE SETS ═══

# R_prolif components
CELL_CYCLE = ['PCNA', 'CCNB1', 'CDK1', 'TOP2A', 'AURKA', 'CDC20', 'UBE2C', 'MCM2', 'MCM6']
REPLICATION = ['MCM2', 'MCM6', 'RPA1', 'FEN1', 'TYMS']
GROWTH = ['MYC']
QUIESCENCE = ['CDKN1A', 'CDKN1B']

# R_emt components (stromal-clean, critic-approved)
MESENCHYMAL = ['VIM', 'CDH2', 'FN1', 'SNAI2', 'TWIST1', 'ZEB1', 'ZEB2']
INVASION = ['MMP2', 'MMP9', 'ITGA5', 'LAMC2']
EPITHELIAL = ['CDH1', 'EPCAM', 'KRT18', 'KRT19', 'CLDN3', 'CLDN4', 'CLDN7']

# R_immune components (Tier 2 — biologically validated, clinically deferred)
CYTOTOXIC = ['CD8A', 'CD8B', 'GZMA', 'GZMB', 'PRF1', 'NKG7', 'GNLY', 'IFNG']
IFN_RESPONSE = ['STAT1', 'IRF1', 'CXCL9', 'CXCL10', 'IDO1', 'HLA-DRA']
ANTIGEN_PRESENT = ['HLA-A', 'HLA-B', 'HLA-C', 'B2M', 'TAP1', 'TAP2']
IMMUNE_EXCLUSION = ['TGFB1', 'VEGFA', 'IL10']

# Affymetrix probe-to-gene mapping (HG-U133A / HG-U133 Plus 2)
PROBE_MAP = {
    '201202_at': 'PCNA', '214710_s_at': 'CCNB1', '203213_at': 'CDK1',
    '201292_at': 'TOP2A', '204092_s_at': 'AURKA', '202870_s_at': 'CDC20',
    '202954_at': 'UBE2C', '202107_s_at': 'MCM2', '201930_at': 'MCM6',
    '201476_s_at': 'RPA1', '204767_s_at': 'FEN1', '202589_at': 'TYMS',
    '202431_s_at': 'MYC', '202284_s_at': 'CDKN1A', '209461_x_at': 'CDKN1B',
    '201426_s_at': 'VIM', '203440_at': 'CDH2', '210495_x_at': 'FN1',
    '203035_s_at': 'SNAI2', '213943_at': 'TWIST1', '212764_at': 'ZEB1',
    '203603_s_at': 'ZEB2', '201069_at': 'MMP2', '203936_s_at': 'MMP9',
    '201389_at': 'ITGA5', '202267_at': 'LAMC2', '201131_s_at': 'CDH1',
    '201839_s_at': 'EPCAM', '201596_x_at': 'KRT18', '201650_at': 'KRT19',
    '203953_s_at': 'CLDN3', '201428_at': 'CLDN4', '202790_at': 'CLDN7',
    '212022_s_at': 'MKI67', '202095_s_at': 'BIRC5', '201710_at': 'MYBL2',
    # Persister/DTP genes (Root 5)
    '201235_s_at': 'LDHA',    '201251_at':   'PKM',
    '200989_at':   'HIF1A',   '202499_s_at': 'SLC2A1',
    '201792_at':   'HSPA5',   '209383_at':   'DDIT3',
    '201111_at':   'ATF4',    '200965_s_at': 'XBP1',
    '201384_at':   'EIF2AK3', '203685_at':   'BCL2',
    '200797_s_at': 'BCL2L1',  '200706_s_at': 'MCL1',
    '209835_at':   'ALDH1A1', '212014_x_at': 'CD44',
    '204468_s_at': 'PROM1',
}

# Entrez ID mapping (for RNA-seq datasets like GSE91061)
ENTREZ_MAP = {
    '5111': 'PCNA', '891': 'CCNB1', '983': 'CDK1', '7153': 'TOP2A',
    '6790': 'AURKA', '990': 'CDC20', '9133': 'UBE2C', '4171': 'MCM2',
    '4175': 'MCM6', '6117': 'RPA1', '2237': 'FEN1', '7298': 'TYMS',
    '4609': 'MYC', '1029': 'CDKN1A', '1030': 'CDKN1B',
    '7431': 'VIM', '1000': 'CDH2', '2335': 'FN1', '6615': 'SNAI1',
    '6591': 'SNAI2', '7291': 'TWIST1', '6935': 'ZEB1', '9839': 'ZEB2',
    '4313': 'MMP2', '4318': 'MMP9', '3678': 'ITGA5', '3918': 'LAMC2',
    '999': 'CDH1', '4072': 'EPCAM', '3875': 'KRT18', '3880': 'KRT19',
    '1365': 'CLDN3', '1364': 'CLDN4', '1366': 'CLDN7',
    '925': 'CD8A', '926': 'CD8B', '3001': 'GZMA', '3002': 'GZMB',
    '5551': 'PRF1', '4818': 'NKG7', '10578': 'GNLY', '3458': 'IFNG',
    '6772': 'STAT1', '3659': 'IRF1', '4283': 'CXCL9', '3627': 'CXCL10',
    '3620': 'IDO1', '3122': 'HLA-DRA',
    '3105': 'HLA-A', '3106': 'HLA-B', '3107': 'HLA-C', '567': 'B2M',
    '6890': 'TAP1', '6891': 'TAP2',
    '7040': 'TGFB1', '7422': 'VEGFA', '3586': 'IL10', '29126': 'CD274',
}


# ═══ CORE FUNCTIONS ═══

def zscore(s):
    """Z-score a pandas Series across samples (within dataset)."""
    mu, sd = s.mean(), s.std()
    return (s - mu) / sd if sd > 1e-10 else pd.Series(0.0, index=s.index)


def compute_r_prolif(expr_df):
    """
    Compute R_prolif from gene expression matrix.
    
    Parameters
    ----------
    expr_df : pd.DataFrame — genes as rows, samples as columns
    
    Returns
    -------
    pd.Series — R_prolif score (0-1) per sample
    """
    cc = [g for g in CELL_CYCLE if g in expr_df.index]
    rp = [g for g in REPLICATION if g in expr_df.index]
    gr = [g for g in GROWTH if g in expr_df.index]
    qu = [g for g in QUIESCENCE if g in expr_df.index]

    Z_cc = zscore(expr_df.loc[cc].mean(axis=0))
    Z_rp = zscore(expr_df.loc[rp].mean(axis=0))
    Z_gr = zscore(expr_df.loc[gr].mean(axis=0))
    Z_qu = zscore(expr_df.loc[qu].mean(axis=0))

    # Note: Z_gr appears twice (growth module weighted 2x by design)
    S = Z_gr + Z_cc + Z_rp + Z_gr - Z_qu
    return 1.0 / (1.0 + np.exp(-S))


def compute_r_emt(expr_df):
    """Compute R_emt from gene expression matrix."""
    mes = [g for g in MESENCHYMAL if g in expr_df.index]
    inv = [g for g in INVASION if g in expr_df.index]
    epi = [g for g in EPITHELIAL if g in expr_df.index]

    S = zscore(expr_df.loc[mes].mean(0)) + zscore(expr_df.loc[inv].mean(0)) - zscore(expr_df.loc[epi].mean(0))
    return 1.0 / (1.0 + np.exp(-S))


def compute_r_immune(expr_df):
    """Compute R_immune from gene expression matrix. (Tier 2 — not in manuscript)"""
    cy = [g for g in CYTOTOXIC if g in expr_df.index]
    ifn = [g for g in IFN_RESPONSE if g in expr_df.index]
    ag = [g for g in ANTIGEN_PRESENT if g in expr_df.index]
    ex = [g for g in IMMUNE_EXCLUSION if g in expr_df.index]

    S = zscore(expr_df.loc[cy].mean(0)) + zscore(expr_df.loc[ifn].mean(0)) + zscore(expr_df.loc[ag].mean(0)) - zscore(expr_df.loc[ex].mean(0))
    return 1.0 / (1.0 + np.exp(-S))


def map_probes_to_genes(expr_df, probe_map=None):
    """Convert probe-level expression to gene-level by averaging probes per gene."""
    if probe_map is None:
        probe_map = PROBE_MAP
    found = {p: g for p, g in probe_map.items() if p in expr_df.index}
    gene_expr = {}
    for probe, gene in found.items():
        if gene not in gene_expr:
            gene_expr[gene] = []
        gene_expr[gene].append(expr_df.loc[probe])
    return pd.DataFrame({g: pd.concat(probes, axis=1).mean(axis=1) 
                         for g, probes in gene_expr.items()}).T


def load_geo_matrix(filepath):
    """Parse GEO series matrix file. Returns (gsm_ids, clinical_dict, expression_df)."""
    import gzip
    gsm_ids = []
    char_rows = []
    expr_lines = []
    data_started = False

    with gzip.open(filepath, 'rt') as f:
        for line in f:
            line = line.strip()
            if line.startswith('!Sample_geo_accession'):
                gsm_ids = [x.strip('"') for x in line.split('\t')[1:]]
            elif line.startswith('!Sample_characteristics_ch1'):
                char_rows.append([x.strip('"') for x in line.split('\t')[1:]])
            elif line.startswith('!series_matrix_table_begin'):
                data_started = True
            elif line.startswith('!series_matrix_table_end'):
                data_started = False
            elif data_started:
                expr_lines.append(line)

    # Clinical
    clinical = {}
    for i, gsm in enumerate(gsm_ids):
        clinical[gsm] = {}
        for row in char_rows:
            if i < len(row) and ':' in row[i]:
                k, v = row[i].split(':', 1)
                clinical[gsm][k.strip()] = v.strip()

    # Expression
    header = [x.strip('"') for x in expr_lines[0].split('\t')]
    probe_ids = []
    expr_data = []
    for line in expr_lines[1:]:
        parts = line.split('\t')
        pid = parts[0].strip('"')
        vals = []
        for v in parts[1:]:
            try:
                vals.append(float(v.strip('"')))
            except:
                vals.append(np.nan)
        probe_ids.append(pid)
        expr_data.append(vals)

    expr = pd.DataFrame(expr_data, index=probe_ids, columns=header[1:])
    return gsm_ids, clinical, expr


if __name__ == '__main__':
    print("KAALCURA Axis Definitions")
    print(f"  R_prolif: {len(CELL_CYCLE)+len(REPLICATION)+len(GROWTH)+len(QUIESCENCE)} genes")
    print(f"  R_emt:    {len(MESENCHYMAL)+len(INVASION)+len(EPITHELIAL)} genes")
    print(f"  R_immune: {len(CYTOTOXIC)+len(IFN_RESPONSE)+len(ANTIGEN_PRESENT)+len(IMMUNE_EXCLUSION)} genes")
    print(f"  Probe map: {len(PROBE_MAP)} probes")
    print(f"  Entrez map: {len(ENTREZ_MAP)} IDs")
