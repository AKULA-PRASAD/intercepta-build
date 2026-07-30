#!/usr/bin/env python3
"""
INTERCEPTA Workstream B Phase 1 — Aggregator (SKELETON)

Subject:    Combine per-cohort Phase 1 outputs into cross-cohort summary.
Spec:       INTERCEPTA_Workstream_B_Phase1_Specification.md §1.2 (phase1_summary.json)
Inputs:     LuCA, Wu, TCGA-LUAD, TCGA-LUSC per-cohort kaalcura_report.json files
Outputs:    data/nsclc/derived/phase1_summary.json

Author:     Prasad Akula (CSO/AI co-founder), 2026-05-10
Status:     SKELETON
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

LOG_DIR = Path('/scratch/akula.pra/INTERCEPTA/logs')
NSCLC_BASE = Path('/scratch/akula.pra/INTERCEPTA/data/nsclc')

COHORT_REPORTS = {
    'luca':       NSCLC_BASE / 'luca_salcher2022/derived/luca_kaalcura_report.json',
    'wu':         NSCLC_BASE / 'wu2021/derived/wu_kaalcura_report.json',
    'tcga_luad':  NSCLC_BASE / 'tcga_luad/derived/tcga_luad_kaalcura_report.json',
    'tcga_lusc':  NSCLC_BASE / 'tcga_lusc/derived/tcga_lusc_kaalcura_report.json',
}

OUTPUT_SUMMARY = NSCLC_BASE / 'derived/phase1_summary.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / f'phase1_aggregate_{datetime.now():%Y%m%d_%H%M%S}.log')
    ]
)
logger = logging.getLogger(__name__)


def load_cohort_report(path: Path) -> dict:
    if not path.exists():
        logger.error(f"Missing cohort report: {path}")
        return {'verdict': 'MISSING', 'path': str(path)}
    with open(path) as f:
        return json.load(f)


def aggregate_phase1():
    """
    Combine 4 per-cohort reports into single cross-cohort summary.
    Per Phase 1 spec §1.2.
    """
    OUTPUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    
    all_reports = {cohort: load_cohort_report(path) for cohort, path in COHORT_REPORTS.items()}
    
    summary = {
        'phase': 'Workstream B Phase 1',
        'spec_tag': 'workstream-b-phase1-spec-locked',
        'date': datetime.now().isoformat(),
        'cohorts': all_reports,
        'cross_cohort_summary': {
            'gene_coverage_per_axis': {
                # TODO: extract from each cohort's G1.1 result and tabulate
                'luca':       {'R_prolif': None, 'R_emt': None, 'R_ddr': None},
                'wu':         {'R_prolif': None, 'R_emt': None, 'R_ddr': None},
                'tcga_luad':  {'R_prolif': None, 'R_emt': None, 'R_ddr': None},
                'tcga_lusc':  {'R_prolif': None, 'R_emt': None, 'R_ddr': None},
            },
            'sample_size_accounting': {
                # TODO: extract n_cells/n_samples per cohort from each G1.4 result
            },
            'gate_verdicts_per_cohort': {
                # TODO: PASS/FAIL per gate per cohort
            },
            'overall_verdict': 'PASS|PASS_WITH_CAVEATS|FAIL_HONESTLY',  # per spec §10
        },
        'caveats': [
            # TODO: collect cohort-specific caveats (e.g., LuCA gene coverage,
            # Wu cell-typing limitation, TCGA Ensembl mapping notes)
        ],
        'phase1_closure_recommendation': 'TBD — fill based on actual gate results',
    }
    
    with open(OUTPUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Phase 1 summary written to {OUTPUT_SUMMARY}")
    logger.info(f"Overall verdict: {summary['cross_cohort_summary']['overall_verdict']}")


if __name__ == '__main__':
    aggregate_phase1()
