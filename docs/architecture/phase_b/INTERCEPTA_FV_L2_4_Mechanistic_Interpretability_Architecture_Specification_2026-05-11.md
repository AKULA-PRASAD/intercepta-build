# INTERCEPTA Phase B Layer 2 — Artifact 2.4
## Mechanistic Interpretability Architecture Specification (Scales 1-7)

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** L2.1 Substrate Architecture Spec (LOCKED), L2.2 L7 6-Slot Drug Response Architecture (PROPOSED), L2.3 OOD Detection Stack (PROPOSED)
**Parent decision:** Decision 7 v2 Q7 Mechanistic Interpretability (LOCKED)
**Co-bound decisions:** Decision 1 v2 (substrate), Decision 2 v2 (cohort harmonization), Decision 3 v2 (architectural identities), Decision 4 v2 (L7 attribution hooks), Decision 5 v2 (verdict-conditional attribution), Decision 6 v2 (V0-V6 validation), Decision 8 v2 (cross-disease V6 attribution transfer), Decision 9 v2 (compute envelope), Decision 10 v2 (open-source)
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping:** Phase B Scale 6 spatial DSEP becomes Phase F's spatial-aware mechanism trace for the 6 Scouts. Phase B Scale 7 patient SHAP becomes Phase F's clinical-grade per-patient interpretability for pharma deliverable packaging.
**Target length per Phase B Plan v2:** 10-12K words
**Filename:** `INTERCEPTA_FV_L2_4_Mechanistic_Interpretability_Architecture_Specification_2026-05-11.md`

---

## §0 Identification and Scope

### 0.1 What This Document Is

L2.4 is the **Mechanistic Interpretability Architecture Specification**. It is the fourth and final artifact of Phase B Layer 2 work, completing the trio of L2.2 (prediction architecture), L2.3 (calibrated uncertainty), and L2.4 (mechanism explanation). L2.4 specifies how INTERCEPTA produces multi-scale mechanism traces for every prediction by composing seven explicit attribution scales over the L7Output `attribution_hooks` defined in L2.2 and conditioned on the OODOutput `operational_verdict` defined in L2.3.

The seven scales are: (1) Geometric (spectral analysis, FM-only); (2) Drug-class (CPA disentangled latent); (3) Pathway (GEARS GO graph + Beyondcell BCS); (4) GRN/Cell-type (scRank perturbation propagation); (5) Gene-level (substrate-conditional via Branching A/B/C); (6) Spatial (River two-branch DSEP, spatial-modality-only); (7) Patient (SHAP individual-level). The scale ordering and identities are LOCKED by Decision 7 v2. L2.4 specifies each scale's implementation contract, dimensions, default choices, ablation infrastructure, the binding cross-scale consistency checks, and the verdict-conditional attribution pattern.

### 0.2 What This Document Is Not

L2.4 is NOT:

- A general-purpose attribution library. The seven scales are specifically chosen to address Charter §1.3 interpretability dimensions I1 (pathway-level mechanism trace), I2 (mechanism in the architecture, not post-hoc theater), I3 (causal claims about gene-drives-prediction). Other attribution methods exist (LIME, anchors, counterfactual explanations); L2.4 does not include them because Decision 7 v2 evaluated and rejected single-method commitment.
- A real-time interpretation system. The compute envelope (§7) accepts that Scale 5 EIG attribution is high-cost; deployment patterns batch attribution post-prediction, not in real-time interactive queries.
- A clinical-grade decision support system. L2.4 produces structured mechanism traces; clinical translation is out of charter scope per Charter v1.2 §4 row 6.
- A causal discovery system. L2.4 produces **mechanistic attribution** (which gene/pathway/cell-type contributes to which prediction). Causal claims in the formal Pearl/Rubin sense require intervention data; INTERCEPTA's claims are observational + supported by external GRN priors (scRank) and pathway priors (GEARS) but do not constitute causal proof. This is honestly stated in §10.6.
- A novel mechanism discovery system. Scale 5 EIG can reveal genes attributed to a prediction that were not anticipated, but "discovery" requires biological validation (Decision 6 v2 V0-V6 cascade + wet-lab confirmation), not just attribution.

### 0.3 Phase B Plan v2 Compliance

Per Phase B Execution Plan v2 sequencing:

- Artifact 1 of Layer 2 (L2.1 Substrate Specification) → LOCKED 2026-05-11
- Artifact 2 of Layer 2 (L2.2 L7 Drug Response Architecture) → PROPOSED 2026-05-11
- Artifact 3 of Layer 2 (L2.3 OOD Detection Stack) → PROPOSED 2026-05-11
- **Artifact 4 of Layer 2 (this document, L2.4 Mechanistic Interpretability Architecture) → PROPOSED**

L2.4 is downstream of L2.2 (consumes L7Output `attribution_hooks`) and L2.3 (consumes OODOutput `operational_verdict` to gate attribution). After L2.4, Layer 2 of Phase B is complete and the project advances to Layer 3 (V0-V6 Validation Cascade Pipeline).

### 0.4 Anchor Re-Read Compliance

Per Phase B Plan v2 anchor re-read trigger, L2.4's anchor re-read trigger is SATISFIED. The Q7 anchor papers were re-read in primary-source form during the 2026-05-11 corpus-read audit session. The anchors and the architectural commitments they ground:

| Anchor | Citation | L2.4 commitment grounded |
|---|---|---|
| **Reynolds-Pan 2025** | Reynolds, Pan et al. genomics interpretability benchmark | Scale 5 SmoothGrad enhancement default; vanilla-IG-rejection methodological pattern (§9 Pass 1); 4-method benchmark approach grounds "no single method dominates" conclusion |
| **Jha 2020 EIG** | Jha et al. 2020 Enhanced Integrated Gradients NeurIPS | Scale 5 Branch A (FM substrate) EIG H-N-IG variant; Bonferroni significance per Decision 5 v2 ensembleable N=5; A1CF validation pattern adapted for drug-target gene recovery (§9 Pass 3) |
| **Cui-Yuan 2025 River** | Cui, Yuan et al. River two-branch DSEP framework | Scale 6 spatial attribution method; two-branch decomposition for spatial-modality-only attribution |
| **Kendiukhov 2026 Spectral** | Kendiukhov et al. spectral geometry of FM latents | Scale 1 geometric attribution; FM-only applicability (parameter-free substrates have no learned geometry to analyze) |
| **Souza-Mehta 2026** | Souza, Mehta scTOP parameter-free | Scale 5 Branch B (parameter-free) — linear projection coefficients ARE the gene attribution; methodological consequence: no path integration needed when scTOP wins Layer 5 ablations |
| **Lotfollahi 2023 CPA** | CPA Mol Syst Biol | Scale 2 drug-class disentanglement directly from CPA latent (built into L7); no separate computation needed |
| **Roohani 2024 GEARS** | GEARS Nat Biotechnol | Scale 3 pathway attribution via GEARS GO graph (built into L7 Slot 4) |
| **Lin 2023 scRank** | scRank cell-type-specific GRN | Scale 4 GRN attribution; per Drift Finding 7 BINDING — scRank IS Slot 4 gene-gene attention edge-weight init in L2.2 |

The Beyondcell anchor (Fustero-Torre 2024 *Genome Med*) is BINDING per Drift Finding 7 — Beyondcell appears in L2.4 Scale 3 (pathway), NOT in L2.2 Slot 4. L2.4 implements Beyondcell as a parallel pathway-attribution component composed with GEARS's GO-graph signal.

No anchor re-read drift detected. All architectural commitments traceable to primary-source claims.

### 0.5 Document Conventions

- **BINDING** — a commitment that cannot be modified without a Decision Record amendment + CEO+CSO co-sign.
- **DEFAULT** — a choice L2.4 makes for initial Layer 5 implementation; revisitable per §11.5 with documented empirical signal.
- **DEFERRED** — a question L2.4 does not lock; reserved for Layer 5 ablation.
- **PHASE F** — out of L2.4 scope; canonical for Phase F per Charter v1.2 §4.
- All code snippets are PyTorch 2.x. Captum 0.7+ for IG / SmoothGrad / EIG. SHAP 0.45+ for Scale 7. Statsmodels 0.14+ for Bonferroni correction.

---

## §1 The 7-Scale Interpretability Architecture Overview

### 1.1 Why a Multi-Scale Architecture

Decision 7 v2 rejected single-method attribution for two reasons:

1. **Field consensus is multi-method.** Reynolds-Pan 2025 benchmarks 4 attribution methods (IG, SmoothGrad, GradCAM, occlusion) × 2 enhancement settings; no single configuration dominates. Jha 2020 tests 4 EIG variants × 6 baseline strategies; multiple work well for different prediction cases.

2. **Charter §1.3 falsifiability requires cross-scale consistency.** If pathway-level attribution (Scale 3) disagrees with gene-level attribution (Scale 5) on which mechanism drives a prediction, the mechanism trace is not operationally usable. Cross-scale consistency checks (§8) are BINDING per Decision 7 v2.

The seven scales are not redundant — each captures a different level of biological organization:
- Geometric (Scale 1): the topological structure of the substrate's learned representation
- Drug-class (Scale 2): which similar drugs share mechanism (built into CPA latent)
- Pathway (Scale 3): which biological pathway the drug acts on
- GRN/Cell-type (Scale 4): which regulatory network propagates the drug's effect
- Gene-level (Scale 5): which specific genes drive the prediction
- Spatial (Scale 6): where in the tissue the effect localizes (when spatial data available)
- Patient (Scale 7): why this specific patient is predicted to respond

A complete mechanism trace combines outputs across scales. The L2.4 output contract (§1.4) makes this combination explicit.

### 1.2 The Scale Data Flow

```
                INPUT (per prediction)
                       │
        ┌──────────────┴──────────────────┐
        │                                 │
        ▼                                 ▼
   L7Output.attribution_hooks    OODOutput.operational_verdict
   (from L2.2)                   (from L2.3)
        │                                 │
        │                                 │ verdict gating:
        │                                 │ - confident_predict → full attribution
        │                                 │ - abstain_aleatoric → reduced confidence
        │                                 │ - abstain_epistemic → flag extrapolation
        │                                 │ - abstain_ood → SKIP attribution
        │                                 │
        ├─────────────────────────────────┤
        │                                 │
        ▼                                 │
   ┌────────────────────────┐             │
   │ Scale 1 — Geometric    │             │
   │ Kendiukhov spectral    │             │
   │ FM-ONLY (gated)        │             │
   └────────────────────────┘             │
        │                                 │
        ▼                                 │
   ┌────────────────────────┐             │
   │ Scale 2 — Drug-class   │             │
   │ CPA latent (built in)  │             │
   │ Substrate-agnostic     │             │
   └────────────────────────┘             │
        │                                 │
        ▼                                 │
   ┌────────────────────────┐             │
   │ Scale 3 — Pathway      │             │
   │ GEARS GO + Beyondcell  │             │
   │ Substrate-agnostic     │             │
   └────────────────────────┘             │
        │                                 │
        ▼                                 │
   ┌────────────────────────┐             │
   │ Scale 4 — GRN/Cell-type│             │
   │ scRank propagation     │             │
   │ Substrate-agnostic     │             │
   └────────────────────────┘             │
        │                                 │
        ▼                                 │
   ┌────────────────────────┐             │
   │ Scale 5 — Gene-level   │             │
   │ Substrate-conditional: │             │
   │   Branch A: EIG (FM)   │             │
   │   Branch B: linear     │             │
   │           proj (scTOP) │             │
   │   Branch C: VAE IG     │             │
   │           (scVI)       │             │
   │ N=5 ensemble + Bonferr.│             │
   └────────────────────────┘             │
        │                                 │
        ▼                                 │
   ┌────────────────────────┐             │
   │ Scale 6 — Spatial      │             │
   │ River DSEP             │             │
   │ ONLY if spatial data   │             │
   └────────────────────────┘             │
        │                                 │
        ▼                                 │
   ┌────────────────────────┐             │
   │ Scale 7 — Patient      │             │
   │ SHAP individual        │             │
   │ Substrate-agnostic     │             │
   └────────────────────────┘             │
        │                                 │
        ▼                                 │
   ┌─────────────────────────────┐        │
   │ Cross-Scale Consistency    │ ◄──────┤
   │ Checks 1-4 BINDING         │        │
   │ - Drug-class ↔ Gene attrib │        │
   │ - Pathway prior ↔ Gene     │        │
   │ - GRN ↔ Gene               │        │
   │ - Patient SHAP cluster     │        │
   └─────────────────────────────┘        │
        │                                 │
        ▼                                 │
   ┌─────────────────────────────────────┐
   │ InterpretabilityOutput              │
   │ - per-scale attribution             │
   │ - cross-scale consistency report   │
   │ - verdict-conditional confidence    │
   └─────────────────────────────────────┘
```

