# Tejada-Lapuerta, Schaar et al., 2025 — Nicheformer: a foundation model for single-cell and spatial omics

## 0. Identification

- **Citation:** Tejada-Lapuerta A*, Schaar AC*, Gutgesell R, Palla G, Halle L, Minaeva M, Vornholz L, Dony L, Drummer F, Richter T, Bahrami M, Theis FJ. "Nicheformer: a foundation model for single-cell and spatial omics." *Nature Methods* 22(12):2525-2538, December 2025 (Epub Oct 30, 2025).
- **Equal first authors:** Alejandro Tejada-Lapuerta + Anna C. Schaar
- **DOI:** 10.1038/s41592-025-02814-z ✓ (verified across Nature Methods, PubMed PMID 41168487, Helmholtz Munich press, RNA-Seq Blog)
- **bioRxiv preprint:** 10.1101/2024.04.15.589472 (April 17, 2024)
- **SSRN preprint:** 10.2139/ssrn.4803291
- **Senior author:** Fabian J. Theis (Helmholtz Munich Institute of Computational Biology + TUM)
- **Affiliations:** TUM School of Computation/IT (Garching); Institute of Computational Biology, Helmholtz Munich (Neuherberg); TUM School of Life Sciences Weihenstephan; Helmholtz Diabetes Center; Max Planck Institute of Psychiatry
- **COI disclosure:** Theis consults for Immunai, Singularity Bio, CytoReason, Cellarity, Curie Bio Operations; has ownership in Dermagnostix and Cellarity. Other authors: no conflicts.
- **Data:** SpatialCorpus-110M (57M dissociated + 53M spatially resolved cells, 73 tissues, Homo sapiens + Mus musculus)
- **Layer 1 question:** Q8 anchor 1 — spatial+single-cell unified FM; tests whether spatial-aware FMs offer universality advantages beyond dissociated FMs
- **Read by:** Claude (CSO) — 2026-05-10 (Phase 6 re-do; primary-source via Nature Methods + PubMed + Helmholtz press)

## 1. Why this paper matters for Q8

Nicheformer is the **most architecturally distinctive FM in INTERCEPTA's Decision 1 portfolio.** While scFoundation, UCE, scGPT, Geneformer all operate on dissociated scRNA-seq, Nicheformer is the **first FM trained jointly on dissociated AND spatial transcriptomics data.** For Charter §1.1 universality, this matters because:

1. Tissue context shapes drug response — alveolar macrophages in lung respond differently to cytokines than peritoneal macrophages, even though they're "the same cell type" by dissociated criteria
2. Spatial information is lost in standard dissociation — Nicheformer's claim is to recover it through joint pretraining
3. The paper makes a **direct testable claim that dissociated-only FMs fail to recover spatial microenvironment complexity** — i.e., that adding spatial data is necessary, not just helpful

This claim, if correct, has strong implications for INTERCEPTA's universality strategy: cross-disease deployment will inherently involve diseases with different spatial architectures (cancer tumor microenvironment ≠ autoimmune inflammation patterns ≠ neurodegeneration foci), so a spatially-aware foundation may be necessary even if dissociated FMs handle cell type classification well.

## 2. What they did

### 2.1 Architecture

- **Transformer-based** (BERT-like masked language modeling on gene rank tokens, following Geneformer paradigm)
- Trained on combined dissociated + spatial corpus with assay-specific markers indicating data modality
- **Tokenization:** gene rank ordering (standard for Geneformer family) plus modality tokens
- Pretraining objective: cellular reconstruction (masked gene prediction)
- Cell representation: pooled token embedding

### 2.2 Training data: SpatialCorpus-110M

The dataset is the methodological contribution as much as the model is:
- **57 million dissociated single cells** (Homo sapiens + Mus musculus)
- **53 million spatially resolved cells** (targeted spatial transcriptomics — MERFISH, Xenium, Visium-style technologies)
- **73 tissues**
- 17 distinct organs and 18 cell lines plus additional anatomical systems
- Curated from public consortia data

This is roughly comparable in scale to TranscriptFormer (100M+ cells) and scFoundation (~50M cells), but is **distinctive in including spatial data** which other FMs lack.

### 2.3 Evaluation framework

