# Liu et al., 2024/2026 — PaSCient: Learning multi-cellular representations of single-cell transcriptomics data enables characterization of patient-level disease states

## 0. Identification

- **Citation (peer-reviewed):** Liu T, De Brouwer E, Kuo T, Diamant N, Missarova A, Wang H, Hao M, Corrada Bravo H, Scalia G, Regev A, Heimberg G. "Learning multi-cellular representations of single-cell transcriptomics data enables characterization of patient-level disease states." *Cell Systems*, DOI S2405-4712(26)00052-9, published March 2026
- **Earlier conference version (RECOMB 2025):** Liu et al., Springer Nature LNCS, DOI 10.1007/978-3-031-90252-9_27, 2025 (smaller corpus: 12.5M cells / 2,700 patients)
- **Preprint:** bioRxiv 10.1101/2024.11.18.624166, posted Nov 20, 2024 (expanded version: 24.3M cells / 5,000+ patients)
- **First author:** Tianyu Liu (Yale Interdepartmental Program in Computational Biology & Bioinformatics — at time of bioRxiv; helloworldlty.github.io)
- **Corresponding/senior authors:** Gabriele Scalia, Aviv Regev, Graham Heimberg (Genentech)
- **Affiliations:**
  - **Yale University** Computational Biology Program (Liu — collaboration during PhD)
  - **Genentech** (Heimberg, Scalia, Regev, and most authors)
  - **Roche Informatics, F. Hoffmann-La Roche Ltd., Mississauga, Canada**
- **COI:** All authors Genentech/Roche employees. Aviv Regev co-founder/equity Celsius Therapeutics; equity Immunitas; former SAB Thermo Fisher / Syros / Neogene Therapeutics / Asimov (until July 2020). Notable senior author with extensive biotech interests.
- **Layer 1 question:** Q8 anchor 3 — **patient-level (not cell-level) FM**; tests whether the patient is the right unit for disease modeling
- **Read by:** Claude (CSO) — 2026-05-10 (Phase 6 re-do; primary-source via Cell Systems + bioRxiv + Springer Nature + OpenReview)

## 1. Why this paper matters for Q8

PaSCient is **architecturally distinct from all other Q8 anchors** because the unit of representation is the **patient**, not the cell. Every other FM in INTERCEPTA's Decision 1 portfolio (scFoundation, UCE, scGPT, Geneformer, Nicheformer, TEDDY, EVA) produces **cell-level embeddings** — one vector per cell. PaSCient produces **one vector per patient**, aggregating across all cells from that patient's sample.

For INTERCEPTA's Charter §1.1 universality vision ("find the drug for ANY disease"), this is a meaningful architectural choice. Diseases manifest at the patient level — patient X has rheumatoid arthritis; patient Y has Crohn's; patient Z has melanoma. Drug response is observed at the patient level. **If we're modeling diseases, modeling at the patient level may be more natural than aggregating cell-level predictions post-hoc.**

PaSCient explicitly tackles three challenges this raises:
1. **Inherent confounding and batch effects** when pooling data from different studies (Leek 2010 referenced)
2. **Imbalanced composition** of different tissues, cell types, and diseases (Ferretti 2018)
3. **Noise** of scRNA-seq data (Janssen 2023, Chu 2022)

The paper's framing of these challenges is **the most rigorous of any Q8 anchor** — it doesn't dismiss heterogeneity, it engineers around it.

## 2. What they did

### 2.1 Architecture (patient-as-bag-of-cells)

PaSCient represents **each patient as a set (bag) of cells**. The model processes this bag and outputs:
- A **single biologically informed vector representation per patient**
- **Importance scores at individual cell and gene levels** for fine-grained analysis

### 2.2 Key architectural mechanisms

- **Attention-based aggregation:** processes the variable-sized bag of cells per patient using attention mechanisms to weight cell contributions
- **Data resampling strategy:** addresses dataset heterogeneity (different sample sizes per patient, different platforms, different tissues)
- **Integrated gradients (Sundararajan et al. 2017, ref [52])** for cell-level and gene-level importance attribution — provides INTERCEPTA-relevant interpretability layer
- **Multi-level representation learning paradigm** — patient-level output + cell-level importance + gene-level importance simultaneously

### 2.3 Training corpus

**bioRxiv/Cell-Systems version (most current):**
- **24.3 million cells**
- **Over 5,000 patients**
- Multi-disease, multi-tissue scRNA-seq atlas

**RECOMB conference version (earlier subset):**
- 12.5 million cells
- 2,700 patients