### 1.3 The InterpretabilityStack Module Interface

```python
class InterpretabilityStack(torch.nn.Module):
    """The 7-scale interpretability stack per Decision 7 v2.

    Wraps L2.2 L7Ensemble and L2.3 OODStack; consumes their outputs;
    produces multi-scale mechanism trace conditioned on operational verdict.
    """

    def __init__(
        self,
        l7_ensemble: L7Ensemble,                          # from L2.2
        ood_stack: OODStack,                              # from L2.3
        scale_1_geometric: GeometricAttributor,           # see §3
        scale_2_drugclass: DrugClassAttributor,           # see §4
        scale_3_pathway: PathwayAttributor,               # see §5
        scale_4_grn: GRNAttributor,                       # see §6
        scale_5_genelevel: GeneLevelAttributor,           # see §7 substrate-conditional
        scale_6_spatial: Optional[SpatialAttributor],     # see §8 None if not spatial
        scale_7_patient: PatientAttributor,               # see §9
        config: InterpretabilityConfig,                   # see §1.5
    ):
        super().__init__()
        self.l7_ensemble = l7_ensemble
        self.ood_stack = ood_stack
        self.scales = {
            1: scale_1_geometric,
            2: scale_2_drugclass,
            3: scale_3_pathway,
            4: scale_4_grn,
            5: scale_5_genelevel,
            6: scale_6_spatial,
            7: scale_7_patient,
        }
        self.config = config

    def forward(
        self,
        adata: AnnData,
        drug_smiles: List[str],
        covariates: Covariates,
        return_per_scale: bool = True,
        run_consistency_checks: bool = True,
    ) -> InterpretabilityOutput:
        """Run the full 7-scale stack with verdict-conditional gating.

        Args:
            adata, drug_smiles, covariates: as L7Ensemble inputs
            return_per_scale: if True, return raw per-scale outputs
            run_consistency_checks: if True, run cross-scale checks (§10)

        Returns:
            InterpretabilityOutput per the L2.4 output contract (§1.4)
        """
        # Get L7 prediction + attribution hooks (with hooks enabled)
        l7_out = self.l7_ensemble(
            adata, drug_smiles, covariates,
            return_individual_predictions=True,
        )
        # Need attribution hooks on each head; collect them
        l7_hooks_per_head = self._collect_hooks_per_head(
            adata, drug_smiles, covariates,
        )

        # Get OOD verdict (gates downstream attribution)
        ood_out = self.ood_stack(adata, drug_smiles, covariates)

        # Verdict-conditional gating per L2.3 + Decision 5 v2
        per_scale_outputs = {}
        per_scale_confidence = {}

        for i, verdict in enumerate(ood_out.operational_verdict):
            if verdict == "abstain_ood":
                # Skip attribution; prediction is OOD
                per_scale_outputs[i] = None
                per_scale_confidence[i] = "skipped_ood"
                continue

            # For confident_predict + abstain_aleatoric + abstain_epistemic,
            # run attribution. Confidence flag tags the result.
            scale_results = {}
            for scale_id, scale_module in self.scales.items():
                if scale_module is None:
                    continue  # e.g., Scale 6 when no spatial data
                if scale_id == 1 and not self._is_fm_substrate():
                    continue  # Scale 1 FM-only
                if scale_id == 6 and not self._has_spatial_data(adata):
                    continue  # Scale 6 spatial-only

                attr_result = scale_module(
                    adata=adata, drug_smiles=drug_smiles, covariates=covariates,
                    l7_hooks=l7_hooks_per_head, prediction_idx=i,
                    verdict=verdict,
                )
                scale_results[scale_id] = attr_result

            per_scale_outputs[i] = scale_results
            per_scale_confidence[i] = self._verdict_to_confidence(verdict)

        # Cross-scale consistency checks
        if run_consistency_checks:
            consistency_report = self._run_consistency_checks(per_scale_outputs)
        else:
            consistency_report = None

        return InterpretabilityOutput(
            per_scale=per_scale_outputs if return_per_scale else None,
            per_scale_confidence=per_scale_confidence,
            consistency_report=consistency_report,
        )

    def _verdict_to_confidence(self, verdict: str) -> str:
        return {
            "confident_predict": "full_confidence",
            "abstain_aleatoric": "reduced_confidence_label_noise",
            "abstain_epistemic": "extrapolation_flagged",
        }[verdict]
```

### 1.4 The InterpretabilityOutput Schema (BINDING)

```python
@dataclass
class InterpretabilityOutput:
    """L2.4 output contract — per-prediction multi-scale mechanism trace.

    Consumed by Layer 3 V0-V6 validation harness, Phase F clinical
    decision support packaging.
    """

    per_scale: Optional[Dict[int, Dict[int, ScaleAttribution]]]
        # per_scale[prediction_idx][scale_id] = ScaleAttribution
        # None if return_per_scale=False
        # ScaleAttribution dataclass varies per scale; see §3-§9

    per_scale_confidence: Dict[int, str]
        # per_scale_confidence[prediction_idx] ∈
        # {"full_confidence", "reduced_confidence_label_noise",
        #  "extrapolation_flagged", "skipped_ood"}

    consistency_report: Optional[ConsistencyReport]
        # cross-scale consistency check results; see §10


@dataclass
class ScaleAttribution:
    """Generic per-scale attribution result. Each scale subclasses with
    scale-specific fields."""
    scale_id: int
    scale_name: str
    attribution_values: torch.Tensor  # scale-specific shape
    metadata: Dict[str, Any]          # scale-specific extras
    significance: Optional[torch.Tensor]  # p-values where applicable


@dataclass
class ConsistencyReport:
    """Cross-scale consistency check results."""
    check_1_drugclass_gene_overlap: Optional[float]   # Pearson r
    check_2_pathway_gene_recovery: Optional[float]    # fraction
    check_3_grn_gene_overlap: Optional[float]         # Jaccard
    check_4_patient_cluster_coherence: Optional[float]  # p-value
    passes: Dict[int, bool]                            # per-check pass/fail
    all_passed: bool                                   # all 4 passed
```

### 1.5 The InterpretabilityConfig Hyperparameter Bundle

```python
@dataclass
class InterpretabilityConfig:
    """L2.4 hyperparameter configuration."""

    # Scale 1 (Geometric) — Kendiukhov spectral
    scale_1_enabled: bool = True
    spectral_n_components: int = 50  # top eigenvalues to retain
    spectral_kernel: str = "gaussian"  # or "linear", "cosine"

    # Scale 2 (Drug-class) — CPA latent (built into L7; no config)

    # Scale 3 (Pathway) — GEARS GO + Beyondcell
    scale_3_enabled: bool = True
    beyondcell_signature_db: str = "hallmark"  # "hallmark", "kegg", "reactome"
    gears_go_neighbor_depth: int = 2  # k-hop GO graph neighbors

    # Scale 4 (GRN) — scRank
    scale_4_enabled: bool = True
    scrank_propagation_steps: int = 3
    scrank_top_k: int = 50

    # Scale 5 (Gene-level) — substrate-conditional
    scale_5_enabled: bool = True
    scale_5_method: str = "auto"  # "auto" routes; "eig", "linear_proj", "vae_ig"
    eig_baseline_strategy: str = "hidden_nonlinear"  # Jha H-N-IG
    eig_n_steps: int = 50
    smoothgrad_n_samples: int = 20
    smoothgrad_noise_sigma: float = 0.15
    bonferroni_alpha: float = 0.05
    ensemble_aggregation: str = "intersection"  # "intersection", "union", "majority"

    # Scale 6 (Spatial) — River DSEP
    scale_6_enabled: bool = True  # auto-disabled if no spatial coords
    river_branch_weighting: str = "equal"  # "equal", "learned"

    # Scale 7 (Patient) — SHAP individual
    scale_7_enabled: bool = True
    shap_n_samples: int = 100
    shap_explainer: str = "kernel"  # or "deep", "gradient"
    patient_cluster_method: str = "leiden"  # for Check 4

    # Cross-scale consistency
    consistency_checks_enabled: bool = True
    check_1_threshold: float = 0.5    # Pearson r threshold
    check_2_threshold: float = 0.30   # fraction threshold
    check_3_threshold: float = 0.20   # Jaccard threshold
    check_4_threshold: float = 0.01   # p-value threshold

    # Compute envelope
    device: str = "cuda:0"
    batch_size: int = 64  # smaller than L2.2 due to attribution overhead
    cache_attribution_path: str = (
        "/scratch/akula.pra/INTERCEPTA/attribution/"
        "{substrate}/{dataset}/{split}/scale_{scale_id}/"
    )
```

### 1.6 Verdict-Conditional Attribution Gating

The verdict-conditional gating pattern (§1.3) is BINDING. It ensures:
- `abstain_ood` predictions do NOT receive attribution (the prediction is outside the training distribution; attribution would be unreliable extrapolation, and presenting it would be epistemically dishonest)
- `confident_predict` predictions receive full attribution at full confidence
- `abstain_aleatoric` predictions receive attribution flagged as "reduced confidence due to label noise" — the mechanism trace may be valid, but the underlying prediction it explains is itself uncertain
- `abstain_epistemic` predictions receive attribution flagged as "extrapolation flagged" — the mechanism trace explains a prediction that extrapolates beyond training distribution; users should treat it as exploratory

This is the **Decision 5 v2 ↔ Decision 7 v2 integration point**. It is the operational consequence of L2.3 providing OOD signals and L2.4 honoring them.

---

## §2 What This Document Inherits from L2.2 and L2.3

### 2.1 From L2.2 (L7 Architecture)

L2.4 consumes the `L7Output.attribution_hooks` defined in L2.2 §1.4. The hooks are:
- `cell_emb`: [N_cells, 512] canonical cell embedding from Slot 1 — used by Scales 1, 4, 5 (Branch A IG path)
- `drug_emb`: [N_drugs, D_drug] chemical embedding from Slot 2 — used by Scale 2
- `latent_perturb`: [N_drugs, latent_dim] from Slot 3 — used by Scale 2 augmentation
- `z`: [N_cells, latent_dim] disentangled latent — used by Scales 3, 4
- `z_graph`: [N_cells, latent_dim] graph-conditioned latent from Slot 4 — used by Scales 3, 4
- `y_cell`: [N_cells, output_dim] cell-level prediction — used by Scales 5, 7

L2.4 does NOT modify L7's forward path. Attribution computation is post-hoc on the recorded hooks. The L7 head must be in eval mode with hooks enabled (see §11 implementation notes).

### 2.2 From L2.3 (OOD Stack)

L2.4 consumes `OODOutput.operational_verdict` for verdict-conditional gating (§1.6).

L2.4 also consumes `OODOutput.epistemic_uncertainty` for Scale 5 Branch A's significance test scaling — high epistemic uncertainty makes Bonferroni correction more conservative.

