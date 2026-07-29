# INTERCEPTA Phase B Layer 3 — Artifact 3.1
## V0-V6 Validation Cascade Pipeline Specification

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** L2.1 (LOCKED), L2.2/L2.3/L2.4 (PROPOSED) — Layer 2 of Phase B COMPLETE 2026-05-11
**Parent decision:** Decision 6 v2 Q6 Validation Cascade (LOCKED)
**Co-bound decisions:** Decision 1 v2, 4 v2, 5 v2, 7 v2, 8 v2, 9 v2, 10 v2
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Target length per Phase B Plan v2:** 5-7K words
**Filename:** INTERCEPTA_FV_L3_1_V0_V6_Validation_Cascade_Pipeline_Specification_2026-05-11.md

---

## §0 Identification and Scope

### 0.1 What This Document Is

L3.1 is the V0-V6 Validation Cascade Pipeline Specification. It is the first artifact of Phase B Layer 3 work, beginning the validation/evaluation phase that follows Layer 2's prediction stack. L3.1 specifies the evaluation harness — data flow, sample-size requirements, computational orchestration, pass-criteria-gating logic — that turns Layer 2's architectural specs into testable empirical claims at each of the seven validation levels V0-V6.

L3.1 does NOT enumerate the 56 specific pass criteria — that is L3.2. L3.1 does NOT specify the cross-disease V6 grid in detail — that is L3.3. L3.1 specifies the pipeline infrastructure that L3.2 and L3.3 will run inside.

### 0.2 What This Document Is Not

L3.1 is NOT a specific empirical evaluation (Layer 5), NOT a statistical methods textbook, NOT a dataset acquisition plan (Layer 4), NOT a clinical trial protocol (Phase F for prospective trials), NOT a regulatory submission package (Phase F).

### 0.3 Phase B Plan v2 Compliance

- Layer 2 (L2.1 LOCKED + L2.2/L2.3/L2.4 PROPOSED) → COMPLETE 2026-05-11
- Artifact 1 of Layer 3 (this document, L3.1) → PROPOSED
- Artifact 2 of Layer 3 (L3.2 56 Pass Criteria) → pending
- Artifact 3 of Layer 3 (L3.3 Cross-Disease V6 Grid) → pending

### 0.4 Anchor Re-Read Compliance

Per Phase B Plan v2 anchor re-read trigger, L3.1's anchor re-read trigger is SATISFIED. Q6 anchor papers re-read in primary-source form during the 2026-05-11 corpus-read audit:

| Anchor | L3.1 commitment grounded |
|---|---|
| Partin 2026 IMPROVE | V1 two-metric framework; GDSC/CCLE/CTRP standardized splits; baseline comparators |
| Tang 2022 | V3 AUROC ≥ 0.77 floor; V4 RMSE ≤ 0.11 TNBC floor |
| Kim 2020 PDXGEM | V4 BINDING — 24.5% biomarker concordance; concordant vs non-concordant separately |
| Yang 2013 GDSC | V0/V1 cell-line dataset |
| Ghandi 2019 CCLE | V1 cross-platform partner |
| Li-Shen 2024 DiSyn | V5 BINDING — ECE ≤ 0.05 |

Additional: Theunissen 2025 (V6 OOD caveat), Decision 8 v2 paradigms (V6 grid). No anchor re-read drift detected.

### 0.5 Document Conventions

- **BINDING** — cannot be modified without Decision Record amendment + CEO+CSO co-sign.
- **DEFAULT** — Layer-5-revisitable per §9.5.
- Pass criterion thresholds (V3 AUROC ≥ 0.77, V4 RMSE ≤ 0.11 TNBC, V6 AUROC ≥ 0.65 ≥2 areas) are BINDING per Decision 6 v2 + Decision 8 v2.

---

## §1 The V0-V6 Cascade Architecture Overview

### 1.1 Why a Cascade

Per Decision 6 v2: drug response validation cannot collapse to a single benchmark because the translation gap is real and quantified at multiple levels:
- Cell-line training → primary tumor: Tang 2022 demonstrates ~0.13 AUROC gap
- PDX → patient: Kim 2020 demonstrates only 24.5% biomarker concordance
- Within-disease → cross-disease: never demonstrated at scale; INTERCEPTA novelty

Each V-level isolates a specific translation transition. A method passing V0 but failing V3 has overfit cell-line context. The cascade architecturally requires each level to be passed in sequence.

### 1.2 The Cascade Data Flow

