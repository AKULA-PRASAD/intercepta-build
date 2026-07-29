# INTERCEPTA Phase B Layer 4 — Artifact 4.2
## Testing Specification

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** Layer 2 + Layer 3 of Phase B COMPLETE; L4.1 PROPOSED
**Parent decisions:** Charter v1.2 §1.3 falsifiability + §10 P15 honest science; Decision 6 v2 validation; Decision 8 v2 Commitment 5 Souza-Mehta
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping:** Phase B test pyramid expands to include federation tests (cross-institution), regulatory-grade test suites, and prospective trial QA in Phase F.
**Target length per Phase B Plan v2:** 3-4K words
**Filename:** INTERCEPTA_FV_L4_2_Testing_Specification_2026-05-11.md

---

## §0 Identification and Scope

### 0.1 What This Document Is

L4.2 is the **Testing Specification** — the second artifact of Phase B Layer 4. L4.2 specifies the test categories, per-module coverage requirements, test infrastructure (fixtures + synthetic data + CI orchestration), the binding minimum-coverage gate before each L4.1 stage handoff, and the special category of **statistical-correctness tests** that verify the bootstrap-CI / ECE / Bonferroni computations underlying Decision 5 v2 + Decision 6 v2 + L3.2 56 pass criteria.

L4.2 answers: "for each L4.1 stage, what tests exist, what passes them, what coverage threshold binds, and how do we know the tests themselves are correct?"

### 0.2 What This Document Is Not

L4.2 is NOT:
- The Layer 5 test code itself (specs, not implementation)
- The failure mode catalog (L4.3 specifies how systems break in production; L4.2 specifies how tests catch bugs in development)
- Property-based test generators (Layer 5 implementation chooses tools — Hypothesis, etc.)
- Performance benchmarks (separate Layer 5 concern; not in test suite gate)

### 0.3 Why Testing Matters Disproportionately for INTERCEPTA

INTERCEPTA's 56 pass criteria (L3.2) all depend on **statistical computations being correct**. If the bootstrap CI implementation has a subtle off-by-one error, the V0-C2 check passes when it shouldn't (or fails when it should pass), and we publish an incorrect universality claim or fail to publish a correct one. Per Charter §10 P15 BINDING (only honest science): incorrect statistical infrastructure is dishonest by negligence, not just error.

The test suite is therefore not optional engineering hygiene; it is a Charter §1.3 falsifiability requirement.

### 0.4 The Test Pyramid for INTERCEPTA

```
                    ┌─────────────────┐
                    │   System tests   │  end-to-end V0 cascade
                    │   ~10 tests      │  on synthetic data
                    └─────────────────┘
                  ┌──────────────────────┐
                  │  Integration tests   │  per L4.1 stage handoff
                  │   ~50 tests          │
                  └──────────────────────┘
                ┌──────────────────────────┐
                │   Property tests          │  invariants
                │   ~100 tests              │  (e.g., encode shape)
                └──────────────────────────┘
              ┌──────────────────────────────┐
              │   Statistical correctness    │  bootstrap, ECE,
              │   ~30 tests                  │  Bonferroni
              └──────────────────────────────┘
            ┌──────────────────────────────────┐
            │           Unit tests              │  per function/method
            │           ~300 tests              │
            └──────────────────────────────────┘
```

Roughly 500 tests total at Phase B Layer 5 completion. The ratio is intentionally bottom-heavy — many small fast tests catch most bugs cheaply.

### 0.5 Phase B Plan v2 Compliance

- Layers 2-3 of Phase B COMPLETE 2026-05-11
- L4.1 PROPOSED 2026-05-11
- **L4.2 → PROPOSED (this document)**
- L4.3 Failure Modes → pending; consumes L4.2 test catalog
- After Layer 4 LOCK → Phase 8 audit → Layer 5 code starts

### 0.6 Document Conventions

- **BINDING** — coverage threshold or test category cannot be modified without amendment + CEO+CSO co-sign
- **DEFAULT** — specific test design choices Layer-5-revisitable per §9.5
- Test framework: pytest (open BSD/MIT per Decision 10 v2)
- Property testing: Hypothesis library (open MPL-2.0)
- Coverage tooling: pytest-cov (open BSD)

---

