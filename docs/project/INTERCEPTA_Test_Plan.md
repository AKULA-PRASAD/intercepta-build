# INTERCEPTA Test Plan — Locked Specification

**Subject:** Comprehensive test plan defining what "testing" means for INTERCEPTA at current stage and how it will be executed.
**Authors:** Prasad Akula and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-08
**Status:** LOCKED. Defines test categories, operational definitions, priority ordering, and execution rules.

---

## 1. Why this test plan

INTERCEPTA has shipped 17 tags this work cycle covering Round 2 closure, vision amendment, selectivity layer redesign, Workstream B Phase 0 prep + execution. The framework runs and produces real measurements. **What's missing is a structured testing strategy.** Without one:

- Reviewers will reject papers for inadequate validation
- Investors will doubt claims that haven't been independently tested
- Pharma BD requires reproducibility and benchmarks
- The team (currently of 1 founder + CSO) cannot trust the framework long-term without documented test discipline

This plan defines what tests will be run, in what order, with what success criteria, and what each test will and will not prove.

## 2. What this test plan is NOT

- **Not a comprehensive validation suite for clinical use.** Clinical validation requires wet lab + IRB-approved cohorts + multi-year arc. Out of scope.
- **Not a unit test suite for code coverage.** Code-level unit tests are valuable but not the bottleneck right now.
- **Not a one-time activity.** Tests will be re-run as the framework evolves.
- **Not a substitute for peer review.** Tests prepare for peer review; they don't replace it.

## 3. Test categories (LOCKED)

Five test categories. Each has a specific question it answers, specific PASS/FAIL criteria, and specific resource requirements.

### Category T1: Reproducibility tests

**Question answered:** "Does the framework produce identical outputs when re-run on the same inputs?"

**What it tests:**
- All scripts run end-to-end without errors
- Numerical outputs match committed git history
- Random seeds produce deterministic results

**Operational definition:**
- Re-run `step6_selectivity_v2.py` for all 4 diseases. Verify outputs byte-identical to committed JSONs (excluding `computed` timestamp).
- Re-run `step6_selectivity_v2_csv_export.py`. Verify mCRPC regression check still PASSES (KLK3 = 16695.58).
- Re-run Round 2.2c multi-modal predictor on BeatAML if data is preserved. Verify Venetoclax AUROC = 0.91 ± 0.001.
- Re-run KAALCURA cross-dataset transfer Q_D. Verify ρ = -0.271 ± 0.01, p < 0.01.

**PASS:** All numerical outputs reproduce within rounding tolerance.
**FAIL:** Any single output disagrees beyond tolerance — investigate as code drift or environmental issue.

**Resource:** 2-4 hrs (Mac, no HPC required). All inputs already committed to repo.
**Priority:** **HIGH** — foundational. If reproducibility fails, all other tests are meaningless.

---

### Category T2: Robustness tests

**Question answered:** "Are findings robust to data perturbation, or are they dataset-specific artifacts?"

**What it tests:**
- Drop random 10% of patients from BeatAML, re-train predictor. Does AUROC stay within 5% of original?
- Add Gaussian noise to RNA features. Does predictor degrade gracefully?
- Subsample to 50% of cells in scRNA cohort. Does KAALCURA cross-dataset signal persist?

**Operational definition:**
- 5 perturbation conditions (10% drop, 25% drop, 50% drop, +5% noise, +10% noise)
- 3 random seeds per condition (reproducibility within stochastic perturbation)
- Compare AUROC distribution to original
- PASS: median AUROC retention >= 90% across perturbations
- FAIL: median AUROC drops below 80% under mild (10% drop) perturbation

**Resource:** 5-10 hrs (BeatAML + Van Galen on Mac OR HPC). Multi-stage execution.
**Priority:** **MEDIUM** — important for paper, not blocking other work.

---

### Category T3: Comparative benchmark

**Question answered:** "Does INTERCEPTA outperform simpler baseline methods?"

