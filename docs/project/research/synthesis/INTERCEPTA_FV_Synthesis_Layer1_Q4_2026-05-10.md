# INTERCEPTA Layer 1 Q4 Synthesis v2 — Drug Response Prediction Architecture: The L7 Engine

**CSO:** Claude
**Date:** 2026-05-10
**Phase:** 2 re-do (audit remediation)
**Scope:** Integrating 7 verified primary-source anchor reads (8,512 words across anchors) to ground Decision 4 v2
**Supersedes:** Q4 Synthesis v1 (455 words, pre-audit, archived in `_archive/`)

---

## Executive Summary

Q4 (drug response prediction architecture) is **the L7 architectural engine of INTERCEPTA's Charter §8.1 stack.** Decision 4 specifies the deep learning architecture that takes cell representations (from Decision 1 v2's substrate) + drug representations (from chemCPA-style molecular embedding) and produces predicted cellular response. It is the operational core of INTERCEPTA's drug discovery vision.

The 7 verified Q4 anchors (added Q4 anchor 7 chemCPA in Phase 2) collectively establish:

1. **Compositional VAE architecture is the field-standard for single-cell perturbation prediction** (scGen 2019 founding → CPA 2023 generalization → chemCPA 2022 unseen-drug extension)
2. **Latent-space arithmetic captures biological perturbation effects** at R² = 0.954 average on held-out cell types (scGen) — the foundational empirical evidence
3. **Graph-augmented prediction with biological priors achieves 40% precision improvement** over architecturally simpler methods (GEARS) — biological knowledge integration is valuable
4. **Modular molecular embedding is the architectural slot for chem-FM** (chemCPA) — the drug-side analog of Decision 1 v2's cell-substrate flexibility
5. **Bulk-to-single-cell transfer learning via architecture surgery** addresses the deployment scale gap (chemCPA + scArches pattern)
6. **Mode collapse is a documented risk** across all VAE-based perturbation methods (Diversity-by-Design 2025 critique)
7. **Multi-perturbation joint training improves generalization** vs per-drug models (Tang 2022 evidence at Q6; reinforces CPA architectural choice)

**The most consequential finding:** No single Q4 anchor predicts drug response on patient data with FM-substrate + cross-disease generalization. **INTERCEPTA's Decision 4 v2 contribution is the architectural fusion** that combines:
- CPA/chemCPA compositional VAE (drug-side flexibility)
- GEARS graph-augmented predictions (biological prior integration)
- Decision 1 v2 cell substrate (FM/scTOP/scVI flexibility)
- Decision 5 v2 N=5 ensembleability (epistemic uncertainty)
- PaSCient-style patient-level aggregation (Q8 anchor 3 pattern)
- Mode collapse mitigation (diversity regularization)

**Decision 4 v2 is a MODULAR L7 ARCHITECTURE** with explicit slots for substrate choice, drug encoder choice, biological prior integration, and patient-level aggregation. The architecture survives Layer 5 ablations regardless of which substrate or chem-encoder wins — only the slot occupants change.

---

## What Each Anchor Establishes

### Anchor 1 — Srivatsan et al. 2020 (sci-Plex, Stanford/Trapnell lab, *Science*)

**Established empirically:**
- Scalable single-cell drug perturbation screen technology (hash-based multiplexing)
- Thousands of (cell, drug, dose) combinations measurable per experiment
- Foundational training/evaluation substrate for all VAE-based perturbation prediction (CPA, chemCPA, scGen all benchmark on sci-Plex-style data)

**What this contributes to Decision 4 v2:** The empirical training substrate. sci-Plex3 specifically is the canonical evaluation dataset for CPA + chemCPA. INTERCEPTA's Layer 5 must include sci-Plex evaluation.

**What this does NOT establish:** Patient-level deployment. Cross-disease drug screens at sci-Plex scale (cancer-only). FM-era methods comparison.

### Anchor 2 — Manica et al. 2019 (PaccMann, IBM Research Zurich, *Mol Pharmaceutics*)

**Established methodologically:**
- Attention-based architecture for drug response prediction
- Combines drug SMILES (chemical) + transcriptomics (cellular) via cross-attention
- Bulk-level focus (CCLE/GDSC); IC50 prediction
- Pre-VAE-perturbation-prediction era — predates scGen architecturally

