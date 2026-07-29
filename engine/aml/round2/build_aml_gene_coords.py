#!/usr/bin/env python3
"""
Build a small gene-coordinate cache for the 9 WES-derived mutation genes
required by Round 2.2c spec Section 5.

For each gene, fetches its genomic coordinates (chromosome, start, end) from
Ensembl REST API (free, no auth, lightweight). Builds a small JSON cache so
build_multimodal_features.py can map WES variant positions to gene symbols
without needing a multi-MB annotation file.

The genes:
  FLT3, DNMT3A, IDH1, IDH2, TET2, ASXL1, KIT, KMT2A, WT1, NRAS, KRAS

Output: ~/INTERCEPTA/round2_aml/data/aml_gene_coords.json

Usage:
  python3 build_aml_gene_coords.py

Author: Prasad Akula & Claude (CSO), 2026-05-06
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

HOME = Path.home()
OUTPUT = HOME / 'INTERCEPTA' / 'round2_aml' / 'data' / 'aml_gene_coords.json'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Genes Round 2.2c Step 1 needs from WES (clinical doesn't cover them)
# Plus NRAS, KRAS for RAS_family
GENES = ['FLT3', 'DNMT3A', 'IDH1', 'IDH2', 'TET2', 'ASXL1', 'KIT', 'KMT2A',
         'WT1', 'NRAS', 'KRAS']

# Ensembl REST API endpoint (GRCh37 to match BeatAML's alignment per BeatAML2 docs)
# BeatAML2 uses GRCh37 for all alignments
ENSEMBL_REST = 'https://grch37.rest.ensembl.org'


def fetch_gene_coords(gene_symbol):
    """Look up gene coordinates via Ensembl REST. Returns (chrom, start, end) or None."""
    url = f"{ENSEMBL_REST}/lookup/symbol/homo_sapiens/{gene_symbol}?expand=0"
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  {gene_symbol}: ERROR {e}")
        return None

    if 'seq_region_name' not in data:
        print(f"  {gene_symbol}: no seq_region in response")
        return None

    chrom = data['seq_region_name']
    # Add a small flanking region (5kb) to capture splice variants and UTRs
    start = max(0, int(data['start']) - 5000)
    end = int(data['end']) + 5000
    return {
        'chrom': str(chrom),
        'start': start,
        'end': end,
        'ensembl_start': int(data['start']),
        'ensembl_end': int(data['end']),
        'biotype': data.get('biotype', ''),
        'description': data.get('description', ''),
        'flanking_bp': 5000,
    }


def main():
    print(f"Building AML gene coordinate cache for {len(GENES)} genes...")
    print(f"Source: Ensembl GRCh37 REST (matches BeatAML2 alignment)")
    print()

    if OUTPUT.exists():
        print(f"Existing cache found at {OUTPUT}")
        with open(OUTPUT) as f:
            cache = json.load(f)
        print(f"  Cached genes: {list(cache.keys())}")
        # Refresh missing ones
        missing = [g for g in GENES if g not in cache]
        if not missing:
            print("All genes already cached. Exiting.")
            return
        print(f"  Missing: {missing}")
    else:
        cache = {}
        missing = GENES

    for gene in missing:
        print(f"  Fetching {gene}...")
        coords = fetch_gene_coords(gene)
        if coords:
            cache[gene] = coords
            print(f"    chr{coords['chrom']}:{coords['ensembl_start']}-{coords['ensembl_end']} "
                  f"({coords['biotype']})")
        else:
            print(f"    FAILED — gene will not be detectable in WES")
        time.sleep(0.5)  # Be polite to Ensembl

    with open(OUTPUT, 'w') as f:
        json.dump(cache, f, indent=2)

    print(f"\nSaved: {OUTPUT}")
    print(f"Total genes cached: {len(cache)}/{len(GENES)}")
    print("\nNow re-run build_multimodal_features.py")


if __name__ == '__main__':
    main()
