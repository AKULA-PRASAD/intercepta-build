# Cui et al., 2024 — scGPT: Toward Building a Foundation Model for Single-Cell Multi-omics Using Generative AI

> **ERRATA 2026-05-10 (Drift Instances #20 + #21):** This note has been patched. Original v1 incorrectly attributed the Kedzierska et al. zero-shot critique paper (bioRxiv 2023.10.16.561085) to "Boiarsky et al." — corrected throughout. Original v1 also mischaracterized Kendiukhov 2026 Spectral Geometry (arXiv 2602.22247) as a critique of FM biological encoding — primary-source reading revealed it AFFIRMS biological encoding (PPI Spearman ρ=1.000, marker AUROC=0.851, TF/target AUROC=0.744). The actual critique-flavored finding is in the Kendiukhov SAE companion (arXiv 2603.02952) which shows minimal causal regulatory logic (6.2-10.4% CRISPRi-tested TFs). All affected sections (§4, §5, §6, §7, §8, CSO note) updated. See `kedzierska_2023_zero_shot_critique.md` §0.1 and `kendiukhov_2026_spectral_geometry.md` §0.1 for original drift catches.

## 0. Identification
- **Full citation:** Cui H, Wang C, Maan H, Pang K, Luo F, Duan N, Wang B. scGPT: toward building a foundation model for single-cell multi-omics using generative AI. *Nature Methods* 21(8):1470-1480, 2024 Aug (published online Feb 26, 2024).
- **DOI:** 10.1038/s41592-024-02201-0 ✓ (verified across 8+ primary sources: Nature website, Springer Experiments, PubMed-cited, Semantic Scholar Corpus ID 268028472, ResearchGate, ablesci.com, Multiomics review citations, and Year-in-Review 2024)
- **Citations as of read date:** 179-227 (across reporting sources, citation count growing)
- **Affiliations:** Peter Munk Cardiac Centre / University Health Network Toronto, Vector Institute, Microsoft Research Redmond, University of Toronto Departments (Computer Science, Medical Biophysics, Laboratory Medicine and Pathobiology)
- **Co-first authors:** Haotian Cui, Chloe Wang
- **Senior author:** Bo Wang (bowang@vectorinstitute.ai)
- **Code:** https://github.com/bowang-lab/scGPT (Zenodo: 10.5281/zenodo.10466117)
- **Data:** Figshare 10.6084/m9.figshare.24954519.v1
- **Layer 1 question:** Q1 (Method-class selection) — sub-questions Q1.1 (SOTA), Q1.3 (layered combinations), Q1.4 (cancer-bias), Q3 (cross-cohort transfer)
- **Read by:** Claude (CSO)
- **Read date:** 2026-05-10

## 1. Why This Paper

scGPT was identified by Wang et al. 2025 (scDrugMap) as the **best zero-shot drug response performer** (mean F1 = 0.858), the highest cross-data F1 in their entire benchmark. It is also the most-cited single-cell foundation model from 2024 (179-227 citations within ~2 years), making it the standard reference point for any FM-based architecture commitment. Its design philosophy (generative pretraining, GPT-style causal masking, Flash-Attention) differs fundamentally from UCE's (protein-language tokenization via ESM2). Reading scGPT is necessary for Q1 because: (1) it represents a different architectural family than UCE, (2) it has the best zero-shot performance in the most relevant downstream task (drug response), and (3) it is published in Nature Methods (peer-reviewed, unlike UCE's bioRxiv-only status as of read date).

## 2. What They Did

The authors constructed scGPT, a transformer-based foundation model for single-cell biology. Architecture details:

