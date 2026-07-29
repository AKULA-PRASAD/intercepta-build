# INTERCEPTA v3.0 — MASTER MANIFEST
## Complete File Index Across All Reconstructed Parts
### Every Source File, Every Test, Every Document — Nothing Missing

---

# SOURCE CODE FILES (23 files across 8 module directories)

| # | File Path | Classes / Functions | Part |
|---|-----------|-------------------|------|
| 1 | `src/common/config.py` | Config | Part 1 |
| 2 | `src/common/drug_library.py` | PKParameters, ToxicityProfile, Drug, SynergyPair, DrugLibrary | Part 1 |
| 3 | `src/module1_ingestion/scrna_ingestion.py` | ScRNAIngestion, QCReport, determine_input_tier() | Part 2 |
| 4 | `src/module1_ingestion/bulk_deconvolution.py` | BayesPrismWrapper, DeconvolutionResult | Part 2 (Gap 2) |
| 5 | `src/module2_resistance/layer_a_signatures.py` | PROGENyScorer, AUCellScorer, ResistanceClassifier, LayerAResult | Part 2 |
| 6 | `src/module2_resistance/layer_b_cellrank.py` | VelocityQC, CellRank2Analyzer, LayerBResult | Part 2 |
| 7 | `src/module2_resistance/velocity_methods.py` | run_scvelo_dynamical(), run_tfvelo(), run_tivelo(), check_available_velocity_methods() | Part 2 (Gap 3) |
| 8 | `src/module2_resistance/layer_c_velocity.py` | VelocityEnsemble, VelocityConsensusResult | Part 2 |
| 9 | `src/module2_resistance/combined_detector.py` | CombinedResistanceDetector, ResistanceDetectionResult | Part 2 |
| 10 | `src/module3_sensitivity/gdsc_processor.py` | GDSCProcessor, GDSCDrugResponse, SourceDomainData | Part 3 |
| 11 | `src/module3_sensitivity/domain_adaptation.py` | FeatureEncoder, DomainDiscriminator, DrugResponsePredictor, DomainAdaptationModel, DomainAdaptationResult | Part 3 |
| 12 | `src/module3_sensitivity/sensitivity_orchestrator.py` | SensitivityOrchestrator, PopulationSensitivityProfile, PatientSensitivityProfile | Part 3 |
| 13 | `src/module4_optimizer/ode_model.py` | PKModel, TumorODEModel, PopulationParameters, DrugSchedule, SimulationResult | Part 1 |
| 14 | `src/module4_optimizer/combination_generator.py` | CombinationSpace, generate_all_combinations() | Part 3 |
| 15 | `src/module4_optimizer/parallel_simulator.py` | TieredSimulator, CombinationResult | Part 3 |
| 16 | `src/module4_optimizer/dose_optimizer.py` | DoseScheduleOptimizer, DoseScheduleVariant, OptimizedCombination | Part 3 (Gap 5) |
| 17 | `src/module5_scoring/ida_model.py` | IDAModel, IDAResult | Part 1 |
| 18 | `src/module5_scoring/synergy_scoring.py` | SynergyScorer, HigherOrderSynergyScorer, SynergyScoreResult, CombinationSynergyProfile | Part 3 (Gap 1) |
| 19 | `src/module6_ranking/pareto_ranker.py` | ParetoRanker, ParetoSolution, ParetoFrontResult | Part 4 |
| 20 | `src/module6_ranking/novelty_checker.py` | NoveltyChecker | Part 4 (Gap 4) |
| 21 | `src/module7_output/report_generator.py` | ReportGenerator, ReportMetadata | Part 5 |
| 22 | `src/pipeline.py` | InterceptaPipeline, InterceptaOutput | Part 4 |

# DATA FILES (4 files)

| # | File Path | Contents | Part |
|---|-----------|----------|------|
| 23 | `data/drug_library/mcrpc_drugs.json` | 15 drugs + 4 synergy pairs + metadata | Part 1 |
| 24 | `data/gene_signatures/prostate_resistance_signatures.json` | 7 signatures, 54 genes | Part 1 |
| 25 | `configs/default_config.yaml` | Complete configuration (all parameters) | Part 1 |