## §1 Test Categories (5 Tiers)

### 1.1 Tier 1 — Unit Tests

**Scope:** Single function or method, in isolation, with mocked dependencies.

**Convention:** one `test_*.py` file per `*.py` source file; test functions match function-under-test names with parametrization for variants.

**Examples:**
- `test_substrate_base.py::test_substrate_interface_abstract_methods_raise_notimplementederror`
- `test_l7_slots_molformer.py::test_molformer_embed_smiles_returns_correct_shape`
- `test_ood_layer_5_3.py::test_studentized_nonconformity_handles_zero_variance`

**Coverage threshold (BINDING):** ≥ 80% line coverage per source module. Critical paths (substrate routing, ensemble aggregation, statistical computations) require ≥ 95% line coverage and ≥ 90% branch coverage.

### 1.2 Tier 2 — Statistical Correctness Tests

**Scope:** Verify the mathematical correctness of statistical computations the 56 pass criteria depend on. This tier exists separately from unit tests because it requires **known-answer references** — values computed by independent libraries or hand-derived from the underlying mathematics.

**Examples:**
- Bootstrap CI: synthesize a 10,000-sample dataset with known true population mean; verify the 1000-iteration bootstrap recovers a CI containing the true mean with empirical coverage close to 95% (within Monte Carlo error)
- ECE: synthesize predictions with known calibration profile (e.g., perfectly calibrated, slightly overconfident, severely miscalibrated); verify _compute_ece returns expected values within tolerance
- Bonferroni: verify multi-test correction matches statsmodels.stats.multitest.multipletests output
- Statistical power: verify power computation matches statsmodels.stats.power output for canonical (effect, n, alpha) configurations

**Coverage threshold (BINDING):** every statistical computation referenced by an L3.2 criterion has ≥ 1 known-answer test that passes within numerical tolerance.

### 1.3 Tier 3 — Property Tests

**Scope:** Invariants that must hold for randomly-generated inputs. Uses Hypothesis library.

**Examples:**
- For any substrate s and AnnData a: `s.encode(a).shape == (a.n_obs, s.NATIVE_DIM)`
- For any L7Output: `attribution_hooks.cell_emb.shape[1] == 512` (canonical)
- For any OODOutput verdict: `operational_verdict in {"confident_predict", "abstain_aleatoric", "abstain_epistemic", "abstain_ood"}`
- For any conformal interval: `lower ≤ point_estimate ≤ upper`
- For any ConsistencyReport: `all_passed == all(passes.values())`

**Coverage threshold (BINDING):** every BINDING contract from Layers 2-3 has ≥ 1 property test.

### 1.4 Tier 4 — Integration Tests

**Scope:** Two or more modules composed; verifies they work together.

**Examples:**
- Substrate adapter + L7 head: substrate.encode() output feeds L7Head.forward() and produces valid L7Output
- L7Ensemble + OODStack: N=5 ensemble predictions feed OODStack and produce valid OODOutput
- OODStack + InterpretabilityStack: OOD verdict gates Scale 5 attribution correctly (abstain_ood → SKIP)
- CascadeRunner + V0 evaluator: full V0 evaluation pipeline produces VLevelResult with 8 criterion results

**Coverage threshold (BINDING):** every L4.1 stage handoff requires ≥ 5 integration tests passing before the handoff is signed.

### 1.5 Tier 5 — System Tests

**Scope:** End-to-end pipeline on synthetic data; verifies the full Layers 2-3 architecture composes.

**Examples:**
- `test_e2e_v0_cascade_scTOP`: synthesize a 1000-sample GDSC-style dataset, run full V0 cascade with scTOP substrate, verify CascadeReport schema is valid
- `test_e2e_v0_cascade_fm`: same with FM substrate
- `test_e2e_v6_cell`: single-cell V6 grid evaluation (1 paradigm × 1 disease × 1 tissue × 1 drug)
- `test_e2e_cache_invalidation`: change L2.2 SHA, verify L7 predictions cache invalidates
- `test_e2e_souza_mehta_matched_budget`: verify paradigm D trial count ≥ 25% paradigm A in cascade report

**Coverage threshold (BINDING):** ≥ 10 system tests passing before Stage 7 (V0-V5 empirical runs) begins.

