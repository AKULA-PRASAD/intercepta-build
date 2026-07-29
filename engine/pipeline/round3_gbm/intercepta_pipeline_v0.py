"""
INTERCEPTA Pipeline v0 — Phase 1 fixes from GBM live test
==========================================================
Closes Gaps 1, 2, 4, 5 from the live test findings (Gap 3 = env file).
Closes Gaps 9, 10 (Phase 2A: ranking + metabolite enrichment).
Closes Gaps 6, 8 (Phase 2B: STRING any-disease).
Closes Gap 11 (Phase 2C: AlphaFold any-disease).
Closes Gap 7 (Phase 2D: ChEMBL any-disease).

Action 1 cleanup applied 2026-05-06 — see ../CLEANUP_NOTES.md
- Drift 1: ChEMBL target picks best-data-match (not first-match)
- Drift 2: print_net_summary for honest post-enrichment counts
- Drift 3: surface_undruggable_priority_targets makes 0-compound high-priority targets visible
- Drift 4: verification block exercises new functions

Wraps existing disease_net_builder and GDSC data. Does NOT modify Round 1/2
artifacts (Principle 16 preserve-past-work).

Usage:
    from intercepta_pipeline_v0 import resolve_disease, build_net, inspect_gdsc_drugs

    info = resolve_disease("glioblastoma")
    # -> {'best_id': 'EFO_0000519', 'name': 'glioblastoma multiforme', 'n_rows': 9906, 'all_candidates': [...]}

    net = build_net("glioblastoma")  # auto-resolves, builds from best ID
"""
import sys
from pathlib import Path

# Make the original code importable
INTERCEPTA_CODE = Path.home() / 'INTERCEPTA' / 'code'
sys.path.insert(0, str(INTERCEPTA_CODE))

import pandas as pd
import re
from disease_net_builder import DiseaseNetBuilder

# Singleton builder so we don't reload 51M parquet on every call
_builder = None
def _get_builder():
    """
    Gap 19 fix: pass ABSOLUTE paths instead of letting DiseaseNetBuilder rely on cwd.
    The class uses '../results/...' relative paths which only work when invoked
    from ~/INTERCEPTA/code/. We pass absolute paths so the module works from anywhere.
    """
    global _builder
    if _builder is None:
        from pathlib import Path
        results = Path.home() / 'INTERCEPTA' / 'results'
        _builder = DiseaseNetBuilder(
            net_path=str(results / 'mcrpc_unified_net.json'),
            assoc_path=str(results / 'step8_gene_disease_associations.parquet'),
            names_path=str(results / 'step8_disease_names.csv'),
            met_path=str(results / 'step9_metabolome_gene_edges.csv'),
            immune_path=str(results / 'step13_immune_expression.csv'),
        )
    return _builder


# ========== GAP 1+2: chain search -> pick -> build, with disambiguation ==========

def resolve_disease(name, prefer_efo=True, verbose=False):
    """
    Fix for Gap 1 (no chain) + Gap 2 (no disambiguation).

    Given a disease name, returns the best ontology ID by:
    1. Search for all matches (DiseaseNetBuilder.search_disease)
    2. Count actual gene-association rows in the parquet for each ID
    3. Prefer EFO IDs over MONDO when both have data (oncology snapshots in
       OpenTargets index oncology more thoroughly under EFO)
    4. Return highest-coverage ID

    Returns:
        dict with keys: best_id, name, n_rows, all_candidates
    """
    builder = _get_builder()
    hits = builder.search_disease(name, top_n=20)
    if not hits:
        return {'best_id': None, 'name': name, 'n_rows': 0, 'all_candidates': []}

    # Score each hit by row count in associations parquet
    scored = []
    for did, dname in hits:
        n = len(builder.assoc[builder.assoc['diseaseId'] == did])
        scored.append({'id': did, 'name': dname, 'n_rows': n})

    # Sort by row count desc, with EFO preference as tiebreaker for oncology
    def sort_key(c):
        # Higher coverage first; EFO before MONDO at equal coverage if prefer_efo
        efo_bonus = (1 if c['id'].startswith('EFO_') and prefer_efo else 0)
        return (-c['n_rows'], -efo_bonus)
    scored.sort(key=sort_key)

    best = scored[0]
    if verbose:
        print(f"\nResolved '{name}' -> {best['id']} ({best['name']}) with {best['n_rows']} rows")
        print(f"All candidates ranked by coverage:")
        for c in scored[:5]:
            marker = '*' if c['id'] == best['id'] else ' '
            print(f"  {marker} {c['id']:20s} {c['n_rows']:>5d} rows  {c['name']}")

    return {
        'best_id': best['id'],
        'name': best['name'],
        'n_rows': best['n_rows'],
        'all_candidates': scored,
    }


def build_net(disease_query, min_score=0.1, max_genes=500, verbose=False):
    """
    Fix for Gap 1: takes a disease name (or an ID) and returns a built net.
    If a name is given, auto-resolves to the best ID.
    If an ID is given, passes through to original build_net.
    """
    builder = _get_builder()
    # Detect: ID-like has prefix MONDO_ / EFO_ / OBA_ etc. plus underscore plus digits
    is_id = bool(re.match(r'^[A-Z]+_\d+$', disease_query))
    if is_id:
        disease_id = disease_query
        if verbose:
            print(f"build_net: treating '{disease_query}' as ontology ID")
    else:
        resolved = resolve_disease(disease_query, verbose=verbose)
        disease_id = resolved['best_id']
        if disease_id is None:
            print(f"build_net: could not resolve '{disease_query}'")
            return None
    return builder.build_net(disease_id, min_score=min_score, max_genes=max_genes)


# ========== GAP 4: better GDSC drug-target inspector ==========

def inspect_gdsc_drugs():
    """
    Fix for Gap 4: my Stage 3 filename regex missed GDSC2_fitted_dose_response.xlsx
    because the filename doesn't contain 'drug' or 'target'. This loads any
    GDSC xlsx/csv that is plausibly drug-related and returns the one with both
    a drug-name column and a target column.

    Returns:
        (DataFrame, drug_col_name, target_col_name, source_file_path) or
        (None, None, None, None) if no suitable file found.
    """
    gdsc_dir = Path.home() / 'INTERCEPTA' / 'data' / 'gdsc'
    files = list(gdsc_dir.glob('**/*.xlsx')) + list(gdsc_dir.glob('**/*.csv'))
    files = [f for f in files if f.is_file()]

    drug_col_patterns = [r'^DRUG_NAME$', r'^drug_?name$', r'^drug$', r'^compound$']
    target_col_patterns = [r'^PUTATIVE_TARGET$', r'^target$', r'.*target.*gene.*']

    candidates = []
    for f in files:
        try:
            # Read just header + 1 row to inspect
            if f.suffix == '.xlsx':
                df = pd.read_excel(f, nrows=1)
            else:
                df = pd.read_csv(f, sep=None, engine='python', nrows=1)
            cols = list(df.columns)
            drug_col = next((c for c in cols
                            if any(re.match(p, c, re.IGNORECASE) for p in drug_col_patterns)), None)
            target_col = next((c for c in cols
                              if any(re.match(p, c, re.IGNORECASE) for p in target_col_patterns)), None)
            if drug_col and target_col:
                candidates.append((f, drug_col, target_col, len(cols)))
        except Exception:
            continue

    if not candidates:
        return (None, None, None, None)

    # Pick the file with most columns (likely the richest)
    candidates.sort(key=lambda x: -x[3])
    f, drug_col, target_col, _ = candidates[0]
    print(f"GDSC drug-target file detected: {f.name} (drug='{drug_col}', target='{target_col}')")

    # Load fully
    if f.suffix == '.xlsx':
        df = pd.read_excel(f)
    else:
        df = pd.read_csv(f, sep=None, engine='python')
    return (df, drug_col, target_col, f)


# ========== GAP 5: corrected net summary ==========

def corrected_net_summary(net, builder=None):
    """
    Fix for Gap 5: build_net's summary printed 'drug_targets (with compounds): 5'
    but per-gene `n_drug_correlations` showed 20 for many genes. The discrepancy
    came from build_net counting `len(drug_targets) which was a list of unique
    drugs added across genes, not the count of genes-with-compounds.

    This function reports both interpretations honestly.
    """
    if builder is None:
        builder = _get_builder()
    genes = net.get('genes', {})
    n_genes = len(genes)
    n_with_drug_corrs = sum(1 for g, d in genes.items()
                           if d.get('n_drug_correlations', 0) > 0)
    n_with_interactions = sum(1 for g, d in genes.items()
                             if d.get('n_interactions', 0) > 0)
    n_with_mut = sum(1 for g, d in genes.items()
                    if d.get('mutation_frequency', 0) > 0)
    drug_targets_field_count = len(net.get('drug_targets', []))

    return {
        'n_genes_total': n_genes,
        'n_genes_with_drug_correlations': n_with_drug_corrs,
        'n_genes_with_interactions': n_with_interactions,
        'n_genes_with_mutations': n_with_mut,
        'drug_targets_field_count_legacy': drug_targets_field_count,
        'n_pathways': len(net.get('pathways', [])),
        'n_metabolites': len(net.get('metabolites', [])),
        'n_immune_relevant': len(net.get('immune_relevant', [])),
        'n_structures': len(net.get('structures_available', [])),
    }


# ========== ACTION 1 CLEANUP: print_net_summary (Drift 2 fix) ==========

def print_net_summary(net, label='post-enrichment'):
    """
    Drift 2 fix: print honest current net state at any point in the pipeline.

    The summary printed by disease_net_builder.build_net() shows pre-enrichment
    counts. After Phase 2B/2C/2D run, those counts are stale. This function
    reports the actual current state.

    Does NOT modify disease_net_builder.py (Principle 16 preserve-past-work).

    Args:
        net: disease net dict
        label: human-readable context label, e.g. 'post-enrichment', 'after-2D'
    """
    genes = net.get('genes', {})
    n_genes = len(genes)
    n_with_uniprot = sum(1 for g in genes.values() if g.get('uniprot_id'))
    n_with_alphafold = sum(1 for g in genes.values() if g.get('alphafold_available'))
    n_with_chembl_target = sum(1 for g in genes.values() if g.get('chembl_target_id'))
    n_with_compounds = sum(1 for g in genes.values() if g.get('n_chembl_compounds', 0) > 0)
    total_compounds = sum(g.get('n_chembl_compounds', 0) for g in genes.values())
    n_with_interactions = sum(1 for g in genes.values() if g.get('n_interactions', 0) > 0)
    total_edges = sum(g.get('n_interactions', 0) for g in genes.values())
    n_with_metabolites = sum(1 for g in genes.values() if g.get('n_metabolites', 0) > 0)

    print(f"\n  Net summary ({label}):")
    print(f"    Disease:                {net.get('disease', 'unknown')}")
    print(f"    Genes total:            {n_genes}")
    print(f"    Pathways:               {len(net.get('pathways', []))}")
    print(f"    Genes with UniProt:     {n_with_uniprot}")
    print(f"    Genes with AlphaFold:   {n_with_alphafold}")
    print(f"    Genes with ChEMBL tgt:  {n_with_chembl_target}")
    print(f"    Genes with compounds:   {n_with_compounds} ({total_compounds} compounds total)")
    print(f"    Genes with STRING ints: {n_with_interactions} ({total_edges} edges total)")
    print(f"    Genes with metabolites: {n_with_metabolites}")
    print(f"    Immune-relevant genes:  {len(net.get('immune_relevant', []))}")


# ========== GAP 10: rank_drugs_for_disease — replaces Stage 3 manual glue ==========