```
Layer 2 Stack (L7 + OOD + Interpretability)
    |
    v
V0 — Within-dataset CV (GDSC 5-fold)
    pass: significant signal > 0
    | PASS
    v
V1 — Cross-dataset (GDSC↔CCLE↔CTRP)
    pass: AUROC ≥ 0.65 + match best IMPROVE baseline
    | PASS
    v
V2 — Cell→Organoid (HCMI/Sanger)
    pass: AUROC ≥ 0.65 (INTERCEPTA novelty)
    | PASS
    v
V3 — Cell→Tumor (TCGA)
    pass: AUROC ≥ 0.77 (Tang 2022 BINDING)
    | PASS
    v
V4 — Cell→PDX (NCI PDXNet)
    pass: RMSE ≤ 0.11 TNBC + concordant/non-concordant separately
    | PASS
    v
V5 — PDX→Patient (Retrospective clinical)
    pass: ECE ≤ 0.05 + AUROC ≥ 0.65 + statistical power
    | PASS
    v
V6 — Cross-disease (Held-out disease scRNA)
    pass: AUROC ≥ 0.65 on ≥2 therapeutic areas BINDING
          + ≥70% failures = epistemic BINDING
```

### 1.3 The CascadeRunner Module Interface

```python
class CascadeRunner:
    """V0-V6 validation cascade orchestration."""

    def __init__(
        self,
        l7_ensemble: L7Ensemble,
        ood_stack: OODStack,
        interpretability_stack: InterpretabilityStack,
        substrate_name: str,
        config: CascadeConfig,
    ):
        self.l7 = l7_ensemble
        self.ood = ood_stack
        self.interp = interpretability_stack
        self.substrate = substrate_name
        self.config = config
        self.evaluators = {
            "V0": V0WithinDatasetEvaluator(config),
            "V1": V1CrossDatasetEvaluator(config),
            "V2": V2CellLineToOrganoidEvaluator(config),
            "V3": V3CellLineToTumorEvaluator(config),
            "V4": V4CellLineToPDXEvaluator(config),
            "V5": V5PDXToPatientEvaluator(config),
            "V6": V6CrossDiseaseEvaluator(config),
        }

    def run_cascade(self, start_at="V0", stop_on_first_failure=True) -> CascadeReport:
        levels = ["V0", "V1", "V2", "V3", "V4", "V5", "V6"]
        start_idx = levels.index(start_at)
        per_level_results = {}
        for level in levels[start_idx:]:
            result = self.evaluators[level].evaluate(
                l7=self.l7, ood=self.ood, interp=self.interp,
                substrate=self.substrate,
            )
            per_level_results[level] = result
            if stop_on_first_failure and not result.passed and result.termination == "hard":
                break
        return self._compose_cascade_report(per_level_results)
```

### 1.4 The CascadeReport Schema (BINDING — Decision 6 v2)

```python
@dataclass
class CascadeReport:
    substrate_name: str
    per_level_results: Dict[str, VLevelResult]
    cross_level_reporting: CrossLevelReport
        # mandatory per Decision 6 v2:
        # - V0→V1 generalization gap (IMPROVE relative performance)
        # - V3 substrate-vs-pathway-baseline comparison (Souza-Mehta bar)
        # - V4 concordant/non-concordant biomarker space separately
        # - V5 statistical power per evaluation
        # - V6 paradigm matrix (Decision 8 v2 4-paradigm)
        # - V6 OOD attribution rate (Decision 5 v2 Pass 4)
    termination_state: str  # "passed_all" | "soft_terminated" | "hard_terminated"
    soft_termination_level: Optional[str]
    hard_termination_level: Optional[str]


@dataclass
class VLevelResult:
    level: str
    passed: bool
    primary_metric_value: float
    primary_metric_name: str
    primary_metric_ci: Tuple[float, float]
    pass_threshold: float
    sample_size: int
    statistical_power: Optional[float]
    failure_modes_detected: List[str]
    termination: str
    notes: List[str]
```

### 1.5 The CascadeConfig Hyperparameter Bundle

```python
@dataclass
class CascadeConfig:
    seed: int = 42
    n_bootstrap: int = 1000
    confidence: float = 0.95

    # V0
    v0_n_folds: int = 5
    v0_dataset: str = "gdsc"
    v0_min_pairs: int = 1000

    # V1
    v1_datasets: List[str] = field(default_factory=lambda: ["gdsc", "ccle", "ctrp"])
    v1_use_improve_workflow: bool = True
    v1_baselines: List[str] = field(default_factory=lambda: ["deepcdr", "paccmann", "naive"])

    # V2
    v2_datasets: List[str] = field(default_factory=lambda: ["hcmi", "sanger_organoid"])
    v2_min_samples_per_cancer: int = 50

    # V3
    v3_dataset: str = "tcga"
    v3_threshold_auroc: float = 0.77  # BINDING
    v3_souza_mehta_baseline_required: bool = True

    # V4
    v4_dataset: str = "nci_pdxnet"
    v4_tnbc_threshold_rmse: float = 0.11  # BINDING
    v4_broad_threshold_rmse: float = 0.20
    v4_kim_concordance: float = 0.245
    v4_report_concordant_separately: bool = True

    # V5
    v5_min_patients_per_drug_cancer: int = 30
    v5_threshold_ece: float = 0.05  # BINDING
    v5_threshold_auroc: float = 0.65
    v5_report_statistical_power: bool = True

    # V6
    v6_min_diseases: int = 3
    v6_min_therapeutic_areas: int = 2  # BINDING
    v6_threshold_auroc: float = 0.65   # BINDING
    v6_epistemic_attribution_threshold: float = 0.70  # BINDING

    # Compute
    device: str = "cuda:0"
    use_slurm_array: bool = True
    cache_predictions: bool = True
    cache_path_template: str = (
        "/scratch/akula.pra/INTERCEPTA/validation/{substrate}/{level}/"
    )
```

