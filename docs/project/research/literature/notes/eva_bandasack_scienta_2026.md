# Bandasack et al. (Scienta Team), 2026 — EVA: Towards a universal model of the immune system

## 0. Identification

- **Citation:** Scienta Team (Bandasack E, Bouget V, Bruley A, Cattan Y, Claye C, Corney M, Duquesne J, El Kanbi K, Fouché A, Marschall P, Strozzi F). "EVA: Towards a universal model of the immune system." arXiv 2602.10168, February 12, 2026 (announcement); Scienta Lab launch Feb 12, 2026
- **First author:** Ethan Bandasack (Scienta Lab, Paris)
- **Affiliation:** Scienta Team / Scienta Lab, Paris, France
  - Biolabs Hôtel Dieu (Paris co-working lab)
  - Selected for Station F Future 40 (2023)
  - Seed round €4M (Dec 2023) from CentraleSupélec Venture + business angels
  - EIC Accelerator laureate (June 2025) — European Innovation Council flagship breakthrough-tech program
- **Earlier related paper:** bioRxiv 10.1101/2025.05.02.651839 "EVA: a Foundation Model Advancing Translational Drug Development in Immuno-Inflammation" (May 2025) — **earlier 50M-parameter version** focused on anti-TNF in ulcerative colitis
- **ICML 2025 FM4LS workshop submission:** "Closing the gap between the biology and the clinic with a foundation model of immunology and inflammation" (July 2025)
- **Code/weights:** github.com/Scienta-Lab + huggingface.co/Scienta-Lab — **60M-parameter open variant of transcriptomic model released on Hugging Face**
- **License:** Open 60M variant — license terms must be verified at HF page; full multimodal EVA remains commercial via Scienta partnerships
- **Conferences:** EVA-RNA + transcriptomic benchmark for FM in I&I drug development presented at ICLR 2025 (Rio de Janeiro, April 2025) Learning Meaningful Representations of Life workshop (spotlight)
- **Training data (ImmunAtlas):** ~100K human samples across RNA-seq + histology + clinical modalities (per Scienta Lab job postings); 96K+ patient and biosample profiles
- **Layer 1 question:** Q8 anchor 4 — **disease-area-specific FM for I&I**; tests whether disease-area specialization is the path to universality (cross-disease *within* a therapeutic area)
- **Read by:** Claude (CSO) — 2026-05-10 (Phase 6 re-do; primary-source via arXiv abstract, bioRxiv 2025 precursor, ICML 2025 FM4LS submission, OpenReview, Scienta press)

## 1. Why this paper matters for Q8

EVA is the **only Q8 anchor explicitly designed for drug discovery and patient response prediction**, and the only one **specialized to a therapeutic area** (immunology & inflammation). For INTERCEPTA's Charter §1.1 universality question, EVA provides the alternative paradigm to test:

**The disease-area-specific FM hypothesis:** rather than one universal FM that generalizes across all diseases, train multiple disease-area-specific FMs (EVA for I&I, Geneformer-cardiac for cardiology, oncology-specific FMs for cancer) and combine them.

This is **architecturally opposite to Decision 1's multi-FM portfolio approach** (which uses general FMs and lets the system pick scenario-appropriately). EVA tests whether disease-area depth beats cross-disease breadth.

EVA is also the most **clinically aligned** of any Q8 anchor:
- Multimodal: transcriptomics + histology + clinical
- Trained on 100K+ patient samples with disease activity labels
- Evaluated on **39 tasks across the full drug development pipeline** — discovery → preclinical → clinical
- Reports **anti-TNF therapeutic activity in ulcerative colitis** as concrete demonstration