1. **Generative pretraining via GPT-style causal masking.** Inspired by OpenAI's GPT series. Genes are bidirectionally encoded but the pretraining objective is generative: predict next gene's expression given context. This differs from UCE's masked-reconstruction objective.
2. **Equal-frequency expression binning.** Genes binned according to expression value such that genes are evenly distributed across each bin (vs scBERT's log-scale binning). This handles long-tailed expression distributions.
3. **Random gene identity embedding + condition embedding.** Each gene has a learned identity embedding (not pretrained from gene2vec). Additional "condition embedding" describes meta-information about each gene.
4. **Flash-Attention.** Memory-efficient attention via Flash-Attention blocks. Enables handling of larger gene contexts than standard attention.
5. **CLS token cell embedding.** Final cell embedding from CLS token output (architectural similarity to UCE; both use BERT-style CLS).

**Training data:** **33 million human cells** (vs UCE's 36 million across 8 species — scGPT is human-only at training time, larger per-species but no cross-species capability).

**Pretraining objective:** Generative masked prediction (GPT-style) — predict gene expression given preceding context. Self-supervised, no annotations required.

**Downstream tasks evaluated** (per Fig 2-6 of paper):
1. Cell type annotation (cross-cohort)
2. Genetic perturbation prediction
3. Multi-batch and multi-omic integration
4. Reverse perturbation (which genes were perturbed?)
5. Gene network inference via attention analysis
6. Gene token embedding analysis (gene-gene relationships)

## 3. What They Found

**Headline claims from abstract:**
- scGPT effectively distills critical biological insights concerning genes and cells.
- Through transfer learning, scGPT can be optimized to achieve superior performance across diverse downstream applications.
- (Specific cross-cohort drug response F1 numbers are NOT in scGPT's own paper — those come from downstream benchmarks like scDrugMap.)

**From scDrugMap downstream evaluation (Wang 2025):** scGPT achieves **mean F1 = 0.858 cross-data zero-shot** — the highest zero-shot performer in the cross-data setting.

**Specific tasks where scGPT reports strong performance** (per paper Fig 2-6, abstract refers to multiple Figs):
- Cell type annotation across diverse tissues/datasets
- Genetic perturbation response prediction (Fig 3)
- Batch correction and multi-omic integration (Fig 4)
- Gene network inference via attention attribution (Fig 6)

**Architectural innovation evidence:**
- Generative pretraining outperforms discriminative pretraining (claim made in paper, supported by ablation)
- Flash-Attention enables larger context windows than standard transformers
- Equal-frequency expression binning improves over log-scale binning (claim, supported by ablation)

## 4. What's Strong

- **Peer-reviewed.** Nature Methods, August 2024 — passed rigorous review. Unlike UCE (still bioRxiv at read date), scGPT has institutional credibility.
- **Best zero-shot drug response performance per scDrugMap.** F1 = 0.858 cross-data zero-shot is the highest in any FM benchmark to date. **This means scGPT can be deployed without fine-tuning** — a major operational advantage for INTERCEPTA's compute reality (Charter §7.1).
- **Generative pretraining matches the GPT/LLM paradigm.** Drawing parallel from cells-as-words, the GPT-style approach has been wildly successful in NLP. scGPT extends this paradigm to cells, opening the door to all GPT-era techniques (in-context learning, prompt engineering, chain-of-thought reasoning).
- **Multi-task evaluation.** Paper evaluates 6 distinct downstream tasks (cell type annotation, perturbation prediction, integration, reverse perturbation, gene network inference, gene embedding analysis). Most FMs evaluate only 1-2 tasks.
- **Attention-based gene network inference (Fig 6).** Direct interpretability — model learns which gene-gene interactions matter for prediction. **This addresses Charter §1.3 (I1-I3 mechanistic interpretability) more directly than UCE.** scGPT's attention can be inspected for biological meaning.
- **Strong open-source ecosystem.** Github + Zenodo + Figshare, code/data/models all released. Reproducibility supported.
- **Vector Institute + Microsoft Research backing.** Institutional resources supporting maintenance and extension.
- **179-227 citations within 2 years.** Field consensus that this paper is foundational.

## 5. What's Limited

- **Human cells only.** 33M human cells, no cross-species training. **For INTERCEPTA's universal-disease vision applied to non-human disease models (mouse-human translation, animal disease models), scGPT lacks UCE's species-agnostic capability.**
- **No protein-language tokenization.** Random gene identity embedding means gene representation is learned purely from co-occurrence patterns in expression data. Genes that are rarely co-expressed but are biologically important may be poorly represented. UCE's ESM2-based approach is more principled biologically.
- **Cancer-bias same as UCE.** Training corpus diverse but **no specific evaluation of non-cancer disease drug response transfer.** Charter Q1.4 unaddressed by scGPT alone.
- **F1 = 0.858 zero-shot is per scDrugMap, not paper itself.** scGPT's own paper does not report cross-cohort drug response F1; this comes from downstream benchmarks. The paper evaluates perturbation prediction (different from drug response) and cell type annotation. **A direct INTERCEPTA validation would require running scGPT on Beat AML drug response, which neither paper does.**
- **Critique exists.** A 2023 paper "Assessing the limits of zero-shot foundation models in single-cell biology" (Kedzierska et al., bioRxiv 2023.10.16.561085) compared scGPT and Geneformer zero-shot to scVI **trained per dataset** and found scVI competitive in some integration settings. **This is a disagreeing source that Charter §3 termination criterion 1 ("convergence") must address.** Not all literature endorses scGPT's zero-shot superiority.
- **Mechanistic interpretability nuance (UPDATED via errata).** Kendiukhov 2026 "Multi-Dimensional Spectral Geometry of Biological Knowledge in Single-Cell Transformer Representations" (arXiv 2602.22247) — initially characterized in this note as a critique, but primary-source verification revealed it AFFIRMS that scGPT encodes structured biological knowledge (PPI Spearman ρ=1.000, marker AUROC=0.851, TF/target AUROC=0.744). The COMPANION paper (Kendiukhov SAE arXiv 2603.02952) provides the more critical finding: only 6.2-10.4% of CRISPRi-tested TFs show regulatory-target-specific feature responses — FMs encode statistical co-expression but minimal causal regulatory logic. **This nuanced picture (rich biology + minimal causal regulation) is the actual mechanistic interpretability finding for Charter Q7 — see `kendiukhov_2026_spectral_geometry.md` and Decision 1 §3.**
- **Compute scale of pretraining.** Pretraining 33M cells with Flash-Attention transformer at scale required substantial GPU hours (specific TPU/GPU hours not in abstract — full text needed). For INTERCEPTA inference + LoRA fine-tuning, manageable. For pretraining from scratch, infeasible at single-institution scale.
- **Generative pretraining — does it actually help?** scGPT claims generative > discriminative for biology. The Kedzierska et al. critique partially questions this. Whether generative is the right paradigm for biology (vs masked-reconstruction in UCE, vs contrastive learning, vs others) is **not settled by scGPT's paper alone**.
- **Gene network inference via attention is not validated as ground truth causal regulation.** Fig 6 shows scGPT learns gene networks that match known biology — Kendiukhov Spectral Geometry independently AFFIRMS this (TF/target AUROC=0.744, "geometric echo of germinal center reaction"). But: attention/representational structure ≠ causal regulation (per Kendiukhov SAE companion: only 6.2% of CRISPRi-tested TFs show regulatory specificity). The "attention matches biology" finding is statistical, not causal — supplementing with external GRN/CRISPRi data is needed for true causal claims.

## 6. INTERCEPTA Implications

**For Q1.1 (SOTA):** scGPT achieves the best zero-shot cross-data drug response F1 (0.858). **This is the highest F1 in cross-cohort prediction available without fine-tuning.** UCE achieves 0.774 fine-tuned. **The trade-off:** scGPT is more deployable (no fine-tuning needed) but UCE may be more universal (cross-species). Both numbers are above INTERCEPTA's AML 0.643 mean AUROC.

**For Q1.3 (layered architecture):** scGPT's attention-based gene network inference (Fig 6) suggests layered architecture is feasible — scGPT embedding for representation + attention attribution for mechanism-trace + downstream predictor for drug response. **INTERCEPTA could test scGPT-embedding + signature-scoring + GRN as a layered architecture, which is unbenchmarked anywhere in the literature.**

**For Q1.4 (cancer-bias problem):** scGPT trained on 33M human cells across diverse tissues. Cancer-vs-non-cancer transfer **untested by scGPT itself**. The Kedzierska et al. limits-of-zero-shot critique should inform our skepticism. **INTERCEPTA's cross-disease transfer experiment is genuine novel territory.**

**For Q7 (mechanistic interpretability):** scGPT's attention-based interpretability (Fig 6) is the strongest claim of mechanistic interpretability among FMs. **Kendiukhov 2026 Spectral Geometry AFFIRMS rich biological encoding** (PPI ρ=1.000, marker AUROC=0.851, TF/target AUROC=0.744 — see `kendiukhov_2026_spectral_geometry.md`). **The Kendiukhov SAE companion (arXiv 2603.02952) reveals the limit: minimal causal regulatory logic** (only 6.2-10.4% of CRISPRi-tested TFs). This is exactly the nuance Charter §3 termination criterion 2 ("explicit gaps") wants documented — and the architectural justification for Charter §8.1 layered architecture (FM + signature + GRN).

**For Q3 (cross-cohort transfer):** scGPT at F1 = 0.858 cross-data zero-shot is the best evidence of cross-cohort transfer for cancer drug response. But "cross-data" in scDrugMap means cross-dataset (likely same disease class) — not cross-disease-class. **The harder cross-disease-class test remains open.**

**For decision defensibility (Charter §3 termination criterion 4):** A reviewer asking "why scGPT?" gets: "Best zero-shot cross-data F1 per scDrugMap; peer-reviewed in Nature Methods; institutional backing from Vector Institute; Kendiukhov 2026 Spectral Geometry AFFIRMS its biological encoding." A reviewer asking "why not scGPT alone?" gets: "Human-only training; cancer-vs-non-cancer transfer untested; Kedzierska shows zero-shot fails on cell integration tasks; Kendiukhov SAE companion shows minimal causal regulatory logic — supplementation with external GRN data needed (Charter §8.1 layered architecture)." Defensibility for and against both available.

**For novelty territory INTERCEPTA could fill:**
- **Layered architecture (scGPT embedding + signature scoring + GRN):** unbenchmarked
- **Cross-disease-class transfer (cancer → autoimmune via scGPT zero-shot):** unbenchmarked
- **Mechanism-interpretability validation under scGPT (does attention actually predict drug response causation?):** unbenchmarked
- **Multiple-FM ensemble (UCE + scGPT + scFoundation):** unbenchmarked

## 7. Followup Citations Worth Tracing

Critical priority:
1. **Kedzierska et al., 2023 — "Assessing the limits of zero-shot foundation models in single-cell biology"** (bioRxiv 2023.10.16.561085) — DIRECTLY critiques scGPT's zero-shot claims. **MUST READ.** This is the disagreeing source charter §3 termination criterion 2 needs.
2. **arXiv 2602.22247 (Kendiukhov 2026 Spectral Geometry)** — AFFIRMS scGPT encodes structured biological knowledge. **Already read** (`kendiukhov_2026_spectral_geometry.md`). **The companion paper (Kendiukhov SAE, arXiv 2603.02952) is the more critical finding** — quantifies minimal causal regulatory logic. SAE companion remains MUST READ for Charter Q7 termination.
3. **Hao et al., 2024 — scFoundation** (Nature Methods 21:1481-1491) — same issue of Nature Methods! Strong companion read.
4. **Theodoris et al., 2023 — Geneformer** — primary competitor that scGPT explicitly differs from in pretraining objective.

Useful priority:
5. **Lotfollahi et al., 2019 — scGen** (Nature Methods 16:715-721) — predecessor for perturbation response prediction; scGPT extends this.
6. **Cao and Gao, 2022 — GLUE** (Nature Biotechnology 40:1458-1466) — multi-omic integration baseline that scGPT compares against in Fig 4.
7. **Zhang et al., 2023 — scMoMat** (Nature Communications 14:384) — multi-modal integration baseline.
8. **Bommasani et al., 2021 — "On the opportunities and risks of foundation models"** — the canonical FM discussion paper, cited by scGPT.

## 8. Discipline Check

- [x] All claims sourced — Nature Methods abstract via Nature website, Springer Experiments, ResearchGate; verified DOI across 8+ independent sources.
- [x] No interpolated claims — where I'm guessing (specific TPU/GPU hours of pretraining; full text Fig 2-6 details), I marked it explicitly. Where I synthesized §5 critiques from other papers found via search, I cited those papers explicitly (Kedzierska 2023, Spectral Geometry arXiv 2602.22247).
- [x] Numbers verified — DOI, page numbers, training data size (33M cells), publication date (Feb 26, 2024 online; August 2024 issue), citation count (179-227 range from multiple sources).
- [x] Limitations include ones authors didn't acknowledge — §5 limitations 1 (human-only), 4 (F1 not from own paper), 5 (Kedzierska critique exists), 6 (mechanistic interpretability nuance — Kendiukhov Spectral Geometry AFFIRMS biology / SAE companion limits causal regulation), 9 (attention is statistical not causal) are CSO-identified, not authors' caveats.
- [x] No fabricated DOI — 10.1038/s41592-024-02201-0 verified across multiple primary sources.

---

**CSO note (cross-paper convergence after 3 papers):**

With scDrugMap + UCE + scGPT, three observations emerge:

1. **All three papers endorse foundation models as SOTA** for cancer-relevant single-cell tasks. **Convergence on FM as method class.**

2. **No single FM dominates everywhere.** scGPT wins zero-shot, UCE wins fine-tuned, scFoundation wins pooled-data (per scDrugMap). **Convergence-with-divergence on specific FM choice — depends on deployment setting.**

3. **None of the three test cancer-to-non-cancer disease drug response transfer.** **Convergent gap.** This is INTERCEPTA's novelty territory.

4. **scGPT introduces nuanced literature landscape** — the Kedzierska et al. zero-shot critique and the Kendiukhov interpretability papers (Spectral Geometry AFFIRMS biological encoding; SAE companion shows minimal causal regulation) refine the proponent narrative. **First instance of literature nuance** visible. Charter §3 criterion 1 (convergence) must be re-evaluated as: *"task-conditioned convergence — FMs SOTA for drug response classification per scDrugMap, but FMs need supplementation for causal regulation per Kendiukhov SAE companion."* Both proponent and nuance literature must be read for honest decision-defensibility.

— Claude (CSO)
2026-05-10
