# INTERCEPTA Phase B Layer 4 — Artifact 4.1
## Implementation Order Specification

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** Layer 2 + Layer 3 of Phase B COMPLETE (L2.1 LOCKED; L2.2/L2.3/L2.4/L3.1/L3.2/L3.3 PROPOSED)
**Parent decisions:** All 10 Decisions v2 inform implementation order; Decision 9 v2 (compute) most binding on sequencing
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping:** Phase B implementation order patterns reused for Phase F's Universal Net + 6 Scouts integration; Phase F adds federation, regulatory, deployment phases not in scope here
**Target length per Phase B Plan v2:** 3-4K words
**Filename:** INTERCEPTA_FV_L4_1_Implementation_Order_Specification_2026-05-11.md

---

## §0 Identification and Scope

### 0.1 What This Document Is

L4.1 is the **Implementation Order Specification** — the first artifact of Phase B Layer 4. L4.1 specifies the topological-sort sequence in which Layer 5 code gets written, the dependency graph between code modules, the milestone checkpoints with deliverables, and the per-stage handoff criteria.

L4.1 converts the architectural specs (Layers 2-3) into an **executable build plan**: which module is written first, what its tests look like, when it can be considered "done enough" to unblock downstream work, and where the first empirical V0 result emerges.

### 0.2 What This Document Is Not

L4.1 is NOT:
- The testing strategy (L4.2 specifies test coverage requirements)
- The failure mode catalog (L4.3 specifies how systems break and how the code handles failures)
- The Phase 8 audit checklist (separate pre-implementation review artifact)
- A specific timeline in calendar days (depends on Layer 5 staffing — CEO-CSO duo pace)
- A Kanban / Jira backlog (Layer 5 implementation operational; L4.1 specifies dependency order, not project management)

### 0.3 The Implementation Order Question

After Layers 2-3 LOCK, we have ~57K words of architectural specs. The implementation order question is:

**Given all these specs, in what dependency-respecting sequence does code get written so that:**
1. **No module is built before its dependencies exist** (avoid stub-stubbing-stubs)
2. **First empirical V0 result emerges as early as possible** (validate the pipeline early)
3. **The Souza-Mehta matched-pair discipline is preserved** (paradigm D parameter-free must be ready before paradigm A FM at V0)
4. **The 4-substrate ablation is tractable** (caching infrastructure must exist before substrate sweeps)
5. **Failure detection is early** (test infrastructure must exist before integration)

L4.1 answers this with **8 sequential stages**, each with explicit prerequisites, deliverables, and handoff criteria.

### 0.4 Phase B Plan v2 Compliance

- Layers 2-3 of Phase B COMPLETE 2026-05-11
- **L4.1 → PROPOSED (this document)**
- L4.2 Testing → pending; consumes L4.1 sequence
- L4.3 Failure Modes → pending; consumes L4.1 + L4.2
- After Layer 4 LOCK: Phase 8 audit; then Layer 5 (CODE STARTS)

### 0.5 Document Conventions

- **BINDING** — stage order cannot be modified without amendment + CEO+CSO co-sign
- **DEFAULT** — within-stage ordering revisitable per §11.5
- "Done enough" = handoff criteria met (specific per stage)
- All paths reference `/Users/kalki/INTERCEPTA/` (local) or `/scratch/akula.pra/INTERCEPTA/` (Northeastern Explorer)

---

## §1 The 8-Stage Implementation Sequence (BINDING)

```
STAGE 1: Foundation (environment + repo + CI)
   ↓
STAGE 2: Data layer (loaders + caching infrastructure)
   ↓
STAGE 3: Substrate adapters (L2.1 implementation)
   ↓
STAGE 4: L7 head (L2.2 implementation)
   ↓
STAGE 5: OOD stack (L2.3) + Interpretability (L2.4) [PARALLEL]
   ↓
STAGE 6: Validation pipeline (L3.1 + L3.2)
   ↓
STAGE 7: V0 → V1 → V2 → V3 → V4 → V5 evaluations [SEQUENTIAL]
   ↓
STAGE 8: V6 cross-disease evaluation (L3.3)
   ↓
[Phase B Layer 5 COMPLETE]
```

Stages 1-5 are **infrastructure + components**. Stages 6-8 are **evaluation + empirical results**. The first empirical result (V0 AUROC for first substrate) emerges at the end of Stage 7 day-1; full V0-V5 cascade results at end of Stage 7; V6 universality verdict at end of Stage 8.

---

## §2 Stage 1 — Foundation

### 2.1 Prerequisites

Layer 4 LOCK (this document + L4.2 + L4.3 LOCKED). Phase 8 audit passed.

### 2.2 Deliverables