### 1.6 What the Architecture Does Not Specify

- Specific dataset versions and URLs (Layer 4)
- Specific scRNA-seq preprocessing (Decision 2 v2 + Layer 4)
- Specific clinical retrospective cohorts (Layer 5)
- Specific held-out diseases for V6 (L3.3)
- Specific 56 pass criteria details (L3.2)

---

## §2 V-Level Evaluator Pattern

### 2.1 The Evaluator Contract

```python
class VLevelEvaluator(ABC):
    LEVEL: str = "abstract"

    def __init__(self, config: CascadeConfig):
        self.config = config

    @abstractmethod
    def evaluate(self, l7, ood, interp, substrate) -> VLevelResult:
        raise NotImplementedError

    def _bootstrap_ci(self, predictions, targets, metric_fn, n_bootstrap=1000):
        n = len(predictions)
        bootstrap_vals = []
        for _ in range(n_bootstrap):
            idx = torch.randint(0, n, (n,))
            val = metric_fn(predictions[idx], targets[idx])
            bootstrap_vals.append(val.item())
        bootstrap_vals = sorted(bootstrap_vals)
        lower = bootstrap_vals[int(n_bootstrap * 0.025)]
        upper = bootstrap_vals[int(n_bootstrap * 0.975)]
        point_est = metric_fn(predictions, targets).item()
        return point_est, (lower, upper)
```

### 2.2 The Termination Logic

```python
class TerminationLogic:
    """Decision 6 v2 hard / soft / pass-with-reservations logic."""

    @staticmethod
    def classify(level, result, config) -> str:
        # Hard termination per Decision 6 v2:
        if level == "V0" and not result["significant_above_zero"]:
            return "hard"
        if level == "V3" and result["auroc"] < 0.65:
            return "hard"
        if level == "V5" and result["ece"] > 0.15:
            return "hard"
        if level == "V6" and max(result["paradigm_aurocs"]) < 0.55:
            return "hard"
        if TerminationLogic._all_pass_criteria_met(level, result, config):
            return "pass"
        if TerminationLogic._meets_minimum_but_not_baseline(level, result, config):
            return "pass_with_reservations"
        return "soft"
```

### 2.3 Cross-Level Caching Pattern

```
/scratch/akula.pra/INTERCEPTA/validation/
├── {substrate}/
│   ├── v0/predictions.h5
│   ├── v0/targets.h5
│   ├── v0/ood_output.h5
│   ├── v0/result.json
│   ├── v1/...
│   ├── ...
│   └── v6/{disease_id}/...
```

Essential for Souza-Mehta methodological bar: 4 substrates × 7 V-levels × N=5 ensembles is expensive; caching makes matched-pair comparison tractable.

---

## §3 V0 — Within-Dataset Cross-Validation

V0 evaluator implements 5-fold CV on GDSC. Min sample size 1000 pairs per Decision 6 v2. Pass criterion: AUROC bootstrap 95% CI lower bound above 0.5. Hard-terminate if model cannot learn (F0). Cache predictions for downstream V-levels.

Compute envelope: standard GPU, ~12-24 hrs per substrate per V0 evaluation. 4 substrates Souza-Mehta matched = 12-20 GPU-days for V0 substrate ablation.

Honest limitations: V0 says nothing about generalization. 5-fold random splits may leak cell-line family information. V0 pass is necessary but not sufficient for any clinical claim.

---

## §4 V1 — Cross-Dataset (IMPROVE Methodology)

V1 evaluator implements IMPROVE workflow: train on dataset A, evaluate on B; rotate across GDSC/CCLE/CTRP. Per Partin 2026 + Decision 6 v2 BINDING: V1 must report BOTH absolute AUROC AND relative performance against IMPROVE baselines.

```python
def _compute_improve_relative(self, preds, targets, baselines, train_ds, test_ds):
    intercepta_auroc = roc_auc_score(targets, preds.prediction)
    baseline_aurocs = [
        load_improve_published_auroc(b, train_ds, test_ds)
        for b in baselines
    ]
    best_baseline = max(baseline_aurocs)
    return intercepta_auroc - best_baseline
```

The V0→V1 gap is the field's standard measure of dataset-specific overfitting. Per Decision 6 v2 BINDING: INTERCEPTA must acknowledge any V0-V1 gap honestly rather than report only the higher V0 number. If V0=0.90 and V1=0.65, the 0.25 gap is reported even if both pass.

Compute envelope: IMPROVE workflow on standard GPU; ~1-2 GPU-days per cross-pair × 6 pairs = 6-12 GPU-days per substrate; 4 substrates Souza-Mehta matched = 24-48 GPU-days.

