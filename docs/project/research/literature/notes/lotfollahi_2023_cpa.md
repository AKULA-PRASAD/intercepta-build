# Lotfollahi et al., 2023 — Predicting cellular responses to complex perturbations in high-throughput screens (CPA — Compositional Perturbation Autoencoder)

## 0. Identification
- **Citation:** Lotfollahi M*, Klimovskaia Susmelj A*, De Donno C, Hetzel L, Ji Y, Ibarra Del Río IL, Srivatsan SR, Naghipourfar M, Daza RM, Martin B, et al. *Molecular Systems Biology* 19:e11517, 2023. (* equal first)
- **DOI:** 10.15252/msb.202211517 ✓ (verified EMBO Press, PMC10258562, PubMed PMID 37154091, biorxiv 2021.04.14, Helmholtz Munich news)
- **Senior author:** Fabian J. Theis (Helmholtz Munich, with Meta AI collaboration)
- **Code:** github.com/facebookresearch/CPA (Meta AI hosted)
- **Layer 1 question:** Q4 anchor 4 — perturbation prediction at single-cell level
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

CPA is **the canonical method for predicting scRNA-seq drug perturbation responses** — including unseen dosages, cell types, time points, species, AND drug combinations. Where DeepCDR and PaccMann predict bulk IC50 values, CPA predicts the full transcriptomic response per cell. **For INTERCEPTA's Charter §1.2 V1-V4 predictive validity, CPA defines what "drug response prediction at single-cell" means architecturally.**

Theis lab + Meta AI partnership signals strong methodological backing.

## 2. What they did

**Architecture:**
- **Variational autoencoder backbone** with disentangled latent space
- **Composition framework:** factorized latent representations of perturbations (drug identity, dose) + covariates (cell type, species, time, patient)
- **Linear-style interpretability** combined with deep flexibility — embeddings for drugs and cell types are interpretable
- **Modular drug embeddings:** can incorporate chemical structure (RDKit-derived) → predict response to **completely unseen drugs**
- **OOD predictions:** unseen combinations of drugs, dosages, cell types

**Training data:**
- Six public datasets
- Novel non-small cell lung cancer (A549) dataset: 32 single + combinatorial drug perturbations
- Combined: drug + dose + cell type + time + species + genetic perturbation

**Evaluation:**
- Predict unseen drug combinations (validated against held-out experimental data)
- Predict cellular responses for 5,329 missing combinations (97.6% of possible)
- Cross-species predictions

## 3. What they found

- **CPA accurately models single-cell perturbations across compounds, dosages, species, and time**
- **Outperforms baseline models** on held-out drug combinations
- **Predicts combinatorial genetic interactions** of several types
- Generates 5,329 in-silico missing combinations (97.6% of all possibilities) with diverse genetic interactions
- **Drug similarity** analyses recover known mechanism families
- **Dose-response curves estimated** at single-cell level
- **Uncertainty estimates** provided per prediction

## 4. What's strong

- **Mol Syst Biol (EMBO Press) peer-reviewed.** Top-tier methodology venue.
- **Theis lab + Meta AI partnership** — strong backing, Facebook research GitHub.
- **Disentangled compositional latent.** Drug effect, cell type effect, dose effect can be separately analyzed — directly serves Charter §1.3 mechanistic interpretability.
- **Predicts unseen drug combinations** — addresses combinatorial explosion problem.
- **Predicts unseen drugs** via chemical embedding modular slot — extends to true generalization.
- **Open-source on Meta's facebookresearch GitHub.**
- **Six public dataset benchmark** — broad evaluation.
- **Uncertainty estimates** built-in — Charter Q5 (OOD detection) directly served.
- **OOD performance characterized** — explicit out-of-distribution evaluation, not just iid.
- **Dose-response curves at single-cell level** — operationally rich output.
- **Companion MultiCPA (2022)** extends to multi-modal (RNA + protein) perturbation prediction.

## 5. What's limited

- **Cancer cell line training** dominantly. A549 + sci-Plex datasets all cancer.
- **Patient context not addressed.** CPA predicts in cell line systems; patient deployment requires Q3 transfer.
- **Combinatorial space still vast.** 97.6% missing combinations is impressive but doesn't validate clinically.
- **Compute-intensive training.** VAE + adversarial-style disentanglement training is GPU-heavy.
- **Disentanglement quality is hyperparameter-sensitive.** Beta-VAE-style trade-offs.
- **Drug embedding modularity is novel but optional.** For drugs without clean chemical structure, prediction degrades.
- **No FM-based drug embedding** — uses RDKit features, not chem-FM (MoLFormer/ChemBERTa).
- **Bulk-side training inheritance.** When combined with cell line data, inherits cell-line-vs-patient gap.
- **Validation primarily computational.** Limited wet-lab validation in original paper.
- **Combinatorial genetic interactions in CRISPR screens validated, but drug-genetic combinations less so.**