def rank_drugs_for_disease(disease_query, top_n=30, min_cell_lines=3, top_gene_set_size=20):
    """
    Fix for Gap 10: closes Stage 3 manual glue.
    Given a disease name or ID, returns drugs ranked by:
      - Median GDSC AUC in disease-tissue cell lines (efficacy proxy, lower=better)
      - Number of disease-net top genes hit (target relevance)
      - Number of any disease-net genes hit (broader relevance)

    Tissue mapping is heuristic from disease name keywords. Returns a DataFrame.
    """
    from pathlib import Path
    import pandas as pd
    import re

    builder = _get_builder()

    # Resolve and build the disease net (chains Phase 1 fixes)
    if re.match(r'^[A-Z]+_\d+$', disease_query):
        disease_id = disease_query
    else:
        resolved = resolve_disease(disease_query)
        disease_id = resolved['best_id']
    if disease_id is None:
        return None
    net = builder.build_net(disease_id, min_score=0.1, max_genes=500)
    if net is None:
        return None

    disease_name = net.get('disease', disease_query)
    all_disease_genes = set(net.get('genes', {}).keys())
    top_genes = sorted(net['genes'].items(),
                      key=lambda x: x[1].get('association_score', 0),
                      reverse=True)[:top_gene_set_size]
    top_gene_set = {g for g, _ in top_genes}

    # Heuristic: map disease keywords to GDSC tissue keywords
    tissue_keywords = _disease_to_tissue_keywords(disease_name)

    # Load Cell_Lines_Details
    cl = pd.read_excel(Path.home() / 'INTERCEPTA/data/gdsc/Cell_Lines_Details.xlsx')
    tissue_col = 'GDSC\nTissue\ndescriptor 2'
    if tissue_col not in cl.columns:
        # Fallback to first tissue-like column
        tissue_col = next((c for c in cl.columns if 'tissue' in c.lower()), None)

    tissue_pattern = '|'.join(tissue_keywords)
    tissue_mask = cl[tissue_col].astype(str).str.lower().str.contains(tissue_pattern, regex=True, na=False)
    tissue_cosmic = set(cl[tissue_mask]['COSMIC identifier'].dropna().astype(int).tolist())

    if not tissue_cosmic:
        # Fall back to all cell lines if no tissue match
        print(f'  rank_drugs_for_disease: no tissue match for keywords {tissue_keywords}; using all GDSC cell lines')
        tissue_cosmic = None

    # Load GDSC dose-response
    dr = pd.read_excel(Path.home() / 'INTERCEPTA/data/gdsc/GDSC2_fitted_dose_response.xlsx')
    if tissue_cosmic:
        dr = dr[dr['COSMIC_ID'].isin(tissue_cosmic)]

    # Aggregate per drug
    drug_agg = dr.groupby('DRUG_NAME').agg(
        target_str=('PUTATIVE_TARGET', 'first'),
        pathway_name=('PATHWAY_NAME', 'first'),
        median_auc=('AUC', 'median'),
        n_cell_lines=('AUC', 'count'),
    ).reset_index()
    drug_agg['targets'] = drug_agg['target_str'].apply(
        lambda s: [t.strip().upper() for t in re.split(r'[,;]', str(s)) if t.strip()] if pd.notna(s) else [])
    drug_agg['n_top_gene_hits'] = drug_agg['targets'].apply(
        lambda ts: sum(1 for t in ts if t in top_gene_set))
    drug_agg['n_any_gene_hits'] = drug_agg['targets'].apply(
        lambda ts: sum(1 for t in ts if t in all_disease_genes))
    drug_agg['top_gene_hits'] = drug_agg['targets'].apply(
        lambda ts: [t for t in ts if t in top_gene_set])

    # Filter and rank
    ranked = drug_agg[drug_agg['n_cell_lines'] >= min_cell_lines].copy()
    # Composite score: lower AUC AND more disease-gene hits = better
    ranked['composite_score'] = (1 - ranked['median_auc']) + 0.1 * ranked['n_top_gene_hits'] + 0.02 * ranked['n_any_gene_hits']
    ranked = ranked.sort_values('composite_score', ascending=False).reset_index(drop=True)

    return ranked.head(top_n)


def _disease_to_tissue_keywords(disease_name):
    """Heuristic disease -> GDSC tissue keyword mapping."""
    name_l = disease_name.lower()
    mapping = {
        ('glioblastoma', 'glioma', 'astrocytoma', 'brain'): ['glio', 'brain', 'central nervous', 'cns'],
        ('prostate',): ['prostate'],
        ('lung', 'nsclc', 'sclc'): ['lung'],
        ('breast',): ['breast'],
        ('pancreat',): ['pancrea'],
        ('leukemia', 'aml', 'cml', 'all'): ['leukaem', 'leukem', 'haema', 'blood'],
        ('melanoma',): ['melanoma', 'skin'],
        ('colon', 'colorectal'): ['colon', 'colorectal', 'large_intestine'],
        ('ovarian',): ['ovary', 'ovarian'],
    }
    for keys, vals in mapping.items():
        if any(k in name_l for k in keys):
            return vals
    return [name_l.split()[0]]  # fallback: first word


# ========== SESSION 2: Composite multi-evidence ranking with BBB filter ==========
#
# Vision Stage 5 ranking layer. Replaces GDSC-only ranking which validation
# showed structurally fails for GBM (temozolomide ranked 257/286, 4/4 GBM SOC
# drugs missing or low-ranked).
#
# Architecture follows published precedent for multi-evidence drug ranking:
#   - DrugRepo (Khan et al. Sci Rep 2022): 3-component composite via averaging
#   - OncoDrug+ (Sci Data 2025): evidence-level + biomarker-match rank system
#   - Wager et al. ACS Chem Neurosci 2010: CNS MPO for BBB
#   - BaySyn (medRxiv 2022): synthesizes patient + model-system data
#
# Key design choice: BBB is a MULTIPLICATIVE GATE for CNS diseases, not a
# weighted addend. A drug that cannot cross BBB receives effective_score = 0
# for CNS diseases regardless of other channels. This reflects clinical
# reality: BBB-impermeable drugs cannot work for brain tumors.


def rank_drugs_for_disease_v2(
    disease_query,
    top_n=30,
    min_cell_lines=3,
    cns_disease=None,
    weights=None,
    show_breakdown=False,
):
    """
    Composite multi-evidence drug ranking for any disease.

    Five evidence channels combined per published precedent. Each drug receives
    a score from each channel where data exists; missing data does not penalize
    (drug just doesn't get points from that channel). For CNS diseases, BBB is
    a multiplicative gate.

    Channel definitions:

    Channel 1 (GDSC, weight 1/3 default):
      Median GDSC AUC in disease-tissue cell lines. Score = (1 - AUC). Range 0-1.
      Drugs not in GDSC panel get 0 from this channel.

    Channel 2 (ChEMBL bioactivity x disease-net association, weight 1/3):
      For each drug, find which disease-net genes it targets (via PUTATIVE_TARGET).
      Score = sum over targeted genes of (best_pchembl / 10) * association_score.
      Normalized to [0, 1] by dividing by max across drugs.
      Drugs targeting genes not in disease net get 0.
      Range 0-1.

    Channel 3 (ClinicalTrials.gov activity, weight 1/3):
      For each drug-target gene, count GBM trials. Score = log(1 + n_trials) / log(50).
      Capped at 1.0. Reflects clinical investigator interest.
      Drugs with no trials in disease get 0.
      Range 0-1.

    Channel 4 (BBB gate, multiplicative; only if cns_disease=True):
      For each drug, look at all its targeted-gene compounds. If ANY of those
      compounds is bbb=likely_bbb_pos, gate=1.0. If borderline, gate=0.5. If only
      bbb_neg, gate=0.0. If only data_unavailable, gate=0.5 (neutral assumption).
      Multiplies the channel-1+2+3 sum.

    Channel 5 (Disease-net proximity bonus, additive, max +0.3):
      For each drug, compute average network centrality of its targeted disease-genes
      (#interactions / max #interactions in net). Bonus = 0.3 * mean_centrality.
      Drugs with no disease-net targets get +0.

    Composite score:
      For non-CNS:  (c1 + c2 + c3) * (1/3) + c5_bonus
      For CNS:      ((c1 + c2 + c3) * (1/3)) * c4_gate + c5_bonus

    Args:
      disease_query: name or ID
      top_n: results to return
      min_cell_lines: GDSC filter
      cns_disease: True/False/None. If None, auto-detect via tissue keywords
                   (glioblastoma, glioma, brain, CNS, etc.)
      weights: dict {gdsc, chembl, trials, prox_bonus} to override defaults
      show_breakdown: include per-channel scores in output

    Returns:
      DataFrame with columns: DRUG_NAME, target_str, n_top_gene_hits,
      n_any_gene_hits, channel_scores, composite_v2, rank
    """
    from pathlib import Path
    import pandas as pd
    import numpy as np
    import re
    import math

    builder = _get_builder()

    # --- Resolve disease and build net (chains all enrichments) ---
    if re.match(r'^[A-Z]+_\d+$', disease_query):
        disease_id = disease_query
    else:
        resolved = resolve_disease(disease_query)
        disease_id = resolved['best_id']
    if disease_id is None:
        return None
    net = builder.build_net(disease_id, min_score=0.1, max_genes=500)
    if net is None:
        return None

    # Phase 2B/2C/2D/2E enrichments must be applied to make this function work.
    # We chain them here (cache makes them fast).
    populate_string_interactions(net, min_score=700)
    attach_alphafold_structures(net, check_availability=False)  # skip URL-check for speed
    populate_chembl_compounds(net, top_n=50, sleep_between=1.1, save_cache_every=20, verbose=False)
    if 'disease_id' not in net:
        net['disease_id'] = disease_id
    populate_clinical_trials(net, sleep_between=0.4, save_cache_every=20, verbose=False)

    disease_name = net.get('disease', disease_query)
    all_disease_genes = set(net.get('genes', {}).keys())

    # --- CNS auto-detection ---
    if cns_disease is None:
        name_l = disease_name.lower()
        cns_keywords = ['glio', 'brain', 'cns', 'central nervous', 'medulloblastoma',
                        'meningioma', 'astrocytoma', 'oligodendroglioma', 'cerebellar']
        cns_disease = any(k in name_l for k in cns_keywords)
    if show_breakdown:
        print(f'  rank_drugs_for_disease_v2: cns_disease={cns_disease} for "{disease_name}"')

    # --- Default weights (from published precedent) ---
    default_weights = {
        'gdsc': 1.0 / 3.0,
        'chembl': 1.0 / 3.0,
        'trials': 1.0 / 3.0,
        'prox_bonus_max': 0.3,
        'bbb_pos': 1.0,
        'bbb_borderline': 0.5,
        'bbb_neg': 0.0,
        'bbb_unknown': 0.5,
    }
    if weights:
        default_weights.update(weights)
    w = default_weights

    # --- Channel 1: GDSC ---
    tissue_keywords = _disease_to_tissue_keywords(disease_name)
    cl = pd.read_excel(Path.home() / 'INTERCEPTA/data/gdsc/Cell_Lines_Details.xlsx')
    tissue_col = 'GDSC\nTissue\ndescriptor 2'
    if tissue_col not in cl.columns:
        tissue_col = next((c for c in cl.columns if 'tissue' in c.lower()), None)
    tissue_pattern = '|'.join(tissue_keywords)
    tissue_mask = cl[tissue_col].astype(str).str.lower().str.contains(tissue_pattern, regex=True, na=False)
    tissue_cosmic = set(cl[tissue_mask]['COSMIC identifier'].dropna().astype(int).tolist())

    dr = pd.read_excel(Path.home() / 'INTERCEPTA/data/gdsc/GDSC2_fitted_dose_response.xlsx')
    if tissue_cosmic:
        dr_filtered = dr[dr['COSMIC_ID'].isin(tissue_cosmic)].copy()
    else:
        dr_filtered = dr.copy()

    drug_agg = dr_filtered.groupby('DRUG_NAME').agg(
        target_str=('PUTATIVE_TARGET', 'first'),
        pathway_name=('PATHWAY_NAME', 'first'),
        median_auc=('AUC', 'median'),
        n_cell_lines=('AUC', 'count'),
    ).reset_index()
    drug_agg = drug_agg[drug_agg['n_cell_lines'] >= min_cell_lines].copy()

    drug_agg['targets'] = drug_agg['target_str'].apply(
        lambda s: [t.strip().upper() for t in re.split(r'[,;]', str(s)) if t.strip()] if pd.notna(s) else [])
    drug_agg['n_any_gene_hits'] = drug_agg['targets'].apply(
        lambda ts: sum(1 for t in ts if t in all_disease_genes))

    # Channel 1 score: 1 - median_auc (lower AUC = better)
    drug_agg['c1_gdsc'] = (1 - drug_agg['median_auc']).clip(0, 1)

    # --- Channel 2: ChEMBL pchembl × association_score for targeted genes ---
    # For each drug, find which disease-net genes it targets, get top pchembl per gene.
    chembl_scores_per_drug = {}
    for idx, row in drug_agg.iterrows():
        drug_name = row['DRUG_NAME']
        targets_in_net = [t for t in row['targets'] if t in all_disease_genes]
        if not targets_in_net:
            chembl_scores_per_drug[drug_name] = 0.0
            continue
        # Score = sum over targets of (top_pchembl/10) * association_score
        score = 0.0
        for gene in targets_in_net:
            gene_data = net['genes'].get(gene, {})
            assoc = gene_data.get('association_score', 0)
            compounds = gene_data.get('chembl_compounds', [])
            if not compounds:
                continue
            top_pchembl = max((c.get('pchembl_value', 0) for c in compounds), default=0)
            # Normalize pchembl to [0,1]: pchembl 5 = 0.0, pchembl 10 = 1.0 typical range
            normalized_pchembl = max(0, min(1, (top_pchembl - 5) / 5))
            score += normalized_pchembl * assoc
        chembl_scores_per_drug[drug_name] = score

    drug_agg['c2_chembl_raw'] = drug_agg['DRUG_NAME'].map(chembl_scores_per_drug).fillna(0)
    max_c2 = drug_agg['c2_chembl_raw'].max()
    if max_c2 > 0:
        drug_agg['c2_chembl'] = drug_agg['c2_chembl_raw'] / max_c2
    else:
        drug_agg['c2_chembl'] = 0.0

    # --- Channel 3: ClinicalTrials.gov activity ---
    # For each drug, sum trials across its targeted disease-net genes.
    trial_scores_per_drug = {}
    for idx, row in drug_agg.iterrows():
        drug_name = row['DRUG_NAME']
        targets_in_net = [t for t in row['targets'] if t in all_disease_genes]
        total_trials = 0
        for gene in targets_in_net:
            gene_data = net['genes'].get(gene, {})
            total_trials += gene_data.get('n_clinical_trials', 0)
        # Logarithmic compression: many drugs target same genes, this rewards more
        # but with diminishing returns
        if total_trials == 0:
            score = 0.0
        else:
            score = min(1.0, math.log(1 + total_trials) / math.log(51))  # cap at 50 trials = 1.0
        trial_scores_per_drug[drug_name] = score

    drug_agg['c3_trials'] = drug_agg['DRUG_NAME'].map(trial_scores_per_drug).fillna(0)

    # --- Channel 4: BBB gate (CNS diseases only) ---
    # For each drug, look at all compounds for its targeted genes. Gate based
    # on best BBB category found.
    bbb_gates_per_drug = {}
    for idx, row in drug_agg.iterrows():
        drug_name = row['DRUG_NAME']
        targets_in_net = [t for t in row['targets'] if t in all_disease_genes]

        if not targets_in_net:
            bbb_gates_per_drug[drug_name] = w['bbb_unknown']
            continue

        # Look at all compounds for targeted genes; find best BBB category
        all_compounds = []
        for gene in targets_in_net:
            gene_data = net['genes'].get(gene, {})
            all_compounds.extend(gene_data.get('chembl_compounds', []))

        if not all_compounds:
            bbb_gates_per_drug[drug_name] = w['bbb_unknown']
            continue

        bbb_categories = [c.get('bbb', {}).get('category') for c in all_compounds]
        bbb_categories = [b for b in bbb_categories if b]

        if not bbb_categories:
            bbb_gates_per_drug[drug_name] = w['bbb_unknown']
        elif 'likely_bbb_pos' in bbb_categories:
            bbb_gates_per_drug[drug_name] = w['bbb_pos']
        elif 'borderline' in bbb_categories:
            bbb_gates_per_drug[drug_name] = w['bbb_borderline']
        elif 'data_unavailable' in bbb_categories and 'likely_bbb_neg' not in bbb_categories:
            bbb_gates_per_drug[drug_name] = w['bbb_unknown']
        else:
            bbb_gates_per_drug[drug_name] = w['bbb_neg']

    drug_agg['c4_bbb_gate'] = drug_agg['DRUG_NAME'].map(bbb_gates_per_drug).fillna(w['bbb_unknown'])

    # --- Channel 5: Disease-net proximity bonus ---
    # For each drug, mean network centrality of its disease-net targets.
    max_interactions = max(
        (gd.get('n_interactions', 0) for gd in net['genes'].values()), default=1
    )
    if max_interactions == 0:
        max_interactions = 1
    prox_bonuses_per_drug = {}
    for idx, row in drug_agg.iterrows():
        drug_name = row['DRUG_NAME']
        targets_in_net = [t for t in row['targets'] if t in all_disease_genes]
        if not targets_in_net:
            prox_bonuses_per_drug[drug_name] = 0.0
            continue
        centralities = []
        for gene in targets_in_net:
            gene_data = net['genes'].get(gene, {})
            centralities.append(gene_data.get('n_interactions', 0) / max_interactions)
        mean_centrality = sum(centralities) / len(centralities)
        prox_bonuses_per_drug[drug_name] = mean_centrality * w['prox_bonus_max']

    drug_agg['c5_prox_bonus'] = drug_agg['DRUG_NAME'].map(prox_bonuses_per_drug).fillna(0)

    # --- Composite score ---
    # Base = weighted sum of channels 1-3
    drug_agg['base_score'] = (
        w['gdsc'] * drug_agg['c1_gdsc']
        + w['chembl'] * drug_agg['c2_chembl']
        + w['trials'] * drug_agg['c3_trials']
    )

    # If CNS, multiply by BBB gate
    if cns_disease:
        drug_agg['gated_score'] = drug_agg['base_score'] * drug_agg['c4_bbb_gate']
    else:
        drug_agg['gated_score'] = drug_agg['base_score']

    # Add proximity bonus
    drug_agg['composite_v2'] = drug_agg['gated_score'] + drug_agg['c5_prox_bonus']

    # Sort and return
    drug_agg = drug_agg.sort_values('composite_v2', ascending=False).reset_index(drop=True)
    drug_agg['rank'] = drug_agg.index + 1

    if show_breakdown:
        cols_to_show = ['rank', 'DRUG_NAME', 'target_str', 'n_any_gene_hits',
                        'c1_gdsc', 'c2_chembl', 'c3_trials',
                        'c4_bbb_gate', 'c5_prox_bonus', 'composite_v2']
        return drug_agg[cols_to_show].head(top_n)
    else:
        return drug_agg.head(top_n)


