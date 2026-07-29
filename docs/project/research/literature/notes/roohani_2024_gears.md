# Roohani et al., 2024 — Predicting transcriptional outcomes of novel multigene perturbations with GEARS

## 0. Identification
- **Citation:** Roohani Y, Huang K, Leskovec J. *Nature Biotechnology* 42(6):927-935, 2024 Jun (Epub Aug 17, 2023). DOI: 10.1038/s41587-023-01905-6 ✓
- **PMC:** PMC11180609
- **License:** CC BY 4.0
- **Senior author:** Jure Leskovec (Stanford CS / Biomedical Data Science / SNAP lab)
- **Code:** github.com/snap-stanford/GEARS
- **Layer 1 question:** Q4 anchor 5 — graph-knowledge-augmented perturbation prediction
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

GEARS is **the canonical graph-augmented perturbation prediction architecture**. It explicitly leverages biological prior knowledge (gene-gene relationships, GO ontology) in a deep learning framework. **For Charter §1.3 mechanistic interpretability and §8.1 layered architecture, GEARS demonstrates how prior biological knowledge (GRN, ontology graphs) integrates with deep learning** — directly relevant to INTERCEPTA's GRN component.

## 2. What they did

**Architecture:**
- **Two prior knowledge graphs:**
  - Gene co-expression graph (gene-gene relationships)
  - Gene Ontology (GO) graph (perturbation-perturbation relationships via shared functional annotation)
- **Multi-dimensional embeddings per gene + per perturbation** (learned on the prior graphs)
- **Cross-gene layer** combines gene + perturbation embeddings
- **Gene-specific output layers** produce post-perturbation expression predictions

**Input:** unperturbed cell expression vector + perturbation set (genes to activate/repress, signed binary)
**Output:** post-perturbation transcriptional state

**Critical capability:** prior knowledge graphs **enable predictions for genes never experimentally perturbed** (graph-based extrapolation).

**Training data:** scRNA-seq from CRISPR perturbation screens (Perturb-Seq).

## 3. What they found

- **40% higher precision** than existing approaches in predicting four distinct genetic interaction subtypes in combinatorial perturbation screens
- **Identified strongest interactions 2× better** than prior approaches
- **Predicts outcomes of perturbing genes never experimentally perturbed** — enabled by knowledge graph embeddings
- **Predicts combinatorial perturbation outcomes** (single + multi-gene)
- Detects non-additive interactions (synergy) — clinically relevant
- Compared against scGen, CPA, GRN-based methods

## 4. What's strong

- **Nature Biotechnology** — top venue.
- **40% precision improvement vs prior** — strong empirical claim.
- **Graph-based knowledge integration** — Charter §1.3 mechanism trace via biological priors.
- **Predicts unseen genes** — true generalization beyond training data.
- **Open-source on snap-stanford GitHub.**
- **CC BY 4.0** open license.
- **Strong institutional backing** — Stanford SNAP lab (Leskovec is graph ML pioneer).
- **Combinatorial genetic interactions characterized** in 4 distinct subtypes — biological richness.
- **Per-gene output layers** enable gene-specific interpretation.
- **Subsequent benchmarks (Diversity-by-Design 2025) cite GEARS as one of four major perturbation prediction archetypes** alongside CPA, scGen, simple baselines.

## 5. What's limited