**1.1 Repository structure (local + GitHub):**
```
~/INTERCEPTA/
├── code/
│   ├── intercepta/
│   │   ├── __init__.py
│   │   ├── data/                  Stage 2
│   │   ├── substrates/             Stage 3
│   │   ├── l7/                     Stage 4
│   │   ├── ood/                    Stage 5
│   │   ├── interpretability/       Stage 5
│   │   ├── validation/             Stage 6
│   │   └── utils/
│   ├── tests/
│   ├── scripts/                    SLURM job scripts
│   ├── notebooks/                  ad-hoc analysis
│   └── configs/                    Hydra-style configs
├── docs/research/                  Layer 1-4 specs (existing)
├── pyproject.toml
├── README.md
└── .github/workflows/              CI
```

**1.2 Python environment:**
- Python 3.11 (scvi-tools compatibility)
- Conda env file `environment.yml` with: torch 2.x, scvi-tools 1.x, anndata, scanpy, scikit-learn, scipy, statsmodels, captum 0.7+, shap 0.45+, pandas, numpy, h5py, pytest, hydra-core, mlflow
- Conda env reproducible: `conda env create -f environment.yml`

**1.3 GitHub CI workflow:**
- `.github/workflows/test.yml` running pytest on push to main
- Pre-commit hooks: ruff format + ruff lint
- License header check (per Decision 10 v2 open-source consistency)

**1.4 Northeastern Explorer onboarding:**
- Verify GPU access: `srun --partition=gpu --gres=gpu:a100:1 nvidia-smi` produces A100 output
- Verify scratch quota: `~/scratch/akula.pra/INTERCEPTA/` has ≥ 2 TB available
- Submit + run "hello world" SLURM job to confirm pipeline

**1.5 MLflow tracking server (or equivalent):**
- Centralized experiment registry per Decision 8 v2 Commitment 5 + Decision 9 v2 budget tracking
- Local MLflow file backend acceptable for Phase B; remote tracking server Phase F

### 2.3 Handoff Criteria (Stage 1 → Stage 2)

- [ ] Repository structure created and pushed to GitHub
- [ ] Conda environment installs cleanly on Mac (`conda env create -f environment.yml`)
- [ ] Conda environment installs cleanly on Explorer login node
- [ ] CI workflow runs and reports pass on a trivial test
- [ ] First SLURM job runs and writes output to scratch
- [ ] MLflow tracking server logs a test experiment

### 2.4 Stage 1 Effort Estimate

Calendar: 2-4 working days for CEO-CSO duo. Most of this is environment debugging on Explorer.

---

## §3 Stage 2 — Data Layer

### 3.1 Prerequisites

Stage 1 handoff met.

### 3.2 Deliverables

**2.1 `intercepta.data.loaders`:**
- `load_dataset(name: str) -> AnnDataset` for: gdsc, ccle, ctrp, tcga, nci_pdxnet, hcmi, sanger_organoid, retrospective_clinical, smillie_uc, mathys_ad, hpap_t2d, (rest as Layer 5 adds)
- Each loader handles: download (if needed; cached locally), parsing into AnnData, basic QC (filter low-quality cells/genes), metadata normalization (cancer type, drug name, drug response label)

**2.2 `intercepta.data.cache`:**
- Hash-key-based caching for substrate embeddings, OOD KDEs, conformal calibration, interpretability attributions, V-level predictions
- Cache invalidation on spec SHA change (Layers 2-3 spec SHA tracked in cache key)