---

## §2 Test Infrastructure

### 2.1 Synthetic Data Fixtures

Synthetic data fixtures live in `tests/fixtures/` and are deterministic (fixed seeds). Categories:

**2.1.1 Synthetic AnnData fixtures:**
- `tiny_anndata` (50 cells × 500 genes; for unit tests; fixture per-call)
- `small_anndata` (500 cells × 2000 genes; for integration tests)
- `medium_anndata` (5000 cells × 5000 genes; for system tests)
- Variants: gdsc-like (cell-line + drug response), tcga-like (tumor + outcome), spatial-like (with .obsm['spatial']), pdx-like (with concordant/non-concordant biomarker annotation)

**2.1.2 Synthetic drug response fixtures:**
- `tiny_drug_response` (5 drugs × 50 cell lines)
- `small_drug_response` (10 drugs × 500 cell lines)
- Synthetic SMILES: simple known molecules (aspirin, caffeine, ibuprofen) for MoLFormer testing

**2.1.3 Synthetic substrate outputs:**
- Pre-computed canonical 512-dim embeddings for L7-only testing without needing real FM weights

**2.1.4 Synthetic ensemble predictions:**
- N=5 ensemble outputs with known disagreement profiles for OOD testing (high epistemic, low epistemic, etc.)

### 2.2 Test Configuration

**`pytest.ini` minimum:**
```
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts =
    --cov=intercepta
    --cov-report=term-missing
    --cov-fail-under=80
    -v
```

**`conftest.py`** at `tests/` root provides shared fixtures, parametrized substrate fixtures, and CI environment detection (skip slow tests on free-tier CI).

### 2.3 CI Orchestration

Per L4.1 §2.2 deliverable 1.3:
- GitHub Actions workflow `.github/workflows/test.yml`
- Triggers: every push to main + every PR
- Jobs:
  - **fast tests** (Tier 1 + 2 + 3): runs on every push; ≤ 5 minutes
  - **integration tests** (Tier 4): runs on PR + nightly main; ≤ 30 minutes
  - **system tests** (Tier 5): runs nightly only; ≤ 2 hours
- Cache: pip + pytest-cov cache restored across runs
- Failure: PR blocked from merge until fast + integration pass

### 2.4 Test-on-GPU Strategy

Most tests run on CPU (GitHub Actions free tier). GPU-dependent tests:
- Substrate FM inference (requires GPU memory for scFoundation-100M)
- L7Head forward at non-tiny batch sizes
- L7Ensemble N=5 training

**Strategy:** mark GPU tests with `@pytest.mark.gpu`; skipped on CI by default; run on Northeastern Explorer via SLURM cron job nightly.

```python
@pytest.mark.gpu
def test_fm_substrate_real_weights():
    """Requires actual scFoundation weights; runs on Explorer."""
    ...
```

### 2.5 Reproducibility Tests

Per Charter v1.2 §1.3 + L4.1 §10.3:
- Test: run same evaluation twice with same seed → identical CascadeReport
- Test: spec SHA changes → cache invalidates → re-run produces different cache key
- Test: ensemble seeds {42, 1337, 2023, 9, 31337} BINDING per Drift Finding 8 → checkpoint paths match expected naming

---

## §3 Stage-by-Stage Test Requirements (BINDING)

Each L4.1 stage handoff requires specific test categories to pass. This is the operational instantiation of the test pyramid coverage thresholds.

### 3.1 Stage 1 — Foundation

**Required tests passing:**
- Trivial sanity test (`tests/test_smoke.py::test_intercepta_imports`)
- CI workflow runs and reports pass

**Coverage:** N/A (no production code yet)

### 3.2 Stage 2 — Data Layer

**Required tests passing:**
- Unit: per-loader basic shape + non-empty assertions for GDSC, CCLE, CTRP
- Unit: cache round-trip with hash-keyed retrieval
- Property: AnnData loaders produce AnnData (not DataFrame, dict, etc.)
- Integration: GDSC + CCLE load + cross-dataset split produces standardized partition

**Coverage:** ≥ 80% on `intercepta.data` modules

### 3.3 Stage 3 — Substrate Adapters