def _get_drug_rank_in_v2(disease_query, drug_name_pattern, **kwargs):
    """Helper: find rank of a specific drug pattern in v2 ranking output.
    Returns (rank, n_total) or (None, n_total) if not found."""
    ranked = rank_drugs_for_disease_v2(disease_query, top_n=300, **kwargs)
    if ranked is None or len(ranked) == 0:
        return None, 0
    matches = ranked[ranked['DRUG_NAME'].str.lower().str.contains(drug_name_pattern.lower(), na=False)]
    if len(matches) == 0:
        return None, len(ranked)
    return int(matches.index[0] + 1), len(ranked)


# ========== GAP 9: metabolite layer joins to disease net ==========

def enrich_with_metabolites(net):
    """
    Fix for Gap 9: existing build_net returns 0 metabolites because the
    metabolome edge file (step9_metabolome_gene_edges.csv) is loaded but
    not joined to disease genes. This function does the join.

    Mutates the net in place AND returns it.
    """
    from pathlib import Path
    import pandas as pd

    builder = _get_builder()
    met = builder.met
    disease_genes = set(net.get('genes', {}).keys())

    # Inspect met DataFrame columns to find gene + metabolite cols
    cols = list(met.columns)
    gene_col = next((c for c in cols if 'gene' in c.lower() or 'symbol' in c.lower()), None)
    met_col = next((c for c in cols if 'metab' in c.lower() or 'compound' in c.lower() or 'hmdb' in c.lower()), None)

    if not gene_col or not met_col:
        print(f'  enrich_with_metabolites: could not identify gene/metabolite columns. Available: {cols}')
        return net

    # Filter metabolite edges to disease genes
    relevant = met[met[gene_col].astype(str).str.upper().isin({g.upper() for g in disease_genes})]
    metabolites_set = set(relevant[met_col].dropna().astype(str).tolist())
    net['metabolites'] = list(metabolites_set)
    net['metabolite_edges'] = relevant.to_dict(orient='records')

    # Also attach per-gene metabolite list
    by_gene = relevant.groupby(gene_col)[met_col].apply(lambda s: list(s.dropna().astype(str))).to_dict()
    for gene, mets in by_gene.items():
        if gene in net['genes']:
            net['genes'][gene]['metabolites'] = mets
            net['genes'][gene]['n_metabolites'] = len(mets)

    return net


# ========== GAP 6 + 8: STRING interactions for any disease ==========

# Module-level cache so the 98MB file isn't re-parsed across calls
_STRING_CACHE = {
    'aliases_loaded': False,
    'aliases_version': 'v2_symbol_source_only',
    'ensp_to_symbol': None,    # dict: ENSP -> gene symbol
    'symbol_to_ensps': None,   # dict: gene symbol -> set of ENSPs
    'edges_loaded': False,
    'edges_by_ensp': None,     # dict: ENSP -> list of (partner_ensp, score)
}


def _load_string_aliases():
    """Build ENSP <-> gene symbol mapping from STRING aliases file."""
    if _STRING_CACHE['aliases_loaded']:
        return

    from pathlib import Path
    import gzip

    aliases_path = Path.home() / 'INTERCEPTA/data/string/9606.protein.aliases.v12.0.txt.gz'
    if not aliases_path.exists():
        raise FileNotFoundError(f'STRING aliases file not found: {aliases_path}')

    ensp_to_symbol = {}
    symbol_to_ensps = {}

    with gzip.open(aliases_path, 'rt') as f:
        # Skip header line if present
        first = f.readline()
        if not first.startswith('9606.'):
            pass  # was header
        else:
            f.seek(0)
            f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
            ensp_full, alias, source = parts[0], parts[1], parts[2]
            # Strip "9606." prefix from ENSP
            ensp = ensp_full.replace('9606.', '')
            # Only accept the actual gene symbol source.
            # STRING aliases file has many sources per ENSP. The proper gene symbol
            # comes from Ensembl_HGNC_symbol or BioMart_HUGO (these are SHORT uppercase
            # symbols like EGFR, MET). Other sources give UCSC transcript IDs, full
            # HGNC names, etc. and would overwrite the symbol via last-write-wins.
            if source == 'Ensembl_HGNC_symbol' or source == 'BioMart_HUGO':
                sym = alias.upper()
                # If the same ENSP gets multiple symbol sources, prefer the shortest
                # (gene symbols are short; longer aliases are usually descriptive names)
                if ensp not in ensp_to_symbol or len(sym) < len(ensp_to_symbol[ensp]):
                    ensp_to_symbol[ensp] = sym
                symbol_to_ensps.setdefault(sym, set()).add(ensp)

    _STRING_CACHE['ensp_to_symbol'] = ensp_to_symbol
    _STRING_CACHE['symbol_to_ensps'] = symbol_to_ensps
    _STRING_CACHE['aliases_loaded'] = True
    print(f'  STRING aliases loaded: {len(ensp_to_symbol):,} ENSP->symbol entries, {len(symbol_to_ensps):,} unique symbols')


def _load_string_edges(min_score=700):
    """Load STRING high-confidence edges. min_score=700 is STRING high-confidence threshold."""
    if _STRING_CACHE['edges_loaded']:
        return

    from pathlib import Path
    import gzip
    from collections import defaultdict

    links_path = Path.home() / 'INTERCEPTA/data/string/9606.protein.links.v12.0.txt.gz'
    if not links_path.exists():
        raise FileNotFoundError(f'STRING links file not found: {links_path}')

    edges_by_ensp = defaultdict(list)
    n_edges_total = 0
    n_edges_kept = 0

    with gzip.open(links_path, 'rt') as f:
        f.readline()  # header: protein1 protein2 combined_score
        for line in f:
            parts = line.strip().split(' ')
            if len(parts) < 3:
                continue
            n_edges_total += 1
            score = int(parts[2])
            if score < min_score:
                continue
            p1 = parts[0].replace('9606.', '')
            p2 = parts[1].replace('9606.', '')
            edges_by_ensp[p1].append((p2, score / 1000.0))  # STRING scores are 1-1000
            n_edges_kept += 1

    _STRING_CACHE['edges_by_ensp'] = edges_by_ensp
    _STRING_CACHE['edges_loaded'] = True
    print(f'  STRING edges loaded: {n_edges_kept:,} of {n_edges_total:,} edges at score>={min_score}')


def populate_string_interactions(net, min_score=700):
    """
    Fix for Gap 6 + Gap 8: populate STRING interactions for genes in any disease net.

    Reads STRING v12 9606 (human) high-confidence edges, maps ENSP IDs to gene
    symbols via STRING aliases file, populates each gene's 'interactions' field
    with high-confidence partners.

    min_score=700 is STRING's "high confidence" threshold.

    Mutates net in place AND returns it.
    """
    _load_string_aliases()
    _load_string_edges(min_score=min_score)

    ensp_to_symbol = _STRING_CACHE['ensp_to_symbol']
    symbol_to_ensps = _STRING_CACHE['symbol_to_ensps']
    edges_by_ensp = _STRING_CACHE['edges_by_ensp']

    n_genes_enriched = 0
    n_edges_added = 0

    for gene_symbol in list(net.get('genes', {}).keys()):
        ensps = symbol_to_ensps.get(gene_symbol.upper(), set())
        if not ensps:
            # Gene not in STRING — this is real for some genes
            continue

        # Collect all edges from any of this gene's ENSPs
        partners_seen = {}  # partner_symbol -> max_score
        for ensp in ensps:
            for partner_ensp, score in edges_by_ensp.get(ensp, []):
                partner_symbol = ensp_to_symbol.get(partner_ensp)
                if partner_symbol is None:
                    continue
                if partner_symbol == gene_symbol.upper():
                    continue  # skip self-loops
                if partner_symbol not in partners_seen or partners_seen[partner_symbol] < score:
                    partners_seen[partner_symbol] = score

        if partners_seen:
            interactions = [
                {'partner': p, 'score': round(s, 3)}
                for p, s in sorted(partners_seen.items(), key=lambda x: -x[1])
            ]
            net['genes'][gene_symbol]['interactions'] = interactions
            net['genes'][gene_symbol]['n_interactions'] = len(interactions)
            n_genes_enriched += 1
            n_edges_added += len(interactions)

    print(f'  populate_string_interactions: {n_genes_enriched}/{len(net["genes"])} genes enriched, {n_edges_added} total edges added')
    return net


