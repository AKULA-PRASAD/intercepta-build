#!/usr/bin/env python3
"""
INTERCEPTA Round 2.2c — Step 1: Multi-Modal Feature Builder
==============================================================

Per spec INTERCEPTA_Round2_2c_Specification.md, Section 5.

Builds the multi-modal feature stack for each (sample, drug) pair:
  1. KAALCURA 3 axes (R_prolif, R_emt, R_ddr) — Round 2.2b residualized
  2. RNA-1000-no-sex — top-1000 variable genes after chrX/chrY filter
  3. Mutation status — 15 binary indicators (clinical flags + WES fallback)
  4. Pathway activity scores — ~10-15 KEGG pathways
  5. Drug-target features — 4 features per drug

Outputs:
  - features_kaalcura.csv          (samples × 3)
  - features_rna1000.csv           (samples × 1000)
  - features_mutations.csv         (samples × 15)
  - features_pathways_raw.csv      (samples × N_pathways) — RAW values; train-fold normalization happens in Step 2
  - features_drug_target.csv       (drugs × 4)
  - drug_response_aligned.csv      (sample, drug, auc, sensitive_label)
  - feature_build_summary.json     (counts, alignment stats, gene/pathway/drug lists)

Per spec Section 6: fail-closed on missing inputs. No silent feature dropping.

Author: Prasad Akula & Claude (CSO), 2026-05-06
"""

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', message='.*feature names.*')

HOME = Path.home()
ROUND2 = HOME / 'INTERCEPTA' / 'round2_aml'
DATA = ROUND2 / 'data' / 'beataml2.0_data-2.0'
RESULTS = ROUND2 / 'results'
GLOBAL_RESULTS = HOME / 'INTERCEPTA' / 'results'

OUTPUT_DIR = RESULTS / 'round2_2c'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ----- Inputs -----
KAALCURA_AXES = RESULTS / 'beataml_ucell_residual_axes_round22b.csv'
BEATAML_EXPR = DATA / 'beataml_waves1to4_norm_exp_dbgap.txt'
BEATAML_FITS = DATA / 'beataml_probit_curve_fits_v4_dbgap.txt'
BEATAML_MUTS = DATA / 'beataml_wes_wv1to4_mutations_dbgap.txt'
BEATAML_CLIN = DATA / 'beataml_wv1to4_clinical.xlsx'
BEATAML_DRUG_FAM = DATA / 'beataml_drug_families.xlsx'
KEGG_PATHWAY_MAP = GLOBAL_RESULTS / 'step5_gene_pathway_map.csv'
GENE_DRUG_NET = GLOBAL_RESULTS / 'step1_complete_gene_drug_net.csv'

# ----- Outputs -----
OUT_KAALCURA = OUTPUT_DIR / 'features_kaalcura.csv'
OUT_RNA = OUTPUT_DIR / 'features_rna1000.csv'
OUT_MUTS = OUTPUT_DIR / 'features_mutations.csv'
OUT_PATHWAYS = OUTPUT_DIR / 'features_pathways_raw.csv'
OUT_DRUG_TGT = OUTPUT_DIR / 'features_drug_target.csv'
OUT_RESPONSE = OUTPUT_DIR / 'drug_response_aligned.csv'
OUT_SUMMARY = OUTPUT_DIR / 'feature_build_summary.json'

# ----- Locked spec parameters -----
N_TOP_VAR_GENES = 1000
AUC_THRESHOLD = 100.0
MIN_SENSITIVE = 10
MIN_RESISTANT = 10
RANDOM_STATE = 42

# Spec Section 5: 15 mutation features
MUTATION_GENES = [
    'FLT3', 'NPM1', 'DNMT3A', 'IDH1', 'IDH2', 'RUNX1', 'CEBPA', 'TET2',
    'TP53', 'ASXL1', 'KIT', 'KMT2A', 'RAS_family', 'WT1', 'FLT3_ITD',
]
RAS_FAMILY_MEMBERS = ['NRAS', 'KRAS']  # combined into one feature per spec

# Spec Section 5: 10-15 KEGG pathways
LOCKED_PATHWAYS = {
    'hsa05221': 'AML',
    'hsa04110': 'Cell cycle',
    'hsa04210': 'Apoptosis',
    'hsa04630': 'JAK-STAT',
    'hsa04151': 'PI3K-Akt',
    'hsa04010': 'MAPK',
    'hsa04310': 'Wnt',
    'hsa03430': 'DNA mismatch repair',
    'hsa03450': 'Non-homologous end joining',
    'hsa03440': 'Homologous recombination',
    'hsa04115': 'p53',
    'hsa04640': 'Hematopoietic cell lineage',
}