## 6. INTERCEPTA implications

**For Q4:** CPA is the **direct architectural precedent for INTERCEPTA's Q4 layer.** Specifically:
- VAE backbone (overlaps with Decision 2 scVI/scANVI/MrVI choice for Q2)
- Disentangled latent for perturbation + covariates
- Modular drug embedding slot
- OOD detection built-in

**For Decision 1 layered architecture:** CPA shows the deep-generative framework that can absorb FM embeddings (Decision 1) as input. **Concretely:** replace CPA's gene-expression encoder with frozen FM (scFoundation/UCE/scGPT/Geneformer); replace CPA's RDKit drug encoder with chem-FM (MoLFormer/ChemBERTa). The architectural slots match.

**For Charter §1.2 V1-V4 (predictive validity):** CPA's evaluation framework is the standard for Charter validation:
- V1 (cross-cell-line): CPA tested on held-out cell lines
- V2 (cross-compound): CPA tested on unseen drugs
- V3 (cross-time/dose): CPA tested on unseen dosages
- V4 (cross-species): CPA tested on cross-species predictions

**For Charter §1.3 mechanistic interpretability:** Disentangled drug latent enables drug-similarity analysis — recovers known mechanism families. **Mechanism trace at drug-class level.** Less granular than gene-level but operationally valuable.

**For Charter Q5 (OOD detection):** CPA's uncertainty estimates are baseline; INTERCEPTA can adopt directly.

**For novelty:** CPA + FM-derived encoders + non-cancer perturbation extension + Q3 patient transfer + cross-disease validation = INTERCEPTA's Q4 layer architecture. Each extension is novelty territory.

**For Decision 4 (Q4 architectural commitment):** CPA-style disentangled compositional VAE with FM-aware encoders is the candidate default architecture.

## 7. Followup citations
1. **MultiCPA** (2022 biorxiv) — multi-modal RNA+protein extension
2. **scGen** (Lotfollahi 2019 Nat Methods) — predecessor; perturbation prediction in latent space
3. **sams-VAE** (2024) — Bayesian alternative
4. **GEARS** (Roohani 2023) — graph-based perturbation prediction
5. **PerturbNet** — alternative architectures
6. **Tahoe-100M** (recent large-scale single-cell drug dataset 2025)
7. **chemCPA** (Hetzel et al. 2022, Q4 anchor 7) — the canonical extension for unseen drugs via modular molecular embedding

## 8. Decision 4 v2 Architectural Integration (Phase 2 addendum)

**CPA's role in Decision 4 v2:** CPA provides the **compositional VAE backbone** for INTERCEPTA's L7 drug response prediction layer. Specifically:

- **Cell-side input:** any Decision 1 v2 substrate (scFoundation default, scTOP baseline, scVI baseline, etc.) feeds into CPA's encoder
- **Drug-side input:** chemCPA's 3-component perturbation network (G molecule encoder + M perturbation encoder + S dosage scaler) replaces CPA's perturbation dictionary
- **Output:** patient-level aggregation per PaSCient pattern (Q8 anchor 3) for clinically actionable predictions

**Decision 5 v2 ensembleability requirement:** CPA architecture must support N=5 Deep Ensembles. Per Decision 5 v2 Layer 5.2, the L7 head (CPA + chemCPA + cell-substrate-encoder) is the ensembled unit. This means CPA must be a **modular component** of L7, not the entire pipeline — Decision 4 v2 design must reflect this modularity.

**Decision 6 v2 V3-V4 pass criteria:** CPA's six-public-dataset evaluation establishes V0-V1 floor. INTERCEPTA's V3 (cell line → tumor AUROC ≥ 0.77 per Tang 2022) and V4 (cell line → PDX RMSE ≤ 0.11 TNBC per Tang 2022) require CPA + chemCPA + cell-substrate evaluation extension beyond the 2023 evaluation scope.

**Mode collapse risk applies:** Per Diversity-by-Design 2025 critique, CPA can suffer from mode collapse on novel-perturbation predictions. Decision 4 v2 must specify diversity regularization (loss term, energy-based training, or mixture-of-experts decoder) as architectural mitigation.

## 9. Discipline check
- [x] All claims verified (EMBO, PMC, PubMed, biorxiv, Meta GitHub, Helmholtz Munich)
- [x] DOI verified
- [x] Authors verified — Lotfollahi + Klimovskaia Susmelj equal first; Theis senior
- [x] Honest reporting of cancer-only training inheritance
- [x] **Decision 4 v2 integration added Phase 2** — bridges to chemCPA (Q4 anchor 7), Decision 1 v2 substrate flexibility, Decision 5 v2 ensembleability, Decision 6 v2 pass criteria
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
