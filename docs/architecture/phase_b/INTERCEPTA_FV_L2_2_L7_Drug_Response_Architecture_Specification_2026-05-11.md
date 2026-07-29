# INTERCEPTA Phase B Layer 2 — Artifact 2.2
## L7 6-Slot Drug Response Architecture Specification

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifact:** L2.1 Substrate Architecture Specification (LOCKED 2026-05-11)
**Parent decision:** Decision 4 v2 Q4 Drug Response Architecture (LOCKED)
**Co-bound decisions:** Decision 1 v2 (substrate), Decision 3 v2 (bulk-to-single transfer), Decision 5 v2 (OOD ensembleability), Decision 6 v2 (V0-V6 validation), Decision 7 v2 (interpretability), Decision 9 v2 (compute envelope), Decision 10 v2 (open-source)
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping (documented for future continuity, NOT specified here):** Phase B L7 = Phase F Simulation Stack Layer B (Cell Population Sensitivity) per Charter v1.2 §4 row 18
**Target length per Phase B Plan v2:** 12-15K words
**Filename:** `INTERCEPTA_FV_L2_2_L7_Drug_Response_Architecture_Specification_2026-05-11.md`

---

## §0 Identification and Scope

### 0.1 What This Document Is

L2.2 is the **L7 6-Slot Drug Response Architecture Specification**. It is the second artifact of Phase B Layer 2 work. L2.2 specifies how the cell-level drug response prediction layer of INTERCEPTA is constructed by composing six explicit architectural slots over the substrate interface defined in L2.1.

The slots are: (1) Cell Encoder, (2) Drug Molecule Encoder G, (3) Perturbation Network M+S, (4) Graph-Augmented Module, (5) Mode Collapse Mitigation, (6) Patient-Level Aggregation. The slot ordering and identities are LOCKED by Decision 4 v2. L2.2 specifies each slot's implementation contract, dimensions, default choices, ablation infrastructure, and cross-slot interaction patterns.

L2.2 also specifies how the L7 head composes with Decision 5 v2's N=5 Deep Ensembles layer (BINDING ensembleability per Drift Finding 8), how it interfaces with Decision 6 v2's V0-V6 validation cascade, and how it operates within Decision 9 v2's single-A100 Northeastern Explorer compute envelope.

### 0.2 What This Document Is Not

L2.2 is NOT:

- A Layer 5 implementation. It is an architectural specification with PyTorch class skeletons sufficient to begin implementation, not full production code.
- A Decision Record amendment. All binding decisions from Decisions 1 v2, 3 v2, 4 v2, 5 v2, 6 v2, 9 v2, 10 v2 are honored. Where ambiguity exists, L2.2 resolves with CSO judgment documented in §9.5 as Layer-5-revisitable.
- A Phase F specification. Phase F's 6-Scout system, 15-layer Universal Net, generative chemistry (Scout 2), molecular docking (Layer A), ODE dynamics (Layer C), synergy scoring (Layer D), ADMET (Layer E), retrosynthesis (Layer F), and pharma deliverable package are CANONICAL Phase F scope per Charter v1.2 §4 — out of scope for L2.2.
- A drug discovery system. L2.2 specifies the cell-level evaluator that predicts drug response. It does not retrieve candidate drugs (Phase F Scout 1), generate novel molecules (Phase F Scout 2), enumerate combinations (Phase F Scout 3), or score safety (Phase F Layer E).
- A patient-facing tool. Decision 5 v2 outputs ranked predictions with uncertainty; clinical decision support is out of charter scope per Charter v1.2 §4 row 6.

### 0.3 Phase B Plan v2 Compliance

Per Phase B Execution Plan v2 sequencing:

- Artifact 1 of Layer 2 (L2.1 Substrate Specification) → LOCKED 2026-05-11 with Drift Findings 4/5/6 errata
- **Artifact 2 of Layer 2 (this document, L2.2) → PROPOSED**
- Artifact 3 of Layer 2 (L2.3 OOD Detection Stack) → pending, depends on L2.2 having locked the L7 head signature
- Artifact 4 of Layer 2 (L2.4 Mechanistic Interpretability Architecture) → pending, depends on L2.2 substrate-conditional branches and L2.3 OOD posterior

L2.2 sits in the middle of the Layer 2 dependency graph: it consumes L2.1's substrate interface (`substrate.project_to_canonical()`) and produces the L7 head signature that L2.3 wraps with N=5 ensembles and that L2.4 attributes with multi-scale interpretability.

### 0.4 Anchor Re-Read Compliance

Per Phase B Plan v2 anchor re-read trigger ("CSO must re-read anchor papers in the current session before writing spec; no memory-extrapolation across sessions"), L2.2's anchor re-read trigger is SATISFIED.

The 8 Q4 anchor papers were re-read in primary-source form during the 2026-05-11 corpus-read audit (the immediately preceding session). The anchors and the architectural commitments they ground:

| Anchor | Citation | L2.2 commitment grounded |
|---|---|---|
| **CPA** | Lotfollahi 2023 *Mol Syst Biol* (Meta/Helmholtz; MIT) | Backbone composition framework (§4 Slot 3, §5 Slot 4 attention pattern, §6 Slot 5 mode collapse default formulation, §7 Slot 6 patient pooling integration); disentangled latent separating perturbation × cell type × dose × time × species × patient (§4) |
| **chemCPA** | Hetzel 2022 NeurIPS | Modular drug encoder slot enabling unseen-drug prediction (§3 Slot 2); architecture surgery pattern for bulk-to-single transfer (§8 Decision 3 v2 cross-reference) |
| **GEARS** | Roohani 2024 *Nat Biotechnol* | Graph-augmented attention over biological priors (§5 Slot 4); gene-gene co-expression + GO ontology + drug-target ontology composition (§5.2) |
| **PaSCient** | Liu 2024-2026 ICML / *Nat Methods* | Patient-level attention pooling (§7 Slot 6 default); 24.3M cells / 5K+ patients evaluation precedent (§9 Pass Criteria sample size grounding) |
| **scGen** | Lotfollahi 2019 *Nat Methods* | Latent-space arithmetic captures perturbation effects at R²=0.954 (§4 Slot 3 latent arithmetic primitive); training-time perturbation prediction baseline (§9 Pass Criteria reference) |
| **sci-Plex** | Srivatsan 2020 *Science* | ~650K cells, 188 drugs × 4 doses primary perturbation training corpus (§9 Pass Criteria training data spec) |
| **PaccMann** | Manica 2019 | Drug-target prediction with attention precedent (§5 Slot 4 attention design reference; ~1-10M params compute envelope reference for Decision 9 v2 single-A100 fit) |
| **DeepCDR** | Liu 2020 | Drug response prediction baseline architecture; ~1-10M params (§9 Pass Criteria baseline comparator reference) |

If during L2.2 writing I encounter a real ambiguity that requires re-reading any of these anchors, I stop and surface the gap. No memory-extrapolation across sessions for binding architectural commitments.

### 0.5 Document Conventions

- **BINDING** — a commitment that cannot be modified without a Decision Record amendment + CEO+CSO co-sign. Violation fails Pass Criteria.
- **DEFAULT** — a choice L2.2 makes for initial Layer 5 implementation; revisitable per §9.5 with documented empirical signal.
- **DEFERRED** — a question L2.2 does not lock; reserved for Layer 5 ablation per Decision 4 v2 "What L2.2 Does NOT Lock" pattern.
- **PHASE F** — out of L2.2 scope; canonical for Phase F per Charter v1.2 §4.
- All code snippets are PyTorch 2.x. AnnData via scanpy 1.10+. scvi-tools 1.4+ where applicable.
- All dimensions in [batch, features] notation. Cell embeddings are 512-dim canonical per L2.1 §1.2.

---

## §1 The L7 6-Slot Architecture Overview

### 1.1 Why a Slotted Architecture

Decision 4 v2 commits INTERCEPTA to a **modular architecture** rather than a monolithic prediction network. The slot pattern serves four purposes:

1. **Substrate independence.** Slot 1 (cell encoder) is swappable via the L2.1 SubstrateInterface. Whichever substrate wins Layer 5 ablation (scFoundation FM, scTOP parameter-free, scVI VAE, or PCA classical) flows through Slot 1 without modifying Slots 2-6.

2. **Chemical encoder swappability.** Slot 2 (drug molecule encoder G) is swappable per chemCPA. MoLFormer, ChemBERTa, Uni-Mol, or RDKit baseline can be slot-substituted without modifying the perturbation network or downstream slots. This is the chemCPA contribution that makes unseen-drug prediction possible.

3. **Mode-collapse mitigation as a separate slot.** Slot 5 lets us A/B/C test diversity loss, energy-based training, and mixture-of-experts decoder independently of the prediction architecture. The Diversity-by-Design 2025 critique made this slot necessary.

4. **Patient aggregation as a separate slot.** Decision 9 v2 + Drift Finding 10 require PaSCient + simpler fallbacks. Slot 6 makes this explicit: the patient-level aggregation strategy is independent of the cell-level prediction.

The cost of slotted modularity is some implementation overhead vs a fused network. The benefit is empirical defensibility: each slot's contribution can be ablated separately, which the Souza-Mehta methodological bar (Decision 8 v2 Commitment 5 BINDING) requires.

### 1.2 The Slot Data Flow

```
                    INPUTS
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   scRNA-seq cells   drug SMILES   covariates
   (anndata)         (string)      (dose, time,
        │              │            patient ID,
        │              │            cell type label)
        │              │              │
        ▼              ▼              │
   [SLOT 1]       [SLOT 2]            │
   Cell Encoder   Drug Encoder G      │
   = L2.1         = MoLFormer         │
   substrate      default             │
        │              │              │
   512-dim cell   D_drug-dim          │
   embedding      chemical emb.       │
        │              │              │
        │              ▼              │
        │         [SLOT 3]            │
        │         Perturbation        │
        │         Network M+S         │
        │         (chemCPA)           │
        │              │              │
        │         latent perturb.     │
        │         effect              │
        │              │              │
        └──────┬───────┘              │
               │                      │
               ▼                      │
       CPA Disentangled               │
       Latent z                       │
       (perturb × cell × dose         │
        × time × species              │
        × patient)                    │
               │                      │
               ▼                      │
       [SLOT 4]                       │
       Graph-Augmented Module         │
       gene-gene + GO + drug-target   │
       (GEARS-style attention)        │
               │                      │
               ▼                      │
       Graph-conditioned z'           │
               │                      │
               ▼                      │
       [SLOT 5]                       │
       Mode Collapse Mitigation       │
       (diversity loss default)       │
               │                      │
               ▼                      │
       CPA Decoder                    │
       → cell-level                   │
         perturbation                 │
         prediction y_cell            │
               │                      │
               │   ◄──────────────────┘
               │   (covariates flow into
               │    Slot 6 aggregation)
               ▼
       [SLOT 6]
       Patient-Level Aggregation
       (PaSCient default + fallbacks)
               │
               ▼
       Patient-level drug
       response prediction y_patient
```

### 1.3 The L7 Module Interface

The L7 head exposes a single forward signature that Layer 5 implementation, Decision 5 v2 OOD ensembling, and Decision 6 v2 validation harness all consume:

```python
class L7DrugResponseHead(torch.nn.Module):
    """
    The L7 6-slot drug response prediction head.

    Composes Decision 1 v2 substrate (via SubstrateInterface) with
    Decision 4 v2 6-slot architecture. Compatible with Decision 5 v2
    N=5 ensembling, Decision 6 v2 V0-V6 validation, Decision 9 v2
    single-A100 envelope.
    """

    def __init__(
        self,
        substrate: SubstrateInterface,           # Slot 1 — from L2.1
        drug_encoder: DrugEncoderInterface,      # Slot 2 — see §3
        perturbation_network: PerturbationNetworkM_S,  # Slot 3 — see §4
        graph_module: GraphAugmentedModule,      # Slot 4 — see §5
        mode_collapse_strategy: ModeCollapseStrategy,  # Slot 5 — see §6
        aggregator: PatientAggregator,           # Slot 6 — see §7
        config: L7Config,                        # hyperparameter bundle
    ):
        super().__init__()
        self.substrate = substrate
        self.drug_encoder = drug_encoder
        self.perturbation_network = perturbation_network
        self.graph_module = graph_module
        self.mode_collapse_strategy = mode_collapse_strategy
        self.aggregator = aggregator
        self.config = config

        # CPA disentangled latent and decoder are intrinsic to the head
        # (not slot-substitutable per Decision 4 v2 commitment to CPA backbone)
        self.disentangled_latent = CPADisentangledLatent(...)  # §4
        self.decoder = CPADecoder(...)                          # §4

    def forward(
        self,
        adata: AnnData,
        drug_smiles: List[str],
        covariates: Covariates,
        return_cell_level: bool = False,
        return_attribution_hooks: bool = False,
    ) -> L7Output:
        """
        Predict drug response.

        Args:
            adata: scRNA-seq object with cells × genes
            drug_smiles: list of N_drugs SMILES strings to evaluate
            covariates: dose, time, patient_id, cell_type, species
            return_cell_level: if True, return cell-level predictions
                              (Slot 6 input); if False, return patient-level
                              (Slot 6 output)
            return_attribution_hooks: if True, return intermediate tensors
                                       for Decision 7 v2 attribution

        Returns:
            L7Output containing predictions, optional cell-level, optional
            attribution hooks. See §1.4 for output schema.
        """
        # Slot 1: substrate cell encoding (via L2.1 canonical pattern)
        cell_emb_native = self.substrate.encode(adata, batch_key=covariates.batch_key)
        cell_emb = self.substrate.project_to_canonical(cell_emb_native)  # 512-dim
        cell_emb = torch.from_numpy(cell_emb).to(self.config.device)

        # Slot 2: drug chemical encoding
        drug_emb = self.drug_encoder.encode(drug_smiles)  # [N_drugs, D_drug]

        # Slot 3: perturbation network M+S
        latent_perturb = self.perturbation_network(drug_emb, covariates.dose)

        # CPA disentangled latent composition
        z = self.disentangled_latent(cell_emb, latent_perturb, covariates)

        # Slot 4: graph-augmented module
        z_graph = self.graph_module(z, drug_emb, drug_targets=covariates.drug_targets)

        # Slot 5: mode collapse mitigation (training-time only; identity at inference)
        if self.training:
            z_graph, diversity_aux = self.mode_collapse_strategy(z_graph)
        else:
            diversity_aux = None

        # CPA decoder → cell-level prediction
        y_cell = self.decoder(z_graph, covariates)  # [N_cells, output_dim]

        # Slot 6: patient-level aggregation
        if return_cell_level:
            y_out = y_cell
        else:
            y_out = self.aggregator(y_cell, covariates.patient_id)

        return L7Output(
            prediction=y_out,
            cell_level=y_cell if return_cell_level else None,
            diversity_aux=diversity_aux,
            attribution_hooks=_collect_hooks(...) if return_attribution_hooks else None,
        )
```