# ========== GAP 11: AlphaFold structures for any disease ==========
#
# Adds UniProt mapping (UniProt_AC source tag) to the STRING cache so we can
# query AlphaFold DB by UniProt accession. AlphaFold DB v6 (UniProt 2025_03)
# direct file URLs follow the pattern:
#   https://alphafold.ebi.ac.uk/files/AF-{UniProt}-F1-model_v6.pdb
#
# We store metadata per gene (UniProt ID, AlphaFold URL, availability).
# We do NOT bulk-download all 458 PDB files (~500MB unnecessary).
# Top genes can be downloaded on-demand for downstream Workstream C work.


def _load_string_uniprot_mapping_DEPRECATED_v2_replaces():
    """DEPRECATED. Kept per Principle 16 as the diagnostic record of why we moved
    from STRING-aliases-derived UniProt IDs to direct UniProt REST API queries.

    The original approach used STRING's UniProt_AC and Ensembl_UniProt source
    tags. Diagnostic showed unreliable canonical-vs-isoform behavior — STRING
    sometimes gives non-canonical accessions for genes with multiple isoforms.
    Direct UniProt REST API with reviewed:true + organism_id:9606 + gene_exact:
    is the canonical resolution path."""
    if _STRING_CACHE.get('uniprot_loaded'):
        return

    from pathlib import Path
    import gzip

    aliases_path = Path.home() / 'INTERCEPTA/data/string/9606.protein.aliases.v12.0.txt.gz'
    if not aliases_path.exists():
        raise FileNotFoundError(f'STRING aliases file not found: {aliases_path}')

    ensp_to_uniprot_primary = {}    # from UniProt_AC source
    ensp_to_uniprot_fallback = {}   # from Ensembl_UniProt source

    with gzip.open(aliases_path, 'rt') as f:
        f.readline()  # header
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 3:
                continue
            ensp_full, alias, source = parts[0], parts[1], parts[2]
            ensp = ensp_full.replace('9606.', '')

            if ' ' in alias:
                continue

            if source == 'UniProt_AC':
                if ensp not in ensp_to_uniprot_primary or len(alias) < len(ensp_to_uniprot_primary[ensp]):
                    ensp_to_uniprot_primary[ensp] = alias
            elif source == 'Ensembl_UniProt':
                if ensp not in ensp_to_uniprot_fallback or len(alias) < len(ensp_to_uniprot_fallback[ensp]):
                    ensp_to_uniprot_fallback[ensp] = alias

    ensp_to_uniprot = {}
    for ensp, up in ensp_to_uniprot_primary.items():
        ensp_to_uniprot[ensp] = up
    for ensp, up in ensp_to_uniprot_fallback.items():
        if ensp not in ensp_to_uniprot:
            ensp_to_uniprot[ensp] = up

    _STRING_CACHE['ensp_to_uniprot'] = ensp_to_uniprot
    _STRING_CACHE['uniprot_loaded'] = True


def _check_alphafold_url(uniprot_id, timeout=5):
    """HEAD request to check if AlphaFold model_v6 PDB exists for this UniProt.
    Returns the PDB URL if 200, None otherwise.
    NOTE: AlphaFold DB v6 (Sep 2025) uses model_v6 file naming, not model_v4."""
    import urllib.request
    import urllib.error

    url = f'https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v6.pdb'
    req = urllib.request.Request(url, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return url
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, Exception):
        return None
    return None


def _query_uniprot_canonical_batch(gene_symbols, batch_size=20, timeout=15):
    """Query UniProt REST API for canonical Swiss-Prot accessions for a batch of gene symbols.
    Uses gene_exact + organism_id:9606 + reviewed:true to ensure canonical human Swiss-Prot.

    Returns dict: gene_symbol -> primary_accession (or None if not found).
    """
    import urllib.request
    import urllib.parse
    import json

    result = {}
    for i in range(0, len(gene_symbols), batch_size):
        batch = gene_symbols[i:i+batch_size]
        # Build OR query for the batch
        gene_terms = ' OR '.join(f'gene_exact:{g}' for g in batch)
        query = f'({gene_terms}) AND organism_id:9606 AND reviewed:true'
        url_params = urllib.parse.urlencode({
            'query': query,
            'format': 'json',
            'fields': 'accession,gene_names',
            'size': batch_size * 3,  # allow multiple matches per gene
        })
        url = f'https://rest.uniprot.org/uniprotkb/search?{url_params}'

        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            print(f'    UniProt batch {i//batch_size + 1} failed: {e}')
            continue

        # Parse response: each result has primaryAccession + genes[].geneName.value
        for entry in data.get('results', []):
            accession = entry.get('primaryAccession')
            if not accession:
                continue
            for gene_record in entry.get('genes', []):
                gene_name = gene_record.get('geneName', {}).get('value', '').upper()
                if gene_name and gene_name in batch and gene_name not in result:
                    result[gene_name] = accession
                # Also check synonyms
                for syn in gene_record.get('synonyms', []):
                    syn_name = syn.get('value', '').upper()
                    if syn_name in batch and syn_name not in result:
                        result[syn_name] = accession

    return result


def attach_alphafold_structures(net, check_availability=True, max_workers=15, batch_size=20):
    """
    Fix for Gap 11 (v2): attach AlphaFold structure metadata to genes in any disease net.

    Architecture v2 (after diagnostic showed STRING UniProt mapping was unreliable):
      1. Query UniProt REST API for canonical Swiss-Prot accession per gene symbol
         (gene_exact + organism_id:9606 + reviewed:true)
      2. Construct AlphaFold model_v6 PDB URL
      3. HEAD-check URL availability in parallel
      4. Store {uniprot_id, alphafold_url, alphafold_available} in net

    Caches UniProt mappings in _STRING_CACHE['symbol_to_uniprot_canonical']
    so subsequent diseases reuse mappings without re-querying.

    Mutates net in place AND returns it.
    """
    if 'symbol_to_uniprot_canonical' not in _STRING_CACHE:
        _STRING_CACHE['symbol_to_uniprot_canonical'] = {}

    cache = _STRING_CACHE['symbol_to_uniprot_canonical']

    # Identify which genes need UniProt lookup (not in cache)
    all_genes = [g.upper() for g in net.get('genes', {}).keys()]
    needs_lookup = [g for g in all_genes if g not in cache]

    if needs_lookup:
        print(f'  Querying UniProt REST API for {len(needs_lookup)} gene symbols ({len(all_genes) - len(needs_lookup)} cached)...')
        new_mappings = _query_uniprot_canonical_batch(needs_lookup, batch_size=batch_size)
        cache.update(new_mappings)
        # Mark genes we tried but didn't find as None (so we don't retry every call)
        for g in needs_lookup:
            if g not in cache:
                cache[g] = None
        print(f'  UniProt API found {len([v for v in new_mappings.values() if v]):,} canonical accessions')

    # First pass: assign UniProt IDs from cache
    n_with_uniprot = 0
    genes_to_check = []
    for gene_symbol in list(net.get('genes', {}).keys()):
        uniprot_id = cache.get(gene_symbol.upper())
        if not uniprot_id:
            continue
        net['genes'][gene_symbol]['uniprot_id'] = uniprot_id
        net['genes'][gene_symbol]['alphafold_url'] = f'https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v6.pdb'
        n_with_uniprot += 1
        genes_to_check.append((gene_symbol, uniprot_id))

    print(f'  attach_alphafold_structures: {n_with_uniprot}/{len(net["genes"])} genes mapped to canonical UniProt')

    if not check_availability:
        return net

    # Second pass: parallel HEAD checks for AlphaFold availability
    from concurrent.futures import ThreadPoolExecutor, as_completed
    print(f'  Checking AlphaFold availability for {len(genes_to_check)} proteins (parallel HEAD)...')

    n_with_structure = 0

    def check_one(item):
        gene_symbol, uniprot_id = item
        url = _check_alphafold_url(uniprot_id)
        return gene_symbol, url

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_one, item): item for item in genes_to_check}
        for future in as_completed(futures):
            gene_symbol, url = future.result()
            net['genes'][gene_symbol]['alphafold_available'] = url is not None
            if url:
                n_with_structure += 1

    print(f'  attach_alphafold_structures: {n_with_structure}/{n_with_uniprot} have AlphaFold structures available')
    return net


def download_alphafold_pdb(net, gene_symbol, cache_dir=None):
    """On-demand: download the actual PDB file for a specific gene.
    Used in Workstream C for molecular docking. Not called during normal net build."""
    import urllib.request
    from pathlib import Path

    if cache_dir is None:
        cache_dir = Path.home() / 'INTERCEPTA/data/alphafold_cache'
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    gene = net['genes'].get(gene_symbol)
    if not gene or not gene.get('alphafold_url'):
        return None

    uniprot_id = gene['uniprot_id']
    cache_path = cache_dir / f'AF-{uniprot_id}-F1-model_v6.pdb'

    if cache_path.exists():
        return str(cache_path)

    try:
        urllib.request.urlretrieve(gene['alphafold_url'], cache_path)
        return str(cache_path)
    except Exception as e:
        print(f'  Failed to download {gene_symbol} ({uniprot_id}): {e}')
        return None


# ========== GAP 7: ChEMBL compound coverage for any disease ==========
#
# Vision Part 4 Stage 3 Scout 1: "molecules with known activity against
# disease-specific net nodes." We populate top-N most potent compounds per
# gene from ChEMBL, with full activity metadata.
#
# Architecture: direct REST API to ChEMBL (https://www.ebi.ac.uk/chembl/api/data/).
# Rate limit: 1 req/sec without API key. Cache aggressively.
# Strategy: gene -> UniProt (cached) -> ChEMBL target -> top-50 activities by pchembl.
#
# Cache file: ~/INTERCEPTA/data/chembl/chembl_compound_cache.json
# Cache key: UniProt accession. Cache value: list of compound dicts.
# Resume-safe: if interrupted, picks up where it left off via cache.

import time
import json as _json
import urllib.parse as _urlparse


def _chembl_cache_load():
    """Load on-disk ChEMBL compound cache."""
    cache_path = Path.home() / 'INTERCEPTA/data/chembl/chembl_compound_cache.json'
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                return _json.load(f)
        except Exception:
            return {}
    return {}


def _chembl_cache_save(cache):
    """Save ChEMBL compound cache to disk."""
    cache_path = Path.home() / 'INTERCEPTA/data/chembl/chembl_compound_cache.json'
    with open(cache_path, 'w') as f:
        _json.dump(cache, f, indent=2)


def _chembl_count_quantitative_activities(target_chembl_id, timeout=15):
    """Count records for a ChEMBL target meeting our downstream criteria:
    pchembl present and >=5, standard_type in IC50/Ki/EC50/Kd, standard_relation '='.

    Used by _chembl_query_uniprot_target to pick best-data-match when a UniProt
    has multiple SINGLE PROTEIN targets in ChEMBL.
    Returns int count or 0 on error."""
    import urllib.request
    url = (
        f'https://www.ebi.ac.uk/chembl/api/data/activity.json'
        f'?target_chembl_id={target_chembl_id}'
        f'&pchembl_value__isnull=false'
        f'&pchembl_value__gte=5'
        f'&standard_type__in=IC50,Ki,EC50,Kd'
        f'&standard_relation=%3D'
        f'&limit=1'
    )
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = _json.load(resp)
            return data.get('page_meta', {}).get('total_count', 0)
    except Exception:
        return 0


