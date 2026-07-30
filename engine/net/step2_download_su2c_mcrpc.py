"""
INTERCEPTA Net Architecture v2.0 — Step 2
Download SU2C/PCF mCRPC genomic data from cBioPortal API.
Study: prad_su2c_2019 (Abida et al., PNAS 2019, 429 patients)
Mutations, CNVs, clinical data.

Author: Prasad Akula
"""
import json, os, time, sys
import urllib.request
import pandas as pd
import numpy as np

start = time.time()
print("=" * 70)
print("INTERCEPTA Step 2: Download SU2C mCRPC Genomic Data")
print("  Study: prad_su2c_2019 (Abida et al., PNAS 2019)")
print("  429 mCRPC patients, WES + RNA-seq")
print("=" * 70)

BASE = "https://www.cbioportal.org/api"
STUDY = "prad_su2c_2019"
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'su2c')
RESULTS = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(OUTDIR, exist_ok=True)

def api_get(endpoint, params={}):
    """Query cBioPortal REST API."""
    url = f"{BASE}/{endpoint}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k,v in params.items())
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())

# [1/5] Get study info
print("\n[1/5] Fetching study metadata...")
try:
    study = api_get(f"studies/{STUDY}")
    print(f"  Name: {study.get('name','?')}")
    print(f"  Samples: {study.get('allSampleCount','?')}")
    print(f"  Citation: {study.get('citation','?')}")
except Exception as e:
    print(f"  Error: {e}")
    sys.exit(1)

# [2/5] Get all mutations
print("\n[2/5] Downloading mutations...")
try:
    # Get molecular profile ID for mutations
    profiles = api_get(f"studies/{STUDY}/molecular-profiles")
    mut_profile = None
    cna_profile = None
    for p in profiles:
        if p.get('molecularAlterationType') == 'MUTATION_EXTENDED':
            mut_profile = p['molecularProfileId']
        if p.get('molecularAlterationType') == 'COPY_NUMBER_ALTERATION':
            if 'gistic' not in p.get('molecularProfileId','').lower():
                cna_profile = p['molecularProfileId']
    print(f"  Mutation profile: {mut_profile}")
    print(f"  CNA profile: {cna_profile}")

    # Get all samples
    samples = api_get(f"studies/{STUDY}/samples", {"pageSize": "10000"})
    sample_ids = [s['sampleId'] for s in samples]
    print(f"  Total samples: {len(sample_ids)}")

    # Download mutations in batches
    print("  Downloading mutations (may take 1-2 minutes)...")
    all_mutations = []
    batch_size = 100
    for i in range(0, len(sample_ids), batch_size):
        batch = sample_ids[i:i+batch_size]
        data = json.dumps({
            "sampleIds": batch,
            "molecularProfileId": mut_profile,
            "entrezGeneIds": []
        }).encode()
        req = urllib.request.Request(
            f"{BASE}/molecular-profiles/{mut_profile}/mutations/fetch",
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            batch_muts = json.loads(resp.read().decode())
            all_mutations.extend(batch_muts)
        print(f"    Batch {i//batch_size+1}: {len(batch_muts)} mutations "
              f"(total: {len(all_mutations)})")

    # Parse mutations
    mut_records = []
    for m in all_mutations:
        mut_records.append({
            'sample': m.get('sampleId',''),
            'patient': m.get('patientId',''),
            'gene': m.get('gene',{}).get('hugoGeneSymbol',''),
            'entrez': m.get('gene',{}).get('entrezGeneId',''),
            'mutation_type': m.get('mutationType',''),
            'protein_change': m.get('proteinChange',''),
            'variant_type': m.get('variantType',''),
            'chr': m.get('chr',''),
            'start': m.get('startPosition',''),
            'end': m.get('endPosition',''),
        })
    mut_df = pd.DataFrame(mut_records)
    mut_df.to_csv(os.path.join(OUTDIR, 'su2c_mutations.csv'), index=False)
    print(f"  Total mutations: {len(mut_df):,}")
    print(f"  Unique genes mutated: {mut_df['gene'].nunique()}")
    print(f"  Unique patients: {mut_df['patient'].nunique()}")

except Exception as e:
    print(f"  Mutation download error: {e}")
    mut_df = pd.DataFrame()

# [3/5] Get clinical data
print("\n[3/5] Downloading clinical data...")
try:
    clinical = api_get(f"studies/{STUDY}/clinical-data",
                       {"clinicalDataType": "SAMPLE", "pageSize": "100000"})
    clin_df = pd.DataFrame(clinical)
    clin_pivot = clin_df.pivot_table(
        index='sampleId', columns='clinicalAttributeId',
        values='value', aggfunc='first'
    )
    clin_pivot.to_csv(os.path.join(OUTDIR, 'su2c_clinical.csv'))
    print(f"  Clinical records: {len(clin_df):,}")
    print(f"  Unique samples: {clin_pivot.shape[0]}")
    print(f"  Clinical attributes: {clin_pivot.shape[1]}")
    if 'ABI_ENZA_EXPOSURE_STATUS' in clin_pivot.columns:
        print(f"  Abi/Enza exposure: {dict(clin_pivot['ABI_ENZA_EXPOSURE_STATUS'].value_counts())}")
except Exception as e:
    print(f"  Clinical download error: {e}")
    clin_pivot = pd.DataFrame()

# [4/5] Compute mutation frequencies
print("\n[4/5] Computing mutation frequencies...")
if len(mut_df) > 0:
    n_patients = mut_df['patient'].nunique()
    gene_freq = mut_df.groupby('gene')['patient'].nunique().sort_values(ascending=False)
    gene_pct = (gene_freq / n_patients * 100).round(1)

    print(f"\n  Top 30 mutated genes in SU2C mCRPC (n={n_patients} patients):")
    print(f"  {'Gene':<15} {'Patients':>9} {'Frequency':>10}")
    print(f"  {'-'*15} {'-'*9} {'-'*10}")
    for gene, pct in gene_pct.head(30).items():
        cnt = gene_freq[gene]
        print(f"  {gene:<15} {cnt:>9} {pct:>9.1f}%")

    # Verify against published values
    print(f"\n  Verification against published (Robinson 2015, Abida 2019):")
    expected = {'TP53': '40-60%', 'AR': '40-60%', 'PTEN': '40-60%',
                'RB1': '~21%', 'BRCA2': '~13%', 'ATM': '~8%',
                'SPOP': '~11%', 'FOXA1': '~10%', 'PIK3CA': '~5%'}
    for gene, exp in expected.items():
        actual = f"{gene_pct.get(gene, 0):.1f}%"
        print(f"  {gene:<10} expected: {exp:<10} actual: {actual}")

    gene_pct.to_csv(os.path.join(RESULTS, 'step2_mutation_frequencies.csv'))

# [5/5] Summary
elapsed = time.time() - start
print(f"\n{'='*70}")
print(f"STEP 2 COMPLETE")
print(f"  Mutations: {len(mut_df):,} across {mut_df['gene'].nunique() if len(mut_df)>0 else 0} genes")
print(f"  Clinical: {clin_pivot.shape[0] if len(clin_pivot)>0 else 0} samples, {clin_pivot.shape[1] if len(clin_pivot)>0 else 0} attributes")
print(f"  Runtime: {elapsed:.0f}s")
print(f"  Saved to ~/INTERCEPTA/data/su2c/")
print(f"  Layer 1 (Genomic): BUILDING")
print(f"{'='*70}")