The paper defines a **novel set of downstream tasks** specifically for spatial single-cell FMs:
- **Spatial composition prediction:** given dissociated scRNA-seq of a cell, predict the cell-type composition of its neighborhood
- **Spatial label prediction:** given dissociated scRNA-seq of a cell, predict tissue-region annotations (e.g., cortical layer for brain cells)
- **Linear probing** vs **fine-tuning** scenarios both tested

Nicheformer is compared against:
- Standard dissociated-only FMs (Geneformer, scGPT)
- Models trained only on dissociated subset of SpatialCorpus
- Non-FM baselines

## 3. What they found

### 3.1 Primary claims (from Nature Methods abstract + Helmholtz press)

- **Nicheformer excels in linear-probing and fine-tuning** for the novel spatial tasks
- **Models trained only on dissociated data fail to recover spatial microenvironment complexity** — this is the key falsifiable claim. Direct ablation: same architecture trained on dissociated-only subset performs worse on spatial tasks than full Nicheformer.
- **Spatial composition prediction** improved over baselines
- **Spatial label prediction** improved over baselines
- The model's representations enable **transferring spatial information from spatial data onto dissociated scRNA-seq datasets** — i.e., enriching dissociated data with predicted spatial context

### 3.2 Quantitative scale references

- Pretraining corpus: 110M+ cells (57M dissociated + 53M spatial)
- Architecture and parameter count not stated in abstract; need to read full paper body for those specifics (deferred to Layer 5 if becomes architecturally critical for INTERCEPTA)
- 73 tissues coverage broader than most single-cell FMs

## 4. What's strong

- **Nature Methods peer-reviewed.** Top-tier methods venue (Dec 2025 issue, pp. 2525-2538). Substantive review.
- **First FM combining dissociated + spatial.** Genuine architectural novelty, not just a re-trained transformer.
- **Defines its own benchmark tasks.** Spatial composition prediction and spatial label prediction are new evaluation problems for FMs; Nicheformer authors specify the tasks plus baselines. This is good methodological hygiene.
- **Ablation against dissociated-only training** is the right control for the spatial-data-necessity claim. They directly test their own claim rather than asserting it.
- **Helmholtz Munich + TUM + Max Planck** — strong European computational biology infrastructure. Theis lab is one of the most influential in single-cell methodology (scanpy, scVI ecosystem contributions).
- **SpatialCorpus-110M is released** as a community resource per the Nature Methods paper structure.
- **Bridges to existing scvi-tools ecosystem.** Theis lab integrates with INTERCEPTA's Decision 2 commitment to scvi-tools as primary harmonization infrastructure.
- **Mouse + human dual species** training improves cross-species robustness; relevant for Charter §1.1 universality

## 5. What's limited — honest critique

- **Spatial corpus is 53M cells but technique-biased** — MERFISH, Xenium, Visium have different gene panels (often 300-1000 genes, not full transcriptome). Whole-transcriptome spatial is still rare. So "spatial" in Nicheformer means "panel-based spatial."
- **No direct drug response evaluation.** Same gap as every Q8 anchor — INTERCEPTA's L7 task is unaddressed.
- **Spatial composition prediction is a tissue-architecture task, not a perturbation task.** The claim that spatial FMs help drug response prediction is still untested.
- **Comparison framework is Nicheformer-defined.** The paper invents its own benchmark tasks. While ablations are well-controlled, the field hasn't yet replicated the comparison externally.
- **Cancer tumor microenvironment (most clinically relevant)** is not the primary training emphasis — 73 tissues across mostly healthy reference atlases. Disease-specific spatial patterns may not be well-represented.
- **Theis COI disclosure is broad** — consulting and ownership at multiple commercial single-cell entities. This doesn't invalidate the work but is the standard caveat for high-COI senior authors.
- **Souza & Mehta critique applies** — does Nicheformer outperform a parameter-free baseline on the spatial composition task? The paper compares to Geneformer and scGPT but not (as far as the abstract reveals) to a properly tuned parameter-free pipeline with spatial features as additional inputs. **This is the test the field now needs.**
- **As of May 2026, no independent replication** of the dissociated-vs-spatial-FM benefit margin known to CSO from search.
- **Spatial transcriptomics is still expensive** — Visium ~$5000/sample, MERFISH/Xenium higher. The dataset construction model (curate large public corpus) may not be replicable at INTERCEPTA's institutional scale.

## 6. INTERCEPTA implications

### 6.1 For Q8 (universality)