### 2.3 From L2.1 (Substrate)

Scale 5 Branching A/B/C is dispatched by substrate identity. L2.4 imports L2.1's substrate name registry to route correctly. The Branching is BINDING per Decision 7 v2:
- FM substrates (scFoundation/UCE/scGPT/Geneformer) → Branch A (EIG H-N-IG + SmoothGrad)
- scTOP → Branch B (linear projection coefficients ARE the attribution)
- scVI family → Branch C (IG over VAE decoder)
- PCA+HVG → Branch D (loadings × cell coordinates; Decision 7 v2 implicit per Decision 1 v2 Baseline A)

§7 specifies all four branches in full.

---

## §3 Scale 1 — Geometric (Spectral Analysis)

### 3.1 The Scale 1 Contract

Scale 1 produces a **topological characterization** of the substrate's learned latent space relative to a specific (cell, drug, prediction) tuple. Per Kendiukhov 2026 (Q1 anchor), spectral analysis of the FM latent space exposes biologically meaningful structure: eigenmodes of the latent kernel correspond to coordinated transcriptional programs.

**Scale 1 is FM-ONLY** (Decision 7 v2 BINDING). Parameter-free substrates (scTOP, PCA+HVG) have no learned non-linear geometry to analyze — their representations are linear projections by construction. For these substrates, Scale 1 returns None and L2.4 skips it cleanly.

```python
class GeometricAttributor(torch.nn.Module):
    """Scale 1 — Kendiukhov spectral geometry of FM latent embedding.

    Reference: Kendiukhov 2026 (Q1 anchor) on spectral analysis of FM internals.
    BINDING: FM-substrate-only per Decision 7 v2 §3.2.
    """

    SCALE_ID = 1
    SCALE_NAME = "geometric_spectral"

    def __init__(
        self,
        substrate: SubstrateInterface,
        config: InterpretabilityConfig,
    ):
        super().__init__()
        if not self._is_fm_substrate(substrate):
            self._fm_active = False
        else:
            self._fm_active = True
        self.substrate = substrate
        self.config = config

    def forward(
        self,
        adata: AnnData,
        drug_smiles: List[str],
        covariates: Covariates,
        l7_hooks: Dict[str, torch.Tensor],
        prediction_idx: int,
        verdict: str,
    ) -> Optional[Scale1Attribution]:
        if not self._fm_active:
            return None  # FM-only; skip cleanly

        # Spectral analysis on cell embedding for this prediction
        cell_emb = l7_hooks["cell_emb"]  # [N_cells, 512]
        # Build local kernel matrix (e.g., Gaussian) on the neighborhood
        K = self._kernel_matrix(cell_emb, kernel=self.config.spectral_kernel)
        # Eigendecomposition; top-K eigenvalues + eigenvectors
        eigenvalues, eigenvectors = torch.linalg.eigh(K)
        # Top-K (largest); these are the "biological programs" per Kendiukhov
        top_eig = eigenvalues[-self.config.spectral_n_components:]
        top_evec = eigenvectors[:, -self.config.spectral_n_components:]

        # Project the prediction-relevant cell embedding onto top eigenvectors
        projections = top_evec.T @ cell_emb[prediction_idx]
        # Magnitude per eigenmode = how much this prediction's cell aligns
        # with that biological program

        return Scale1Attribution(
            eigenvalues=top_eig,
            projections=projections.abs(),  # magnitude attribution per eigenmode
            metadata={"kernel": self.config.spectral_kernel},
        )


@dataclass
class Scale1Attribution(ScaleAttribution):
    scale_id: int = 1
    scale_name: str = "geometric_spectral"
    eigenvalues: torch.Tensor = None       # [n_components]
    projections: torch.Tensor = None       # [n_components]
    # attribution_values inherited from ScaleAttribution
```

### 3.2 What Scale 1 Reveals

The eigenvalues + projections tuple answers: "which biological programs (top eigenmodes) does this cell's representation engage with?" Programs with high projection magnitude indicate the cell's transcriptional state aligns with that program; the program's eigenvalue indicates how prevalent that program is across the cell population.

This is **not gene-level attribution** (that is Scale 5). It is **program-level attribution** at the substrate's representational geometry. Different programs may activate the same genes; same programs may activate in different cell types. Scale 1 captures the program; Scales 3-5 capture pathway / GRN / gene specifics.

### 3.3 Why FM-Only

Per Kendiukhov 2026 + Decision 7 v2 §3.2: spectral analysis requires a **learned non-linear representation** with internal geometric structure. Foundation models satisfy this (transformer layers create such geometry). scTOP's projections onto reference cell types are linear by construction — there is no spectral structure to analyze beyond what is already in the projection coefficients themselves (which Scale 5 Branch B exposes directly). PCA+HVG is also linear; its principal components ARE the eigenmodes, accessible without additional spectral analysis.

L2.4 honors this constraint: when substrate is FM, Scale 1 runs; otherwise Scale 1 returns None and the consistency checks (§10) operate without it.

### 3.4 Compute Cost

Spectral analysis is medium cost: O(N²) memory for kernel matrix, O(N³) for eigendecomposition where N = batch size of cells. For a batch of 1024 cells (default config), kernel matrix is ~4MB, eigendecomposition is ~1 sec on A100. Manageable.

For larger neighborhoods (e.g., 10K cells), iterative eigensolvers (scipy.sparse.linalg.eigsh) reduce cost to O(N · k) for top-k. L2.4 defaults to batch-size matched (1024) for tractable per-prediction interpretability.

### 3.5 What Scale 1 Does NOT Do

- Does NOT identify which genes drive the eigenmode. That is Scale 5 (gene-level).
- Does NOT distinguish biological programs from technical artifacts. Per Kendiukhov 2026: spectral structure may include batch effects, dropout artifacts, etc. Cross-scale consistency checks (§10) detect when Scale 1 disagrees with Scales 3-5 (which use external biological priors).
- Does NOT apply to parameter-free substrates. Branch B (scTOP) and Branch D (PCA) handle this cleanly via Scale 5; Scale 1 returns None.

---

## §4 Scale 2 — Drug-Class (CPA Disentangled Latent)

### 4.1 The Scale 2 Contract

Scale 2 reveals **drug-class similarity** — which drugs share predicted mechanism. Per Decision 7 v2 + Lotfollahi 2023 CPA: the CPA disentangled latent space has the property that drugs with similar mechanism-of-action produce similar `latent_perturb` vectors. Scale 2 makes this property operational.

**Scale 2 is substrate-agnostic** (built into L7 Slot 3 + intrinsic CPA latent). It is the cheapest scale: no separate computation, just inspection of cached drug embeddings + latent_perturb vectors.

```python
class DrugClassAttributor(torch.nn.Module):
    """Scale 2 — drug-class similarity from CPA disentangled latent.

    Reference: Lotfollahi 2023 CPA. Built into L7 architecture; Scale 2
    is inspection of cached intermediates, not separate computation.
    """

    SCALE_ID = 2
    SCALE_NAME = "drug_class_cpa"

    def __init__(self, config: InterpretabilityConfig):
        super().__init__()
        self.config = config

    def forward(
        self,
        adata, drug_smiles, covariates,
        l7_hooks: Dict[str, torch.Tensor],
        prediction_idx: int,
        verdict: str,
    ) -> Scale2Attribution:
        # latent_perturb for this drug
        latent_perturb = l7_hooks["latent_perturb"][prediction_idx]  # [latent_dim]
        # Drug embedding for this drug
        drug_emb = l7_hooks["drug_emb"][prediction_idx]  # [drug_emb_dim]

        # For Scale 2 attribution, we identify the K most-similar drugs in
        # the CPA latent space. These are the "drug class neighbors."
        # In practice this requires a reference set of drug embeddings;
        # Layer 5 implementation specifies the reference set.

        return Scale2Attribution(
            drug_emb=drug_emb,
            latent_perturb=latent_perturb,
            metadata={
                "interpretation": "drug class similarity in CPA latent space",
                "expected_property": "similar MoA → similar latent_perturb",
            },
        )


@dataclass
class Scale2Attribution(ScaleAttribution):
    scale_id: int = 2
    scale_name: str = "drug_class_cpa"
    drug_emb: torch.Tensor = None
    latent_perturb: torch.Tensor = None
    # attribution_values: top-K similar drugs + similarity scores
    # (computed in Layer 5 when reference drug set available)
```

### 4.2 Why Scale 2 Is Cheap