Honest limitations: cross-dataset transfer within cell-line space is easier than cross-modality transfer. IMPROVE baselines have their own idiosyncrasies. Three-dataset coverage may not capture all real-world variation.

---

## §5 V2 — Cell Line → Organoid (INTERCEPTA Novelty)

V2 evaluator trains on cell-line data, evaluates on organoid datasets (HCMI, Sanger). Min 50 samples per cancer type. Pass: AUROC ≥ 0.65.

V2 is the ONLY level without an established empirical anchor. Per Decision 6 v2: INTERCEPTA may be defining the V2 standard rather than meeting an existing one. Honestly stated in VLevelResult notes.

The AUROC ≥ 0.65 threshold is INTERCEPTA's commitment based on continuity with V1 (cross-dataset) and being substantially below V3 (translational, Tang 2022 anchor 0.77). The gap reflects increasing translation difficulty.

Compute envelope: organoid scRNA-seq requires medium-large GPU memory. ~1-2 GPU-days per organoid dataset. HCMI + Sanger panels: ~3-5 GPU-days per substrate.

Honest limitations: no published baseline to compare against (INTERCEPTA defines the standard). Organoid selection bias (F3): organoid generation selects for specific cell types. 3D context affects gene expression beyond scRNA-seq capture (pH, oxygen, mechanical cues).

---

## §6 V3 — Cell Line → Tumor (TCGA, Tang 2022 BINDING)

### 6.1 V3 Evaluator Implementation

V3 evaluator trains on cell-line data, evaluates on TCGA gene expression with documented clinical outcomes. Pass criterion: AUROC ≥ 0.77 (Tang 2022 BINDING per Decision 6 v2).

```python
class V3CellLineToTumorEvaluator(VLevelEvaluator):
    LEVEL = "V3"

    def evaluate(self, l7, ood, interp, substrate) -> VLevelResult:
        cell_line_data = load_dataset(self.config.v0_dataset)
        tcga_data = load_dataset("tcga")
        self._train_l7(l7, cell_line_data)
        preds = l7(tcga_data.adata, tcga_data.drug_smiles, tcga_data.covariates)
        targets = tcga_data.targets
        auroc, ci = self._bootstrap_ci(
            preds.prediction, targets, roc_auc_score_torch,
            n_bootstrap=self.config.n_bootstrap,
        )
        # CRITICAL per Decision 6 v2 + Souza-Mehta:
        # Train pathway-feature baseline at >=25% hyperparameter budget
        pathway_baseline_auroc = self._train_eval_pathway_baseline(
            cell_line_data, tcga_data, budget_fraction=0.25,
        )
        passed = auroc >= self.config.v3_threshold_auroc
        souza_mehta_consistent = auroc >= pathway_baseline_auroc - 0.02
        return VLevelResult(
            level="V3", passed=passed,
            primary_metric_value=auroc, primary_metric_name="AUROC_tumor",
            primary_metric_ci=ci, pass_threshold=self.config.v3_threshold_auroc,
            sample_size=len(tcga_data),
            failure_modes_detected=self._diagnose_v3_failures(auroc, pathway_baseline_auroc),
            termination=TerminationLogic.classify("V3", {"auroc": auroc}, self.config),
            notes=[
                f"Tang 2022 floor: {self.config.v3_threshold_auroc}",
                f"Pathway baseline AUROC: {pathway_baseline_auroc:.3f}",
                f"Souza-Mehta consistent: {souza_mehta_consistent}",
            ],
        )
```

### 6.2 V3 Souza-Mehta Methodological Requirement (BINDING)

Per Decision 6 v2 + Decision 8 v2 Commitment 5: V3 must include a pathway-feature baseline at ≥25% of INTERCEPTA hyperparameter budget. If INTERCEPTA V3 is below or close to the pathway baseline, FM/multi-paradigm complexity is not earning its cost.

This is the operational instantiation of Souza-Mehta parameter-free-matches-FM finding at the translational level. L3.1 enforces this in evaluator code: v3_souza_mehta_baseline_required = True is the default; cannot be disabled without amending Decision 6 v2 or 8 v2.

### 6.3 V3 Hard Termination Threshold

Per Decision 6 v2: V3 AUROC < 0.65 triggers hard termination. This is substantially below Tang 2022 0.77 floor — means the architecture is not translating cell-line learning to tumor space at all.

Soft termination: 0.65 ≤ AUROC < 0.77 triggers architecture revision but not termination. The cascade continues to V4-V6 to gather full evidence; INTERCEPTA reports V3 shortfall honestly.

### 6.4 V3 Compute Envelope

TCGA bulk data processable on CPU clusters or single GPU. ~1-2 GPU-days per substrate for V3 evaluation. Pathway baseline training: ~1 GPU-day per substrate. Total V3: ~3-5 GPU-days per substrate × 4 substrates = 12-20 GPU-days.

### 6.5 V3 Honest Limitations

- TCGA samples are predominantly treatment-naive primary tumors.
- TCGA clinical response annotations are sometimes ambiguous.
- Cell-line training inherently lacks tumor microenvironment (F3): stromal, immune, vascular components absent. V3 partially exposes this gap; V6 cross-disease fully tests universality.