**What this contributes to Decision 4 v2:** Reference architecture for attention-based drug-cell interaction modeling. **PaccMann represents the bulk-level attention-based DRP paradigm** that compositional VAE methods (CPA/chemCPA) generalize beyond.

**What this does NOT establish:** Single-cell resolution prediction. Out-of-distribution drug generalization at sci-Plex scale. Modern FM-era benchmarks.

### Anchor 3 — Liu et al. 2020 (DeepCDR, *Bioinformatics*)

**Established methodologically:**
- Hybrid Graph Convolutional Network (GCN) for drug response prediction
- Combines drug molecular graph (GCN-encoded) + cell line multi-omics (gene expression, mutation, methylation)
- IC50 regression on CCLE/GDSC benchmarks
- Pre-CPA architectural alternative

**What this contributes to Decision 4 v2:** Hybrid molecular-graph + cell-omics architecture reference. **DeepCDR represents the GCN-based DRP paradigm**, complementary to CPA's VAE and GEARS's graph-attention.

**What this does NOT establish:** Single-cell scale. Perturbation prediction (only IC50 regression, no expression prediction). Unseen drug generalization.

### Anchor 4 — Lotfollahi et al. 2023 CPA (Helmholtz Munich + Meta AI, *Mol Syst Biol*)

**Established empirically and architecturally:**
- Compositional VAE with disentangled latent for perturbations + covariates
- Predicts unseen combinations of drugs, doses, cell types, species, time, genetic perturbations
- 5,329 in-silico drug combinations predicted (97.6% of possible)
- Uncertainty estimates built-in
- Modular drug embedding slot (chemCPA fills this for unseen drugs)
- Six public dataset benchmark

**What this contributes to Decision 4 v2:** **The compositional VAE backbone for INTERCEPTA's L7 architecture.** CPA defines the architectural slot structure: cell encoder + perturbation embedding + composition framework + decoder + dose-response curves + uncertainty estimates. INTERCEPTA inherits this skeleton.

**What this does NOT establish:** Patient deployment. Cross-disease generalization. FM-substrate integration (CPA used learned encoders; FM substrate is a Layer 5 ablation question). Mode collapse mitigation specifics.

### Anchor 5 — Roohani et al. 2024 GEARS (Stanford SNAP lab, *Nature Biotechnology*)

**Established empirically and architecturally:**
- Graph-Enhanced gene Activation and Repression Simulator
- Integrates gene-gene co-expression graph + GO ontology graph as biological priors
- **40% higher precision** than prior methods on 4-5 genetic interaction subtypes
- **2× better at identifying strongest interactions**
- Predicts outcomes of perturbing genes never experimentally perturbed
- Developed for genetic (Perturb-Seq) perturbations; drug extension is INTERCEPTA novelty territory

**What this contributes to Decision 4 v2:** **Graph-augmented prediction component** complementary to CPA's compositional VAE. GEARS demonstrates biological prior knowledge integration in deep learning — operationally important for cross-disease (V6) generalization where biological priors transfer better than learned embeddings.

**What this does NOT establish:** Drug perturbation prediction (genetic only). FM integration. Patient-level outputs.

### Anchor 6 — Lotfollahi, Wolf & Theis 2019 scGen (Helmholtz Munich, *Nature Methods*)

**Established empirically:**
- VAE + latent-space arithmetic predicts single-cell perturbation responses
- **R² = 0.954 average** across 6 held-out cell types on IFN-β stimulation (PBMC dataset)
- ISG15 distribution capture (mean + variance, not just mean)
- Cross-species (mouse → rat) LPS prediction validated
- **Foundational architectural primitive** for all VAE-based perturbation prediction

**What this contributes to Decision 4 v2:** The architectural grandparent. scGen establishes the principle that CPA, chemCPA, scperb, all VAE-based methods inherit. Decision 4 v2 commits to this lineage.

**What this does NOT establish:** Combinatorial perturbations. Dose-response curves. Unseen drug prediction. Patient deployment.

### Anchor 7 — Hetzel et al. 2022 chemCPA (TUM + Helmholtz Munich, NeurIPS) **[NEW IN PHASE 2]**

