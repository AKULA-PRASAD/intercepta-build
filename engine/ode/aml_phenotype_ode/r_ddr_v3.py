"""
r_ddr_axis.py  — VERSION 3
===========================
KAALCURA R_ddr axis. Proliferation-residualized HRR deficiency.

WHY v1 AND v2 FAILED:
  All DNA repair genes are cell-cycle regulated — they go up in dividing cells
  because dividing cells need more repair. Every HRR gene correlates with MKI67
  at r~0.5-0.6 in pan-cancer. No gene selection can escape this.

THE INSIGHT:
  HRD tumors do not have low HRR gene expression in absolute terms.
  They have LOW HRR gene expression RELATIVE TO their proliferation level.
  
  HRR-proficient high-proliferating tumor:
    High BRCA2, PALB2 (expected — dividing fast, needs repair)
    Normal BRCA2/proliferation ratio
    
  HRD high-proliferating tumor:
    High absolute expression (dividing fast)
    But BRCA2, PALB2 specifically silenced by promoter methylation
    ABNORMALLY LOW HRR relative to proliferation level  ← the signal

THE SOLUTION:
  Compute HRR gene expression residuals after regressing out R_prolif.
  Residuals are orthogonal to R_prolif by construction.
  Negative residuals = less HRR than proliferation predicts = HRD signal.
  
  R_ddr = sigmoid(-mean_residual)
  
  Negative residual (less HRR than expected) → high R_ddr score → HRD
  Wait — let's be careful with direction:
  
  We define R_ddr as HRR COMPETENCY:
    High R_ddr = HRR intact (proficient) = PARP resistant
    Low  R_ddr = HRR deficient = PARP sensitive
    
  Positive residual (more HRR than expected) = proficient = High R_ddr
  Negative residual (less HRR than expected) = deficient  = Low R_ddr
  
  R_ddr = sigmoid(mean_positive_residual) = sigmoid(+residual)

NOVELTY:
  No existing RNA-based HRD tool uses proliferation residualization.
  All existing tools confound HRD with quiescence.
  This approach specifically captures epigenetic HRR silencing.

Frozen: March 8, 2026
"""

import numpy as np
import pandas as pd
from scipy import stats

# ═══ FROZEN GENE SETS ═══

# HRR genes to residualize against proliferation
# Selected for: (1) known epigenetic silencing in HRD tumors
#               (2) strong proliferation coupling (so residuals are informative)
#               (3) direct HRR pathway membership
HRR_RESIDUAL_GENES = [
    'BRCA2',   # epigenetically silenced, direct RAD51 loader
    'PALB2',   # BRCA1-BRCA2 bridge, methylated in HRD
    'BRIP1',   # FANCJ, biallelic silencing = HRD
    'FANCA',   # FA pathway, specifically suppressed in HRD
    'FANCD2',  # FA core, epigenetically regulated
    'RAD51C',  # RAD51 paralog, promoter methylation in sporadic HRD
]

# Cell-cycle reference genes (used to compute expected HRR level)
# These are the most proliferation-coupled, used as the regression predictor
# Note: we use Z_prolif from R_prolif computation, not raw gene expression
PROLIFERATION_REF = ['MKI67', 'PCNA', 'MCM2']  # for reference only

PROBE_MAP_DDR = {
    '209186_at':   'BRCA2',
    '219530_at':   'PALB2',
    '204548_at':   'BRIP1',
    '209905_at':   'FANCA',
    '205569_at':   'FANCD2',
    '219528_at':   'RAD51C',
}

ENTREZ_MAP_DDR = {
    '675':   'BRCA2',
    '79728': 'PALB2',
    '83990': 'BRIP1',
    '2175':  'FANCA',
    '2177':  'FANCD2',
    '5889':  'RAD51C',
}


def zscore(s):
    mu, sd = s.mean(), s.std()
    return (s - mu) / sd if sd > 1e-10 else pd.Series(0.0, index=s.index)


def compute_r_ddr(expr_df, r_prolif=None):
    """
    Compute R_ddr — proliferation-residualized HRR deficiency axis.

    Parameters
    ----------
    expr_df  : pd.DataFrame — genes as rows, samples as columns
    r_prolif : pd.Series (optional) — pre-computed R_prolif scores
               If None, computed internally from expr_df

    Returns
    -------
    pd.Series — R_ddr scores (0-1) per sample
      High (~0.8-1.0) = HRR competent (proficient), PARP inhibitor RESISTANT
      Low  (~0.0-0.3) = HRR deficient, PARP inhibitor SENSITIVE

    Method
    ------
    1. For each HRR gene: z-score within dataset
    2. Regress each z-scored HRR gene on R_prolif score
    3. Take residuals (proliferation-independent HRR signal)
    4. Average residuals across genes
    5. Sigmoid transform
    """
    # Get R_prolif if not provided
    if r_prolif is None:
        from axis_definitions import compute_r_prolif
        r_prolif = compute_r_prolif(expr_df)

    hrr_found = [g for g in HRR_RESIDUAL_GENES if g in expr_df.index]

    if len(hrr_found) < 3:
        raise ValueError(
            f"Too few HRR_RESIDUAL_GENES found ({len(hrr_found)}): {hrr_found}. "
            f"Need at least 3."
        )

    # Z-score R_prolif for use as regressor
    rp_z = zscore(r_prolif)

    # For each HRR gene: compute residual after regressing on R_prolif
    residuals = []
    for gene in hrr_found:
        gene_z = zscore(expr_df.loc[gene])

        # Linear regression: gene ~ R_prolif
        # residual = gene - (slope * R_prolif + intercept)
        slope, intercept, _, _, _ = stats.linregress(rp_z, gene_z)
        expected = slope * rp_z + intercept
        residual = gene_z - expected
        residuals.append(residual)

    # Average residuals across HRR genes
    mean_residual = pd.concat(residuals, axis=1).mean(axis=1)

    # Positive residual = more HRR than proliferation predicts = proficient
    # Negative residual = less HRR than proliferation predicts = deficient
    # R_ddr = sigmoid(mean_residual): high = proficient, low = deficient
    return 1.0 / (1.0 + np.exp(-mean_residual))


def get_gene_counts(expr_df):
    found   = [g for g in HRR_RESIDUAL_GENES if g in     expr_df.index]
    missing = [g for g in HRR_RESIDUAL_GENES if g not in expr_df.index]
    return {'HRR_RESIDUAL': found}, {'HRR_RESIDUAL': missing}


if __name__ == '__main__':
    print("R_ddr v3 — Proliferation-Residualized HRR Deficiency")
    print(f"HRR_RESIDUAL_GENES: {HRR_RESIDUAL_GENES}")
    print(f"Formula: sigmoid(mean_residual[HRR ~ R_prolif])")
    print(f"High = HRR proficient. Low = HRD = PARP sensitive.")
    print(f"Orthogonal to R_prolif by construction.")