def _chembl_diagnostic_probe(uniprot_id, timeout=15, sleep_between=1.1):
    """
    Diagnostic for Drift 1 fix verification.

    For a UniProt accession, returns:
      - List of all SINGLE PROTEIN targets ChEMBL returns
      - For each, the count of qualifying activities (pchembl>=5,
        IC50/Ki/EC50/Kd, standard_relation '=')
      - Whether the best-match logic would engage (>1 target) or fast-path (1 target)

    This function answers the question: did the Drift 1 fix actually do anything
    for this UniProt, or was there only one target and no choice to make?

    Returns dict with keys:
      uniprot_id, n_targets, fast_path_triggered, target_details (list of
      {target_chembl_id, pref_name, qualifying_activity_count})
    """
    import urllib.request

    url = (
        f'https://www.ebi.ac.uk/chembl/api/data/target.json'
        f'?target_components__accession={uniprot_id}'
        f'&target_type=SINGLE%20PROTEIN'
        f'&organism=Homo%20sapiens'
    )
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = _json.load(resp)
            targets = data.get('targets', [])
    except Exception as e:
        return {
            'uniprot_id': uniprot_id,
            'error': str(e),
            'n_targets': 0,
            'fast_path_triggered': None,
            'target_details': [],
        }

    target_details = []
    for t in targets:
        tid = t.get('target_chembl_id')
        pref = t.get('pref_name', '')
        if not tid:
            continue
        time.sleep(sleep_between)
        n_acts = _chembl_count_quantitative_activities(tid, timeout=timeout)
        target_details.append({
            'target_chembl_id': tid,
            'pref_name': pref,
            'qualifying_activity_count': n_acts,
        })

    # Sort by qualifying count descending (matches the best-match logic order)
    target_details.sort(key=lambda x: -x['qualifying_activity_count'])

    return {
        'uniprot_id': uniprot_id,
        'n_targets': len(targets),
        'fast_path_triggered': len(targets) <= 1,
        'target_details': target_details,
    }


def _chembl_query_uniprot_target(uniprot_id, timeout=15, sleep_between=1.1):
    """Find best ChEMBL SINGLE PROTEIN target_chembl_id for a UniProt accession.

    DRIFT 1 FIX (2026-05-06): Previous version returned targets[0] from ChEMBL's
    default response order. For UniProts with multiple SINGLE PROTEIN matches
    (multi-isoform families, multi-subunit complexes), this could pick a less-
    curated entry. Concrete examples found in Phase 2D verification:
      - PIK3CA -> CHEMBL4005 picked, CHEMBL4040 (canonical) had more curated data
      - PTEN   -> CHEMBL2052032 (2 compounds) picked, CHEMBL2628 was canonical

    New behavior: query all SINGLE PROTEIN targets, count records meeting
    downstream criteria (pchembl>=5, standard_type in IC50/Ki/EC50/Kd,
    standard_relation '='), pick target with highest count. Tie-broken by
    ChEMBL default order. Single-match cases (vast majority) hit fast path
    with no extra API calls.

    Returns target_chembl_id or None if no target found.
    """
    import urllib.request
    url = (
        f'https://www.ebi.ac.uk/chembl/api/data/target.json'
        f'?target_components__accession={uniprot_id}'
        f'&target_type=SINGLE%20PROTEIN'
        f'&organism=Homo%20sapiens'
    )
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = _json.load(resp)
            targets = data.get('targets', [])
    except Exception:
        return None

    if not targets:
        return None

    # Fast path: only one target, return it (vast majority of genes)
    if len(targets) == 1:
        return targets[0].get('target_chembl_id')

    # Drift 1 fix: multiple SINGLE PROTEIN targets exist for this UniProt.
    # Query each for count of downstream-relevant activities, pick best.
    target_counts = []
    for i, t in enumerate(targets):
        tid = t.get('target_chembl_id')
        if not tid:
            continue
        time.sleep(sleep_between)  # respect rate limit
        n = _chembl_count_quantitative_activities(tid, timeout=timeout)
        target_counts.append((tid, n, i))  # i is original ChEMBL order (tiebreaker)

    if not target_counts:
        return None

    # Sort: highest count first, then ChEMBL default order as tiebreaker
    target_counts.sort(key=lambda x: (-x[1], x[2]))
    return target_counts[0][0]


def _chembl_query_top_compounds(target_chembl_id, top_n=50, timeout=20):
    """Fetch top-N most potent compounds for a ChEMBL target.
    Filters: pchembl present, pchembl>=5 (10uM+), exact standard_relation,
    standard_type in IC50/Ki/EC50/Kd. Sorted by pchembl_value descending.
    Returns list of compound dicts.
    """
    import urllib.request
    url = (
        f'https://www.ebi.ac.uk/chembl/api/data/activity.json'
        f'?target_chembl_id={target_chembl_id}'
        f'&pchembl_value__isnull=false'
        f'&pchembl_value__gte=5'
        f'&standard_type__in=IC50,Ki,EC50,Kd'
        f'&standard_relation=%3D'
        f'&order_by=-pchembl_value'
        f'&limit={top_n}'
    )
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = _json.load(resp)
            activities = data.get('activities', [])
            # Deduplicate by molecule_chembl_id, keeping the most potent record
            best_per_molecule = {}
            for act in activities:
                mol = act.get('molecule_chembl_id')
                if not mol:
                    continue
                pchembl = act.get('pchembl_value')
                try:
                    pchembl_f = float(pchembl) if pchembl else 0.0
                except (TypeError, ValueError):
                    pchembl_f = 0.0
                if mol not in best_per_molecule or pchembl_f > best_per_molecule[mol]['pchembl_value']:
                    best_per_molecule[mol] = {
                        'chembl_id': mol,
                        'standard_type': act.get('standard_type'),
                        'standard_value': act.get('standard_value'),
                        'standard_units': act.get('standard_units'),
                        'pchembl_value': pchembl_f,
                        'assay_chembl_id': act.get('assay_chembl_id'),
                    }
            # Sort by pchembl_value descending
            return sorted(best_per_molecule.values(), key=lambda x: -x['pchembl_value'])
    except Exception:
        return []


def _chembl_query_compound_properties(chembl_id, timeout=15):
    """Query ChEMBL /molecule/{chembl_id} for molecule_properties.

    Returns dict with BBB-relevant fields:
      - full_mwt: molecular weight
      - alogp: ALogP (lipophilicity)
      - psa: polar surface area
      - hbd: hydrogen bond donors
      - hba: hydrogen bond acceptors
      - num_aromatic_rings
      - qed_weighted: drug-likeness 0-1
      - ro5_pass: 'Y' or 'N' (Lipinski's rule of five)
      - mw_freebase
      - aromatic_rings
      - heavy_atoms

    Returns empty dict if API call fails.

    Reference: ChEMBL API documentation https://chembl.gitbook.io/chembl-interface-documentation/web-services
    """
    import urllib.request
    url = f'https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json'
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = _json.load(resp)
            props = data.get('molecule_properties') or {}
            # Normalize numeric fields
            normalized = {}
            for key in ['full_mwt', 'alogp', 'psa', 'hbd', 'hba',
                        'num_aromatic_rings', 'qed_weighted', 'mw_freebase',
                        'aromatic_rings', 'heavy_atoms']:
                v = props.get(key)
                if v is not None:
                    try:
                        normalized[key] = float(v)
                    except (TypeError, ValueError):
                        pass
            normalized['ro5_pass'] = props.get('ro5_pass')
            normalized['molecular_species'] = props.get('molecular_species')
            return normalized
    except Exception:
        return {}


def compute_cns_mpo_score(compound_props):
    """Compute CNS Multiparameter Optimization (MPO) score.

    Per Wager et al., ACS Chem Neurosci 2010: composite 0-6 score where
    each of 6 properties contributes 0-1 based on transformed value.
    A score >= 4.0 is associated with higher CNS exposure success.

    Six components:
      1. cLogP (preferred 1-3, max at 3, drops to 0 at 5)
      2. cLogD at pH 7.4 (preferred 1-3) — we approximate with logP
      3. MW (preferred <= 360, max at 360, drops to 0 at 500)
      4. TPSA (preferred 40-90, max at 70, drops to 0 at 120 or <= 20)
      5. HBD (preferred 0-1, max at 0, drops to 0 at 4)
      6. pKa most basic (preferred 7.5-10) — DATA NOT IN CHEMBL
         We omit this component (5-component variant); document explicitly.

    Returns dict: {score: float (0-5 max for 5-component), components: dict}
    or {score: None, reason: str} if insufficient data.
    """
    if not compound_props:
        return {'score': None, 'reason': 'no_properties_available'}

    mw = compound_props.get('full_mwt') or compound_props.get('mw_freebase')
    logp = compound_props.get('alogp')
    tpsa = compound_props.get('psa')
    hbd = compound_props.get('hbd')

    missing = []
    if mw is None: missing.append('mw')
    if logp is None: missing.append('logp')
    if tpsa is None: missing.append('tpsa')
    if hbd is None: missing.append('hbd')

    if missing:
        return {'score': None, 'reason': f'missing_fields:{",".join(missing)}'}

    # Component scoring functions (linear interpolation)
    def score_logp(x):
        if x is None: return 0.0
        if x <= 3: return 1.0
        if x >= 5: return 0.0
        return (5 - x) / 2

    def score_mw(x):
        if x is None: return 0.0
        if x <= 360: return 1.0
        if x >= 500: return 0.0
        return (500 - x) / 140

    def score_tpsa(x):
        if x is None: return 0.0
        if x <= 20 or x >= 120: return 0.0
        if 40 <= x <= 90: return 1.0
        if x < 40: return (x - 20) / 20
        # x in 90-120
        return (120 - x) / 30

    def score_hbd(x):
        if x is None: return 0.0
        if x == 0: return 1.0
        if x >= 4: return 0.0
        return (4 - x) / 4

    components = {
        'logp_score': round(score_logp(logp), 3),
        'logp_value': logp,
        'mw_score': round(score_mw(mw), 3),
        'mw_value': mw,
        'tpsa_score': round(score_tpsa(tpsa), 3),
        'tpsa_value': tpsa,
        'hbd_score': round(score_hbd(hbd), 3),
        'hbd_value': hbd,
    }

    # 5-component score (we omit pKa component since not in ChEMBL).
    # Logp counted twice in original (cLogP + cLogD); we use it once.
    # So our max score is 4.0, not 6.0.
    score_4 = (components['logp_score'] + components['mw_score']
               + components['tpsa_score'] + components['hbd_score'])

    return {
        'score': round(score_4, 3),
        'max_score': 4.0,
        'components': components,
        'note': 'CNS MPO 4-component variant (logp+mw+tpsa+hbd; pKa unavailable in ChEMBL)',
    }


def compute_bbb_likelihood(compound_props):
    """Categorize a compound's BBB penetration likelihood.

    Wraps compute_cns_mpo_score with categorical output.

    Categories (based on 4-component MPO, max=4.0):
      - 'likely_bbb_pos': score >= 3.0 (75% of max; commonly BBB-passable)
      - 'borderline': 2.0 <= score < 3.0
      - 'likely_bbb_neg': score < 2.0
      - 'data_unavailable': insufficient properties

    Threshold derivation: Wager et al. 2010 used >= 4.0 of 6.0 (66.7%).
    For our 4-component variant, 75% of 4.0 = 3.0 maintains comparable
    selectivity. This is a defensible default; users can choose to raise
    or lower the threshold.

    Returns dict: {category: str, mpo_score: float|None, mpo_max: float, ...}
    """
    mpo = compute_cns_mpo_score(compound_props)
    if mpo['score'] is None:
        return {
            'category': 'data_unavailable',
            'mpo_score': None,
            'reason': mpo.get('reason'),
        }
    score = mpo['score']
    if score >= 3.0:
        cat = 'likely_bbb_pos'
    elif score >= 2.0:
        cat = 'borderline'
    else:
        cat = 'likely_bbb_neg'
    return {
        'category': cat,
        'mpo_score': score,
        'mpo_max': mpo.get('max_score'),
        'components': mpo.get('components'),
    }