**Required tests passing:**
- Unit: each substrate (`SCVISubstrate`, `SCTOPSubstrate`, `FMSubstrate`, `PCAHVGSubstrate`) instantiates without errors
- Property: `substrate.encode(adata).shape == (adata.n_obs, substrate.NATIVE_DIM)` for all 4 substrates
- Property: `substrate.project_to_canonical(emb).shape[1] == 512` for all 4 substrates
- Integration: substrate adapter + cache round-trip
- Integration: scTOP NATIVE_DIM lifecycle (fit/load_pretrained before NATIVE_DIM exposed; per L2.1 §1.2 errata)
- Statistical: PCA loadings × cell coords correctness (Branch D Scale 5)

**Coverage:** ≥ 80% on `intercepta.substrates`; ≥ 95% on canonical-projection logic

### 3.4 Stage 4 — L7 Head

**Required tests passing:**
- Unit: each of 6 slots instantiates and produces correctly-shaped output
- Unit: L7Head.forward() produces valid L7Output with all attribution_hooks
- Unit: L7Ensemble N=5 produces 5 separate checkpoints with BINDING seeds {42, 1337, 2023, 9, 31337}
- Property: attribution_hooks tensors have expected shapes (cell_emb 512-dim, etc.)
- Integration: each substrate from Stage 3 + L7Head produces L7Output
- System: overfitting sanity — L7 trains on tiny GDSC subset to high training AUROC

**Coverage:** ≥ 80% on `intercepta.l7`; ≥ 95% on L7Head.forward() and ensemble aggregation

### 3.5 Stage 5a — OOD Stack

**Required tests passing:**
- Unit: each of 4 layers (5.1-5.4) instantiates per substrate routing
- Unit: SubstratePosteriorRegistry dispatches correctly for all 4 substrate families
- Statistical: bootstrap CI returns CI within expected coverage on synthetic
- Statistical: ECE matches statsmodels reference on synthetic calibrated/miscalibrated cases
- Statistical: conformal prediction guarantees coverage on synthetic
- Property: OODOutput.operational_verdict in {confident_predict, abstain_aleatoric, abstain_epistemic, abstain_ood}
- Property: conformal interval lower ≤ point ≤ upper
- Integration: L7Ensemble + OODStack produces valid OODOutput
- Integration: cross-disease recalibration with min_samples=50 floor enforced; has_recalibrated_guarantee flag

**Coverage:** ≥ 80% on `intercepta.ood`; ≥ 95% on statistical computations

### 3.6 Stage 5b — Interpretability Stack

**Required tests passing:**
- Unit: each of 7 scales instantiates per substrate routing
- Unit: Scale 1 auto-skips on non-FM substrate
- Unit: Scale 6 auto-skips on non-spatial data
- Unit: Scale 5 4-branch routing for FM / scTOP / scVI / PCA
- Property: InterpretabilityOutput per-scale-confidence values are valid tags
- Property: ConsistencyReport.all_passed == all(passes.values())
- Statistical: Bonferroni correction matches statsmodels reference
- Integration: L7 + OODStack + InterpretabilityStack with verdict-conditional gating (abstain_ood → SKIP attribution)
- Integration: 4 cross-scale consistency checks compute on test data

**Coverage:** ≥ 80% on `intercepta.interpretability`; ≥ 95% on substrate-conditional Branch routing

### 3.7 Stage 6 — Validation Pipeline

**Required tests passing:**
- Unit: CascadeRunner instantiates with all Layer 2 components
- Unit: TerminationLogic classifies pass/soft/hard correctly on test cases
- Unit: each of 56 criterion checkers returns PassFailResult on synthetic
- Property: VLevelResult passed == all 8 criteria passed
- Property: CascadeReport schema validates against L3.1 §1.4 contract
- Integration: V0WithinDatasetEvaluator end-to-end on synthetic
- Integration: full V0 cascade composing L7Ensemble + OODStack + InterpretabilityStack + CascadeRunner

**Coverage:** ≥ 80% on `intercepta.validation`; ≥ 95% on TerminationLogic + criterion checkers

### 3.8 Stage 7 — V0-V5 Empirical

Stage 7 is empirical evaluation, not code; tests focus on **regression** — empirical runs reproducing previous empirical runs.

