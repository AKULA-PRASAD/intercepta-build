# Zheng et al., 2023 — Enabling Single-Cell Drug Response Annotations from Bulk RNA-Seq Using SCAD

## 0. Identification
- **Citation:** Zheng Z, Chen J, Chen X, Huang L, Xie W, Lin Q, Li X, Wong K-C. *Advanced Science* 10(11):2204113, 2023.
- **DOI:** 10.1002/advs.202204113 ✓ (verified via Wiley Online Library, PubMed PMID 36762572, PMC10104628)
- **Senior author:** Ka-Chun Wong (City University of Hong Kong)
- **Status:** Peer-reviewed Advanced Science (Wiley); open-access PMC.
- **Layer 1 question:** Q3 (Bulk-to-single-cell transfer) — anchor 1
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

SCAD is **the canonical adversarial domain adaptation method for bulk-to-scRNA drug response transfer**. For Charter Q3, this is the method-of-record baseline. Reading SCAD first establishes the field's primary approach to the bulk→single-cell knowledge transfer problem.

## 2. What they did

**Architecture:**
1. **Source domain:** GDSC bulk RNA-seq + drug sensitivity labels (IC50 values) for ~1000 cell lines × ~250 drugs
2. **Target domain:** scRNA-seq cells (no drug labels initially)
3. **Shared feature extractor:** neural network encoder mapping both domains to common latent space
4. **Domain discriminator:** adversarial classifier trying to distinguish source vs target latent representations; gradient reversal layer (GRL) forces feature extractor to learn **domain-invariant** representations
5. **Drug response predictor:** trained on source domain (bulk + labels); transfers to target domain via shared encoder

**Validation:**
- 7 drugs benchmarked (sequenced prior to treatment)
- 5-fold cross-validation for hyperparameter selection
- Metrics: average AUC, AUPR
- Used SCP542 dataset (EpiSen-high vs EpiSen-low cells with distinct drug response, validated by in vitro cell viability)

## 3. What they found

- SCAD outperforms direct transfer (no domain adaptation) and prior baselines on AUC/AUPR
- Including all genes (not just HVG/PPI subsets) gave higher 5-fold AUC and AUPR — more genes = more information for domain discriminator
- EpiSen-high vs EpiSen-low cells correctly stratified by drug sensitivity prediction (validated by independent in vitro experiments)
- Source domain restricted to solid tumor cell lines vs all cell lines: solid-tumor-only sometimes outperforms (more focused training data)

## 4. What's strong

- **First clean adversarial DA framework for bulk→scRNA drug response transfer.** Establishes paradigm.
- **Validated with independent in vitro cell viability experiments** — ground truth beyond computational metrics.
- **GDSC integration** — uses the largest publicly available pharmacogenomic database.
- **Open-source code + clear architecture description**.
- **Per-drug validation across 7 drugs** — not single-drug overfitting.
- **Peer-reviewed Advanced Science (Wiley); open-access PMC.**
- **DAGFormer 2025 (PLoS Comp Bio) explicitly benchmarks against SCAD as state-of-the-art baseline**, confirming SCAD's continued relevance.

## 5. What's limited

- **Only 7 drugs.** Far from the ~250 drugs in GDSC. Coverage of pharmacology is narrow.
- **Single-source-domain limitation.** Per the scAdaDrug 2024 paper (arxiv 2403.05260), SCAD's reliance on a single source (all cell lines or solid tumor only) "limits ability to learn essential mechanism of diverse cell types responding to drug treatment."
- **AUC/AUPR but no ACC** — DAGFormer note that SCAD's metric set is incomplete.
- **No FM integration tested.** SCAD predates scFoundation/UCE/scGPT integration; uses raw gene expression as input.
- **No cross-disease test.** Cancer-trained → autoimmune-applied unbenchmarked.
- **Domain adaptation is unsupervised on target side.** No use of cell type or pathway information at single-cell resolution.
- **scRNA-seq dropout and batch effects not explicitly modeled.** SCAD treats scRNA-seq as a generic target domain; doesn't leverage scRNA-seq-specific structure.
- **AUC values for 7 drugs typically in 0.6-0.85 range per paper** — useful but not approaching the F1=0.97 reported by scFoundation on cancer drug response.

## 6. INTERCEPTA implications

**For Q3 (bulk-to-scRNA bridge):**
- SCAD establishes that **adversarial domain adaptation works** in principle for this problem. Not toy demonstration; published peer-reviewed validation.
- However, single-source single-drug-set limitations leave room for INTERCEPTA's improvement.

**For Decision 1 architecture:**
- SCAD's "domain-invariant feature extractor" is conceptually the same as INTERCEPTA's "FM cell representation that works across cancer + autoimmune + neurodegeneration." **Adversarial DA is a candidate Layer 2 mechanism for cross-disease generalization.**

**For novelty:** SCAD + FM embeddings is unbenchmarked. SCAD + multi-source domain (all GDSC drugs simultaneously) is what scAdaDrug attempted — read next.

## 7. Followup citations
1. **Chen et al., 2022 — scDEAL** (Nat Commun) — MMD-based predecessor; needs read
2. **scAdaDrug** (arxiv 2403.05260, 2024) — multi-source DA extension; needs read
3. **DAGFormer 2025** (PLoS Comp Bio 1013832) — graph-based domain adaptation
4. **GDSC source dataset** (Yang 2012) — reference database
5. **scRank** (Li 2024 Cell Reports Medicine) — different approach: GRN-based, no DA needed
6. **Beyondcell** (Fustero-Torre 2021) — pathway-signature-based alternative

## 8. Discipline check
- [x] All claims sourced (Wiley, PMC, PubMed, DAGFormer paper, scAdaDrug paper)
- [x] DOI verified across 4+ sources
- [x] Authors verified primary-source (Zheng Z first; Wong K-C senior — confirmed via PMC and PubMed)
- [x] Limitations include CSO-identified ones (single-source, no FM, no cross-disease)
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