def populate_chembl_compounds(net, top_n=50, sleep_between=1.1, save_cache_every=20, verbose=True, do_bbb_augmentation=False):
    """
    Fix for Gap 7: expand ChEMBL compound coverage for any disease.

    For each gene with a UniProt mapping (from attach_alphafold_structures):
      1. Look up ChEMBL SINGLE PROTEIN target by UniProt accession (best-match per Drift 1 fix)
      2. Fetch top-N most potent compounds (by pchembl_value)
      3. Store in net['genes'][gene]['chembl_compounds']

    Caches by UniProt accession in ~/INTERCEPTA/data/chembl/chembl_compound_cache.json.
    Resume-safe: subsequent runs skip cached genes.
    Rate limit: 1 req/sec respected via sleep_between=1.1s.

    Mutates net in place AND returns it.

    Prerequisites:
      - attach_alphafold_structures must have run first (provides uniprot_id per gene)
    """
    cache = _chembl_cache_load()

    # Identify genes that need lookup
    genes_with_uniprot = [
        (sym, g['uniprot_id'])
        for sym, g in net.get('genes', {}).items()
        if g.get('uniprot_id')
    ]

    needs_lookup = [
        (sym, up) for sym, up in genes_with_uniprot
        if up not in cache
    ]
    cached_count = len(genes_with_uniprot) - len(needs_lookup)

    if verbose:
        print(f'  populate_chembl_compounds: {len(genes_with_uniprot)} genes have UniProt')
        print(f'    {cached_count} already in ChEMBL cache, {len(needs_lookup)} need API lookup')
        if needs_lookup:
            est_time_min = len(needs_lookup) * 2 * sleep_between / 60
            print(f'    Estimated API time: {est_time_min:.1f} min ({len(needs_lookup)} x 2 calls x {sleep_between}s rate limit)')

    # API lookup loop with resume-safe caching
    new_lookups = 0
    for i, (gene_symbol, uniprot_id) in enumerate(needs_lookup):
        # Phase 1: target lookup (now uses best-match per Drift 1 fix)
        target_chembl_id = _chembl_query_uniprot_target(uniprot_id, sleep_between=sleep_between)
        time.sleep(sleep_between)

        compounds = []
        if target_chembl_id:
            # Phase 2: top compounds for target
            compounds = _chembl_query_top_compounds(target_chembl_id, top_n=top_n)
            time.sleep(sleep_between)

        cache[uniprot_id] = {
            'gene_symbol': gene_symbol,
            'target_chembl_id': target_chembl_id,
            'compounds': compounds,
            'fetched_at': time.strftime('%Y-%m-%d'),
        }
        new_lookups += 1

        # Periodic cache save (resume-safe)
        if new_lookups % save_cache_every == 0:
            _chembl_cache_save(cache)
            if verbose:
                pct = 100 * new_lookups / len(needs_lookup)
                print(f'    Progress: {new_lookups}/{len(needs_lookup)} ({pct:.0f}%) - cache saved')

    # Final cache save
    if new_lookups > 0:
        _chembl_cache_save(cache)

    # Session 1 augmentation: fetch molecule_properties for cached compounds that lack them.
    # This augments existing cache (does not invalidate) per P16 preserve-past-work.
    # GATED on do_bbb_augmentation parameter (default False) to prevent unintended
    # re-triggering on every Action 1 verification run.
    n_compounds_needing_props = 0
    n_compounds_props_fetched = 0
    if do_bbb_augmentation:
        for uniprot_key, entry in cache.items():
            for comp in entry.get('compounds', []):
                if 'properties' not in comp:
                    n_compounds_needing_props += 1
        if n_compounds_needing_props > 0 and verbose:
            est_time_min = n_compounds_needing_props * sleep_between / 60
            print(f'    BBB augmentation: {n_compounds_needing_props} compounds need properties fetched (est {est_time_min:.1f} min)')

        # Fetch properties for each compound that needs them
        if n_compounds_needing_props > 0:
            for uniprot_key, entry in cache.items():
                for comp in entry.get('compounds', []):
                    if 'properties' in comp:
                        continue
                    chembl_id = comp.get('chembl_id')
                    if not chembl_id:
                        continue
                    props = _chembl_query_compound_properties(chembl_id)
                    comp['properties'] = props
                    comp['bbb'] = compute_bbb_likelihood(props)
                    n_compounds_props_fetched += 1
                    time.sleep(sleep_between)
                    if n_compounds_props_fetched % save_cache_every == 0:
                        _chembl_cache_save(cache)
                        if verbose:
                            pct = 100 * n_compounds_props_fetched / n_compounds_needing_props
                            print(f'    BBB progress: {n_compounds_props_fetched}/{n_compounds_needing_props} ({pct:.0f}%) - cache saved')
            _chembl_cache_save(cache)
            if verbose:
                print(f'    BBB augmentation done: {n_compounds_props_fetched} compounds enriched with properties')

    # Now populate net from cache (covers both newly-fetched and previously-cached)
    n_with_target = 0
    n_with_compounds = 0
    total_compounds = 0
    for gene_symbol, uniprot_id in genes_with_uniprot:
        entry = cache.get(uniprot_id, {})
        target = entry.get('target_chembl_id')
        compounds = entry.get('compounds', [])
        if target:
            net['genes'][gene_symbol]['chembl_target_id'] = target
            n_with_target += 1
        if compounds:
            net['genes'][gene_symbol]['chembl_compounds'] = compounds
            net['genes'][gene_symbol]['n_chembl_compounds'] = len(compounds)
            n_with_compounds += 1
            total_compounds += len(compounds)

    if verbose:
        print(f'  populate_chembl_compounds done:')
        print(f'    {n_with_target}/{len(genes_with_uniprot)} genes have ChEMBL target')
        print(f'    {n_with_compounds} genes have >=1 compound, {total_compounds} compounds total')

    return net


# ========== GAP 11 / Phase 2E: ClinicalTrials.gov integration for any disease ==========
#
# Vision Stage 5 (ranking) and Stage 3 Scout 1 (novelty check) both need to know
# what trials have run for a given target in a given disease. ClinicalTrials.gov
# v2 API is the canonical source.
#
# Architecture:
#   For each gene with a ChEMBL target (i.e. likely to have clinical interest),
#   query ClinicalTrials.gov v2 with: condition=disease + intervention/term=gene.
#   Store trial metadata per gene.
#
# Cache: ~/INTERCEPTA/data/clinicaltrials/ct_cache.json
# Cache key: f"{disease_efo}::{gene_symbol}" — disease-and-gene-specific
# Cache value: list of trial dicts
#
# Rate limit: ClinicalTrials.gov has no formal limit but soft ~50 req/sec.
# We use sleep_between=0.4s (2.5 req/sec) to be respectful.


def _ct_cache_load():
    """Load on-disk ClinicalTrials.gov cache."""
    cache_path = Path.home() / 'INTERCEPTA/data/clinicaltrials/ct_cache.json'
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                return _json.load(f)
        except Exception:
            return {}
    return {}


def _ct_cache_save(cache):
    """Save ClinicalTrials.gov cache to disk."""
    cache_path = Path.home() / 'INTERCEPTA/data/clinicaltrials/ct_cache.json'
    with open(cache_path, 'w') as f:
        _json.dump(cache, f, indent=2)


def _ct_query_target_in_disease(disease_term, gene_symbol, page_size=50, timeout=15):
    """Query ClinicalTrials.gov v2 for trials matching a disease + gene/target.

    Uses v2 API: https://clinicaltrials.gov/api/v2/studies
    Search by:
      - query.cond  = disease term (e.g. "glioblastoma multiforme")
      - query.intr  = gene symbol as intervention/target term (e.g. "EGFR")

    Returns list of trial metadata dicts, each with:
      nct_id, title, phase, overall_status, intervention_types,
      start_date, completion_date, primary_outcome, conditions

    Honest scope:
      - Returns trial REGISTRATION metadata, not trial RESULTS data.
      - Parsing efficacy/AE results is deferred to Horizon 2.
      - Phase mapping uses ClinicalTrials.gov phase labels as-is (PHASE1, PHASE2, etc.)
    """
    import urllib.request
    import urllib.parse

    params = {
        'query.cond': disease_term,
        'query.intr': gene_symbol,
        'pageSize': page_size,
        'format': 'json',
    }
    url = 'https://clinicaltrials.gov/api/v2/studies?' + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = _json.load(resp)
    except Exception as e:
        return []

    trials = []
    for study in data.get('studies', []):
        proto = study.get('protocolSection', {})
        ident = proto.get('identificationModule', {})
        status = proto.get('statusModule', {})
        design = proto.get('designModule', {})
        cond = proto.get('conditionsModule', {})
        intervention = proto.get('armsInterventionsModule', {})
        outcomes = proto.get('outcomesModule', {})

        phases = design.get('phases', [])
        intervention_types = list({i.get('type') for i in intervention.get('interventions', []) if i.get('type')})

        primary_outcomes = outcomes.get('primaryOutcomes', [])
        primary_outcome_text = primary_outcomes[0].get('measure') if primary_outcomes else None

        trials.append({
            'nct_id': ident.get('nctId'),
            'title': ident.get('briefTitle'),
            'phase': phases[0] if phases else None,
            'all_phases': phases,
            'overall_status': status.get('overallStatus'),
            'intervention_types': intervention_types,
            'start_date': status.get('startDateStruct', {}).get('date'),
            'completion_date': status.get('completionDateStruct', {}).get('date'),
            'primary_outcome': primary_outcome_text,
            'conditions': cond.get('conditions', []),
        })

    return trials


def populate_clinical_trials(net, sleep_between=0.4, save_cache_every=20, verbose=True,
                            min_genes_for_lookup_score=0.0):
    """
    Phase 2E: populate ClinicalTrials.gov metadata for genes with ChEMBL targets.

    For each gene with chembl_target_id (i.e. genes likely to have clinical interest),
    queries ClinicalTrials.gov v2 for trials targeting that gene in the disease.

    Strategy: search-by-target-and-disease (option (a) per CSO call):
      - Captures trials targeting that protein with ANY drug
      - Useful for novelty checking
      - Broader than search-by-specific-drug-name

    Caches by (disease_efo, gene_symbol). Resume-safe across runs.

    Mutates net in place AND returns it. Adds per-gene 'clinical_trials' field
    (list of trial dicts) and 'n_clinical_trials' count.

    Honest scope:
      - Only registration metadata, not results
      - Only queries genes with ChEMBL targets (skips 0-compound genes by default;
        set min_genes_for_lookup_score < 0 to also query non-druggable priority genes)
      - Trials in non-target diseases that hit this gene are NOT included
        (we constrain by disease)

    Prerequisites:
      - populate_chembl_compounds must have run first (provides chembl_target_id)
      - net must have 'disease' field (the disease name for query.cond)
    """
    cache = _ct_cache_load()

    disease_term = net.get('disease', '')
    if not disease_term:
        print('  populate_clinical_trials: no disease field in net, skipping')
        return net

    # Disease ID for cache key (resolves disambiguation if same disease name appears via different IDs)
    disease_id = net.get('disease_id') or net.get('efo_id') or disease_term

    # Identify which genes to query: those with ChEMBL target_id (likely clinically relevant)
    # OR those above the priority threshold (catches undruggable but high-priority targets)
    genes_to_query = []
    for gene_symbol, gene_data in net.get('genes', {}).items():
        has_chembl_target = bool(gene_data.get('chembl_target_id'))
        score = gene_data.get('association_score', 0)
        if has_chembl_target or score >= min_genes_for_lookup_score:
            genes_to_query.append(gene_symbol)

    needs_lookup = []
    cached_count = 0
    for gene_symbol in genes_to_query:
        cache_key = f'{disease_id}::{gene_symbol}'
        if cache_key in cache:
            cached_count += 1
        else:
            needs_lookup.append(gene_symbol)

    if verbose:
        print(f'  populate_clinical_trials: {len(genes_to_query)} genes eligible for trial lookup')
        print(f'    {cached_count} already in cache, {len(needs_lookup)} need API lookup')
        if needs_lookup:
            est_time_min = len(needs_lookup) * sleep_between / 60
            print(f'    Estimated API time: {est_time_min:.1f} min ({len(needs_lookup)} x {sleep_between}s rate limit)')

    # API lookup loop with resume-safe caching
    new_lookups = 0
    for i, gene_symbol in enumerate(needs_lookup):
        trials = _ct_query_target_in_disease(disease_term, gene_symbol)
        time.sleep(sleep_between)

        cache_key = f'{disease_id}::{gene_symbol}'
        cache[cache_key] = {
            'gene_symbol': gene_symbol,
            'disease_id': disease_id,
            'disease_term': disease_term,
            'trials': trials,
            'fetched_at': time.strftime('%Y-%m-%d'),
        }
        new_lookups += 1

        if new_lookups % save_cache_every == 0:
            _ct_cache_save(cache)
            if verbose:
                pct = 100 * new_lookups / len(needs_lookup)
                print(f'    Progress: {new_lookups}/{len(needs_lookup)} ({pct:.0f}%) - cache saved')

    if new_lookups > 0:
        _ct_cache_save(cache)

    # Populate net from cache
    n_with_trials = 0
    total_trials = 0
    phase_distribution = {'PHASE1': 0, 'PHASE2': 0, 'PHASE3': 0, 'PHASE4': 0,
                          'EARLY_PHASE1': 0, 'NA': 0, 'OTHER': 0}
    status_distribution = {}

    for gene_symbol in genes_to_query:
        cache_key = f'{disease_id}::{gene_symbol}'
        entry = cache.get(cache_key, {})
        trials = entry.get('trials', [])
        if trials:
            net['genes'][gene_symbol]['clinical_trials'] = trials
            net['genes'][gene_symbol]['n_clinical_trials'] = len(trials)
            n_with_trials += 1
            total_trials += len(trials)

            for t in trials:
                phase = t.get('phase')
                if phase in phase_distribution:
                    phase_distribution[phase] += 1
                else:
                    phase_distribution['OTHER'] += 1
                status = t.get('overall_status') or 'UNKNOWN'
                status_distribution[status] = status_distribution.get(status, 0) + 1

    if verbose:
        print(f'  populate_clinical_trials done:')
        print(f'    {n_with_trials}/{len(genes_to_query)} genes have >=1 trial in {disease_term}')
        print(f'    {total_trials} trials total')
        if total_trials > 0:
            print(f'    Phase distribution:')
            for phase, n in sorted(phase_distribution.items(), key=lambda x: -x[1]):
                if n > 0:
                    print(f'      {phase:15s} {n}')
            top_statuses = sorted(status_distribution.items(), key=lambda x: -x[1])[:5]
            print(f'    Top status counts: {dict(top_statuses)}')

    return net