**2.3 `intercepta.data.harmonization` (Decision 2 v2 minimal Phase B placeholder):**
- Light wrapper around scvi-tools' integration; INTEGRATION method default per L2.1
- NOT the full Decision 2 v2 specification (that's Layer 5 + future Layer 4 spec)

**2.4 `intercepta.data.splits`:**
- Standardized train/val/test splits per V-level
- IMPROVE-published splits for V1 (load from IMPROVE-workflow accessor)
- Stratified by cell-line lineage where applicable (per L3.1 J1)

### 3.3 Handoff Criteria (Stage 2 → Stage 3)

- [ ] `load_dataset("gdsc")` returns AnnData with ≥1000 (cell line, drug) pairs
- [ ] `load_dataset("ccle")` and `load_dataset("ctrp")` work for V1 cross-pair
- [ ] Cache layer round-trips a test tensor with hash-keyed retrieval
- [ ] IMPROVE splits load and partition GDSC/CCLE/CTRP into standardized train/test
- [ ] Per-dataset unit tests pass (basic shape + non-empty assertions)

### 3.4 Stage 2 Effort Estimate

Calendar: 1-2 weeks. Data loading is "boring but high-value"; getting GDSC alone is multi-day.

---

## §4 Stage 3 — Substrate Adapters (L2.1)

### 4.1 Prerequisites

Stage 2 handoff met. L2.1 LOCKED.

### 4.2 Deliverables

**3.1 `intercepta.substrates.base.SubstrateInterface`:**
- Abstract base per L2.1 §3
- `fit()`, `load_pretrained()`, `encode()`, `project_to_canonical()`, `NATIVE_DIM` property

**3.2 `intercepta.substrates.scvi.SCVISubstrate`:**
- Wraps scvi-tools scVI per L2.1 §4
- KDE fit on training latents for L2.3 Layer 5.1 use (deferred but interface ready)

**3.3 `intercepta.substrates.sctop.SCTOPSubstrate`:**
- Souza-Mehta scTOP parameter-free per L2.1 §5
- BINDING per L2.1 §1.2 errata: NATIVE_DIM lifecycle requires fit()/load_pretrained() before output_dim
- Linear projection coefficients exposed for L2.4 Scale 5 Branch B

**3.4 `intercepta.substrates.fm.FMSubstrate`:**
- scFoundation-100M default (smallest of FM family; quickest to validate before scaling to UCE/scGPT/Geneformer)
- Encapsulates pretrained weights loading from Hugging Face
- `project_to_canonical()` zero-pads/projects to 512-canonical per L2.1 §1.2 errata

**3.5 `intercepta.substrates.pca_hvg.PCAHVGSubstrate`:**
- PCA on HVG-selected genes per L2.1 §4 Baseline A
- BINDING per Souza-Mehta methodological bar

### 4.3 Handoff Criteria (Stage 3 → Stage 4)

- [ ] All 4 substrate adapters instantiate without errors
- [ ] `encode()` on a small AnnData returns expected shape per substrate.NATIVE_DIM
- [ ] `project_to_canonical()` always returns 512-dim regardless of substrate
- [ ] Cached embedding round-trip works for all 4 substrates
- [ ] L2.1 unit tests pass (per-substrate canonical shape, NATIVE_DIM lifecycle)
- [ ] Souza-Mehta methodological readiness: PCA+HVG baseline embedding cached at V0-targetable scale

### 4.4 Stage 3 Effort Estimate

Calendar: 2-3 weeks. FM substrate weight loading + scvi-tools integration is the longest sub-task.

---

## §5 Stage 4 — L7 Drug Response Head (L2.2)

### 5.1 Prerequisites

Stage 3 handoff met. L2.2 LOCKED.

### 5.2 Deliverables

**4.1 `intercepta.l7.L7Head` (per L2.2 §1):**
- 6-slot architecture: substrate adapter (Slot 1) + MoLFormer drug embed (Slot 2) + chemCPA amortizer (Slot 3) + GEARS 3-graph attention (Slot 4) + DPP-diversity (Slot 5) + PaSCient attention pooling (Slot 6)
- `forward()` returns L7Output with predictions + attribution_hooks tensors

**4.2 `intercepta.l7.ensemble.L7Ensemble`:**
- N=5 Deep Ensemble per Decision 5 v2 + L2.2 §1.5
- BINDING per Drift Finding 8: ensemble seeds {42, 1337, 2023, 9, 31337}; per-head saved separately

**4.3 `intercepta.l7.slots.molformer.MoLFormerEmbed`:**
- MoLFormer DEFAULT per L2.2 §3.2 BINDING
- Drug SMILES → embedding; cached per drug

**4.4 `intercepta.l7.slots.chemcpa.ChemCPAModule`:**
- chemCPA amortized perturbation latent per L2.2 §4
- CPA disentangled latent (for L2.4 Scale 2 attribution intrinsic)

**4.5 `intercepta.l7.slots.gears.GEARSGraphAttention`:**
- 3-graph attention per L2.2 §5 Drift Finding 7 BINDING
- scRank gene-gene attention edge-weight init
- GO-graph attention pathway component

**4.6 `intercepta.l7.slots.dpp.DPPSlot5`:**
- DPP-diversity DEFAULT per L2.2 J4
- (Alternative: drug2cell — Layer-5-revisitable)

**4.7 `intercepta.l7.slots.pascient.PaSCientAttention`:**
- PaSCient attention pooling DEFAULT per L2.2 §6 + Drift Finding 10
- Learned-weighted auto-fallback path per Drift Finding 10

### 5.3 Handoff Criteria (Stage 4 → Stage 5)

- [ ] L7Head instantiates with any of the 4 substrates from Stage 3
- [ ] Forward pass produces L7Output with all attribution_hooks populated
- [ ] N=5 Deep Ensemble runs; 5 separate checkpoints saved
- [ ] L2.2 unit tests pass (per-slot shape contracts; full forward integration)
- [ ] First overfitting test: L7 trains on tiny GDSC subset to high training AUROC (sanity)

### 5.4 Stage 4 Effort Estimate

Calendar: 3-4 weeks. 6 slots × careful unit test per slot. MoLFormer + GEARS graph + chemCPA each are non-trivial.

---

## §6 Stage 5 — OOD (L2.3) + Interpretability (L2.4) [PARALLEL]

### 6.1 Prerequisites

Stage 4 handoff met. L2.3 + L2.4 LOCKED.

### 6.2 Why Parallel

L2.3 OODStack consumes L7Output but does NOT modify L7. L2.4 InterpretabilityStack consumes L7Output + OODOutput verdict. The shared dependency is L7's attribution hooks; both can be built independently once L7 is stable.

CEO-CSO duo: split sub-stages 5a (OOD) and 5b (Interpretability) if convenient; or serialize 5a → 5b if focus discipline preferred.

### 6.3 Deliverables — Stage 5a OOD Stack (L2.3)

**5a.1 `intercepta.ood.layer_5_1.SubstratePosteriorRegistry`:**
- Substrate-conditional posterior dispatcher per L2.3 §3
- SCVIPosterior (scVI family), FMDeterministicPosterior with KDE (FM substrates), SCTOPPosterior (cosine+entropy), PCAPosterior

**5a.2 `intercepta.ood.layer_5_2.EpistemicQuantifier`:**
- Variance across L7Ensemble N=5 predictions per L2.3 §4
- MIMO8 + MC Dropout T=50 fallbacks per Drift Finding 8 BINDING

**5a.3 `intercepta.ood.layer_5_3.ConformalPrediction`:**
- Studentized non-conformity DEFAULT per L2.3 J5
- Standard split-conformal calibration
- Cross-disease recalibration with min_samples=50 + has_recalibrated_guarantee flag per L2.3 §5.5

**5a.4 `intercepta.ood.layer_5_4.EnergyScoring`:**
- E(x) = -T·log Σ exp(z_i/T) per L2.3 §6
- 95th-percentile threshold default

**5a.5 `intercepta.ood.OODStack`:**
- Composes all 4 layers into the OODStack class per L2.3 §1
- OODOutput schema BINDING per Decision 5 v2

### 6.4 Deliverables — Stage 5b Interpretability Stack (L2.4)

**5b.1 `intercepta.interpretability.scale_1_geometric.GeometricAttributor`:**
- Kendiukhov spectral analysis (FM-only) per L2.4 §3

**5b.2 `intercepta.interpretability.scale_2_drugclass.DrugClassAttributor`:**
- CPA latent inspection per L2.4 §4 (free, built into L7)

**5b.3 `intercepta.interpretability.scale_3_pathway.PathwayAttributor`:**
- GEARS GO + Beyondcell BCS per L2.4 §5 Drift Finding 7 BINDING

**5b.4 `intercepta.interpretability.scale_4_grn.GRNAttributor`:**
- scRank GRN propagation per L2.4 §6

**5b.5 `intercepta.interpretability.scale_5_gene.GeneLevelAttributor`:**
- 4-branch substrate-conditional per L2.4 §7
- Branch A (FM/EIG+SmoothGrad), B (scTOP/linear), C (scVI/VAE-IG), D (PCA/loadings)

**5b.6 `intercepta.interpretability.scale_6_spatial.SpatialAttributor`:**
- River two-branch DSEP (spatial-only) per L2.4 §8

**5b.7 `intercepta.interpretability.scale_7_patient.PatientAttributor`:**
- SHAP kernel DEFAULT per L2.4 §9

**5b.8 `intercepta.interpretability.consistency.ConsistencyChecker`:**
- 4 cross-scale consistency checks per L2.4 §10 BINDING

**5b.9 `intercepta.interpretability.InterpretabilityStack`:**
- Composes all 7 scales + consistency per L2.4 §1.3
- Verdict-conditional gating per L2.4 §1.6 BINDING

### 6.5 Handoff Criteria (Stage 5 → Stage 6)

- [ ] OODStack instantiates and produces OODOutput on test data
- [ ] All 4 OOD verdict categories produced (confident_predict / abstain_aleatoric / abstain_epistemic / abstain_ood) at expected rates on synthetic test
- [ ] Conformal calibration min_samples=50 floor enforced with has_recalibrated_guarantee flag
- [ ] InterpretabilityStack instantiates and produces InterpretabilityOutput on test predictions
- [ ] All 7 scales execute; Scale 1 auto-skips on non-FM; Scale 6 auto-skips on non-spatial
- [ ] Substrate-conditional Scale 5 routes correctly for all 4 substrates
- [ ] 4 cross-scale consistency checks compute (may fail on small test data; computation not pass-criteria checked at this stage)
- [ ] L2.3 + L2.4 unit tests pass

### 6.6 Stage 5 Effort Estimate

Calendar: 5-7 weeks (parallel a+b). OOD is mathematically dense; interpretability has 7 sub-modules. Captum + SHAP integration adds week-scale overhead.

---

## §7 Stage 6 — Validation Pipeline (L3.1 + L3.2)

### 7.1 Prerequisites

Stage 5 handoff met. L3.1 + L3.2 LOCKED.

### 7.2 Deliverables

**6.1 `intercepta.validation.cascade.CascadeRunner`:**
- Per L3.1 §1.3; composes L7Ensemble + OODStack + InterpretabilityStack
- `run_cascade(start_at, stop_on_first_failure)` per L3.1 §1.3

**6.2 `intercepta.validation.evaluators` (one per V-level):**
- `V0WithinDatasetEvaluator` per L3.1 §3
- `V1CrossDatasetEvaluator` per L3.1 §4
- `V2CellLineToOrganoidEvaluator` per L3.1 §5
- `V3CellLineToTumorEvaluator` per L3.1 §6
- `V4CellLineToPDXEvaluator` per L3.1 §7
- `V5PDXToPatientEvaluator` per L3.1 §8
- `V6CrossDiseaseEvaluator` per L3.1 §9 (stub; full impl Stage 8)

**6.3 `intercepta.validation.termination.TerminationLogic`:**
- Per L3.1 §2.2; hard/soft/pass-with-reservations dispatcher

**6.4 `intercepta.validation.criteria` (per-V-level criterion checkers):**
- 8 criterion checks per V-level per L3.2
- Naming convention: `_check_v{N}_c{C}_*` per L3.2 §13.5
- 56 functions total (8 × 7)

**6.5 `intercepta.validation.reporting.CascadeReport`:**
- Per L3.1 §1.4; mandatory cross-level reporting per Decision 6 v2 7 elements

### 7.3 Handoff Criteria (Stage 6 → Stage 7)

- [ ] CascadeRunner instantiates with all Layer 2 components
- [ ] V0WithinDatasetEvaluator executes end-to-end on synthetic test data
- [ ] All 8 V0-criterion checkers (V0-C1 through V0-C8) return PassFailResult on synthetic data
- [ ] TerminationLogic correctly classifies pass/soft/hard on test cases
- [ ] CascadeReport schema serializes to JSON with all required fields
- [ ] Pipeline unit tests pass

### 7.4 Stage 6 Effort Estimate

Calendar: 3-4 weeks. The 56 criterion checkers are mostly small functions but require careful threshold + statistical-test wiring.

---

## §8 Stage 7 — V0 → V5 Empirical Evaluation [SEQUENTIAL]

### 8.1 Prerequisites

Stage 6 handoff met. Required datasets accessible (Stage 2 already validated this).

### 8.2 Stage 7 Is Different

Unlike Stages 1-6 (infrastructure), Stage 7 is **empirical evaluation runs**. The deliverables are NOT code; they are:
- Trained model checkpoints per (substrate × V-level)
- Cached predictions per (substrate × V-level)
- CascadeReport JSON per (substrate × V-level)
- Empirical pass/fail determination per L3.2 criteria

### 8.3 Per-V-Level Sequence

Each V-level (V0 through V5) runs:
1. Train L7Ensemble on V-level training data for each of 4 substrates (4 separate training runs)
2. Run cascade evaluator + 8 criterion checks
3. Cache predictions + OODOutput + InterpretabilityOutput
4. Generate CascadeReport
5. CEO + CSO review: pass/soft/hard per TerminationLogic; decide next-V-level

**Critical:** Souza-Mehta matched-budget discipline enforced. All 4 substrates train at matched hyperparameter trial counts per V-level.

### 8.4 V-Level Compute Estimates

Per L3.1 + Decision 9 v2:
- V0: ~12-20 GPU-days for 4-substrate ablation (5-fold CV × N=5 ensemble)
- V1: ~24-48 GPU-days (IMPROVE 6 cross-pairs × 4 substrates)
- V2: ~3-5 GPU-days per substrate × 4 = ~12-20 GPU-days
- V3: ~3-5 GPU-days per substrate × 4 = ~12-20 GPU-days (+ pathway baseline)
- V4: ~5-8 GPU-days for 4-substrate ablation
- V5: ~4-6 GPU-days

**Total V0-V5: ~70-120 GPU-days.** With Decision 9 v2 single-A100 + 10× SLURM concurrency, ~8-14 wall-clock weeks for Stage 7.

### 8.5 First Empirical Result Milestone

**Stage 7 Day 1, V0 evaluation completes for first substrate (likely scTOP — cheapest):** the FIRST empirical INTERCEPTA AUROC result.

This is the project's first empirical evidence. After this point, INTERCEPTA is no longer "in spec"; it is generating empirical findings.

### 8.6 Handoff Criteria (Stage 7 → Stage 8)

Per V-level CEO+CSO sign-off:
- [ ] V0: all 4 substrates pass V0-C1 through V0-C8 (or document soft termination)
- [ ] V1: cross-dataset evaluation completes; V0→V1 gap reported
- [ ] V2: organoid evaluation completes; INTERCEPTA V2 standard documented
- [ ] V3: TCGA evaluation completes; Tang 2022 floor passed or hard-terminate
- [ ] V4: PDX evaluation completes; concordant/non-concordant subsets separately reported
- [ ] V5: clinical retrospective completes; ECE ≤ 0.05 verified; statistical power reported
- [ ] V0-V5 CascadeReport generated for each substrate
- [ ] Souza-Mehta matched-pair compute log verified (paradigm D ≥ 25% paradigm A trials)

### 8.7 Possible Soft Terminations During Stage 7

Per L3.1 §2.2 TerminationLogic:
- V2 organoid data unavailable → soft terminate; document and proceed to V3
- V3 AUROC = 0.77 exactly (matches Tang 2022 but doesn't exceed) → soft terminate; revise Decision 1 v2 substrate choice
- V5 power insufficient → soft terminate; document and proceed to V6 with caveats

Each soft termination triggers focused Decision revision per Decision 6 v2 §"Soft Termination" — NOT vision pivot.

---

## §9 Stage 8 — V6 Cross-Disease Evaluation (L3.3)

### 9.1 Prerequisites

Stage 7 handoff met (V0-V5 evaluations complete). L3.3 LOCKED. V6 dataset access verified (Stage 2 partial; final Stage 8 verification).

### 9.2 Deliverables

**8.1 SLURM job array execution per L3.3 §5:**
- 140-cell array submission
- 10× concurrent SLURM jobs
- ~15-20 wall-clock days total

**8.2 Per-(paradigm × disease × tissue × drug) cell results:**
- predictions.h5
- ood_output.h5
- interpretability_output.h5
- per_criterion_pass_fail.json (V6-C1 through V6-C8)

**8.3 V6 aggregation per L3.3 §6:**
- Per-disease aggregation (across tissues + drugs)
- Per-therapeutic-area determination (≥0.65 on ≥2 areas BINDING)
- 4-paradigm matrix per L3.3 §6.4
- OOD attribution determination (≥70% epistemic on failures BINDING)
- Interpretability transfer determination (≥80% canonical recovery BINDING)

**8.4 V6 final verdict:**
- Universality PASSES: at least 1 paradigm meets V6-C1 on ≥2 therapeutic areas
- Universality FAILS: no paradigm meets bar → Charter §1.1 narrowed per Decision 8 v2 termination criteria

### 9.3 Handoff Criteria (Stage 8 → Phase B Layer 5 COMPLETE)

- [ ] All ~140 V6 cells evaluated (or documented data-access exclusions)
- [ ] CascadeReport V6 section populated with 4-paradigm matrix
- [ ] V6-C1 through V6-C8 evaluated for each cell
- [ ] Universality verdict (pass / fail / pass-with-reservations) determined
- [ ] Q5 attribution accuracy ≥ 70% verified or documented failure
- [ ] Q7 interpretability transfer ≥ 80% verified or documented failure
- [ ] Souza-Mehta paradigm D within 5pp of best paradigm OR architectural justification documented

### 9.4 Stage 8 Effort Estimate

Calendar: 4-6 weeks for SLURM execution + aggregation + verdict. Includes buffer for resubmissions and OOMs.

### 9.5 Phase B Layer 5 COMPLETE

When Stage 8 handoff met, **Phase B is COMPLETE**. INTERCEPTA has:
- 4-substrate Souza-Mehta-matched empirical comparison V0-V6
- Universality verdict per Charter §1.1
- Mechanism trace per Decision 7 v2 across all evaluation cells
- Calibrated uncertainty per Decision 5 v2 across all evaluation cells
- Open-source code per Decision 10 v2
- Honest reporting per Charter §1.3 + §10 P15

This is the deliverable for Phase B → Phase F transition per Charter v1.2 §1.7.

---

## §10 Cross-Cutting Concerns

### 10.1 Experiment Tracking (per Decision 8 v2 Commitment 5)

Every training run + evaluation run logs to MLflow:
- Hyperparameters per trial
- Compute consumed (GPU-hours, memory)
- Cache hits/misses
- L3.2 criterion pass/fail per evaluation

This is the operational instantiation of "reviewer-style scrutiny" per Decision 8 v2: when a publication is written, the experiment registry produces the matched-budget evidence.

### 10.2 Cache Coherence (per L3.1 §2.3)

Cache key invalidation on spec SHA change:
- L2.1 SHA → invalidates substrate embeddings
- L2.2 SHA → invalidates L7 predictions
- L2.3 SHA → invalidates OOD outputs
- L2.4 SHA → invalidates attribution caches
- L3.1/L3.2/L3.3 SHA → invalidates validation cascade results

Layer 5 implementation includes cache-invalidation utility script.

### 10.3 Reproducibility (per Charter v1.2 §1.3)

- All ensemble seeds BINDING per Drift Finding 8 {42, 1337, 2023, 9, 31337}
- All hyperparameter seeds in MLflow
- Conda env pinned exactly
- Dataset version hashes recorded

A reproducer should be able to clone the repo, install env, and recreate any (substrate × V-level) result.

### 10.4 Failure Recovery (per L4.3 — to be specified)

L4.1 commits the order; L4.3 will specify how each stage's failures are handled. The placeholder pattern:
- Stage 1 failure → environment issue; debug locally before Explorer
- Stage 2-3 failure → data or substrate issue; resolve before downstream
- Stage 4 failure → architectural issue; potentially re-spec L2.2
- Stage 5 failure → either OOD or interpretability sub-issue; isolate
- Stage 6 failure → pipeline integration issue; identify which Layer 2 component is at fault
- Stage 7 failure → empirical result issue; per-V-level TerminationLogic decides
- Stage 8 failure → V6 universality issue; per Decision 8 v2 termination criteria

L4.3 will catalog the specific failure modes and recovery procedures.

---

## §11 Pass Criteria for L4.1 LOCK

### 11.1 Sequence Pass Criteria (BINDING)

- **A1:** 8 stages enumerated with prerequisites + deliverables + handoff criteria
- **A2:** Stages 1-6 are infrastructure; Stage 7 produces first empirical result; Stage 8 is V6 universality
- **A3:** Souza-Mehta matched-pair discipline preserved across all 4 substrates from Stage 3 onward
- **A4:** First empirical result milestone identified (Stage 7 Day 1, first substrate V0)
- **A5:** Compute estimates within Decision 9 v2 envelope (V0-V5 ~70-120 GPU-days; V6 ~100-200 GPU-days; total ~200-300 GPU-days)

### 11.2 Cross-Decision Compatibility (BINDING)

- **X1:** L4.1 consumes all 7 Phase B Layer 2-3 specs
- **X2:** Decision 9 v2 compute envelope respected per §8.4 + §9.4
- **X3:** Decision 8 v2 Commitment 5 (Souza-Mehta) enforced per §8.6 paradigm D matched-budget check
- **X4:** Decision 5 v2 + Decision 6 v2 BINDING constraints enforced through per-stage handoff criteria
- **X5:** Decision 10 v2 open-source: all listed Python packages open (BSD/MIT/Apache)
- **X6:** MLflow tracking server experiment registry per Decision 8 v2 Commitment 5

### 11.3 Documentation Pass Criteria

- **D1:** L4.1 referenced by L4.2 (testing strategy operates within L4.1 stages) + L4.3 (failure modes mapped to L4.1 stages)
- **D2:** Each L4.1 stage maps cleanly to a directory in `~/INTERCEPTA/code/intercepta/`
- **D3:** Drift catalog this session: 0 new instances

### 11.4 CEO Sign-Off

L4.1 advances from PROPOSED to LOCKED when:
1. CEO reviews §1 8-stage sequence
2. CEO confirms §11.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag phase-b-l4.1-locked pushed to origin

### 11.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | Stage 5 ordering | parallel a+b | sequential 5a→5b | Single-person focus discipline preferred |
| J2 | Stage 3 substrate order | scTOP → PCA → scVI → FM | FM first | Validating quickest-to-implement first |
| J3 | First FM in Stage 3 | scFoundation-100M | UCE / scGPT / Geneformer | Empirical loading complexity |
| J4 | MLflow vs Weights & Biases | MLflow | W&B | Hosted tracking preference |
| J5 | Stage 1 CI provider | GitHub Actions | GitLab CI | Pricing / Explorer integration |
| J6 | First V-level evaluated | V0 | V1 (skip V0) | NOT recommended per Decision 6 v2 "Why not skip V0" |
| J7 | Stage 4 first substrate × first slot integration | scTOP + Slot 1 only | full 6-slot integration | Bootstrapping speed |
| J8 | Stage 6 stub V6 evaluator vs full | stub only at Stage 6 | full V6 at Stage 6 | V6 complexity scope |
| J9 | Per-stage handoff CEO review | yes (every stage) | only V-level evaluations | CEO bandwidth |
| J10 | Resubmission policy on Stage 7 OOMs | auto-retry 3× then alert | manual review every OOM | SLURM operational friction |

### 11.6 Honest Limitations (per Charter §10 P15 BINDING)

- **The 8-stage sequence is optimistic on calendar.** 2-3 month elapsed for Stages 1-6, plus 8-14 weeks Stage 7, plus 4-6 weeks Stage 8 = ~6-9 months for full Phase B Layer 5. Real engineering work consistently overruns; honest 8-12 month estimate.
- **Stage 2 data access is the biggest schedule risk.** Retrospective clinical (V5) and cross-disease scRNA-seq (V6) access is non-trivial.
- **Stage 5 parallel is conditional on CEO-CSO duo capacity.** If single-person bandwidth dominant, serial 5a→5b adds ~3-4 weeks.
- **Stage 7 sequential V-levels means a V3 failure delays V4-V5.** The cascade is sequential by design (Decision 6 v2); accepting this delay is the cost of falsifiability.
- **First empirical result at Stage 7 Day 1 is the V0 sanity check, not a clinical claim.** V0 is the most permissive evaluation; INTERCEPTA's value claim is V3-V6.

---

## §12 What L4.1 Does NOT Lock

- The testing strategy (L4.2)
- The failure mode catalog (L4.3)
- The Phase 8 pre-implementation audit checklist (separate artifact)
- The Phase F transition criteria (Phase F-specific spec)
- The Layer 5 calendar / Gantt chart (operational, not strategic)

---

## §13 Cross-Decision Implications

- **Decision 1 v2 (substrate flexibility):** Stage 3 implements all 4 substrate families
- **Decision 2 v2 (harmonization):** Stage 2 §3.3 minimal Phase B placeholder; full harmonization is Layer 5 + future Layer 4 spec
- **Decision 3 v2 (architectural identities):** Drift Finding 7 BINDING placement enforced per Stage 4 + Stage 5 deliverables
- **Decision 4 v2 (L7 architecture):** Stage 4 implements L7 6-slot per L2.2
- **Decision 5 v2 (OOD):** Stage 5a implements OOD stack per L2.3
- **Decision 6 v2 (validation):** Stage 6 + Stage 7 implement V0-V5 cascade per L3.1 + L3.2
- **Decision 7 v2 (interpretability):** Stage 5b implements 7-scale stack per L2.4
- **Decision 8 v2 (universality):** Stage 8 implements V6 cross-disease per L3.3
- **Decision 9 v2 (compute):** §8.4 + §9.4 wall-clock estimates within budget
- **Decision 10 v2 (open-source):** §2.2 all listed packages open-licensed

---

## §14 Provenance and Appendix

### 14.1 Provenance

L4.1 written by Claude (CSO, 2026-05-11) per Phase B Plan v2 sequencing. Consumes all 7 Layers 2-3 specs. After L4.1 + L4.2 + L4.3 LOCK + Phase 8 audit, Layer 5 code starts.

### 14.2 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ L4.1 is "research-before-code" operational instantiation — all 7 Layer 2-3 specs read before sequencing
- **P15 (honest science):** ✅ §11.6 honest calendar; §8.7 soft termination explicit
- **P16 (preserve past work):** ✅ all Layer 2-3 commitments preserved in stage handoff criteria
- **Charter §5.3:** ✅ §11 pass criteria explicit
- **Charter v1.2 §1.7 phase discipline:** ✅ Phase F items noted but not specified

### 14.3 Drift Catalog This Session

New drift instances introduced: 0.

### 14.4 Layer 4 Phase B Status

| Artifact | Status | Words |
|---|---|---|
| **L4.1 Implementation Order** | **PROPOSED** | (this artifact) |
| L4.2 Testing | pending | target 3-4K |
| L4.3 Failure Modes | pending | target 3-4K |

### 14.5 8-Stage Sequence Quick Reference

| Stage | Name | Specs Consumed | Deliverable | Effort Est. |
|---|---|---|---|---|
| 1 | Foundation | — | Repo + env + CI + Explorer onboarding + MLflow | 2-4 days |
| 2 | Data Layer | — | Dataset loaders + cache | 1-2 weeks |
| 3 | Substrate Adapters | L2.1 | 4 substrate families | 2-3 weeks |
| 4 | L7 Head | L2.2 | 6-slot L7 + N=5 ensemble | 3-4 weeks |
| 5 | OOD + Interpretability (parallel) | L2.3 + L2.4 | OODStack + InterpretabilityStack | 5-7 weeks |
| 6 | Validation Pipeline | L3.1 + L3.2 | CascadeRunner + 7 V-evaluators + 56 criterion checkers | 3-4 weeks |
| 7 | V0-V5 Empirical | All Layer 2-3 | Trained checkpoints + CascadeReports per V-level per substrate | 8-14 weeks |
| 8 | V6 Cross-Disease | L3.3 | 4-paradigm matrix; universality verdict | 4-6 weeks |
| **Total** | | | Phase B Layer 5 COMPLETE | **6-9 months** |

### 14.6 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L4_1_Implementation_Order_Specification_2026-05-11.md`
- Code root (future): `~/INTERCEPTA/code/intercepta/`
- Tests root (future): `~/INTERCEPTA/code/tests/`
- SLURM scripts (future): `~/INTERCEPTA/code/scripts/`
- Scratch (future): `/scratch/akula.pra/INTERCEPTA/`
- MLflow backend (future): `/scratch/akula.pra/INTERCEPTA/mlflow/`

---

— L4.1 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l4.1-locked` tag.
— Next: L4.2 Testing Specification.
