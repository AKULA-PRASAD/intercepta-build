# INTERCEPTA Phase B Layer 2 — Artifact 2.3
## OOD Detection Stack Specification (Layers 5.1-5.4)

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** L2.1 Substrate Architecture Spec (LOCKED 2026-05-11), L2.2 L7 6-Slot Drug Response Architecture Spec (PROPOSED 2026-05-11)
**Parent decision:** Decision 5 v2 Q5 OOD Detection Stack (LOCKED)
**Co-bound decisions:** Decision 1 v2 (substrate posterior), Decision 2 v2 (scANVI/MrVI native uncertainty), Decision 4 v2 (L7 head as ensembled unit), Decision 6 v2 (V0-V6 pass criteria including Pass 1-4 OOD criteria), Decision 9 v2 (compute envelope), Decision 10 v2 (open-source)
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping:** Phase B OOD stack provides the calibrated uncertainty layer that Phase F's 6 Scouts will consume when their candidate molecules are evaluated by L7. Phase F adds A3 deployment-monitoring drift detection on top of Phase B's per-prediction OOD detection.
**Target length per Phase B Plan v2:** 8-10K words
**Filename:** `INTERCEPTA_FV_L2_3_OOD_Detection_Stack_Specification_2026-05-11.md`

---

## §0 Identification and Scope

### 0.1 What This Document Is

L2.3 is the **OOD Detection Stack Specification**. It is the third artifact of Phase B Layer 2 work. L2.3 specifies how INTERCEPTA quantifies predictive uncertainty and detects when L7's predictions cannot be trusted, by composing four explicit uncertainty layers (5.1 through 5.4) on top of the L7 6-slot drug response head defined in L2.2.

The four layers are: (5.1) Native Substrate Uncertainty as foundation; (5.2) Epistemic Refinement via N=5 Deep Ensembles default with MIMO8 and MC Dropout fallbacks; (5.3) Statistical-Guarantee Layer via conformal prediction; (5.4) Post-Hoc Energy Flag as fast pre-filter. The layer ordering and identities are LOCKED by Decision 5 v2. L2.3 specifies each layer's implementation contract, dimensions, default choices, fallback paths, and the pipeline integration that produces the binding Layer 5 Output Contract.

L2.3 also specifies the operational verdict logic — how the 4 layers' outputs combine into one of {confident_predict, abstain_aleatoric, abstain_epistemic, abstain_ood} — and the cross-disease conformal recalibration mechanism for V6.

### 0.2 What This Document Is Not

L2.3 is NOT:

- A Bayesian neural network specification. Decision 5 v2 explicitly rejected the "Bayesian Neural Networks from the start" alternative; INTERCEPTA's uncertainty comes from ensembles + conformal prediction + energy scoring, not from variational inference over weights.
- A drift-detection-over-time system. Per Charter v1.2 §1.6 reframe, A3 has TWO components: (a) cell-level epistemic drift detection per prediction (Phase B, L2.3) and (b) deployment-monitoring drift over time (Phase F). L2.3 covers (a) only.
- A clinical decision support system. The Layer 5 Output Contract produces structured uncertainty signals; how those signals are presented to clinicians is downstream of L2.3 (and out of charter scope per Charter v1.2 §4 row 6).
- A failure attribution system in the Decision 8 v2 F1-F7 sense. The F1-F7 taxonomy (Decision 8 v2 Commitment 4) attributes failures to causes (cross-resolution, cross-platform, cross-tissue, cross-species, drug-class OOD, disease-class OOD, patient population). L2.3 detects that a prediction is OOD; F1-F7 attribution happens in L3.x validation work.
- An interpretability tool. Decision 7 v2 (L2.4) consumes L7Output `attribution_hooks` to explain predictions. L2.3 tells you whether to trust the prediction; L2.4 tells you why the prediction was made. Different layers, different functions.

### 0.3 Phase B Plan v2 Compliance

Per Phase B Execution Plan v2 sequencing:

- Artifact 1 of Layer 2 (L2.1 Substrate Specification) → LOCKED 2026-05-11
- Artifact 2 of Layer 2 (L2.2 L7 Drug Response Architecture) → PROPOSED 2026-05-11
- **Artifact 3 of Layer 2 (this document, L2.3 OOD Detection Stack) → PROPOSED**
- Artifact 4 of Layer 2 (L2.4 Mechanistic Interpretability Architecture) → pending; depends on L2.3 OOD posterior for substrate-conditional attribution branching

L2.3 sits downstream of L2.2 (consumes L7Output and L7Ensemble) and upstream of L2.4 (provides OOD signal that L2.4 conditions interpretability on). The L2.3 output contract feeds L3.1 (V0-V6 validation cascade) and the future Layer 5 production deployment.

### 0.4 Anchor Re-Read Compliance

Per Phase B Plan v2 anchor re-read trigger, L2.3's anchor re-read trigger is SATISFIED. The 6 Q5 anchor papers were re-read in primary-source form during the 2026-05-11 corpus-read audit session. The anchors and the architectural commitments they ground:

| Anchor | Citation | L2.3 commitment grounded |
|---|---|---|
| **Theunissen 2025** | Theunissen et al. *Brief Bioinformatics* 26(3):bbaf239 | The only published OOD method benchmark on scRNA-seq data; informs the "OOD methods can identify severe data shifts, but not reliably" empirical caveat (§9 Pass criteria caveats); validates Deep Ensembles vs MC Dropout ordering for Layer 5.2 default |
| **López-De-Castro 2025** | López-De-Castro et al. *Bioinformatics* 41(10):btaf521 | Conformal prediction methodology for Layer 5.3; non-conformity measure choice; marginal vs conditional coverage trade-off |
| **Lakshminarayanan 2017** | NeurIPS 2017 | Deep Ensembles foundational method for Layer 5.2 default (N=5 standard) |
| **Gal & Ghahramani 2016** | ICML 2016 | MC Dropout fallback for Layer 5.2 compute-tight scenarios (T=50 forward passes); architectural constraint (dropout throughout network) |
| **Liu 2020 energy** | NeurIPS 2020 | Energy score E(x) = -T·log Σ exp(z_i/T) for Layer 5.4; post-hoc applicability to any pretrained classifier |
| **Engelmann 2022** | ICML 2022 Workshop | Atlas-level uncertainty quantification on HLCA establishes scArches WKNN inadequate; MIMO8 single-forward-pass alternative for Layer 5.2 fallback; aleatoric/epistemic decomposition operationalization |

No anchor re-read drift detected. All architectural commitments traceable to primary-source claims.

### 0.5 Document Conventions

- **BINDING** — a commitment that cannot be modified without a Decision Record amendment + CEO+CSO co-sign. Violation fails Pass Criteria.
- **DEFAULT** — a choice L2.3 makes for initial Layer 5 implementation; revisitable per §10.5 with documented empirical signal.
- **DEFERRED** — a question L2.3 does not lock; reserved for Layer 5 ablation per Decision 5 v2 "What Decision 5 Does NOT Decide."
- **PHASE F** — out of L2.3 scope; canonical for Phase F per Charter v1.2 §4.
- All code snippets are PyTorch 2.x. Conformal prediction implementation uses standard scipy + numpy; no proprietary dependencies.

---

## §1 The 4-Layer OOD Architecture Overview

### 1.1 Why a Stacked Architecture

Per Decision 5 v2: no single OOD detection method provides all four required properties simultaneously: (a) cheap inference, (b) statistical guarantees, (c) aleatoric/epistemic decomposition, (d) compatibility with arbitrary L7 head architectures. The stacked architecture composes four methods, each contributing one or more properties:

| Property | 5.1 Substrate Posterior | 5.2 Ensemble | 5.3 Conformal | 5.4 Energy |
|---|---|---|---|---|
| Cheap inference | ✓ | × | ✓ | ✓ (cheapest) |
| Statistical guarantee | × | × | ✓ | × |
| Aleatoric/epistemic decomposition | ✓ | ✓ (epistemic) | × | × |
| L7 head compatibility | ✓ (upstream) | ✓ | ✓ (post-hoc) | ✓ (post-hoc) |

The architecture stacks them in a pipeline so that the cheapest method (Layer 5.4 energy) acts as a fast pre-filter, the most rigorous method (Layer 5.3 conformal) wraps the prediction for statistical guarantee, and the decomposition (5.1 + 5.2) provides the aleatoric vs epistemic verdict that drives the operational decision.

### 1.2 The Stack Data Flow