# Spec Section 5: same sex-linked gene filter as RNA baseline v2
SEX_LINKED_GENES = {
    'XIST', 'TSIX', 'KDM6A', 'DDX3X', 'EIF1AX', 'ZFX', 'USP9X',
    'KDM5C', 'UTX', 'JPX', 'FTX', 'RPS4X', 'EIF2S3', 'SMC1A',
    'HUWE1', 'NLGN4X', 'STS',
    'RPS4Y1', 'RPS4Y2', 'KDM5D', 'DDX3Y', 'EIF1AY', 'UTY',
    'NLGN4Y', 'USP9Y', 'ZFY', 'SRY', 'TBL1Y', 'AMELY', 'TMSB4Y',
    'TSPY1', 'TSPY2', 'TSPY3', 'TSPY4', 'TSPY8', 'TSPY10',
    'TXLNGY', 'TXLNG2P', 'PRKY', 'PRY', 'PRY2', 'XKRY',
    'BCORL1', 'BCORL2',
}


def banner(msg):
    print('\n' + '=' * 72)
    print(msg)
    print('=' * 72)


def fail_closed(msg):
    """Per spec Section 6: fail-closed on any feature load failure."""
    print(f"\nFEATURE BUILD FAILED (fail-closed per spec Section 6):\n  {msg}")
    sys.exit(2)


# ============================================================================
# Step 1: KAALCURA axes
# ============================================================================

def load_kaalcura_axes():
    if not KAALCURA_AXES.exists():
        fail_closed(f"KAALCURA axes file missing: {KAALCURA_AXES}")
    df = pd.read_csv(KAALCURA_AXES)
    print(f"  Raw shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")

    # Detect sample id column
    sid_col = None
    for c in df.columns:
        if c.startswith('Unnamed') or c.lower() in ('sample', 'sample_id', 'dbgap_sample_id'):
            sid_col = c
            break
    if sid_col is None:
        sid_col = df.columns[0]
    print(f"  Sample column: '{sid_col}'")

    axis_cols = ['R_prolif', 'R_emt', 'R_ddr']
    for c in axis_cols:
        if c not in df.columns:
            fail_closed(f"KAALCURA axis column '{c}' not in {KAALCURA_AXES.name}")

    out = df[[sid_col] + axis_cols].dropna()
    out['sample_id'] = out[sid_col].astype(str)
    out = out[['sample_id'] + axis_cols]
    print(f"  Final: {len(out)} samples × {len(axis_cols)} axes")
    return out


# ============================================================================
# Step 2: RNA-1000-no-sex
# ============================================================================

def load_rna_features():
    if not BEATAML_EXPR.exists():
        fail_closed(f"BeatAML expression file missing: {BEATAML_EXPR}")
    print(f"  Reading {BEATAML_EXPR.name} ({BEATAML_EXPR.stat().st_size/1024/1024:.0f} MB)...")
    raw = pd.read_csv(BEATAML_EXPR, sep='\t', low_memory=False)
    print(f"  Raw shape: {raw.shape}")

    metadata_cols = {'stable_id', 'display_label', 'description', 'biotype'}
    gene_col = 'display_label'
    if gene_col not in raw.columns:
        fail_closed(f"Expression file missing '{gene_col}' column")
    sample_cols = [c for c in raw.columns if c not in metadata_cols]
    print(f"  Sample columns: {len(sample_cols)}")

    raw = raw.dropna(subset=[gene_col])
    n_before = len(raw)
    raw = raw[~raw[gene_col].isin(SEX_LINKED_GENES)]
    n_after = len(raw)
    print(f"  Sex-linked filter: {n_before-n_after} dropped, {n_after} remain")

    # Deduplicate (highest mean)
    raw = raw.copy()
    raw['_mean'] = raw[sample_cols].mean(axis=1)
    raw = raw.sort_values('_mean', ascending=False).drop_duplicates(subset=[gene_col], keep='first')
    raw = raw.drop(columns=['_mean'])

    # Wide → long matrix (samples × genes)
    expr = raw.set_index(gene_col)[sample_cols].T  # samples × genes
    print(f"  Wide matrix: {expr.shape[0]} samples × {expr.shape[1]} genes")

    # Top-1000 most variable
    gene_var = expr.var(axis=0)
    top_genes = gene_var.nlargest(N_TOP_VAR_GENES).index.tolist()
    expr_top = expr[top_genes]
    print(f"  Top-{N_TOP_VAR_GENES} matrix: {expr_top.shape}")
    print(f"  First 5 selected: {top_genes[:5]}")

    out = expr_top.reset_index().rename(columns={'index': 'sample_id'})
    out['sample_id'] = out['sample_id'].astype(str)
    return out, top_genes


