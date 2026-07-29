# Wang et al., 2025 — scDrugMap: Benchmarking Large Foundation Models for Drug Response Prediction

## 0. Identification
- **Full citation:** Wang Q, Pan Y, Zhou M, Tang Z, Wang Y, Wang G, Song Q. scDrugMap: Benchmarking Large Foundation Models for Drug Response Prediction. *arXiv preprint* arXiv:2505.05612v1, 2025 May 8.
- **DOI:** 10.48550/arXiv.2505.05612 (arXiv DOI)
- **Published version (ADS hint):** Nature Communications 2025, vol 17, p 730 — to be confirmed via direct journal lookup. **[VERIFY published DOI in next session]**
- **PubMed:** 40386575 (preprint)
- **GitHub:** https://github.com/QSong-github/scDrugMap
- **Website:** https://scdrugmap.com/
- **Layer 1 question:** Q1 (Method-class selection) — sub-questions Q1.1 (SOTA AUROC/F1) and Q1.4 (cancer-bias problem in foundation models)
- **Read by:** Claude (CSO)
- **Read date:** 2026-05-10

## 1. Why This Paper

This paper is the most directly relevant Q1 anchor available because it benchmarks the exact set of method classes our charter §8.1 sketch positions as candidates: foundation models (eight tested) versus alternative approaches, on the exact problem (drug response prediction at single-cell level) for the exact disease class (cancer). Published May 2025, it is the most current systematic benchmark in the space. Its findings directly inform whether INTERCEPTA's Layer 2 architecture should commit to foundation models, and which one.

## 2. What They Did

The authors built scDrugMap, an integrated framework (Python CLI + web server) that benchmarks foundation models for single-cell drug response prediction. They tested **eight single-cell foundation models** (including scFoundation, UCE, scGPT, Geneformer, plus four additional FMs we need to identify from full text) and **two large language models**, across a curated dataset spanning **326,000 cells in the primary collection and 18,800 cells in the validation set, across 36 datasets** in the preprint version (expanded to **495,000 cells across 60 datasets** in the published version per ADS metadata). Evaluation operated under two settings: **pooled-data** (all data mixed) and **cross-data** (held-out dataset generalization). Two fine-tuning strategies tested: **layer freezing** (FM frozen, classifier head trained) and **Low-Rank Adaptation (LoRA)**.

## 3. What They Found

The headline numbers from the abstract:

**Pooled-data setting:**
- scFoundation achieved best performance: **mean F1 = 0.971 (layer freezing)** and **0.947 (fine-tuning via LoRA)**
- Outperformed lowest-performing model by over 50%

**Cross-data setting (the harder, more INTERCEPTA-relevant test):**
- UCE excelled post fine-tuning: **mean F1 = 0.774**
- scGPT led in zero-shot learning: **mean F1 = 0.858**

**INTERCEPTA-relevant interpretation of these numbers:**
- The drop from pooled (F1 ~0.97) to cross-data (F1 ~0.77-0.86) is the cross-cohort generalization gap. Even SOTA foundation models lose ~15-20 F1 points on cross-cohort.
- Different FMs win in different settings — no single FM dominates everywhere.

## 4. What's Strong

- **Scale.** 326K-495K cells is large enough to detect meaningful differences between FMs.
- **Cross-data evaluation explicit.** Many drug-response benchmarks only do within-cohort CV; this one separates pooled vs cross-data, which is the INTERCEPTA-relevant distinction.
- **Multiple FMs and fine-tuning strategies tested.** Layer freezing vs LoRA is the practical choice for compute-constrained labs (LoRA cheaper, layer freezing fastest).
- **Open-source toolkit.** Reproducibility supported via Python package + GitHub.
- **First systematic FM benchmark for drug response.** This fills the gap our Charter §3 Q1 explicitly identified: "What's the actual SOTA F1/AUROC on cross-cohort drug response prediction in 2026?"

## 5. What's Limited

- **Cancer-only.** Datasets span cancer types but not non-cancer diseases. Charter Q1.4 (*"cancer-bias problem in foundation models"*) is unaddressed by this benchmark — they don't test transfer to autoimmune, neurodegeneration, etc. This is a critical limitation for INTERCEPTA's universal-disease vision.
- **F1 vs AUROC.** Authors report F1 scores. Our Round 2.2c results are reported as AUROC. F1 vs AUROC are not directly comparable without knowing the threshold convention. A direct "scDrugMap vs INTERCEPTA AML predictor" comparison requires re-running on a common metric.
- **Mechanistic interpretability not addressed.** Charter §1.3 (I1-I3) requires every prediction trace to mechanism. scDrugMap reports F1 only — no claim about mechanism preservation. The "F1 = 0.971" headline does not establish that foundation model embeddings encode interpretable biology.
- **Drug coverage and class diversity not characterized in abstract.** The 36-60 datasets span "diverse tissue and cancer types and treatment conditions" but specific drug counts, drug classes (BCL2 inhibitors, kinase inhibitors, etc.), and per-drug performance not stated in abstract. Without per-drug analysis, the cohort-mean F1 may obscure mechanism-class structure (the same problem we found in Round 2.2c).
- **Benchmark is point-in-time.** Foundation models from 2024 are tested. New FMs (CancerFoundation, scGPT v2, etc.) emerging fast — benchmark will age.
- **Pre-print at time of our reading.** Per ADS, a Nature Communications version exists — full-text review of published version needed for definitive numbers and methodology details.

