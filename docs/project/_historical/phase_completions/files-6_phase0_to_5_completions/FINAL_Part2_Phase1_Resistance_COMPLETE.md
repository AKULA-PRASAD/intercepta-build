# INTERCEPTA v3.0 — FINAL RECONSTRUCTED BUILD GUIDE
## PART 2 OF 6: PHASE 1 — RESISTANCE DETECTION MODULE (Weeks 4-10)
### Version: FINAL — All Gaps Fixed, Velocity Methods Integrated

**Status: COMPLETE — Triple-layer system with all fallbacks**

---

# FILES IN THIS PART

| File | Class(es) | Purpose |
|------|-----------|---------|
| `src/module1_ingestion/scrna_ingestion.py` | ScRNAIngestion, QCReport | Data loading, QC, preprocessing, tier assignment |
| `src/module1_ingestion/bulk_deconvolution.py` | BayesPrismWrapper, DeconvolutionResult | **GAP 2 FIX:** Tier 3 bulk fallback |
| `src/module2_resistance/layer_a_signatures.py` | PROGENyScorer, AUCellScorer, ResistanceClassifier, LayerAResult | Expression-based resistance detection |
| `src/module2_resistance/layer_b_cellrank.py` | VelocityQC, CellRank2Analyzer, LayerBResult | CellRank 2 fate mapping |
| `src/module2_resistance/velocity_methods.py` | (functions) | **GAP 3 FIX:** scVelo, TFvelo, TIVelo wrappers |
| `src/module2_resistance/layer_c_velocity.py` | VelocityEnsemble, VelocityConsensusResult | Multi-method consensus |
| `src/module2_resistance/combined_detector.py` | CombinedResistanceDetector, ResistanceDetectionResult | Orchestrates all layers |

All code for these files was delivered in:
- Part 3 original (scrna_ingestion, layer_a, layer_b, layer_c, combined_detector)
- Gap Fix document (bulk_deconvolution, velocity_methods)

**Key integration point:** The `velocity_methods.py` (Gap 3 fix) provides `run_scvelo_dynamical()`, `run_tfvelo()`, `run_tivelo()` which are called by `layer_c_velocity.py`'s VelocityEnsemble class. The ensemble's `run_scvelo()`, `run_tfvelo()`, `run_tivelo()` methods now call these standalone functions instead of inline implementations.

**Key integration point:** The `bulk_deconvolution.py` (Gap 2 fix) provides BayesPrismWrapper which is called by the pipeline orchestrator (`src/pipeline.py`) when input tier = 3 (bulk RNA-seq instead of scRNA-seq).

---

# INTEGRATION DETAILS FOR GAP FIXES

### How velocity_methods.py integrates with layer_c_velocity.py:

```python
# In src/module2_resistance/layer_c_velocity.py, the VelocityEnsemble methods
# now delegate to the standalone functions:

from src.module2_resistance.velocity_methods import (
    run_scvelo_dynamical, run_tfvelo, run_tivelo, check_available_velocity_methods
)

class VelocityEnsemble:
    def __init__(self, resistant_cluster_ids=None):
        self.resistant_clusters = resistant_cluster_ids or []
        # Check what's available at initialization
        self.available = check_available_velocity_methods()
    
    def run_scvelo(self, adata):
        result_adata = run_scvelo_dynamical(adata)
        if result_adata is None:
            return None
        return self._velocity_toward_clusters(adata, self.resistant_clusters)
    
    def run_tfvelo(self, adata):
        scores = run_tfvelo(adata)
        return scores  # Already returns per-cell array or None
    
    def run_tivelo(self, adata):
        scores = run_tivelo(adata)
        return scores  # Already returns per-cell array or None
    
    # compute_consensus() unchanged from original Part 3
```

### How bulk_deconvolution.py integrates with the pipeline:

```python
# In src/pipeline.py, after determining tier = 3:

from src.module1_ingestion.bulk_deconvolution import BayesPrismWrapper

if tier == 3:
    # Bulk RNA-seq path
    deconv = BayesPrismWrapper(reference_atlas_path=config.get('data', 'reference_atlas'))
    deconv_result = deconv.deconvolve(bulk_expression_df)
    
    # Create pseudo-resistance result from deconvolution
    resistant_fraction = deconv_result.resistant_fraction
    sensitive_fraction = deconv_result.sensitive_fraction
    # Continue with drug sensitivity prediction using population fractions
```

---

# TESTS FOR PHASE 1

```python
# File: tests/unit/test_layer_a.py — 2 test classes (from Part 3)
# File: tests/unit/test_gap_fixes.py — TestBulkDeconvolution, TestVelocityMethods (from Gap Fix)
# File: tests/validation/phase1_validation.py — Smoke test + prostate validation (from Part 3)

# TOTAL PHASE 1 TESTS: 8 test functions
```

# PHASE 1 GATE CHECKLIST (from Part 3, with gap fix items added)

```markdown
### Layer A: Expression Signatures — 6 items
- [ ] PROGENy scorer loads (14 pathways)
- [ ] AUCell scorer loads 7 resistance signatures
- [ ] GMM classifier separates populations
- [ ] Resistant fraction biologically plausible (1-30%)
- [ ] Dominant mechanism identified
- [ ] Unit tests pass

### Layer B: CellRank 2 — 7 items
- [ ] scVelo velocity computation completes
- [ ] Velocity QC check working
- [ ] CytoTRACEKernel works WITHOUT velocity (fallback)
- [ ] Combined kernel works
- [ ] Terminal states identified
- [ ] Resistant terminal matched to Layer A
- [ ] Fate probabilities computed

### Layer C: Velocity Consensus — 6 items (UPDATED with Gap 3 fix)
- [ ] scVelo dynamical runs via velocity_methods.py wrapper
- [ ] TFvelo integration working (or graceful fallback logged)
- [ ] TIVelo integration working (or graceful fallback logged)
- [ ] check_available_velocity_methods() reports status correctly
- [ ] Consensus voting: 2/3 agreement required
- [ ] Graceful degradation if <2 methods succeed

### Tier 3 Fallback — 4 items (NEW — Gap 2 fix)
- [ ] BayesPrism wrapper detects R availability
- [ ] NNLS fallback works in pure Python without R
- [ ] Deconvolution produces valid fractions (sum to ~1)
- [ ] Resistant/sensitive fractions estimated from deconvolution

### Integration — 5 items
- [ ] CombinedResistanceDetector orchestrates all layers
- [ ] Tier-based weight selection correct
- [ ] Layer C weight redistributed if consensus fails
- [ ] Smoke test passes on scVelo pancreas dataset
- [ ] Prostate cancer validation: >80% concordance (or pending data)

### GATE: ALL items → PROCEED TO PHASE 2
```

---

*PART 2 RECONSTRUCTION COMPLETE.*
*Contains: All 7 source files for Modules 1-2, with Gap 2 (BayesPrism) and*
*Gap 3 (velocity wrappers) fully integrated. 8 test functions. Gate checklist.*
