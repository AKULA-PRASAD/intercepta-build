#!/usr/bin/env python3
"""
Add NSCLC to disease_tissue_mapping.json.

Per spec INTERCEPTA_Workstream_B_NSCLC_Specification.md Section 3 + 5
Phase 0 task 5: move NSCLC from future_diseases_planned to active
diseases section.

Bumps schema_version 1.1 -> 1.2 with amendment note.
Backs up existing config before write.
Idempotent: won't double-add if NSCLC already in diseases section.

Author: Prasad Akula & Claude (CSO), 2026-05-08
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


CONFIG_PATH = Path.home() / 'INTERCEPTA' / 'configs' / 'disease_tissue_mapping.json'
BACKUP_PATH = CONFIG_PATH.with_suffix('.json.PRE_NSCLC_BACKUP')


def main():
    print('=' * 60)
    print('Adding NSCLC to disease_tissue_mapping.json')
    print('=' * 60)

    if not CONFIG_PATH.exists():
        print(f"FAIL: Config missing: {CONFIG_PATH}")
        sys.exit(2)

    # Load existing
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    # Check current state
    diseases = config.get('diseases', {})
    future = config.get('future_diseases_planned', {})

    print(f"  Currently active diseases: {sorted(diseases.keys())}")
    print(f"  Currently planned: {sorted([k for k in future.keys() if not k.startswith('_')])}")

    # Idempotency check
    if 'nsclc' in diseases:
        print(f"\n  NSCLC already in active diseases. Nothing to do.")
        sys.exit(0)

    if 'nsclc' not in future:
        print(f"\n  NOTE: NSCLC not in future_diseases_planned either. "
              f"Adding fresh.")

    # Backup before destructive write
    if not BACKUP_PATH.exists():
        print(f"\n  Creating backup: {BACKUP_PATH.name}")
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
    else:
        print(f"\n  Backup already exists: {BACKUP_PATH.name} (preserving)")

    # Build NSCLC entry per established schema
    nsclc_entry = {
        "disease_id": "nsclc",
        "disease_full_name": "Non-Small Cell Lung Carcinoma (LUAD + LUSC)",
        "gtex_primary_tissue": "Lung",
        "gtex_comparator_tissues": ["Lung"],
        "gtex_comparator_strategy": "single_tissue",
        "tissue_proxy_caveat": None,
        "gene_list_path": "configs/genes_nsclc.json"
    }

    # Insert into active diseases
    config['diseases']['nsclc'] = nsclc_entry

    # Remove from future_diseases_planned if present (preserve _note key)
    if 'nsclc' in future:
        del config['future_diseases_planned']['nsclc']

    # Bump schema version + add amendment note
    metadata = config.get('_metadata', {})
    metadata['schema_version'] = "1.2"
    metadata['amended'] = "2026-05-08"
    prior_amendment = metadata.get('amendment_note', '')
    new_note = ("Added NSCLC to active diseases for Workstream B Phase 0. "
                "Per spec workstream-b-spec-locked. Single-tissue GTEx mapping "
                "(Lung).")
    if prior_amendment:
        metadata['amendment_note'] = prior_amendment + " | " + new_note
    else:
        metadata['amendment_note'] = new_note
    config['_metadata'] = metadata

    # Validate by re-serializing
    try:
        serialized = json.dumps(config, indent=2)
    except (TypeError, ValueError) as e:
        print(f"FAIL: Serialization error: {e}")
        sys.exit(2)

    # Write
    with open(CONFIG_PATH, 'w') as f:
        f.write(serialized)
        f.write('\n')

    # Verify by re-reading
    with open(CONFIG_PATH) as f:
        verify = json.load(f)
    if 'nsclc' not in verify['diseases']:
        print(f"FAIL: NSCLC not in active diseases after write")
        sys.exit(2)

    print(f"\n  Updated config:")
    print(f"    Active diseases: {sorted(verify['diseases'].keys())}")
    print(f"    Schema version: {verify['_metadata']['schema_version']}")
    print(f"    NSCLC entry:")
    nsclc_check = verify['diseases']['nsclc']
    for k, v in nsclc_check.items():
        print(f"      {k}: {v}")

    print(f"\n  Done. Backup at: {BACKUP_PATH.name}")
    print(f"  Next: run audit_gtex_columns.py to verify 'Lung' tissue match.")


if __name__ == '__main__':
    main()