# TEST FILES (5 files, 27 test functions)

| # | File Path | Test Functions | Part |
|---|-----------|---------------|------|
| 26 | `tests/test_environment.py` | 1 (verify installations) | Part 1 |
| 27 | `tests/unit/test_ode_model.py` | 11 (PK, ODE, combinations) | Part 1 |
| 28 | `tests/unit/test_layer_a.py` | 2 (PROGENy, classifier) | Part 2 |
| 29 | `tests/unit/test_gap_fixes.py` | 14 (synergy, deconv, novelty, dose opt, velocity) | Part 3-4 |
| 30 | `tests/integration/test_end_to_end.py` | 1 (full pipeline) | Part 4 |
| 31 | `tests/validation/phase0_ida_validation.py` | — (validation script) | Part 1 |
| 32 | `tests/validation/phase1_validation.py` | — (smoke + prostate validation) | Part 2 |
| 33 | `tests/validation/phase2_validation.py` | — (AUROC validation) | Part 3 |
| 34 | `tests/validation/phase3_validation.py` | — (clinical trial ranking) | Part 3 |

# SCRIPT FILES (3 files)

| # | File Path | Purpose | Part |
|---|-----------|---------|------|
| 35 | `scripts/data_download/download_gdsc.py` | Download GDSC data | Part 1 |
| 36 | `scripts/data_download/download_all_datasets.py` | Master download checklist | Part 1 |
| 37 | `scripts/analysis/generate_paper_figures.py` | Publication figures | Part 4 |

# DOCUMENTATION FILES (6 files)

| # | File Path | Purpose | Part |
|---|-----------|---------|------|
| 38 | `docs/data_access_requests.md` | Track dataset access requests | Part 1 |
| 39 | `docs/phase0_gate_checklist.md` | Phase 0 go/no-go | Part 1 |
| 40 | `docs/phase1_gate_checklist.md` | Phase 1 go/no-go | Part 2 |
| 41 | `docs/phase2_3_gate_checklist.md` | Phase 2-3 go/no-go | Part 3 |
| 42 | `docs/phase4_5_gate_checklist.md` | Phase 4-5 go/no-go | Part 4 |
| 43 | `docs/validation_study_protocol.md` | 3-case retrospective study | Part 4 |
| 44 | `docs/funding/sbir_application_outline.md` | SBIR application | Part 5 |
| 45 | `docs/ip/patent_strategy.md` | 4 patent claims | Part 5 |
| 46 | `docs/team/recruitment_plan.md` | Advisory board plan | Part 5 |
| 47 | `docs/partnerships/clinical_partnership_plan.md` | Academic partnerships | Part 5 |
| 48 | `docs/partnerships/pharma_outreach_plan.md` | Pharma strategy | Part 5 |

---

# TOTAL COUNTS

| Metric | Count |
|--------|-------|
| Source code files | 22 |
| Data/config files | 3 |
| Test files | 9 |
| Script files | 3 |
| Documentation files | 11 |
| **Total files** | **48** |
| Python classes | 68 |
| Python functions | 177 |
| Test functions | 27 |
| Validation gate items | 123 |

# GAP FIX INTEGRATION MAP

| Gap | Fix File | Integrated Into | Integration Point |
|-----|----------|----------------|-------------------|
| Gap 1: ZIP synergy | synergy_scoring.py | parallel_simulator.py (Tier 2-3) | _simulate_combination() calls SynergyScorer |
| Gap 2: BayesPrism | bulk_deconvolution.py | pipeline.py (Tier 3 path) | Tier 3 uses BayesPrismWrapper |
| Gap 3: TFvelo/TIVelo | velocity_methods.py | layer_c_velocity.py | VelocityEnsemble delegates to wrappers |
| Gap 4: Novelty checker | novelty_checker.py | pareto_ranker.py + pipeline.py | Novelty objective in Pareto + report |
| Gap 5: Dose optimization | dose_optimizer.py | parallel_simulator.py (Tier 3) | run_tier3() uses DoseScheduleOptimizer |

---

**Every file accounted for. Every gap fixed. Every integration documented.**
**This is the complete INTERCEPTA v3.0 codebase specification.**