```
            INPUT
              │
              ▼
   ┌─────────────────────┐
   │  L2.2 L7Ensemble    │
   │  (N=5 Deep Ensemble)│ ← This is Layer 5.2 itself,
   │  produces:          │   per Drift Finding 8 BINDING:
   │  - prediction       │   L7 head is ensembled unit
   │  - disagreement     │
   │  - logits per head  │
   └─────────────────────┘
              │
              ├──────────────┬──────────────┬──────────────┐
              │              │              │              │
              ▼              ▼              ▼              ▼
   ┌──────────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────┐
   │ Layer 5.1        │ │ Layer 5.2  │ │ Layer 5.3│ │ Layer 5.4  │
   │ Substrate        │ │ Epistemic  │ │ Conformal│ │ Energy     │
   │ Posterior        │ │ Refinement │ │ Wrapping │ │ Score      │
   │                  │ │            │ │          │ │            │
   │ from L2.1        │ │ ensemble   │ │ wraps    │ │ post-hoc   │
   │ substrate +      │ │ disagree-  │ │ prediction│ │ on logits │
   │ CPA disentangled │ │ ment       │ │ → set/    │ │ → binary  │
   │ latent           │ │            │ │   interval│ │   OOD flag│
   │                  │ │ aleatoric +│ │          │ │            │
   │ aleatoric +      │ │ epistemic  │ │ coverage │ │ E(x) > τ ? │
   │ epistemic (raw)  │ │ (refined)  │ │ 1-α      │ │            │
   └──────────────────┘ └────────────┘ └──────────┘ └────────────┘
              │              │              │              │
              └──────────────┴───┬──────────┴──────────────┘
                                 │
                                 ▼
                     ┌─────────────────────────────┐
                     │ Layer 5 Output Contract     │
                     │ - aleatoric_uncertainty     │
                     │ - epistemic_uncertainty     │
                     │ - energy_ood_flag           │
                     │ - conformal_set / interval  │
                     │ - operational_verdict       │
                     │   ∈ {confident_predict,     │
                     │      abstain_aleatoric,     │
                     │      abstain_epistemic,     │
                     │      abstain_ood}           │
                     └─────────────────────────────┘
                                 │
                                 ▼
                     downstream: L2.4 interpretability,
                                 L3.1 V0-V6 validation,
                                 deployment serving
```

### 1.3 The OODStack Module Interface

```python
class OODStack(torch.nn.Module):
    """The 4-layer OOD detection stack per Decision 5 v2.

    Wraps L2.2's L7Ensemble (which is itself Layer 5.2) and composes
    Layer 5.1 (substrate posterior), Layer 5.3 (conformal prediction),
    and Layer 5.4 (energy score) into the binding Layer 5 Output Contract.
    """

    def __init__(
        self,
        l7_ensemble: L7Ensemble,                # from L2.2; this IS Layer 5.2
        substrate_posterior: SubstratePosterior,  # Layer 5.1; see §2
        conformal_predictor: ConformalPredictor,  # Layer 5.3; see §4
        energy_scorer: EnergyScorer,              # Layer 5.4; see §5
        config: OODConfig,                        # hyperparameter bundle; see §1.5
    ):
        super().__init__()
        self.l7_ensemble = l7_ensemble
        self.substrate_posterior = substrate_posterior
        self.conformal_predictor = conformal_predictor
        self.energy_scorer = energy_scorer
        self.config = config

    def forward(
        self,
        adata: AnnData,
        drug_smiles: List[str],
        covariates: Covariates,
        return_individual_layer_outputs: bool = False,
    ) -> OODOutput:
        """Run the full 4-layer stack.

        Args:
            adata, drug_smiles, covariates: same as L7Ensemble inputs
            return_individual_layer_outputs: if True, also return raw
                outputs from each of 5.1, 5.2, 5.3, 5.4 for debugging
                and ablation analysis

        Returns:
            OODOutput per the binding Layer 5 Output Contract (§1.4)
        """
        # Run L7 ensemble (this is Layer 5.2)
        ensemble_out = self.l7_ensemble(
            adata, drug_smiles, covariates,
            return_individual_predictions=True,
        )
        # ensemble_out.mean: [N_patients, output_dim] aggregated prediction
        # ensemble_out.disagreement: [N_patients, output_dim] epistemic signal
        # ensemble_out.individual: [N_heads, N_patients, output_dim] for energy

        # Layer 5.1: substrate posterior (cheap; runs from L2.1 substrate)
        substrate_unc = self.substrate_posterior(
            adata, batch_key=covariates.batch_key,
        )
        # substrate_unc.aleatoric: [N_cells, 1]
        # substrate_unc.epistemic: [N_cells, 1]

        # Layer 5.4: energy score (fast pre-filter)
        # Compute on ensemble mean logits (or per-head logits averaged)
        energy_per_pred = self.energy_scorer(ensemble_out.individual)
        energy_ood_flag = (energy_per_pred > self.config.energy_threshold)

        # Layer 5.3: conformal prediction (only when energy_ood_flag is False;
        # for energy-OOD points, conformal coverage guarantee does not hold)
        # We still compute conformal output for ALL points, but for energy-OOD
        # points the operational verdict will prefer abstain_ood over the
        # conformal output. This preserves the pipeline's principled fail-safe
        # ordering.
        conformal_out = self.conformal_predictor(
            ensemble_out.mean,
            ensemble_out.disagreement,
        )
        # conformal_out.prediction_set: list of sets (classification)
        # or [N, 2] intervals (regression)
        # conformal_out.coverage_target: 1-α (e.g., 0.95)

        # Composite aleatoric / epistemic estimates
        # Aleatoric: from substrate posterior (5.1), aggregated to patient level
        # Epistemic: combination of substrate epistemic (5.1) and ensemble
        # disagreement (5.2). Per Decision 5 v2 + Engelmann 2022 decomposition,
        # both contribute to "model OOD-ness" and are summed (or maxed) per
        # the operational policy.
        aleatoric = _aggregate_substrate_aleatoric(
            substrate_unc.aleatoric, covariates.patient_id,
        )
        epistemic_substrate = _aggregate_substrate_epistemic(
            substrate_unc.epistemic, covariates.patient_id,
        )
        epistemic_ensemble = ensemble_out.disagreement.norm(dim=-1)  # [N_patients]
        epistemic = self._compose_epistemic(
            epistemic_substrate, epistemic_ensemble,
        )  # see §3.6 for composition rule

        # Operational verdict: §6 logic
        verdict = self._compute_operational_verdict(
            aleatoric=aleatoric,
            epistemic=epistemic,
            energy_ood_flag=energy_ood_flag,
            conformal_out=conformal_out,
        )

        return OODOutput(
            prediction=ensemble_out.mean,
            aleatoric_uncertainty=aleatoric,
            epistemic_uncertainty=epistemic,
            energy_ood_flag=energy_ood_flag,
            conformal_set=conformal_out.prediction_set,
            conformal_interval=conformal_out.prediction_interval,
            coverage_target=conformal_out.coverage_target,
            operational_verdict=verdict,
            individual_layer_outputs=_collect_individual(
                substrate_unc, ensemble_out, conformal_out, energy_per_pred,
            ) if return_individual_layer_outputs else None,
        )
```

### 1.4 The OODOutput Schema (BINDING — Layer 5 Output Contract)

```python
@dataclass
class OODOutput:
    """Binding Layer 5 Output Contract per Decision 5 v2.

    Consumed by Decision 6 v2 validation harness, Decision 7 v2 (L2.4)
    interpretability conditioning, and any downstream deployment.
    """

    prediction: torch.Tensor
        # [N_patients, output_dim] from L7Ensemble mean

    aleatoric_uncertainty: torch.Tensor
        # [N_patients, 1] in [0, 1] — biological/label noise per patient
        # aggregated from substrate posterior

    epistemic_uncertainty: torch.Tensor
        # [N_patients, 1] in [0, 1] — model out-of-distribution-ness
        # composition of substrate epistemic + ensemble disagreement

    energy_ood_flag: torch.Tensor
        # [N_patients, 1] boolean — fast pre-filter result

    conformal_set: Optional[List[Set[int]]]
        # classification: prediction set per patient with 1-α coverage
        # None for regression task

    conformal_interval: Optional[torch.Tensor]
        # regression: [N_patients, 2] [lower, upper] with 1-α coverage
        # None for classification task

    coverage_target: float
        # 1-α (e.g., 0.95) for the conformal output

    operational_verdict: List[str]
        # one of {"confident_predict", "abstain_aleatoric",
        #         "abstain_epistemic", "abstain_ood"} per patient

    individual_layer_outputs: Optional[Dict[str, torch.Tensor]]
        # raw per-layer outputs for ablation analysis; None at production
```

This output schema is BINDING per Decision 5 v2 "Layer 5 Output Contract." Modifications require Decision Record amendment.

### 1.5 The OODConfig Hyperparameter Bundle