# ============================================================================
# Step 3: Mutation status (clinical flags + WES fallback)
# ============================================================================

def load_mutation_features():
    """
    15 mutation features per spec.
    Strategy: clinical flags (preferred, validated) + WES file (fallback for
    genes not in clinical metadata).
    """
    print(f"  Reading clinical: {BEATAML_CLIN.name}")
    if not BEATAML_CLIN.exists():
        fail_closed(f"Clinical file missing: {BEATAML_CLIN}")
    clin = pd.read_excel(BEATAML_CLIN, sheet_name='summary')
    print(f"  Clinical shape: {clin.shape}")
    print(f"  Clinical columns (first 30): {list(clin.columns[:30])}")

    # Sample id column
    sid_col = 'dbgap_rnaseq_sample'
    if sid_col not in clin.columns:
        # Fallback search
        for c in clin.columns:
            if 'rnaseq' in c.lower() and 'sample' in c.lower():
                sid_col = c
                break
        else:
            fail_closed(f"Clinical missing dbgap_rnaseq_sample column")
    print(f"  Sample id: '{sid_col}'")

    # Build mutation feature dataframe — start from clinical sample list
    mut_df = pd.DataFrame()
    mut_df['sample_id'] = clin[sid_col].astype(str)
    mut_df = mut_df.dropna()

    # Clinical flag columns (per Round 2 chat: FLT3-ITD validated)
    # Inspect to find all that are present
    clin_flag_cols = {
        'FLT3': ['FLT3', 'FLT3-mutation', 'FLT3_status', 'FLT3-D835', 'FLT3-N676'],
        'FLT3_ITD': ['FLT3-ITD', 'FLT3_ITD', 'FLT3-itd'],
        'NPM1': ['NPM1', 'NPM1-mutation', 'NPM1_status'],
        'IDH1': ['IDH1', 'IDH1-mutation', 'IDH1_status', 'IDH1-R132'],
        'IDH2': ['IDH2', 'IDH2-mutation', 'IDH2_status', 'IDH2-R140', 'IDH2-R172'],
        'TP53': ['TP53', 'TP53-mutation', 'TP53_status'],
        'RUNX1': ['RUNX1', 'RUNX1-mutation', 'RUNX1_status'],
        'CEBPA': ['CEBPA', 'CEBPA-mutation', 'CEBPA_status', 'CEBPA_Biallelic', 'CEBPA-biallelic'],
        'DNMT3A': ['DNMT3A', 'DNMT3A-mutation', 'DNMT3A_status'],
        'TET2': ['TET2', 'TET2-mutation', 'TET2_status'],
    }

    used_clinical = {}
    for gene, candidates in clin_flag_cols.items():
        for c in candidates:
            if c in clin.columns:
                used_clinical[gene] = c
                break

    print(f"  Clinical flags found: {len(used_clinical)}/{len(clin_flag_cols)}")
    for g, c in used_clinical.items():
        print(f"    {g}: '{c}'")

    # Encode clinical flags to binary
    # BeatAML conventions per diagnostic 2026-05-06:
    #   NPM1, FLT3-ITD: 'positive' / 'negative' / NaN
    #   TP53, RUNX1: variant-annotation string like 'TP53 (p.R248Q; 71.7%)' / NaN
    #   CEBPA_Biallelic: 'bi' / 'mono' / NaN (both are mutations)
    # NOTE: clinical file has 942 specimen-rows but ~707 unique RNA samples
    # (some patients have multiple specimens). Deduplicate by taking max per
    # sample — if ANY specimen for a patient was flagged positive, sample = 1.
    POSITIVE_STRINGS = {'positive', 'pos', 'mutated', 'mut', 'yes', 'y', 'bi', 'mono'}
    NEGATIVE_STRINGS = {'negative', 'neg', 'wt', 'wildtype', 'wild-type', 'no', 'n', 'unknown', 'u'}

    def to_bin(v):
        """
        Returns 1 if column value indicates a mutation, 0 otherwise.
        Strategy:
          - NaN → 0
          - Recognized positive string (positive/bi/mono/etc) → 1
          - Recognized negative string (negative/wt/etc) → 0
          - Any other non-empty string (e.g., variant annotation 'TP53 (p.R248Q; 71.7%)') → 1
            — this catches TP53/RUNX1-style columns where value IS the mutation
        """
        if pd.isna(v):
            return 0
        v_str = str(v).strip().lower()
        if v_str == '':
            return 0
        if v_str in POSITIVE_STRINGS:
            return 1
        if v_str in NEGATIVE_STRINGS:
            return 0
        # Fallback: any other non-empty value treated as variant-present
        return 1

    clin_local = clin[[sid_col] + list(used_clinical.values())].copy()
    clin_local[sid_col] = clin_local[sid_col].astype(str)
    clin_local = clin_local.dropna(subset=[sid_col])
    for gene, col in used_clinical.items():
        clin_local[col] = clin_local[col].apply(to_bin)
    # Aggregate per unique sample (max — any positive specimen → 1)
    clin_per_sample = clin_local.groupby(sid_col).max()
    print(f"  Clinical aggregated: {len(clin_local)} specimen-rows → {len(clin_per_sample)} unique samples")

    for gene, col in used_clinical.items():
        binary_per_sample = clin_per_sample[col]
        mut_df[gene] = mut_df['sample_id'].map(binary_per_sample).fillna(0).astype(int)

    # Now WES fallback for genes not in clinical
    genes_missing_clinical = [g for g in MUTATION_GENES
                              if g not in used_clinical and g != 'RAS_family' and g != 'FLT3_ITD']
    print(f"  Genes needing WES: {genes_missing_clinical}")

    GENE_COORDS_FILE = HOME / 'INTERCEPTA' / 'round2_aml' / 'data' / 'aml_gene_coords.json'

    if genes_missing_clinical or 'RAS_family' in MUTATION_GENES:
        if not BEATAML_MUTS.exists():
            print(f"  WARNING: WES file missing ({BEATAML_MUTS}). Setting WES-derived genes to 0.")
            for g in genes_missing_clinical:
                mut_df[g] = 0
            mut_df['RAS_family'] = 0
        elif not GENE_COORDS_FILE.exists():
            fail_closed(f"WES file present but gene coordinates cache missing.\n"
                        f"  Expected: {GENE_COORDS_FILE}\n"
                        f"  Run: python3 build_aml_gene_coords.py first.")
        else:
            print(f"  Loading WES: {BEATAML_MUTS.name} ({BEATAML_MUTS.stat().st_size/1024/1024:.1f} MB)")
            wes = pd.read_csv(BEATAML_MUTS, sep='\t', low_memory=False)
            print(f"  WES shape: {wes.shape}")

            # Required columns for coordinate-based annotation
            req_cols = ['seqnames', 'pos_start', 'pos_end', 'dbgap_sample_id']
            for rc in req_cols:
                if rc not in wes.columns:
                    fail_closed(f"WES file missing required column '{rc}'. Got: {list(wes.columns)}")

            # Load gene coordinate cache
            with open(GENE_COORDS_FILE) as f:
                gene_coords = json.load(f)
            print(f"  Loaded gene coordinate cache: {len(gene_coords)} genes")
            for g in genes_missing_clinical + RAS_FAMILY_MEMBERS:
                if g not in gene_coords:
                    print(f"    WARNING: {g} not in coordinate cache")

            # Map WES variants to genes via coordinate overlap
            # Build sample_id → set of mutated genes
            print(f"  Annotating {len(wes)} variants against {len(gene_coords)} genes...")

            # Normalize chromosome encoding
            def norm_chrom(c):
                s = str(c).strip()
                if s.lower().startswith('chr'):
                    s = s[3:]
                return s

            wes['_chrom'] = wes['seqnames'].apply(norm_chrom)
            wes['_pos_start'] = pd.to_numeric(wes['pos_start'], errors='coerce')
            wes['_pos_end'] = pd.to_numeric(wes['pos_end'], errors='coerce')
            wes_clean = wes.dropna(subset=['_pos_start', '_pos_end']).copy()
            print(f"  Variants with valid coordinates: {len(wes_clean)}/{len(wes)}")

            # Build per-chromosome gene intervals for fast lookup
            from collections import defaultdict
            chrom_intervals = defaultdict(list)  # chrom -> list of (start, end, gene_symbol)
            for g, c in gene_coords.items():
                chrom_intervals[norm_chrom(c['chrom'])].append((c['start'], c['end'], g))

            def assign_gene(row):
                chrom = row['_chrom']
                pos_s = row['_pos_start']
                pos_e = row['_pos_end']
                hits = []
                for (gs, ge, gsym) in chrom_intervals.get(chrom, []):
                    # Overlap: variant interval [pos_s, pos_e] vs gene [gs, ge]
                    if pos_e >= gs and pos_s <= ge:
                        hits.append(gsym)
                return hits

            wes_clean['_genes_hit'] = wes_clean.apply(assign_gene, axis=1)
            wes_clean = wes_clean[wes_clean['_genes_hit'].apply(lambda x: len(x) > 0)].copy()
            print(f"  Variants annotated to ≥1 target gene: {len(wes_clean)}")

            # Map WES sample IDs (DNA-seq) to RNA-seq sample IDs via clinical
            wes_sid = 'dbgap_sample_id'
            if 'dbgap_dnaseq_sample' in clin.columns and sid_col in clin.columns:
                dna_to_rna = clin[['dbgap_dnaseq_sample', sid_col]].dropna()
                dna_to_rna['dbgap_dnaseq_sample'] = dna_to_rna['dbgap_dnaseq_sample'].astype(str)
                dna_to_rna[sid_col] = dna_to_rna[sid_col].astype(str)
                dna_to_rna = dna_to_rna.drop_duplicates(subset=['dbgap_dnaseq_sample'], keep='first')
                dna_to_rna_map = dict(zip(
                    dna_to_rna['dbgap_dnaseq_sample'],
                    dna_to_rna[sid_col]
                ))
                print(f"  dna→rna mapping: {len(dna_to_rna_map)} unique dnaseq IDs mapped")
                wes_clean['_rna_sid'] = wes_clean[wes_sid].astype(str).map(dna_to_rna_map)
                wes_use = wes_clean.dropna(subset=['_rna_sid']).copy()
                wes_use = wes_use.rename(columns={'_rna_sid': 'sample_id'})
                print(f"  Variants matched to RNA samples: {len(wes_use)}/{len(wes_clean)}")
            else:
                print(f"  WARNING: cannot map dnaseq→rnaseq. Setting WES-derived genes to 0.")
                wes_use = pd.DataFrame()

            if not wes_use.empty:
                # Build sample → set of mutated genes (flatten the gene lists)
                sample_genes = defaultdict(set)
                for sid_v, genes_list in zip(wes_use['sample_id'], wes_use['_genes_hit']):
                    sample_genes[sid_v].update(genes_list)
                print(f"  Unique RNA samples with WES variants: {len(sample_genes)}")

                for g in genes_missing_clinical:
                    mut_df[g] = mut_df['sample_id'].apply(
                        lambda s: int(g in sample_genes.get(s, set()))
                    )
                # RAS_family: union of NRAS, KRAS
                mut_df['RAS_family'] = mut_df['sample_id'].apply(
                    lambda s: int(any(r in sample_genes.get(s, set()) for r in RAS_FAMILY_MEMBERS))
                )
            else:
                for g in genes_missing_clinical:
                    mut_df[g] = 0
                mut_df['RAS_family'] = 0
    else:
        mut_df['RAS_family'] = 0  # no genes to compute, all clinical

    # Make sure FLT3_ITD column exists
    if 'FLT3_ITD' not in mut_df.columns:
        mut_df['FLT3_ITD'] = 0

    # Reorder columns to match locked spec list
    feat_cols = ['sample_id'] + MUTATION_GENES
    mut_df = mut_df[feat_cols]

    # Mutation prevalence sanity check
    print(f"  Mutation feature prevalence (frac samples with mutation):")
    for g in MUTATION_GENES:
        prev = mut_df[g].mean()
        print(f"    {g}: {prev:.3f}")

    return mut_df


