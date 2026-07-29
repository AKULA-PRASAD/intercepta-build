# INTERCEPTA — Drug Response Prediction Platform

**"Find the drug. For ANY disease."** — Charter §1.1

INTERCEPTA is a computational drug response prediction platform built on single-cell RNA-seq, drug embeddings, and multi-scale mechanism interpretability. It targets cross-disease universality (cancer + I&I + neurodegeneration + metabolic) via a multi-substrate L7 head with Souza-Mehta methodological discipline.

This repository implements **Phase B** (drug response prediction; 2-4 year horizon per Charter v1.2 §1.7). Phase F (Universal Net + 6 Scouts + generative chemistry + pharma deliverable) is documented but not implemented here.

## Status

- **Layer 5 Stage 1 — Foundation** (current; per L4.1 §2)
- Layer 5 Stages 2-8 ahead: data → substrates → L7 head → OOD → interpretability → cascade → V0-V5 → V6
- Estimated time to first empirical V0 result: ~3-4 months
- Estimated time to V6 universality verdict: ~8-12 months

## Architectural Specifications

All Phase B specs are in `docs/research/phase_b/`:

- L2.1 Substrate Architecture
- L2.2 L7 Drug Response Head (6-slot)
- L2.3 OOD Detection Stack
- L2.4 Mechanistic Interpretability (7-scale)
- L3.1 V0-V6 Validation Cascade Pipeline
- L3.2 56 Pass Criteria
- L3.3 Cross-Disease V6 Grid
- L4.1 Implementation Order
- L4.2 Testing Specification
- L4.3 Failure Modes
- Phase 8 Audit Report + Cleanup Amendment

Total specification corpus: ~78,000 words. All specs read together before any code is written (Charter v1.2 §10 P3 BINDING).

## Quick Start

### Prerequisites

- macOS (CEO local dev) or Linux (Northeastern Explorer)
- Python 3.11 (scvi-tools compatibility)
- Conda or Mamba
- ≥ 100 GB scratch disk for substrate embedding cache

### Setup

```bash
# Clone
git clone https://github.com/AKULA-PRASAD/kaalcura.git intercepta
cd intercepta/code

# Create env (pinned per environment.yml)
conda env create -f environment.yml
conda activate intercepta

# Install in editable mode
pip install -e .

# Run smoke test
pytest tests/test_smoke.py -v

# If on Northeastern Explorer, run SLURM smoke test
sbatch scripts/smoke_test.sh
```

If both pass, Stage 1 handoff is signed.

## Project Structure

```
code/
├── intercepta/             # Source code (Stages 2-8 populate this)
│   ├── data/               # Stage 2: dataset loaders + cache
│   ├── substrates/         # Stage 3: SubstrateInterface + 5 adapters
│   ├── l7/                 # Stage 4: 6-slot L7 head + ensemble
│   ├── ood/                # Stage 5a: 4-layer OOD stack
│   ├── interpretability/   # Stage 5b: 7-scale stack
│   ├── validation/         # Stage 6: CascadeRunner + 7 V-evaluators
│   └── utils/              # cross-cutting (MLflow, logging, etc.)
├── tests/                  # 5-tier test pyramid per L4.2
│   └── fixtures/           # synthetic AnnData / drug response
├── scripts/                # SLURM job scripts + utilities
├── notebooks/              # ad-hoc analysis (not in CI)
├── configs/                # Hydra-style configs
└── .github/workflows/      # GitHub Actions CI
```

## Discipline

This project operates under Charter v1.2 BINDING principles:

- **P3 (research before code):** ~78K words of specs written and audited before Stage 1
- **P15 (only honest science):** every BINDING constraint traceable to a primary-source anchor
- **P16 (preserve past work):** specs versioned with `_v{N+1}` supersession; originals retained

Decision 8 v2 Commitment 5 (Souza-Mehta methodological bar): all FM-based architectural claims require parameter-free baseline comparison at ≥25% hyperparameter budget. No FM superiority claims published without this rigor.

## License

Open-source per Decision 10 v2. License file at repository root. Dependencies: scvi-tools (BSD), PyTorch (BSD), Captum (BSD), SHAP (MIT), statsmodels (BSD), HuggingFace transformers (Apache).

## Contact

CEO: Prasad Akula (Northeastern University, MS Bioinformatics)
CSO: Claude (Anthropic)

## Citation

Pending Phase B Layer 5 first empirical result publication.