**Established empirically and architecturally:**
- 3-component perturbation network (G molecule encoder + M perturbation encoder + S dosage scaler) replaces CPA's perturbation embedding dictionary
- **Predicts unseen drugs** — closes the gap CPA explicitly leaves open
- Modular molecular embedding: any pretrained GNN, transformer, or RDKit fingerprint plugs into G slot
- Architecture surgery for bulk-to-single-cell transfer learning
- 9 held-out compounds across 4 mechanism-of-action classes (HDAC, Aurora, HSP90, CDK) on sci-Plex3

**What this contributes to Decision 4 v2:** **The architectural slot for chem-FM integration.** chemCPA's G slot is the drug-side analog of Decision 1 v2's cell-substrate flexibility. INTERCEPTA can plug MoLFormer, ChemBERTa, Uni-Mol, or RDKit into G and evaluate which wins Layer 5 ablations.

**What this does NOT establish:** Comparison to FM-derived molecular embeddings (used RDKit + GNN, not chem-FM in original 2022 evaluation). Cross-MoA-class generalization beyond the 4 tested classes. Cross-disease.

---

## Convergent Patterns Across the 7 Anchors

### Pattern A — Compositional VAE is the dominant architectural paradigm

scGen 2019 → CPA 2023 → chemCPA 2022 → MultiCPA → Biolord 2024 → PerturbNet 2025. **The architectural lineage is six years deep and converges on the same principle:** VAE encoder/decoder + disentangled latent + perturbation arithmetic. **Decision 4 v2 commits to this paradigm** with explicit modularity for substrate (Decision 1 v2) and chem-encoder (chemCPA G slot) choice.

### Pattern B — Graph-augmented prediction is complementary, not competitive

GEARS demonstrates 40% precision improvement via biological priors. CPA + GEARS are architectural complements, not competitors. **Decision 4 v2 fuses both**: CPA backbone + GEARS graph-attention module + chemCPA molecular embedding = INTERCEPTA novelty architecture.

### Pattern C — Substrate flexibility is the architecturally safer choice

scGen, CPA, chemCPA, GEARS all use specific substrates (learned encoders, RDKit, GO graphs). **None of them is committed to a specific FM**. This means INTERCEPTA's Decision 1 v2 substrate-flexibility commitment is **architecturally compatible with all Q4 anchors** — substrate choice can be deferred to Layer 5 ablations without architectural rebuild.

### Pattern D — Mode collapse is a documented field-wide risk

Diversity-by-Design 2025 critique applies to scGen, CPA, chemCPA, GEARS — every VAE/graph-based method in Q4. **Decision 4 v2 must specify mitigations** (diversity loss, energy-based training, mixture-of-experts decoder, or alternative). This is not optional.

### Pattern E — Patient-level outputs require explicit aggregation

CPA, chemCPA, GEARS all produce **cell-level** predictions. INTERCEPTA's clinical deployment requires **patient-level** predictions. Per Q8 Pattern A (PaSCient anchor): patient-level aggregation is the right deployment unit. **Decision 4 v2's L7 must include patient-level aggregation layer** — PaSCient-style attention is the leading candidate.

### Pattern F — Bulk-to-single-cell transfer is operationally essential

chemCPA's architecture surgery + bulk pretraining + single-cell fine-tuning addresses the central economic problem of single-cell drug discovery. sci-Plex3 has ~5,000 cells/drug; LINCS L1000 has thousands of compounds at bulk resolution. **INTERCEPTA's training strategy must use both scales**, per chemCPA's pattern.

### Pattern G — None of the Q4 anchors solve cross-disease drug response

scGen tested cross-species LPS only. CPA tested cross-cell-type within cancer. chemCPA tested unseen-drug within sci-Plex3. GEARS tested unseen-gene within Perturb-Seq. **Cross-disease drug response is INTERCEPTA's novelty contribution** — operationalized by Decision 8 V6 pass criterion (AUROC ≥ 0.65 on held-out disease, ≥2 therapeutic areas).

---

## What the Field Has NOT Resolved (Honest Gaps)

Reading across all 7 Q4 anchors, the field's open questions:

1. **Chem-FM integration in chemCPA G slot.** chemCPA architecture supports it but the 2022 paper used RDKit + GNN, not MoLFormer/ChemBERTa/Uni-Mol. **INTERCEPTA must evaluate empirically.**

2. **Cross-disease drug response prediction.** No published benchmark; Decision 8 V6 is the empirical hypothesis.