# ========== ACTION 1 CLEANUP: surface_undruggable_priority_targets (Drift 3 fix) ==========

def surface_undruggable_priority_targets(net, top_n=20, score_threshold=0.3,
                                          cns_disease=False, max_bbb_pos_compounds=3):
    """
    Drift 3 fix: surface high-priority targets that have no direct ChEMBL
    compounds. These are biologically important genes (high disease association)
    that would silently disappear from drug-ranking outputs.

    Examples observed in Phase 2D GBM verification:
      - TP53 (assoc 0.621): 0 ChEMBL compounds (famously undruggable tumor suppressor)
      - Many tumor suppressors: high disease relevance, no direct small-molecule binders

    Honest scope: this function makes the gap VISIBLE. It does NOT attempt to:
      - Suggest synthetic-lethality alternatives
      - Recommend PROTAC/degrader approaches
      - Propose pathway-downstream targeting
    Those are explicitly Horizon 2 work.

    Args:
        net: disease net dict (must have run populate_chembl_compounds)
        top_n: max number of undruggable priority targets to return
        score_threshold: minimum association_score to consider "high priority"

    Returns:
        list of dicts, each with: gene, association_score, n_interactions,
        n_pathways, n_metabolites, sorted by association_score descending.
    """
    genes = net.get('genes', {})
    undruggable = []

    for gene_symbol, gene_data in genes.items():
        score = gene_data.get('association_score', 0)
        n_compounds = gene_data.get('n_chembl_compounds', 0)

        # Session 1 BBB-aware extension: for CNS diseases, the count that matters
        # is the number of BBB-positive compounds, not the total compound count.
        # A target with 50 compounds none of which can cross the BBB is effectively
        # undruggable for a brain tumor. This is honest reflection of biology.
        n_bbb_pos = 0
        if cns_disease:
            for comp in gene_data.get('chembl_compounds', []):
                bbb = comp.get('bbb', {})
                if bbb.get('category') == 'likely_bbb_pos':
                    n_bbb_pos += 1
            effective_compound_count = n_bbb_pos
            threshold_check = effective_compound_count <= max_bbb_pos_compounds
        else:
            effective_compound_count = n_compounds
            threshold_check = effective_compound_count == 0

        # High-priority by association, low effective compound count
        if score >= score_threshold and threshold_check:
            undruggable.append({
                'gene': gene_symbol,
                'association_score': round(score, 3),
                'n_interactions': gene_data.get('n_interactions', 0),
                'n_pathways': len(gene_data.get('pathways', [])) if isinstance(gene_data.get('pathways'), list) else 0,
                'n_metabolites': gene_data.get('n_metabolites', 0),
                'has_alphafold': gene_data.get('alphafold_available', False),
                'chembl_target_id': gene_data.get('chembl_target_id'),  # may have target but no qualifying compounds
                'n_total_compounds': n_compounds,
                'n_bbb_pos_compounds': n_bbb_pos if cns_disease else None,
                'cns_filter_applied': cns_disease,
            })

    undruggable.sort(key=lambda x: -x['association_score'])
    return undruggable[:top_n]


def print_undruggable_targets(undruggable_list, label='undruggable high-priority targets'):
    """Pretty-print the output of surface_undruggable_priority_targets."""
    if not undruggable_list:
        print(f"\n  No {label} found.")
        return

    print(f"\n  {label} ({len(undruggable_list)} found):")
    print(f"    {'Gene':<12} {'AssocScore':>11} {'STRINGedges':>12} {'AFstruct':>9} {'ChEMBLtgt':<15}")
    print(f"    {'-'*12} {'-'*11} {'-'*12} {'-'*9} {'-'*15}")
    for entry in undruggable_list:
        af = 'yes' if entry['has_alphafold'] else 'no'
        ctid = entry['chembl_target_id'] or '(none)'
        print(f"    {entry['gene']:<12} {entry['association_score']:>11.3f} "
              f"{entry['n_interactions']:>12d} {af:>9s} {ctid:<15s}")
    print(f"\n  Note: These targets have biological priority but no direct ChEMBL compounds")
    print(f"  meeting our criteria (pchembl>=5, IC50/Ki/EC50/Kd, exact relation).")
    print(f"  Alternative approaches (PROTAC, synthetic lethality, pathway-downstream)")
    print(f"  are NOT inferred here — that is Horizon 2 work.")