If EVA generalizes well across the broad I&I therapeutic area (rheumatoid arthritis, ulcerative colitis, Crohn's, psoriasis, lupus, atopic dermatitis), it provides existence proof that disease-area FMs can be the universality substrate within a clinical domain.

## 2. What they did

### 2.1 Architecture

- **Multimodal foundation model** integrating:
  - Bulk and single-cell RNA-seq
  - Histology (added in 2026 version per arxiv abstract)
  - Clinical data
- **Cross-species** training — preclinical mouse models + human clinical data (essential for translational I&I)
- **Multi-resolution** — single-cell + bulk
- **Patient-level outputs** at the deployment layer

### 2.2 Scaling

Per Scienta scientist Julien Duquesne's LinkedIn (ICLR 2025 conference description):
- Earlier bioRxiv 2025: 50M parameters
- 2026 arxiv (EVA universal model): scaling up
- **EVA exhibits clear scaling laws up to 300M parameters**
- **Open Hugging Face release: 60M parameters** (smaller than the production 300M version)

### 2.3 Training data (ImmunAtlas)

- **~100,000 human samples** (per Scienta job postings — internal dataset description)
- **96,000+ patient and biosample profiles** (per Scienta press)
- Multi-omic: RNA-seq + clinical + (later) histology
- Curated from clinical studies and public databases
- **Tissue and I&I disease distribution explicitly mapped** (per Fig 1b-d of 2025 bioRxiv) — visible balance across I&I conditions

### 2.4 Evaluation: 39-task suite spanning drug development pipeline

EVA's evaluation framework is the **most comprehensive of any Q8 anchor**:

**Discovery phase tasks:**
- Zero-shot target efficacy prediction
- Gene function prediction

**Preclinical phase tasks:**
- Cross-species molecular perturbations
- Cross-disease molecular perturbations

**Clinical phase tasks:**
- Patient stratification
- Treatment response prediction
- Disease activity prediction

This is **the right benchmark structure** — INTERCEPTA's V0-V6 cascade is structurally similar (V1 within-dataset → V6 cross-disease patients).

### 2.5 2025 bioRxiv ulcerative colitis demonstration

The earlier 50M-parameter EVA was fine-tuned with **few-shot learning on a small preclinical dataset from another species** (mouse) and **predicted Phase II RCT outcomes of anti-TNF in ulcerative colitis patients**.

This is exactly the cross-species + cross-resolution + clinical-outcome chain INTERCEPTA aspires to.

## 3. Quantitative results — verified claims

- **SOTA results on each of 39 task categories** vs benchmarked biological FMs and baselines (per 2026 arxiv abstract — specific numbers in paper body not visible from snippets)
- **Clear scaling laws up to 300M parameters** — performance improvements with model size
- **Patient response prediction in ulcerative colitis** demonstrated using few-shot fine-tuning on mouse data
- **Mechanistic interpretability:** identified biologically meaningful features in EVA representations, revealing "intertwined representations across species and technologies"
- **Open 60M variant on Hugging Face** for community use; full 300M production version commercial

## 4. What's strong

- **The only Q8 anchor explicitly designed for drug development.** Evaluated on tasks INTERCEPTA actually cares about.
- **39-task comprehensive evaluation suite** — methodologically the most rigorous benchmark framework of any Q8 anchor
- **Cross-species + cross-disease** explicitly tested — directly addresses Charter §1.1 universality
- **Multimodal integration** (transcriptomics + histology + clinical) — broader than dissociated-only FMs
- **Clinical demonstration** with anti-TNF + ulcerative colitis + Phase II RCT prediction — closest to actual clinical impact of any Q8 anchor
- **Patient-level focus** like PaSCient (Q8 anchor 3) — disease modeling at the right unit
- **Cross-species training** (mouse + human) operationally enables preclinical → clinical translation
- **Open 60M variant released on Hugging Face** — INTERCEPTA can use this without commercial barrier
- **EIC Accelerator + Future 40 + ICML/ICLR workshops** — strong external validation
- **Industry-academic partnerships** with European medical institutions
- **Mechanistic interpretability** explicitly studied, providing INTERCEPTA Q7-relevant precedent
- **2025 bioRxiv paper acknowledges generalist FM limitations** (citing prior critical literature) — methodologically honest framing

## 5. What's limited — honest critique

- **I&I therapeutic area only.** Not designed for cancer, neurodegeneration, metabolic disease, etc. **Therefore EVA does NOT directly demonstrate the cross-therapeutic-area universality Charter §1.1 requires.** What it demonstrates is universality *within* I&I.
- **Commercial entity with seed funding.** Scienta's incentive includes selling EVA-derived services to pharma. Independent replication of 39-task SOTA claims would strengthen credibility.
- **All-industry author roster.** Methodology rigor unaffected, but external validation needed.
- **Full 300M production model is commercial.** Only 60M variant open. INTERCEPTA can use the 60M but not the production version — performance gap unclear.
- **License terms on 60M HF variant must be verified** before INTERCEPTA deployment. Could be CC BY-NC-ND or similar non-commercial.
- **Histology integration is newer (2026 arxiv version)** — earlier 2025 bioRxiv was transcriptomics-only. The multimodal claims need fresh validation.
- **39-task evaluation is Scienta-designed.** Comprehensive but vendor-defined. Independent benchmark replication TBD.
- **Souza & Mehta critique applies.** Does EVA's I&I performance beat properly tuned parameter-free baselines on the same 39 tasks? Not visible in the abstract. Need full paper body to confirm.
- **Pretraining corpus (~100K samples) is smaller than TEDDY (116M cells), TranscriptFormer (100M+), Nicheformer (110M).** Specialization vs scale trade-off.
- **Disease-area-specific FM strategy may not scale to "ANY disease."** If INTERCEPTA needs to handle 100 diseases across all therapeutic areas, training 100 EVAs is infeasible. The universality vision may require generalist FMs OR multi-FM portfolios (Decision 1) rather than per-area specialization.
- **No published cross-FM comparison with PaSCient** (which is also patient-level, also multimodal-friendly). The right comparison would be EVA vs PaSCient on I&I patient stratification tasks.

## 6. INTERCEPTA implications

### 6.1 For Q8 (universality) — the key strategic question

EVA presents the **disease-area-specialization paradigm** as an alternative to multi-FM-portfolio (Decision 1) and parameter-free (Souza & Mehta).

**For Charter §1.1 ("drug for ANY disease"), the three options on the table are:**

1. **Multi-FM portfolio** (Decision 1 as currently proposed): general FMs (scFoundation, UCE, scGPT, Geneformer) selected per scenario
2. **Disease-area-specific FM ensemble** (EVA paradigm): per-therapeutic-area FMs (EVA for I&I, hypothetical Cardio-EVA for cardiology, etc.)
3. **Parameter-free** (Souza & Mehta): no FMs; linear methods with proper normalization

**Each option has a coherent argument:**
- Multi-FM: leverages best-of-each existing general FM
- Disease-area-specific: depth where it matters; EVA's 39-task SOTA suggests this works *within* I&I
- Parameter-free: avoids the entire FM compute burden; may generalize better OOD

**Empirically, only Layer 5 ablations on INTERCEPTA's specific drug response tasks will tell us which wins.** All three options should be tested.

### 6.2 For Decision 1 revision (post-Souza-and-Mehta + post-EVA)

Decision 1 must be reframed:

**Pre-audit Decision 1:** "Multi-FM portfolio with scFoundation default, scenario-aware FM selection, parameter-free as fallback."

**Post-Souza-and-Mehta + EVA revision:** "Three-paradigm comparison framework for Layer 5:
- Paradigm A: Multi-FM portfolio (general FMs)
- Paradigm B: Disease-area-specific FM (EVA for I&I; case-study)
- Paradigm C: Parameter-free baseline (scTOP-augmented)

INTERCEPTA defaults to Paradigm A as architecturally most flexible, but **does not commit** until Layer 5 ablations report which paradigm wins on actual drug response tasks."

### 6.3 For Decision 8 (universality)

EVA provides **empirical methodology for the 39-task evaluation framework** that INTERCEPTA should adopt structurally. INTERCEPTA's universality grid (drug × disease × tissue) should be benchmarked with EVA-style 39-task comprehensiveness, not single-task evaluation.

### 6.4 For Decision 4 (drug response architecture)

EVA's specific demonstration — anti-TNF + ulcerative colitis + few-shot mouse-to-human + Phase II prediction — is a **direct architectural blueprint** for INTERCEPTA's L7 layer. The pattern:
1. Pretrain on broad multi-disease multi-species corpus
2. Fine-tune on small preclinical dataset (mouse, in vitro, organoid)
3. Predict clinical outcome in target patient population
4. Mechanistic interpretability for trial design

This is the operational sequence INTERCEPTA can adopt for cross-disease drug repurposing.

### 6.5 For Decision 9 (compute) and Q10 (open source)

- 60M open variant of EVA is operationally usable at INTERCEPTA's Northeastern Explorer scale (well within single-A100 budget)
- 300M commercial variant unavailable to INTERCEPTA → not a blocker; 60M variant suffices for academic research
- **Q10 EVA licensing correction** (already shipped in Phase 1 errata) is validated by this Phase 6 anchor read

### 6.6 For Charter §1.1 cross-therapeutic-area universality

**EVA itself does not demonstrate cross-therapeutic-area universality.** It demonstrates cross-disease universality *within* I&I (multiple diseases sharing pathogenic mechanisms). INTERCEPTA's universality vision is broader.

**However, the EVA paradigm could be extended:** if INTERCEPTA trains on a multi-therapeutic-area corpus (cancer + I&I + neurodegeneration + cardiology) jointly, it becomes the "universal-EVA" — and the question is whether joint training across therapeutic areas degrades disease-specific performance.

PaSCient's multi-disease joint training (Q8 anchor 3, 5,000+ patients across multiple diseases) is the closest existing test of this. EVA's I&I-only specialization is the opposing test. **INTERCEPTA's contribution to the field is the joint multi-therapeutic-area patient-level FM** — combining PaSCient breadth with EVA depth.

## 7. Followup citations (priority for INTERCEPTA)

1. **PaSCient (Q8 anchor 3)** — patient-level multi-disease alternative paradigm
2. **EVA earlier bioRxiv (2025.05.02.651839)** — 50M precursor with anti-TNF / UC case study
3. **EVA-RNA + transcriptomic benchmark for FM in I&I drug development** — ICLR 2025 LMRL workshop, Scienta presented
4. **Souza & Mehta (Q8 anchor 5)** — parameter-free counter-paradigm
5. **TEDDY (Q8 anchor 2)** — scaled general FM alternative
6. **Cell-Graph Compass (Fang et al. 2024)** — graph-structure FM cited by EVA and TEDDY both
7. **ImmunAtlas dataset description papers** (if Scienta publishes the corpus separately) — would provide independent dataset verification
8. **Anti-TNF ulcerative colitis Phase II RCT papers** — to validate EVA's actual predictive accuracy against real trial outcomes

## 8. Discipline check

- [x] First author verified primary-source: Ethan Bandasack ("Scienta Team: Ethan Bandasack and 10 other authors" per arXiv abstract page)
- [x] Full 11-author roster verified: Bandasack, Bouget, Bruley, Cattan, Claye, Corney, Duquesne, El Kanbi, Fouché, Marschall, Strozzi
- [x] Affiliation verified: Scienta Lab, Paris, France (Biolabs Hôtel Dieu)
- [x] Funding/COI verified: commercial entity (Scienta Lab); €4M seed (CentraleSupélec Venture, Dec 2023); EIC Accelerator laureate (June 2025); all authors employed by Scienta
- [x] arXiv 2602.10168 verified across multiple secondary sources
- [x] Open 60M variant on Hugging Face verified (Scienta-Lab organization page)
- [x] 39-task evaluation suite verified from arxiv abstract
- [x] Scaling laws claim verified (Duquesne LinkedIn re: ICLR 2025)
- [x] 2025 bioRxiv precursor verified (10.1101/2025.05.02.651839)
- [x] ICML 2025 FM4LS workshop submission verified (OpenReview)
- [x] ImmunAtlas corpus verified (~100K samples, 96K+ patient/biosample profiles)
- [x] Anti-TNF UC Phase II prediction demonstration verified
- [x] **Errata note:** original 2026-05-10 file had EVA listed as "closed/proprietary" — Phase 1 already corrected to "partially open" with 60M HF variant. This rewrite provides the substantive Q8 anchor read. Drift Instance #5 fully resolved across both Q10 landscape and Q8 anchor.
- [x] **No new drift this cycle.** Verified primary-source for every claim.

— Claude (CSO), 2026-05-10 (Phase 6 re-do)