```python
@dataclass
class OODConfig:
    """OOD stack hyperparameter configuration."""

    # Layer 5.1 — substrate posterior
    substrate_posterior_strategy: str = "decision1_substrate_native"
        # "decision1_substrate_native": use substrate's native posterior
        #   (scANVI/MrVI for Baseline C; scFoundation deterministic for FM;
        #    scTOP deterministic for Baseline B; PCA deterministic for A)
        # "kde_in_latent": kernel density estimation over training-set
        #   embeddings as fallback for deterministic substrates

    # Layer 5.2 — epistemic refinement (configured via L7Ensemble)
    # ensemble_n is in L7Config per L2.2 §1.5; OODConfig does not duplicate

    epistemic_fallback: str = "mimo8"
        # If L7Ensemble compute budget exceeded: "mimo8" (Engelmann 2022)
        # or "mc_dropout" (T=50 forward passes per Gal 2016)

    mc_dropout_T: int = 50  # forward passes if fallback to MC Dropout

    # Layer 5.3 — conformal prediction
    conformal_alpha: float = 0.05  # 95% coverage target
    conformal_nonconformity: str = "softmax"
        # "softmax": 1 - p(y_true | x); standard CP for classification
        # "absolute_error": |y_pred - y_true|; standard CP for regression
        # "studentized": (y_pred - y_true) / ensemble_std; uncertainty-aware
    conformal_taxonomy: str = "standard"
        # "standard" (López-De-Castro variant 1): single threshold across classes
        # "classwise" (variant 2): per-class threshold; better for class imbalance
        # "cluster" (variant 3): cluster-aware; harder to implement; for V6

    # Layer 5.4 — energy score
    energy_temperature: float = 1.0  # T in E(x) = -T·log Σ exp(z_i/T)
    energy_threshold: float = 0.0
        # Calibrated on held-out OOD data; 0.0 is placeholder

    # Composite verdict logic (§6)
    aleatoric_abstain_threshold: float = 0.7  # if >0.7 → abstain_aleatoric
    epistemic_abstain_threshold: float = 0.7  # if >0.7 → abstain_epistemic
    epistemic_composition: str = "max"
        # "max": max(substrate_epistemic, ensemble_disagreement)
        # "sum": substrate_epistemic + ensemble_disagreement
        # "learned": learned linear combination

    # Cross-disease conformal recalibration (V6)
    crossdisease_recalibration_enabled: bool = True
    crossdisease_min_calibration_samples: int = 50
        # below this, conformal guarantees flagged as unreliable

    # Compute envelope (Decision 9 v2)
    device: str = "cuda:0"
    batch_size: int = 1024
```

All defaults documented as Layer-5-revisitable per §10.5.

### 1.6 What the Architecture Does Not Specify

Per Decision 5 v2 "What Decision 5 Does NOT Decide":

- Whether to deploy Layer 5.2 default (Deep Ensembles N=5) vs fallbacks (MIMO8 or MC Dropout); this is a per-deployment compute envelope decision (Decision 9 v2)
- Specific non-conformity measure within the 3 López-De-Castro variants
- Specific energy threshold (calibrated on held-out data; depends on substrate and dataset)
- Specific verdict policy weights (CSO defaults documented in §6.5; Layer 5 ablation tunes)

---

## §2 Layer 5.1 — Native Substrate Uncertainty (FOUNDATION)

### 2.1 The Layer 5.1 Contract

Layer 5.1 derives aleatoric and epistemic uncertainty estimates from the cell-encoder substrate (Decision 1 v2 / L2.1) and the CPA disentangled latent (intrinsic to L7 / L2.2). It is the cheapest layer: zero marginal compute beyond the L2.1 substrate forward pass + CPA latent computation.

The contract is:

```python
class SubstratePosterior(torch.nn.Module, ABC):
    """Layer 5.1 — native uncertainty from Decision 1 v2 substrate posterior."""

    NAME: str = "abstract"

    @abstractmethod
    def forward(
        self,
        adata: AnnData,
        batch_key: str,
    ) -> SubstrateUncertainty:
        """Returns per-cell aleatoric and epistemic uncertainty."""
        raise NotImplementedError


@dataclass
class SubstrateUncertainty:
    aleatoric: torch.Tensor   # [N_cells, 1] in [0, 1]
    epistemic: torch.Tensor   # [N_cells, 1] in [0, 1]
```

### 2.2 Substrate-Specific Implementations

Because Decision 1 v2 commits to substrate flexibility, Layer 5.1 must implement different uncertainty extraction strategies per substrate family:

**scVI / scANVI / MrVI (Baseline C — probabilistic VAE):**

These substrates produce native posterior distributions over the latent space. Aleatoric and epistemic uncertainty extracted directly per Smith & Gal 2018 decomposition:

```python
class SCVIPosterior(SubstratePosterior):
    """Layer 5.1 for scVI / scANVI / MrVI substrates."""
    NAME = "scvi_native"

    def __init__(self, substrate: SubstrateInterface, n_posterior_samples: int = 50):
        super().__init__()
        if substrate.NAME not in ("scvi", "scanvi", "mrvi"):
            raise ValueError(f"SCVIPosterior incompatible with {substrate.NAME}")
        self.substrate = substrate
        self.n_samples = n_posterior_samples

    def forward(self, adata, batch_key):
        # Sample N posterior samples per cell from scVI's latent
        # (scvi-tools API: model.get_latent_representation(give_mean=False, ...))
        samples = []
        for _ in range(self.n_samples):
            z = self.substrate.encode(adata, batch_key=batch_key, sample=True)
            samples.append(z)
        samples = torch.stack(samples, dim=0)  # [n_samples, N_cells, latent_dim]

        # Aleatoric: mean variance across samples
        mean_z = samples.mean(dim=0)
        var_z = samples.var(dim=0)  # [N_cells, latent_dim]
        aleatoric = var_z.mean(dim=-1, keepdim=True)  # [N_cells, 1]
        aleatoric = torch.sigmoid(aleatoric)  # normalize to [0, 1]

        # Epistemic: distance from training-set posterior support
        # Use KDE over training-set posterior means as a proxy
        epistemic = self._kde_distance(mean_z)  # [N_cells, 1]

        return SubstrateUncertainty(aleatoric=aleatoric, epistemic=epistemic)
```

**scFoundation / UCE / scGPT / Geneformer (Paradigm A — Foundation Models):**

These substrates are deterministic at inference (no native posterior). Layer 5.1 uses KDE over the training-set embedding distribution to estimate epistemic uncertainty, and uses CPA disentangled latent variance as the aleatoric proxy.

```python
class FMDeterministicPosterior(SubstratePosterior):
    """Layer 5.1 for foundation model substrates (deterministic at inference).

    Epistemic uncertainty estimated via KDE on training-set embeddings.
    Aleatoric uncertainty estimated via CPA disentangled latent variance
    over the covariate-marginalized posterior.
    """
    NAME = "fm_deterministic"

    def __init__(
        self,
        substrate: SubstrateInterface,
        training_embeddings_path: str,
        kde_bandwidth: float = 0.1,
    ):
        super().__init__()
        self.substrate = substrate
        # Load training set embeddings for KDE reference
        self.training_emb = self._load_training_embeddings(training_embeddings_path)
        # KDE built once at instantiation
        from sklearn.neighbors import KernelDensity
        self.kde = KernelDensity(bandwidth=kde_bandwidth, kernel="gaussian")
        self.kde.fit(self.training_emb)

    def forward(self, adata, batch_key):
        # Get substrate canonical embedding (deterministic; no sampling)
        cell_emb_native = self.substrate.encode(adata, batch_key=batch_key)
        cell_emb = self.substrate.project_to_canonical(cell_emb_native)

        # Epistemic: -log p(cell_emb | training_distribution) per KDE
        log_density = self.kde.score_samples(cell_emb)  # [N_cells]
        # Normalize to [0, 1]: higher = more OOD (lower density)
        epistemic = self._normalize_density_to_unc(log_density)
        epistemic = epistemic.unsqueeze(-1)

        # Aleatoric: variance of CPA-disentangled latent over covariate marginal
        # (Layer 5 implementation detail; placeholder here)
        aleatoric = self._cpa_aleatoric(cell_emb)

        return SubstrateUncertainty(aleatoric=aleatoric, epistemic=epistemic)
```

**scTOP (Baseline B — parameter-free):**

scTOP is deterministic by construction (zero free parameters). Aleatoric uncertainty derived from the projection-coefficient distribution; epistemic uncertainty derived from cosine distance to the nearest reference cell type basis vector.

```python
class SCTOPPosterior(SubstratePosterior):
    """Layer 5.1 for scTOP parameter-free substrate.

    Epistemic uncertainty from cosine distance to reference basis;
    aleatoric from softmax entropy over reference projections.
    """
    NAME = "sctop_native"

    def __init__(self, substrate: SubstrateInterface):
        super().__init__()
        if substrate.NAME != "sctop":
            raise ValueError(...)
        if substrate.NATIVE_DIM < 0:
            raise RuntimeError(
                "scTOP substrate not initialized. Call fit() or load_pretrained() "
                "before constructing SCTOPPosterior. (L2.1 Finding 6 BINDING.)"
            )
        self.substrate = substrate

    def forward(self, adata, batch_key):
        # scTOP encode produces projection coefficients [N_cells, n_celltypes]
        projections = self.substrate.encode(adata, batch_key=batch_key)
        projections = torch.from_numpy(projections)

        # Aleatoric: softmax entropy over projections
        # High entropy = uncertain about which cell type
        sm = F.softmax(projections, dim=-1)
        ent = -(sm * sm.clamp_min(1e-9).log()).sum(dim=-1, keepdim=True)
        # Normalize to [0, 1] by max possible entropy = log(n_celltypes)
        aleatoric = ent / torch.tensor(projections.shape[-1]).log()

        # Epistemic: 1 - max projection magnitude
        # Low max projection = cell is far from any reference type
        max_proj = projections.max(dim=-1, keepdim=True).values
        epistemic = (1.0 - torch.sigmoid(max_proj)).clamp(0, 1)

        return SubstrateUncertainty(aleatoric=aleatoric, epistemic=epistemic)
```