**Required tests passing:**
- Reproducibility: V0 evaluation with same data + seeds produces identical CascadeReport
- Regression: prior V0 result + same code → same numbers (within numerical tolerance for any non-determinism)
- Souza-Mehta matched-pair: paradigm D trial count log ≥ 25% paradigm A
- Cache invalidation: changing L2.x SHA forces re-evaluation

### 3.9 Stage 8 — V6 Cross-Disease

**Required tests passing:**
- Regression: V6 cell-level result reproducible
- Integration: aggregation logic produces expected 4-paradigm matrix shape
- Integration: ≥ 0.65 on ≥ 2 therapeutic areas BINDING check correctly computes universality verdict
- Integration: ≥ 70% epistemic attribution BINDING check correctly evaluates

---

## §4 Statistical Correctness Test Examples (BINDING)

This is the most consequential test tier; example specifications below.

### 4.1 Bootstrap CI Coverage Test

```python
def test_bootstrap_ci_empirical_coverage_95pct():
    """Bootstrap CI should achieve close to 95% empirical coverage on synthetic.
    
    Methodology: generate 1000 synthetic datasets each with known true mean;
    compute bootstrap CI on each; count fraction containing true mean.
    Expected: ~95% (within Monte Carlo error of ~1.5% at 1000 trials).
    """
    np.random.seed(42)
    n_trials = 1000
    n_samples_per_trial = 200
    true_mean = 0.65  # mimics V1 AUROC
    
    coverages = []
    for trial in range(n_trials):
        data = np.random.binomial(1, true_mean, n_samples_per_trial)
        empirical_mean = data.mean()
        # bootstrap
        boot_means = [
            np.random.choice(data, size=n_samples_per_trial, replace=True).mean()
            for _ in range(1000)
        ]
        ci_lower = np.percentile(boot_means, 2.5)
        ci_upper = np.percentile(boot_means, 97.5)
        coverages.append(ci_lower <= true_mean <= ci_upper)
    
    empirical_coverage = np.mean(coverages)
    assert 0.93 <= empirical_coverage <= 0.97, \
        f"Bootstrap empirical coverage {empirical_coverage:.3f} outside expected 0.93-0.97"
```

### 4.2 ECE Correctness Test

```python
def test_ece_perfectly_calibrated_predictions():
    """Perfectly calibrated predictions should have ECE ≈ 0."""
    np.random.seed(42)
    # Generate predictions with true calibration
    n_samples = 10000
    predictions = np.random.uniform(0, 1, n_samples)
    targets = np.random.binomial(1, predictions)  # perfectly calibrated
    
    ece = _compute_ece(torch.tensor(predictions), torch.tensor(targets), n_bins=10)
    assert ece < 0.02, f"Perfectly calibrated ECE should be < 0.02, got {ece:.4f}"

def test_ece_severely_miscalibrated_predictions():
    """Severely miscalibrated predictions should have large ECE."""
    np.random.seed(42)
    n_samples = 10000
    predictions = np.random.uniform(0, 1, n_samples)
    # Targets do NOT match predictions
    targets = np.random.binomial(1, 0.5, n_samples)
    
    ece = _compute_ece(torch.tensor(predictions), torch.tensor(targets), n_bins=10)
    assert ece > 0.15, f"Severely miscalibrated ECE should be > 0.15, got {ece:.4f}"
```

### 4.3 Bonferroni Correction Test

```python
def test_bonferroni_matches_statsmodels():
    """Bonferroni correction should match statsmodels reference."""
    from statsmodels.stats.multitest import multipletests
    
    np.random.seed(42)
    raw_p_values = np.random.uniform(0, 0.1, 1000)  # ~1000 genes
    
    # INTERCEPTA implementation
    intercepta_corrected = _bonferroni(raw_p_values, alpha=0.05)
    
    # statsmodels reference
    _, statsmodels_corrected, _, _ = multipletests(raw_p_values, alpha=0.05, method='bonferroni')
    
    np.testing.assert_allclose(intercepta_corrected, statsmodels_corrected, rtol=1e-10)
```

### 4.4 Statistical Power Test