**What it tests:**
- Run baseline elastic net regression on same BeatAML features → compare to LightGBM
- Run published method (e.g., MOLI, DeepCDR) if implementation available → compare AUROC
- Run RNA-only LightGBM (no KAALCURA, no mutation, no pathway) → quantify multi-modal contribution

**Operational definition:**
- 3 baselines: ElasticNet, RandomForest, RNA-only-LightGBM
- Same per-drug 5-fold CV protocol as Round 2.2c
- Same drugs (those passing 10/10 filter)
- Per-drug AUROC comparison
- PASS: INTERCEPTA multi-modal beats best baseline by ≥ 0.02 mean AUROC across drugs
- FAIL: INTERCEPTA does not significantly outperform baselines (= negative result, also publishable but weaker story)

**Resource:** 8-15 hrs (HPC, multiple model trainings)
**Priority:** **HIGH** — this is the test reviewers will demand. Without it, paper acceptance is harder.

---

### Category T4: Biological face validity tests

**Question answered:** "Do the framework's top predictions match known biology?"

**What it tests:**
- Does selectivity layer correctly identify clinically-validated drug targets per disease?
  - mCRPC: Should rank KLK3, AR high (it does — verified)
  - AML: Should rank FLT3, JAK3 high (it does — verified)
  - GBM: Should rank EGFR, IDH1 (need to check)
  - NSCLC: Should rank EGFR, KRAS, ALK, ROS1 (verified ROS1=83 — clinically correct)
- Does multi-modal predictor identify EGFR inhibitors as effective for EGFR-mutant LUAD when LuCA data arrives?
- Does it correctly identify Venetoclax as effective in BCL2-positive AML (BeatAML showed 0.91 — verified)?

**Operational definition:**
- For each disease, define "ground truth" = 5-10 FDA-approved drugs with known mechanism
- Check whether framework correctly ranks them in top-N predictions
- PASS: ≥ 70% of ground truth drugs in top-20 predicted-effective for matched mutation/expression context
- FAIL: < 50% recall (suggests framework is not learning real biology)

**Resource:** 4-6 hrs (Mac, mostly post-hoc analysis of existing predictions)
**Priority:** **HIGH** — foundational sanity check. If face validity fails, framework is not biologically meaningful.

---

### Category T5: Code-level unit tests

**Question answered:** "Are the building blocks of the framework correct in isolation?"

**What it tests:**
- KAALCURA computation produces expected output on tiny synthetic data
- Selectivity ratio formula matches mathematical definition
- Multi-modal predictor handles edge cases (missing data, single-class, all-zero features)
- Disease net loaders parse JSON correctly

**Operational definition:**
- Use `pytest` framework
- ~30-50 unit tests covering core functions
- PASS: 100% test pass rate
- FAIL: any test fails — fix immediately, do not proceed

**Resource:** 6-12 hrs (Mac, focused writing)
**Priority:** **LOW** — important long-term but not immediately blocking. Framework currently works; unit tests would catch future regressions.

---

## 4. Priority ordering (LOCKED)

The five categories execute in this order:

| Order | Category | Priority | Resource | Rationale |
|---|---|---|---|---|
| 1 | T1 Reproducibility | HIGH | 2-4 hrs | Foundational. Must pass before anything else means anything. |
| 2 | T4 Biological face validity | HIGH | 4-6 hrs | Foundational sanity. If framework isn't biologically meaningful, T2/T3 are pointless. |
| 3 | T3 Comparative benchmark | HIGH | 8-15 hrs | Reviewer-required for publication. |
| 4 | T2 Robustness | MEDIUM | 5-10 hrs | Strengthens paper claims. |
| 5 | T5 Unit tests | LOW | 6-12 hrs | Long-term maintenance. Defer until publication artifact exists. |

**Total estimated work:** 25-47 hours across 4-8 sessions.

## 5. What CAN be tested tonight vs what cannot

**CAN be tested tonight (with downloads still running):**
- T1 Reproducibility partial: re-run `step6_selectivity_v2.py` for 4 diseases. ~30 min. Real value.

