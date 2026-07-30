"""
INTERCEPTA - Real Data Loaders v1.0
=====================================
Scripts to load GDSC, TCGA-PRAD, and scRNA-seq data into INTERCEPTA's pipeline.

Run these once your data is downloaded. Each function tells you exactly
what file to download and from where.

Author: Prasad Akula
Date: March 2026
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import os
import logging

logger = logging.getLogger("INTERCEPTA.DATALOADER")


# ═══════════════════════════════════════════════════════════════════════════
# GDSC DATA LOADER
# ═══════════════════════════════════════════════════════════════════════════

def load_gdsc_drug_sensitivity(filepath: str) -> pd.DataFrame:
    """
    Load GDSC2 fitted dose-response data.
    
    DOWNLOAD FROM: https://www.cancerrxgene.org/downloads/bulk_download
    FILE: GDSC2_fitted_dose_response_24Jul22.xlsx (or latest)
    DIRECT FTP: ftp://ftp.sanger.ac.uk/project/cancerrxgene/releases/
    
    Expected columns: COSMIC_ID, DRUG_NAME, DRUG_ID, LN_IC50, AUC, 
                      RMSE, MIN_CONC, MAX_CONC, DATASET
    
    Returns: DataFrame with COSMIC_ID as index, drug names as columns, 
             LN_IC50 as values.
    """
    logger.info(f"Loading GDSC drug sensitivity from: {filepath}")
    
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)
    
    # Identify key columns (GDSC format varies slightly between releases)
    id_col = next(c for c in df.columns if 'COSMIC' in c.upper() or 'CELL_LINE' in c.upper())
    drug_col = next(c for c in df.columns if 'DRUG_NAME' in c.upper())
    ic50_col = next(c for c in df.columns if 'LN_IC50' in c.upper() or 'IC50' in c.upper())
    
    # Pivot to cell_line x drug matrix
    ic50_matrix = df.pivot_table(
        index=id_col, columns=drug_col, values=ic50_col, aggfunc='median'
    )
    
    logger.info(f"  Loaded: {ic50_matrix.shape[0]} cell lines x "
                f"{ic50_matrix.shape[1]} drugs")
    logger.info(f"  Missing values: {ic50_matrix.isna().sum().sum()} "
                f"({ic50_matrix.isna().mean().mean():.1%})")
    
    return ic50_matrix


def load_gdsc_expression(filepath: str) -> pd.DataFrame:
    """
    Load GDSC cell line gene expression data.
    
    DOWNLOAD FROM: https://www.cancerrxgene.org/downloads/bulk_download
    FILE: Cell_line_RMA_proc_basalExp.txt (RMA normalized)
    OR: sanger_cell_line_rnaseq_tpm.csv (RNA-seq TPM)
    
    Returns: DataFrame with cell line IDs as index, gene symbols as columns.
    """
    logger.info(f"Loading GDSC expression from: {filepath}")
    
    if filepath.endswith('.txt'):
        df = pd.read_csv(filepath, sep='\t', index_col=0)
    else:
        df = pd.read_csv(filepath, index_col=0)
    
    # If genes are in rows, transpose
    if df.shape[0] > df.shape[1]:
        # Check if first column looks like gene names
        if any(g in df.index[:100] for g in ['MKI67', 'TP53', 'BRCA1', 'AR']):
            df = df.T
    
    logger.info(f"  Loaded: {df.shape[0]} cell lines x {df.shape[1]} genes")
    
    return df


def load_gdsc_cell_line_info(filepath: str) -> pd.DataFrame:
    """
    Load GDSC cell line annotation (tissue type, cancer type).
    
    DOWNLOAD FROM: https://www.cancerrxgene.org/downloads/bulk_download
    FILE: Cell_Lines_Details.xlsx
    
    Returns: DataFrame with COSMIC_ID as index, tissue columns.
    """
    logger.info(f"Loading cell line info from: {filepath}")
    
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)
    
    # Find tissue column
    tissue_col = next((c for c in df.columns 
                       if 'TISSUE' in c.upper() or 'SITE' in c.upper()), None)
    
    if tissue_col:
        logger.info(f"  Tissues: {df[tissue_col].nunique()} unique")
    
    return df


def prepare_gdsc_for_kaalcura(expression_path: str,
                                sensitivity_path: str,
                                cell_info_path: Optional[str] = None
                                ) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.Series]]:
    """
    Complete GDSC data preparation for KAALCURA training.
    
    Returns:
        expression_df: Cell line x gene expression matrix
        ic50_df: Cell line x drug IC50 matrix
        tissue_labels: Tissue type per cell line (for residualization)
    """
    expr = load_gdsc_expression(expression_path)
    ic50 = load_gdsc_drug_sensitivity(sensitivity_path)
    
    # Align cell lines between expression and sensitivity
    common = list(set(expr.index) & set(ic50.index))
    logger.info(f"  Common cell lines: {len(common)}")
    
    expr = expr.loc[common]
    ic50 = ic50.loc[common]
    
    # Load tissue labels if available
    tissues = None
    if cell_info_path:
        info = load_gdsc_cell_line_info(cell_info_path)
        # Try to match cell line IDs
        tissue_col = next((c for c in info.columns 
                          if 'TISSUE' in c.upper()), None)
        id_col = next((c for c in info.columns 
                      if 'COSMIC' in c.upper() or 'NAME' in c.upper()), None)
        if tissue_col and id_col:
            tissue_map = dict(zip(info[id_col], info[tissue_col]))
            tissues = pd.Series({cl: tissue_map.get(cl, 'unknown') 
                               for cl in common})
    
    return expr, ic50, tissues


# ═══════════════════════════════════════════════════════════════════════════
# TCGA-PRAD DATA LOADER
# ═══════════════════════════════════════════════════════════════════════════

def load_tcga_prad(expression_path: str, 
                   clinical_path: Optional[str] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Load TCGA-PRAD RNA-seq data.
    
    DOWNLOAD FROM: 
    Option A: https://portal.gdc.cancer.gov/projects/TCGA-PRAD
    Option B: https://xenabrowser.net/datapages/ (UCSC Xena - easier)
    Option C: curatedPCaData R package (pre-harmonized)
    
    For Xena: download TCGA-PRAD gene expression RNAseq (TOIL RSEM TPM)
    File: tcga_RSEM_gene_tpm.gz
    
    Returns:
        expression_df: Sample x gene expression matrix (log2 TPM)
        clinical_df: Clinical data (if provided)
    """
    logger.info(f"Loading TCGA-PRAD from: {expression_path}")
    
    expr = pd.read_csv(expression_path, sep='\t', index_col=0)
    
    # Filter to PRAD samples if pan-cancer file
    prad_cols = [c for c in expr.columns if 'TCGA' in c and 'PRAD' in c]
    if prad_cols:
        expr = expr[prad_cols]
    
    # Transpose if needed (genes should be columns)
    if expr.shape[0] > expr.shape[1]:
        expr = expr.T
    
    logger.info(f"  Loaded: {expr.shape[0]} samples x {expr.shape[1]} genes")
    
    clinical = None
    if clinical_path:
        clinical = pd.read_csv(clinical_path, sep='\t', index_col=0)
        logger.info(f"  Clinical: {clinical.shape[0]} patients")
    
    return expr, clinical