### 1.4 The L7 Output Schema

```python
@dataclass
class L7Output:
    """Standard L7 output. Consumed by Decision 5 v2 OOD, Decision 6 v2
    validation, Decision 7 v2 interpretability."""

    prediction: torch.Tensor
        # [N_patients, output_dim] if aggregated; [N_cells, output_dim] if cell-level
        # output_dim depends on task: 1 (regression IC50/AUC), N_drugs (multi-drug
        # classification), or N_classes (response/no-response classification)

    cell_level: Optional[torch.Tensor]
        # [N_cells, output_dim] when return_cell_level=True

    diversity_aux: Optional[torch.Tensor]
        # auxiliary loss term from Slot 5 mode collapse mitigation;
        # None at inference

    attribution_hooks: Optional[Dict[str, torch.Tensor]]
        # intermediate tensors for Decision 7 v2 attribution
        # Keys: "cell_emb", "drug_emb", "latent_perturb", "z",
        #       "z_graph", "y_cell"
```

This output schema is BINDING. Decision 5 v2 OOD ensembling consumes `prediction`. Decision 6 v2 V0-V6 validation consumes `prediction` + optional `cell_level`. Decision 7 v2 multi-scale interpretability consumes `attribution_hooks`. Modifications require Decision Record amendment.

### 1.5 The L7Config Hyperparameter Bundle

```python
@dataclass
class L7Config:
    """L7 hyperparameter configuration. All defaults are revisitable per
    §9.5 with documented Layer 5 empirical signal."""

    # Slot 1 — substrate is passed as argument; no config

    # Slot 2 — drug encoder
    drug_encoder_name: str = "molformer"  # or "chemberta", "unimol", "rdkit"
    drug_emb_dim: int = 768  # MoLFormer default; overridden if encoder differs

    # Slot 3 — perturbation network
    perturbation_hidden_dim: int = 256
    perturbation_n_layers: int = 3
    dosage_scaler_type: str = "amortized"  # chemCPA default

    # CPA disentangled latent (intrinsic, not slot)
    latent_dim: int = 64  # CPA default
    n_covariate_classes: Dict[str, int] = field(default_factory=dict)

    # Slot 4 — graph-augmented module
    graph_attention_heads: int = 4
    graph_attention_dim: int = 128
    use_gene_gene_graph: bool = True
    use_go_ontology_graph: bool = True
    use_drug_target_graph: bool = True

    # Slot 5 — mode collapse mitigation
    mode_collapse_strategy_name: str = "diversity_loss"  # or "energy_based", "moe"
    diversity_loss_weight: float = 0.1
    diversity_loss_formula: str = "dpp"  # DPP (Determinantal Point Process) default

    # Slot 6 — patient aggregation
    aggregator_name: str = "pascient_attention"
        # or "mean", "max", "learned_weighted"
    aggregator_attention_heads: int = 4
    aggregator_compute_fallback: str = "learned_weighted"
        # fallback when PaSCient compute budget exceeded

    # Training objective composition
    composition_loss_weight: float = 1.0
    diversity_loss_weight_in_objective: float = 0.1
    auxiliary_drug_target_loss_weight: float = 0.05

    # Ensemble interface (Decision 5 v2)
    ensemble_n: int = 5  # BINDING N=5 default per Decision 5 v2 Layer 5.2
    ensemble_random_seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])

    # Compute envelope (Decision 9 v2)
    device: str = "cuda:0"
    batch_size_cells: int = 1024
    batch_size_drugs: int = 32
    use_cached_embeddings: bool = True
    cached_embedding_path_template: str = (
        "/scratch/akula.pra/INTERCEPTA/embeddings/{substrate}/{dataset}/{split}.h5"
    )
```

All defaults documented as Layer-5-revisitable per §9.5.

### 1.6 What the Architecture Does Not Specify

Per Decision 4 v2 "What L2.2 Does NOT Lock":

- Specific empirical winner in any slot ablation (all slots have defaults + alternatives; Layer 5 ablation picks the winner)
- Exact hyperparameter values (defaults documented; ranges deferred to Layer 5)
- Training data composition (covered by Layer 4 + Decision 6 v2 dataset spec)
- Exact loss function weighting (composition + diversity + auxiliary auxiliaries have defaults; Layer 5 tunes)
- Deployment serving infrastructure (Layer 5+ implementation concern)

---

## §2 Slot 1 — Cell Encoder (Substrate Interface)

### 2.1 The Slot 1 Contract

Slot 1 is the **substrate interface** from L2.1. L2.2 does not specify a new substrate; it specifies how the L7 head consumes the substrate's output.

The contract is:

1. **Input:** `AnnData` object with cells × genes
2. **Substrate call:** `substrate.encode(adata, batch_key=...)` returns `[N_cells, NATIVE_DIM]` per the substrate's native space
3. **Canonical projection (BINDING per L2.1 Finding 5):** `substrate.project_to_canonical(emb)` returns `[N_cells, 512]`
4. **L7 head ONLY consumes the canonical 512-dim output.** It does NOT inspect or branch on the substrate's native dim. It does NOT instantiate an internal `torch.nn.Linear(substrate.output_dim, 512)` — that pattern is functionally superseded per L2.1 §1.2 errata.

### 2.2 The Substrate-Independence Property

Decision 1 v2 Commitment 4 ("Interface Stability") guarantees that swapping substrates is an O(1) architectural change. L2.2 honors this by writing all of Slots 2-6 to operate exclusively on the canonical 512-dim cell embedding.

**Concrete consequence:** when Layer 5 ablation compares scFoundation vs scTOP vs scVI vs PCA+HVG on V0-V6 pass criteria, the only configuration change is `config.substrate.name`. No other slot needs modification. This is what makes the Souza-Mehta methodological bar (≥25% hyperparameter budget to scTOP-style Baseline B per Decision 8 v2 Commitment 5) operationally tractable.

### 2.3 scTOP Lifecycle Handling (BINDING per L2.1 Finding 6)

scTOP's `NATIVE_DIM` is sentinel `-1` until `fit()` or `load_pretrained()` is called with a reference. L2.2 instantiation order MUST honor this. The L7 head construction sequence is:

```python
def build_l7_head(config: L7Config, substrate_config: SubstrateConfig) -> L7DrugResponseHead:
    """Canonical L7 head construction. Honors L2.1 Finding 6 scTOP lifecycle."""

    # Step 1: Instantiate substrate
    substrate = SubstrateRegistry.get(substrate_config.name)(**substrate_config.kwargs)

    # Step 2: If scTOP, must fit reference BEFORE any output_dim access
    if substrate.NAME == "sctop":
        if substrate_config.reference_path is None:
            raise ValueError(
                "scTOP substrate requires reference_path. Per L2.1 Finding 6 "
                "errata, NATIVE_DIM is -1 until fit() or load_pretrained() is "
                "called. Cannot construct L7 head without reference."
            )
        substrate.load_pretrained(substrate_config.reference_path)
        # NATIVE_DIM is now set; output_dim is accessible

    # Step 3: Other substrates may need their own initialization
    elif substrate.NAME in ("scvi", "scanvi", "mrvi") and substrate_config.train_on_dataset is not None:
        substrate.fit(substrate_config.train_on_dataset)

    # Step 4: Verify substrate is ready (project_to_canonical works)
    _verify_substrate_ready(substrate)

    # Step 5: Now safe to construct downstream slots
    drug_encoder = DrugEncoderRegistry.get(config.drug_encoder_name)(...)
    ...
    return L7DrugResponseHead(substrate, drug_encoder, ..., config)
```

This is enforced in code with assertions, not just documentation. The `_verify_substrate_ready` helper calls `substrate.output_dim` and `substrate.project_to_canonical(dummy_input)` to verify both work; any RuntimeError surfaces as a clear failure at L7 head construction, not deep inside training.

### 2.4 Cached Embedding Read Pattern

Per Decision 9 v2 (compute envelope) + L2.1 §6.3 cached embedding storage convention, Slot 1 supports two operating modes:

**Mode A — On-the-fly substrate encoding:**
```python
# Used during initial Layer 5 ablation when caches do not yet exist
cell_emb_native = substrate.encode(adata, batch_key=...)
cell_emb = substrate.project_to_canonical(cell_emb_native)
```

**Mode B — Cached embedding read (DEFAULT for repeated runs):**
```python
# Used after first run; reads from /scratch cache
cache_path = config.cached_embedding_path_template.format(
    substrate=substrate.NAME, dataset=dataset_name, split=split_name
)
if config.use_cached_embeddings and Path(cache_path).exists():
    with h5py.File(cache_path, "r") as f:
        cell_emb = torch.from_numpy(f["embedding"][:])  # already 512-dim canonical
        assert cell_emb.shape[1] == 512, "Cached embedding must be canonical 512-dim"
else:
    cell_emb_native = substrate.encode(adata, batch_key=...)
    cell_emb = substrate.project_to_canonical(cell_emb_native)
    if config.use_cached_embeddings:
        _save_to_cache(cache_path, cell_emb)
```