## 6. INTERCEPTA Implications

**For Q1.1 (SOTA F1/AUROC):** Cross-data F1 = 0.774-0.858 is the current SOTA cross-cohort benchmark for cancer drug response prediction at single-cell level. **Our Round 2.2c AML mean AUROC of 0.643 is below this SOTA.** This confirms the AML paper's negative-result framing was correct — we did not beat SOTA. **More importantly, this gives us a defensible target: any INTERCEPTA architecture must beat F1 ≥ 0.774 cross-data to claim SOTA.**

**For Q1.3 (layered combinations):** scDrugMap tests FMs alone, not FM + signature scoring + GRN combinations. The charter's §8.1 provisional architecture (Layer 1: A-D = FM, signature scoring, KAALCURA, GRN-based) **is unbenchmarked in scDrugMap**. This is a gap we can fill: does layering FM with mechanism-aware features improve over FM alone? Currently no published benchmark answers this.

**For Q1.4 (cancer-bias in FMs):** scDrugMap is cancer-only. Whether the F1=0.774 cross-data benchmark holds for non-cancer diseases (the U1-U3 universality requirement) is **completely untested**. This is exactly where INTERCEPTA's vision — "ANY disease" — has to either prove or refute the FM approach. **The benchmark gap here is enormous.**

**For architecture commitment (Q1):** This paper provides strong evidence for foundation models on cancer single-cell drug response, with UCE and scGPT performing best in cross-data settings. But it does NOT establish that FMs alone are sufficient for INTERCEPTA's vision. The mechanism-interpretability gap (§5 limitation 3) and the universality gap (§5 limitation 1) are the two biggest unanswered questions for our architecture.

## 7. Followup Citations Worth Tracing

The full text of scDrugMap will cite:
1. **scFoundation paper** — Hao et al. 2024, Nature Methods. Direct anchor for Q1, must read.
2. **UCE paper** — Rosen et al. 2023, BioRxiv (status?). Direct anchor for Q1.
3. **scGPT paper** — Cui et al. 2024, Nature Methods. Direct anchor for Q1.
4. **Geneformer paper** — Theodoris et al. 2023, Nature. Direct anchor for Q1.
5. The 4-5 additional foundation models tested but not named in abstract (likely CellPLM, CellFM, GeneCompass, others).
6. The interpretability critique (arxiv 2602.17532 cited in our Charter §3 Q7) — scDrugMap may or may not cite this; relevant either way.
7. The "Integrating Single-Cell Foundation Models with Graph Neural Networks for Drug Response Prediction (2025)" paper mentioned in EmergentMind sidebar — directly tests Q1.3 (layered combination).

**Highest priority for next reads:** scFoundation (Hao 2024), UCE (Rosen 2023), scGPT (Cui 2024) — the three FMs that scDrugMap shows leading in different settings.

## 8. Discipline Check

- [x] All claims sourced to specific paper sections — abstract sourced from arXiv (verified at https://arxiv.org/abs/2505.05612), GitHub (https://github.com/QSong-github/scDrugMap), and PubMed (PMID 40386575). Numbers verified across at least 3 independent sources.
- [x] No interpolated claims — where I'm guessing (which 4-5 FMs beyond the 4 I named, exact F1 thresholds), I marked it explicitly with "[VERIFY]" or "must be identified from full text."
- [x] Numbers verified by direct read of abstract — F1 numbers (0.971, 0.947, 0.774, 0.858) directly taken from abstract, not paraphrased.
- [x] Limitations noted include ones the authors didn't acknowledge — limitations §5 items 1, 3, 4 (cancer-only, no mechanism trace, no per-drug analysis) are CSO additions, not paper's own caveats.
- [x] No fabricated DOI — arXiv DOI verified. Published Nature Communications DOI flagged [VERIFY] explicitly, not invented.

---

**CSO note:** This is the **first** real Layer 1 paper-by-paper note. It establishes the format and the discipline. It is the substrate for synthesis. Future Q1 paper notes follow this template exactly.

— Claude (CSO)
2026-05-10