# ═══════════════════════════════════════════════════════════════════════════
# scRNA-seq DATA LOADER
# ═══════════════════════════════════════════════════════════════════════════

def load_scrna_h5ad(filepath: str) -> Dict:
    """
    Load scRNA-seq data from h5ad (AnnData) format.
    
    REQUIRES: pip install scanpy anndata
    
    DOWNLOAD FROM GEO:
    - GSE193337: 4 PCa samples (10X Chromium)
    - GSE206962: 3 CRPC samples
    - Deblois 2021: LNCaP parental + ENZ-resistant
    
    Process: 
    1. Download .h5ad or .mtx files from GEO
    2. If .mtx: use scanpy.read_10x_mtx()
    3. If .h5ad: use scanpy.read_h5ad()
    
    Returns dict with expression matrix and metadata.
    """
    try:
        import scanpy as sc
        adata = sc.read_h5ad(filepath)
        
        logger.info(f"  Loaded: {adata.n_obs} cells x {adata.n_vars} genes")
        
        return {
            "adata": adata,
            "n_cells": adata.n_obs,
            "n_genes": adata.n_vars,
            "obs_columns": list(adata.obs.columns),
            "has_velocity": "spliced" in adata.layers if hasattr(adata, 'layers') else False,
        }
    except ImportError:
        logger.warning("scanpy not installed. Install: pip install scanpy")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# QUICK-START GUIDE