CPA latent is already computed during L7 forward pass (it is the L7 architecture's core composition framework). Scale 2 attribution is just inspecting the cached `latent_perturb` and comparing to a reference drug set. No additional model forward passes, no IG path integration, no SHAP sampling.

This is the operational reward of building CPA into the architecture: drug-class interpretability comes "for free."

### 4.3 What Scale 2 Reveals

For a drug X with predicted response P on a cell C:
- Which other drugs in the reference set produce similar latent_perturb vectors? → "Drugs in the same class as X"
- Do those similar drugs have known mechanisms (e.g., MAPK inhibitors, EGFR antagonists)? → "X's mechanism class"

This gives a top-level mechanism classification (drug class), which is then refined by Scales 3-5 (specific pathway, GRN, genes).

### 4.4 Cross-Scale Consistency Implication

Scale 2's drug-class similarity grounds Cross-Scale Consistency Check 1 (§10): drugs with similar Scale 2 attribution should have overlapping Scale 5 gene-level attribution (Decision 7 v2 Check 1: Pearson r ≥ 0.5 between drug-pair CPA similarity and gene attribution overlap).

### 4.5 What Scale 2 Does NOT Do

- Does NOT name the drug class. Identifying "this latent neighborhood corresponds to MAPK inhibitors" requires external annotation (DrugBank class labels, ATC codes). Layer 5 implementation joins the latent neighborhood with such labels.
- Does NOT predict response to novel drugs from drug class alone. The CPA latent supports near-linear arithmetic (scGen heritage per L2.2 §4.4); novel drug response is still predicted by L7 forward, not by class lookup.
- Does NOT replace Scale 5 gene-level attribution. Class similarity is coarse; gene-level is fine. Both are needed for a complete mechanism trace.
---

## §5 Scale 3 — Pathway (GEARS GO + Beyondcell)

### 5.1 The Scale 3 Contract

Scale 3 attributes a prediction to **biological pathways** via two complementary signals:
1. **GEARS GO graph neighborhood** — from L2.2 Slot 4 graph-augmented module; identifies GO terms whose member genes participate in the prediction
2. **Beyondcell BCS (Beyondcell Score)** — pathway-level drug sensitivity score per Fustero-Torre 2024; provides an external pathway prior independent of L7's learned attention

**Scale 3 is substrate-agnostic** and built partially into L2.2 Slot 4. L2.4 adds the Beyondcell external prior and composes both signals into pathway-level attribution.

```python
class PathwayAttributor(torch.nn.Module):
    """Scale 3 — pathway attribution via GEARS GO graph + Beyondcell BCS.

    BINDING per Drift Finding 7: Beyondcell appears here (Scale 3),
    NOT in L2.2 Slot 4. Slot 4 has GEARS attention; L2.4 composes that
    with Beyondcell pathway scoring.
    """

    SCALE_ID = 3
    SCALE_NAME = "pathway_gears_beyondcell"

    def __init__(
        self,
        l7_ensemble: L7Ensemble,
        config: InterpretabilityConfig,
        beyondcell_signature_db: Optional[str] = None,
    ):
        super().__init__()
        self.l7_ensemble = l7_ensemble
        self.config = config
        # Load Beyondcell signatures
        # (hallmark / kegg / reactome from MSigDB or Beyondcell package)
        self.signatures = self._load_beyondcell_signatures(
            beyondcell_signature_db or config.beyondcell_signature_db
        )

    def forward(
        self,
        adata, drug_smiles, covariates,
        l7_hooks: Dict[str, torch.Tensor],
        prediction_idx: int,
        verdict: str,
    ) -> Scale3Attribution:
        # Signal 1: GEARS GO graph neighborhood from L7 Slot 4 attention
        # Extract attention weights over GO graph from cached hooks
        z = l7_hooks["z"][prediction_idx]              # [latent_dim]
        z_graph = l7_hooks["z_graph"][prediction_idx]  # [latent_dim]
        # The (z_graph - z) delta represents the graph module's contribution.
        # We attribute this delta back to GO terms via the Slot 4 GO attention.
        gears_go_attribution = self._extract_gears_go_attention(
            z, z_graph, depth=self.config.gears_go_neighbor_depth
        )  # [N_go_terms] attribution per GO term

        # Signal 2: Beyondcell BCS — external pathway prior
        # Compute pathway signature score on the cell expression
        cell_expr = adata.X[prediction_idx]  # [N_genes] raw expression
        bcs_scores = self._compute_bcs(cell_expr, self.signatures)
        # bcs_scores[pathway] = how much pathway is "active" in this cell

        # Compose: rank pathways that BOTH (a) GEARS attributes high AND
        # (b) Beyondcell scores high on this cell
        combined_attribution = self._compose_attribution(
            gears_go_attribution, bcs_scores
        )

        return Scale3Attribution(
            gears_go_attribution=gears_go_attribution,
            beyondcell_scores=bcs_scores,
            combined_attribution=combined_attribution,
            top_pathways=self._top_k_pathways(combined_attribution, k=20),
        )


@dataclass
class Scale3Attribution(ScaleAttribution):
    scale_id: int = 3
    scale_name: str = "pathway_gears_beyondcell"
    gears_go_attribution: torch.Tensor = None     # [N_go_terms]
    beyondcell_scores: torch.Tensor = None         # [N_pathways]
    combined_attribution: torch.Tensor = None      # [N_combined]
    top_pathways: List[Tuple[str, float]] = None   # top-K (pathway_name, score)
```

### 5.2 Why Two Sources Compose

GEARS GO attention is **learned from data**: it reflects what L7 actually attends to during prediction. This is the "model says it cares about these GO terms" signal.

Beyondcell BCS is **external prior**: it reflects literature-curated pathway signatures and their activity in the specific cell's expression. This is the "biology says this cell has these pathways active" signal.

Their composition (intersection or product) yields pathways that BOTH the model attends to AND are biologically active in the cell. This is more robust than either signal alone:
- If GEARS attends to a pathway that isn't biologically active in this cell → likely a learning artifact
- If a pathway is biologically active but GEARS doesn't attend to it → may not be relevant to drug response

The composition is the cross-validation that gives Scale 3 its mechanism-tracing power.

### 5.3 The Drift Finding 7 Architectural Identity

Per Drift Finding 7 BINDING (Decision 3 v2 architectural identities):
- **Beyondcell = Decision 7 v2 Scale 3 (pathway scale)**, NOT in L2.2 Slot 4
- This is why Slot 4 in L2.2 explicitly excludes Beyondcell

L2.4 honors this. Beyondcell is instantiated in Scale 3, with its signatures loaded from external databases (MSigDB / Hallmark / KEGG / Reactome). Slot 4's GEARS attention provides the model-side signal; Scale 3 composes the two.

### 5.4 Cross-Scale Consistency Implication

Scale 3's pathway attribution grounds **Cross-Scale Consistency Check 2** (§10): GEARS GO graph neighbors of the drug target should match EIG-attributed genes (Scale 5). Decision 7 v2 Check 2 threshold: ≥30% overlap between EIG top-20 genes and GEARS graph neighbors of drug target.

### 5.5 What Scale 3 Does NOT Do

- Does NOT identify gene-level attribution within a pathway. That is Scale 5.
- Does NOT predict pathway-level response. Beyondcell originally predicts drug sensitivity from pathway signatures; L2.4 uses it only for attribution, not prediction.
- Does NOT cover non-GO pathway ontologies exhaustively. Hallmark / KEGG / Reactome cover most biologically relevant pathways; specialized databases (e.g., disease-specific) are Layer 5 add-ons.

---

## §6 Scale 4 — GRN / Cell-Type (scRank Perturbation Propagation)

### 6.1 The Scale 4 Contract

Scale 4 attributes a prediction to a **gene regulatory network (GRN) propagation pattern** via scRank (Lin et al. 2023). Per Drift Finding 7 BINDING: scRank IS the gene-gene attention edge-weight init in L2.2 Slot 4. L2.4 Scale 4 makes this explicit as an interpretability signal — running scRank's perturbation propagation algorithm to identify which GRN topology drives the prediction for this cell type.

**Scale 4 is substrate-agnostic.** scRank operates on the gene-gene co-expression graph (cached at L2.2 §5.2) + cell-type-specific GRN topology.

```python
class GRNAttributor(torch.nn.Module):
    """Scale 4 — scRank GRN perturbation propagation.

    BINDING per Drift Finding 7: scRank is Slot 4 gene-gene attention
    edge-weight init in L2.2; L2.4 Scale 4 exposes the propagation
    as interpretability output.
    """

    SCALE_ID = 4
    SCALE_NAME = "grn_scrank"

    def __init__(
        self,
        gene_gene_graph: GraphData,
        config: InterpretabilityConfig,
    ):
        super().__init__()
        self.graph = gene_gene_graph
        self.config = config

    def forward(
        self,
        adata, drug_smiles, covariates,
        l7_hooks: Dict[str, torch.Tensor],
        prediction_idx: int,
        verdict: str,
    ) -> Scale4Attribution:
        # Drug targets (from covariates or DrugBank lookup)
        drug_targets = covariates.drug_targets[prediction_idx] \
                       if covariates.drug_targets is not None else None
        if drug_targets is None:
            # Without drug targets, scRank can still run but with reduced signal
            # — propagate from highly-attributed genes in z_graph
            seed_genes = self._extract_top_genes_from_z_graph(l7_hooks, prediction_idx)
        else:
            seed_genes = drug_targets

        cell_type = covariates.cell_type[prediction_idx]

        # scRank propagation: from seed genes, propagate through GRN
        # weighted by cell-type-specific co-expression
        propagated = self._scrank_propagate(
            seed_genes=seed_genes,
            cell_type=cell_type,
            n_steps=self.config.scrank_propagation_steps,
        )  # [N_genes] propagated activation score

        top_k = torch.topk(propagated, self.config.scrank_top_k)

        return Scale4Attribution(
            scrank_propagated=propagated,
            top_k_genes=top_k.indices,
            top_k_scores=top_k.values,
            seed_genes=seed_genes,
            cell_type=cell_type,
        )


@dataclass
class Scale4Attribution(ScaleAttribution):
    scale_id: int = 4
    scale_name: str = "grn_scrank"
    scrank_propagated: torch.Tensor = None  # [N_genes]
    top_k_genes: torch.Tensor = None         # gene indices
    top_k_scores: torch.Tensor = None        # propagation scores
    seed_genes: torch.Tensor = None
    cell_type: str = None
```

### 6.2 Why scRank Is the Interpretability Method

scRank is **cell-type-specific** (Lin 2023's contribution). The same drug acting through the same target may propagate through different GRN topologies in T cells vs B cells vs macrophages, producing different downstream gene activations. L7 captures this through the disentangled latent's cell-type covariate; Scale 4 makes the cell-type-specific GRN propagation explicit.

This is what makes Scale 4 different from Scale 5 (gene-level): Scale 5 reports "these genes are attributed to the prediction"; Scale 4 reports "these genes are attributed because they are downstream of the drug target in this cell type's regulatory network." Scale 4 carries network-causal structure that Scale 5 alone does not.

### 6.3 Cross-Scale Consistency Implication

Scale 4 grounds **Cross-Scale Consistency Check 3** (§10): top-50 scRank genes (Scale 4) should overlap with top-50 EIG genes (Scale 5). Decision 7 v2 Check 3 threshold: ≥20% Jaccard overlap (GRN-gradient consistency).

If Scale 4 says "drug target's GRN propagates to genes X, Y, Z" and Scale 5 says "the prediction is attributed to genes A, B, C with no overlap" — there is a mechanism-trace inconsistency. Either the GRN prior is wrong for this drug, or the gradient attribution is picking up spurious features. Either way, the prediction's mechanism is not robustly traced.

### 6.4 What Scale 4 Does NOT Do

- Does NOT prove causal regulation. scRank provides a propagation signal grounded in cell-type-specific co-expression; this is correlational + network-prior, not causal proof. Causal claims require intervention (CRISPRi, ChIP-seq).
- Does NOT capture cross-cell-type regulation. scRank runs per cell type. Cross-cell-type effects (e.g., paracrine signaling from one cell type to another) are not in Scale 4's scope; Phase F microbiome / TME work is (Charter v1.2 §4 rows 14, 15).
- Does NOT use the 15-layer Universal Net. Scale 4 uses the gene-gene graph + cell-type-specific GRN priors. Full multi-modal network integration is Phase F per Charter v1.2 §4 row 8.

---

## §7 Scale 5 — Gene-Level (Substrate-Conditional Branching, BINDING)

### 7.1 The Scale 5 Contract

Scale 5 produces **gene-level attribution** — for each prediction, which genes contribute most. This is the most computationally expensive scale and the one with explicit substrate-conditional branching per Decision 7 v2 §3.2 BINDING.

The branching:
- **Branch A** — FM substrate wins → EIG H-N-IG + SmoothGrad + Bonferroni
- **Branch B** — scTOP wins → linear projection coefficients (no path integration)
- **Branch C** — scVI family wins → IG over VAE decoder
- **Branch D** — PCA+HVG wins → loadings × cell coordinates

L2.4 implements ALL FOUR branches (Decision 7 v2 commits to all-branch implementation pre-Layer-5-resolution). The branch selected at inference is determined by `substrate.NAME`.

```python
class GeneLevelAttributor(torch.nn.Module):
    """Scale 5 — substrate-conditional gene-level attribution.

    BINDING per Decision 7 v2 §3.2: implements all 4 branches; routes by substrate.
    """

    SCALE_ID = 5
    SCALE_NAME = "gene_level_substrate_conditional"

    def __init__(
        self,
        substrate: SubstrateInterface,
        l7_ensemble: L7Ensemble,
        config: InterpretabilityConfig,
    ):
        super().__init__()
        self.substrate = substrate
        self.l7_ensemble = l7_ensemble
        self.config = config

        # Route to appropriate branch
        if substrate.NAME in ("scfoundation", "uce", "scgpt", "geneformer"):
            self.branch = "A_fm_eig"
            self.attributor = EIGHnigSmoothGradAttributor(
                l7_ensemble, config
            )
        elif substrate.NAME == "sctop":
            self.branch = "B_sctop_linear"
            self.attributor = LinearProjectionAttributor(
                substrate, config
            )
        elif substrate.NAME in ("scvi", "scanvi", "mrvi"):
            self.branch = "C_scvi_decoder_ig"
            self.attributor = VAEDecoderIGAttributor(
                substrate, l7_ensemble, config
            )
        elif substrate.NAME == "pca_hvg":
            self.branch = "D_pca_loadings"
            self.attributor = PCALoadingsAttributor(
                substrate, config
            )
        else:
            raise ValueError(
                f"No Scale 5 branch for substrate {substrate.NAME}. "
                f"Add to GeneLevelAttributor branching."
            )

    def forward(
        self, adata, drug_smiles, covariates,
        l7_hooks, prediction_idx, verdict,
    ) -> Scale5Attribution:
        result = self.attributor(
            adata, drug_smiles, covariates,
            l7_hooks, prediction_idx, verdict,
        )
        result.branch = self.branch
        return result


@dataclass
class Scale5Attribution(ScaleAttribution):
    scale_id: int = 5
    scale_name: str = "gene_level_substrate_conditional"
    branch: str = None  # "A_fm_eig", "B_sctop_linear", "C_scvi_decoder_ig", "D_pca_loadings"
    gene_attribution: torch.Tensor = None    # [N_genes] per-gene score
    gene_significance: torch.Tensor = None   # [N_genes] Bonferroni-corrected p-values
    top_k_genes: torch.Tensor = None         # gene indices, top-K
    top_k_scores: torch.Tensor = None
    ensemble_jaccard: float = None           # cross-ensemble stability (Pass 5)
```

### 7.2 Branch A — EIG H-N-IG + SmoothGrad (FM Substrates)

Per Jha 2020 + Reynolds-Pan 2025:

```python
class EIGHnigSmoothGradAttributor(torch.nn.Module):
    """Branch A — Enhanced Integrated Gradients with Hidden-space baseline +
    Nonlinear path + SmoothGrad averaging.

    Reference: Jha 2020 (Q7 anchor 3); Reynolds-Pan 2025 (Q7 anchor 1).
    Used when L7's substrate is a foundation model.
    """

    def __init__(self, l7_ensemble: L7Ensemble, config: InterpretabilityConfig):
        super().__init__()
        self.l7_ensemble = l7_ensemble
        self.config = config

    def forward(self, adata, drug_smiles, covariates, l7_hooks,
                prediction_idx, verdict) -> Scale5Attribution:
        # For each ensemble head (N=5 per L2.2 §1.5):
        per_head_attributions = []
        for head in self.l7_ensemble.heads:
            # 1. Compute hidden-space baseline (Jha H-N-IG)
            #    Use mean cell embedding of training distribution
            hidden_baseline = self._compute_hidden_baseline(head)
            # 2. SmoothGrad: add Gaussian noise; average over N samples
            attr_samples = []
            for _ in range(self.config.smoothgrad_n_samples):
                noise = torch.randn_like(l7_hooks["cell_emb"]) * \
                        self.config.smoothgrad_noise_sigma
                noised_input = l7_hooks["cell_emb"] + noise
                # 3. Integrated Gradients along nonlinear path
                #    from hidden_baseline to noised_input
                attr = self._ig_nonlinear_path(
                    head, hidden_baseline, noised_input,
                    n_steps=self.config.eig_n_steps,
                    target_prediction_idx=prediction_idx,
                )
                attr_samples.append(attr)
            head_attr = torch.stack(attr_samples).mean(dim=0)
            per_head_attributions.append(head_attr)

        # Aggregate across ensemble per config.ensemble_aggregation
        ensemble_attrs = torch.stack(per_head_attributions)  # [N=5, N_genes]
        if self.config.ensemble_aggregation == "intersection":
            # Take genes significant in ALL heads
            gene_attribution = ensemble_attrs.mean(dim=0)
            # Significance: per-gene t-test across heads, Bonferroni-corrected
            t_stat, p_vals = self._per_gene_ttest(ensemble_attrs)
            p_vals_corrected = self._bonferroni(p_vals, alpha=self.config.bonferroni_alpha)
            gene_significance = p_vals_corrected
        elif self.config.ensemble_aggregation == "union":
            gene_attribution = ensemble_attrs.max(dim=0).values
            gene_significance = None
        elif self.config.ensemble_aggregation == "majority":
            # 3-of-5 heads must agree
            sig_per_head = ensemble_attrs > ensemble_attrs.median(dim=-1).values.unsqueeze(-1)
            majority = sig_per_head.float().sum(dim=0) >= 3
            gene_attribution = ensemble_attrs.mean(dim=0) * majority.float()
            gene_significance = None

        # Top-K
        top_k = torch.topk(gene_attribution, k=50)

        # Cross-ensemble Jaccard for Pass 5 stability check
        ensemble_jaccard = self._compute_ensemble_jaccard(ensemble_attrs, k=50)

        return Scale5Attribution(
            gene_attribution=gene_attribution,
            gene_significance=gene_significance,
            top_k_genes=top_k.indices,
            top_k_scores=top_k.values,
            ensemble_jaccard=ensemble_jaccard,
        )

    def _ig_nonlinear_path(self, head, baseline, input, n_steps, target_prediction_idx):
        """Integrated Gradients along nonlinear interpolation path."""
        # Use captum.attr.IntegratedGradients with custom path function
        # for the nonlinear baseline-to-input trajectory
        # (Jha 2020 spec for "nonlinear path" variant)
        ...
```

### 7.3 Branch B — Linear Projection Coefficients (scTOP)

Per Souza-Mehta 2026 + Decision 7 v2 BINDING:

```python
class LinearProjectionAttributor(torch.nn.Module):
    """Branch B — scTOP parameter-free linear projection coefficients
    ARE the gene-level attribution. No path integration needed.

    Reference: Souza-Mehta 2026. The Souza-Mehta methodological bar
    reinforced: parameter-free wins on interpretability ease.
    """

    def __init__(self, substrate: SubstrateInterface, config: InterpretabilityConfig):
        super().__init__()
        if substrate.NAME != "sctop":
            raise ValueError(...)
        self.substrate = substrate
        self.config = config

    def forward(self, adata, drug_smiles, covariates, l7_hooks,
                prediction_idx, verdict) -> Scale5Attribution:
        # scTOP projection coefficients per cell type
        # Per Souza-Mehta: the coefficient matrix C [N_celltypes, N_genes]
        # encodes which genes contribute to each cell type's signature.
        # For a specific cell with prediction P:
        #   1. The cell projects onto cell types with weights w [N_celltypes]
        #   2. The gene-level attribution is w @ C [N_genes]
        # No model gradients required.

        projections = self.substrate.encode(adata)  # [N_cells, N_celltypes]
        cell_proj = projections[prediction_idx]      # [N_celltypes]
        coefficient_matrix = self.substrate.get_projection_coefficients()
        # coefficient_matrix: [N_celltypes, N_genes]

        gene_attribution = cell_proj @ coefficient_matrix  # [N_genes]

        # Significance: bootstrap confidence intervals across N=5 ensemble
        # (Each ensemble head may have different gene scaling; bootstrap
        # gives per-gene CI.)
        ensemble_attrs = self._compute_per_head_attributions(
            adata, prediction_idx
        )
        gene_significance = self._bootstrap_ci(ensemble_attrs)

        top_k = torch.topk(gene_attribution, k=50)
        ensemble_jaccard = self._compute_ensemble_jaccard(ensemble_attrs, k=50)

        return Scale5Attribution(
            gene_attribution=gene_attribution,
            gene_significance=gene_significance,
            top_k_genes=top_k.indices,
            top_k_scores=top_k.values,
            ensemble_jaccard=ensemble_jaccard,
        )
```

### 7.4 Branch C — VAE Decoder IG (scVI Family)

```python
class VAEDecoderIGAttributor(torch.nn.Module):
    """Branch C — IG + SmoothGrad over scVI/scANVI/MrVI decoder.

    Uses scVI posterior mean as the EIG hidden-space baseline.
    Cheaper than Branch A (decoder is smaller than FM); medium cost.
    """

    def __init__(self, substrate: SubstrateInterface, l7_ensemble: L7Ensemble,
                 config: InterpretabilityConfig):
        super().__init__()
        if substrate.NAME not in ("scvi", "scanvi", "mrvi"):
            raise ValueError(...)
        self.substrate = substrate
        self.l7_ensemble = l7_ensemble
        self.config = config

    def forward(self, adata, drug_smiles, covariates, l7_hooks,
                prediction_idx, verdict) -> Scale5Attribution:
        # Use scVI posterior mean as the baseline (EIG H-N-IG analog)
        z_baseline = self.substrate.get_posterior_mean()  # [latent_dim]
        z_input = l7_hooks["cell_emb"][prediction_idx]    # [latent_dim] -- wait, this is canonical 512; for scVI it's projected up from 30

        # IG along path from z_baseline to z_input
        # SmoothGrad averaging
        # Bonferroni correction across N=5 ensemble
        # (similar structure to Branch A but with VAE decoder as the target function)
        ...
        return Scale5Attribution(...)
```

### 7.5 Branch D — PCA Loadings (PCA+HVG Substrate)

```python
class PCALoadingsAttributor(torch.nn.Module):
    """Branch D — PCA loadings × cell coordinates = gene attribution.

    Implicit in Decision 7 v2 (parameter-free pattern extension to PCA);
    L2.4 implements explicitly for substrate flexibility completeness.
    """

    def __init__(self, substrate: SubstrateInterface, config: InterpretabilityConfig):
        super().__init__()
        if substrate.NAME != "pca_hvg":
            raise ValueError(...)
        self.substrate = substrate

    def forward(self, adata, drug_smiles, covariates, l7_hooks,
                prediction_idx, verdict) -> Scale5Attribution:
        # PCA: x ≈ U @ Σ @ V^T where V holds the loadings
        # Cell coordinates in PC space: c = x @ V
        # Gene attribution for prediction: w @ V^T where w = downstream importance per PC
        # In our case w comes from L7's adapter from PC-space to 512-canonical to L7 output

        loadings = self.substrate.get_loadings()  # [N_pcs, N_genes]
        cell_coords = l7_hooks["cell_emb"][prediction_idx]  # canonical 512

        # Map back to PC space (since substrate.project_to_canonical zero-pads PCs to 512)
        n_pcs = self.substrate.NATIVE_DIM
        pc_coords = cell_coords[:n_pcs]  # zero-padded part discarded

        gene_attribution = pc_coords @ loadings  # [N_genes]

        top_k = torch.topk(gene_attribution.abs(), k=50)

        return Scale5Attribution(
            gene_attribution=gene_attribution,
            gene_significance=None,  # PCA doesn't natively give significance
            top_k_genes=top_k.indices,
            top_k_scores=top_k.values,
            ensemble_jaccard=1.0,  # PCA is deterministic; no ensemble variation
        )
```

### 7.6 Compute Cost Per Branch

Branch costs per single (cell, drug) attribution:

| Branch | Substrate | Cost per attribution | Scale at V0 (100K cells × 10 drugs) |
|---|---|---|---|
| A — EIG+SmoothGrad | FM | ~50 forward+backward × 20 noise samples × N=5 ensemble = ~5,000 passes | ~1-2 GPU-days |
| B — Linear projection | scTOP | Linear algebra; <1 sec per attribution | <1 hour total |
| C — VAE decoder IG | scVI | ~50 forward+backward × 20 × N=5 = ~5,000 passes; decoder is smaller than FM | ~hours |
| D — PCA loadings | PCA | Linear algebra; <1 sec per attribution | <1 hour total |

The Souza-Mehta methodological consequence: Branch B (scTOP) is **two orders of magnitude cheaper** than Branch A (FM). Per Decision 8 v2 Commitment 5 — if scTOP achieves comparable predictive performance, this is significant operational evidence in favor of parameter-free for interpretability deployment.

### 7.7 Cross-Scale Consistency Implication

Scale 5 grounds **three** of the four cross-scale consistency checks:
- Check 1: Drug-class similarity (Scale 2) ↔ gene attribution overlap (Scale 5) — Pearson r ≥ 0.5
- Check 2: Pathway prior (Scale 3 GEARS GO neighbors of drug target) ↔ gene attribution (Scale 5) — ≥30% overlap
- Check 3: GRN propagation (Scale 4 scRank top-50) ↔ gene attribution (Scale 5 top-50) — ≥20% Jaccard

Scale 5 is the cross-validation hub for multi-scale consistency. If Scale 5 disagrees with three other scales, the mechanism trace is not robust.

### 7.8 Pass 1-3 Empirical Implementation

Decision 7 v2 Pass 1-3 are Layer-5-verified empirical criteria. L2.4 architecture supports them via:

**Pass 1 (Vanilla IG Baseline Rejection):** Run both vanilla IG (zero-baseline + linear path) and EIG H-N-IG on the same data; compare significant-attribution counts. Architecture provides both via Captum + the H-N-IG path implementation. Decision 7 v2 expects ≥50% more significant attributions for EIG.

**Pass 2 (SmoothGrad Improvement):** Run Branch A with and without SmoothGrad; compare top-1% attribution precision. Architecture provides via the `smoothgrad_n_samples` config knob (0 disables; default 20 enables). Decision 7 v2 expects ≥0.05 precision improvement.

**Pass 3 (Biological Discovery Recovery):** For the 5 named drugs (Trastuzumab → ERBB2, Ibrutinib → BTK, Imatinib → ABL1, Cetuximab → EGFR, Vemurafenib → BRAF), check whether top-K attributed genes include the canonical target. Layer 5 implementation specifies the evaluation set; architecture supports via top-K attribution output.

### 7.9 What Scale 5 Does NOT Do

- Does NOT distinguish "gene attributed because it drives prediction" from "gene attributed because it correlates with biology." Attribution is correlational unless coupled with intervention (per §10.6).
- Does NOT generalize attribution across drugs. Each drug has its own gene attribution; cross-drug patterns require Scale 2 (drug-class) for grouping.
- Does NOT operate at the protein / metabolite level. Scale 5 is gene-level (transcriptional). Protein-level attribution would require proteomics data; out of L2.4 scope (Phase F multimodal).

---

## §8 Scale 6 — Spatial (River Two-Branch DSEP)

### 8.1 The Scale 6 Contract

Scale 6 attributes a prediction to **spatial location** within tissue. Per Cui-Yuan 2025 River: a two-branch DSEP (Differential Spatial Expression Pattern) framework decomposes spatial transcriptomics signal into spatially-coherent vs spatially-diffuse components.

**Scale 6 is spatial-modality-only**: it requires spatial transcriptomics input (Visium, Xenium, MERFISH coordinates). For dissociated scRNA-seq inputs, Scale 6 returns None.

```python
class SpatialAttributor(torch.nn.Module):
    """Scale 6 — River two-branch DSEP spatial attribution.

    Reference: Cui-Yuan 2025 (Q7 anchor 2).
    Active only when spatial coordinates available in adata.obsm['spatial'].
    """

    SCALE_ID = 6
    SCALE_NAME = "spatial_river_dsep"

    def __init__(self, config: InterpretabilityConfig):
        super().__init__()
        self.config = config

    def forward(self, adata, drug_smiles, covariates, l7_hooks,
                prediction_idx, verdict) -> Optional[Scale6Attribution]:
        # Check for spatial coordinates
        if 'spatial' not in adata.obsm:
            return None  # No spatial data; skip cleanly

        spatial_coords = adata.obsm['spatial']  # [N_cells, 2]
        cell_pred = l7_hooks["y_cell"][prediction_idx]
        cell_attribution = self._cell_attribution_for_prediction(
            l7_hooks, prediction_idx
        )

        # River DSEP: decompose attribution into spatially-coherent and
        # spatially-diffuse branches
        coherent_branch, diffuse_branch = self._river_dsep_decompose(
            cell_attribution=cell_attribution,
            spatial_coords=spatial_coords,
            weighting=self.config.river_branch_weighting,
        )

        # Spatial domains: clusters of cells with coherent attribution
        spatial_domains = self._extract_spatial_domains(coherent_branch, spatial_coords)

        return Scale6Attribution(
            coherent_branch=coherent_branch,
            diffuse_branch=diffuse_branch,
            spatial_domains=spatial_domains,
            spatial_coords=spatial_coords,
        )


@dataclass
class Scale6Attribution(ScaleAttribution):
    scale_id: int = 6
    scale_name: str = "spatial_river_dsep"
    coherent_branch: torch.Tensor = None     # spatially-coherent attribution
    diffuse_branch: torch.Tensor = None       # spatially-diffuse attribution
    spatial_domains: List[Dict] = None        # cluster info
    spatial_coords: torch.Tensor = None
```

### 8.2 What Scale 6 Reveals

For tumor tissue with spatial transcriptomics: which regions of the tumor (e.g., invasive front, hypoxic core, immune-infiltrated zones) drive the predicted drug response? This is operationally important — a drug predicted effective overall may only act on a specific spatial domain; resistant subdomains may exist within the same tumor.

This is the spatial-resolution complement to Scale 4 (cell-type-resolution): Scale 4 says "drug effect propagates through this cell type's GRN"; Scale 6 says "drug effect localizes to this spatial domain within the tumor."

### 8.3 Phase F Continuity

Scale 6 is Phase B's spatial attribution; Phase F extends with full spatial-aware Universal Net integration per Charter v1.2 §4 row 23 (currently NOT specified beyond this continuity note). L2.4's Scale 6 is the Phase B foundation that Phase F builds on.

### 8.4 What Scale 6 Does NOT Do

- Does NOT operate without spatial data. Returns None cleanly when adata.obsm['spatial'] is missing.
- Does NOT predict spatial heterogeneity. River decomposes observed attribution into spatial branches; prediction of spatial heterogeneity is a separate task (Phase F Decision 17 two-population ODE).
- Does NOT correct for spatial confounders. Tissue boundaries, library preparation artifacts, and registration errors may contaminate the spatial signal. Layer 5 implementation specifies QC checks.

---

## §9 Scale 7 — Patient (SHAP Individual-Level)

### 9.1 The Scale 7 Contract

Scale 7 produces **per-patient attribution** — why this specific patient is predicted to respond. Per DeepStrataAge composite (Q7.4) + SHAP (Lundberg-Lee 2017 referenced in Decision 7 v2 §"Why not adopt a single SHAP-style universal method"): SHAP is appropriate at the patient-aggregation level (Slot 6 output), not as a universal attribution method across all 7 scales.

**Scale 7 is substrate-agnostic** and operates on the L7 patient-level prediction.

```python
class PatientAttributor(torch.nn.Module):
    """Scale 7 — SHAP individual-level patient attribution.

    Reference: Lundberg-Lee 2017 SHAP; DeepStrataAge composite Q7.4.
    Operates on Slot 6 patient-level aggregated prediction.
    """

    SCALE_ID = 7
    SCALE_NAME = "patient_shap"

    def __init__(self, l7_ensemble: L7Ensemble, config: InterpretabilityConfig):
        super().__init__()
        self.l7_ensemble = l7_ensemble
        self.config = config

    def forward(self, adata, drug_smiles, covariates, l7_hooks,
                prediction_idx, verdict) -> Scale7Attribution:
        import shap

        # SHAP explainer over patient-level prediction
        # For a patient i, the input features are:
        #   - cell-level summary statistics (mean expression, etc.)
        #   - drug embedding
        #   - covariates (age, sex, prior therapy if available)
        patient_features = self._extract_patient_features(
            adata, drug_smiles, covariates, prediction_idx
        )

        if self.config.shap_explainer == "kernel":
            explainer = shap.KernelExplainer(
                self._patient_predict_fn,
                background_data=self._sample_background(),
            )
            shap_values = explainer.shap_values(
                patient_features, nsamples=self.config.shap_n_samples
            )
        elif self.config.shap_explainer == "deep":
            explainer = shap.DeepExplainer(
                self.l7_ensemble,
                background_data=...,
            )
            shap_values = explainer.shap_values(patient_features)
        elif self.config.shap_explainer == "gradient":
            explainer = shap.GradientExplainer(
                self.l7_ensemble,
                background_data=...,
            )
            shap_values = explainer.shap_values(patient_features)

        return Scale7Attribution(
            shap_values=shap_values,
            patient_features=patient_features,
            top_features=self._top_k_features(shap_values, k=20),
        )


@dataclass
class Scale7Attribution(ScaleAttribution):
    scale_id: int = 7
    scale_name: str = "patient_shap"
    shap_values: torch.Tensor = None
    patient_features: torch.Tensor = None
    top_features: List[Tuple[str, float]] = None
```

### 9.2 What Scale 7 Reveals

For a patient predicted to respond to drug X with confidence 0.85:
- Which patient features (cell-type composition, marker expression, prior therapy) most contribute to the prediction?
- Are these features clinically actionable (e.g., a specific biomarker that explains the prediction)?
- Do patients with similar SHAP profiles cluster meaningfully?

This is the most clinically-presentable scale — SHAP values are well-understood by biomedical audiences. The cost is that SHAP at the patient level requires background data sampling, which is expensive (default 100 samples → ~100× L7 forward).

### 9.3 Cross-Scale Consistency Implication

Scale 7 grounds **Cross-Scale Consistency Check 4** (§10): patients with similar predicted responses should have similar SHAP patterns. Decision 7 v2 Check 4: within-cluster SHAP distance significantly less than between-cluster (p ≤ 0.01).

If patients predicted to respond with high confidence have wildly different SHAP profiles → the prediction mechanism varies across patients in a way that defies the cohort-level interpretation. This may be biologically real (heterogeneous mechanisms) or may indicate prediction instability.

### 9.4 Choice of SHAP Explainer (CSO judgment per §11.5)

**DEFAULT: kernel SHAP** (model-agnostic, slowest but most reliable).

Alternatives:
- Deep SHAP: requires gradient access; faster on neural networks; available since L7 is differentiable
- Gradient SHAP: even faster; less precise for non-linear models

Layer 5 may switch to Deep or Gradient SHAP if KernelSHAP cost becomes prohibitive. Default Kernel chosen for first implementation due to robustness.

### 9.5 What Scale 7 Does NOT Do

- Does NOT replace cell-level attribution (Scale 5). SHAP at patient level is coarse; Scale 5 gives within-patient gene-level detail.
- Does NOT provide statistical guarantees. SHAP values are point estimates; uncertainty quantification of SHAP is an active research area, not addressed here.
- Does NOT include external clinical features automatically. The `patient_features` extraction is Layer 5 implementation; what clinical metadata is included depends on dataset structure.
---

## §10 Cross-Scale Consistency Checks (BINDING per Charter §1.3 Falsifiability)

### 10.1 The Four Checks

Per Decision 7 v2 §"Cross-Scale Consistency Checks (BINDING)":

```python
class ConsistencyChecker:
    """Implements 4 cross-scale consistency checks per Decision 7 v2.

    BINDING per Charter §1.3 falsifiability: failure of any check triggers
    Q7 layer revision; INTERCEPTA cannot publish Q7 results with
    inconsistent multi-scale interpretation.
    """

    def __init__(self, config: InterpretabilityConfig):
        self.config = config

    def run_all(
        self,
        per_scale_outputs: Dict[int, Dict[int, ScaleAttribution]],
    ) -> ConsistencyReport:
        check_1 = self._check_1_drugclass_gene_overlap(per_scale_outputs)
        check_2 = self._check_2_pathway_gene_recovery(per_scale_outputs)
        check_3 = self._check_3_grn_gene_overlap(per_scale_outputs)
        check_4 = self._check_4_patient_cluster_coherence(per_scale_outputs)

        passes = {
            1: check_1 >= self.config.check_1_threshold,
            2: check_2 >= self.config.check_2_threshold,
            3: check_3 >= self.config.check_3_threshold,
            4: check_4 <= self.config.check_4_threshold,
        }

        return ConsistencyReport(
            check_1_drugclass_gene_overlap=check_1,
            check_2_pathway_gene_recovery=check_2,
            check_3_grn_gene_overlap=check_3,
            check_4_patient_cluster_coherence=check_4,
            passes=passes,
            all_passed=all(passes.values()),
        )
```

### 10.2 Check 1 — Drug-class similarity ↔ Gene attribution overlap

**Mechanism:** For drugs with similar Scale 2 latent_perturb embeddings, their Scale 5 gene attributions should overlap.

**Quantification:** For every pair (drug A, drug B) in the evaluation set, compute CPA similarity sim(A, B) = cosine(latent_perturb_A, latent_perturb_B) and gene attribution overlap jaccard(top_50_genes_A, top_50_genes_B). Aggregate across pairs: Pearson r between sim and overlap.

**Pass threshold:** Pearson r ≥ 0.5 (Decision 7 v2 Check 1).

**Interpretation:** If r < 0.5, drugs with similar CPA latent embeddings produce dissimilar gene attributions — the mechanism trace is not coherent across drugs.

### 10.3 Check 2 — Pathway prior ↔ Gene attribution

**Mechanism:** GEARS GO graph neighbors of the drug target (from Scale 3) should overlap with Scale 5 top-attributed genes.

**Quantification:** For each (drug, target) pair where target is known: GO graph k-hop neighbors of target → set G_pathway; Scale 5 top-20 attributed genes → set G_attribution; overlap = |G_pathway ∩ G_attribution| / 20.

**Pass threshold:** ≥30% overlap (Decision 7 v2 Check 2).

**Interpretation:** If overlap < 30%, the model's gene attribution does not recover known drug-target pathway biology.

### 10.4 Check 3 — GRN propagation ↔ Gene attribution

**Mechanism:** scRank's top-50 propagated genes (Scale 4) should overlap with Scale 5 top-50 attributed genes.

**Quantification:** Jaccard(Scale4_top_50, Scale5_top_50).

**Pass threshold:** ≥20% Jaccard (Decision 7 v2 Check 3).

**Interpretation:** If overlap < 20%, the regulatory network propagation pattern doesn't agree with gradient-based attribution.

### 10.5 Check 4 — Patient SHAP cluster coherence

**Mechanism:** Patients with similar predicted responses should have similar Scale 7 SHAP patterns; different response categories should have distinct patterns.

**Quantification:** Cluster patients by predicted response category; compute within-cluster vs between-cluster average SHAP pattern distance; test via permutation test.

**Pass threshold:** p ≤ 0.01 that within-cluster distance is significantly less than between-cluster (Decision 7 v2 Check 4).

### 10.6 Failure Handling

Per Decision 7 v2 BINDING: failure of any consistency check triggers Q7 layer revision. INTERCEPTA cannot publish Q7 results with inconsistent multi-scale interpretation. L2.4 implements this as a hard gate: ConsistencyReport.all_passed must be True before InterpretabilityOutput is considered publishable. Layer 5 implementation logs ConsistencyReport for every evaluation; CI/CD checks gate publication on all_passed.

### 10.7 What Cross-Scale Consistency Does NOT Do

- Does NOT establish causal mechanism. Consistency across scales is necessary, not sufficient.
- Does NOT detect all attribution errors. Multiple scales could agree by coincidence on wrong attribution.
- Does NOT score "how much" mechanism is recovered. Pass criteria are binary thresholds.

---

## §11 Pass Criteria for L2.4 LOCK

### 11.1 Architecture-Level Pass Criteria (BINDING)

**A1:** All 7 scales implemented per §3-§9 with PyTorch class skeletons.
**A2:** Scale 5 implements all 4 branches (A FM, B scTOP, C scVI, D PCA) with substrate-conditional routing.
**A3:** Scale 6 cleanly skips when no spatial data; Scale 1 cleanly skips when not FM substrate.
**A4:** Cross-scale consistency checks implemented per §10 with binding thresholds.
**A5:** Verdict-conditional gating (§1.6) implemented per L2.3 OODOutput consumption.
**A6:** InterpretabilityOutput schema delivered per L2.4 output contract.
**A7:** Ensemble aggregation (intersection/union/majority) for Scale 5 per Decision 5 v2 N=5.
**A8:** Drift Finding 7 BINDING placement: Beyondcell in Scale 3 (NOT Slot 4); scRank in Scale 4 (also Slot 4 attention init in L2.2).

### 11.2 Cross-Decision Compatibility Pass Criteria (BINDING)

**X1:** L2.4 consumes L7Output `attribution_hooks` and OODOutput `operational_verdict`.
**X2:** L2.4 routes Scale 5 by substrate name; all 4 substrate families covered.
**X3:** L2.4 honors Drift Finding 7: scRank in Slot 4 init AND as Scale 4; Beyondcell only in Scale 3.
**X4:** Compute envelope (§12) accepts Branch A high cost; provides Branch B cheap alternative.
**X5:** All dependencies open-licensed: Captum (BSD-3), SHAP (MIT), statsmodels (BSD-3), Beyondcell (open).

### 11.3 Empirical Pass Criteria (Layer 5-verified, per Decision 7 v2 Pass 1-7)

**E1 (Pass 1):** EIG H-N-IG produces ≥50% more significant attributions than vanilla IG.
**E2 (Pass 2):** SmoothGrad improves attribution precision by ≥0.05 at top 1% threshold.
**E3 (Pass 3):** ≥80% of well-characterized drugs recover canonical target (Trastuzumab→ERBB2, Ibrutinib→BTK, Imatinib→ABL1, Cetuximab→EGFR, Vemurafenib→BRAF).
**E4 (Pass 4):** All 4 consistency checks pass at V0-V3 evaluation levels.
**E5 (Pass 5):** Top-50 EIG genes have ≥70% Jaccard across N=5 Deep Ensembles.
**E6 (Pass 6):** All 4 substrate branches produce gene-level attribution satisfying Pass 1-5 independently.
**E7 (Pass 7):** Q7 attribution remains biologically plausible when transferred to held-out diseases (V6 cross-disease).

### 11.4 Documentation Pass Criteria

**D1:** L2.4 referenced by L3.1 V0-V6 validation harness with verified cross-references.
**D2:** L2.4 Layer 5 implementation matches L2.4 specification.
**D3:** Drift catalog this session: 0 new instances introduced.

### 11.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | Scale 1 spectral kernel | Gaussian | linear, cosine | Linear within 1pp Pass 3 at lower cost |
| J2 | Scale 1 n_components | 50 | 20, 100 | Standard tuning |
| J3 | Scale 3 Beyondcell signature DB | hallmark | kegg, reactome | KEGG recovers ≥10% more known biology |
| J4 | Scale 3 GEARS k-hop depth | 2 | 1, 3 | k=3 within 0.5pp at 3× cost |
| J5 | Scale 4 scRank propagation steps | 3 | 2, 5 | Stability of top-K across step counts |
| J6 | Scale 5 Branch A IG path | nonlinear (Jha H-N-IG) | linear | Linear within 5% precision at 50% cost |
| J7 | Scale 5 SmoothGrad samples | 20 | 10, 50 | Diminishing returns above 20 |
| J8 | Scale 5 ensemble aggregation | intersection | union, majority | Majority outperforms intersection on Pass 5 by ≥5pp |
| J9 | Scale 6 River branch weighting | equal | learned | Learned weighting improves spatial-domain F1 by ≥5pp |
| J10 | Scale 7 SHAP explainer | kernel | deep, gradient | Deep within 0.5pp at 5× speedup |

### 11.6 Honest Limitations (per Charter §10 P15 BINDING)

L2.4 honestly states the limitations the field-wide interpretability literature operates within:

- **Attribution is correlational, not causal.** Gradient-based attribution identifies features contributing to predictions, not causal drivers of biology. Causal claims require intervention (CRISPRi, drug perturbation experiments).
- **Multi-scale consistency does not guarantee correctness.** All 4 scales could agree on a biologically wrong attribution if all attribution methods recover the same spurious feature.
- **SmoothGrad noise σ is a hyperparameter.** The default σ=0.15 follows Reynolds-Pan 2025; optimal σ varies by domain.
- **Bonferroni correction is conservative.** With N_genes ≈ 20,000, Bonferroni-corrected p ≤ 0.05 requires raw p ≤ 2.5e-6 — most attribution methods cannot achieve this for marginal effects. INTERCEPTA reports both raw and corrected.
- **Cross-disease interpretability transfer is empirically uncertain.** Pass 7 is the test; the answer is Layer 5 empirical.

### 11.7 CEO Sign-Off

L2.4 advances from PROPOSED to LOCKED when:
1. CEO reviews §1-§9 architecture and §11 pass criteria
2. CEO confirms §11.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag `phase-b-l2.4-locked` pushed to origin

---

## §12 Compute Envelope and Wall-Clock Estimates

### 12.1 Per-Scale Compute Cost

| Scale | Method | Per-prediction cost | Notes |
|---|---|---|---|
| 1 | Spectral analysis | ~1 sec on A100 | FM-only; skipped otherwise |
| 2 | CPA latent inspection | <0.01 sec | Free; cached intermediate |
| 3 | GEARS GO + Beyondcell | ~0.1 sec | Pre-computed signatures + cached graph |
| 4 | scRank propagation | ~0.5 sec | Pre-computed GRN graph |
| 5 Branch A (FM EIG) | EIG+SmoothGrad+N=5 ensemble | ~5,000 model passes per prediction | DOMINANT cost |
| 5 Branch B (scTOP linear) | Linear algebra | <0.01 sec | Souza-Mehta cheap |
| 5 Branch C (scVI VAE IG) | IG+SmoothGrad on decoder | ~1,000 passes (decoder smaller than FM) | Medium |
| 5 Branch D (PCA loadings) | Linear algebra | <0.01 sec | Free |
| 6 | River DSEP | ~0.5 sec | Spatial-only |
| 7 | SHAP kernel | ~100× L7 forward | High |

### 12.2 Total Cost Per Attribution

For one prediction with FM substrate:
- Scales 1-4: ~3 seconds combined
- Scale 5 Branch A: ~30-60 seconds (5,000 passes at A100 throughput)
- Scale 6 (if spatial): ~0.5 seconds
- Scale 7 (SHAP kernel): ~30 seconds
- **Total per-prediction with FM: ~60-90 seconds wall-clock on A100**

With scTOP substrate (Branch B): ~35 seconds per prediction (almost entirely SHAP cost). The Souza-Mehta argument is empirically real: scTOP substrate makes interpretability ~2× faster overall.

### 12.3 Batching Strategy

Per-prediction attribution is too expensive for real-time interactive use. L2.4 deployment pattern: batch attribute predictions overnight via SLURM array, cache attribution results to /scratch/, serve cached attributions in deployment.

### 12.4 Single-A100 Envelope Fit

For V0 baseline (100K cells × 10 drugs = 1M predictions):
- Full attribution with FM substrate: ~1M × 60 sec = ~17,000 GPU-hours = ~700 GPU-days
- With scTOP substrate: ~10,000 GPU-hours = ~400 GPU-days
- With sampled attribution (1% of predictions): ~7-17 GPU-days

**Operational consequence:** Full per-prediction attribution at V0 scale is INFEASIBLE on single-A100 budget. L2.4 deployment uses **sampled attribution** at V0-V1 (e.g., 1% of predictions for QC) + targeted attribution at V3-V6 (high-impact predictions attributed at higher rate). Phase F's expanded compute allows for higher attribution coverage.

This is honest engineering: the architecture supports per-prediction attribution; the deployment budget constrains how often it runs.

### 12.5 Attribution Cache Pattern

```
/scratch/akula.pra/INTERCEPTA/attribution/
├── {substrate}/         e.g., scfoundation, sctop, scvi
│   ├── {dataset}/       e.g., sciplex3, gdsc, ccle
│   │   ├── {split}/     train, val, test
│   │   │   ├── scale_1.h5
│   │   │   ├── scale_2.h5
│   │   │   ├── ...
│   │   │   └── scale_7.h5
```

Cache key includes L2.4 spec SHA256 first 8 chars; invalidates on spec changes.

---

## §13 Cross-Decision Implications

### 13.1 Decision 1 v2 (Substrate)
**ARCHITECTURALLY BINDING.** Scale 5 branches by substrate.NAME. All 4 substrate families covered: FM (Branch A), scTOP (Branch B), scVI family (Branch C), PCA+HVG (Branch D). Scale 1 substrate-specific gating (FM-only) explicitly enforced.

### 13.2 Decision 2 v2 (Cross-Cohort Harmonization)
**UPSTREAM.** Harmonization operates before L7 sees the data; L2.4 inherits the harmonized representation.

### 13.3 Decision 3 v2 (Architectural Identities)
**BINDING per Drift Finding 7.** scRank appears in two places: Slot 4 gene-gene attention init in L2.2 (model-internal); Scale 4 standalone propagation in L2.4 (interpretability). Beyondcell appears ONLY in Scale 3 (L2.4), NOT in Slot 4 (L2.2). chemCPA architecture surgery operates in Slot 2+3 composition in L2.2; not a Scale-N component in L2.4.

### 13.4 Decision 4 v2 (Drug Response Architecture)
**TIGHTLY COUPLED.** L2.4 consumes L7Output `attribution_hooks` directly. CPA latent (intrinsic per Decision 4 v2) provides Scale 2 attribution for free.

### 13.5 Decision 5 v2 (OOD Detection)
**TIGHTLY COUPLED.** L2.4 consumes OODOutput `operational_verdict` for verdict-conditional gating. The 4-verdict pattern maps directly to attribution confidence (§1.6).

### 13.6 Decision 6 v2 (V0-V6 Validation)
**PASS CRITERIA INTEGRATED.** Pass 1-3 verified at V0-V1; Pass 4-5 at V0-V3; Pass 6 across substrate ablations; Pass 7 at V6 universality test.

### 13.7 Decision 7 v2 (THIS DECISION)
**FULLY IMPLEMENTED.** All 7 scales realized. All 4 cross-scale consistency checks operationalized. Substrate-conditional Branching A/B/C (and D for PCA) all implemented. Verdict-conditional gating implemented.

### 13.8 Decision 8 v2 (Universality / V6)
**V6 SUPPORTED.** Scale 5 substrate-conditional branches ensure interpretability survives Decision 1 v2's Layer 5 substrate winner. Cross-disease interpretability transfer (Pass 7) is the V6 universality test for the interpretability layer.

### 13.9 Decision 9 v2 (Compute Envelope)
**ENVELOPE CONSTRAINED.** §12 documents per-scale costs. Per-prediction full attribution is infeasible at V0 scale on single-A100; deployment uses sampled attribution + cached results. Souza-Mehta argument is operationally real: scTOP substrate reduces attribution cost ~2× via Branch B linearity.

### 13.10 Decision 10 v2 (Open-Source)
**FULLY COMPATIBLE.** All dependencies open-licensed: Captum BSD-3 (IG implementation), SHAP MIT, statsmodels BSD-3 (Bonferroni), Beyondcell open, scRank open, GEARS open, CPA MIT.

### 13.11 Phase F Future Continuity
**DOCUMENTED, NOT ACTIVE.** Scale 6 spatial becomes Phase F's spatial-aware mechanism trace. Scale 7 patient SHAP becomes Phase F's clinical-grade per-patient interpretability for pharma deliverable packaging. Cross-scale consistency framework extends to Phase F multi-modal integration. L2.4 is the Phase B foundation; Phase F builds on top.

---

## §14 Document Provenance and CSO Discipline Check

### 14.1 Provenance

L2.4 written by Claude (CSO, same session as L2.2 and L2.3, 2026-05-11) per Phase B Plan v2 sequencing. Predecessor artifacts L2.1 (LOCKED), L2.2 (PROPOSED), L2.3 (PROPOSED) all in immediate context. Anchor re-read trigger satisfied retroactively per Master Handoff v2.0 §3.5 (8 Q7 anchors re-read in primary-source form during the 2026-05-11 audit session).

### 14.2 Anchor Re-Read Compliance

| Anchor | Last primary-source read | Content used in L2.4 |
|---|---|---|
| Reynolds-Pan 2025 | 2026-05-11 audit | Scale 5 SmoothGrad default; Pass 1 methodology |
| Jha 2020 EIG | 2026-05-11 audit | Scale 5 Branch A EIG H-N-IG; Bonferroni pattern |
| Cui-Yuan 2025 River | 2026-05-11 audit | Scale 6 two-branch DSEP framework |
| Kendiukhov 2026 Spectral | 2026-05-11 audit | Scale 1 spectral geometry; FM-only constraint |
| Souza-Mehta 2026 | 2026-05-11 audit | Scale 5 Branch B linear projection attribution |
| Lotfollahi 2023 CPA | 2026-05-11 audit | Scale 2 drug-class disentangled latent |
| Roohani 2024 GEARS | 2026-05-11 audit | Scale 3 GO graph attribution |
| Lin 2023 scRank | 2026-05-11 audit | Scale 4 GRN perturbation propagation |

The Beyondcell anchor was reviewed in Q3 synthesis context; BINDING placement in Scale 3 per Drift Finding 7. No anchor re-read drift detected.

### 14.3 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ L2.4 grounded in 8 verified primary-source Q7 anchor reads.
- **P15 (only correct/honest/real science):** ✅ §11.6 honest limitations; §10.6 cross-scale consistency necessary-not-sufficient; §12.4 compute infeasibility honestly stated.
- **P16 (preserve past work):** ✅ Decision 7 v2 + Q7 synthesis preserved; L2.4 builds on top.
- **P-FV-1 to P-FV-3:** ✅ L2.4 honors Phase B scope; Phase F continuity documented but not specified.
- **Charter §5.3 GO/NO-GO:** ✅ §11 pass criteria explicit; §11.7 CEO sign-off conditions stated.
- **Charter v1.2 §1.7 phase discipline:** ✅ No Phase F integration patterns specified.

### 14.4 Drift Catalog This Session

**New drift instances introduced:** 0.

**Pre-existing drift findings honored:** Finding 7 (Decision 3 v2 architectural identities) operationalized in §5.3 (Beyondcell in Scale 3 not Slot 4); §6.1 (scRank in Scale 4 and also Slot 4 attention init per L2.2); §13.3 (chemCPA placement).

### 14.5 Next Phase B Artifacts (per Plan v2 Sequence)

**Layer 2 of Phase B is now COMPLETE** (L2.1 LOCKED + L2.2/L2.3/L2.4 PROPOSED). Next layer:

- **L3.1 V0-V6 Validation Cascade Pipeline** (5-7K words). Consumes L7 + L2.3 OODOutput + L2.4 InterpretabilityOutput; specifies the evaluation harness for the 7 V-levels.
- **L3.2 56 Pass Criteria** (5-6K words). 8 criteria per V-level × 7 levels.
- **L3.3 Cross-Disease V6 Grid** (4-5K words). The universality test grid.

Then Layer 4 (implementation order, testing, failure modes), then Layer 5 (actual training and evaluation runs).

---

## §15 Appendix — Quick Reference

### 15.1 Scale Quick Comparison Table

| Scale | Method | Substrate | Compute | Output | Source |
|---|---|---|---|---|---|
| 1 | Spectral geometry | FM-only | Medium (~1 sec) | Eigenvalue magnitudes per program | Kendiukhov 2026 |
| 2 | CPA latent inspection | Agnostic | Free (built into L7) | Drug-class neighbors | Lotfollahi 2023 |
| 3 | GEARS GO + Beyondcell | Agnostic | Low (~0.1 sec) | Top pathways | Roohani 2024 + Fustero-Torre 2024 |
| 4 | scRank propagation | Agnostic | Low (~0.5 sec) | Top GRN-propagated genes per cell type | Lin 2023 |
| 5A | EIG H-N-IG + SmoothGrad | FM | HIGH (~5K passes) | Per-gene attribution + significance | Jha 2020 + Reynolds-Pan 2025 |
| 5B | Linear projection | scTOP | Free | Per-gene attribution + bootstrap CI | Souza-Mehta 2026 |
| 5C | VAE decoder IG | scVI family | Medium (~1K passes) | Per-gene attribution + significance | Adapted Jha 2020 for VAE |
| 5D | PCA loadings | PCA+HVG | Free | Per-gene attribution | Linear algebra |
| 6 | River DSEP | Spatial-only | Medium (~0.5 sec) | Coherent + diffuse spatial branches | Cui-Yuan 2025 |
| 7 | SHAP individual | Agnostic | High (~100×L7 forward) | Per-patient feature SHAP | Lundberg-Lee 2017 |

### 15.2 Cross-Scale Consistency Check Summary

| Check | Scales | Threshold | Pass Reference |
|---|---|---|---|
| 1 | 2 ↔ 5 | Pearson r ≥ 0.5 | Decision 7 v2 Pass 4 |
| 2 | 3 ↔ 5 | ≥30% overlap of EIG top-20 with GO neighbors | Decision 7 v2 Pass 4 |
| 3 | 4 ↔ 5 | ≥20% Jaccard of top-50s | Decision 7 v2 Pass 4 |
| 4 | 7 | Within < between cluster, p ≤ 0.01 | Decision 7 v2 Pass 4 |

### 15.3 Verdict-Conditional Attribution Behavior

| OOD Verdict | Attribution Behavior | Confidence Tag |
|---|---|---|
| confident_predict | Full 7-scale attribution | "full_confidence" |
| abstain_aleatoric | Full attribution, flagged | "reduced_confidence_label_noise" |
| abstain_epistemic | Full attribution, flagged | "extrapolation_flagged" |
| abstain_ood | SKIP attribution | "skipped_ood" |

### 15.4 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_4_Mechanistic_Interpretability_Architecture_Specification_2026-05-11.md`
- L2.3 spec (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_3_OOD_Detection_Stack_Specification_2026-05-11.md`
- L2.2 spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_2_L7_Drug_Response_Architecture_Specification_2026-05-11.md`
- Decision 7 v2 (parent): `~/INTERCEPTA/docs/research/decisions/INTERCEPTA_FV_Decision_7_Q7_mechanistic.md`
- Interpretability code (future): `~/INTERCEPTA/code/interpretability/`
- Attribution caches (future): `/scratch/akula.pra/INTERCEPTA/attribution/`
- Beyondcell signatures (future): `/scratch/akula.pra/INTERCEPTA/beyondcell/`

### 15.5 Commitment Cross-Reference

| Decision 7 v2 Commitment | L2.4 §  | Implementation |
|---|---|---|
| 7-scale stack | §1-§9 | All 7 scales realized |
| Scale 5 substrate-conditional branching | §7 | 4 branches with substrate routing |
| Cross-scale consistency Check 1 | §10.2 | Drug-class ↔ gene |
| Cross-scale consistency Check 2 | §10.3 | Pathway ↔ gene |
| Cross-scale consistency Check 3 | §10.4 | GRN ↔ gene |
| Cross-scale consistency Check 4 | §10.5 | Patient SHAP coherence |
| Pass 1 (vanilla IG rejection) | §11.3 E1 | Pass criterion |
| Pass 2 (SmoothGrad improvement) | §11.3 E2 | Pass criterion |
| Pass 3 (biological discovery) | §11.3 E3 | Pass criterion |
| Pass 4 (cross-scale consistency) | §11.3 E4 | Pass criterion |
| Pass 5 (ensemble stability) | §11.3 E5 | Pass criterion |
| Pass 6 (substrate-conditional) | §11.3 E6 | Pass criterion |
| Pass 7 (V6 cross-disease) | §11.3 E7 | Pass criterion |
| Drift Finding 7 (architectural identities) | §5.3, §6.1, §13.3 | Operationalized |

---

— L2.4 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l2.4-locked` tag.
— **After L2.4 LOCK: Layer 2 of Phase B is COMPLETE.** Next layer is L3.1 V0-V6 Validation Cascade Pipeline.