**PCA+HVG (Baseline A — classical):**

```python
class PCAPosterior(SubstratePosterior):
    """Layer 5.1 for PCA+HVG classical substrate.

    Epistemic via reconstruction error from PCA basis;
    aleatoric via per-cell explained variance ratio.
    """
    NAME = "pca_native"
    ...
```

### 2.3 The Substrate-Conditional Branching Pattern

L2.3 inherits the substrate-conditional branching pattern from Decision 7 v2 §3.2 (which L2.4 will operationalize for attribution). For Layer 5.1, the branching is:

```python
class SubstratePosteriorRegistry:
    """Routes substrate → appropriate Layer 5.1 implementation."""

    _map = {
        "scvi": SCVIPosterior,
        "scanvi": SCVIPosterior,
        "mrvi": SCVIPosterior,
        "scfoundation": FMDeterministicPosterior,
        "uce": FMDeterministicPosterior,
        "scgpt": FMDeterministicPosterior,
        "geneformer": FMDeterministicPosterior,
        "sctop": SCTOPPosterior,
        "pca_hvg": PCAPosterior,
    }

    @classmethod
    def build(cls, substrate: SubstrateInterface, **kwargs) -> SubstratePosterior:
        if substrate.NAME not in cls._map:
            raise ValueError(
                f"No Layer 5.1 implementation for substrate {substrate.NAME}. "
                f"Add to SubstratePosteriorRegistry."
            )
        return cls._map[substrate.NAME](substrate, **kwargs)
```

The L7Ensemble's substrate is shared across all 5 heads, so the Layer 5.1 posterior is computed **once** per (cell, batch) and shared across the ensemble's predictions.

### 2.4 KDE Cache Pattern

For FM-deterministic substrates, KDE construction over training embeddings is expensive at scale (50K+ training cells). KDE objects are cached after fit:

```
/scratch/akula.pra/INTERCEPTA/kde/
├── scfoundation_ccle_kde_bw0.1.pkl
├── scfoundation_sciplex_kde_bw0.1.pkl
├── uce_ccle_kde_bw0.1.pkl
└── ...
```

Cache key: `(substrate_name, training_set_name, kde_bandwidth)`.

### 2.5 What Layer 5.1 Does NOT Do

- Does NOT compute per-prediction uncertainty over (cell, drug) pairs. Layer 5.1 operates at the cell level, before any drug is considered. Per-(cell, drug) uncertainty comes from composition with Layer 5.2 (L7 ensemble disagreement is per-prediction).
- Does NOT distinguish "biological noise" from "label noise." The aleatoric estimate captures both as a single signal.
- Does NOT calibrate uncertainty. Calibration is Layer 5.3 (conformal prediction); 5.1 produces raw uncertainty estimates that 5.3 wraps with statistical guarantees.
- Does NOT use the L7 head. It runs from L2.1 substrate output directly.

---

## §3 Layer 5.2 — Epistemic Refinement (THE L7 ENSEMBLE)

### 3.1 The Layer 5.2 Contract

Per Decision 5 v2 + Drift Finding 8 BINDING: Layer 5.2 IS the L2.2 L7Ensemble. The L7 head is the ensembled unit (substrate + drug encoder shared across N=5 heads; Slots 3-6 independent). L2.3 does not redefine the ensemble; it consumes its output.

### 3.2 Composition with L2.2

L2.3 takes the L7Ensemble's `ensemble_out` and routes:
- `ensemble_out.mean` → main prediction passed through to OODOutput
- `ensemble_out.disagreement` → epistemic uncertainty signal
- `ensemble_out.individual` → per-head logits for energy score computation in Layer 5.4

```python
# In OODStack.forward (§1.3):
ensemble_out = self.l7_ensemble(
    adata, drug_smiles, covariates,
    return_individual_predictions=True,
)
```

The `return_individual_predictions=True` is BINDING — Layer 5.4 needs per-head logits, not just the aggregated mean.

### 3.3 The Default Path: N=5 Deep Ensembles

Per Lakshminarayanan 2017 + Decision 5 v2 Layer 5.2 default:

- N=5 independently-trained L7 heads
- Each with different random seed (parameter init + mini-batch shuffling)
- Substrate (Slot 1) + drug encoder (Slot 2) shared (frozen) across heads
- Slots 3-6 trained independently per head
- Disagreement (per-prediction standard deviation across the 5 heads) is the epistemic uncertainty signal

This is the BINDING default per Decision 5 v2 when compute permits.

### 3.4 Fallback Path: MIMO8

Per Engelmann 2022 Q5 anchor + Decision 5 v2 fallback option:

MIMO (Multi-Input Multi-Output) with M=8 subnetworks. Single network architecture with M-way input-output channels that implicitly trains M sub-networks. Single forward pass; ~1.5× parameters of standard classifier.

```python
class MIMO8Refinement(torch.nn.Module):
    """MIMO8 fallback for Layer 5.2 when N=5 Deep Ensembles compute exceeds budget.

    Reference: Havasi et al. 2021, used by Engelmann 2022 on HLCA.

    NOTE: MIMO requires retraining the L7 head with M-way input-output
    channels; it is NOT a wrapper around an existing trained L7. Selection
    of MIMO8 over Deep Ensembles is a training-time decision, not inference.
    """

    NAME = "mimo8"
    M_SUBNETS = 8

    def __init__(self, l7_head: L7DrugResponseHead):
        super().__init__()
        # ... MIMO architectural surgery (Layer 5 implementation detail) ...

    def forward(self, adata, drug_smiles, covariates):
        # Single forward pass; produces M-way prediction distribution
        # Per-prediction disagreement extracted from the M outputs
        ...
```

### 3.5 Further Fallback: MC Dropout T=50

Per Gal & Ghahramani 2016 + Decision 5 v2 further fallback:

Standard L7 head with dropout active at inference; T=50 stochastic forward passes; variance/entropy = uncertainty.

```python
class MCDropoutRefinement(torch.nn.Module):
    """MC Dropout fallback for Layer 5.2 when latency permits but training
    compute does not (single trained model, T=50 inference passes).

    Trade-off: 1× training (cheapest), 50× inference latency (most expensive
    inference). Used when ensemble training infeasible.

    Theunissen 2025: MC Dropout outperformed by Deep Ensembles on most
    scRNA-seq OOD tasks. Use only when Deep Ensembles infeasible.
    """

    NAME = "mc_dropout"
    T = 50

    def __init__(self, l7_head: L7DrugResponseHead, T: int = 50):
        super().__init__()
        self.l7_head = l7_head
        self.T = T

    def forward(self, adata, drug_smiles, covariates):
        # Set dropout layers to train mode (active); model is in eval mode
        # except for dropout
        _enable_dropout(self.l7_head)
        outputs = []
        for _ in range(self.T):
            out = self.l7_head(adata, drug_smiles, covariates)
            outputs.append(out.prediction)
        stacked = torch.stack(outputs)  # [T, N, output_dim]
        mean = stacked.mean(dim=0)
        std = stacked.std(dim=0)
        return EnsembleOutput(mean=mean, std=std, disagreement=std, individual=stacked)
```

### 3.6 The Epistemic Composition Rule

The OODOutput's `epistemic_uncertainty` is composed from two signals:
- `epistemic_substrate` from Layer 5.1 (substrate-level OOD-ness)
- `epistemic_ensemble` from Layer 5.2 (prediction-level disagreement)

Default composition: `max(epistemic_substrate, epistemic_ensemble)` per OODConfig.epistemic_composition. This is conservative — a cell flagged as substrate-OOD OR prediction-disagreement-OOD gets the larger epistemic value.

Alternative compositions:
- `sum`: additive; over-counts when both signals are high
- `learned`: linear combination with weights learned on a held-out set

Default `max` chosen for honesty: better to over-flag epistemic uncertainty than under-flag. §10.5 J3 documents revisitability.

### 3.7 What Layer 5.2 Does NOT Do

- Does NOT replace Layer 5.1. Substrate posterior and ensemble disagreement are complementary signals; Layer 5.2 specifically captures L7 head uncertainty over the prediction, not over the substrate.
- Does NOT provide statistical guarantees. Ensemble disagreement is a heuristic, not a coverage guarantee. Layer 5.3 (conformal) provides the guarantee.
- Does NOT distinguish "model is uncertain" from "ensemble disagrees." Per Lakshminarayanan 2017, these are operationally the same; we use ensemble disagreement as a proxy for epistemic uncertainty without claiming it is exactly Bayesian model uncertainty.
---

## §4 Layer 5.3 — Statistical-Guarantee Layer (CONFORMAL PREDICTION)

### 4.1 The Layer 5.3 Contract