---

## §7 V4 — Cell Line → PDX (Tang 2022 + Kim 2020 BINDING)

### 7.1 V4 Evaluator Implementation

V4 evaluator applies cell-line-trained model to NCI PDXNet. Dual pass criteria: RMSE ≤ 0.11 on TNBC (Tang 2022 BINDING); RMSE ≤ 0.20 on broader PDX panel. Per Decision 6 v2 BINDING: concordant vs non-concordant biomarker space reported separately (Kim 2020 24.5% concordance).

```python
class V4CellLineToPDXEvaluator(VLevelEvaluator):
    LEVEL = "V4"

    def evaluate(self, l7, ood, interp, substrate) -> VLevelResult:
        cell_line_data = load_dataset(self.config.v0_dataset)
        pdx_data = load_dataset(self.config.v4_dataset)
        self._train_l7(l7, cell_line_data)
        preds = l7(pdx_data.adata, pdx_data.drug_smiles, pdx_data.covariates)
        # CRITICAL per Kim 2020: separate concordant vs non-concordant
        tnbc_mask = (pdx_data.cancer_type == "TNBC")
        broad_mask = ~tnbc_mask
        concordant_mask, non_concordant_mask = self._classify_biomarker_concordance(
            pdx_data, kim_concordance=self.config.v4_kim_concordance,
        )
        tnbc_rmse = mse(preds.prediction[tnbc_mask], pdx_data.targets[tnbc_mask]).sqrt()
        broad_rmse = mse(preds.prediction[broad_mask], pdx_data.targets[broad_mask]).sqrt()
        concordant_rmse = mse(preds.prediction[concordant_mask], pdx_data.targets[concordant_mask]).sqrt()
        non_concordant_rmse = mse(preds.prediction[non_concordant_mask], pdx_data.targets[non_concordant_mask]).sqrt()
        # OOD attribution check: are non-concordant predictions flagged as epistemic OOD?
        ood_output = ood(pdx_data.adata, pdx_data.drug_smiles, pdx_data.covariates)
        non_concordant_flagged = (
            ood_output.epistemic_uncertainty[non_concordant_mask] >
            self.config.v6_epistemic_attribution_threshold
        ).float().mean()
        passed = (
            tnbc_rmse <= self.config.v4_tnbc_threshold_rmse and
            broad_rmse <= self.config.v4_broad_threshold_rmse
        )
        return VLevelResult(
            level="V4", passed=passed,
            primary_metric_value=tnbc_rmse.item(),
            primary_metric_name="RMSE_TNBC",
            primary_metric_ci=self._bootstrap_rmse_ci(...),
            pass_threshold=self.config.v4_tnbc_threshold_rmse,
            sample_size=len(pdx_data),
            failure_modes_detected=self._diagnose_v4_failures(...),
            termination=TerminationLogic.classify("V4", {...}, self.config),
            notes=[
                f"Tang 2022 TNBC RMSE floor: {self.config.v4_tnbc_threshold_rmse}",
                f"Concordant RMSE: {concordant_rmse:.3f}",
                f"Non-concordant RMSE: {non_concordant_rmse:.3f}",
                f"Non-concordant flagged as epistemic OOD: {non_concordant_flagged:.1%}",
                f"Kim 2020 biomarker concordance: {self.config.v4_kim_concordance:.1%}",
            ],
        )
```

### 7.2 V4 Concordant/Non-Concordant Separation (BINDING)

Per Kim 2020: only 24.5% of biomarkers translate from PDX to primary tumor. The 75% non-concordant space is fundamentally a different statistical regime.

L3.1 enforces separate reporting:
- Concordant subset: where PDX biomarkers track primary tumor behavior — predictions expected to generalize
- Non-concordant subset: where PDX biomarkers DO NOT track primary tumor — predictions inherently unreliable; L7 + L2.3 OOD stack should flag these as epistemic OOD

This is the operational integration of Decision 5 v2 into V4. If L2.3 does not flag non-concordant predictions as epistemic, that is a Decision 5 v2 Pass 4 failure surfacing at V4.

### 7.3 V4 Compute Envelope

PDX scRNA-seq standard. ~1-2 GPU-days per substrate. Total V4: ~5-8 GPU-days for 4-substrate ablation.

### 7.4 V4 Honest Limitations

- NCI PDXNet engraftment selects for specific tumor subtypes (F4).
- Non-concordant biomarker space is real. V4 results there are reported but cannot be the basis for predictions in deployment.
- Tang 2022 TNBC floor established for a specific PDX panel and may not generalize to all TNBC PDXs.

---

## §8 V5 — PDX → Patient (Retrospective Clinical, ECE BINDING)

### 8.1 V5 Evaluator Implementation

V5 evaluator applies PDX-trained or cell-line-trained model to retrospective clinical drug response data. Pass: ECE ≤ 0.05 (Decision 5 v2 + Li-Shen 2024 BINDING) AND AUROC ≥ 0.65 AND statistical power reported.