**CANNOT be tested tonight:**
- T1 Reproducibility full: requires re-running Round 2.2c BeatAML predictor (multi-hour HPC job)
- T2 Robustness: requires Round 2.2c data setup that takes hours
- T3 Comparative benchmark: requires baseline implementations (multi-session work)
- T4 Biological face validity for NSCLC: requires LuCA data (still downloading)
- T5 Unit tests: requires focused multi-hour writing session

## 6. Tonight's bounded test execution (CSO call)

**T1-Lite reproducibility test.** Bounded scope, executable now, real artifact.

**Procedure:**
1. Re-run `step6_selectivity_v2.py` for all 4 diseases
2. Verify outputs match committed JSONs (excluding `computed` timestamp)
3. Re-run `step6_selectivity_v2_csv_export.py`
4. Verify mCRPC regression check (KLK3 ratio_vs_mean ≥ 10000)
5. Document results in `T1_REPRODUCIBILITY_LOG.md`

**Estimated time:** 30-45 min
**PASS criteria:** All 4 diseases regenerate same numerical outputs. mCRPC regression PASS.
**FAIL criteria:** Any output disagrees → halt and investigate.

This IS testing. It IS bounded. It IS productive. It IS appropriate scope for tonight.

## 7. Anti-scope-creep clauses (BINDING)

If during testing we discover:

- **A new test category that seems important** → log for future test plan amendment, do NOT add to current execution
- **A failing test reveals a bug** → fix the bug, NOT the test threshold
- **A test takes longer than estimated** → time-box per the spec, do NOT let one test consume the session
- **A "comprehensive" framing emerges** ("let's test everything!") → defer to plan, do NOT abandon priority order
- **External pressure to ship something** → do not reduce test rigor for speed

These clauses are binding. Same discipline as Round 2.2c.

## 8. What success looks like

After all 5 test categories complete:

- **T1 PASS** + **T4 PASS** = framework is reproducible and biologically meaningful (foundational claims defensible)
- **T3 PASS** = framework outperforms baselines (publication-ready)
- **T2 PASS** = framework is robust (high-impact paper-ready)
- **T5 PASS** = code is maintainable (long-term sustainable)

Per Round 2.2c discipline, **PASS results AND FAIL results are both publishable.** A FAIL on T3 (does not beat baselines) is an honest negative result that improves the field. We do not goalpost-move.

## 9. What this does NOT prove

Even after all tests pass, INTERCEPTA has NOT been validated for:
- Clinical use (requires IRB cohort + clinician evaluation)
- Wet lab confirmation (requires biology lab + experimental work)
- Real-world drug discovery impact (requires multi-year prospective tracking)
- Cross-disease universality at vision-scale (requires expansion beyond 4 diseases)

These are explicitly future work, multi-year arc, multi-million dollar funding scope.

## 10. Test plan amendment process

This plan can be amended (like Round 2.2c spec was amended) when:
- Reality reveals a flaw in test design → erratum document + new tag
- A test is found to be unmeasurable as designed → modify operational definition
- New data source / capability emerges → add new test category

Amendments must be documented openly in errata. No silent goalpost moves.

## 11. Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | Test plan written before any test execution. |
| P4 (fix structure, don't tune) | Test thresholds locked before execution. No post-hoc threshold adjustment. |
| P15 (only correct, honest, real science) | Pre-specifies that FAIL results are publishable. Lists what tests do NOT prove. |
| P16 (preserve past work) | Existing measurements (KLK3=16696, Venetoclax 0.91, etc.) treated as ground truth that reproducibility tests verify. |

## 12. Closure honesty

This test plan does not claim INTERCEPTA is "validated" or "production ready." It defines what current-stage testing looks like for a 1-founder framework with no wet lab and no clinical access.

Real validation for clinical use requires resources we do not currently have. This test plan prepares INTERCEPTA for the publications + funding round that would unlock those resources.

The discipline that produced 17 honest tags also produces this plan: bounded scope, falsifiable criteria, publishable failures, anti-scope-creep binding.

---

*Locked test plan. Real categories. Real priorities. Real execution starts only when each test's preconditions are met.*

— Prasad Akula & Claude (CSO)
2026-05-08