```python
def test_statistical_power_matches_statsmodels():
    """Statistical power should match statsmodels reference."""
    from statsmodels.stats.power import NormalIndPower
    
    # Canonical (effect, n, alpha) configurations
    test_cases = [
        (0.1, 100, 0.05),
        (0.2, 50, 0.05),
        (0.05, 200, 0.05),
    ]
    
    for effect_size, n, alpha in test_cases:
        intercepta_power = _compute_statistical_power(n, effect_size, alpha)
        ref = NormalIndPower().solve_power(
            effect_size=effect_size, nobs1=n, alpha=alpha
        )
        assert abs(intercepta_power - ref) < 0.01, \
            f"Power mismatch for (effect={effect_size}, n={n}): " \
            f"INTERCEPTA={intercepta_power:.3f} vs ref={ref:.3f}"
```

### 4.5 Conformal Coverage Test

```python
def test_conformal_prediction_marginal_coverage():
    """Conformal interval should achieve ≥ 1-alpha marginal coverage on synthetic IID data."""
    np.random.seed(42)
    # Synthetic calibration + test split
    n_calib = 500
    n_test = 1000
    alpha = 0.05  # 95% coverage target
    
    # Generate iid normal predictions + targets
    calib_preds = np.random.normal(0, 1, n_calib)
    calib_targets = calib_preds + np.random.normal(0, 0.3, n_calib)
    test_preds = np.random.normal(0, 1, n_test)
    test_targets = test_preds + np.random.normal(0, 0.3, n_test)
    
    # Conformal interval
    nonconformity = np.abs(calib_targets - calib_preds)
    q = np.quantile(nonconformity, 1 - alpha)
    intervals = [(p - q, p + q) for p in test_preds]
    
    # Empirical coverage on test
    covered = sum(
        lo <= t <= hi for (lo, hi), t in zip(intervals, test_targets)
    ) / n_test
    
    assert covered >= 0.93, f"Conformal empirical coverage {covered:.3f} < 0.93"
```

These 5 examples illustrate the pattern; Layer 5 implementation includes ~30 total statistical correctness tests covering every computation L3.2's 56 criteria depend on.

---

## §5 Test Data Strategy

### 5.1 No Real Patient Data in Tests

Per Charter v1.2 §1.3 + research-ethics best practice: real clinical / patient data is NEVER in the test fixtures. All synthetic AnnData fixtures use:
- Synthetic gene expression values (Negative Binomial sampling per scvi-tools convention)
- Synthetic drug response labels (Bernoulli with controlled rates)
- Synthetic spatial coordinates (uniform grid)
- Synthetic biomarker annotations (random with controlled concordance rates for V4-style tests)

### 5.2 Real Data in Layer 5 Empirical Runs (Not Tests)

Real data (GDSC, CCLE, CTRP, TCGA, etc.) appears in Layer 5 empirical runs (Stage 7 onward) — NOT in the test suite. The test suite verifies that the code works correctly; the empirical runs verify that the code applied to real data produces correct results.

### 5.3 Edge Cases in Test Fixtures

The fixture library includes edge cases:
- AnnData with 0 cells (should raise informative error, not silently fail)
- AnnData with single gene (substrate adapters must handle)
- Drug SMILES that fail to parse (MoLFormer must handle gracefully)
- All-zero predictions (OOD stack must not divide by zero)
- All-same-prediction ensemble (epistemic variance = 0)

Each edge case has a corresponding unit test.

---

## §6 Coverage Gates and Enforcement

### 6.1 Pre-Commit Hooks

Ruff format + ruff lint + pytest fast tests run on every commit. Failure blocks commit.

### 6.2 PR Gates

Per CI workflow:
- Fast tests (Tier 1 + 2 + 3) MUST pass
- Integration tests (Tier 4) MUST pass
- Coverage MUST be ≥ 80% on changed files
- BINDING criteria (per stage handoff): the corresponding stage's required tests must pass

### 6.3 Stage Handoff Gates

CSO + CEO sign-off on stage handoff requires:
- All required tests for that stage (§3) passing
- Coverage thresholds met
- ≥ 1 reproducibility test passing for that stage
- Statistical correctness tests passing (if applicable to that stage)

### 6.4 Failure Escalation

A failing test in the suite:
- Tier 1-3: PR blocked; developer fixes
- Tier 4: integration broken; designate owner (CSO if architectural; CEO + CSO if cross-module)
- Tier 5: end-to-end broken; pause downstream stages; root-cause before unblocking