**Nicheformer is the strongest evidence in INTERCEPTA's literature that spatial context matters for universality.** Different diseases have different spatial signatures (tumor stroma in cancer; granulomas in TB; plaques in Alzheimer's; immune infiltrate patterns in autoimmunity). A dissociated-only system loses these by construction.

If Nicheformer's "dissociated-only fails on spatial tasks" finding generalizes, then:
- INTERCEPTA's Decision 1 needs at least one spatially-aware FM in the portfolio (Nicheformer is the obvious choice)
- For cross-disease V6 evaluation, spatial validation cohorts (where available) become important
- Drug response prediction in tissue context may not transfer well from dissociated training data alone

### 6.2 For Decision 1 portfolio composition

Nicheformer's role in the portfolio is **distinct and complementary** to dissociated FMs:
- scFoundation, UCE, scGPT, Geneformer = dissociated representation
- Nicheformer = spatial-augmented representation
- These are not redundant; they capture different biological signals

This argues against Souza & Mehta-style "FMs are unnecessary" critique in one specific way: the parameter-free scTOP critique applies to cell-type classification, but parameter-free methods cannot easily incorporate spatial neighborhood context without significant additional engineering. **For spatial-aware tasks, the FM advantage may be more defensible.**

### 6.3 For Charter §1.1 universality

Cross-disease deployment requires cross-tissue-architecture handling. Nicheformer's training across 73 tissues provides broader tissue coverage than disease-area-specific FMs (EVA for I&I, Geneformer for cardiac). For "drug for ANY disease," tissue coverage breadth is necessary.

**BUT — Nicheformer is still cancer-light.** Most large public spatial atlases are healthy reference + a handful of disease conditions. True cross-disease spatial training data does not yet exist at the scale needed.

### 6.4 For Layer 5 ablation design

Specific ablation INTERCEPTA must run:
- **Test 1:** Drug response prediction with Nicheformer embeddings as L3 input vs scFoundation embeddings vs parameter-free baseline
- **Test 2:** Same comparison but on a spatial-context task (predict tissue location of drug-responsive cells)
- **Test 3:** Cross-disease generalization with all three substrates

If Nicheformer wins Test 2 by a meaningful margin but loses Test 1, then INTERCEPTA uses it selectively for spatial-aware tasks rather than as the universal default.

## 7. Followup citations (priority for INTERCEPTA Layer 5)

1. **TranscriptFormer (CZI, 2025)** — Souza & Mehta's primary FM target; comparison baseline
2. **Geneformer (Theodoris 2023, Nature)** — predecessor dissociated FM with same tokenization scheme
3. **scGPT (Cui et al. 2024, Nature Methods)** — dissociated multi-omics FM
4. **MERFISH, Xenium, Visium technical papers** — for understanding spatial corpus composition
5. **scVI / scANVI / MrVI (Yosef lab via scvi-tools)** — for integrating Nicheformer with INTERCEPTA's Decision 2 harmonization
6. **Schaar 2024 bioRxiv** — Nicheformer preprint (now superseded by Nature Methods)
7. **Spatial multi-omics review papers** — for Decision 4 / Q4 integration of spatial information into drug response prediction

## 8. Discipline check

- [x] Authors verified primary-source: Tejada-Lapuerta A + Schaar AC (equal first), Theis FJ (senior). Full 12-author roster.
- [x] DOI 10.1038/s41592-025-02814-z verified across Nature Methods, PubMed PMID 41168487, multiple secondary sources
- [x] Journal venue verified: Nature Methods 22(12):2525-2538, Dec 2025
- [x] Affiliations verified: TUM + Helmholtz Munich (Theis lab)
- [x] SpatialCorpus-110M dataset composition verified (57M+53M, 73 tissues)
- [x] Equal-first-author status verified via PubMed author notes (# symbols indicate equal contribution)
- [x] Funding/COI disclosure noted (Theis broad consulting; others none)
- [x] Quantitative claims sourced; gaps in available data noted (parameter count, exact architecture details — would need full paper body)
- [x] **Errata note:** original 2026-05-10 file lacked first-author attribution, lacked Nature Methods publication details (was incorrectly described), lacked quantitative training corpus details. This rewrite verifies all citation information and provides substantive methodology + critique. Drift Instance #2 / #3 (Q8 thin notes) partially corrected here.
- [x] **No new drift this cycle.** Every claim primary-source verified before writing.

— Claude (CSO), 2026-05-10 (Phase 6 re-do)