```python
class V5PDXToPatientEvaluator(VLevelEvaluator):
    LEVEL = "V5"

    def evaluate(self, l7, ood, interp, substrate) -> VLevelResult:
        training_data = self._load_training_for_v5()
        clinical_cohort = load_dataset("retrospective_clinical")
        self._train_l7(l7, training_data)
        per_drug_cancer_results = {}
        for (drug, cancer_type) in clinical_cohort.unique_drug_cancer_pairs():
            subset = clinical_cohort.filter(drug=drug, cancer_type=cancer_type)
            if len(subset) < self.config.v5_min_patients_per_drug_cancer:
                per_drug_cancer_results[(drug, cancer_type)] = {
                    "n": len(subset), "below_min": True,
                    "statistical_power": "insufficient",
                }
                continue
            preds = l7(subset.adata, [drug] * len(subset), subset.covariates)
            auroc, ci = self._bootstrap_ci(preds.prediction, subset.targets, roc_auc_score_torch)
            ece = self._compute_ece(preds.prediction, subset.targets)
            power = self._compute_statistical_power(
                n=len(subset), effect_size=auroc - 0.5, alpha=0.05,
            )
            per_drug_cancer_results[(drug, cancer_type)] = {
                "n": len(subset), "auroc": auroc, "auroc_ci": ci,
                "ece": ece, "statistical_power": power,
            }
        adequate = {k: v for k, v in per_drug_cancer_results.items() if not v.get("below_min")}
        if not adequate:
            return self._insufficient_data_result(per_drug_cancer_results)
        mean_auroc = np.mean([v["auroc"] for v in adequate.values()])
        mean_ece = np.mean([v["ece"] for v in adequate.values()])
        passed = (mean_ece <= self.config.v5_threshold_ece and
                  mean_auroc >= self.config.v5_threshold_auroc)
        return VLevelResult(
            level="V5", passed=passed,
            primary_metric_value=mean_ece, primary_metric_name="ECE",
            primary_metric_ci=self._bootstrap_ece_ci(...),
            pass_threshold=self.config.v5_threshold_ece,
            sample_size=sum(v["n"] for v in adequate.values()),
            statistical_power=np.mean([v["statistical_power"] for v in adequate.values()]),
            failure_modes_detected=self._diagnose_v5_failures(per_drug_cancer_results),
            termination=TerminationLogic.classify("V5", {"ece": mean_ece}, self.config),
            notes=[
                f"ECE floor: {self.config.v5_threshold_ece}",
                f"AUROC: {mean_auroc:.3f}",
                f"Cohorts below min n: "
                f"{sum(1 for v in per_drug_cancer_results.values() if v.get('below_min'))}",
            ],
        )
```

### 8.2 V5 Statistical Power Mandatory Reporting (BINDING)

Retrospective clinical data has small sample sizes (often n < 100 per drug-cancer combination). Per Decision 6 v2 BINDING: V5 must report statistical power alongside performance metrics. A V5 result with n=20 cannot be the basis for binding pass/fail.

L3.1 enforces: cohorts below v5_min_patients_per_drug_cancer (default 30) reported separately with insufficient-power tags; aggregate pass/fail uses only adequate-power cohorts.

### 8.3 V5 ECE Computation

```python
def _compute_ece(self, predictions, targets, n_bins=10):
    bin_boundaries = torch.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        in_bin = ((predictions >= bin_boundaries[i]) &
                  (predictions < bin_boundaries[i + 1]))
        n_in_bin = in_bin.sum()
        if n_in_bin > 0:
            bin_acc = targets[in_bin].float().mean()
            bin_conf = predictions[in_bin].mean()
            ece += (n_in_bin / len(predictions)) * (bin_acc - bin_conf).abs()
    return ece.item()
```

### 8.4 V5 Compute Envelope

Standard compute; bottleneck is data access. ~1 GPU-day per substrate. Total V5: ~4-6 GPU-days.

### 8.5 V5 Honest Limitations

- Clinical retrospective cohorts have selection effects.
- Small per-drug-cancer sample sizes limit statistical power.
- Cross-cohort generalization within V5 is itself uncertain.
- DiSyn (Li-Shen 2024) is CC BY-NC-ND license; INTERCEPTA uses architectural ideas, not codebase per Decision 10 v2.

---

## §9 V6 — Cross-Disease (Universality Test, BINDING)

### 9.1 V6 Evaluator Implementation

V6 evaluator implements the Charter §1.1 universality test. Pass: AUROC ≥ 0.65 on held-out disease spanning ≥2 therapeutic areas (Decision 8 v2 BINDING) AND ≥70% of failed predictions correctly attributed to epistemic uncertainty (Decision 5 v2 Pass 4 BINDING).

V6 evaluates across all 4 Decision 8 v2 paradigms (A general FM, B disease-area FM, C patient-aggregation, D parameter-free). Held-out disease grid specified by L3.3.

For each (paradigm × disease), train paradigm-specific L7 + compute AUROC + run OOD stack + compute epistemic-fraction-of-failures.