# ═══════════════════════════════════════════════════════════════════════════

def print_quickstart():
    """Print the exact steps to get real data into INTERCEPTA."""
    guide = """
╔══════════════════════════════════════════════════════════════════════╗
║            INTERCEPTA - Real Data Quick-Start Guide                 ║
╚══════════════════════════════════════════════════════════════════════╝

STEP 1: Set up environment
──────────────────────────
    pip install numpy pandas scipy scikit-learn matplotlib networkx
    pip install scanpy scvelo cellrank anndata
    pip install openpyxl xlrd  # For reading GDSC Excel files
    
STEP 2: Download GDSC2 data (required for KAALCURA training)
─────────────────────────────────────────────────────────────
    Go to: https://www.cancerrxgene.org/downloads/bulk_download
    Download:
    (a) GDSC2_fitted_dose_response_[date].xlsx  (~50MB)
        → Drug IC50 values per cell line
    (b) Cell_line_RMA_proc_basalExp.txt.gz  (~200MB)
        → Gene expression per cell line
    (c) Cell_Lines_Details.xlsx  (~1MB)
        → Cell line tissue annotations

STEP 3: Download TCGA-PRAD (required for tissue residualization)
────────────────────────────────────────────────────────────────
    Go to: https://xenabrowser.net/datapages/
    Search: TCGA-PRAD
    Download: Gene expression RNAseq (TOIL RSEM tpm)
    
STEP 4: Run KAALCURA on real data
──────────────────────────────────
    from intercepta_kaalcura_v1 import KAALCURA
    from intercepta_data_loaders_v1 import prepare_gdsc_for_kaalcura
    
    expr, ic50, tissues = prepare_gdsc_for_kaalcura(
        expression_path="Cell_line_RMA_proc_basalExp.txt",
        sensitivity_path="GDSC2_fitted_dose_response.xlsx",
        cell_info_path="Cell_Lines_Details.xlsx"
    )
    
    kaalcura = KAALCURA(n_tissue_pcs=5)
    kaalcura.fit_reference(expr, tissue_labels=tissues)
    axes = kaalcura.compute_axes(expr)
    drug_results = kaalcura.train_drug_models(axes, ic50)
    
    # Check AUROC values — this is THE validation moment
    for drug, info in sorted(drug_results.items(), 
                              key=lambda x: x[1]['auroc'], reverse=True)[:20]:
        print(f"  {drug}: AUROC={info['auroc']:.3f}")

STEP 5: Download scRNA-seq (required for RNA velocity)
──────────────────────────────────────────────────────
    Go to: https://www.ncbi.nlm.nih.gov/geo/
    Search: GSE193337 (PCa scRNA-seq)
    Download: Supplementary .h5ad files
    
    # Process with scVelo for RNA velocity
    import scvelo as scv
    adata = scv.read("GSE193337_data.h5ad")
    scv.pp.filter_and_normalize(adata)
    scv.pp.moments(adata)
    scv.tl.velocity(adata, mode='dynamical')
    scv.tl.velocity_graph(adata)
    
STEP 6: Run full pipeline
──────────────────────────
    from intercepta_pipeline_v1 import InterceptaPipeline
    pipeline = InterceptaPipeline("mCRPC")
    results = pipeline.run_full_pipeline(n_patients=200)

═══════════════════════════════════════════════════════════════════════
Total download size: ~300MB
Total setup time: ~2 hours
Time to first real validation result: ~4 hours
═══════════════════════════════════════════════════════════════════════
"""
    print(guide)


if __name__ == "__main__":
    print_quickstart()