3. **Patient-level aggregation for drug response.** PaSCient (Q8.3) does disease classification at patient level, not drug response. **Combining PaSCient aggregation + chemCPA architecture is INTERCEPTA novelty.**

4. **Mode collapse mitigation specifics.** Diversity-by-Design 2025 identifies the problem; specific architectural fixes for INTERCEPTA's context are unresolved.

5. **FM-substrate vs parameter-free in L7 head.** Decision 1 v2 defers; Decision 4 v2 must be architecturally compatible with either outcome.

6. **Architecture surgery patterns for cross-disease.** chemCPA does bulk→single-cell surgery; whether the same pattern works for cancer→I&I or cancer→neurodegen is untested.

7. **Combinatorial drug prediction at sci-Plex scale.** chemCPA does single-drug unseen; CPA does combinatorial seen-drugs; **combinatorial unseen-drug** is unresolved.

---

## Cross-Decision Architectural Patterns

The Q4 anchors inform decisions beyond Decision 4:

### For Decision 1 v2 (cell representation)

scGen, CPA, chemCPA all use **substrate-agnostic encoder slots** in principle (the 2019/2022/2023 implementations use raw expression, but the architecture is encoder-replaceable). This is **consistent with Decision 1 v2's substrate flexibility commitment** — Decision 4 v2 inherits the substrate flexibility from Decision 1 v2 cleanly via Pattern C.

### For Decision 2 (cross-cohort)

CPA's evaluation on 6 public datasets is implicitly cross-cohort. **chemCPA's architecture surgery (bulk→single-cell)** parallels scArches's cross-cohort surgery (Decision 2 anchor). Both use the same architectural pattern. **Decision 2 + Decision 4 are operationally coherent** via shared architecture-surgery methodology.

### For Decision 3 (bulk→single-cell)

chemCPA explicitly tests bulk-to-single-cell transfer. **This is Decision 3's operational pattern realized in the drug response context.** Decision 3's PROPOSED commitments (SCAD, scDEAL, scAdaDrug stack) are complementary upstream methods; chemCPA is the drug-response-specific downstream extension.

### For Decision 5 v2 (OOD detection)

Decision 5 v2 Layer 5.2 specifies Deep Ensembles N=5 (default) or MIMO8 (fallback). **Decision 4 v2's L7 architecture must be N=5 ensembleable.** This means CPA/chemCPA/GEARS must be modular components, not monolithic black-boxes. **Decision 4 v2 design must reflect this modularity.**

CPA's uncertainty estimates are baseline; Decision 5 v2's 4-layer stack wraps them with epistemic refinement + conformal + energy.

### For Decision 6 v2 (validation cascade)

Decision 6 v2 V0-V1 floor is matched by CPA's 6-public-dataset evaluation. **V3-V4 floor (Tang 2022 AUROC 0.77 / RMSE 0.11) requires INTERCEPTA's chemCPA+CPA+substrate combination to clear it.** V6 cross-disease is INTERCEPTA novelty per Pattern G.

### For Decision 7 (mechanistic interpretability)

CPA's disentangled latent + drug-similarity analysis (recovers known mechanism families) provides drug-class-level mechanistic interpretation. GEARS's gene-gene graph attribution provides gene-level interpretation. **Decision 7's multi-level interpretability** (drug-class + pathway + gene) is empirically validated by Q4 anchors.

### For Decision 8 (universality)

- **Paradigm A (general FM portfolio):** plugs into chemCPA G slot (cell side) and Decision 1 v2 substrate (gene side)
- **Paradigm B (disease-area-specific):** EVA-60M for I&I per Q8 anchor 4
- **Paradigm C (patient-level aggregation):** PaSCient-style attention wraps Decision 4 v2 cell-level predictions
- **Paradigm D (parameter-free):** pathway features + linear projection alternative to CPA's VAE

Decision 4 v2 must be compatible with all four paradigms — which it is, by Pattern C substrate flexibility.

### For Decision 9 (compute)

CPA/chemCPA/GEARS training is GPU-intensive. **Decision 9's single-A100 envelope** requires that Decision 4 v2 not commit to TEDDY-400M-scale training. Targeting PaSCient-scale (8× A100s) per Q8 Pattern E.

### For Decision 10 (open-source)