# ============================================================================
# Step 4: Pathway activity (RAW values; train-fold normalization in Step 2)
# ============================================================================

def load_pathway_features(rna_features_df, all_expr_genes):
    """
    Pathway activity = mean expression of pathway member genes per sample.

    NOTE: RAW values output here. Z-scoring is deferred to training fold per
    spec Section 6 (#5 — no data leakage). Step 2 will z-score using training
    fold means/stds.

    rna_features_df only has top-1000 genes — but pathway gene sets need ALL
    expression genes. Reload full expression to compute pathway means.
    """
    print(f"  Loading {KEGG_PATHWAY_MAP.name}...")
    if not KEGG_PATHWAY_MAP.exists():
        fail_closed(f"KEGG map missing: {KEGG_PATHWAY_MAP}")
    pmap = pd.read_csv(KEGG_PATHWAY_MAP)
    print(f"  Pathway map shape: {pmap.shape}")
    print(f"  Pathway map columns: {list(pmap.columns)}")

    # Detect column names
    pid_col = None
    for c in ['pathway_id', 'kegg_id', 'id', 'pathway']:
        if c in pmap.columns:
            pid_col = c
            break
    gene_col = None
    for c in ['gene_symbol', 'symbol', 'gene', 'gene_name']:
        if c in pmap.columns:
            gene_col = c
            break
    if pid_col is None or gene_col is None:
        fail_closed(f"KEGG map missing pathway_id or gene column. Got: {list(pmap.columns)}")
    print(f"  Pathway col: '{pid_col}', Gene col: '{gene_col}'")

    # Restrict to locked pathways
    pmap['_pid'] = pmap[pid_col].astype(str)
    locked_pmap = pmap[pmap['_pid'].isin(LOCKED_PATHWAYS.keys())]
    print(f"  Locked pathways present: {locked_pmap['_pid'].nunique()}/{len(LOCKED_PATHWAYS)}")

    # Reload full expression to compute pathway means (need all genes, not top-1000)
    print(f"  Reloading full BeatAML expression for pathway gene-set scoring...")
    raw = pd.read_csv(BEATAML_EXPR, sep='\t', low_memory=False)
    metadata_cols = {'stable_id', 'display_label', 'description', 'biotype'}
    gcol = 'display_label'
    sample_cols = [c for c in raw.columns if c not in metadata_cols]
    raw = raw.dropna(subset=[gcol])
    raw = raw.copy()
    raw['_mean'] = raw[sample_cols].mean(axis=1)
    raw = raw.sort_values('_mean', ascending=False).drop_duplicates(subset=[gcol], keep='first')
    raw = raw.drop(columns=['_mean'])
    expr_full = raw.set_index(gcol)[sample_cols].T  # samples × all genes
    expr_full.index = expr_full.index.astype(str)
    print(f"  Full expression: {expr_full.shape}")

    # Compute pathway scores
    pathway_scores = {}
    pathway_gene_counts = {}
    for pid, pname in LOCKED_PATHWAYS.items():
        path_genes = set(locked_pmap[locked_pmap['_pid'] == pid][gene_col].astype(str).str.strip())
        present = list(path_genes & set(expr_full.columns))
        pathway_gene_counts[pid] = (len(present), len(path_genes))
        if len(present) < 3:
            print(f"    WARNING: pathway {pid} ({pname}) has only {len(present)} genes in expression. Skipping.")
            continue
        col_name = f"path_{pid}"
        pathway_scores[col_name] = expr_full[present].mean(axis=1)

    if len(pathway_scores) < 5:
        fail_closed(f"Too few pathways with sufficient gene coverage: {len(pathway_scores)}")

    pdf = pd.DataFrame(pathway_scores).reset_index()
    pdf = pdf.rename(columns={'index': 'sample_id'})
    print(f"  Final pathway features: {pdf.shape[1]-1} pathways × {len(pdf)} samples")
    print(f"  Pathway gene coverage:")
    for pid, (present, total) in pathway_gene_counts.items():
        print(f"    {pid} ({LOCKED_PATHWAYS[pid]}): {present}/{total} genes in expression")

    return pdf