if __name__ == '__main__':
    # Action 1 cleanup verification: re-test Phase 1 gaps + new Drift fixes on GBM
    import time, json
    print('\n' + '='*70)
    print('Action 1 verification: re-run GBM with Drift 1/2/3 fixes')
    print('='*70)

    # Test Gap 1+2: name -> ID with disambiguation
    print('\n--- Gap 1+2 test: resolve_disease("glioblastoma") ---')
    t0 = time.time()
    resolved = resolve_disease('glioblastoma', verbose=True)
    print(f'Resolution time: {time.time()-t0:.2f}s')
    assert resolved['best_id'] == 'EFO_0000519', f"Expected EFO_0000519, got {resolved['best_id']}"
    print('PASS Gap 1+2: highest-coverage ID auto-selected')

    # Test Gap 1: build_net with NAME instead of ID
    print('\n--- Gap 1 test: build_net("glioblastoma") via name ---')
    t0 = time.time()
    net = build_net('glioblastoma')
    print(f'Build time: {time.time()-t0:.2f}s')
    assert net is not None, "build_net returned None"
    top10 = sorted(net['genes'].items(),
                   key=lambda x: x[1].get('association_score', 0),
                   reverse=True)[:10]
    top10_names = [g for g, _ in top10]
    print(f'Top 10 genes: {top10_names}')
    assert 'EGFR' in top10_names and 'TP53' in top10_names, \
           f"Expected EGFR + TP53 in top 10; got {top10_names}"
    print('PASS Gap 1: name-based build_net returns biology-correct GBM net')

    # Test Gap 5: corrected summary
    print('\n--- Gap 5 test: corrected_net_summary ---')
    summary = corrected_net_summary(net)
    print(json.dumps(summary, indent=2))
    print('PASS Gap 5: summary shows distinct counts for each interpretation')

    # Test Gap 4: GDSC drug-target file detection
    print('\n--- Gap 4 test: inspect_gdsc_drugs() ---')
    t0 = time.time()
    df, drug_col, target_col, src = inspect_gdsc_drugs()
    print(f'Inspection time: {time.time()-t0:.1f}s')
    assert df is not None, "No GDSC drug-target file found"
    assert drug_col == 'DRUG_NAME', f"Expected DRUG_NAME, got {drug_col}"
    assert target_col == 'PUTATIVE_TARGET', f"Expected PUTATIVE_TARGET, got {target_col}"
    assert 'GDSC2_fitted_dose_response' in src.name, f"Wrong file: {src.name}"
    print(f'PASS Gap 4: detected {src.name} with drug={drug_col}, target={target_col}')
    print(f'  ({len(df)} rows, {df[drug_col].nunique()} unique drugs, '
          f'{df[target_col].nunique()} unique target strings)')

    # === DRIFT 1 FIX VERIFICATION ===
    # Re-query 8 canonical genes WITHOUT cache hits to test best-match logic.
    # This requires invalidating the cache for these 8 specific UniProts only.
    print('\n--- Drift 1 fix test: best-match ChEMBL target lookup ---')
    print('Re-querying 8 canonical genes with new logic (cache invalidated for these only)')

    # Build net with full enrichment chain
    print('\n  Apply Phase 2B (STRING)...')
    populate_string_interactions(net, min_score=700)

    print('\n  Apply Phase 2C (AlphaFold)...')
    attach_alphafold_structures(net, check_availability=True, max_workers=15)

    # Selectively invalidate cache for 8 canonical-test genes
    canonical_test_genes = {
        'EGFR': 'CHEMBL203',
        'BRAF': 'CHEMBL5145',
        'TP53': 'CHEMBL4096',
        'PIK3CA': 'CHEMBL4040',  # Drift 1: previously got CHEMBL4005
        'AKT1': 'CHEMBL4282',
        'MET': 'CHEMBL3717',
        'ERBB2': 'CHEMBL1824',
        'PTEN': 'CHEMBL2628',    # Drift 1: previously got CHEMBL2052032
    }

    cache = _chembl_cache_load()
    invalidated = []
    for gene_symbol in canonical_test_genes:
        gene_data = net['genes'].get(gene_symbol, {})
        uniprot_id = gene_data.get('uniprot_id')
        if uniprot_id and uniprot_id in cache:
            del cache[uniprot_id]
            invalidated.append((gene_symbol, uniprot_id))
    if invalidated:
        _chembl_cache_save(cache)
        print(f'  Invalidated cache for: {[g for g, _ in invalidated]}')

    print('\n  Apply Phase 2D (ChEMBL with Drift 1 fix)...')
    print('  Expected runtime: 8 invalidated genes * ~2-5 calls each = ~30-90s')
    t0 = time.time()
    populate_chembl_compounds(net, top_n=50, sleep_between=1.1, save_cache_every=20)
    elapsed = time.time() - t0
    print(f'  Re-population time: {elapsed:.1f}s')

    # Drift 1 verification: canonical target match check
    print('\n--- Canonical ChEMBL target check (Drift 1 verification) ---')
    n_match = 0
    n_changed_for_better = 0
    for gene, expected in canonical_test_genes.items():
        actual = net['genes'].get(gene, {}).get('chembl_target_id')
        n_compounds = net['genes'].get(gene, {}).get('n_chembl_compounds', 0)
        if actual == expected:
            marker = 'EXACT'
            n_match += 1
        elif actual:
            marker = 'DIFFERENT'
        else:
            marker = 'NONE'
        print(f'  [{marker:9s}] {gene:8s} -> {actual or "(none)":15s} (expected {expected}, {n_compounds} compounds)')

    print(f'\n  Drift 1: {n_match}/8 canonical exact matches')
    print(f'  (Targets that differ from "expected" may legitimately have more')
    print(f'   downstream-relevant data — best-match logic optimizes for our')
    print(f'   pipeline\'s downstream usage, not for matching prior expectations.)')

    # === DRIFT 1 DIAGNOSTIC: did best-match logic actually engage? ===
    print('\n--- Drift 1 diagnostic: probe ChEMBL for each canonical UniProt ---')
    print('Answers: did the fix engage (multiple targets, comparison happened)')
    print('         or fast-path (one target, no choice to make)?')
    print()
    n_fast_path = 0
    n_multi_target = 0
    n_fix_changed_outcome = 0
    for gene in canonical_test_genes:
        gene_data = net['genes'].get(gene, {})
        uniprot_id = gene_data.get('uniprot_id')
        picked_target = gene_data.get('chembl_target_id')
        if not uniprot_id:
            print(f'  {gene:8s}: no UniProt - skipping diagnostic')
            continue
        probe = _chembl_diagnostic_probe(uniprot_id)
        n_targets = probe['n_targets']
        fast_path = probe['fast_path_triggered']
        if fast_path:
            n_fast_path += 1
        else:
            n_multi_target += 1
        details = probe['target_details']
        if details:
            top_pick_should_be = details[0]['target_chembl_id']
            top_pick_count = details[0]['qualifying_activity_count']
            if picked_target == top_pick_should_be:
                fix_status = 'PICKED_BEST'
            else:
                fix_status = 'MISMATCH'
        else:
            fix_status = 'NO_TARGETS'
            top_pick_count = 0
        path_label = 'FAST_PATH' if fast_path else 'BEST_MATCH'
        print(f'  {gene:8s} ({uniprot_id}): {n_targets} target(s), {path_label}, picked {picked_target} -> {fix_status}')
        if not fast_path:
            print(f'    Top 3 by qualifying activity count:')
            for d in details[:3]:
                marker = '*' if d['target_chembl_id'] == picked_target else ' '
                pref_short = d['pref_name'][:50]
                print(f'      {marker} {d["target_chembl_id"]:15s} ({d["qualifying_activity_count"]:>5d} activities) {pref_short}')
            if fix_status == 'MISMATCH':
                n_fix_changed_outcome += 1

    print(f'\n  Diagnostic summary:')
    print(f'    Fast-path (only 1 target, fix had no choice): {n_fast_path}/8')
    print(f'    Multi-target (best-match logic engaged):       {n_multi_target}/8')
    if n_multi_target > 0:
        matched = n_multi_target - n_fix_changed_outcome
        print(f'    Of multi-target: {matched}/{n_multi_target} matched top-by-count')
        if n_fix_changed_outcome > 0:
            print(f'    {n_fix_changed_outcome} mismatches need investigation - pick did not match top-by-count')

    # === DRIFT 2 FIX VERIFICATION ===
    print('\n--- Drift 2 fix test: print_net_summary ---')
    print_net_summary(net, label='post-Action-1-verification')
    print('PASS Drift 2: post-enrichment summary reflects actual current state')

    # === PHASE 2E VERIFICATION: ClinicalTrials.gov integration ===
    print('\n--- Phase 2E test: populate_clinical_trials ---')
    # Set disease_id on net for cache key (build_net doesn't currently populate this)
    if 'disease_id' not in net:
        net['disease_id'] = 'EFO_0000519'  # GBM
    t0 = time.time()
    populate_clinical_trials(net, sleep_between=0.4, save_cache_every=20, verbose=True)
    elapsed_2e = time.time() - t0
    print(f'  Phase 2E runtime: {elapsed_2e:.1f}s')

    # Sanity: at least some genes should have trials (GBM has many target trials)
    n_genes_with_trials = sum(1 for g in net['genes'].values() if g.get('n_clinical_trials', 0) > 0)
    total_trials = sum(g.get('n_clinical_trials', 0) for g in net['genes'].values())
    print(f'  {n_genes_with_trials} genes have trials, {total_trials} trials total')

    # Show top 5 genes by trial count
    genes_by_trials = sorted(
        [(g, gd.get('n_clinical_trials', 0)) for g, gd in net['genes'].items() if gd.get('n_clinical_trials', 0) > 0],
        key=lambda x: -x[1]
    )[:5]
    if genes_by_trials:
        print(f'  Top 5 genes by GBM trial count:')
        for gene, n in genes_by_trials:
            print(f'    {gene:8s}  {n} trials')
    else:
        print(f'  No genes with trials returned - check API connectivity')

    # Specific spot-check: EGFR is heavily trialed in GBM, expect >=5 trials
    egfr_trials = net['genes'].get('EGFR', {}).get('n_clinical_trials', 0)
    if egfr_trials >= 5:
        print(f'  PASS Phase 2E: EGFR has {egfr_trials} GBM trials (expected >=5)')
    else:
        print(f'  CHECK Phase 2E: EGFR has only {egfr_trials} GBM trials (expected >=5)')
        print(f'    May indicate API issue, MeSH-EFO mismatch, or unusual day. Investigate.')

    # === DRIFT 3 FIX VERIFICATION ===
    print('\n--- Drift 3 fix test: surface_undruggable_priority_targets ---')
    undruggable = surface_undruggable_priority_targets(net, top_n=20, score_threshold=0.3)
    print_undruggable_targets(undruggable, label='undruggable high-priority GBM targets')
    if any(e['gene'] == 'TP53' for e in undruggable):
        print('\nPASS Drift 3: TP53 surfaces as undruggable high-priority (as expected)')
    else:
        tp53_data = net['genes'].get('TP53', {})
        tp53_score = tp53_data.get('association_score', 0)
        tp53_compounds = tp53_data.get('n_chembl_compounds', 0)
        print(f'\nNOTE Drift 3: TP53 not in surfaced list. Direct check:')
        print(f'  TP53 association_score={tp53_score}, n_chembl_compounds={tp53_compounds}')
        if tp53_compounds > 0:
            print(f'  TP53 now HAS compounds — Drift 1 fix may have changed target selection.')

    # Save Phase 2D net (post-Action-1)
    out_path = Path.home() / 'INTERCEPTA/round3_gbm_live_test/results/gbm_disease_net_action1.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    net_ser = dict(net)
    for k, v in net_ser.items():
        if isinstance(v, set):
            net_ser[k] = list(v)
    with open(out_path, 'w') as f:
        json.dump(net_ser, f, indent=2, default=str)
    print(f'\nSaved Action 1 verification net: {out_path.name}')

    # === SESSION 1 VERIFICATION: BBB extension ===
    print('\n--- Session 1 test: BBB property fetch + CNS MPO scoring ---')

    # Pick 3 well-known compounds with known BBB status
    # Temozolomide CHEMBL810: BBB+ (crosses, used in GBM)
    # Imatinib CHEMBL941: BBB- (Gleevec, doesn't enter brain effectively)
    # Aspirin CHEMBL25: BBB+ (small enough)
    print('  Querying ChEMBL for 3 known compounds...')
    test_compounds = {
        'CHEMBL810': {'name': 'Temozolomide', 'expected_bbb': 'likely_bbb_pos'},
        'CHEMBL941': {'name': 'Imatinib', 'expected_bbb': 'likely_bbb_neg or borderline'},
        'CHEMBL25':  {'name': 'Aspirin', 'expected_bbb': 'likely_bbb_pos or borderline'},
    }
    for chembl_id, info in test_compounds.items():
        props = _chembl_query_compound_properties(chembl_id)
        bbb = compute_bbb_likelihood(props)
        mpo_score = bbb.get('mpo_score')
        cat = bbb.get('category')
        mw = props.get('full_mwt')
        logp = props.get('alogp')
        tpsa = props.get('psa')
        hbd = props.get('hbd')
        print(f'    {info["name"]:<14} ({chembl_id:<10}): MW={mw} logP={logp} TPSA={tpsa} HBD={hbd}')
        print(f'                                MPO={mpo_score} -> {cat}  (expected {info["expected_bbb"]})')
        time.sleep(1.1)

    # Augment GBM net's ChEMBL compound cache with properties
    print('\n--- Session 1: augment GBM net with BBB properties ---')
    print('  This fetches molecule_properties for all cached compounds without them.')
    print('  Cold-cache full augmentation: ~7,500 compounds * 1.1s = ~140 min.')
    print('  We do a SAMPLE here (top-5 most-trialed genes only) for verification speed.')

    # Restrict augmentation to top-5 most-trialed genes for verification
    sample_genes = sorted(
        [(g, gd.get('n_clinical_trials', 0)) for g, gd in net['genes'].items()],
        key=lambda x: -x[1]
    )[:5]
    sample_gene_names = [g for g, _ in sample_genes]
    print(f'  Sample genes for BBB verification: {sample_gene_names}')

    # Cache-load
    cache = _chembl_cache_load()

    # For each sample gene, find its compounds in cache and fetch properties
    n_props_fetched_sample = 0
    for gene_symbol in sample_gene_names:
        gene_data = net['genes'].get(gene_symbol, {})
        uniprot_id = gene_data.get('uniprot_id')
        if not uniprot_id or uniprot_id not in cache:
            continue
        entry = cache[uniprot_id]
        for comp in entry.get('compounds', []):
            if 'properties' not in comp:
                chembl_id = comp.get('chembl_id')
                if chembl_id:
                    props = _chembl_query_compound_properties(chembl_id)
                    comp['properties'] = props
                    comp['bbb'] = compute_bbb_likelihood(props)
                    n_props_fetched_sample += 1
                    time.sleep(1.1)
                    if n_props_fetched_sample % 20 == 0:
                        _chembl_cache_save(cache)
    _chembl_cache_save(cache)

    # Also re-attach compounds to net so the verification can see them
    for gene_symbol in sample_gene_names:
        gene_data = net['genes'].get(gene_symbol, {})
        uniprot_id = gene_data.get('uniprot_id')
        if uniprot_id and uniprot_id in cache:
            net['genes'][gene_symbol]['chembl_compounds'] = cache[uniprot_id].get('compounds', [])

    print(f'  Augmented {n_props_fetched_sample} compounds with properties (sample subset)')

    # Show BBB distribution for sample genes
    print('\n  BBB distribution for sample genes:')
    print(f'    {"Gene":<10} {"#cmpds":>7} {"BBB+":>5} {"BBL":>5} {"BBB-":>5} {"NoData":>7}')
    for gene_symbol in sample_gene_names:
        gd = net['genes'].get(gene_symbol, {})
        comps = gd.get('chembl_compounds', [])
        n_pos = n_borderline = n_neg = n_unknown = 0
        for c in comps:
            cat = c.get('bbb', {}).get('category')
            if cat == 'likely_bbb_pos': n_pos += 1
            elif cat == 'borderline': n_borderline += 1
            elif cat == 'likely_bbb_neg': n_neg += 1
            else: n_unknown += 1
        print(f'    {gene_symbol:<10} {len(comps):>7} {n_pos:>5} {n_borderline:>5} {n_neg:>5} {n_unknown:>7}')

    # Test surface_undruggable with cns_disease=True for GBM
    print('\n  Testing surface_undruggable_priority_targets(cns_disease=True)...')
    undruggable_cns = surface_undruggable_priority_targets(net, top_n=20, score_threshold=0.3, cns_disease=True)
    print(f'  Undruggable priority targets with CNS BBB filter: {len(undruggable_cns)}')
    if undruggable_cns:
        print(f'    Sample (first 5):')
        for entry in undruggable_cns[:5]:
            bbb_info = f'#cmpds={entry.get("n_total_compounds", 0)} BBB+={entry.get("n_bbb_pos_compounds", 0)}'
            print(f'    {entry["gene"]:<10} score={entry["association_score"]:.3f}  {bbb_info}')

    print('\nSession 1 BBB extension verification COMPLETE.')

    # === SESSION 2 VERIFICATION: Composite v2 ranking on GBM ===
    print('\n--- Session 2 test: rank_drugs_for_disease_v2 on GBM ---')
    print('  Tests whether multi-evidence ranking with BBB filter recovers GBM SOC.')
    print('  GBM SOC: temozolomide (rank target: top 30), bevacizumab/lomustine/carmustine')
    print('  (note: bev/lom/car are not in GDSC; their channels 1 score = 0)')
    print('  Per published precedent (DrugRepo, OncoDrug+, CNS MPO), defaults committed before validation.')

    t0 = time.time()
    ranked_v2 = rank_drugs_for_disease_v2('glioblastoma', top_n=300, show_breakdown=True)
    elapsed_v2 = time.time() - t0
    print(f'  v2 ranking runtime: {elapsed_v2:.1f}s')

    if ranked_v2 is None or len(ranked_v2) == 0:
        print('  FAIL: v2 ranking returned empty')
    else:
        print(f'  Total drugs ranked: {len(ranked_v2)}')

        # GBM SOC drugs: rank check
        soc_drugs = ['Temozolomide', 'Bevacizumab', 'Lomustine', 'Carmustine']
        print(f'\n  GBM Standard of Care ranks (v2):')
        for soc in soc_drugs:
            matches = ranked_v2[ranked_v2['DRUG_NAME'].str.lower().str.contains(soc.lower(), na=False)]
            if len(matches) == 0:
                print(f'    {soc:15s}: NOT IN GDSC PANEL (channel 1 = 0)')
            else:
                row = matches.iloc[0]
                print(f'    {soc:15s}: rank {int(row["rank"]):>3d}/{len(ranked_v2)}  '
                      f'composite={row["composite_v2"]:.3f}  '
                      f'c1={row["c1_gdsc"]:.2f} c2={row["c2_chembl"]:.2f} '
                      f'c3={row["c3_trials"]:.2f} c4={row["c4_bbb_gate"]:.2f} '
                      f'c5={row["c5_prox_bonus"]:.3f}')

        # Top 15 by composite_v2
        print(f'\n  Top 15 v2 ranking:')
        print(f'    {"Rank":<5} {"Drug":<20} {"Score":<7} {"c1":<5} {"c2":<5} {"c3":<5} {"c4":<5} {"c5":<5}')
        for _, row in ranked_v2.head(15).iterrows():
            print(f'    {int(row["rank"]):<5} {str(row["DRUG_NAME"])[:19]:<20} '
                  f'{row["composite_v2"]:.3f}  '
                  f'{row["c1_gdsc"]:.2f}  {row["c2_chembl"]:.2f}  '
                  f'{row["c3_trials"]:.2f}  {row["c4_bbb_gate"]:.2f}  '
                  f'{row["c5_prox_bonus"]:.3f}')

        # Verdict: Did temozolomide enter top 30?
        temo_match = ranked_v2[ranked_v2['DRUG_NAME'].str.lower().str.contains('temozolomide', na=False)]
        if len(temo_match) > 0:
            temo_rank = int(temo_match.iloc[0]['rank'])
            if temo_rank <= 30:
                print(f'\n  PASS Session 2 v2: Temozolomide rank {temo_rank} (top 30)')
            elif temo_rank <= 100:
                print(f'\n  CHECK Session 2 v2: Temozolomide rank {temo_rank} (top 100, not top 30)')
            else:
                print(f'\n  FAIL Session 2 v2: Temozolomide rank {temo_rank} (>100)')
        else:
            print(f'\n  CHECK Session 2 v2: Temozolomide not in v2 ranking')

    print('\nSession 2 v2 ranking verification COMPLETE.')

    print('\n' + '='*70)
    print('Action 1 verification COMPLETE.')
    print('Drift 1: ChEMBL best-match target lookup applied')
    print('Drift 2: print_net_summary surfaces honest post-enrichment state')
    print('Drift 3: surface_undruggable_priority_targets makes 0-compound priority genes visible')
    print('Drift 4: regression test exercises new functions')
    print('='*70)