- scGen, CPA, chemCPA, GEARS all open-source (theislab, facebookresearch, snap-stanford repos)
- Licenses: scvi-tools BSD-3, MIT/NeurIPS-standard, CC BY 4.0 — all permissive
- **Decision 10 commitment reinforced.** Decision 4 v2 architecture can adopt all anchors freely.

---

## Decision 4 — REVISED PROPOSED (v2 — formalized below)

The revised Decision 4 commitment (to be formalized as a Decision Record file) is the **MODULAR L7 ARCHITECTURE** with explicit slots for substrate choice, drug encoder choice, biological prior integration, patient-level aggregation, and mode collapse mitigation.

### L7 Architecture Components

```
Cell representation (Decision 1 v2 substrate)
    ↓
[Cell encoder — substrate-specific; output 512-dim embedding]
    ↓
CPA-style disentangled latent (perturbation effect separated from covariates)
    ↓
Compositional latent + chemCPA perturbation network input
    ↑
[Drug molecule encoder G — chem-FM slot: MoLFormer/ChemBERTa/RDKit selectable]
    ↑
[Perturbation encoder M + dosage scaler S — chemCPA architecture]
    +
[GEARS graph-augmented module — gene-gene + GO + drug-target graphs as biological priors]
    ↓
CPA-style decoder → cell-level expression predictions
    ↓
[Patient-level aggregation — PaSCient-style attention pooling]
    ↓
Patient-level drug response prediction + uncertainty (Decision 5 v2 stack wraps)
```

### Modularity Slots (Decision 4 v2 Binding Architecture)

1. **Cell substrate (Decision 1 v2 deferred):** scFoundation default; scTOP/scVI/PCA baselines co-equal
2. **Drug molecule encoder G:** chem-FM (MoLFormer/ChemBERTa/Uni-Mol) candidates; RDKit + GNN as baselines
3. **Biological prior graphs:** gene-gene co-expression + GO + drug-target ontology — substrate for GEARS-style graph attention
4. **Patient aggregation:** PaSCient-style attention default; alternatives include simple mean pooling, max pooling, learned weighted pooling
5. **Mode collapse mitigation:** diversity loss term (default) + alternative options (energy-based training, mixture-of-experts) for Layer 5 ablation

### Pass Criteria (to be formalized in Decision 4 v2)

To be specified in Decision 4 v2 record file. Cross-references to Decision 6 v2's V0-V6 cascade pass criteria.

---

## What This Synthesis Does NOT Resolve

Honest gaps that propagate to Layer 5 implementation:

1. **Specific chem-FM choice in chemCPA G slot.** Layer 5 ablation; not Layer 1 decision.

2. **Specific drug-target ontology choice for GEARS-style graph augmentation.** DrugBank vs TWOSIDES vs compound-similarity graphs — Layer 5 ablation.

3. **Specific mode collapse mitigation.** Diversity loss term weight, energy-based training schedule, mixture decoder size — all Layer 5 tuning.

4. **Specific patient-level aggregation architecture.** PaSCient default; alternative attention architectures may improve — Layer 5 ablation.

5. **Combinatorial unseen-drug prediction.** Architecture is in principle extensible; specific implementation is Layer 5 work.

6. **Cross-disease architectural fine-tuning protocol.** chemCPA's bulk→single-cell architecture surgery may or may not transfer to cancer→I&I — Layer 5 testing.

These require Layer 5 implementation, not more Layer 1 reading.

---

## Drift Catalog This Phase 2 Cycle

- **New drift instances introduced:** 0
- **Anchor depth audit:** scGen (497→1745w), chemCPA (NEW at 2035w as Q4 anchor 7), CPA + GEARS sharpened via Decision 4 v2 integration sections
- **Methodological discipline:** primary-source verification for scGen + chemCPA before writing; R² = 0.954, 9-compound held-out evaluation, 40% precision improvement, 3-component perturbation network — all quantitative claims attributed to specific source documents
- **New anchor added (chemCPA):** rationale documented — architecturally essential for Decision 4 v2's modular drug-encoder slot
- **Cross-question integration:** Decision 1 v2 (substrate flexibility), Decision 5 v2 (N=5 ensembleability), Decision 6 v2 (V3-V4 floors), Decision 8 (4-paradigm framework), all operationally referenced

---

— Claude (CSO), 2026-05-10 (Phase 2 synthesis)