- **Genetic perturbations primary, not drug perturbations.** GEARS was developed on Perturb-Seq (CRISPR knockdowns), not chemical screens. **Drug response application requires extension or adaptation.**
- **Knowledge graph quality is bottleneck.** GEARS depends on co-expression + GO graphs. **Missing/incorrect edges propagate errors.** For poorly characterized genes (most of the genome's "dark matter"), graph prior is unreliable.
- **Combinatorial space still vast.** Predicting unseen 5-gene combinations requires graph extrapolation that may break down for high-order interactions.
- **No FM integration.** Pre-FM era; uses raw expression + graph features.
- **Cancer cell line training (mostly).** Cross-disease application untested.
- **Compute-intensive.** Graph neural network on full gene × perturbation graphs is GPU-heavy.
- **2024 publication; field has moved.** Foundation model era methods (post-2024) may already supersede.
- **Mode collapse issues.** Per Diversity-by-Design 2025 critique, perturbation prediction methods including GEARS suffer from mode collapse — predictions cluster around mean rather than capturing perturbation-specific shifts.

## 6. INTERCEPTA implications

**For Q4:** GEARS demonstrates **graph-augmented perturbation prediction**, a fourth Q4 architectural paradigm alongside CPA's compositional VAE, DeepCDR's hybrid GCN, PaccMann's attention-based.

**For Decision 1 layered architecture:** GEARS's gene-gene + GO graph priors are the **GRN component** of INTERCEPTA's Charter §8.1 architecture. **The architecture slot exists in Decision 1; GEARS provides the operational mechanism.**

**For Charter §1.3 mechanistic interpretability:**
- **I1:** GEARS gene-gene graph attribution = which genes drove prediction
- **I2:** GO graph navigation = pathway-level mechanism
- **I3:** Predicted unseen-gene perturbations are falsifiable by experiment

**For Charter §1.2 V1-V4:** GEARS's "predict unseen perturbations" framework is the validation paradigm.

**For Charter Q5 OOD detection:** GEARS uncertainty was not extensively characterized in the original paper — INTERCEPTA would need to add OOD detection.

**For drug perturbation extension:** GEARS architecture can extend to drug perturbations by:
- Replace gene-gene perturbation embedding with chemical structure embedding (chem-FM)
- Replace GO ontology with drug-target ontology
- Train on sci-Plex-style chemical perturbation data
- **This is INTERCEPTA's novelty territory.**

**Critique acknowledged:** Mode collapse is a known issue in perturbation prediction; INTERCEPTA Q4 architecture must explicitly address this (possible solutions: diversity loss, regularized embeddings).

## 7. Followup citations
1. **scGen** (Lotfollahi 2019 Nat Methods) — predecessor; latent-space arithmetic
2. **CellOracle / Kamimoto 2023 Nature 614** — alternative GRN-based perturbation
3. **CPA** — compositional VAE (already read)
4. **STRING database** (Szklarczyk) — protein-protein graph priors
5. **scperb** (Tang 2024) — style-transfer VAE alternative
6. **Diversity-by-Design (2025)** — mode collapse critique of all perturbation prediction methods
7. **chemCPA** (Hetzel et al. 2022, Q4 anchor 7) — modular molecular embedding extension

## 8. Decision 4 v2 Architectural Integration (Phase 2 addendum)

**GEARS's role in Decision 4 v2:** GEARS provides the **graph-augmented prediction component** for INTERCEPTA's L7 drug response layer, complementary to CPA/chemCPA's compositional VAE. Specifically:

- **Gene-gene knowledge graph + GO graph** as biological priors — relevant for V3 (cell line → tumor) and V6 (cross-disease) where biological prior knowledge transfers more reliably than learned embeddings on cancer-only training data
- **40% precision improvement** over prior methods on 4 (or 5 per biorxiv) distinct genetic interaction subtypes — quantitative benchmark for INTERCEPTA's V0-V1 floor on perturbation prediction with combinatorial effects
- **Predicts unseen-gene perturbations** via graph extrapolation — directly relevant for INTERCEPTA's drug-target inference where drug targets may be poorly characterized

**Decision 1 v2 substrate compatibility:** GEARS's gene-gene graph operates on gene-level features. **It is compatible with both FM-derived gene embeddings (Decision 1 v2 Paradigm A) and parameter-free pathway/gene representations (Paradigm D).** The graph prior is substrate-agnostic in principle.

**Decision 5 v2 ensembleability requirement:** GEARS must be N=5 Deep Ensembles-compatible per Decision 5 v2 Layer 5.2. The graph neural network components and per-gene output layers are independently trainable, so Deep Ensembles N=5 is operationally feasible (5× compute cost acknowledged in Decision 9).

**Decision 6 v2 V6 cross-disease applicability:** GEARS's biological prior knowledge (gene-gene + GO) is **transferable across diseases by construction** — gene-gene relationships in cancer are largely the same gene-gene relationships in I&I and neurodegeneration. **This makes GEARS particularly suitable for V6 cross-disease evaluation**, potentially more so than CPA which learns perturbation embeddings dataset-specifically.

**Drug perturbation extension (INTERCEPTA novelty):** GEARS was developed for genetic perturbations. For drug perturbations, INTERCEPTA must:
1. Replace gene-gene knowledge graph with drug-target ontology (DrugBank, TWOSIDES, etc.) or compound-similarity graph
2. Use chemCPA's modular molecular embedding (G slot) as the perturbation input
3. Retain GEARS's graph attention mechanism for prior-knowledge-augmented predictions

This is the **architectural fusion** of GEARS + chemCPA that INTERCEPTA's Decision 4 v2 should evaluate.

**Mode collapse risk applies:** Per Diversity-by-Design 2025 critique, GEARS suffers from mode collapse like CPA and scGen. Decision 4 v2 mitigations apply equally.

## 9. Discipline check
- [x] All claims verified (Nature Biotech, PMC, NSF, GitHub, multiple secondary sources)
- [x] DOI verified
- [x] Authors verified — Roohani first; Leskovec senior (Stanford SNAP)
- [x] Honest reporting of mode collapse + drug-vs-genetic-perturbation gap
- [x] **Decision 4 v2 integration added Phase 2** — graph-augmentation role; chemCPA fusion architecture; V6 cross-disease applicability via substrate-agnostic biological priors
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