Pass: at least one paradigm achieves ≥0.65 AUROC on ≥2 therapeutic areas AND overall epistemic-attribution-of-failures ≥0.70.

### 9.2 V6 4-Paradigm Matrix (Decision 8 v2 BINDING)

V6 reports performance across all 4 Decision 8 v2 paradigms:
- A: general FM (scFoundation/UCE/scGPT/Geneformer)
- B: disease-area-specific FM (EVA-60M for I&I)
- C: patient-level aggregation (PaSCient on top of A/B/D substrate)
- D: parameter-free baseline (scTOP)

4-paradigm reporting is BINDING per Decision 8 v2 Commitment 5 (Souza-Mehta methodological bar).

### 9.3 V6 OOD Attribution (Decision 5 v2 Pass 4 BINDING)

When V6 predictions fail, ≥70% must be correctly attributed to epistemic uncertainty by L2.3 OOD stack. Integration test of L2.3 with V6:
- V6 fails AND failures epistemic-flagged: architecture correctly knows it does not know
- V6 fails AND failures NOT epistemic-flagged: OOD stack not detecting cross-disease shift; major architecture issue

### 9.4 V6 Compute Envelope (LARGEST)

V6 is the largest of any V-level. Decision 8 v2 4-paradigm × held-out diseases = ~75-100 evaluation cells. Per cell: ~1-2 GPU-days. Total V6: ~100-200 GPU-days (~20-40 wall-clock days with SLURM array parallelization at 5× concurrent).

This is the dominant Phase B compute cost. Decision 9 v2 budget tight; AWS/GCP burst CEO-approved for ≤5% may be needed.

### 9.5 V6 Honest Limitations

- Cross-disease generalization is INTERCEPTA novel research contribution. The 0.65 threshold is a commitment, not an empirical anchor.
- Per Theunissen 2025: OOD methods detect severe shifts reliably; subtle shifts less reliably. V6 may include both kinds.
- Held-out disease selection (L3.3) is consequential.
- A V6 negative result (universality fails) is also valuable scientific contribution; INTERCEPTA reports either outcome honestly.

---

## §10 Pass Criteria for L3.1 LOCK

### 10.1 Architecture-Level Pass Criteria (BINDING)

- A1: CascadeRunner implements all 7 V-level evaluators per §3-§9.
- A2: TerminationLogic implements Decision 6 v2 hard/soft/pass-with-reservations.
- A3: Cross-level caching pattern implemented per §2.3.
- A4: V3 Souza-Mehta pathway baseline integration per §6.2.
- A5: V4 concordant/non-concordant biomarker separation per §7.2.
- A6: V5 statistical power reporting per §8.2.
- A7: V6 4-paradigm matrix per §9.2.
- A8: V6 OOD attribution check per §9.3 (Decision 5 v2 Pass 4 BINDING).

### 10.2 Cross-Decision Compatibility (BINDING)

- X1: L3.1 consumes L7Ensemble (L2.2), OODStack (L2.3), InterpretabilityStack (L2.4).
- X2: L3.1 cascades all 4 substrate families (Decision 1 v2).
- X3: V3 enforces Souza-Mehta ≥25% pathway baseline (Decision 8 v2 Commitment 5).
- X4: V4 honors Kim 2020 biomarker concordance separation (Decision 6 v2 BINDING).
- X5: V5 ECE ≤0.05 floor (Decision 5 v2 + Li-Shen 2024).
- X6: V6 Decision 8 v2 universality test BINDING.
- X7: All dependencies open-licensed (Decision 10 v2).

### 10.3 Documentation Pass Criteria

- D1: L3.1 referenced by L3.2 + L3.3.
- D2: L3.1 Layer 5 implementation matches L3.1 specification.
- D3: Drift catalog this session: 0 new instances.

### 10.4 CEO Sign-Off

L3.1 advances from PROPOSED to LOCKED when:
1. CEO reviews §1-§9 cascade architecture and §10 pass criteria
2. CEO confirms §10.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag phase-b-l3.1-locked pushed to origin

### 10.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | V0 CV folds | 5 | 10, lineage-stratified | Lineage-stratified reduces V0→V1 gap |
| J2 | V0/V1 default dataset | GDSC | CCLE, CTRP | Layer 5 ablation |
| J3 | V1 baselines | DeepCDR, PaccMann, naive | + more IMPROVE methods | IMPROVE expansion |
| J4 | V2 organoid datasets | HCMI + Sanger | + others | New panels available |
| J5 | V5 min patients per drug-cancer | 30 | 50, 20 | Statistical power analysis |
| J6 | V6 min therapeutic areas | 2 | 3 | Stricter universality claim |
| J7 | V6 hard termination threshold | 0.55 across paradigms | 0.50, 0.60 | Empirical V6 floor |
| J8 | Bootstrap iterations | 1000 | 500, 5000 | Speed vs CI precision |
| J9 | Cache invalidation policy | substrate change | + dataset version | If dataset versions drift |
| J10 | Termination on first failure | True | False | Whether to gather V4-V6 evidence after V3 fails |