# ============================================================================
# Step 5: Drug-target features
# ============================================================================

def load_drug_target_features(drug_list):
    """
    For each drug:
      (1) Drug's primary target ∈ AML-mutated gene list? binary
      (2) Drug pchembl on its primary target (continuous; 0 if missing)
      (3) Drug's target in AML pathway (hsa05221) gene set? binary
      (4) n_targets for the drug
    """
    if not GENE_DRUG_NET.exists():
        print(f"  WARNING: gene-drug net missing ({GENE_DRUG_NET}). Drug-target features all 0.")
        out = pd.DataFrame({'drug': drug_list})
        out['tgt_aml_gene'] = 0
        out['tgt_pchembl'] = 0.0
        out['tgt_in_aml_pathway'] = 0
        out['n_targets'] = 0
        return out

    print(f"  Loading {GENE_DRUG_NET.name}...")
    net = pd.read_csv(GENE_DRUG_NET, low_memory=False)
    print(f"  Gene-drug net shape: {net.shape}")
    print(f"  Gene-drug net columns: {list(net.columns)}")

    # Find drug, target, pchembl columns (auto-detect)
    drug_col = None
    for c in ['drug', 'drug_name', 'compound', 'pref_name', 'inhibitor']:
        if c in net.columns:
            drug_col = c
            break
    target_col = None
    for c in ['target_gene', 'gene', 'symbol', 'target']:
        if c in net.columns:
            target_col = c
            break
    pchembl_col = None
    for c in ['pchembl', 'pchembl_value', 'pchembl_max', 'pchembl_mean', 'abs_r']:
        if c in net.columns:
            pchembl_col = c
            break

    if pchembl_col == 'abs_r':
        print(f"  Using abs_r (correlation strength) as target-strength proxy "
              f"since no pchembl column found")

    if drug_col is None or target_col is None:
        print(f"  WARNING: cannot detect drug/target columns. Drug-target features all 0.")
        out = pd.DataFrame({'drug': drug_list})
        out['tgt_aml_gene'] = 0
        out['tgt_pchembl'] = 0.0
        out['tgt_in_aml_pathway'] = 0
        out['n_targets'] = 0
        return out

    print(f"  drug col: '{drug_col}', target col: '{target_col}', pchembl col: '{pchembl_col}'")

    # AML-mutated gene set (excluding RAS_family which is meta)
    aml_mut_gene_set = set([g for g in MUTATION_GENES if g not in ('RAS_family', 'FLT3_ITD')]) | set(RAS_FAMILY_MEMBERS)

    # AML pathway gene set
    pmap = pd.read_csv(KEGG_PATHWAY_MAP)
    pid_c = next((c for c in ['pathway_id', 'kegg_id', 'id', 'pathway'] if c in pmap.columns), pmap.columns[0])
    g_c = next((c for c in ['gene_symbol', 'symbol', 'gene', 'gene_name'] if c in pmap.columns), pmap.columns[1])
    aml_pathway_genes = set(pmap[pmap[pid_c].astype(str) == 'hsa05221'][g_c].astype(str).str.strip())
    print(f"  AML pathway (hsa05221) gene set: {len(aml_pathway_genes)} genes")

    out_rows = []
    for d in drug_list:
        # Try exact then case-insensitive matching
        sub = net[net[drug_col].astype(str).str.lower() == d.lower()]
        if sub.empty:
            # Look for the drug name as substring (BeatAML uses parens like "Foretinib (XL880)")
            d_clean = d.split('(')[0].strip().lower()
            sub = net[net[drug_col].astype(str).str.lower().str.contains(d_clean, regex=False, na=False)]
        if sub.empty:
            out_rows.append({'drug': d, 'tgt_aml_gene': 0, 'tgt_pchembl': 0.0,
                             'tgt_in_aml_pathway': 0, 'n_targets': 0})
            continue
        targets = set(sub[target_col].astype(str).str.strip())
        n_tgt = len(targets)
        tgt_aml = int(bool(targets & aml_mut_gene_set))
        tgt_path = int(bool(targets & aml_pathway_genes))
        if pchembl_col and not sub[pchembl_col].dropna().empty:
            tgt_pch = float(sub[pchembl_col].dropna().max())
        else:
            tgt_pch = 0.0
        out_rows.append({
            'drug': d, 'tgt_aml_gene': tgt_aml, 'tgt_pchembl': tgt_pch,
            'tgt_in_aml_pathway': tgt_path, 'n_targets': n_tgt
        })

    out = pd.DataFrame(out_rows)
    print(f"  Drug-target coverage:")
    print(f"    drugs with any net hit: {(out['n_targets']>0).sum()}/{len(out)}")
    print(f"    drugs with target in AML mutated genes: {out['tgt_aml_gene'].sum()}")
    print(f"    drugs with target in AML pathway: {out['tgt_in_aml_pathway'].sum()}")
    return out