Conformal prediction wraps L7's point predictions with prediction sets (classification) or prediction intervals (regression) carrying a distribution-free coverage guarantee 1-α. Per López-De-Castro 2025 + Decision 5 v2 Layer 5.3.

```python
class ConformalPredictor(torch.nn.Module, ABC):
    """Layer 5.3 — conformal prediction with 1-α coverage guarantee."""

    NAME: str = "abstract"

    @abstractmethod
    def fit(
        self,
        calibration_predictions: torch.Tensor,
        calibration_targets: torch.Tensor,
        calibration_uncertainty: Optional[torch.Tensor] = None,
    ) -> None:
        """Fit conformal scores on calibration set."""
        raise NotImplementedError

    @abstractmethod
    def forward(
        self,
        predictions: torch.Tensor,
        uncertainty: Optional[torch.Tensor] = None,
    ) -> ConformalOutput:
        """Predict prediction set / interval per input."""
        raise NotImplementedError


@dataclass
class ConformalOutput:
    prediction_set: Optional[List[Set[int]]]  # classification
    prediction_interval: Optional[torch.Tensor]  # regression [N, 2]
    coverage_target: float
```

### 4.2 The Conformal Prediction Mechanism

For classification with N classes and target coverage 1-α:

1. **Calibration phase:**
   - Take held-out calibration set (X_cal, y_cal) with known labels
   - Compute non-conformity score s_i = nonconformity(f(x_i), y_i) for each calibration point
   - Sort scores; find empirical (1-α) quantile q̂

2. **Inference phase:**
   - For each test point x*, compute scores s_y* = nonconformity(f(x*), y) for each candidate class y
   - Prediction set = {y : s_y* ≤ q̂}
   - **Coverage guarantee:** P(y_true ∈ prediction_set) ≥ 1 - α (under exchangeability of calibration and test data)

For regression: prediction interval is [f(x*) - q̂, f(x*) + q̂] (or studentized variant).

### 4.3 Three Non-Conformity Measures (Per López-De-Castro 2025)

```python
class SoftmaxNonconformity:
    """Standard CP for classification.
    s(x, y) = 1 - softmax(f(x))[y]
    """
    def __call__(self, logits, target):
        return 1 - F.softmax(logits, dim=-1).gather(1, target.unsqueeze(1)).squeeze(1)


class AbsoluteErrorNonconformity:
    """Standard CP for regression.
    s(x, y) = |f(x) - y|
    """
    def __call__(self, pred, target):
        return torch.abs(pred - target)


class StudentizedNonconformity:
    """Uncertainty-aware CP. Tighter intervals for confident predictions.
    s(x, y) = |f(x) - y| / ensemble_std(x)
    
    INTERCEPTA-relevant: leverages L7Ensemble disagreement (5.2) to produce
    tighter intervals when ensemble agrees, wider when ensemble disagrees.
    This is the principled composition of Layer 5.2 and 5.3.
    """
    def __init__(self, eps=1e-3):
        self.eps = eps
    def __call__(self, pred, target, ensemble_std):
        return torch.abs(pred - target) / (ensemble_std + self.eps)
```

**DEFAULT: Studentized non-conformity** (CSO judgment per §10.5 J5).

Rationale:
1. Studentized scores integrate Layer 5.2 ensemble disagreement directly into Layer 5.3 — the two layers compose principled rather than parallel.
2. Tighter intervals on confident predictions improve clinical utility (smaller "what should we do?" set).
3. Maintains the 1-α coverage guarantee (per López-De-Castro 2025 — variant tested empirically).

Alternatives revisitable per §10.5: Softmax (classification standard), Absolute error (simplest), Cluster-aware (López-De-Castro variant 3 — defer to V6 ablation).

### 4.4 Three Taxonomies (Per López-De-Castro 2025)

```python
class StandardConformalPredictor(ConformalPredictor):
    """Variant 1 — single threshold across all classes / regression range."""
    NAME = "standard"

    def fit(self, cal_pred, cal_target, cal_unc=None):
        scores = self.nonconformity(cal_pred, cal_target, cal_unc)
        n = len(scores)
        # Empirical (1-α) quantile with finite-sample correction:
        q_idx = int(np.ceil((n + 1) * (1 - self.alpha))) - 1
        self.q_hat = torch.sort(scores).values[q_idx]
        self._fitted = True

    def forward(self, pred, unc=None):
        # ... construct prediction set / interval using q_hat ...
        ...


class ClasswiseConformalPredictor(ConformalPredictor):
    """Variant 2 — per-class threshold; better for class imbalance.
    
    For each class c, fit q̂_c from class-c calibration samples only.
    """
    NAME = "classwise"
    ...


class ClusterConformalPredictor(ConformalPredictor):
    """Variant 3 — cluster-aware. Groups similar inputs and uses cluster-
    specific thresholds. Defer to V6 ablation when reference cluster
    structure available.
    """
    NAME = "cluster"
    ...
```

**DEFAULT: Standard conformal predictor with studentized non-conformity** (CSO judgment per §10.5 J5).

Alternatives revisitable: Classwise (better when class imbalance is severe; L2.3 default for V5 clinical retrospective with imbalanced responder/non-responder ratios; revisited at V6).

### 4.5 Cross-Disease Conformal Recalibration (V6 BINDING)

Per Decision 5 v2 + Charter §1.1 universality test:

> "For held-out diseases, the calibration set requirement is non-trivial.
> INTERCEPTA commitment: when small labeled samples from a new disease
> become available, perform cross-disease conformal recalibration. If
> no labeled samples available: report uncertainty without statistical
> guarantees and flag this explicitly."

L2.3 implements this commitment as a recalibration protocol:

```python
class CrossDiseaseRecalibrationManager:
    """Manages conformal recalibration across diseases for V6 universality."""

    def __init__(
        self,
        base_predictor: ConformalPredictor,
        min_samples: int = 50,
    ):
        self.base = base_predictor
        self.min_samples = min_samples
        self._recalibrated_predictors: Dict[str, ConformalPredictor] = {}

    def maybe_recalibrate(
        self,
        disease_id: str,
        new_calibration_predictions: torch.Tensor,
        new_calibration_targets: torch.Tensor,
        new_calibration_uncertainty: Optional[torch.Tensor] = None,
    ) -> ConformalPredictor:
        """If enough labeled samples available for this disease, recalibrate.
        Otherwise, return base predictor with a flag that guarantees
        are not honored for this disease.
        """
        n = len(new_calibration_targets)
        if n < self.min_samples:
            return self.base  # caller should flag coverage unreliable

        # Clone base predictor and recalibrate on disease-specific samples
        recalibrated = copy.deepcopy(self.base)
        recalibrated.fit(
            new_calibration_predictions,
            new_calibration_targets,
            new_calibration_uncertainty,
        )
        self._recalibrated_predictors[disease_id] = recalibrated
        return recalibrated

    def get_predictor(self, disease_id: str) -> Tuple[ConformalPredictor, bool]:
        """Returns (predictor, has_recalibrated_guarantee).
        
        If has_recalibrated_guarantee is False, the 1-α coverage cannot
        be claimed for this disease's predictions.
        """
        if disease_id in self._recalibrated_predictors:
            return self._recalibrated_predictors[disease_id], True
        return self.base, False
```

The `has_recalibrated_guarantee` flag is propagated to OODOutput. When False, the conformal_set / conformal_interval is computed but the `coverage_target` is reported as "unreliable for held-out disease" rather than 1-α. This is the honest-science discipline Charter v1.2 P15 BINDING requires.

### 4.6 What Layer 5.3 Does NOT Do

- Does NOT provide conditional coverage. Conformal coverage is marginal (over the joint distribution), not conditional on any specific subgroup. Pathologically, a model can achieve marginal coverage by being overconfident on common cases and underconfident on rare cases. Layer 5.3 does NOT correct for this; flagged explicitly in §10.6 limitations.
- Does NOT replace Layer 5.2 disagreement signal. Studentized non-conformity uses ensemble disagreement as the scale; Layer 5.3 augments rather than replaces.
- Does NOT recalibrate automatically. The recalibration manager requires explicit calibration data per new disease. Auto-recalibration (online learning) is Phase F per Charter v1.2 §1.6 A2.

---

## §5 Layer 5.4 — Post-Hoc Energy Flag (FAST PRE-FILTER)

### 5.1 The Layer 5.4 Contract

Per Liu 2020 + Decision 5 v2 Layer 5.4:

Energy score E(x) = -T · log Σ exp(z_i / T) on L7 logits. Cheap (one log-sum-exp per prediction). No retraining required. Post-hoc applicable to any pretrained classifier.