### 10.6 Honest Limitations (per Charter §10 P15 BINDING)

- V0-V6 cascade is sequential; passing all 7 is hard. INTERCEPTA may legitimately fail at V3 or V5; cascade designed to surface this honestly.
- Cross-level caching couples Layer 2 architectural changes to cache invalidation. Cache key includes L2.x spec SHA prefix.
- Statistical power thresholds at V5 may be too lenient or too strict; revisitable.
- V6 grid selection (L3.3) can bias results — easy diseases pass, hard diseases fail. L3.3 must specify a balanced grid.

---

## §11 What L3.1 Does NOT Lock

- The 56 specific pass criteria (L3.2)
- The cross-disease V6 grid composition (L3.3)
- Specific dataset version pinning (Layer 4)
- Specific clinical retrospective cohort access agreements (Layer 5)
- The training loop within each evaluator (Layer 4)
- Logging / monitoring instrumentation (Layer 4)

---

## §12 Cross-Decision Implications

- Decision 1 v2 (Substrate): L3.1 cascades all 4 substrate families in matched-pair training. Souza-Mehta budget bar enforced at V3 explicitly.
- Decision 2 v2 (Harmonization): Cohort harmonization upstream; L3.1 inherits harmonized data.
- Decision 3 v2 (Bulk→Single): chemCPA bridge in L2.2 Slot 2-3; L3.1 evaluates at V3-V4.
- Decision 4 v2 (L7): L3.1 consumes L7Ensemble at every V-level.
- Decision 5 v2 (OOD): L3.1 V4 + V6 integrate OOD verdict (BINDING).
- Decision 6 v2 (Validation): L3.1 IS the operational instantiation.
- Decision 7 v2 (Interpretability): Pass 7 cross-disease interpretability transfer tested at V6.
- Decision 8 v2 (Universality): V6 4-paradigm matrix BINDING.
- Decision 9 v2 (Compute): V6 dominates budget; SLURM array + cache mitigate.
- Decision 10 v2 (Open-Source): All tools open-licensed.

---

## §13 Provenance and Appendix

### 13.1 Provenance

L3.1 written by Claude (CSO, 2026-05-11) per Phase B Plan v2 sequencing. Predecessor artifacts L2.1 LOCKED + L2.2/L2.3/L2.4 PROPOSED in immediate context. Q6 anchor re-read trigger satisfied retroactively per Master Handoff v2.0 §3.5.

### 13.2 Discipline Check Per Charter v1.2 Principles

- P3 (research before code): ✅ Q6 anchor papers re-read.
- P15 (honest science): ✅ §10.6 honest limitations; V2 no-anchor caveat; V5 statistical power; V6 cross-disease universality is INTERCEPTA novelty.
- P16 (preserve past work): ✅ Decision 6 v2 + Q6 synthesis preserved.
- Charter §5.3: ✅ §10 pass criteria explicit.
- Charter v1.2 §1.7 phase discipline: ✅ No Phase F items specified.

### 13.3 Drift Catalog This Session

New drift instances introduced: 0.

### 13.4 Next Phase B Artifacts

- L3.2 56 Pass Criteria (5-6K words): 8 criteria × 7 V-levels with thresholds, sample sizes, statistical tests, abstain protocols.
- L3.3 Cross-Disease V6 Grid (4-5K words): N×(N-1) train-test scenarios; SLURM job array operational pattern per Q9 compute synthesis.

### 13.5 V-Level Quick Reference Table

| V | Source → Target | Pass Criterion | Anchor | Hard Term |
|---|---|---|---|---|
| V0 | GDSC CV | AUROC CI > 0.5 | N/A | model cannot learn |
| V1 | GDSC↔CCLE↔CTRP | ≥0.65 + match IMPROVE | Partin 2026 | — |
| V2 | Cell→Organoid | ≥0.65 | INTERCEPTA novelty | — |
| V3 | Cell→Tumor | ≥0.77 | Tang 2022 | <0.65 |
| V4 | Cell→PDX | ≤0.11 RMSE TNBC + concordant separately | Tang 2022 + Kim 2020 | — |
| V5 | PDX→Patient | ECE ≤0.05 + ≥0.65 + power | Li-Shen 2024 | ECE >0.15 |
| V6 | Cross-disease | ≥0.65 on ≥2 areas + ≥70% epistemic | INTERCEPTA novelty | max paradigm <0.55 |

### 13.6 Key File Paths

- This spec: ~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L3_1_V0_V6_Validation_Cascade_Pipeline_Specification_2026-05-11.md
- Decision 6 v2 (parent): ~/INTERCEPTA/docs/research/decisions/INTERCEPTA_FV_Decision_6_Q6_validation.md
- Validation cache (future): /scratch/akula.pra/INTERCEPTA/validation/
- IMPROVE workflow (external): https://github.com/JDACS4C-IMPROVE/IMPROVE

---

— L3.1 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and phase-b-l3.1-locked tag.
— After L3.1 LOCK, Phase B Plan v2 next artifact is L3.2 56 Pass Criteria.