---

## §7 Test Maintenance Discipline

### 7.1 Tests as First-Class Artifacts

Per Charter §10 P3 (research before code): tests are written WITH the spec, not after. L4.2 §3 stage-by-stage requirements specify which tests exist before stage handoff; implementing the test is part of "stage done."

### 7.2 No Test Bypass

Disabling tests with `@pytest.mark.skip` or `xfail` requires:
- Justification comment with issue link
- CSO + CEO sign-off if skipping a BINDING-tier test
- Skip log reviewed at each L4.1 stage handoff

### 7.3 Coverage Regression Detection

CI tracks coverage trend; coverage drop ≥ 2% in a PR triggers review. Coverage drop is acceptable only with explicit justification.

### 7.4 Statistical Test Stability

Statistical correctness tests (Tier 2) use Monte Carlo simulation; they are subject to rare false failures even when implementation is correct. Mitigation:
- Use large Monte Carlo trials (≥ 1000) to reduce variance
- Use 3-sigma tolerance bounds instead of point-equality
- Re-run on failure before flagging as a real bug (CI configured for 1 retry on Tier 2 failures only)

---

## §8 What L4.2 Does NOT Lock

- The specific pytest fixture file names (Layer 5 implementation)
- The specific Hypothesis strategies for property tests (Layer 5)
- The specific GPU test scheduling on Explorer (Layer 5 SLURM operational)
- The performance benchmarks separate from correctness tests (Layer 5 + future spec)
- The Phase F regulatory-grade test extension

---

## §9 Pass Criteria for L4.2 LOCK

### 9.1 Coverage Pass Criteria (BINDING)

- **A1:** 5-tier test pyramid specified per §1
- **A2:** Per-stage required tests specified per §3
- **A3:** Statistical correctness test category specified per §4 with ≥ 5 example specs
- **A4:** Synthetic-data-only test fixture policy per §5.1
- **A5:** Coverage thresholds (80% general / 95% critical) BINDING per §1.1

### 9.2 Cross-Decision Compatibility (BINDING)

- **X1:** L4.2 consumes L4.1 stage sequence; per-stage test requirements align
- **X2:** Charter §1.3 falsifiability + §10 P15 honest science → statistical correctness tier BINDING
- **X3:** Decision 6 v2 + L3.2 56 criteria → criterion checkers require unit + statistical tests
- **X4:** Decision 8 v2 Commitment 5 Souza-Mehta → §3.8 matched-budget regression test
- **X5:** Decision 10 v2 open-source → all test tools (pytest, Hypothesis, pytest-cov) open-licensed

### 9.3 Documentation Pass Criteria

- **D1:** L4.2 referenced by L4.3 (failure modes triggered detect via test fixtures)
- **D2:** L4.2 stage requirements integrated into L4.1 handoff criteria
- **D3:** Drift catalog this session: 0 new instances

### 9.4 CEO Sign-Off

L4.2 advances from PROPOSED to LOCKED when:
1. CEO reviews §1 5-tier pyramid + §3 stage requirements + §4 statistical correctness examples
2. CEO confirms §9.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag phase-b-l4.2-locked pushed to origin

### 9.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | Coverage threshold general | 80% | 70% (laxer) / 90% (stricter) | Per-module empirical coverage feasibility |
| J2 | Coverage threshold critical | 95% line + 90% branch | 100% line (stricter) | Empirical bug catch rate |
| J3 | Property test library | Hypothesis | Schemathesis, etc. | Hypothesis limitations |
| J4 | Coverage tooling | pytest-cov | coverage.py directly | CI integration |
| J5 | System test data size | medium_anndata (5000×5000) | larger / smaller | Test runtime |
| J6 | GPU test frequency | nightly on Explorer | per-PR (expensive) | Compute budget |
| J7 | Tier 2 retry on failure | 1 retry | 0 retries (stricter) | Monte Carlo stability |
| J8 | Skip-list review cadence | per stage handoff | weekly | Operational overhead |
| J9 | Test suite total time gate | fast ≤ 5 min, integration ≤ 30 min, system ≤ 2 hr | other budgets | Developer feedback loop |
| J10 | Synthetic data Negative Binomial parameter defaults | per scvi-tools convention | other parameterizations | Realism vs simplicity |