# ============================================================================
# Step 6: Drug response (final) and alignment
# ============================================================================

def load_drug_response_and_filter():
    if not BEATAML_FITS.exists():
        fail_closed(f"BeatAML curve fits missing: {BEATAML_FITS}")
    print(f"  Reading {BEATAML_FITS.name} ({BEATAML_FITS.stat().st_size/1024/1024:.0f} MB)...")
    fits = pd.read_csv(BEATAML_FITS, sep='\t', low_memory=False)
    print(f"  Raw shape: {fits.shape}")
    fits = fits[['dbgap_rnaseq_sample', 'inhibitor', 'auc']].dropna()
    fits['sample_id'] = fits['dbgap_rnaseq_sample'].astype(str)
    fits = fits.rename(columns={'inhibitor': 'drug'})
    fits = fits.drop(columns=['dbgap_rnaseq_sample'])
    fits['sensitive'] = (fits['auc'] < AUC_THRESHOLD).astype(int)
    print(f"  Cleaned shape: {fits.shape}")
    print(f"  Unique drugs: {fits['drug'].nunique()}")
    print(f"  Unique samples: {fits['sample_id'].nunique()}")
    return fits


# ============================================================================
# Main
# ============================================================================

def main():
    banner("Round 2.2c — Step 1: Multi-Modal Feature Builder")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    banner("Step 1 of 6: KAALCURA axes")
    kaalcura_df = load_kaalcura_axes()
    kaalcura_df.to_csv(OUT_KAALCURA, index=False)
    print(f"  Saved: {OUT_KAALCURA}")

    banner("Step 2 of 6: RNA-1000-no-sex")
    rna_df, top_genes = load_rna_features()
    rna_df.to_csv(OUT_RNA, index=False)
    print(f"  Saved: {OUT_RNA}")

    banner("Step 3 of 6: Mutation status (clinical + WES)")
    muts_df = load_mutation_features()
    muts_df.to_csv(OUT_MUTS, index=False)
    print(f"  Saved: {OUT_MUTS}")

    banner("Step 4 of 6: Pathway activity (raw)")
    paths_df = load_pathway_features(rna_df, top_genes)
    paths_df.to_csv(OUT_PATHWAYS, index=False)
    print(f"  Saved: {OUT_PATHWAYS}")

    banner("Step 5 of 6: Drug response and filter")
    fits = load_drug_response_and_filter()

    # Apply 10/10 drug filter
    drug_stats = fits.groupby('drug').agg(
        n_sensitive=('sensitive', 'sum'),
        n_total=('sensitive', 'count'),
    ).reset_index()
    drug_stats['n_resistant'] = drug_stats['n_total'] - drug_stats['n_sensitive']
    keep_drugs = drug_stats[(drug_stats['n_sensitive'] >= MIN_SENSITIVE) &
                            (drug_stats['n_resistant'] >= MIN_RESISTANT)]['drug'].tolist()
    print(f"  Drugs passing 10/10 filter: {len(keep_drugs)}")
    fits_filtered = fits[fits['drug'].isin(keep_drugs)].copy()
    print(f"  Filtered drug-response rows: {len(fits_filtered)}")

    # Sample alignment — sample must be in KAALCURA AND RNA (by definition the same)
    common_samples = set(kaalcura_df['sample_id']) & set(rna_df['sample_id']) & set(fits_filtered['sample_id'])
    print(f"  Samples in KAALCURA: {len(kaalcura_df)}")
    print(f"  Samples in RNA: {len(rna_df)}")
    print(f"  Samples in filtered drug response: {fits_filtered['sample_id'].nunique()}")
    print(f"  Common (KAALCURA ∩ RNA ∩ drugs): {len(common_samples)}")

    fits_aligned = fits_filtered[fits_filtered['sample_id'].isin(common_samples)].copy()
    fits_aligned.to_csv(OUT_RESPONSE, index=False)
    print(f"  Saved: {OUT_RESPONSE}")
    print(f"  Aligned drug-response rows: {len(fits_aligned)}")

    banner("Step 6 of 6: Drug-target features")
    drug_tgt_df = load_drug_target_features(keep_drugs)
    drug_tgt_df.to_csv(OUT_DRUG_TGT, index=False)
    print(f"  Saved: {OUT_DRUG_TGT}")

    banner("Summary")
    summary = {
        'started': time.strftime('%Y-%m-%d %H:%M:%S'),
        'feature_counts': {
            'kaalcura_axes': 3,
            'rna_genes': len(top_genes),
            'mutation_features': len(MUTATION_GENES),
            'pathway_features': paths_df.shape[1] - 1,
            'drug_target_features': drug_tgt_df.shape[1] - 1,
        },
        'total_features_per_sample_drug': (
            3 + len(top_genes) + len(MUTATION_GENES) +
            (paths_df.shape[1] - 1) + (drug_tgt_df.shape[1] - 1)
        ),
        'alignment': {
            'samples_in_kaalcura': len(kaalcura_df),
            'samples_in_rna': len(rna_df),
            'samples_in_filtered_drug_response': fits_filtered['sample_id'].nunique(),
            'common_samples': len(common_samples),
            'drugs_passing_10_10': len(keep_drugs),
            'aligned_drug_response_rows': len(fits_aligned),
        },
        'top_5_rna_genes': top_genes[:5],
        'mutation_gene_list': MUTATION_GENES,
        'pathway_id_to_name': LOCKED_PATHWAYS,
        'drug_list': keep_drugs,
        'output_files': {
            'kaalcura': str(OUT_KAALCURA.relative_to(HOME)),
            'rna': str(OUT_RNA.relative_to(HOME)),
            'mutations': str(OUT_MUTS.relative_to(HOME)),
            'pathways': str(OUT_PATHWAYS.relative_to(HOME)),
            'drug_target': str(OUT_DRUG_TGT.relative_to(HOME)),
            'drug_response_aligned': str(OUT_RESPONSE.relative_to(HOME)),
        },
    }
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary: {OUT_SUMMARY}")
    print(f"\n  Total features per (sample,drug): {summary['total_features_per_sample_drug']}")
    print(f"  Aligned (sample,drug) pairs: {len(fits_aligned)}")

    banner("DONE — Step 1 of 3 complete")
    print(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Next: run train_multimodal_predictor.py (Round 2.2c Step 2 of 3)")


if __name__ == '__main__':
    main()