```python
class EnergyScorer(torch.nn.Module):
    """Layer 5.4 — energy-based OOD detection per Liu et al. 2020."""

    NAME = "energy"

    def __init__(self, temperature: float = 1.0, threshold: float = 0.0):
        super().__init__()
        self.T = temperature
        self.threshold = threshold

    def forward(self, individual_logits: torch.Tensor) -> torch.Tensor:
        """
        Args:
            individual_logits: [N_heads, N_patients, output_dim] from L7Ensemble
        Returns:
            energy: [N_patients, 1] per-prediction energy score
        """
        # Average logits across ensemble heads (or use any aggregator)
        avg_logits = individual_logits.mean(dim=0)  # [N_patients, output_dim]
        # Energy score: -T·log Σ exp(z_i / T)
        # numerically stable via logsumexp
        energy = -self.T * torch.logsumexp(avg_logits / self.T, dim=-1, keepdim=True)
        return energy  # [N_patients, 1]

    def calibrate_threshold(
        self,
        in_dist_energies: torch.Tensor,
        target_in_dist_recall: float = 0.95,
    ) -> None:
        """Calibrate energy_threshold from in-distribution data.

        Sets threshold so that target_in_dist_recall of ID points are
        below threshold (NOT flagged as OOD).
        """
        # Sort in-dist energies; threshold = (1 - target_recall) quantile
        # of the energy distribution above which we flag OOD
        sorted_energies = torch.sort(in_dist_energies.flatten()).values
        n = len(sorted_energies)
        threshold_idx = int(n * target_in_dist_recall)
        self.threshold = sorted_energies[threshold_idx].item()
```

### 5.2 The Two-Tier Pipeline (Energy → Conformal)

Per Decision 5 v2 §5.4:

1. L7 produces logits
2. Layer 5.4 computes energy score E(x)
3. If E(x) above ID threshold → flag as OOD; route to abstain_ood verdict
4. If E(x) below ID threshold → proceed to Layer 5.3 (conformal) for statistical-guarantee output

This is operationally efficient (energy is ~free relative to conformal) and methodologically defensible (energy filters obviously-OOD before invoking conformal, which assumes calibration-set exchangeability).

**Note on conformal calibration validity:** when energy flags a point as OOD, the conformal coverage guarantee may not hold for that point (the calibration set does not contain analogous OOD points). The two-tier pipeline preserves Layer 5.3's coverage guarantee for the in-distribution subset.

### 5.3 Threshold Calibration

The energy threshold is calibrated **per substrate × per dataset** on the in-distribution training set. Default protocol:

- Compute energy scores for all training-set predictions
- Threshold at the 95th percentile of the in-dist energy distribution
- Operational meaning: 95% of ID points will pass the energy filter (proceed to conformal); 5% will be flagged as borderline OOD even within distribution (false positive rate ≈ 5%)

Layer 5 implementation tunes the threshold per V0-V1 results. Per Liu 2020 empirical scale: FPR@95%TPR reduction from 51% (softmax baseline) to 16% (energy post-hoc) — order of magnitude improvement on standard image benchmarks. On scRNA-seq, Theunissen 2025 finds OOD methods less reliable in general; specific magnitudes on INTERCEPTA tasks are Layer 5 empirical questions.

### 5.4 What Layer 5.4 Does NOT Do

- Does NOT replace conformal prediction. Energy is fast pre-filter; conformal provides the statistical guarantee.
- Does NOT distinguish aleatoric from epistemic. Energy is a single scalar; decomposition lives in 5.1 + 5.2.
- Does NOT detect subtle OOD shifts. Per Theunissen 2025, energy-based methods detect severe shifts; subtle shifts are unreliably flagged. This is a field-wide limitation, not specific to L2.3.

---

## §6 The Operational Verdict Logic

### 6.1 The Four Verdict Outcomes

Per Decision 5 v2 Layer 5 Output Contract:

- **confident_predict** — proceed with the prediction; uncertainty and conformal output usable
- **abstain_aleatoric** — biological/label ambiguity exceeds threshold; prediction may be unreliable due to data noise; consider obtaining more data
- **abstain_epistemic** — model out-of-distribution-ness exceeds threshold; prediction extrapolates beyond training distribution; flag for review
- **abstain_ood** — energy filter flagged this as OOD; statistical guarantees do not hold

These are operationally distinct — they trigger different downstream actions (retry vs flag vs reject) and require distinct user-facing presentations.

### 6.2 The Verdict Computation

```python
def _compute_operational_verdict(
    self,
    aleatoric: torch.Tensor,           # [N, 1] in [0, 1]
    epistemic: torch.Tensor,            # [N, 1] in [0, 1]
    energy_ood_flag: torch.Tensor,      # [N, 1] boolean
    conformal_out: ConformalOutput,
) -> List[str]:
    """Compute per-patient operational verdict."""

    N = aleatoric.shape[0]
    verdicts = []
    for i in range(N):
        # Priority order: OOD flag wins (most conservative)
        if energy_ood_flag[i].item():
            verdicts.append("abstain_ood")
        elif epistemic[i].item() > self.config.epistemic_abstain_threshold:
            verdicts.append("abstain_epistemic")
        elif aleatoric[i].item() > self.config.aleatoric_abstain_threshold:
            verdicts.append("abstain_aleatoric")
        else:
            verdicts.append("confident_predict")

    return verdicts
```

### 6.3 The Priority Order Rationale

The verdict priority is: **OOD → epistemic → aleatoric → confident**.

Rationale:
1. **OOD beats everything.** If energy says we're outside distribution, the conformal guarantee fails AND the aleatoric/epistemic decomposition becomes unreliable. Conservative.
2. **Epistemic beats aleatoric.** If both signals fire, "model doesn't know" is a stronger reason to abstain than "data is ambiguous." Epistemic uncertainty is reducible (with more data); aleatoric is irreducible.
3. **Aleatoric still triggers abstain.** High biological/label noise means we shouldn't act on the prediction even if the model is "confident."

### 6.4 The Threshold Defaults (CSO judgment per §10.5)

| Threshold | Default | Rationale |
|---|---|---|
| `aleatoric_abstain_threshold` | 0.7 | Above this, biological/label noise dominates; conservative |
| `epistemic_abstain_threshold` | 0.7 | Above this, model is outside familiar territory; symmetric with aleatoric |
| `energy_threshold` | data-dependent | Calibrated per (substrate, dataset) at 95th percentile of ID energy |

All thresholds revisitable per §10.5 J6, J7, J8.

### 6.5 The Verdict Quality Property

Per Decision 5 v2 Pass 4: aleatoric/epistemic decomposition must correctly attribute ≥70% of failed predictions to epistemic (rather than aleatoric). This means: when L7 prediction is wrong, the verdict should preferentially fire abstain_epistemic, not abstain_aleatoric.

This is a Layer 5 empirical pass criterion (§9 Pass 4) that L2.3 architecture is designed to satisfy via:
- Layer 5.1 substrate-conditional epistemic estimation (KDE distance to training distribution)
- Layer 5.2 ensemble disagreement (epistemic by construction)
- max-composition (§3.6) — high in either → flag epistemic

---

## §7 Compute Envelope and Wall-Clock Estimates

### 7.1 Per-Layer Compute Cost

Per Decision 9 v2 single-A100 envelope:

| Layer | Compute cost | Wall-clock per 10K predictions |
|---|---|---|
| 5.1 Substrate posterior | ~0.5 sec (KDE pre-computed) | 0.5 sec |
| 5.2 N=5 Deep Ensembles | 5× L7 forward | 5 × L7_time (cached embeddings dominate L7 time) |
| 5.3 Conformal prediction | O(N) set construction | <0.1 sec |
| 5.4 Energy score | O(N) log-sum-exp | <0.1 sec |
| **Total OOD stack** | ~5× L7 forward | bounded by Layer 5.2 |

For Layer 5.2 fallbacks:
- MIMO8: 1× forward (1.5× param model); ~1× L7 time
- MC Dropout T=50: 50× forward; ~50× L7 time (worst latency)

### 7.2 Memory Envelope

| Component | Memory |
|---|---|
| L7Ensemble N=5 | 5× L7 params (~100MB at 20M params per head) |
| KDE for FM-deterministic posterior | ~50MB (training emb + KDE object) |
| Conformal calibration scores | <10MB (sorted scores per disease) |
| Per-batch OODOutput | ~10MB |

Total: ~500MB. Comfortable for single-A100 (40-80GB).

### 7.3 Training Compute (L7Ensemble per L2.2 §8.3)

- Substrate forward + caching: ~6-12 hrs one-time
- Drug encoder forward + caching: ~1 hr one-time
- L7 head training: ~12-24 hrs per head; N=5 = ~3-5 days sequential OR ~1 day SLURM array
- OOD stack fitting (conformal on calibration set): <1 hr

### 7.4 Inference Compute (Production)

- Cached substrate forward: ~0.5 sec / 10K cells
- L7Ensemble N=5 forward: ~5 sec / 10K cells
- OOD stack: ~5.5 sec / 10K cells