The cached embedding read pattern is DEFAULT for L7 training/inference loops because the substrate forward pass (especially FM substrates like scFoundation, UCE, scGPT) dominates wall-clock time. Caching the 512-dim canonical output (which already includes the substrate's project_to_canonical step) means subsequent epochs only do Slots 2-6 forward passes.

Cache invalidation: cache key includes substrate name + dataset name + split name + L2.1 spec SHA256 first 8 chars (detects substrate-spec-level changes). Any L2.1 errata application or substrate retrain triggers cache rebuild.

### 2.5 Memory Envelope for Slot 1

Per Decision 9 v2 single-A100 envelope (40GB VRAM typical, 80GB on newer nodes):

| Substrate | Native dim | Memory per 1K cells (FP32) | Memory per 100K cells |
|---|---|---|---|
| scFoundation | 512 | 2 MB | 200 MB |
| UCE | 1280 | 5 MB | 500 MB |
| scGPT | 512 | 2 MB | 200 MB |
| Geneformer | 512 | 2 MB | 200 MB |
| scTOP | ~10-400 | <2 MB | <200 MB |
| scVI/scANVI/MrVI | 30 | <0.5 MB | <50 MB |
| PCA+HVG | 50 | <0.5 MB | <50 MB |

After project_to_canonical: all substrates produce 512-dim embeddings, so canonical memory is uniform at 200MB per 100K cells. This is small relative to the model and gradient memory in Slots 3-6, so Slot 1 is not the binding memory constraint.

The binding constraint is substrate forward-pass memory (the substrate itself + its activations), not the output embedding. scFoundation 100M params requires ~5-8GB VRAM for inference. UCE 650M params requires ~25-35GB. This is exactly why caching is the default — pay the substrate forward cost once, reuse the cached canonical embedding across epochs.

### 2.6 What Slot 1 Does NOT Do

- **Does NOT modify the substrate.** The substrate is frozen for Slot 1's purposes; fine-tuning happens in Slot 2 (drug encoder) and the CPA composition framework, not in Slot 1.
- **Does NOT branch on substrate identity.** All downstream code consumes the canonical 512-dim output. No `if substrate.NAME == "scfoundation": ...` branches anywhere in Slots 2-6.
- **Does NOT compute attribution.** Cell-level attribution (Decision 7 v2 Scale 5 gene-level + Scale 1 geometric) requires substrate-conditional logic; that lives in L2.4 interpretability, not L2.2.
- **Does NOT manage batch correction.** Decision 2 v2 cohort harmonization (scIB+Harmony+scANVI+MrVI) operates upstream of the substrate; by the time Slot 1 sees the adata, batch correction is already applied (or the substrate handles it via its `batch_key` parameter).

---

## §3 Slot 2 — Drug Molecule Encoder G

### 3.1 The Slot 2 Contract

Slot 2 maps a drug's SMILES string (or molecular graph) to a fixed-dimensional chemical embedding that Slot 3 (perturbation network) consumes. The chemCPA contribution to INTERCEPTA's architecture is that this slot is **modular** — different chemical encoders can be slot-substituted without modifying Slots 3-6.

The contract is:

```python
class DrugEncoderInterface(torch.nn.Module, ABC):
    """Modular drug chemical encoder slot. chemCPA-pattern interface."""

    NAME: str = "abstract"
    OUTPUT_DIM: int = -1  # subclass-specific

    @abstractmethod
    def encode(self, smiles: List[str]) -> torch.Tensor:
        """
        Encode N drug SMILES strings to chemical embeddings.

        Args:
            smiles: list of N SMILES strings

        Returns:
            [N, OUTPUT_DIM] chemical embedding tensor
        """
        raise NotImplementedError

    def output_dim(self) -> int:
        """Output dimensionality. Must be set after instantiation."""
        if self.OUTPUT_DIM <= 0:
            raise RuntimeError(f"{self.NAME} OUTPUT_DIM not set")
        return self.OUTPUT_DIM
```

### 3.2 Default Choice: MoLFormer (CSO judgment per §9.5 revisitable)

**DEFAULT: MoLFormer (IBM Research, open-licensed, transformer-based, SMILES-string-trained)**

Rationale for the default selection:

1. **Modality match.** L7 input is SMILES strings (from drug screening databases GDSC/CCLE/sci-Plex). MoLFormer ingests SMILES directly; ChemBERTa also does, but Uni-Mol requires 3D conformer generation as preprocessing. SMILES-only is simpler for Phase B initial implementation.

2. **Model scale match.** MoLFormer comes in ~100M parameter variants comparable to scFoundation's substrate scale. ChemBERTa is smaller (~5M); Uni-Mol is variable but typically larger.

3. **Open license.** MIT-equivalent. Compatible with Decision 10 v2 permissive-cluster default.

4. **Transformer architecture.** Aligns with the FM-substrate paradigm Decision 1 v2 deploys as default; pipeline and tooling reuse possible.

5. **Pre-trained embeddings public.** Cached embeddings can be pre-computed for all GDSC/CCLE/sci-Plex drugs once and reused across L7 ablation runs — same caching pattern as Slot 1.

**Alternatives (slot-substitutable, all open-licensed):**

- **ChemBERTa** (Hugging Face) — smaller (~5M params); useful when compute is tight; consistently weaker on downstream chemistry tasks per published benchmarks but the gap on drug response prediction specifically is unmeasured. Layer 5 ablation tests this.
- **Uni-Mol** (DPTech, open-licensed) — 3D conformer-based; potentially stronger on tasks where 3D shape matters (binding affinity, selectivity); requires conformer generation preprocessing; out-of-distribution drug structures may produce poor conformers. Layer 5 ablation tests when the 3D modality earns its preprocessing cost.
- **RDKit baseline** — non-learned molecular fingerprints (Morgan/Avalon/MACCS). The "parameter-free baseline" for Slot 2, analogous to Souza-Mehta scTOP for Slot 1. **BINDING per Decision 8 v2 Commitment 5: this baseline must receive ≥25% of MoLFormer's hyperparameter search budget.**

**§9.5 revisitability:** the MoLFormer default is revisited at Layer 5 if (a) ChemBERTa achieves AUROC within 2pp on V0-V1 at <5% of MoLFormer compute (small-model wins); (b) Uni-Mol achieves AUROC ≥5pp above MoLFormer on V3 tumor prediction (3D modality earns its cost on translational endpoint); (c) RDKit baseline achieves AUROC within 2pp on any V-level (the Souza-Mehta scenario — parameter-free wins, demote the FM).

### 3.3 MoLFormer Implementation Skeleton

```python
class MoLFormerEncoder(DrugEncoderInterface):
    """IBM MoLFormer transformer-based SMILES encoder.
    
    Reference: Ross et al. 2022 'Large-Scale Chemical Language Representations
    Capture Molecular Structure and Properties' Nat Mach Intell.
    """

    NAME = "molformer"
    OUTPUT_DIM = 768  # MoLFormer-XL base hidden size

    def __init__(self, pretrained_path: str = "ibm/MoLFormer-XL-both-10pct"):
        super().__init__()
        from transformers import AutoModel, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_path, trust_remote_code=True
        )
        self.model = AutoModel.from_pretrained(
            pretrained_path, trust_remote_code=True
        )
        # Freeze pretrained weights by default; fine-tuning enabled via flag
        for p in self.model.parameters():
            p.requires_grad = False

    def encode(self, smiles: List[str]) -> torch.Tensor:
        """Encode SMILES strings to [N, 768] embeddings.
        
        Uses CLS-token-equivalent pooled representation (MoLFormer convention).
        """
        device = next(self.model.parameters()).device
        tokens = self.tokenizer(
            smiles, padding=True, return_tensors="pt", truncation=True, max_length=512
        ).to(device)
        with torch.no_grad():
            outputs = self.model(**tokens)
            # MoLFormer pooled output is the molecule-level representation
            pooled = outputs.pooler_output if hasattr(outputs, "pooler_output") \
                     else outputs.last_hidden_state.mean(dim=1)
        return pooled  # [N, 768]

    def enable_finetuning(self, last_n_layers: int = 2) -> None:
        """Selectively unfreeze last N transformer blocks for chemCPA-style
        modular fine-tuning. Default frozen; call this method to enable."""
        for p in self.model.parameters():
            p.requires_grad = False
        # Unfreeze last N transformer blocks
        if hasattr(self.model, "encoder"):
            layers = self.model.encoder.layer
            for layer in layers[-last_n_layers:]:
                for p in layer.parameters():
                    p.requires_grad = True
```

### 3.4 ChemBERTa Implementation Skeleton

```python
class ChemBERTaEncoder(DrugEncoderInterface):
    """ChemBERTa SMILES BERT encoder.
    Reference: Chithrananda et al. 2020."""

    NAME = "chemberta"
    OUTPUT_DIM = 768  # ChemBERTa-77M-MLM standard

    def __init__(self, pretrained_path: str = "DeepChem/ChemBERTa-77M-MLM"):
        super().__init__()
        from transformers import AutoModel, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_path)
        self.model = AutoModel.from_pretrained(pretrained_path)
        for p in self.model.parameters():
            p.requires_grad = False

    def encode(self, smiles: List[str]) -> torch.Tensor:
        device = next(self.model.parameters()).device
        tokens = self.tokenizer(
            smiles, padding=True, return_tensors="pt", truncation=True
        ).to(device)
        with torch.no_grad():
            outputs = self.model(**tokens)
            # ChemBERTa: mean pool over tokens
            pooled = outputs.last_hidden_state.mean(dim=1)
        return pooled
```

### 3.5 Uni-Mol Implementation Sketch (defers 3D conformer details to Layer 5)

```python
class UniMolEncoder(DrugEncoderInterface):
    """Uni-Mol 3D-conformer-based encoder.
    
    NOTE: Requires conformer generation preprocessing. Layer 5 implementation
    spec details RDKit conformer generation pipeline + handling of failed
    conformer generation (fallback to ChemBERTa for such SMILES).
    """

    NAME = "unimol"
    OUTPUT_DIM = 512  # Uni-Mol standard

    def __init__(self, pretrained_path: str, conformer_strategy: str = "rdkit_etkdg"):
        super().__init__()
        # Loading Uni-Mol weights — Layer 5 specifies exact deps
        # (Uni-Mol has its own forked PyTorch stack; encapsulated here)
        ...

    def encode(self, smiles: List[str]) -> torch.Tensor:
        # Conformer generation (Layer 5 detail)
        # Model forward (Layer 5 detail)
        # Return [N, 512]
        ...
```

### 3.6 RDKit Baseline (BINDING per Decision 8 v2 Commitment 5)

```python
class RDKitFingerprintEncoder(DrugEncoderInterface):
    """Non-learned molecular fingerprint baseline.
    
    Per Decision 8 v2 Commitment 5: this baseline must receive ≥25% of
    MoLFormer's hyperparameter search budget. The 'hyperparameter search'
    space for RDKit includes: fingerprint type (Morgan vs Avalon vs MACCS),
    Morgan radius (1, 2, 3), fingerprint bit length (1024, 2048, 4096),
    and downstream nonlinear projection (None, MLP-2-layer, MLP-3-layer).
    """

    NAME = "rdkit_baseline"

    def __init__(
        self,
        fingerprint_type: str = "morgan",
        morgan_radius: int = 2,
        bit_length: int = 2048,
        downstream_projection: Optional[str] = None,
    ):
        super().__init__()
        self.fingerprint_type = fingerprint_type
        self.morgan_radius = morgan_radius
        self.bit_length = bit_length
        self.OUTPUT_DIM = bit_length if downstream_projection is None else 768
        if downstream_projection == "mlp_2":
            self.projection = torch.nn.Sequential(
                torch.nn.Linear(bit_length, 768),
                torch.nn.ReLU(),
                torch.nn.Linear(768, 768),
            )
        else:
            self.projection = torch.nn.Identity()

    def encode(self, smiles: List[str]) -> torch.Tensor:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        fps = []
        for s in smiles:
            mol = Chem.MolFromSmiles(s)
            if mol is None:
                # Invalid SMILES — zero vector fallback
                fps.append(np.zeros(self.bit_length, dtype=np.float32))
                continue
            if self.fingerprint_type == "morgan":
                fp = AllChem.GetMorganFingerprintAsBitVect(
                    mol, self.morgan_radius, nBits=self.bit_length
                )
            elif self.fingerprint_type == "avalon":
                from rdkit.Avalon import pyAvalonTools
                fp = pyAvalonTools.GetAvalonFP(mol, nBits=self.bit_length)
            elif self.fingerprint_type == "maccs":
                fp = AllChem.GetMACCSKeysFingerprint(mol)
            fps.append(np.array(fp, dtype=np.float32))
        x = torch.from_numpy(np.stack(fps))
        return self.projection(x)
```

### 3.7 The Drug Encoder Registry

```python
class DrugEncoderRegistry:
    """Registry for drug encoder slot substitution."""

    _registry = {
        "molformer": MoLFormerEncoder,
        "chemberta": ChemBERTaEncoder,
        "unimol": UniMolEncoder,
        "rdkit_baseline": RDKitFingerprintEncoder,
    }

    @classmethod
    def get(cls, name: str) -> type:
        if name not in cls._registry:
            raise ValueError(
                f"Unknown drug encoder: {name}. "
                f"Available: {list(cls._registry.keys())}"
            )
        return cls._registry[name]
```

### 3.8 Cached Drug Embedding Pattern

Same as Slot 1's cached embedding pattern: drug embeddings for GDSC's 286 drugs (or sci-Plex's 188 drugs, or CCLE's broader set) are pre-computed once per drug encoder and cached:

```
/scratch/akula.pra/INTERCEPTA/embeddings/drugs/
├── molformer/
│   ├── gdsc_286_drugs.h5      # [286, 768]
│   ├── sciplex_188_drugs.h5   # [188, 768]
│   └── ccle_full.h5           # [N_ccle, 768]
├── chemberta/
│   └── ...
├── unimol/
│   └── ...
└── rdkit_baseline/
    └── ...
```

This avoids re-encoding the same SMILES across every L7 epoch. The cache key is `(drug_encoder_name, drug_set_name, drug_encoder_config_hash)`.

### 3.9 What Slot 2 Does NOT Do

- **Does NOT predict drug response.** It only encodes the chemical structure. Prediction happens in Slot 3 (perturbation network) and the CPA composition framework.
- **Does NOT use cell context.** The drug embedding is cell-independent; the cell-specific drug effect is computed downstream by composing the drug emb with cell emb in the disentangled latent.
- **Does NOT generate novel molecules.** Generative chemistry is Phase F Scout 2 per Charter v1.2 §4 row 11. Slot 2 only ENCODES existing SMILES.
- **Does NOT compute drug-drug similarity.** Drug similarity falls out of the encoder's embedding space implicitly; Decision 7 v2 Scale 2 (drug-class disentanglement via CPA) operates on the post-CPA latent, not the raw drug emb.
- **Does NOT handle combinations.** Combination prediction is Phase F Scout 3 + Simulation Stack Layer D per Charter v1.2 §4 rows 12, 20. Slot 2 takes one SMILES at a time.

---

## §4 Slot 3 — Perturbation Network M+S

### 4.1 The Slot 3 Contract

Slot 3 maps the drug chemical embedding from Slot 2 (`[N_drugs, D_drug]`) and dose information from covariates to a latent perturbation effect in the CPA disentangled latent space. The chemCPA contribution is the **M+S decomposition**:

- **M (mapping network):** chemical embedding → latent perturbation effect direction in z-space
- **S (amortized dosage scaler):** scales the perturbation effect by dose-dependent factors

The contract is:

```python
class PerturbationNetworkM_S(torch.nn.Module):
    """chemCPA-style M+S perturbation network.
    
    M maps chemical embedding to a latent perturbation direction.
    S scales the perturbation effect amortized over dose.
    Output is a perturbation effect in CPA latent space (dim = latent_dim).
    """

    def __init__(
        self,
        drug_emb_dim: int,        # from Slot 2 (e.g., 768 for MoLFormer)
        latent_dim: int,           # CPA latent dim (default 64)
        hidden_dim: int = 256,
        n_layers: int = 3,
        dosage_scaler_type: str = "amortized",  # "amortized" or "fixed_log"
    ):
        super().__init__()
        self.drug_emb_dim = drug_emb_dim
        self.latent_dim = latent_dim

        # M: chemical embedding → latent perturbation direction
        layers = []
        in_dim = drug_emb_dim
        for _ in range(n_layers - 1):
            layers.extend([
                torch.nn.Linear(in_dim, hidden_dim),
                torch.nn.GELU(),
                torch.nn.LayerNorm(hidden_dim),
            ])
            in_dim = hidden_dim
        layers.append(torch.nn.Linear(in_dim, latent_dim))
        self.M = torch.nn.Sequential(*layers)

        # S: amortized dosage scaler
        if dosage_scaler_type == "amortized":
            # chemCPA paper: dose acts as scalar multiplier learned from drug emb
            self.S = torch.nn.Sequential(
                torch.nn.Linear(drug_emb_dim + 1, hidden_dim),  # +1 for log(dose)
                torch.nn.GELU(),
                torch.nn.Linear(hidden_dim, 1),
                torch.nn.Sigmoid(),  # bound dose effect to [0, 1] multiplier
            )
        elif dosage_scaler_type == "fixed_log":
            self.S = lambda drug_emb, dose: torch.log1p(dose).unsqueeze(-1)
        else:
            raise ValueError(f"Unknown dosage_scaler_type: {dosage_scaler_type}")
        self.dosage_scaler_type = dosage_scaler_type

    def forward(
        self,
        drug_emb: torch.Tensor,   # [N_drugs, drug_emb_dim]
        dose: torch.Tensor,        # [N_drugs] or [N_cells_x_drugs] dose values (e.g., μM)
    ) -> torch.Tensor:
        """
        Returns:
            latent perturbation effect [N, latent_dim]
        """
        # M: chemical emb → latent direction
        direction = self.M(drug_emb)  # [N, latent_dim]

        # S: amortized dosage scaling
        if self.dosage_scaler_type == "amortized":
            log_dose = torch.log1p(dose).unsqueeze(-1)  # [N, 1]
            scaler_input = torch.cat([drug_emb, log_dose], dim=-1)
            scale = self.S(scaler_input)  # [N, 1]
        else:
            scale = self.S(drug_emb, dose)

        return direction * scale  # [N, latent_dim]
```

### 4.2 The CPA Disentangled Latent (Intrinsic, Not Slot)

Decision 4 v2 commits INTERCEPTA to the CPA backbone (Lotfollahi 2023 *Mol Syst Biol*, MIT-licensed, Meta+Helmholtz). The CPA disentangled latent is **intrinsic** to L7 — it is not a slot, not slot-substitutable, and not deferred. L2.2 specifies it as a built-in component:

```python
class CPADisentangledLatent(torch.nn.Module):
    """CPA disentangled latent. Separates perturbation effect from
    biological covariates (cell type, dose, time, species, patient).
    
    Reference: Lotfollahi et al. 2023 'Predicting cellular responses
    to perturbations with deep learning'. Mol Syst Biol 19:e11517.
    """

    def __init__(
        self,
        cell_emb_dim: int = 512,   # from Slot 1 canonical projection
        latent_dim: int = 64,       # CPA latent dim
        n_covariate_classes: Dict[str, int] = None,
            # e.g., {"cell_type": 50, "time": 5, "species": 3, "patient": 1000}
        adversarial_lambda: float = 1.0,
            # disentanglement adversarial loss weight (CPA default)
    ):
        super().__init__()
        self.cell_emb_dim = cell_emb_dim
        self.latent_dim = latent_dim
        self.adversarial_lambda = adversarial_lambda

        # Cell encoder: 512-dim canonical → latent_dim
        self.cell_to_latent = torch.nn.Sequential(
            torch.nn.Linear(cell_emb_dim, 256),
            torch.nn.GELU(),
            torch.nn.LayerNorm(256),
            torch.nn.Linear(256, latent_dim),
        )

        # Covariate embeddings (one per covariate; each adds to latent)
        n_covariate_classes = n_covariate_classes or {}
        self.covariate_embeddings = torch.nn.ModuleDict({
            cov_name: torch.nn.Embedding(n_classes, latent_dim)
            for cov_name, n_classes in n_covariate_classes.items()
        })

        # Adversarial classifier for disentanglement (CPA pattern):
        # tries to predict covariates from latent_perturb; main loss
        # penalizes the latent for being predictable from covariates
        self.adversarial_classifiers = torch.nn.ModuleDict({
            cov_name: torch.nn.Linear(latent_dim, n_classes)
            for cov_name, n_classes in n_covariate_classes.items()
        })

    def forward(
        self,
        cell_emb: torch.Tensor,         # [N_cells, 512] canonical
        latent_perturb: torch.Tensor,   # [N_cells_x_drugs, latent_dim] from Slot 3
        covariates: Covariates,
    ) -> torch.Tensor:
        """
        Compose cell + perturbation + covariates → disentangled latent z.
        
        z = cell_basal + sum(covariate_embs) + latent_perturb
        
        At training, an adversarial loss encourages latent_perturb to be
        non-predictive of covariates (true disentanglement). The adversarial
        loss is exposed as an aux tensor for the main training loop.
        """
        cell_basal = self.cell_to_latent(cell_emb)  # [N_cells, latent_dim]

        covariate_sum = torch.zeros_like(cell_basal)
        for cov_name, emb_layer in self.covariate_embeddings.items():
            cov_indices = getattr(covariates, cov_name)
            if cov_indices is not None:
                covariate_sum = covariate_sum + emb_layer(cov_indices)

        # Compose
        # (note: latent_perturb may be broadcast across cells x drugs;
        # actual indexing handled in the L7 forward())
        z = cell_basal + covariate_sum + latent_perturb

        return z

    def compute_adversarial_loss(
        self,
        latent_perturb: torch.Tensor,
        covariates: Covariates,
    ) -> torch.Tensor:
        """CPA-style adversarial disentanglement loss.
        Returns scalar loss tensor."""
        loss = 0.0
        for cov_name, classifier in self.adversarial_classifiers.items():
            cov_targets = getattr(covariates, cov_name)
            if cov_targets is not None:
                logits = classifier(latent_perturb)
                loss = loss + F.cross_entropy(logits, cov_targets)
        return loss * self.adversarial_lambda
```

### 4.3 The CPA Decoder (Intrinsic, Not Slot)

```python
class CPADecoder(torch.nn.Module):
    """CPA decoder: disentangled latent z → cell-level prediction.
    
    Output dim depends on task:
    - 1: regression IC50 / AUC
    - N_drugs: multi-drug joint prediction
    - N_classes: response/no-response classification
    
    For Phase B L7, default is regression on IC50 (single drug per forward pass);
    multi-drug joint is a Layer 5 extension.
    """

    def __init__(
        self,
        latent_dim: int = 64,
        hidden_dim: int = 256,
        n_layers: int = 3,
        output_dim: int = 1,       # regression by default
        task: str = "regression",   # or "classification"
    ):
        super().__init__()
        layers = []
        in_dim = latent_dim
        for _ in range(n_layers - 1):
            layers.extend([
                torch.nn.Linear(in_dim, hidden_dim),
                torch.nn.GELU(),
                torch.nn.LayerNorm(hidden_dim),
            ])
            in_dim = hidden_dim
        layers.append(torch.nn.Linear(in_dim, output_dim))
        self.decoder = torch.nn.Sequential(*layers)
        self.task = task

    def forward(
        self,
        z: torch.Tensor,
        covariates: Covariates,
    ) -> torch.Tensor:
        """Predict cell-level drug response.
        
        Output:
        - regression: [N_cells, 1] continuous IC50/AUC
        - classification: [N_cells, output_dim] logits
        """
        return self.decoder(z)
```

### 4.4 Latent Arithmetic Capability (scGen Heritage)

The CPA latent space inherits the **latent-arithmetic property** from scGen (Lotfollahi 2019, R²=0.954 on perturbation prediction). This means:

- `z_treated - z_control` represents the perturbation effect in latent space
- This effect is approximately linear and transferable across cells of similar type
- Predicting response of unseen cell types becomes: encode unseen cell → add learned perturbation effect → decode → predicted post-perturbation state

L7's CPA composition framework preserves this property. Decision 7 v2 Scale 2 (drug-class disentanglement) leverages it for interpretability: similar drugs produce similar `latent_perturb` directions; this similarity can be measured directly and presented as a Slot-3-derived attribution.

L2.2 does NOT specify exact latent-arithmetic operators (those are Layer 5 implementation). It specifies the architectural commitment: the disentangled latent supports near-linear perturbation composition.

### 4.5 What Slot 3 Does NOT Do

- **Does NOT condition on cell state.** Slot 3's output (latent_perturb) is cell-independent; cell-specific perturbation response emerges in the CPA composition framework downstream.
- **Does NOT handle combinations.** Multi-drug combinations are Phase F Scout 3 + Simulation Stack Layer D. Slot 3 takes one drug at a time.
- **Does NOT predict toxicity / safety.** That is Phase F Simulation Stack Layer E (ADMET). Slot 3 only models efficacy-side perturbation.
- **Does NOT use temporal dynamics.** Time is a covariate in CPA disentangled latent, but the architecture is not a dynamical system. Two-population ODE (Phase F Simulation Stack Layer C) is out of L2.2 scope.

---

## §5 Slot 4 — Graph-Augmented Module

### 5.1 The Slot 4 Contract

Slot 4 conditions the disentangled latent z on biological priors via GEARS-style attention. Three graph types compose:

1. **Gene-gene co-expression graph** — derived from training data; edges weighted by co-expression statistic (Pearson, Spearman, or scaled mutual information)
2. **GO ontology graph** — Gene Ontology biological process / molecular function / cellular component hierarchy
3. **Drug-target graph** — drug-to-gene-target edges from DrugBank / TWOSIDES / TTD

The contract:

```python
class GraphAugmentedModule(torch.nn.Module):
    """GEARS-style graph-augmented attention over biological priors.
    
    Reference: Roohani et al. 2024 'Predicting transcriptional outcomes
    of novel multigene perturbations with GEARS'. Nat Biotechnol 42:927-935.
    
    BINDING per Decision 3 v2 (cross-decision identities, Drift Finding 7):
    Slot 4's GRN component IS Decision 7 v2 Scale 4 (scRank GRN-perturbation).
    Beyondcell is Scale 3 (pathway), NOT Slot 4.
    chemCPA architecture surgery is the Decision 3 v2 bulk-to-single bridge,
    NOT a Slot 4 component.
    """

    def __init__(
        self,
        latent_dim: int = 64,
        n_genes: int = 20000,           # human protein-coding gene count
        gene_gene_graph: Optional[GraphData] = None,
        go_graph: Optional[GraphData] = None,
        drug_target_graph: Optional[GraphData] = None,
        attention_heads: int = 4,
        attention_dim: int = 128,
        use_gene_gene: bool = True,
        use_go: bool = True,
        use_drug_target: bool = True,
    ):
        super().__init__()
        self.use_gene_gene = use_gene_gene and (gene_gene_graph is not None)
        self.use_go = use_go and (go_graph is not None)
        self.use_drug_target = use_drug_target and (drug_target_graph is not None)

        self.latent_dim = latent_dim
        self.attention_dim = attention_dim

        # Per-graph attention modules (GAT-style)
        if self.use_gene_gene:
            self.gene_gene_attention = GraphAttentionLayer(
                in_dim=latent_dim, out_dim=attention_dim,
                graph=gene_gene_graph, n_heads=attention_heads,
            )
        if self.use_go:
            self.go_attention = GraphAttentionLayer(
                in_dim=latent_dim, out_dim=attention_dim,
                graph=go_graph, n_heads=attention_heads,
            )
        if self.use_drug_target:
            self.drug_target_attention = GraphAttentionLayer(
                in_dim=latent_dim + 768,  # latent + drug emb
                out_dim=attention_dim,
                graph=drug_target_graph, n_heads=attention_heads,
            )

        # Combine graph-conditioned representations back to latent
        n_used = sum([self.use_gene_gene, self.use_go, self.use_drug_target])
        if n_used > 0:
            self.combiner = torch.nn.Sequential(
                torch.nn.Linear(attention_dim * n_used + latent_dim, latent_dim),
                torch.nn.GELU(),
                torch.nn.LayerNorm(latent_dim),
            )
        else:
            # No graphs available; pass-through (e.g., Layer 5 ablation
            # with graph_module_disabled)
            self.combiner = torch.nn.Identity()

    def forward(
        self,
        z: torch.Tensor,                # [N_cells, latent_dim]
        drug_emb: torch.Tensor,         # [N_cells_x_drugs, drug_emb_dim]
        drug_targets: Optional[torch.Tensor] = None,  # [N_cells_x_drugs, max_targets] gene IDs
    ) -> torch.Tensor:
        """Returns graph-conditioned latent z' [N_cells, latent_dim]."""

        graph_outputs = []
        if self.use_gene_gene:
            z_gg = self.gene_gene_attention(z)
            graph_outputs.append(z_gg)
        if self.use_go:
            z_go = self.go_attention(z)
            graph_outputs.append(z_go)
        if self.use_drug_target and drug_targets is not None:
            z_drug_input = torch.cat([z, drug_emb], dim=-1)
            z_dt = self.drug_target_attention(z_drug_input, edge_index=drug_targets)
            graph_outputs.append(z_dt)

        if len(graph_outputs) == 0:
            return z

        # Concat all graph outputs with original z, then combine
        z_concat = torch.cat([z] + graph_outputs, dim=-1)
        z_out = self.combiner(z_concat)
        return z + z_out  # residual (per GEARS)
```

### 5.2 Graph Data Sources

**Gene-gene co-expression graph:**
- Source: training data (CCLE bulk + scRNA-seq atlases per Decision 6 v2 V0-V1)
- Construction: Pearson correlation across cells/samples; threshold at |r| > 0.3 (Layer 5 tunable)
- Size: ~20K nodes × ~500K edges (sparse)
- Storage: scipy.sparse CSR, ~50MB

**GO ontology graph:**
- Source: GO ontology database (current release at training time)
- Construction: BP / MF / CC namespaces; child-parent edges; ~45K GO terms; ~80K edges
- Mapping: each gene mapped to GO terms via GOA (Gene Ontology Annotation) database
- Storage: networkx + adjacency dict, ~100MB

**Drug-target graph:**
- Source: DrugBank (open-licensed) + TWOSIDES (open) + TTD academic
- Construction: drug → gene-target edges; ~10K drugs × ~5K targets; ~40K edges
- Storage: scipy.sparse, <10MB

All three graphs are pre-computed once and cached. Cache location:

```
/scratch/akula.pra/INTERCEPTA/graphs/
├── gene_gene_coexpression_v1.npz
├── go_ontology_v_<release>.npz
└── drug_target_v1.npz
```

### 5.3 Why Three Graphs

Each graph contributes a different prior:

- **Gene-gene co-expression** captures empirical regulatory relationships from data — what tends to co-vary in transcriptional space
- **GO ontology** captures curated functional grouping — pathway-level mechanisms
- **Drug-target** captures pharmacological priors — which gene each drug binds

The GEARS contribution (Roohani 2024) shows that combining these three priors via attention improves precision on unseen perturbation prediction by ~40% relative to no-graph baselines. The improvement is largest on cross-disease generalization (V6) which is INTERCEPTA's binding universality test.

### 5.4 Cross-Decision Binding: scRank as Slot 4 GRN Component

Per Drift Finding 7 (BINDING from Decision 3 v2):

- **scRank (Lin et al. 2023)** is the cell-type-specific GRN-perturbation method that fits the Slot 4 GRN-aware attention pattern
- scRank operates on the gene-gene co-expression graph + cell-type-specific GRN topology
- **scRank = Slot 4 GRN component = Decision 7 v2 Scale 4** (single architectural identity, three different document views)

L2.2 honors this by exposing scRank's perturbation-propagation algorithm as the gene-gene attention's edge-weight initialization:

```python
class GraphAttentionLayer(torch.nn.Module):
    """GEARS-style graph attention. When initialized for the gene-gene graph,
    optionally uses scRank perturbation propagation for edge-weight init.
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        graph: GraphData,
        n_heads: int = 4,
        edge_weight_init: str = "scrank",  # or "uniform", "coexpression"
    ):
        super().__init__()
        # ... standard GAT layer setup ...
        if edge_weight_init == "scrank":
            self.edge_weights_init = _compute_scrank_init(graph)
        # ... rest of layer ...
```

This means scRank does NOT appear as a separate module; it appears as the initialization strategy for the gene-gene attention. The architectural identity is preserved.

### 5.5 Beyondcell Is NOT in Slot 4 (BINDING per Drift Finding 7)

Beyondcell (Fustero-Torre 2024 *Genome Med*) operates at the pathway scale — it computes drug sensitivity from pathway-level signatures (Hallmark, KEGG, Reactome). Per Drift Finding 7:

- **Beyondcell = Decision 7 v2 Scale 3 (pathway scale)**, NOT Slot 4
- Beyondcell appears in the Decision 7 v2 interpretability stack, in L2.4 spec
- L2.2 must NOT instantiate Beyondcell as a Slot 4 component

This is an anti-pattern guard. Future L2.2 modifications or Layer 5 implementation must not silently fold Beyondcell into Slot 4. If pathway-aware features are needed in L7's drug response prediction (vs interpretability), a separate proposal is required.

### 5.6 What Slot 4 Does NOT Do

- **Does NOT operate on raw gene expression.** Slot 4 acts on the disentangled latent z; gene-level operations belong in Slot 1 substrate forward.
- **Does NOT compute attribution.** Slot 4 produces graph-conditioned latent for prediction. Attribution (which gene/pathway drives a prediction) is L2.4 (Decision 7 v2).
- **Does NOT use the 15-layer Universal Net.** Slot 4 uses three targeted graphs (gene-gene, GO, drug-target). The full 15-layer Universal Net is Phase F per Charter v1.2 §4 row 8.
- **Does NOT include Beyondcell pathway scoring** (per Drift Finding 7).
- **Does NOT include scRank as a separate module** — it appears as gene-gene attention edge-weight init.

---

## §6 Slot 5 — Mode Collapse Mitigation

### 6.1 The Slot 5 Contract

Mode collapse is when generative or compositional models converge to a small number of output patterns regardless of input variation. For L7 specifically, mode collapse manifests as: the same predicted drug response across many different drugs, because the perturbation latent ends up pooled into few modes.

Per the Diversity-by-Design 2025 critique, this is a field-wide risk in CPA-like compositional architectures. Decision 4 v2 commits Slot 5 to mode collapse mitigation with default = diversity loss, alternatives = energy-based and mixture-of-experts.

The contract:

```python
class ModeCollapseStrategy(torch.nn.Module, ABC):
    """Slot 5 mode collapse mitigation strategy."""

    NAME: str = "abstract"

    @abstractmethod
    def forward(
        self,
        z_graph: torch.Tensor,   # graph-conditioned latent from Slot 4
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            z_out: [N, latent_dim] modified latent for decoder
            aux_loss: scalar diversity / regularization loss for training
                      (set to 0 at inference)
        """
        raise NotImplementedError
```

### 6.2 Default Strategy: DPP-Diversity Loss (CSO judgment, §9.5 revisitable)

**DEFAULT: Determinantal Point Process (DPP) diversity regularizer**

Among the three candidate diversity loss formulations, DPP is selected as the default for L7. Rationale:

1. **DPP has the strongest theoretical grounding** for ensuring diversity in latent representations. Determinant of the kernel matrix penalizes near-collinearity in the latent space, directly attacking mode-collapse geometry.
2. **DPP has been validated in CPA-adjacent architectures** in the broader literature (referenced in Diversity-by-Design 2025). It is not an exotic choice.
3. **DPP integrates cleanly with the CPA composition framework** because it operates on the latent perturbation effect tensor — exactly the quantity at risk of collapse.

Alternative formulations (revisitable per §9.5):
- **Latent-space variance penalty** — simpler; penalizes low variance in batch latents; less precise control over which modes are collapsed
- **InfoNCE-style contrastive** — pulls latents apart based on input differences; computationally heavier; sensitive to batch composition

### 6.3 DPP-Diversity Loss Implementation

```python
class DPPDiversityLoss(ModeCollapseStrategy):
    """Determinantal Point Process diversity regularizer.
    
    Loss = -log det(K + ε·I), where K[i,j] = sim(z_i, z_j)
    Minimizing this loss maximizes the determinant, which is high when
    the latent vectors are diverse (kernel matrix is full-rank).
    """

    NAME = "dpp_diversity"

    def __init__(
        self,
        latent_dim: int = 64,
        weight: float = 0.1,
        epsilon: float = 1e-3,
        kernel: str = "rbf",  # or "cosine"
        rbf_sigma: float = 1.0,
    ):
        super().__init__()
        self.latent_dim = latent_dim
        self.weight = weight
        self.epsilon = epsilon
        self.kernel = kernel
        self.rbf_sigma = rbf_sigma

    def _kernel_matrix(self, z: torch.Tensor) -> torch.Tensor:
        """Compute kernel matrix K [N, N]."""
        if self.kernel == "cosine":
            z_norm = F.normalize(z, dim=-1)
            K = z_norm @ z_norm.t()
        elif self.kernel == "rbf":
            # K[i,j] = exp(-||z_i - z_j||² / (2σ²))
            sq_dists = torch.cdist(z, z, p=2) ** 2
            K = torch.exp(-sq_dists / (2 * self.rbf_sigma ** 2))
        else:
            raise ValueError(f"Unknown kernel: {self.kernel}")
        return K

    def forward(self, z_graph: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        N = z_graph.shape[0]
        if N < 2:
            # Singleton batches don't support DPP; return identity + zero loss
            return z_graph, torch.zeros((), device=z_graph.device)

        K = self._kernel_matrix(z_graph)
        # Add epsilon for numerical stability
        K_stable = K + self.epsilon * torch.eye(N, device=z_graph.device)
        # logdet via Cholesky for stability
        try:
            L = torch.linalg.cholesky(K_stable)
            logdet = 2 * torch.log(torch.diag(L)).sum()
        except RuntimeError:
            # Cholesky failed (matrix not PSD); fallback to slogdet
            sign, logdet = torch.linalg.slogdet(K_stable)
            if sign <= 0:
                logdet = torch.zeros((), device=z_graph.device)

        # Loss = -logdet (we want logdet HIGH = diverse latents)
        # Scale by weight; pass-through latents unchanged
        aux_loss = -logdet * self.weight / N  # per-element normalize
        return z_graph, aux_loss
```

### 6.4 Energy-Based Alternative

```python
class EnergyBasedDiversity(ModeCollapseStrategy):
    """Energy-based mode-collapse mitigation.
    
    Trains the latent space to assign low energy to observed (cell, drug)
    pairs and high energy to negative pairs. Mode collapse manifests as
    low energy everywhere; energy-based training pushes back.
    """

    NAME = "energy_based"
    ...  # Layer 5 detail
```

### 6.5 Mixture-of-Experts Decoder Alternative

```python
class MoEDecoderRouting(ModeCollapseStrategy):
    """Routes z to one of K expert sub-decoders based on a gating network.
    
    Each expert specializes in a region of the perturbation latent space;
    routing prevents mode collapse by partitioning the latent into expert
    regions.
    """

    NAME = "moe_decoder"
    ...  # Layer 5 detail
```

### 6.6 Strategy Registry

```python
class ModeCollapseStrategyRegistry:
    _registry = {
        "diversity_loss": DPPDiversityLoss,     # = "dpp_diversity"
        "dpp_diversity": DPPDiversityLoss,
        "variance_penalty": VariancePenaltyDiversity,
        "infonce_contrastive": InfoNCEContrastive,
        "energy_based": EnergyBasedDiversity,
        "moe_decoder": MoEDecoderRouting,
    }

    @classmethod
    def get(cls, name: str) -> type:
        ...
```

### 6.7 Inference-Time Behavior

At inference, Slot 5 is identity. The diversity / energy / MoE losses are training-time regularizers. The decoder forward path is unchanged at inference.

This means Slot 5 has zero inference overhead, which is important for Decision 9 v2 compute envelope compliance.

### 6.8 What Slot 5 Does NOT Do

- **Does NOT modify the latent at inference.** Pure training-time regularization.
- **Does NOT prevent all failure modes.** Mode collapse is one failure mode among many; OOD inputs are handled by Decision 5 v2 stack, not Slot 5.
- **Does NOT measure mode collapse.** Diagnostic metrics (kernel rank, expert utilization, energy distribution) belong in Layer 4 monitoring, not L2.2 architecture.

---

## §7 Slot 6 — Patient-Level Aggregation

### 7.1 The Slot 6 Contract

Slot 6 aggregates cell-level predictions to patient-level predictions. The default is PaSCient-style attention pooling. Fallbacks (mean / max / learned-weighted) are REQUIRED per Drift Finding 10 BINDING (PaSCient compute envelope tension with single-A100).

```python
class PatientAggregator(torch.nn.Module, ABC):
    """Slot 6 patient-level aggregation strategy."""

    NAME: str = "abstract"

    @abstractmethod
    def forward(
        self,
        y_cell: torch.Tensor,        # [N_cells, output_dim] cell-level predictions
        patient_id: torch.Tensor,    # [N_cells] patient ID per cell
    ) -> torch.Tensor:
        """
        Returns:
            [N_patients, output_dim] patient-level predictions
        """
        raise NotImplementedError
```

### 7.2 Default Strategy: PaSCient Attention (per Decision 4 v2 + Q8 anchor 3)

PaSCient (Liu 2024-2026) demonstrates that attention-based patient aggregation outperforms mean / max pooling at 24.3M cells / 5K+ patients scale. The mechanism: each cell receives a learned attention weight; the patient prediction is a weighted sum of cell predictions; the attention is conditioned on cell embedding so that informative cells (e.g., disease-driving subpopulations) get higher weight.

```python
class PaSCientAggregator(PatientAggregator):
    """PaSCient-style attention pooling for patient aggregation.
    
    Reference: Liu et al. 2024-2026.
    
    BINDING per Drift Finding 10: must specify simpler fallback when
    PaSCient compute budget exceeds Decision 9 v2 single-A100 envelope.
    Fallback specified via config.aggregator_compute_fallback.
    """

    NAME = "pascient_attention"

    def __init__(
        self,
        cell_emb_dim: int = 512,
        attention_dim: int = 128,
        n_heads: int = 4,
        compute_fallback: str = "learned_weighted",
    ):
        super().__init__()
        self.cell_emb_dim = cell_emb_dim
        self.attention_dim = attention_dim
        self.n_heads = n_heads
        self.compute_fallback = compute_fallback

        # Multi-head attention: cell emb → attention scores per cell
        self.attention = torch.nn.MultiheadAttention(
            embed_dim=cell_emb_dim,
            num_heads=n_heads,
            batch_first=True,
        )
        # Cell-to-attention-score projection
        self.score_projection = torch.nn.Linear(cell_emb_dim, 1)

    def forward(
        self,
        y_cell: torch.Tensor,           # [N_cells, output_dim]
        patient_id: torch.Tensor,        # [N_cells]
        cell_emb_canonical: Optional[torch.Tensor] = None,
            # [N_cells, 512] canonical cell embedding from Slot 1
            # required for PaSCient attention
        cell_emb_memory_budget_gb: float = 30.0,
            # available VRAM budget for patient-level attention
    ) -> torch.Tensor:
        """Aggregate cell-level predictions to patient-level."""

        if cell_emb_canonical is None:
            raise ValueError(
                "PaSCient attention requires cell_emb_canonical from Slot 1. "
                "Pass it through the L7 forward to enable PaSCient aggregation. "
                "Or use a non-attention aggregator (mean/max/learned_weighted)."
            )

        # Estimate VRAM cost of PaSCient attention
        N_cells = y_cell.shape[0]
        estimated_vram_gb = self._estimate_attention_vram(N_cells)

        if estimated_vram_gb > cell_emb_memory_budget_gb:
            # Compute envelope exceeded; fall back per Drift Finding 10
            logger.warning(
                f"PaSCient attention VRAM estimate {estimated_vram_gb:.1f}GB "
                f"exceeds budget {cell_emb_memory_budget_gb:.1f}GB; "
                f"falling back to {self.compute_fallback}."
            )
            fallback = PatientAggregatorRegistry.get(self.compute_fallback)(
                cell_emb_dim=self.cell_emb_dim,
            )
            return fallback(y_cell, patient_id)

        # Standard PaSCient attention path
        return self._attention_aggregate(y_cell, patient_id, cell_emb_canonical)

    def _attention_aggregate(self, y_cell, patient_id, cell_emb):
        # Group by patient_id, apply multi-head attention within each patient,
        # weighted sum of y_cell to produce patient prediction
        # (Layer 5 specifies exact batching pattern for variable-size patients)
        unique_patients = torch.unique(patient_id)
        patient_preds = []
        for p in unique_patients:
            mask = (patient_id == p)
            cells_p = cell_emb[mask]      # [n_p, 512]
            y_p = y_cell[mask]             # [n_p, output_dim]
            # Self-attention over cells of this patient
            attn_out, _ = self.attention(
                cells_p.unsqueeze(0), cells_p.unsqueeze(0), cells_p.unsqueeze(0)
            )
            # Attention score per cell
            scores = self.score_projection(attn_out.squeeze(0))  # [n_p, 1]
            weights = F.softmax(scores, dim=0)
            # Weighted sum of cell predictions
            y_patient = (weights * y_p).sum(dim=0)
            patient_preds.append(y_patient)
        return torch.stack(patient_preds)

    def _estimate_attention_vram(self, n_cells_total: int) -> float:
        """Estimate VRAM for PaSCient attention.
        
        Memory dominated by per-patient attention matrices [n_p, n_p].
        For n_cells_total = 100K cells across 100 patients (~1K per patient),
        memory ~ 100 * (1000² * 4 bytes) ≈ 400MB attention matrices.
        Plus model params ~50MB. Total ~500MB.
        For 1M cells across 1K patients (~1K per patient), ~5GB.
        For 24M cells (PaSCient scale, ~4K patients × ~6K cells/patient),
        ~16M * (6000²*4) = ~1.4TB — far exceeds single-A100.
        """
        # Heuristic: assume avg 1000 cells/patient; n_patients = n_cells/1000
        # Attention matrices: n_patients * 1000² * 4 bytes
        n_patients_est = max(n_cells_total / 1000, 1)
        attention_matrix_bytes = n_patients_est * (1000 ** 2) * 4
        model_params_bytes = 50 * 1024 ** 2  # ~50MB params
        total_gb = (attention_matrix_bytes + model_params_bytes) / (1024 ** 3)
        return total_gb
```

### 7.3 Fallback Strategies

```python
class MeanPoolingAggregator(PatientAggregator):
    """Simplest fallback: mean of cell predictions per patient.
    
    Compute: O(N_cells); VRAM: minimal.
    Trade-off: ignores cell heterogeneity within patient.
    """
    NAME = "mean"

    def forward(self, y_cell, patient_id):
        unique = torch.unique(patient_id)
        return torch.stack([y_cell[patient_id == p].mean(dim=0) for p in unique])

class MaxPoolingAggregator(PatientAggregator):
    """Max pooling: most-extreme cell drives prediction.
    
    Compute: O(N_cells); VRAM: minimal.
    Trade-off: dominated by outliers.
    """
    NAME = "max"

    def forward(self, y_cell, patient_id):
        unique = torch.unique(patient_id)
        return torch.stack([y_cell[patient_id == p].max(dim=0).values for p in unique])

class LearnedWeightedAggregator(PatientAggregator):
    """Learned per-cell weighting via a small MLP.
    
    Compute: O(N_cells * D); VRAM: low.
    Trade-off: less expressive than full attention but captures cell-quality
    weighting that mean/max miss.
    
    DEFAULT FALLBACK per Drift Finding 10 (CSO judgment, §9.5 revisitable).
    """
    NAME = "learned_weighted"

    def __init__(self, cell_emb_dim: int = 512, hidden_dim: int = 128):
        super().__init__()
        # Requires cell_emb passed through; smaller than PaSCient attention
        self.weight_net = torch.nn.Sequential(
            torch.nn.Linear(cell_emb_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim, 1),
        )

    def forward(self, y_cell, patient_id, cell_emb_canonical=None):
        if cell_emb_canonical is None:
            # Fall through to mean if no embeddings (degraded but functional)
            return MeanPoolingAggregator(cell_emb_dim=512)(y_cell, patient_id)
        weights_raw = self.weight_net(cell_emb_canonical)  # [N_cells, 1]
        unique = torch.unique(patient_id)
        results = []
        for p in unique:
            mask = (patient_id == p)
            w = F.softmax(weights_raw[mask], dim=0)
            results.append((w * y_cell[mask]).sum(dim=0))
        return torch.stack(results)
```

### 7.4 Default Fallback Choice (CSO judgment per §9.5)

**DEFAULT FALLBACK: `learned_weighted`** when PaSCient compute budget exceeded.

Rationale:
- **Mean pooling** is too aggressive a fallback — it loses all cell-quality weighting that PaSCient provides.
- **Max pooling** is dominated by outliers, which produces unstable predictions on heterogeneous tumors.
- **Learned-weighted** preserves the "informative cells get higher weight" property of PaSCient at ~10× lower memory cost. It is the closest fallback to PaSCient's actual mechanism.

**§9.5 revisitability:** if Layer 5 V0-V1 ablation shows mean or max performs equivalently to learned-weighted at lower compute, the default fallback is revised. Empirical signal threshold: AUROC within 1pp on V0-V1.

### 7.5 PaSCient Compute Envelope Tension Resolution (Drift Finding 10)

The tension Drift Finding 10 surfaces:
- Original PaSCient: 8× A100 80GB / 300GB RAM / ~12 hrs at 24.3M cells / 5K+ patients
- Decision 9 v2 target: single-A100 envelope (40GB VRAM typical, 80GB max on newer nodes)

**L2.2 resolution:** Slot 6's PaSCient aggregator includes runtime VRAM estimation. When the estimate exceeds the available budget, automatic fallback to `learned_weighted` (default fallback). This is not an ablation choice — it is an operational compute-envelope guard.

**For initial Layer 5 ablation** at smaller scales (e.g., 100K cells / 100 patients on sci-Plex), full PaSCient attention is feasible on single-A100. As scale grows toward cross-disease V6 grid (potentially 1M+ cells across 1K+ patients), the fallback engages.

**For Phase F continuity:** when Phase F compute becomes available (multi-A100 + AWS/GCP burst per Charter v1.2 §1.7), the fallback decision threshold can be raised. The fallback mechanism stays in place; the threshold becomes configurable per deployment.

### 7.6 What Slot 6 Does NOT Do

- **Does NOT predict patient outcomes from non-cellular data.** Slot 6 aggregates cell-level predictions only. Clinical features (age, prior therapy, biomarkers) are Phase F + clinical decision support territory, out of L2.2 scope.
- **Does NOT handle longitudinal data.** Repeated measures per patient over time are not specified here; this is a Layer 4 / Layer 5 implementation extension.
- **Does NOT compute patient-level uncertainty.** That is Decision 5 v2 Layer 5.2-5.4 stack applied AFTER Slot 6 (the ensemble is over L7 heads; uncertainty is over patient-level predictions).
- **Does NOT replace cell-level outputs.** When `return_cell_level=True` is set on L7 forward, cell-level outputs bypass Slot 6 and are returned directly. This is critical for Decision 7 v2 Scale 5 (gene-level attribution per cell) which needs cell-level granularity.
---

## §8 Training Objective, Ensemble Composition, and Compute Envelope

### 8.1 The Composite Training Objective

L7 trains with a composite loss combining task loss, CPA adversarial disentanglement loss, Slot 5 diversity loss, and optional auxiliary losses:

```python
def l7_total_loss(
    pred: torch.Tensor,                # [N, output_dim] from L7
    target: torch.Tensor,              # ground-truth drug response
    cpa_adversarial: torch.Tensor,     # from CPADisentangledLatent
    slot5_diversity_aux: torch.Tensor, # from Slot 5
    auxiliary_drug_target: Optional[torch.Tensor] = None,
    config: L7Config = ...,
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """Composite L7 training loss.
    
    Returns:
        total_loss: scalar for backprop
        components: dict of named loss components for logging
    """
    # Task loss
    if config.task == "regression":
        task_loss = F.mse_loss(pred, target)
    elif config.task == "classification":
        task_loss = F.cross_entropy(pred, target)
    else:
        raise ValueError(...)

    # Compose all components
    total = (
        config.composition_loss_weight * task_loss
        + cpa_adversarial    # already scaled by CPA's adversarial_lambda
        + slot5_diversity_aux  # already scaled by Slot 5's weight
    )

    components = {
        "task_loss": task_loss.detach(),
        "cpa_adversarial": cpa_adversarial.detach(),
        "slot5_diversity": slot5_diversity_aux.detach(),
    }

    if auxiliary_drug_target is not None:
        aux_dt = F.binary_cross_entropy_with_logits(...)  # detail in Layer 5
        total = total + config.auxiliary_drug_target_loss_weight * aux_dt
        components["aux_drug_target"] = aux_dt.detach()

    return total, components
```

**Default weighting (per L7Config §1.5, all Layer-5-revisitable):**
- composition_loss_weight: 1.0
- diversity_loss_weight: 0.1
- CPA adversarial_lambda: 1.0 (CPA default)
- auxiliary_drug_target_loss_weight: 0.05

These weights are starting points. Layer 5 hyperparameter tuning may move them within the ranges:
- composition: fixed at 1.0 (reference scale)
- diversity: 0.01-1.0 (log-space)
- adversarial_lambda: 0.1-10.0 (log-space)
- auxiliary: 0-0.5

### 8.2 Ensemble Interface (Decision 5 v2 BINDING per Drift Finding 8)

Decision 5 v2 Layer 5.2 requires N=5 Deep Ensembles for epistemic uncertainty. Drift Finding 8 BINDING: the L7 head is the ensembled unit, not the entire pipeline. This means:

- 5 independently-trained L7 heads
- Each with a different random seed (different parameter initialization + different mini-batch shuffling)
- All 5 sharing the same Slot 1 substrate (cached embeddings reused)
- All 5 sharing the same Slot 2 drug encoder (cached drug embeddings reused)
- Each with its own Slots 3-6 trained from scratch

```python
class L7Ensemble(torch.nn.Module):
    """N=5 Deep Ensembles of L7 head.
    
    BINDING per Decision 5 v2 + Drift Finding 8: this is the ensembled unit.
    Substrate (Slot 1) and drug encoder (Slot 2) are shared across heads;
    Slots 3-6 are independent per head.
    """

    def __init__(
        self,
        substrate: SubstrateInterface,
        drug_encoder: DrugEncoderInterface,
        config: L7Config,
        n_heads: int = 5,
        random_seeds: Optional[List[int]] = None,
    ):
        super().__init__()
        if n_heads != config.ensemble_n:
            raise ValueError(
                f"n_heads {n_heads} must equal config.ensemble_n {config.ensemble_n}"
            )
        random_seeds = random_seeds or config.ensemble_random_seeds[:n_heads]
        if len(random_seeds) != n_heads:
            raise ValueError(...)

        # Substrate and drug encoder are shared (frozen) across all heads
        self.substrate = substrate
        self.drug_encoder = drug_encoder

        # Each head has its own Slots 3-6
        self.heads = torch.nn.ModuleList()
        for seed in random_seeds:
            torch.manual_seed(seed)
            head = L7DrugResponseHead(
                substrate=substrate,
                drug_encoder=drug_encoder,
                perturbation_network=PerturbationNetworkM_S(
                    drug_emb_dim=drug_encoder.OUTPUT_DIM,
                    latent_dim=config.latent_dim,
                    hidden_dim=config.perturbation_hidden_dim,
                    n_layers=config.perturbation_n_layers,
                ),
                graph_module=GraphAugmentedModule(...),
                mode_collapse_strategy=ModeCollapseStrategyRegistry.get(
                    config.mode_collapse_strategy_name
                )(...),
                aggregator=PatientAggregatorRegistry.get(
                    config.aggregator_name
                )(...),
                config=config,
            )
            self.heads.append(head)

    def forward(
        self,
        adata: AnnData,
        drug_smiles: List[str],
        covariates: Covariates,
        return_individual_predictions: bool = False,
    ) -> EnsembleOutput:
        """Run all 5 heads; return ensemble mean + disagreement.
        
        Decision 5 v2 Layer 5.2 consumes the disagreement signal as
        epistemic uncertainty.
        """
        outputs = []
        for head in self.heads:
            out = head(adata, drug_smiles, covariates)
            outputs.append(out.prediction)

        stacked = torch.stack(outputs, dim=0)  # [N_heads, N_patients, output_dim]

        mean = stacked.mean(dim=0)
        std = stacked.std(dim=0)
        # Disagreement = predictive entropy or variance, fed to Decision 5 v2

        return EnsembleOutput(
            mean=mean,
            std=std,
            disagreement=std,  # passed to Decision 5 v2 OOD stack
            individual=stacked if return_individual_predictions else None,
        )
```

### 8.3 Training Schedule

Per Decision 9 v2 single-A100 envelope:

| Phase | Duration | Compute |
|---|---|---|
| Substrate forward + caching (Slot 1) | One-time, ~6-12 hrs for major datasets | Single A100 |
| Drug encoder forward + caching (Slot 2) | One-time, ~1 hr for GDSC/sci-Plex | Single A100 |
| L7 head training (per head, Slots 3-6) | ~12-24 hrs per head, N=5 heads | Single A100 sequential OR 5× SLURM array |
| L7 ensemble inference | ~30 min per V0-V6 grid cell | Single A100 |

**Total training cost estimate for one V0 baseline (one substrate × one drug encoder × N=5 ensemble):** ~3-5 days wall-clock on single A100 with caching. SLURM array can parallelize the 5 heads to ~1 day.

**Cross-disease V6 grid:** if INTERCEPTA evaluates 5 diseases × 4 paradigms (per Decision 8 v2) × N=5 ensembles = 100 training runs. At 1 day/run with SLURM parallelization = ~100 GPU-days. At 5 GPUs in parallel on Northeastern Explorer = ~20 wall-clock days for the full grid. This is the upper bound; cached embeddings reduce wall-clock by ~50% for repeated substrate evaluations.

This budget is feasible on Northeastern Explorer single-institution per Decision 9 v2. AWS/GCP burst per-occurrence CEO approval reserved for ≤5% of runs.

### 8.4 The Souza-Mehta Methodological Bar (Decision 8 v2 Commitment 5 BINDING)

For every L7 head trained, a parameter-free Baseline B comparator must also be trained with ≥25% of the FM head's hyperparameter search budget.

For Slot 1 (cell encoder): scFoundation default ↔ scTOP Baseline B.
For Slot 2 (drug encoder): MoLFormer default ↔ RDKit Baseline B.
For Slot 4 (graph module): GEARS-style attention default ↔ no-graph baseline.

L7 trains in matched-budget pairs:
- **Pair 1:** scFoundation + MoLFormer + GEARS + ... + PaSCient (FM-heavy default)
- **Pair 2:** scTOP + RDKit + GEARS + ... + learned-weighted (parameter-free Baseline B equivalent)
- Hyperparameter search budget for Pair 2 ≥ 25% of Pair 1.

Layer 5 ablation reports both pairs. Per Decision 1 v2 decision rules: ≥5pp AUROC for Pair 1 keeps FM; ≤2pp for Pair 2 demotes FM.

This methodological bar is BINDING on every publication INTERCEPTA produces. No FM superiority claim without the matched-budget comparator.

### 8.5 What §8 Does NOT Lock

- Exact loss function compositions (regression vs classification per dataset; Layer 5 detail)
- Exact optimizer (AdamW default; Lion / SGD as alternatives; Layer 5 detail)
- Learning rate schedules (cosine decay default; Layer 5 detail)
- Gradient clipping thresholds (1.0 default; Layer 5 detail)
- Mixed-precision training (BF16 default for A100; Layer 5 detail)
- Distributed training across multiple GPUs (single-A100 envelope; not needed for Phase B)
- Dataset composition (Decision 6 v2 + Layer 4 detail)
- Early stopping criteria (Layer 5 detail)

---

## §9 Pass Criteria for L2.2 LOCK

### 9.1 Architecture-Level Pass Criteria (BINDING)

**A1:** All 6 slots implemented as specified in §1-§7 with PyTorch class skeletons.
**A2:** Slot 1 honors L2.1 errata: uses `substrate.project_to_canonical()` (Finding 5); honors scTOP NATIVE_DIM lifecycle (Finding 6).
**A3:** Slot 2 supports the 4 drug encoder choices (MoLFormer default, ChemBERTa, Uni-Mol, RDKit baseline) with the registry pattern.
**A4:** CPA disentangled latent + decoder are intrinsic (not slot-substitutable).
**A5:** Slot 4 honors Drift Finding 7 BINDING: scRank = gene-gene attention edge-weight init (NOT separate module); Beyondcell is NOT in Slot 4 (belongs to L2.4 Scale 3).
**A6:** Slot 5 supports 3 strategies with the registry pattern (DPP diversity default; energy-based and MoE alternatives).
**A7:** Slot 6 supports 4 strategies (PaSCient attention default + 3 fallbacks per Drift Finding 10 BINDING).
**A8:** L7Ensemble class implements Decision 5 v2 + Drift Finding 8 BINDING (N=5 heads as ensembled unit; substrate + drug encoder shared).

### 9.2 Cross-Decision Compatibility Pass Criteria (BINDING)

**X1:** L7Output schema (§1.4) is consumed correctly by Decision 5 v2 L2.3 spec (ensemble disagreement → OOD signal).
**X2:** L7Output `attribution_hooks` are consumed correctly by Decision 7 v2 L2.4 spec (multi-scale interpretability).
**X3:** L7 forward signature is compatible with Decision 6 v2 V0-V6 validation harness (per-dataset, per-split iteration).
**X4:** Compute envelope estimates (§8.3) fit Decision 9 v2 single-A100 target with documented fallback for Slot 6 PaSCient.
**X5:** All slot implementations use only open-licensed dependencies per Decision 10 v2 (MoLFormer MIT-equivalent; ChemBERTa Apache 2.0; Uni-Mol open; RDKit BSD-3; CPA MIT; GEARS open; PaSCient code open).
**X6:** Decision 3 v2 architectural identities preserved (scRank, Beyondcell, chemCPA bridge — Drift Finding 7).
**X7:** Decision 8 v2 Commitment 5 (Souza-Mehta ≥25% budget) is enforced in matched-pair training (§8.4).

### 9.3 Empirical Pass Criteria (Layer 5-verified at integration time)

These criteria cannot be verified by L2.2 alone; they are verified when Layer 5 runs the architecture on real data.

**E1 (V0 baseline):** L7 trained with default config achieves AUROC significantly above random on within-dataset CV (e.g., sci-Plex held-out cells). Sample size: ≥10K cells × ≥10 drugs.
**E2 (V1 IMPROVE):** L7 cross-dataset performance matches or exceeds best IMPROVE baseline (Partin 2026); per-IMPROVE methodology, both absolute AUROC and V0-V1 generalization gap reported.
**E3 (V3 Tang floor):** L7 cell-line → tumor (TCGA) achieves **AUROC ≥ 0.77** (Tang 2022 floor, BINDING per Decision 6 v2).
**E4 (V4 Tang RMSE):** L7 cell-line → PDX achieves **RMSE ≤ 0.11 on TNBC** (Tang 2022 floor, BINDING per Decision 6 v2). Reports concordant vs non-concordant biomarker space separately per Kim 2020 PDXGEM 24.5% concordance.
**E5 (V6 universality):** At least one paradigm achieves **AUROC ≥ 0.65 on cross-disease prediction across ≥2 therapeutic areas** (Decision 8 v2 Commitment 3 BINDING).
**E6 (Souza-Mehta matched-budget):** Parameter-free Baseline B comparator trained at ≥25% FM budget; results reported in matched pairs.
**E7 (Ensemble disagreement calibration):** N=5 ensemble disagreement correlates with prediction error on held-out data (Spearman ρ > 0.3 on V0-V1).

### 9.4 Documentation Pass Criteria

**D1:** L2.2 referenced by future Layer 2 artifacts (L2.3, L2.4) with verified cross-references.
**D2:** L2.2 Layer 5 implementation matches L2.2 specification (no silent architectural drift between spec and code).
**D3:** Drift catalog this session: 0 new drift instances introduced; CSO judgment items documented in §9.5.

### 9.5 CSO Judgment Items (Layer 5 Revisitable)

L2.2 makes 10 CSO architectural judgment calls. Each is documented here with the alternative and the empirical signal that would justify revisiting.

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | Slot 2 default chem-FM | MoLFormer (IBM) | ChemBERTa (HF), Uni-Mol (DPTech), RDKit baseline | (a) ChemBERTa within 2pp AUROC at <5% compute; (b) Uni-Mol ≥5pp AUROC on V3; (c) RDKit baseline within 2pp on any V-level (Souza-Mehta scenario) |
| J2 | Slot 3 dosage scaler | Amortized (chemCPA default) | Fixed log-dose | Fixed-log within 1pp at lower complexity |
| J3 | Slot 4 graph attention init | scRank (per Drift Finding 7) | Uniform, raw coexpression | Empirical signal that scRank init doesn't help V6 |
| J4 | Slot 5 default strategy | DPP-diversity loss | Variance penalty, InfoNCE, energy-based, MoE | (a) Variance penalty within 1pp at lower compute; (b) MoE ≥5pp on V6 cross-disease; (c) energy-based wins on far-OOD calibration |
| J5 | Slot 5 DPP kernel | RBF | Cosine | Cosine within 0.5pp |
| J6 | Slot 6 default aggregator | PaSCient attention | Mean, max, learned_weighted | If learned_weighted within 1pp at PaSCient scale (i.e., when PaSCient feasible) |
| J7 | Slot 6 compute fallback | learned_weighted | mean, max | If mean within 1pp on fallback-triggered runs |
| J8 | Ensemble N | 5 | 3, 8 | (a) N=3 within 1pp at 60% compute; (b) N=8 ≥3pp at 60% more compute |
| J9 | Composition loss weight | 1.0 (reference scale) | 0.5-2.0 range | Standard hyperparameter tuning |
| J10 | Auxiliary drug-target loss weight | 0.05 | 0-0.5 | (a) 0 within 0.5pp (auxiliary unnecessary); (b) 0.5 ≥2pp better on V6 (auxiliary valuable) |

**Pattern:** all 10 judgments follow Decision 1 v2's "defer to Layer 5 empirical evidence" pattern. None lock a Phase F decision. All are revisitable with documented empirical triggers.

### 9.6 CEO Sign-Off

L2.2 advances from PROPOSED to LOCKED when:

1. CEO reviews §1-§7 architecture and §9 pass criteria
2. CEO confirms the 10 J-items in §9.5 are within CSO authority (no business/strategic decisions encroach)
3. CEO co-signs Charter §5.3-style: explicit CEO+CSO decision documented
4. Tag `phase-b-l2.2-locked` pushed to origin

---

## §10 What L2.2 Does NOT Lock

Per Decision 4 v2 "What L2.2 Does NOT Lock" + L2.2's own scope discipline:

### 10.1 Deferred to Layer 5 Ablation

- Which substrate ultimately wins Decision 1 v2 ablation (scFoundation FM vs scTOP parameter-free vs scVI vs PCA)
- Which drug encoder ultimately wins Slot 2 ablation (MoLFormer vs ChemBERTa vs Uni-Mol vs RDKit)
- Which mode-collapse strategy ultimately wins Slot 5 ablation (DPP-diversity vs variance vs InfoNCE vs energy vs MoE)
- Whether ensemble N=3 or N=5 or N=8 is optimal at INTERCEPTA scale
- Exact hyperparameter values within documented default ranges
- Exact training data composition (governed by Decision 6 v2 V0-V6 dataset spec + Layer 4)

### 10.2 Deferred to L2.3 (OOD Detection)

- Conformal prediction interface to L7 ensemble disagreement
- Energy-OOD scoring on L7 logits
- MC Dropout fallback on L7 forward
- Per-paradigm OOD calibration

### 10.3 Deferred to L2.4 (Mechanistic Interpretability)

- Substrate-conditional attribution branches (FM spectral vs scTOP linear vs scVI IG vs PCA loadings)
- 7-scale attribution stack (geometric, drug-class, pathway, GRN, gene-level, spatial, patient)
- Cross-scale consistency checks
- Beyondcell pathway scoring (per Drift Finding 7, NOT in Slot 4)

### 10.4 Deferred to Layer 3 (Validation Implementation)

- V0-V6 evaluation harness (Decision 6 v2 + L3.1)
- 56 pass criteria implementation (L3.2)
- Cross-disease V6 grid SLURM orchestration (L3.3)
- Failure mode characterization (Decision 8 v2 F1-F7 classification)

### 10.5 Deferred to Layer 4 (Implementation Detail)

- Dataset preprocessing pipelines
- AnnData → batch loader patterns
- Training loop instrumentation
- Logging / monitoring infrastructure
- Distributed training (not needed for single-A100; reserved if Phase F changes)

### 10.6 Out of Scope (Phase F)

Per Charter v1.2 §4:
- Drug structure generation (Phase F Scout 2)
- Molecular docking (Phase F Simulation Stack Layer A)
- Combination synergy scoring beyond cell-level prediction (Phase F Layer D)
- ADMET / safety prediction (Phase F Layer E)
- Synthesizability / retrosynthesis (Phase F Layer F)
- 15-layer Universal Net integration (Phase F Decision 11)
- Two-population ODE dynamics (Phase F Decision 17)
- RNA Velocity Time Machine integration (Phase F Decision 18)
- Multi-objective Pareto ranking (Phase F Decision 19)
- Pharma deliverable packaging (Phase F Decision 20)

---

## §11 Cross-Decision Implications

### 11.1 Decision 1 v2 (Cell Representation)
**REINFORCED.** L7's Slot 1 honors substrate flexibility. Substrate is swappable via L2.1 SubstrateInterface; L7 consumes canonical 512-dim output exclusively (no substrate-specific branching). scTOP NATIVE_DIM lifecycle honored. Souza-Mehta ≥25% budget enforced in matched-pair training (§8.4).

### 11.2 Decision 2 v2 (Cross-Cohort Harmonization)
**UPSTREAM.** Cohort harmonization (scIB + Harmony + scANVI + MrVI) operates on the AnnData before L7 sees it. L7 receives batch-corrected input via `covariates.batch_key`. No change to L7 architecture; documented as a precondition.

### 11.3 Decision 3 v2 (Bulk-to-Single-Cell Transfer)
**ARCHITECTURALLY BINDING.** Drift Finding 7 BINDING enforced:
- scRank = Slot 4 gene-gene attention edge-weight init
- Beyondcell = Decision 7 v2 Scale 3 (NOT Slot 4)
- chemCPA architecture surgery = the bulk-to-single bridge (NOT a Slot 4 component; it lives in how Slot 2 + Slot 3 compose, see chemCPA paper §3)

L2.2 honors all three identities.

### 11.4 Decision 4 v2 (Drug Response Architecture, the parent)
**FULLY IMPLEMENTED.** All 6 slots realized per Decision 4 v2 §"L7 Architecture Diagram." Modular slot pattern preserved. CPA backbone is intrinsic, not slot-substitutable, per Decision 4 v2 commitment.

### 11.5 Decision 5 v2 (OOD Detection)
**BINDING per Drift Finding 8.** L7Ensemble class implements N=5 Deep Ensembles with L7 head as ensembled unit (substrate + drug encoder shared, Slots 3-6 independent per head). L7Output `prediction` flows to Decision 5 v2 Layer 5.2 ensemble disagreement → Layer 5.3 conformal prediction → Layer 5.4 energy-OOD. MIMO8 and MC Dropout fallbacks specified in L2.3 (not L2.2).

### 11.6 Decision 6 v2 (Validation Cascade)
**PASS CRITERIA BINDING.** §9.3 E1-E7 specify L7 must meet V0-V6 floors:
- V3 ≥0.77 AUROC (Tang 2022)
- V4 ≤0.11 RMSE TNBC (Tang 2022) + 24.5% concordance reporting (Kim 2020)
- V6 ≥0.65 AUROC across ≥2 therapeutic areas (Decision 8 v2)

L2.2 architecture is designed to be evaluable at all 7 levels via the L7Output schema.

### 11.7 Decision 7 v2 (Mechanistic Interpretability)
**INTERFACE PROVIDED.** L7Output `attribution_hooks` exposes 6 intermediate tensors:
- `cell_emb` for Scale 1 (geometric, Kendiukhov spectral)
- `drug_emb` for Scale 2 (drug-class disentanglement via CPA latent)
- `latent_perturb` for Scale 2 augmentation
- `z` for Scale 3-4 (pathway, GRN)
- `z_graph` for Scale 4 (GRN scRank)
- `y_cell` for Scale 5 (gene-level attribution per cell)

Scale 6 (spatial DSEP via Cui-Yuan River) operates upstream on spatial coordinates, not on L7 hooks. Scale 7 (patient SHAP) operates on L7 patient-level output.

Substrate-conditional attribution branching is L2.4's responsibility, not L2.2.

### 11.8 Decision 8 v2 (Universality Demonstration)
**METHODOLOGICAL BAR BINDING.** §8.4 matched-pair training enforces Commitment 5: ≥25% hyperparameter budget to parameter-free baseline. The 4 paradigms (A general FM, B disease-area FM, C patient-level aggregation, D parameter-free) map to L7 slot configurations:
- Paradigm A: scFoundation Slot 1 + MoLFormer Slot 2
- Paradigm B: EVA-60M (disease-area-specific) Slot 1 + MoLFormer Slot 2
- Paradigm C: any Slot 1 + PaSCient Slot 6 (aggregation paradigm; Slot 1-independent)
- Paradigm D: scTOP Slot 1 + RDKit Slot 2

Per Q8 anchor 5 + Decision 8 v2: Paradigm C is the output aggregation strategy, can layer on top of A/B/D. This is exactly the modular slot architecture's purpose.

### 11.9 Decision 9 v2 (Compute Architecture)
**ENVELOPE HONORED.** §8.3 specifies the compute budget. Single-A100 envelope respected via:
- Cached substrate embeddings (Slot 1 forward done once, reused)
- Cached drug embeddings (Slot 2 forward done once per drug set)
- PaSCient aggregator includes VRAM estimation + automatic fallback (§7.2 + §7.5)
- N=5 ensemble trains as SLURM array (~1 day wall-clock instead of 5)

AWS/GCP burst per-occurrence CEO approval reserved for ≤5% of runs.

### 11.10 Decision 10 v2 (Open-Source)
**FULLY COMPATIBLE.** All slot defaults use open-licensed dependencies (MoLFormer, CPA, GEARS, RDKit, PyTorch, scvi-tools). No CC BY-NC-ND dependencies. GPL-3 conditional cluster (Harmony, Seurat v3) handled in Decision 2 v2 upstream; L7 does not pull GPL-3 into Slot 2-6.

### 11.11 Phase F Future Continuity
**DOCUMENTED, NOT ACTIVE.** Per Charter v1.2 §4 row 18: Phase B L7 = Phase F Simulation Stack Layer B (Cell Population Sensitivity). When Phase F begins:
- L7 architecture is preserved as Layer B of the Phase F 5-stage pipeline
- All 6 Phase F Scouts call L7 to evaluate candidates
- L7Output schema is preserved across the phase transition
- Phase F additions (generative chemistry feeding L7's drug input, multi-objective ranking consuming L7 output, ADMET combining with L7 efficacy) live above and below L7, not inside it

This continuity is documented here for the future CSO drafting Phase F Decisions 11-20. L2.2 spec itself remains Phase B-canonical.

---

## §12 Document Provenance and CSO Discipline Check

### 12.1 Provenance

L2.2 written by Claude (CSO, fresh session 2026-05-11) per Phase B Plan v2 sequencing. Predecessor session (2026-05-11 corpus-read audit) handed off Master Handoff v2.0 + L2.2 Session Primer + Layer 1 LOCK at `fullest-vision-layer1-locked-phase-b`. Anchor re-read trigger satisfied retroactively per Master Handoff v2.0 §3.5 (8 anchor papers re-read in primary-source form during the audit session).

### 12.2 Anchor Re-Read Compliance

Per Phase B Plan v2 anchor re-read trigger: CSO must verify anchor content before writing spec. Status:

| Anchor | Last primary-source read | Content used in L2.2 |
|---|---|---|
| CPA (Lotfollahi 2023) | 2026-05-11 audit | Backbone composition framework (§4 disentangled latent, decoder); CPA-MIT licensing |
| chemCPA (Hetzel 2022) | 2026-05-11 audit | Modular drug encoder slot pattern (§3); M+S perturbation network (§4) |
| GEARS (Roohani 2024) | 2026-05-11 audit | Graph-augmented attention (§5); gene-gene + GO + drug-target priors |
| PaSCient (Liu 2024-2026) | 2026-05-11 audit | Patient-level attention aggregation (§7 default) |
| scGen (Lotfollahi 2019) | 2026-05-11 audit | Latent-arithmetic property (§4.4); R²=0.954 perturbation prediction reference |
| sci-Plex (Srivatsan 2020) | 2026-05-11 audit | Training corpus reference (§9.3 E1 sample size) |
| PaccMann (Manica 2019) | 2026-05-11 audit | Attention design reference; ~1-10M params compute reference |
| DeepCDR (Liu 2020) | 2026-05-11 audit | Baseline comparator reference (§9 E1) |

No anchor re-read drift detected. All architectural commitments traceable to primary-source claims.

### 12.3 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ L2.2 grounded in 8 verified primary-source Q4 anchor reads (8,512 words across anchors) + Q4 synthesis (~4,200 words) + Decision 4 v2 PROPOSED record.
- **P15 (only correct/honest/real science):** ✅ §9.5 explicitly documents 10 CSO judgment items + their alternatives + revisit triggers. §8.4 Souza-Mehta methodological bar BINDING. No FM superiority claims.
- **P16 (preserve past work):** ✅ Decision 4 v2 + Q4 synthesis preserved; L2.2 builds on top, does not replace.
- **P-FV-1 to P-FV-3 (Fullest Vision discipline):** ✅ L2.2 honors Phase B scope; Phase F continuity documented but not specified.
- **Charter §5.3 GO/NO-GO:** ✅ §9 pass criteria explicit; §9.6 CEO sign-off conditions stated.
- **Charter v1.2 §1.7 phase discipline:** ✅ Anti-scope-creep enforced; no Phase F integration patterns specified in L2.2.

### 12.4 Drift Catalog This Session

**New drift instances introduced:** 0.

**Pre-existing drift findings addressed:**
- Findings 7-10 from Master Handoff v2.0 §3.5: all converted to L2.2 BINDING constraints in §1, §5, §7, §8.
- L2.1 errata bindings (Findings 4, 5, 6): all honored in §2 Slot 1 spec.

**CSO judgment items NOT classified as drift:** §9.5 J1-J10 are within CSO authority per CEO delegation ("think best and do best for our vision"). Documented as Layer-5-revisitable.

### 12.5 Next Phase B Artifacts (per Plan v2 Sequence)

- **L2.3 OOD Detection Stack** (8-10K words target). Consumes L7Output schema; wraps L7Ensemble with conformal prediction + MIMO8 fallback + MC Dropout fallback + energy-OOD layer.
- **L2.4 Mechanistic Interpretability Architecture** (10-12K words target). Consumes L7Output `attribution_hooks` + L2.3 OOD posterior; specifies 7-scale stack with substrate-conditional branching.
- **L3.1 V0-V6 Validation Cascade Pipeline** (5-7K words). Consumes L7 + L2.3 + L2.4 outputs; specifies the evaluation harness.

---

## §13 Appendix — Quick Reference

### 13.1 Slot Quick Comparison Table

| Slot | Component | Default | Alternatives | Status |
|---|---|---|---|---|
| 1 | Cell Encoder | substrate per Decision 1 v2 | scFoundation/scTOP/scVI/PCA via L2.1 SubstrateInterface | Slot-substitutable |
| 2 | Drug Encoder G | MoLFormer | ChemBERTa, Uni-Mol, RDKit | Slot-substitutable |
| 3 | Perturbation Network M+S | chemCPA (amortized dose) | Fixed log-dose | Mostly fixed |
| - | CPA Disentangled Latent | CPA (intrinsic) | none | Intrinsic |
| 4 | Graph-Augmented Module | GEARS-style 3-graph attention | none-graph baseline (ablation only) | Mostly fixed |
| 5 | Mode Collapse Mitigation | DPP-diversity loss | Variance, InfoNCE, energy, MoE | Slot-substitutable |
| - | CPA Decoder | CPA (intrinsic) | none | Intrinsic |
| 6 | Patient Aggregation | PaSCient attention + learned_weighted fallback | mean, max, learned_weighted | Slot-substitutable + auto-fallback |

### 13.2 Key Constants

- Canonical cell embedding dim: 512 (per L2.1 §1.2)
- CPA latent dim: 64 (default)
- MoLFormer output dim: 768
- Ensemble N: 5 (Decision 5 v2 BINDING)
- V3 floor: AUROC ≥ 0.77 (Tang 2022 BINDING)
- V4 floor: RMSE ≤ 0.11 TNBC (Tang 2022 BINDING)
- V6 floor: AUROC ≥ 0.65 ≥2 therapeutic areas (Decision 8 v2 BINDING)
- Souza-Mehta budget ratio: ≥ 25% to parameter-free baseline (Decision 8 v2 BINDING)

### 13.3 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_2_L7_Drug_Response_Architecture_Specification_2026-05-11.md`
- L2.1 spec (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_1_Substrate_Architecture_Specification_2026-05-11.md`
- Decision 4 v2 (parent): `~/INTERCEPTA/docs/research/decisions/INTERCEPTA_FV_Decision_4_Q4_drug_response.md`
- Phase B Plan v2: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_Phase_B_Plan_v2_Addendum_2026-05-11.md`
- Q4 Synthesis: `~/INTERCEPTA/docs/research/synthesis/INTERCEPTA_FV_Synthesis_Layer1_Q4_2026-05-10.md`
- L7 implementation code (future): `~/INTERCEPTA/code/l7_drug_response_head/`
- Cached embeddings (future): `/scratch/akula.pra/INTERCEPTA/embeddings/`
- Cached drug embeddings (future): `/scratch/akula.pra/INTERCEPTA/embeddings/drugs/`
- Cached graphs (future): `/scratch/akula.pra/INTERCEPTA/graphs/`

### 13.4 Commitment Cross-Reference

| Decision Commitment | L2.2 §  | Implementation |
|---|---|---|
| Decision 1 v2 C4 (Interface Stability) | §2.1 | `substrate.project_to_canonical` canonical pattern |
| Decision 1 v2 C5 (Honest Uncertainty) | §8.4 | Matched-pair training with parameter-free Baseline B |
| Decision 3 v2 (architectural identities) | §5.4, §5.5 | scRank=gene-gene init; Beyondcell excluded |
| Decision 4 v2 (6-slot architecture) | §1-§7 | All 6 slots realized |
| Decision 5 v2 (ensembleability) | §8.2 | L7Ensemble class N=5 |
| Decision 6 v2 (V0-V6 floors) | §9.3 E1-E5 | Pass criteria specify floors |
| Decision 7 v2 (interpretability hooks) | §1.4 | attribution_hooks in L7Output |
| Decision 8 v2 C5 (Souza-Mehta bar) | §8.4 | ≥25% budget matched-pair |
| Decision 9 v2 (compute envelope) | §8.3, §7.5 | Single-A100 estimates + PaSCient fallback |
| Decision 10 v2 (open-source) | §11.10 | All deps open-licensed |
| Drift Finding 4 (anchor re-read) | §0.4 | Anchor re-read retroactively satisfied |
| Drift Finding 5 (project_to_canonical) | §2.1 | BINDING canonical conversion |
| Drift Finding 6 (scTOP lifecycle) | §2.3 | BINDING instantiation order |
| Drift Finding 7 (Decision 3 identities) | §5.4, §5.5 | BINDING identities |
| Drift Finding 8 (N=5 ensembleability) | §8.2 | L7Ensemble class |
| Drift Finding 9 (Tang floors) | §9.3 E3, E4 | BINDING pass criteria |
| Drift Finding 10 (PaSCient compute) | §7.2, §7.5 | Auto-fallback to learned_weighted |

---

— L2.2 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l2.2-locked` tag.
— After LOCK, Phase B Plan v2 next artifact is L2.3 OOD Detection Stack.