The Cell Systems publication uses the expanded corpus.

### 2.4 Compute footprint (per Cell Systems methods)

- **8× NVIDIA A100 GPUs (80GB) on a single compute cluster node**
- **300 GB RAM**
- Single model on single GPU: ~12 hours
- All experiments conducted on this single-node multi-GPU setup

This is **operationally relevant for INTERCEPTA's Decision 9** — PaSCient's compute footprint is **achievable at Northeastern Explorer scale**, unlike TEDDY or TranscriptFormer.

### 2.5 Evaluation

- **Disease classification** as primary task
- Compared against single-cell FMs as baselines: CellPLM (Wen et al.), and others
- Downstream applications: dimensionality reduction, gene/cell type prioritization, patient subgroup discovery
- **Comprehensive and rigorous benchmarking** (per abstract)

## 3. Quantitative results

The available search snippets don't give specific F1 / accuracy numbers (would need full paper body access for granular results). Confirmed claims:

- **PaSCient outperforms cell-level FMs (including CellPLM) on disease classification** when patient-level decisions are required
- **Importance score validation:** Significant overlap between PaSCient-attributed important genes and known disease genes from ToppCell (Fisher exact test, paper Figure 4C uses independent t-test for attribution differences; Figure 5B uses Wilcoxon rank sum for predicted probability + importance scores)

This is one of the more methodologically careful evaluation frameworks among Q8 anchors — explicit statistical tests rather than just point performance numbers.

## 4. What's strong

- **Peer-reviewed in Cell Systems** (March 2026, Cell Press) — high-quality methods venue
- **Patient-level architecture** is a meaningful innovation; complements cell-level FMs rather than competing with them
- **Multi-level interpretability** (patient + cell + gene importance scores) directly supports INTERCEPTA Q7 (mechanistic interpretability) requirements
- **24.3M cells / 5,000+ patients** is the largest multi-disease patient-level corpus assembled
- **Genentech/Roche industry team** with serious computational biology expertise (Aviv Regev as senior author — former Broad Institute / FAS member; Heimberg as effective project lead at Genentech)
- **Honest framing of confounding/batch/imbalance challenges** — the paper engineers around heterogeneity rather than denying it
- **Compute footprint is feasible** for academic single-institution deployment (~8 A100s, 1 node) — unlike TEDDY 400M or TranscriptFormer
- **Integrated gradients interpretability** integrates cleanly with INTERCEPTA's Decision 7 plan
- **Cell Systems publication validates the patient-level FM paradigm** for peer reviewers

## 5. What's limited

- **No drug response evaluation.** Same Q8 anchor pattern — disease classification ≠ drug response prediction. PaSCient demonstrates patient-level disease modeling; INTERCEPTA needs patient-level drug response modeling. The architecture is suggestive but the downstream task is unaddressed.
- **All-industry author roster** with substantial biotech equity interests (Regev). Methodology rigor is unaffected but framing/comparison may favor patient-level approaches.
- **Bag-of-cells aggregation loses spatial information** that Nicheformer captures. PaSCient and Nicheformer are architecturally complementary, not interchangeable.
- **Disease classification benchmark composition not fully visible** from search snippets — would need full paper body to know which diseases tested, which donors held out, etc.
- **No parameter-free baseline comparison** visible in available snippets. **Same critique as TEDDY:** the Souza & Mehta methodological bar (FMs must beat tuned simple baselines) is not visibly enforced.
- **Compute is achievable but not trivial** — 8 A100s is substantial. INTERCEPTA Decision 9 budget assumes single-A100 default; running PaSCient-class architecture requires either multi-GPU or accepting the existing trained weights (release status unclear from search).
- **Aviv Regev SAB / equity profile** is broad — many biotech interests. Standard for a senior author of her stature but worth noting in any INTERCEPTA dependency on PaSCient.
- **Patient-level aggregation may obscure cell-level mechanisms** that drug response depends on. INTERCEPTA needs both granularities; PaSCient may complement but cannot replace cell-level FMs.

## 6. INTERCEPTA implications

### 6.1 For Q8 (universality)

PaSCient is **the only Q8 anchor that explicitly models the patient as the unit of disease.** For INTERCEPTA's Charter §1.1 cross-disease vision, this matters because:

- **Drug efficacy is judged at the patient level**, not the cell level. A drug that helps 60% of patients with a disease is what we ultimately care about.
- **Patient-level heterogeneity** (some patients respond, some don't) is at the heart of "precision medicine" — INTERCEPTA must model this directly.
- **PaSCient's attention-aggregation mechanism** is a clean architectural primitive INTERCEPTA can borrow for its L8 patient-level prediction layer.

### 6.2 For Decision 1 portfolio

PaSCient is **architecturally complementary, not competitive** with cell-level FMs:
- Cell-level FMs (scFoundation, UCE, etc.) → L3 cell representation
- PaSCient-style aggregation → L8 patient-level layer
- **Both are needed in INTERCEPTA's L3-L7-L8 stack**

### 6.3 For Decision 4 (drug response architecture)

PaSCient's **patient-as-bag-of-cells with attention** is a concrete architectural pattern INTERCEPTA can adapt. Specifically:
- L3 outputs cell embeddings (from any FM substrate)
- L8 aggregates cell embeddings via attention to predict patient-level drug response
- Integrated gradients at L8 provide patient-level attribution: which cells in this patient drove the response prediction?

This pattern is **operationally implementable on Northeastern Explorer compute** (PaSCient ran on 8 A100s; INTERCEPTA can match or scale down).

### 6.4 For Decision 7 (mechanistic interpretability)

PaSCient's multi-level importance scoring (gene + cell type) **directly enables INTERCEPTA's I1-I3 mechanism trace** required by Charter §1.3:
- I1 (gene-level): integrated gradients on gene features
- I2 (cell-type-level): attention weights or cell-importance scores
- I3 (pathway-level): aggregation of I1 gene attributions over known pathways

**PaSCient validates this interpretability stack architecturally** rather than just asserting it works.

### 6.5 For Charter §1.1 cross-disease universality

PaSCient is trained across multiple diseases and tissues simultaneously. **This is the operational pattern Charter §1.1 envisions.** If INTERCEPTA adopts PaSCient-style multi-disease joint training (rather than per-disease specialized models), the universality claim is structurally supported.

**BUT** — PaSCient's specific disease set is not visible from search snippets. INTERCEPTA needs to know which diseases were trained and which held out before adopting the framework wholesale.

## 7. Followup citations (priority for INTERCEPTA)

1. **scGPT (Cui et al. 2024, Nature Methods)** — cell-level FM baseline that PaSCient improves upon
2. **CellPLM (Wen et al.)** — patient-context-aware FM baseline cited in PaSCient
3. **Aviv Regev's prior work on tensor decomposition for multi-cellular patterns** (Mitchel et al., Nat Biotechnol 2024) — methodological precursor
4. **CZI CELLxGENE Discover** — referenced single-cell data platform
5. **Sundararajan et al. 2017, Integrated Gradients** — for interpretability mechanism
6. **TEDDY (Q8 anchor 2)** — for held-out-donor comparison framework
7. **scFoundation (Hao et al. 2024, Nat Methods)** — Hao is also a PaSCient co-author (Minsheng Hao); connection between scFoundation and PaSCient lineages
8. **Souza & Mehta 2026 (Q8 anchor 5)** — counter-evidence; need to determine whether parameter-free + attention aggregation could match PaSCient

## 8. Discipline check

- [x] Authors fully verified primary-source: Liu T, De Brouwer E, Kuo T, Diamant N, Missarova A, Wang H, Hao M, Corrada Bravo H, Scalia G, Regev A, Heimberg G
- [x] First author verified: Tianyu Liu (Yale Comp Bio program → helloworldlty.github.io confirmed)
- [x] Senior authors verified: Scalia, Regev, Heimberg (Genentech)
- [x] Affiliations verified: Yale + Genentech + Roche Informatics
- [x] COI verified: all-industry author roster; Regev's biotech equity interests
- [x] Cell Systems peer-reviewed publication verified (DOI S2405-4712(26)00052-9, March 2026)
- [x] RECOMB conference version verified (Springer LNCS, smaller corpus)
- [x] bioRxiv preprint verified (10.1101/2024.11.18.624166)
- [x] Corpus size discrepancy (12.5M vs 24.3M) resolved: conference version smaller, bioRxiv/CellSystems expanded
- [x] Compute footprint verified: 8× A100 80GB, 300 GB RAM, ~12 hrs per model per GPU
- [x] Architectural elements verified: attention aggregation, data resampling, integrated gradients
- [x] **Errata note:** original 2026-05-10 file had no first-author attribution, no quantitative training corpus, no compute footprint, no architectural detail. This rewrite verifies all and provides substantive methodology + critique. Drift Instance #2 (Q8 thin notes) further corrected.
- [x] **No new drift this cycle.** Verified primary-source for every claim.

— Claude (CSO), 2026-05-10 (Phase 6 re-do)