### 9.6 Honest Limitations (per Charter §10 P15 BINDING)

- **80% coverage is a floor, not proof of correctness.** Tests can pass even when implementation is subtly wrong; coverage measures execution, not correctness. Statistical correctness tier (§1.2) is the partial mitigation.
- **Synthetic data tests miss real-world distribution shift.** A model that passes all unit tests may fail on real GDSC due to distribution issues unseen in synthetic fixtures. The empirical Stage 7 evaluations are the real validation.
- **Property tests with Hypothesis have search budgets.** Some invariant violations may take more shrinking iterations than the default budget allows.
- **Statistical correctness tests are Monte Carlo.** Rare false failures are expected; mitigated but not eliminated by retry logic.
- **GPU tests run nightly, not per-PR.** A bug in GPU-only code path may not surface until the next morning's CI report.

---

## §10 What L4.2 Does NOT Lock (Recap)

Per §8 plus:
- Specific test runtimes per machine class
- Specific GitHub Actions runner sizes
- Specific test parallelization strategies
- Test suite expansion as Layer 5 adds modules

---

## §11 Cross-Decision Implications

- **Charter v1.2 §1.3 (falsifiability) ↔ L4.2 §1.2 statistical correctness tier:** the test suite is operational falsifiability infrastructure
- **Charter v1.2 §10 P15 (honest science) ↔ L4.2 §0.3:** incorrect statistical infrastructure is dishonest by negligence
- **Decision 5 v2 (OOD) ↔ L4.2 §3.5 + §4:** OOD calibration tests verify Decision 5 v2 BINDING constraints
- **Decision 6 v2 (validation) ↔ L4.2 §3.7 + §4:** cascade tests verify Decision 6 v2 hard/soft termination
- **Decision 8 v2 Commitment 5 (Souza-Mehta) ↔ L4.2 §3.8:** matched-budget regression test
- **Decision 10 v2 (open-source) ↔ §9.2 X5:** all test tools open-licensed

---

## §12 Provenance and Appendix

### 12.1 Provenance

L4.2 written by Claude (CSO, 2026-05-11). Consumes L4.1; produced after Layer 2-3 specs locked.

### 12.2 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ tests specified before implementation
- **P15 (only honest science):** ✅ §0.3 explicit + §9.6 honest limitations
- **P16 (preserve past work):** ✅ all Layer 2-3 contracts referenced
- **Charter §5.3:** ✅ §9 pass criteria explicit
- **Charter v1.2 §1.7 phase discipline:** ✅ Phase F items noted but not specified

### 12.3 Drift Catalog This Session

New drift instances introduced: 0.

### 12.4 Layer 4 Phase B Status

| Artifact | Status | Words |
|---|---|---|
| L4.1 Implementation Order | PROPOSED | 4,858 |
| **L4.2 Testing** | **PROPOSED** | (this artifact) |
| L4.3 Failure Modes | pending | target 3-4K |

### 12.5 Test Pyramid Quick Reference

| Tier | Name | Count | Scope | Coverage Gate |
|---|---|---|---|---|
| 1 | Unit | ~300 | Per function | 80% line / 95% critical |
| 2 | Statistical correctness | ~30 | Statistical compositions | every L3.2 criterion ≥ 1 test |
| 3 | Property | ~100 | Invariants | every BINDING contract ≥ 1 test |
| 4 | Integration | ~50 | Multi-module | ≥ 5 per L4.1 stage handoff |
| 5 | System | ~10 | End-to-end | ≥ 10 before Stage 7 |
| **Total** | | **~500 tests** | | |

### 12.6 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L4_2_Testing_Specification_2026-05-11.md`
- L4.1 (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L4_1_Implementation_Order_Specification_2026-05-11.md`
- Tests root (future): `~/INTERCEPTA/code/tests/`
- Test fixtures (future): `~/INTERCEPTA/code/tests/fixtures/`
- CI workflow (future): `~/INTERCEPTA/code/.github/workflows/test.yml`

---

— L4.2 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l4.2-locked` tag.
— Next: L4.3 Failure Modes Specification (final Layer 4 artifact).