This is feasible for clinical-scale deployment (10K cells = ~1 patient's biopsy at scRNA-seq throughput).

---

## §8 Cross-Decision Implications

### 8.1 Decision 1 v2 (Substrate)
**FOUNDATIONAL.** Layer 5.1 routes per substrate (SubstratePosteriorRegistry); the substrate is shared across L7Ensemble heads; KDE caching for FM-deterministic posterior is per substrate.

### 8.2 Decision 2 v2 (Cross-Cohort Harmonization)
**UPSTREAM.** scANVI/MrVI native posteriors are used directly when those are the substrate. Harmony/Seurat v3 are upstream of substrate; do not produce native posteriors; rely on KDE-over-embeddings fallback in Layer 5.1.

### 8.3 Decision 3 v2 (Bulk-to-Single Transfer)
**REINFORCED.** Bulk-to-single transfer creates additional OOD risk (bulk training, single-cell deployment). Layer 5.1 epistemic uncertainty + Layer 5.4 energy are essential signals for V3-V4 translation OOD detection (Decision 5 v2 Pass 2).

### 8.4 Decision 4 v2 (Drug Response Architecture)
**TIGHTLY COUPLED.** L2.3 consumes L2.2's L7Ensemble directly. L7Ensemble IS Layer 5.2. The L7Output `attribution_hooks` are NOT used by L2.3 (those go to L2.4); L2.3 uses `prediction` and `individual` (ensemble).

### 8.5 Decision 5 v2 (THIS DECISION)
**FULLY IMPLEMENTED.** All 4 layers realized. Output contract delivered. Cross-disease recalibration mechanism specified. The two-tier pipeline (energy → conformal) operationalized. Default + fallback paths specified.

### 8.6 Decision 6 v2 (Validation Cascade)
**PASS CRITERIA INTEGRATED.** OODOutput consumed by Decision 6 v2 validation harness at V0-V6. Per Decision 5 v2 Pass 1-4:
- Pass 1 (V0-V1): OOD detection AUROC ≥ 0.80 on held-out cell lines
- Pass 2 (V3-V4): OOD detection AUROC ≥ 0.70 on PDX/organoid shifts
- Pass 3 (V5): ECE ≤ 0.05 on patient predictions
- Pass 4 (V6): ≥70% of failed predictions correctly attributed to epistemic

### 8.7 Decision 7 v2 (Mechanistic Interpretability — L2.4)
**INTERFACE PROVIDED.** OODOutput's `operational_verdict` conditions L2.4 interpretability:
- For `confident_predict`: full 7-scale attribution
- For `abstain_aleatoric`: skip interpretability or run with reduced confidence
- For `abstain_epistemic`: flag attribution as extrapolation-prone
- For `abstain_ood`: do not run attribution (out of training distribution)

### 8.8 Decision 8 v2 (Universality / V6)
**V6 BINDING.** The cross-disease recalibration mechanism (§4.5) is the operational instantiation of Decision 8 v2 V6 ≥0.65 AUROC across ≥2 therapeutic areas. Decision 5 v2 Pass 4 binds: ≥70% of V6 failures correctly attributed to epistemic.

### 8.9 Decision 9 v2 (Compute Envelope)
**ENVELOPE HONORED.** §7 documents per-layer compute. Layer 5.2 N=5 Deep Ensembles dominate cost (~5× L7 forward); fallbacks (MIMO8 ~1×, MC Dropout 50×) provide compute-quality trade-off. Single-A100 envelope respected.

### 8.10 Decision 10 v2 (Open-Source)
**FULLY COMPATIBLE.** All dependencies open-licensed: scvi-tools (BSD-3); sklearn KDE (BSD-3); scipy / numpy / PyTorch baseline; no proprietary OOD libraries used.

### 8.11 Phase F Future Continuity
**A3 + A6 BRIDGED.** Per Charter v1.2 §1.6 reframe:
- A3 (drift detection) — Phase B delivers cell-level epistemic drift detection per prediction (§3); Phase F adds deployment-monitoring drift over time using OODOutput aggregation
- A6 (self-aware meta-confidence) — Phase B delivers statistical uncertainty (Layer 5.3 conformal); Phase F adds meta-cognition over reliability across novel scenarios

L2.3 architecture provides the Phase B substrate that Phase F builds on. No Phase F integration specified here; documented for future continuity.

---

## §9 Pass Criteria for L2.3 LOCK

### 9.1 Architecture-Level Pass Criteria (BINDING)

**A1:** All 4 layers (5.1 through 5.4) implemented as specified in §2-§5 with PyTorch class skeletons.
**A2:** Layer 5.1 supports all 4 substrate families (scVI/scANVI/MrVI, FM-deterministic, scTOP, PCA+HVG) via SubstratePosteriorRegistry.
**A3:** Layer 5.2 consumes L2.2 L7Ensemble directly; provides MIMO8 + MC Dropout fallbacks per Decision 5 v2.
**A4:** Layer 5.3 supports 3 non-conformity measures (softmax / absolute / studentized) and 3 taxonomies (standard / classwise / cluster).
**A5:** Layer 5.4 implements energy score E(x) = -T·log Σ exp(z_i/T) with calibratable threshold.
**A6:** OODOutput schema delivered per Decision 5 v2 Layer 5 Output Contract.
**A7:** Cross-disease recalibration mechanism implemented per §4.5.
**A8:** Operational verdict priority order (OOD → epistemic → aleatoric → confident) implemented per §6.

### 9.2 Cross-Decision Compatibility Pass Criteria (BINDING)

**X1:** L2.3 consumes L2.2 L7Ensemble with `return_individual_predictions=True`.
**X2:** OODOutput passed correctly to L2.4 (operational_verdict conditions interpretability).
**X3:** OODOutput passed correctly to L3.1 V0-V6 validation harness.
**X4:** Compute envelope (§7) fits Decision 9 v2 single-A100 target; fallbacks specified for budget-constrained scenarios.
**X5:** All dependencies open-licensed per Decision 10 v2.

### 9.3 Empirical Pass Criteria (Layer 5-verified per Decision 5 v2 Pass 1-4)

**E1 (Pass 1, V0-V1):** OOD detection AUROC ≥ 0.80 on held-out cell lines (within-cohort, cross-cell-line dataset).
**E2 (Pass 2, V3-V4):** OOD detection AUROC ≥ 0.70 on PDX/organoid shifts.
**E3 (Pass 3, V5):** Calibration error (ECE) ≤ 0.05 on patient predictions in clinical retrospective evaluation.
**E4 (Pass 4, V6):** Aleatoric/epistemic decomposition correctly attributes ≥ 70% of failed predictions to epistemic uncertainty.
**E5 (Conformal coverage):** Empirical coverage on held-out test sets within ±2pp of target 1-α (e.g., 93-97% for α=0.05) under exchangeability assumptions.
**E6 (Energy calibration):** FPR@95%TPR for energy filter improves over softmax-MSP baseline by ≥10pp on V0-V1 (per Liu 2020 empirical magnitudes).

### 9.4 Documentation Pass Criteria

**D1:** L2.3 referenced by L2.4 with verified cross-references.
**D2:** L2.3 Layer 5 implementation matches L2.3 specification.
**D3:** Drift catalog this session: 0 new drift instances introduced.

### 9.5 CEO Sign-Off

L2.3 advances from PROPOSED to LOCKED when:
1. CEO reviews §1-§6 architecture and §9 pass criteria
2. CEO confirms §10.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag `phase-b-l2.3-locked` pushed to origin

---

## §10 What L2.3 Does NOT Lock

### 10.1 Deferred to Layer 5 Ablation

- Default Layer 5.2 mode (N=5 Deep Ensembles vs MIMO8 vs MC Dropout) — per-deployment compute decision
- Default conformal taxonomy (standard vs classwise vs cluster) — per-V-level decision
- Exact energy threshold (calibrated per substrate × dataset)
- Verdict thresholds within documented default ranges
- Composition rule for epistemic (max vs sum vs learned) within §10.5 J3 alternatives

### 10.2 Deferred to L2.4

- Substrate-conditional attribution branches conditioned on OOD verdict
- Per-verdict interpretability presentation

### 10.3 Deferred to L3.1 (Validation Cascade)

- V0-V6 OOD evaluation harness implementation
- Pass 1-4 empirical verification
- Cross-disease F1-F7 failure attribution

### 10.4 Out of Scope (Phase F)

- Deployment-monitoring drift over time (Phase F A3 completion)
- Meta-cognition over novel scenarios (Phase F A6 completion)
- Online recalibration as new labeled data arrives (Phase F A2)
- Federated conformal calibration across institutions (Phase F per Charter v1.2 §4 row 2)

### 10.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | Layer 5.1 strategy for FM substrate | KDE-over-training-emb | CPA-latent-marginal, learned posterior network | KDE epistemic correlation with prediction error < 0.3 (signal too weak) |
| J2 | Layer 5.1 KDE bandwidth | 0.1 | 0.05, 0.2 (log-spaced) | Standard tuning at Layer 5 |
| J3 | Epistemic composition | max | sum, learned linear combo | Learned outperforms max by ≥5pp on Pass 4 |
| J4 | Layer 5.2 fallback choice if N=5 infeasible | MIMO8 | MC Dropout T=50 | MIMO8 retraining cost prohibitive at V6 scale |
| J5 | Layer 5.3 non-conformity | studentized | softmax, absolute_error | Standard within 1pp coverage at lower compute |
| J6 | Layer 5.3 default taxonomy | standard | classwise (for imbalanced), cluster (for V6) | Classwise improves V5 ECE by ≥30% relative |
| J7 | Verdict threshold aleatoric | 0.7 | 0.5-0.9 range | Standard tuning at Layer 5 |
| J8 | Verdict threshold epistemic | 0.7 | 0.5-0.9 range | Standard tuning at Layer 5 |
| J9 | Energy threshold target FPR | 0.05 (5% false-positive rate) | 0.01, 0.10 | Operational FPR/abstain-rate trade-off |
| J10 | Cross-disease min calibration samples | 50 | 30, 100 | Statistical power analysis at V6 |

### 10.6 Honest Limitations (per Charter §10 P15 BINDING)

L2.3 honestly states the limitations that the field-wide OOD literature also faces:

- **Theunissen 2025 empirical caveat:** "OOD methods can identify severe data shifts, but not reliably." L2.3 inherits this caveat. Severe OOD (cancer cell → autoimmune cell) detected reliably; subtle OOD (cancer subtype shift within disease) unreliably detected. INTERCEPTA publications must state this.
- **Conformal marginal vs conditional coverage:** Layer 5.3 provides marginal coverage guarantees, not conditional. A model could achieve 95% marginal coverage by being overconfident on common cases and underconfident on rare cases. Not corrected by L2.3.
- **Cross-disease conformal recalibration limit:** When fewer than 50 labeled samples are available for a held-out disease, L2.3 does NOT provide statistical coverage guarantees for that disease. Honestly flagged in OODOutput.
- **N=5 ensemble may not capture epistemic uncertainty fully.** Per Osband 2016, Hron 2017 (cited in Q5 anchor 4 Gal 2016 critique): ensembles approximate epistemic uncertainty heuristically, not exactly. L2.3 inherits this approximation.
- **Energy threshold calibration assumes IID ID samples.** When ID distribution itself shifts (e.g., new batch added to training), threshold must be recalibrated. Not done automatically by L2.3.

These limitations are stated for honest deployment, not as reasons to abandon the architecture. The field-wide OOD literature operates within the same limitations.

---

## §11 Document Provenance and CSO Discipline Check

### 11.1 Provenance

L2.3 written by Claude (CSO, fresh session 2026-05-11) per Phase B Plan v2 sequencing. Predecessor artifacts L2.1 (LOCKED) and L2.2 (PROPOSED) in immediate context. Anchor re-read trigger satisfied retroactively per Master Handoff v2.0 §3.5 (6 Q5 anchors re-read in primary-source form during the 2026-05-11 audit session).

### 11.2 Anchor Re-Read Compliance

| Anchor | Last primary-source read | Content used in L2.3 |
|---|---|---|
| Theunissen 2025 | 2026-05-11 audit | Empirical caveat §10.6; Deep Ensembles vs MC Dropout ordering §3.3 |
| López-De-Castro 2025 | 2026-05-11 audit | Conformal prediction methodology §4; 3 non-conformity measures §4.3; 3 taxonomies §4.4; marginal-vs-conditional limitation §10.6 |
| Lakshminarayanan 2017 | 2026-05-11 audit | Deep Ensembles foundational §3.3 |
| Gal & Ghahramani 2016 | 2026-05-11 audit | MC Dropout fallback §3.5; T=50 default |
| Liu 2020 energy | 2026-05-11 audit | Energy score formula §5; empirical magnitudes §5.3 |
| Engelmann 2022 | 2026-05-11 audit | MIMO8 fallback §3.4; aleatoric/epistemic decomposition §3.6; scArches WKNN inadequacy motivation §0 |

No anchor re-read drift detected.

### 11.3 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ L2.3 grounded in 6 verified primary-source Q5 anchor reads.
- **P15 (only correct/honest/real science):** ✅ §10.6 honest limitations explicit; §4.5 cross-disease recalibration flag for unreliable coverage; §10.5 J-items document CSO judgment with revisit triggers.
- **P16 (preserve past work):** ✅ Decision 5 v2 + Q5 synthesis preserved; L2.3 builds on top.
- **P-FV-1 to P-FV-3:** ✅ L2.3 honors Phase B scope; Phase F A3/A6 continuity documented but not specified.
- **Charter §5.3 GO/NO-GO:** ✅ §9 pass criteria explicit; §9.5 CEO sign-off conditions stated.
- **Charter v1.2 §1.7 phase discipline:** ✅ No Phase F integration patterns specified.

### 11.4 Drift Catalog This Session

**New drift instances introduced:** 0.

**Pre-existing drift findings addressed:**
- Finding 8 (Decision 5 v2 N=5 ensembleability) — operationalized via §3 explicit "L7 head is ensembled unit" + L2.2 L7Ensemble class consumption pattern.

### 11.5 Next Phase B Artifacts (per Plan v2 Sequence)

- **L2.4 Mechanistic Interpretability Architecture** (10-12K words target). Consumes L2.2 L7Output `attribution_hooks` + L2.3 OODOutput `operational_verdict` for substrate-conditional and verdict-conditional attribution.
- **L3.1 V0-V6 Validation Cascade Pipeline** (5-7K words). Consumes L7 + L2.3 + L2.4 outputs; specifies the evaluation harness.

---

## §12 Appendix — Quick Reference

### 12.1 Layer Quick Comparison Table

| Layer | Function | Compute | Output | Source Anchor |
|---|---|---|---|---|
| 5.1 | Substrate posterior | Cheap (cached substrate forward) | aleatoric + epistemic per cell | Engelmann 2022 + Decision 1 v2 |
| 5.2 | Epistemic refinement (= L2.2 L7Ensemble) | 5× L7 forward (N=5 default) | ensemble disagreement | Lakshminarayanan 2017 |
| 5.3 | Conformal prediction | O(N) post-fit | prediction set / interval with 1-α coverage | López-De-Castro 2025 |
| 5.4 | Energy score | O(N) log-sum-exp | binary OOD flag | Liu 2020 |

### 12.2 Operational Verdict Quick Reference

| Verdict | Trigger | Downstream Action |
|---|---|---|
| `confident_predict` | All thresholds passed | Proceed with prediction |
| `abstain_aleatoric` | aleatoric > 0.7 | Flag biological/label noise; consider more data |
| `abstain_epistemic` | epistemic > 0.7 | Flag model OOD; refer for review |
| `abstain_ood` | energy_ood_flag = True | Reject; do not predict |

### 12.3 Key Constants

- Default N for ensembles: 5 (Decision 5 v2 BINDING)
- Default conformal α: 0.05 (95% coverage)
- Default MC Dropout T: 50
- Default verdict thresholds: 0.7 aleatoric / 0.7 epistemic
- Default energy temperature: T = 1.0
- Min cross-disease calibration samples: 50

### 12.4 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_3_OOD_Detection_Stack_Specification_2026-05-11.md`
- L2.2 spec (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_2_L7_Drug_Response_Architecture_Specification_2026-05-11.md`
- Decision 5 v2 (parent): `~/INTERCEPTA/docs/research/decisions/INTERCEPTA_FV_Decision_5_Q5_ood_detection.md`
- OOD implementation code (future): `~/INTERCEPTA/code/ood_stack/`
- KDE caches (future): `/scratch/akula.pra/INTERCEPTA/kde/`
- Conformal calibration storage (future): `/scratch/akula.pra/INTERCEPTA/conformal/`

### 12.5 Commitment Cross-Reference

| Decision Commitment | L2.3 §  | Implementation |
|---|---|---|
| Decision 5 v2 Layer 5.1 (foundation) | §2 | Substrate-conditional registry |
| Decision 5 v2 Layer 5.2 (epistemic refinement) | §3 | L7Ensemble consumption + fallbacks |
| Decision 5 v2 Layer 5.3 (statistical guarantee) | §4 | Conformal predictor with 3 non-conformity + 3 taxonomies |
| Decision 5 v2 Layer 5.4 (energy pre-filter) | §5 | EnergyScorer with calibratable threshold |
| Decision 5 v2 Output Contract | §1.4 | OODOutput dataclass BINDING |
| Decision 5 v2 cross-disease recalibration | §4.5 | CrossDiseaseRecalibrationManager |
| Decision 5 v2 Pass 1 (V0-V1 AUROC ≥ 0.80) | §9.3 E1 | Pass criterion |
| Decision 5 v2 Pass 2 (V3-V4 AUROC ≥ 0.70) | §9.3 E2 | Pass criterion |
| Decision 5 v2 Pass 3 (V5 ECE ≤ 0.05) | §9.3 E3 | Pass criterion |
| Decision 5 v2 Pass 4 (V6 ≥70% epistemic attribution) | §9.3 E4 | Pass criterion |
| Drift Finding 8 (N=5 ensembleability) | §3.1 | L7 head as ensembled unit |
| Charter v1.2 §1.6 A3 (drift detection partial) | §8.11 | Phase B cell-level epistemic drift detection |
| Charter v1.2 §1.6 A6 (statistical uncertainty partial) | §8.11 | Phase B conformal coverage |

---

— L2.3 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l2.3-locked` tag.
— After LOCK, Phase B Plan v2 next artifact is L2.4 Mechanistic Interpretability Architecture.
